---
description: Diagnose Agent Memory installation, contracts, schemas, hooks, privacy posture, and adapter readiness.
---

Run a read-only diagnostic pass for the current host project.

Prefer:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\memory-doctor.ps1 -ProjectRoot .
python tools\agent_memory_cli.py --project-root . test-contracts
```

If local tools are missing, ask for the Owledge Kit path and use it explicitly:

```powershell
python "C:\AgentMemoryKit\tools\agent_memory_cli.py" --project-root . doctor
python "C:\AgentMemoryKit\tools\agent_memory_cli.py" --project-root . test-contracts
```

Inspect and report:

- missing host files
- validation failures
- hook script reachability
- raw `events.jsonl` privacy posture
- unsafe shared records
- missing `DESIGN.md`
- whether `.gitignore` excludes raw runtime events

Do not run build, export, compact, promote, or report commands unless the user explicitly asks for repair or output generation.
