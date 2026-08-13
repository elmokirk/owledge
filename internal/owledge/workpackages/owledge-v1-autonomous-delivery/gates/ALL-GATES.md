---
title: "Owledge V1 Minimal Core Promotion Gates"
date: "2026-08-11"
version: "3.0.0"
document_version: 5
memory_id: "mem:owledge:global:owledge:qa:v1-delivery-gate-catalog"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "gate_catalog"
status: "active"
visibility: "private"
data_class: "internal"
project: "owledge"
scope: "v1-minimal-core"
semantic_title: "Owledge V1 minimal core promotion gates"
summary: "Executable promotion contracts for the active minimal-Core V1 train; completed OW-071/080/081 gates are evidence history."
concept_tags: ["qa-gates", "release-promotion", "v1-roadmap"]
stack_tags: ["markdown", "python", "git"]
problem_patterns: ["false-promotion", "self-approval", "evidence-drift"]
architecture_patterns: ["gate-driven-delivery", "independent-qa", "evidence-manifests"]
failure_modes: ["waived-security-gate", "benchmark-gaming", "missing-evidence"]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-16T00:00:00Z"
updated_at: "2026-08-13T00:00:00+02:00"
source_hash: ""
owners:
  - "release-assurance"
tags:
  - "gates"
  - "qa"
  - "release"
reusable_lessons: []
edges: []
---

# Owledge V1 Minimal Core Promotion Gates

## Active V1M gate catalog

The active V1 surface is Principles, deterministic local Core, private local
`user_global` and Codex/Claude/generic MCP/CLI adapters. Pi, Hub, LightRAG,
Documentation Compiler, supply-chain manifests, enterprise-provider matrices,
and generic JSONL export are parked. They cannot appear in a V1M threshold,
claim or release witness.

## Common Gate Contract

Every gate starts from the tested integration commit and controlled environment recorded in `evidence/<gate-id>/manifest.yaml`. Entry requires all listed tickets `done`, a QA role distinct from every ticket owner, the independence mode recorded under `CONTROL-PLANE-POLICY.md`, and agreement among backlog, run state, tickets, commits, and evidence manifests. Commands run non-interactively; manual observations must be reproducible. Evidence must obey retention, redaction, and size policy. Security, privacy, data integrity, canonical-promotion, and acceptance boundaries are not silently waiverable. A release RC/GA gate authorizes only its user-alignment stop; publication and next-version execution require the matching alignment gate. Failure creates a finding and the smallest corrective ticket.

### G-V1M-PLAN - Minimal Core control-plane reconciliation

- Tickets: `V1M-01`.
- Commands: `python tools/validate_v1_delivery_plan.py`; `python -m unittest tests.unit.test_validate_v1_delivery_plan -v`; deterministic frontmatter and traceability checks; `git diff --check`.
- Thresholds: every unstarted `OW-*` ticket is mapped to one V1M ticket or a `PARK-*` record; all active gates/waves/dependencies contain only V1M tickets; active state names one plan; budget is exactly 8 CLI verbs, 5 MCP tools, 2 scopes, 3 adapters, <=15 files and <=8 directories; G-081-A evidence is referenced but not rerun.
- Demonstrable increment: a fresh agent can select only V1M-02 after reading the compact active control plane.
- Promotion: permits V1M-02 and V1M-03 only; it does not authorize runtime scope expansion, publication, tag, push or release.

### G-V1M-SURFACE - Principles, minimal profile and public facade

- Tickets: `V1M-02`, `V1M-03`.
- Commands: fresh principles/minimal/full profile tests; default-help snapshot; package-resource and upgrade-preservation tests.
- Thresholds: Principles has no Core installation requirement; minimal footprint is within budget; default help has exactly eight operations; full/maintainer is explicit.
- Demonstrable increment: a new user starts Principles or installs the compact local Core without dogfood trees.
- Promotion: permits V1M-04 and V1M-05.

### G-V1M-READ - Local Null-Space, recall and context

- Tickets: `V1M-04`, `V1M-05`.
- Commands: linked two-project local fixture; direct-scan/rebuilt-index equivalence; purpose/budget/permission negative corpus.
- Thresholds: two scopes only; no implicit discovery/network; recall and context are source-linked, deterministic and budgeted.
- Demonstrable increment: a reviewed local fact is found across explicit projects without full-history injection.
- Promotion: permits V1M-06 and V1M-07.

