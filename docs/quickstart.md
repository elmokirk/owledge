# Quickstart

Use this when you want Owledge inside a coding project and Markdown should stay
the source of truth.

## Path A: Add Owledge To An Existing Project

From your local Owledge clone:

```bash
python tools/owledge.py init-project --target /path/to/your-project --include-plugin-adapter
```

Then verify inside the host project:

```bash
python tools/owledge.py doctor --project-root .
python tools/agent_memory_cli.py --project-root . validate-memory --strict
```

## Path B: Generate A Project-Local Starter Kit

Use this when you want a small local kit without copying the full repo layout
into the host project:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --verify
```

With the Claude/Cowork-compatible plugin adapter:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --include-plugin-adapter --verify
```

## First Useful Commands

```bash
python tools/agent_memory_cli.py --project-root . build-memory-index
python tools/agent_memory_cli.py --project-root . render-memory-report --report-type project-dashboard --audience private
```

## What Gets Added

| Path | Purpose |
| --- | --- |
| `PROJECT_CONTEXT.md` | Project-level durable context |
| `AGENTS.md` and `CLAUDE.md` | Runtime instructions |
| `agent-memory/` | Plans, evidence, reviews, handoffs, indexes, sessions |
| `tools/` | Local Python CLI |
| `plugins/agent-memory-cowork/` | Optional runtime adapter |

## Rules

- Use local paths and local Python tools.
- Keep raw runtime sessions private.
- Export to RAG only from reviewed artifacts.
- Treat generated indexes as rebuildable views, not canonical memory.

For plugin setup, read [install-plugin.md](install-plugin.md). For a drop-in
knowledgebase install instead of a coding project, read
[agent-integration-guide.md](agent-integration-guide.md).
