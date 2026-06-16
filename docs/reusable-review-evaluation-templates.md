# Reusable Review And Evaluation Templates

Status: active  
Purpose: turn repeated red-team reviews, expert evaluations, scenario simulations, and finalization reviews into reusable Markdown workflows.

## Source Patterns Consolidated

The templates consolidate patterns already used across the kit:

| Source Pattern | Existing Location | Reusable Shape |
| --- | --- | --- |
| PI Red Team scoring | `agent-memory/pi-agent/red-team/`, `skills/pi-agent-red-team-evaluator/` | 1-100 score, recommendation, blocking issues, evidence |
| Senior expert critique | planning and finalization reviews | dynamic expert lens, findings, tradeoffs, next actions |
| 10-scenario simulation | plugin and system validation tasks | scenario matrix, success metrics, residual risk |
| Enterprise / UX / DX review | publish and dashboard reviews | persona-based critique with adoption metrics |
| Closure plan | `docs/archive/finalization-report.md` | finding to fix mapping with acceptance criteria |

## Template Index

| Template | Use When | Output |
| --- | --- | --- |
| `multi-perspective-red-team-review-template.md` | A plan, plugin, repo, architecture, or RAG flow needs 3-5 critical personas | Findings, scores, cross-persona synthesis, required fixes |
| `expert-lens-evaluation-template.md` | One artifact needs a senior expert evaluation from dynamic roles | Expert findings, tradeoffs, score, next actions |
| `scenario-simulation-evaluation-template.md` | A system must be tested against realistic usage scenarios | Scenario matrix, metric results, residual risks |
| `evaluation-persona-pack-template.md` | A reviewer needs reusable persona definitions | Persona library and injection blocks |
| `review-to-task-plan-template.md` | Red-team or evaluation findings need to become executable work | Task table, acceptance criteria, QA gates |

## Default Metrics

Use these metrics unless the review needs a specialized rubric.

| Metric | Why It Exists | Default Target |
| --- | --- | ---: |
| Correctness | Prevents confident but wrong outputs | >= 90 |
| Evidence quality | Forces source-grounded reviews | >= 85 |
| Coverage | Prevents blind spots | >= 90 |
| Actionability | Makes findings executable | >= 85 |
| Scalability | Protects long-running multi-agent use | >= 85 |
| UX / DX clarity | Keeps setup and daily use practical | >= 85 |
| Safety / privacy | Blocks unsafe promotion and shared export leakage | 100 |
| Reusability | Extracts patterns and lessons from one-off reviews | >= 80 |
| Context efficiency | Avoids raw-log dumping and token waste | >= 80 |

## Review Workflow

Use the `review-evaluation-workflow` skill when a Codex, Claude, Cowork, or generic runtime agent needs a red team review, expert evaluation, scenario simulation, scorecard, promotion-readiness check, or task conversion from findings.

1. Choose the artifact: plan, report, code change, memory candidate, export, workflow, or system behavior.
2. Choose the template from `agent-memory/templates/`.
3. Inject personas from `evaluation-persona-pack-template.md` or define explicit roles inline.
4. Collect evidence: source paths, hashes, command results, screenshots, logs, memory IDs, or clearly marked assumptions.
5. Score dimensions from 1-100.
6. Classify the verdict as `block`, `revise`, `accept`, or `promote-candidate`.
7. Create the review artifact in the appropriate review, QA, evidence, or scorecard location.
8. Convert unresolved findings into tasks with acceptance criteria and QA gates.
9. Rerun QA or request the relevant verification pass after fixes land.

Runtime commands and plugins may automate these steps, but Markdown remains the source of truth. Generated indexes, dashboards, MCP tools, and command wrappers are adapters.

## Verdict Scale

| Verdict | Score | Meaning |
| --- | ---: | --- |
| `block` | 0-69 | Do not proceed; serious correctness, coverage, safety, or evidence gaps exist |
| `revise` | 70-84 | Fix material issues and rerun the review or QA gate |
| `accept` | 85-94 | Accept for the reviewed scope with documented residual risk |
| `promote-candidate` | 95-100 | Candidate for promotion only; curator or owner approval is still required |

## DoD And QA

| Check | Required Evidence |
| --- | --- |
| Artifact selected | Path, memory ID, PR, command target, or explicit identifier |
| Template selected | One template from the template index with a short reason |
| Personas injected | Role, optimization goal, distrusts, evidence requirement, success metric, confidence threshold |
| Evidence collected | Source paths, hashes, command output summaries, screenshots, logs, memory IDs, or marked assumptions |
| Scores assigned | 1-100 dimension scores and an overall score |
| Verdict classified | One of `block`, `revise`, `accept`, or `promote-candidate` |
| Findings created | Blocking issues, non-blocking risks, and evidence-backed recommendations |
| Tasks generated | Owner or role, acceptance criteria, QA gate, and follow-up artifact path |
| QA rerun defined | Command, manual verification step, reviewer pass, or reason QA cannot run yet |
| Promotion boundary preserved | Scores of 95 or above remain promotion candidates only, not automatic approval |

## Dynamic Persona Rule

Every review should declare its personas explicitly. A persona must include:

- role
- what it optimizes for
- what it distrusts
- required evidence
- success metric
- confidence threshold

Do not treat a persona's intuition as evidence. Use source paths, memory IDs, command results, hashes, or clearly marked assumptions.

## Promotion Boundary

Scores of 95 or above are promotion candidates, not automatic approvals. A curator or owner still needs to approve any write into `canonical/`, `compiled/`, `patterns/`, `lessons/`, shared exports, or external RAG systems.