### G-V1M-LIFECYCLE - Candidate, review, tombstone and health

- Tickets: `V1M-06`, `V1M-07`.
- Commands: Candidate/park/resurface, review conflict, deletion/rebuild and privacy-safe doctor fixtures.
- Thresholds: raw/parked ordinary recall count=0; planning resurfacing has matching reason/trigger; transitions and tombstones are idempotent; health leaks no body content.
- Demonstrable increment: a valuable deferred idea is safely preserved and later reconsidered without becoming active work.
- Promotion: permits V1M-08.

### G-V1M-ADAPTERS - Thin reference adapters

- Tickets: `V1M-08`.
- Commands: common Codex/Claude/generic conformance journey; MCP-tool allowlist; adapter boundary scan; G-081-A evidence reference review.
- Thresholds: exactly three reference adapters and five MCP tools; no adapter forks Core search/storage/lifecycle/migration; degradation is explicit.
- Demonstrable increment: a user resumes the same local journey from any supported harness.
- Promotion: permits V1M-09.

### G-V1M-GA - Minimal Core candidate

- Tickets: `V1M-09`, `V1M-10`.
- Commands: fresh install, preview upgrade, interrupted recovery, offline/security-negative corpus, compact journey, wheel/sdist inspection and docs claim-map.
- Thresholds: no unresolved P0/P1; no V1 claim depends on parked work; package/prompt privacy is clean; Windows proof is executed and macOS/Linux wheel-only proof is executed before publication.
- Demonstrable increment: a clean local GA candidate proves the complete V1 daily journey.
- Promotion: creates the owner publication decision only; no push, tag, release, upload or publication is authorized.

### G-V1M-PUBLISH - Owner-controlled external action

- Tickets: `V1M-11`.
- Commands: inspect the explicit owner authorization, candidate commit and artifact hashes.
- Thresholds: authorization names the exact candidate and each external action; otherwise status remains blocked.
- Demonstrable increment: external state changes are impossible through generic approval.
- Promotion: only the exact authorized action.

## Historical completed gate catalog (non-selectable evidence only)

## v0.7.1 Gates

### G-071-A-TRUTH - Truth and baseline

- Tickets: `OW-071-01`, `OW-071-02`, `OW-071-03`, `OW-071-13`.
- Commands: `python tools/validate_v1_delivery_plan.py`;
  `python tools/validate_live_work_register.py --project-root .`;
  `python -m pytest tests/unit/test_validate_live_work_register.py -q`;
  focused FB-019/020/021 tests; public docs; Benchmark Kit CI and held-out
  comparison; local HTTP auth, Endpoint x Role x Tenant authorization matrix,
  health-disclosure, remote-bind, body-size, timeout, concurrency, rate, and
  stable error-code negative fixtures.
- Thresholds: delivery-plan contract errors=0; zero active version
  contradictions; zero dead retained flags; malformed upgrade note fails;
  token/correct reduction >=80%; retrieval quality non-regressing; privacy and
  stale failures=0; unsupported remote bind fails; unauthenticated local path
  disclosure=0; cross-tenant writes=0; every endpoint and administrator action
  has an explicit tenant rule; every published bound has boundary/over-limit
  coverage.
- Demonstrable increment: an agent selects the first real open ticket from the live register and reproduces the benchmark baseline.
- Promotion: pass enables adoption and compatibility work; failure blocks all later releases.

### G-071-B-ADOPTION - Beginner first value

- Tickets: `OW-071-04`, `OW-071-10`, `OW-071-11`, `OW-071-12`, `OW-071-14`, `OW-071-05`.
- Commands: docs link/lint and claim-map gates; Mermaid source validation;
  extracted-command smoke for every install route; host-project agent scenarios;
  clean human and agent demo setup/run/reset on the supported Windows fixture
  plus the tracked Windows/macOS/Linux CI fixture contract. Under `D-071-24`,
  executed macOS/Linux package transcripts remain mandatory Stable/GA evidence
  in `OW-100-09`, not a v0.7.1 cross-platform support claim.
