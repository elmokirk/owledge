---
name: concept-blindspot-audit
description: Stress-test Owledge's own concepts (distribution, lifecycle, coherence, self-description) against 8 audit dimensions. Surfaces blindspots the way a red-team would, but for conceptual gaps rather than code bugs. Use when the user asks to audit concepts, find blindspots, stress-test the kit, or review the project's own foundations.
version: 0.1.0
---

# Concept Blindspot Audit

## What this skill does

This skill audits the Owledge kit's own foundations, not user application code. It
stress-tests the project's distribution, lifecycle, dogfood fidelity, contract
completeness, cross-layer integrity, failure-mode coverage, conceptual coherence,
and self-description accuracy against an 8-dimension rubric. It surfaces
blindspots the way a red-team would, but for conceptual gaps rather than code
bugs: missing upgrade paths, version drift across sources, silent-skip install
behavior, undetected global-link breakage, dogfood drift, and the absence of a
self-audit loop.

Dimensions 1-4 are mechanical (deterministic checks run by the
`concept_audit` function in `tools/agent_memory_cli.py`). Dimensions 5-8 are
guided: the function emits a checklist and evidence packet, and the agent or
user scores them after working through the questions. Findings are candidate
artifacts only. They never auto-promote into canonical memory.

## Trigger Signals

Use this skill when the user asks to:

- audit concepts
- find blindspots
- stress-test the kit
- review foundations
- run a concept audit
- run a self-description check
- check distribution integrity
- check lifecycle and upgrade paths
- check dogfood fidelity
- check contract completeness
- check conceptual coherence

## Hard Rules

- **No auto-promotion.** Findings are candidate artifacts. They require curator
  review before any write into `canonical/`, `compiled/`, `patterns/`, or
  `lessons/`.
- **No destructive writes.** Never delete or overwrite existing memory. New
  findings are appended as new files only.
- **No edits outside `agent-memory/`.** The only writes this skill performs are:
  - `agent-memory/decisions/concept-audit-YYYY-MM-DD.md` (in
    `approve-automatically` mode only)
  - draft idea cards under `agent-memory/ideas/` (in `approve-automatically`
    mode only, one card per `fail` finding, `status: captured`, edges to the
    report)
  - a feedback ticket via `docs/feedback-round-YYYY-MM.template.md` (in
    `full-access` mode only, when `project_mode >= mvp`)
- **Never blocks.** The `concept-audit-fresh` finalization gate is a reminder or
  warning, not a hard block. The single exception is `project_mode: saas`, where
  a stale or missing audit fails the gate (per Decision Q6).

## Workflow

1. **Detect `project_mode`** (poc/mvp/side/saas) from `PROJECT_CONTEXT.md`
   frontmatter. Default to `mvp` if the field is absent.
2. **Detect `planning_mode`** (supervised/approve-automatically/full-access)
   from `PROJECT_CONTEXT.md` frontmatter. Default to `supervised` if absent.
3. **Load the profile.** If `agent-memory/concept-audit-profile.json` exists,
   load it; otherwise use the defaults from
   `references/profile-template.json`. The profile carries per-dimension
   weights, dimension overrides, and `freshness_days` (default 30).
4. **Run dimensions 1-4 mechanically.** Invoke the deterministic checks via the
   `concept_audit` function (`python tools/agent_memory_cli.py --project-root .
   concept-audit`). These return concrete findings with severity
   (`error`/`warning`/`info`), detail, and evidence.
5. **Run dimensions 5-8 as a guided self-audit.** Work through the checklists
   the function returns under `guided_checklists`. Collect evidence (file paths,
  command output, frontmatter snippets) for each answer. Score each dimension
   0-10 using the scoring guide in `references/audit-dimensions.md`.
6. **Score each dimension 0-10.** Mechanical dimensions are scored by the
   function. Guided dimensions are scored by the agent/user after working
   through the checklist.
7. **Deliver findings per `planning_mode`:**
   - `supervised` (default): present findings inline. Write no files. Create no
     idea cards or tickets.
   - `approve-automatically`: write `concept-audit-YYYY-MM-DD.md` to
     `agent-memory/decisions/` using the report template. Promote each `fail`
     finding to a draft idea card under `agent-memory/ideas/` with
     `status: captured` and an edge to the report. No canonical promotion.
   - `full-access`: do everything `approve-automatically` does, plus open a
     feedback ticket via `docs/feedback-round-YYYY-MM.template.md` when
     `project_mode >= mvp`.
8. **State the next audit due date.** Compute it as
   `audit_date + freshness_days` (default 30). Remind the user that the
   `concept-audit-fresh` finalization gate will warn (or fail at `saas`) if the
   next audit is not run before the version bumps or the freshness window
   expires.

## Read References

- Read `references/audit-dimensions.md` before running an audit. It contains
  the full 8-dimension rubric, mechanical check lists, guided checklists, depth
  scales per `project_mode`, the 0-10 scoring guide, and worked examples drawn
  from the v0.6.1 session that motivated this skill.
- Read `references/profile-template.json` to understand the default
  `concept-audit-profile.json` shape (weights, dimension overrides,
  `freshness_days`).