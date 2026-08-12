---
memory_id: "mem:owledge:global:owledge:plan:v1-federated-research-memory-pi-reprioritization"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "plan"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v1 federated research memory and Pi adapter reprioritization"
summary: "Owner-approved roadmap amendment that deepens Owledge's existing research layer, introduces three explicit knowledge scopes, makes Pi a reference runtime adapter, and targets Standalone Core GA plus a bounded Single-Organization Hub Beta without turning Owledge into a hosted SaaS or autonomous super-agent."
concept_tags: ["v1-roadmap", "research-memory", "federated-knowledge", "pi-adapter", "single-org-hub"]
stack_tags: ["python", "markdown", "git", "mcp", "oauth"]
problem_patterns: ["duplicate-research", "stale-research", "context-pollution", "runtime-coupling", "feature-bloat"]
architecture_patterns: ["markdown-canonical", "scope-first-retrieval", "candidate-before-promotion", "ports-and-adapters", "derived-projections"]
failure_modes: ["research-repeated-without-recall", "stale-source-presented-as-current", "cross-scope-leak", "pi-specific-core", "hub-as-second-truth"]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-11T19:33:00+02:00"
updated_at: "2026-08-12T14:32:51+02:00"
plan_version: "1.5.0"
document_version: 4
source_hash: ""
reusable_lessons: []
edges:
  - type: "relates_to"
    target: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
    confidence: 1.0
    reason: "The product owner changed the v1 target from local-only to Standalone Core GA plus a bounded Single-Organization Hub Beta and approved explicit research-memory and Pi-adapter priorities."
---

# Owledge v1 Federated Research Memory and Pi Adapter Reprioritization

## Decision Summary

Owledge v1 targets two coordinated product surfaces:

1. **Standalone Core GA** remains local-first, Markdown/Git-canonical, runtime-independent, and useful without a server, database, model provider, or vector store.
2. **Single-Organization Hub Beta** adds OAuth/OIDC-backed remote access, a
   project registry, scope-aware policy enforcement, audit receipts, centrally
   reviewed enterprise retrieval, and read/propose MCP operations for one
   organization per deployment. Private `user_global` memory remains local-first
   in v1 and is never uploaded implicitly.

Pi remains the agent runtime. `@owledge/pi` becomes a thin reference adapter over versioned Owledge capabilities. It must not duplicate retrieval, promotion, or artifact semantics.

## Owner Decisions

Recorded on 2026-08-11:

- v1 outcome: **Standalone Core GA plus Single-Organization Hub Beta**.
- Project Markdown/Git remains canonical in local and Hub operation.
- One organization per Hub deployment is sufficient for v1; contracts remain tenant-ready.
- Remote identity uses an existing OAuth/OIDC provider plus agent/service identities; Owledge does not ship a password database in v1.
- Agents write Evidence and Candidates by default. Canonical promotion is a separately authorized, reviewed operation.
- Three knowledge scopes are first-class:
  1. `project_user` — one user's knowledge inside one project;
  2. `user_global` — one user's private local knowledge across explicitly linked
     projects; Hub synchronization is not a v1 default;
  3. `enterprise` — organization-approved knowledge across multiple projects, users, and agents.
- v1 golden flows:
  1. cross-project question with sources and freshness;
  2. session close with Decisions, Learnings, Evidence, open questions, and Candidates;
  3. Candidate to Review to Promotion to refreshed Context Pack.
- Private `user_global` stays local-first in v1 without implicit Hub sync.
- Autonomous recall/capture behavior is controlled by versioned user settings;
  no harness may invent policy from prose or silently widen a configured scope.
- Cross-project promotion uses a private global inbox lifecycle:
  `project candidate -> global raw inbox -> reviewed/promoted or rejected/archived`.
  The raw inbox is excluded from normal retrieval and RAG by default.
- Every material edit to an Owledge-managed artifact increments a deterministic
  `document_version`; schema/profile versions describe contract shape and must
  never be used as a substitute for the document's content revision.
- The promoted `user_global` or `enterprise` layer is a central Knowledge Base
  of reviewed Research essences, learnings, patterns, and transferable concepts.
  Global Raw is only its private review queue, never the Knowledge Base itself.
- Global essences retain stable, permission-checked drill-down paths to project
  canonical artifacts and source Evidence so authorized agents can request
  deeper context without copying every project document into the global layer.
- V1 includes deterministic Knowledge Health and privacy-safe Hub operational
  health. It does not become a generic prompt/trace observability backend.

## Product Thesis

Owledge is not a transcript warehouse, vector database, research crawler, generic
observability backend, or autonomous super-agent. It is a deterministic,
governed Knowledge Lifecycle and Context system that lets agents reuse prior
work before spending tokens, latency, and external-search cost again. A
"second brain" is a valid user-facing use case, but the product category is the
more precise **agentic knowledge lifecycle, project memory, and context layer**.

