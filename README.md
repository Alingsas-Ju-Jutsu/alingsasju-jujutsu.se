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

The homepage and local subpages use the archived site's logo, desktop/mobile
hero photos, club address, contact details, social links, and navigation. All
club navigation links point to pages on this site. The completed public archive
has been migrated into 25 club subpages and 60 dated news pages, available from
`/arkiv/`. Fees, contacts, rules, instructor posters, schedules, statutes,
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

## Editing pages

Edit the relevant file in `_club_pages/`: text, headings, links, images and
tables use Markdown, not separate HTML content files. Keep the YAML frontmatter
at the top; `title` controls the heading and `permalink` controls the URL.
News articles are in `_club_pages/nyheter/` and grading posts are in
`_club_pages/graderingar/`. Both use `YYYY-MM-DD-title.md` filenames based on
the publication date. Their `permalink` values keep the existing public URLs
unchanged. The news/document index is `nyhetsarkiv.md`.

The homepage is `index.md`: its YAML frontmatter contains hero, navigation and
contact text, and its Markdown body contains the schedule section. Shared
markup lives in `_layouts/` and `_includes/` to preserve the responsive design.
Navigation, schedules, document lists and sponsor details live in `_data/`.
The calendar link opens Google Calendar instead of embedding an HTML iframe.

When maintaining an imported page, add `maintained_content: true` to its
frontmatter to prevent future imports from overwriting your edits.
`_data/excluded_archive_pages.yml` lists removed news IDs that must not be
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
