---
memory_id: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:qa:multi-perspective-red-team-SLUG"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project_id: "PROJECT_ID"
doc_type: "qa"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "Multi-Perspective Red Team Review"
summary: "Reusable red-team review template with dynamic personas, evidence requirements, success metrics, scores, and action plan."
concept_tags:
  - "red-team"
  - "multi-perspective-review"
  - "evaluation"
stack_tags: []
problem_patterns: []
architecture_patterns: []
failure_modes: []
reusable_lessons: []
confidence: 0.7
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "YYYY-MM-DDT00:00:00Z"
updated_at: "YYYY-MM-DDT00:00:00Z"
source_hash: ""
review_subject: "PATH_OR_MEMORY_ID"
review_question: "What should this review prove or disprove?"
persona_count: 3
score_total: 0
promotion_recommendation: "block | revise | accept | promote-candidate"
edges: []
---

# Multi-Perspective Red Team Review

## Review Setup

| Field | Value |
| --- | --- |
| Subject | `PATH_OR_MEMORY_ID` |
| Review question | |
| Decision needed | |
| Reviewer / orchestrator | |
| Evidence cutoff | |

## Success Metrics

| Metric | Target | Actual | Evidence |
| --- | ---: | ---: | --- |
| Finding precision | >= 85 | 0 | Findings cite real source paths or memory IDs |
| Coverage | >= 90 | 0 | Each critical area has a persona review |
| Actionability | >= 85 | 0 | Each serious finding has a concrete fix |
| Risk detection | >= 90 | 0 | Privacy, scalability, safety, UX/DX, and maintenance risks checked |
| Token efficiency | >= 80 | 0 | Review avoids raw-log dumping and quotes only relevant excerpts |

## Dynamic Persona Inputs

Replace the rows below with task-specific perspectives. Keep the first three unless there is a reason to specialize.

| Persona ID | Perspective | Primary Attack Surface | Success Metric | Required Evidence |
| --- | --- | --- | --- | --- |
| P1 | Scalability / Systems Engineer | Concurrency, data growth, maintainability, runtime boundaries | System still works after 100+ agents or long-term use | File paths, scale assumptions, bottlenecks |
| P2 | Enterprise / Compliance Reviewer | Governance, privacy, auditability, role boundaries | Safe enough for team or agency rollout | Policy docs, export rules, data classes |
| P3 | UX / DX Midlevel Adopter | Install path, first-run clarity, daily usability | A new user can succeed without hidden knowledge | Quickstart, commands, examples |

## Baseline Facts

- Source files reviewed:
- Commands run:
- Constraints:
- Assumptions:

## Persona Reviews

### P1: PERSONA_NAME

**Review stance:**  

| Finding | Severity | Evidence | Impact | Fix |
| --- | --- | --- | --- | --- |
| | P0/P1/P2/P3 | `path:line` or `memory_id` | | |

**Score:** 0/100  
**Confidence:** 0.0  

### P2: PERSONA_NAME

**Review stance:**  

| Finding | Severity | Evidence | Impact | Fix |
| --- | --- | --- | --- | --- |
| | P0/P1/P2/P3 | `path:line` or `memory_id` | | |

**Score:** 0/100  
**Confidence:** 0.0  

### P3: PERSONA_NAME

**Review stance:**  

| Finding | Severity | Evidence | Impact | Fix |
| --- | --- | --- | --- | --- |
| | P0/P1/P2/P3 | `path:line` or `memory_id` | | |

**Score:** 0/100  
**Confidence:** 0.0  

## Cross-Persona Synthesis

| Theme | Personas Agreeing | Evidence | Decision |
| --- | --- | --- | --- |
| | | | |

## Scorecard

| Dimension | Weight | Score 1-100 | Weighted Result | Evidence |
| --- | ---: | ---: | ---: | --- |
| Correctness | 20 | 0 | 0 | |
| Coverage | 15 | 0 | 0 | |
| Evidence quality | 15 | 0 | 0 | |
| Risk handling | 15 | 0 | 0 | |
| Scalability | 10 | 0 | 0 | |
| UX / DX clarity | 10 | 0 | 0 | |
| Actionability | 10 | 0 | 0 | |
| Reusability | 5 | 0 | 0 | |

Overall score: 0/100  
Recommendation: `block | revise | accept | promote-candidate`

## Required Fixes

| Priority | Fix | Owner | Acceptance Criteria | Due |
| --- | --- | --- | --- | --- |
| P0/P1/P2/P3 | | | | |

## Open Questions

- Question:

## Reusable Lessons

- Lesson:
