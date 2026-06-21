---
memory_id: "mem:tenant-local:customer-local:ts-adapter-fixture:compiled:retrieval-adapter"
tenant_id: "tenant-local"
customer_id: "customer-local"
project_id: "ts-adapter-fixture"
doc_type: "compiled"
status: "reviewed"
visibility: "private"
data_class: "internal"
semantic_title: "TypeScript adapter retrieval fixture"
summary: "A deterministic keyword harness proves that Node tooling can retrieve Owledge records from Markdown fixtures."
concept_tags:
  - "retrieval-fixture"
  - "typescript-adapter"
stack_tags:
  - "node"
  - "typescript"
problem_patterns: []
architecture_patterns:
  - "read-only-adapter"
failure_modes: []
reusable_lessons:
  - "Keep retrieval tests deterministic and fixture-backed."
confidence: 0.8
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-20T00:00:00Z"
updated_at: "2026-06-20T00:00:00Z"
source_hash: "fixture"
edges:
  - type: "derived_from"
    target: "mem:tenant-local:customer-local:ts-adapter-fixture:canonical:markdown-contract"
---

# TypeScript Adapter Retrieval Fixture

This record exercises the owledge-lint retrieval fixture runner. The runner uses
stable keyword scoring against Markdown body text and frontmatter fields. It is
not a vector store and does not replace the Python memory tooling.
