---
title: "Owledge v1 Promotion Gates"
date: "2026-07-16"
version: "1.0.0"
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
scope: "v0.7.1-v1.0"
semantic_title: "Owledge v1 delivery promotion gates"
summary: "Executable phase-promotion contracts and evidence requirements for the Owledge v1 release train."
concept_tags: ["qa-gates", "release-promotion", "v1-roadmap"]
stack_tags: ["markdown", "python", "git"]
problem_patterns: ["false-promotion", "self-approval", "evidence-drift"]
architecture_patterns: ["gate-driven-delivery", "independent-qa", "evidence-manifests"]
failure_modes: ["waived-security-gate", "benchmark-gaming", "missing-evidence"]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-16T00:00:00Z"
updated_at: "2026-07-18T00:00:00Z"
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

# Owledge v1 Promotion Gates

## Common Gate Contract

Every gate starts from the tested integration commit and controlled environment recorded in `evidence/<gate-id>/manifest.yaml`. Entry requires all listed tickets `done`, a QA role distinct from every ticket owner, the independence mode recorded under `CONTROL-PLANE-POLICY.md`, and agreement among backlog, run state, tickets, commits, and evidence manifests. Commands run non-interactively; manual observations must be reproducible. Evidence must obey retention, redaction, and size policy. Security, privacy, data integrity, canonical-promotion, and acceptance boundaries are not silently waiverable. A release RC/GA gate authorizes only its user-alignment stop; publication and next-version execution require the matching alignment gate. Failure creates a finding and the smallest corrective ticket.

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
  clean human and agent demo setup/run/reset on Windows/macOS/Linux fixtures.
- Thresholds: all public docs English; five-second fixture identifies audience,
  problem, outcome, boundary, and next action; no install command before the
  minimum mental model; no unexplained prerequisite or working directory;
  primary adoption routes require no more than two navigation clicks; command
  chains pass 100%; every preset reports compressed artifact, installed CLI,
  and host-project footprint plus ownership; Principles-only writes=0;
  automation/responsibility and capability maturity are complete; fixture
  agents select the supported path and report exact writes; 30-second,
  no-write 30-second proof exposes its result and success signal; package-only
  five-minute and cross-session proofs pass; rerun is idempotent; Owlib cannot
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
- Commands: kit doctor; strict validation; public docs; quality ratchet; build; twine check; wheel/sdist inspection; wheel-based `uvx` help/quickstart/doctor.
- Thresholds: clean tracked source state; version alignment; all prior gates green; no private path/secret; artifacts install on supported fixtures.
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

### G-080-A-CONTRACTS - Portable contracts

- Tickets: `OW-080-01` through `OW-080-04`, `OW-080-12`.
- Commands: schema suites; migration round-trip; DAG/state-machine tests; checkpoint/evidence integrity tests; autonomous-profile default-off, consent, dependency-link, and no-dispatch fixtures.
- Thresholds: stable IDs/typed edges/unknown extensions preserved; cycles rejected; no done/accepted without gates/evidence; stale evidence rejected; atomic state consistency=100%; profile disabled means zero spawned lanes; unknown profile, missing consent, and overlapping lane fail closed.
- Demonstrable increment: human intent compiles into a ready ticket DAG and resumable state without prose-only completion; optional delivery planning produces a risk brief but cannot dispatch.
- Promotion: contract version is frozen for v0.8 implementation.

### G-080-B-CONTEXT - Context and small models

- Tickets: `OW-080-05`, `OW-080-06`, `OW-080-07`, `OW-080-13`, `OW-080-14`, `OW-080-15`.
- Commands: deterministic pack fixtures; synopsis freshness; active-tool tests; 4k/8k/16k tool-choice and structured-output matrix; false-pass/retry fixtures; legacy benchmark regression. Runtime-split for OW-080-13 evidence: under Codex `/goal` the worker runs and self-judges; under Claude Code `/goal` v2.1.139+ the worker runs every command and prints the command, stdout, exit code, and equality verdict to the transcript for the Haiku judge (which cannot run commands or open files). Commands: resume-context file-content token delta (`cold_resume_drain` + `warm_resume_drain`) with Codex `model_auto_compact_token_limit` ON; gate-result equality (both digests + diff to transcript); sidecar roundtrip (capped + reconstructed payloads to transcript); stale-handoff negative fixture (REJECT to transcript).
- Thresholds: identical digest for identical inputs; every selection/exclusion explained; Tier-1 4B/8k completion, tool-selection, contract-validity, retry, and false-pass thresholds pass; pack <= configured budget; legacy >=80% token/correct reduction; privacy/stale failures=0; `/goal` resume loads strictly fewer file-content tokens than the pre-OW-080-13 baseline for identical active state, reported as `cold_resume_drain` and `warm_resume_drain` in both runtimes (Codex `/goal` v0.128+ warm-resume persisted docs count as 0 newly loaded; Claude Code `/goal` v2.1.139+ counts the full post-`--resume` reload); capped gate error payload reconstructs the full payload from the sidecar (transcript-visible under Claude Code); stable IDs/SHAs and the owner-alignment stop unchanged, the stop verified by a verifiable command not protocol assertion alone.
- Demonstrable increment: a small local model plans, retrieves, and resumes using only the task pack.
- Promotion: context profile may be used by adapters.

