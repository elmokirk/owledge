---
title: "PI Agent Red Team Evaluation Plan"
date: "2026-05-15"
version: "0.1.0"
status: "draft"
type: "implementation-plan"
---

# PI Agent Red Team Evaluation Plan

## Evaluation Of The Approach

Adding a QA Red Team PI Agent is the right next quality layer. The PI Global Intelligence Agent creates candidate insights; the Red Team PI Agent challenges those insights before they influence planning, promotion, or central project decisions.

| Dimension | Benefit | Risk | Design Decision |
| --- | --- | --- | --- |
| Quality | Catches weak evidence, vague findings, missing sources, and unsafe promotion | Can add process overhead | Make it scorecard-based and fast |
| Scalability | Creates comparable 1-100 quality signals across projects and agents | Scores can become arbitrary without calibration | Use explicit dimensions and thresholds |
| Learning loop | Recurring low scores reveal agent failure patterns | Agents may optimize for the metric instead of the work | Keep human/curator review as final authority |
| Governance | Documents why a PI report was accepted, revised, or blocked | False confidence from automated evaluation | Scores are recommendations, not approvals |
| RAG quality | Prevents unreviewed PI interpretations from entering memory | More artifacts to filter during export | Keep red-team outputs private and non-canonical by default |

## Architecture

```text
PI Global Intelligence Agent
  -> candidate report
  -> QA Red Team PI Agent
  -> 1-100 scorecard
  -> block | revise | accept | promote-candidate
  -> curator / owner review
  -> optional promotion
```

## Score Model

| Score | Meaning | Action |
| ---: | --- | --- |
| 95-100 | Excellent, evidence-backed, promotion-ready candidate | Curator review for promotion |
| 85-94 | Good enough for planning use | Accept, fix minor notes |
| 70-84 | Incomplete or weakly evidenced | Revise before use |
| 1-69 | Unsafe, unsupported, or misleading | Block |

## Default Dimensions

| Dimension | Weight | Checks |
| --- | ---: | --- |
| Coverage | 18 | Required sections exist |
| Evidence Quality | 22 | Source links, scanned counts, hashes, commands |
| Determinism | 18 | Frontmatter, tags, patterns, edges before semantic guessing |
| Actionability | 17 | Concrete next actions and fix proposals |
| Safety / Guardrails | 15 | Candidate-only status, no secret signals, no auto-promotion |
| Challenge Strength | 10 | Weak signals, contradictions, and limits are called out |

## Implementation

| Artifact | Purpose |
| --- | --- |
| `skills/pi-agent-red-team-evaluator/` | Root skill for Red Team PI behavior |
| `plugins/pi-agent-workspace/skills/pi-agent-red-team-evaluator/` | Plugin skill mirror |
| `plugins/pi-agent-workspace/agents/pi-red-team-evaluator.md` | Runtime agent persona |
| `tools/pi-redteam-evaluate.ps1` | Deterministic evaluator |
| `agent-memory/templates/evaluation-framework-template.md` | Generic framework template |
| `agent-memory/templates/pi-red-team-evaluation-template.md` | PI report evaluation template |
| `agent-memory/templates/agent-quality-scorecard-template.md` | General agent scorecard |
| `agent-memory/pi-agent/red-team/` | Generated red-team reports |
| `agent-memory/pi-agent/evaluations/` | Evaluation artifacts |
| `agent-memory/pi-agent/scorecards/` | Scorecard history |

## Operating Rule

No PI Agent finding should be promoted without either:

1. Red Team score >= 85 and curator review, or
2. explicit owner override recorded in a decision or gate report.

## Future Extension

Create task-specific evaluation frameworks for:

- implementation quality
- planning quality
- market research quality
- design decision quality
- RAG/GraphRAG readiness
- compliance readiness
- multi-agent handoff quality
