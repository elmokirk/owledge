---
title: "Global Agent Memory Kit Instructions"
date: "2026-05-13"
version: "0.6.0"
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
3. Prefer project-local Python tools when `tools/agent_memory_cli.py` exists. Otherwise initialize from an explicit local Owledge checkout.
4. Do not overwrite existing project memory unless the user explicitly asks for force/overwrite.
5. Repo layout:
   - `templates/agent-memory/` is the pristine product source (shipped to users via `init-project` and `build-project-kit`).
   - `internal/agent-memory/` is the maintainers' live dogfood workspace (decision traces, compiled snapshots, indexes, exports, benchmarks).
   - For product health checks: `python tools/agent_memory_cli.py --project-root . doctor --mode kit`
   - For dogfood gates: `python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports` (the function auto-detects `internal/agent-memory/` for memory operations)
   - Never write generated artifacts (decision traces, compiled snapshots, indexes, exports) into `templates/`. That directory is the shipped product source.

## Global vs Project Local

| Layer | Location | Purpose |
| --- | --- | --- |
| Global kit | explicit local Owledge checkout | Templates, tools, skills, plugins |
| Global skills | `.claude/skills`, `.codex/skills` | Agent behavior and bootstrap rules |
| Global user context | `USER_CONTEXT.md` | Private user profile, preferences, goals, and agent collaboration defaults |
| Global user memory | `global-memory/` | Private preferences, goals, daily notes, tasks, ideas, research, patterns, and coach reports |
| Project memory | active repo | Durable project truth |
| PI intelligence | `agent-memory/pi-agent/` | Candidate parallels, trends, recurring errors, and central project ideas |
| PI red team | `agent-memory/pi-agent/red-team/` | 1-100 scorecards and challenge reports |
| Enterprise hub | optional central vault | Reviewed cross-project aggregation |

## Bootstrap Command

```bash
python tools/owledge.py init-project --target /path/to/project --include-plugin-adapter
```

Project-folder-only setup:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/agent-memory-project-kit --verify
```

## Core Rule

Global plugins and skills are runtime bridges. Project-local Markdown is the source of truth for projects. `USER_CONTEXT.md` and `global-memory/` are private user-level context and must not override project decisions.

PI Agent intelligence and Red Team evaluations are candidate artifacts. They can guide planning and curator review, but they do not become canonical memory without explicit promotion.

Daily notes, personal tasks, onboarding profiles, and private user preferences are not shared RAG input by default.

## Session Continuity

When working from a multi-phase plan with per-phase checklists, resume from the first unchecked box. Do not restart completed phases. If a session breaks mid-phase, re-run that phase's QA gate before continuing; if it fails, uncheck the box and redo the phase. Subagents check their own boxes before returning to the orchestrator. The checkbox is a navigation aid; the phase's QA gate output is the durable evidence.
