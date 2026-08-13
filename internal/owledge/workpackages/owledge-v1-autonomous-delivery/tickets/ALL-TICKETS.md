---
title: "Owledge v1 Ticket Contracts"
date: "2026-07-16"
version: "2.3.0"
document_version: 3
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
updated_at: "2026-08-12T14:32:51+02:00"
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
  footprint; command truth has one canonical owner. For v0.7.1 development,
  the package chain must pass on supported Windows and the tracked three-OS
  fixture must remain ready. Actual macOS/Linux execution is deferred by
  `D-071-24` to the Stable/GA gate; no v0.7.1 cross-platform support claim is
  permitted before then.
- Verify/evidence: Windows extracted-command and wheel-only smoke, three-OS
  fixture review, and independent install review; stable evidence in
  `OW-100-09` must include executed Windows, macOS, and Linux artifact smoke.
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
- Allowed paths: `VERSION`, `pyproject.toml`, `CHANGELOG.md`, release workflows/docs,
  package manifests, finalization-gate runner, and focused release-gate tests.
- Implement: repair the `upgrade-drift` generated-surface mode regression with a
  non-mocked fixture; stream/flush aggregate gate completion and durations;
  version bump, migration notes, artifact build, wheel-based `uvx` smoke,
  install/upgrade smoke, and clean-state evidence.
- Accept: the full 38-gate finalization suite, including `upgrade-drift`, passes
  from a clean committed integration branch and writes a terminal JSON manifest;
  no generated private path enters artifacts.
- Verify/evidence: focused host/Kit generated-surface regression, full
  `finalization-gates --include-compliance --include-exports`, build, twine,
  wheel/sdist inspection, `uvx` quickstart/doctor; `evidence/OW-071-08/`.
- Negative QA: a green nested version row cannot mask a failed parent doctor;
  source-only imports, stale build artifacts, version mismatch, missing terminal
  manifest, and dirty tracked source fail.

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
- Outcome: accepted ADRs fix source-of-truth, schema/profile/document versioning, lifecycle,
  extension, authority, migration, the transport-neutral Core seam, and the
  separation of Standalone Core GA from Single-Organization Hub Beta.
- Allowed paths: `docs/architecture*`, `internal/owledge/decisions/`, schemas overview, plan references.
- Implement: ADRs for contract set, Markdown/YAML boundary, unknown-field
  preservation, ID stability, status machine, compatibility window,
  Query/Command plus capability envelopes, orthogonal authority-scope,
  knowledge-abstraction, and lifecycle axes, and adapter authority limits. Add
  the generic contracts for a Managed Surface Manifest, transactional upgrade,
  module compatibility/permission/health lifecycle, media-neutral `ResourceRef`,
  and separate `system.doctor|knowledge.health|hub.health` profiles. Keep a
  public plugin SDK, binary/media store, transcription pipeline, and
  subject-rights erasure orchestrator outside V1.
- Accept: no later schema ticket requires an unresolved product decision; reversible local details stay outside ADRs.
- Verify/evidence: architecture review and contract decision matrix; `evidence/OW-080-01/`.
- Negative QA: database-as-canonical, automatic promotion, and destructive migration designs are rejected.

### OW-080-02 - Implement ProjectManifest, ArtifactEnvelope, Schema Registry, and Settings v1

- Priority/dependencies: P0; `OW-080-01`.
- Outcome: project identity, `project_user|user_global|enterprise` knowledge
  scopes, modes, privacy, adapters, gates, artifact lifecycle, provenance,
  typed edges, frontmatter profiles, and effective settings validate consistently.
- Allowed paths: `templates/`, `internal/owledge/templates/`, `skills/`, schema/tool/test/docs paths.
- Implement: a small versioned common envelope plus artifact-specific JSON
  Schema profiles, required/optional fields, defaults, examples, upgrade mapping,
  `additionalProperties: false` for Core objects, and a namespaced inert
  `extensions` object; replace the single broad required-field contract without
  rewriting user-authored Markdown. Define `schema_version` for contract shape,
  `profile_version` for artifact rules, monotonic `document_version` for each
  material edit under a stable ID, and `source_hash` for byte/content integrity;
  reject missed, duplicate, or non-monotonic revision bumps. Add layered settings for immutable Core
  invariants, deployment/organization policy, private user preferences, project
  preferences, and bounded session overrides; denies win and later layers may
  narrow but never widen authority. Preserve extension fields; add the
  owner-approved transferability model as separate fields
  from audience and privacy; define `knowledge_scope`, `owner_user_id`,
  server-resolved project scope, and stable capability Request/Result receipts.
  Define optional `ResourceRef` with stable ID/relation, URI or opaque locator,
  media type, hash, size, data class, access/availability state, and extraction
  provenance; resolving a reference remains a separately authorized capability.
- Accept: round-trip preserves stable IDs, typed edges, namespaced unknown
  extensions, schema/profile/document versions, effective-settings explanation receipt,
  visibility, data class, audience IDs, transferability, applies-to scope, and
  all three knowledge scopes without treating caller-supplied paths as authority.
- Verify/evidence: schema positive/negative and migration tests; `evidence/OW-080-02/`.
- Negative QA: invalid lifecycle, missing identity, unknown Core key, unnamespaced
  extension, policy-widening override, unsafe visibility/data-class combination,
  overloaded audience/privacy fields, invalid transferability value, material
  edit without exactly one document-version increment, unverified resource
  locator, and ID mutation fail.

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

#### Deferred OW-080-12 - Optional Autonomous Delivery Profile (post-v1 add-on)

Deferred from the required v1 train because runtime orchestration policy is not
needed to prove Owledge's Core, Research Memory, adapter, or Hub value. The
concept remains available for a separately versioned add-on after the four
reference profiles and capability contracts are stable.

- Former priority/dependencies: P0; `OW-080-02`, `OW-080-03`, `OW-080-04`.
- Outcome: small work stays single-agent by default, while larger work can use a runtime-neutral, consent-first delivery profile.
- Allowed paths: execution schemas/templates, planning tools/CLI/tests/docs, `internal/owledge/workpackages/`.
- Implement: default-off profile fields for blockers, subagent eligibility, orchestrator, model profile, QA, Red Team, approval mode, Git lane, and parallelism; render dependency links from the canonical backlog; record a risk brief and consent state without dispatching a runtime.
- Accept: parsing or dry-run planning cannot spawn an agent or create a worktree; `subagent: true` is eligibility only; unknown model, missing consent, overlapping lane, or raw credential fails closed.
- Verify/evidence: profile round-trip, default-off, consent, dependency-link, and negative fixtures; `evidence/OW-080-12/`.
- Negative QA: implicit spawn, generic write fallback, same-context QA, unsupported profile, or unapproved high-risk ticket is rejected.
### OW-080-16 - Implement Research Memory contracts and recall-first lookup

