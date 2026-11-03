import { test } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { archiveSite, publicPage } from "./scrape.mjs";

test("crawl stays on public same-site pages", () => {
  assert.equal(publicPage("/?page_id=31#fees", "https://alingsasju-jutsu.se/", "alingsasju-jutsu.se"), "https://alingsasju-jutsu.se/?page_id=31");
  for (const link of ["/wp-admin/", "/wp-login.php", "/?action=logout", "https://example.com/", "mailto:info@example.com", "/photo.jpg", "/registration.xls", "/rules.docx"]) {
    assert.equal(publicPage(link, "https://alingsasju-jutsu.se/", "alingsasju-jutsu.se"), null);
  }
});

test("archives linked public content and rewrites page, CSS, image and PDF URLs", async () => {
  const server = http.createServer((request, response) => {
    if (request.url === "/style.css") {
      response.setHeader("content-type", "text/css");
      response.end('body { background-image: url("/photo.svg"); }');
    } else if (request.url === "/photo.svg") {
      response.setHeader("content-type", "image/svg+xml");
      response.end('<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"></svg>');
    } else if (request.url === "/registration.xls") {
      response.setHeader("content-type", "application/vnd.ms-excel");
      response.end("example spreadsheet");
    } else if (request.url === "/rules.pdf") {
      response.setHeader("content-type", "application/pdf");
      response.end("%PDF-1.4\n%%EOF");
    } else if (request.url === "/blocked") {
      response.statusCode = 503;
      response.setHeader("content-type", "text/html");
      response.end('<meta name="onehop-proof-of-work-id" content="test"><h1>Blocked</h1>');
    } else if (request.url === "/missing") {
      response.statusCode = 404;
      response.end("Missing page");
    } else {
      response.setHeader("content-type", "text/html");
      response.end(`<!doctype html><html><head><title>Club</title><link rel="stylesheet" href="/style.css"></head><body><h1>Club page</h1><a href="/?page_id=31">Fees</a><a href="/rules.pdf">Rules</a><a href="/registration.xls">Registration</a><img src="/photo.svg"></body></html>`);
    }
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const url = `http://127.0.0.1:${server.address().port}/`;
  const directory = await mkdtemp(path.join(os.tmpdir(), "club-archive-test-"));
  try {
    const report = await archiveSite({ url, output: directory, delayMs: 0 });
    assert.equal(report.complete, true);
    assert.equal(report.pages.length, 2);
    assert.equal(report.assets.length, 4);
    const html = await readFile(path.join(directory, "index.html"), "utf8");
    assert.match(html, /href="pages\/[a-f0-9]+\/index.html"/);
    assert.match(html, /src="assets\/[a-f0-9]+\.svg"/);
    assert.match(html, /href="assets\/[a-f0-9]+\.pdf"/);
    assert.match(html, /href="assets\/[a-f0-9]+\.xls"/);
    const stylesheet = report.assets.find((asset) => asset.mime === "text/css");
    assert.match(await readFile(path.join(directory, stylesheet.file), "utf8"), /url\("[a-f0-9]+\.svg"\)/);
    const partialDir = path.join(directory, "partial");
    const partial = await archiveSite({ url, output: partialDir, delayMs: 0, maxPages: 1 });
    assert.equal(partial.complete, false);
    assert.equal(partial.remainingPages.length, 1);
    const resumed = await archiveSite({ url, output: partialDir, delayMs: 0, resume: true });
    assert.equal(resumed.complete, true);
    assert.equal(resumed.pages.length, 2);
    const resumedHtml = await readFile(path.join(partialDir, "index.html"), "utf8");
    assert.match(resumedHtml, /href="pages\/[a-f0-9]+\/index.html"/);
    assert.match(resumedHtml, /src="assets\/[a-f0-9]+\.svg"/);
    const dead = await archiveSite({ url: url + "missing", output: path.join(directory, "missing"), delayMs: 0 });
    assert.equal(dead.brokenLinks[0].status, 404);
    const denied = await archiveSite({ url: url + "blocked", output: path.join(directory, "blocked"), delayMs: 0, challengeTimeoutMs: 500 });
    assert.equal(denied.complete, false);
    assert.equal(denied.pages.length, 0);
    assert.ok(denied.errors.length > 0);
    assert.match(await readFile(path.join(directory, "blocked", "last-page.html"), "utf8"), /Blocked/);
  } finally {
    await new Promise((resolve) => server.close(resolve));
    await rm(directory, { recursive: true });
  }
});
