# Website editing instructions

This is Alingsås Ju-Jutsuklubb's Swedish-language Jekyll site, published with
GitHub Pages at https://alingsasju-jutsu.se. Read README.md for editing and
local development commands. Use the assigned issue or request for the specific
content changes; preserve unrelated content and design.

## Working with non-technical editors

- Accept requests in ordinary Swedish or English. Editors do not need to name
  files, supply YAML, or explain Jekyll. Locate and update the right source.
- For schedule requests, read `_data/training_schedule.yml`, apply only the
  requested changes, and preserve all unspecified groups, sessions, term start
  and exceptions. Never treat example text in an issue form as actual instructions.
- Distinguish recurring time changes from dated exceptions. Do not infer that
  an exception cancels every group unless the request says so.
- If dates, affected groups, times or effective periods are ambiguous, ask one
  focused plain-language question in the issue and do not guess or merge an
  incomplete change. An unanswered question is a blocker, not approval.
- There is no scheduled publishing or date-effective recurring timetable
  mechanism. Merging publishes the configured recurring times immediately.
  If a request calls for future publication or temporary recurring times,
  explain this limitation and agree on the approach before replacing current
  times. Do not promise automatic activation or reversion.
- Use a clear Swedish pull request title. Describe the before/after changes
  and affected groups in everyday language, including dates for exceptions.
  Explain that schedule data is shared by Startsidan, Schema and Börja träna.
  Avoid making the editor inspect a code diff to understand the result.
- State any remaining decision needed. Do not merge or publish unless explicitly
  authorized; prepare a pull request for a maintainer to review.

## Adding news from an issue

- The "Publicera en nyhet" form is intended to be as easy as sending an email.
  Accept finished text or notes. Propose a short Swedish headline and readable
  Markdown without asking the editor about filenames, frontmatter or slugs.
  Preserve the facts and intent; do not invent quotes, results or event details.
- Create one Markdown page in `_club_pages/nyheter/`, or
  `_club_pages/graderingar/` for grading news. News without images is allowed;
  grading photo galleries require available photos. A text-only grading
  announcement is not a photo gallery.
- Use the explicitly supplied publication date, or the current date when the
  editor asks to publish as soon as reviewed. Do not confuse an event date in
  the body with the publication date. Use `YYYY-MM-DD-title.md` filenames with
  a lowercase ASCII slug (å/ä → a, ö → o). Use `/nyheter/YYYY-MM-DD-slug/`
  as the permalink for new articles; preserve URLs of existing articles.
- Set `title`, `category: Nyheter`, `news: true`, `grading` (boolean),
  `published_label` (for example `3 november 2026`) and `published_sort`
  (for example `"20261103"`). Do not assign a made-up author; omit
  `source_author` unless supplied. New content needs no legacy source metadata.
- Download supplied issue images into `assets/images/nyheter/<date>-<slug>/`
  using descriptive filenames and Markdown alt text. Only retrieve images
  explicitly supplied for publication; never use external upload services or
  commit credentials. If an attachment cannot be retrieved, report that and
  request an accessible copy rather than silently dropping it.
- The `/nyheter/` index updates automatically through `news: true`. For a
  grading post, also add an appropriate local link to the Graderingar overview
  when it belongs in that gallery list; keep `maintained_content: true` there.
- Do not add scheduling infrastructure or promise future automatic publication.
  For a future publication request, prepare the draft pull request and explain
  that a maintainer must merge it at the intended time.
- In the pull request, show the proposed headline, publication date, public URL
  and whether images were included. Make it easy to review the Swedish text
  without reading the raw diff. Build and verify that the article is included
  in the news index and its links and images resolve.

## Content locations

- `index.md`: homepage text and YAML frontmatter. `_layouts/home.html` supplies
  the visual structure; do not copy that markup into the Markdown.
- `_club_pages/**/*.md`: directly editable page bodies, including Markdown
  headings, tables, links and images. Keep raw HTML out of content files;
  reuse Liquid includes for shared components.
- `_club_pages/nyheter/`: news posts named `YYYY-MM-DD-title.md`.
- `_club_pages/graderingar/`: grading posts with the same dated filename format.
- `_club_pages/alingsaslagret/`: `index.md` for the camp overview and year files
  such as `2004.md`. Preserve the Läger → Alingsåslägret → year navigation.
- `_club_pages/nyheter.md`: the `/nyheter/` index. It automatically lists pages
  with `news: true`; do not maintain a second manual list.
- `_data/navigation.yml`: shared menus.
- `_data/training_schedule.yml`: the single source for training group names,
  ages, recurring sessions, term start and exceptions. Never duplicate current
  schedule values in page text. Keep dates and times quoted. Exceptions use
  `YYYY-MM-DD` dates and a `reason`; they remain visible until explicitly removed.
- `_layouts/`, `_includes/`, `assets/css/main.scss`: shared presentation.
  Change these only when the task needs a layout or component change.
- `assets/`: local images and documents. Reuse existing assets where possible.

## Editorial rules

- Write public content in Swedish with correct spelling and diacritics.
- Use only supplied or verified facts. Do not invent dates, fees, contacts,
  cancellations, qualifications or event details. If a necessary fact is
  missing, request clarification or state the blocker rather than guessing.
- Preserve existing `permalink` values when moving or renaming files. Article
  URLs under `/arkiv/<id>/` are still intentional even though the index is
  called Nyheter. Do not silently change URLs.
- Preserve relevant frontmatter. New news posts need `news: true`,
  `published_label` (Swedish display date), `published_sort` (quoted `YYYYMMDD`)
  and a unique `permalink`. Set `grading: true` for grading posts and `false`
  for other news. Do not invent legacy `source_id` or `source_date` values.
- Mark edited imported pages with `maintained_content: true`, including news
  posts, so future imports do not overwrite editorial changes.
- Keep old news dated and historical events distinct from current schedules.
  Do not add visitor-facing scraping or migration notices.
- Keep internal links local, using `relative_url`, for example
  `[Träningsavgifter]({{ '/traning/traningsavgifter/' | relative_url }})`.
  Do not link back to old WordPress pages or hotlink their images.
- Use descriptive image alt text. Do not create grading galleries without
  available photos. Do not restore the removed login page or pages listed in
  `_data/excluded_archive_pages.yml`.
- The Börja träna page must show the shared current schedule and link to
  Träningsavgifter, without restoring its old beginner-information section.

## Scope and validation

- Never edit generated `_site/` output. Do not run `make import` or `make scrape`
  for routine content edits: imports can overwrite unprotected editorial work,
  and the ignored `_old_site/` archive may not exist on GitHub runners.
- For site/content changes, run `make build` with Docker. Alternatively, with
  the repository's Ruby/Bundler dependencies installed, run
  `bundle exec jekyll build`, as the deployment workflow does.
- Check the build output for Liquid/YAML errors, not just the exit code.
  Inspect affected generated pages for the requested wording, links, images
  and dates. For shared schedule changes, check the homepage, Schema and
  Börja träna. For layout changes, check mobile and desktop rendering.
- Run `make import-test` only when the completed source archive is available.
  It checks original content on unmaintained pages plus local links and shared
  schedules. Mark intentionally edited imported pages as maintained rather than
  weakening comparisons to accommodate editorial changes.
- Run `make scrape-test` if changing the browser archiver. Documentation-only
  edits do not require a site build.
- In the pull request, summarize the content changed, list validation actually
  performed, and plainly report anything that could not be verified.
