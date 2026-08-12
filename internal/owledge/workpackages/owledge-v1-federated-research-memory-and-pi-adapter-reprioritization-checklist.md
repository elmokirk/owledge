---
memory_id: "mem:owledge:global:owledge:workpackage:v1-federated-research-memory-pi-reprioritization"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "task"
artifact_type: "workpackage"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v1 federated research memory and Pi adapter reprioritization checklist"
summary: "Resume-oriented checklist for integrating the owner-approved research-memory, three-scope, Pi reference-adapter, and Single-Organization Hub Beta changes into the v1 control plane."
concept_tags: ["v1-roadmap", "research-memory", "pi-adapter", "phase-checklist"]
stack_tags: ["markdown", "yaml", "mcp", "oauth"]
problem_patterns: ["plan-drift", "feature-bloat", "orphan-requirement"]
architecture_patterns: ["bidirectional-traceability", "gate-driven-delivery"]
failure_modes: ["chat-only-plan", "unvalidated-ticket-dag", "silent-scope-expansion"]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-11T19:33:00+02:00"
updated_at: "2026-08-12T14:32:51+02:00"
workpackage_version: "1.5.0"
document_version: 4
source_hash: ""
reusable_lessons: []
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:plan:v1-federated-research-memory-pi-reprioritization"
    confidence: 1.0
    reason: "Operationalizes the approved roadmap reprioritization."
---

# Owledge v1 Federated Research Memory and Pi Adapter Reprioritization Checklist

## Resume State

Current resume point: **Phase B — Amend the v1 control plane**.

Current product execution remains independently at `OW-071-05`. This checklist
tracks planning changes only and does not authorize v0.8.0 implementation.

## Phase A — Sources and Owner Alignment

- [x] Product owner confirmed the recommended answers for v1 target, canonical storage, deployment, authentication, and write authority.
- [x] Three knowledge scopes recorded: `project_user`, `user_global`, and `enterprise`.
- [x] Three v1 golden flows accepted.
- [x] `research-orchestrator.skill` read in Blueprint mode, including orchestration, protocol, and finding schema references.
- [x] `Owledge × Pi Agent — Core Architecture Context.md` evaluated against the runtime-independent Core seam.
- [x] Existing Owledge research folders, templates, freshness logic, and Roadmap tickets inspected to prevent duplicate features.

### Phase A Evidence

- Product-owner response in the 2026-08-11 sparring session.
- `C:/Users/Kirk/Downloads/research-orchestrator.skill`
- `C:/Users/Kirk/Downloads/Owledge × Pi Agent — Core Architecture Context.md`
- `templates/owledge/templates/research-brief-template.md`
- `templates/owledge/templates/research-finding-template.md`
- `templates/owledge/templates/research-card-template.md`
- `tools/owledge_core.py`

## Phase B — Amend the v1 Control Plane

- [x] Update the master plan outcome, locked decisions, non-goals, release train, and v1 DoD.
- [x] Add Research Memory and Pi/Hub requirements to the public Roadmap without claiming them shipped.
- [x] Amend v0.8.0 contracts for Research artifacts, three scopes, stable capability envelopes, and recall-before-research.
- [x] Amend v0.8.1 for structured Session Recap, Pi reference adapter, and reduced bespoke-adapter/autonomous-delivery critical path.
- [x] Amend v0.9.0 for Research Evidence, delta refresh, semantic Candidate writes, and scope-aware promotion.
- [x] Amend v1.0 for a truthfully labelled Single-Organization Hub Beta with OAuth/OIDC remote MCP.
- [x] Update BACKLOG dependencies/waves without reopening accepted v0.7.1 work.
- [x] Update gates and traceability for Research recall, scope isolation, Pi conformance, and Hub security.
- [x] Record the owner decisions and implementation constraints in durable run-state planning registers.

### Phase B Evidence

- Active DAG reduced from 64 to 61 tickets while adding `OW-080-16` and
  `OW-100-11`; five delivery-orchestration tickets are retained only as
  documented post-v1 add-ons.
- `D-071-25` records the product-owner decisions without changing current
  `OW-071-05` execution or the `G-071-ALIGNMENT` lock.
