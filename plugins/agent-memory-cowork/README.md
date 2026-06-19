# Owledge Cowork Adapter

Host-project adapter for Owledge's Markdown-first agent memory layer.

## Purpose

This plugin can be installed by a compatible runtime, but it writes to the
active host project. It is not a second memory store.

```text
Runtime plugin = skills, commands, hooks
Host project = PROJECT_CONTEXT.md, DESIGN.md, agent-memory/
Reviewed exports = optional consumers such as RAG or reports
```

Use the principles-only path when a runtime can follow instructions without a
plugin. This adapter is for local hooks and commands around the same Markdown
contract.

## Requirements

- Python 3 available to the runtime command environment.
- A host project initialized with `PROJECT_CONTEXT.md` and `agent-memory/`.
- Local `tools/agent_memory_cli.py` in the host project or an Owledge repo
  checkout.

## Install

Install this folder through the runtime's local plugin mechanism, or copy the
full `plugins/agent-memory-cowork/` folder into the plugin directory that the
runtime reads from.

Runtime-specific install and uninstall steps are documented in
[`docs/install-plugin.md`](../../docs/install-plugin.md).

## Configuration

The normal path is project-local:

1. Start the runtime from the initialized project root.
2. Keep `PROJECT_CONTEXT.md`, `agent-memory/`, and `tools/agent_memory_cli.py`
   in that project.
3. Let the hooks discover the project root by walking upward from the current
   directory.

## Capture Policy

- Raw hook events are private working memory.
- Capture defaults to redacted `standard` mode.
- Hook errors are logged to `.agent-control/logs/plugin-errors.jsonl` and do
  not break runtime sessions.
- Runtime session artifacts are private and ignored by default:
  `events.jsonl`, `session.md`, and `summary.md`.
- Shared exports require approved review and sanitization.

## Install Shape

```text
plugins/agent-memory-cowork/
|-- .claude-plugin/plugin.json
|-- .codex-plugin/plugin.json
|-- commands/
|-- agents/
|-- skills/
|-- hooks/hooks.json
|-- hooks/hooks.python.json
|-- scripts/
|   |-- capture-claude-event.py
|   `-- close-runtime-session.py
|-- tests/fixtures/
|-- LICENSE
|-- VERSION
`-- CHANGELOG.md
```

Use `agent-memory-principles` as the primary entrypoint when an agent should
connect to an existing Markdown knowledgebase, Obsidian vault, or LLM wiki
without forcing the preset folder structure. It supports a principles-first
workflow with an optional local `agent-memory-map.json`.

## Local Starter

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --include-plugin-adapter --verify
```

## Commands

| Command | Writes? | Use |
| --- | --- | --- |
| `memory-init` | Yes | Initialize a host project without overwriting existing memory. |
| `memory-status` | No | Read-only project status. |
| `memory-doctor` | No | Read-only install, privacy, schema, and adapter diagnosis. |
| `memory-report` | Yes | Generate local HTML report views. Markdown remains canonical. |

`memory-report` can also route to optional Project Snapshot Kit report types
after `project-snapshot-kit` is installed in the host project.

## Manual Smoke Test

Use a temporary copy or a private test project.

```bash
python plugins/agent-memory-cowork/scripts/capture-claude-event.py < plugins/agent-memory-cowork/tests/fixtures/session-start.json
python plugins/agent-memory-cowork/scripts/close-runtime-session.py < plugins/agent-memory-cowork/tests/fixtures/stop.json
python tools/owledge.py doctor --project-root .
```

For a normal verification path, prefer:

```bash
python tools/owledge.py test runtime-adapters --project-root .
python tools/owledge.py test release-trust --project-root .
```
