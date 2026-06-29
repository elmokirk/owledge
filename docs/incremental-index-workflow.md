# Incremental Index Workflow

Owledge is Markdown-first. Files under `.owledge/` and approved project context files are the source of truth. Indexes, manifests, tombstones, RAG exports, LightRAG exports, GraphRAG exports, and hub payloads are generated operational views. They can be deleted and rebuilt from Markdown.

## Generated Files

| Artifact | Role |
| --- | --- |
| `.owledge/indexes/memory-index.jsonl` | Generated JSONL view of memory records for agents, QA, reports, and export tools |
| `.owledge/indexes/memory-index-manifest.json` | Generated run metadata: mode, counts, source hashes, generated timestamp, and indexed records |
| `.owledge/indexes/memory-index-tombstones.jsonl` | Generated deletion metadata for files that previously appeared in an index but no longer exist |
| `.owledge/exports/rag/` | Generated RAG documents from reviewed/promoted, exportable memory |
| `.owledge/exports/lightrag/` | Generated LightRAG arrays and manifest |
| `.owledge/exports/graphrag/` | Generated graph nodes, edges, and manifest |

Do not edit generated index rows, manifests, tombstones, or exports as canonical memory. Fix the Markdown source, then rebuild.

## Full Rebuild vs Incremental

Use a full rebuild when:

- bootstrapping a project or recovering from unknown state
- changing frontmatter schema, indexing rules, path filters, or export eligibility
- moving many files between memory folders
- validating before release, hub sync, or broad RAG export
- an index, manifest, or tombstone file is missing, corrupt, or suspected stale

Use incremental mode when:

- normal agent work changed a small number of Markdown memory files
- you need a fast freshness update before context-pack, QA, RAG-readiness, or dashboard work
- the previous index manifest is present and matches the same project root and filter rules
- the tool can compare current file hash/mtime data with the previous manifest

When no prior manifest exists, incremental mode falls back to the previous index rows where possible and updates every record it cannot verify.

## Tombstone Semantics

Deleted files are not forgotten silently. When a file that appeared in the previous index is absent from the current scan, incremental indexing identifies a deleted record. When `-TrackTombstones` is used, it writes a tombstone with:

- `memory_id`
- `source_path`
- previous `source_hash`
- `deleted_at`
- `reason`

Tombstones exist for hub sync, auditability, RAG freshness, and dashboard diagnostics. They tell downstream systems to remove or mark stale content that was previously exported. Tombstones are generated operational metadata, not canonical knowledge.

By default, tombstones must not enter shared RAG corpora. Shared RAG exports should only include current exportable memory records that pass visibility, review, and sanitization gates.

## QA And Definition Of Done

An incremental index run is ready for phase QA when:

- output reports `changed`, `unchanged`, `deleted`, and `tombstoned`
- deleted records have tombstones with `memory_id`, path, hash, `deleted_at`, and reason
- generated export folders are not indexed as memory sources:
  - `.owledge/exports/rag/`
  - `.owledge/exports/lightrag/`
  - `.owledge/exports/graphrag/`
  - `global-memory/exports/rag/`
  - `global-memory/exports/lightrag/`
  - `global-memory/exports/graphrag/`
- `.owledge/indexes/memory-index.jsonl` remains valid JSONL: every non-empty line parses as one JSON object
- index rows point back to source Markdown paths and source hashes
- manifests and tombstones are treated as generated metadata and are not promoted as canonical memory
- tombstones do not enter shared RAG by default
- RAG, LightRAG, GraphRAG, and hub sync consumers use tombstones only to expire stale downstream records

Validate the generated index with a full rebuild:

```bash
python tools/owledge_core.py --project-root . build-memory-index
```

Run an incremental update with tombstone tracking:

```bash
python tools/owledge_core.py --project-root . build-memory-index --incremental --track-tombstones
```

The command writes `.owledge/indexes/memory-index.jsonl`, `.owledge/indexes/memory-index-manifest.json`, and, when requested, `.owledge/indexes/memory-index-tombstones.jsonl`.

## RAG And Hub Safety

RAG and hub systems are consumers. They must not become canonical memory stores.

- Export only current records that pass the export tool's review, visibility, sanitization, and scope checks.
- Use tombstones to remove or mark stale downstream records from previous exports.
- Keep private user memory and raw session material out of shared exports unless a reviewed, sanitized derivative is explicitly promoted.
- Preserve tenant, customer, and project scope in every manifest and export.
- Rebuild from Markdown whenever downstream state conflicts with source files.
