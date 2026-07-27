---
title: "Owledge v1 Ticket Contracts"
date: "2026-07-16"
version: "1.0.0"
memory_id: "mem:owledge:global:owledge:task:v1-delivery-ticket-catalog"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "ticket_catalog"
status: "active"
visibility: "private"
data_class: "internal"
project: "owledge"
scope: "v0.7.1-v1.0"
semantic_title: "Owledge v1 delivery ticket catalog"
summary: "Normalized implementation contracts for every ticket in the autonomous Owledge v1 release train."
concept_tags: ["tickets", "v1-roadmap", "autonomous-delivery"]
stack_tags: ["markdown", "yaml", "python", "git"]
problem_patterns: ["ambiguous-tickets", "dependency-drift", "self-approval"]
architecture_patterns: ["ticket-dag", "selective-context-loading", "role-separated-qa"]
failure_modes: ["missing-negative-test", "unbounded-scope", "weak-acceptance"]
confidence: 0.95
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-16T00:00:00Z"
updated_at: "2026-07-18T00:00:00Z"
source_hash: ""
owners:
  - "release-orchestrator"
tags:
  - "tickets"
  - "qa-gates"
  - "roadmap"
reusable_lessons: []
edges: []
---

# Owledge v1 Ticket Contracts

This file is the compact ticket catalog referenced by `BACKLOG.yaml`. Load only the active ticket section plus the common execution contract.

## Common Execution Contract

For every ticket:

- Definition of ready: dependencies are `done`; referenced decisions are accepted; base SHA, branch, worktree, allowed paths, QA owner, and expected evidence path are recorded.
- Assignment: `owner_role`, distinct `qa_role`, estimated turns, dependencies, gate, and selective ticket path come from `BACKLOG.yaml`; an assignee must not self-approve.
- Context rule: load `GOAL.md`, `RUN-STATE.yaml`, `CONTROL-PLANE-POLICY.md`, and only the active ticket/gate sections via `python tools/validate_v1_delivery_plan.py --ticket-id <id>` and `--gate-id <id>`.
- Scope rule: change only `Allowed paths`. Ask the integration owner before scope overlap or contract changes.
- Verification: run the listed positive check plus a targeted negative/failure test. Record commands, versions, exit codes, artifacts, commit SHA, and limitations under `evidence/<ticket-id>/manifest.yaml`.
- Definition of done: acceptance criteria pass non-interactively, docs/contracts in scope are current, checkpoint and backlog agree, and an independent QA owner approves.
- Checkpoint: record last completed action, changed files, passed/failed commands, workspace/commit state, next exact action, assumptions, blockers, and prohibited shortcuts.
- Rollback: revert the cohesive ticket commit or disable the additive capability; migrations must retain a reversible preview or backup path.
- QA handoff: include attack/failure cases, residual risks, and the smallest cumulative gate affected.
- Alignment tickets: after a release RC/GA, create the required version update from `ALIGNMENT-PROTOCOL.md`, including complete finding/decision/question registers and next-version plan reflection; set the run state to `awaiting_user_alignment`, and stop. Only an explicit recorded user `approve`, `adjust`, or `defer` decision may resolve the ticket.

## v0.7.1 - Adoption, Truth, and Compatibility

### OW-071-01 - Normalize live work state

- Priority/dependencies: P0; none.
- Outcome: one live register accurately distinguishes shipped, open, superseded, and deferred work.
- Allowed paths: worker may edit `ROADMAP.md`, `docs/feedback-round-2026-06.md`,
  `docs/roadmap-ideas-2026-06.md`, `docs/v0.6.0-implementation-plan.md`,
  `docs/strategic-roadmap-2026-2027.md`,
  `internal/owledge/workpackages/owledge-v1-autonomous-delivery/LIVE-WORK-REGISTER.yaml`,
  `tools/validate_live_work_register.py`,
  `tests/unit/test_validate_live_work_register.py`,
  `tests/fixtures/live-work-register/`, and `evidence/OW-071-01/`.
  `BACKLOG.yaml`, `RUN-STATE.yaml`, central checklists, and release updates are
  orchestrator-only integration paths.
- Source set: the five named roadmap/feedback/legacy-plan documents above,
  `VERSION`, `pyproject.toml`, `CHANGELOG.md`, and the v0.7/v0.7.1 checklists
  referenced by those documents. New sources require an orchestrator decision.
- Implement: compile `LIVE-WORK-REGISTER.yaml` with exactly
  `shipped|open|superseded|deferred`; reconcile FB-001 through FB-021, v0.7
  checklists, Owlib status, adapter claims, and version evidence. Preserve
  history: `superseded` requires a replacement reference; `deferred` requires
  target release and reason; unchecked historical boxes are source evidence,
  not active work.
- Accept: every item has state, source, acceptance gap or shipped evidence,
  target release, owner role, and evidence link; every FB-001..FB-021 item
  appears exactly once; no active document contradicts `VERSION` or
  `pyproject.toml`; no historical unchecked box re-enters active scope.
- Verify/evidence: `python tools/validate_live_work_register.py --project-root .`;
  `python tools/validate_v1_delivery_plan.py`;
  `python -m unittest tests.unit.test_validate_live_work_register -v`;
  `python tools/owledge.py test public-docs --project-root .`;
  `evidence/OW-071-01/`.
- Negative QA: deliberately stale fixture state is detected; historical unchecked boxes do not re-enter the live backlog.

### OW-071-02 - Close v0.7 release-trust gaps

- Priority/dependencies: P0; `OW-071-01`.
- Outcome: retained flags, upgrade-note contracts, and final v0.7 artifacts have executable proof.
- Allowed paths: `tools/`, `tests/`, `.github/workflows/`, `CHANGELOG.md`, `docs/upgrade*`, release plans/checklists.
- Implement: complete or explicitly retract FB-019/020/021; remove dead flags or test dispatch; replace brittle upgrade-note assumptions with a validated contract.
- Accept: each retained CLI flag has a dispatch test; malformed upgrade notes fail; no unresolved P0/P1 v0.7 release finding remains.
- Verify/evidence: focused unit tests, `python tools/owledge.py test publish-readiness --project-root .`; `evidence/OW-071-02/`.
- Negative QA: missing `breaking` field and dead parser-only flags fail deterministically.

### OW-071-03 - Freeze token and retrieval regression baseline

- Priority/dependencies: P0; `OW-071-01`.
- Outcome: future releases cannot silently lose the v0.7 context-efficiency advantage.
- Allowed paths: `benchmarks/`, `addons/benchmark-kit/`, `docs/benchmark-kit.md`, `tests/`, release gates.
- Implement: version the legacy fixture and comparison contract; add sealed held-out journeys; gate answer quality, privacy, staleness, pollution, and at least 80% token-per-correct reduction; label the claim synthetic and fixture-bounded.
- Accept: three reference profiles and a held-out set remain reproducible; correctness/retrieval quality is reported separately from token efficiency; threshold or fixture changes require an explicit decision and new baseline version.
- Verify/evidence: Benchmark Kit CI and comparison commands; `evidence/OW-071-03/`.
- Negative QA: privacy leak, stale answer, quality drop, or 79.99% result fails.

### OW-071-13 - Classify and secure the local HTTP control-plane boundary

- Priority/dependencies: P0; `OW-071-01`.
- Outcome: the shipped `serve` surface has one truthful product status and
  cannot be mistaken for a production Team Hub.
- Allowed paths: `tools/owledge_core.py`, control-plane security tests,
  command/reference/security docs, capability registry, release gates.
- Implement: decide product/internal/prototype status; default to loopback-only
  unless an approved remote contract exists; remove sensitive health details;
  bind actor identity to tenant/customer/project authorization; publish and
  test an Endpoint x Role x Tenant matrix, including explicit administrator
  cross-tenant behavior; add versioned maximum body-size, request-timeout,
  concurrency, rate/abuse, and stable error-code bounds for the supported local
  profile; document TLS,
  token rotation/revocation, backup/restore, and deployment as unsupported or
  required future work.