- Thresholds: all public docs English; five-second fixture identifies audience,
  problem, outcome, boundary, and next action; no install command before the
  minimum mental model; no unexplained prerequisite or working directory;
  primary adoption routes require no more than two navigation clicks; command
  chains pass 100%; every preset reports compressed artifact, installed CLI,
  and host-project footprint plus ownership; Principles-only writes=0;
  automation/responsibility and capability maturity are complete; fixture
  agents select the supported path and report exact writes; 30-second,
  no-write 30-second proof exposes its result and success signal; the bounded
  Windows package-only five-minute and cross-session proofs pass; rerun is
  idempotent; Owlib cannot
  be labelled available/current before `G-071-C-COMPAT` is green;
  privacy, Hub-conflation, and unsupported-runtime overclaim failures=0.
- Demonstrable increment: a vibecoder or coding agent understands
  why/when/how, distinguishes footprint from delivery and runtime integration,
  installs, runs one feature journey, and sees scoped-context benefit.
- Promotion: pass permits v0.7.1 public adoption claims.

### G-071-C-COMPAT - Owlib and Hermes preview

- Tickets: `OW-071-06`, `OW-071-07`.
- Commands: Owlib unit/quality tests; current/legacy sync fixtures; MCP protocol smoke; Hermes pinned fixture.
- Thresholds: current `.owledge` layout is default; unsafe/unreviewed imports rejected; Hermes read-only tools pass; path escape and unbound project fail.
- Demonstrable increment: one local project and one VPS-style fixture are read by Hermes without permanent prompt injection.
- Promotion: pass labels Owlib preview and Hermes read-only profile accurately.

### G-071-RC - v0.7.1 release candidate

- Tickets: `OW-071-08` plus all earlier v0.7.1 gates.
- Commands: focused generated-host/Kit `upgrade-drift` regression; full
  `python tools/owledge.py finalization-gates --project-root .
  --include-compliance --include-exports`; build; twine check; wheel/sdist
  inspection; wheel-based `uvx` help/quickstart/doctor.
- Thresholds: clean committed tracked source state; aggregate finalization
  38/38 including `upgrade-drift`; terminal JSON manifest present; bounded gate
  progress/durations observable; version alignment; all prior gates green; no
  private path/secret; artifacts install on supported fixtures.
- Demonstrable increment: fresh user installs v0.7.1 and completes the golden demo.
- Promotion: technical candidate only; execute `G-071-ALIGNMENT` before publication/tag or v0.8.0 work.

### G-071-ALIGNMENT - v0.7.1 user alignment

- Tickets: `OW-071-09`.
- Commands: `python tools/validate_v1_delivery_plan.py`; required-heading check for `release-updates/v0.7.1.md`; evidence and source-link review.
- Thresholds: `G-071-RC` green; update has all eleven protocol headings; every claim and finding links evidence; finding/decision/question registers and v0.8.0 plan reflection are complete or explicitly `None`; user decision is explicit and recorded.
- Demonstrable increment: the product owner can assess v0.7.1 benefits, compatibility, proof, limitations, and exact v0.8.0 implications without chat reconstruction.
- User alignment: agent stops in `awaiting_user_alignment`; only user `approve` unlocks v0.8.0 and optional publication, while `adjust`/`defer` remain blocked.
- Promotion: user-approved alignment authorizes recorded publication constraints and v0.8.0 execution.

## v0.8.0 Gates

### G-080-A-CONTRACTS - Portable contracts and Research Memory

- Tickets: `OW-080-01` through `OW-080-04`, `OW-080-16`.
- Commands: common-envelope and artifact-profile schema suites; layered-settings
  and policy-widening fixtures; migration round-trip; DAG/state-machine tests;
  checkpoint/evidence integrity tests; Research contract round-trip,
  recall/dedup/freshness, scope-isolation, rename-stability, delta-brief,
  `ResourceRef`, Managed Surface Manifest, module-contract, and health-profile
  boundary fixtures.
- Thresholds: stable IDs/typed edges/namespaced inert extensions preserved;
  material edit without exactly one monotonic document-version bump accepted=0;
  schema/profile migrations remain distinguishable from document revisions;
  unknown Core keys and authority-widening settings accepted=0; effective policy
  has an explanation receipt; cycles
  rejected; no done/accepted without gates/evidence; stale evidence rejected;
  atomic state consistency=100%; current immutable, versioned, and mutable
  sources receive correct freshness results; authorized fresh coverage returns
  `sufficient_current`; external search calls from deterministic recall=0;
  cross-scope findings=0; arbitrary resource-path authority=0; extensions
  bypassing Core policy or storage seams=0.
- Demonstrable increment: human intent compiles into a ready ticket DAG and an
  agent can determine whether prior Research Memory is current, stale, partial,
  missing, or conflicted before opening the web.
