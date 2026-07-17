---
memory_id: "mem:owledge:global:owledge:review:v1-roadmap-blindspot-analysis"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "qa"
artifact_type: "review"
status: "reviewed"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v1 roadmap blindspot analysis"
summary: "Concept-level blindspot audit of the autonomous v0.7.1-to-v1.0 delivery plan, with mechanical evidence, guided scores, ticket mappings, and residual controls."
concept_tags: ["blindspot-audit", "v1-roadmap", "autonomous-delivery"]
stack_tags: ["python", "mcp", "rag", "git"]
problem_patterns: ["benchmark-gaming", "evidence-bloat", "external-adapter-dependency", "planning-context-bloat"]
architecture_patterns: ["candidate-review", "gate-driven-delivery"]
failure_modes: ["synthetic-proof-overclaim", "solo-self-approval", "stale-hub-copy", "unbounded-context"]
confidence: 0.88
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-16T00:00:00Z"
updated_at: "2026-07-16T00:00:00Z"
source_hash: ""
reusable_lessons:
  - "A long-horizon control plane must be validated and selectively loaded, or its planning detail becomes context bloat."
  - "Token regression, retrieval quality, privacy, and correctness require separate thresholds to prevent benchmark gaming."
edges:
  - type: "validates"
    target: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
    confidence: 0.92
    reason: "This review stress-tests the delivery plan after ticket and gate creation."
---

# Owledge v1 Roadmap Blindspot Analysis

## Verdict

**Promote as an execution candidate with controlled follow-through.** The plan is
coherent, vertically releasable, and safety-aware. No new owner decision blocks the
first release. The strongest remaining risks are execution-quality risks rather than
missing product direction: synthetic benchmark overfitting, evidence leakage/bloat,
external Hermes ownership, solo-review independence, and the control plane itself
becoming context bloat.

Roadmap-readiness score: **8.3/10**. This is not a product-quality score.

Next concept audit due: **2026-08-15**, or before any release-scope or contract change,
whichever comes first.

## Control-Plane Remediation Status

The findings below are fixed at the planning/control-plane level. Product implementation evidence remains intentionally gated by the mapped tickets; this report does not claim those future features already exist.

| Finding | Control-plane status | Durable control | Remaining proof |
| --- | --- | --- | --- |
| BS-01 context bloat | fixed | selective ticket/gate loader and mandatory read order | token telemetry during implementation |
| BS-02 benchmark gaming | fixed | sealed holdouts and separate correctness/token thresholds | run versioned held-out suite |
| BS-03 Hermes ownership | fixed | pinned conformance boundary and generic MCP fallback policy | test pinned upstream release |
| BS-04 solo QA | fixed | distinct owner/QA roles and three permitted independence modes | record mode per gate |
| BS-05 evidence leak/bloat | fixed | retention, redaction, transcript, size, and external-hash rules | attack and deletion fixtures |
| BS-06 second source of truth | fixed | source/freshness/tombstone acceptance contracts | unavailable-source and deregistration tests |
| BS-07 RAG overfitting | fixed | projection/retrieval/embedding/language strata | publish per-stratum results |
| BS-08 small-model tool choice | fixed | tool-choice, validity, retry, completion, and false-pass metrics | run 4B/8k matrix |
| BS-09 hardware variance | fixed | correctness and performance gates are independent | run declared hardware profiles |
| BS-10 MCP attack surface | fixed | expanded semantic-write attack corpus | threat-model and negative suite |
| BS-11 waterfall scope | fixed | explicit no-pull-forward scope rule | enforce at release reviews |
| BS-12 plan drift | fixed | standard-library validator in the first gate and resume path | keep validator green on every edit |

## Mechanical Audit Evidence

Command: `python tools/owledge_core.py --project-root . concept-audit`.

