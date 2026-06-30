---
memory_id: "mem:owledge:global:owledge:workpackage:v0.7.0-benchmark-kit-addon-real-fixtures"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "workpackage"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 benchmark kit add-on real fixtures checklist"
summary: "Agent checklist for implementing the optional Benchmark Kit add-on with real Markdown fixtures and fixing the local doctor smoke warning."
concept_tags:
  - "phase-checklist"
  - "benchmark-kit"
  - "doctor-smoke"
stack_tags:
  - "python"
  - "markdown"
  - "github-actions"
problem_patterns:
  - "benchmark-without-real-files"
  - "core-bloat"
architecture_patterns:
  - "optional-addon"
  - "phase-gate"
failure_modes:
  - "checkbox-without-evidence"
  - "generated-fixtures-tracked"
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-27T00:00:00Z"
updated_at: "2026-06-27T00:00:00Z"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:plan:v0.7.0-benchmark-kit-addon-real-fixtures"
    confidence: 0.95
    reason: "This checklist operationalizes the benchmark add-on implementation plan."
---

# Owledge v0.7.0 Benchmark Kit Add-on Real Fixtures Checklist

## Resume State

Current resume point: **Complete - final QA passed**.

## Phase 1 - Doctor Smoke Fix

- [x] Host-project `cli-local` check accepts an external installed Owledge CLI.
- [x] Active doctor fix text no longer mentions `agent_memory_cli.py`.
- [x] Smoke doctor score is 100 for a valid uvx/source-created host project.
- [x] Phase 1 QA gate passed.

## Phase 2 - Benchmark Add-on Consolidation

- [x] `addons/benchmark-kit/addon.json` exists.
- [x] `addons/benchmark-kit/README.md` exists.
- [x] `addons/benchmark-kit/BENCHMARK_EXPLAINED.md` exists.
- [x] `addons/benchmark-kit/tools/run-benchmark-kit.py` exists.
- [x] `addons/benchmark-kit/tools/render-benchmark-report.py` exists.
- [x] `addons/benchmark-kit/starter/.owledge/benchmark-kit/profile.md` exists.
- [x] Add-on install writes profile, explanation Markdown, docs, and scripts.
- [x] Phase 2 QA gate passed.

## Phase 3 - Real Markdown Fixture Benchmark

- [x] Scale mode `small` maps to 100 files.
- [x] Scale mode `mid` maps to 500 files.
- [x] Scale mode `large` maps to 1000 files.
- [x] Generated fixtures are real English Markdown files.
- [x] `queries.json` and `oracle.json` are generated.
- [x] Scenarios cover needle, multi-hop, stale-conflict, privacy-trap,
  distractor-heavy, and handoff-resume.
- [x] Generated fixture paths live under `.owledge/tmp/benchmark-kit/fixtures/`.
- [x] Phase 3 QA gate passed.

## Phase 4 - Power-User Metrics and Report UX

- [x] HTML summary shows total tokens.
- [x] HTML summary shows context pollution.
- [x] HTML summary shows duration and tokens/sec.
- [x] HTML summary shows privacy and stale failures.
- [x] HTML report links to `BENCHMARK_EXPLAINED.md`.
- [x] Markdown, JSON, JSONL, HTML, and SVG outputs are generated.
- [x] Phase 4 QA gate passed.

## Phase 5 - CI, Docs, and Release Gates

- [x] Active README describes Benchmark Kit as optional add-on.
- [x] Command reference uses add-on script commands.
- [x] Performance docs explain `small`, `mid`, and `large`.
- [x] Changelog notes benchmark add-on consolidation.
- [x] Release gate validates benchmark add-on manifest, explanation Markdown,
  install smoke, and CI report smoke.
- [x] Phase 5 QA gate passed.

## Final Verification

- [x] `python tools/owledge.py test public-docs --project-root .` passed.
- [x] `python tools/owledge.py test publish-readiness --project-root .` passed.
- [x] `python tools/owledge.py test legacy-naming-clean --project-root .` passed.
- [x] `python -m compileall -q tools addons/benchmark-kit` passed.
- [x] Local benchmark with `gemma4:latest` passed or environment limitation was documented.

## Evidence

- Doctor smoke: source-created host project scored `100`; `cli-local` passed
  with "Local or installed Owledge CLI is available."
- Add-on install smoke: installed `benchmark-kit` into an ignored temporary
  project under `.agent-control/tmp/`.
- Deterministic add-on gate: `python tools/owledge.py test benchmark-kit-ci
  --project-root .` passed with 20 checks.
- Public docs: `python tools/owledge.py test public-docs --project-root .`
  passed with 224 checks.
- Launch readiness: `python tools/owledge.py test launch-readiness
  --project-root .` passed with 78 checks.
- Publish readiness: `python tools/owledge.py test publish-readiness
  --project-root .` passed with score `100` and verdict `promote-candidate`.
- Local benchmark smoke: `gemma4:latest`, `small`, 100 files, passed; total
  tokens `32662`, context pollution `0.2737`, avg tokens/sec `61.1641`,
  duration `202602ms`; HTML and SVG reports were generated.