- Accept: unsupported non-loopback bind fails closed; no unauthenticated local
  path disclosure; cross-tenant task/evidence/gate/promotion operations fail;
  every endpoint is covered by the authorization matrix; every documented
  bound has a boundary and over-limit fixture; public capability matrix labels
  the surface accurately.
- Verify/evidence: auth, tenant, health disclosure, remote bind, payload, and
  regression fixtures; security review; `evidence/OW-071-13/`.
- Negative QA: the existence of an admin token alone cannot authorize remote
  exposure; no docs call this a hosted, production, or team-sync service.
- Execution checkpoints: (1) capability/threat contract and failing fixtures;
  (2) loopback, health, tenant authorization, payload, timeout/concurrency/rate
  bounds, and stable errors; (3) docs, full negative matrix, independent
  security QA, and evidence manifest.

### OW-071-04 - Rewrite adoption-first English documentation

- Priority/dependencies: P0; `OW-071-02`, `OW-071-13`.
- Outcome: README and docs navigation explain why, when, benefits, boundaries,
  and the Owledge lifecycle before routing a beginner to installation.
- Allowed paths: `README.md`, `docs/README.md`, new English concept and
  navigation docs, public-doc tests, adoption fixtures.
- Implement: resolve category and default-path decisions; enforce a pre-install
  information budget; move maintainer detail below adoption; add an early
  lifecycle diagram; pair capabilities with outcomes; surface privacy/non-goals;
  define one canonical page per concern and keep every primary adoption route
  within two navigation clicks; establish `contracts/public-capabilities.json`
  as the versioned capability registry with schema and release-owner review;
  publish maturity as available, local experimental, preview, planned, or
  post-v1 with evidence; require external current-capability claims to record
  source date or retrieval date in the evidence record; preserve an explicit
  pre-install information budget so adoption docs cannot become a context dump.
- Accept: a five-second fixture identifies audience, problem, outcome,
  boundary, and next action; no install command precedes the mental model;
  every claim is current or explicitly labelled roadmap; Hermes-specific
  performance claims are not treated as current until fixture evidence exists.
- Verify/evidence: comprehension, claim-map, navigation, link, and lint checks;
  `evidence/OW-071-04/`.
- Negative QA: artifact inventory, repo layout, benchmark detail, or install
  syntax cannot displace the first-screen product explanation.

### OW-071-10 - Build the canonical Installation Hub and command contract

- Priority/dependencies: P0; `OW-071-04`.
- Outcome: a user or agent selects a complete supported recipe without mixing
  delivery mechanisms or assuming unavailable commands.
- Allowed paths: `docs/install/`, setup/upgrade/uninstall docs, README/docs
  routing, CLI help/manifests, extracted-command fixtures and tests.
- Implement: separate footprint, package delivery, runtime adapter, and
  optional capability; publish complete supported recipes with prerequisites,
  working directory, writes, output, verification, idempotency, recovery,
  upgrade, and uninstall; eliminate unexplained `uvx` to `owledge` transitions;
  generate per-preset compressed artifact size, installed CLI footprint, host
  project footprint, file count, folder purpose,
  canonical/private/generated ownership, rebuildability, and removal impact.
- Accept: each command chain runs from its documented clean state and links
  from top navigation; Principles-only reports zero host writes and N/A install
  footprint; command truth has one canonical owner.
- Verify/evidence: extracted-command smoke on Windows, macOS, and Linux;
  `evidence/OW-071-10/`.
- Negative QA: package recipes cannot require a checkout/persistent binary;
  source recipes cannot leave checkout/target roots ambiguous; unsupported
  runtime wiring cannot be labelled supported.

### OW-071-11 - Explain the lifecycle and core workflows

- Priority/dependencies: P0; `OW-071-04`.
- Outcome: beginners and agents can explain how project truth becomes scoped
  context, work, evidence, handoff, resume state, and reviewed knowledge.
- Allowed paths: concept/workflow docs, README/docs routing, Mermaid checks,
  templates/CLI references, adoption fixtures.
- Implement: canonical how-it-works page; read/write/privacy and
  canonical/candidate/generated boundaries; setup, context, planning,
  execution, evidence, review, handoff, resume, KB, and MCP workflows; glossary;
  prose fallbacks for diagrams; action-by-actor automation matrix with fixed
  `Action`, `Actor`, `Trigger`, `Default`, `Side effect`, `Authority`, and
  `Recovery` columns, covering
  instructions, harness discovery, hooks, skills, CLI, MCP, curator, sync, and
  background processes; canonical best-practice loop with task variants.
- Accept: every diagram node maps to a real artifact/current command and a
  beginner can narrate the lifecycle and locate the files.
- Verify/evidence: traceability, diagram validation, narration, and
  architecture/privacy review; `evidence/OW-071-11/`.
- Negative QA: Owledge cannot be presented as a runtime, hosted store,
  automatic truth engine, automatic promoter, or required vector database.

### OW-071-12 - Separate skills and make agent integrations executable

- Priority/dependencies: P0; `OW-071-04`.
- Outcome: humans and agents distinguish policy skills, workflow skills,
  runtime adapters, read-only MCP, and add-ons and execute a verified path.
- Allowed paths: skill READMEs/metadata, agent/harness/integration and plugin
  docs, instruction templates, runtime and agent-choice fixtures/tests.
- Implement: public registry with trigger, IO, effects, dependencies, runtime
  support, and stability; instruction/skill/hook precedence; exact verified
  runtime recipes; agent preflight, writes, report, recovery, and stop contract;
  skill invocation and reviewed-promotion diagram; official happy-path skill
  order and explicit small-task, multi-agent, KB, and advanced variants; make
  the runtime-independent `owledge-contract` the Principles-only default and
  exclude skills that would require runtime-dependent rewrites; state that the
  v0.7.1 MCP integration profile is read-only and that agents must not assume a
  write path; ship `owledge-long-horizon-delivery` with bounded
  `mvp-sparring`, `version-steering`, ticket, gate, and recovery modes; install
  Codex repository mirrors under `.agents/skills/`, keep root `skills/` as the
  Owledge source/vendor tree, use plugin-local `skills/` roots where declared,
  and state explicitly that `.owledge/skills/` is not automatic discovery.
- Accept: fixture agents select the correct path and prove it in the host
  project; a fresh init contains hash-matching root and `.agents/skills`
  copies; missing/drifting mirrors are diagnosed; manual and experimental
  steps are bounded explicitly.
- Verify/evidence: agent-choice scenarios, host integration smoke, runtime
  conformance review; `evidence/OW-071-12/`.
- Negative QA: implied plugin folders, maintainer-repo checks as host proof,
  implied write-enabled MCP, or hidden canonical mutation fails.

### OW-071-14 - Define adoption presets and Global/Hub maturity

- Priority/dependencies: P0; `OW-071-04`.
- Outcome: users can choose a supported adoption preset and distinguish local
  personal context, static maps, local cross-project indexing, and future team
  synchronization.
- Allowed paths: English adoption/global/hub docs, README/docs routing,
  capability registry, preset decision fixtures/tests.
- Implement: presets for no-install principles, manual mini-kit, existing repo,
  standalone project, Markdown KB, runtime adapter, private global layer, and
  cross-project power-user use; separate `global-memory`, Cross-Project Hub
  Kit, Owlib, local HTTP prototype, and future Team Hub; show maturity, value,
  authority, automation, privacy, prerequisites, limits, and upgrade path.
  Define Owlib's future central role for reviewed cross-project learnings,
  parallel extraction, PI intelligence, and agent maintenance, while keeping
  it local/explicit before v1; label the multi-tenant Team Hub and Git/CI Sync
  Layer post-v1 with no v1 dependency.
