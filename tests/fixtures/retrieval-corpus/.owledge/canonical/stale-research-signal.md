---
memory_id: "mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:stale-research-signal"
tenant_id: "tenant-fixture"
customer_id: "customer-fixture"
project_id: "retrieval-fixture"
doc_type: "canonical"
status: "reviewed"
visibility: "shared"
data_class: "internal"
semantic_title: "Stale research freshness signal"
summary: "Stale research valid until dates and stale_after fields should produce freshness warnings without deleting memory."
concept_tags:
  - "stale-research"
  - "freshness"
stack_tags:
  - "owledge"
problem_patterns:
  - "stale-memory"
architecture_patterns:
  - "markdown-first-memory"
failure_modes:
  - "outdated-context"
reusable_lessons:
  - "Expired research should be flagged before retrieval use."
confidence: 0.86
review_status: "approved"
sanitization_status: "approved"
retention_class: "standard"
stale_after: "2000-01-01T00:00:00Z"
valid_until: "2000-01-01"
last_reviewed_at: "2020-01-01T00:00:00Z"
review_cycle: "annual"
created_at: "2026-05-20T00:00:00Z"
updated_at: "2026-05-20T00:00:00Z"
source_hash: ""
edges:
  - type: "relates_to"
    target: "mem:tenant-fixture:customer-fixture:retrieval-fixture:pattern:cross-project-parallel"
    reason: "Freshness is part of reusable retrieval quality."
    confidence: 0.7
---

# Stale Research Freshness Signal

Stale research valid until dates, stale_after fields, and review cycles should create freshness warnings while preserving the original memory record for review.
