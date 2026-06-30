---
title: "Project Snapshot Kit Profile"
status: "active"
type: "project-snapshot-profile"
project_snapshot_enabled: true
default_token_budget: 12000
full_site_token_budget: 40000
allow_large_context_default: false
generated_html_default: false
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
---

# Project Snapshot Kit Profile

This optional Owledge add-on generates project orientation snapshots and static
HTML views from local Markdown memory. Markdown remains the source of truth.

## Defaults

- Ask before generating snapshots or HTML in interactive mode.
- Use `.owledge/indexes/memory-index.jsonl` before loading Markdown bodies.
- Treat `agent-plans/` as volatile source evidence.
- Treat `.owledge/plans/` as durable Owledge planning memory.
- Keep generated HTML local and static.
