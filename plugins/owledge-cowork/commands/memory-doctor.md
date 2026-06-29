---
description: Diagnose Owledge installation, contracts, schemas, hooks, privacy posture, and adapter readiness.
---

Run a read-only diagnostic pass for the current host project.

Prefer:

```bash
python tools/owledge.py doctor --project-root .
python tools/owledge_core.py --project-root . test-contracts
```

If local tools are missing, ask for the Owledge repo checkout path and use it
explicitly.

Inspect and report:

- missing host files
- validation failures
- hook script reachability
- raw `events.jsonl` privacy posture
- unsafe shared records
- missing `DESIGN.md`
- whether `.gitignore` excludes raw runtime events

Do not run build, export, compact, promote, or report commands unless the user
explicitly asks for repair or output generation.