- Backlog, execution matrix, tickets, gates, traceability, Roadmap, Goal, and
  master plan all map the same release cut.

## Phase C — QA and Handoff

- [x] Run `python tools/validate_v1_delivery_plan.py` and resolve every new error.
- [x] Run focused validator tests for ticket/gate/wave/traceability consistency.
- [x] Run `git diff --check`.
- [x] Confirm edited planning artifacts have RFC 3339 `updated_at` and bumped plan/workpackage versions.
- [x] Confirm current execution remains `OW-071-05` and v0.8.0 stays locked behind `G-071-ALIGNMENT`.
- [x] Produce a concise owner handoff listing kept, amended, deferred, and dropped scope.

### Phase C Evidence and Owner Handoff

- Validation: 61 tickets, 25 gates, 43 waves, zero errors, zero warnings.
- Focused tests: six of six `test_validate_v1_delivery_plan` cases pass.
- Diff hygiene: `git diff --check` passes.
- **Kept:** Standalone Core, Markdown/Git authority, deterministic Context Packs,
  existing Research layout, Candidate/Review/Promotion, Owlib, generic RAG export.
- **Amended:** three scopes, recall-before-research, structured Session Recap,
  Pi reference adapter, Research drift/delta refresh, four reference profiles.
- **Added:** `OW-080-16` Research Memory and `OW-100-11` Single-Org Hub Beta.
- **Deferred:** Autonomous Delivery Profile, worktree planner, orchestration
  adapters, edge delivery profile, multi-tenant SaaS, SAML/SCIM, and HA.
- **Dropped from Core:** mandatory vector/graph database, built-in password store,
  raw transcript warehouse, and automatic canonical agent writes.

## Definition of Done

- All completed amendment phases are checked with evidence.
- The future ticket DAG embodies the new product direction without adding a second Research system.
- Standalone Core GA and Single-Organization Hub Beta have separate maturity claims.
- Pi is one reference adapter over shared contracts.
- No plan-only statement is presented as implemented product capability.

## Phase D — Architecture Sparring Amendments

- [x] Confirm `user_global` remains local-first in v1.
- [x] Record deterministic user settings as the authority for autonomous
  recall/capture behavior.
- [x] Add a private global raw-inbox lifecycle with reviewed promotion and
  reasoned rejection/archive; exclude raw candidates from normal retrieval.
- [x] Specify a versioned common-envelope plus artifact-profile Schema Registry
  and namespaced inert extensions; lock it as `1B+` after explicit owner
  confirmation.
- [x] Preserve pre-plan idea/roadmap resurfacing as a Core planning value without
  adding an autonomous planning agent to v1.
- [x] Classify LangGraph, generic telemetry, multi-judge dispatch, full harness,
  scheduler, and frontend work as adapters or post-v1 discovery rather than Core.

### Phase D Evidence

- Product-owner answers and 18-question architecture sparring on 2026-08-11.
- Current `CORE_FRONTMATTER_REQUIRED` and `frontmatter_errors` implementation in
  `tools/owledge_core.py`, showing the need for artifact-specific profiles.
- Existing `OW-080-02/03/05`, `OW-081-01/08`, `OW-090-01/02/03/04`, and
  `OW-100-03/11` provide the correct tickets to deepen; no new critical-path
  subsystem is required.

## Phase E — Knowledge Hierarchy, Revision, and Health Feedback

- [x] Add the owner-required material-document version bump and distinguish it
  from schema/profile versions and the content hash.
- [x] Separate authority scope, knowledge abstraction, and lifecycle as three
  orthogonal axes.
- [x] Clarify that Global Raw is a private review queue while the promoted
  global layer is the central Knowledge Base of reviewed essences.
- [x] Add reviewed-global-essence-first recall with authorized project/Evidence
  `explain|deep_dive|refresh` expansion and explicit unavailable/denied states.
- [x] Add deterministic Knowledge Health and separate privacy-safe Hub
  Operations Health without reopening the generic observability/dashboard non-goal.
- [x] Preserve all considered D1/D2/D3 variants, scores, failure costs,
  reversibility, owner requirements, and open selections in a decision record.
- [x] Research plausible primary arXiv sources without claiming the unnamed
  paper has been identified.