- Accept: users select a preset without source-code interpretation; no local
  capability is presented as automatic remote team sync; current Owlib claims
  cannot be labelled `available` or `current` until `G-071-C-COMPAT` is green
  and otherwise remain explicitly labelled preview/legacy.
- Verify/evidence: preset-choice scenarios, maturity/evidence traceability,
  power-user and architecture review; `evidence/OW-071-14/`.
- Negative QA: global link, Hub Kit, Owlib, HTTP serve, remote MCP, and hosted
  team sync cannot be used as synonyms or share an unsupported Ready claim.

### OW-071-05 - Ship the vibecoding golden demo v1

- Priority/dependencies: P0; `OW-071-10`, `OW-071-11`, `OW-071-12`, `OW-071-14`.
- Outcome: a user tries one feature request and sees scoped context, evidence, resume, and benefit.
- Allowed paths: `examples/`, `docs/`, `addons/launch-demo-kit/`, demo fixtures/tests.
- Implement: 30-second no-install mental-model/example proof with zero disk
  writes, one visible representative result, and an unambiguous success signal;
  package-only
  five-minute scratch journey with expected output, verification, and reset;
  fresh-session/second-agent resume proof using documented entrypoints; keep
  source-only add-on demo separate and labelled; bounded before/after explanation.
- Accept: all three proofs meet their time/scope contracts without API key or
  maintainer interpretation; the 30-second proof performs zero writes and names
  its visible result and success signal; package-only proof needs no checkout; fresh agent
  resumes without chat; generated artifacts link to sources.
- Verify/evidence: scripted demo smoke on three OS fixtures; `evidence/OW-071-05/`.
- Negative QA: rerun is idempotent and missing optional runtime degrades with a clear message.

### OW-071-06 - Migrate Owlib to the v0.7 project contract

- Priority/dependencies: P0; `OW-071-02`.
- Outcome: Owlib `0.2` reads `OWLEDGE.md` and `.owledge/` safely while supporting explicit legacy migration.
- Allowed paths: `owlib/`, Owlib docs/tests, package metadata.
- Implement: current-layout discovery, reviewed-only default, compatibility reader, deprecation warning, no raw-session import, stable source IDs/hashes.
- Accept: current and legacy fixtures sync; current layout is default; unsafe shared and unreviewed records are rejected with reasons.
- Verify/evidence: Owlib unit/quality/benchmark suites; `evidence/OW-071-06/`.
- Negative QA: traversal, missing project entrypoint, unsafe shared data, and mixed legacy/current ambiguity fail safely.

### OW-071-07 - Hermes required Tier-1 read-only profile

- Priority/dependencies: P0; `OW-071-03`.
- Outcome: Hermes proves the minimal required Tier-1 read-only Owledge MCP
  profile locally or on a VPS without implying unsupported write authority.
- Allowed paths: `tools/owledge_mcp.py`, Hermes adapter/skill paths, runtime conformance fixtures, English integration docs/tests.
- Implement: installation/routing skill, project-root binding, tool allowlist, MCP reload/test instructions, memory-boundary guidance, compact tool descriptions; allow an initial entrypoint/search/context-pack smoke to reduce tool-choice risk, but do not treat that starter mode as the full ticket proof.
- Accept: Hermes can read entrypoint, search, build context pack, list tasks/reviews; no write tool exists; repository path errors are clear; Hermes memory/compression remains separate from Owledge project artifacts; Hermes-specific token/performance claims remain candidate until fixture evidence exists.
- Verify/evidence: protocol smoke plus Hermes fixture transcript; `evidence/OW-071-07/`.
- Negative QA: unbound project, path escape, disabled tool, and unavailable MCP server fail explicitly.

### OW-071-08 - Cut v0.7.1 release candidate

- Priority/dependencies: P0; `OW-071-03`, `OW-071-05`, `OW-071-06`, `OW-071-07`.
- Outcome: clean wheel/sdist and release notes prove adoption, compatibility, and regression gates.
- Allowed paths: `VERSION`, `pyproject.toml`, `CHANGELOG.md`, release workflows/docs, package manifests.
- Implement: version bump, migration notes, artifact build, wheel-based `uvx` smoke, install/upgrade smoke, clean-state evidence.
- Accept: `G-071-RC` passes from a clean integration branch; no generated private path enters artifacts.
- Verify/evidence: build, twine, wheel/sdist inspection, `uvx` quickstart/doctor; `evidence/OW-071-08/`.
- Negative QA: dirty source state or mismatched version blocks promotion.

### OW-071-09 - Align v0.7.1 with the product owner

- Priority/dependencies: P0; `OW-071-08`.
- Outcome: the product owner receives an evidence-linked v0.7.1 feature update, all unresolved questions, and an explicit choice before publishing or beginning v0.8.0.
- Allowed paths: `internal/owledge/workpackages/owledge-v1-autonomous-delivery/release-updates/`, `RUN-STATE.yaml`, `BACKLOG.yaml`, `TRACEABILITY.md`, release evidence/manifests.
- Implement: create `release-updates/v0.7.1.md` from `ALIGNMENT-PROTOCOL.md`; reconcile planned versus shipped scope, include complete implementation finding/decision/question registers, reflect affected v0.8.0 tickets and gates as keep/amend/defer/drop, present the review in chat, and set the run state to `awaiting_user_alignment`.
- Accept: `G-071-RC` is green; the update contains all eleven required headings and no untracked claim, finding, or decision; proposed plan amendments validate; user `approve`, `adjust`, or `defer` is recorded with scope/constraints; only `approve` unlocks v0.8.0.
- Verify/evidence: `python tools/validate_v1_delivery_plan.py`; required-heading check; update, decision, and evidence links under `evidence/OW-071-09/`.
- Negative QA: omitted finding/question/decision, absent next-plan reflection, automatic next-ticket selection, or autonomous publish/tag leaves the ticket blocked.

## v0.8.0 - Portable Control Plane and Retrieval Foundation

### OW-080-01 - Accept contract architecture and migrations

- Priority/dependencies: P0; `OW-071-09`.
- Outcome: accepted ADRs fix source-of-truth, schema versioning, lifecycle, extension, authority, and migration rules.
- Allowed paths: `docs/architecture*`, `internal/owledge/decisions/`, schemas overview, plan references.
- Implement: ADRs for contract set, Markdown/YAML boundary, unknown-field preservation, ID stability, status machine, compatibility window.
- Accept: no later schema ticket requires an unresolved product decision; reversible local details stay outside ADRs.
- Verify/evidence: architecture review and contract decision matrix; `evidence/OW-080-01/`.
- Negative QA: database-as-canonical, automatic promotion, and destructive migration designs are rejected.

### OW-080-02 - Implement ProjectManifest and ArtifactEnvelope v1

- Priority/dependencies: P0; `OW-080-01`.
- Outcome: project identity, modes, privacy, adapters, gates, artifact lifecycle, provenance, and typed edges validate consistently.
- Allowed paths: `templates/`, `internal/owledge/templates/`, `skills/`, schema/tool/test/docs paths.
- Implement: JSON Schemas, defaults, examples, upgrade mapping, extension-field preservation; add the owner-approved transferability model as separate fields from audience and privacy: `audience_ids` for target roles/lenses, `transferability: universal|partial|local` for reuse outside the origin context, optional `applies_to` for partial scope, and existing `visibility`/`data_class` for privacy.
- Accept: round-trip preserves stable IDs, typed edges, unknown extensions, visibility, data class, audience IDs, transferability, and applies-to scope.
- Verify/evidence: schema positive/negative and migration tests; `evidence/OW-080-02/`.
- Negative QA: invalid lifecycle, missing identity, unsafe visibility/data-class combination, overloaded audience/privacy fields, invalid transferability value, and ID mutation fail.

### OW-080-03 - Implement WorkContract, Backlog, and RunState v1