- Priority/dependencies: P0; `OW-080-02`.
- Outcome: Owledge reuses prior source-linked Research Memory before recommending
  external research and emits bounded freshness/gap results across authorized scopes.
- Allowed paths: research schemas/templates/skills, Core recall/index code,
  fixtures/tests, command and architecture docs.
- Implement: versioned Research Brief, Source Record, Atomic Finding, Synthesis,
  and Research Task Index contracts; source mutability classes; research reason,
  context, publication/version, search/retrieval/verification timestamps, source
  hash, lifecycle, relations, and deterministic recall results for
  `sufficient_current|stale|partial|missing|conflicted`; reuse the existing
  `.owledge/research/` and `global-memory/research/` layouts; no web or LLM call
  in the recall primitive.
- Accept: an immutable paper, versioned tool release, and mutable documentation
  fixture receive distinct freshness behavior; fresh coverage prevents an
  unnecessary refresh recommendation; stale or incomplete coverage produces a
  delta brief; every result exposes source revision, scope, freshness, reasons,
  contradictions, and gaps.
- Verify/evidence: schema round-trip, recall/dedup/freshness, scope-isolation,
  rename-stability, and delta-brief fixtures; `evidence/OW-080-16/`.
- Negative QA: duplicate stable ID, unknown source mutability, caller path escape,
  cross-scope finding, missing research reason/source, and silent external search fail.

### OW-080-05 - Build deterministic Context Compiler v1

- Priority/dependencies: P0; `OW-080-02`, `OW-080-03`, `OW-080-04`, `OW-080-16`.
- Outcome: bootstrap, task, reviewer, handoff, and release packs explain inclusion/exclusion and respect budgets.
- Allowed paths: context-pack core/CLI, schemas, fixtures, tests, docs.
- Implement: deterministic ordering/digest, typed selection reasons,
  privacy/staleness filters, dropped-source list, pack version; add bounded
  pre-plan and pre-research capsules that inspect relevant idea, concept,
  decision, pattern, lesson, research synthesis/finding, and roadmap metadata;
  distinguish source, research, and review freshness; retrieve reviewed global
  essences first where allowed, then expose `explain|deep_dive|refresh`
  expansion over stable project/source revisions; expand only material
  candidates and enforce explicit context budgets without silent omission.
- Accept: identical inputs produce identical pack and digest; every
  included/excluded source has a reason; fresh Research Memory is reused before
  a refresh is proposed; stale source, stale research, stale review, scope,
  privacy, conflict, and over-budget exclusions are distinguishable.
- Verify/evidence: golden pack tests and v0.7 regression fixture; `evidence/OW-080-05/`.
- Negative QA: private, stale, unrelated, unauthorized deep-dive, unavailable
  project source, or over-budget source cannot enter silently.

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

### OW-080-13 - Collapse /goal resume token drain (R1-R7)

- Priority/dependencies: P1; `OW-071-09`, `OW-080-05`.
- Outcome: each `/goal` resume loads only the active RUN-STATE slice and the delta of control docs (or skips them when the runtime already retains them), reuses the latest handoff before re-deriving context, and failed-gate triage reads a capped payload; the fix is runtime-neutral across Codex `/goal` v0.128+ (persisted context, worker self-judges) and Claude Code `/goal` v2.1.139+ (`--resume` resets the token baseline, Haiku judge sees transcript only); stable IDs, evidence SHAs, gate independence, and the owner-alignment stop are preserved.
- Allowed paths: `RUN-STATE.yaml`, `skills/owledge-long-horizon-delivery/references/modes.md`, `ALIGNMENT-PROTOCOL.md`, `CONTROL-PLANE-POLICY.md`, `tools/owledge.py`, `tools/owledge_core.py`, `internal/owledge/reports/token-usage-red-team-review-2026-07-28.md`. Disjoint from OW-071-13's HTTP/security/control-plane-capability paths.
- Implement: estimate savings separately for cold resume (full re-load) and warm resume (Codex persisted context; docs already in context) — the 8-20k figure is the cold-resume ceiling and warm-resume savings are smaller and must be measured, not assumed. (R1) hash-delta load of the 3 control docs via `last_control_sha`, branched on `RUN-STATE.session.runtime_resume_model`: if `persisted` (Codex warm resume), detect docs already in context and skip re-read, with hash-delta as a fallback only when content is not already in context; if `reset_baseline` (Claude Code `--resume`), apply hash-delta as the primary saving every resume. (R2) split `RUN-STATE.yaml` into two tiers: `session_slice` (warm-resume minimum, <1KB: active version, active ticket, current step, next command) and `durable_state` (registers/SHAs/evidence/decisions, cold-resume only); warm resume loads only `session_slice`, cold resume loads `session_slice` + `durable_state`. (R3) handoff-first recovery branched on `runtime_resume_model`: Codex warm resume verifies handoff presence in-context and skips re-read if present; Claude Code `--resume` reads `.owledge/handoffs/<latest>` mandatorily because the baseline reset discards prior turn state. The "5 resume items" are the `modes.md:140-146` Recovery list; reconcile with the `ALIGNMENT-PROTOCOL.md:109` resume list so a `/goal` resume that triggers Recovery loads one coherent set, not the union. (R4) cap `run_gate` error payload to `{passed, failed, total, first_failings[:5]}` with a sidecar holding the full payload for audit; under Claude Code the worker also emits the capped payload plus a manifest of sidecar contents to the transcript so the Haiku judge can verify completeness without opening files. (R5) slim the RUN-STATE `findings` block to ID + status + manifest ref. (R6) compress `last_completed_actions` to decision-ID refs. (R7) trim `last_commands` to current-ticket-relevant entries. All changes stay behind the existing resume contract; no new always-loaded docs.
- Accept: runtime-neutral — pass on BOTH the active Codex desktop `/goal` runtime (the primary Codex harness; `/goal` is host-managed and must not recursively invoke a second Codex binary) AND Claude Code `/goal` v2.1.139+ with evidence recorded in each. Codex CLI v0.128.0+ `exec resume` receipts may supplement this evidence, but are not a substitute for an active Goal-thread receipt. A `/goal` resume loads strictly fewer file-content tokens than the pre-OW-080-13 baseline for identical active state, measured by a file-content tokenizer (sum of `token_count(loaded_file_content)`), NOT by harness-reported context tokens which reset to ~0 on Claude Code `--resume`; report `cold_resume_drain` and `warm_resume_drain` separately, both strictly less than baseline. Identical inputs produce identical gate results. Failed-gate triage still reconstructs the full payload from the sidecar. Every acceptance clause is expressible as a verifiable command runnable by the worker with output printed to the transcript (the Claude Code Haiku judge cannot run commands or open files). Stable finding IDs `F-NN`, evidence SHAs, gate independence, and the owner-alignment stop behave unchanged — the owner-alignment stop verified by a verifiable command (e.g., a state-transition check), not protocol assertion alone.
- Verify/evidence: every acceptance property is expressed as a verifiable command whose output the worker prints to the transcript as text: before/after file-content token delta (`cold_resume_drain`, `warm_resume_drain`) measured with Codex `model_auto_compact_token_limit` ON; golden gate-result equality (worker prints both digests + diff exit code); sidecar-roundtrip (worker prints capped + reconstructed payloads + equality verdict); stale-handoff negative fixture (worker prints the REJECT result). Repeated in both runtimes. `evidence/OW-080-13/`.
- Negative QA: a changed control doc whose SHA differs but content is byte-identical cannot trigger a reload; a control doc already in persisted Codex context is not re-read on warm resume, while a baseline-reset Claude Code resume still applies hash-delta. A missing handoff cannot bypass the 5-item SHA gate; under Claude Code `--resume` R3 reads the handoff mandatorily, under Codex warm resume R3 verifies handoff presence without re-read. A capped error payload must not drop the full audit sidecar; under Claude Code a sidecar-only audit trail that is not transcript-visible fails the gate (the Haiku judge cannot read disk). An over-aggressive `session_slice` must not hide a finding that still affects the active version; `durable_state` must remain cold-resume-reconstructable. An owner-alignment stop expressed only as a protocol rule (not a verifiable command) fails under Claude Code.

