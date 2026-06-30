# PI Agent Workspace Adapter

Optional standalone adapter for Owledge.

## Purpose

The PI Agent checks workspace quality, asks targeted questions, inspects ideas before new plans, and routes quality review through project-local Owledge. It also provides a global intelligence mode for parallels, trends, recurring agent errors, and central project candidates. A QA Red Team PI Agent can challenge those reports with a 1-100 scorecard.

## Components

```text
.claude-plugin/plugin.json
.codex-plugin/plugin.json
agents/pi-workspace-guardian.md
agents/pi-global-intelligence.md
agents/pi-red-team-evaluator.md
commands/pi-workspace-check.md
commands/pi-intelligence-report.md
commands/pi-redteam-evaluate.md
skills/pi-agent-workspace-quality/SKILL.md
skills/pi-agent-global-intelligence/SKILL.md
skills/pi-agent-red-team-evaluator/SKILL.md
skills/personal-pi-agent/SKILL.md
```

## Rule

The adapter is not canonical memory. Project-local Markdown remains the source of truth.

## Default Command

```bash
python tools/owledge.py doctor --project-root .
```

This default check is read-only. Pass `-BuildIndex` only when index regeneration is wanted.

Generate a PI intelligence report:

```bash
python tools/owledge_core.py --project-root . run-review-workflow --review-type expert-lens --subject .owledge/pi-agent/reports --question "What intelligence should be curated?"
```

Reports are written to `.owledge/pi-agent/reports/` and remain candidate knowledge until reviewed.

Personal PI findings can read `USER_CONTEXT.md` and `global-memory/` when present. Private coach reports are written under `global-memory/coach/` and must not become shared RAG input without explicit review and sanitization.

Evaluate the latest PI report with the Red Team scorecard:

```bash
python tools/owledge_core.py --project-root . run-review-workflow --review-type multi-perspective-red-team --subject .owledge/pi-agent/reports --question "Evaluate PI intelligence quality."
```

## Rules

- Do not overwrite project-local memory.
- Do not promote ideas automatically.
- Use ideas as planning inputs, not as accepted scope.
- Ask concise questions when quality, context, or acceptance criteria are missing.
- Treat PI intelligence as candidate knowledge until a curator or owner approves promotion.
- Treat Red Team scores as quality gates and calibration signals, not as automatic approval.
