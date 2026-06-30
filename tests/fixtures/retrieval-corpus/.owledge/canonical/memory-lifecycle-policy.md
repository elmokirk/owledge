---
memory_id: "mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy"
tenant_id: "fixture"
customer_id: "demo"
project_id: "retrieval-fixture"
doc_type: "canonical"
status: "reviewed"
visibility: "tenant"
data_class: "internal"
semantic_title: "Memory lifecycle policy for project kits"
summary: "Retention, stale-after review, conflict edges, sensitive-data scans, and raw-session privacy are required before shared retrieval export."
concept_tags:
  - "owledge"
  - "project-kit"
  - "retrieval-calibration"
  - "production-ready"
stack_tags:
  - "markdown"
  - "python"
problem_patterns:
  - "stale-memory"
  - "contradictory-memory"
architecture_patterns:
  - "markdown-source-of-truth"
  - "project-folder-only"
failure_modes:
  - "raw-session-export"
  - "unreviewed-shared-memory"
reusable_lessons:
  - "Treat retention and conflict checks as read-only gates before promotion."
  - "Keep raw runtime sessions private and summarize before retrieval."
confidence: 0.95
review_status: "approved"
sanitization_status: "approved"
created_at: "2026-05-20T00:00:00Z"
updated_at: "2026-05-26T00:00:00Z"
retention_class: "long"
stale_after: "2026-08-26T00:00:00Z"
expires_at: ""
last_reviewed_at: "2026-05-26T00:00:00Z"
review_cycle: "quarterly"
source_hash: "fixture"
edges: []
---

# Memory Lifecycle Policy For Project Kits

This canonical record states that the Owledge Project Kit must run
retention audit, stale memory review, conflict review, and sensitive-data scan
before publishing retrieval fixtures or shared exports.

The production-ready baseline keeps Markdown as canonical project memory,
uses context packs for working memory, and excludes raw runtime event logs from
RAG exports.
