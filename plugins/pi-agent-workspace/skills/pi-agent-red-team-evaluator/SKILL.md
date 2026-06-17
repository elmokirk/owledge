---
name: pi-agent-red-team-evaluator
description: Use when a QA Red Team PI Agent should evaluate PI Agent reports, agent outputs, plans, or memory candidates with a 1-100 scorecard and challenge weak evidence, unsafe promotion, missing sources, recurring errors, and quality risks.
---

# PI Agent Red Team Evaluator

This plugin skill mirrors the root `skills/pi-agent-red-team-evaluator` skill.

## Core Rule

Evaluate and challenge PI outputs before promotion. Write scorecards and red-team reports under `agent-memory/pi-agent/`; never write canonical memory directly.

## Runtime Command

```bash
python tools/agent_memory_cli.py --project-root . run-review-workflow --review-type multi-perspective-red-team --subject agent-memory/pi-agent/reports --question "Evaluate PI intelligence quality and release risk."
```

## Recommendation Bands

| Score | Recommendation |
| ---: | --- |
| 95-100 | `promote-candidate` |
| 85-94 | `accept` |
| 70-84 | `revise` |
| 1-69 | `block` |

## Required Output

- 1-100 total score
- dimension scores
- blocking issues
- improvement suggestions
- evaluated artifact path
- curator-facing recommendation
