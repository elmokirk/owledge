---
memory_id: "mem:owledge:global:owledge:idea:pre-plan-idea-concept-harness-hooks"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "idea"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "Harness pre-plan idea and concept hooks"
summary: "A portable lifecycle hook that supplies a scoped Owledge idea/concept capsule before feature planning and returns proposed MVP, roadmap, and idea dispositions for owner approval."
concept_tags:
  - "pre-plan-hook"
  - "idea-retrieval"
  - "mvp-cutline"
  - "harness-adapter"
stack_tags:
  - "codex"
  - "claude-code"
  - "mcp"
  - "python"
problem_patterns:
  - "planning-starts-without-existing-ideas"
  - "scope-creep"
  - "future-concepts-get-lost"
architecture_patterns:
  - "deterministic-context-capsule"
  - "capability-negotiation"
  - "human-approved-promotion"
failure_modes:
  - "background-hook-writes-canonical-memory"
  - "whole-vault-injection"
  - "unsupported-hook-silently-skipped"
reusable_lessons:
  - "Discovery, read-only context selection, and durable promotion are separate authority boundaries."
confidence: 0.91
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-27T00:00:00Z"
updated_at: "2026-07-27T00:00:00Z"
retention_class: "standard"
stale_after: ""
expires_at: ""
last_reviewed_at: "2026-07-27T00:00:00Z"
review_cycle: "monthly"
source_hash: ""
idea_stage: "implementation-plan"
idea_source: "user-request"
idea_fit:
  current_project: "high"
  future_project: "high"
  cross_project: "high"
planning_relevance:
  - "check-before-new-plan"
  - "check-before-harness-adapter-work"
edges:
  - type: "relates_to"
    target: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
    reason: "The implementation is staged across the v0.8.0 context compiler and v0.8.1 adapter tickets."
    confidence: 0.98
---

# Harness Pre-Plan Idea and Concept Hooks

## Idea

Before a harness creates a new feature plan, request a deterministic,
budget-bounded capsule of relevant ideas, PI concepts, decisions, patterns,
lessons, and roadmap entries. The planning skill classifies each relevant
candidate as required now, enabling dependency, roadmap, idea candidate, or
reject/defer. Durable writes or promotions require owner approval.

## Trigger

The new bounded MVP-sparring mode can apply this behavior today when agents
follow the skill, but no shared adapter lifecycle hook guarantees that every
supported harness requests the same scoped context before planning.

## Problem Pattern

- Agents can rediscover old ideas instead of reusing them.
- Broad concepts can silently inflate the current MVP.
- Future-value ideas can disappear from chat without a durable route.
- Harness-specific hooks can imply capabilities they do not actually support.

## Possible Outcome

- `OW-080-05`: deterministic read-only pre-plan capsule.
- `OW-080-03`: WorkContract MVP cutline and candidate dispositions.
- `OW-081-01` through `OW-081-05`: shared capability and conformance contract.
- `OW-081-13`: harness-specific lifecycle hook/adapters.
- `OW-090-02` and `OW-090-04`: reviewed semantic linking and promotion.

## Similar Ideas / Existing Work

- `skills/owledge-long-horizon-delivery/`
- `skills/owledge-planning-layer/`
- `docs/ideation-workflow.md`
- `internal/owledge/plans/owledge-v1-autonomous-delivery-master-plan.md`

## Next Action

During `OW-080-05`, define the capsule input/output schema, selection budget,
typed inclusion/exclusion reasons, and golden fixtures before any harness hook
is implemented.
