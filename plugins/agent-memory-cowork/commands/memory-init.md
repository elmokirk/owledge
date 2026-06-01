---
description: Initialize Agent Memory in the host project without overwriting existing memory.
---

Bootstrap the current repository as an Agent Memory host project.

Before running anything, inspect whether these exist:

- `PROJECT_CONTEXT.md`
- `AGENTS.md`
- `CLAUDE.md`
- `DESIGN.md`
- `agent-memory/`
- `tools/agent_memory_cli.py`

If the project already has Agent Memory, do not overwrite it. Prefer an explicit kit path when the user provides one:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\AgentMemoryKit\tools\bootstrap-agent-memory.ps1" -ProjectRoot . -KitRoot "C:\AgentMemoryKit"
```

If `AGENT_MEMORY_KIT_ROOT` is set, this equivalent command also works:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:AGENT_MEMORY_KIT_ROOT\tools\bootstrap-agent-memory.ps1" -ProjectRoot . -KitRoot "$env:AGENT_MEMORY_KIT_ROOT"
```

If the local tools folder already exists, this also works because `init-agent-memory.ps1` delegates to bootstrap when it can resolve the kit root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\init-agent-memory.ps1 -ProjectRoot . -KitRoot "$env:AGENT_MEMORY_KIT_ROOT"
```

After init, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\memory-doctor.ps1 -ProjectRoot .
```

macOS/Linux project-folder-only setup:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

From inside an initialized project:

```bash
bash tools/memory-doctor.sh --project-root .
```

Report what was created, what already existed, and what the user must still fill in manually.
