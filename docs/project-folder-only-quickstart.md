# Project Folder Only Quickstart

Use this path when you want a minimal project-local Owledge install without
copying the full repository.

## 1. Generate The Folder

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --verify
```

Include the Claude/Cowork-compatible plugin adapter:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --include-plugin-adapter --verify
```

Use `--force` only for disposable folders under a temporary workspace. The
generator refuses unsafe replacement outside known temp roots.

## 2. Move Or Copy Into A Project

The generated folder contains:

- `PROJECT_CONTEXT.md`, `AGENTS.md`, `CLAUDE.md`, `DESIGN.md`, `.gitignore`
- `agent-memory/` schemas, templates, empty memory folders, and `.gitkeep` files
- `global-memory/` empty private user-memory folders
- core Python tools
- selected skills
- a short local `README.md`

It deliberately excludes tests, PI sample reports, generated indexes, generated
exports, and raw runtime events.

Optional Compliance Light support can be included explicitly:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit-compliance --include-compliance --verify
```

## 3. Verify And Build The Index

From inside the generated or copied project folder:

```bash
python tools/owledge.py doctor --project-root .
python tools/agent_memory_cli.py --project-root . validate-memory --strict
python tools/agent_memory_cli.py --project-root . build-memory-index
```

Agents can then build scoped context packs:

```bash
python tools/owledge.py build-context-pack --project-root . --task-id "TASK-ID" --agent-role worker
```

Markdown frontmatter remains canonical; indexes and exports are rebuildable
views.
