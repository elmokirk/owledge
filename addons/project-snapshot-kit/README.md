# Project Snapshot Kit Add-on

Optional project cockpit layer for Owledge.

This add-on is intentionally not part of the default project kit. Install it
only when a project should generate reusable orientation snapshots, pitch
summaries, workflow maps, MVP/roadmap views, local task status, and static HTML
pages.

Markdown remains the source of truth. HTML pages and manifests are generated
views.

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon project-snapshot-kit
```

## Generate

Interactive mode asks before writing snapshots or HTML:

```bash
python tools/owledge.py project-snapshot --project-root .
```

Non-interactive examples:

```bash
python tools/owledge.py project-snapshot --project-root . --yes
python tools/owledge.py project-snapshot --project-root . --snapshots-only
python tools/owledge.py project-snapshot --project-root . --render-html
```

`--render-html` renders from existing Markdown snapshots. Use `--yes` for a
single scripted run that updates snapshots and renders HTML.

The file copy contract for this add-on lives in `addon.json`.
