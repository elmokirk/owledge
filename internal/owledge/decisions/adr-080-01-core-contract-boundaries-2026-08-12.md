---
memory_id: "mem:owledge:global:owledge:decision:adr-080-01-core-contract-boundaries-2026-08-12"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "architecture_decision_record"
document_version: 1
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "ADR-080-01 Core contract boundaries"
summary: "Locks the small transport-neutral Core contract, version separation, authority axes, and explicit V1 non-goals before schema implementation."
concept_tags: ["adr", "core-contract", "schema-registry", "authority", "migration"]
stack_tags: ["markdown", "yaml", "json", "mcp"]
problem_patterns: ["transport-owned-policy", "ambiguous-authority", "silent-revision-rewrite"]
architecture_patterns: ["transport-neutral-core", "orthogonal-authority-axes", "fail-closed-capability-envelope"]
failure_modes: ["adapter-bypasses-core", "global-scope-implies-drilldown", "migration-erases-revision-history"]
reusable_lessons:
  - "Transport adapters may narrow Core policy but must never establish a competing authority model."
  - "Identity, revision, authority scope, knowledge abstraction, and lifecycle need independent contracts."
confidence: 0.98
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-12T16:00:00+02:00"
updated_at: "2026-08-12T16:00:00+02:00"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:decision:v1-schema-global-knowledge-health-matrix-2026-08-12"
    confidence: 1.0
    reason: "Implements the owner-locked 1B+/2C+/3B architecture baseline."
---

# ADR-080-01: Core Contract Boundaries

## Status

Accepted for `OW-080-01`. This ADR implements the owner-locked `1B+ / 2C+ /
3B` baseline from [the decision matrix](v1-schema-global-knowledge-health-decision-matrix-2026-08-12.md).

## Decision

1. The Core is transport-neutral and owns only deterministic validation,
   authorization evaluation, lifecycle transitions, identity/revision checks,
   receipts, and read/query planning. MCP, CLI, Pi, Owlib, and Hub are adapters;
   none may establish a competing canonical store or bypass Core policy.
2. Every managed artifact uses a small common envelope plus an
   artifact-specific profile. `schema_version`, `profile_version`,
   `document_version`, and `source_hash` are distinct facts. A material edit to
   the same stable `memory_id` increments `document_version` exactly once;
   schema/profile migration never silently replaces that revision fact.
3. Unknown namespaced fields are preserved but inert by default. They cannot
   widen a Core permission, scope, lifecycle transition, or validation rule.
4. Authority scope (`project_user`, `user_global`, `enterprise`), knowledge
   abstraction, and lifecycle are orthogonal axes. A global essence does not
   confer project drill-down; every deep resolution re-evaluates principal,
   scope, data class, availability, freshness, and token budget.
5. Query and Command envelopes remain separate. A command includes target
   identity, expected revision/base hash, idempotency key, requested transition,
   authorization context, and a conflict/reconciliation receipt. No transport
   receives arbitrary-file-write authority.
6. Markdown and Git remain canonical for project truth. The Standalone Core may
   be GA only at its later evidence gate; the one-organization Hub remains
   Pilot/Beta and owns no hidden canonical substitute.

## Consequences

`OW-080-02` implements the profiles and registry against these boundaries.
`OW-090-04` is the sole semantic mutation interface. Later adapters can add
capabilities only by declared compatibility and never by importing Core-internal
storage semantics.

## Lifecycle State Machine

The lifecycle vocabulary is `candidate`, `raw_inbox`, `reviewed`, `canonical`,
`superseded`, and `archived`. Only these directed transitions are valid:

| From | To | Required authority and preconditions |
| --- | --- | --- |
| `candidate` | `raw_inbox`, `archived` | Authorized creator may submit or discard; creation receipt and provenance required. |
| `raw_inbox` | `reviewed`, `archived` | Explicit human/policy review with reviewer identity, rationale, and receipt. No automatic promotion. |
| `reviewed` | `canonical`, `superseded`, `archived` | Authorized owner/policy plus current revision and evidence/provenance validation. |
| `canonical` | `superseded`, `archived` | Authorized owner/policy; successor or retention reason and source-withdrawal check are required. |
| `superseded` | `archived` | Retention policy or authorized owner with a receipt. |

Every transition is a semantic command with target `memory_id`, expected
revision/base hash, idempotency key, effective policy, timestamp, actor, result,
and conflict/reconciliation receipt. Any omitted precondition, unknown state,
or non-listed transition fails closed. Reinstatement is never an in-place
transition: a new candidate must cite the archived source and pass review.

Agents may create `candidate` or Evidence material only within their effective
scope. They may not promote an artifact to `reviewed` or `canonical` merely from
their own output.

## Capability Envelope and Compatibility Window

A capability envelope contains `protocol_version`, `core_api_range`,
`capability_id`, `operation_kind` (`query` or `command`), requested scopes,
principal/effective-permission summary, data class, resource limits, required
features, optional namespaced extensions, and a deterministic result status.
The result is `supported`, `unsupported`, or `denied`, with a stable reason
code, remediation/migration hint where relevant, and no widened fallback.

Negotiation takes the intersection of declared Core and adapter ranges,
permissions, scopes, and required features. An unknown required capability, an
incompatible API range, or a denied scope is rejected before any operation.
Unknown optional namespaced extensions are preserved inertly.

The V1 compatibility window supports the current schema/profile major for reads
and writes. Pre-registry legacy artifacts remain readable and preview-migratable
through the V1 release train, but are never silently rewritten and cannot be
created by new writes. The v1.0 owner-alignment review decides any retirement or
major-version extension; no earlier ticket may silently shorten this window.

## Rejected Alternatives

- Database-as-canonical or a shadow canonical index: rejected because it breaks
  Markdown/Git authority and source-withdrawal guarantees.
- A single broad mandatory frontmatter list: rejected because it causes dummy
  metadata and schema ossification.
- Automatic promotion or autonomous conflict resolution: rejected because
  lifecycle and authority require explicit policy and receipts.
- A generic agent harness, scheduler, dashboard, or public plugin SDK in Core:
  rejected as V1 scope expansion.
