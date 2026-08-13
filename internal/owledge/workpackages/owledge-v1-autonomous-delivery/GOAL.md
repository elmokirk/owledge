---
title: "Owledge v1.0 Federated Research Memory Delivery Goal"
date: "2026-08-11"
version: "2.3.0"
document_version: 2
memory_id: "mem:owledge:global:owledge:goal:v1-autonomous-delivery"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "delivery_goal"
status: "active"
visibility: "private"
data_class: "internal"
project: "owledge"
scope: "v0.7.1-v1.0"
semantic_title: "Owledge v1 federated research memory delivery goal"
summary: "Deliver an installable Standalone Core GA with local user-global Null-Space, recall-first Research Memory, and Codex/Claude/generic adapters."
concept_tags: ["v1-roadmap", "delivery-goal", "long-horizon"]
stack_tags: ["markdown", "yaml", "git"]
problem_patterns: ["scope-drift", "unsafe-autonomy"]
architecture_patterns: ["gate-driven-delivery", "durable-control-plane"]
failure_modes: ["unverified-completion", "self-approval"]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-16T00:00:00Z"
updated_at: "2026-08-13T00:00:00+02:00"
source_hash: ""
owners:
  - "product-owner"
  - "release-orchestrator"
tags:
  - "roadmap"
  - "autonomous-delivery"
  - "long-horizon"
reusable_lessons: []
edges: []
---

# Owledge v1.0 Federated Research Memory Delivery Goal

Deliver the approved v0.7.1-to-v1.0 roadmap through the ticket DAG and cumulative
gates, culminating in a Standalone Core GA and private local user-global
Null-Space. Hub Beta is post-V1.

The product must let Codex, Claude Code, and generic MCP/CLI harnesses reuse
durable project and Research Memory across `project_user` and private local
`user_global` scopes without making any runtime,
vector database, web-search provider, or orchestration framework canonical.
Private cross-project knowledge moves only through a settings-controlled raw
inbox and reviewed promotion lifecycle. The proposed versioned Schema Registry,
pending owner confirmation, and deterministic effective settings are intended
to prevent agents from inventing frontmatter, scope, provider, or automation policy.

The promoted global layer is the central Knowledge Base of reviewed Research
essences, learnings, patterns, and transferable concepts. It starts retrieval
compactly and preserves permission-checked drill-down to exact project and
Evidence revisions. Scope, abstraction, and lifecycle remain independent.
Every material managed-document edit bumps `document_version`. Deterministic
local Knowledge Health keeps the local knowledge base maintainable without
turning Owledge into a trace warehouse.

## First Allowed Step

Run `python tools/validate_v1_delivery_plan.py`, then resume the first active
ticket recorded in `RUN-STATE.yaml`. After the approved v0.8.0 scope cut is
validated and recorded, that ticket is `OW-081-01`.

## WIP and Execution Rule

- One active ticket per agent.
- Only dependency-ready tickets may start.
- Parallel tickets, when an external runtime supports them, require separate
  worktrees and non-overlapping `allowed_paths`; Owledge records evidence but
  does not own runtime dispatch.
- `subagent: true` is eligibility metadata only and never authorizes dispatch.
- Small tickets remain single-agent. High-risk work needs explicit approval and
  independent QA/Red-Team evidence.
- The release integration branch advances only through an integration owner.
- After every RC/GA gate, run only its matching alignment ticket. It must set `RUN-STATE.yaml` to `awaiting_user_alignment`, create the required version update, and stop until the user responds.
- During each version, append non-blocking questions, implementation findings,
  and decisions to the matching alignment registers; include every accumulated
  item in the version update rather than silently deciding or omitting it.

## Prohibited Shortcuts

- No automatic canonical promotion or implicit subagent dispatch.
- No arbitrary MCP filesystem-write tool.
- No loading the full control plane into every model prompt.
- No web or model call inside deterministic Research recall; external research
  starts only from a stale, partial, missing, or conflicted delta brief.
- No raw frontmatter in embedding text.
- No agent writes directly to canonical knowledge; agents create Candidate or
  Evidence artifacts and promotion remains a separate reviewed transition.
- No Hub, remote identity, enterprise scope, Pi Tier-1 adapter, LightRAG,
  Documentation Compiler, supply-chain system, multi-tenant SaaS, SAML/SCIM,
  or highly available cluster in the V1 critical path.
- No raw global inbox content in normal retrieval, no silent discard without a
  reason receipt, and no customization layer may widen Core/organization policy.
- No full project copy as the global default, no pointer-only global essence,
  and no deep-dive source expansion without a fresh authorization and budget check.
- No generic tracing backend, full agent harness, model jury, scheduler,
  LangGraph-owned memory, or knowledge frontend in the v1 Core.
- No silent capability fallback, privacy waiver, threshold reduction, or scope change.
- No publication or release tag from a dirty tracked worktree.
- No publish/tag or next-release ticket after an RC/GA until the matching user-alignment ticket is `done`.

## Escalation

Ask the owner before costs, credentials, production/VPS changes, customer data, destructive migration, irreversible architecture, or changes to locked product decisions. Stop immediately for likely data loss, secret exposure, unauthorized cross-project data, or contradictory security criteria.

## `/goal` Version-Stop Protocol

When a version release gate passes, load `ALIGNMENT-PROTOCOL.md`, create the
matching `release-updates/<version>.md`, and present the complete review in
chat: shipped delta, evidence, implementation findings, decision log,
limitations, next-version plan reflection, and owner questions. Set
`status: awaiting_user_alignment`, `active_ticket` to the alignment ticket, and
do not select another ticket.

Only an explicit user response recorded in that update may resolve the stop:

- `approve`: mark the alignment ticket done, allow the documented publish/tag decision, and unlock the next release.
- `adjust`: create/modify the smallest affected tickets and gates, re-run validation, then ask again.
- `defer`: record the deferred work and limitation, then ask whether publication and the next release remain authorized.

## Final Success

`G-100-GA` and `G-100-ALIGNMENT` pass; their evidence reconstructs recall-first
Research reuse, local user-global continuity, reviewed promotion, Standalone
Core GA, and final user alignment without chat history.