- Priority/dependencies: P0; `OW-080-01`.
- Outcome: intent becomes a machine-readable dependency DAG with scopes, evidence, gates, handoff, and live state.
- Allowed paths: planning templates/skills, schemas, `tools/owledge_core.py`, CLI/tests/docs.
- Implement: ticket compiler/validator, status transitions, dependency readiness, WIP rules, atomic state updates; encode goal, target user, smallest useful outcome, observable success signal, MVP cutline, definition of done, QA gates, out-of-scope, evidence, handoff, unresolved questions, and explicit roadmap/idea dispositions as first-class WorkContract fields.
- Accept: task cannot reach accepted/done without required gate/evidence refs; prose-only completion is rejected; cyclic or missing dependencies fail.
- Verify/evidence: state-machine, DAG, WIP, and atomic-write tests; `evidence/OW-080-03/`.
- Negative QA: prose-only completion, cycle, double claim, and partial state update fail.

### OW-080-04 - Implement Checkpoint, GateResult, and EvidenceManifest v1

- Priority/dependencies: P0; `OW-080-01`.
- Outcome: interrupted work can be resumed and gates can be independently reproduced.
- Allowed paths: execution schemas/templates, core/CLI/tests/docs.
- Implement: checkpoint hashes, command results, side-effect/idempotency fields, gate thresholds, reviewer, limitations, evidence manifest.
- Accept: checkpoint identifies exact next action and tested commit; gate refuses missing/stale evidence.
- Verify/evidence: recovery and evidence-integrity fixtures; `evidence/OW-080-04/`.
- Negative QA: mismatched input hash, missing exit code, self-only QA, and stale tested commit fail.

### OW-080-12 - Define the optional Autonomous Delivery Profile v1

- Priority/dependencies: P0; `OW-080-02`, `OW-080-03`, `OW-080-04`.
- Outcome: small work stays single-agent by default, while larger work can use a runtime-neutral, consent-first delivery profile.
- Allowed paths: execution schemas/templates, planning tools/CLI/tests/docs, `internal/owledge/workpackages/`.
- Implement: default-off profile fields for blockers, subagent eligibility, orchestrator, model profile, QA, Red Team, approval mode, Git lane, and parallelism; render dependency links from the canonical backlog; record a risk brief and consent state without dispatching a runtime.
- Accept: parsing or dry-run planning cannot spawn an agent or create a worktree; `subagent: true` is eligibility only; unknown model, missing consent, overlapping lane, or raw credential fails closed.
- Verify/evidence: profile round-trip, default-off, consent, dependency-link, and negative fixtures; `evidence/OW-080-12/`.
- Negative QA: implicit spawn, generic write fallback, same-context QA, unsupported profile, or unapproved high-risk ticket is rejected.
### OW-080-05 - Build deterministic Context Compiler v1

- Priority/dependencies: P0; `OW-080-02`, `OW-080-03`, `OW-080-04`, `OW-080-12`.
- Outcome: bootstrap, task, reviewer, handoff, and release packs explain inclusion/exclusion and respect budgets.
- Allowed paths: context-pack core/CLI, schemas, fixtures, tests, docs.
- Implement: deterministic ordering/digest, typed selection reasons, privacy/staleness filters, dropped-source list, pack version; add a bounded pre-plan capsule that inspects relevant idea, concept, decision, pattern, lesson, and roadmap metadata before plan creation and expands only candidates that can change the MVP cutline; distinguish source freshness from review freshness and enforce explicit context budgets without silent omission.
- Accept: identical inputs produce identical pack and digest; every included/excluded source has a reason; the pre-plan capsule records required-now, dependency, roadmap, idea-candidate, or reject/defer disposition without auto-promoting candidates; stale source, stale review, privacy exclusion, and over-budget exclusion are distinguishable.
- Verify/evidence: golden pack tests and v0.7 regression fixture; `evidence/OW-080-05/`.
- Negative QA: private, stale, unrelated, or over-budget source cannot enter silently.

### OW-080-06 - Add progressive disclosure and active-tool profiles

- Priority/dependencies: P1; `OW-080-05`.
- Outcome: agents start from synopsis and references, expanding bodies/evidence/tools only when required.
- Allowed paths: context compiler, MCP/adapter manifests, quick-read schemas, tests/docs.
- Implement: freshness-linked synopses, expansion API, task-class tool allowlists, concise descriptions.
- Accept: synopsis never claims canonical authority; stale synopsis is flagged; unused tools stay inactive.
- Verify/evidence: synopsis freshness and tool-selection fixtures; `evidence/OW-080-06/`.
- Negative QA: body change without synopsis refresh and unknown tool capability fail.

### OW-080-07 - Establish small-model compatibility profiles

- Priority/dependencies: P0; `OW-080-05`, `OW-080-06`.
- Outcome: 4k, 8k, 16k, and standard profiles reserve context for reasoning, tools, and output.
- Allowed paths: benchmark kits, context profiles, adapter config, tests/docs.
- Implement: hard pack budgets, 4B/8k Tier-1 tasks, structured-output validation/retry, tool-count limits, multi-hop ceilings.
- Accept: Tier-1 small model completes defined planning/retrieval/resume tasks within budget; thresholds cover tool-selection accuracy, contract-valid output, retries, completion, privacy/staleness, and false gate passes.
- Verify/evidence: local small-model matrix with prompt/tool schemas, deterministic fallback tests, and per-metric results; `evidence/OW-080-07/`.
- Negative QA: wrong tool, oversized pack, invalid structured result, retry loop, false acceptance, or hidden model downgrade fails.

### OW-080-08 - Build clean RAG Retrieval Projection v1

- Priority/dependencies: P0; `OW-080-02`, `OW-080-05`.
- Outcome: embedding text contains semantic title, summary, and clean section body while governance metadata stays separate.
- Allowed paths: RAG/export core, schemas, fixtures, benchmark/docs/tests.
- Implement: heading-aware chunks, boilerplate/frontmatter removal, dedupe, source hash/version/tombstone metadata, typed-edge hints.
- Accept: raw frontmatter tokens are absent from embedding text; IDs, policy, source, freshness, and edges remain metadata.
- Verify/evidence: raw-vs-projection retrieval evaluation; `evidence/OW-080-08/`.
- Negative QA: duplicate compiled/source chunks, private chunk, stale hash, and template boilerplate fail.

### OW-080-09 - Add status view and preview migration

- Priority/dependencies: P1; `OW-080-03`, `OW-080-04`.
- Outcome: users inspect work state and preview legacy migration without mutation.
- Allowed paths: CLI/core, templates, migration tools, tests/docs.
- Implement: `status`/board read view, `migrate --dry-run`, patch/manifest output, collision report, explicit apply mode.
- Accept: read view does not mutate; preview lists every proposed write and never-touch file; apply is idempotent.
- Verify/evidence: 1k-ticket performance plus migration fixtures; `evidence/OW-080-09/`.
- Negative QA: edited template collision, ambiguous legacy layout, and second apply do not overwrite silently.

### OW-080-10 - Cut v0.8.0 release candidate

- Priority/dependencies: P0; `OW-080-07`, `OW-080-08`, `OW-080-09`.
- Outcome: portable contracts, context efficiency, small models, retrieval projection, and migration ship together.
- Allowed paths: version/changelog/workflows/release docs/package manifests.
- Implement: cumulative gates, contract fixtures, migration notes, artifacts, wheel-based smoke.
- Accept: `G-080-RC` passes from clean state and v0.7 legacy regression remains green.
- Verify/evidence: release matrix; `evidence/OW-080-10/`.
- Negative QA: schema/version mismatch or missing migration path blocks release.

### OW-080-11 - Align v0.8.0 with the product owner

