---
memory_id: "mem:owledge:global:owledge:decision:adr-080-02-preview-first-migrations-2026-08-12"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "architecture_decision_record"
document_version: 1
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "ADR-080-02 Preview-first migration and compatibility"
summary: "Defines non-destructive, receipt-backed migration boundaries and compatibility behavior for Owledge-managed artifacts."
concept_tags: ["adr", "migration", "compatibility", "rollback", "revision"]
stack_tags: ["markdown", "yaml", "json"]
problem_patterns: ["silent-in-place-migration", "lossy-compatibility-fallback", "unrecoverable-partial-apply"]
architecture_patterns: ["preview-first-migration", "checkpointed-transaction", "immutable-migration-receipt"]
failure_modes: ["apply-without-preview", "user-content-overwrite", "ambiguous-mapping-accepted"]
reusable_lessons:
  - "A migration is safe only when its preview, checkpoint, postflight result, and receipt are independently inspectable."
  - "Compatibility must preserve stable identity and lifecycle history without making legacy writes permanent."
confidence: 0.98
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-12T16:00:00+02:00"
updated_at: "2026-08-12T16:00:00+02:00"
source_hash: ""
edges:
  - type: "depends_on"
    target: "mem:owledge:global:owledge:decision:adr-080-01-core-contract-boundaries-2026-08-12"
    confidence: 1.0
    reason: "Applies the Core identity, revision, authority, and compatibility boundaries to migrations."
---

# ADR-080-02: Preview-First Migrations

## Status

Accepted for `OW-080-01` and binding on `OW-080-02`, `OW-080-09`, and release
migration work.

## Decision

Migration is opt-in, preview-first, dry-run capable, and recoverable. A
transaction has six visible stages: preflight `system.doctor`, deterministic
diff/preview, checkpoint, apply, postflight health, and an immutable receipt.
Rollback restores only Core-managed material from the checkpoint; it never
silently rewrites user-authored Markdown, external resources, or user-managed
extension files.

Compatibility is explicit and bounded by ADR-080-01: the current
schema/profile major accepts reads and writes; pre-registry legacy artifacts
remain readable and preview-migratable only through V1. The v1.0 owner-alignment
review controls any retirement or major-version extension. Within that window:

- Legacy aliases may be read during the declared V1 compatibility window,
  but cannot replace the generic `document_version` contract.
- A migration emits an artifact-level mapping and receipt; an ambiguous or
  lossy mapping fails closed and asks for human resolution.
- Stable `memory_id`, source provenance, and lifecycle history survive a
  successful migration. Content hashes are recomputed facts, not identity.
- A destructive migration, automatic promotion, or an apply-without-preview
  operation is invalid by contract.

## Consequences

Schema implementation must expose dry-run and receipt fixtures before any
existing project is updated. Health/projection code may consume a migration
receipt but cannot treat an incomplete migration as a successful artifact.

## Rejected Alternatives

- In-place silent frontmatter rewrite: rejected because it can destroy
  user-authored meaning and hides compatibility risk.
- Permanent broad legacy support: rejected because it leaves ambiguous
  authority and revision semantics indefinitely.
- Best-effort partial apply: rejected because every accepted state needs a
  recoverable transaction boundary.
