---
memory_id: "mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety"
tenant_id: "tenant-fixture"
customer_id: "customer-fixture"
project_id: "retrieval-fixture"
doc_type: "lesson"
status: "promoted"
visibility: "shared"
data_class: "internal"
semantic_title: "Runtime raw sessions stay out of shared RAG"
summary: "Runtime raw sessions must stay private and must not enter shared RAG exports without reviewed sanitized promotion."
concept_tags:
  - "runtime-capture"
  - "rag-safety"
stack_tags:
  - "agent-memory"
problem_patterns:
  - "raw-session-leakage"
architecture_patterns:
  - "markdown-first-memory"
failure_modes:
  - "shared-rag-pollution"
reusable_lessons:
  - "Raw sessions are evidence, not default retrieval corpus."
confidence: 0.97
review_status: "approved"
sanitization_status: "approved"
retention_class: "long"
last_reviewed_at: "2026-05-20T00:00:00Z"
review_cycle: "quarterly"
created_at: "2026-05-20T00:00:00Z"
updated_at: "2026-05-20T00:00:00Z"
source_hash: ""
edges:
  - type: "relates_to"
    target: "mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:context-pack-objective"
    reason: "Context packs must not include raw logs by default."
    confidence: 0.9
---

# Runtime RAG Safety

Runtime raw sessions must stay out of shared RAG exports. Reviewed and sanitized compiled summaries may be promoted later.
