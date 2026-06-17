# Plugin Install

Use this when you want Owledge attached to a runtime rather than only as local
files.

## Primary Plugin Bundle

The current plugin bundle is:

```text
plugins/agent-memory-cowork/
```

It contains Claude/Cowork-compatible hooks, Codex-compatible skill metadata,
commands, skills, and a memory-curator agent.

## Install Shape

### Claude Code / Cowork-compatible

Use the runtime's plugin install flow when available. If the runtime expects a
manual plugin folder, copy the full `plugins/agent-memory-cowork/` directory
into that runtime's plugin area.

Start the runtime from the initialized project root when possible. The Python
hooks discover:

- `PROJECT_CONTEXT.md`
- `agent-memory/`
- `tools/agent_memory_cli.py`

### Codex

Use the `.codex-plugin` manifest in the same plugin bundle or install the
skills and local Python CLI alongside the project.

### OpenCode-style agents

Use the repo link and project-local instructions in `AGENTS.md`; no marketplace
dependency is required.

## Local Starter With Plugin

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --include-plugin-adapter --verify
```

## Smoke Test

Inside the initialized host project:

```bash
python tools/owledge.py doctor --project-root .
python tools/owledge.py test runtime-adapters --project-root .
```

## Rule

Plugins and runtime skills are adapters. The project's local Markdown remains
the source of truth.
