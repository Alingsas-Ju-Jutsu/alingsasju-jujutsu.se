# Website editing instructions

This is Alingsås Ju-Jutsuklubb's Swedish-language Jekyll site, published with
GitHub Pages at https://alingsasju-jutsu.se. Read README.md for editing and
local development commands. Use the assigned issue or request for the specific
content changes; preserve unrelated content and design.

## Working with non-technical editors

- Accept requests in ordinary Swedish or English. Editors do not need to name
  files, supply YAML, or explain Jekyll. Locate and update the right source.
- For schedule requests, read `_data/groups.yml`, apply only the
  requested changes, and preserve all unspecified groups, sessions, term start
  and exceptions. Never treat example text in an issue form as actual instructions.
- Distinguish recurring time changes from dated exceptions. Do not infer that
  an exception cancels every group unless the request says so.
- If dates, affected groups, times or effective periods are ambiguous, ask one
  focused plain-language question in the issue and do not guess or merge an
  incomplete change. An unanswered question is a blocker, not approval.
- There is no scheduled publishing or date-effective recurring timetable
  mechanism. Merging into `main` publishes the configured recurring times immediately.
  If a request calls for future publication or temporary recurring times,
  explain this limitation and agree on the approach before replacing current
  times. Do not promise automatic activation or reversion.
- Use a clear Swedish change summary. Describe the before/after changes
  and affected groups in everyday language, including dates for exceptions.
  Explain that schedule data is shared by Startsidan, Schema and Börja träna.
  Avoid making the editor inspect a code diff to understand the result.
- Commit and push changes to the task's branch and prepare a pull request
  targeting `main`. GitHub's Copilot coding agent cannot push directly to
  `main` or approve and merge its own pull request. Do not retry direct pushes,
  bypass restrictions, change branch protection or force-push.
- Explain the remaining publishing step in plain language: a maintainer reviews
  and merges the pull request; GitHub Actions then publishes the website.
- State any remaining decision needed before publishing an ambiguous request.

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
  For a future publication request, prepare a
  draft pull request and explain that a maintainer must merge it at the intended time.
- In the completion summary, show the headline, publication date, public URL
  and whether images were included. Make it easy to review the Swedish text
  without reading the raw diff. Ensure `news: true` is set so the index includes
  the article, and check link paths and image filenames in the source files.

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
- `_data/groups.yml`: the single source for training group names,
  ages, recurring sessions, term start and exceptions. Never duplicate current
  schedule values in page text. Keep dates and times quoted. Exceptions use
  `YYYY-MM-DD` dates and a `reason`; they remain visible until explicitly removed.
- `_layouts/`, `_includes/`, `assets/css/main.scss`: shared presentation.
  Change these only when the task needs a layout or component change.
- `assets/`: local images and documents. Reuse existing assets where possible.

## Editorial rules

- Write public content in Swedish with correct spelling and diacritics.
- Add a concise, factual Swedish `description` to new pages for search results.
  New news posts also need a quoted ISO `date` (`YYYY-MM-DD`) matching the
  publication date and `seo: { type: BlogPosting }`.
- Keep heading levels logical: the layout supplies the only `h1`, so start
  Markdown sections at `##` and do not skip levels. Give Markdown tables
  meaningful column headers and images useful alt text. Essential text must
  also be readable outside images; do not publish text-only posters as the
  sole source of instructions.
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
- The Schema poster is generated from `_data/groups.yml` during
  deployment. Do not edit the old poster or commit `assets/generated/`;
  change the shared YAML to update the poster's date and training times.
- Edit instructor names, portrait paths and optional descriptions in
  `_data/instructors.yml`. Keep their cards in `_includes/instructors.html`;
  use portrait photos without baked-in names or grades, not poster images.

## Lightweight content workflow

- For routine news, page text or schedule updates, edit or create the Markdown,
  shared YAML data and supplied image files, then commit and push to the task's
  branch/pull request targeting `main`. Commit only files relevant to the
  request and report that a maintainer must review and merge to publish.
- Do not run Docker, install dependencies, build Jekyll, start a preview server,
  or run test suites for routine content edits. GitHub Actions builds and
  deploys the site after the change reaches `main`.
- Review the edited source for correct wording, dates, YAML indentation,
  required frontmatter, existing local paths and the requested scope. This
  should not require setting up a development environment.

- Never edit generated `_site/` output. Do not run `make import` or `make scrape`
  for routine content edits: imports can overwrite unprotected editorial work,
  and the ignored `_old_site/` archive may not exist on GitHub runners.
- Changes to layouts, components, CSS, workflows or tooling are development
  tasks, not routine content edits. Use relevant build or tests for those
  changes; see README.md for available commands.
- In the completion summary or pull request, summarize the content changed, list validation actually
  performed, and do not claim a build or tests ran when they did not.
