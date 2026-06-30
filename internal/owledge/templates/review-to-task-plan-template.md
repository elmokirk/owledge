---
memory_id: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:task:review-to-task-plan-SLUG"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project_id: "PROJECT_ID"
doc_type: "task"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "Review To Task Plan"
summary: "Reusable template for converting red-team findings, evaluations, and review reports into executable tasks with acceptance criteria and metrics."
concept_tags:
  - "review-to-tasks"
  - "task-planning"
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
source_review: "PATH_OR_MEMORY_ID"
target_score: 95
edges: []
---

# Review To Task Plan

## Source Review

| Field | Value |
| --- | --- |
| Source review | `PATH_OR_MEMORY_ID` |
| Current score | 0/100 |
| Target score | 95/100 |
| Recommendation | `block | revise | accept | promote-candidate` |

## Finding Triage

| Finding | Severity | Source Evidence | Root Cause | Task Needed |
| --- | --- | --- | --- | --- |
| | P0/P1/P2/P3 | `path:line` or `memory_id` | | |

## Task Plan

| Task ID | Task | Owner / Agent Role | Write Scope | Acceptance Criteria | Validation |
| --- | --- | --- | --- | --- | --- |
| T01 | | | | | |

## Success Metrics

| Metric | Baseline | Target | Measurement |
| --- | ---: | ---: | --- |
| Review score | 0 | >= 95 | Re-run source evaluation |
| Blocking findings | 0 | 0 | Red-team report |
| Evidence coverage | 0 | >= 90 | Source links per finding |
| Context efficiency | 0 | >= 80 | Context pack metrics |
| Regression risk | 0 | <= 10 | Failed checks or known risks |

## Execution Order

1. Fix P0/P1 blockers.
2. Add or update validation.
3. Re-run evaluation.
4. Promote only if score and gates pass.

## QA Gates

| Gate | Command / Review | Pass Rule | Evidence Path |
| --- | --- | --- | --- |
| Memory validation | `python tools/owledge_core.py --project-root . validate-memory --strict` | 0 failed checks | |
| Contract tests | `python tools/owledge_core.py --project-root . test-contracts` | 0 failed checks | |
| Review rerun | Use matching review template | Target score reached | |

## Promotion Decision

- Decision:
- Owner:
- Evidence:
- Follow-up review date:

## Checklist

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done
