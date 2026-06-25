---
memory_id: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:plan:swarm-orchestration-SLUG"
doc_type: "plan"
status: "draft"
visibility: "private"
data_class: "internal"
review_status: "unreviewed"
sanitization_status: "not_required"
---

# Swarm Orchestration Plan

## Original Goal

## MVP Cutline

## Non-Goals

## Agent Lanes

| Lane | Runtime | Task | Allowed writes |
| --- | --- | --- | --- |
| orchestrator | Codex / Claude / Hermes | | plans, workpackages |
| worker | Codex / Claude / Hermes | | evidence, handoffs |
| reviewer | Codex / Claude / Hermes | | reviews |
| curator | Codex / Claude / Hermes | | promotion proposals |

## Review Gate

No promotion until evidence and review artifacts exist.

