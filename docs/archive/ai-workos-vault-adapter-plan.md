# AI-WorkOS Vault Adapter Plan

The uploaded AI-WorkOS Obsidian Vault should become an adapter, not a second source of truth. Agent Memory Kit stays the canonical Markdown/RAG contract; the vault becomes an import, discovery, and migration layer for broader concept and project collections.

## Target Architecture

| Layer | Responsibility | Owner |
| --- | --- | --- |
| AI-WorkOS Vault | Raw inboxes, Obsidian notes, concept collections, legacy project maps | External adapter input |
| Adapter index | Read-only scan, field mapping, duplicate detection, migration preview | New adapter tooling |
| Agent Memory Kit | Canonical memory, schemas, typed edges, RAG exports, report rendering | Core system |
| RAG/GraphRAG | Consumers of reviewed Agent Memory exports | Downstream systems |

## Optimal Path

1. Keep the vault zip/folder outside the project core.
2. Add an optional adapter folder later, for example `adapters/ai-workos-vault/`.
3. Build a read-only scanner that emits `agent-memory/indexes/ai-workos-import-candidates.jsonl`.
4. Map vault frontmatter into Agent Memory fields without modifying source vault files.
5. Convert Obsidian links into candidate typed edges.
6. Run duplicate and overlap scoring before import.
7. Write migrated outputs as `status=draft`, never as promoted canonical memory.
8. Require curator review before any migrated record becomes RAG-exportable.

## Field Mapping

| AI-WorkOS Field | Agent Memory Field | Notes |
| --- | --- | --- |
| `type` | `doc_type` | Map with a controlled alias table |
| `id` | legacy source id | Do not use directly as `memory_id` |
| `name` | `semantic_title` | Human title |
| `status` | `status` | Needs vocabulary normalization |
| `canonical` | `review_status` candidate | `true` can suggest reviewed, not approved |
| `kb_ready` | export eligibility candidate | Must still pass Agent Memory validation |
| `confidentiality` | `data_class` and `visibility` | Needs explicit policy mapping |
| `source_ids` | evidence links / `derived_from` edges | Preserve provenance |
| Obsidian links | typed `edges` | Convert only when target can be resolved |
| folder path | `source_path` | Keep original vault path |

## Benefits

| Benefit | Impact |
| --- | --- |
| Reuses existing concept work | The old vault becomes useful immediately without weakening the new core |
| Keeps project memory portable | Agent Memory stays clean and project-local |
| Better cross-project discovery | Vault merge maps and project registry can seed `find-parallels` |
| Safer RAG ingestion | Raw inboxes stay outside shared RAG unless reviewed |
| Obsidian compatibility remains possible | The vault can still be used by humans as an ideation surface |

## Costs And Risks

| Risk | Mitigation |
| --- | --- |
| Two taxonomies create confusion | Treat AI-WorkOS as adapter input, not canonical memory |
| Weaker frontmatter could pollute strict schemas | Import as draft candidates only |
| Obsidian links may not resolve to stable IDs | Emit unresolved edge warnings |
| Confidentiality mapping can be wrong | Require explicit data-class review before export |
| Duplicate project ideas can multiply | Run merge scoring before migration |
| Large raw inboxes can hurt token/RAG quality | Summarize and hash raw sources instead of ingesting them |

## Adapter Commands To Build Later

| Command | Purpose |
| --- | --- |
| `scan-ai-workos-vault` | Read vault files and create import candidate JSONL |
| `map-ai-workos-frontmatter` | Normalize fields and report missing required values |
| `convert-obsidian-edges` | Resolve wiki links into candidate typed edges |
| `score-vault-overlaps` | Apply merge-map scoring against existing Agent Memory records |
| `import-vault-candidates` | Write draft Agent Memory files with provenance |
| `validate-vault-import` | Ensure migrated drafts cannot leak into shared RAG |

## Recommendation

Build this as an optional adapter after the first GitHub publish. The core is already stricter and more RAG-ready than the vault. The vault is valuable as a migration source, concept inbox, and project registry seed, but merging it directly would reduce maintainability and compliance clarity.