- Priority/dependencies: P0; `OW-080-10`.
- Outcome: the product owner receives an evidence-linked v0.8.0 feature update and decides whether the portable control plane and retrieval foundation may publish and unlock v0.8.1.
- Allowed paths: `internal/owledge/workpackages/owledge-v1-autonomous-delivery/release-updates/`, `RUN-STATE.yaml`, `BACKLOG.yaml`, `TRACEABILITY.md`, release evidence/manifests.
- Implement: create `release-updates/v0.8.0.md` from `ALIGNMENT-PROTOCOL.md`; reconcile planned versus shipped scope, include contract/migration impact, small-model and retrieval evidence, complete finding/decision/question registers, and a keep/amend/defer/drop reflection for affected v0.8.1 tickets and gates; present it in chat and set the run state to `awaiting_user_alignment`.
- Accept: `G-080-RC` is green; the update contains all eleven required headings and no untracked claim, finding, or decision; proposed plan amendments validate; user `approve`, `adjust`, or `defer` is recorded with scope/constraints; only `approve` unlocks v0.8.1.
- Verify/evidence: `python tools/validate_v1_delivery_plan.py`; required-heading check; update, decision, and evidence links under `evidence/OW-080-11/`.
- Negative QA: omitted migration limitation or finding, absent next-plan reflection/decision, automatic next-ticket selection, or autonomous publish/tag leaves the ticket blocked.

## v0.8.1 - Tier-1 Agentic Coding

### OW-081-01 - Define AdapterManifest and conformance protocol

- Priority/dependencies: P0; `OW-080-11`.
- Outcome: adapters declare detect/install/inject/capture/execute/resume/health/cleanup, versions, permissions, limits, and degradation.
- Allowed paths: runtime conformance add-on, schemas, adapter templates, tests/docs.
- Implement: capability schema, negotiation result, fixture protocol, support-tier rules; define optional pre-plan lifecycle capabilities for scoped idea/concept lookup, MVP-cutline handoff, roadmap/idea capture, and explicit unsupported degradation without requiring background writes.
- Accept: undeclared capability cannot run; unsupported feature returns explicit structured result; adapters cannot claim automatic pre-plan inspection or durable routing unless they pass the shared fixtures.
- Verify/evidence: manifest and negative compatibility suite; `evidence/OW-081-01/`.
- Negative QA: version mismatch, missing permission, or false capability claim fails.

### OW-081-02 - Codex Tier-1 adapter

- Priority/dependencies: P1; `OW-081-01`.
- Outcome: Codex bootstrap, context, task, checkpoint, handoff, hooks where available, and cleanup pass conformance.
- Allowed paths: `.codex/`, Codex plugin/skill/fixtures, runtime docs/tests.
- Implement: compact AGENTS/skill bridge, `.agents/skills/` discovery verification, MCP/CLI routing, permission mapping, bounded pre-plan capsule handoff, and fixture transcript.
- Accept: Codex completes common conformance fixture with source-linked outputs.
- Verify/evidence: Tier-1 suite; `evidence/OW-081-02/`.
- Negative QA: missing hook is declared unsupported rather than silently skipped.

### OW-081-03 - Claude Code Tier-1 adapter

- Priority/dependencies: P1; `OW-081-01`.
- Outcome: Claude Code plugin hooks and skills pass the common contract.
- Allowed paths: `plugins/owledge-cowork/`, Claude fixtures, runtime docs/tests.
- Implement: lifecycle validation, compact routing, plugin skill discovery, tool/scoped write mapping, bounded pre-plan capsule handoff, and fixture transcript.
- Accept: same artifacts and lifecycle semantics as other Tier-1 profiles.
- Verify/evidence: Tier-1 suite; `evidence/OW-081-03/`.
- Negative QA: hook failure surfaces at session close and cannot mark ticket done.

### OW-081-04 - OpenCode Tier-1 adapter

- Priority/dependencies: P0; `OW-081-01`.
- Outcome: OpenCode bootstrap, context, task, checkpoint, handoff, supported
  hooks, and cleanup pass the common contract.
- Allowed paths: OpenCode adapter/skill/fixtures, runtime docs/tests.
- Implement: pinned install/setup, capability manifest, compact instruction
  layer, context and resume wiring, bounded pre-plan capsule handoff,
  health/cleanup, and explicit degradation.
- Accept: OpenCode completes the common conformance fixture with source-linked
  outputs and no hidden canonical writes.
- Verify/evidence: pinned OpenCode fixture/conformance transcript;
  `evidence/OW-081-04/`.
- Negative QA: instruction-path mismatch, disabled capability, unsupported hook,
  and unavailable integration fail clearly.

### OW-081-05 - Generic MCP/CLI portable baseline adapter

- Priority/dependencies: P1; `OW-081-01`.
- Outcome: any capable harness can use the same versioned read/control contract without runtime-specific files.
- Allowed paths: MCP/CLI server, generic adapter fixtures, docs/tests.
- Implement: protocol-compliant surface, capability discovery, JSON output, stdio lifecycle, project binding, and a read-only pre-plan capsule endpoint with explicit promotion/write boundaries.
- Accept: reference client passes common conformance suite.
- Verify/evidence: protocol and CLI fixtures; `evidence/OW-081-05/`.
- Negative QA: malformed JSON-RPC, unknown project, and tool mismatch fail without server crash.

### OW-081-06 - Implement claims, path scopes, and worktree planner

- Priority/dependencies: P0; `OW-080-03`, `OW-081-01`.
- Outcome: independent work receives explicit claim, branch/worktree, allowed paths, base SHA, merge order, and TTL.
- Allowed paths: workpackage/claim schemas, Git helper core/CLI, tests/docs.
- Implement: dry-run worktree plan, overlap detection, advisory lease, ownership journal, no direct integration-branch worker writes; treat single-writer/write-claim policy as a claims-and-scope protocol before any MCP write lock.
- Accept: eight non-overlapping fixture workers plan cleanly; overlap requires owner decision; no worker receives write authority without explicit claim, allowed paths, base SHA, TTL, and merge order.
- Verify/evidence: Git fixture suite; `evidence/OW-081-06/`.
- Negative QA: overlapping glob, stale base, dirty target, invalid branch, and expired claim block dispatch.

### OW-081-07 - Implement checkpoint reconciliation and cross-harness resume

- Priority/dependencies: P0; `OW-080-04`, `OW-081-06`.
- Outcome: kill/retry at every checkpoint avoids duplicate canonical records and side effects.
- Allowed paths: checkpoint/resume core, adapter fixtures, tests/docs.
- Implement: input/output hashes, idempotency keys, side-effect journal, reconciliation status, resume pack.
- Accept: second Tier-1 harness resumes exact work from checkpoint without chat history.
- Verify/evidence: kill/retry and harness-switch matrix; `evidence/OW-081-07/`.
- Negative QA: hash mismatch or uncertain external side effect blocks automatic resume.

### OW-081-08 - Add runtime hooks and integration manifest

- Priority/dependencies: P1; `OW-081-02`, `OW-081-03`, `OW-081-04`, `OW-081-05`, `OW-081-07`.
- Outcome: supported hooks validate mutations and an integration manifest records commits, scopes, gates, reviews, conflicts, and risks.
- Allowed paths: adapter hooks, integration schemas, CLI/tests/docs.
- Implement: post-tool validation, stop/session summary, explicit unsupported warnings, deterministic merge manifest.
- Accept: invalid ticket edit cannot pass session close; integration order is reproducible.
- Verify/evidence: hook and merge fixtures; `evidence/OW-081-08/`.
- Negative QA: missing evidence, failed hook, scope conflict, or unreachable commit blocks integration.

### OW-081-12 - Ship the optional autonomous-delivery skill

