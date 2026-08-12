---
memory_id: "mem:owledge:global:owledge:decision:adr-080-03-managed-extension-seams-2026-08-12"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "architecture_decision_record"
document_version: 1
status: "accepted"
visibility: "private"
data_class: "internal"
semantic_title: "ADR-080-03 Managed surfaces and extension seams"
summary: "Defines the minimal managed-surface, module, resource, and health contracts without creating a plugin marketplace or binary store."
concept_tags: ["adr", "managed-surface", "module-manifest", "resource-ref", "health"]
stack_tags: ["markdown", "json", "mcp"]
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-12T16:00:00+02:00"
updated_at: "2026-08-12T16:00:00+02:00"
source_hash: ""
---

# ADR-080-03: Managed Surfaces and Extension Seams

## Status

Accepted for `OW-080-01`, derived from the
[post-V1 extensibility decision](post-v1-erasure-extensibility-and-resource-link-decision-2026-08-12.md).

## Decision

The following are compatibility contracts, not newly shipped V1 subsystems:

| Contract | Required declaration | Boundary |
| --- | --- | --- |
| Managed Surface Manifest | Core-managed, user-managed, generated, or extension-managed files; installed version and hashes | Core updates may alter only Core-managed material. |
| Module Manifest | module kind, Core API range, permissions, profiles, migrations, health, cleanup, uninstall | No public SDK/marketplace promise and no Core-internal storage access. |
| `ResourceRef` | stable source ID, relation, locator, media type, hash, size, data class, availability/access, extraction provenance | No binary store, upload service, transcription engine, or arbitrary-path retrieval. |
| Health result envelope | profile, checks, severity, stable IDs, bounded receipts, timestamps | `system.doctor`, `knowledge.health`, and `hub.health` remain distinct; no raw knowledge/prompt telemetry. |

Permissions only narrow the Core policy. A module cannot declare itself healthy,
compatible, or authorized merely through its own manifest; Core validates the
declared compatibility range and effective permissions.

## Consequences

OW-080-02 supplies the typed profiles. OW-080-09 implements Knowledge Health;
OW-100-03/11 implement the bounded system/Hub surfaces. Subject-rights erasure,
third-party marketplace, universal connectors, binary storage, and transcription
remain post-V1 decisions.
