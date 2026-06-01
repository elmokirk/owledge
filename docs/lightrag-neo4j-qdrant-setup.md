# LightRAG + Neo4j + Qdrant Setup

Date: 2026-05-16  
Status: integration plan  
Scope: connect the Markdown-first Agent Memory Kit to an existing local LightRAG installation using Neo4j for graph storage and Qdrant for vector storage.

## Positioning

LightRAG, Neo4j and Qdrant are retrieval infrastructure. They must consume reviewed Agent Memory exports, but they must not become the source of truth.

```text
Markdown memory -> validated index -> reviewed RAG export -> LightRAG ingest -> Neo4j/Qdrant retrieval
```

This integration is one adapter profile, not a hard dependency. The same export contract should support LightRAG, GraphRAG, custom vector databases, local search, MCP tools, dashboards and future retrieval systems.

## Best Target Setup

| Layer | Recommended Role |
| --- | --- |
| `agent-memory/` | Canonical project memory, summaries, lessons, decisions, patterns |
| `agent-memory/indexes/memory-index.jsonl` | Fast local metadata index |
| `agent-memory/exports/rag/` | Neutral reviewed JSONL corpus |
| `agent-memory/exports/lightrag/` | LightRAG-ready `texts`, `ids`, `file_paths`, `manifest` |
| LightRAG workspace | Project/customer/tenant scoped retrieval runtime |
| Qdrant | Vector storage for semantic retrieval |
| Neo4j | Graph storage for entity/relationship retrieval |

## Recommended Isolation Model

Use LightRAG workspaces to isolate tenants/projects.

| Agent Memory Scope | LightRAG Workspace |
| --- | --- |
| One local project | `project_id` |
| Customer hub | `tenant_id__customer_id` |
| Enterprise hub project | `tenant_id__customer_id__project_id` |
| Shared approved knowledge | `shared` |

Do not mix private customer corpora into `shared`. Shared ingestion should only use approved and sanitized records.

## Environment Baseline

Your LightRAG runtime should use Neo4j and Qdrant as storage backends.

```powershell
$env:NEO4J_URI="neo4j://localhost:7687"
$env:NEO4J_USERNAME="neo4j"
$env:NEO4J_PASSWORD="<your-password>"
$env:NEO4J_DATABASE="neo4j"

$env:LIGHTRAG_GRAPH_STORAGE="Neo4JStorage"
$env:LIGHTRAG_VECTOR_STORAGE="QdrantVectorDBStorage"
$env:WORKSPACE="tenant-local__customer-local__project-local"
```

Keep provider keys and database passwords outside Markdown, Git, reports, exports and session logs.

## Agent Memory Export Flow

From a bootstrapped project:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\validate-memory.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build-memory-index.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-rag-documents.ps1 -ProjectRoot . -CorpusType private
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-lightrag.ps1 -ProjectRoot . -CorpusType private
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-graphrag.ps1 -ProjectRoot . -CorpusType private
```

For an enterprise hub or multi-project vault, always scope the export:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-lightrag.ps1 `
  -ProjectRoot . `
  -CorpusType private `
  -TenantId tenant-a `
  -CustomerId customer-a `
  -ProjectId project-a
```

For shared/cross-project retrieval:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-lightrag.ps1 -ProjectRoot . -CorpusType shared
```

Shared export includes only records that satisfy the shared gates:

- `visibility=shared`
- `review_status=approved`
- `sanitization_status=approved`
- safe `data_class`
- accepted document type

## LightRAG Export Files

The exporter writes:

| File | Use |
| --- | --- |
| `agent-memory/exports/lightrag/texts.json` | Array of retrieval texts |
| `agent-memory/exports/lightrag/ids.json` | Stable IDs from `memory_id` |
| `agent-memory/exports/lightrag/file_paths.json` | Source paths for citation |
| `agent-memory/exports/lightrag/manifest.json` | Export metadata, hashes, generation ID |
| `agent-memory/exports/lightrag/latest.json` | Pointer to immutable generation folder |

Use the immutable generation folder for reproducible ingestion when possible:

```text
agent-memory/exports/lightrag/generations/<generation_id>/
```

## Minimal Ingestion Adapter

Create this in your LightRAG project, not inside the Agent Memory Kit, unless you intentionally vendor an adapter later.