- Priority/dependencies: P1; `OW-080-12`, `OW-081-01`, `OW-081-06`, `OW-081-08`.
- Outcome: one portable skill assesses ticket risk, proposes lanes and models, explains risks, and requests user consent before a runtime is allowed to act.
- Allowed paths: `skills/owledge-autonomous-delivery/`, plugin skill entrypoints, runtime docs, fixtures/tests, workpackage templates.
- Implement: small/medium/high-risk classifier, phase/per-ticket approval flow, model-profile guidance, isolated Worker/QA/Red-Team handoff rules, Git-lane checklist, risk brief, and safe single-agent fallback.
- Accept: the skill starts with recommendation rather than execution; small tickets stay simple; high-risk tickets cannot dispatch without fresh approval; each runtime receives a compact, explicit capability boundary.
- Verify/evidence: classifier, consent, capability-degradation, and lane-isolation fixtures; `evidence/OW-081-12/`.
- Negative QA: implicit invocation, automatic spawn, omitted risk, same-context QA, or claimed unsupported runtime capability fails.

### OW-081-13 - Add optional runtime orchestration adapters

- Priority/dependencies: P1; `OW-081-12`.
- Outcome: Codex, Claude Code, OpenCode, Hermes, and generic MCP/CLI can
  consume the approved delivery plan without making any runtime a Core
  dependency.
- Allowed paths: runtime adapters, integration manifests, CLI/tests/docs, adapter fixtures.
- Implement: read-only `execution plan` dry-run, model-profile resolution, consent verification, worktree/branch/merge manifests, explicit capability/degradation results, `/goal` mapping as a Codex adapter, and harness-specific pre-plan hooks that request the deterministic idea/concept capsule before new feature planning and return roadmap/idea dispositions for owner approval.
- Accept: adapters never launch externally while planning; pre-plan hooks are scoped, observable, and fail visibly without inventing context or writing automatically; approved non-overlapping lanes can be proposed; unsupported features degrade visibly and safely; integration writes remain owned by the integration role.
- Verify/evidence: cross-runtime dry-run, consent, worktree, merge-manifest, and degradation fixtures; `evidence/OW-081-13/`.
- Negative QA: no consent, overlap, direct integration write, unsupported model/runtime, or hidden external launch blocks dispatch.

### OW-081-14 - Add the edge/local-model delivery profile

- Priority/dependencies: P0; `OW-080-07`, `OW-081-12`, `OW-081-13`.
- Outcome: constrained local models receive compact task capsules and deterministic guardrails instead of excessive context or unsafe authority.
- Allowed paths: context profiles, adapter configuration, benchmark fixtures, deterministic validators, docs/tests.
- Implement: `edge_small` capability boundary, task-capsule format, hard budgets, progressive disclosure, unsupported-task responses, offline fixtures, and one real local-model smoke protocol.
- Accept: edge models can perform declared bounded tasks without full-plan injection; deterministic validators catch malformed output; unsupported architecture, merge, security, and cross-project actions are refused clearly.
- Verify/evidence: 4B-class local-model smoke run plus budget, structured-output, false-pass, and fallback fixtures; `evidence/OW-081-14/`.
- Negative QA: oversized context, hidden model downgrade, improvised unsupported action, false acceptance, or missing real-model evidence blocks the v0.8.1 claim.
### OW-081-09 - Add scoped Owlib retrieval and hub context packs

- Priority/dependencies: P1; `OW-071-06`, `OW-080-05`, `OW-080-11`.
- Outcome: Owlib queries current project plus explicit allowlisted projects and explains source selection.
- Allowed paths: `owlib/`, hub skills/MCP/docs/tests.
- Implement: `--projects`, exclusions, scope profiles, project-filter-first retrieval, context-pack budget/digest, source reasons.
- Accept: default never scans all projects; output identifies project, source, freshness, review, and exclusion reasons.
- Verify/evidence: cross-project privacy/relevance fixtures; `evidence/OW-081-09/`.
- Negative QA: unauthorized project ID, empty scope, and mixed private/shared context fail safely.

### OW-081-10 - Prove multi-agent golden journey and cut v0.8.1

- Priority/dependencies: P0; `OW-081-08`, `OW-081-09`, `OW-081-12`, `OW-081-13`, `OW-081-14`.
- Outcome: plan, parallel dispatch, deliberate interruption, cross-harness resume, failed review, correction, integration, and source-linked report run end to end.
- Allowed paths: golden fixtures/demo, conformance kit, release/version/docs/workflows.
- Implement: deterministic journey using all Tier-1 profiles, clean artifact build, public support matrix.
- Accept: no clobbered files, silent degradation, duplicate writes, or chat dependency; `G-081-RC` passes.
- Verify/evidence: full journey and release artifact matrix; `evidence/OW-081-10/`.
- Negative QA: overlap and missing test evidence deliberately fail before recovery.

### OW-081-11 - Align v0.8.1 with the product owner

- Priority/dependencies: P0; `OW-081-10`.
- Outcome: the product owner receives an evidence-linked Tier-1 agentic-coding update and decides whether the adapter release may publish and unlock v0.9.0.
- Allowed paths: `internal/owledge/workpackages/owledge-v1-autonomous-delivery/release-updates/`, `RUN-STATE.yaml`, `BACKLOG.yaml`, `TRACEABILITY.md`, release evidence/manifests.
- Implement: create `release-updates/v0.8.1.md` from `ALIGNMENT-PROTOCOL.md`; reconcile planned versus shipped scope, include profile conformance, Hermes boundary, multi-agent journey, known degradation, complete finding/decision/question registers, and a keep/amend/defer/drop reflection for affected v0.9.0 tickets and gates; present it in chat and set the run state to `awaiting_user_alignment`.
- Accept: `G-081-RC` is green; the update contains all eleven required headings and no untracked claim, finding, or decision; proposed plan amendments validate; user `approve`, `adjust`, or `defer` is recorded with scope/constraints; only `approve` unlocks v0.9.0.
- Verify/evidence: `python tools/validate_v1_delivery_plan.py`; required-heading check; update, decision, and evidence links under `evidence/OW-081-11/`.
- Negative QA: untested Tier-1 claim, omitted degradation/finding, absent next-plan reflection/decision, automatic next-ticket selection, or autonomous publish/tag leaves the ticket blocked.

## v0.9.0 - Trusted Writes and Knowledge Lifecycle

### OW-090-01 - Implement append-only Evidence Ledger and authority policy

- Priority/dependencies: P0; `OW-081-11`.
- Outcome: claims trace to source, run, commit, test, reviewer, and explicit authority/supersession rules.
- Allowed paths: evidence/authority schemas, core/CLI/tests/docs.
- Implement: append-only events, stable refs, code/ADR/issue/memory conflict policy, tamper/digest checks.
- Accept: public claim can be reconstructed and contradictions remain visible.
- Verify/evidence: ledger and authority fixtures; `evidence/OW-090-01/`.
- Negative QA: event mutation, broken source ref, and ambiguous authority block current status.

### OW-090-02 - Implement reviewed promotion lifecycle

- Priority/dependencies: P0; `OW-090-01`.
- Outcome: candidate, reviewed, canonical, superseded/rejected transitions are explicit, reversible, and evidenced.
- Allowed paths: promotion core/schemas/CLI/templates/tests/docs.
- Implement: promotion request, reviewer separation, contradiction link, supersession, policy profile, rollback.
- Accept: no agent or full-access profile promotes without required gate and audit record.
- Verify/evidence: lifecycle matrix; `evidence/OW-090-02/`.
- Negative QA: self-approval, missing sanitization, private-to-shared transition, and stale evidence fail.

### OW-090-03 - Enforce end-to-end privacy ingestion policy

- Priority/dependencies: P0; `OW-090-01`.
- Outcome: consent, scan allowlist, data class, redaction, retention, and export policies apply before retrieval or sharing.
- Allowed paths: privacy/config schemas, ingest/export core, fixtures/tests/docs.
- Implement: deny-by-default external scope, per-project consent, redaction results, negative corpus.
- Accept: private, confidential, unsanitized, unreviewed, and disallowed-project records never enter shared output.
- Verify/evidence: privacy attack corpus; `evidence/OW-090-03/`.
- Negative QA: prompt relevance cannot override privacy policy.

