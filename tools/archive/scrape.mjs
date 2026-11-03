import { chromium } from "playwright";
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const hash = (url) => createHash("sha256").update(url).digest("hex").slice(0, 24);
const attachmentPattern = /\.(?:pdf|docx?|xlsx?|pptx?|odt|ods|zip|jpe?g|png|gif|webp|svg|mp4|mp3)$/i;
const assetTypes = {
  "text/css": ".css",
  "application/javascript": ".js",
  "text/javascript": ".js",
  "image/jpeg": ".jpg",
  "image/png": ".png",
  "image/webp": ".webp",
  "image/gif": ".gif",
  "image/svg+xml": ".svg",
  "image/x-icon": ".ico",
  "font/woff": ".woff",
  "font/woff2": ".woff2",
  "application/font-woff": ".woff",
  "application/pdf": ".pdf",
};

export function publicPage(value, base, hostname) {
  const url = new URL(value, base);
  if (!["http:", "https:"].includes(url.protocol)) return null;
  if (url.username || url.password) return null;
  if (url.hostname.replace(/^www\./, "") !== hostname.replace(/^www\./, "")) return null;
  if (/\/(?:wp-admin|wp-login\.php|wp-json|feed)(?:\/|$)/i.test(url.pathname)) return null;
  if (/\.(?:xml|json)$/i.test(url.pathname) || attachmentPattern.test(url.pathname)) return null;
  if ([...url.searchParams.keys()].some((key) => !["page_id", "p", "paged", "page"].includes(key))) return null;
  url.hash = "";
  url.searchParams.sort();
  return url.href;
}

function relativeReference(from, to) {
  return path.posix.relative(path.posix.dirname(from), to) || path.posix.basename(to);
}

