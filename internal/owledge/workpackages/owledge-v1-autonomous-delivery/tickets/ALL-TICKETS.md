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
updated_at: "2026-07-16T00:00:00Z"
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

## v0.7.1 - Adoption, Truth, and Compatibility

### OW-071-01 - Normalize live work state

- Priority/dependencies: P0; none.
- Outcome: one live register accurately distinguishes shipped, open, superseded, and deferred work.
- Allowed paths: `ROADMAP.md`, `docs/strategic-roadmap-2026-2027.md`, `internal/owledge/plans/`, this control plane.
- Implement: reconcile FB-001 through FB-021, v0.7 checklists, Owlib status, adapter claims, and version evidence; archive or supersede stale active claims without deleting history.
- Accept: every open item has state, source, acceptance gap, target release, owner role, and evidence link; no active document contradicts `VERSION` or `pyproject.toml`.
- Verify/evidence: `python tools/validate_v1_delivery_plan.py`, roadmap status validator, plus `python tools/owledge.py test public-docs --project-root .`; `evidence/OW-071-01/`.
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

### OW-071-04 - Rewrite adoption-first English documentation

- Priority/dependencies: P0; `OW-071-02`.
- Outcome: README and Easy Install answer why, when, how, benefits, privacy, and removal for a beginner.
- Allowed paths: `README.md`, `docs/README.md`, `docs/try-owledge-in-5-minutes.md`, new English beginner docs, docs navigation.
- Implement: two paths—beginner local setup and agent/MCP setup; define terms inline; show first value before architecture; include expected output and recovery.
- Accept: moderated fixture users can select an install path and reach first success without maintainer interpretation.
- Verify/evidence: docs link/lint gates and scripted fresh-install walkthrough; `evidence/OW-071-04/`.
- Negative QA: no step assumes MCP, Git, Python packaging, or frontmatter knowledge without explanation.

### OW-071-05 - Ship the vibecoding golden demo v1

- Priority/dependencies: P0; `OW-071-04`.
- Outcome: a user tries one feature request and sees scoped context, evidence, resume, and benefit.
- Allowed paths: `examples/`, `docs/`, `addons/launch-demo-kit/`, demo fixtures/tests.
- Implement: offline deterministic eight-minute journey, expected outputs, reset command, Windows/macOS/Linux path handling, token-before/after explanation.
- Accept: demo runs from clean fixture without API key; human steps are explicit; generated artifacts link to sources.
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

### OW-071-07 - Hermes read-only Tier-1 preview

- Priority/dependencies: P0; `OW-071-03`.
- Outcome: Hermes uses the minimal Owledge MCP profile locally or on a VPS without prompt stuffing.
- Allowed paths: `tools/owledge_mcp.py`, Hermes adapter/skill paths, runtime conformance fixtures, English integration docs/tests.
- Implement: installation/routing skill, project-root binding, tool allowlist, MCP reload/test instructions, memory-boundary guidance, compact tool descriptions.
- Accept: Hermes can read entrypoint, search, build context pack, list tasks/reviews; no write tool exists; repository path errors are clear.
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

## v0.8.0 - Portable Control Plane and Retrieval Foundation

### OW-080-01 - Accept contract architecture and migrations

- Priority/dependencies: P0; `OW-071-08`.
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
- Implement: JSON Schemas, defaults, examples, upgrade mapping, extension-field preservation.
- Accept: round-trip preserves stable IDs, typed edges, unknown extensions, visibility, and data class.
- Verify/evidence: schema positive/negative and migration tests; `evidence/OW-080-02/`.
- Negative QA: invalid lifecycle, missing identity, unsafe visibility/data-class combination, and ID mutation fail.

### OW-080-03 - Implement WorkContract, Backlog, and RunState v1

