# Project Folder Only Quickstart

Use this path when you want a minimal project-local Agent Memory install without
plugins, release reports, PI examples, or test workspaces.

## 1. Generate The Folder

### Windows

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build-project-folder-kit.ps1 -OutputPath C:\tmp\agent-memory-project-kit -Verify
```

Use `-Force` only for disposable folders under `C:\tmp` or the project's
`.agent-control\tmp`. The generator refuses to replace existing folders outside
those safe roots.

### macOS And Linux

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

Include the Claude/Cowork plugin adapter with Unix hooks:

```bash
python3 tools/build_project_folder_kit.py \
  --output-path /tmp/agent-memory-project-kit \
  --include-plugin-adapter \
  --plugin-hook-profile unix \
  --verify
```

## 2. Move Or Copy Into A Project

The generated folder contains only the project-local surface:

- `PROJECT_CONTEXT.md`, `AGENTS.md`, `CLAUDE.md`, `DESIGN.md`, `.gitignore`
- `agent-memory/` schemas, templates, empty memory folders, and `.gitkeep` files
- `global-memory/` empty private user-memory folders
- core `tools/`
- selected `skills/`
- a short local `README.md`

It deliberately excludes plugins, tests, PI sample reports, generated indexes,
generated exports, raw runtime events, release notes, compliance add-ons, and
repository-level docs.

Optional Compliance Light support can be included explicitly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build-project-folder-kit.ps1 -OutputPath C:\tmp\agent-memory-project-kit-compliance -Verify -IncludeCompliance
```

This adds local compliance-support templates and read-only checks only. It does
not provide legal advice, certification, RBAC, encryption, or enterprise
compliance automation.

## 3. Verify And Build The Index

From inside the generated or copied project folder:

### Windows

```powershell
tools\verify-host-install.ps1 -ProjectRoot .
tools\build-memory-index.ps1 -ProjectRoot .
```

### macOS And Linux

```bash
bash tools/verify-host-install.sh --project-root .
bash tools/build-memory-index.sh --project-root .
```

Equivalent direct Python commands:

```bash
python3 tools/agent_memory_cli.py --project-root . doctor --mode host
python3 tools/agent_memory_cli.py --project-root . validate-memory --strict
python3 tools/agent_memory_cli.py --project-root . build-memory-index
```

After that, agents can use `tools\build-context-pack.ps1 -ProjectRoot .` and the
Markdown memory folders directly. Markdown frontmatter remains canonical;
indexes and exports are rebuildable views.

On macOS/Linux agents should use:

```bash
python3 tools/agent_memory_cli.py --project-root . build-context-pack --task-id "TASK-ID" --agent-role worker
```

No global `AGENT_MEMORY_KIT_ROOT` variable is required after generation because
the project folder contains its own CLI.
