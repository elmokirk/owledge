---
title: "Owledge project router"
version: "1.0.0"
status: "active"
memory_id: "mem:local:project:owledge:router"
tenant_id: "local"
customer_id: "local"
project_id: "project"
doc_type: "owledge_entrypoint"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge project router"
summary: "Minimal local Owledge entrypoint. Markdown is canonical; use Core only when deterministic recall, review, health or upgrade is needed."
concept_tags: ["owledge", "project-context"]
stack_tags: []
problem_patterns: []
architecture_patterns: ["markdown-canonical"]
failure_modes: []
confidence: 1.0
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "1970-01-01T00:00:00Z"
updated_at: "1970-01-01T00:00:00Z"
source_hash: ""
reusable_lessons: []
edges: []
---

# Owledge

This project uses local Markdown as durable knowledge. Read this file before
planning or research. Use normal project files for truth, and write only
reviewable Candidates or decisions when a durable delta is useful.

For deterministic local operations, install or invoke Owledge Core and use its
bounded `recall`, `context`, `propose`, `review`, `sync`, `doctor`, or `upgrade`
operations. No network, model, database or service is required.