- Promotion: contract version is frozen for v0.8 implementation.

### G-080-B-CONTEXT - Context and small models

- Tickets: `OW-080-05`, `OW-080-06`, `OW-080-07`, `OW-080-13`, `OW-080-14`, `OW-080-15`.
- Commands: deterministic pack fixtures; Research recall-before-context and
  recall-before-external-research fixtures; synopsis freshness; active-tool
  tests; 4k/8k/16k tool-choice and structured-output matrix; false-pass/retry
  fixtures; legacy benchmark regression. Runtime-split for OW-080-13 evidence:
  under Codex `/goal` the worker runs and self-judges; under Claude Code `/goal`
  v2.1.139+ the worker runs every command and prints the command, stdout, exit
  code, and equality verdict to the transcript for the Haiku judge (which cannot
  run commands or open files). Commands: resume-context file-content token delta
  (`cold_resume_drain` + `warm_resume_drain`) with Codex
  `model_auto_compact_token_limit` ON; gate-result equality (both digests + diff
  to transcript); sidecar roundtrip (capped + reconstructed payloads to
  transcript); stale-handoff negative fixture (REJECT to transcript).
- Thresholds: identical digest for identical inputs; every selection/exclusion explained; Tier-1 4B/8k completion, tool-selection, contract-validity, retry, and false-pass thresholds pass; pack <= configured budget; legacy >=80% token/correct reduction; privacy/stale failures=0; `/goal` resume loads strictly fewer file-content tokens than the pre-OW-080-13 baseline for identical active state, reported as `cold_resume_drain` and `warm_resume_drain` in both runtimes (Codex `/goal` v0.128+ warm-resume persisted docs count as 0 newly loaded; Claude Code `/goal` v2.1.139+ counts the full post-`--resume` reload); capped gate error payload reconstructs the full payload from the sidecar (transcript-visible under Claude Code); stable IDs/SHAs and the owner-alignment stop unchanged, the stop verified by a verifiable command not protocol assertion alone.
- Demonstrable increment: a small local model plans, reuses current Research
  Memory, retrieves, and resumes using only the task pack.
- Promotion: context profile may be used by adapters.

### G-080-C-RETRIEVAL - Projection and safe migration

- Tickets: `OW-080-08`, `OW-080-09`.
- Commands: raw-vs-projection retrieval eval; Research source/finding/synthesis
  dedupe and freshness projection; chunk contract tests; 10/1k deterministic
  Knowledge Health fixtures with seeded revision, duplicate, edge, source,
  freshness, budget, and projection faults; managed-surface ownership plus
  migration preflight/dry-run/checkpoint/apply/postflight/receipt/recovery fixtures.
- Thresholds: raw frontmatter absent from embedding text; recall/ranking meets
  or improves baseline; source revision and freshness survive projection;
  privacy leak=0; duplicate chunk=0; seeded health issue detection=100%; model
  calls from health=0; knowledge bodies in health output=0; status meets agreed
  p95; migration never silently overwrites user edits; failed postflight has a
  verified recovery path.
- Demonstrable increment: user previews migration, inspects actionable
  Knowledge Health, and exports clean retrieval chunks.
- Promotion: retrieval projection and migration become supported v0.8 surfaces.

### G-080-RC - v0.8.0 release candidate

- Tickets: `OW-080-10` plus all earlier v0.8.0 gates.
- Commands: cumulative contract/context/retrieval suites; frozen v0.7 legacy-regression replay; upgrade from v0.7.1; build/twine/wheel smoke; docs extraction. No new comparative benchmark campaign runs at this gate.
- Thresholds: all v0.8 gates green; frozen v0.7 regression green; schema/version/migration docs aligned; clean artifacts. New performance/quality claims are prohibited; the release-wide comparative evaluation is deferred to `OW-100-04`/`G-100-B-PRODUCT`.
- Demonstrable increment: fresh and upgraded projects complete planning-to-context journey.
- Promotion: technical candidate only; execute `G-080-ALIGNMENT` before publication/tag or v0.8.1 work.

### G-080-ALIGNMENT - v0.8.0 user alignment

