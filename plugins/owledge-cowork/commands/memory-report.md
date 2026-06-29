---
description: Generate a local HTML Owledge report from reviewed Markdown memory.
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
- `project-site` (requires optional `project-snapshot-kit`)
- `execution-dashboard` (requires optional `project-snapshot-kit`)

Default private report:

```bash
python tools/owledge_core.py --project-root . render-memory-report --report-type project-dashboard --audience private
```

Customer-safe report:

```bash
python tools/owledge_core.py --project-root . render-memory-report --report-type project-dashboard --audience customer
```

Shared-safe report:

```bash
python tools/owledge_core.py --project-root . render-memory-report --report-type project-dashboard --audience shared
```

Report the generated file path and any audience-filtered records.

Optional Project Snapshot Kit reports:

```bash
python tools/owledge.py install-addon --project-root . --addon project-snapshot-kit
python tools/owledge.py project-snapshot --project-root . --yes
```
