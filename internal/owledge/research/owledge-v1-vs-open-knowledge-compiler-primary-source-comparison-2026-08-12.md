---
memory_id: "mem:owledge:global:owledge:research:v1-vs-open-knowledge-compiler-2026-08-12"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "research"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge V1 versus Open Knowledge Compiler: primary-source comparison"
summary: "Mission-weighted architecture and product comparison of the planned Owledge V1 control plane against Open Knowledge Compiler v1.1.0 and main commit 57e55e3, including a common 0-100 score, USPs, tradeoffs, and integration guidance."
concept_tags:
  - "competitive-analysis"
  - "knowledge-lifecycle"
  - "knowledge-compiler"
  - "open-knowledge-format"
stack_tags:
  - "python"
  - "markdown"
  - "postgresql"
  - "mcp"
problem_patterns:
  - "compiled engineering knowledge confused with governed organizational memory"
  - "planned capability compared as if already shipped"
  - "duplicate source-compilation scope"
architecture_patterns:
  - "compiler as upstream knowledge producer"
  - "knowledge lifecycle control plane"
  - "derived OKF projection"
  - "reviewed cross-scope promotion"
failure_modes:
  - "unfair plan-versus-product comparison"
  - "direct promotion of generated wiki output"
  - "duplicated code-analysis pipeline"
reusable_lessons:
  - "OKC and Owledge are strongest as adjacent layers: OKC compiles software evidence; Owledge governs reusable knowledge across projects, users, and agents."
  - "Owledge should interoperate with OKC through the existing OKF and ResourceRef seams instead of reproducing its analyzers and reconciliation pipeline."
confidence: 0.93
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "2026-08-12T12:52:40Z"
updated_at: "2026-08-12T12:52:40Z"
document_version: 1
retention_class: "standard"
stale_after: "2026-09-12T00:00:00Z"
expires_at: ""
last_reviewed_at: ""
review_cycle: "monthly"
source_url: "https://github.com/kushal-omnius/open-knowledge-compiler"
source_date: "2026-08-12"
retrieved_at: "2026-08-12T12:52:40Z"
valid_until: "2026-09-12T00:00:00Z"
version_context: "OKC latest GitHub release v1.1.0 published 2026-08-10; audited main HEAD 57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf dated 2026-08-12. Owledge comparison target: master plan 2.5.0/document 4 and reprioritization plan 1.5.0/document 4, updated 2026-08-12."
source_hash: "57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf"
edges:
  - type: "validates"
    target: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
    confidence: 0.92
    reason: "Tests the Owledge V1 positioning and scope against an implemented adjacent system."
---

# Owledge V1 versus Open Knowledge Compiler

## Executive verdict

Open Knowledge Compiler (OKC) and Owledge overlap at Markdown/YAML, provenance,
retrieval, MCP, incremental state, and multi-repository knowledge. They are not,
however, the same product category:

- **OKC is currently the stronger software-engineering knowledge compiler.** It
  deterministically extracts code, Git, PR, test, Jira, API, dependency, and
  semantic entities into a persistent Knowledge IR and an OKF wiki; it already
  ships reconcile, verify, hybrid retrieval, QA-planning queries, and a read-only
  local MCP server. [OKC README at audited commit](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/README.md)
- **The Owledge V1 target is the stronger governed knowledge-lifecycle and
  context-control plane.** It is designed for research reuse, explicit
  `project_user`/`user_global`/`enterprise` scopes, deterministic Context Packs,
  Candidate/Review/Promotion, global essences with authorized source drill-down,
  Knowledge Health, portable agent capabilities, and a bounded authenticated
  Single-Organization Hub Beta. [Owledge V1 master plan](../plans/owledge-v1-autonomous-delivery-master-plan.md)
- **The strongest architecture combines them rather than merging their cores:**
  OKC can be an upstream, project-scoped evidence/OKF producer; Owledge remains
  the authority for lifecycle, scope, recall-before-research, review, promotion,
  and cross-harness Context Packs. This fits the already planned OKF interchange
  profile and media-neutral `ResourceRef`; no OKC-like compiler belongs in the
  Owledge V1 critical path. [Owledge roadmap](../../../ROADMAP.md)

The forced answer to “which is generally stronger?” therefore depends on the
time horizon: **OKC is stronger as a usable system today; Owledge V1 is stronger
for the stated long-term personal/global/enterprise knowledge mission if the
planned gates are actually delivered.**

