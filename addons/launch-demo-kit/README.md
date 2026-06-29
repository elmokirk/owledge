# Launch Demo Kit

Launch Demo Kit is an optional Owledge add-on for a recordable five-minute
demo. It installs safe sample artifacts into a host project so a new user can
see evidence, handoff, index, and report outputs immediately.

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon launch-demo-kit
```

## What It Adds

| Path | Purpose |
| --- | --- |
| `.owledge/evidence/launch-demo-before.md` | Shows that evidence can leave chat and become durable Markdown. |
| `.owledge/handoffs/launch-demo-resume-handoff.md` | Gives the next agent concrete resume instructions. |
| `.owledge/reports/launch-demo/project-memory-cockpit.html` | Static proof asset for README, demos, and screenshots. |
| `.owledge/templates/launch-demo-next-agent-prompt.md` | Copy-paste prompt for the next agent. |

The add-on does not change the core memory contract or runtime behavior.

