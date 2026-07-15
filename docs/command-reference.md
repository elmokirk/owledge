# Command Reference

Owledge is Python-first. Use `tools/owledge.py` for public workflows and
`tools/owledge_core.py` for lower-level memory operations.

Package examples can be run as `uvx owledge ...` or, after `uv tool install owledge`, as `owledge ...`.

## Public Owledge CLI

| Command | Writes | Purpose |
| --- | --- | --- |
| `python tools/owledge.py doctor --project-root .` | No | Diagnose kit or host setup |
| `python tools/owledge.py init-project --target /path/to/project` | Yes | Add Owledge files to an existing coding project |
| `python tools/owledge.py quickstart --target /path/to/project` | Yes | Initialize, run doctor, and validate in one simple project-local flow |
| `python tools/owledge.py add-kb-module --knowledgebase-root /path/to/vault` | Yes | Add a drop-in module to an existing Markdown KB |
| `python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --verify` | Yes | Generate a minimal project-local kit |
| `python tools/owledge.py install-addon --project-root . --addon project-snapshot-kit` | Yes | Install an optional add-on without changing the core setup |
| `python tools/owledge.py install-addon --project-root . --addon launch-demo-kit` | Yes | Install five-minute demo evidence, handoff, and proof report assets |
| `python tools/owledge.py install-addon --project-root . --addon trust-readiness-kit` | Yes | Install team trust, data-flow, threat-model, and security-readiness docs |
| `python tools/owledge.py install-addon --project-root . --addon runtime-conformance-kit` | Yes | Install read-only runtime conformance contracts and fixtures |
| `python tools/owledge.py install-addon --project-root . --addon pi-proof-kit` | Yes | Install a synthetic PI Agent proof corpus and scorecard |
| `python tools/owledge.py install-addon --project-root . --addon ts-adapter-kit` | Yes | Install optional Node/TypeScript CI validation for the Markdown contract |
| `python tools/owledge.py install-addon --project-root . --addon benchmark-kit` | Yes | Install optional real Markdown fixture benchmark assets |
| `python tools/owledge.py install-addon --project-root . --addon decision-trace-kit` | Yes | Install optional read-only decision trace JSON and HTML assets |
| `python tools/owledge.py install-addon --project-root . --addon cross-project-hub-kit` | Yes | Install optional reviewed cross-project learning hub assets |
| `python tools/owledge.py install-addon --project-root . --addon swarm-coordination-kit` | Yes | Install optional multi-agent role-lane coordination templates |
| `python tools/owledge.py install-addon --project-root . --addon poweruser-positioning-kit` | Yes | Install optional snapshot-first poweruser positioning scorecard assets |
| `python tools/owledge.py project-snapshot --project-root . --snapshots-only` | Yes | Generate optional Project Snapshot Kit Markdown snapshots |
| `python tools/owledge.py project-snapshot --project-root . --render-html` | Yes | Render optional static dashboard pages from existing snapshots |
| `python tools/owledge.py project-snapshot --project-root . --yes` | Yes | Generate snapshots and dashboard pages without prompts |
| `python tools/owledge.py build-context-pack --project-root . --task-id publish-v1` | No | Generate scoped task context |
| `python tools/owledge.py wikilink-audit --project-root . --check` | No | Audit Obsidian-style wiki links for valid, broken, and ambiguous targets |
| `python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode small --yes` | Yes, ignored reports | Run optional Benchmark Kit deterministic real Markdown fixture benchmark |
| `python tools/benchmark-kit/run-benchmark-kit.py --mode local --scale-mode small --models gemma4:latest --yes` | Yes, ignored reports | Run selected Ollama model sequentially against real Markdown fixtures |
| `python tools/benchmark-kit/render-benchmark-report.py --format html` | Yes, ignored reports | Re-render the latest Benchmark Kit result as HTML/SVG |
| `python tools/benchmark-kit/compare-benchmark-runs.py --inputs <reports...> --output .owledge/reports/generated/benchmark-kit-comparison` | Yes, ignored reports | Compare completed Benchmark Kit reports without running models |
| `python tools/owledge.py test mcp-readonly --project-root .` | Yes, temp project | Smoke-test the read-only MCP stdio server |
| `python tools/owledge.py test public-docs --project-root .` | No | Check public docs integrity |
| `python tools/owledge.py test release-trust --project-root .` | No | Check version alignment, product naming, and bounded runtime claims |
| `python tools/owledge.py test private-path-clean --project-root .` | No | Check active release files for real local user path leaks |
| `python tools/owledge.py test principles-only --project-root .` | No | Check the no-plugin/no-generator principles integration path |
| `python tools/owledge.py test kb-ingestion-safety --project-root .` | Yes, temp KB | Check metadata-first non-destructive KB integration |
| `python tools/owledge.py test generated-kit-surface --project-root .` | Yes, temp projects | Check generated kits for platform-neutral Python surface |
| `python tools/owledge.py test retrieval --project-root .` | Yes, ignored reports | Run the retrieval fixture eval directly |
| `python tools/owledge.py test launch-readiness --project-root .` | No | Check 95+ launch-readiness evidence, add-ons, packaging, and PI proof |
| `python tools/owledge.py test quality-ratchet --project-root .` | Yes, ignored reports | Run platform, ingestion, runtime, retrieval, benchmark, and QA guardrails |
| `python tools/owledge.py test poweruser-simulations --project-root .` | Yes, temp project | Run dirty-vault and first-user DX simulations |
| `python tools/owledge.py test runtime-adapters --project-root .` | Yes, temp project | Smoke-test plugin runtime capture |
| `python tools/owledge.py finalization-gates --project-root . --include-compliance` | Yes | Run release gates |
| `python tools/owledge.py benchmark --project-root . --scale-files 100,1000,10000` | Yes, ignored results | Run local benchmark harness |
| `python tools/owledge.py upgrade --dry-run --project-root .` | No | Show what would change to bring the project to the current kit version |
| `python tools/owledge.py upgrade --apply --project-root .` | Yes, templates | Apply pending kit updates in safe mode (preserves user-edited files) |
| `python tools/owledge.py upgrade --apply --mode=force-templates --yes --project-root .` | Yes, templates | Force-update all updatable files (respects never-touch list) |
| `python tools/owledge.py upgrade --dry-run --mode=manual --project-root .` | Yes, patch file | Emit a `git apply`-able patch to `.owledge/exports/upgrade-pending.patch` |
| `python tools/owledge.py sync-dogfood --dry-run --project-root .` | No | Show template drift between product and dogfood trees (maintainer-only) |
| `python tools/owledge.py sync-dogfood --apply --project-root .` | Yes, internal templates | One-way mirror `templates/owledge/templates/` to `internal/owledge/templates/` (maintainer-only) |
| `python tools/owledge.py concept-audit --project-root .` | No | Run the 8-dimension concept blindspot audit (dims 1-4 mechanical, 5-8 guided) |
| `python tools/owledge.py concept-audit --dimension lifecycle --project-root .` | No | Run a single audit dimension by name |
| `python tools/owledge.py concept-audit --profile .owledge/concept-audit-profile.json --project-root .` | No | Run the audit with a custom weights/overrides profile |
| `python tools/owledge.py concept-audit --format summary --project-root .` | No | Print a one-line-per-dimension summary instead of JSON |

