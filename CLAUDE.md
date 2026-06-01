---
title: "Global Agent Memory Kit Instructions"
date: "2026-05-13"
version: "0.4.0"
status: "active"
type: "global-kit-instructions"
---

# Global Agent Memory Kit Instructions

This repository can be used as a global Agent Memory Kit.

## Session Start Rule

At the beginning of every agent session:

1. Check whether the current repo has:
   - `PROJECT_CONTEXT.md`
   - `USER_CONTEXT.md` when personal/global context is used
   - `AGENTS.md`
   - `CLAUDE.md`
   - `DESIGN.md`
   - `agent-memory/`
   - `global-memory/` when the private user layer is enabled
   - `tools/agent_memory_cli.py`
2. If anything is missing in a host project, use the `bootstrap-agent-memory` skill.
3. Prefer project-local tools when `tools/agent_memory_cli.py` exists. Otherwise bootstrap from an explicit `-KitRoot`; `AGENT_MEMORY_KIT_ROOT` is only a convenience fallback.
4. Do not overwrite existing project memory unless the user explicitly asks for force/overwrite.
5. In this kit repository, use `tools\memory-doctor.ps1 -ProjectRoot .` on Windows or `python3 tools/agent_memory_cli.py --project-root . doctor --mode kit` on macOS/Linux.

## Global vs Project Local

| Layer | Location | Purpose |
| --- | --- | --- |
| Global kit | explicit `-KitRoot` or optional `AGENT_MEMORY_KIT_ROOT` | Templates, tools, skills, plugins |
| Global skills | `.claude/skills`, `.codex/skills` | Agent behavior and bootstrap rules |
| Global user context | `USER_CONTEXT.md` | Private user profile, preferences, goals, and agent collaboration defaults |
| Global user memory | `global-memory/` | Private preferences, goals, daily notes, tasks, ideas, research, patterns, and coach reports |
| Project memory | active repo | Durable project truth |
| PI intelligence | `agent-memory/pi-agent/` | Candidate parallels, trends, recurring errors, and central project ideas |
| PI red team | `agent-memory/pi-agent/red-team/` | 1-100 scorecards and challenge reports |
| Enterprise hub | optional central vault | Reviewed cross-project aggregation |

## Bootstrap Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\AgentMemoryKit\tools\bootstrap-agent-memory.ps1" -ProjectRoot . -KitRoot "C:\AgentMemoryKit"
```

Project-folder-only macOS/Linux setup:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

## Core Rule

Global plugins and skills are runtime bridges. Project-local Markdown is the source of truth for projects. `USER_CONTEXT.md` and `global-memory/` are private user-level context and must not override project decisions.

PI Agent intelligence and Red Team evaluations are candidate artifacts. They can guide planning and curator review, but they do not become canonical memory without explicit promotion.

Daily notes, personal tasks, onboarding profiles, and private user preferences are not shared RAG input by default.
