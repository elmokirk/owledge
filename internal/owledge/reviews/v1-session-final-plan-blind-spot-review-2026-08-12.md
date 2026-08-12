---
memory_id: "mem:owledge:global:owledge:evidence:v1-session-final-plan-blind-spot-review-2026-08-12"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "qa"
artifact_type: "review_evidence"
document_version: 3
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v1 session final plan and blind-spot review"
summary: "Evidence-linked final review comparing the pre-session and amended v1 plans, inventorying included and deferred ideas, identifying four bounded plan gaps, and recording release-benefit scores and the V1 execution recommendation."
concept_tags: ["v1-roadmap", "blind-spot-review", "scope-control", "release-readiness"]
stack_tags: ["python", "markdown", "git", "mcp"]
problem_patterns: ["plan-bloat", "release-gate-regression", "remote-global-ambiguity", "derived-data-revocation"]
architecture_patterns: ["deep-module", "semantic-write-seam", "local-first-global", "gate-driven-delivery"]
failure_modes: ["false-green-release", "lost-user-global-value", "concurrent-write-loss", "stale-derived-knowledge"]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-12T13:34:00+02:00"
updated_at: "2026-08-12T13:59:20+02:00"
source_hash: ""
reusable_lessons:
  - "A failed aggregate gate must be decomposed before roadmap promotion; a green nested check is not a green parent gate."
  - "Immediate personal value needs its own local user-global journey even when remote user-global synchronization is deferred."
edges:
  - type: "relates_to"
    target: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
    confidence: 1.0
    reason: "Reviews the amended v1 execution plan against the session goals and current gate evidence."
  - type: "relates_to"
    target: "mem:owledge:global:owledge:plan:v1-federated-research-memory-pi-reprioritization"
    confidence: 1.0
    reason: "Reviews the session-specific roadmap amendment and its bloat cutline."
---

# Owledge V1 Session Final Plan and Blind-Spot Review

## Subject and Review Question

Subject: the pre-session v1 plan at `HEAD` versus the current amended roadmap,
ticket, gate, traceability, decision, and research artifacts on
`codex/v071-integration`.

Question: does the amended plan preserve Owledge's local-first deterministic
Core while adding the highest-value Research, user-global, cross-harness, and
Single-Organization Hub capabilities without creating a second knowledge truth
or an oversized agent platform?

## Expert Lenses

- Senior AI Agent Engineer: cross-harness continuity, deterministic capture,
  small-context use, and semantic tool calls.
- Senior Software Architect: deep Core interface, adapter seams, consistency,
  migration, and recovery.
- Product/Scope Strategist: time-to-value, release sequencing, bloat cutline,
  and maturity claims.
- Security/Privacy Reviewer: scope isolation, promotion, revocation, derived
  data, identity, and content-free monitoring.
- QA Gate Owner: executable acceptance, clean-source evidence, and regression
  truth.

## Evidence Reviewed

- `ROADMAP.md` and its `HEAD` predecessor.
- `internal/owledge/plans/owledge-v1-autonomous-delivery-master-plan.md` and its
  `HEAD` predecessor.
- `internal/owledge/plans/owledge-v1-federated-research-memory-and-pi-adapter-reprioritization.md`.
- Ticket, gate, traceability, live-work, and run-state control artifacts.
- The decision matrix and both architecture Research notes created in this
  session.
- `python tools/owledge.py finalization-gates --project-root .
  --include-compliance --include-exports`, completed on 2026-08-12: 36/38 gates
  passed; `source-identity` failed on the intentionally dirty planning tree and
  `upgrade-drift` failed because a host-project fixture was validated in Kit mode.
- Targeted source inspection of `tools/owledge.py:2639-2649` and
  `tools/owledge_core.py:2426-2598`.

## Coverage Inventory

