---
memory_id: "mem:owledge:global:owledge:plan:v0.7.0-final-publishing-95-release-cut"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "plan"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 final publishing 95+ release cut"
summary: "Final publishing plan for Owledge v0.7.0: zero-legacy Owledge naming, standalone skills, scalable Benchmark Kit V2, release gates, final docs, and 95+ publish readiness."
concept_tags:
  - "release-readiness"
  - "publishing"
  - "owledge-v0.7.0"
  - "zero-legacy-naming"
  - "standalone-skills"
  - "benchmark-kit"
  - "docs"
  - "publish-readiness"
stack_tags:
  - "python"
  - "markdown"
  - "github-actions"
  - "mcp"
problem_patterns:
  - "legacy-brand-drift"
  - "docs-code-mismatch"
  - "benchmark-scale-proof-gap"
  - "skill-install-friction"
architecture_patterns:
  - "markdown-first-memory"
  - "git-native-memory"
  - "read-only-adapter"
  - "standalone-skill-surface"
  - "simulation-benchmark"
failure_modes:
  - "public-release-with-legacy-naming-leaks"
  - "docs-overclaim-unimplemented-interface"
  - "benchmark-without-scale-scenarios"
  - "agent-confusion-from-stale-docs"
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-27T00:00:00Z"
updated_at: "2026-06-27T00:00:00Z"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:plan:v0.7.0-pre-release-realization"
    confidence: 0.9
    reason: "This final cut extends the v0.7.0 pre-release plan with publishing-grade QA and red-team fixes."
  - type: "derived_from"
    target: "mem:owledge:global:owledge:session:release-sparring-2026-06-26"
    confidence: 0.8
    reason: "The plan reflects release sparring decisions and the final red-team/blindspot review."
---

# Owledge v0.7.0 Final Publishing 95+ Release Cut

## Objective

Make Owledge ready for international publishing to power users, AI creators,
agent builders, developer communities, and early team adopters.

The release target is not only a green technical build. The repository must be
understandable, installable, brand-consistent, benchmarkable, and credible from
the first README screen.

## Locked Release Standards

- Public surface is fully Owledge.
- Active docs, plugins, skills, add-ons, templates, workflows, package metadata,
  and release gates do not expose legacy naming.
- A short migration note is allowed in `CHANGELOG.md` so users can understand
  old archived docs or pre-v0.7 local installs.
- Final docs are the last implementation phase.
- Benchmark Kit V2 proves scalable simulation capability at 100, 1000, 5000,
  and 10000 files.
- Benchmark scenarios include deliberate retrieval traps and challenge cases.
- `standalone-skills/` exposes independently useful Owledge skills.
- Publish readiness target is 95+.
- No unresolved P0 or P1 red-team findings remain.

## Phase Plan

| Phase | Goal | Done Definition | QA Gate |
| ---: | --- | --- | --- |
| 0 | Baseline and release contract | Current branch, dirty state, gates, legacy inventory, and release score baseline are known. | Existing gates run; legacy inventory recorded. |
| 1 | Owledge naming cut | Active public surface uses Owledge names; plugin, skills, tools, package metadata, workflows, and generated kit paths are aligned. | `legacy-naming-clean`; zero active legacy leaks except allowlisted migration/archive/test cases. |
| 2 | Standalone skills surface | `standalone-skills/` contains independently usable skills with manifest and install guidance. | Manifest parses; standalone skill smoke passes; no full-kit dependency in standalone docs. |
| 3 | Benchmark Kit V2 finalization | Benchmark CLI supports scale selection and challenge simulations; CI and local modes are stable; HTML/SVG reports are clear. | `benchmark-kit run --mode ci --scale 100`; report files exist; chart-label and schema checks pass. |
| 4 | Release gates and CI | CI enforces naming, contracts, MCP, wikilinks, benchmark CI, package smoke, and publish-readiness. | `publish-readiness >= 95`; contracts 100%; concept-audit >= 9.5. |
| 5 | Final docs and positioning | README, docs, roadmap, changelog, troubleshooting, Mermaid workflows, and release notes are current and persuasive. | `public-docs`; stale-claim gate; link gate; README score >= 95; docs red-team >= 95. |
| 6 | Final release verification | Full release candidate is packageable, installable, benchmarkable, and red-team clean. | Full final test plan green; red-team verdict target `promote-candidate`. |

