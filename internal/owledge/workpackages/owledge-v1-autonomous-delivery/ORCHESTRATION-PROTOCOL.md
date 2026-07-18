---
title: "Owledge Optional Autonomous Delivery Protocol"
date: "2026-07-18"
version: "1.0.0"
memory_id: "mem:owledge:global:owledge:protocol:autonomous-delivery"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "execution_protocol"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge consent-first autonomous delivery protocol"
summary: "Default-off rules for ticket classification, consent, agent lanes, model profiles, Git isolation, and edge-model task capsules."
concept_tags: ["autonomous-delivery", "subagents", "consent", "small-models"]
stack_tags: ["git", "markdown", "yaml", "mcp"]
problem_patterns: ["implicit-delegation", "unsafe-parallel-writes", "small-model-overreach"]
architecture_patterns: ["opt-in-orchestration", "independent-qa", "worktree-isolation"]
failure_modes: ["implicit-spawn", "same-context-qa", "integration-branch-write"]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-18T00:00:00Z"
updated_at: "2026-07-18T00:00:00Z"
source_hash: ""
owners: ["release-orchestrator"]
tags: ["orchestration", "user-control"]
reusable_lessons: []
edges: []
---

# Optional Autonomous Delivery Protocol

Owledge remains single-agent by default. `subagent: true` is eligibility only; it never authorizes a spawn, worktree, write, merge, or external runtime call. The `owledge-autonomous-delivery` skill must first classify work and obtain recorded user consent.

## Classification and Consent

| Class | Definition | Approval | Default lanes |
| --- | --- | --- | --- |
| Small | One outcome, <=3 implementation files; no public contract, migration, security/privacy, MCP, release, cross-project, or concurrent write | none | one agent |
| Medium | More than three files or independent QA value; no high-risk boundary | phase | Worker + independent QA |
| High-risk | Refactor, merge, migration, public API/schema, MCP, security/privacy, release, cross-project, or concurrent write | per ticket | Worker + QA + Red Team |

The consent brief names ticket/dependencies, model profiles, file scopes, worktrees/branches, write/network/cost risk, evidence retention, rollback, and safe fallback. Consent expires at the next version-alignment stop.

## Lanes and Git

One Worker may write for a ticket. QA uses a separately initialized context; Red Team uses an adversarial brief and is required only for high-risk work. Lanes claim non-overlapping paths in separate worktrees. Workers never write the integration branch. The integration owner may merge only a manifest containing base SHA, changed paths, commands, evidence, approvals, review result, and rollback target.

## Small Models

`edge_small` receives a bounded task capsule, not the full control plane. It may run deterministic checks and bounded implementation only. Architecture, merge authority, security sign-off, and cross-project coordination are unsupported. v0.8.1 support claims require deterministic fixtures and one real local-model smoke run.