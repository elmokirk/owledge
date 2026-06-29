---
memory_id: "mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring"
tenant_id: "fixture"
customer_id: "demo"
project_id: "retrieval-fixture"
doc_type: "compiled"
status: "reviewed"
visibility: "tenant"
data_class: "internal"
semantic_title: "Context pack scoring with task objective"
summary: "Context packs rank memory by task objective, reviewed status, doc type priority, tag-summary match, edge proximity, freshness, and budget exclusions."
concept_tags:
  - "owledge"
  - "context-pack"
  - "retrieval-calibration"
  - "production-ready"
stack_tags:
  - "markdown"
  - "cli"
problem_patterns:
  - "context-budget"
  - "stale-memory"
architecture_patterns:
  - "progressive-disclosure"
  - "project-folder-only"
failure_modes:
  - "middle-context-loss"
  - "irrelevant-context"
reusable_lessons:
  - "Score context with the task id plus objective instead of task id alone."
  - "Expose score_breakdown and freshness_warnings for deterministic QA."
confidence: 0.9
review_status: "approved"
sanitization_status: "approved"
created_at: "2026-05-20T00:00:00Z"
updated_at: "2026-05-26T00:00:00Z"
retention_class: "standard"
stale_after: "2026-07-26T00:00:00Z"
expires_at: ""
last_reviewed_at: "2026-05-26T00:00:00Z"
review_cycle: "monthly"
source_hash: "fixture"
edges:
  - type: "relates_to"
    target: "mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy"
    confidence: 0.9
    reason: "Context scoring consumes lifecycle freshness signals."
---

# Context Pack Scoring With Task Objective

The fixture verifies that build-context-pack can use an explicit objective and
still emit compatible output. The expected QA fields are score_breakdown,
freshness_warnings, included_sources, and excluded_sources.

The same record is intentionally rich in shared retrieval terms so query
fixtures can test ranking, project coverage, and safety gates deterministically.
