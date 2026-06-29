---
memory_id: "mem:owledge:global:owledge:plan:v0.7.0-final-publishing-quality"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "plan"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 final publishing quality plan"
summary: "Final publishing polish plan for benchmark verdicts, embedded charts, private path leak gates, demo readiness, and release artifact hygiene."
concept_tags:
  - "publishing-quality"
  - "v0.7.0"
  - "benchmark-kit"
  - "private-path-gate"
  - "release-artifacts"
stack_tags:
  - "python"
  - "markdown"
  - "uv"
  - "pypi"
problem_patterns:
  - "benchmark-metrics-without-interpretation"
  - "private-path-leak"
  - "dirty-worktree-before-publish"
  - "demo-story-gap"
architecture_patterns:
  - "phase-gate"
  - "optional-addon"
  - "release-surface-gate"
failure_modes:
  - "publish-with-private-local-path"
  - "benchmark-report-unclear-to-power-users"
  - "stale-generated-build-artifacts"
confidence: 0.93
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-27T00:00:00Z"
updated_at: "2026-06-27T00:00:00Z"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:plan:v0.7.0-final-release-focus"
    confidence: 0.95
    reason: "This plan adds the final publishing polish layer after the release focus plan."
  - type: "derived_from"
    target: "mem:owledge:global:owledge:plan:v0.7.0-benchmark-kit-addon-real-fixtures"
    confidence: 0.9
    reason: "Benchmark interpretation builds on the optional Benchmark Kit add-on."
---

# Owledge v0.7.0 Final Publishing Quality Plan

## Goal

Cut a high-quality public v0.7.0 release with no private-path leaks, readable
Benchmark Kit verdicts, embedded benchmark charts, and a compact creator-ready
demo story.

## Locked Scope

- Benchmark Kit remains an optional add-on, not a core install claim.
- Benchmark reports must tell users whether a result is good, mixed, or bad.
- Active release files must not contain real user paths such as
  `C:\Users\USERPATH\...` with a real username in place of `USERPATH`.
- If a user path is necessary in docs or fixtures, use placeholders:
  `C:\Users\USERPATH\...`, `C:/Users/USERPATH/...`, or `/Users/USERPATH/...`.
- HyperFrames launch video planning is valuable, but not a package publishing
  blocker.

## Phase 1 - Benchmark Verdict and Interpretation

Objective: make Benchmark Kit output readable for power users and non-research
reviewers.

Tasks:

- Add top-level verdict: `pass`, `warn`, or `fail`.
- Add conclusion copy explaining whether the run is good, mixed, or bad.
- Add metric bands for context pollution, privacy failures, stale failures,
  failed scenarios, and tokens per correct answer.
- Add scenario-level pass/warn/fail status labels.
- Move practical metrics above detailed research tables.
- Add "What This Means" explanations for token usage, pollution, failures,
  performance, and duration.

QA gate:

```powershell
python tools\owledge.py test benchmark-kit-ci --project-root .
```

Metric target:

- Benchmark Kit CI gate passes.
- HTML and Markdown include `Verdict`, `Conclusion`, `Tokens per correct answer`,
  `Context pollution`, `Privacy failures`, and `Stale failures`.

## Phase 2 - Embedded Benchmark Charts

Objective: make the generated HTML report self-contained enough for manual
review and demos.

Tasks:

- Continue generating standalone `charts.svg`.
- Embed the generated SVG inline inside `index.html`.
- Add chart captions that state metric direction, for example lower pollution
  is better and higher tokens/sec is better.
- Keep release/demo links relative where possible.

QA gate:

```powershell
python tools\owledge.py test benchmark-kit-ci --project-root .
```

Metric target:

- Benchmark Kit HTML contains embedded `<svg`.
- Standalone `charts.svg` is still generated.

## Phase 3 - Private Path Leak Gate

Objective: prevent local private paths from entering public release artifacts.

Tasks:

- Add a gate for active publishable files that blocks:
  - `C:\Users\<real-user>`
  - `C:/Users/<real-user>`
  - `/Users/<real-user>`
- Allow explicit placeholders such as `C:\Users\USERPATH\...`.
- Ignore `.git/`, `.agent-control/`, `.pytest_cache/`, generated benchmark
  outputs, and local smoke artifacts.
- Add the gate to publish readiness.
- Sanitize Benchmark Kit shared report fields such as project root and fixture
  directories.

QA gate:

```powershell
python tools\owledge.py test private-path-clean --project-root .
python tools\owledge.py test publish-readiness --project-root .
```

Metric target:

- `private-path-clean` has zero findings.
- `publish-readiness` remains `promote-candidate`.

## Phase 4 - Demo Story Readiness

Objective: define a compact launch narrative without blocking package release.

Demo narrative:

1. Agent starts without durable memory and loses continuity.
2. Owledge initializes `OWLEDGE.md` and `.owledge/`.
3. Agent writes plan, tasklist, review, and handoff.
4. A new agent resumes from Owledge context and passes `doctor`.
5. Optional Benchmark Kit validates retrieval traps, context pollution, stale and
   private records, and handoff resume with real Markdown fixtures.

HyperFrames direction:

- Use the provided engineered sci-fi dark visual identity.
- Avoid AI-purple gradients, gradient text, and heavy glassmorphism.
- Use square, precise, instrumentation-like scenes with readable captions.
- Treat the video as a launch asset after v0.7.0 artifacts are stable.

QA gate:

```powershell
python tools\owledge.py test launch-readiness --project-root .
```

Metric target:

- Launch readiness remains green.
- Demo story stays compact and not feature-catalog shaped.

## Phase 5 - Final Artifact Hygiene

Objective: build releasable artifacts from the current implementation while
keeping generated state under control.

Tasks:

- Remove stale generated build intermediates before building.
- Build sdist and wheel.
- Run metadata checks when `twine` is available.
- Run wheel-based `uvx` smoke from a clean temp project.
- Run private path scan against active files and built artifacts.
- Keep `dist/` artifacts for manual publishing review.

QA gate:

```powershell
python -m compileall -q tools addons\benchmark-kit plugins\owledge-cowork
python -m build
python -m twine check dist\*
uvx --from dist\owledge-0.7.0-py3-none-any.whl owledge --help
uvx --from dist\owledge-0.7.0-py3-none-any.whl owledge quickstart --target C:\tmp\owledge-v070-final-smoke
uvx --from dist\owledge-0.7.0-py3-none-any.whl owledge doctor --project-root C:\tmp\owledge-v070-final-smoke
```

Metric target:

- Wheel and sdist exist.
- Wheel `uvx` help, quickstart, and doctor pass.
- Doctor score is `100` for a valid wheel-created smoke project.
- Built artifacts contain no real private user path.

## Current Evidence

- `public-docs`: passed, 224 checks.
- `publish-readiness`: passed, score 110, verdict `promote-candidate`.
- `release-trust`: passed.
- `legacy-naming-clean`: passed.
- `private-path-clean`: passed with zero findings.
- `benchmark-kit-ci`: passed, 36 checks.
- Wheel-based `uvx` help, quickstart, and doctor smoke passed.
- `twine check` remains pending in an environment with `twine` installed.
