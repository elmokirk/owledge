---
name: owledge-planning-layer
description: Add Owledge's MVP-first planning, evidence, handoff, and context-hygiene layer on top of an existing project's own AGENTS.md, skills, hooks, or custom agent harness without replacing them. Use for planning sparring, scope reduction, MVP cutlines, idea-to-roadmap routing, and preparation of resumable multi-phase delivery.
version: 0.1.0
---

# Owledge Planning Layer

Use this skill when a user wants Owledge planning discipline inside an existing project that already has its own agent instructions, skills, hooks, Superpowers workflow, LLM wiki, Obsidian vault, or custom harness.

## Core Promise

Respect the host project first. Add Owledge as a planning and memory layer only.
Default planning to the `mvp-sparring` mode of
`owledge-long-horizon-delivery`.

## Mode Routing

- Use `mvp-sparring` for new plans, broad feature requests, scope negotiation,
  and planning that risks expanding indefinitely.
- Use `version-steering` after a release/version gate.
- Use this skill directly as a compatibility facade when the long-horizon
  skill is unavailable; preserve the same cutline and stop rules.

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
4. Inspect relevant `.owledge/ideas/`, `.owledge/pi-agent/concepts/`,
   `ROADMAP.md`, decisions, patterns, and lessons before creating new scope.
5. Identify the initial user goal, target user, one observable success signal,
   non-goals, MVP cutline, constraints, and source evidence.
6. Classify extra concepts as required now, enabling dependency, roadmap,
   idea candidate, or reject/defer.
7. Ask only questions whose answers can change the cutline; provide a
   recommendation and safe default.
8. Load metadata and scoped sources first; do not load full vaults or raw logs by default.
9. Produce the smallest plan with:
   - goal
   - target user and success signal
   - non-goals
   - MVP cutline
   - evidence sources
   - first executable task
   - review gates
   - routed roadmap/idea candidates
   - handoff expectations
10. **Embed session-continuity checklists** only when the locked MVP genuinely
    needs multiple phases. For each phase add `implementation done`, `QA checks
    done`, and `quick review done`; resume from the first unchecked box.
11. **Create an Owledge phase tasklist** only for multi-phase release work.
12. Present `lock`, `adjust`, or `defer`. When the cutline is complete, stop
    planning; do not generate another variant unless the user chooses `adjust`.
13. Write only to allowed Owledge locations and end with the exact next action.

## Hard Rules

- Do not overwrite or rewrite a host project's `AGENTS.md`, `CLAUDE.md`, skills, hooks, Superpowers files, or vault taxonomy.
- Do not install Owledge automatically.
- Do not migrate a knowledgebase structure unless explicitly requested.
- Do not use raw session logs, private notes, or unsanitized records as shared context.
- Do not expand scope beyond the MVP cutline without calling it out as a separate idea, future task, or rejected expansion.
- Do not discard useful out-of-cutline ideas; route them to `.owledge/ideas/`
  or an accepted roadmap/backlog item.
- Do not keep producing alternative plans after the user locks the cutline.
- Do not promote candidate ideas, PI reports, or agent interpretations into canonical memory without review.

## Default Output

Return:

- active mode: project-local, mapped KB, module, or principles-only
- sources consulted
- MVP plan and non-goals
- first executable task and write locations
- routed roadmap and idea candidates
- context budget notes
- review gates
- next handoff
