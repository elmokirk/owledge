# Quickstart

Use this when you want Owledge inside a coding project and Markdown should stay
the source of truth.

## Path A: Add Owledge To An Existing Project

From your local Owledge clone:

```bash
python tools/owledge.py init-project --target /path/to/your-project
```

This is additive. It does not change the project's framework, package manager,
build system, source tree, or existing agent workflow.

Then verify inside the host project:

```bash
python tools/owledge.py doctor --project-root .
python tools/agent_memory_cli.py --project-root . validate-memory --strict
```

## Optional: Add Runtime Hooks

Use the plugin adapter only when a local runtime should capture private hook
events:

```bash
python tools/owledge.py init-project --target /path/to/your-project --include-plugin-adapter
```

## Path B: Generate A Project-Local Starter Kit

Use this when you want a small local kit without copying the full repo layout
into the host project:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --verify
```

With the Claude/Cowork-compatible plugin adapter when hooks are needed:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --include-plugin-adapter --verify
```

## Path C: Principles-Only

Use this when an existing coding agent or agent platform only needs Owledge's
memory discipline:

```text
Use Owledge principles only. Keep existing files unchanged. Treat Markdown as
canonical memory, write evidence-linked plans and handoffs, use typed
frontmatter edges, keep raw sessions private, and promote only reviewed memory.
```

No plugin, generated kit, wrapper script, or OS-specific setting is required for
this mode.

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
| `plugins/agent-memory-cowork/` | Optional Python-hook runtime adapter |

## Rules

- Use local paths and local Python tools.
- Keep raw runtime sessions private.
- Export to RAG only from reviewed artifacts.
- Treat generated indexes as rebuildable views, not canonical memory.

For plugin setup, read [install-plugin.md](install-plugin.md). For a drop-in
knowledgebase install instead of a coding project, read
[agent-integration-guide.md](agent-integration-guide.md).

## Optional Project Cockpit

Project Snapshot Kit is an optional add-on for reusable project snapshots and
static HTML pages. It is not installed by default.

```bash
python tools/owledge.py install-addon --project-root . --addon project-snapshot-kit
python tools/owledge.py project-snapshot --project-root .
```

The generation command asks before creating Markdown snapshots or HTML pages
unless `--snapshots-only`, `--render-html`, or `--yes` is passed.
