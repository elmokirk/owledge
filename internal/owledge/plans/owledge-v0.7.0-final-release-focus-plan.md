---
memory_id: "mem:owledge:global:owledge:plan:v0.7.0-final-release-focus"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "plan"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 final release focus plan"
summary: "Final focus plan for cutting the v0.7.0 release after the Benchmark Kit add-on, smoke doctor fix, docs, and publish readiness gates have passed."
concept_tags:
  - "release-focus"
  - "v0.7.0"
  - "publish-readiness"
  - "agent-native-roadmap"
stack_tags:
  - "python"
  - "uv"
  - "pypi"
  - "markdown"
problem_patterns:
  - "dirty-worktree-before-release"
  - "artifact-not-verified"
  - "demo-gap"
architecture_patterns:
  - "phase-gate"
  - "optional-addon"
  - "agent-runtime-contract"
failure_modes:
  - "publish-without-wheel-smoke"
  - "overclaiming-runtime-readiness"
  - "unclear-demo-story"
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-27T00:00:00Z"
updated_at: "2026-06-27T00:00:00Z"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:plan:v0.7.0-final-publishing-95-release-cut"
    confidence: 0.95
    reason: "This plan narrows the final publishing cut to release execution and post-release focus."
  - type: "derived_from"
    target: "mem:owledge:global:owledge:workpackage:v0.7.0-benchmark-kit-addon-real-fixtures"
    confidence: 0.9
    reason: "The Benchmark Kit add-on implementation is complete and now feeds the final release proof."
---

# Owledge v0.7.0 Final Release Focus Plan

## Goal

Cut v0.7.0 only after the release artifacts, install path, final docs, demo story,
and publish evidence are coherent. The current implementation has passed the
major publish readiness gates, but the worktree is intentionally large and must
be converted into a disciplined release artifact before publication.

## Locked Release Scope

- `.owledge/` and `OWLEDGE.md` are the public memory contract.
- The core package stays lightweight.
- Benchmark Kit is an optional add-on with real synthetic Markdown fixtures.
- Read-only MCP, Wikilink Audit, Native Planning Layers, Standalone Skills, and
  release gates are included in v0.7.0.
- Harness benchmarks, PI Agent runtime adapter, write-enabled MCP, cloud/frontier
  benchmark matrix, own-vault benchmarking, RAG integrations, Hermes adapter, and
  marketplace certification stay roadmap unless explicitly implemented later.

## Phase 1 - Release Artifact Cut

Objective: turn the current implementation into a verifiable package candidate.

Tasks:

- Review `git status --short` and separate intentional v0.7.0 changes from
  generated or accidental artifacts.
- Build sdist and wheel.
- Run `twine check` against the built artifacts.
- Run wheel-based `uvx` smoke commands from a clean temp project.
- Confirm `owledge doctor` scores 100 on the fresh project.

QA gate:

```powershell
python -m build
python -m twine check dist\*
uvx --from dist\owledge-0.7.0-py3-none-any.whl owledge --help
uvx --from dist\owledge-0.7.0-py3-none-any.whl owledge quickstart --target C:\tmp\owledge-v070-final-smoke
uvx --from dist\owledge-0.7.0-py3-none-any.whl owledge doctor --project-root C:\tmp\owledge-v070-final-smoke
```

Done when:

- Wheel and sdist pass metadata checks.
- Fresh install smoke creates `OWLEDGE.md` and `.owledge/`.
- Doctor passes with score 100.

## Phase 2 - Final Gate Sweep

Objective: prove the public contract and docs still match the implementation.

Tasks:

- Run publish readiness, release trust, public docs, legacy naming, private path,
  Wikilink Audit, and Benchmark Kit CI gates.
- Confirm no active docs present old benchmark commands or old public naming.
- Confirm no active release files contain real local user paths such as
  `C:\Users\<real-user>`, `C:/Users/<real-user>`, or `/Users/<real-user>`;
  use placeholders such as `C:\Users\USERPATH\...` when examples need a user path.
- Confirm the Benchmark Kit remains optional and add-on based.
- Confirm Benchmark Kit HTML and Markdown reports include a verdict, conclusion,
  scenario pass/warn/fail states, and embedded SVG charts.

QA gate:

```powershell
python tools\owledge.py test publish-readiness --project-root .
python tools\owledge.py test public-docs --project-root .
python tools\owledge.py test release-trust --project-root .
python tools\owledge.py test legacy-naming-clean --project-root .
python tools\owledge.py test private-path-clean --project-root .
python tools\owledge.py wikilink-audit --project-root . --check
python tools\owledge.py test benchmark-kit-ci --project-root .
```

Done when:

- Publish readiness is at least 95.
- Legacy naming has zero active findings.
- Private path scan has zero active findings.
- Public docs and release trust pass.
- Wikilink Audit has zero broken or ambiguous links.

## Phase 3 - Local Proof Assets

Objective: prepare proof that a creator, power user, or reviewer can inspect.

Tasks:

- Run one small local Benchmark Kit run with an installed local model such as
  `gemma4:latest`.
- Preserve paths to `latest.md`, `latest.json`, `index.html`, `charts.svg`, and
  the generated fixture vault.
- Create a short demo outline showing the before/after memory handoff story.

Recommended demo story:

1. Agent starts with no durable memory and loses project continuity.
2. Owledge quickstart creates `OWLEDGE.md` and `.owledge/`.
3. Agent writes a plan, tasklist, review, and handoff.
4. A new agent resumes from the handoff and passes `doctor`.
5. Optional Benchmark Kit proves retrieval, context pollution, privacy, stale,
   and handoff-resume behavior with generated Markdown fixtures.

QA gate:

```powershell
python tools\owledge.py install-addon --project-root C:\tmp\owledge-demo-benchmark --addon benchmark-kit
cd C:\tmp\owledge-demo-benchmark
python tools\benchmark-kit\run-benchmark-kit.py --mode local --scale-mode small --models gemma4:latest --yes
python tools\benchmark-kit\render-benchmark-report.py --format html
```

Done when:

- HTML and SVG reports exist.
- Metrics include total tokens, context pollution, tokens/sec, privacy failures,
  stale failures, and scale mode.
- Demo outline has a clear 5-minute narrative.

## Phase 4 - Release Notes and Tag

Objective: publish with clear scope and no overclaims.

Tasks:

- Finalize `CHANGELOG.md`.
- Confirm `VERSION`, README badge, plugin versions, and package metadata match.
- Draft release notes focused on the v0.7.0 public contract.
- Tag only after final gates pass.

QA gate:

```powershell
python tools\owledge.py test release-trust --project-root .
git status --short
```

Done when:

- No generated benchmark fixtures are staged.
- Release notes clearly mark roadmap boundaries.
- The tag is created only after artifact and gate evidence is recorded.

## Post-v0.7.0 Focus

| Priority | Track | Why next | Done Definition |
| ---: | --- | --- | --- |
| 1 | CLI UX simplification | Reduces install friction for non-expert users and agent-assisted installs. | `owledge init`, `owledge add`, and `owledge benchmark` aliases work and are documented. |
| 2 | Agent-native runtime contract | Makes Owledge easier for Claude Code, Codex, OpenCode, Zed, Cursor, and PI Agent to consume efficiently. | Contract doc, fixtures, and conformance gate exist. |
| 3 | PI Agent runtime adapter | PI Agent may be a strong lightweight runtime if it stays deterministic and plugin-friendly. | Adapter passes runtime conformance and preserves `.owledge/` as canonical truth. |
| 4 | Harness benchmarks | Converts agent-native claims into evidence. | Claude Code, Codex, and OpenCode reports exist first. |
| 5 | Own-vault benchmark mode | Lets power users measure their real project without synthetic-only caveats. | Local privacy-safe benchmark mode with redaction and no upload. |
| 6 | Write-enabled MCP | Adds real automation power but must be gated carefully. | Scoped writes, locks, audit log, rollback, and privacy tests. |
| 7 | RAG integrations | Opens team and enterprise knowledge workflows. | Export adapters preserve Markdown as canonical layer. |
| 8 | Demo/video launch assets | Improves adoption and creator shareability. | 5-minute demo script plus optional HyperFrames video composition. |

## Demo Recommendation

HyperFrames can cover the launch demo well if used as a short product-story
video: show context loss, Owledge initialization, structured `.owledge/`
artifacts, agent resume, and benchmark proof. Do not make the first demo a
feature catalog. The strongest narrative is: "the agent forgets, Owledge gives
the project a durable operating memory, the next agent resumes with evidence."
