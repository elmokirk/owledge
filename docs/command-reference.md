# Command Reference

Owledge is Python-first. Use `tools/owledge.py` for public workflows and
`tools/agent_memory_cli.py` for lower-level memory operations.

## Public Owledge CLI

| Command | Writes | Purpose |
| --- | --- | --- |
| `python tools/owledge.py doctor --project-root .` | No | Diagnose kit or host setup |
| `python tools/owledge.py init-project --target /path/to/project` | Yes | Add Owledge files to an existing coding project |
| `python tools/owledge.py quickstart --target /path/to/project` | Yes | Initialize, run doctor, and validate in one simple project-local flow |
| `python tools/owledge.py add-kb-module --knowledgebase-root /path/to/vault` | Yes | Add a drop-in module to an existing Markdown KB |
| `python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --verify` | Yes | Generate a minimal project-local kit |
| `python tools/owledge.py install-addon --project-root . --addon project-snapshot-kit` | Yes | Install an optional add-on without changing the core setup |
| `python tools/owledge.py project-snapshot --project-root . --snapshots-only` | Yes | Generate optional Project Snapshot Kit Markdown snapshots |
| `python tools/owledge.py project-snapshot --project-root . --render-html` | Yes | Render optional static dashboard pages from existing snapshots |
| `python tools/owledge.py project-snapshot --project-root . --yes` | Yes | Generate snapshots and dashboard pages without prompts |
| `python tools/owledge.py build-context-pack --project-root . --task-id publish-v1` | No | Generate scoped task context |
| `python tools/owledge.py test public-docs --project-root .` | No | Check public docs integrity |
| `python tools/owledge.py test release-trust --project-root .` | No | Check version alignment, product naming, and bounded runtime claims |
| `python tools/owledge.py test principles-only --project-root .` | No | Check the no-plugin/no-generator principles integration path |
| `python tools/owledge.py test kb-ingestion-safety --project-root .` | Yes, temp KB | Check metadata-first non-destructive KB integration |
| `python tools/owledge.py test generated-kit-surface --project-root .` | Yes, temp projects | Check generated kits for platform-neutral Python surface |
| `python tools/owledge.py test quality-ratchet --project-root .` | Yes, ignored reports | Run platform, ingestion, runtime, retrieval, benchmark, and QA guardrails |
| `python tools/owledge.py test poweruser-simulations --project-root .` | Yes, temp project | Run dirty-vault and first-user DX simulations |
| `python tools/owledge.py test runtime-adapters --project-root .` | Yes, temp project | Smoke-test plugin runtime capture |
| `python tools/owledge.py finalization-gates --project-root . --include-compliance` | Yes | Run release gates |
| `python tools/owledge.py benchmark --project-root . --scale-files 100,1000,10000` | Yes, ignored results | Run local benchmark harness |

## Lower-Level Memory CLI

| Command | Writes | Purpose |
| --- | --- | --- |
| `python tools/agent_memory_cli.py --project-root . validate-memory --strict` | No | Validate frontmatter, IDs, edges, and memory records |
| `python tools/agent_memory_cli.py --project-root . build-memory-index` | Yes | Generate full memory indexes |
| `python tools/agent_memory_cli.py --project-root . build-memory-index --incremental --track-tombstones` | Yes | Incremental index with tombstone tracking |
| `python tools/agent_memory_cli.py --project-root . build-project-snapshot` | Yes | Lower-level optional Project Snapshot Kit snapshot builder |
| `python tools/agent_memory_cli.py --project-root . audit-retention` | No | Preview retention, stale, expiry, and review-cycle findings |
| `python tools/agent_memory_cli.py --project-root . review-memory-conflicts` | No | Detect stale records and contradiction edges |
| `python tools/agent_memory_cli.py --project-root . scan-memory-sensitive-data` | No | Scan memory and private runtime logs for secret-like content |
| `python tools/agent_memory_cli.py --project-root . run-review-workflow --review-type expert-lens --subject docs/README.md` | Yes | Create review/evaluation artifacts |
| `python tools/agent_memory_cli.py --project-root . export-rag-documents --corpus-type shared` | Yes | Generate reviewed RAG export |
| `python tools/agent_memory_cli.py --project-root . export-lightrag --corpus-type shared` | Yes | Generate LightRAG export |
| `python tools/agent_memory_cli.py --project-root . export-graphrag --corpus-type shared` | Yes | Generate GraphRAG export |
| `python tools/agent_memory_cli.py --project-root . render-memory-report --report-type project-dashboard --audience private` | Yes | Generate local HTML report |

## Existing Markdown Knowledgebase Module

```bash
python tools/owledge.py add-kb-module --knowledgebase-root /path/to/knowledgebase --include-cli
```

With an existing vault map:

```bash
python tools/owledge.py add-kb-module --knowledgebase-root /path/to/knowledgebase --map-file agent-memory-map.json
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
`agent-memory/project-snapshot/project-snapshot-manifest.json` for future
agent-authored narrative refreshes.

`--render-html` uses existing Markdown snapshots and does not update them.

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
`agent-memory/exports/finalization-gates/latest.json`; the Markdown summary is
`agent-memory/exports/finalization-gates/latest.md`.
The quality ratchet summary is written to
`agent-memory/exports/finalization-gates/quality-ratchet-summary.json`.

## Scope Rules

For aggregate roots, pass explicit scope arguments to lower-level exports and
reports whenever multiple tenants or customers are present:

```bash
python tools/agent_memory_cli.py --project-root . export-rag-documents --corpus-type shared --tenant-id tenant-a --customer-id customer-a --project-id project-a
```

## Promotion Requirements

Promotion requires valid source frontmatter, matching scope, reviewed status,
approved review evidence, safe shared visibility, and an optional source hash
match. Promotion writes an audit manifest to
`agent-memory/evidence/promotions/`.
