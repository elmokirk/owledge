---
title: "Owledge v1 Version Alignment Protocol"
date: "2026-07-18"
version: "1.0.0"
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
summary: "Mandatory user-alignment stop, feature-update format, question register, and decision recording contract after each Owledge version gate through v1.0."
concept_tags: ["version-alignment", "goal-handoff", "autonomous-delivery", "user-authority"]
stack_tags: ["markdown", "yaml", "git"]
problem_patterns: ["autonomous-scope-drift", "unanswered-design-questions", "release-without-alignment"]
architecture_patterns: ["human-in-the-loop-gate", "evidence-backed-handoff", "release-boundary"]
failure_modes: ["next-release-autostart", "unrecorded-user-decision", "premature-publication"]
confidence: 0.97
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-18T00:00:00Z"
updated_at: "2026-07-18T00:00:00Z"
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

After `G-<release>-RC` or `G-100-GA` passes, execute only the matching alignment ticket. Create `release-updates/<version>.md`, present the feature update and every question to the user, set `RUN-STATE.yaml` to `awaiting_user_alignment`, and mark the ticket `blocked`. Do not publish/tag or begin the next version.

## Required Version Update

Every update must contain these exact headings:

1. `## Feature Update`
2. `## User Benefits and Adoption Impact`
3. `## Gate and Evidence Summary`
4. `## Compatibility, Migration, and Operations`
5. `## Known Limitations and Deferred Work`
6. `## Questions and Decisions Required`
7. `## Recommendation and Safe Default`
8. `## Recorded User Decision`

Statements of fact link to ticket/gate/evidence identifiers. Product claims distinguish shipped behavior, preview/experimental behavior, and future work. Every unresolved issue is a numbered question; write `None` explicitly when none remain.

## Question Capture During a Version

Tickets and gates append non-blocking questions to `RUN-STATE.yaml` under `alignment.open_questions`, with source, impact, recommendation, and safe default. The alignment ticket transfers every open entry into **Questions and Decisions Required**; it may not silently resolve or omit one. Safety, privacy, credentials/cost, data-loss, external-commitment, and irreversible-architecture questions escalate immediately.

## User Decision Contract

| Decision | Agent action | Release/next-version state |
| --- | --- | --- |
| `approve` | Record approver, date, scope, and any constraints; run validator. | Alignment ticket may become `done`; publish/tag and next release are allowed only within the recorded constraints. |
| `adjust` | Create or amend the smallest affected ticket/gate, record the change and its impact, re-run validation. | Remain blocked; present a refreshed update. |
| `defer` | Record deferred item, rationale, risk, limitation, and target backlog. | Remain blocked until the user separately authorizes publish/tag and/or the next release. |

## Copy-Ready `/goal` Resume Prompt

```text
Resume Owledge v1 delivery from RUN-STATE.yaml. Read GOAL.md, CONTROL-PLANE-POLICY.md, ALIGNMENT-PROTOCOL.md, the active ticket, its gate, and directly referenced evidence only. If alignment.state is awaiting_user_alignment, do not implement or select any other ticket. Present release-updates/<version>.md, collect explicit approve/adjust/defer decisions for every open question, record the decision, run python tools/validate_v1_delivery_plan.py, and stop again unless the user explicitly unlocks the next action.
```

## Version Update Template

```markdown
# Owledge <version> Feature Update

## Feature Update

## User Benefits and Adoption Impact

## Gate and Evidence Summary

## Compatibility, Migration, and Operations

## Known Limitations and Deferred Work

## Questions and Decisions Required

## Recommendation and Safe Default

## Recorded User Decision

- Status: awaiting_user_alignment
- Decision: pending
- Decider: product-owner
- Date: pending
- Constraints: none
```
