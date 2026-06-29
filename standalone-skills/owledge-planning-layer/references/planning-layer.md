# Owledge Planning Layer Reference

## Purpose

This skill lets Owledge operate inside existing user projects without competing with project-specific instructions. It is a planning layer, not a replacement for the host agent workflow.

## Priority Order

1. System and developer instructions.
2. Host project `AGENTS.md`, `CLAUDE.md`, or equivalent local agent rules.
3. User request.
4. Owledge planning rules.
5. Optional Owledge add-ons and generated views.

If Owledge rules conflict with host project rules, preserve the host project rule and state the tradeoff.

## Mode Detection

| Signal | Mode |
| --- | --- |
| `.owledge/` and `OWLEDGE.md` exist | Project-local Owledge |
| `owledge-map.json` exists | Mapped knowledgebase |
| `owledge-module/` exists | Drop-in KB module |
| none of the above | Principles-only |

## Planning Contract

Every plan should answer:

- What is the original user goal?
- What is explicitly out of scope?
- What is the smallest useful MVP?
- Which source files or memory records support this plan?
- Which tasks can be assigned independently?
- Which artifacts must workers write?
- What review gate prevents overengineering or unsafe promotion?
- What should the next agent read first?

## Context Hygiene

Default to this order:

1. Project/context root files.
2. Memory index metadata.
3. Relevant compiled or canonical summaries.
4. Relevant plans, decisions, evidence, and reviews.
5. Full source files only when needed.
6. Raw logs only for explicit debugging or compaction.

Avoid:

- whole-vault prompt loading
- long transcript paste
- generated report bodies as canonical evidence
- unrelated historical plans
- private global memory in project/shared exports

## Multi-Agent Lanes

| Lane | Purpose | Output |
| --- | --- | --- |
| Orchestrator | Preserve goal, MVP cutline, dependencies, and task split | plan, work packages, context pack |
| Worker | Implement bounded task | evidence, handoff, changed paths |
| Reviewer | Evaluate correctness, risk, missing tests, and scope creep | review artifact |
| Curator | Propose durable memory promotion | canonical draft, lesson, pattern, promotion manifest |

Workers should not promote memory. Reviewers should not rewrite implementation. Curators should not accept unreviewed or unsanitized records.

## Scope Creep Control

When an agent discovers extra work:

- If required for the MVP, add it as an explicit dependency.
- If useful but not required, capture it as an idea or future task.
- If risky or unclear, route it to review.
- If it changes architecture, require a decision record.

## Handoff Shape

A useful handoff includes:

- initial goal
- current status
- sources read
- files changed or artifacts created
- open risks
- exact next action
- what not to do next

## Session Continuity

When producing or resuming a multi-phase plan, use per-phase checklists so a
new agent can resume from the exact last-completed step.

- Every phase in a multi-phase plan gets three checkboxes: `- [ ] implementation done`, `- [ ] QA checks done`, `- [ ] quick review done`.
- Every phase lists its concrete QA gate commands before the checklist.
- For multi-agent release work, create a separate Owledge workpackage tasklist from `.owledge/templates/phase-tasklist-template.md` under `.owledge/workpackages/`. In this repository's dogfood workspace, use `internal/owledge/workpackages/` until dogfood memory is migrated.
- **Resume rule:** find the first unchecked box and continue from there. Never restart a completed phase.
- If a checkbox is stale (checked but work incomplete), re-run that phase's QA gate; if it fails, uncheck and redo.
- Subagents check their own boxes before returning to the orchestrator.
- The checkbox is a navigation aid, not an audit record; the QA gate output is the durable evidence.

See `session-continuity.md` for the full protocol and worked examples.
