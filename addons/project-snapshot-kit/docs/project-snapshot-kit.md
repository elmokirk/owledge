# Project Snapshot Kit

Project Snapshot Kit is an optional Owledge add-on for projects that need a
local project cockpit without making dashboard output canonical memory.

## What It Adds

- reusable Markdown snapshots under `agent-memory/compiled/`
- a project snapshot profile under `agent-memory/project-snapshot/`
- a durable planning folder under `agent-memory/plans/`
- static HTML reports under `agent-memory/reports/project-site/`
- source-hash and token-estimate metadata in a generated manifest

## Rules

- Installing the add-on copies templates and profile files only.
- Generating snapshots or HTML requires explicit user confirmation in
  interactive mode or `--yes` in scripted mode.
- HTML is generated from Markdown snapshots and local indexes.
- Raw runtime logs are never loaded into reports.
- External issue systems are future adapters; MVP task status is Owledge-local.

## Token Model

The CLI is deterministic and does not call a model. Token costs are estimates
for future agent-authored narrative refreshes:

| Operation | Estimated model tokens |
| --- | ---: |
| Install add-on | 0 |
| Render HTML from snapshots | 0 |
| Deterministic task/status refresh | 0 |
| Incremental narrative refresh | 3k-12k input, 1k-3k output |
| First medium-project snapshot | 15k-35k input, 4k-8k output |
| Large full-site narrative refresh | 40k input default cap |

Use `--token-budget` and `--allow-large-context` to make large refresh intent
explicit.
