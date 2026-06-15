# Command Reference

Use PowerShell with `-NoProfile -ExecutionPolicy Bypass -File` on Windows when execution policy may block direct script calls. On macOS/Linux, use `python3 tools/agent_memory_cli.py --project-root . <command>` or the `.sh` wrappers included in the lean project folder.

| Command | Writes | Purpose |
| --- | --- | --- |
| `tools\bootstrap-agent-memory.ps1` | Yes | Copy missing kit files into a host project |
| `tools\verify-host-install.ps1` | No | Host-project doctor plus strict validation |
| `tools\memory-doctor.ps1` | No | Diagnose kit or host setup |
| `tools\validate-memory.ps1` | No | Validate project and global user-memory frontmatter, IDs, edges, research fields, preferences and coach reports |
| `tools\build-memory-index.ps1` | Yes | Generate full or incremental memory indexes with optional tombstones |
| `tools\build-context-pack.ps1` | No | Generate scoped task context with optional objective-aware scoring |
| `tools\audit-retention.ps1` | No | Preview retention, stale, expiry, and review-cycle findings |
| `tools\review-memory-conflicts.ps1` | No | Detect stale records plus active contradiction and supersession edges |
| `tools\scan-memory-sensitive-data.ps1` | No | Scan memory Markdown and raw session events for secret-like content |
| `tools\capture-idea.ps1` | Yes | Add unique idea card |
| `tools\pi-agent-check.ps1` | No by default | PI workspace diagnostics; pass `-BuildIndex` to write index |
| `tools\pi-intelligence-report.ps1` | Yes | Generate PI candidate intelligence report |
| `tools\pi-redteam-evaluate.ps1` | Yes | Score PI reports from 1-100 |
| `tools\run-review-workflow.ps1` | Yes | Create reusable review/evaluation artifacts from templates |
| `tools\run-redteam-qa.ps1` | Yes | Create a multi-perspective red-team release QA artifact |
| `tools\promote-memory.ps1` | Yes | Promote reviewed memory with hardened gates |
| `tools\export-rag-documents.ps1` | Yes | Generate neutral RAG export and snapshot |
| `tools\export-lightrag.ps1` | Yes | Generate LightRAG arrays and snapshot |
| `tools\export-graphrag.ps1` | Yes | Generate GraphRAG nodes/edges and snapshot |
| `tools\render-memory-report.ps1` | Yes | Generate HTML report views |
| `tools\run-memory-evals.ps1` | Yes, temp DB | Run control-plane concurrency eval |
| `tools\eval-memory-retrieval.ps1` | Yes | Run retrieval calibration and write eval reports |
| `tools\test-runtime-adapters.ps1` | Yes, temp project | Run Claude/Cowork plus generic CLI runtime smoke fixtures |
| `tools\test-agent-memory-principles-skill.ps1` | No | Validate the principles skill frontmatter, references, concision, and plugin mirror |
| `tools\test-agent-memory-principles-scenarios.ps1` | Yes, temp KBs | Exercise large-codebase, existing-KB, skill-bloat, subagent-boundary, and edge-case scenarios |
| `tools\build-project-folder-kit.ps1` | Yes | Generate a minimal project-folder-only kit |
| `tools/build_project_folder_kit.py` | Yes | Cross-platform generator for macOS/Linux project-folder-only kits |
| `tools\build-kb-module.ps1` | Yes | Add a drop-in Agent Memory module to an existing Markdown KB without env vars |
| `tools/build_kb_module.py` | Yes | Cross-platform drop-in KB module generator |
| `tools\test-kb-module.ps1` | Yes, temp KB | Smoke-test KB module install without modifying existing notes |
| `tools/*.sh` | Mixed | macOS/Linux convenience wrappers for verify, doctor, validate, index, and context packs |
| `tools\run-finalization-gates.ps1` | Yes | Run the v0.5 release gate chain |

Optional Compliance Light add-on commands are installed only with
`-IncludeCompliance` or `addons\compliance-light\install-compliance-layer.ps1`:

