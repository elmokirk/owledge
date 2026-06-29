---
memory_id: "mem:owledge:global:owledge:workpackage:v0.7.0-benchmark-comparison-publishing-proof-checklist"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "workpackage"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 benchmark comparison publishing proof checklist"
summary: "Agent-facing tasklist for the multi-model Benchmark Kit comparison report and publishing proof update."
concept_tags:
  - "phase-checklist"
  - "benchmark-kit"
  - "comparison-report"
stack_tags:
  - "python"
  - "markdown"
problem_patterns:
  - "checked-box-without-evidence"
  - "benchmark-proof-story-gap"
architecture_patterns:
  - "phase-gate"
  - "orchestrator-owned-tasklist"
failure_modes:
  - "parallel-model-execution"
  - "missing-output-evidence"
confidence: 0.94
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-29T00:00:00Z"
updated_at: "2026-06-29T00:00:00Z"
source_hash: ""
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:v0.7.0-benchmark-comparison-publishing-proof"
    confidence: 0.98
    reason: "This checklist operationalizes the benchmark comparison publishing proof plan."
---

# Owledge v0.7.0 Benchmark Comparison Publishing Proof Checklist

## Resume State

Current resume point: **Phase 6 - Final QA and Audience Evaluation**.

## Agent Rules

- Do not run local/cloud models in parallel.
- Do not fabricate optional model results.
- Check a box only when implementation and QA evidence exist.
- If report code changes, rerun `benchmark-kit-ci`.

## Phase 1 - Comparison Data Contract

- [x] Add comparison command that reads existing Benchmark Kit JSON reports.
- [x] Ensure comparison command does not call Ollama or run models.
- [x] Normalize baseline, Owledge, and oracle profile totals per model.
- [x] Phase 1 QA evidence recorded.

## Phase 2 - Comparison Renderer

- [x] Generate comparison JSON.
- [x] Generate comparison Markdown.
- [x] Generate comparison HTML.
- [x] Generate comparison SVG.
- [x] Phase 2 QA evidence recorded.

## Phase 3 - Expert-Level Report UX

- [x] Add Executive Verdict.
- [x] Add Creator Pull Quote.
- [x] Add Model Matrix.
- [x] Add Before vs Owledge charts.
- [x] Add Scenario Heatmap.
- [x] Add audience interpretation and caveats.
- [x] Phase 3 QA evidence recorded.

## Phase 4 - Sequential Release Evidence

- [x] Compare `gemma4:latest`, `qwen3.5:4b`, and `glm-5.1:cloud` release proof reports.
- [x] Document `nemotron-nano:cloud` as skipped if unavailable.
- [x] Confirm report folders are isolated and not overwritten.
- [x] Phase 4 QA evidence recorded.

## Phase 5 - Docs and README

- [x] Update README Benchmark Proof section.
- [x] Update `docs/benchmark-kit.md`.
- [x] Update `docs/try-owledge-in-5-minutes.md`.
- [x] Update roadmap boundary.
- [x] Phase 5 QA evidence recorded.

## Phase 6 - Final QA and Audience Evaluation

- [x] Run `benchmark-kit-ci`.
- [x] Run `private-path-clean`.
- [x] Run `public-docs`.
- [x] Run `publish-readiness`.
- [x] Record audience scorecard.

## Evidence

- Added `tools/benchmark-kit/compare-benchmark-runs.py` as an optional add-on
  command. It reads completed `latest.json` reports and does not call Ollama.
- `benchmark-kit-ci`: passed, 69 checks, including comparison JSON/MD/HTML/SVG
  outputs and required proof sections.
- Local comparison report created from:
  - `gemma4:latest`
  - `qwen3.5:4b`
  - `glm-5.1:cloud`
- Optional `nemotron-nano:cloud` input was skipped because no local report was
  available.
- Comparison result: release proof `pass`; 3/3 Owledge profiles passed;
  privacy failures prevented `3`; stale failures prevented `3`; average
  pollution reduction `88.36%`; average tokens/correct reduction `83.54%`.
- Generated local review report:
  `.agent-control/tmp/owledge-benchmark-release-proof/.owledge/reports/generated/benchmark-kit-comparison/index.html`.
- `private-path-clean`: passed with zero findings.
- `public-docs`: passed, 224 checks.
- `publish-readiness`: passed, score `110`, verdict `promote-candidate`.