The Research Memory promise is:

> Recall first, evaluate freshness second, refresh only the stale or missing delta, and preserve source-linked findings for future sessions.

## What Already Exists and Is Reused

| Existing surface | v1 treatment |
| --- | --- |
| `.owledge/research/{briefs,sources,findings,syntheses,lanes}` | Preserve as the project-native Research Memory layout; deepen contracts in place |
| `global-memory/research/` | Reuse for private `user_global` Research Memory; never treat it as enterprise-shared by default |
| Research brief, finding, and card templates | Evolve with stable IDs, reason/context, source mutability, revision, and freshness fields instead of adding parallel templates |
| Freshness logic in `tools/owledge_core.py` | Generalize behind one Core recall interface and source-mutability policy |
| Owlib scoped retrieval/indexing | Extend with three scope namespaces, source receipts, and Research freshness rather than introducing a second hub indexer |
| Existing read-only MCP/CLI profile | Keep as the transport baseline; Pi, Hermes, OpenCode, and future harnesses consume shared capability contracts |
| Candidate, Evidence, gate, and promotion concepts | Reuse for Research and Session Recap lifecycle; no separate approval system |
| Markdown/Git artifact authority | Preserve in Standalone and Hub operation; derived indexes remain rebuildable projections |

## Not in v1 Scope

| Deferred capability | Why it is outside the v1 proof |
| --- | --- |
| Autonomous Delivery Profile, eight-worker planner, and runtime dispatch | Agent orchestration is a separate product concern and would widen the Core interface |
| Edge/local-model delivery profile | Small-context correctness stays in Core; model-specific delivery policy can follow as an add-on |
| Mandatory vector or graph database | Retrieval acceleration does not justify a second canonical truth |
| Hosted multi-tenant SaaS control plane | Requires a separate tenancy, billing, operations, and compliance program after Single-Org evidence |
| Built-in password database | Existing OAuth/OIDC providers give stronger identity leverage with less security surface |
| SAML/SCIM, Kubernetes/HA, and multi-region replication | Enterprise procurement/operations extensions should be customer-triggered after Beta |
| Full Research crawler or always-on PI research guardian | External research remains a skill/runtime concern triggered by a Core freshness gap |
| Raw transcript warehouse | Structured deltas provide reuse without privacy cost and context pollution |
| Owledge as a full agent harness or scheduler | Pi, Hermes, LangGraph, cron, and workflow engines remain runtimes that consume Owledge capabilities |
| Generic agent tracing/logging backend | Owledge stores evidence and audit receipts; traces belong in an observability system and may link to Owledge IDs |
| Multi-model judge dispatcher | v1 defines portable review/evaluation artifacts; provider execution and judge panels remain optional adapters |
| LangChain/LangGraph-owned memory backend | A thin tool/store adapter may follow the stable Core interface; graph checkpoints must not become Owledge truth |
| Full knowledge-management frontend | CLI/MCP and generated reports prove the lifecycle first; a UI follows demonstrated administration demand |
| Bounded personal-data erasure/DSAR control plane | General source withdrawal and projection cleanup stay in V1; subject-resolution, connector, restore-guard, and legal-policy orchestration is a post-v1 enterprise module |
| Binary/media warehouse and transcription pipeline | V1 defines only a media-neutral source-reference contract; storage and transcription remain external adapters |
| Public plugin SDK or marketplace | V1 proves compatibility/permission/health manifests first; third-party extension distribution follows frozen contracts |

## Target Module Seams

| Module | Owns | Must not own |
| --- | --- | --- |
| Standalone Core | artifact contracts, stable identity, lifecycle, provenance, scope semantics, validation, research recall, context packs, candidate/promotion rules | OAuth, HTTP deployment, Pi lifecycle, mandatory DB, vendor-specific RAG |
| Hub | authentication, principal-to-scope authorization, project registry, routing, quotas, operational audit, jobs, backup of Hub state, registered-project and enterprise derived indexes | new knowledge semantics, implicit `user_global` upload, silent project writes, a second exclusive source of truth |
| MCP adapters | versioned tool/resource projection and transport error mapping | policy decisions after retrieval, arbitrary file paths, canonical bypass |
| `@owledge/pi` | Pi lifecycle hooks, tool registration, minimal bootstrap injection, session-close handoff | Owledge indexing, schemas, promotion logic, raw transcript auto-persistence |
| Librarian | intent clarification, scoped capability planning, evidence-linked answers, abstention, Candidate proposals | superuser credentials, direct DB/filesystem access, automatic promotion |
| Research Orchestrator skill | dedup-first orchestration, source search, atomic finding production, delta refresh | canonical authority, mandatory model routing, Owledge storage semantics |
| Automation/scheduler adapters | invoke bounded recall, digest, drift, and report capabilities on a schedule | arbitrary code execution, policy decisions, credentials, canonical promotion |
| Observability adapter | correlate Owledge artifact/run/receipt IDs with external traces and export privacy-safe events | raw prompts, raw outputs, or becoming the primary trace store |