| Dimension | Score | Evidence | Roadmap response |
| --- | ---: | --- | --- |
| Lifecycle and upgrade | 7 | Commands exist; source-root `kit-manifest.json` absent as expected for producer; source-root upgrade dry-run warned | OW-071-02 and OW-100-05 prove consumer-project lifecycle and rollback/recovery |
| Distribution integrity | 10 | VERSION/badge match and sdist-clean passed | Release gates keep artifact proof cumulative |
| Dogfood fidelity | 10 | dogfood sync passed | Every release retains dogfood and contract gates |
| Contract completeness | 10 | 368 checks passed; 19/19 CLI commands documented | New commands require contract/doc tests in their tickets |
| Cross-layer integrity | 7 guided | Boundaries exist, but future global scopes and semantic writes expand the surface | OW-090-03, OW-090-04, OW-100-02 |
| Failure-mode coverage | 7 guided | Ticket negatives are strong; cross-platform and external-runtime failures remain operationally variable | All gates require negative/recovery evidence; OW-081-04 and OW-100-04 |
| Conceptual coherence | 7 guided | Direction is consistent; old plans and legacy Owlib terms still risk drift | OW-071-01 and OW-071-06 |
| Self-description accuracy | 7 guided | Current contract gates are strong; future support claims require evidence linkage | OW-100-06 and OW-100-07 |

## Findings and Mitigations

### BS-01 - The planning control plane can become context bloat

- Severity: P1.
- Risk: a naive agent may load the master plan, complete backlog, all tickets, and all gates, erasing the token-efficiency benefit.
- Existing control: required read order loads only run state, backlog, active ticket section, current gate, and direct decisions.
- Ticket mapping: OW-080-05, OW-080-06, OW-100-04.
- Required proof: measure control-plane bootstrap and active-ticket prompt tokens against full-plan loading; active path must stay inside the selected model profile.
- Residual rule: ticket catalog is a planning source, not a prompt payload. Implementations may materialize one-file-per-ticket views deterministically, but those views must not become a conflicting source of truth.

### BS-02 - Synthetic benchmark preservation can encourage gaming

- Severity: P1.
- Risk: optimizing solely for the fixed 80% legacy threshold could preserve the metric while worsening real planning, resume, or retrieval outcomes.
- Existing control: legacy threshold is isolated from new outcome fixtures; correctness cannot be traded for token reduction.
- Ticket mapping: OW-071-03, OW-100-04, OW-100-07.
- Required proof: add harder held-out and case-study journeys; publish fixture, environment, command, limitations, and quality metrics beside token claims.

### BS-03 - Hermes Tier-1 depends on another repository and release cadence

- Severity: P1.
- Risk: Owledge can own contracts and fixtures but cannot guarantee upstream Hermes packaging or lifecycle behavior.
- Existing control: Owledge owns the conformance contract and an in-repo reference fixture; upstream ownership is explicit.
- Ticket mapping: OW-071-07, OW-081-04, OW-081-10.
- Required proof: pin a tested Hermes version, record upstream commit/version, maintain a graceful generic MCP fallback, and never label newer untested Hermes versions Tier 1 automatically.

### BS-04 - Independent QA is ambiguous for solo users

- Severity: P1.
- Risk: requiring a second human would block solo adoption; letting the same agent self-approve weakens gates.
- Existing control: worker cannot be sole QA owner.
- Ticket mapping: OW-080-04, OW-081-08, OW-100-06.
- Required contract: independence may be a human, a separately initialized reviewer agent with no author context, or a deterministic gate bundle plus owner approval for high-risk promotion. The evidence must state which mode was used.

### BS-05 - Evidence and hub excerpts can leak or bloat Git history

- Severity: P0 for privacy, P1 for repository health.
- Risk: commands, paths, logs, excerpts, and model transcripts may contain secrets or private data; large evidence artifacts can permanently bloat Git.
- Existing control: manifests link artifacts; raw sessions are excluded; privacy policy precedes shared export.
- Ticket mapping: OW-090-03, OW-090-09, OW-100-02.
- Required proof: retention classes, redaction before persistence, size limits, ignore policy, hash-linked external artifacts, and delete/tombstone tests. Do not commit raw model transcripts by default.

