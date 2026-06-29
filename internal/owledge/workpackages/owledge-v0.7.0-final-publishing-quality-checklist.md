---
memory_id: "mem:owledge:global:owledge:workpackage:v0.7.0-final-publishing-quality-checklist"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "workpackage"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 final publishing quality checklist"
summary: "Agent-facing checklist for final v0.7.0 publishing polish, benchmark interpretation, private path gates, demo readiness, and artifact hygiene."
concept_tags:
  - "phase-checklist"
  - "publishing-quality"
  - "benchmark-kit"
  - "private-path-gate"
stack_tags:
  - "python"
  - "markdown"
  - "uv"
problem_patterns:
  - "benchmark-report-unclear"
  - "private-path-leak"
  - "artifact-hygiene"
architecture_patterns:
  - "phase-gate"
  - "orchestrator-owned-tasklist"
failure_modes:
  - "checked-box-without-evidence"
  - "twine-check-skipped-without-note"
confidence: 0.92
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-27T00:00:00Z"
updated_at: "2026-06-27T00:00:00Z"
source_hash: ""
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:v0.7.0-final-publishing-quality"
    confidence: 0.98
    reason: "This checklist operationalizes the final publishing quality plan."
---

# Owledge v0.7.0 Final Publishing Quality Checklist

## Resume State

Current resume point: **Phase 5 - Final Artifact Hygiene / twine check pending**.

## Agent Rules

- Orchestrator owns this checklist.
- Check a box only when implementation and QA evidence exist.
- If later edits touch Benchmark Kit reporting, rerun `benchmark-kit-ci`.
- If later edits touch release files, rerun `private-path-clean` and
  `publish-readiness`.
- If later edits touch package metadata, rebuild the wheel and sdist.

## Phase 1 - Benchmark Verdict and Interpretation

Goal: make benchmark results understandable without reading raw JSON.

Checklist:

- [x] Add top-level `pass`, `warn`, or `fail` verdict.
- [x] Add conclusion copy to Markdown and HTML reports.
- [x] Add metric bands for pollution, privacy, stale, failed scenarios, and
  token usage.
- [x] Add scenario-level status labels.
- [x] Add "What This Means" explanations.
- [x] Phase 1 QA gate passed.

QA gate:

```powershell
python tools\owledge.py test benchmark-kit-ci --project-root .
```

Evidence:

- `benchmark-kit-ci`: passed, 36 checks.

## Phase 2 - Embedded Benchmark Charts

Goal: make the HTML report visually self-contained for review and demos.

Checklist:

- [x] Continue writing standalone `charts.svg`.
- [x] Embed SVG inline in `index.html`.
- [x] Add readable chart captions and metric direction hints.
- [x] Keep Benchmark Kit output paths share-safe.
- [x] Phase 2 QA gate passed.

QA gate:

```powershell
python tools\owledge.py test benchmark-kit-ci --project-root .
```

Evidence:

- Benchmark HTML contains embedded `<svg`.
- Standalone `charts.svg` exists in generated Benchmark Kit reports.

## Phase 3 - Private Path Leak Gate

Goal: block private user paths from active release surfaces.

Checklist:

- [x] Add `private-path-clean` release gate.
- [x] Block real Windows and Unix/macOS user paths.
- [x] Allow explicit `USERPATH` placeholders.
- [x] Add private path gate to publish readiness.
- [x] Sanitize Benchmark Kit shared report paths.
- [x] Phase 3 QA gate passed.

QA gate:

```powershell
python tools\owledge.py test private-path-clean --project-root .
python tools\owledge.py test publish-readiness --project-root .
```

Evidence:

- `private-path-clean`: passed with zero findings.
- `publish-readiness`: passed, score 110, verdict `promote-candidate`.

## Phase 4 - Demo Story Readiness

Goal: keep the launch demo focused and creator-ready without blocking the
package cut.

Checklist:

- [x] Define compact five-step demo narrative.
- [x] Keep HyperFrames as launch asset after artifacts are stable.
- [x] Preserve dark engineered sci-fi visual direction.
- [x] Phase 4 QA gate passed.

QA gate:

```powershell
python tools\owledge.py test launch-readiness --project-root .
```

Evidence:

- `launch-readiness` passed as part of `publish-readiness`.

## Phase 5 - Final Artifact Hygiene

Goal: produce verified package artifacts and record remaining publishing work.

Checklist:

- [x] Remove stale generated build intermediates before the final artifact build.
- [x] Build fresh wheel and sdist.
- [x] Run wheel-based `uvx --help` smoke.
- [x] Run wheel-based `quickstart` smoke.
- [x] Run wheel-based `doctor` smoke.
- [x] Confirm wheel-created smoke project reaches doctor score `100`.
- [x] Scan built artifacts for private path leaks.
- [ ] Run `python -m twine check dist\*` in an environment with `twine`
  installed.
- [ ] Do final manual review of generated Benchmark Kit HTML.
- [ ] Commit or otherwise freeze the v0.7.0 release candidate before tagging.

QA gate:

```powershell
python -m compileall -q tools addons\benchmark-kit plugins\owledge-cowork
python -m build
python -m twine check dist\*
uvx --from dist\owledge-0.7.0-py3-none-any.whl owledge --help
uvx --from dist\owledge-0.7.0-py3-none-any.whl owledge quickstart --target C:\tmp\owledge-v070-final-smoke
uvx --from dist\owledge-0.7.0-py3-none-any.whl owledge doctor --project-root C:\tmp\owledge-v070-final-smoke
```

Evidence:

- Built artifacts:
  - `dist/owledge-0.7.0-py3-none-any.whl`
  - `dist/owledge-0.7.0.tar.gz`
- Wheel `uvx` help, quickstart, and doctor smoke passed.
- Built artifact private-path scan passed.
- `twine check` is pending because `twine` is not installed in the current
  restricted environment.
