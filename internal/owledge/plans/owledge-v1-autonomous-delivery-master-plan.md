---
memory_id: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "plan"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge autonomous delivery master plan through v1.0"
summary: "Gate-driven release and ticket plan for delivering Owledge v0.7.1 through v1.0 with a local Standalone Core GA, bounded Single-Organization Hub Beta, reusable Research Memory, portable capability contracts, reference runtime adapters, trusted knowledge workflows, and product hardening."
concept_tags: ["v1-roadmap", "autonomous-delivery", "long-horizon", "agentic-coding"]
stack_tags: ["python", "markdown", "yaml", "mcp", "git"]
problem_patterns: ["roadmap-drift", "context-bloat", "unsafe-agent-writes", "adapter-drift"]
architecture_patterns: ["gate-driven-delivery", "markdown-first-control-plane", "ticket-dag", "worktree-isolation"]
failure_modes: ["checkbox-without-evidence", "silent-scope-expansion", "token-regression", "canonical-auto-promotion"]
confidence: 0.94
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-16T00:00:00Z"
updated_at: "2026-08-12T14:32:51+02:00"
plan_version: "2.5.0"
document_version: 4
source_hash: ""
reusable_lessons: []
edges:
  - type: "supersedes"
    target: "docs/strategic-roadmap-2026-2027.md"
    confidence: 0.9
    reason: "This plan converts the approved strategic direction into an executable release and ticket control plane."
---

# Owledge Autonomous Delivery Master Plan Through v1.0

## Outcome

Deliver Owledge v1.0 as a local-first, Git-native Knowledge Lifecycle and
Context control plane with two truthfully separated product surfaces:

- **Standalone Core GA** for solo power users and AI-first local workflows;
- **Single-Organization Hub Beta** for one organization per deployment, with
  OAuth/OIDC-backed remote MCP, scoped project discovery, centrally reviewed
  enterprise knowledge, audit receipts, and read/propose operations. Private
  `user_global` memory stays local-first in v1 and is not uploaded implicitly.

Codex, Claude Code, Pi, Hermes, OpenCode, and generic MCP/CLI consumers must use
the same portable capability and artifact semantics. Owledge recalls existing
Research Memory before recommending external research and preserves source,
reason, context, freshness, contradictions, and promotion state for reuse.

The v1.0 promotion boundary requires the full golden journey to work without chat
history: install, initialize, plan, compile scoped context, execute with interruption,
resume in another Tier-1 harness, attach evidence, pass independent QA, promote
reviewed knowledge, compile living documentation, and reproduce the result from the
evidence bundle.

## Locked Product Decisions

- Primary ICP through v1.0: solo power users and AI-first builders, including
  beginner AI users and vibecoders. A bounded Single-Organization Hub Beta is a
  secondary v1 product surface for small teams and enterprise architecture proof;
  a hosted multi-tenant SaaS remains post-v1.
- All public product documentation is English.
- Canonical promotion is explicit and gate-controlled. Agents may create candidates,
  evidence, handoffs, and checkpoints automatically within declared paths.
- Required reference profiles through v1: Codex, Claude Code, Pi, and generic
  MCP/CLI. Hermes and OpenCode must consume the same generic contract and may
  gain dedicated adapters only when they add measurable value beyond MCP/CLI.
- Docker remains an optional deployment adapter rather than the Standalone
  installation model. The Single-Organization Hub Beta may ship one bounded
  single-node deployment recipe if its security and recovery gates pass.
- Owlib remains a technically separate optional package behind coherent Owledge
  UX. It provides user-global and Hub-derived cross-project recall, freshness,
  Research Memory discovery, PI intelligence, and candidate synthesis. It writes
  central candidates, never project truth.
- Owlib and Hub retrieval default to the current project. Additional projects and
  `user_global` or `enterprise` scopes require explicit grants and allowlists.
- The three knowledge scopes are `project_user`, `user_global`, and `enterprise`.
  `user_global` is a private local federation across explicitly linked projects;
  personal global memory and organization-shared knowledge never share a default
  scope or implicit synchronization path.