### OW-080-08 - Build clean RAG Retrieval Projection v1

- Priority/dependencies: P0; `OW-080-02`, `OW-080-05`, `OW-080-16`.
- Outcome: embedding text contains semantic title, summary, and clean section body while governance metadata stays separate.
- Allowed paths: RAG/export core, schemas, fixtures, benchmark/docs/tests.
- Implement: heading-aware chunks, boilerplate/frontmatter removal, source- and
  claim-level dedupe, source hash/version/freshness/tombstone metadata, research
  reason/context filters, and typed-edge hints.
- Accept: raw frontmatter tokens are absent from embedding text; IDs, policy, source, freshness, and edges remain metadata.
- Verify/evidence: raw-vs-projection retrieval evaluation; `evidence/OW-080-08/`.
- Negative QA: duplicate compiled/source chunks, private chunk, stale hash, and template boilerplate fail.

### OW-080-09 - Add Knowledge Health status and preview migration

- Priority/dependencies: P1; `OW-080-03`, `OW-080-04`.
- Outcome: users inspect deterministic project/knowledge health and preview
  legacy migration without mutation or an LLM.
- Allowed paths: CLI/core, templates, migration tools, tests/docs.
- Implement: `status`/board and `knowledge.health` read views for schema/profile/
  document revisions, duplicate IDs/claims, broken/orphaned edges, unresolved
  source refs, Research freshness, context-pack budget/pollution, and projection
  watermark; `migrate --dry-run`, patch/manifest output, collision report, and
  explicit apply mode. Define a Managed Surface Manifest that classifies files
  as Core-managed, user-managed, generated, or extension-managed and records
  installed version, delivery hash, and current hash. Preview uses a
  transactional protocol: preflight `system.doctor`, dry-run/diff, recoverable
  checkpoint, apply, postflight health, and receipt. Reports contain metadata
  and stable IDs, not knowledge bodies.
- Accept: read view does not mutate or call a model; seeded health failures are
  classified with reason and remediation; preview lists every proposed write
  and never-touch file; apply is idempotent and a failed postflight has an
  explicit recovery path.
- Verify/evidence: 10/1k artifact health performance plus migration fixtures; `evidence/OW-080-09/`.
- Negative QA: missed revision bump, broken edge, stale source, over-budget pack,
  edited template collision, ambiguous ownership, ambiguous legacy layout,
  failed postflight, and second apply do not pass silently.

### OW-080-10 - Cut v0.8.0 release candidate

- Priority/dependencies: P0; `OW-080-07`, `OW-080-08`, `OW-080-09`.
- Outcome: portable contracts, context efficiency, small models, retrieval projection, and migration ship together.
- Allowed paths: version/changelog/workflows/release docs/package manifests.
- Implement: cumulative functional gates, contract fixtures, migration notes, artifacts, wheel-based smoke, and frozen legacy-regression replay. Do not introduce a new comparative benchmark campaign or a new performance/quality claim in v0.8.0.
- Accept: `G-080-RC` passes from clean state and v0.7 legacy regression remains green. Comprehensive comparative benchmarking and final outcome claims are deferred to `OW-100-04`/`G-100-B-PRODUCT`; ticket-local deterministic measurements remain required where they prove an implemented behavior.
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
- Outcome: adapters and modules declare detect/install/inject/capture/execute/
  resume/health/cleanup/uninstall, versions, Core compatibility, permissions,
  profiles, migrations, limits, and degradation.
- Allowed paths: runtime conformance add-on, schemas, adapter templates, tests/docs.
- Implement: capability schema, negotiation result, fixture protocol,
  support-tier rules, module kind, compatibility range, declared artifact
  profiles/migrations, and health contract; define optional pre-plan lifecycle
  capabilities for scoped idea/concept lookup, MVP-cutline handoff,
  roadmap/idea capture, and explicit unsupported degradation without requiring
  background writes or access to Core storage internals.
- Accept: undeclared capability cannot run; unsupported feature returns explicit structured result; adapters cannot claim automatic pre-plan inspection or durable routing unless they pass the shared fixtures.
- Verify/evidence: manifest and negative compatibility suite; `evidence/OW-081-01/`.
- Negative QA: version mismatch, missing permission, undeclared profile or
  migration, Core-internal storage access, or false capability claim fails.

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

### OW-081-04 - Pi reference adapter

- Priority/dependencies: P0; `OW-081-01`.
- Outcome: `@owledge/pi` proves that a custom agent runtime can use Owledge for
  durable memory, scoped context, Research recall, and continuity without
  duplicating Core semantics.
