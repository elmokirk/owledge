# AI-WorkOS Obsidian Vault Merge Evaluation

Evaluation date: 2026-05-12

The uploaded `AI-WorkOS-Obsidian-Vault.zip` is strategically aligned with Agent Memory Kit, but it should not replace the Markdown-first core. It is best treated as a source concept library and optional enterprise-vault adapter.

Detailed implementation plan: [AI-WorkOS Vault Adapter Plan](ai-workos-vault-adapter-plan.md).

## Recommendation

| Decision | Rationale |
| --- | --- |
| Do not merge as-is | The vault has a separate folder taxonomy, Obsidian-oriented frontmatter, and broader inbox/processing semantics. Direct merge would dilute the stricter Agent Memory contracts. |
| Merge selected concepts | Merge map scoring, indexing tiers, graph vocabulary, and raw-to-reviewed lifecycle are useful and compatible. |
| Keep as optional adapter | A future migration tool can map vault fields into Agent Memory `memory_id`, `doc_type`, `status`, `review_status`, `sanitization_status`, `data_class`, and typed `edges`. |

## Merge Map

| Vault Artifact | Agent Memory Target | Action |
| --- | --- | --- |
| `00_SYSTEM/MERGE_MAP.md` | `find-parallels`, future merge-assessment docs | Merge scoring rubric |
| `00_SYSTEM/FRONTMATTER_SCHEMA.md` | `agent-memory/schemas/frontmatter.schema.json` | Map aliases only |
| `00_SYSTEM/GRAPH_SCHEMA.md` | GraphRAG schemas and export docs | Merge node/edge vocabulary as aliases |
| `00_SYSTEM/INGEST_PIPELINE.md` | runtime capture, compaction, promotion docs | Merge lifecycle language |
| `00_SYSTEM/RAG_INDEXING_POLICY.md` | RAG export policy | Merge tiering model |
| `05_AGENT_CONTEXT/global/GLOBAL_AGENT_CONTEXT.md` | runtime bridge skill and project router | Merge the "check registry first" rule |
| Obsidian folder structure | optional enterprise hub adapter | Keep separate |

## Migration Path

1. Build a read-only importer that scans the vault and emits a candidate `memory-index.jsonl`.
2. Map vault fields:
   - `type` -> `doc_type`
   - `id` -> legacy source id
   - `canonical` -> `review_status`
   - `kb_ready` -> export eligibility
   - `confidentiality` -> `data_class` and `visibility`
3. Convert Obsidian links and merge relations into typed `edges`.
4. Create draft `compiled` summaries for reviewed vault records.
5. Run validation before any RAG or LightRAG export.

## Keep Separate Until

- duplicate id handling is deterministic
- confidentiality mapping is reviewed
- Obsidian wiki links are converted to stable `memory_id` targets
- shared corpus export excludes private raw inbox files
- migration output passes `validate-memory`
