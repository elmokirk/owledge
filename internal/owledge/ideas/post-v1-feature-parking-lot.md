---
memory_id: "mem:owledge:global:owledge:project_context:post-v1-feature-parking-lot"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "roadmap"
document_version: 1
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge post-V1 feature parking lot"
summary: "Canonical searchable register of features deliberately excluded from the minimal V1, including value, rationale, dependencies, reconsideration triggers, and source links."
concept_tags: ["post-v1", "parking-lot", "roadmap", "scope-control"]
stack_tags: ["markdown", "python", "mcp", "oauth"]
problem_patterns: ["feature-ideas-lost-in-chat", "parked-work-silently-reactivated", "roadmap-bloat"]
architecture_patterns: ["durable-candidate-register", "trigger-based-resurfacing", "explicit-scope-promotion"]
failure_modes: ["parked-without-trigger", "duplicate-roadmap-item", "future-idea-loaded-into-working-context"]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-13T17:20:00+02:00"
updated_at: "2026-08-13T17:20:00+02:00"
source_hash: ""
reusable_lessons:
  - "A parked feature is durable only when its future evaluation trigger and original reasoning are explicit."
  - "Parking preserves option value; it does not create a hidden dependency on the active release."
edges:
  - type: "relates_to"
    target: "mem:owledge:global:owledge:plan:v1-minimal-core-finalization"
    confidence: 1.0
    reason: "Holds every feature removed by the V1 scope-reduction plan."
---

# Post-V1 Feature Parking Lot

## Contract

`parked` means deliberately valuable but not required for the currently approved
V1 outcome. Parked items:

- never enter a V1 gate or dependency;
- remain searchable by stable ID, tags, related projects, and source links;
- are excluded from ordinary execution context;
- may surface in planning-purpose recall when their `reconsider_when` trigger
  matches;
- require an explicit owner decision before moving to `candidate` or `active`.

Canonical V1 boundary: [[owledge-v1-minimal-core-finalization-plan]].
Decision: [[v1-minimal-core-and-product-surfaces-2026-08-13]].

## Priority meanings

| Horizon | Meaning |
| --- | --- |
| V1.1 candidate | Evaluate immediately after V1 adoption evidence |
| V1.x add-on | Optional module that can evolve independently of Core |
| Future product | Separate commercial/deployment surface requiring discovery |
| Research only | Preserve concept; do not schedule until evidence changes |

## Parked register