- Allowed paths: Pi extension/package adapter, skills/fixtures, runtime docs/tests.
- Implement: detect local project or Hub configuration; register thin
  read/search/context/artifact/task/review/handoff tools; inject only minimal
  bootstrap context; map Pi session lifecycle to structured Candidate handoff;
  declare permissions and explicit degradation; depend on Owledge capability
  contracts rather than direct internal file/database calls.
- Accept: a new Pi session retrieves prior scoped state without chat history,
  only task-relevant context enters the model, SessionEnd creates a private
  Candidate handoff, and durable Markdown remains Core-owned.
- Verify/evidence: pinned Pi fixture/conformance transcript;
  `evidence/OW-081-04/`.
- Negative QA: raw transcript promotion, Pi-specific Core branch, direct
  database/filesystem bypass, undeclared write, disabled capability, and
  unavailable integration fail clearly.

### OW-081-05 - Generic MCP/CLI portable baseline adapter

- Priority/dependencies: P1; `OW-081-01`.
- Outcome: any capable harness can use the same versioned read/control contract without runtime-specific files.
- Allowed paths: MCP/CLI server, generic adapter fixtures, docs/tests.
- Implement: protocol-compliant surface, capability discovery, JSON output, stdio lifecycle, project binding, and a read-only pre-plan capsule endpoint with explicit promotion/write boundaries.
- Accept: reference client passes common conformance suite.
- Verify/evidence: protocol and CLI fixtures; `evidence/OW-081-05/`.
- Negative QA: malformed JSON-RPC, unknown project, and tool mismatch fail without server crash.

#### Deferred OW-081-06 - Claims and worktree planner (post-v1 add-on)

Deferred because eight-worker planning is a delivery-orchestration feature, not
a prerequisite for cross-harness memory continuity. The required v1 path keeps
checkpoint idempotency and explicit adapter permissions without owning worktrees.

- Priority/dependencies: P0; `OW-080-03`, `OW-081-01`.
- Outcome: independent work receives explicit claim, branch/worktree, allowed paths, base SHA, merge order, and TTL.
- Allowed paths: workpackage/claim schemas, Git helper core/CLI, tests/docs.
- Implement: dry-run worktree plan, overlap detection, advisory lease, ownership journal, no direct integration-branch worker writes; treat single-writer/write-claim policy as a claims-and-scope protocol before any MCP write lock.
- Accept: eight non-overlapping fixture workers plan cleanly; overlap requires owner decision; no worker receives write authority without explicit claim, allowed paths, base SHA, TTL, and merge order.
- Verify/evidence: Git fixture suite; `evidence/OW-081-06/`.
- Negative QA: overlapping glob, stale base, dirty target, invalid branch, and expired claim block dispatch.

### OW-081-07 - Implement checkpoint reconciliation and cross-harness resume

- Priority/dependencies: P0; `OW-080-04`, `OW-081-01`.
- Outcome: kill/retry at every checkpoint avoids duplicate canonical records
  and side effects while a second supported harness resumes without chat history.
- Allowed paths: checkpoint/resume core, adapter fixtures, tests/docs.
- Implement: input/output hashes, idempotency keys, side-effect journal, reconciliation status, resume pack.
- Accept: second Tier-1 harness resumes exact work from checkpoint without chat history.
- Verify/evidence: kill/retry and harness-switch matrix; `evidence/OW-081-07/`.
- Negative QA: hash mismatch or uncertain external side effect blocks automatic resume.

### OW-081-08 - Add runtime hooks and integration manifest

- Priority/dependencies: P1; `OW-081-02`, `OW-081-03`, `OW-081-04`, `OW-081-05`, `OW-081-07`.
- Outcome: supported hooks validate mutations, create structured Session Recap
  Candidates, and record scopes, gates, reviews, conflicts, risks, and resumable deltas.
- Allowed paths: adapter hooks, integration schemas, CLI/tests/docs.
- Implement: settings-controlled pre-research recall, post-research delta
  proposal, post-tool validation, and Stop/SessionEnd recap with Outcomes,
  Decisions, Learnings, Gotchas, open questions, Evidence, affected artifacts,
  Research Candidates, and Promotion Candidates; no raw transcript promotion;
  explicit unsupported warnings and deterministic integration manifest.
- Accept: invalid ticket edit cannot pass session close; the recap is private,
  source-linked, schema-valid, resumable from another harness, and remains a
  Candidate until review; integration order is reproducible.
- Verify/evidence: hook and merge fixtures; `evidence/OW-081-08/`.
- Negative QA: missing recall receipt, autonomous capture disabled by settings,
  missing evidence, failed hook, scope conflict, or unreachable commit blocks integration.

#### Deferred OW-081-12 - Optional autonomous-delivery skill (post-v1 add-on)

Deferred until the runtime-neutral Core and adapter capability surface are
proven. Shipping it in v1 would make Owledge look like an agent orchestrator
rather than the durable knowledge and project-memory layer it is meant to be.

- Priority/dependencies: P1; `OW-080-12`, `OW-081-01`, `OW-081-06`, `OW-081-08`.
- Outcome: one portable skill assesses ticket risk, proposes lanes and models, explains risks, and requests user consent before a runtime is allowed to act.
- Allowed paths: `skills/owledge-autonomous-delivery/`, plugin skill entrypoints, runtime docs, fixtures/tests, workpackage templates.
- Implement: small/medium/high-risk classifier, phase/per-ticket approval flow, model-profile guidance, isolated Worker/QA/Red-Team handoff rules, Git-lane checklist, risk brief, and safe single-agent fallback.
- Accept: the skill starts with recommendation rather than execution; small tickets stay simple; high-risk tickets cannot dispatch without fresh approval; each runtime receives a compact, explicit capability boundary.
- Verify/evidence: classifier, consent, capability-degradation, and lane-isolation fixtures; `evidence/OW-081-12/`.
- Negative QA: implicit invocation, automatic spawn, omitted risk, same-context QA, or claimed unsupported runtime capability fails.

#### Deferred OW-081-13 - Optional runtime orchestration adapters (post-v1 add-on)

Deferred with the delivery skill. Codex `/goal` mapping and harness-specific
worker dispatch stay outside the v1 Core; generic MCP/CLI remains the portable
integration seam.

- Priority/dependencies: P1; `OW-081-12`.
- Outcome: Codex, Claude Code, OpenCode, Hermes, and generic MCP/CLI can
  consume the approved delivery plan without making any runtime a Core
  dependency.