function replaceReferences(text, from, files, base) {
  return text.replace(/url\(\s*(['"]?)(.*?)\1\s*\)/gi, (match, quote, value) => {
    if (!value || value.startsWith("data:") || value.startsWith("#")) return match;
    const resolved = new URL(value, base);
    const fragment = resolved.hash;
    resolved.hash = "";
    const file = files.get(resolved.href);
    return file ? `url("${relativeReference(from, file)}${fragment}")` : match;
  });
}

export async function archiveSite({
  url,
  output,
  maxPages = 500,
  delayMs = 2000,
  challengeTimeoutMs = 45000,
  resume = false,
}) {
  const start = new URL(url);
  if (!["http:", "https:"].includes(start.protocol) || start.username || start.password) {
    throw new Error("SOURCE_URL must be a public HTTP(S) URL without credentials.");
  }
  if (!Number.isInteger(maxPages) || maxPages < 1 || !Number.isFinite(delayMs) || delayMs < 0) {
    throw new Error("MAX_PAGES must be a positive integer and DELAY_MS must be non-negative.");
  }
  await mkdir(output, { recursive: true });
  const report = { source: start.href, complete: false, pages: [], assets: [], errors: [], skipped: [], brokenLinks: [] };
  const files = new Map();
  const snapshots = [];
  const assets = new Map();
  const pending = new Set();
  const queue = [start.href];
  const seen = new Set();
  let browser;
  let page;
  let documentStatus;

  if (resume) {
    const previous = JSON.parse(await readFile(path.join(output, "manifest.json"), "utf8"));
    if (previous.source !== start.href) throw new Error("Resume source must match the existing archive.");
    if (!Array.isArray(previous.remainingPages)) throw new Error("This archive has no saved crawl queue.");
    report.pages = previous.pages;
    report.skipped = previous.skipped;
    report.brokenLinks = previous.brokenLinks || [];
    report.previousRunErrors = previous.errors;
    queue.splice(0, queue.length, ...previous.remainingPages);
    for (const entry of previous.pages) {
      seen.add(entry.url);
      seen.add(entry.requestedUrl);
      files.set(entry.url, entry.file);
      files.set(entry.requestedUrl, entry.file);
      snapshots.push({ ...entry, html: await readFile(path.join(output, entry.file), "utf8"), archived: true });
    }
    for (const entry of previous.assets) {
      assets.set(entry.url, { ...entry, body: await readFile(path.join(output, entry.file)), archived: true });
      files.set(entry.url, entry.file);
    }
  }

  async function saveResponse(response) {
    if (response.request().method() !== "GET" || !response.ok()) return;
    if (response.frame().url() && new URL(response.frame().url()).hostname.replace(/^www\./, "") !== start.hostname.replace(/^www\./, "")) return;
    const mime = (response.headers()["content-type"] || "").split(";")[0].trim();
    const extension = assetTypes[mime];
    if (!extension) return;
    const address = response.url();
    if (assets.has(address)) return;
    assets.set(address, null);
    const body = await response.body();
    const file = `assets/${hash(address)}${extension}`;
    assets.set(address, { url: address, file, mime, body });
    files.set(address, file);
  }

  try {
    browser = await chromium.launch();
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    page = await context.newPage();
    page.on("response", (response) => {
      if (response.request().isNavigationRequest() && response.frame() === page.mainFrame()) {
        documentStatus = response.status();
      }
      const task = saveResponse(response).catch((error) => {
        report.errors.push({ url: response.url(), error: `Asset: ${error.message}` });
        console.error(`Asset failed: ${response.url()}: ${error.message}`);
      }).finally(() => pending.delete(task));
      pending.add(task);
    });

    while (queue.length && report.pages.length < maxPages) {
      const address = queue.shift();
      if (seen.has(address)) continue;
      seen.add(address);
      console.log(`Loading ${address}`);
      const response = await page.goto(address, { waitUntil: "domcontentloaded", timeout: 60000 });
      if (!response) throw new Error(`No document response for ${address}`);

      // Let ordinary browser JavaScript finish; never solve CAPTCHAs or retry a denied page.
      await page.waitForFunction(() => !document.querySelector(
        'meta[name^="onehop-proof-of-work"], iframe[src*="captcha"], #challenge-form',
      ), null, { timeout: challengeTimeoutMs });
      if (documentStatus >= 400) {
        if ([404, 410].includes(documentStatus)) {
          report.brokenLinks.push({ url: address, status: documentStatus });
          console.error(`Dead source link: HTTP ${documentStatus} ${address}`);
          await page.waitForTimeout(delayMs);
          continue;
        }
        throw new Error(`HTTP ${documentStatus} at ${page.url()}; access is still denied.`);
      }
      const finalAddress = publicPage(page.url(), address, start.hostname);
      if (!finalAddress) throw new Error(`Redirect outside public crawl scope: ${page.url()}`);
      seen.add(finalAddress);

      await page.waitForTimeout(1000);
      // Scroll to trigger lazy-loaded photographs, then collect the mobile image variants too.
      for (let i = 0; i < 30; i++) {
        const bottom = await page.evaluate(() => {
          window.scrollBy(0, window.innerHeight);
          return window.scrollY + window.innerHeight >= document.documentElement.scrollHeight;
        });
        await page.waitForTimeout(150);
        if (bottom) break;
      }
      const links = await page.locator("a[href]").evaluateAll((nodes) => nodes.map((node) => node.href));
      for (const link of links) {
        const target = publicPage(link, finalAddress, start.hostname);
        if (target && !seen.has(target) && !queue.includes(target)) queue.push(target);
        if (!target) report.skipped.push(link);
      }
      for (const link of new Set(links)) {
        const download = new URL(link);
        if (!["http:", "https:"].includes(download.protocol) || !attachmentPattern.test(download.pathname)) continue;
        if (download.hostname.replace(/^www\./, "") !== start.hostname.replace(/^www\./, "")) continue;
        download.hash = "";
        const address = download.href;
        if (assets.get(address)) continue;
        const result = await context.request.get(link);
        if (!result.ok()) throw new Error(`Document download failed: HTTP ${result.status()} ${link}`);
        const mime = (result.headers()["content-type"] || "").split(";")[0].trim();
        if (mime === "text/html") throw new Error(`Attachment returned HTML instead of a file: ${link}`);
        const file = `assets/${hash(address)}${path.extname(download.pathname).toLowerCase()}`;
        assets.set(address, { url: address, file, mime, body: await result.body() });
        files.set(address, file);
        await page.waitForTimeout(delayMs);
      }
      const file = report.pages.length === 0 ? "index.html" : `pages/${hash(finalAddress)}/index.html`;
      files.set(address, file);
      files.set(finalAddress, file);
      const html = await page.evaluate(() => {
        const copy = document.documentElement.cloneNode(true);
        const originals = [...document.querySelectorAll("img")];
        copy.querySelectorAll("img").forEach((image, index) => {
          if (originals[index].currentSrc) image.setAttribute("src", originals[index].currentSrc);
        });
        return "<!doctype html>\n" + copy.outerHTML;
      });
      snapshots.push({ url: finalAddress, file, html });
      report.pages.push({ url: finalAddress, requestedUrl: address, file, title: await page.title() });
      console.log(`Archived ${finalAddress} -> ${file}`);
      await page.setViewportSize({ width: 390, height: 844 });
      await page.waitForTimeout(1000);
      await page.setViewportSize({ width: 1440, height: 1000 });
      await page.waitForTimeout(delayMs);
    }
    if (queue.some((address) => !seen.has(address))) {
      throw new Error(`MAX_PAGES=${maxPages} reached with uncrawled links remaining; archive is partial.`);
    }
  } catch (error) {
    report.errors.push({ error: error.message });
    console.error(`Archive stopped: ${error.message}`);
    if (page && !page.isClosed()) {
      await writeFile(path.join(output, "last-page.html"), await page.content());
      await page.screenshot({ path: path.join(output, "last-page.png") });
    }
  } finally {
    await Promise.all([...pending]);
    if (browser) await browser.close();
  }

  // Rewrite snapshots after discovery so links to pages visited later resolve locally.
  for (const file of files.values()) {
    files.set(`https://archive.invalid/${file}`, file);
  }
  browser = await chromium.launch();
  try {
    const page = await browser.newPage({ javaScriptEnabled: false });
    for (const snapshot of snapshots) {
      await page.route("**/*", (route) => route.abort());
      await page.setContent(snapshot.html);
      await page.evaluate(({ entries, file, base }) => {
        const mapping = new Map(entries);
        const relative = (target) => {
          const parts = file.split("/").slice(0, -1);
          const next = target.split("/");
          while (parts.length && next.length && parts[0] === next[0]) {
            parts.shift();
            next.shift();
          }
          return [...parts.map(() => ".."), ...next].join("/");
        };
        document.querySelectorAll("base, script").forEach((node) => node.remove());
        for (const node of document.querySelectorAll("[href], [src], [poster]")) {
          for (const name of ["href", "src", "poster"]) {
            const value = node.getAttribute(name);
            if (!value || value.startsWith("#")) continue;
            const target = new URL(value, base);
            const fragment = target.hash;
            target.hash = "";
            if (mapping.has(target.href)) node.setAttribute(name, relative(mapping.get(target.href)) + fragment);
            else node.setAttribute(name, target.href);
          }
        }
        document.querySelectorAll("[srcset]").forEach((node) => node.removeAttribute("srcset"));
      }, {
        entries: [...files],
        file: snapshot.file,
        base: snapshot.archived ? `https://archive.invalid/${snapshot.file}` : snapshot.url,
      });
      const html = replaceReferences(await page.content(), snapshot.file, files,
        snapshot.archived ? `https://archive.invalid/${snapshot.file}` : snapshot.url);
      await mkdir(path.dirname(path.join(output, snapshot.file)), { recursive: true });
      await writeFile(path.join(output, snapshot.file), html);
    }
    await mkdir(path.join(output, "assets"), { recursive: true });
    for (const asset of assets.values()) {
      if (!asset) continue;
      const body = asset.mime === "text/css"
        ? replaceReferences(asset.body.toString(), asset.file, files,
          asset.archived ? `https://archive.invalid/${asset.file}` : asset.url)
        : asset.body;
      await writeFile(path.join(output, asset.file), body);
      report.assets.push({ url: asset.url, file: asset.file, mime: asset.mime });
    }
  } finally {
    await browser.close();
  }
  report.complete = report.errors.length === 0 && report.pages.length > 0;
  report.remainingPages = queue.filter((address) => !seen.has(address));
  await writeFile(path.join(output, "manifest.json"), JSON.stringify(report, null, 2) + "\n");
  return report;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const directory = new Date().toISOString().replace(/[:.]/g, "-");
  const report = await archiveSite({
    url: process.env.SOURCE_URL || "https://alingsasju-jutsu.se/",
    output: process.env.RESUME_ARCHIVE || path.join(process.env.ARCHIVE_DIR || "/archive", directory),
    maxPages: Number(process.env.MAX_PAGES || 500),
    delayMs: Number(process.env.DELAY_MS || 2000),
    resume: Boolean(process.env.RESUME_ARCHIVE),
  });
  console.log(`Saved ${report.pages.length} pages and ${report.assets.length} assets. Complete: ${report.complete}`);
  process.exitCode = report.complete ? 0 : 1;
}
