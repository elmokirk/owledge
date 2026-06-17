# Command Reference

Owledge is Python-first. Use `tools/owledge.py` for public workflows and
`tools/agent_memory_cli.py` for lower-level memory operations.

## Public Owledge CLI

| Command | Writes | Purpose |
| --- | --- | --- |
| `python tools/owledge.py doctor --project-root .` | No | Diagnose kit or host setup |
| `python tools/owledge.py init-project --target /path/to/project` | Yes | Add Owledge files to an existing coding project |
| `python tools/owledge.py add-kb-module --knowledgebase-root /path/to/vault` | Yes | Add a drop-in module to an existing Markdown KB |
| `python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --verify` | Yes | Generate a minimal project-local kit |
| `python tools/owledge.py build-context-pack --project-root . --task-id publish-v1` | No | Generate scoped task context |
| `python tools/owledge.py test public-docs --project-root .` | No | Check public docs integrity |
| `python tools/owledge.py test runtime-adapters --project-root .` | Yes, temp project | Smoke-test plugin runtime capture |
| `python tools/owledge.py finalization-gates --project-root . --include-compliance` | Yes | Run release gates |
| `python tools/owledge.py benchmark --project-root .` | Yes, ignored results | Run local benchmark harness |

## Lower-Level Memory CLI

| Command | Writes | Purpose |
| --- | --- | --- |
| `python tools/agent_memory_cli.py --project-root . validate-memory --strict` | No | Validate frontmatter, IDs, edges, and memory records |
| `python tools/agent_memory_cli.py --project-root . build-memory-index` | Yes | Generate full memory indexes |
| `python tools/agent_memory_cli.py --project-root . build-memory-index --incremental --track-tombstones` | Yes | Incremental index with tombstone tracking |
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
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --include-plugin-adapter --verify
```

The generator uses an explicit copy manifest and excludes tests, generated
indexes, generated exports, and raw runtime sessions. Compliance Light remains
opt-in:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit-compliance --include-compliance --verify
```

## Finalization Gates

```bash
python tools/owledge.py finalization-gates --project-root . --include-compliance
python tools/owledge.py redteam-qa --project-root .
```

The finalization gate runs compile checks, skill validation, scenario tests,
public-docs integrity, contracts, doctor, validation, indexes, lifecycle checks,
runtime smoke tests, memory evals, retrieval fixture eval, KB-module safety, and
project-folder verification.

The latest machine-readable report is written to
`agent-memory/exports/finalization-gates/latest.json`; the Markdown summary is
`agent-memory/exports/finalization-gates/latest.md`.

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