| Command | Writes | Purpose |
| --- | --- | --- |
| `tools\compliance-doctor.ps1` | No | Read-only Compliance Light profile, provider, AI-system, processing, export-safety, retention, and sensitive-data checks |
| `tools\run-compliance-gates.ps1` | Yes | Run Compliance Light gates and write ignored reports under `agent-memory\exports\compliance\` |

## Memory Index

Current wrapper:

```powershell
tools\build-memory-index.ps1 -ProjectRoot .
```

Incremental wrapper with tombstones:

```powershell
tools\build-memory-index.ps1 -ProjectRoot . -Incremental -TrackTombstones
```

Output fields:

- `path`: generated index path, normally `agent-memory/indexes/memory-index.jsonl`
- `rows`: number of JSONL rows written
- `changed`: records updated or added in this run
- `unchanged`: unchanged records carried forward during incremental mode
- `deleted`: records missing from the current scan
- `tombstoned`: deleted records identified as tombstone candidates in this run
- `mode`: `full` or `incremental`
- `manifest_path`: generated manifest path
- `tombstone_path`: generated tombstone JSONL path when `-TrackTombstones` is used

P1 incremental indexing is documented in `docs/incremental-index-workflow.md`. Indexes, manifests, and tombstones are generated views, not canonical memory.

## Lifecycle And Safety Gates

Lifecycle checks are deterministic and read-only. They report findings and
previews; they do not delete or mutate memory records.

```powershell
tools\audit-retention.ps1 -ProjectRoot .
tools\review-memory-conflicts.ps1 -ProjectRoot .
tools\scan-memory-sensitive-data.ps1 -ProjectRoot .
```

`audit-retention` adds an implicit retention class when a record omits
`retention_class`, then reports expired `expires_at`, stale `stale_after`,
expired `valid_until`, and due `review_cycle` records. `review-memory-conflicts`
reports contradiction and supersession edges between active records.
`scan-memory-sensitive-data` scans Markdown memory plus raw `events.jsonl` logs
without printing unredacted secret-like values.

## Context Packs

Objective-aware context packs keep the old defaults and add optional scoring
metadata:

```powershell
tools\build-context-pack.ps1 -ProjectRoot . -TaskId "publish-v0.5" -Objective "Finalize project-folder setup and release gates"
```

The JSON output includes `score_breakdown`, `freshness_warnings`, and
`excluded_sources` reasons such as `no_relevance` or `context_budget`.

## Retrieval Calibration

The release fixture corpus is under `tests\fixtures\retrieval-corpus\` and is
paired with `tests\fixtures\retrieval-queries.json`.

```powershell
tools\eval-memory-retrieval.ps1 -ProjectRoot . -ProjectRoots tests\fixtures\retrieval-corpus -QueriesFile tests\fixtures\retrieval-queries.json -MinOverallScore 85 -MinSafetyScore 100
```

Fixture runs fail if the corpus is empty, safety drops below the threshold, or
the overall score is below the configured threshold. Raw sessions are excluded
unless `-IncludeSessions` is explicitly passed.

## Project Folder Only

Generate and verify a minimal local project kit:

```powershell
tools\build-project-folder-kit.ps1 -OutputPath C:\tmp\agent-memory-project-kit -Verify
```

macOS/Linux equivalent:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

With Claude/Cowork plugin adapter and Unix hooks:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --include-plugin-adapter --plugin-hook-profile unix --verify
```

The generator uses an explicit copy manifest and excludes plugins, tests, PI
sample reports, generated indexes, generated exports, and raw runtime sessions.
Release wrappers use `C:\tmp` when writable and fall back to project-local
`.agent-control\tmp` in restricted environments.

Compliance Light remains opt-in:

```powershell
tools\build-project-folder-kit.ps1 -OutputPath C:\tmp\agent-memory-project-kit-compliance -Verify -IncludeCompliance
```