### OW-090-04 - Add semantic write-enabled MCP

- Priority/dependencies: P0; `OW-090-02`, `OW-090-03`.
- Outcome: MCP supports create candidate, append evidence, claim/release work, checkpoint, handoff, and promotion request under policy.
- Allowed paths: MCP server, semantic write service, schemas, tests/docs.
- Implement: capability scopes, project binding, locks/idempotency, dry run, audit event, structured result; no arbitrary write tool; support candidate creation and experience/evidence append only as semantic contract operations with target identity and provenance.
- Accept: every write maps to a contract transition and evidence event; read-only remains default profile; generic `log()`-style writes and direct canonical mutation are unavailable.
- Verify/evidence: protocol/security/idempotency suite; `evidence/OW-090-04/`.
- Negative QA: traversal, symlink escape, confused-deputy project ID, undeclared scope, replay, oversized payload, lock theft/expiry race, injected retrieved instruction, and direct canonical edit fail.

### OW-090-05 - Build source-linked Documentation Compiler

- Priority/dependencies: P1; `OW-090-01`, `OW-090-02`.
- Outcome: ADRs, architecture, runbooks, onboarding, release notes, and capability catalog compile with source hashes and interpretation labels.
- Allowed paths: documentation compiler, templates, reports, tests/docs.
- Implement: section provenance, draft/review/current lifecycle, deterministic rebuild, impact map.
- Accept: each generated factual section links sources or is labelled interpretation.
- Verify/evidence: golden compiler fixture; `evidence/OW-090-05/`.
- Negative QA: missing or changed source hash prevents current/published status.

### OW-090-06 - Add drift and impact analysis

- Priority/dependencies: P1; `OW-090-05`.
- Outcome: changed sources identify stale decisions, missing acceptance evidence, and affected documents/contracts.
- Allowed paths: drift/index core/CLI, reports, tests/docs.
- Implement: source hash graph, freshness classes, impact reasons, remediation tickets.
- Accept: deliberate code/ADR/contract changes mark only justified dependent artifacts stale.
- Verify/evidence: drift precision fixture; `evidence/OW-090-06/`.
- Negative QA: rebuilt view without source resolution remains stale.

### OW-090-07 - Implement generic JSONL RAG export contract

- Priority/dependencies: P0; `OW-080-08`, `OW-090-03`.
- Outcome: reviewed clean chunks export with separate governance metadata, stable IDs, versions, hashes, edges, and tombstones.
- Allowed paths: RAG schemas/export core, fixtures/tests/docs.
- Implement: deterministic projection manifest, namespaces, dedupe, incremental changes, safe portable format.
- Accept: embedding text excludes frontmatter; consumer can filter project/review/privacy before ranking.
- Verify/evidence: round-trip, retrieval quality, and privacy fixtures; `evidence/OW-090-07/`.
- Negative QA: raw frontmatter, duplicate chunk, unreviewed record, and missing tombstone fail.

### OW-090-08 - Ship LightRAG reference adapter and evaluation

- Priority/dependencies: P1; `OW-090-07`.
- Outcome: one reference consumer ingests, updates, deletes, retrieves, and cites the generic contract without becoming canonical.
- Allowed paths: LightRAG adapter/add-on, eval fixtures, docs/tests.
- Implement: optional dependency boundary, dry-run export, ID mapping, keyword/vector/hybrid/graph examples, source citations, and projection variants for body-only, title+summary+body, and selective semantic tags.
- Accept: projected retrieval meets or improves raw-Markdown recall/ranking while reducing pollution across at least two embedding profiles and multilingual project terms; results state where a projection loses quality.
- Verify/evidence: reference round-trip and stratified retrieval evaluation by projection, retrieval mode, embedding profile, and language; `evidence/OW-090-08/`.
- Negative QA: unavailable backend degrades safely; remote failure cannot corrupt canonical Markdown.

### OW-090-09 - Add incremental Owlib sync, tombstones, and freshness

- Priority/dependencies: P1; `OW-081-09`, `OW-090-03`.
- Outcome: hub indexes update changed records, remove deleted projections, and expose freshness without full rebuild.
- Allowed paths: `owlib/`, sync/index schemas, tests/docs.
- Implement: manifests, hashes, tombstones, atomic swap, interrupted-sync recovery, scoped cache.
- Accept: add/change/delete and interrupted sync reconcile deterministically; unavailable sources are explicitly stale, never current; de-registration tombstones every derived projection; source projects remain read-only.
- Verify/evidence: incremental/failure/scale fixtures; `evidence/OW-090-09/`.
- Negative QA: stale cache, missing source, partial write, and project de-registration do not leak old context.

### OW-090-10 - Cut v0.9.0 release candidate

- Priority/dependencies: P0; `OW-090-04`, `OW-090-06`, `OW-090-08`, `OW-090-09`.
- Outcome: trusted writes, living docs, RAG, and hub freshness ship as one policy-consistent release.
- Allowed paths: release/version/changelog/workflows/docs/manifests.
- Implement: cumulative security/privacy gates, migration notes, artifact build, read-only/write-profile docs.
- Accept: `G-090-RC` passes and default install remains local/read-only unless write profile is explicitly enabled.
- Verify/evidence: release matrix; `evidence/OW-090-10/`.
- Negative QA: write capability without policy or missing RAG deletion proof blocks release.

### OW-090-11 - Align v0.9.0 with the product owner

- Priority/dependencies: P0; `OW-090-10`.
- Outcome: the product owner receives an evidence-linked trusted-knowledge update and decides whether scoped semantic writes and RAG/Owlib workflows may publish and unlock v1.0.
- Allowed paths: `internal/owledge/workpackages/owledge-v1-autonomous-delivery/release-updates/`, `RUN-STATE.yaml`, `BACKLOG.yaml`, `TRACEABILITY.md`, release evidence/manifests.
- Implement: create `release-updates/v0.9.0.md` from `ALIGNMENT-PROTOCOL.md`; reconcile planned versus shipped scope, include write-policy boundaries, privacy/RAG evidence, complete finding/decision/question registers, and a keep/amend/defer/drop reflection for affected v1.0 tickets and gates; present it in chat and set the run state to `awaiting_user_alignment`.
- Accept: `G-090-RC` is green; the update contains all eleven required headings and no untracked claim, finding, or decision; proposed plan amendments validate; user `approve`, `adjust`, or `defer` is recorded with scope/constraints; only `approve` unlocks v1.0.
- Verify/evidence: `python tools/validate_v1_delivery_plan.py`; required-heading check; update, decision, and evidence links under `evidence/OW-090-11/`.
- Negative QA: unsafe write claim, omitted privacy/finding, absent next-plan reflection/decision, automatic next-ticket selection, or autonomous publish/tag leaves the ticket blocked.

## v1.0 - Product Hardening and Release

### OW-100-01 - Establish scale and performance SLOs

- Priority/dependencies: P0; `OW-090-11`.
- Outcome: 10, 1k, and 10k artifact profiles publish index, context, drift, sync, and status latency/resource targets.
- Allowed paths: benchmark kits/results methodology, performance core/tests/docs.
- Implement: controlled fixtures, a hardware-independent deterministic correctness suite, cold/warm runs, p50/p95, memory/disk, and Windows/macOS/Linux performance profiles.
- Accept: correctness passes independently of runner availability; performance targets are reproducible, evidence-bounded, and met or transparently limited without waiving correctness.
- Verify/evidence: scale matrix; `evidence/OW-100-01/`.
- Negative QA: cache-hidden cold result or unreported hardware limitation invalidates claim.

### OW-100-02 - Harden secrets, PII, and prompt-injection boundaries

