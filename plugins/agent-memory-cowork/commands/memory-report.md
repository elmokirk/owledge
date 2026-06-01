---
description: Generate a local HTML Agent Memory report from reviewed Markdown memory.
---

Generate a local HTML view. Markdown remains canonical.

If the report type is unclear, default to `project-dashboard`.

Valid report types:

- `decision`
- `handoff`
- `rag-readiness`
- `agent-activity`
- `project-dashboard`
- `website-ui`

Default private report:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\render-memory-report.ps1 -ProjectRoot . -ReportType project-dashboard -Audience private
```

Customer-safe report:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\render-memory-report.ps1 -ProjectRoot . -ReportType project-dashboard -Audience customer
```

Shared-safe report:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\render-memory-report.ps1 -ProjectRoot . -ReportType project-dashboard -Audience shared
```

Report the generated file path and any audience-filtered records.