### Compatibility Seams for Post-v1 Modules

| Seam | V1 ownership | Boundary |
| --- | --- | --- |
| Managed Surface Manifest | classify Core-managed, user-managed, generated, and extension-managed files; record installed version and hashes | upgrades never infer ownership from path alone |
| Upgrade Transaction | preflight doctor -> dry-run/diff -> checkpoint -> apply -> postflight health -> receipt/recovery | no destructive rewrite of user-authored knowledge |
| Module Manifest | module kind, Core compatibility, permissions, artifact profiles, migrations, health, cleanup, uninstall | no direct access to Core storage internals or policy bypass |
| `ResourceRef` | stable source ID/relation, locator, media type, hash, size, data class, access/availability, extraction provenance | no arbitrary path exposure, binary canonical store, or automatic transcription |
| Health profiles | separate `system.doctor`, `knowledge.health`, and `hub.health` over a shared result envelope | installation, knowledge, and operations concerns do not collapse into one dashboard subsystem |

These contracts prevent structural breaking changes while keeping their first
specialized consumers—media ingestion, third-party modules, and enterprise
erasure—outside V1.

## Schema Registry, Settings, and Customization Contract

**Status: `1B+ / 2C+ / 3B` owner-approved and locked on 2026-08-12.**

V1 replaces the current single broad required-field list with a versioned
registry of a small common envelope plus artifact-specific profiles. This is
the locked `1B+` baseline, including the owner requirement that every material
document edit has an explicit revision bump. Agents submit typed intent; the
Core renders and validates canonical frontmatter.

The common envelope owns stable identity, artifact kind, schema/profile
versions, a monotonic `document_version`, scope, lifecycle, title/summary,
timestamps, provenance, and extension namespace. `schema_version` describes
the envelope contract, `profile_version` describes artifact-specific rules,
`document_version` increments by exactly one for each accepted material content
edit under a stable `memory_id`, and `source_hash` verifies exact content.
Research, plan, idea, evidence, handoff, and promotion profiles define their own
required and optional fields. Core fields use `additionalProperties: false`;
custom fields are preserved only below a namespaced `extensions` object and are
inert unless a declared adapter understands them.

Configuration uses deterministic layered settings rather than prompt prose:

```text
immutable Core safety invariants
  + deployment/organization policy
  + private user preferences
  + project preferences
  + bounded session overrides
  -> effective settings + explanation receipt
```

Later layers may narrow authority or tune budgets/presentation, but never widen
permissions. Allowlists intersect, denies win, secrets are referenced from an
external secret store, and unknown policy keys fail closed. Schema and settings
migrations require dry-run, compatibility-window, round-trip, and no-rewrite
proof for user-authored Markdown.

## Orthogonal Knowledge Axes

Owledge must not encode scope, abstraction, and lifecycle in one overloaded
"layer" field. They are independent axes:

| Axis | Values | Governs |
| --- | --- | --- |
| Authority scope | `project_user`, `user_global`, `enterprise` | who may discover, read, propose, review, and promote |
| Knowledge abstraction | `source_evidence`, `canonical_detail`, `compiled_context`, `global_essence` | how condensed the content is and which drill-down path it exposes |
| Lifecycle | `observed`, `candidate`, `raw_inbox`, `reviewed`, `canonical`, `superseded`, `rejected`, `archived` | whether content may influence normal retrieval and decisions |

The default recall path loads reviewed global essences plus the current
project's compiled context. `explain` expands the cited canonical artifacts;
`deep_dive` follows stable source/project references to detailed Research,
plans, decisions, and Evidence; `refresh` proposes only a stale or missing
delta. Every expansion rechecks caller, project, scope, data class, revision,
freshness, availability, and token budget. An unavailable or unauthorized
source returns an explicit unresolved/denied result rather than a copied or
hallucinated substitute.

## Global Raw Promotion Inbox and Global Knowledge Base

The inbox is a review queue, not a second canonical store, the global Knowledge
Base, or a dumping ground for full project plans or transcripts. The promoted
global layer is the central Knowledge Base of reviewed, reusable essences.

1. Project work remains canonical in its project.
2. A hook, agent, automation, or user may submit a source-linked promotion
   candidate containing a bounded, self-explanatory reusable delta capsule,
   source revision/hash/reference, reason, applicability, data class, and
   requested target scope. A pointer without the reusable delta is insufficient.
3. The private `user_global` raw inbox deduplicates by stable claim/source IDs,
   validates privacy and transferability, and remains excluded from ordinary
   retrieval.
4. A separate review/promotion operation either creates a reviewed, condensed
   global essence with drill-down relations to its project/source artifacts or
   records `rejected|archived` with reason, retention, and receipt.