- Priority/dependencies: P0; `OW-090-03`, `OW-090-04`, `OW-090-11`.
- Outcome: ingestion and export identify secrets/PII, label untrusted external instructions, and block unsafe sharing.
- Allowed paths: security/privacy core, trust add-on, threat model, fixtures/tests/docs.
- Implement: detectors with explicit limitations, injection provenance labels, safe preview, audit events, retention classes, redaction before persistence, committed-artifact size limits, ignore rules, and hash-linked external evidence.
- Accept: negative corpus yields zero unsafe shared exports; raw model transcripts are not committed by default; retention/deletion/tombstone behavior and false-positive handling remain reviewable.
- Verify/evidence: security attack suite; `evidence/OW-100-02/`.
- Negative QA: encoded secret, instruction-like retrieved content, and cross-project PII cannot bypass policy.

### OW-100-03 - Add skill/plugin permission and supply-chain manifests

- Priority/dependencies: P1; `OW-081-01`, `OW-100-02`.
- Outcome: extensions declare version, provenance, read/write/network/credential scopes, updates, and compatibility tests.
- Allowed paths: skills/plugins/add-ons manifests, installer, conformance/security tests/docs.
- Implement: permission diff on update, undeclared-scope rejection, checksums/signature-ready fields, registry policy.
- Accept: third-party adapter cannot request or exercise undeclared write scope.
- Verify/evidence: malicious extension fixtures; `evidence/OW-100-03/`.
- Negative QA: tampered manifest and permission expansion without approval fail install/update.

### OW-100-04 - Build portable outcome evaluation suite

- Priority/dependencies: P0; `OW-071-03`, `OW-080-07`, `OW-081-10`, `OW-090-10`, `OW-100-01`.
- Outcome: provenance accuracy, relevance, resume, portability, stale-doc detection, false gate passes, merge conflict, rework, and small-model quality are measured together.
- Allowed paths: evaluation/benchmark kits, fixtures, reports, tests/docs.
- Implement: versioned development and sealed held-out scenarios, oracle sources, quality thresholds, small-model tool-choice/contract metrics, RAG projection/retrieval/embedding/language strata, and no universal ROI claim.
- Accept: legacy token, held-out correctness, small-model, retrieval-quality, and lifecycle outcome gates pass and are reported independently.
- Verify/evidence: full evaluation matrix with fixture version, environment, commands, limitations, and per-metric verdicts; `evidence/OW-100-04/`.
- Negative QA: token savings with lower correctness cannot pass.

### OW-100-05 - Finish CLI lifecycle and recovery UX

- Priority/dependencies: P1; `OW-080-09`, `OW-100-01`.
- Outcome: install/init/doctor/plan/context/why/status/resume/validate/promote/export/upgrade/uninstall are discoverable, dry-run capable where mutating, and machine-readable.
- Allowed paths: CLI/core, packaging, tests, command/reference/troubleshooting docs.
- Implement: short commands, JSON errors, actionable recovery, idempotency, uninstall preview, no orphaned canonical data; text output includes title or compact description when rendering IDs, while machine-readable JSON remains stable.
- Accept: beginner and automation journeys both work; every mutation explains writes before apply; no text-mode command emits naked IDs unless an explicit machine-oriented option requests IDs only.
- Verify/evidence: command matrix and fresh/dirty/broken fixtures; `evidence/OW-100-05/`.
- Negative QA: interrupted upgrade/uninstall is recoverable and never deletes user-authored knowledge.

### OW-100-06 - Publish support, migration, and deprecation policy

- Priority/dependencies: P1; `OW-100-02`, `OW-100-03`.
- Outcome: users know compatibility window, Tier-1 commitment, experimental status, migration support, and security process.
- Allowed paths: governance/security/support docs, roadmap/changelog/templates.
- Implement: core schema window, adapter support matrix, deprecation stages, vulnerability intake, telemetry/privacy statement.
- Accept: every public capability claim has tier, version, evidence, and limitation.
- Verify/evidence: claim-to-proof documentation audit; `evidence/OW-100-06/`.
- Negative QA: experimental add-on cannot appear stable without conformance proof.

### OW-100-07 - Complete English v1 documentation and case studies

- Priority/dependencies: P0; `OW-100-04`, `OW-100-05`, `OW-100-06`.
- Outcome: beginner, power-user, adapter-author, and maintainer paths are complete and source-linked.
- Allowed paths: `README.md`, `docs/`, `examples/`, docs reports/assets.
- Implement: benefits/use cases, easy install, architecture, contracts, adapters, Hermes/VPS, Owlib scopes, RAG, privacy, migrations, troubleshooting, three real or controlled case studies.
- Accept: docs match shipped commands and support tiers; user testing reaches first value and advanced setup.
- Verify/evidence: docs gates, command extraction tests, moderated journeys; `evidence/OW-100-07/`.
- Negative QA: stale command, missing limitation, inaccessible diagram, or unexplained term fails.

### OW-100-08 - Prove final Tier-1 and evidence-only golden journey

- Priority/dependencies: P0; `OW-100-04`, `OW-100-07`.
- Outcome: all four profiles reach at least 95% declared contract equivalence and evidence reconstructs the full journey without chat.
- Allowed paths: conformance/golden fixtures, reports, release evidence/tests/docs.
- Implement: clean cross-platform run, harness switch, failure/recovery, semantic writes, promotion, docs, RAG, hub scope.
- Accept: every result links artifact, commit, gate, reviewer, and limitation; unsupported capabilities are explicit.
- Verify/evidence: final conformance and reconstruction suite; `evidence/OW-100-08/`.
- Negative QA: remove chat/session state and one evidence item; reconstruction must work in the first case and fail clearly in the second.

### OW-100-09 - Cut and verify v1.0 general availability artifacts

- Priority/dependencies: P0; `OW-100-08`.
- Outcome: clean, reproducible v1.0 wheel/sdist, release notes, support matrix, upgrade/uninstall proof, and final gate are ready for owner-controlled publication.
- Allowed paths: `VERSION`, `pyproject.toml`, `CHANGELOG.md`, workflows, release docs/manifests, artifact configuration.
- Implement: clean build, artifact inspection, fresh install, upgrades from supported versions, uninstall, offline smoke, provenance manifest.
- Accept: `G-100-GA` passes with no unresolved P0/P1, no private path/secret, and no dirty tracked source state.
- Verify/evidence: full release commands and hashes; `evidence/OW-100-09/`.
- Negative QA: publishing/tagging remains owner-controlled; failed artifact or dirty worktree blocks GA.

### OW-100-10 - Align v1.0 closeout with the product owner

- Priority/dependencies: P0; `OW-100-09`.
- Outcome: the product owner receives the final evidence-linked v1.0 feature update, post-v1 questions, and explicitly authorizes or adjusts GA publication and post-v1 work.
- Allowed paths: `internal/owledge/workpackages/owledge-v1-autonomous-delivery/release-updates/`, `RUN-STATE.yaml`, `BACKLOG.yaml`, `TRACEABILITY.md`, release evidence/manifests, post-v1 backlog.
- Implement: create `release-updates/v1.0.md` from `ALIGNMENT-PROTOCOL.md`; reconcile the complete v1 plan against shipped scope, include support/compatibility position, final quality evidence, complete finding/decision/question registers, and a keep/amend/defer/drop post-v1 plan reflection; present it in chat and set the run state to `awaiting_user_alignment`.
- Accept: `G-100-GA` is green; the update contains all eleven required headings and no untracked claim, finding, or decision; post-v1 amendments validate; user `approve`, `adjust`, or `defer` is recorded with scope/constraints; only `approve` authorizes GA publication and v1 closeout.
- Verify/evidence: `python tools/validate_v1_delivery_plan.py`; required-heading check; update, decision, and evidence links under `evidence/OW-100-10/`.
- Negative QA: false GA claim, omitted finding/post-v1 item, absent plan reflection/decision, or autonomous publish/tag leaves the ticket blocked.
