---
memory_id: "mem:owledge:global:owledge:project_context:v1-control-plane-policy"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "execution_policy"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v1 autonomous delivery control-plane policy"
summary: "Cross-cutting policy for context loading, QA independence, evidence retention, external adapters, benchmarks, RAG, small models, and release execution."
concept_tags: ["execution-policy", "qa-independence", "context-budget", "evidence-retention"]
stack_tags: ["git", "python", "mcp", "rag"]
problem_patterns: ["planning-context-bloat", "self-approval", "evidence-leak", "benchmark-gaming"]
architecture_patterns: ["selective-context-loading", "role-separated-qa", "manifest-only-evidence"]
failure_modes: ["full-plan-prompt", "raw-transcript-commit", "untested-runtime-claim", "quality-hidden-by-token-savings"]
confidence: 0.94
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-16T00:00:00Z"
updated_at: "2026-07-27T00:00:00Z"
source_hash: ""
reusable_lessons:
  - "Planning detail should improve resumability without becoming default prompt context."
  - "Independent QA is a property of evidence and context separation, not necessarily a second human."
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
    confidence: 1.0
    reason: "This policy closes cross-cutting blindspots discovered after the ticket plan was created."
---

# Owledge v1 Control-Plane Policy

## Context Loading

An execution turn loads only:

1. `RUN-STATE.yaml`.
2. the compact ticket row from `BACKLOG.yaml`.
3. the active ticket section from `tickets/ALL-TICKETS.md`.
4. the current gate section from `gates/ALL-GATES.md`.
5. directly referenced decisions or evidence manifests.

Use `python tools/validate_v1_delivery_plan.py --ticket-id <ID>` and `--gate-id <ID>` to extract sections. Loading the full master plan, ticket catalog, or gate catalog into a routine agent prompt is a policy violation. OW-080-05 must measure this bootstrap path against full-plan loading.

## Role and QA Assignment

- `owner_role` is responsible for implementation and checkpoint accuracy.
- `qa_role` is responsible for attack/failure cases and evidence verification.
- Owner and QA roles must differ for every ticket.
- Acceptable independent QA modes are: a different human; a separately initialized reviewer agent without author conversation state; or deterministic gates plus explicit owner approval for high-risk promotion.
- Semantic MCP writes, privacy/export decisions, security changes, release cuts, and canonical promotion may not use author-only QA.
- Every evidence manifest records the concrete actor/runtime and QA mode, not only the abstract role.

## Optional Autonomous Delivery

- Default execution is single-agent. Use `owledge-autonomous-delivery` only to assess and propose an optional delivery workflow.
- `subagent: true` is eligibility only. It does not authorize spawning, worktrees, writes, merges, or runtime calls; recorded user consent is required first.
- Small tickets have one bounded outcome, at most three implementation files, and no public contract, migration, security/privacy, MCP, release, cross-project, or concurrent-write impact. They remain single-agent.
- Medium work requires phase approval for one Worker plus independent QA. High-risk refactors, merges, migrations, public API/schema, MCP, security/privacy, release, cross-project, or concurrent-write work requires per-ticket approval and a risk-triggered Red Team.
- User consent records lanes, model profiles, allowed paths, Git/worktree plan, write/network/cost risk, evidence retention, rollback, and safe fallback. It expires at the next alignment stop.
- Worker, QA, and Red Team contexts are isolated. One Worker may write per ticket; only the integration owner may merge an evidenced manifest to the integration branch.

## Evidence Retention and Privacy

- Commit compact manifests, reports required for reproducibility, and stable hashes—not raw model transcripts or unrestricted command logs.
- Redact secrets, credentials, personal paths, customer data, and private prompts before persistence.
- Default maximum committed evidence artifact is 1 MiB; larger artifacts stay ignored or external and are referenced by path, hash, environment, and retention class.
- Evidence classes: `release` retained with release history; `ticket` retained through the support window; `diagnostic` ignored and disposable; `sensitive` never committed.
- Owlib excerpts and RAG projections inherit the source data class, review state, project scope, and deletion/tombstone lifecycle.

## Benchmark Integrity

