---
memory_id: "mem:tenant-local:customer-local:ts-adapter-fixture:canonical:markdown-contract"
tenant_id: "tenant-local"
customer_id: "customer-local"
project_id: "ts-adapter-fixture"
doc_type: "canonical"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Markdown remains the adapter source of truth"
summary: "Owledge adapters read Markdown memory records and must not create a second memory engine."
concept_tags:
  - "markdown-first"
  - "adapter-contract"
stack_tags:
  - "node"
  - "typescript"
problem_patterns: []
architecture_patterns:
  - "read-only-adapter"
failure_modes:
  - "second-memory-engine"
reusable_lessons: []
confidence: 0.9
review_status: "approved"
sanitization_status: "not_required"
created_at: "2026-06-20T00:00:00Z"
updated_at: "2026-06-20T00:00:00Z"
source_hash: "fixture"
edges: []
---

# Markdown Contract

The optional TypeScript adapter treats Owledge Markdown frontmatter as canonical.
It can lint records and run retrieval fixtures, but it does not persist a new
database, vector index, or memory engine.