| ID | Feature / concept | Horizon | Why parked | Reconsider when | Dependencies / source |
| --- | --- | --- | --- | --- | --- |
| PARK-001 | Single-Organization Hub Beta | V1.1 candidate | Auth, remote transport, backup, operations, and security multiply V1 scope without enabling the owner's immediate local use | Core GA is used across >=3 real projects and local Null-Space pain justifies central deployment | `OW-100-11`; [[v1-schema-global-knowledge-health-decision-matrix-2026-08-12]] |
| PARK-002 | Enterprise/shared knowledge scope | V1.1 candidate | Multi-user authority and privacy rules are unnecessary for private local V1 | Hub product decision is approved with tenant/principal model | `OW-100-11`, PARK-001 |
| PARK-003 | OAuth/OIDC, RBAC, agent/service identities and bearer-token management | V1.1 candidate | Security-sensitive server concern, not a local kernel responsibility | A bounded Hub deployment and identity provider are selected | PARK-001; enterprise research |
| PARK-004 | Enterprise provider/model/region/data-class allowlists | V1.1 candidate | Valuable for EU/customer policy but no cloud/model calls exist in Core V1 | First enterprise pilot has an approved provider policy | PARK-001/003 |
| PARK-005 | Hub/admin frontend for knowledge, permissions and agent verification | Future product | UI and admin workflows add a second product surface | Hub API/security contract is stable and customers request self-service | PARK-001/003 |
| PARK-006 | Hosted multi-tenant SaaS, billing, SAML/SCIM, HA, Kubernetes, multi-region | Future product | Fundamentally different operational and commercial product | Repeated single-org pilots prove demand and operating model | strategic roadmap; PARK-001 |
| PARK-007 | Pi reference adapter and Owledge Pi Librarian agent | V1.x add-on | Generic MCP provides the portable seam; Pi-specific lifecycle is not needed for V1 | Generic adapter cannot deliver a measured Pi use case | `OW-081-04` |
| PARK-008 | Hermes-specific integration, cron jobs, daily summaries and coaching automation | V1.x add-on | Automation/scheduling is not knowledge-kernel behavior | Stable MCP lifecycle exists and a concrete automation has a measured owner/team benefit | session ideas; PARK-007 |
| PARK-009 | LangChain/LangGraph adapters | V1.x add-on | Framework-specific adoption surface; generic MCP/CLI is sufficient | Two real integrations reveal missing generic capability | session question 10 |
| PARK-010 | Multi-model judge/review dispatcher | V1.x add-on | Review orchestration is separate from storing evidence/results | Stable review artifact contract exists and repeated manual cross-model review is costly | session question 14 |
| PARK-011 | Agent-system logging, tracing and team observability | Future product | Owledge should store knowledge/evidence, not become a generic telemetry backend | A bounded evidence/receipt use case cannot be served by external observability tools | session question 11 |
| PARK-012 | Autonomous delivery skill, worker/worktree claims and harness orchestration | V1.x add-on | Makes Owledge look like an agent orchestrator and expands authority | Core lifecycle is stable and users explicitly choose an orchestration add-on | `OW-080-12`, `OW-081-06`, `OW-081-12`, `OW-081-13` |
| PARK-013 | Edge/local-model delivery profile and real 4B orchestration claims | V1.x add-on | Small context packs belong in Core; model-specific delivery claims need separate evidence | Minimal Core context journey is green and a pinned local model is selected | `OW-081-14` |
| PARK-014 | Documentation Compiler and broad impact-analysis engine | V1.x add-on | Separate derived-doc product; Knowledge Health covers the V1 need | Teams request generated living docs and source graph is stable | `OW-090-05`; trimmed `OW-090-06` |
| PARK-015 | Generic JSONL RAG export and LightRAG adapter | V1.x add-on | Existing Markdown/direct index path is sufficient; external retrieval evaluation delays V1 | A consumer requests export or local scale exceeds the Core index path | `OW-090-07`, `OW-090-08` |
| PARK-016 | Additional vector, graph, GraphRAG and embedding backends | Research only | Backend proliferation would fragment retrieval semantics | Generic export contract is reactivated and a backend wins evidence-based evaluation | PARK-015 |
| PARK-017 | Extension registry, signatures and broad supply-chain permission manifests | V1.x add-on | Needed for third-party ecosystem, not first-party local V1 | Third-party extension distribution begins | `OW-100-03` |
| PARK-018 | Deterministic DSAR/erasure orchestration and connector suite | V1.1 candidate | Enterprise-only breadth; V1 only needs extension seams and local deletion/tombstones | Enterprise pilot requires coverage-bounded subject erasure | [[enterprise-agentic-knowledge-and-deterministic-erasure-architecture-2026-08-12]] |
| PARK-019 | PII Masker integration as privacy adapter | V1.x add-on | Masking is not erasure and no concrete package/contract is selected | A specific PII Masker is chosen for preview/redaction, never as deletion proof | erasure research; user correction from PyMasking to PII Masker |
| PARK-020 | OKC/Open Knowledge Compiler integration | V1.x add-on | OKC is an optional upstream evidence producer, not Owledge Core | Users need repo/API/test/Jira compilation feeding Owledge candidates | [[owledge-v1-vs-open-knowledge-compiler-primary-source-comparison-2026-08-12]] |
| PARK-021 | Knowledge browser/UI | Future product | Markdown/CLI/MCP prove product value first | Retrieval/lifecycle telemetry shows CLI inspection is the adoption bottleneck | session idea |
| PARK-022 | Advanced comparative benchmarks, broad case studies and ROI claims | V1.x add-on | Core GA needs bounded proof, not a research campaign | Stable V1 release exists and claims need public comparison | trimmed `OW-100-04` |
| PARK-023 | Full profile/module decomposition into separately published packages | Research only | Premature packaging split increases release burden before contracts stabilize | V1 usage proves independent versioning or dependency needs | [[owledge-v1-minimal-core-finalization-plan]] |
| PARK-024 | Remote user-global synchronization | Future product | Private local user-global is the V1 promise; remote sync changes trust model | Users explicitly request multi-device sharing and encryption/identity are designed | prior scope decision |

## Retained V1 items that must not be parked accidentally

- Research recall, freshness and delta-only refresh;
- private local user-global Null-Space;
- deterministic context budgets and progressive disclosure;
- Candidate/Idea/Feature parking and planning-purpose resurfacing;
- reviewed local promotion and source drill-down;
- local health, tombstones, upgrade and recovery;
- Codex, Claude Code, and generic MCP/CLI thin adapters.

## Reevaluation workflow

At every post-V1 planning gate:

1. query only parked entries whose triggers or related projects match;
2. show the essence, original value, park reason, dependencies, and new evidence;
3. choose `keep_parked`, `promote_to_candidate`, `reject`, or `archive`;
4. if promoted, create a new scoped plan/ticket; do not mutate this history away;
5. update `document_version` and `last reviewed` evidence.