### G-080-C-RETRIEVAL - Projection and safe migration

- Tickets: `OW-080-08`, `OW-080-09`.
- Commands: raw-vs-projection retrieval eval; chunk contract tests; 1k status benchmark; migration dry-run/apply/idempotency fixtures.
- Thresholds: raw frontmatter absent from embedding text; recall/ranking meets or improves baseline; privacy leak=0; duplicate chunk=0; status meets agreed p95; migration never silently overwrites user edits.
- Demonstrable increment: user previews migration, inspects status, and exports clean retrieval chunks.
- Promotion: retrieval projection and migration become supported v0.8 surfaces.

### G-080-RC - v0.8.0 release candidate

- Tickets: `OW-080-10` plus all earlier v0.8.0 gates.
- Commands: cumulative contract/context/retrieval suites; upgrade from v0.7.1; build/twine/wheel smoke; docs extraction.
- Thresholds: all v0.8 gates green; v0.7 regression green; schema/version/migration docs aligned; clean artifacts.
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

### G-081-A-ADAPTERS - Tier-1 conformance

- Tickets: `OW-081-01` through `OW-081-05`.
- Commands: common capability/manifest suite against Codex, Claude/Cowork, Hermes, generic MCP/CLI.
- Thresholds: 100% required read/control capabilities; unsupported optional capability explicitly reported; undeclared scope calls=0; artifact semantics equivalent.
- Demonstrable increment: same fixture can bootstrap and produce a task context/handoff in every profile.
- Promotion: profiles may be labelled Tier 1 for declared capabilities.

### G-081-B-CONCURRENCY - Git safety and recovery

- Tickets: `OW-081-06`, `OW-081-07`, `OW-081-08`, `OW-081-12`, `OW-081-13`.
- Commands: eight-worker non-overlap simulation; overlap/dirty/stale-base negatives; kill/retry matrix; hook and integration-manifest fixtures; skill classifier, consent, runtime dry-run, and capability-degradation fixtures.
- Thresholds: clobbered files=0; duplicate canonical writes=0; uncertain side effects block; overlaps require decision; every merged commit/evidence reachable; default-off profiles spawn zero lanes; high-risk dispatch has fresh approval; QA context is independent; Red Team is risk-triggered; unsupported runtime never launches silently.
- Demonstrable increment: after the user approves a displayed dry-run plan, parallel work is integrated after one worker is killed and resumed in another harness.
- Promotion: autonomous parallel execution may be enabled within declared lanes.

### G-081-C-JOURNEY - Scoped hub journey

- Tickets: `OW-081-09`, `OW-081-14`.
- Commands: Owlib project-filter/privacy fixtures; hub context determinism and relevance eval; edge-small task-capsule, budget, structured-output, fallback, and real local-model smoke fixtures.
- Thresholds: default all-project scan=never; unauthorized project results=0; every selected/excluded project and source explained; context budget honored; edge-small model receives no full-plan injection; unsupported authority actions=0; real local-model smoke evidence=present.
- Demonstrable increment: task context uses current project plus one explicit related project, while an edge-small model completes one declared bounded task from its capsule.
- Promotion: scoped cross-project context becomes supported preview.

### G-081-RC - v0.8.1 multi-agent release

- Tickets: `OW-081-10` plus all earlier v0.8.1 gates.
- Commands: complete golden multi-agent journey; cumulative conformance; release artifact and upgrade smoke.
- Thresholds: no chat dependency, silent degradation, clobber, or duplicate write; deliberate evidence failure blocks and recovers; all support claims evidence-linked.
- Demonstrable increment: plan-to-merge journey switches harness mid-ticket.
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
- Commands: ledger integrity; authority conflict; lifecycle matrix; privacy attack corpus.
- Thresholds: mutable/tampered event accepted=0; self-only approval=0; automatic canonical promotion=0; unsafe shared records=0; contradictions preserved=100%.
- Demonstrable increment: candidate with conflict is reviewed, rejected or promoted with complete evidence.
- Promotion: semantic write surfaces may be implemented.

### G-090-B-WRITES - Semantic writes and living docs

