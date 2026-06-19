# Project Site

Use when the optional Project Snapshot Kit add-on is installed and the user
wants a static project cockpit, project website, pitch overview, workflow map,
implementation status, or source-backed stakeholder view.

## Sources

Prefer:

- `agent-memory/compiled/project-story-snapshot.md`
- `agent-memory/compiled/project-execution-snapshot.md`
- `agent-memory/project-snapshot/project-snapshot-manifest.json`
- `agent-memory/indexes/memory-index.jsonl`
- Owledge-local TaskCard, WorkPackage, EpicOverview, plans, handoffs, and evidence

## Sections

| Page | Purpose |
| --- | --- |
| `index.html` | Project status, pitch, focus, and next actions |
| `product.html` | Problem, users, painpoints, core value, and features |
| `workflows.html` | User, agent, and memory workflows |
| `implementation.html` | MVP, out-of-scope work, roadmap, and task status |
| `activity.html` | Agent activity from handoffs/evidence, not raw logs |
| `sources.html` | Source paths, hashes, memory IDs, and token estimates |

## Rules

- HTML is generated output and not canonical memory.
- Do not load raw runtime event logs.
- Render from existing snapshots when possible.
- Include source hashes and token-estimate metadata.
