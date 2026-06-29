---
memory_id: "mem:owledge:global:owledge:workpackage:v0.7.0-final-publishing-95-release-checklist"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "workpackage"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 final publishing 95+ release checklist"
summary: "Agent-facing implementation and QA checklist for the final Owledge v0.7.0 publishing cut."
concept_tags:
  - "phase-checklist"
  - "release-readiness"
  - "publishing"
  - "qa-gates"
  - "subagent-coordination"
stack_tags:
  - "python"
  - "markdown"
  - "github-actions"
problem_patterns:
  - "legacy-brand-drift"
  - "docs-code-mismatch"
  - "benchmark-scale-proof-gap"
architecture_patterns:
  - "orchestrator-owned-tasklist"
  - "lane-handoff"
  - "phase-gate"
failure_modes:
  - "checkbox-without-evidence"
  - "partial-phase-resume"
  - "docs-finalized-before-interface"
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
    reason: "This tasklist operationalizes the final publishing plan."
---

# Owledge v0.7.0 Final Publishing 95+ Release Checklist

## Resume State

Current resume point: **Phase 6 - Final Release Verification / packaging
environment unblock**.

## Agent Rules

- Orchestrator owns this tasklist, README merge, CI merge, release notes, and
  final publish score.
- Subagents work in scoped lanes and return evidence before checkboxes are
  checked.
- Subagents do not edit this central checklist directly unless explicitly
  assigned by the orchestrator.
- Lane handoffs should be written under `.owledge/workpackages/<wp>/lanes/`
  after Phase 1 creates or validates the public structure.
- A checkbox is checked only after implementation and QA evidence exist.
- If a checked box becomes stale after later edits, uncheck it and rerun the
  phase gate.
- Resume rule: find the first unchecked checkbox and continue there.

## Phase 0 - Baseline and Release Contract

Goal: Capture current truth before changing naming, benchmark behavior, or docs.

Subagent lanes:

- QA Baseline Subagent: run non-destructive baseline gates and record results.
- Red-Team Subagent: validate the cutline against the 95+ publishing goal.

QA gate:

```bash
git status --short
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py test release-trust --project-root .
python tools/owledge.py test launch-readiness --project-root .
python tools/owledge.py concept-audit --project-root . --format summary
```

Checklist:

- [x] Current branch and dirty state documented.
- [x] Baseline gate results captured.
- [x] Legacy naming inventory captured.
- [x] Current publish score or proxy score documented.
- [x] Phase 0 QA gate passed or blockers documented.

Metric check:

- Baseline gates have known pass/fail state: `public-docs`, `release-trust`,
  `launch-readiness`, and `concept-audit` exited `0`.
- Legacy inventory has explicit allowed and blocked categories. Initial active
  scan excluding archives, caches, `dist/`, and egg-info found substantial
  pre-migration naming drift across old public paths, docs, tests, plugins,
  and tool references.

## Phase 1 - Owledge Naming Cut

Goal: Remove active legacy naming from the public release surface.

Subagent lanes:

- Migration Subagent: rename plugin paths, skill paths, manifests, package data,
  workflows, and active public tool references.
- Compatibility Subagent: preserve only hidden migration shims required for
  older installs or tests.
- QA Naming Subagent: implement and run the `legacy-naming-clean` gate.

QA gate:

```bash
python tools/owledge.py test legacy-naming-clean --project-root .
python tools/owledge.py test release-trust --project-root .
python tools/owledge.py test runtime-adapters --project-root .
python tools/owledge.py test mcp-readonly --project-root .
```

Checklist:

- [x] Legacy cowork plugin path replaced by `plugins/owledge-cowork/`.
- [x] Plugin manifests use Owledge naming.
- [x] Active skill names use Owledge naming.
- [x] Active workflows and package metadata reference Owledge paths.
- [x] Public command docs no longer expose old naming.
- [x] Compatibility shims are hidden and documented only in migration context.
- [x] `legacy-naming-clean` gate implemented.
- [x] Phase 1 QA gate passed.

Metric check:

- Active legacy naming leaks: `0`.
- Runtime adapter smoke passes after rename.
- Release trust remains green.
- MCP read-only smoke remains green.

## Phase 2 - Standalone Skills Surface

Goal: Make selected Owledge skills usable without adopting the full project kit.

Subagent lanes:

- Skills Packaging Subagent: create `standalone-skills/` and copy/adapt the
  standalone-ready skills.
- Skill QA Subagent: validate manifests, dependencies, and install shape.

QA gate:

```bash
python tools/owledge.py test standalone-skills --project-root .
python tools/owledge.py test legacy-naming-clean --project-root .
```

Checklist:

- [x] `standalone-skills/README.md` created.
- [x] `standalone-skills/manifest.json` created.
- [x] `owledge-blindspot-audit` standalone skill included.
- [x] `owledge-agentic-review` standalone skill included.
- [x] `owledge-brainstorm` standalone skill included.
- [x] Optional `owledge-planning-layer` included only if no-full-kit mode is clear.
- [x] Each standalone skill has install guidance.
- [x] Each standalone skill declares dependencies and supported runtimes.
- [x] Phase 2 QA gate passed.

Metric check:

- Standalone manifest parses.
- Each listed skill has `SKILL.md`.
- Standalone docs do not require full Owledge adoption.
- `standalone-skills` gate passed with 36 checks.

## Phase 3 - Benchmark Kit V2 Finalization

Goal: Support scalable benchmark simulations and deliberate retrieval challenge
scenarios.

Subagent lanes:

- Benchmark Simulation Subagent: add scale selection and simulation corpus
  generation.
- Benchmark Challenge Subagent: implement needle, multi-hop, stale-conflict,
  privacy-trap, distractor-heavy, and handoff-resume scenarios.
- Report Subagent: improve HTML/SVG report clarity and metric labeling.

QA gate:

```bash
python tools/owledge.py benchmark-kit run --mode ci --scale 100 --yes
python tools/owledge.py benchmark-kit report --format html
python tools/owledge.py test benchmark-kit-ci --project-root .
python tools/owledge.py test publish-readiness --project-root .
```

Checklist:

- [x] CLI accepts `--scale 100`.
- [x] CLI accepts `--scale 1000`.
- [x] CLI accepts `--scale 5000`.
- [x] CLI accepts `--scale 10000`.
- [x] CI mode remains deterministic and no-model.
- [x] Local mode scans Ollama models.
- [x] Local mode asks for explicit consent unless `--yes` is passed.
- [x] Local mode runs selected models sequentially.
- [x] Needle scenario implemented.
- [x] Multi-hop scenario implemented.
- [x] Stale-conflict scenario implemented.
- [x] Privacy-trap scenario implemented.
- [x] Distractor-heavy scenario implemented.
- [x] Handoff-resume scenario implemented.
- [x] JSON, Markdown, HTML, and SVG outputs are generated.
- [x] Report labels include mode, scale, scenario, commit, seed, caveats, and metrics.
- [x] Phase 3 QA gate passed.

Metric check:

- Benchmark schema stable.
- Chart label gate passes.
- Deterministic CI run produces 18 records for required scenarios.
- Scale smoke passed for 100, 1000, 5000, and 10000 files.
- Local smoke path is documented for final verification.

## Phase 4 - Release Gates and CI

Goal: Make CI enforce the 95+ publishing contract.

Subagent lanes:

- CI Subagent: update GitHub workflows.
- Gate Subagent: add or wire `publish-readiness`, `standalone-skills`, and
  `legacy-naming-clean`.
- QA Subagent: run the release gate matrix locally where possible.

QA gate:

```bash
python tools/owledge.py test publish-readiness --project-root .
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py test release-trust --project-root .
python tools/owledge.py test launch-readiness --project-root .
python tools/owledge.py wikilink-audit --project-root . --check
python tools/owledge.py concept-audit --project-root . --format summary
```

Checklist:

- [x] CI runs legacy naming gate.
- [x] CI runs standalone skills gate.
- [x] CI runs benchmark kit CI with explicit scale.
- [x] CI runs MCP read-only gate.
- [x] CI runs Wikilink Audit.
- [x] CI runs package/build smoke where feasible.
- [x] Publish-readiness gate target is 95+.
- [x] Concept-audit target is 9.5+.
- [x] Phase 4 QA gate passed.

Metric check:

- Publish-readiness score: `100`.
- Concept-audit target is wired for final verification.
- Contracts: fixed for `.owledge/` path resolution and generated-state ignore policy.
- P0/P1 findings: `0` in the Phase 4 gate set.

## Phase 5 - Final Docs and Positioning

Goal: Finalize all active docs after interfaces, names, benchmark CLI, and gates
are stable.

Subagent lanes:

- Docs Writer Subagent: update README, docs, roadmap, changelog, templates, and
  plugin/add-on docs.
- Docs Red-Team Subagent: independently check stale claims, naming leaks, link
  quality, install friction, and international clarity.
- Orchestrator: resolve disagreements and own final README positioning.

QA gate:

```bash
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py test legacy-naming-clean --project-root .
python tools/owledge.py test publish-readiness --project-root .
python tools/owledge.py wikilink-audit --project-root . --check
```

Checklist:

- [x] README first screen has clear claim, install command, and value.
- [x] Problem to Owledge solution table is current.
- [x] uv-first quickstart is current.
- [x] 5-minute demo path is current.
- [x] MCP docs link to the read-only MCP surface.
- [x] Wikilink Audit docs are current.
- [x] Benchmark docs include scale and scenario support.
- [x] Standalone skills docs are linked.
- [x] Roadmap is a table with Status, Ticket, Feature, DoD, and Target.
- [x] Changelog contains the legacy naming migration note.
- [x] Troubleshooting covers old v0.6-style installs.
- [x] Mermaid workflows are present and current.
- [x] Docs Red-Team review completed.
- [x] Phase 5 QA gate passed.

Metric check:

- README first-screen score: `>= 95` by public-docs gate and manual first-screen review.
- Docs Red-Team score: `>= 95` by stale-claim, link, naming, and benchmark surface checks.
- Active legacy naming leaks: `0`; only the explicit `CHANGELOG.md` migration note is allowed.
- Broken links or stale public claims: `0` in public-docs and wikilink checks.

## Phase 6 - Final Release Verification

Goal: Verify the final release candidate end to end.

Subagent lanes:

- Packaging QA Subagent: build and check wheel/sdist.
- Install QA Subagent: run `uvx --from dist/<wheel>` smoke tests.
- Benchmark QA Subagent: run local benchmark smoke with one selected Ollama
  model if available.
- Red-Team Subagent: final release review and score.

QA gate:

```bash
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py test release-trust --project-root .
python tools/owledge.py test launch-readiness --project-root .
python tools/owledge.py test mcp-readonly --project-root .
python tools/owledge.py wikilink-audit --project-root . --check
python tools/owledge.py benchmark-kit run --mode ci --scale 100 --yes
python tools/owledge.py benchmark-kit report --format html
python tools/owledge.py concept-audit --project-root . --format summary
python tools/owledge.py test publish-readiness --project-root .
python -m build
python -m twine check dist/*
```

Install smoke:

```bash
uvx --from dist/<built-wheel>.whl owledge --help
uvx --from dist/<built-wheel>.whl owledge quickstart --target <tmp>
```

Local benchmark smoke:

```bash
owledge benchmark-kit run --mode local --scale 100 --yes
owledge benchmark-kit report --format html
```

Checklist:

- [ ] Full final test plan passed.
- [ ] Wheel build passed.
- [ ] Sdist build passed.
- [ ] `twine check` passed.
- [ ] `uvx --from dist/<wheel> owledge --help` passed.
- [ ] `uvx --from dist/<wheel> owledge quickstart` passed.
- [x] Benchmark CI smoke passed.
- [x] Local benchmark smoke passed or environment limitation documented.
- [x] Final red-team verdict is `promote-candidate` or explicit owner waiver exists.
- [x] No unresolved P0/P1 findings remain.

Metric check:

- Public docs: passed with `221` checks.
- Release trust: passed with version `0.7.0`.
- Launch readiness: passed with `78` checks.
- MCP read-only: passed; write-like tools `0`.
- Wikilink audit: passed; unresolved `0`, ambiguous `0`.
- Benchmark CI: passed with `--mode ci --scale 100`; report regenerated as
  JSON, Markdown, HTML, and SVG.
- Local benchmark smoke: passed with
  `python tools/owledge.py benchmark-kit run --mode local --scale 100 --models qwen3.5:4b --yes`.
  Ollama scan found installed local and cloud model tags, recommended
  `gemma4:latest`, `qwen3.5:4b`, `qwen3:latest`, and `llama3.2:latest`,
  then ran the selected model sequentially across all six scenarios.
- Local benchmark report: `python tools/owledge.py benchmark-kit report --format html`
  passed and regenerated JSON, Markdown, HTML, and SVG report files.
- Publish-readiness score: `100`; verdict `promote-candidate`.
- Python compile smoke: `python -m compileall -q tools tests` passed.
- Concept-audit: command exited `0`; mechanical categories include dogfood `10`
  and contracts `10`. The summary output still reports lifecycle and
  distribution at `7`, so this remains a final-review note even though the
  release gate passes.
- Docs Red-Team score: `>= 95`.
- README first-screen score: `>= 95`.
- Active legacy naming leaks: `0`.
- MCP write-like tools: `0`.
- Wikilink broken/ambiguous: `0`.
- Unit tests, `python -m build`, `twine check`, and `uvx --from dist/<wheel>`
  smokes are not completed in this session because the available Python
  environment lacks `pytest`, `build`, `twine`, `setuptools`, and `wheel`.
  `uv` dependency resolution also requires PyPI access for `setuptools>=69`,
  but the sandbox blocks network sockets and the escalation request was
  rejected by the host. These are environment blockers, not failing Owledge
  gates.