- [x] Run plan/frontmatter validation, focused tests, and diff hygiene checks.
- [x] Confirm current execution remains `OW-071-05` and V0.8 implementation
  remains locked behind `G-071-ALIGNMENT`.

### Phase E Evidence

- `internal/owledge/decisions/v1-schema-global-knowledge-health-decision-matrix-2026-08-12.md`
- `internal/owledge/research/hierarchical-memory-global-essence-source-drilldown-arxiv-2026-08-12.md`
- HORMA, H-MEM, HiGMem, and Generative Agents primary arXiv papers.
- `OW-080-01/02/05/09`, `OW-081-09`, `OW-090-01/02/06/09`, and
  `OW-100-01/04/11` were deepened instead of adding a parallel subsystem.
- Validation: 61 tickets, 25 gates, 43 waves, zero errors/warnings; nine
  changed/new frontmatter artifacts valid; live work register 21/21 valid.
- Focused tests: 24/24 plan and live-register validator tests pass.
- Diff hygiene: `git diff --check` passes; current branch remains
  `codex/v071-integration`, active ticket remains `OW-071-05`.

## Phase F — Final Plan Review and Blind-Spot Closure

- [x] Complete the full Dogfood finalization suite instead of relying on the
  earlier controlled abort.
- [x] Diagnose both failed gates and distinguish the expected dirty-source
  rejection from the real `upgrade-drift` host/Kit mode regression.
- [x] Compare the pre-session and amended plans against one weighted scorecard.
- [x] Inventory session ideas as included, considered/deferred, or unresolved.
- [x] Deepen existing tickets for clean finalization, local multi-harness
  `user_global`, one semantic mutation Core interface, revocation propagation,
  and bounded Hub Beta recovery.
- [x] Preserve `OW-071-05` as the only active implementation lane and keep
  V0.8 locked behind V0.7.1 RC/alignment after architecture selection.
- [x] Record explicit owner selection of `1B+ / 2C+ / 3B` on 2026-08-12.
- [ ] Identify the exact hierarchical-memory arXiv paper if the owner supplies
  its title or ID.

### Phase F Evidence

- `internal/owledge/reviews/v1-session-final-plan-blind-spot-review-2026-08-12.md`
- Product-owner confirmation in the 2026-08-12 architecture sparring session:
  `1B+ / 2C+ / 3B` approved as the V1 architecture baseline.
- Full finalization command completed in about 126 seconds: 36/38 gates passed;
  all quality-ratchet dimensions scored 100. `source-identity` correctly rejected
  the dirty planning tree. `upgrade-drift` exposed the generated host/Kit mode
  regression and is routed to `OW-071-08` as `F-071-24`.
- `OW-071-08`, `OW-081-09`, `OW-090-02`, `OW-090-04`, `OW-090-09`,
  `OW-100-02`, and `OW-100-11` were deepened; no new subsystem or active V1
  product line was added.

## Phase G — Final Braindump, Extensibility, and Erasure Cutline

- [x] Correct the owner's term from `PyMasking` to generic `PII Masker` without
  inventing an exact package or its guarantees.
- [x] Park the coverage-bounded personal-data erasure/DSAR control plane as a
  relevant post-v1 enterprise module rather than V1 Beta scope.
- [x] Preserve general V1 source-withdrawal, access-revocation, tombstone, and
  derived-projection cleanup because they benefit individual users too.
- [x] Add only the managed-surface, upgrade-transaction, module-manifest,
  `ResourceRef`, and separated-health-profile seams to existing V1 tickets.
- [x] Park media storage, transcription, public plugin SDK/marketplace,
  universal connector suite, and full Owledge harness outside V1.
- [x] Record the final braindump scenarios, differentiation, scores, and owner
  decision in a versioned decision record and the public Roadmap.

### Phase G Evidence

- `internal/owledge/decisions/post-v1-erasure-extensibility-and-resource-link-decision-2026-08-12.md`
- `internal/owledge/research/enterprise-agentic-knowledge-and-deterministic-erasure-architecture-2026-08-12.md`
- Existing tickets were deepened; ticket count, release waves, and active
  execution lane remain unchanged.