- V1 must prove one local `user_global` reference composition used by at least
  two harnesses. Remote synchronization of private user-global memory remains a
  separate post-V1 product decision.
- Cross-project promotion uses a private raw inbox excluded from normal
  retrieval: `project candidate -> global raw -> reviewed/promoted or
  rejected/archived`. Rejection retains reason, retention, and receipt.
- Autonomous recall, capture, and model/provider use are governed by versioned
  deterministic settings. Later settings layers may narrow authority but may
  never weaken Core or organization safety invariants.
- Existing-project migration is opt-in, preview-first, dry-run capable, and must not
  overwrite user-owned Markdown silently.
- MCP writes are semantic operations, never a general arbitrary-file-write API.
- Every semantic write crosses one Core mutation interface with target identity,
  expected document revision/base hash, idempotency, authorized transition,
  atomic result, and conflict/reconciliation receipt; transports remain adapters.
- Small-model Tier 1 targets a 4B-class model with at least an 8k context window; v0.8.1 claims require deterministic fixtures plus one real local-model smoke run.
- The existing v0.7 benchmark fixture must retain at least 80% reduction in tokens per
  correct answer against its naive baseline, with no quality, privacy, or stale-source
  regression. New harder fixtures use separate thresholds.
- RAG v1 begins with a generic JSONL retrieval projection and a LightRAG reference
  adapter. Raw frontmatter is metadata, not embedding text.
- Research v1 uses the existing `.owledge/research/` and `global-memory/research/`
  layers. Recall, deduplication, source mutability, freshness, and delta-only
  refresh are Core semantics; web search and model routing remain Skill/adapter behavior.
- Scope, knowledge abstraction, and lifecycle are orthogonal contracts. The
  promoted global Knowledge Base stores reviewed Research essences, learnings,
  patterns, and transferable concepts; its private raw inbox remains excluded
  from retrieval and is not itself the global Knowledge Base.
- Reviewed global essences retain stable, permission-checked drill-down
  relations to project canonical detail and source Evidence. Deep retrieval is
  explicit, budgeted, source-aware, and never implemented by copying every
  project file into the global layer.
- Source withdrawal, access revocation, and policy-driven deletion propagate
  through global essences, drill-down refs, exports, and derived indexes without
  leaving retrievable shadow content.
- Every material Owledge-managed artifact edit increments a deterministic
  document revision distinct from schema/profile versions and the content hash.
- Deterministic Knowledge Health is a V1 product capability. Hub readiness and
  privacy-safe operational metrics are a separate adapter surface; Owledge does
  not store raw prompts/outputs or become a generic observability backend.
- Hub Beta recovery covers only Hub-owned state under published tested bounds;
  canonical project Markdown/Git backup remains an explicit customer responsibility.
- Pi is a v1 reference runtime adapter. `@owledge/pi` owns lifecycle/tool wiring
  only and may not duplicate Core search, context, artifact, or promotion logic.
- A hosted multi-tenant Team Hub, remote Git/CI synchronization, SAML/SCIM,
  Kubernetes/HA, and multi-region operation remain post-v1. The v1 Hub Beta is
  one organization per deployment and must not be marketed as hosted SaaS.

## Locked V1 Architecture Decision

- The product owner approved `1B+ / 2C+ / 3B` on 2026-08-12. Replace the current
  broad frontmatter required-field list with a versioned
  Schema Registry: a small common envelope plus artifact-specific profiles.
  Custom fields remain namespaced, preserved, inert by default, and unable to
  override Core policy. The recommendation now includes required
  `document_version` bumping for material edits and explicit separation from
  `schema_version`, `profile_version`, and `source_hash`.
- Use bounded delta capsules by default, allow snapshots only by explicit policy,
  orient recall through reviewed global essences, and retain permission-checked
  project/Evidence drill-down.
