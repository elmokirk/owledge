---
name: bootstrap-agent-memory
description: Initialize Agent Memory automatically at session start or when a repo lacks PROJECT_CONTEXT.md, AGENTS.md, CLAUDE.md, DESIGN.md, tools, or agent-memory. Use for global setup, project-local bootstrap, Claude/Codex first-run checks, and making a repo ready for Agent Memory without manual copy-paste.
---

# Bootstrap Agent Memory

Use this skill at the beginning of a session when the project may not yet contain Agent Memory files.

## Session Start Check

1. Check the current repo for:
   - `USER_CONTEXT.md` when global user memory is enabled
   - `PROJECT_CONTEXT.md`
   - `AGENTS.md`
   - `CLAUDE.md`
   - `DESIGN.md`
   - `agent-memory/`
   - `global-memory/`
   - `tools/agent_memory_cli.py`
2. If all exist, continue with `PROJECT_CONTEXT.md`.
3. If any are missing, initialize from the global kit.

## Kit Root Resolution

Prefer an explicit kit path when the user or runtime provides one. The bootstrap script accepts `-KitRoot`, so a system-wide environment variable is not required.

Use `AGENT_MEMORY_KIT_ROOT` as a convenience fallback. If neither `-KitRoot` nor `AGENT_MEMORY_KIT_ROOT` is available, ask the user for the kit root once. Do not guess outside the current workspace.

## Preferred Bootstrap Command

Run from the target project:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\AgentMemoryKit\tools\bootstrap-agent-memory.ps1" -ProjectRoot . -KitRoot "C:\AgentMemoryKit"
```

Optional environment-variable equivalent:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:AGENT_MEMORY_KIT_ROOT\tools\bootstrap-agent-memory.ps1" -ProjectRoot .
```

macOS/Linux project-folder-only setup:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

Use `-Force` only when the user explicitly wants to overwrite existing Agent Memory files.

## After Bootstrap

1. Read `USER_CONTEXT.md` when present, then `PROJECT_CONTEXT.md`.
2. Run validation if needed:

```powershell
tools\validate-memory.ps1 -ProjectRoot .
tools\build-memory-index.ps1 -ProjectRoot .
```

3. Treat `agent-memory/` as the project-local source of truth.
4. Treat `USER_CONTEXT.md` and `global-memory/` as private user-level context, ignored by default in normal project repos.

## Safety Rules

- Do not overwrite existing project files unless the user asks for `Force`.
- Do not write raw runtime events into shared exports.
- Do not promote bootstrap-generated placeholder content as real project knowledge.
- Keep global skills/plugins separate from project-local memory.
- Do not export daily notes, personal tasks, onboarding profiles, or private preferences to shared RAG.
