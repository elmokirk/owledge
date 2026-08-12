---
memory_id: "mem:demo:sample:filter-demo:evidence:filter-request-check"
tenant_id: "demo"
customer_id: "sample"
project_id: "filter-demo"
doc_type: "qa"
status: "reviewed"
visibility: "private"
data_class: "internal"
semantic_title: "Evidence: completed-item filter"
summary: "The demo records the acceptance check for the local completed-item filter."
concept_tags: ["filter", "evidence"]
stack_tags: ["demo"]
problem_patterns: []
architecture_patterns: ["evidence-linked-delivery"]
failure_modes: []
reusable_lessons: ["Record an observable outcome, not a chat-only claim."]
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-12T00:00:00Z"
updated_at: "2026-08-12T00:00:00Z"
source_hash: ""
edges:
  - type: "evidence_for"
    target: "mem:demo:sample:filter-demo:canonical:filter-request"
    confidence: 1.0
    reason: "Records the acceptance check for the scoped request."
---

# Evidence: completed-item filter

Source: [the scoped request](../canonical/filter-request.md).

| Check | Result |
| --- | --- |
| Unfinished item remains visible with filter on | pass |
| Completed item is hidden with filter on | pass |
| Stored items are unchanged when filter toggles | pass |

The result is intentionally small: it proves one feature request without
claiming a full product workflow.
