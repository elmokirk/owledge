---
name: bootstrap-agent-memory
description: Initialize Agent Memory automatically at session start or when a repo lacks PROJECT_CONTEXT.md, AGENTS.md, CLAUDE.md, DESIGN.md, tools, or agent-memory. Use for Claude/Cowork and Codex first-run project setup from an explicit or global Agent Memory Kit path.
---

# Bootstrap Agent Memory

At session start, check for `USER_CONTEXT.md` when global user memory is enabled, `PROJECT_CONTEXT.md`, `AGENTS.md`, `CLAUDE.md`, `DESIGN.md`, `agent-memory/`, `global-memory/`, and `tools/agent_memory_cli.py`.

If anything is missing, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\AgentMemoryKit\tools\bootstrap-agent-memory.ps1" -ProjectRoot . -KitRoot "C:\AgentMemoryKit"
```

If `AGENT_MEMORY_KIT_ROOT` is set, this equivalent command also works:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:AGENT_MEMORY_KIT_ROOT\tools\bootstrap-agent-memory.ps1" -ProjectRoot .
```

macOS/Linux users can generate a project-local folder without environment
variables:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

If no kit path is available, ask the user for the kit path once.

Never use `-Force` unless the user explicitly asks to overwrite existing files.

After bootstrap, read `USER_CONTEXT.md` when present, then `PROJECT_CONTEXT.md`, and use project-local `agent-memory/` as the project source of truth. Treat `USER_CONTEXT.md` and `global-memory/` as private user-level context and do not export daily notes, personal tasks, onboarding profiles, or private preferences to shared RAG.
