---
description: Show read-only Owledge status for the current host project.
---

Inspect the current project as an Owledge workspace without creating,
modifying, exporting, compacting, or promoting files.

Run read-only checks from the project root:

```bash
python tools/agent_memory_cli.py --project-root . validate-memory --strict
python tools/owledge.py doctor --project-root .
```

Then inspect these folders directly:

- `agent-memory/sessions/`
- `agent-memory/compiled/`
- `agent-memory/exports/`

Report:

- current project root
- latest session folders under `agent-memory/sessions/`
- draft compiled summaries under `agent-memory/compiled/`
- validation status
- existing export artifact timestamps if present
- any private/confidential artifacts that must not be shared