## Comparison boundary and current evidence

This is deliberately not presented as an equal maturity comparison. The OKC
column describes audited, shipped repository behavior. The Owledge column
describes the approved V1 target, while the delivery-maturity metric discounts
capabilities that are not yet implemented.

| Evidence point | OKC | Owledge |
| --- | --- | --- |
| Audited version | Latest GitHub release `v1.1.0`, published 2026-08-10; audited `main` HEAD `57e55e3` from 2026-08-12 is one commit ahead of that tag. [Release](https://github.com/kushal-omnius/open-knowledge-compiler/releases/tag/v1.1.0) · [HEAD commit](https://github.com/kushal-omnius/open-knowledge-compiler/commit/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf) | V1 target is the uncommitted planning baseline on `codex/v071-integration`: master plan `2.5.0`, document `4`; execution remains gated before v0.8. [Master plan](../plans/owledge-v1-autonomous-delivery-master-plan.md) |
| Shipping evidence | Implemented package, migrations, CLI, source analyzers, Postgres CI, 174 repository test functions, self-compilation claim, tagged releases. [CI workflow](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/.github/workflows/ci.yml) · [tests](https://github.com/kushal-omnius/open-knowledge-compiler/tree/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/tests) | Gate-driven roadmap with 61 tickets, explicit V1 QA gates, traceability, and a current v0.7.1 alignment stop; most differentiated V1 capabilities remain planned. [Tickets](../workpackages/owledge-v1-autonomous-delivery/tickets/ALL-TICKETS.md) · [gates](../workpackages/owledge-v1-autonomous-delivery/gates/ALL-GATES.md) |
| Important release caveat | The `v1.1.0` GitHub release is real, but audited `pyproject.toml` and `knowledge_compiler.__version__` still say `1.0.0`, while `SECURITY.md` still calls the project pre-1.0. This is release-metadata drift, not evidence that the pipeline is absent. [package metadata](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/pyproject.toml) · [version constant](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/knowledge_compiler/__init__.py) · [security policy](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/SECURITY.md) | Owledge avoids this specific comparison error by separating Standalone Core GA from Hub Beta, but must still prove clean source, upgrade, install, and finalization gates before V1 claims are valid. [Master plan, Definition of Done](../plans/owledge-v1-autonomous-delivery-master-plan.md#definition-of-v10-done) |

## Unified 0–100 scoring matrix

Scale: `0` absent, `25` concept only, `50` narrow/partial, `75` usable with
meaningful limits, `90` strong and evidenced, `100` unusually complete. Weighted
total is `sum(score × weight) / 100`. The weighting follows the stated Owledge
mission, so it intentionally values research reuse, lifecycle governance, agent
context, and enterprise-safe scope more than source-code analysis alone.

| Metric | Weight | OKC current | Owledge V1 target | Evidence-based interpretation |
| --- | ---: | ---: | ---: | --- |
| Canonical knowledge and portability | 10% | 88 | 94 | OKC emits OKF v0.2 Markdown, but Postgres Knowledge IR is durable truth and the wiki is disposable. Owledge keeps local Markdown/Git canonical and treats projections as rebuildable. [OKC OKF contract](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/docs/okf-conformance.md) · [Owledge canonical control plane](../plans/owledge-v1-autonomous-delivery-master-plan.md#canonical-control-plane) |
| Deterministic ingestion and compilation | 12% | 96 | 76 | OKC's central strength is implemented incremental source compilation, reconcile, identity matching, atomic persist, delta history, and full-vs-incremental verify. Owledge captures bounded deltas and artifacts but does not plan a comparable code-analysis compiler. [OKC pipeline](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/docs/pipeline.md) |
| Retrieval and token/context efficiency | 12% | 86 | 95 | OKC offers Postgres FTS plus optional pgvector/RRF and composed engineering queries. Owledge adds deterministic budgeted Context Packs, progressive disclosure, clean-body projections, receipts, and small-model gates. [OKC retrieval](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/docs/retrieval.md) · [Owledge reprioritization](../plans/owledge-v1-federated-research-memory-and-pi-adapter-reprioritization.md#context-pollution-controls) |
| Lifecycle, authority, and provenance | 14% | 76 | 97 | OKC has stable identity, provenance, current state, atomic deltas, and history, but its compile pipeline writes authoritative state directly. Owledge explicitly separates Evidence, Candidate, Review, Promotion, Supersession, revocation, and canonical authority. [OKC IR](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/docs/ir.md) · [Owledge lifecycle tickets](../workpackages/owledge-v1-autonomous-delivery/tickets/ALL-TICKETS.md#ow-090-01---implement-append-only-evidence-ledger-and-authority-policy) |
| Research, ideas, preferences, and human knowledge reuse | 12% | 58 | 97 | OKC intentionally focuses on software-engineering artifacts. Owledge makes recall-before-research, freshness/gaps, session handoffs, idea resurfacing, global essences, and selective cross-project reuse first-class. [OKC vision](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/docs/vision.md) · [Owledge Research Memory contract](../plans/owledge-v1-federated-research-memory-and-pi-adapter-reprioritization.md#research-memory-contract) |
| Agent and harness interoperability | 10% | 84 | 94 | OKC ships a useful read-only stdio MCP surface. Owledge plans a transport-neutral capability contract, read and controlled semantic writes, conformance gates, and thin Codex/Claude/Pi/generic MCP adapters. [OKC MCP](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/knowledge_compiler/mcp/server.py) · [Owledge Pi adapter](../plans/owledge-v1-federated-research-memory-and-pi-adapter-reprioritization.md#pi-reference-adapter) |
| Enterprise identity, isolation, and policy | 12% | 38 | 89 | OKC explicitly has no MCP authentication layer; local stdio and database controls are the boundary, and same-database multi-repo configuration is manual. Owledge V1 plans audience-bound OAuth/OIDC, server-side project/scope resolution, audit receipts, quotas, and a one-organization Hub Beta—not a multi-tenant SaaS. [OKC security](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/SECURITY.md) · [Owledge Hub target](../plans/owledge-v1-autonomous-delivery-master-plan.md#version-v10---product-hardening-and-release) |
| Health, validation, freshness, and drift control | 8% | 91 | 96 | OKC already has reconcile, `kc verify`, OKF validation, migrations, and fail-fast database checks. Owledge's planned Knowledge Health is broader: stale/conflicted/orphaned knowledge, raw-inbox debt, source/drill-down availability, budget pollution, and projection drift. [OKC CLI](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/docs/kc-cli-reference.md) · [Owledge Knowledge Health](../plans/owledge-v1-federated-research-memory-and-pi-adapter-reprioritization.md#knowledge-health-and-operations-monitoring) |
| Extensibility and upgradeability | 5% | 62 | 87 | OKC has good Protocol/ADR seams, but source comments and README say real entry-point activation/ecosystem remains unfinished. Owledge plans namespaced extensions, managed surfaces, module manifests, dry-run migrations, health, recovery, and transactional multi-surface upgrades; public SDK/marketplace stays post-V1. [OKC interfaces](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/knowledge_compiler/interfaces.py) · [OKC bootstrap](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/knowledge_compiler/compiler/bootstrap.py) · [Owledge roadmap](../../../ROADMAP.md) |
| Shipping maturity and immediate time-to-value | 5% | 90 | 62 | OKC has tagged releases, working CLI/CI/tests, and a concrete install path, despite mandatory Postgres/Docker and version drift. Owledge has a disciplined plan and existing v0.7 core but the differentiated V1 target remains gated future work. [OKC installation](https://github.com/kushal-omnius/open-knowledge-compiler/blob/57e55e3fb1edbe7ce98ff5b001d485f7f9ea7dbf/README.md#installation) · [Owledge release train](../plans/owledge-v1-autonomous-delivery-master-plan.md#release-train) |
| **Mission-weighted total** | **100%** | **76.1** | **90.4** | **OKC's score describes available repository behavior; Owledge's total describes the V1 architecture target and must not be presented as already shipped.** |

## USP and system-level advantages

| System | Clear USP | Principal advantages | Principal disadvantages |
| --- | --- | --- | --- |
| **OKC** | Incrementally compiles software delivery evidence into a persistent, queryable engineering knowledge graph and OKF wiki. | Implemented deterministic analyzers; PR/direct-commit reconciliation; full-vs-incremental equivalence check; stable entity identity; Postgres transactions and history; optional semantic extraction and hybrid search; concrete impact/test/coverage queries; read-only MCP; OKF output. | Mandatory Postgres/Docker raises local adoption cost; compiled wiki is derived rather than canonical; no built-in remote auth, principal, tenant, or three-scope policy; no reviewed agent-write/promotion lifecycle; research, personal preferences, product ideas, and user-global memory are not first-class; cross-repo search requires manual shared DB/config and multiple serve processes; plugin ecosystem is designed more fully than it is implemented; release metadata currently drifts. |
| **Owledge V1** | Governed recall and context control across projects, sessions, users, and agent harnesses without making any one model, runtime, database, or RAG projection canonical. | Markdown/Git inspectability; three knowledge scopes; recall-before-research; bounded Context Packs; global essence plus permission-checked drill-down; Candidate/Review/Promotion and controlled semantic writes; idea resurfacing; deterministic Knowledge Health; local/global/Hub separation; portable capability contract; explicit upgrade/recovery seams. | Most differentiating capabilities are still plan commitments; a V1 Hub Beta plus standalone GA is a substantial execution burden; Owledge is not and should not become a deep source-code compiler; value depends on reliable harness hooks and conformance; broad connectors, media ingestion, public extension ecosystem, DSAR orchestration, HA, and multi-tenant SaaS are intentionally absent through V1. |

## Which system is stronger for which purpose?

| Primary job | OKC | Owledge V1 | Winner |
| --- | ---: | ---: | --- |
| Turn repositories, PRs, APIs, tests, and Jira evidence into an always-current engineering wiki/graph | 96 | 68 | **OKC** |
| Give a QA/coding agent impact, dependency, test-plan, and coverage context from compiled code evidence | 94 | 76 | **OKC** |
| Reuse research, decisions, learnings, ideas, and preferences across sessions and harnesses | 58 | 97 | **Owledge V1** |
| Govern project-local, user-global, and enterprise knowledge without silent promotion | 40 | 97 | **Owledge V1** |
| Produce minimal, budgeted context for small and frontier models with source receipts | 82 | 95 | **Owledge V1** |
| Deploy a remotely authenticated organizational knowledge service | 35 | 89 | **Owledge V1 target**; Hub is Beta, not GA |
| Install and use the compared advanced feature set today | 90 | 62 | **OKC today** |

## Architecture recommendation for Owledge

1. **Do not add code parsing, PR reconciliation, Jira compilation, test coverage
   inference, or a Postgres-first Knowledge IR to the Owledge V1 Core.** OKC
   already solves that coherent producer problem, and reproducing it would bloat
   Owledge while weakening its lifecycle USP.
2. **Model OKC as an optional upstream producer.** A future adapter reads a
   version-pinned OKF bundle or `kc-wiki/`, maps its generated/provenance/commit
   references into `ResourceRef` plus Evidence/Source records, and submits only
   project-scoped Candidates by default. Generated OKC pages must never flow
   directly into `user_global` or `enterprise` canonical knowledge.
3. **Reuse the existing V1 seams, not a new subsystem.** `POST-012` (OKF
   interchange), `POST-020`/`OW-080-02` (ResourceRef), stable identity,
   Candidate/Review/Promotion, and derived projection contracts are sufficient
   foundations. One conformance fixture can later prove an OKC-generated OKF
   bundle imports without losing source commit, generated-by, and stable
   external identifiers.
4. **Keep one truth boundary explicit.** OKC's Postgres Knowledge IR owns the
   current compiled view of software artifacts; Owledge owns the reviewed
   knowledge lifecycle and Context Pack receipts. The OKC wiki remains a linked,
   refreshable source projection inside Owledge, not duplicated canonical truth.
5. **Make the integration demand-triggered.** Do not add an OKC-specific V1 P0
   ticket now. Re-evaluate after the generic OKF import/export and ResourceRef
   contracts stabilize, or earlier only if a real dogfood workflow shows that
   repository compilation is blocking Owledge recall quality.

## Final product-positioning statement

> **OKC compiles software into current engineering knowledge. Owledge governs
> which knowledge agents and people should reuse, in which scope, with which
> evidence, freshness, review state, and context budget.**

This distinction is both defensible and commercially useful. It keeps Owledge
compatible with OKC, Google OKF, existing Markdown vaults, RAG systems, and
future compiler/importer tools without making their storage or extraction model
part of the Owledge Core.
