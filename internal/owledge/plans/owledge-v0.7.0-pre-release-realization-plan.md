---
memory_id: "mem:owledge:global:owledge:plan:v0.7.0-pre-release-realization"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "plan"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 pre-release realization plan"
summary: "Implementation plan for the Owledge v0.7.0 pre-release: .owledge root migration, OWLEDGE.md entrypoint, release gates, packaging, read-only MCP, native planning layers, wikilink audit, benchmark kit, final docs, and verification."
concept_tags:
  - "release-readiness"
  - "owledge-v0.7.0"
  - "root-migration"
  - "mcp"
  - "benchmark-kit"
  - "wikilink-audit"
  - "planning-layer"
  - "docs"
stack_tags:
  - "python"
  - "markdown"
  - "github-actions"
problem_patterns:
  - "contract-gate-root-mismatch"
  - "docs-package-mismatch"
  - "owledge-brand-drift"
  - "source-checkout-first-docs"
architecture_patterns:
  - "markdown-first-memory"
  - "git-native-memory"
  - "read-only-adapter"
  - "candidate-before-promotion"
failure_modes:
  - "public-release-with-failing-contracts"
  - "docs-overclaim-unimplemented-interface"
  - "mcp-private-data-leak"
  - "benchmark-local-resource-overload"
  - "parallel-subagent-plan-conflict"
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-26T00:00:00Z"
updated_at: "2026-06-26T00:00:00Z"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:session:release-sparring-2026-06-26"
---

# Owledge v0.7.0 Pre-Release Realization Plan

## Objective

Make Owledge publish-ready for an international audience of power users, AI
creators, agent builders, and developer communities.

Public v0.7.0 contract:

- `.owledge/` is the canonical project memory root.
- `OWLEDGE.md` replaces `OWLEDGE.md` as the visible user and agent
  entrypoint.
- Public docs are `uvx` / `uv tool install` first, not source-checkout first.
- Read-only MCP, Wikilink Audit, Native Planning Layers, and Benchmark Kit V2
  are P0.
- Harness benchmarks, Hermes, write-enabled MCP, RAG integrations, marketplace
  certification, and the cloud/frontier benchmark matrix are roadmap items.

This plan is stored in the current dogfood memory root
`internal/owledge/plans/`. Phase 1 must migrate active dogfood plans to the
new `.owledge/plans/` shape once the v0.7.0 root exists.

## Current Verified State

- `release-trust` is green for v0.6.1.
- `public-docs` is green, but it still encodes old documentation assumptions.
- `concept-audit` score is 7.2.
- `contracts` score is 5.
- `test-contracts` fails with 89 checks because contracts still expect the old
  `.owledge/` root.
- README, Roadmap, packaging, command docs, and templates still reference
  `.owledge/`, `OWLEDGE.md`, source-checkout-first commands, and
  v0.5/v0.6 framing.
- CI exists, but it validates the v0.6.1 surface rather than the v0.7.0 release
  contract.

## Critical Findings

| Problem | Severity | Required Fix |
| --- | ---: | --- |
| Contracts expect the old root structure | 10 | Block Phase 1 until contracts and gates validate `.owledge/` and `OWLEDGE.md`. |
| Public naming is not fully migrated | 9 | Make the public contract Owledge-first; keep legacy names only as internal or compatibility shims. |
| Packaging points at `templates/owledge` | 9 | Migrate package data, MANIFEST, wheel/sdist, and smoke tests to the v0.7.0 package surface. |
| CI does not test the new release surface | 9 | Add `.owledge` fresh install, MCP smoke, wikilink audit, benchmark-kit CI, and wheel/uvx smoke gates. |
| Docs must be last | 9 | Finalize docs only after MCP, native planning, wikilink audit, and benchmark kit interfaces exist. |
| MCP may leak private/generated data | 8 | Scope read-only MCP to project root and reviewed/tracked artifacts; add a privacy boundary test. |
| Local benchmarks must not overload CI or users | 8 | Keep `ci` deterministic and model-free; make `local` opt-in and sequential. |
| Generated exports can pollute release diffs | 7 | Fix generated-state policy before feature work; ignore generated/private outputs by default. |
| Subagents can collide on central files | 7 | Use lane handoffs; only the orchestrator edits the central plan, README merge, CI merge, and release notes. |

## Phase Plan