5. Enterprise promotion later uses the same lifecycle with organization policy
   and a distinct target namespace; personal and enterprise global knowledge
   never share a default corpus.

Research and agent learnings are eligible for global promotion, not globally
authoritative by default. Project plans remain project-local unless a bounded,
reusable pattern or idea is proposed explicitly.

Full-content snapshots are policy-controlled exceptions for volatile,
non-reproducible, explicitly portable, or audit-required sources. They remain
scope-bound, encrypted where applicable, retention/TTL-controlled, excluded
from normal retrieval, and are never promoted automatically with the delta.

## Knowledge Health and Operations Monitoring

Knowledge Health is a deep Core module with one deterministic report interface,
not a dashboard-first subsystem. It evaluates artifact and retrieval integrity
without requiring an LLM or exporting knowledge bodies:

- schema/profile/document-version validity and missed revision bumps;
- duplicate IDs/claims, broken or orphaned edges, and unresolved source refs;
- stale Research, conflicting/superseded knowledge, and review debt;
- raw-inbox age/volume/TTL and promotion/rejection backlog;
- project registry/source availability and drill-down resolvability;
- derived-index watermark, tombstone, rebuild, and projection drift;
- context-pack selection, expansion depth, token budget, and pollution metrics;
- scope-isolation and privacy-policy failures.

Hub Operations Health remains a separate adapter surface for readiness,
latency/error rates, queue depth, auth failures, storage, backup age, index lag,
and restore status. It emits content-free metrics and stable artifact/run/receipt
IDs to external monitoring systems. Raw prompts, outputs, project bodies, and a
generic tracing backend remain outside Owledge Core. A read-only dashboard can
consume these reports after V1 but is not required to prove the health contract.

## Planning and Idea Preservation

The existing MVP-sparring and idea layers remain part of the product value. A
pre-plan Context Pack must surface relevant prior ideas, rejected/deferred
reasons, decisions, patterns, research, and roadmap items before a new feature
plan is cut. Every considered item receives one durable disposition:
`required_now`, `enabling_dependency`, `roadmap`, `idea`, `rejected`, or
`superseded`, including a review trigger. This preserves PoC -> MVP -> roadmap
discipline without automatically expanding current scope.

## Research Memory Contract

### Existing Surface to Preserve

Owledge already ships project-native research folders and templates:

- `.owledge/research/briefs/`
- `.owledge/research/sources/`
- `.owledge/research/findings/`
- `.owledge/research/syntheses/`
- `.owledge/research/lanes/`
- `global-memory/research/`

The roadmap must deepen these assets rather than introduce a parallel research database or folder taxonomy.

### Required Artifact Roles

| Artifact | Purpose | Authority |
| --- | --- | --- |
| Research Brief | question, reason, context, scope, known research, source policy, success criteria | canonical work intent after owner acceptance |
| Source Record | stable source identity, source kind, publication/version facts, retrieval history, content hash | evidence |
| Atomic Finding | one bounded claim plus evidence, caveats, applicability, confidence, and freshness policy | candidate until reviewed |
| Research Synthesis | cross-source conclusions, contradictions, gaps, decisions affected, and recommended actions | candidate until reviewed |
| Research Task Index | links one research reason/run to briefs, findings, models/agents, cost/evidence, and refresh state | derived/audit |
| Promotion Receipt | review, sanitization, scope target, supersession, and source revisions | append-only evidence |

### Minimum Contract Fields

Every reusable research record must be able to express:

- stable `memory_id` independent of file path;
- `tenant_id`, `project_id`, `knowledge_scope`, `owner_user_id`, and visibility;
- `research_question`, `research_reason`, and `research_context`;
- `source_id`, `source_url`, `source_type`, author/publisher, and publication date/version;
- `searched_at`, `retrieved_at`, `last_verified_at`, `next_check_at`, and `freshness_class`;
- source mutability: `immutable_publication`, `versioned_release`, or `mutable_web`;
- `source_hash` and optional version/commit identifier;
- supported claim, counterevidence, caveats, confidence, and applicability;
- lifecycle: `observed`, `candidate`, `reviewed`, `canonical`, `superseded`, `archived`;
- relations to originating task/session, decisions, plans, sibling findings, and superseded records;
- retrieval and promotion receipts without embedding raw governance frontmatter.

Dates alone do not determine truth. An immutable paper may remain valid while a tool's public documentation becomes stale quickly. Freshness policy therefore derives from source mutability, explicit recheck triggers, and version context, not one global expiry period.

### Recall-before-Research Flow

```text
question or research intent
  -> resolve caller and allowed knowledge scopes
  -> search briefs, findings, syntheses, and source records
  -> report coverage, source authority, freshness, contradictions, and gaps
  -> if sufficient and current: reuse with citations
  -> if stale or incomplete: create delta research brief
  -> search only missing/expired claims and changed sources
  -> store Evidence and Candidates
  -> review/promote deliberately
```

