# Incremental Index Finalization Sprint

Date: 2026-05-23  
Status: active  
Scope: P1 incremental memory indexes with manifest and tombstone tracking.

## Project Status Before Sprint

v0.4.0 P0 is publish-ready and staged. The reusable review workflow is complete. The next P1 bottleneck is index scalability: full rebuilds are simple and safe, but long-running multi-project hubs need change accounting, deletion visibility, and deterministic freshness metadata.

## Operating Model

The orchestration agent owns integration and final QA. Each task has a worker slice and a QA checker. Workers must use disjoint write scopes and must not revert other edits.

## Task Matrix

| Task | Worker Scope | QA Checker Scope | Definition Of Done | Quality Checks |
| --- | --- | --- | --- | --- |
| P1-T1 Index tooling | `tools/agent_memory_cli.py`, `tools/build-memory-index.ps1` | CLI behavior, wrapper behavior, atomic writes, tombstones | Full rebuild remains default; incremental mode updates changed/new records, preserves unchanged valid records, and tombstones deleted records when requested | Python compile, full build, incremental build, temp deletion simulation, JSONL parse |
| P1-T2 Index workflow docs | `docs/incremental-index-workflow.md`, command docs, README references, roadmap wording | Accuracy, source-of-truth boundary, RAG safety | Docs explain full vs incremental rebuild, manifest fields, tombstone semantics, QA, and RAG/Hub safety | Paths exist, syntax matches wrapper, no canonical-index claims |
| P1-T3 Contract integration | Required files and release docs | Contract coverage | New docs and wrapper behavior are protected by contract tests | `test-agent-memory-contracts` passes |
| P1-T4 End-to-end validation | Generated ignored index artifacts only | Release health | Local kit passes full validation after smoke tests | `validate-memory`, `test-agent-memory-contracts`, `memory-doctor` |

## Required Output Semantics

| Output | Path | Role | Canonical? |
| --- | --- | --- | --- |
| Memory index | `agent-memory/indexes/memory-index.jsonl` | Current generated retrieval/index view | No |
| Index manifest | `agent-memory/indexes/memory-index-manifest.json` | Build metadata, counts, generated time, mode | No |
| Tombstones | `agent-memory/indexes/memory-index-tombstones.jsonl` | Deletion visibility for hub sync and RAG freshness | No |

## Acceptance Criteria

- Full rebuild works without new flags.
- Incremental mode works with existing index and without an existing manifest.
- Deleted records are represented as tombstones only when tombstone tracking is requested.
- Tombstones are not treated as canonical memory and are not shared RAG input.
- Index and manifest writes are atomic.
- The command returns machine-readable counts for changed, unchanged, deleted, and total rows.