- Ship Standalone Core as GA and the one-organization Hub only as Pilot/Beta.
  The locked selection removes the architecture-choice blocker; compatibility
  migration proof and the existing release gates remain mandatory.

## Non-Goals Through v1.0

- No hosted multi-tenant Owledge SaaS, billing, mandatory cloud backend, or
  Owledge-owned password database.
- No replacement for agent runtimes, vector databases, graph databases, issue
  trackers, or IDEs.
- No automatic canonical promotion, autonomous conflict resolution, hidden writes, or implicit subagent dispatch.
- No claim that the synthetic benchmark percentages generalize to every repository.
- No Pi-only Core, automatic raw-transcript promotion, mandatory vector/graph
  database, or unconditional external research before checking existing memory.
- No remote multi-tenant MCP service, SAML/SCIM, HA, or multi-region promise in v1.
- No generic tracing backend, full Owledge agent harness, scheduler, knowledge
  frontend, multi-model judge dispatcher, or LangGraph-owned memory in v1.
  Knowledge Health and Hub operations metrics remain bounded report/adapter
  interfaces and do not reopen these non-goals.

## Canonical Control Plane

Execution source of truth:

`internal/owledge/workpackages/owledge-v1-autonomous-delivery/`

Required read order for every execution turn:

1. `GOAL.md` and `RUN-STATE.yaml`
2. `CONTROL-PLANE-POLICY.md`
3. the active or first ready ticket assignment from `BACKLOG.yaml`
4. only that ticket and its gate via `python tools/validate_v1_delivery_plan.py --ticket-id <id>` and `--gate-id <id>`
5. the latest gate report and directly referenced decisions/contracts only

Run `python tools/validate_v1_delivery_plan.py` before claiming or promoting work. The master plan is strategic context, not the per-turn execution payload.

## Release Train

| Release | User-visible increment | Technical promotion boundary | Mandatory alignment stop |
| --- | --- | --- | --- |
| v0.7.1 | A beginner can understand, install, try, and verify Owledge; Owlib and the required Hermes read-only profile match the v0.7 project contract. | Adoption journey and release truth are green on Windows, macOS, and Linux fixtures. | Feature update, open questions, and explicit user alignment before publishing or v0.8.0. |
| v0.8.0 | Human intent and prior Research Memory become validated, scope-aware, token-budgeted contracts and clean retrieval projections. | Artifact/scope/capability contracts, Research recall, context determinism, RAG projection, and migration gates are green. | Feature update, open questions, and explicit user alignment before publishing or v0.8.1. |
| v0.8.1 | Codex, Claude, Pi, and generic MCP/CLI reuse the same capabilities, share one private local user-global federation, create structured session recaps, and resume without chat history. | Adapter conformance, local multi-harness user-global recall, Session Recap, and cross-harness resume gates are green; optional autonomous delivery does not block Knowledge-Librarian value. | Feature update, open questions, and explicit user alignment before publishing or v0.9.0. |
| v0.9.0 | Reviewed operational and Research knowledge can be evidenced, promoted, superseded, compiled, exported, delta-refreshed, and policy-revoked across authorized scopes. | Single-interface semantic writes, promotion, privacy, revocation propagation, research drift, RAG round-trip, and Owlib freshness gates are green. | Feature update, open questions, and explicit user alignment before publishing or v1.0. |
| v1.0 | Standalone Core is GA and a bounded Single-Organization Hub is Beta, measurable and secure by default. | OAuth/OIDC remote MCP, project registry, scope isolation, audit, three golden flows, portability, CLI lifecycle, docs, evidence reconstruction, and final artifact gates are green. | Final feature update, post-v1 question register, and explicit user closeout before GA/Beta publication. |

## Version Alignment and `/goal` Handoff

Every RC/GA is a technical promotion candidate, not permission to continue autonomously. After its release gate passes, Codex must execute that version's dedicated alignment ticket, write the matching `release-updates/<version>.md`, present the update and all open questions to the user, and set the run state to `awaiting_user_alignment`.

