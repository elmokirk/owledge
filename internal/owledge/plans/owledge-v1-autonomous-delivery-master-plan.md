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
summary: "Gate-driven release and ticket plan for delivering Owledge v0.7.1 through v1.0 with adoption, portable work contracts, Tier-1 agent adapters, trusted knowledge workflows, RAG quality, small-model support, and product hardening."
concept_tags: ["v1-roadmap", "autonomous-delivery", "long-horizon", "agentic-coding"]
stack_tags: ["python", "markdown", "yaml", "mcp", "git"]
problem_patterns: ["roadmap-drift", "context-bloat", "unsafe-agent-writes", "adapter-drift"]
architecture_patterns: ["gate-driven-delivery", "markdown-first-control-plane", "ticket-dag", "worktree-isolation"]
failure_modes: ["checkbox-without-evidence", "silent-scope-expansion", "token-regression", "canonical-auto-promotion"]
confidence: 0.94
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-16T00:00:00Z"
updated_at: "2026-07-27T00:00:00Z"
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

Deliver Owledge v1.0 as a local-first, Git-native project knowledge and agentic
delivery control plane that a solo power user can install and understand quickly,
while Codex, Claude Code, OpenCode, Hermes, and generic MCP/CLI agents can execute the same
portable work contracts safely and efficiently.

The v1.0 promotion boundary requires the full golden journey to work without chat
history: install, initialize, plan, compile scoped context, execute with interruption,
resume in another Tier-1 harness, attach evidence, pass independent QA, promote
reviewed knowledge, compile living documentation, and reproduce the result from the
evidence bundle.

## Locked Product Decisions

- Primary ICP through v1.0: solo power users, including beginner AI users and
  vibecoders. OSS teams are a secondary design target; multi-user service features
  remain post-v1 unless required for on-disk interoperability.
- All public product documentation is English.
- Canonical promotion is explicit and gate-controlled. Agents may create candidates,
  evidence, handoffs, and checkpoints automatically within declared paths.
- Tier-1 runtime profiles through v1: Codex, Claude Code, OpenCode, and Hermes,
  with generic MCP/CLI as the portable baseline. Hermes begins as a required
  read-only profile and must gain explicit conformance evidence; it is not an
  optional path.
- Docker is a lower-priority optional hub/runtime distribution after v1.0.
- Owlib remains a technically separate optional package behind coherent Owledge
  UX. Its long-term role is the central synchronization and intelligence
  interface for reviewed cross-project agent learnings, parallel extraction,
  PI intelligence, and agent-maintenance knowledge. It writes central
  candidates, never project truth.
- Owlib retrieval defaults to the current project plus an explicit project allowlist.
- Existing-project migration is opt-in, preview-first, dry-run capable, and must not
  overwrite user-owned Markdown silently.
- MCP writes are semantic operations, never a general arbitrary-file-write API.
- Small-model Tier 1 targets a 4B-class model with at least an 8k context window; v0.8.1 claims require deterministic fixtures plus one real local-model smoke run.
- The existing v0.7 benchmark fixture must retain at least 80% reduction in tokens per
  correct answer against its naive baseline, with no quality, privacy, or stale-source
  regression. New harder fixtures use separate thresholds.
- RAG v1 begins with a generic JSONL retrieval projection and a LightRAG reference
  adapter. Raw frontmatter is metadata, not embedding text.
- A Pi.dev planning/documentation adapter is post-v1 concept work and is not on
  the v1.0 critical path.
- A hosted Team Hub is post-v1 multi-tenant vision work. Remote Git/CI sync and
  a Sync Layer have no v1 priority; local single-user value must be proven first.

## Non-Goals Through v1.0

- No hosted Owledge SaaS, account system, billing, or mandatory cloud backend.
- No replacement for agent runtimes, vector databases, graph databases, issue
  trackers, or IDEs.
- No automatic canonical promotion, autonomous conflict resolution, hidden writes, or implicit subagent dispatch.
- No claim that the synthetic benchmark percentages generalize to every repository.
- No Docker-first installation or remote multi-tenant MCP service before v1.0.

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
| v0.8.0 | Human intent becomes a validated, token-budgeted, resumable work contract and clean retrieval projection. | Contract round-trip, context determinism, small-model, RAG, and migration gates are green. | Feature update, open questions, and explicit user alignment before publishing or v0.8.1. |
| v0.8.1 | Four Tier-1 harness profiles can execute and resume isolated work without silent capability degradation. | Conformance, worktree/claim safety, cross-harness resume, and multi-agent demo gates are green. | Feature update, open questions, and explicit user alignment before publishing or v0.9.0. |
| v0.9.0 | Reviewed knowledge can be written, promoted, compiled, exported, and refreshed with provenance and privacy controls. | Semantic-write, promotion, privacy, drift, RAG round-trip, and Owlib freshness gates are green. | Feature update, open questions, and explicit user alignment before publishing or v1.0. |
| v1.0 | Owledge is measurable, secure by default, supportable, and release-ready at realistic scale. | Security, scale, portability, CLI lifecycle, docs, evidence reconstruction, and final artifact gates are green. | Final feature update, post-v1 question register, and explicit user closeout before GA publication. |

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

Tickets: `OW-080-01`, `OW-080-02`, `OW-080-03`, `OW-080-04`, `OW-080-12`.

Outcome: ProjectManifest, ArtifactEnvelope, WorkContract, Backlog, RunState,
Checkpoint, GateResult, EvidenceManifest, and a default-off Autonomous Delivery Profile are versioned, validated, and migratable.

Gate: `G-080-A-CONTRACTS`.

### Phase 080-B - Context and small-model runtime

Tickets: `OW-080-05`, `OW-080-06`, `OW-080-07`.