- The fixed v0.7 fixture protects regression only; it is not training data for claims about general repositories.
- Token reduction, correctness, privacy, staleness, retrieval ranking, tool selection, contract validity, false gate passes, and task completion are reported separately.
- Held-out and case-study fixtures must not be inspected by implementation logic.
- A token improvement cannot compensate for lower correctness or a privacy/stale failure.
- Hardware performance claims state CPU/GPU, memory, filesystem, OS, model, quantization, runtime, cold/warm state, and limitations. Correctness gates remain independent of hardware availability.

## Small-Model Proof

Tier-1 4B/8k support requires pack-budget compliance plus tool-selection accuracy, valid structured-contract rate, retry count, task completion, resume correctness, and false-pass rate. A model that fits the context but cannot follow the workflow does not pass.

## RAG Proof

- Compare body-only, title+summary+body, and selective semantic-tag projections.
- Evaluate keyword, vector, and hybrid retrieval with at least two embedding profiles and multilingual project terminology before broad claims.
- Raw frontmatter remains filter metadata and never enters default embedding text.
- Source and compiled chunks must not duplicate the same canonical fact without an explicit dedupe relation.
- Unavailable or deleted sources make derived records stale/tombstoned, never current.

## Hermes and External Runtime Ownership

Owledge owns the adapter contract, pinned conformance fixture, support matrix, and generic MCP fallback. The Hermes repository may own its native adapter. Tier-1 status applies only to explicitly tested Hermes versions; newer versions are unverified until the suite passes.

## Semantic MCP Threat Boundary

Before write-enabled MCP promotion, negative fixtures cover traversal, symlink escape, confused-deputy project identifiers, replay, oversized payloads, lock theft/expiry, undeclared scopes, injected retrieved instructions, and direct canonical-write attempts. Read-only remains the default profile.

## Scope Control

Each version is independently releasable. Downstream v0.9/v1 functionality may enter a v0.8 ticket only when a current acceptance criterion is otherwise impossible. New ideas go to a later backlog instead of expanding an active ticket silently.

## Version Alignment and User Authority

- A passed RC/GA gate proves technical release readiness only. It does not authorize a publish/tag, the next release, a scope change, or closure of open product questions.
- Each release has one alignment ticket and gate. The ticket compiles a factual feature update from committed evidence, lists all findings, decisions, and design/product/release questions, reflects the next-version plan, and creates `release-updates/<version>.md` using `ALIGNMENT-PROTOCOL.md`.
- After the update is presented, the agent sets the run state to `awaiting_user_alignment` and the alignment ticket to `blocked` with the exact questions and safe default. This is an intentional pause, not a failure.
- Until an explicit user response is recorded, no next-release ticket may become `ready`, and no publish/tag occurs. Agents may answer questions or repair evidence only within the active release.
- `approve`, `adjust`, and `defer` are the only valid outcomes. `adjust` requires the smallest ticket/gate update and a fresh validation run; `defer` records impact, limitation, and the user decision before further work.

## Version Finding, Decision, and Question Registers

- During every ticket and gate, capture non-blocking product, architecture, UX/DX, integration, performance, security, privacy, and scope questions in `RUN-STATE.yaml` under `alignment.open_questions`. Capture problems, gaps, deviations, regressions, and new risks under `alignment.findings`; capture decisions made or requested under `alignment.decisions`.
- Every finding and decision uses a stable version-scoped ID and records its source, evidence, impact, status, recommendation, safe default, authority, and affected artifacts as applicable.
- Do not interrupt a version for ordinary alignment items. Carry every entry into the next mandatory version update, where it must be resolved, explicitly deferred, or marked `None` when the register is empty.
- Escalate immediately instead of waiting for the version stop when a question affects safety, privacy, credentials/cost, data loss, external commitments, or an irreversible architecture decision.

## Next-Version Reflection

- After the release gate passes, evaluate the next version against current evidence before asking the owner to unlock it.
- Record affected tickets and gates under `alignment.next_plan_reflection` with one disposition per item: `keep`, `amend`, `defer`, or `drop`.
- Validate every proposed plan/ticket/gate amendment before presenting the review. The owner remains the authority for scope and acceptance changes.
