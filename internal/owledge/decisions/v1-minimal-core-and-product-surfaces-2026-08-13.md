---
memory_id: "mem:owledge:global:owledge:decision:v1-minimal-core-and-product-surfaces-2026-08-13"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "decision_record"
document_version: 1
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge V1 minimal core and product surfaces"
summary: "Owner decision to keep one Owledge product while separating Principles, deterministic Core, local user-global Null-Space, thin adapters, and post-V1 add-ons/Hub, with a hard V1 complexity budget."
concept_tags: ["v1-scope", "minimal-core", "product-surfaces", "complexity-budget"]
stack_tags: ["python", "markdown", "mcp", "git"]
problem_patterns: ["monolithic-product-surface", "default-install-bloat", "runtime-overreach"]
architecture_patterns: ["one-brand-modular-surfaces", "ports-and-adapters", "on-demand-runtime"]
failure_modes: ["separate-products-before-contract-stability", "internal-dogfood-shipped-by-default", "adapter-logic-fork"]
confidence: 0.98
review_status: "approved"
sanitization_status: "not_required"
created_at: "2026-08-13T17:20:00+02:00"
updated_at: "2026-08-13T17:20:00+02:00"
source_hash: ""
reusable_lessons:
  - "One brand can expose multiple installation and authority surfaces without becoming one monolithic runtime."
  - "The V1 contract is the smallest complete daily journey, not the union of every proven internal capability."
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:v1-minimal-core-finalization"
    confidence: 1.0
    reason: "Locks the product and architecture boundary implemented by the finalization plan."
  - type: "supersedes"
    target: "mem:owledge:global:owledge:decision:v1-schema-global-knowledge-health-matrix-2026-08-12"
    confidence: 0.9
    reason: "Supersedes only the prior 3B delivery timing: Hub remains architecturally possible but moves from V1 Beta to post-V1. The 1B+ schema and 2C+ knowledge decisions remain active."
---

# V1 Minimal Core and Product Surfaces Decision

## Decision

Owledge remains one product and repository through V1, with five strictly
separated surfaces:

1. Principles: zero-install skill and Markdown conventions.
2. Core: on-demand deterministic local Python kernel.
3. Null-Space: private local user-global composition.
4. Adapters: Codex, Claude Code, and generic MCP/CLI translations.
5. Add-ons/Hub: optional post-V1 products.

V1 ships surfaces 1-4. Surface 5 is parked.

## Public complexity budget

- eight Core CLI operations;
- five MCP tools;
- two knowledge scopes;
- three reference adapters;
- no required daemon, database, vector store, network, model, or cloud;
- minimal install <=15 files and <=8 directories.

## Compatibility strategy

The current broad codebase is not rewritten before V1. Verified behavior remains
behind a small public facade, explicit `full`/`maintainer` profiles, compatibility
aliases, or optional add-ons. New logic may only enter Core when it serves the
V1 daily journey and cannot be implemented as a skill or thin adapter.

## V1 idea-management decision

Parked ideas are first-class Candidate lifecycle records, not a second issue
tracker. They remain excluded from ordinary recall and are returned only for
planning-purpose recall when project/tags/triggers match. Activation always
requires an explicit plan decision.

## Supersession scope

The prior decisions for a versioned common envelope/artifact profiles (`1B+`)
and global essence with source drill-down (`2C+`) remain valid. Only the previous
decision to ship a Single-Organization Hub Beta in V1 (`3B`) is superseded by
the later owner-approved scope cut. Hub becomes a post-V1/V1.1 evaluation.

## Consequences

- The default user never sees the internal release-control plane, benchmarks,
  report design, Pi trees, or unused schema/template families.
- Skills handle behavior and model orchestration; Core handles validation,
  storage, retrieval, lifecycle, health, and migration guarantees.
- MCP and harness adapters cannot access storage internals or create their own
  knowledge semantics.
- Pulling any parked surface back into V1 requires a named owner amendment.

