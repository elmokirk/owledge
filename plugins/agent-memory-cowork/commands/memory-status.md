---
description: Show read-only Agent Memory status for the current host project.
---

Inspect the current project as an Agent Memory workspace without creating, modifying, building, exporting, compacting, or promoting files.

Run read-only checks from the project root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\validate-memory.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File tools\memory-doctor.ps1 -ProjectRoot .
Get-ChildItem agent-memory\sessions -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name,LastWriteTime
Get-ChildItem agent-memory\compiled -File -Filter *.md -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 10 Name,LastWriteTime
Get-ChildItem agent-memory\exports -Recurse -File -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime
```

Report:

- current project root
- latest session folders under `agent-memory/sessions/`
- draft compiled summaries under `agent-memory/compiled/`
- validation status
- existing RAG/LightRAG export artifact timestamps if present
- any private/confidential artifacts that must not be shared