| Session theme | Current disposition | Owning release/tickets | Status |
| --- | --- | --- | --- |
| Research recall before web search and bounded delta refresh | Core V1 | v0.8.0 `OW-080-16`, `OW-080-05` | included |
| Three authority scopes and scope-first retrieval | Core V1 | `OW-080-02`, `OW-081-09`, `OW-100-11` | included |
| Global Raw to reviewed global essence with source drill-down | Core V1 | v0.9.0 `OW-090-02`, `OW-090-06`, `OW-090-09` | included |
| Deterministic schemas, settings, linter, validator, and document revisions | Core V1 | v0.8.0 `OW-080-01`, `OW-080-02`, `OW-080-09` | included; `1B+` owner-approved |
| Context/token pollution and small-model compatibility | Core V1 | `OW-080-05` through `OW-080-08`, `OW-100-04` | included |
| Codex, Claude, Pi, Hermes/OpenCode portability | Adapter V1 | v0.8.1 `OW-081-01` through `OW-081-09` | included |
| Semantic MCP writes and autonomous session/research deltas | Governed V1 | `OW-081-08`, `OW-090-04` | included |
| Knowledge Health and content-free operations monitoring | Core/Hub V1 | `OW-080-09`, `OW-090-06/09`, `OW-100-01/11` | included |
| Existing Markdown KB and optional RAG interoperability | Projection V1 | `OW-080-08`, `OW-090-07/08` | included |
| Planning focus and deferred-idea resurfacing | Core V1 | `OW-080-03/05`, adapter pre-plan fixtures | included |
| Paid self-hosted one-customer deployment | Product option | `OW-100-11`, Hub Beta claim | included with bounded maturity |
| Full agent harness, scheduler, cron automation, generic tracing, multi-judge dispatcher, frontend, LangGraph ownership | Post-V1 add-ons | explicit Not-in-V1 list | considered and deferred |
| Hosted multi-tenant SaaS, SAML/SCIM, HA/multi-region | Post-V1 enterprise program | explicit Not-in-V1 list | considered and deferred |
| Remote synchronization of private `user_global` memory | Post-V1 decision | Hub explicitly rejects implicit sync | considered and deferred |
| Exact unnamed hierarchical-memory paper | Owner input required | research note lists plausible papers only | unresolved, not guessed |

## Findings

### P1 — Release finalization has a real `upgrade-drift` regression

`upgrade_drift_check` initializes a normal host project and then invokes
`memory_doctor(..., mode="kit")`. The nested `version-drift` row passes, but
Kit-only entrypoint checks make the doctor result false. This blocks truthful
V0.7.1 RC evidence.

Acceptance: `OW-071-08` must add a non-mocked regression fixture that validates
the generated surface in its actual mode, then the full 38-gate suite must pass
from a clean committed source tree.

### P1 — The immediate personal `user_global` journey is implicit

Cross-project retrieval exists, but the plan does not clearly require a local
reference composition where Codex, Claude, Pi, and generic MCP share one private
user-global Knowledge Base without using Hub synchronization.

Acceptance: `OW-081-09` proves one local user-global daemon/process or equivalent
local composition across at least two harnesses, with project allowlists,
source reasons, no implicit upload, and clear Hub-unavailable degradation.

### P1 — Concurrent semantic writes need one explicit Core interface

Locks, leases, idempotency, atomic state, and Git conflicts appear across
multiple tickets, but the external Core seam is not stated as one semantic
mutation interface. Leaving this distributed across adapters would produce
shallow pass-through modules and inconsistent conflict behavior.

Acceptance: `OW-090-04` owns a single semantic mutation module using target
identity, expected `document_version`/base hash, idempotency key, authorized
transition, atomic file/Git result, and conflict/reconciliation receipt. MCP,
Pi, CLI, and Hub remain adapters to that interface.

### P1 — Revocation and deletion propagation is under-specified

Tombstones and de-registration exist, but the plan does not explicitly cover a
source that must be withdrawn after promotion into a global essence. Source
deletion, access revocation, or legal retention changes must not leave a
retrievable derived shadow.

Acceptance: `OW-090-02`, `OW-090-09`, and `OW-100-02` prove a policy-driven
revocation event propagates to global essences, drill-down refs, exports, and
indexes while preserving the minimum non-content audit tombstone allowed by
policy.