Without `-IncludeCompliance`, no `agent-memory\compliance\` folder and no
Compliance Light commands are included.

## Existing Markdown Knowledgebase Module

Add Agent Memory planning support to an existing Markdown KB, Obsidian vault, or
LLM wiki without changing existing notes, wiki links, frontmatter, or OS
environment variables:

```powershell
tools\build-kb-module.ps1 -KnowledgebaseRoot C:\path\to\knowledgebase -IncludeCli
```

macOS/Linux:

```bash
python3 tools/build_kb_module.py --knowledgebase-root /path/to/knowledgebase --include-cli
```

Default output:

```text
agent-memory-module/
|-- AGENT_MEMORY_MODULE.md
|-- agent-memory/plans/
|-- agent-memory/handoffs/
|-- agent-memory/evidence/
|-- agent-memory/reviews/
`-- agent-memory/indexes/
```

The builder scans Markdown files read-only, preserves existing `[[Wiki Links]]`,
and writes module-owned status/index artifacts under
`agent-memory-module\agent-memory\indexes\`. Use `--layout flat` only when the
user explicitly wants module files at the KB root.

To use existing vault folders instead of the default module structure, create
`agent-memory-map.json` in the KB and run:

```powershell
tools\build-kb-module.ps1 -KnowledgebaseRoot C:\path\to\knowledgebase -MapFile agent-memory-map.json
```

Mapped paths must be relative existing directories inside the KB. Traversal,
absolute paths, symlinks, junctions, and missing targets fail closed.
In mapped mode, generated module docs, status, and indexes stay under the mapped
`indexes` folder; the builder does not create a root-level
`AGENT_MEMORY_MODULE.md`.

Smoke test:

```powershell
tools\test-kb-module.ps1 -ProjectRoot .
```

## Finalization Gates

Use the combined release gate before publishing:

```powershell
tools\run-finalization-gates.ps1 -ProjectRoot .
tools\run-redteam-qa.ps1 -ProjectRoot .
```

`run-finalization-gates` executes compile, principles-skill validation,
principles scenario tests, contracts, doctor, validation, full and incremental
indexes, lifecycle checks, runtime smoke tests, memory evals, retrieval fixture
eval, KB-module safety checks, and project-folder-only verification. Add
`-IncludeExports` when you also want shared export/report generation in the
same run. Add `-IncludeCompliance` to verify the optional Compliance Light
add-on through a separate generated project kit. The latest machine-readable
report is written to
`agent-memory\exports\finalization-gates\latest.json`; the matching Markdown
summary is `agent-memory\exports\finalization-gates\latest.md`. Both are
generated ignored artifacts.

## Review Evaluation Workflow

Use the `review-evaluation-workflow` skill and command for red-team reviews, expert evaluations, scenario simulations, scorecards, and converting findings into tasks. The contract is Markdown-first and does not require backend infrastructure.

Create a review artifact:

```powershell
tools\run-review-workflow.ps1 -ProjectRoot . -ReviewType expert-lens -Subject docs\reusable-review-evaluation-templates.md -Question "Does this review workflow have enough evidence and QA?"
```

Supported `-ReviewType` values:

- `multi-perspective-red-team`
- `expert-lens`
- `scenario-simulation`
- `persona-pack`
- `review-to-task-plan`

The command writes a private draft artifact under the relevant PI review folder and returns JSON with the output path, source template, review type, and QA commands. Scores of 95 or above are `promote-candidate` only; they do not automatically approve promotion.

## Scope Rules

For enterprise hubs or aggregate roots, pass:

```powershell
-TenantId tenant-a -CustomerId customer-a -ProjectId project-a
```

Do this for context packs, reports, and exports whenever multiple tenants are present.

## Promotion Requirements

Promotion now requires:

- source file has valid core frontmatter
- source `tenant_id`, `customer_id`, and `project_id` match CLI args
- source `status` is `reviewed` or `promoted`
- source `review_status` is `reviewed` or `approved`
- target folder matches source `doc_type`
- shared visibility has approved sanitization
- review artifact approves the promotion
- optional `-SourceHash` matches the source file

Promotion writes an audit manifest to `agent-memory/evidence/promotions/`.