```python
import asyncio
import json
from pathlib import Path

from lightrag import LightRAG


EXPORT_DIR = Path(r"C:\path\to\project\agent-memory\exports\lightrag")
WORKING_DIR = r"C:\path\to\lightrag\storage"
WORKSPACE = "tenant-local__customer-local__project-local"


async def main():
    texts = json.loads((EXPORT_DIR / "texts.json").read_text(encoding="utf-8"))
    ids = json.loads((EXPORT_DIR / "ids.json").read_text(encoding="utf-8"))
    file_paths = json.loads((EXPORT_DIR / "file_paths.json").read_text(encoding="utf-8"))
    manifest = json.loads((EXPORT_DIR / "manifest.json").read_text(encoding="utf-8"))

    if not (len(texts) == len(ids) == len(file_paths)):
        raise RuntimeError("LightRAG export arrays have different lengths")

    rag = LightRAG(
        working_dir=WORKING_DIR,
        workspace=WORKSPACE,
        graph_storage="Neo4JStorage",
        vector_storage="QdrantVectorDBStorage",
        max_parallel_insert=4,
    )
    await rag.initialize_storages()

    await rag.ainsert(texts, ids=ids, file_paths=file_paths)

    print({
        "ingested": len(texts),
        "workspace": WORKSPACE,
        "generation_id": manifest.get("generation_id"),
        "rag_generation_id": manifest.get("rag_generation_id"),
    })


if __name__ == "__main__":
    asyncio.run(main())
```

## Ingestion Policy

| Corpus | Ingest Into | Rule |
| --- | --- | --- |
| Project private | Project workspace | For active project retrieval and agent context |
| Customer private | Customer workspace | Only if access boundaries are clear |
| Shared approved | `shared` workspace | For reusable lessons and cross-project patterns |
| Draft/debug | Temporary workspace | Local debugging only, never shared |

## Retrieval Use Cases

| Question Type | Preferred Corpus |
| --- | --- |
| "What is the current project context?" | project private |
| "What decisions were already made?" | project private + decisions |
| "Have we solved this before?" | shared + patterns + lessons |
| "What recurring agent failures exist?" | PI workspace + shared lessons |
| "Which projects are similar?" | shared + graph export + PI parallels |
| "What can be reused for this customer?" | customer private + shared |

## Neo4j / GraphRAG Alignment

Agent Memory already exports typed edges:

```text
agent-memory/exports/graphrag/nodes.jsonl
agent-memory/exports/graphrag/edges.jsonl
```

Use these as a deterministic graph layer next to LightRAG's extracted graph. The recommended long-term approach is:

1. Let LightRAG build its graph from reviewed text.
2. Keep Agent Memory typed edges as explicit human/agent-curated truth.
3. Compare extracted graph edges against frontmatter edges.
4. Promote only confirmed new relationships back into Markdown.

## Qdrant / Vector Alignment

Use `memory_id` as the stable document ID. It should not change when a file path changes.

Recommended payload fields for Qdrant or downstream retrieval traces:

| Field | Source |
| --- | --- |
| `memory_id` | LightRAG `ids.json` |
| `source_path` | `file_paths.json` |
| `source_hash` | `manifest.json` documents |
| `tenant_id` | export manifest |
| `customer_id` | export manifest |
| `project_id` | export manifest |
| `corpus_type` | export manifest |
| `generation_id` | export manifest |

## Validation Before Ingest

Run these before ingestion:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\memory-doctor.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\validate-memory.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-lightrag.ps1 -ProjectRoot . -CorpusType private
```

Then inspect:

```powershell
Get-Content .\agent-memory\exports\lightrag\manifest.json
Get-Content .\agent-memory\exports\lightrag\latest.json
```

## Do Not Do This

| Anti-Pattern | Reason |
| --- | --- |
| Embed raw sessions by default | Creates noisy, private, low-quality retrieval |
| Use Vector DB as source of truth | Breaks review, audit and portability |
| Mix tenants in one workspace without scope | Unsafe for agency and enterprise use |
| Re-ingest drafts into shared | Leaks unreviewed and possibly confidential output |
| Use file paths as stable IDs | Paths change; `memory_id` should not |
| Let LightRAG extracted edges overwrite Markdown edges | Contradictions and provenance would be lost |

## Recommended Next Implementation

Add a small local adapter in a later milestone:

| Task | Output |
| --- | --- |
| `tools/ingest-lightrag.ps1` | Wrapper that calls the user's local LightRAG adapter |
| `adapters/lightrag/ingest_agent_memory.py` | Optional sample adapter |
| `docs/lightrag-roundtrip-eval.md` | Test plan for insert, query, source citation, and stale export handling |
| Retrieval eval fixture | Known question set with expected memory IDs |

This should remain optional. The core kit should continue to work without LightRAG, Neo4j or Qdrant installed.