- Tickets: `OW-080-11`.
- Commands: `python tools/validate_v1_delivery_plan.py`; required-heading check for `release-updates/v0.8.0.md`; evidence and source-link review.
- Thresholds: `G-080-RC` green; update has all eleven protocol headings; contract, migration, small-model, retrieval, and finding claims link evidence; finding/decision/question registers and v0.8.1 plan reflection are complete or explicitly `None`; user decision is explicit and recorded.
- Demonstrable increment: the product owner can assess v0.8.0 adoption impact and v0.8.1 scope without reopening planning history.
- User alignment: agent stops in `awaiting_user_alignment`; only user `approve` unlocks v0.8.1 and optional publication, while `adjust`/`defer` remain blocked.
- Promotion: user-approved alignment authorizes recorded publication constraints and v0.8.1 execution.

## v0.8.1 Gates

### G-081-A-ADAPTERS - Three-profile adapter conformance

- Tickets: `OW-081-01`, `OW-081-02`, `OW-081-03`, `OW-081-05`.
- Commands: common capability/manifest suite against Codex, Claude Code, and
  generic MCP/CLI. Hermes, OpenCode, and Pi are post-V1 generic consumers and
  are neither executed V1 profiles nor V1 claims.
- Thresholds: 100% required read/control capabilities; unsupported optional capability explicitly reported; undeclared scope calls=0; artifact semantics equivalent.
- Demonstrable increment: same fixture can bootstrap and produce a task context/handoff in every profile.
- Promotion: profiles may be labelled Tier 1 for declared capabilities.

### G-081-B-CONCURRENCY - Session continuity and recovery

- Tickets: `OW-081-07`, `OW-081-08`.
- Commands: kill/retry and harness-switch matrix; hook and integration-manifest
  fixtures; structured Session Recap schema, evidence-link, privacy, idempotency,
  and no-raw-transcript fixtures.
- Thresholds: duplicate canonical writes=0; uncertain side effects block;
  checkpoint input/output hashes reconcile; Session Recap Candidates include
  outcomes, decisions, learnings, gotchas, open questions, Evidence, affected
  artifacts, and Research/Promotion Candidates; canonical auto-promotion=0;
  unsupported hooks fail visibly.
- Demonstrable increment: a stopped session creates a compact private recap and
  another harness resumes exact work without chat history.
- Promotion: structured continuity and recovery may be enabled by declared adapters.

### G-081-C-JOURNEY - Local user-global Null-Space journey

- Tickets: `OW-081-09`.
- Commands: Owlib project-filter/privacy fixtures; `project_user` and private
  local `user_global` namespace isolation; Research and general
  context determinism, freshness, and relevance evaluation; two-harness local
  `user_global` reference composition with network upload disabled.
- Thresholds: default all-project scan=never; unauthorized project/scope
  results=0; every selected/excluded project, scope, source revision, and
  freshness state is explained; context budget honored; caller paths grant no authority.
- Demonstrable increment: two V1 harnesses use the same private local user-global
  federation for the current project plus one explicitly authorized related
  project; no network upload or remote synchronization is possible.
- Promotion: scoped cross-project context becomes supported preview.

### G-081-RC - v0.8.1 reference-adapter release

- Tickets: `OW-081-10` plus all earlier v0.8.1 gates.
- Commands: Research-to-resume cross-harness journey; cumulative conformance;
  release artifact and upgrade smoke.
- Thresholds: no chat dependency, silent degradation, clobber, or duplicate write; deliberate evidence failure blocks and recovers; all support claims evidence-linked.
- Demonstrable increment: research recall, task work, recap, and resume switch
  from one reference harness to another mid-ticket.
- Promotion: technical candidate only; execute `G-081-ALIGNMENT` before publication/tag or v0.9.0 work.

### G-081-ALIGNMENT - v0.8.1 user alignment

- Tickets: `OW-081-11`.
- Commands: `python tools/validate_v1_delivery_plan.py`; required-heading check for `release-updates/v0.8.1.md`; evidence and source-link review.
- Thresholds: `G-081-RC` green; update has all eleven protocol headings; Tier-1 claims, Hermes boundary, degradation, golden-journey findings link evidence; finding/decision/question registers and v0.9.0 plan reflection are complete or explicitly `None`; user decision is explicit and recorded.
- Demonstrable increment: the product owner can assess agentic-coding readiness and v0.9.0 risk without reopening planning history.
- User alignment: agent stops in `awaiting_user_alignment`; only user `approve` unlocks v0.9.0 and optional publication, while `adjust`/`defer` remain blocked.
- Promotion: user-approved alignment authorizes recorded publication constraints and v0.9.0 execution.

