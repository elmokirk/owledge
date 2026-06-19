# Project Snapshot Kit

Project Snapshot Kit is an optional Owledge add-on for reusable project
orientation, local planning status, and static HTML project cockpit pages.

It is not installed with the core kit. Install it only when a project should
generate dashboard-style views from existing Owledge memory.

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon project-snapshot-kit
```

## Generate

Interactive mode asks before writing snapshots or HTML pages:

```bash
python tools/owledge.py project-snapshot --project-root .
```

Scripted mode must be explicit:

```bash
python tools/owledge.py project-snapshot --project-root . --yes
python tools/owledge.py project-snapshot --project-root . --snapshots-only
python tools/owledge.py project-snapshot --project-root . --render-html
```

`--render-html` renders from existing Markdown snapshots and fails if they are
missing. Use `--yes` for a single scripted run that updates snapshots and HTML.

## Outputs

| Path | Purpose |
| --- | --- |
| `agent-memory/compiled/project-story-snapshot.md` | Pitch, problem, painpoints, workflows, features, and status |
| `agent-memory/compiled/project-execution-snapshot.md` | MVP, out-of-MVP scope, local tasks, blockers, QA, and activity |
| `agent-memory/reports/project-site/` | Static generated HTML pages |
| `agent-memory/project-snapshot/project-snapshot-manifest.json` | Generated source hashes, skipped files, and token estimates |

## Token Behavior

The CLI path is deterministic and uses zero model tokens. It estimates future
agent-authored refresh costs in the manifest:

- normal refresh budget: `12000` input tokens
- full-site refresh budget: `40000` input tokens
- larger budgets require `--allow-large-context`

HTML rendering from existing snapshots is zero-token.