- Allowed paths: runtime adapters, integration manifests, CLI/tests/docs, adapter fixtures.
- Implement: read-only `execution plan` dry-run, model-profile resolution, consent verification, worktree/branch/merge manifests, explicit capability/degradation results, `/goal` mapping as a Codex adapter, and harness-specific pre-plan hooks that request the deterministic idea/concept capsule before new feature planning and return roadmap/idea dispositions for owner approval.
- Accept: adapters never launch externally while planning; pre-plan hooks are scoped, observable, and fail visibly without inventing context or writing automatically; approved non-overlapping lanes can be proposed; unsupported features degrade visibly and safely; integration writes remain owned by the integration role.
- Verify/evidence: cross-runtime dry-run, consent, worktree, merge-manifest, and degradation fixtures; `evidence/OW-081-13/`.
- Negative QA: no consent, overlap, direct integration write, unsupported model/runtime, or hidden external launch blocks dispatch.

#### Deferred OW-081-14 - Edge/local-model delivery profile (post-v1 add-on)

Deferred because the deterministic Core should first prove small context packs
and machine-readable errors independently of a model-specific delivery profile.

- Priority/dependencies: P0; `OW-080-07`, `OW-081-12`, `OW-081-13`.
- Outcome: constrained local models receive compact task capsules and deterministic guardrails instead of excessive context or unsafe authority.
- Allowed paths: context profiles, adapter configuration, benchmark fixtures, deterministic validators, docs/tests.
- Implement: `edge_small` capability boundary, task-capsule format, hard budgets, progressive disclosure, unsupported-task responses, offline fixtures, and one real local-model smoke protocol.
- Accept: edge models can perform declared bounded tasks without full-plan injection; deterministic validators catch malformed output; unsupported architecture, merge, security, and cross-project actions are refused clearly.
- Verify/evidence: 4B-class local-model smoke run plus budget, structured-output, false-pass, and fallback fixtures; `evidence/OW-081-14/`.
- Negative QA: oversized context, hidden model downgrade, improvised unsupported action, false acceptance, or missing real-model evidence blocks the v0.8.1 claim.
### OW-081-09 - Add scoped Owlib retrieval and hub context packs

- Priority/dependencies: P1; `OW-071-06`, `OW-080-05`, `OW-080-11`.
- Outcome: Owlib queries `project_user`, private `user_global`, or approved
  `enterprise` knowledge across explicit allowlisted projects and explains every
  scope and source selection.
- Allowed paths: `owlib/`, hub skills/MCP/docs/tests.
- Implement: `--projects`, exclusions, three knowledge-scope profiles,
  principal/owner binding, orthogonal abstraction/lifecycle filters,
  project-filter-first Research and general retrieval, reviewed-global-essence
  first recall, explicit permission-checked project `deep_dive`, context-pack
  budget/digest, source reasons, and separate personal-global versus enterprise
  indexes or namespaces; add one local `user_global` reference composition that
  at least two harnesses can query through the generic Core/MCP seam without Hub
  upload or remote user-global synchronization.
- Accept: default never scans all projects; project-user data never enters
  another user's global or enterprise result; output identifies scope, owner,
  project, abstraction level, lifecycle, source revision, freshness, review,
  and exclusion reasons; an unavailable or unauthorized drill-down is explicit.
- Verify/evidence: cross-project privacy/relevance fixtures; `evidence/OW-081-09/`.
- Negative QA: unauthorized project ID, deep-dive permission bypass, missing
  source presented as current, empty scope, mixed private/shared context, and
  implicit Hub upload fail safely.

### OW-081-10 - Prove Research-to-resume golden journey and cut v0.8.1

- Priority/dependencies: P0; `OW-081-08`, `OW-081-09`.
- Outcome: Research recall, scoped context, deliberate interruption, structured
  Session Recap, cross-harness resume, failed review, correction, and source-linked
  report run end to end; optional autonomous delivery is measured separately.
- Allowed paths: golden fixtures/demo, conformance kit, release/version/docs/workflows.
- Implement: deterministic journey using Codex, Claude, Pi, and generic MCP/CLI;
  prove Hermes/OpenCode generic compatibility without requiring bespoke adapters;
  clean artifact build and public support matrix.
- Accept: fresh research is reused, stale research creates a delta brief, recap
  resumes without chat, and no scope leak, silent degradation, duplicate write,
  or Core runtime coupling occurs; `G-081-RC` passes.
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
- Outcome: claims and Research findings trace to source revision, research
  reason/context, retrieval/verification time, run, commit, test, reviewer, and
  explicit authority/supersession rules.
- Allowed paths: evidence/authority schemas, core/CLI/tests/docs.
- Implement: append-only events, stable refs, code/ADR/issue/memory/research
  conflict policy, document-version events distinct from schema migration,
  source mutability and revision facts, tamper/digest checks.
- Accept: public claim can be reconstructed and contradictions remain visible.
- Verify/evidence: ledger and authority fixtures; `evidence/OW-090-01/`.
- Negative QA: event mutation, broken source ref, and ambiguous authority block current status.

### OW-090-02 - Implement reviewed promotion lifecycle

- Priority/dependencies: P0; `OW-090-01`.
- Outcome: candidate, raw-inbox, reviewed, canonical, superseded,
  rejected/archived transitions are
  explicit, reversible, evidenced, and valid across project-user, user-global,
  and enterprise scopes.
- Allowed paths: promotion core/schemas/CLI/templates/tests/docs.
- Implement: promotion request, a private `user_global` raw inbox excluded from
  ordinary retrieval/RAG, stable claim/source dedupe, source-linked reusable
  delta capsules rather than pointer-only records or full project plans/transcripts,
  policy-controlled TTL snapshots only for volatile/non-reproducible sources,
  reviewed global-essence compilation with stable project/Evidence drill-down,
  reviewer separation,
  contradiction link, supersession, policy profile, rollback, retention, and
  explicit research finding or synthesis promotion without copying raw research
  dumps; define policy-driven withdrawal/revocation transitions for already
  promoted essences and their drill-down refs.
- Accept: no agent or full-access profile promotes without required gate and
  audit record; every promote/reject/archive result retains source revision,
  reason, target, retention, and receipt.
- Verify/evidence: lifecycle matrix; `evidence/OW-090-02/`.
- Negative QA: raw candidate returned by normal search, self-approval, missing
  sanitization, private-to-shared transition, silent discard, stale evidence,
  and withdrawn source remaining retrievable fail.

### OW-090-03 - Enforce end-to-end privacy ingestion policy

