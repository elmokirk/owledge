---
name: pi-agent-global-intelligence
description: Use when a PI Agent should act as a global knowledge assistant that finds parallels, trends, repeated agent errors, and central project candidates from Owledge.
---

# PI Agent Global Intelligence

This plugin skill mirrors the root `skills/pi-agent-global-intelligence` skill. Use it for Claude/Cowork, Codex, and other runtimes that load skills from `plugins/pi-agent-workspace/skills/`.

## Core Rule

PI intelligence is candidate knowledge. Write project-level findings to `.owledge/pi-agent/`, private user-level findings to `global-memory/coach/`, and never directly promote them into canonical memory.

## Runtime Command

```bash
python tools/owledge_core.py --project-root . run-review-workflow --review-type expert-lens --subject .owledge/pi-agent/reports --question "What cross-project intelligence should be curated?"
```

## Artifact Workspace

- `.owledge/pi-agent/reports/`
- `.owledge/pi-agent/parallels/`
- `.owledge/pi-agent/trends/`
- `.owledge/pi-agent/recurring-errors/`
- `.owledge/pi-agent/concepts/`
- `.owledge/pi-agent/indexes/`
- `global-memory/coach/`

## Workflow

1. Read `USER_CONTEXT.md` when present, then `OWLEDGE.md`.
2. Inspect global preferences, goals, ideas, research and patterns when relevant.
3. Inspect memory index and relevant project memory folders.
4. Run or simulate the PI intelligence report.
5. Classify findings as parallels, trends, recurring errors, central project candidates or private coach recommendations.
6. Recommend promotions to the memory curator or owner, but do not apply them automatically.
