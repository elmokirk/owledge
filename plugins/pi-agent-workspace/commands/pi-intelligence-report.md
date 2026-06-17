---
name: pi-intelligence-report
description: Generate a PI Agent intelligence report for parallels, trends, recurring errors, and central project candidates.
---

# PI Intelligence Report

Run this from the project root:

```bash
python tools/agent_memory_cli.py --project-root . run-review-workflow --review-type expert-lens --subject agent-memory/pi-agent/reports --question "What intelligence should be curated?"
```

The report is written to `agent-memory/pi-agent/reports/`. It is candidate intelligence and requires curator or owner review before promotion.
