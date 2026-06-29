---
memory_id: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:workpackage:phase-tasklist"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project_id: "PROJECT_ID"
doc_type: "workpackage"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "Phase tasklist"
summary: "Agent-facing implementation and QA checklist for a multi-phase Owledge plan."
concept_tags: ["phase-checklist", "qa-gates", "subagent-coordination"]
stack_tags: []
problem_patterns: []
architecture_patterns: ["orchestrator-owned-tasklist", "lane-handoff"]
failure_modes: ["checkbox-without-evidence", "partial-phase-resume"]
confidence: 0.7
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:plan:PLAN_ID"
    confidence: 0.8
    reason: "This tasklist operationalizes the referenced plan."
---

# PROJECT Phase Tasklist

## Resume State

Current resume point: **Phase N - PHASE NAME**.

## Agent Rules

- Orchestrator owns this tasklist and central release notes.
- Subagents write lane handoffs under `.owledge/workpackages/<wp>/lanes/<agent-id>.md`.
- A checkbox is only checked after its QA evidence exists.
- If a checked box becomes stale after later edits, uncheck it and rerun the phase gate.
- Resume rule: find the first unchecked checkbox and continue there.

## Phase N - PHASE NAME

Goal: PHASE GOAL.

QA gate:

```bash
COMMANDS
```

Checklist:

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done
