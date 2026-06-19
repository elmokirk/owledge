# Execution Dashboard

Use when the optional Project Snapshot Kit add-on is installed and the user
wants a compact implementation dashboard for MVP, roadmap, tickets, blockers,
QA gates, and latest agent activity.

## Sources

Prefer:

- `agent-memory/compiled/project-execution-snapshot.md`
- `agent-memory/project-snapshot/project-snapshot-manifest.json`
- Owledge-local TaskCard, WorkPackage, EpicOverview, plans, handoffs, and evidence

## Sections

| Section | Purpose |
| --- | --- |
| MVP | Smallest useful scope |
| Out of MVP | Explicit cutline |
| Workstreams | Active implementation areas |
| Task status | Deterministic local ticket counts |
| Blockers | Current blocked work and risks |
| QA gates | Required validation |
| Agent activity | Recent handoffs and evidence summaries |

## Rules

- Keep task/status tables deterministic and zero-token.
- Use narrative summaries only from stored snapshots.
- Include source hashes and generated timestamp.