- Priority/dependencies: P0; `OW-080-01`.
- Outcome: intent becomes a machine-readable dependency DAG with scopes, evidence, gates, handoff, and live state.
- Allowed paths: planning templates/skills, schemas, `tools/owledge_core.py`, CLI/tests/docs.
- Implement: ticket compiler/validator, status transitions, dependency readiness, WIP rules, atomic state updates.
- Accept: task cannot reach accepted/done without required gate/evidence refs; cyclic or missing dependencies fail.
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

### OW-080-05 - Build deterministic Context Compiler v1

- Priority/dependencies: P0; `OW-080-02`, `OW-080-03`, `OW-080-04`.
- Outcome: bootstrap, task, reviewer, handoff, and release packs explain inclusion/exclusion and respect budgets.
- Allowed paths: context-pack core/CLI, schemas, fixtures, tests, docs.
- Implement: deterministic ordering/digest, typed selection reasons, privacy/staleness filters, dropped-source list, pack version.
- Accept: identical inputs produce identical pack and digest; every included/excluded source has a reason.
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

## v0.8.1 - Tier-1 Agentic Coding

### OW-081-01 - Define AdapterManifest and conformance protocol

- Priority/dependencies: P0; `OW-080-10`.
- Outcome: adapters declare detect/install/inject/capture/execute/resume/health/cleanup, versions, permissions, limits, and degradation.
- Allowed paths: runtime conformance add-on, schemas, adapter templates, tests/docs.
- Implement: capability schema, negotiation result, fixture protocol, support-tier rules.
- Accept: undeclared capability cannot run; unsupported feature returns explicit structured result.
- Verify/evidence: manifest and negative compatibility suite; `evidence/OW-081-01/`.
- Negative QA: version mismatch, missing permission, or false capability claim fails.

### OW-081-02 - Codex Tier-1 adapter

- Priority/dependencies: P1; `OW-081-01`.
- Outcome: Codex bootstrap, context, task, checkpoint, handoff, hooks where available, and cleanup pass conformance.
- Allowed paths: `.codex/`, Codex plugin/skill/fixtures, runtime docs/tests.
- Implement: compact AGENTS/skill bridge, MCP/CLI routing, permission mapping, fixture transcript.
- Accept: Codex completes common conformance fixture with source-linked outputs.
- Verify/evidence: Tier-1 suite; `evidence/OW-081-02/`.
- Negative QA: missing hook is declared unsupported rather than silently skipped.

### OW-081-03 - Claude/Cowork Tier-1 adapter

- Priority/dependencies: P1; `OW-081-01`.
- Outcome: Claude/Cowork plugin hooks and skills pass the common contract.
- Allowed paths: `plugins/owledge-cowork/`, Claude fixtures, runtime docs/tests.
- Implement: lifecycle validation, compact routing, tool/scoped write mapping, fixture transcript.
- Accept: same artifacts and lifecycle semantics as other Tier-1 profiles.
- Verify/evidence: Tier-1 suite; `evidence/OW-081-03/`.
- Negative QA: hook failure surfaces at session close and cannot mark ticket done.

### OW-081-04 - Hermes Tier-1 adapter

- Priority/dependencies: P0; `OW-081-01`.
- Outcome: native Hermes local/VPS skill and MCP configuration pass the common contract.
- Allowed paths: Hermes adapter/skill/fixtures, MCP server, runtime docs/tests.
- Implement: repo-bound project discovery, tool allowlist, memory boundary, MCP reload/test, context/resume flow, upstream handoff contract.
- Accept: Hermes runs with compact permanent prompt and on-demand Owledge context; adapter ownership boundary is documented.
- Verify/evidence: pinned Hermes fixture/conformance transcript; `evidence/OW-081-04/`.
- Negative QA: VPS path mismatch, disabled tool, unavailable server, and unsupported write fail clearly.

### OW-081-05 - Generic MCP/CLI Tier-1 adapter

