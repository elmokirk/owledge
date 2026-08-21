---
memory_id: "mem:owledge:global:owledge:ticket:post-v1-routing-001"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "task"
artifact_type: "post_release_ticket"
document_version: 1
status: "draft"
priority: "P1"
visibility: "private"
data_class: "internal"
semantic_title: "Enforce a knowledge-routing matrix for agents and users"
summary: "Replace ambiguous folder choice with one project-scoped routing policy, explicit scope approval and an ask-user default."
concept_tags: ["post-v1", "routing", "agents", "knowledge-lifecycle"]
stack_tags: ["markdown", "python", "cli", "mcp"]
problem_patterns: ["ambiguous-knowledge-destination", "agent-infers-global-scope", "handoff-misclassified-as-lesson"]
architecture_patterns: ["versioned-routing-policy", "pure-route-classifier", "owner-approved-global-promotion"]
failure_modes: ["direct-write-outside-route", "ambiguous-content-auto-routed", "ninth-v1-verb-added"]
reusable_lessons:
  - "Ambiguous or mixed-scope knowledge should ask for an owner decision instead of choosing a durable destination."
confidence: 0.95
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "2026-08-21T00:00:00+02:00"
updated_at: "2026-08-21T00:00:00+02:00"
source_hash: ""
edges:
  - type: "relates_to"
    target: "mem:owledge:global:owledge:project_context:post-v1-feature-parking-lot"
    confidence: 1.0
    reason: "PARK-025 holds the work outside the released minimal Core."
---

# POST-V1-ROUTING-001: Enforced knowledge-routing matrix

## Outcome

Ship one versioned routing policy that tells a user or agent where a durable
item belongs, whether it may be written, and whether owner approval is needed.

## Required rules

| Incoming item | Only permitted destination | Rule |
| --- | --- | --- |
| Ephemeral session observation | No durable write | Keep it in the current context unless it becomes a Candidate. |
| Agent-to-agent continuation | Project handoff | Never label a handoff as a lesson. |
| Potential lesson, pattern, idea or research delta | Project Candidate | Use `propose`; it is excluded from normal recall until reviewed. |
| User-approved project decision | Project decision record | The owner, source and revision are required. |
| Reusable reviewed essence | Explicitly linked user-global `reviewed/` record | Only `review promote` may write it. |
| Unknown, mixed-scope or sensitive content | No write | Return `needs_user_decision` with the candidate routes and reasons. |

## Implementation contract

1. Put the matrix in one versioned project policy consumed by CLI, MCP and
   discoverable skills, rather than duplicating prose in folders.
2. Add a pure classifier that returns `allow`, `deny` or `needs_user_decision`.
   It must not create files while classifying.
3. Reject direct agent writes outside the selected route. Record route, scope,
   actor, source and reason in Candidate and review receipts.
4. Require explicit owner scope for user-global promotion. The agent must not
   infer cross-project reuse from a summary or a session reflection.
5. Test the exact failure reported by the owner: a session learning cannot
   become a handoff, and ambiguous content asks the user instead of choosing a
   legacy `lessons/` folder.

## Boundary

This is proposed post-V1 work. It must not reactivate any parked Hub,
enterprise or remote-sync feature, and it may not add a ninth public V1 verb
without a separate owner decision.
