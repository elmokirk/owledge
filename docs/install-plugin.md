# Plugin Install

Use this when you want Owledge attached to an agent runtime instead of only
using the local file/folder kit.

Plugins are optional adapters. If the runtime can follow project instructions,
the principles-only path in [agent-integration-guide.md](agent-integration-guide.md)
is enough.

The canonical plugin bundle is:

```text
plugins/agent-memory-cowork/
```

The plugin is a local adapter. It does not replace the runtime, and it does not
make Markdown memory global or hosted.

## Prerequisites

Initialize the host project first:

```bash
python tools/owledge.py init-project --target /path/to/project
python tools/owledge.py init-project --target /path/to/project --include-plugin-adapter
```

The first command is the standard project setup. The second command is the
optional adapter step when the runtime should load local Python hooks.

Then run all runtime commands from the initialized project root when possible.
The hooks discover:

- `PROJECT_CONTEXT.md`
- `agent-memory/`
- `tools/agent_memory_cli.py`

## Codex

Install shape:

```text
plugins/agent-memory-cowork/.codex-plugin/plugin.json
plugins/agent-memory-cowork/skills/
plugins/agent-memory-cowork/commands/
```

Use the Codex plugin flow when available. For manual setup, copy the full
`plugins/agent-memory-cowork/` directory into the plugin area that your Codex
runtime reads from, then start Codex from the initialized project root.

Verify:

```bash
python tools/owledge.py doctor --project-root .
python tools/owledge.py test release-trust --project-root .
```

## Claude Code

Install shape:

```text
plugins/agent-memory-cowork/.claude-plugin/plugin.json
plugins/agent-memory-cowork/hooks/hooks.json
plugins/agent-memory-cowork/scripts/
```

Copy the full `plugins/agent-memory-cowork/` folder into the Claude-compatible
plugin directory used by your local runtime. Start Claude Code from the
initialized project root so the Python hooks can discover the local CLI.

Verify:

```bash
python tools/owledge.py test runtime-adapters --project-root .
python tools/agent_memory_cli.py --project-root . validate-memory --strict
```

## Cowork-Compatible

Use the same bundle as Claude Code. The default hook profile is Python-first:

```text
plugins/agent-memory-cowork/hooks/hooks.json
```

Hook errors are fail-soft and logged under:

```text
.agent-control/logs/plugin-errors.jsonl
```

Verify hook health:

```bash
python tools/owledge.py doctor --project-root .
python tools/owledge.py test runtime-adapters --project-root .
```

## OpenCode-Style

Use instruction-based integration:

1. Initialize the project with Owledge.
2. Give the agent the repo link and project root.
3. Ask it to follow `AGENTS.md` and use local Python commands.

Verify:

```bash
python tools/owledge.py doctor --project-root .
python tools/owledge.py build-context-pack --project-root . --task-id opencode-smoke
```

## Generic Agents

Use the repo-link flow when the runtime has no plugin system:

```text
Use Owledge from this repo and this project root.
Read AGENTS.md first.
Write only plans, evidence, reviews, and handoffs into Owledge-owned folders.
Do not rewrite existing knowledgebase files.
```

Verify:

```bash
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py test kb-module --project-root .
```

## Verify

For a release-quality local install, run:

```bash
python tools/owledge.py finalization-gates --project-root . --include-compliance
python tools/owledge.py benchmark --project-root .
```

For a plugin-only smoke test, run:

```bash
python tools/owledge.py test runtime-adapters --project-root .
```

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Hooks do not write session files | Run `python tools/owledge.py doctor --project-root .` and inspect `.agent-control/logs/plugin-errors.jsonl`. |
| Runtime starts outside the project root | Start from the initialized project root or copy `tools/agent_memory_cli.py` into the host project. |
| Session logs grow too large | Close/compact sessions and keep raw event files private. |
| Agent cannot find commands | Confirm the runtime loaded `plugins/agent-memory-cowork/commands/`. |

## Uninstall

Remove the copied plugin folder from the runtime plugin area. In the host
project, remove `plugins/agent-memory-cowork/` only if the project no longer
uses the local adapter.

Do not delete `agent-memory/` unless you intentionally want to remove project
memory. Raw private session logs can be cleaned separately after summaries have
been reviewed.

## Rule

Plugins and runtime skills are adapters. The project's local Markdown remains
the source of truth.