- Tickets: `OW-090-04`, `OW-090-05`, `OW-090-06`.
- Commands: MCP protocol/security/idempotency plus traversal, symlink, confused-deputy, oversized-payload, lock-theft, and prompt-injection attack corpus; docs compiler golden fixture; drift/impact precision.
- Thresholds: arbitrary write tool absent; replay/escape/symlink/confused-deputy/undeclared-scope/oversized/injected-instruction accepted=0; lock theft accepted=0; generated factual sections source-linked=100%; stale sources cannot be current.
- Demonstrable increment: agent appends evidence, requests promotion, compiles docs, then source change triggers targeted drift.
- Promotion: reviewed semantic writes may ship as opt-in profile.

### G-090-C-RAG - RAG and hub freshness

- Tickets: `OW-090-07`, `OW-090-08`, `OW-090-09`.
- Commands: JSONL round-trip; body-only vs title+summary+body vs semantic-tag evaluation over keyword/vector/hybrid modes, two embedding profiles, and multilingual terms; LightRAG reference; Owlib incremental/add-change-delete/interruption/source-unavailable fixtures.
- Thresholds: privacy leaks=0; raw frontmatter embedding=0; dedupe/tombstone accuracy=100%; unavailable source current-results=0; retrieval quality meets declared per-stratum thresholds; interrupted sync recovers atomically.
- Demonstrable increment: reviewed change flows through projection and LightRAG, then deletion removes it without changing canonical Markdown.
- Promotion: generic RAG contract stable; LightRAG remains optional adapter.

### G-090-RC - v0.9.0 release candidate

- Tickets: `OW-090-10` plus all earlier v0.9.0 gates.
- Commands: cumulative trust/write/RAG suites; default read-only install test; opt-in write profile test; build and upgrade smoke.
- Thresholds: default cannot write; policy-enabled semantic writes audited; RAG deletion proof present; all privacy gates green.
- Demonstrable increment: user enables one scoped write workflow and one RAG adapter safely.
- Promotion: technical candidate only; execute `G-090-ALIGNMENT` before publication/tag or v1.0 work.

### G-090-ALIGNMENT - v0.9.0 user alignment

- Tickets: `OW-090-11`.
- Commands: `python tools/validate_v1_delivery_plan.py`; required-heading check for `release-updates/v0.9.0.md`; evidence and source-link review.
- Thresholds: `G-090-RC` green; update has all eleven protocol headings; privacy, semantic-write, RAG, Owlib, and finding claims link evidence; finding/decision/question registers and v1.0 plan reflection are complete or explicitly `None`; user decision is explicit and recorded.
- Demonstrable increment: the product owner can assess trusted-write boundaries and final-v1 scope without reopening planning history.
- User alignment: agent stops in `awaiting_user_alignment`; only user `approve` unlocks v1.0 and optional publication, while `adjust`/`defer` remain blocked.
- Promotion: user-approved alignment authorizes recorded publication constraints and v1.0 execution.

## v1.0 Gates

### G-100-A-HARDENING - Security and scale

- Tickets: `OW-100-01`, `OW-100-02`, `OW-100-03`.
- Commands: hardware-independent deterministic correctness suite; 10/1k/10k cold/warm benchmark with environment profile; security attack corpus; evidence retention/redaction/size checks; malicious extension/update fixtures.
- Thresholds: deterministic correctness always passes; published p95/resource targets met or explicit non-promotable limitation; unsafe shared export=0; raw transcripts committed=0; oversized committed evidence=0; undeclared extension scope=0; permission expansion requires approval.
- Demonstrable increment: 10k project compiles scoped context and rejects malicious content/extension.
- Promotion: v1 security and performance claims may be drafted.

### G-100-B-PRODUCT - Outcomes and lifecycle

- Tickets: `OW-100-04`, `OW-100-05`, `OW-100-06`.
- Commands: versioned development and sealed held-out outcome evaluation; small-model tool-choice/structured-output/false-pass matrix; stratified RAG retrieval evaluation; CLI command matrix; install/upgrade/interruption/uninstall fixtures; claim-to-proof audit.
- Thresholds: token savings cannot mask quality loss; legacy >=80%; held-out correctness non-regressing; Tier-1 small-model completion/tool-selection/contract-validity thresholds pass; RAG per-stratum thresholds pass; mutations support preview/JSON; user knowledge survives uninstall; every claim has tier/version/evidence/limitation.
- Demonstrable increment: beginner and automated client complete lifecycle and recover from interrupted upgrade.
- Promotion: product surface freezes for v1 docs.

### G-100-C-PROOF - Documentation and final journey

- Tickets: `OW-100-07`, `OW-100-08`.
- Commands: docs link/accessibility/command extraction; moderated beginner/power-user journeys; four-profile conformance; evidence-only reconstruction.
- Thresholds: public docs English; first-value journey succeeds without maintainer; Tier-1 declared equivalence >=95%; missing evidence fails clearly; no chat history required.
- Demonstrable increment: complete v1 story from install through reviewed knowledge and RAG citation.
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
