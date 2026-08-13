---
title: "Owledge v1 Traceability"
date: "2026-08-11"
version: "2.5.0"
document_version: 4
memory_id: "mem:owledge:global:owledge:compiled:v1-delivery-traceability"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "traceability_matrix"
status: "active"
visibility: "private"
data_class: "internal"
project: "owledge"
scope: "v0.7.1-v1.0"
semantic_title: "Owledge v1 delivery traceability"
summary: "Traceability from compact Standalone/local-user-global V1 outcomes to tickets, gates, and evidence."
concept_tags: ["traceability", "v1-roadmap", "qa"]
stack_tags: ["markdown", "yaml"]
problem_patterns: ["orphan-requirements", "unmapped-gates"]
architecture_patterns: ["bidirectional-traceability", "gate-driven-delivery"]
failure_modes: ["ticket-gate-drift", "unproven-claim"]
confidence: 0.95
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-16T00:00:00Z"
updated_at: "2026-08-13T00:00:00+02:00"
source_hash: ""
owners:
  - "release-orchestrator"
tags:
  - "traceability"
  - "qa"
  - "roadmap"
reusable_lessons: []
edges: []
---

# Owledge v1 Traceability

## 2026-08-13 V1 Scope-Cut Traceability Override

The following rows are the authoritative V1 traceability where they conflict
with the historical matrix below. Hub, enterprise, Pi Tier-1, LightRAG,
Documentation Compiler, supply-chain, and generic JSONL export trace rows are
post-V1 and cannot be used to justify V1 gate completion or product claims.

| V1 requirement | Active tickets | Active gates |
| --- | --- | --- |
| Installable Standalone Core and safe upgrade | OW-071-10, OW-080-09, OW-100-05, OW-100-09 | G-071-B-ADOPTION, G-080-C-RETRIEVAL, G-100-B-PRODUCT, G-100-GA |
| Local user-global Null-Space, recall, and authorized cross-project context | OW-081-09, OW-090-02, OW-090-03, OW-090-09 | G-081-C-JOURNEY, G-090-A-TRUST, G-090-C-RAG |
| Codex, Claude Code, and generic MCP/CLI capability/degradation contract | OW-081-01, OW-081-02, OW-081-03, OW-081-05, OW-081-10 | G-081-A-ADAPTERS, G-081-RC |
| Checkpoint, handoff, recall-before-research, Candidate and Research delta | OW-081-07, OW-081-08, OW-090-04 | G-081-B-CONCURRENCY, G-090-B-WRITES |
| Reviewed local promotion and controlled semantic writes | OW-090-01, OW-090-02, OW-090-03, OW-090-04 | G-090-A-TRUST, G-090-B-WRITES |
| Local health, freshness, tombstones, and safe source withdrawal | OW-080-09, OW-090-06, OW-090-09 | G-080-C-RETRIEVAL, G-090-B-WRITES, G-090-C-RAG |
| Compact Core security, regression, lifecycle, docs, and GA proof | OW-100-01, OW-100-02, OW-100-04 through OW-100-10 | G-100-A-HARDENING through G-100-GA |

## Appendix A — Historical Superseded Matrix (Post-V1 Reference Only)

The following pre-cut matrix is retained solely for decision provenance. It is
not an active V1 planning or selective-read source: its Hub, enterprise, Pi,
LightRAG, Documentation Compiler, supply-chain, and JSONL rows are superseded
by the binding matrix above and must not be used for ticket selection or gate
promotion.

