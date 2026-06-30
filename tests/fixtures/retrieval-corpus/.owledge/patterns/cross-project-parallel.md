---
memory_id: "mem:tenant-fixture:customer-fixture:retrieval-fixture:pattern:cross-project-parallel"
tenant_id: "tenant-fixture"
customer_id: "customer-fixture"
project_id: "retrieval-fixture"
doc_type: "pattern"
status: "reviewed"
visibility: "shared"
data_class: "internal"
semantic_title: "Cross project parallel discovery"
summary: "Cross project parallel discovery uses typed edges, recurring patterns, shared tags, and stable memory IDs."
concept_tags:
  - "parallel-discovery"
  - "typed-edges"
stack_tags:
  - "owledge"
problem_patterns:
  - "context-fragmentation"
architecture_patterns:
  - "markdown-first-memory"
failure_modes:
  - "missing-parallels"
reusable_lessons:
  - "Shared pattern fields make project parallels testable."
confidence: 0.92
review_status: "approved"
sanitization_status: "approved"
retention_class: "long"
last_reviewed_at: "2026-05-20T00:00:00Z"
review_cycle: "quarterly"
created_at: "2026-05-20T00:00:00Z"
updated_at: "2026-05-20T00:00:00Z"
source_hash: ""
edges:
  - type: "similar_to"
    target: "mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety"
    reason: "Both use reusable memory safety patterns."
    confidence: 0.8
---

# Cross Project Parallel Discovery

Cross project parallel discovery should find typed edges, recurring patterns, shared tags, and stable memory identifiers across reviewed records.