## Implementation Requirements

### Naming and Migration Policy

- Rename active plugin surface to `plugins/owledge-cowork/`.
- Rename standalone and bundled skills to Owledge names:
  - `owledge-principles`
  - `owledge-runtime-bridge`
  - `bootstrap-owledge`
- Rename or hide public-facing lower-level names where feasible.
- Compatibility shims are allowed only if they are not visible in normal docs,
  package metadata, plugin manifests, active skills, templates, or workflows.
- Add a `CHANGELOG.md` migration note explaining that pre-v0.7 docs or installs
  may mention the old surface, while current projects use `OWLEDGE.md` plus
  `.owledge/`.
- Add a hard `legacy-naming-clean` gate with an explicit allowlist:
  - allowed: `CHANGELOG.md` migration note, `docs/archive/**`, and tests that
    explicitly validate migration behavior.
  - blocked: README, active docs, templates, package metadata, active skills,
    active add-ons, workflows, plugin manifests, and command docs.

### Standalone Skills

- Create `standalone-skills/` as a user-facing folder.
- Include only skills that work without adopting the full Owledge kit:
  - `owledge-blindspot-audit`
  - `owledge-agentic-review`
  - `owledge-brainstorm`
  - optional `owledge-planning-layer` only if its no-full-kit mode is clear.
- Each standalone skill must include:
  - `SKILL.md`
  - a local README or manifest entry
  - supported runtime notes
  - manual install steps
  - dependency notes
  - optional full-Owledge integration note
- A CLI skill installer remains post-release roadmap unless it falls out
  trivially from this work.

### Benchmark Kit V2

- Add CLI scale selection:
  - `--scale 100`
  - `--scale 1000`
  - `--scale 5000`
  - `--scale 10000`
- Add challenge scenario families:
  - `needle`: one relevant fact hidden in a large corpus.
  - `multi-hop`: answer requires two or three linked notes.
  - `stale-conflict`: newer record must override older record.
  - `privacy-trap`: private or unsafe record must be excluded or refused.
  - `distractor-heavy`: many plausible but wrong notes.
  - `handoff-resume`: model must continue from compact handoff plus selected
    context.
- CI mode remains deterministic and no-model.
- Local mode scans Ollama models, asks for consent, and runs selected models
  sequentially.
- Reports must generate JSON, Markdown, HTML, and SVG.
- HTML must include clear labels, caveats, model/runtime metadata, simulation
  scale, scenario type, commit, and seed.
- Stable metrics:
  - retrieval precision and recall
  - context pack tokens
  - irrelevant-token ratio
  - answer correctness
  - citation accuracy
  - privacy and staleness failures
  - contradiction handling
  - handoff resume score
  - prompt/eval token counts
  - duration and tokens per second
  - failure frontier scale

### Final Docs

Docs are intentionally last. They must be updated only after naming,
standalone skills, benchmark CLI, and release gates are implemented.

Docs must include:

- Strong README first screen with claim, install command, value, and quick path.
- Problem to Owledge solution table.
- uv-first install and quickstart.
- 5-minute demo path.
- Mermaid workflows for quickstart, MCP, planning/review/research, wikilink
  audit, benchmark, and handoff/resume.
- Roadmap table with `Status`, `Ticket`, `Feature`, `DoD`, and `Target`.
- Troubleshooting for old v0.6-style installs.
- Changelog migration note for old naming.
- Clear roadmap deferrals for harness benchmarks, write-enabled MCP, Hermes,
  RAG integrations, marketplace certification, and cloud/frontier benchmark
  matrix.

## Final Acceptance Criteria

- Publish readiness score is at least 95.
- Concept audit score is at least 9.5.
- Docs red-team score is at least 95.
- README first-screen score is at least 95.
- Active legacy naming leaks are zero.
- Wikilink audit has zero broken or ambiguous links.
- MCP has zero write-like tools.
- Benchmark CI and one local smoke path pass.
- Wheel, sdist, and `uvx --from dist/<wheel>` smoke paths pass.
- No unresolved P0 or P1 red-team findings remain.

