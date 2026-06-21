---
memory_id: "mem:tenant-demo:customer-demo:owledge-launch-demo:handoff:launch-demo-resume"
tenant_id: "tenant-demo"
customer_id: "customer-demo"
project_id: "owledge-launch-demo"
doc_type: "handoff"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Launch demo resume handoff"
summary: "Next-agent handoff for the five-minute Owledge demo."
concept_tags: ["launch-demo", "handoff"]
stack_tags: ["markdown"]
problem_patterns: ["agent-context-loss"]
architecture_patterns: ["markdown-first-memory"]
failure_modes: ["chat-only-handoff"]
reusable_lessons: ["A durable handoff should include objective, evidence, risks, and the next instruction."]
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
edges:
  - type: "evidence_for"
    target: "mem:tenant-demo:customer-demo:owledge-launch-demo:qa:launch-demo-before"
    confidence: 0.9
    reason: "The evidence explains why the handoff exists."
---

# Launch Demo Resume Handoff

## Objective And Success Criteria

Continue the demo from durable Markdown memory. Success means the next agent can
state the objective, cite evidence, and propose the next step without asking for
chat-history reconstruction.

## Current Artifact Versions

- Evidence: `agent-memory/evidence/launch-demo-before.md`
- Static report: `agent-memory/reports/launch-demo/project-memory-cockpit.html`
- Prompt template: `agent-memory/templates/launch-demo-next-agent-prompt.md`

## Decisions Made In This Cycle

- Keep Owledge core small.
- Put launch, trust, runtime-conformance, and PI proof into optional add-ons.
- Use reviewed Markdown artifacts as the visible proof.

## Blockers And Risks

- Do not treat demo artifacts as customer evidence.
- Do not promote demo records into shared RAG.

## Next Agent Instructions

Read this handoff and the linked evidence. Then explain what changed on disk and
which command should run next for verification.