- Priority/dependencies: P0; `OW-090-01`.
- Outcome: consent, scan allowlist, data class, redaction, retention, and export policies apply before retrieval or sharing.
- Allowed paths: privacy/config schemas, ingest/export core, fixtures/tests/docs.
- Implement: deny-by-default external scope, per-project consent, layered
  settings with deny-wins semantics, provider/model/region/data-class allowlists
  using secret references rather than credentials, redaction results, negative corpus.
- Accept: private, confidential, unsanitized, unreviewed, and disallowed-project records never enter shared output.
- Verify/evidence: privacy attack corpus; `evidence/OW-090-03/`.
- Negative QA: prompt relevance cannot override privacy policy.

### OW-090-04 - Add semantic write-enabled MCP

- Priority/dependencies: P0; `OW-090-02`, `OW-090-03`.
- Outcome: MCP supports create candidate, append evidence, checkpoint, handoff,
  Research Candidate/delta brief, and promotion request under policy.
- Allowed paths: MCP server, semantic write service, schemas, tests/docs.
- Implement: capability scopes, principal/project/scope binding, one
  transport-neutral semantic mutation Core interface, target identity,
  expected `document_version` and base hash, locks/idempotency, dry run,
  authorized lifecycle transition, atomic file/Git result, conflict and
  reconciliation receipt, audit event, and structured result; no arbitrary
  write tool; support Candidate, Research Candidate, experience/evidence append,
  and refresh proposal only as semantic contract operations with provenance.
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
- Outcome: changed sources identify stale decisions, Research Memory, missing
  acceptance evidence, promotion/review debt, unresolved drill-down sources,
  and affected documents/contracts.
- Allowed paths: drift/index core/CLI, reports, tests/docs.
- Implement: source hash graph, source-mutability-aware freshness classes,
  impact reasons, raw-inbox age/TTL, global-essence source coverage, health
  aggregation, delta-only research refresh proposals, remediation tickets.
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
- Outcome: project-user, user-global, and enterprise indexes update changed
  records, remove deleted projections, and expose general and Research
  freshness plus project-source availability without full rebuild.
- Allowed paths: `owlib/`, sync/index schemas, tests/docs.
- Implement: manifests, hashes, tombstones, atomic swap, interrupted-sync
  recovery, distinct scope namespaces, source-version/freshness metadata, and
  project-filter-first caches, essence-to-project source resolution, and
  content-free health watermarks/backlog metrics; propagate policy-driven source
  withdrawal, access revocation, and deletion through global essences,
  drill-down availability, exports, and every derived namespace.
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
- Outcome: 10, 1k, and 10k artifact profiles publish index, context, drift,
  sync, deep-retrieval, and Knowledge Health latency/resource targets.
- Allowed paths: benchmark kits/results methodology, performance core/tests/docs.
- Implement: controlled fixtures, a hardware-independent deterministic
  correctness suite, cold/warm runs, p50/p95, memory/disk, Knowledge Health
  issue cardinality/backlog and source-resolution metrics, and Windows/macOS/Linux performance profiles.
- Accept: correctness passes independently of runner availability; performance targets are reproducible, evidence-bounded, and met or transparently limited without waiving correctness.
- Verify/evidence: scale matrix; `evidence/OW-100-01/`.
- Negative QA: cache-hidden cold result or unreported hardware limitation invalidates claim.

### OW-100-02 - Harden secrets, PII, and prompt-injection boundaries

- Priority/dependencies: P0; `OW-090-03`, `OW-090-04`, `OW-090-11`.
- Outcome: ingestion and export identify secrets/PII, label untrusted external instructions, and block unsafe sharing.
- Allowed paths: security/privacy core, trust add-on, threat model, fixtures/tests/docs.
- Implement: detectors with explicit limitations, injection provenance labels, safe preview, audit events, retention classes, redaction before persistence, committed-artifact size limits, ignore rules, and hash-linked external evidence.
- Accept: negative corpus yields zero unsafe shared exports; raw model
  transcripts are not committed by default; retention/deletion/tombstone and
  source-withdrawal propagation through promoted and derived surfaces remain
  reviewable and leave no retrievable shadow content.
- Verify/evidence: security attack suite; `evidence/OW-100-02/`.
- Negative QA: encoded secret, instruction-like retrieved content, and cross-project PII cannot bypass policy.

### OW-100-03 - Add skill/plugin permission and supply-chain manifests

- Priority/dependencies: P1; `OW-081-01`, `OW-100-02`.
- Outcome: extensions, model/provider adapters, and agent/service identities
  declare version, provenance, read/write/network/credential and knowledge
  scopes, permitted data classes/regions, updates, and compatibility tests.
- Allowed paths: skills/plugins/add-ons manifests, installer, conformance/security tests/docs.
- Implement: permission diff on update, undeclared-scope rejection,
  principal/capability binding, provider/deployment policy metadata, external
  secret references, checksums/signature-ready fields, registry policy, Core
  compatibility range, owned schema/profile and migration declarations,
  bounded health checks, cleanup, and uninstall contract. Installed extension
  files are `extension-managed` in the Managed Surface Manifest.
- Accept: third-party adapter cannot request or exercise undeclared write scope.
- Verify/evidence: malicious extension fixtures; `evidence/OW-100-03/`.
- Negative QA: raw credential, unapproved provider/region/data class, tampered
  manifest, undeclared migration, overwrite of user-managed content, and
  permission expansion without approval fail install/update.

### OW-100-11 - Ship Single-Organization Hub Beta with external identity

- Priority/dependencies: P0; `OW-090-04`, `OW-090-09`, `OW-100-02`, `OW-100-03`.
- Outcome: one organization can run Owledge centrally, authenticate developers
  and agent/service identities through an existing OAuth/OIDC provider, and use
  scoped MCP/HTTP access without changing Markdown/Git source-of-truth semantics.
- Allowed paths: Hub server package, identity/capability configuration,
  deployment examples, MCP/HTTP transport, security/conformance tests/docs.
- Implement: one-organization-per-deployment configuration; issuer/audience/JWKS
  validation; human and service principal mapping; project allowlists; explicit
  registered-project and `enterprise` capabilities; explicit rejection of
  implicit `user_global` ingestion or synchronization; read-only default;
  Candidate/Evidence-only agent writes; reviewed promotion; audit receipts;
  Docker reference deployment; content-free readiness/latency/error/auth/storage/
  backup-age/index-lag metrics with an external monitoring adapter; and
  backup/restore runbook with tested Beta RPO/RTO bounds for Hub-owned state and
  an explicit customer-owned project Markdown/Git backup boundary. Raw prompts,
  outputs, and knowledge bodies are forbidden telemetry.
