---
memory_id: "mem:shared:shared:retrieval-reference:lesson:privacy-export-gate"
tenant_id: "shared"
customer_id: "shared"
project_id: "retrieval-reference"
doc_type: "lesson"
status: "promoted"
visibility: "shared"
data_class: "internal"
semantic_title: "Shared export privacy gate"
summary: "Shared retrieval exports must reject private raw sessions, confidential data classes, and unapproved sanitization states."
concept_tags:
  - "agent-memory"
  - "privacy"
  - "retrieval-calibration"
  - "production-ready"
stack_tags:
  - "markdown"
  - "rag"
problem_patterns:
  - "raw-session-export"
  - "unreviewed-shared-memory"
architecture_patterns:
  - "markdown-source-of-truth"
  - "project-folder-only"
failure_modes:
  - "private-data-leak"
  - "unsafe-shared-export"
reusable_lessons:
  - "A shared memory record needs approved review_status and approved sanitization_status."
  - "Raw sessions are evidence inputs, not shared RAG documents."
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
edges:
  - type: "shared_lesson_for"
    target: "mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy"
    confidence: 0.9
    reason: "The lifecycle policy depends on safe shared export rules."
---

# Shared Export Privacy Gate

This shared lesson is sanitized and approved. It demonstrates the safety path
for retrieval fixtures: shared documents can enter reusable RAG only after
review and sanitization, while raw runtime sessions remain private.