## v0.9.0 Gates

### G-090-A-TRUST - Evidence, authority, promotion, privacy

- Tickets: `OW-090-01`, `OW-090-02`, `OW-090-03`.
- Commands: ledger integrity; source-revision and research-reason traceability;
  authority conflict; local project/user-global lifecycle matrix; private global raw-inbox
  retrieval exclusion, bounded delta-capsule and policy-snapshot fixtures,
  reviewed global-essence/project-drill-down relations, promote/reject/archive
  receipts; privacy attack corpus.
- Thresholds: mutable/tampered event accepted=0; research finding without source
  and reason accepted=0; self-only approval=0; automatic canonical promotion=0;
  pointer-only promotable delta accepted=0; raw-inbox records in normal
  retrieval=0; full snapshot without purpose/scope/TTL accepted=0; reasonless
  discard=0; unsafe shared records=0; contradictions preserved=100%.
- Demonstrable increment: a source-linked Research Candidate with conflict is
  reviewed, rejected, or promoted to an authorized scope with complete evidence.
- Promotion: semantic write surfaces may be implemented.

### G-090-B-WRITES - Local semantic writes and Knowledge Health

- Tickets: `OW-090-04`, `OW-090-06`.
- Commands: MCP protocol/security/idempotency plus traversal, symlink,
  confused-deputy, oversized-payload, lock-theft, and prompt-injection attack
  corpus; expected-document-revision/base-hash conflict and replay matrix;
  Research Candidate and delta-refresh contracts; source-mutability-aware
  freshness, review-debt, stale-source and Knowledge Health precision,
  including raw-inbox debt and unresolved drill-down sources.
- Thresholds: arbitrary write tool absent; replay/escape/symlink/confused-deputy/undeclared-scope/oversized/injected-instruction accepted=0; lock theft accepted=0; lost accepted revisions=0; every write returns idempotent success or explicit conflict/reconciliation receipt; generated factual sections source-linked=100%; stale sources cannot be current.
- Demonstrable increment: agent appends evidence, requests promotion, then a
  mutable source change triggers a targeted local Research delta brief.
- Promotion: reviewed semantic writes may ship as opt-in profile.

### G-090-C-RAG - Local index freshness and tombstones

- Tickets: `OW-090-09`.
- Commands: local project/user-global Owlib Research/general
  incremental add/change/delete/interruption/source-unavailable fixtures;
  reviewed-global-essence-first recall plus authorized/denied/missing/stale
  project deep-dive matrix; source-withdrawal/access-revocation propagation
  across essences, drill-down refs, exports, and derived namespaces.
- Thresholds: privacy leaks=0; raw frontmatter embedding=0; withdrawn-source
  retrievable shadows=0; dedupe/tombstone
  accuracy=100%; unavailable source current-results=0; unauthorized deep-dive
  results=0; essence answers retain exact source revision refs=100%; retrieval
  quality meets declared per-stratum thresholds; interrupted sync recovers atomically.
- Demonstrable increment: reviewed local change flows through the local index,
  then deletion removes it without changing canonical Markdown.
- Promotion: local index freshness is stable; export/adapters remain post-V1.

### G-090-RC - v0.9.0 release candidate

- Tickets: `OW-090-10` plus all earlier v0.9.0 gates.
- Commands: cumulative trust/write/local-index suites; default read-only install test; opt-in write profile test; build and upgrade smoke.
- Thresholds: default cannot write; policy-enabled semantic writes audited; local tombstone deletion proof present; all privacy gates green.
- Demonstrable increment: user enables one scoped local write workflow safely.
- Promotion: technical candidate only; execute `G-090-ALIGNMENT` before publication/tag or v1.0 work.

### G-090-ALIGNMENT - v0.9.0 user alignment

- Tickets: `OW-090-11`.
- Commands: `python tools/validate_v1_delivery_plan.py`; required-heading check for `release-updates/v0.9.0.md`; evidence and source-link review.
- Thresholds: `G-090-RC` green; update has all eleven protocol headings; privacy, semantic-write, RAG, Owlib, and finding claims link evidence; finding/decision/question registers and v1.0 plan reflection are complete or explicitly `None`; user decision is explicit and recorded.
- Demonstrable increment: the product owner can assess trusted-write boundaries and final-v1 scope without reopening planning history.
- User alignment: agent stops in `awaiting_user_alignment`; only user `approve` unlocks v1.0 and optional publication, while `adjust`/`defer` remain blocked.
- Promotion: user-approved alignment authorizes recorded publication constraints and v1.0 execution.

