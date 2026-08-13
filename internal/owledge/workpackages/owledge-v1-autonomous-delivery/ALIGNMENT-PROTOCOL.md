---
title: "Owledge v1 Version Alignment Protocol"
date: "2026-07-27"
version: "1.1.0"
memory_id: "mem:owledge:global:owledge:project_context:v1-version-alignment-protocol"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "alignment_protocol"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge version alignment protocol for autonomous goal execution"
summary: "Mandatory user-alignment stop, feature-update format, finding/decision/question registers, and next-version plan reflection after each Owledge version gate through v1.0."
concept_tags: ["version-alignment", "goal-handoff", "autonomous-delivery", "user-authority"]
stack_tags: ["markdown", "yaml", "git"]
problem_patterns: ["autonomous-scope-drift", "unanswered-design-questions", "release-without-alignment"]
architecture_patterns: ["human-in-the-loop-gate", "evidence-backed-handoff", "release-boundary"]
failure_modes: ["next-release-autostart", "unrecorded-user-decision", "premature-publication"]
confidence: 0.97
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-18T00:00:00Z"
updated_at: "2026-07-27T00:00:00Z"
source_hash: ""
reusable_lessons:
  - "Technical readiness and product alignment are separate decisions that require separate evidence."
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
    confidence: 1.0
    reason: "Implements the mandatory user-alignment boundaries required by the v1 master plan."
---

# Owledge v1 Version Alignment Protocol

## Hard Stop

After `G-<release>-RC` or `G-100-GA` passes, execute only the matching alignment ticket. Create `release-updates/<version>.md`, present the complete version review to the user, set `RUN-STATE.yaml` to `awaiting_user_alignment`, and mark the ticket `blocked`. Do not publish/tag or begin the next version.

## Required Version Update

Every update must contain these exact headings:

1. `## Feature Update`
2. `## User Benefits and Adoption Impact`
3. `## Gate and Evidence Summary`
4. `## Implementation Findings: Problems, Gaps, and Deviations`
5. `## Decision Log`
6. `## Compatibility, Migration, and Operations`
7. `## Known Limitations and Deferred Work`
8. `## Next-Version Plan Reflection`
9. `## Questions and Decisions Required`
10. `## Recommendation and Safe Default`
11. `## Recorded User Decision`

Statements of fact link to ticket/gate/evidence identifiers. Product claims distinguish shipped behavior, preview/experimental behavior, and future work. Every unresolved issue is a numbered question; write `None` explicitly when none remain.

## Finding, Decision, and Question Capture During a Version

Tickets and gates append:

- non-blocking questions to `alignment.open_questions`;
- problems, gaps, deviations, regressions, and new risks to
  `alignment.findings`;
- decisions made or requested to `alignment.decisions`.

Each finding uses a stable `F-<release>-NN` ID and records source ticket/gate,
evidence, severity, user impact, release impact, options, recommendation, safe
default, and status. Each decision uses a stable `D-<release>-NN` ID and records
its related finding/question, authority, rationale, constraints, affected
artifacts, and verification status.

The alignment ticket transfers every entry into the corresponding update
section; it may not silently resolve, merge away, or omit one. Write `None`
explicitly when a register is empty. Safety, privacy, credentials/cost,
data-loss, external-commitment, acceptance-boundary, and
irreversible-architecture questions escalate immediately.

## Next-Version Plan Reflection

After the current release gate is green, compare the next version's accepted
scope to the implementation evidence just produced. For every affected ticket
or gate, record one result:

- `keep`: evidence still supports the existing plan;
- `amend`: change acceptance, dependency, scope, or gate before execution;
- `defer`: move work with rationale, limitation, residual risk, and target;
- `drop`: remove unsupported or no-longer-valuable work without deleting its
  decision history.

Record the proposal under `alignment.next_plan_reflection`. Plan/ticket/gate
amendments required by the proposal must pass
`python tools/validate_v1_delivery_plan.py` before owner review. The proposal is
not accepted until the owner decides.

## User Decision Contract

| Decision | Agent action | Release/next-version state |
| --- | --- | --- |
| `approve` | Record approver, date, scope, and any constraints; run validator. | Alignment ticket may become `done`; publish/tag and next release are allowed only within the recorded constraints. |
| `adjust` | Create or amend the smallest affected ticket/gate, record the change and its impact, re-run validation. | Remain blocked; present a refreshed update. |
| `defer` | Record deferred item, rationale, risk, limitation, and target backlog. | Remain blocked until the user separately authorizes publish/tag and/or the next release. |

## Copy-Ready `/goal` Resume Prompt

```text
Resume Owledge v1 delivery with the bounded `resume-context-v1` capsule, the active ticket/checkpoint, its compact backlog row, its gate, and directly referenced evidence only. Runtime branch: a persisted runtime verifies retained control-document and handoff hashes before skipping re-reads; a baseline-reset runtime reads the latest handoff first, then applies the control-document hash delta. Read a capped gate-result summary first and reconstruct its sidecar only for triage. If alignment.state is awaiting_user_alignment, do not implement or select any other ticket. Present release-updates/<version>.md, including the complete finding, decision, question, and next-plan-reflection sections. Collect explicit approve/adjust/defer decisions, record them, run python tools/validate_v1_delivery_plan.py, and stop again unless the user explicitly unlocks the next action.
```

## Version Update Template

```markdown
# Owledge <version> Feature Update

## Feature Update

## User Benefits and Adoption Impact

## Gate and Evidence Summary

## Implementation Findings: Problems, Gaps, and Deviations

## Decision Log

## Compatibility, Migration, and Operations

## Known Limitations and Deferred Work

## Next-Version Plan Reflection

## Questions and Decisions Required

## Recommendation and Safe Default

## Recorded User Decision

- Status: awaiting_user_alignment
- Decision: pending
- Decider: product-owner
- Date: pending
- Constraints: none
```
