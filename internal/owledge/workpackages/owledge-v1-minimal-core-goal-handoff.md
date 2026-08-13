---
memory_id: "mem:owledge:global:owledge:goal:v1-minimal-core-goal-handoff"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "goal"
artifact_type: "goal_handoff"
document_version: 2
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge V1 minimal core Goal handoff"
summary: "Copy-ready bounded Goal prompt for integrating the reviewed minimal Core plan at a clean gate boundary and autonomously delivering the V1 GA candidate."
concept_tags: ["goal", "v1", "handoff", "autonomous-delivery"]
stack_tags: ["codex", "python", "markdown", "git"]
problem_patterns: ["goal-restarts-completed-work", "generic-approval-expands-scope", "publish-without-owner"]
architecture_patterns: ["immutable-goal-envelope", "single-writer", "resume-from-state"]
failure_modes: ["dirty-cherry-pick", "parallel-control-plane", "parked-feature-reactivation"]
confidence: 0.98
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-13T17:20:00+02:00"
updated_at: "2026-08-13T17:20:00+02:00"
source_hash: ""
reusable_lessons:
  - "Generic approval is valid only inside the named Goal envelope."
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:v1-minimal-core-finalization"
    confidence: 1.0
    reason: "Provides the bounded autonomous execution contract for the final plan."
---

# Copy-ready Goal Prompt

```text
/goal

Deliver the reviewed Owledge V1 Minimal Core plan to a technically green GA
candidate, then stop for explicit publication authorization.

Repository and integration
- Work on the current Owledge integration branch and its existing control plane.
- First read AGENTS.md, GOAL.md, RUN-STATE.yaml, BACKLOG.yaml, the active gate,
  and the latest clean checkpoint.
- Integrate the planning commit only when no ticket is in_progress and the
  delivery checkout is clean.
- Read in full:
  internal/owledge/plans/owledge-v1-minimal-core-finalization-plan.md
  internal/owledge/decisions/v1-minimal-core-and-product-surfaces-2026-08-13.md
  internal/owledge/ideas/post-v1-feature-parking-lot.md
  internal/owledge/workpackages/owledge-v1-minimal-core-finalization-checklist.md
- Reuse all completed v0.7.1, v0.8.0 and OW-081-01/02/03/05 evidence. Do not
  restart or reimplement completed tickets.

Immutable Goal boundary
- V1 is one product with Principles, deterministic local Core, private local
  user-global Null-Space, and thin Codex/Claude/generic MCP/CLI adapters.
- Complexity limits: 8 public CLI verbs, 5 MCP tools, 2 scopes, 3 adapters,
  <=15 files and <=8 directories in a fresh minimal profile.
- No required daemon, DB/vector store, network, model, embedding or cloud.
- All entries in post-v1-feature-parking-lot.md remain outside V1.
- Generic messages such as “continue” or “everything approved” authorize work
  only inside this envelope.
- Scope expands only after the exact owner phrase:
  AMEND GOAL BOUNDARY: <named change>

Execution order
1. Finish/reconcile the current clean gate checkpoint.
2. Execute V1M-01 and make the existing master plan/control plane the single
   reconciled execution truth. Do not create a second live backlog/run state.
3. Run G-V1M-PLAN.
4. Execute V1M-02 through V1M-10 in dependency/gate order with WIP=1 by default.
5. For every ticket: update status/checkpoint, implement only allowed paths,
   run positive/negative/recovery checks, record evidence, obtain risk-tiered
   independent QA, commit atomically, and update traceability.
6. Build and verify the clean GA candidate and run G-V1M-GA.
7. Stop before V1M-11 external publication actions.

Quality and context rules
- Load only active state, ticket, gate, directly referenced decisions and evidence.
- Use delta updates, not full historical recaps.
- Preserve user changes and never stage unrelated/untracked files.
- Every material Owledge-managed document edit increments document_version.
- Treat Markdown/Git as canonical; indexes are disposable projections.
- Skills control agent behavior; Core provides deterministic guarantees; adapters
  only translate capabilities.
- Normal recall excludes raw/parked items. Planning-purpose recall may return
  matching parked essences with park reason, source and reevaluation trigger.
- No recursive Codex invocation as proof of the active Desktop Goal host.

Autonomous authority
- Decide reversible local implementation details inside accepted contracts.
- Stop for a ninth verb, sixth MCP tool, third scope, fourth adapter, relaxed
  privacy/promotion/no-network boundary, destructive migration, credentials,
  external costs, real customer data or any parked feature proposed for V1.
- Failed gates create findings/tickets; never lower a threshold silently.

External-action stop
- Do not push, tag, publish, create a public release or upload artifacts without
  a separate explicit owner approval naming the exact candidate/action.
- At G-V1M-GA report only: shipped scope, changed decisions, gate evidence,
  residual risks, exact commit/artifact hashes, parked-register integrity and
  the publication decision required.

Success condition
- A clean GA candidate proves: zero-install Principles path; minimal install;
  local project/user-global recall; bounded context; Research/Idea deltas;
  park and later resurface; reviewed promotion/tombstones/health; cross-harness
  resume through Codex, Claude and generic MCP/CLI; safe upgrade/recovery; clean
  wheel/sdist and honest documentation.
- Do not mark the Goal complete before this candidate is green. Do not publish
  until the owner separately approves V1M-11.
```

## Recommended task topology

Prefer a **fresh Goal task after the current Goal reaches its clean gate stop**.
The current Goal owns the active checkout and should finish its atomic gate. The
fresh Goal starts with compact persisted state and this prompt, avoiding another
long conversational history while keeping one writer.
