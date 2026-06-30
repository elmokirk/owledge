---
name: pi-agent-global-intelligence
description: Use when a PI Agent should act as a global knowledge assistant that finds parallels, trends, repeated agent errors, and central project candidates from Owledge.
---

# PI Agent Global Intelligence

## When To Use

Use this skill when the user asks the PI Agent to:

- find parallels across projects, ideas, decisions, sessions, patterns, or lessons
- detect trends in Owledge
- identify repeated agent mistakes and propose fixes
- derive central project candidates from existing goals and ideas
- inspect global user goals, preferences, ideas, research and personal patterns
- produce a global knowledge report for review

## Core Rule

PI intelligence is candidate knowledge. Do not edit `canonical/`, `compiled/`, `patterns/`, or `lessons/` directly from this skill. Write findings to `.owledge/pi-agent/` and ask for curator or owner review before promotion.

## Workspace

Use these artifact folders:

| Path | Purpose |
| --- | --- |
| `.owledge/pi-agent/reports/` | Periodic intelligence reports |
| `.owledge/pi-agent/parallels/` | Parallel candidates across workstreams or projects |
| `.owledge/pi-agent/trends/` | Trend summaries and signal logs |
| `.owledge/pi-agent/recurring-errors/` | Repeated agent failure modes and fix proposals |
| `.owledge/pi-agent/concepts/` | Central project candidates and concept derivatives |
| `.owledge/pi-agent/indexes/` | Generated helper indexes |
| `global-memory/coach/` | Private user-level coach reports and sourced recommendations |

## Workflow

1. Read `USER_CONTEXT.md` when present, then `OWLEDGE.md`.
2. Build or inspect `.owledge/indexes/memory-index.jsonl` if present.
3. Inspect relevant global memory groups: `global-memory/preferences/`, `global-memory/goals/`, `global-memory/ideas/`, `global-memory/research/`, and `global-memory/patterns/`.
4. Inspect only relevant project memory groups: `ideas/`, `canonical/`, `compiled/`, `patterns/`, `lessons/`, `decisions/`, `handoffs/`, `evidence/`, and reviewed session summaries.
5. Run the runtime command when available:

```bash
python tools/owledge_core.py --project-root . run-review-workflow --review-type expert-lens --subject .owledge/pi-agent/reports --question "What cross-project intelligence should be curated?"
```

6. Review the generated report and classify findings:
   - `parallel-candidate`
   - `trend-signal`
   - `recurring-error`
   - `central-project-candidate`
   - `promotion-candidate`
6. For high-confidence findings, create a short recommendation for the memory curator. Do not promote automatically.

## Reporting Standard

Each report must include:

- scanned artifact count
- top parallel candidates
- top trend signals
- recurring agent errors with likely causes
- solution proposals for repeated failures
- central project candidates with source signals
- explicit next actions and review owner

## Quality Bar

- Prefer deterministic signals first: shared `problem_patterns`, `architecture_patterns`, `failure_modes`, `concept_tags`, and typed edges.
- Do not use raw chat logs as primary truth.
- Keep reports compact and link source files.
- Preserve contradictions instead of resolving them silently.
- Do not include private customer data in shared reports.
- If a finding relies on unreviewed or private data, mark it clearly.