The next version's tickets are dependency-blocked by the prior alignment ticket. The agent may prepare evidence and answer questions, but it must not publish/tag, begin the next version, or mark the alignment ticket `done` until the user explicitly chooses `approve`, `adjust`, or `defer`.

`GOAL.md`, `ALIGNMENT-PROTOCOL.md`, `RUN-STATE.yaml`, and the active alignment ticket form the copy-ready `/goal` handoff. Each update covers shipped features, user benefits, evidence/gates, migrations, known limitations, deferred work, implementation findings, decisions, proposed next-version scope, and complete finding/decision/question registers.

## Version Reflection and Steering Contract

For delivery control, one owner-facing phase equals one version bump:
v0.7.1, v0.8.0, v0.8.1, v0.9.0, v1.0. Internal A/B/C phases remain
technical gates inside that version.

Every ticket and gate records material problems, gaps, deviations, regressions,
new risks, and decisions in `RUN-STATE.yaml`. The version alignment ticket must
then:

1. reconcile planned versus actually shipped scope;
2. present the complete implementation finding and decision logs;
3. distinguish resolved items from owner decisions still required;
4. reflect the next version ticket-by-ticket as `keep`, `amend`, `defer`, or
   `drop`, including gate and dependency impact;
5. recommend a safe default for every unresolved item;
6. stop until the owner records `approve`, `adjust`, or `defer`.

No material finding may disappear between ticket evidence, gate evidence, and
the release update. Safety, privacy, credentials/cost, data-loss, external
commitment, acceptance-boundary, and irreversible-architecture findings
escalate immediately rather than waiting for the version stop.

Decision source:
`internal/owledge/decisions/v0.7.1-v1-version-reflection-contract-2026-07-27.md`.

## Version v0.7.1 - Adoption, Truth, and Compatibility

### Phase 071-A - Truth and release baseline

Tickets: `OW-071-01`, `OW-071-02`, `OW-071-03`, `OW-071-13`.

Outcome: one truthful work register, a reproducible release baseline, an enforced
token-efficiency floor, and a safe explicit boundary for the shipped local HTTP
control-plane prototype.

Gate: `G-071-A-TRUTH`.

### Phase 071-B - Beginner adoption journey

Tickets: `OW-071-04`, `OW-071-10`, `OW-071-11`, `OW-071-12`, `OW-071-14`, `OW-071-05`.

Outcome: an English adoption surface first explains why, when, benefits,
boundaries, and the end-to-end Owledge lifecycle; a dedicated Installation Hub
separates integration footprint, delivery method, runtime adapter, and optional
capabilities; skills and agent recipes are explicit; the vibecoding demo works
without maintainer interpretation. Named adoption presets separate personal
global memory, static Hub maps, Owlib, the local HTTP prototype, and a future
remote Team Hub.

Plan: `internal/owledge/plans/v0.7.1-public-docs-adoption-plan.md`.

Gate: `G-071-B-ADOPTION`.

### Phase 071-C - Owlib and Hermes Tier-1 read compatibility

Tickets: `OW-071-06`, `OW-071-07`, `OW-071-08`.

Outcome: Owlib reads the current `.owledge` layout safely and Hermes proves the
required minimal read-only MCP profile locally or on a VPS.

Gate: `G-071-C-COMPAT` and release gate `G-071-RC`.

## Version v0.8.0 - Portable Control Plane and Retrieval Foundation

### Phase 080-A - Versioned contract foundation

Tickets: `OW-080-01`, `OW-080-02`, `OW-080-03`, `OW-080-04`, `OW-080-16`.

Outcome: ProjectManifest, ArtifactEnvelope, WorkContract, Backlog, RunState,
Checkpoint, GateResult, EvidenceManifest, knowledge scopes, capability envelopes,
a common-envelope plus artifact-profile Schema Registry, layered policy settings,
document revisions, orthogonal scope/abstraction/lifecycle axes, and Research
Brief/Source/Finding/Synthesis contracts are versioned, validated, and
migratable. Autonomous Delivery remains a post-v1 add-on rather than a Core dependency.

