---
name: pi-redteam-evaluate
description: Run the QA Red Team PI Agent evaluator against the latest PI intelligence report.
---

# PI Red Team Evaluate

Run from the project root:

```bash
python tools/agent_memory_cli.py --project-root . run-review-workflow --review-type multi-perspective-red-team --subject agent-memory/pi-agent/reports --question "Evaluate PI intelligence quality."
```

For a specific report:

```bash
python tools/agent_memory_cli.py --project-root . run-review-workflow --review-type multi-perspective-red-team --subject agent-memory/pi-agent/reports/pi-intelligence-YYYYMMDDHHMMSS.md --question "Evaluate this PI intelligence report."
```

The evaluator writes a 1-100 scorecard under `agent-memory/pi-agent/red-team/`.
