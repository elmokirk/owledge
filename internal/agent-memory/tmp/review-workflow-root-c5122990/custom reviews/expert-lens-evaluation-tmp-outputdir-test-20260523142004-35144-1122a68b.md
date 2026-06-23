---
memory_id: "mem:tenant-local:customer-local:review-workflow-root-c5122990:qa:expert-lens-evaluation-tmp-outputdir-test-20260523142004-35144-1122a68b"
tenant_id: "tenant-local"
customer_id: "customer-local"
project_id: "review-workflow-root-c5122990"
doc_type: "qa"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "Expert Lens Evaluation: subject.md"
summary: "Reusable template for evaluating a concept, architecture, plan, repo, plugin, RAG setup, or agent harness from one or more expert perspectives."
concept_tags:
  - "expert-review"
  - "evaluation"
  - "scorecard"
stack_tags: []
problem_patterns: []
architecture_patterns: []
failure_modes: []
reusable_lessons: []
confidence: 0.7
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "2026-05-23T14:20:04Z"
updated_at: "2026-05-23T14:20:04Z"
source_hash: ""
evaluated_artifact: "subject.md"
expert_lenses:
  - "Senior AI Agent Engineer"
  - "RAG / GraphRAG Engineer"
  - "Power User / Builder"
score_total: 0
edges: []
---

# Expert Lens Evaluation

## Evaluation Target

| Field | Value |
| --- | --- |
| Artifact | `subject.md` |
| User goal | |
| Evaluation question | |
| Decision needed | |
| Context budget | |

## Expert Lenses

Use the defaults or replace them with task-specific roles.

| Lens | What This Lens Cares About | Failure Modes To Hunt | Success Metric |
| --- | --- | --- | --- |
| Senior AI Agent Engineer | Agent workflows, delegation, memory boundaries, harness quality | Agents duplicate work, overwrite truth, lack evidence | Agents can resume and coordinate without rereading everything |
| RAG / GraphRAG Engineer | Retrieval quality, stable IDs, graph edges, chunking, freshness | Raw logs in RAG, unstable IDs, weak metadata, stale knowledge | Answers cite precise sources and find cross-project parallels |
| Power User / Builder | Setup speed, UX, DX, daily usefulness, mental model clarity | Too many steps, unclear rules, brittle install, hidden magic | A new project can be productive in one session |

## Evidence Reviewed

| Source | Type | Why It Matters | Hash / Date |
| --- | --- | --- | --- |
| `path` | doc/code/report | | |

## Evaluation Metrics

| Metric | Weight | Score 1-100 | Evidence | Notes |
| --- | ---: | ---: | --- | --- |
| Goal fit | 15 | 0 | | |
| Architectural soundness | 15 | 0 | | |
| Retrieval / memory readiness | 15 | 0 | | |
| Agent workflow quality | 15 | 0 | | |
| Scalability / maintainability | 10 | 0 | | |
| UX / DX | 10 | 0 | | |
| Evidence and auditability | 10 | 0 | | |
| Risk and compliance posture | 10 | 0 | | |

Overall score: 0/100

## Findings By Lens

### Senior AI Agent Engineer

| Finding | Severity | Evidence | Recommendation |
| --- | --- | --- | --- |
| | P0/P1/P2/P3 | | |

### RAG / GraphRAG Engineer

| Finding | Severity | Evidence | Recommendation |
| --- | --- | --- | --- |
| | P0/P1/P2/P3 | | |

### Power User / Builder

| Finding | Severity | Evidence | Recommendation |
| --- | --- | --- | --- |
| | P0/P1/P2/P3 | | |

## Contradictions And Tradeoffs

| Tradeoff | Benefit | Cost | Decision |
| --- | --- | --- | --- |
| | | | |

## Verdict

Score: 0/100  
Recommendation: `block | revise | accept | promote-candidate`  
Confidence: 0.0

## Next Actions

| Action | Owner | Acceptance Criteria | Evidence To Attach |
| --- | --- | --- | --- |
| | | | |
