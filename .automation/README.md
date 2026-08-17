# Student Materials Auto-Publish Workflow

Automatically publishes new student-facing course materials from Google
Drive to [art-of-telling.com](https://art-of-telling.com), and logs each
update to the "Media Kit Backlog" Notion database.

## How it works

1. **Watch folder**: the Google Drive folder named `Art of Telling`
   (id `10XE4eEIe1t6tsATlYgSq3KDrcM9UItBC`). Drop new student handouts,
   worksheets, or companion booklets here as PDFs.
2. **Student-only filter**: a file is published only if its name matches
   student-facing conventions (contains "Student", "Companion",
   "Handout", "Booklet", "Worksheet", or "Guide") AND does not match an
   instructor-only pattern (`_Brief_`, "Instructor", "Proposal",
   "Answer Key", "Teacher", "Private", "Draft", "WIP"). The
   `Art of Telling — Private Memoir Resources` Drive folder is never
   touched — nothing in it is ever considered for publishing.
3. **Public index**: `handouts.html` (linked from the homepage menu) —
   a clean, auto-generated index of every published item, grouped by
   session.
4. **Per-session sections**: any still-empty `HANDOUTS-sN` marker block
   on `s1.html`–`s10.html` (and the course-wide block on `index.html`)
   gets filled automatically. Marker blocks that already have
   hand-written content (like `s8.html`) are never touched.
5. **Media Kit Backlog**: every new publish or file update is logged to
   the Notion database
   [Media Kit Backlog](https://app.notion.com/p/9acc4aea26f64430bb017b13809b7fd9)
   so it's easy to see what's new when refreshing press/media materials.

## Running it

```bash
bash run_workflow.sh
```

This does everything except the final `git push` and the Notion write —
those two steps need live credentials attached to the calling shell, so
the scheduled task that invokes this script performs them directly
afterward using `notion_payload.json` and a plain `git push`.

## Files

- `sync_drive_to_site.py` — lists the Drive folder, filters for
  student-facing files, downloads anything new/changed, updates
  `handouts/manifest.json`, writes `new_publishes.json`.
- `generate_handouts_page.py` — rebuilds `handouts.html` from the
  manifest.
- `inject_session_markers.py` — fills empty per-session handout blocks.
- `log_to_notion.py` — turns `new_publishes.json` into a
  `notion-create-pages` payload for the Media Kit Backlog.
- `run_workflow.sh` — runs steps 1–3 above plus a local git commit.

## Manifest

`handouts/manifest.json` is the source of truth for "what's already
published." It's keyed by Drive file ID (falling back to the original
Drive filename) and stores an MD5 checksum so edited files under the
same name are correctly detected as updates rather than duplicates.

## Adding a new course/companion site to this same pattern

This workflow is specific to art-of-telling.com. To reuse it for another
Silver Current Press course site, copy this folder, change
`DRIVE_FOLDER_ID` / `EXCLUDED_FOLDER_IDS` in `sync_drive_to_site.py`,
`AOT_REPO_DIR`, and the Notion `DATA_SOURCE_ID` in `log_to_notion.py`.