## v1.0 Gates

### G-100-A-HARDENING - Core security and reproducible scale smokes

- Tickets: `OW-100-01`, `OW-100-02`.
- Commands: hardware-independent deterministic correctness suite; small/medium/
  large local cold/warm smoke with environment profile; Core security attack
  corpus; evidence retention/redaction/size checks; local MCP/HTTP scope-deny,
  restart/recovery, and Knowledge Health scale fixtures.
- Thresholds: deterministic correctness always passes; local p95/resource bounds
  are met or explicitly non-promotable; unsafe export=0; raw transcripts and
  oversized evidence committed=0; undeclared local scope=0; cross-project/scope
  result=0; agent direct canonical promotion=0; standalone regression=green;
  private `user_global` upload=0; seeded health faults missed=0; raw prompt,
  output, or knowledge body in reports=0.
- Demonstrable increment: reproducible small/medium/large local fixtures compile
  scoped context and reject malicious content without remote identity.
- Promotion: v1 security and performance claims may be drafted.

### G-100-B-PRODUCT - Core journey regression and lifecycle

- Tickets: `OW-100-04`, `OW-100-05`, `OW-100-06`.
- Commands: core-journey regression evaluation; recall-before-research,
  stale/partial/conflict and delta-only refresh matrix; adapter contract matrix;
  project/user-global authorization tests; CLI command matrix; Standalone/user-global
  install/upgrade/interruption/postflight-recovery/uninstall fixtures;
  claim-to-proof audit.
- Thresholds: regression cannot mask correctness loss; legacy >=80%; fresh
  Research prevents redundant refresh; stale/partial/conflicted Research never
  passes as current; three-profile contract-validity thresholds pass; scope
  leak=0; mutations support preview/JSON; user knowledge survives uninstall;
  every claim has tier/version/evidence/limitation.
- Demonstrable increment: beginner and automated client complete lifecycle and recover from interrupted upgrade.
- Promotion: product surface freezes for v1 docs.

### G-100-C-PROOF - Core documentation and final journey

- Tickets: `OW-100-07`, `OW-100-08`.
- Commands: docs link/accessibility/command extraction; moderated standalone and
  user-global journeys; Codex/Claude/generic MCP conformance; evidence-only
  reconstruction. No Pi, Hub, or enterprise runtime witness is a V1 requirement.
- Thresholds: public docs English; first-value journey succeeds without
  maintainer; three-profile declared equivalence >=95%; no Hub/Pi Tier-1 claim;
  missing evidence fails clearly; no chat history required.
- Demonstrable increment: complete V1 story from standalone install through
  local user-global Research reuse, reviewed knowledge, and three-profile usage.
- Promotion: v1 release artifacts may be cut.

### G-100-GA - v1.0 general availability

- Tickets: `OW-100-09` plus every earlier gate.
- Commands: clean-source finalization gates; full test/eval/conformance matrix; build/twine; artifact inspection; fresh install; supported upgrades; uninstall; offline smoke; private path/secret scans.
- Thresholds: every prior gate green; unresolved P0/P1=0; dirty tracked source=0; version mismatch=0; artifact secret/private path=0; evidence manifest complete and hashed.
- Demonstrable increment: a clean machine can install the artifacts and reproduce the documented golden journey.
- Promotion: technical GA candidate only; execute `G-100-ALIGNMENT` before publication/tag or v1 closeout.

### G-100-ALIGNMENT - v1.0 user closeout

- Tickets: `OW-100-10`.
- Commands: `python tools/validate_v1_delivery_plan.py`; required-heading check for `release-updates/v1.0.md`; final evidence and source-link review.
- Thresholds: `G-100-GA` green; update has all eleven protocol headings; shipped scope, support, quality, compatibility, findings, and post-v1 claims link evidence; finding/decision/question registers and post-v1 plan reflection are complete or explicitly `None`; user decision is explicit and recorded.
- Demonstrable increment: the product owner can approve or adjust v1.0 GA with a complete evidence-backed product handover.
- User alignment: agent stops in `awaiting_user_alignment`; only explicit user `approve` authorizes publication/tag and v1 closeout; `adjust`/`defer` remain blocked.
- Promotion: user-approved alignment authorizes recorded v1.0 GA publication constraints; agents still never publish autonomously.