Outcome: deterministic pack types, progressive disclosure, active-tool filtering,
and 4k/8k/16k budgets keep stored control-plane detail outside prompt context unless
needed.

Gate: `G-080-B-CONTEXT`.

### Phase 080-C - Retrieval projection, status, and migration

Tickets: `OW-080-08`, `OW-080-09`, `OW-080-10`.

Outcome: clean-body retrieval projections, a read-only status view, and safe preview
migration are available to real users.

Gate: `G-080-C-RETRIEVAL` and release gate `G-080-RC`.

## Version v0.8.1 - Tier-1 Agentic Coding

### Phase 081-A - Capability contract and Tier-1 adapters

Tickets: `OW-081-01`, `OW-081-02`, `OW-081-03`, `OW-081-04`, `OW-081-05`.

Outcome: Codex, Claude Code, OpenCode, Hermes, and generic MCP/CLI declare and
prove the same portable capability contract without pretending unsupported
hooks exist. Hermes' read-only capability proof begins in `OW-071-07` and its
full runtime orchestration conformance is completed in `OW-081-13`.

Gate: `G-081-A-ADAPTERS`.

### Phase 081-B - Git-safe concurrency and recovery

Tickets: `OW-081-06`, `OW-081-07`, `OW-081-08`, `OW-081-12`, `OW-081-13`.

Outcome: the optional autonomous-delivery skill, consent checks, claims, path scopes, worktrees, checkpoints, hooks, runtime adapters, and integration manifests support safe parallel execution and cross-harness resume.

Gate: `G-081-B-CONCURRENCY`.

### Phase 081-C - Scoped hub context and golden multi-agent journey

Tickets: `OW-081-09`, `OW-081-14`, `OW-081-10`.

Outcome: Owlib can compile explicitly scoped cross-project context; edge/local models receive constrained task capsules; and the golden journey proves interrupted work can resume in another Tier-1 harness.

Gate: `G-081-C-JOURNEY` and release gate `G-081-RC`.

## Version v0.9.0 - Trusted Writes and Knowledge Lifecycle

### Phase 090-A - Evidence, authority, and promotion

Tickets: `OW-090-01`, `OW-090-02`, `OW-090-03`.

Outcome: evidence is append-only, contradictions are visible, authority is explicit,
and canonical promotion requires policy and gate evidence.

Gate: `G-090-A-TRUST`.

### Phase 090-B - Semantic MCP writes and living documentation

Tickets: `OW-090-04`, `OW-090-05`, `OW-090-06`.

Outcome: scoped semantic writes, source-linked compiled documentation, and drift/impact
analysis are available without general filesystem mutation.

Gate: `G-090-B-WRITES`.

### Phase 090-C - RAG and Owlib freshness

Tickets: `OW-090-07`, `OW-090-08`, `OW-090-09`.

Outcome: generic JSONL and LightRAG adapters improve retrieval quality, while
incremental Owlib sync, tombstones, and project scopes prevent stale or mixed context.

Gate: `G-090-C-RAG` and release gate `G-090-RC`.

## Version v1.0 - Product Hardening and Release

### Phase 100-A - Security and scale

Tickets: `OW-100-01`, `OW-100-02`, `OW-100-03`.

Outcome: secret/PII handling, prompt-injection labels, permission manifests, and
10/1k/10k scale targets are published and enforced.

Gate: `G-100-A-HARDENING`.

### Phase 100-B - Evaluation and product lifecycle

Tickets: `OW-100-04`, `OW-100-05`, `OW-100-06`.

Outcome: portability, resume, false-pass, rework, install, upgrade, uninstall,
support, migration, and deprecation behavior are measurable and documented.

Gate: `G-100-B-PRODUCT`.

### Phase 100-C - v1 proof and artifact cut

Tickets: `OW-100-07`, `OW-100-08`, `OW-100-09`.

Outcome: English docs, case studies, final conformance, artifact installation, and an
evidence-only reconstruction prove the v1 promise.

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

- All tickets through `OW-100-10` are `done` with independent QA evidence and every version alignment decision is recorded.
- All version and final gates are green from documented clean states.
- Four Tier-1 runtime profiles achieve at least 95% declared contract equivalence on
  the same fixture; unsupported capabilities fail explicitly.
- Existing v0.7 benchmark fixture retains at least 80% token reduction per correct
  answer, zero privacy/stale failures, and no answer-quality regression.
- The 4B/8k profile completes the defined small-model golden tasks within budget.
- Raw frontmatter is excluded from embedding text; retrieval projections improve or
  preserve the published recall/ranking thresholds against the raw-Markdown baseline.
- A new user completes the vibecoding demo without maintainer help on supported OS
  fixtures.
- The evidence bundle reconstructs the complete golden journey without chat history.
- Wheel and sdist build, install, upgrade, uninstall, and fresh-project smoke tests pass
  from a clean release candidate.

## Post-v1 Deferred Concepts

- PI.dev runtime concept and optional long-running knowledge guardian.
- Add-on Decision Layer: provenance-preserving ingestion of external feedback,
  agent evaluations, and plan comparisons; independent model sparring and
  Project Hardening use shared metrics and owner-approved conclusions rather
  than automatic plan rewrites. Discovery plan:
  `internal/owledge/plans/add-on-decision-layer-discovery-plan.md`.
- Docker-first hub distribution and authenticated remote MCP.
- Hosted team sync, multi-tenant service, marketplace certification, and commercial
  features.

## Resume Rule

Read the execution control plane, select the first ready ticket whose dependencies are
done, and continue from its checkpoint. Never restart a completed phase. If evidence is
stale after later changes, reopen the smallest affected ticket and gate.
