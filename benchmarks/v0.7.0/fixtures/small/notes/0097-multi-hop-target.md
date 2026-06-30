---
memory_id: "mem:benchmark:synthetic:owledge:plan:multi-hop-target-0000-9dcc00ef56"
tenant_id: "benchmark"
customer_id: "synthetic"
project_id: "owledge-benchmark"
doc_type: "plan"
status: "active"
visibility: "tenant"
data_class: "internal"
semantic_title: "Multi Hop Target"
summary: "Synthetic target record for the multi-hop benchmark scenario."
concept_tags:
  - "benchmark"
  - "multi-hop"
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
benchmark_scenario: "multi-hop"
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

# Multi Hop Target

The billing migration plan depends on reviewed evidence A and reviewed decision B. The implementation should follow both linked notes.

## Benchmark Links

- [[0085-multi-hop-support-a]]
- [[0061-multi-hop-support-b]]