### BS-06 - Owlib can become a hidden second source of truth

- Severity: P0.
- Risk: imported excerpts and generated reports may be mistaken for current project facts, especially after source deletion or project relocation.
- Existing control: project files are read-only; outputs are candidates; scoped retrieval is explicit.
- Ticket mapping: OW-071-06, OW-081-09, OW-090-09.
- Required proof: every result carries source project/path/hash/freshness; source-unavailable records are stale, never current; de-registration tombstones all derived projections.

### BS-07 - RAG improvement may be benchmark-specific

- Severity: P1.
- Risk: stripping frontmatter improves embeddings in many cases but can remove useful semantic labels; LightRAG results may not generalize to other embedding models or languages.
- Existing control: governance metadata remains filterable, and generic JSONL precedes vendor adapters.
- Ticket mapping: OW-080-08, OW-090-07, OW-090-08, OW-100-04.
- Required proof: compare body-only, title+summary+body, and selective semantic-tag projections across keyword, vector, and hybrid retrieval; test at least two embedding profiles and multilingual project terms before broad claims.

### BS-08 - Small-model support can fail on tool choice, not context size

- Severity: P1.
- Risk: a pack may fit 8k while a 4B model still selects the wrong tool, violates a state transition, or produces invalid structured output.
- Existing control: deterministic pre-filtering, active-tool limits, schema validation, and atomic tickets.
- Ticket mapping: OW-080-06, OW-080-07, OW-100-04.
- Required proof: measure tool-selection accuracy, valid-contract rate, retry count, gate false-pass rate, and completion—not just prompt tokens.

### BS-09 - Cross-platform release gates can be blocked by unavailable hardware

- Severity: P2.
- Risk: local-model and 10k performance thresholds vary by CPU/GPU, quantization, filesystem, antivirus, and CI limits.
- Existing control: controlled environments and evidence-bounded claims.
- Ticket mapping: OW-100-01, OW-100-04, OW-100-09.
- Required proof: separate deterministic correctness gates from hardware performance profiles; never waive correctness because a benchmark runner is unavailable.

### BS-10 - Semantic MCP writes expand the attack surface sharply

- Severity: P0.
- Risk: project binding, replay, symlinks, lock expiry, malicious tool arguments, and injected retrieved instructions can turn narrow writes into arbitrary effects.
- Existing control: read-only default; privacy/promotion contracts precede writes; no general file tool.
- Ticket mapping: OW-090-03, OW-090-04, OW-100-02.
- Required proof: threat model and negative fixtures for traversal, symlink escape, replay, confused-deputy project IDs, oversized payloads, lock theft, and prompt-injection instructions.

### BS-11 - Scope length risks a waterfall despite vertical releases

- Severity: P2.
- Risk: v0.8.0 contracts can expand until downstream adapter and trust work stalls.
- Existing control: every version has an independently demonstrable user increment and release candidate gate.
- Ticket mapping: all release-cut tickets.
- Required rule: do not pull v0.9/v1 features into v0.8 contracts unless a currently scheduled acceptance criterion cannot be met. New ideas go to post-release backlog.

### BS-12 - Plan validation is not yet a permanent product gate

- Severity: P1.
- Risk: ticket IDs, dependencies, gates, paths, and status may drift as agents edit the control plane.
- Existing control: machine-readable backlog and traceability.
- Ticket mapping: OW-080-03, OW-080-04.
- Required proof: add a validator that checks unique IDs, dependency existence/acyclicity, gate coverage, one source ticket section per backlog item, allowed paths, and run-state consistency before autonomous execution expands.

## Blindspot Acceptance Summary

- No finding requires changing the approved release order.
- All blindspots now have durable policy, ticket, gate, and traceability controls; product-level proof remains attached to mapped tickets.
- The control plane is structurally validated before execution and promotion.
- PI.dev remains deferred and does not distract from v1 delivery.
- Re-run this audit after v0.8 contract freeze, before enabling semantic writes, and before v1 GA.
