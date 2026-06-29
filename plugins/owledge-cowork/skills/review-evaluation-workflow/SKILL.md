---
name: review-evaluation-workflow
description: Use when the user asks for red team, expert review, evaluation, scenario simulation, scorecard, promotion readiness, promotion-readiness checks, or converting review findings into tasks.
version: 0.1.0
---

# Review Evaluation Workflow

## Core Rule

Markdown review artifacts are the source of truth. Runtime tools, commands, dashboards, plugins, and MCP servers are adapters only.

## Triggers

Use this skill for requests that mention red team, expert review, evaluation, scenario simulation, scorecard, QA score, acceptance verdict, promotion readiness, or turning findings into tasks.

## Workflow

1. Choose the artifact: identify the plan, report, code change, memory candidate, export, workflow, or system behavior being reviewed.
2. Choose the template from `.owledge/templates/`.
3. Inject personas from `evaluation-persona-pack-template.md` or define explicit roles inline.
4. Collect evidence: source paths, hashes, command results, screenshots, logs, memory IDs, or stated assumptions.
5. Score dimensions from 1-100.
6. Classify verdict:
   - `block`: below 70 or any serious safety/privacy issue
   - `revise`: 70-84
   - `accept`: 85-94
   - `promote-candidate`: 95-100, still requiring curator or owner approval
7. Create the review artifact in the appropriate review, QA, evidence, or scorecard location.
8. Convert findings into tasks with acceptance criteria and QA gates.
9. Rerun QA or request the relevant verification pass after fixes land.

When available, create the draft artifact with:

```bash
python tools/owledge_core.py --project-root . run-review-workflow --review-type expert-lens --subject path/to/artifact.md --question "What should this review decide?"
```

If the command is unavailable in a host project, copy the matching template manually and preserve the same frontmatter fields, evidence requirements, score scale, and promotion boundary.

## Template Selection

| Template | Use When | Required Output |
| --- | --- | --- |
| `multi-perspective-red-team-review-template.md` | A plan, plugin, repo, architecture, or RAG flow needs 3-5 critical personas | Persona findings, dimension scores, verdict, required fixes |
| `expert-lens-evaluation-template.md` | One artifact needs a senior expert review from a focused role | Expert findings, tradeoffs, score, recommendation |
| `scenario-simulation-evaluation-template.md` | Behavior must be tested against realistic usage scenarios | Scenario matrix, success metrics, residual risks |
| `evaluation-persona-pack-template.md` | Reviewers need reusable persona definitions | Persona injection blocks with evidence requirements |
| `review-to-task-plan-template.md` | Review findings need executable follow-up work | Task table, acceptance criteria, owners, QA gates |

## Success Metrics

Score these dimensions unless the review defines a stricter rubric.

| Metric | Default Target |
| --- | ---: |
| Correctness | >= 90 |
| Evidence quality | >= 85 |
| Coverage | >= 90 |
| Actionability | >= 85 |
| Scalability | >= 85 |
| UX / DX clarity | >= 85 |
| Safety / privacy | 100 |
| Reusability | >= 80 |
| Context efficiency | >= 80 |

Every review artifact must include:

- target artifact path or identifier
- selected template and personas
- evidence links or clearly marked assumptions
- dimension scores from 1-100
- overall verdict
- blocking findings, if any
- task conversion path for unresolved findings
- QA rerun or verification requirement

Scores of 95 or above are promotion candidates only, not automatic approval.
