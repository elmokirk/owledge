---
memory_id: "mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:context-pack-objective"
tenant_id: "tenant-fixture"
customer_id: "customer-fixture"
project_id: "retrieval-fixture"
doc_type: "canonical"
status: "reviewed"
visibility: "shared"
data_class: "internal"
semantic_title: "Context pack objective relevance scoring"
summary: "Context pack objective relevance scoring should use task objective terms, freshness warnings, reviewed status, and typed edges."
concept_tags:
  - "context-pack"
  - "objective"
  - "retrieval"
stack_tags:
  - "agent-memory"
problem_patterns:
  - "context-fragmentation"
architecture_patterns:
  - "markdown-first-memory"
failure_modes:
  - "irrelevant-context"
reusable_lessons:
  - "Score context by objective and freshness, not only by file order."
confidence: 0.95
review_status: "approved"
sanitization_status: "approved"
retention_class: "long"
stale_after: "2030-01-01T00:00:00Z"
last_reviewed_at: "2026-05-20T00:00:00Z"
review_cycle: "quarterly"
created_at: "2026-05-20T00:00:00Z"
updated_at: "2026-05-20T00:00:00Z"
source_hash: ""
edges:
  - type: "relates_to"
    target: "mem:tenant-fixture:customer-fixture:retrieval-fixture:compiled:promotion-audit"
    reason: "Context packs cite promotion-ready memory."
    confidence: 0.8
---

# Context Pack Objective Relevance Scoring

Context pack objective relevance scoring should prefer documents matching the explicit objective, then apply freshness warnings, status boosts, review boosts, and typed edge matches.