- Accept: two users and two service identities can access only permitted
  projects/scopes; revoked/expired tokens fail closed; canonical changes remain
  Markdown/Git commits; no local password database exists; local standalone mode
  works without the Hub package; the capability is labeled Beta in every claim.
- Verify/evidence: OIDC fixture provider, token and confused-deputy attack
  corpus, scope-isolation matrix, MCP/HTTP conformance, restart/recovery and
  standalone-regression and health-export privacy tests; `evidence/OW-100-11/`.
- Negative QA: caller-supplied filesystem path, wrong issuer/audience, unknown
  principal, cross-project token replay, agent canonical promotion, audit gap,
  raw-content metric label, unproven recovery claim, or Hub outage may not leak
  or corrupt canonical data.

### OW-100-04 - Build portable outcome evaluation suite

- Priority/dependencies: P0; `OW-071-03`, `OW-080-07`, `OW-081-10`, `OW-090-10`, `OW-100-01`, `OW-100-11`.
- Outcome: provenance accuracy, Research recall/reuse, freshness, scope
  isolation, resume, portability, stale-doc detection, false gate passes,
  rework, hierarchical essence-to-project retrieval, Knowledge Health, and Hub authorization are measured together.
- Allowed paths: evaluation/benchmark kits, fixtures, reports, tests/docs.
- Implement: versioned development and sealed held-out scenarios, oracle
  sources, quality thresholds, research recall-before-search and stale/delta
  metrics, cross-scope leak tests, adapter contract metrics, RAG
  projection/retrieval/embedding/language strata, and no universal ROI claim.
- Scope: this is the first release-wide comparative benchmark and outcome-claim
  campaign. Earlier releases retain only frozen-regression replays and
  ticket-local deterministic measurements needed to prove their behavior.
- Accept: legacy token, held-out correctness, small-model, retrieval-quality, and lifecycle outcome gates pass and are reported independently.
- Verify/evidence: full evaluation matrix with fixture version, environment, commands, limitations, and per-metric verdicts; `evidence/OW-100-04/`.
- Negative QA: token savings with lower correctness cannot pass.

### OW-100-05 - Finish CLI lifecycle and recovery UX

- Priority/dependencies: P1; `OW-080-09`, `OW-100-01`.
- Outcome: install/init/doctor/plan/context/why/status/resume/validate/promote/export/upgrade/uninstall are discoverable, dry-run capable where mutating, and machine-readable.
- Allowed paths: CLI/core, packaging, tests, command/reference/troubleshooting docs.
- Implement: short commands, JSON errors, actionable recovery, idempotency,
  uninstall preview, no orphaned canonical data, and one visible upgrade
  transaction across Standalone, user-global, and Hub-owned surfaces:
  preflight doctor -> dry-run/diff -> checkpoint -> apply -> postflight health
  -> receipt/recovery. Text output includes title or compact description when
  rendering IDs, while machine-readable JSON remains stable.
- Accept: beginner and automation journeys both work; every mutation explains writes before apply; no text-mode command emits naked IDs unless an explicit machine-oriented option requests IDs only.
- Verify/evidence: command matrix and fresh/dirty/broken fixtures; `evidence/OW-100-05/`.
- Negative QA: interrupted or failed-postflight upgrade/uninstall is recoverable
  and never deletes user-authored knowledge or mistakes it for managed content.

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
- Outcome: beginner standalone, user-global power-user, Hub administrator,
  adapter-author, and maintainer paths are complete and source-linked.
- Allowed paths: `README.md`, `docs/`, `examples/`, docs reports/assets.
- Implement: benefits/use cases, easy standalone install, Core GA versus Hub
  Beta architecture, Research recall, Codex/Claude/Pi/generic MCP profiles,
  generic Hermes/OpenCode compatibility, three scopes, OIDC deployment, RAG,
  privacy, migrations, troubleshooting, three real or controlled case studies.
- Accept: docs match shipped commands and support tiers; user testing reaches first value and advanced setup.
- Verify/evidence: docs gates, command extraction tests, moderated journeys; `evidence/OW-100-07/`.
- Negative QA: stale command, missing limitation, inaccessible diagram, or unexplained term fails.

### OW-100-08 - Prove final Tier-1 and evidence-only golden journey

- Priority/dependencies: P0; `OW-100-04`, `OW-100-07`.
- Outcome: Codex, Claude Code, Pi, and generic MCP/CLI reach at least 95%
  declared contract equivalence and evidence reconstructs the full scoped
  Research-to-resume journey without chat.
- Allowed paths: conformance/golden fixtures, reports, release evidence/tests/docs.
- Implement: clean cross-platform run, recall-before-research, harness switch,
  structured Session Recap, failure/recovery, Candidate/Evidence writes,
  reviewed promotion, docs, RAG, project-user/user-global/enterprise isolation,
  and the Single-Org Hub Beta flow.
- Accept: every result links artifact, commit, gate, reviewer, and limitation; unsupported capabilities are explicit.
- Verify/evidence: final conformance and reconstruction suite; `evidence/OW-100-08/`.
- Negative QA: remove chat/session state and one evidence item; reconstruction must work in the first case and fail clearly in the second.

### OW-100-09 - Cut and verify v1.0 general availability artifacts

- Priority/dependencies: P0; `OW-100-08`.
- Outcome: clean, reproducible Core GA wheel/sdist plus explicitly labeled
  Single-Org Hub Beta artifact, release notes, support matrix,
  upgrade/uninstall proof, and final gate are ready for owner-controlled publication.
- Allowed paths: `VERSION`, `pyproject.toml`, `CHANGELOG.md`, workflows, release docs/manifests, artifact configuration.
- Implement: clean build, artifact inspection, fresh install, upgrades from
  supported versions, uninstall, offline smoke, provenance manifest, the
  transactional upgrade matrix for Standalone/user-global/Hub surfaces, and
  the deferred executed Windows/macOS/Linux wheel-only install smoke from
  `D-071-24`.
- Accept: `G-100-GA` passes with no unresolved P0/P1, no private path/secret, and no dirty tracked source state.
- Verify/evidence: full release commands and hashes plus clean Windows, macOS, and Linux wheel-only install transcripts; `evidence/OW-100-09/`.
- Negative QA: publishing/tagging remains owner-controlled; failed artifact or dirty worktree blocks GA.

### OW-100-10 - Align v1.0 closeout with the product owner