The deterministic recall stage must not call an LLM or the web. An optional Librarian or Research Orchestrator may plan a refresh only after the recall result identifies a gap.

## Context Pollution Controls

- Enforce knowledge scope and data-class policy before lexical, semantic, or graph retrieval.
- Index governance metadata as filters; exclude raw frontmatter from embedding text.
- Retrieve title/summary/claim/source receipts first and expand bodies only on demand.
- Prefer reviewed syntheses for orientation while retaining exact source/finding drill-down.
- Preserve contradictions and superseded claims rather than averaging them away.
- Return explicit `insufficient_evidence`, `stale`, and `partial` states.
- Record pack version, source revisions, selection reasons, exclusions, and token/item budgets.

## Pi Reference Adapter

`@owledge/pi` proves that an external custom harness can consume Owledge without Owledge becoming that harness.

### P0 Read Surface

- detect project/Hub configuration;
- read `OWLEDGE.md` or the equivalent entrypoint capability;
- search authorized memory;
- build scoped Context Packs;
- read artifacts by stable ID;
- list tasks and reviews;
- expose freshness and source receipts.

### P1 Session Continuity

- capture structured session-close deltas, not full transcripts;
- write a private Candidate handoff containing Outcomes, Decisions, Learnings, Gotchas, open questions, Evidence references, and affected artifacts;
- let later sessions resume from the handoff without chat history.

### P2 Controlled Writes

- append Evidence;
- create Decision, Research, and Memory Candidates;
- request Promotion;
- never expose arbitrary file writes or direct canonical mutation.

## Prioritization and Bloat Cutline

Scoring uses 25% Core Fit, 20% User Value, 20% Architecture Leverage, 15% Trust/Risk Reduction, 10% Adoption, and 10% inverse Complexity.

