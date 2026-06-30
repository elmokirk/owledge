---
memory_id: "mem:owledge:global:owledge:benchmark-kit:profile"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "benchmark-profile"
status: "active"
visibility: "tenant"
data_class: "internal"
semantic_title: "Owledge Benchmark Kit Profile"
summary: "Local configuration profile for the optional Owledge Benchmark Kit add-on."
concept_tags:
  - "benchmark-kit"
  - "real-fixtures"
  - "context-pollution"
stack_tags:
  - "python"
  - "markdown"
problem_patterns:
  - "context-loss"
  - "retrieval-drift"
architecture_patterns:
  - "optional-addon"
  - "deterministic-fixture"
failure_modes:
  - "overfetching"
  - "private-context-leakage"
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-27T00:00:00Z"
updated_at: "2026-06-27T00:00:00Z"
source_hash: "benchmark-kit-v0.1"
edges: []
---

# Owledge Benchmark Kit Profile

This optional add-on creates synthetic Markdown fixture vaults and evaluates
how well an Owledge-style retrieval flow keeps useful context while avoiding
distractors, stale records, and private records.

Default scale mode: `small`.

Supported scale modes:

| Mode | Files |
| --- | ---: |
| `small` | 100 |
| `mid` | 500 |
| `large` | 1000 |