Gate: `G-080-A-CONTRACTS`.

### Phase 080-B - Context and small-model runtime

Tickets: `OW-080-05`, `OW-080-06`, `OW-080-07`.

Outcome: deterministic pack types, recall-before-research, progressive disclosure,
active-tool filtering, and bounded context budgets keep existing knowledge reusable
without loading full histories or repeating external research unnecessarily.

Gate: `G-080-B-CONTEXT`.

### Phase 080-C - Retrieval projection, status, and migration

Tickets: `OW-080-08`, `OW-080-09`, `OW-080-10`.

Outcome: clean-body retrieval projections, a deterministic Knowledge Health
status view, and safe preview migration are available to real users. Health
detects schema/revision, edge, source, freshness, duplication, context-budget,
and projection failures without an LLM or knowledge-body telemetry.

Gate: `G-080-C-RETRIEVAL` and release gate `G-080-RC`.

## Version v0.8.1 - Tier-1 Agentic Coding

### Phase 081-A - Capability contract and reference adapters

Tickets: `OW-081-01`, `OW-081-02`, `OW-081-03`, `OW-081-04`, `OW-081-05`.

Outcome: Codex, Claude Code, Pi, and generic MCP/CLI declare and prove the same
portable capability contract without pretending unsupported hooks exist. Hermes
and OpenCode compatibility is proven through the generic contract before any
dedicated adapter scope is accepted.

Gate: `G-081-A-ADAPTERS`.

### Phase 081-B - Session continuity and recovery

Tickets: `OW-081-07`, `OW-081-08`.

Outcome: structured Session Recap Candidates, checkpoints, hooks, and handoffs
support cross-harness resume without chat history. Claims, worktrees, and
autonomous-delivery behavior remain post-v1 add-on capabilities and do not
expand the Knowledge-Librarian Core interface.

Gate: `G-081-B-CONCURRENCY`.

### Phase 081-C - Scoped context and golden cross-harness journey

Tickets: `OW-081-09`, `OW-081-10`.

Outcome: Owlib can compile explicitly authorized `project_user`, `user_global`,
and `enterprise` context, start with reviewed global essences, drill down through
stable project/source revisions on explicit request, and prove Research recall
plus interrupted work can resume in another reference harness.

Gate: `G-081-C-JOURNEY` and release gate `G-081-RC`.

## Version v0.9.0 - Trusted Writes and Knowledge Lifecycle

### Phase 090-A - Evidence, authority, and promotion

Tickets: `OW-090-01`, `OW-090-02`, `OW-090-03`.

Outcome: operational and Research evidence is append-only; claims trace to search
reason, context, source version, retrieval state, reviewer, and authority;
contradictions remain visible; private global raw candidates are excluded from
normal retrieval; promoted user-global/enterprise essences form the central
Knowledge Base with project/Evidence drill-down; and promote/reject/archive
transitions require policy, reason, retention, and gate evidence.

Gate: `G-090-A-TRUST`.

### Phase 090-B - Semantic MCP writes and living documentation

Tickets: `OW-090-04`, `OW-090-05`, `OW-090-06`.

Outcome: scoped semantic writes, source-linked compiled documentation,
Research/source drift, promotion debt, unresolved drill-down sources, and
knowledge-health impact analysis are available without general filesystem
mutation. Refresh work is delta-only.

Gate: `G-090-B-WRITES`.

### Phase 090-C - RAG and Owlib freshness

Tickets: `OW-090-07`, `OW-090-08`, `OW-090-09`.

Outcome: generic JSONL and LightRAG adapters improve retrieval quality, while
incremental Owlib sync, Research freshness, tombstones, project-source
availability, and the three knowledge scopes prevent stale or mixed context.

Gate: `G-090-C-RAG` and release gate `G-090-RC`.

## Version v1.0 - Product Hardening and Release

### Phase 100-A - Security, scale, and Single-Organization Hub Beta