| Capability | Score | v1 disposition | Current roadmap mapping/change | Reason |
| --- | ---: | --- | --- | --- |
| Stable IDs, typed relations, lifecycle, provenance | 98 | P0 | Keep `OW-080-01` through `OW-080-04`; deepen `OW-090-01/02` | Foundation for deterministic recall, moves, supersession, and enterprise audit |
| Three explicit knowledge scopes | 96 | P0 | Deepen `OW-080-02`, `OW-081-09`, `OW-090-03/09`; Hub enforces project/enterprise access and rejects implicit `user_global` upload in `OW-100-11` | Implements personal local, personal global, and enterprise use without mixing authority |
| Recall-before-research and freshness evaluation | 95 | P0 | Add `OW-080-16`; connect `OW-080-05/08`, `OW-090-06`, `OW-100-04` | Prevents repeated research cost and is a differentiated Owledge capability |
| Deterministic Context Packs with source receipts | 94 | P0 | Keep and deepen `OW-080-05/06` | Core value and context-pollution control |
| Candidate/Review/Promotion lifecycle | 94 | P0 | Keep `OW-090-01/02/04`; extend to Research and all scopes | Prevents agent output from silently becoming truth |
| Transport-neutral capability contract | 93 | P0 | Keep `OW-081-01/05`; make it the Pi/Hub seam | Keeps MCP, Pi, CLI, and future harnesses thin |
| Structured session recap and handoff | 89 | P0/P1 | Deepen `OW-081-07/08/10` | High personal value; deepens existing capture rather than adding a new subsystem |
| Scoped Owlib/User-Global recall | 91 | P0 | Keep and deepen `OW-081-09`, `OW-090-09` | Primary current user use case and basis for organization Hub |
| Pi reference adapter | 84 | P1 | Repurpose `OW-081-04` from a bespoke runtime adapter | Strategic distribution and proof of harness independence |
| OAuth/OIDC Single-Organization Hub Beta | 89 | v1 Beta | Add `OW-100-11`; extend `OW-100-02/03/04/07/08` | Required for remote team use; bounded to one organization per deployment |
| Versioned schema registry and policy settings | 97 | P0 | Deepen `OW-080-01/02`, `OW-090-03`, `OW-100-03` | Removes agent guessing and makes safe customization/upgrades possible |
| Global raw promotion inbox | 94 | P0/P1 | Deepen `OW-090-01/02/04/09` | Enables selective cross-project reuse without polluting global truth |
| Document revision and no-silent-edit contract | 96 | P0 | Deepen `OW-080-01/02/09`, `OW-090-01` | Separates schema evolution from content history and makes agent edits auditable |
| Global essence with permission-checked project drill-down | 97 | P0/P1 | Deepen `OW-080-05/08/16`, `OW-081-09`, `OW-090-02/09` | Centralizes reusable knowledge without discarding or copying project detail |
| Deterministic Knowledge Health report | 95 | P0/P1 | Deepen `OW-080-09`, `OW-090-06/09`, `OW-100-01/11` | Keeps large knowledge bases maintainable without creating a generic observability product |
| Pre-plan idea/roadmap resurfacing | 92 | P0 | Keep `OW-080-03/05`, `OW-081-01/08`, `OW-090-02` | Prevents lost ideas while preserving a strict MVP cutline |
| Daily/PI research digest | 68 | P1 optional | Derived view after `OW-080-16`; no new critical-path ticket | Valuable after research contracts and recall work |
| Audit receipts linked to external traces | 74 | P1/adapter | Deepen Evidence/Hub receipts; generic telemetry stays post-v1 | Gives accountability without turning Owledge into a logging platform |
| Multi-model review artifact import | 72 | P1 contract | Extend portable evaluation artifacts; dispatcher post-v1 | Useful quality lever when rubric- and evidence-bound |
| LangGraph/LangChain adapter | 61 | Post-v1 adapter | Evaluate after capability interface stabilizes | Distribution benefit, but no Core dependency or checkpoint ownership |
| Owledge-native agent harness/frontend | 45 | Post-v1 | Keep as product discovery candidate | High scope and duplicates mature runtimes/schedulers |
| Generic clean RAG export | 82 | P1 | Keep `OW-090-07/08`; derived only | Useful adapter contract; not canonical |
| Autonomous multi-agent delivery/worktree planner | 58 | Add-on | Remove `OW-080-12`, `OW-081-06/12/13` from active v1 DAG | Solves delivery orchestration, not the Knowledge Librarian Core |
| Edge/local-model delivery profile | 57 | Add-on | Remove `OW-081-14`; retain Core small-context work in `OW-080-06/07` | Avoids coupling knowledge semantics to one execution policy |
| Four bespoke Tier-1 harness implementations | 62 | Reduce | Codex, Claude, Pi, generic MCP; Hermes/OpenCode generic first | Fewer adapters provide more leverage and clearer conformance evidence |
| Mandatory vector/graph database | 42 | Drop from Core | Keep only optional `OW-090-07/08` projections | Adds infrastructure and does not solve authority or freshness |
| Full hosted multi-tenant SaaS | 53 | Post-v1 | Replace with bounded `OW-100-11` Single-Org Beta | Separate commercial/security program after Single-Organization evidence |
| Dashboard, SAML/SCIM, Kubernetes/HA, broad SaaS connectors | 28-55 | Post-v1/pilot | No active v1 tickets | Customer-driven extensions, not v1 proof |
| Media/source-link adapter | 84 | Post-v1 P1 | Define `ResourceRef` only in `OW-080-01/02/16` | Valuable for transcripts and external documents without bloating canonical storage |
| Bounded enterprise erasure/DSAR module | 78 | Post-v1 enterprise | Keep generic lifecycle hygiene in `OW-090-02/09`, `OW-100-02`; no V1 DSAR workflow | Important for regulated customers but disproportionate for individuals |
| PII detection/redaction adapter | 67 | Post-v1 adapter | Exact product must be supplied and evaluated; no V1 dependency | Useful assistance, never deletion or compliance proof |
| Universal connector suite | 36 | Post-v1/customer-triggered | No active v1 ticket | High maintenance surface with weak pre-demand Core value |

## Release Re-sequencing

### v0.8.0 — Knowledge Contracts and Recall Foundation

Keep the portable control-plane work, but make these explicit P0 outcomes:

- stable entity/relation/provenance contracts;
- three knowledge scopes and scope-resolution rules;
- transport-neutral Query/Command and Capability envelopes;
- Research Brief, Source, Finding, Synthesis, and Task Index contracts;
- deterministic Research Recall result with coverage/freshness/gap states;
- Context Compiler consumes research records without full-vault loading;
- clean retrieval projection excludes governance frontmatter.
- versioned Schema Registry and deterministic effective-settings receipt;
- explicit document revision distinct from schema/profile versions, with
  missed-bump and history-integrity validation;
- orthogonal scope, abstraction, and lifecycle dimensions plus stable
  essence-to-project drill-down relations;
- custom extensions are namespaced, preserved, inert by default, and unable to
  weaken Core/organization safety policy.

### v0.8.1 — Runtime Continuity and Reference Adapters

- Codex and Claude remain direct reference adapters.
- Generic MCP/CLI is the portable baseline.
- Add Pi as the third reference proof, not a privileged Core path.
- Deepen SessionEnd into structured Recap/Handoff Candidates.
- Reframe the golden journey around Recall -> Context -> Session Recap -> Resume.
- Prove one private local `user_global` reference composition shared by at
  least two harnesses over explicit project allowlists; this is local federation,
  not Hub upload or remote user-global synchronization.
- Keep autonomous delivery/worktrees optional and remove them from the Knowledge-Librarian critical path.

### v0.9.0 — Trusted Research and Knowledge Lifecycle

