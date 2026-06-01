---
name: pi-redteam-evaluate
description: Run the QA Red Team PI Agent evaluator against the latest PI intelligence report.
---

# PI Red Team Evaluate

Run from the project root:

```powershell
tools\pi-redteam-evaluate.ps1 -ProjectRoot .
```

For a specific report:

```powershell
tools\pi-redteam-evaluate.ps1 -ProjectRoot . -ReportPath agent-memory\pi-agent\reports\pi-intelligence-YYYYMMDDHHMMSS.md
```

The evaluator writes a 1-100 scorecard under `agent-memory/pi-agent/red-team/`.
