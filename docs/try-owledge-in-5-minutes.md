# Try Owledge In 5 Minutes

Use this path when a new user needs to see Owledge produce durable memory
artifacts before reading the full architecture.

## Goal

Show the core story quickly:

```text
Before: the next agent must reconstruct the work from chat history.
After: the next agent resumes from Markdown evidence, a handoff, and a checked
project memory index.
```

## Three Commands

Run these commands from a local Owledge checkout.

```bash
python tools/owledge.py quickstart --target .agent-control/tmp/owledge-five-minute-demo
python tools/owledge.py install-addon --project-root .agent-control/tmp/owledge-five-minute-demo --addon launch-demo-kit
python tools/owledge_core.py --project-root .agent-control/tmp/owledge-five-minute-demo build-memory-index
```

## Expected Result

The demo project now contains:

| Path | What it proves |
| --- | --- |
| `OWLEDGE.md` | The project has a durable context router. |
| `.owledge/evidence/launch-demo-before.md` | Evidence no longer lives only in chat. |
| `.owledge/handoffs/launch-demo-resume-handoff.md` | The next agent has scoped resume instructions. |
| `.owledge/reports/launch-demo/project-memory-cockpit.html` | A shareable static proof asset exists. |
| `.owledge/indexes/memory-index.jsonl` | Memory can be rebuilt and inspected. |

Verify the install:

```bash
python tools/owledge.py doctor --project-root .agent-control/tmp/owledge-five-minute-demo
```

Expected result: `passed` is `true`.

## Next agent prompt

Paste this into Codex, Claude Code, Cowork, or another coding agent from the
demo project root:

```text
Use Owledge project memory. Read OWLEDGE.md, then
.owledge/handoffs/launch-demo-resume-handoff.md. Continue from the evidence
listed there, do not rely on chat history, and write any new evidence or
handoff as Markdown under .owledge/.
```

## What Changed On Disk

Owledge added project-local files only. Existing source files were not rewritten.
Raw runtime logs remain private, and shared exports still require reviewed and
sanitized memory.

## When To Use A Different Path

Use `docs/quickstart.md` for a real coding project. Use
`docs/agent-integration-guide.md` when adding Owledge to an existing Markdown
knowledgebase or Obsidian-style vault.