- Priority/dependencies: P1; `OW-081-01`.
- Outcome: any capable harness can use the same versioned read/control contract without runtime-specific files.
- Allowed paths: MCP/CLI server, generic adapter fixtures, docs/tests.
- Implement: protocol-compliant surface, capability discovery, JSON output, stdio lifecycle, project binding.
- Accept: reference client passes common conformance suite.
- Verify/evidence: protocol and CLI fixtures; `evidence/OW-081-05/`.
- Negative QA: malformed JSON-RPC, unknown project, and tool mismatch fail without server crash.

### OW-081-06 - Implement claims, path scopes, and worktree planner

- Priority/dependencies: P0; `OW-080-03`, `OW-081-01`.
- Outcome: independent work receives explicit claim, branch/worktree, allowed paths, base SHA, merge order, and TTL.
- Allowed paths: workpackage/claim schemas, Git helper core/CLI, tests/docs.
- Implement: dry-run worktree plan, overlap detection, advisory lease, ownership journal, no direct integration-branch worker writes.
- Accept: eight non-overlapping fixture workers plan cleanly; overlap requires owner decision.
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

### OW-081-09 - Add scoped Owlib retrieval and hub context packs

- Priority/dependencies: P1; `OW-071-06`, `OW-080-05`.
- Outcome: Owlib queries current project plus explicit allowlisted projects and explains source selection.
- Allowed paths: `owlib/`, hub skills/MCP/docs/tests.
- Implement: `--projects`, exclusions, scope profiles, project-filter-first retrieval, context-pack budget/digest, source reasons.
- Accept: default never scans all projects; output identifies project, source, freshness, review, and exclusion reasons.
- Verify/evidence: cross-project privacy/relevance fixtures; `evidence/OW-081-09/`.
- Negative QA: unauthorized project ID, empty scope, and mixed private/shared context fail safely.

### OW-081-10 - Prove multi-agent golden journey and cut v0.8.1

- Priority/dependencies: P0; `OW-081-08`, `OW-081-09`.
- Outcome: plan, parallel dispatch, deliberate interruption, cross-harness resume, failed review, correction, integration, and source-linked report run end to end.
- Allowed paths: golden fixtures/demo, conformance kit, release/version/docs/workflows.
- Implement: deterministic journey using all Tier-1 profiles, clean artifact build, public support matrix.
- Accept: no clobbered files, silent degradation, duplicate writes, or chat dependency; `G-081-RC` passes.
- Verify/evidence: full journey and release artifact matrix; `evidence/OW-081-10/`.
- Negative QA: overlap and missing test evidence deliberately fail before recovery.

## v0.9.0 - Trusted Writes and Knowledge Lifecycle

### OW-090-01 - Implement append-only Evidence Ledger and authority policy

- Priority/dependencies: P0; `OW-081-10`.
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
- Implement: capability scopes, project binding, locks/idempotency, dry run, audit event, structured result; no arbitrary write tool.
- Accept: every write maps to a contract transition and evidence event; read-only remains default profile.
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

## v1.0 - Product Hardening and Release

### OW-100-01 - Establish scale and performance SLOs

- Priority/dependencies: P0; `OW-090-10`.
- Outcome: 10, 1k, and 10k artifact profiles publish index, context, drift, sync, and status latency/resource targets.
- Allowed paths: benchmark kits/results methodology, performance core/tests/docs.
- Implement: controlled fixtures, a hardware-independent deterministic correctness suite, cold/warm runs, p50/p95, memory/disk, and Windows/macOS/Linux performance profiles.
- Accept: correctness passes independently of runner availability; performance targets are reproducible, evidence-bounded, and met or transparently limited without waiving correctness.
- Verify/evidence: scale matrix; `evidence/OW-100-01/`.
- Negative QA: cache-hidden cold result or unreported hardware limitation invalidates claim.

### OW-100-02 - Harden secrets, PII, and prompt-injection boundaries

- Priority/dependencies: P0; `OW-090-03`, `OW-090-04`.
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
- Implement: short commands, JSON errors, actionable recovery, idempotency, uninstall preview, no orphaned canonical data.
- Accept: beginner and automation journeys both work; every mutation explains writes before apply.
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
