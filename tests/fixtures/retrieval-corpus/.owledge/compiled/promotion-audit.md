---
memory_id: "mem:tenant-fixture:customer-fixture:retrieval-fixture:compiled:promotion-audit"
tenant_id: "tenant-fixture"
customer_id: "customer-fixture"
project_id: "retrieval-fixture"
doc_type: "compiled"
status: "reviewed"
visibility: "shared"
data_class: "internal"
semantic_title: "Promotion audit source hash review approval manifest"
summary: "Promotion audit requires source hash, review approval, target policy, and manifest evidence before durable memory promotion."
concept_tags:
  - "promotion"
  - "audit"
stack_tags:
  - "owledge"
problem_patterns:
  - "unsafe-promotion"
architecture_patterns:
  - "markdown-first-memory"
failure_modes:
  - "missing-review-evidence"
reusable_lessons:
  - "Promotion gates must be deterministic and evidence-linked."
confidence: 0.94
review_status: "approved"
sanitization_status: "approved"
retention_class: "long"
last_reviewed_at: "2026-05-20T00:00:00Z"
review_cycle: "quarterly"
created_at: "2026-05-20T00:00:00Z"
updated_at: "2026-05-20T00:00:00Z"
source_hash: ""
edges:
  - type: "validates"
    target: "mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:context-pack-objective"
    reason: "Promotion audit validates context-pack source quality."
    confidence: 0.8
---

# Promotion Audit

Promotion audit requires source hash checks, review approval, target folder policy, and manifest evidence before durable memory promotion.