### P2 — Full-suite progress is buffered too long for reliable agent control

The completed run emitted no usable progress for roughly two minutes. The
result is correct, but CI/agent operators cannot distinguish expensive work
from a stuck process.

Acceptance: the release gate runner streams or flushes gate completion and
durations and always writes a machine-readable terminal manifest. This is a
release-engineering improvement inside `OW-071-08`, not a product subsystem.

### P2 — Hub Beta recovery claims need bounded objectives

Backup/restore is planned, but Hub Beta needs an explicit tested recovery
objective and a clear statement that Git/project backup remains customer-owned.

Acceptance: `OW-100-11` publishes tested Beta RPO/RTO bounds for Hub-owned state,
states exclusions, and proves no canonical project knowledge is silently lost
or claimed to be backed up by Hub.

## Pre-Session Versus Current Plan Score

Weights: Core fidelity 15, user value 15, Research reuse 15, cross-harness
portability 10, enterprise viability 10, governance/privacy 10, scope discipline
10, token/small-model efficiency 5, health/maintainability 5, testability 5.

| Dimension | Weight | Pre-session | Current amended plan |
| --- | ---: | ---: | ---: |
| Core fidelity | 15 | 12.0 | 14.3 |
| Immediate user value | 15 | 10.5 | 12.8 |
| Research reuse | 15 | 3.8 | 14.3 |
| Cross-harness portability | 10 | 8.0 | 9.0 |
| Enterprise viability | 10 | 4.0 | 8.5 |
| Governance and privacy | 10 | 7.0 | 9.5 |
| Scope discipline | 10 | 6.0 | 9.0 |
| Token/small-model efficiency | 5 | 4.0 | 4.5 |
| Health and maintainability | 5 | 2.0 | 4.3 |
| Testability and evidence | 5 | 4.5 | 4.6 |
| **Total** | **100** | **61.8** | **90.8** |

The pre-session score is relative to the newly clarified product target, not a
claim that its implementation discipline was poor. It was strong as a local
agentic delivery plan but did not yet cover the Research-reuse, personal-global,
or bounded enterprise product thesis.

## Release Benefit Matrix

| Release | Main value | User benefit (1-10) | Architecture leverage (1-10) | Delivery risk (1-10, lower is better) | Recommendation |
| --- | --- | ---: | ---: | ---: | --- |
| v0.7.1 | install/adoption truth, golden demo, compatibility | 6 | 8 | 3 | finish first; it is the trustworthy launchpad |
| v0.8.0 | contracts, Research recall, context compiler, schema/settings, small-model basis | 9 | 10 | 6 | highest foundation benefit |
| v0.8.1 | cross-harness continuity, Pi, local user-global cross-project read | 9 | 9 | 6 | fastest multi-harness personal benefit |
| v0.9.0 | governed deltas, Raw promotion, global essences, semantic writes, freshness | 10 | 10 | 8 | largest direct power-user benefit |
| v1.0 | hardened Core GA plus Single-Organization Hub Beta | 8 | 9 | 9 | enterprise proof; do not pull earlier |

## Verdict

- Architecture-plan quality: **90.8/100 — accept** after the bounded ticket
  deepening in this review.
- Current release execution readiness: **80/100 — revise** after owner approval
  of `1B+ / 2C+ / 3B`. V0.8 work remains blocked until `OW-071-05`, V0.7.1
  RC/alignment, the `upgrade-drift` repair, and a clean 38/38 finalization run.

## Residual Risks and Follow-up QA

- The exact arXiv paper remains unidentified until the owner supplies a title
  or ID.
- Hub Beta is not Enterprise-ready; paid setup is viable only with explicit
  support, backup, security-update, and maturity boundaries.
- Autonomous harness use cannot be guaranteed by Owledge alone. Each adapter
  must prove hook/conformance behavior and report unsupported lifecycle events.
- Generated diagnostic exports from a dirty source tree are not release
  evidence; the authoritative finalization run must occur after source commit.
