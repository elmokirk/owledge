---
memory_id: "mem:tenant-local:customer-local:agent-memory-standalone:evidence:poweruser-proof-generated-reports"
tenant_id: "tenant-local"
customer_id: "customer-local"
project_id: "agent-memory-standalone"
doc_type: "evidence"
status: "reviewed"
visibility: "private"
data_class: "internal"
semantic_title: "Poweruser Proof Generated Reports"
summary: "Generated local benchmark, chart, decision-trace, positioning, and cross-project-map artifacts from project-root tools."
concept_tags:
  - "generated-reports"
  - "benchmark-results"
  - "decision-tree"
stack_tags:
  - "python"
problem_patterns:
  - "unverified feature integration"
architecture_patterns:
  - "generated reports ignored by git"
failure_modes:
  - "stale report"
reusable_lessons: []
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-21T18:30:00Z"
updated_at: "2026-06-21T18:30:00Z"
retention_class: "standard"
stale_after: ""
expires_at: ""
last_reviewed_at: "2026-06-21T18:30:00Z"
review_cycle: "monthly"
source_hash: ""
edges:
  - target: "mem:tenant-local:customer-local:agent-memory-standalone:review:poweruser-proof-qa"
    type: "reviewed_by"
    reason: "The generated artifacts are checked through compile, memory validation, doctor, and docs tests."
---

# Poweruser Proof Generated Reports

Generated artifacts:

- `benchmarks/results/context-growth.json`
- `benchmarks/results/context-growth-charts.json`
- `benchmarks/results/token-efficiency.md`
- `agent-memory/reports/enterprise-context-benchmark/index.html`
- `agent-memory/decision-trace/trace.json`
- `agent-memory/reports/decision-trace/index.html`
- `agent-memory/reports/poweruser-positioning/index.html`
- `agent-memory/cross-project-hub/cross-project-map.json`