Tickets: `OW-100-01`, `OW-100-02`, `OW-100-03`, `OW-100-11`.

Outcome: secret/PII handling, prompt-injection labels, permission manifests,
OAuth/OIDC remote identity, server-side scope resolution, project registry,
audit receipts, and 10/1k/10k scale targets are published and enforced for the
truthfully labelled Hub Beta.

Gate: `G-100-A-HARDENING`.

### Phase 100-B - Evaluation and product lifecycle

Tickets: `OW-100-04`, `OW-100-05`, `OW-100-06`.

Outcome: portability, Research recall, scope isolation, session resume,
false-pass, rework, install, upgrade, uninstall, support, migration, and
deprecation behavior are measurable and documented.

Gate: `G-100-B-PRODUCT`.

### Phase 100-C - v1 proof and artifact cut

Tickets: `OW-100-07`, `OW-100-08`, `OW-100-09`.

Outcome: English docs, case studies, final conformance, artifact installation,
and evidence-only reconstructions prove Standalone Core GA plus the three bounded
Hub Beta golden flows without conflating their maturity claims.

Gate: `G-100-C-PROOF` and final gate `G-100-GA`.

## Autonomous Execution Policy

- WIP limit is one active ticket per agent and one active integration gate per release.
- Only tickets in `ready` state with all dependencies `done` may start.
- The worker sets the ticket and `RUN-STATE.yaml` to `in_progress` before code changes.
- Workers write only within `allowed_paths`; any overlap requires an explicit
  integration-owner decision before dispatch.
- Every ticket includes positive, negative, privacy/security where relevant,
  regression, rollback, and checkpoint evidence.
- Passing a release candidate or GA gate triggers its alignment ticket; it never authorizes the next release by itself.
- Alignment tickets are deliberate hard stops: the agent records `awaiting_user_alignment`, asks every unresolved question in the user update, and does no next-version or publication work until an explicit user decision is recorded.
- A worker may not be the sole QA owner for its ticket. A separate reviewer verifies
  evidence and attack/failure cases before `done`.
- Failed gates create findings and new tickets. Gates are never made green by silently
  lowering privacy, security, acceptance, context, or compatibility thresholds.
- Agents stop and request owner input for external costs, credentials, production
  resources, customer data, destructive migration, irreversible architecture, or a
  change to the locked product decisions.

## Git, Worktree, and Commit Protocol

Planning branch: `codex/owledge-v1-autonomous-roadmap`.

For each release:

1. Create `codex/vXYZ-integration` from a clean, current `main` after the prior release
   gate is green and tagged.
2. Create one worktree and branch per independent ticket:
   `codex/vXYZ-<ticket-id>-<slug>`.
3. Before dispatch, record base SHA, worktree path, allowed paths, dependency SHAs,
   expected commits, and merge order in the ticket checkpoint.
4. Commit cohesive changes immediately after broad migrations or contract renames.
5. Preferred phase commits are `foundation`, `feature`, `gates`, `docs`, and
   `release-artifacts`; do not mix generated evidence with unrelated source edits.
6. Worker branches never commit directly to the integration branch. The integrator
   merges in DAG order, records commit SHAs in the integration manifest, and reruns the
   cumulative phase gate.
7. Delete worktrees only after their commit and evidence references are reachable from
   the integration branch. Never use destructive reset or checkout to clean user work.
8. A release candidate must have a clean tracked worktree before build, artifact,
   benchmark, or publishing gates run.

Commit convention:

`<type>(<release>/<ticket>): <observable outcome>`

Examples: `feat(v080/OW-080-05): compile deterministic task context packs` and
`test(v081/G-081-B): prove overlapping claims block dispatch`.

## Documentation Contract

Every user-visible ticket must update the same release's English documentation. The
required audience layers are:

- Beginner: Easy Install, first success, terminology, common failure recovery.
- Power user: configuration, scopes, privacy, budgets, Git behavior, migration.
- Adapter author: contract versions, capabilities, fixtures, negative cases.
- Maintainer: release gates, evidence, migration policy, known limitations.

