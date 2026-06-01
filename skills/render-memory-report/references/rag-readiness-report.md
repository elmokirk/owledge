# RAG Readiness Report

## Use When

Use when the user asks whether memory is ready for RAG, LightRAG, GraphRAG, vector DB ingestion, shared corpus, or retrieval.

## Sources

Prefer:

- `agent-memory/indexes/*.jsonl`
- `agent-memory/exports/rag/`
- `agent-memory/exports/lightrag/`
- `agent-memory/exports/graphrag/`
- schemas and validation outputs

## Sections

| Section | Purpose |
| --- | --- |
| Readiness score | Executive summary |
| Corpus composition | Counts by doc type and status |
| Safety gates | Private/shared exclusions |
| Broken edges | Missing graph targets |
| Export status | RAG/LightRAG/GraphRAG files |
| Ingestion commands | Exact next commands |
| Sources | Links and hashes |

## Visual Pattern

Use score panels, corpus tables, pass/fail gates, and graph summary cards.