## Release QA Contracts

The machine-readable release surface at contracts/release-surface.json names
every current-version sink, the public documentation surface, historical
document exclusions, and feature documentation/test obligations.

| Command | Writes | Purpose |
| --- | --- | --- |
| python tools/owledge.py test version-contract --project-root . | No | Verify every declared current-version sink against VERSION |
| python tools/owledge.py test docs-contract --project-root . --base-ref origin/main | No | Verify all public docs and require impacted docs in a PR |
| python tools/owledge.py test release-contract --project-root . --require-dist --evidence-path dist/release-evidence.json | Yes, build artifact | Combine version, documentation, package-artifact, and evidence checks |

Product PRs run docs-contract against their base branch. A change to a declared
product surface must update every mapped public document in the same PR.
Historical release and migration documents retain older version references only
when explicitly labelled Historical.

Releases run from release/vX.Y.Z, not from a direct version bump on main. After
PyPI confirms the version, the release workflow fast-forwards the tested commit
to main, creates the tag, and uploads release-evidence.json.

## Lower-Level Memory CLI

| Command | Writes | Purpose |
| --- | --- | --- |
| `python tools/owledge_core.py --project-root . validate-memory --strict` | No | Validate frontmatter, IDs, edges, and memory records |
| `python tools/owledge_core.py --project-root . build-memory-index` | Yes | Generate full memory indexes |
| `python tools/owledge_core.py --project-root . build-memory-index --incremental --track-tombstones` | Yes | Incremental index with tombstone tracking |
| `python tools/owledge_core.py --project-root . build-project-snapshot` | Yes | Lower-level optional Project Snapshot Kit snapshot builder |
| `python tools/owledge_core.py --project-root . audit-retention` | No | Preview retention, stale, expiry, and review-cycle findings |
| `python tools/owledge_core.py --project-root . review-memory-conflicts` | No | Detect stale records and contradiction edges |
| `python tools/owledge_core.py --project-root . scan-memory-sensitive-data` | No | Scan memory and private runtime logs for secret-like content |
| `python tools/owledge_core.py --project-root . run-review-workflow --review-type expert-lens --subject docs/README.md` | Yes | Create review/evaluation artifacts |
| `python tools/owledge_core.py --project-root . export-rag-documents --corpus-type shared` | Yes | Generate reviewed RAG export |
| `python tools/owledge_core.py --project-root . export-lightrag --corpus-type shared` | Yes | Generate LightRAG export |
| `python tools/owledge_core.py --project-root . export-graphrag --corpus-type shared` | Yes | Generate GraphRAG export |
| `python tools/owledge_core.py --project-root . render-memory-report --report-type project-dashboard --audience private` | Yes | Generate local HTML report |
| `python tools/owledge_core.py --project-root . dogfood-sync-check` | No | Check dogfood template drift (maintainer-only) |