Generated docs carry source hashes and refresh state. Generated views never become a
second source of truth.

## Definition of v1.0 Done

- All v1 critical tickets, including `OW-080-16` and `OW-100-11`, are `done`
  with independent QA evidence and every version alignment decision is recorded.
- All version and final gates are green from documented clean states.
- Codex, Claude, Pi, and generic MCP/CLI achieve at least 95% declared contract
  equivalence on the same fixture; Hermes/OpenCode generic compatibility and all
  unsupported capabilities fail explicitly.
- Existing v0.7 benchmark fixture retains at least 80% token reduction per correct
  answer, zero privacy/stale failures, and no answer-quality regression.
- The 4B/8k profile completes the defined small-model golden tasks within budget.
- Raw frontmatter is excluded from embedding text; retrieval projections improve or
  preserve the published recall/ranking thresholds against the raw-Markdown baseline.
- Existing Research Memory is checked before external refresh; fresh coverage is
  reused, stale or incomplete coverage produces a bounded delta brief, and every
  answer exposes source version and freshness.
- Project-user, user-global, and enterprise fixtures produce zero unauthorized
  cross-scope results before and after lexical, semantic, and graph projection.
- The Single-Organization Hub Beta validates OAuth/OIDC audience binding,
  server-side project authorization, audit receipts, backup/restore of Hub state,
  privacy-safe operations health, and read/propose MCP while direct canonical
  writes remain unavailable.
- A global essence answers a bounded query first and an authorized explicit
  deep dive resolves the exact project artifact and Evidence revision; missing,
  stale, and unauthorized sources are explicit.
- Knowledge Health detects seeded stale, duplicate, orphaned, unresolved,
  over-budget, raw-backlog, missed document-revision, and projection-drift
  failures at 10, 1k, and 10k artifact profiles without exposing knowledge bodies.
- A new user completes the vibecoding demo without maintainer help on supported OS
  fixtures.
- The evidence bundle reconstructs the complete golden journey without chat history.
- Wheel and sdist build, install, upgrade, uninstall, and fresh-project smoke tests pass
  from a clean release candidate.

## Post-v1 Deferred Concepts

- Optional long-running PI intelligence/daily Research guardian after deterministic
  Recall and Research lifecycle metrics prove value.
- Coverage-bounded personal-data erasure/DSAR control plane with subject
  resolution, connector inventory, policy actions, restore guards, and receipts.
  V1 retains only general source-withdrawal, revocation, tombstone, and derived
  projection hygiene; a PII Masker is an optional detector/redactor, not proof
  of deletion.
- Media/file ingestion and voice-transcription adapters over the V1 `ResourceRef`
  seam. Owledge stores the text artifact, provenance, and controlled source link
  by default rather than becoming a binary-file warehouse or transcription engine.
- Public third-party plugin SDK and marketplace after Core compatibility,
  permission, migration, health, cleanup, and uninstall manifests have V1 proof.
- Add-on Decision Layer: provenance-preserving ingestion of external feedback,
  agent evaluations, and plan comparisons; independent model sparring and
  Project Hardening use shared metrics and owner-approved conclusions rather
  than automatic plan rewrites. Discovery plan:
  `internal/owledge/plans/add-on-decision-layer-discovery-plan.md`.
- Docker-first distribution, hosted multi-tenant service, SAML/SCIM, Kubernetes/HA,
  multi-region operation, marketplace certification, and commercial features.

The V1 compatibility foundation for those extensions is deliberately small:
a managed-surface manifest, transactional upgrade protocol, generic module
manifest, media-neutral `ResourceRef`, and distinct `system.doctor`,
`knowledge.health`, and `hub.health` profiles. These deepen existing tickets and
do not create new V1 product modules.

## Resume Rule

Read the execution control plane, select the first ready ticket whose dependencies are
done, and continue from its checkpoint. Never restart a completed phase. If evidence is
stale after later changes, reopen the smallest affected ticket and gate.
