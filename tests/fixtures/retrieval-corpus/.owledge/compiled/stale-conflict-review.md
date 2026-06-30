---
memory_id: "mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review"
tenant_id: "fixture"
customer_id: "demo"
project_id: "retrieval-reference"
doc_type: "compiled"
status: "active"
visibility: "tenant"
data_class: "internal"
semantic_title: "Stale conflict review edge case"
summary: "This active compiled record is intentionally stale and contradicts the lifecycle policy to exercise conflict-review fixtures."
concept_tags:
  - "owledge"
  - "stale-memory"
  - "retrieval-calibration"
  - "production-ready"
stack_tags:
  - "markdown"
  - "qa"
problem_patterns:
  - "contradictory-memory"
  - "stale-memory"
architecture_patterns:
  - "markdown-source-of-truth"
  - "project-folder-only"
failure_modes:
  - "unreviewed-shared-memory"
  - "unsafe-shared-export"
reusable_lessons:
  - "Stale active memory should remain visible to auditors but be penalized in context selection."
  - "Contradictions should be recorded as edges instead of overwriting history."
confidence: 0.65
review_status: "reviewed"
sanitization_status: "approved"
created_at: "2026-01-01T00:00:00Z"
updated_at: "2026-01-01T00:00:00Z"
retention_class: "standard"
stale_after: "2026-02-01T00:00:00Z"
expires_at: ""
last_reviewed_at: "2026-01-01T00:00:00Z"
review_cycle: "monthly"
source_hash: "fixture"
edges:
  - type: "contradicts"
    target: "mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy"
    confidence: 0.7
    reason: "Fixture deliberately models contradictory active memory."
---

# Stale Conflict Review Edge Case

This record is stale by design. Retrieval should still be able to find it for
QA, while context-pack scoring surfaces freshness_warnings so a memory curator
can decide whether to archive, supersede, or promote a corrected record.
