---
memory_id: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:qa:evaluation-framework-SLUG"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project_id: "PROJECT_ID"
doc_type: "qa"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "Evaluation Framework"
summary: "Scoring framework for agent output quality with 1-100 score, dimensions, thresholds, and required evidence."
concept_tags:
  - "evaluation-framework"
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
edges: []
---

# Evaluation Framework

## Scope

Define the artifact, task type, or agent behavior being evaluated.

## Score Dimensions

| Dimension | Weight | Pass Target | Evidence |
| --- | ---: | ---: | --- |
| Correctness | 25 | 90 | Source-grounded answer or passing tests |
| Evidence Quality | 20 | 85 | Linked files, hashes, reports, or commands |
| Actionability | 20 | 85 | Clear next steps, owners, and fixes |
| Risk / Safety | 15 | 90 | Privacy, compliance, and blast-radius checks |
| Reusability | 10 | 80 | Patterns, lessons, templates, or reusable outputs |
| Token Efficiency | 10 | 80 | Compact context and no raw-log dumping |

## Score Meaning

| Score | Meaning |
| ---: | --- |
| 95-100 | Production-grade, strong evidence, low residual risk |
| 85-94 | Usable with minor fixes or review notes |
| 70-84 | Needs revision before promotion |
| 0-69 | Block; do not promote or rely on this output |

## Required Output

- Total score from 1-100
- Dimension scores
- Blocking issues
- Non-blocking improvements
- Evidence links
- Promotion recommendation