| Requirement | Tickets | Gates |
| --- | --- | --- |
| English product narrative and beginner adoption | OW-071-04, OW-071-05, OW-100-07 | G-071-B-ADOPTION, G-100-C-PROOF |
| Canonical installation and cross-platform command truth | OW-071-10, OW-071-05, OW-100-05, OW-100-09 | G-071-B-ADOPTION, G-100-B-PRODUCT, G-100-GA |
| Clean aggregate finalization, generated-surface upgrade drift, and observable gate progress | OW-071-08, OW-100-09 | G-071-RC, G-100-GA |
| End-to-end workflow and privacy-boundary explanation | OW-071-11, OW-090-06, OW-100-07 | G-071-B-ADOPTION, G-090-B-WRITES, G-100-C-PROOF |
| Skills taxonomy and executable agent integration guidance | OW-071-12, OW-081-01 through OW-081-05 | G-071-B-ADOPTION, G-081-A-ADAPTERS |
| Reliable skill discovery and bounded long-horizon planning modes | OW-071-12, OW-081-01 through OW-081-05 | G-071-B-ADOPTION, G-081-A-ADAPTERS |
| MVP cutline, planning stop, and durable roadmap/idea routing | OW-080-03, OW-080-05, OW-090-02, OW-090-04 | G-080-A-CONTRACTS, G-080-B-CONTEXT, G-090-A-TRUST, G-090-B-WRITES |
| Versioned common-envelope/artifact-profile Schema Registry and deterministic layered settings | OW-080-01, OW-080-02, OW-090-03, OW-100-03 | G-080-A-CONTRACTS, G-090-A-TRUST, G-100-A-HARDENING |
| Material document revision distinct from schema/profile version and content hash | OW-080-01, OW-080-02, OW-080-09, OW-090-01 | G-080-A-CONTRACTS, G-080-C-RETRIEVAL, G-090-A-TRUST |
| Private global raw inbox excluded from retrieval with promote/reject/archive receipts | OW-090-01, OW-090-02, OW-090-04, OW-090-09 | G-090-A-TRUST, G-090-B-WRITES, G-090-C-RAG |
| Promoted global Knowledge Base centralizes reviewed essences while preserving permission-checked project/Evidence drill-down | OW-080-05, OW-080-08, OW-080-16, OW-081-09, OW-090-02, OW-090-09 | G-080-B-CONTEXT, G-080-C-RETRIEVAL, G-081-C-JOURNEY, G-090-A-TRUST, G-090-C-RAG |
| Scope, knowledge abstraction, and lifecycle remain orthogonal contracts | OW-080-01, OW-080-02, OW-080-05, OW-081-09, OW-090-02 | G-080-A-CONTRACTS, G-080-B-CONTEXT, G-081-C-JOURNEY, G-090-A-TRUST |
| Deterministic Knowledge Health and privacy-safe Hub operations monitoring | OW-080-09, OW-090-06, OW-090-09, OW-100-01, OW-100-11 | G-080-C-RETRIEVAL, G-090-B-WRITES, G-090-C-RAG, G-100-A-HARDENING |
| Pre-plan idea/concept/research capsule and harness lifecycle hooks | OW-080-05, OW-080-16, OW-081-01 through OW-081-05, OW-081-08 | G-080-A-CONTRACTS, G-080-B-CONTEXT, G-081-A-ADAPTERS, G-081-B-CONCURRENCY |
| Recall prior Research Memory before external search | OW-080-16, OW-080-05, OW-080-08, OW-100-04 | G-080-A-CONTRACTS, G-080-B-CONTEXT, G-080-C-RETRIEVAL, G-100-B-PRODUCT |
| Research reason, context, source revision, mutability, and freshness are durable | OW-080-16, OW-090-01, OW-090-06, OW-090-09 | G-080-A-CONTRACTS, G-090-A-TRUST, G-090-B-WRITES, G-090-C-RAG |
| Delta-only refresh for stale, partial, missing, or conflicted Research Memory | OW-080-16, OW-090-04, OW-090-06, OW-100-04 | G-080-A-CONTRACTS, G-090-B-WRITES, G-100-B-PRODUCT |
| Adoption presets and Standalone/Core/Hub maturity boundaries | OW-071-14, OW-071-06, OW-081-09, OW-090-09, OW-100-11 | G-071-B-ADOPTION, G-071-C-COMPAT, G-081-C-JOURNEY, G-090-C-RAG, G-100-A-HARDENING |
| Truthful work register and release state | OW-071-01, OW-071-02 | G-071-A-TRUTH |
| Local HTTP control-plane truth and safe exposure boundary | OW-071-13, OW-100-02 | G-071-A-TRUTH, G-100-A-HARDENING |
| Preserve context/token efficiency | OW-071-03, OW-080-05, OW-080-07, OW-100-04 | G-071-A-TRUTH, G-080-B-CONTEXT, G-100-B-PRODUCT |
| Project-user, private user-global, and reviewed enterprise scope isolation | OW-080-02, OW-081-09, OW-090-02, OW-090-03, OW-090-09, OW-100-11 | G-080-A-CONTRACTS, G-081-C-JOURNEY, G-090-A-TRUST, G-090-C-RAG, G-100-A-HARDENING |
| One private local user-global federation shared across harnesses without Hub upload | OW-081-09, OW-100-07, OW-100-08 | G-081-C-JOURNEY, G-100-C-PROOF |
| Owlib current-layout compatibility and scoped federation | OW-071-06, OW-081-09, OW-090-09 | G-071-C-COMPAT, G-081-C-JOURNEY, G-090-C-RAG |
| Pi thin reference adapter over the Core interface | OW-081-01, OW-081-04, OW-081-08, OW-081-10 | G-081-A-ADAPTERS, G-081-B-CONCURRENCY, G-081-RC |
| Hermes and OpenCode generic MCP/CLI compatibility before dedicated adapters | OW-071-07, OW-081-05, OW-081-10 | G-071-C-COMPAT, G-081-A-ADAPTERS, G-081-RC |
| Long-horizon portable contracts | OW-080-01 through OW-080-04 | G-080-A-CONTRACTS |
| 4B/8k small-model context and contract support | OW-080-06, OW-080-07, OW-100-04 | G-080-B-CONTEXT, G-100-B-PRODUCT |
| Structured Session Recap Candidate and cross-harness resume | OW-080-04, OW-081-07, OW-081-08, OW-081-10 | G-080-A-CONTRACTS, G-081-B-CONCURRENCY, G-081-RC |
| RAG projection improves or preserves retrieval | OW-080-08, OW-090-07, OW-090-08 | G-080-C-RETRIEVAL, G-090-C-RAG |
| Four reference profiles and explicit degradation | OW-081-02, OW-081-03, OW-081-04, OW-081-05, OW-081-08 | G-081-A-ADAPTERS, G-081-B-CONCURRENCY |
| Gate-controlled canonical promotion | OW-090-01 through OW-090-04 | G-090-A-TRUST, G-090-B-WRITES |
| Agents write Candidate/Evidence only; promotion is separate | OW-081-08, OW-090-02, OW-090-04, OW-100-11 | G-081-B-CONCURRENCY, G-090-A-TRUST, G-090-B-WRITES, G-100-A-HARDENING |
| Semantic MCP writes only | OW-090-04, OW-100-11 | G-090-B-WRITES, G-100-A-HARDENING |
| Single semantic mutation Core interface with revision/base-hash concurrency and conflict receipts | OW-090-04 | G-090-B-WRITES |
| Source withdrawal, access revocation, and deletion propagate through global and derived surfaces | OW-090-02, OW-090-09, OW-100-02 | G-090-A-TRUST, G-090-C-RAG, G-100-A-HARDENING |
| Managed-surface ownership and transactional upgrades preserve user-authored knowledge across Standalone, user-global, and Hub surfaces | OW-080-01, OW-080-09, OW-100-05, OW-100-09 | G-080-A-CONTRACTS, G-080-C-RETRIEVAL, G-100-B-PRODUCT, G-100-GA |
| Generic module compatibility, permissions, profiles, migrations, health, cleanup, and uninstall without Core-internal storage access | OW-080-01, OW-081-01, OW-100-03 | G-080-A-CONTRACTS, G-081-A-ADAPTERS, G-100-A-HARDENING |
| Media-neutral external `ResourceRef` preserves source provenance without a binary store or arbitrary-path authority | OW-080-01, OW-080-02, OW-080-16 | G-080-A-CONTRACTS |
| `system.doctor`, `knowledge.health`, and `hub.health` remain distinct profiles with content-safe result contracts | OW-080-01, OW-080-09, OW-100-03, OW-100-11 | G-080-A-CONTRACTS, G-080-C-RETRIEVAL, G-100-A-HARDENING |
| Generic JSONL plus LightRAG reference | OW-090-07, OW-090-08 | G-090-C-RAG |
| Single-Organization Hub Beta with external OAuth/OIDC, agent identities, and no implicit user-global upload | OW-100-02, OW-100-03, OW-100-11 | G-100-A-HARDENING |
| Hub-owned-state Beta RPO/RTO and explicit customer-owned project backup boundary | OW-100-11 | G-100-A-HARDENING |
| Markdown/Git remains canonical in Hub mode | OW-080-01, OW-090-04, OW-100-11 | G-080-A-CONTRACTS, G-090-B-WRITES, G-100-A-HARDENING |
| Security, scale, lifecycle, support, v1 Core GA and Hub Beta proof | OW-100-01 through OW-100-09, OW-100-11 | G-100-A-HARDENING through G-100-GA |
| Selective context and permanent plan validation | OW-071-01, OW-080-03, OW-080-04 | G-071-A-TRUTH, G-080-A-CONTRACTS |
| Independent solo QA and evidence retention | OW-080-04, OW-090-03, OW-100-02, OW-100-06 | G-080-A-CONTRACTS, G-090-A-TRUST, G-100-A-HARDENING |
| Benchmark integrity and cross-profile RAG proof | OW-071-03, OW-080-07, OW-090-08, OW-100-04 | G-071-A-TRUTH, G-080-B-CONTEXT, G-090-C-RAG, G-100-B-PRODUCT |
| Semantic MCP threat boundary | OW-090-04, OW-100-02 | G-090-B-WRITES, G-100-A-HARDENING |
| Mandatory user alignment after every version | OW-071-09, OW-080-11, OW-081-11, OW-090-11, OW-100-10 | G-071-ALIGNMENT, G-080-ALIGNMENT, G-081-ALIGNMENT, G-090-ALIGNMENT, G-100-ALIGNMENT |
| Complete implementation finding/decision log and next-version plan reflection after every version | OW-071-09, OW-080-11, OW-081-11, OW-090-11, OW-100-10 | G-071-ALIGNMENT, G-080-ALIGNMENT, G-081-ALIGNMENT, G-090-ALIGNMENT, G-100-ALIGNMENT |
| Autonomous Delivery Profile, worktree planner, orchestration adapters, and edge delivery profile | no active v1 ticket | explicitly deferred as post-v1 add-ons |
| Multi-tenant SaaS, SAML/SCIM, HA clustering, and built-in identity store | no v1 ticket | explicitly deferred beyond Single-Org Hub Beta |
| Generic tracing backend, full Owledge harness/scheduler/frontend, multi-judge dispatcher, and native LangGraph memory | no v1 Core ticket | adapter or post-v1 discovery; portable receipts/review artifacts only in v1 |
| Bounded personal-data erasure/DSAR orchestration and PII detection/redaction adapters | no active v1 ticket | post-v1 enterprise module; V1 retains general lifecycle/tombstone/projection hygiene only |
| Media/file ingestion, transcription, public plugin SDK/marketplace, and universal connector suite | no active v1 ticket | post-v1 adapters/products over V1 compatibility seams |
| PI.dev is non-critical post-v1 concept | no v1 ticket | explicitly deferred |
