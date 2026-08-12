---
title: "Owledge V1 Contract Architecture"
document_version: 2
status: active
---

# Owledge V1 Contract Architecture

Owledge V1 uses a small, versioned Core contract. Project Markdown and Git are
canonical; adapters and derived indexes are not a second source of truth.

## Contract layers

1. A common artifact envelope supplies stable identity, distinct schema/profile/
   document revisions, integrity facts, authority scope, lifecycle, and
   provenance.
2. Artifact profiles add only domain-specific validation. Unknown namespaced
   extensions are preserved but inert and cannot widen policy.
3. Query envelopes plan authorized reads. Command envelopes require identity,
   expected revision/base hash, idempotency, authorized transition, and a
   receipt; they never provide arbitrary file writes.
4. Migration is opt-in, preview-first, checkpointed, receipt-backed, and
   recoverable. User-owned Markdown is never silently overwritten.

The shipped `tools/owledge_contracts.py` validator can produce a preview mapping
for legacy frontmatter. It does not read caller-supplied paths as authority and
does not apply a write; the server-resolved project scope, owner, source hash,
preserved legacy fields, and `apply: false` receipt are explicit.

## Scope and product boundary

Scope (`project_user`, `user_global`, `enterprise`), knowledge abstraction, and
lifecycle are independent. Reviewed global essences orient retrieval but do not
automatically reveal source projects; deep retrieval is separately authorized
and budgeted.

Standalone Core is the GA target. A one-organization Hub is Pilot/Beta only.
Owledge does not promise a public plugin marketplace, binary store,
transcription product, DSAR orchestration, generic telemetry backend, or hosted
multi-tenant SaaS in V1.

## Extension safety

Managed surface, module, resource-reference, and health contracts allow future
adapters without granting storage or authority bypasses. The normative records
are [Core Contract Boundaries](../internal/owledge/decisions/adr-080-01-core-contract-boundaries-2026-08-12.md),
[Preview-First Migrations](../internal/owledge/decisions/adr-080-02-preview-first-migrations-2026-08-12.md),
and [Managed Extension Seams](../internal/owledge/decisions/adr-080-03-managed-extension-seams-2026-08-12.md).