- append-only Evidence and Research source receipts;
- Candidate/Review/Promotion/Supersession across project, user-global, and enterprise targets;
- semantic MCP operations for Evidence, Handoff, Research Candidate, Decision Candidate, and Promotion Request;
- one transport-neutral semantic mutation interface with expected document
  revision/base hash, idempotency, atomic result, and conflict receipt;
- private global raw-inbox submit/review/reject/promote operations with
  deduplication, retention, and receipts;
- reviewed global-essence compilation with authorized deep retrieval back to
  project canonical detail and source Evidence;
- Knowledge Health for stale/conflicted/orphaned knowledge, raw-inbox debt,
  source availability, and projection drift;
- research source drift, freshness, delta refresh, and Owlib incremental sync;
- policy-driven revocation/deletion propagation from source records through
  promoted essences, drill-down refs, exports, and derived indexes;
- generic RAG export remains optional and derived.

### v1.0 — Core GA and Single-Organization Hub Beta

- OAuth/OIDC protected remote MCP with audience-bound tokens;
- one organization per deployment, tenant-ready contracts, project registry, allowlists, quotas, audit, backup/restore of Hub state;
- tested Beta recovery objectives for Hub-owned state and an explicit statement
  that project Markdown/Git backup remains customer-owned;
- privacy-safe readiness and operational health metrics with external
  monitoring export and no knowledge-body telemetry;
- registered project and reviewed enterprise surfaces are server-visible;
  private `user_global` remains client-local unless a later explicit sync product is approved;
- object authorization and knowledge-scope checks before retrieval;
- remote read and propose profiles; read-only remains the default;
- three golden flows pass with zero cross-scope leakage;
- Standalone lifecycle, install, upgrade, uninstall, and offline proof remain GA requirements;
- hosted multi-tenant SaaS, SCIM/SAML, HA, and multi-region remain post-v1.

## Final Blind-Spot Amendments

The evidence-linked review in
`internal/owledge/reviews/v1-session-final-plan-blind-spot-review-2026-08-12.md`
adds four bounded requirements without creating new product modules:

1. `OW-071-08` owns repair of the current `upgrade-drift` finalization-gate
   regression, useful progress output, and a clean 38/38 aggregate run before RC.
2. `OW-081-09` owns the immediate local multi-harness `user_global` proof.
3. `OW-090-04` owns the single semantic mutation Core interface; MCP, CLI, Pi,
   and Hub remain adapters at that seam.
4. `OW-090-02`, `OW-090-09`, `OW-100-02`, and `OW-100-11` own derived-data
   revocation plus bounded Hub Beta recovery evidence.
5. `OW-080-01/02/09`, `OW-081-01`, and `OW-100-03/05/09` own only the
   compatibility seams for managed surfaces, modules, linked external
   resources, health profiles, and transactional upgrades. Media ingestion,
   third-party extension distribution, and bounded DSAR orchestration remain
   post-v1 products.

The review does not unlock v0.8.0. The owner selection of
`1B+ / 2C+ / 3B` is complete; `OW-071-05`, V0.7.1 RC/alignment, and a clean
38/38 finalization run remain mandatory stops.

## Required QA Gates

1. **Research contract gate:** IDs, source receipts, lifecycle, scope, and freshness fields round-trip; malformed or ambiguous records fail clearly.
2. **Recall gate:** fresh existing research prevents an unnecessary refresh recommendation; stale or missing claims produce a bounded delta brief.
3. **Scope isolation gate:** project-user, user-global, and enterprise records never cross into an unauthorized pack or index result.
4. **Session recap gate:** session close produces a private Candidate with structured deltas and no raw transcript promotion.
5. **Pi conformance gate:** Pi uses the same capability and artifact semantics as MCP/CLI and remains a thin adapter.
6. **Promotion gate:** no Agent or Librarian can promote without the required review, policy, sanitization, and audit evidence.
7. **Hub security gate:** OAuth resource/audience validation, server-side scope resolution, project ACLs, rate limits, audit, and zero cross-scope leakage.
8. **Rebuild gate:** all indexes, search projections, and Hub retrieval views can be rebuilt from canonical Markdown/Git plus append-only receipts.
9. **Schema/settings gate:** artifact profiles, extensions, layered settings,
   deny-wins policy, migration dry-run, and unknown-key behavior round-trip
   without rewriting user-authored knowledge.
10. **Global inbox gate:** raw candidates cannot enter normal retrieval; every
    promote/reject/archive result retains source revision, reason, target, and
    audit receipt.
11. **Idea resurfacing gate:** a feature-planning fixture rediscovers relevant
    deferred ideas and records a disposition without expanding the MVP silently.
12. **Document revision gate:** a material edit without exactly one
    `document_version` increment fails; schema/profile migration and content
    revision remain distinguishable and legacy documents stay readable.
13. **Deep-retrieval gate:** a reviewed global essence answers the bounded
    question first, then an authorized explicit deep dive resolves the exact
    project artifact and Evidence revision; unauthorized, missing, and stale
    sources fail explicitly without copied fallback content.
