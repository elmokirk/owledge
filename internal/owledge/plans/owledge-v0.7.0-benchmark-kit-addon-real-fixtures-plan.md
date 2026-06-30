---
memory_id: "mem:owledge:global:owledge:plan:v0.7.0-benchmark-kit-addon-real-fixtures"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "plan"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 benchmark kit add-on with real Markdown fixtures"
summary: "Implementation plan for moving Benchmark Kit V2 into an optional add-on with real synthetic Markdown fixtures, power-user metrics, and the local doctor smoke fix."
concept_tags:
  - "benchmark-kit"
  - "release-readiness"
  - "real-fixtures"
  - "doctor-smoke"
stack_tags:
  - "python"
  - "markdown"
  - "github-actions"
problem_patterns:
  - "benchmark-without-real-files"
  - "core-bloat"
  - "stale-doctor-copy"
architecture_patterns:
  - "optional-addon"
  - "deterministic-fixtures"
  - "generated-report"
failure_modes:
  - "synthetic-benchmark-overclaim"
  - "generated-fixtures-tracked"
  - "core-docs-overclaim-addons"
confidence: 0.92
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-27T00:00:00Z"
updated_at: "2026-06-27T00:00:00Z"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:plan:v0.7.0-final-publishing-95-release-cut"
    confidence: 0.9
    reason: "This plan implements the final benchmark and smoke-test follow-up required before publishing."
---

# Owledge v0.7.0 Benchmark Kit Add-on + Smoke Test Fix Plan

## Summary

Implement the v0.7.0 benchmark as a dedicated optional `benchmark-kit`
add-on. The add-on generates real English Markdown fixture vaults, runs
deterministic and local Ollama tests against those files, and emits Markdown,
JSON, HTML, and SVG reports focused on token usage, performance, and context
pollution.

Also fix the host-project doctor warning for uvx/installed CLI usage by making
local project tools optional when an external Owledge CLI is running the check.

## Decisions

- Add-on name: `benchmark-kit`.
- Active benchmark surface consolidates around `addons/benchmark-kit/`.
- `pilot-benchmark-kit` and `enterprise-context-benchmark-kit` are no longer
  promoted in active public docs.
- Public scale modes are `small`, `mid`, and `large`.
- `xl`, 10k files, external datasets, cloud/frontier benchmark matrices, and
  own-vault benchmarking are post-v0.7 roadmap items.
- Benchmark content and documentation are English-only.
- Generated fixtures, raw result files, and generated reports are ignored by
  default.

## Phase Gates

1. Doctor smoke fix: `doctor` scores 100 for a valid uvx-created host project.
2. Add-on install: `benchmark-kit` installs scripts, profile, and explanation
   Markdown into a temporary host project.
3. Fixture benchmark: `small` creates real Markdown fixtures, `queries.json`,
   `oracle.json`, result exports, HTML, and SVG.
4. Local benchmark: one selected Ollama model runs sequentially and records
   token, speed, and context pollution metrics.
5. Docs/gates: active docs describe Benchmark Kit as optional and release gates
   verify the add-on surface without making it core.
