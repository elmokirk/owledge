---
memory_id: "mem:demo:sample:filter-demo:canonical:filter-request"
tenant_id: "demo"
customer_id: "sample"
project_id: "filter-demo"
doc_type: "canonical"
status: "reviewed"
visibility: "private"
data_class: "internal"
semantic_title: "Filter request: hide completed items"
summary: "The first useful slice is a local filter that hides completed items without changing stored data."
concept_tags: ["filter", "mvp"]
stack_tags: ["demo"]
problem_patterns: ["completed-items-obscure-active-work"]
architecture_patterns: ["smallest-useful-slice"]
failure_modes: ["filter-mutates-stored-items"]
reusable_lessons: ["Write the smallest observable request before implementation."]
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-12T00:00:00Z"
updated_at: "2026-08-12T00:00:00Z"
source_hash: ""
edges: []
---

# Filter request: hide completed items

## Smallest useful outcome

A user can hide completed items in the current view. The underlying items are
unchanged.

## Success signal

With the filter on, an unfinished item remains visible and a completed item is
not shown. Turning the filter off shows both again.

## Out of scope

No account settings, sync, bulk editing, or deletion.
