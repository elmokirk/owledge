---
memory_id: "mem:owledge:global:owledge:plan:v0.7.0-benchmark-comparison-publishing-proof"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "plan"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 benchmark comparison publishing proof plan"
summary: "Implement a multi-model Benchmark Kit comparison report that turns baseline-vs-Owledge results into a publishing-ready proof story."
concept_tags:
  - "benchmark-kit"
  - "publishing-proof"
  - "comparison-report"
  - "v0.7.0"
stack_tags:
  - "python"
  - "markdown"
  - "html"
problem_patterns:
  - "single-run-benchmark-lacks-comparison"
  - "poweruser-proof-story-gap"
  - "creator-demo-needs-before-after"
architecture_patterns:
  - "optional-addon"
  - "generated-report"
  - "sequential-local-benchmark"
failure_modes:
  - "parallel-local-model-runs"
  - "fabricated-missing-model-results"
  - "oracle-confused-with-product-claim"
confidence: 0.94
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-29T00:00:00Z"
updated_at: "2026-06-29T00:00:00Z"
source_hash: ""
edges:
  - type: "extends"
    target: "mem:owledge:global:owledge:plan:v0.7.0-final-publishing-quality"
    confidence: 0.95
    reason: "This plan adds the multi-model benchmark comparison proof layer requested after final publishing polish."
---

# Owledge v0.7.0 Benchmark Comparison Publishing Proof Plan

## Goal

Add a multi-model comparison report to the optional Benchmark Kit so release
evidence shows baseline vs Owledge improvements across local and cloud model
tiers.

## Phases

| Phase | Goal | DoD | QA Gate |
| ---: | --- | --- | --- |
| 1 | Comparison data contract | Comparison command reads two or more existing `latest.json` files and never calls Ollama. | Fixture inputs parse and produce normalized rows. |
| 2 | Comparison renderer | JSON, Markdown, HTML, and SVG comparison outputs are generated. | Output files exist and include all input models. |
| 3 | Expert-level report UX | Report includes executive verdict, creator pull quote, model matrix, charts, heatmap, audience interpretation, and caveats. | First screen explains what improved. |
| 4 | Sequential release evidence | Existing local/cloud model reports are compared; missing optional Nemotron is documented if absent. | No overwritten report folders; comparison report renders. |
| 5 | Docs and README | Public docs explain single-run vs comparison reports, model tiers, and sequential execution. | `public-docs`, `private-path-clean`, `publish-readiness`. |
| 6 | Audience QA | Poweruser, AI YouTuber, expert, researcher, and architect acceptance criteria are explicit. | Audience scorecard is present in report/docs. |

## Locked Decisions

- The comparison command only reads completed Benchmark Kit JSON outputs.
- Local/cloud benchmarks are run sequentially outside the comparison command.
- `gemma4:latest`, `qwen3.5:4b`, and `glm-5.1:cloud` are release proof inputs when available.
- `nemotron-nano:cloud` is optional; absence is a documented skip, not a blocker.
- Oracle is described as ground-truth reference, not a model or product claim.

## Current Evidence

- `benchmark-kit-ci`: passed, 69 checks.
- `private-path-clean`: passed with zero findings.
- `public-docs`: passed, 224 checks.
- `publish-readiness`: passed, score `110`, verdict `promote-candidate`.
- Local comparison proof: 3/3 Owledge profiles passed across `gemma4:latest`,
  `qwen3.5:4b`, and `glm-5.1:cloud`; average context pollution reduction
  `88.36%`; average tokens/correct reduction `83.54%`.
