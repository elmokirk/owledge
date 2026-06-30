---
name: personal-pi-agent
description: Use when a PI Agent should manage private global user knowledge: preferences, goals, daily work, ideas, research freshness, personal patterns, and coach reports.
---

# Personal PI Agent

## When To Use

Use this skill when the user asks for help with personal knowledge continuity, goals, daily execution, idea triage, research freshness, recurring patterns, or proactive coaching across projects.

## Core Rule

Personal PI findings are candidate knowledge. Do not overwrite `USER_CONTEXT.md`, project canonical memory, or shared lessons without explicit user review.

## Read Order

1. `USER_CONTEXT.md`
2. `global-memory/preferences/`
3. `global-memory/goals/`
4. `global-memory/ideas/`
5. `global-memory/research/`
6. `global-memory/patterns/`
7. Active project `OWLEDGE.md` and project memory when relevant

Use `global-memory/daily/`, `global-memory/tasks/`, and onboarding profiles only for explicit deep dives.

## Write Targets

| Path | Purpose |
| --- | --- |
| `global-memory/ideas/` | Cross-project ideas and opportunity drafts |
| `global-memory/patterns/` | Personal pattern candidates |
| `global-memory/coach/` | Sourced coach reports with next actions |

## Quality Bar

- Cite source memory IDs and paths.
- Mark confidence and stale sources.
- Preserve contradictions; do not flatten them.
- Prefer deterministic signals before semantic similarity.
- Never export private daily notes, personal tasks, onboarding profiles or raw preference drafts to shared RAG.

