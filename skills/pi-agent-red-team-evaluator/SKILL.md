---
name: pi-agent-red-team-evaluator
description: Use when a QA Red Team PI Agent should evaluate PI Agent reports, agent outputs, plans, or memory candidates with a 1-100 scorecard and challenge weak evidence, unsafe promotion, missing sources, recurring errors, and quality risks.
---

# PI Agent Red Team Evaluator

## Core Rule

Challenge PI Agent outputs before promotion. The evaluator writes scorecards and red-team reports, not canonical truth.

## When Running

1. Read the target artifact and its source links.
2. Prefer deterministic checks: required sections, evidence links, explicit source files, privacy guardrails, promotion status, and actionability.
3. Score every evaluation from 1-100.
4. Classify the recommendation:
   - `block`: score below 70 or serious safety issue
   - `revise`: score 70-84
   - `accept`: score 85-94
   - `promote-candidate`: score 95-100, still requiring curator approval
5. Write findings under `agent-memory/pi-agent/red-team/`, `evaluations/`, or `scorecards/`.

## Runtime Command

```powershell
tools\pi-redteam-evaluate.ps1 -ProjectRoot .
```

Pass a specific report when needed:

```powershell
tools\pi-redteam-evaluate.ps1 -ProjectRoot . -ReportPath agent-memory\pi-agent\reports\pi-intelligence-YYYYMMDDHHMMSS.md
```

## Evaluation Dimensions

| Dimension | Meaning |
| --- | --- |
| Coverage | Required sections and expected scope are present |
| Evidence Quality | Claims cite source files, counts, hashes, or validation commands |
| Determinism | Findings rely on frontmatter, typed edges, and explicit metadata before semantic guessing |
| Actionability | Findings lead to concrete fixes, owners, gates, or next actions |
| Safety / Guardrails | Private data, shared-export safety, and promotion boundaries are respected |
| Challenge Strength | Weak signals, contradictions, and missing data are explicitly called out |

## Output Standard

Every evaluation must include:

- total score from 1-100
- dimension scores
- blocking issues
- improvement suggestions
- source artifact path
- recommendation

## Promotion Boundary

Even a score of 95+ is only `promote-candidate`. A memory curator or owner must still approve any write into `canonical/`, `compiled/`, `patterns/`, or `lessons/`.
