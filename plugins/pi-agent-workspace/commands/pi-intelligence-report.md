---
name: pi-intelligence-report
description: Generate a PI Agent intelligence report for parallels, trends, recurring errors, and central project candidates.
---

# PI Intelligence Report

Run this from the project root:

```bash
python tools/owledge_core.py --project-root . run-review-workflow --review-type expert-lens --subject .owledge/pi-agent/reports --question "What intelligence should be curated?"
```

The report is written to `.owledge/pi-agent/reports/`. It is candidate intelligence and requires curator or owner review before promotion.