14. **Knowledge-health gate:** deterministic health detects seeded stale,
    duplicate, orphaned, unresolved, over-budget, raw-backlog, and projection
    drift failures; Hub health export contains no knowledge body or raw prompt.
15. **Local user-global gate:** two reference harnesses query the same private
    local federation with explicit project allowlists and no Hub upload.
16. **Semantic mutation gate:** concurrent or replayed writes cannot lose an
    accepted revision; every mutation returns an idempotent success or an
    explicit conflict/reconciliation receipt.
17. **Revocation propagation gate:** a withdrawn source becomes unavailable in
    global essences, drill-down, exports, and indexes according to policy while
    retaining only the permitted non-content audit tombstone.
18. **Release-finalization gate:** the full suite streams bounded progress and
    passes from a clean committed source tree; a green nested version check
    cannot mask a failed generated-surface doctor result.

## Test and Failure-Mode Map

```text
RESEARCH-TO-RESUME COVERAGE
===========================
question
  -> resolve principal + project + allowed scopes
  -> deterministic recall
       -> sufficient_current -> cited reuse; no external search
       -> stale/partial/missing/conflicted -> bounded delta brief
  -> optional external research adapter
  -> Evidence + Candidate artifacts
  -> reviewed promotion
  -> rebuilt scoped index/context pack
  -> structured Session Recap Candidate
  -> second harness resumes by stable IDs and checkpoint hashes

HUB AUTHORIZATION COVERAGE
==========================
OIDC token
  -> issuer/audience/signature/time validation
  -> human or service principal mapping
  -> project allowlist + knowledge-scope capability
  -> semantic MCP/HTTP operation
       -> read -> scoped result + receipt
       -> propose -> Candidate/Evidence + audit receipt
       -> promote -> separate reviewer/policy gate
```

| Path | Realistic production failure | Required coverage | Required handling | User-visible result |
| --- | --- | --- | --- | --- |
| Recall | Mutable documentation changed but cached finding appears current | source-hash/version and expiry regression | return `stale` with delta reasons | explicit stale result, never silent reuse |
| Scope resolution | Caller supplies another project's path or ID | confused-deputy and cross-scope corpus | server resolves allowlist from principal, not path | authorization error with stable code |
| Research dedupe | Renamed finding creates a duplicate claim | stable-ID/path-rename fixture | preserve ID and report duplicate/conflict | conflict/dedupe receipt |
| Delta refresh | Search adapter times out after partial findings | interruption/idempotency fixture | retain Evidence, mark run partial, retry only missing delta | partial result with retry plan |
| Session recap | Hook fires twice during client retry | idempotency-key and hash fixture | return the existing Candidate receipt | successful no-op or explicit mismatch |
| Promotion | Agent attempts direct canonical edit | permission and lifecycle negative test | reject and require Promotion Request | policy error naming required review |
| Hub identity | JWKS is unavailable or token is revoked/expired | OIDC outage/revocation fixture | fail closed; allow no stale authorization extension | retryable authentication error |
| Derived index | Process crashes during rebuild | atomic-swap/restart fixture | retain previous complete projection and resume | stale-but-safe status with rebuild action |
| Canonical Git write | Concurrent accepted promotions conflict | commit/base-hash conflict fixture | no overwrite; create reconciliation finding | conflict result with affected IDs |

No listed path may fail silently. Each negative path is part of its owning ticket's
acceptance evidence; Hub authorization and promotion paths require integration or
end-to-end coverage, while deterministic recall and contract branches use unit and
fixture tests.

Inline ASCII pipeline comments should be added during implementation only where
the state transition is otherwise non-obvious: the Core recall classifier,
promotion state machine, Hub authorization resolver, and atomic index rebuild.

## Definition of Done

- The v1 master plan, backlog, tickets, gates, traceability matrix, and checklist reflect the owner decisions and release cuts above.
- No current v0.7.1 execution ticket or accepted gate is silently reopened.
- Research reuse is a native Owledge lifecycle, not a duplicate external vault system.
- Pi is a reference adapter, not a Core dependency.
- Single-Organization Hub Beta has a separately truthful maturity label from Standalone Core GA.
- Deferred features remain visible with rationale and trigger conditions.
- All edited plan artifacts carry RFC 3339 `updated_at` values and explicit plan versions.
- `python tools/validate_v1_delivery_plan.py` passes with no new errors.

## Resume State

Planning integration is active. Resume from the first unchecked item in
`internal/owledge/workpackages/owledge-v1-federated-research-memory-and-pi-adapter-reprioritization-checklist.md`.

Current v0.7.1 execution remains at `OW-071-05`; this planning amendment may change only future release scope until the mandatory `G-071-ALIGNMENT` owner stop authorizes v0.8.0 execution.
