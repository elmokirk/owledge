---
memory_id: "mem:benchmark:synthetic:owledge:decision:stale-conflict-target-0000-212839a44b"
tenant_id: "benchmark"
customer_id: "synthetic"
project_id: "owledge-benchmark"
doc_type: "decision"
status: "active"
visibility: "tenant"
data_class: "internal"
semantic_title: "Stale Conflict Target"
summary: "Synthetic target record for the stale-conflict benchmark scenario."
concept_tags:
  - "benchmark"
  - "stale-conflict"
  - "target"
stack_tags:
  - "owledge"
  - "benchmark-kit"
problem_patterns:
  - "context-pollution"
architecture_patterns:
  - "markdown-source-of-truth"
failure_modes:
  - "context-loss"
confidence: 0.91
review_status: "reviewed"
sanitization_status: "not_required"
benchmark_scenario: "stale-conflict"
benchmark_role: "target"
benchmark_expected: true
benchmark_stale: false
benchmark_private: false
benchmark_distractor: false
created_at: "2026-06-01T00:00:00Z"
updated_at: "2026-06-20T00:00:00Z"
source_hash: "synthetic-benchmark"
edges: []
---

# Stale Conflict Target

The current authentication plan is passwordless sign-in with reviewed rollback notes and no legacy session rewrite.

## Benchmark Links

- none
