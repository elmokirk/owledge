# Quickstart

Use this when you want Owledge inside a coding project and Markdown should stay
the source of truth.

> The [Installation Hub](install/README.md) is the canonical installation
> contract. It separates no-install, package, source-only add-on, footprint,
> recovery, upgrade, and removal paths. This page remains a project quickstart
> reference; do not combine its package and source commands in one chain.

## Path A: Add Owledge To An Existing Project

Use either the complete [package recipe](install/project.md#package-recipe) or
the complete [source recipe](install/project.md#source-recipe). They use
different delivery boundaries and must not be mixed. Both are additive: they do
not change the project's framework, package manager, build system, source tree,
or existing agent workflow.

## Optional: Add Runtime Hooks

Use the plugin adapter only when a local runtime should capture private hook
events. It is source-checkout only; follow [Plugin installation](install-plugin.md).

## Path B: Generate A Project-Local Starter Kit

Use this source-checkout-only option when you want a small local kit without
copying the full repo layout into the host project:

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
python tools/owledge_core.py --project-root . build-memory-index
python tools/owledge_core.py --project-root . render-memory-report --report-type project-dashboard --audience private
```

## What Gets Added

| Path | Purpose |
| --- | --- |
| `OWLEDGE.md` | Project-level durable context and agent entrypoint |
| `AGENTS.md` and `CLAUDE.md` | Runtime instructions |
| `.owledge/` | Plans, tasks, workpackages, evidence, reviews, handoffs, research, indexes, sessions |
| `skills/` | Owledge skill source/vendor bundle and generic-agent fallback |
| `.agents/skills/` | Project-local Codex skill discovery mirror |
| `tools/` | Local Python CLI |
| `plugins/owledge-cowork/` | Optional Python-hook runtime adapter |

## Rules

- Use local paths and local Python tools.
- Keep raw runtime sessions private.
- Export to RAG only from reviewed artifacts.
- Treat generated indexes as rebuildable views, not canonical memory.

For plugin setup, read [install-plugin.md](install-plugin.md). For a drop-in
knowledgebase install instead of a coding project, read
[agent-integration-guide.md](agent-integration-guide.md).

## P0 Checks

```bash
owledge wikilink-audit --project-root . --check
python tools/owledge.py install-addon --project-root . --addon benchmark-kit
python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode small --yes
python tools/benchmark-kit/render-benchmark-report.py --format html
```

Local Ollama benchmark mode is opt-in and sequential:

```bash
python tools/benchmark-kit/run-benchmark-kit.py --mode local --scale-mode small --models gemma4:latest --yes
```

## Optional Project Cockpit

Project Snapshot Kit is an optional add-on for reusable project snapshots and
static HTML pages. It is not installed by default.

```bash
python tools/owledge.py install-addon --project-root . --addon project-snapshot-kit
python tools/owledge.py project-snapshot --project-root .
```

The generation command asks before creating Markdown snapshots or HTML pages
unless `--snapshots-only`, `--render-html`, or `--yes` is passed.