| Phase | Goal | Subagent Lanes | Done Definition | QA Gate |
| ---: | --- | --- | --- | --- |
| 0 | Branch and baseline | Orchestrator | Branch `codex/owledge-v0.7-pre-release`; dirty state and baseline gates recorded | `git status --short`; baseline concept-audit, release-trust, public-docs, test-contracts |
| 1 | `.owledge/` foundation | Migration, Contracts | Init and quickstart create `.owledge/` and `OWLEDGE.md`; no public dependency on `OWLEDGE.md` | quickstart, doctor, test-contracts, finalization-gates |
| 2 | Generated-state policy | Migration, QA | Private/generated paths ignored; durable plans/reviews/handoffs/audiences/research are trackable | Gitignore gate; no generated diff except explicit release evidence |
| 3 | Packaging and CLI parity | Packaging | Wheel/sdist include the new templates, skills, plugins, and core add-ons or claims are reduced | build, twine check, wheel smoke, `uvx owledge --help`, `uvx owledge quickstart` |
| 4 | CI release gates | CI, QA | CI validates v0.7.0 contracts rather than the v0.6.1 surface | core matrix, release-gates, docs workflow, release workflow |
| 5 | Read-only MCP P0 | MCP | MCP tools expose entrypoint, doctor, search, context pack, tasks, and reviews; no write tools | stdio smoke, privacy boundary test, runtime-adapters gate |
| 6 | Native planning layers | Planning | `.owledge/reviews`, `.owledge/audiences`, `.owledge/research`, and Brainstorm skill/spec exist | schema/template validation, review workflow smoke, concept-audit |
| 7 | Wikilink Audit | Wikilinks | Read-only audit for valid, broken, and ambiguous `[[Wiki Links]]`; candidate edges only | valid/broken/ambiguous fixtures |
| 8 | Benchmark Kit V2 | Benchmark | `ci` deterministic; `local` scans Ollama tags, asks model choice, runs sequentially; HTML first | JSON/MD/HTML/SVG outputs, stable metrics, chart-label checks |
| 9 | Runtime/add-on boundary | Packaging, Runtime | Core add-ons/plugins install or public claims are reduced; harness/cloud/Hermes deferrals are clear | add-on smoke, runtime conformance, no-overclaim gate |
| 10 | Final docs and launch surface | Docs writer, Docs red-team | README, docs, command reference, roadmap, troubleshooting, Mermaid workflows, and links are final | public-docs, release-trust, stale-claim gate, docs red-team score >= 90 |
| 11 | Final verification | Orchestrator, QA | v0.7.0 release candidate is publish-ready | all gates green, concept-audit >= 8.5, contracts = 10 |

## Target Project Shape

```text
OWLEDGE.md
.owledge/context/
.owledge/plans/
.owledge/tasks/
.owledge/workpackages/
.owledge/handoffs/
.owledge/decisions/
.owledge/reviews/
.owledge/audiences/
.owledge/research/
.owledge/templates/
.owledge/schemas/
.owledge/indexes/
.owledge/exports/
.owledge/reports/generated/
.owledge/tmp/
.owledge/cache/
```

Track durable knowledge by default:

- context
- plans
- tasks
- workpackages
- decisions
- reviews
- audiences
- research briefs/findings/syntheses
- curated handoffs

Ignore generated and private state by default:

- tmp
- cache
- raw sessions
- generated indexes
- generated exports
- generated reports

## Public Interfaces

```bash
uvx owledge --help
uvx owledge quickstart --target <path>
uv tool install owledge
owledge doctor --project-root <path>
owledge wikilink-audit --project-root .
owledge benchmark-kit run --mode ci
owledge benchmark-kit run --mode local
owledge benchmark-kit report --format html
```

Read-only MCP P0 tools:

- `owledge_read_entrypoint`
- `owledge_doctor`
- `owledge_search_memory`
- `owledge_build_context_pack`
- `owledge_list_tasks`
- `owledge_list_reviews`

Benchmark modes:

- `ci`: deterministic, no model, CI-safe.
- `local`: Ollama scan, user model selection, sequential execution.
- `frontier`: post-release/opt-in path with hard cost warning.
- `harness`: roadmap mode.
- `all`: sequential only, explicit warning.

Stable benchmark metrics:

- retrieval precision/recall
- context pack tokens
- irrelevant-token ratio
- answer correctness
- citation accuracy
- privacy/staleness failures
- contradiction handling
- handoff resume score
- prompt/eval token counts
- duration and tokens/sec
- failure frontier scale

## CI Requirements

Update `.github/workflows/ci.yml`:

- compile new modules and plugin scripts.
- run `public-docs`, `release-trust`, and runtime adapters.
- add `.owledge` fresh quickstart smoke.
- add `wikilink-audit --check`.
- add `benchmark-kit run --mode ci`.
- keep Ubuntu/Windows/macOS and Python 3.10-3.12 matrix.

Update the release-gates job:

- run unit tests.
- run `test-contracts`.
- run `finalization-gates`.
- run kit integrity against a generated `.owledge` kit.
- run add-on boundary check.
- run sdist-clean after build.

Update fresh-install-cycle:

- editable source install smoke.
- wheel install smoke.
- assert `.owledge/` and `OWLEDGE.md`.
- assert no public dependency on `OWLEDGE.md`.
- run doctor and upgrade dry-run.

Update `.github/workflows/docs.yml` last:

- public docs gate.
- release trust gate.
- stale public claim gate.
- benchmark-kit docs/report smoke after benchmark implementation exists.

Update `.github/workflows/release.yml`:

- build sdist and wheel.
- twine check.
- sdist-clean.
- verify upgrade notes on root/template/schema changes.
- upload/download artifacts.
- PyPI Trusted Publishing with `id-token: write`.

## Docs Requirements

Docs are intentionally last. Final docs must update:

- `README.md`
- `docs/README.md`
- `docs/quickstart.md`
- `docs/command-reference.md`
- `docs/distribution.md`
- `docs/harness-plugin-matrix.md`
- `docs/install-plugin.md`
- `docs/performance-scale-notes.md`
- `ROADMAP.md`
- `CHANGELOG.md`
- `AGENTS.template.md`
- `CLAUDE.template.md`
- plugin READMEs

Docs must include:

- v0.7.0 abstract.
- problem to Owledge solution table.
- `uvx` / `uv tool install` first install path.
- 5-minute demo path.
- Mermaid workflows for core usage, MCP read-only flow,
  planning/review/research, wikilink audit, benchmark flow, and handoff/resume.
- troubleshooting section.
- roadmap boundaries for harness/cloud/Hermes/RAG.
- links to MCP, native planning, wikilink audit, and benchmark kit docs.
- no stale source-checkout-first messaging.

Docs QA uses two lanes:

- Docs Writer: updates docs after implementation is complete.
- Docs Red-Team: independently checks links, overclaims, install friction,
  README first-screen clarity, and international audience fit.

Docs pass only when both lanes agree or the orchestrator resolves explicit
disagreement.

## Subagent Lane Protocol

| Lane | Task | Can Run Parallel |
| --- | --- | --- |
| Migration | `.owledge` root, `OWLEDGE.md`, root resolver | Yes |
| Contracts | contract constants, finalization gates, doctor | Yes, after migration target is fixed |
| Packaging | pyproject, MANIFEST, wheel/sdist smoke | Yes |
| CI | workflow updates and release gate wiring | Yes, after expected commands are known |
| MCP | read-only MCP implementation and smoke tests | Yes |
| Planning Layers | reviews/audiences/research/brainstorm templates | Yes |
| Wikilinks | wikilink audit and fixtures | Yes |
| Benchmark | benchmark-kit runner, schema, HTML report | Yes |
| Docs Writer | final docs implementation | Last only |
| Docs Red-Team | final docs sparring and stale-claim check | Last only |

Rules:

- Orchestrator owns the central plan, README merge, CI merge, and release notes.
- Subagents write lane handoffs under
  `.owledge/workpackages/<wp>/lanes/<agent-id>.md`.
- Subagents do not edit the central plan/tasklist directly.
- Blockers become explicit blocker artifacts.
- After each phase, the orchestrator records accepted deltas and reruns that
  phase's QA gate.

## Final Verification Commands

```bash
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py test release-trust --project-root .
python tools/owledge.py test launch-readiness --project-root .
python tools/owledge.py test runtime-adapters --project-root .
python tools/owledge.py test quality-ratchet --project-root .
python tools/owledge_core.py --project-root . test-contracts
python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports
python tools/owledge.py concept-audit --project-root . --format summary
python -m pytest tests/unit -q
python -m build
```

Install smoke:

```bash
uvx --from dist/<built-wheel>.whl owledge --help
uvx --from dist/<built-wheel>.whl owledge quickstart --target C:\tmp\owledge-v070-smoke
```

Benchmark smoke:

```bash
owledge benchmark-kit run --mode ci --output .owledge/reports/generated/benchmark
owledge benchmark-kit report --format html
```

Optional local benchmark:

```bash
owledge benchmark-kit run --mode local
```

Expected local behavior:

- scan installed Ollama models.
- recommend `gemma4:latest` and `qwen3.5:4b` if present.
- ask the user to choose models.
- run selected models sequentially.
- write JSON, Markdown, HTML, and SVG reports with explicit labels and caveats.

## Roadmap Deferrals

- Claude Code/Codex/OpenCode harness benchmarks.
- Cursor/Zed harness support.
- Full Hermes adapter.
- Write-enabled MCP.
- Frontier/cloud benchmark matrix.
- Mem0/Graphiti/LlamaIndex integrations.
- GitHub Action marketplace-style release gate.
- Official marketplace certification claims.
- Public case-study gallery.
- GIF/video launch demo after HTML report is stable.

## Assumptions

- Target version is `0.7.0`.
- Branch is `codex/owledge-v0.7-pre-release`.
- No external users require migration compatibility.
- Internal compatibility shims are allowed, but public docs must not center
  legacy names.
- Docs are the final implementation phase, not an early phase.
- The release does not claim mature swarm, harness, cloud, RAG, Hermes, or
  marketplace readiness before those tracks are implemented and benchmarked.

