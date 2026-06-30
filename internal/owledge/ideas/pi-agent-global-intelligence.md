---
memory_id: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:idea:pi-agent-global-intelligence"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project_id: "PROJECT_ID"
doc_type: "idea"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "PI Agent Global Intelligence"
summary: "A PI Agent layer that finds cross-project parallels, trends, repeated agent errors, and central project opportunities from Owledge."
concept_tags:
  - "pi-agent"
  - "global-knowledge-assistant"
  - "cross-project-intelligence"
  - "quality-loop"
stack_tags:
  - "markdown"
  - "graphrag"
  - "owledge"
problem_patterns:
  - "agents-repeat-avoidable-mistakes"
  - "project-ideas-get-lost-between-sessions"
  - "cross-project-lessons-are-hard-to-reuse"
architecture_patterns:
  - "markdown-first-control-layer"
  - "curated-intelligence-workspace"
failure_modes:
  - "auto-promoted-agent-interpretations"
  - "unreviewed-trend-reports-treated-as-truth"
reusable_lessons:
  - "Keep PI findings as candidates until reviewed by a curator or owner."
confidence: 0.86
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "2026-05-15T00:00:00Z"
updated_at: "2026-05-15T00:00:00Z"
source_hash: ""
idea_stage: "implementation-plan"
idea_source: "user-request"
idea_fit:
  current_project: "high"
  future_project: "high"
  cross_project: "high"
planning_relevance:
  - "check-before-new-plan"
  - "check-before-agent-runtime-design"
edges:
  - type: "relates_to"
    target: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:idea:IDEA_SLUG"
    reason: "This becomes the first PI intelligence idea and should compare future ideas against it."
    confidence: 0.5
    external: true
---

# PI Agent Global Intelligence

## Evaluation

This is a strong extension for the kit because the existing memory structure already captures ideas, decisions, lessons, patterns, sessions, evidence, and exports. A PI Agent can turn that into a practical quality loop: repeated errors become fix patterns, recurring idea clusters become central project candidates, and cross-project parallels become visible before planning starts from zero.

The main risk is authority confusion. PI reports must remain candidate intelligence, not canonical truth. The correct model is: PI Agent observes, logs, clusters, and recommends; a human, orchestrator, or memory curator approves promotions.

## Proposed Capability

- Find repeated agent errors across sessions, handoffs, QA reports, and failure modes.
- Find trends across ideas, goals, canonical docs, patterns, lessons, and ADRs.
- Derive central project candidates when multiple projects or ideas converge on the same problem pattern.
- Produce private or internal reports in `.owledge/pi-agent/`.
- Route stable findings to memory curator review before they enter `canonical/`, `compiled/`, `patterns/`, or `lessons/`.

## First Implementation Slice

- Add PI Agent artifact workspace.
- Add a `pi-agent-global-intelligence` skill.
- Add a `pi-intelligence-report` runtime command.
- Add templates for reports, parallels, recurring errors, and central project candidates.
- Add this file as Idea 1 so future planning has a concrete reference point.
