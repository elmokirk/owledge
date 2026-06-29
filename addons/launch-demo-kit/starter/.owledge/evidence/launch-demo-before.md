---
memory_id: "mem:tenant-demo:customer-demo:owledge-launch-demo:qa:launch-demo-before"
tenant_id: "tenant-demo"
customer_id: "customer-demo"
project_id: "owledge-launch-demo"
doc_type: "qa"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Before Owledge context loss evidence"
summary: "Synthetic QA evidence showing the problem a new agent faces when project context only lives in chat."
concept_tags: ["launch-demo", "context-loss"]
stack_tags: ["markdown"]
problem_patterns: ["agent-context-loss", "handoff-friction"]
architecture_patterns: ["markdown-first-memory"]
failure_modes: ["chat-only-plan-lost", "evidence-scattered"]
reusable_lessons: ["Move decisions and evidence into Markdown before the next agent resumes."]
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-19T00:00:00Z"
updated_at: "2026-06-19T00:00:00Z"
retention_class: "standard"
stale_after: ""
expires_at: ""
last_reviewed_at: "2026-06-19T00:00:00Z"
review_cycle: "quarterly"
source_hash: ""
edges: []
---

# Before Owledge Context Loss Evidence

## Evidence Summary

A previous agent decided that the project needs a launch demo, a trust page, and
a PI proof loop. Without durable memory, the next agent would need the user to
repeat that context.

## Source Links

- `docs/launch-readiness.md`
- `docs/try-owledge-in-5-minutes.md`

## Hashes

Synthetic demo artifact. No source hash is required.

## Validation Notes

The important behavior is that this evidence can be discovered by path and
memory index instead of transcript recall.
