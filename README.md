# Alingsås Ju-Jutsu

Jekyll site for GitHub Pages, configured for `https://alingsasju-jutsu.se`.

## Local development with Docker

Install Docker with the Compose plugin and GNU Make, then start the live-reloading
development server:

```sh
make serve
```

Open [http://localhost:4000](http://localhost:4000). The project directory is
mounted into the container, so changes are picked up automatically. Stop the
server with `Ctrl+C` or `make stop`.

Build the static site into `_site/` or remove generated output with:

```sh
make build
make clean
```

The site is built and deployed by the GitHub Actions workflow in
`.github/workflows/pages.yml`. In the repository settings, set Pages' build and
deployment source to **GitHub Actions**.

The deployment workflow reads the site's origin and base path from GitHub
Pages, overriding `_config.yml` for that build. The project preview at
`https://alingsas-ju-jutsu.github.io/alingsasju-jujutsu.se/` therefore uses the
repository path for assets and links. When ready to launch, configure
`alingsasju-jutsu.se` as the custom domain in **Settings → Pages**, update DNS,
and run the deployment workflow again. It will use the custom domain without
the repository path; no code change is needed. Local Docker preview is unchanged.

## Launching on alingsasju-jutsu.se

1. Keep the existing domain DNS unchanged while reviewing the test site.
   Ensure the updated deployment workflow has been pushed to `main`.
2. When ready to switch, open **Settings → Pages**, keep the source set to
   **GitHub Actions**, and set **Custom domain** to `alingsasju-jutsu.se`.
   The repository's `CNAME` file already contains this domain; with this
   Actions-based deployment, configure the domain in Pages settings as well.
3. At the DNS provider, replace conflicting website A/AAAA records for the
   apex domain (`@`) with GitHub Pages' A records:

   | Type | Name | Value |
   | --- | --- | --- |
   | A | @ | 185.199.108.153 |
   | A | @ | 185.199.109.153 |
   | A | @ | 185.199.110.153 |
   | A | @ | 185.199.111.153 |
   | CNAME | www | alingsas-ju-jutsu.github.io |

   Use the DNS provider's equivalent of `@` for the root domain. The `www`
   CNAME is a hostname only, with no repository path. Preserve email/MX
   records and unrelated TXT records. If IPv6/AAAA records exist, update them
   to GitHub's documented values or remove stale website AAAA records so
   IPv6 visitors do not continue reaching the old server. Check the current
   values in GitHub's [custom-domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
   before changing DNS.
4. Open **Actions → Deploy Jekyll site to Pages → Run workflow** on `main`
   after saving the custom domain. The build automatically uses the domain
   and an empty base path instead of `/alingsasju-jujutsu.se`.
5. Wait for the Pages DNS check and certificate provisioning, then enable
   **Enforce HTTPS** in **Settings → Pages** when available.
6. Verify `https://alingsasju-jutsu.se/` and `https://www.alingsasju-jutsu.se/`,
   including images, menus, training schedules and a news article. Confirm
   that links and canonical URLs use the real domain without the repository
   prefix. The GitHub project URL may redirect to the custom domain afterward.

No changes to `_config.yml`, Markdown links or CSS paths are needed for this
switch: the workflow derives the deployment URL from GitHub Pages settings.
DNS changes and certificate provisioning can take time; retain access to the
old hosting until the new site is confirmed working.

The homepage and local subpages use the archived site's logo, desktop/mobile
hero photos, club address, contact details, social links, and navigation. All
club navigation links point to pages on this site. The completed public archive
has been migrated into 24 club subpages and 60 dated news pages, available from
`/nyheter/`. Fees, contacts, rules, instructor posters, schedules, statutes,
camp reports, grading galleries and linked documents are included. Alingsåslägret
year pages remain nested under Läger → Alingsåslägret.

Source information was captured on 2026-11-03, not verified as current. The 2013
calendar, dated schedule and news are explicitly historical. Instructor-only
material was password protected and is not available in this static site.
Grading posts without available photos have been removed. One unavailable
external camp image is marked rather than hotlinked. Dead source links are also labelled. `_data/import_report.json`
records unresolved references. The original `_old_site` archive is retained
locally as a source reference and excluded from Git and the generated site.
Page content is stored directly in `_club_pages/*.md`, with media in
`assets/archive/`, so deployment does not depend on the local source archive.

## Publicera en nyhet utan att redigera filer

Välj **Issues → New issue → Publicera en nyhet**. Skriv eller klistra in
texten, eller ge agenten stödord med de fakta som ska vara med. Dra in bilder
om du vill. Det enda obligatoriska fältet är vad du vill berätta.

En ansvarig person tilldelar ärendet till **Copilot**, som föreslår rubrik,
formaterar texten och skapar ett ändringsförslag. Nyheten kommer automatiskt
med på sidan Nyheter. Kontrollera text och bilder, godkänn och slå ihop
förslaget till **main** för att publicera. Samma krav på Copilot-behörighet och
granskning som för schemaändringar gäller här.

Lämna publiceringsdatum tomt för publicering så snart förslaget är granskat.
För ett framtida datum behöver en ansvarig person vänta med sammanslagningen;
webbplatsen har ingen automatisk tidsinställd publicering.

## Ändra schemat utan att redigera filer

1. Öppna fliken **Issues** på GitHub, välj **New issue** och sedan
   **Ändra träningsschema**.
2. Beskriv ändringen med vanliga ord: vilken grupp, vilka tider eller vilket
   datum och när ändringen ska gälla. Du behöver inte kunna YAML eller kod.
3. En person med rätt behörighet tilldelar ärendet till **Copilot**.
   Detta kräver att Copilot coding agent är tillgänglig och aktiverad för
   kontot/organisationen; formuläret startar inte agenten automatiskt.
4. Copilot förbereder ett ändringsförslag (pull request) med en sammanfattning.
   Kontrollera att grupper, tider och datum är rätt. Besvara eventuella frågor
   i ärendet eller ändringsförslaget.
5. En ansvarig person godkänner och slår ihop förslaget till **main**.
   GitHub Actions bygger och publicerar sedan webbplatsen.

Samma schemauppgifter används på startsidan, Schema och Börja träna. Ändringar
behöver därför bara beskrivas en gång. Publiceringen sker vid sammanslagning,
inte automatiskt på ett framtida startdatum. Om ändringen ska publiceras senare
behöver sammanslagningen planeras av en ansvarig person.

## Editing pages

GitHub Copilot agents follow
[`.github/copilot-instructions.md`](.github/copilot-instructions.md) for
repository-wide editing rules. Keep enduring conventions there; put the exact
requested wording, dates, affected pages and acceptance criteria in the GitHub
issue assigned to the agent. Update these instructions when the site's content
structure or editing workflow changes.

Edit the relevant file in `_club_pages/`: text, headings, links, images and
tables use Markdown, not separate HTML content files. Keep the YAML frontmatter
at the top; `title` controls the heading and `permalink` controls the URL.
News articles are in `_club_pages/nyheter/` and grading posts are in
`_club_pages/graderingar/`. Both use `YYYY-MM-DD-title.md` filenames based on
the publication date. Their `permalink` values keep the existing public URLs
unchanged. The news/document index is `nyheter.md`, available at `/nyheter/`.
Alingsåslägret pages are grouped in `_club_pages/alingsaslagret/`, with
`index.md` for the overview and year filenames such as `2004.md`.

The homepage is `index.md`: its YAML frontmatter contains hero, navigation and
contact text, and its Markdown body contains the schedule section. Shared
markup lives in `_layouts/` and `_includes/` to preserve the responsive design.
Navigation, schedules, document lists and sponsor details live in `_data/`.
The calendar link opens Google Calendar instead of embedding an HTML iframe.

When maintaining an imported page, add `maintained_content: true` to its
frontmatter to prevent future imports from overwriting your edits.
`_data/excluded_archive_pages.yml` lists removed source page IDs that must not be
restored by future imports.

To repeat the content migration using a completed archive:

```sh
make import
# Or choose another completed archive:
make import ARCHIVE=_old_site/<timestamp-directory>
make build
make import-test
```

The importer preserves the existing club routes and converts WordPress links
to local pages and assets. Re-importing replaces generated page bodies and
metadata unless `maintained_content: true` is set. It does not restore WordPress
plugins, authentication or source theme scripts.
The import check compares original text, image and table counts on unedited
pages, verifies media copies, and checks all generated local links and shared
schedule displays. Maintained pages are excluded from source-content comparisons.

## Updating training times

Set `term_start.date` in `_data/training_schedule.yml` to the term start date
as quoted display text, for example `"15 januari 2027"`. It appears under
“Terminsstart” wherever the shared schedule is displayed. An empty date shows
“Datum meddelas snart.” instead of assuming a date.

Add schedule exceptions under `exceptions` in the same file, with a quoted
`date` in `YYYY-MM-DD` format and a `reason`, for example `Höstlov`.
They appear in date order under “Avvikelser i träningsschemat” on every page
using the schedule. Dates remain visible until removed, including past dates.
Set `exceptions: []` to hide the section.

Edit `_data/training_schedule.yml` to change group names, ages, weekdays and
training times. Keep `start` and `end` quoted so YAML treats them as strings.
`_includes/training-schedule.html` renders this shared data on the homepage,
Schema and Börja träna pages. To display it elsewhere, use
`{% include training-schedule.html %}` beneath a suitable heading.

The current schedule is separate from the historical schedule on Schema.
Börja träna shows the current groups and links to the fee page, without the old
beginner information. Both pages use `maintained_content: true` so `make import`
preserves their edited Markdown content.

## Archive the public source site

```sh
make scrape
```

This builds a separate Playwright container and visits public same-site links
with ordinary Chromium. It does not access administration pages, authenticate,
use stealth plugins, solve CAPTCHAs, or retry an ongoing access block. Requests
are sequential with a two-second pause between pages.

Each run creates a timestamped directory inside `_old_site/`, leaving previous
archives untouched. It saves rendered HTML, loaded images/backgrounds/fonts/CSS,
linked same-site documents (including PDFs, Word and Excel files), and
`manifest.json`. Page and asset links are rewritten
to local files; external links are retained. Scripts are removed from saved
HTML, so this is a content archive for migration, not a working WordPress clone.
Only pages reachable through public links are discovered; unlinked pages and
private instructor material require an authorized export.

The command exits with an error for blocked pages, failed assets, or a partial
crawl. Dead source links (404/410) are logged in `brokenLinks` and do not stop
the crawl. Inspect the manifest and `last-page.html` / `last-page.png` for the
failure details. If ordinary browser loading still fails, request an export or
scraper allowlisting from the hosting provider.

To adjust the source or crawl limits:

```sh
SOURCE_URL=https://alingsasju-jutsu.se/ MAX_PAGES=500 DELAY_MS=2000 make scrape
make scrape-test
```

A partial archive with a saved queue can be resumed in place:

```sh
RESUME_ARCHIVE=/archive/<timestamp-directory> make scrape
```