- Priority/dependencies: P0; `OW-100-09`.
- Outcome: the product owner receives the final evidence-linked v1.0 feature update, post-v1 questions, and explicitly authorizes or adjusts GA publication and post-v1 work.
- Allowed paths: `internal/owledge/workpackages/owledge-v1-autonomous-delivery/release-updates/`, `RUN-STATE.yaml`, `BACKLOG.yaml`, `TRACEABILITY.md`, release evidence/manifests, post-v1 backlog.
- Implement: create `release-updates/v1.0.md` from `ALIGNMENT-PROTOCOL.md`; reconcile the complete v1 plan against shipped scope, include support/compatibility position, final quality evidence, complete finding/decision/question registers, and a keep/amend/defer/drop post-v1 plan reflection; present it in chat and set the run state to `awaiting_user_alignment`.
- Accept: `G-100-GA` is green; the update contains all eleven required headings and no untracked claim, finding, or decision; post-v1 amendments validate; user `approve`, `adjust`, or `defer` is recorded with scope/constraints; only `approve` authorizes GA publication and v1 closeout.
- Verify/evidence: `python tools/validate_v1_delivery_plan.py`; required-heading check; update, decision, and evidence links under `evidence/OW-100-10/`.
- Negative QA: false GA claim, omitted finding/post-v1 item, absent plan reflection/decision, or autonomous publish/tag leaves the ticket blocked.

### OW-080-14 - Shard RUN-STATE into a pointer manifest + per-version registers (WS-B)

- Priority/dependencies: P1; `OW-071-09`, `OW-080-13`.
- Outcome: `RUN-STATE.yaml` becomes a <2KB pointer manifest (`active_version`, `active_ticket`, `active_gate`, `register_index`, `last_checkpoint_sha`); per-version findings/decisions/tickets/gates live in `registers/<v>/` and only the active-version register loads on cold resume; historical versions are pointer-reachable, not auto-loaded; stable `F-NN`/`D-NN` IDs and evidence SHAs are preserved (not renumbered); the live dogfood `RUN-STATE.yaml` used by paused OW-071-13 is not mutated by this ticket — the new schema ships behind a flag and dogfood migrates in a separate phase.
- Allowed paths: `RUN-STATE.yaml` schema, `registers/`, `tools/owledge.py`, `tools/owledge_core.py`, `skills/owledge-long-horizon-delivery/references/modes.md`, `ALIGNMENT-PROTOCOL.md`, migration fixtures/tests. Disjoint from OW-071-13's HTTP/security/control-plane-capability paths and from OW-080-13's per-entry trim paths.
- Implement: split `RUN-STATE` into a pointer manifest + per-version registers; gate loading on `active_version`; preserve stable `F-NN`/`D-NN` IDs and SHAs across the shard; add a migration tool that reads the legacy flat `RUN-STATE` and emits the sharded form without rewriting the live file until an explicit `migrate` command; keep the legacy flat form valid behind a flag.
- Accept: a cold resume loads only the pointer manifest + active-version register — strictly fewer file-content tokens than the pre-shard baseline, measured by a file-content tokenizer (sum of `token_count(loaded_file_content)`), not harness-reported context tokens; a stable finding ID resolves to the same content SHA before and after sharding; the legacy flat `RUN-STATE` still validates until an explicit migrate; the live paused-OW-071-13 `RUN-STATE.yaml` is byte-unchanged by this ticket.
- Verify/evidence: pointer-manifest size fixture (<2KB); before/after cold-resume file-content token delta; ID/SHA preservation round-trip; migration dry-run on a copy; `evidence/OW-080-14/`.
- Negative QA: an over-aggressive shard that hides a finding still affecting the active version fails; a renumbered ID/SHA fails; mutating the live `RUN-STATE.yaml` during this ticket fails; auto-loading a historical version on cold resume fails.

### OW-080-15 - Native harness/hooks integration, self-contained project scope, no manual calls (WS-F)

- Priority/dependencies: P1; `OW-080-01`.
- Outcome: a project-local `init-project`-ed host runs a full Claude Code session with zero external-path approval prompts; Owledge works as a structured layer (project and global scoped) without being called manually; the `SessionStart` context-injection hook emits a compact capsule read from project-local `OWLEDGE.md` + `.owledge/indexes/memory-index.jsonl`; `resolve_cli` no longer silently walks to an external checkout.
- Allowed paths: `plugins/owledge-cowork/`, `plugins/owledge-cowork/scripts/capture-claude-event.py`, `plugins/owledge-cowork/scripts/inject-owledge-context.py` (new), `.claude/settings.json` template, `docs/install-plugin.md`, `tools/owledge.py` (`init-project --include-plugin-adapter`), tests/docs. Disjoint from OW-071-13's and OW-080-13's paths.
- Implement: ship a project-local `.claude/settings.json` allow-list alongside `init-project --include-plugin-adapter` (allow the capture/inject hook commands + `tools/owledge_core.py` + `tools/owledge.py`); document/offer a project-local plugin install so `${CLAUDE_PLUGIN_ROOT}` resolves inside the project — update `docs/install-plugin.md:67-80`; guard `resolve_cli` (`capture-claude-event.py:48-57`) so the external-checkout fallback runs only when `OWLEDGE_ALLOW_GLOBAL_KIT` is set, otherwise fail-soft with a "run init-project" doctor hint; add a `SessionStart` context-injection hook that reads project-local `OWLEDGE.md` + `.owledge/indexes/memory-index.jsonl` and emits a compact capsule to stdout (promote `internal/owledge/ideas/pre-plan-idea-concept-harness-hooks.md`).
- Accept: a project-local `init-project`-ed host runs `SessionStart`/`UserPromptSubmit`/`PostToolUse`/`Stop` hooks with zero external-path approval prompts across a full session; the `SessionStart` injection hook emits a capsule without a manual `/owledge` call; a host without project-local tools and without `OWLEDGE_ALLOW_GLOBAL_KIT` fails soft with the doctor hint instead of issuing an external-path command; global-plugin install still works when the env var is set.
- Verify/evidence: a full-session prompt-count fixture (zero external-path approvals); injection-hook capsule content fixture; `resolve_cli` guard fixture (fail-soft without the env var, works with it); `evidence/OW-080-15/`.
- Negative QA: an external absolute path in any hook command under project-local install fails; `resolve_cli` silently walking to an external checkout without the env var fails; an injection capsule that loads more than the `OWLEDGE.md` + index capsule (e.g., full registers) violates the "load only essentials" contract and fails; a missing `OWLEDGE.md` must not crash the injection hook.