## Existing Markdown Knowledgebase Module

```bash
python tools/owledge.py add-kb-module --knowledgebase-root /path/to/knowledgebase --include-cli
```

With an existing vault map:

```bash
python tools/owledge.py add-kb-module --knowledgebase-root /path/to/knowledgebase --map-file owledge-map.json
```

The builder scans Markdown files read-only, preserves existing `[[Wiki Links]]`,
and writes module-owned status/index artifacts under the module or mapped
indexes folder.

## Project Folder Kit

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --verify
```

The generator uses an explicit copy manifest and excludes tests, generated
indexes, generated exports, and raw runtime sessions. Compliance Light remains
opt-in:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit-compliance --include-compliance --verify
```

## Optional Project Snapshot Kit

Install the optional project cockpit add-on:

```bash
python tools/owledge.py install-addon --project-root . --addon project-snapshot-kit
```

Interactive generation asks before writing snapshots or HTML:

```bash
python tools/owledge.py project-snapshot --project-root .
```

Scripted generation must be explicit:

```bash
python tools/owledge.py project-snapshot --project-root . --yes
python tools/owledge.py project-snapshot --project-root . --snapshots-only
python tools/owledge.py project-snapshot --project-root . --render-html
```

The CLI itself uses zero model tokens. It writes token estimates to
`.owledge/project-snapshot/project-snapshot-manifest.json` for future
agent-authored narrative refreshes.

`--render-html` uses existing Markdown snapshots and does not update them.

## Optional Launch Add-Ons

These add-ons are for broad distribution readiness. They are not required for
the minimal Owledge core.

```bash
python tools/owledge.py install-addon --project-root . --addon launch-demo-kit
python tools/owledge.py install-addon --project-root . --addon trust-readiness-kit
python tools/owledge.py install-addon --project-root . --addon runtime-conformance-kit
python tools/owledge.py install-addon --project-root . --addon pi-proof-kit
python tools/owledge.py install-addon --project-root . --addon ts-adapter-kit
python tools/owledge.py install-addon --project-root . --addon benchmark-kit
python tools/owledge.py install-addon --project-root . --addon decision-trace-kit
python tools/owledge.py install-addon --project-root . --addon cross-project-hub-kit
python tools/owledge.py install-addon --project-root . --addon swarm-coordination-kit
python tools/owledge.py install-addon --project-root . --addon poweruser-positioning-kit
python tools/enterprise-context-benchmark/run-enterprise-context-benchmark.py --project-root . --profile enterprise_default --seed 42
python tools/decision-trace/render-decision-trace.py --project-root .
python tools/poweruser-positioning/render-poweruser-positioning.py --project-root .
python tools/cross-project-hub/build-cross-project-map.py --project-root .
python tools/owledge.py test launch-readiness --project-root .
```

