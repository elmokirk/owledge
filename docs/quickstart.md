# Quickstart

Use this when you want Owledge inside a coding project and Markdown should stay the source of truth.

## Path A: Bootstrap An Existing Project

From your local Owledge clone:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\bootstrap-agent-memory.ps1 -ProjectRoot C:\path\to\your-project -KitRoot .
```

Then verify inside the host project:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-host-install.ps1 -ProjectRoot .
```

## Path B: Generate A Project-Local Starter Kit

Use this when you want a small local kit without copying the full repo layout into the host project:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build-project-folder-kit.ps1 -OutputPath C:\tmp\agent-memory-project-kit -Verify
```

macOS/Linux:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

Plugin adapter on Unix:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --include-plugin-adapter --plugin-hook-profile unix --verify
```

## First Useful Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build-memory-index.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\render-memory-report.ps1 -ProjectRoot . -ReportType project-dashboard -Audience private
```

## What Gets Added

| Path | Purpose |
| --- | --- |
| `PROJECT_CONTEXT.md` | Project-level durable context |
| `AGENTS.md` and `CLAUDE.md` | Runtime instructions |
| `agent-memory/` | Plans, evidence, reviews, handoffs, indexes, sessions |
| `tools/` | Local CLI and wrappers |
| `plugins/agent-memory-cowork/` | Optional runtime adapter |

## Rules

- Use local paths and local tools.
- Do not treat environment variables as the normal setup path.
- Keep raw runtime sessions private.
- Export to RAG only from reviewed artifacts.

For plugin setup, read [install-plugin.md](install-plugin.md). For a drop-in knowledgebase install instead of a coding project, read [agent-integration-guide.md](agent-integration-guide.md).
