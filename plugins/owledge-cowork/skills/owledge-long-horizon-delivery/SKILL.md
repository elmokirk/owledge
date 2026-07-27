---
name: owledge-long-horizon-delivery
description: Run Owledge's bounded long-horizon planning and delivery modes for MVP sparring, release/version steering, one-ticket execution, gate review, and recovery. Use when a user asks to reduce broad planning to a shippable MVP, prevent scope creep, preserve future ideas in a roadmap, execute a multi-phase or multi-version plan, reflect after a release, resume interrupted work, or maintain evidence-backed user control across long-running agent sessions.
---

# Owledge Long-Horizon Delivery

Treat chat as transient and Owledge Markdown as durable control state. Select
one mode and keep its stop condition visible.

## Mode Selection

| Signal | Mode |
| --- | --- |
| Broad request, planning sparring, too many ideas, unclear MVP | `mvp-sparring` |
| Release/phase completed, version bump, next-plan reflection | `version-steering` |
| One dependency-ready task should be implemented | `ticket-execution` |
| Evidence or promotion boundary must be checked | `gate-review` |
| Interrupted session or handoff should continue | `recovery` |

Read `references/modes.md` before writing a plan, changing version state, or
resuming execution.

## Universal Workflow

1. Read host instructions, `OWLEDGE.md`, current run state, and the smallest
   relevant planning slice.
2. Inspect relevant project ideas, concepts, decisions, patterns, lessons, and
   roadmap entries before creating new scope.
3. State the active mode, outcome, non-goals, authority boundary, and stop
   condition.
4. Persist the smallest durable artifact required by the mode.
5. Record findings, decisions, questions, evidence, and the exact next action.
6. Stop when the selected mode's completion test passes.

## MVP Sparring Rule

Default planning work to `mvp-sparring`. Ask only questions whose answers can
change the current cutline. Once one smallest useful increment has a target
user, observable outcome, success signal, non-goals, first executable task,
and QA gate, stop planning and ask the user to lock or adjust it.

Classify every extra idea:

- required now;
- enabling dependency;
- roadmap;
- idea candidate;
- reject/defer with reason.

Do not silently discard useful ideas and do not add them to current scope
without owner approval.

## Version Steering Rule

After every release/version gate, compile the complete shipped delta,
implementation findings, decisions, questions, limitations, and next-version
plan reflection. Mark affected next-version work as `keep`, `amend`, `defer`,
or `drop`. Stop for explicit `approve`, `adjust`, or `defer`.

Technical readiness never authorizes publication, tagging, or next-version
execution.

## Hard Rules

- Never continue ideation merely because more options are possible.
- Never let token savings or schedule pressure weaken acceptance, privacy, or
  security boundaries.
- Never auto-promote an idea, candidate, lesson, or roadmap item.
- Never start a later version before its prior alignment decision is recorded.
- Never use `.owledge/skills` as an assumed harness discovery path.
- Never load whole vaults or raw session history when scoped sources suffice.

## Required Output

Return:

- active mode and stop condition;
- current shippable cutline or active ticket/gate;
- evidence and sources consulted;
- findings, decisions, and owner questions;
- routed roadmap/idea candidates;
- exact next action.