The launch-readiness gate validates the add-on manifests, five-minute demo
docs, runtime contracts, PI proof corpus, non-empty red-team scorecard, and
packaging metadata, optional TypeScript evaluation adapter files, and optional
Benchmark Kit proof assets. Decision trace, cross-project hub, swarm
coordination, and positioning kits remain optional power-user proof layers;
they do not become core dependencies.

## Benchmark Kit

Benchmark Kit is an optional add-on. It supports deterministic CI proof and
opt-in local Ollama validation against real synthetic Markdown fixtures.
Supported scale modes are `small`, `mid`, and `large`. The scenario set is
`needle`, `multi-hop`, `stale-conflict`, `privacy-trap`, `distractor-heavy`,
and `handoff-resume`.

```bash
python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode small --yes
python tools/benchmark-kit/run-benchmark-kit.py --mode local --scale-mode small --models gemma4:latest --yes
python tools/benchmark-kit/render-benchmark-report.py --format html
python tools/benchmark-kit/compare-benchmark-runs.py --inputs .owledge/exports/benchmark-kit-gemma4-latest/latest.json .owledge/exports/benchmark-kit-qwen3-5-4b/latest.json --output .owledge/reports/generated/benchmark-kit-comparison
```

Local mode scans Ollama models, requires explicit consent unless `--yes` is
passed, and runs selected models sequentially to avoid resource distortion.

Benchmark Kit outputs are generated views:

```text
.owledge/exports/benchmark-kit/latest.json
.owledge/exports/benchmark-kit/latest.md
.owledge/exports/benchmark-kit/results.jsonl
.owledge/reports/generated/benchmark-kit/index.html
.owledge/reports/generated/benchmark-kit/charts.svg
.owledge/exports/benchmark-kit-comparison/latest.json
.owledge/exports/benchmark-kit-comparison/latest.md
.owledge/reports/generated/benchmark-kit-comparison/index.html
.owledge/reports/generated/benchmark-kit-comparison/charts.svg
```

Decision trace and positioning outputs are also generated views:

```text
.owledge/decision-trace/trace.json
.owledge/reports/decision-trace/index.html
.owledge/reports/poweruser-positioning/positioning.json
.owledge/reports/poweruser-positioning/index.html
.owledge/cross-project-hub/cross-project-map.json
```

## Finalization Gates

```bash
python tools/owledge.py finalization-gates --project-root . --include-compliance
python tools/owledge.py redteam-qa --project-root .
```

The finalization gate runs compile checks, public-docs integrity, release-trust
checks, skill validation, principles-only validation, scenario tests,
power-user simulations, contracts, platform-neutrality checks, generated-kit
surface checks, doctor, validation, indexes, lifecycle checks, runtime smoke
tests, memory evals, retrieval fixture eval, KB ingestion safety, benchmark
thresholds, red-team QA, and project-folder verification.

The latest machine-readable report is written to
`.owledge/exports/finalization-gates/latest.json`; the Markdown summary is
`.owledge/exports/finalization-gates/latest.md`.
The quality ratchet summary is written to
`.owledge/exports/finalization-gates/quality-ratchet-summary.json`.

## Scope Rules

For aggregate roots, pass explicit scope arguments to lower-level exports and
reports whenever multiple tenants or customers are present:

```bash
python tools/owledge_core.py --project-root . export-rag-documents --corpus-type shared --tenant-id tenant-a --customer-id customer-a --project-id project-a
```

## Promotion Requirements

Promotion requires valid source frontmatter, matching scope, reviewed status,
approved review evidence, safe shared visibility, and an optional source hash
match. Promotion writes an audit manifest to
`.owledge/evidence/promotions/`.
