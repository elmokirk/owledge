# Agent Memory Map Contract

Use `agent-memory-map.json` when a user wants Agent Memory principles applied to
an existing vault structure instead of the default `agent-memory-module/` folder.

## Example

```json
{
  "ideas": "01_Inbox/Ideas",
  "plans": "20_Projects/Plans",
  "evidence": "30_Research/Evidence",
  "handoffs": "40_Agent-Handoffs",
  "reviews": "50_Reviews",
  "indexes": ".agent-memory/indexes"
}
```

## Rules

- All paths are relative to the knowledgebase root.
- Absolute paths are invalid.
- `..` path segments are invalid.
- Targets must already exist as directories.
- Symlinks and junctions are invalid for write targets.
- Writes must stay inside the resolved knowledgebase root.
- Missing map: use `agent-memory-module/` fallback.
- Invalid map: fail closed and ask the user to fix the map.

## Minimum Keys

Required:

- `plans`
- `evidence`
- `handoffs`
- `reviews`
- `indexes`

Optional:

- `ideas`
- `tasks`
- `scratch`

## Agent Behavior

- Read from the broader vault only as needed.
- Write only to mapped locations.
- Keep generated indexes in the mapped `indexes` folder.
- Do not create new mapped folders unless the user asks.
