---
name: owledge-planning-layer
description: Add Owledge's MVP-first planning, evidence, handoff, and context-hygiene layer on top of an existing project's own AGENTS.md, skills, hooks, or custom agent harness without replacing them.
version: 0.1.0
---

# Owledge Planning Layer

Use this skill when a user wants Owledge planning discipline inside an existing project that already has its own agent instructions, skills, hooks, Superpowers workflow, LLM wiki, Obsidian vault, or custom harness.

## Core Promise

Respect the host project first. Add Owledge as a planning and memory layer only.

## Read References

- Read `references/planning-layer.md` before producing a plan, assigning agents, or writing Owledge artifacts.

## Trigger Signals

Use this skill when the user asks for:

- an MVP plan that stays tied to the original goal
- scoped context before implementation
- multi-agent or subagent coordination
- planning inside an existing `AGENTS.md` project
- Superpowers, LLM Wiki, Obsidian, Graphify, Hermes, Codex, Claude Code, or custom harness coexistence
- handoffs, evidence, reviews, decisions, lessons, or cross-project reuse

## Workflow

1. **Concept audit freshness check**: if the last concept audit (`.owledge/decisions/concept-audit-*.md`) is older than the last `VERSION` change OR older than 30 days, remind the user to run `owledge concept-audit`. This is a reminder only - never blocks planning.
2. Read existing project instructions and treat them as higher-priority local operating rules.
3. Detect Owledge mode:
   - project-local `.owledge/`
   - mapped knowledgebase via `owledge-map.json`
   - `owledge-module/`
   - principles-only fallback
4. Identify the initial user goal, non-goals, MVP cutline, constraints, and source evidence.
5. Load metadata and scoped sources first; do not load full vaults or raw logs by default.
6. Produce a plan with:
   - goal
   - non-goals
   - MVP cutline
   - evidence sources
   - task lanes
   - review gates
   - handoff expectations
7. **Embed session-continuity checklists.** For each phase in the plan, add three checkboxes: `- [ ] implementation done`, `- [ ] QA checks done`, `- [ ] quick review done`. State the resume rule: a new agent reads the plan, finds the first unchecked box, and continues from there - never restarting the whole plan. See `references/session-continuity.md` for the full protocol.
8. **Create an Owledge phase tasklist for multi-agent release work.** When a plan has multiple phases, QA gates, and subagent lanes, create or update a workpackage from `.owledge/templates/phase-tasklist-template.md` under `.owledge/workpackages/`. The tasklist must list each phase, its QA gate commands, and the three checkboxes. In this repository's dogfood workspace, use `internal/owledge/workpackages/` until dogfood memory is migrated.
9. Write only to allowed Owledge locations if writing is requested or clearly needed.
10. End with the next action and a handoff-ready summary.

## Hard Rules

- Do not overwrite or rewrite a host project's `AGENTS.md`, `CLAUDE.md`, skills, hooks, Superpowers files, or vault taxonomy.
- Do not install Owledge automatically.
- Do not migrate a knowledgebase structure unless explicitly requested.
- Do not use raw session logs, private notes, or unsanitized records as shared context.
- Do not expand scope beyond the MVP cutline without calling it out as a separate idea, future task, or rejected expansion.
- Do not promote candidate ideas, PI reports, or agent interpretations into canonical memory without review.

## Default Output

Return:

- active mode: project-local, mapped KB, module, or principles-only
- sources consulted
- MVP plan and non-goals
- task lanes and write locations
- context budget notes
- review gates
- next handoff
