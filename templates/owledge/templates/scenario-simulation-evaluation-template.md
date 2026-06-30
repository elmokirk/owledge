---
memory_id: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:qa:scenario-simulation-SLUG"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project_id: "PROJECT_ID"
doc_type: "qa"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "Scenario Simulation Evaluation"
summary: "Reusable template for simulating realistic usage scenarios and measuring scalability, retrieval precision, UX/DX, safety, and maintainability."
concept_tags:
  - "scenario-simulation"
  - "evaluation"
  - "qa"
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
simulation_target: "PATH_OR_MEMORY_ID"
scenario_count: 10
score_total: 0
edges: []
---

# Scenario Simulation Evaluation

## Simulation Goal

Describe what must be proven under realistic use.

## Scenario Matrix

| ID | Scenario | Persona / Runtime | Load / Complexity | Expected Outcome | Success Metric |
| --- | --- | --- | --- | --- | --- |
| S01 | First install from repository link | Midlevel developer | Fresh machine, no prior context | Project initializes without manual archaeology | Setup succeeds in <= 15 minutes |
| S02 | New agent starts in existing project | Codex / Claude / generic agent | Existing memory with decisions and tasks | Agent reads correct context before planning | Context pack includes relevant sources only |
| S03 | Parallel agent work | 5-50 agents | Multiple sessions and handoffs | No canonical overwrite or scope confusion | 0 duplicate ownership conflicts |
| S04 | Long-running project | 5 months of memory | Many sessions, decisions, reports | Retrieval still finds current truth | >= 85 retrieval precision |
| S05 | Shared RAG export | RAG adapter | Mixed private/shared data | Private and unreviewed data excluded | 0 unsafe shared records |
| S06 | Cross-project parallel discovery | Enterprise hub | Many projects with overlapping tags | Similar patterns become candidates | >= 80 candidate usefulness |
| S07 | Runtime plugin capture | Cowork / Claude / Codex | Raw chat and tool events | Raw logs remain private | 0 raw logs in shared export |
| S08 | Design/report generation | HTML report skill | User asks visual report | Output cites Markdown sources | 100% source traceability |
| S09 | Compliance-sensitive work | Private/customer data | Confidential docs present | Data class and visibility respected | 0 policy violations |
| S10 | Recovery after stale memory | Old research/preferences | Expired dates and contradictions | Stale records flagged, not deleted | Staleness debt reported |

## Metrics

| Metric | Target | Actual | Evidence |
| --- | ---: | ---: | --- |
| Retrieval precision | >= 85 | 0 | Answer-source match evaluation |
| Context efficiency | >= 80 | 0 | Included chars vs relevant sources |
| Scalability | >= 85 | 0 | Scenario load results |
| Safety / privacy | 100 | 0 | Shared export and data-class checks |
| UX / DX success | >= 85 | 0 | New-user setup and command clarity |
| Maintainability | >= 85 | 0 | Clear ownership, templates, docs |
| Reusability | >= 80 | 0 | Lessons, patterns, reusable artifacts |

## Scenario Results

### S01: Scenario Name

| Check | Result | Evidence | Notes |
| --- | --- | --- | --- |
| | pass/fail | | |

Score: 0/100  
Residual risk:

## Aggregate Findings

| Finding | Severity | Affected Scenarios | Evidence | Fix |
| --- | --- | --- | --- | --- |
| | P0/P1/P2/P3 | | | |

## Verdict

Overall score: 0/100  
Recommendation: `block | revise | accept | promote-candidate`

## Follow-Up Tasks

| Task | Owner | Acceptance Criteria | Priority |
| --- | --- | --- | --- |
| | | | |
