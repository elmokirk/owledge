---
memory_id: "mem:owledge:global:owledge:decision:post-v1-erasure-extensibility-resource-link-2026-08-12"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "decision_record"
document_version: 1
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Post-v1 erasure, extensibility, resource links, and upgrade architecture decision"
summary: "Owner decision to keep enterprise bounded erasure outside v1 while adding only the compatibility seams needed for modular extensions, linked source resources, deterministic health, and transactional upgrades."
concept_tags: ["post-v1-roadmap", "bounded-erasure", "extensions", "resource-ref", "upgrade-safety"]
stack_tags: ["python", "markdown", "mcp", "git"]
problem_patterns: ["enterprise-scope-creep", "plugin-core-coupling", "binary-content-in-canonical-memory", "unsafe-upgrade"]
architecture_patterns: ["ports-and-adapters", "managed-surface-manifest", "transactional-upgrade", "external-resource-reference"]
failure_modes: ["pii-masking-treated-as-erasure", "extension-bypasses-core-policy", "upgrade-overwrites-user-knowledge", "missing-source-provenance"]
confidence: 0.97
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-12T14:32:51+02:00"
updated_at: "2026-08-12T14:32:51+02:00"
source_hash: ""
reusable_lessons:
  - "Keep general source withdrawal and projection cleanup in Core; keep subject-rights orchestration in a later enterprise module."
  - "A small compatibility seam is cheaper than either a premature plugin SDK or a later storage-breaking migration."
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:research:enterprise-agentic-knowledge-and-deterministic-erasure-architecture-2026-08-12"
    confidence: 1.0
    reason: "Uses the research distinction between masking, anonymisation, deletion, and coverage-bounded erasure."
  - type: "relates_to"
    target: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
    confidence: 1.0
    reason: "Defines which seams enter the existing V1 tickets and which products remain post-v1."
---

# Post-v1 Erasure, Extensibility, Resource Links, and Upgrade Decision

## Owner Decision

The owner classifies the coverage-bounded personal-data erasure/DSAR control
plane as **relevant but non-essential after V1**, not as V1 Beta scope. V1 keeps
only general lifecycle hygiene that benefits every user: stable identities,
provenance, revisions, source withdrawal, access revocation, tombstones,
derived-projection cleanup, idempotent semantic operations, receipts, policy,
and adapter manifests.

A PII Masker remains an optional future detection/redaction adapter. It is not
an anonymisation, deletion, lineage, or compliance guarantee. The exact tool is
unresolved until the owner supplies its package name or repository.

## Minimal V1 Compatibility Seams

| Seam | V1 requirement | Explicit non-goal |
| --- | --- | --- |
| Managed Surface Manifest | Classify installed files as Core-managed, user-managed, generated, or extension-managed; record installed version and hashes | no marketplace or third-party registry |
| Upgrade Transaction | Preflight doctor, dry-run/diff, checkpoint, apply, postflight health, receipt, and recoverable rollback boundary | no destructive rewrite of user-authored knowledge |
| Module Manifest | Module kind, Core API compatibility range, permissions, profiles, migrations, health, cleanup, and uninstall declarations | no stable public plugin SDK promise before V1 contracts freeze |
| `ResourceRef` | Stable source ID, relation, locator, media type, hash, size, data class, availability/access state, and extraction provenance | no binary store, upload service, transcription engine, or arbitrary-path retrieval |
| Health Profiles | Separate `system.doctor`, `knowledge.health`, and `hub.health` with a shared result envelope | no generic observability backend or dashboard dependency |

These seams are additive extensions of the already approved `1B+ / 2C+ / 3B`
architecture. They do not add a new V1 subsystem or unlock V0.8 work.

## Post-v1 Roadmap Queue

| Capability | Priority after V1 | Score | Dependency/trigger |
| --- | ---: | ---: | --- |
| Media/source-link adapter over `ResourceRef` | P1 | 84 | stable profiles and real user demand |
| Voice transcription ingestion adapter | P2 | 69 | external transcription provider plus provenance policy |
| Bounded Erasure/DSAR control plane | Enterprise P1 | 78 | customer/legal requirement and registered connector coverage |
| PII detection/redaction adapter | P2 | 67 | exact tool evaluation, false-positive/negative corpus, policy owner |
| Third-party module SDK/marketplace | P2/P3 | 61 | frozen Core API and supply-chain proof |
| Universal connector suite | P3 | 36 | repeated paid customer demand; never speculative Core work |
| Full Owledge agent harness/scheduler | Discovery | 45 | measured gap not served by Pi, Hermes, cron, or workflow engines |

Scoring uses the session weights: 25% Core Fit, 20% User Value, 20%
Architecture Leverage, 15% Trust/Risk Reduction, 10% Adoption, and 10% inverse
Complexity.

## Product Position

Owledge remains a deterministic Knowledge Librarian and planning/memory control
plane, not a file warehouse, transcription product, observability platform, or
privacy-management suite. Its differentiator is governed, scope-aware,
provenance-preserving knowledge reuse across humans and agents with small,
explainable context packs and authorized source drill-down.
