---
memory_id: "mem:owledge:global:owledge:decision:add-on-decision-layer-final-bridge-2026-07-27"
doc_type: "decision"
status: "accepted"
visibility: "private"
data_class: "internal"
semantic_title: "Add-on Decision Layer final project hardening bridge"
summary: "Final owner-approved mapping from KEOS and Hermes candidate feedback into v0.7.1 amendments, v0.8/v0.9/v1 tickets, deferred work, and rejected shapes."
created_at: "2026-07-27T00:00:00Z"
updated_at: "2026-07-27T00:00:00Z"
review_status: "accepted"
source_hash: "88e081d0e573fd6166ccf60f9d6d6b9fb858c77e06cdb3657b4064f810f18133"
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:report:add-on-decision-layer-keos-handout-red-team-2026-07-27"
    confidence: 1.0
    reason: "Promotes the reviewed candidate feedback into an owner-approved implementation bridge."
  - type: "amends"
    target: "mem:owledge:global:owledge:plan:v0.7.1-public-docs-adoption"
    confidence: 0.9
    reason: "Adds only documentation-truth and read-only integration boundaries to v0.7.1."
---

# Add-on Decision Layer Final Bridge

## Decision

The owner approved the Add-on Decision Layer rubric, the narrow v0.7.1
documentation-truth amendments, and the separated
audience/transferability/privacy model on 2026-07-27.

This bridge is the implementation control. The private KEOS handoff and Hermes
reflection remain candidate evidence unless mapped here. Raw private source
content is not promoted into public docs, shared retrieval, or canonical
project truth.

## v0.7.1 Commitments

Keep v0.7.1 local first-value scope intact. Do not implement runtime, hosted,
semantic-write, approval-state, concept-graph, or language-gate features before
v0.7.1.

Allowed v0.7.1 changes:

- Public docs and evidence must record source date or retrieval date for
  external current-capability claims.
- Pre-install docs must keep an explicit information budget and avoid becoming
  context dumps.
- Integration docs must state that the current MCP profile is read-only and no
  agent may assume a write path.
- Hermes is framed as a project-local read-only MCP sidecar, not a replacement
  for Hermes memory or compression.
- Hermes-specific performance claims remain candidate claims until validated by
  a Hermes fixture.

Hermes proof rule: keep the current `OW-071-07` acceptance surface. A first
smoke may use only entrypoint/search/context-pack to reduce tool-choice risk,
but the ticket is not accepted until the full read-only profile also proves
tasks/reviews and absence of write tools.

## Implementation Mapping

| Finding | Decision | Destination | Implementation Rule |
| --- | --- | --- | --- |
| Source vs review freshness | Accept | `OW-071-04`, `OW-080-05`, `OW-090-06`, `OW-090-09` | v0.7.1 records evidence freshness; later context/drift layers distinguish source freshness from review freshness. |
| Plaintext IDs in text output | Accept later | `OW-100-05` | CLI/MCP text output should include title/summary with IDs while machine-readable JSON stays stable. |
| Archive terminal state | Accept principle | `OW-090-01`, `OW-090-02`, `OW-100-05` | Never delete user-authored canonical Markdown as a lifecycle side effect; archive/supersede with reason. Generated caches may be rebuilt separately. |
| Write MCP | Reject exact generic shape; accept semantic direction | `OW-090-04` | No generic `log()` write primitive before policy. Every write maps to a contract transition, evidence event, scope, idempotency key, and audit record. |
| Audience field | Accept separated model | `OW-071-14`, `OW-080-02` | Keep `audience_ids` for target roles/lenses; add `transferability` and optional `applies_to`; keep `visibility`/`data_class` for privacy. |
| Single-writer matrix | Accept later | `OW-081-06`, `OW-090-04` | Start with claims, allowed paths, branch/worktree, TTL, and overlap detection before write locks. |
| Task contract | Accept | `OW-080-03` | WorkContract must encode goal, definition of done, QA gates, out-of-scope, evidence, handoff, and unresolved questions. |
| Context budget | Accept | `OW-071-03`, `OW-080-05`, `OW-080-07`, `OW-100-04` | Context packs must explain inclusion/exclusion and never silently exceed budget. |
| Concept document type | Defer/rework | `OW-080-02` exploration only | Do not add a new top-level type until existing `concept_tags`, typed edges, and concept-audit behavior are reconciled. |
| Approval gates | Accept later | `OW-080-12`, `OW-081-12`, `OW-090-02` | Human approval gates apply to strategy/privacy/high-risk transitions, not routine mechanical work. |
| Experience append | Accept later | `OW-090-04`, `OW-090-02` | Append only through semantic write policy, with target identity, provenance, similarity suggestion, and no direct canonical mutation. |
| Integration write block | Defer | post-`OW-090-04` docs | Do not document write-path instructions until the semantic write profile ships. |
| Language/voice gate | Defer | post-v1 QA hardening | Useful as configurable lint, but not part of v0.7.1 or v0.8 foundations. |

## Execution Order

1. Finish v0.7.1 adoption, truth, and Hermes read-only proof.
2. In `OW-080-01`, lock contract architecture and migration rules so later
   schema changes have one authority model.
3. In `OW-080-02`, implement the separated
   audience/transferability/privacy model with defaults, migration tests, and
   negative tests against overloaded fields.
4. In `OW-080-03`, implement WorkContract and RunState so tasks cannot be
   accepted on prose-only completion.
5. In `OW-080-05` and `OW-080-07`, implement deterministic context budgets,
   dropped-source reasons, source/review freshness separation, and small-model
   profiles.
6. In `OW-081-06`, implement claims, allowed paths, TTL, overlap detection, and
   worktree planning before any multi-writer promise.
7. In `OW-090-01` and `OW-090-02`, implement evidence ledger and reviewed
   promotion lifecycle.
8. In `OW-090-04`, implement semantic write-enabled MCP only after privacy,
   promotion, idempotency, locking, and audit controls are available.
9. In `OW-100-04` and `OW-100-05`, prove outcome evaluation and command UX,
   including plaintext ID rendering and recoverable lifecycle behavior.

## Stop Rules

- Do not add write-enabled MCP to v0.7.1.
- Do not describe future write integration blocks as current capability.
- Do not treat Hermes token/performance claims as current without fixture
  evidence.
- Do not collapse target audience, transferability, and privacy into one field.
- Do not delete user-authored canonical Markdown as a lifecycle operation.

## Resume State

The planning bridge is final for implementation. Continue v0.7.1 from the
active release runbook and use this decision as a constraint source when
working `OW-071-*`, `OW-080-*`, `OW-081-*`, `OW-090-*`, and `OW-100-*` tickets.
