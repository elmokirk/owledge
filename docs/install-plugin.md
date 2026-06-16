# Plugin Install

Use this when you want Owledge attached to a runtime rather than only as local files.

## Primary Plugin Bundle

The current plugin bundle is:

```text
plugins/agent-memory-cowork/
```

It contains:

- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `commands/`
- `hooks/`
- `skills/`
- `agents/`

## Install Shape

### Claude Code / Cowork-compatible

Use the runtime's plugin install flow when available. If the runtime expects a manual plugin folder, copy the full `plugins/agent-memory-cowork/` directory into that runtime's plugin area.

Start the runtime from the initialized project root when possible. That lets the hooks discover:

- `PROJECT_CONTEXT.md`
- `agent-memory/`
- `tools/agent_memory_cli.py`

without any OS-wide setup.

### Codex

Use the `.codex-plugin` manifest in the same plugin bundle or install the skills and local CLI alongside the project.

### OpenCode-style agents

Use the repo link and project-local instructions in `AGENTS.md`; no marketplace dependency is required.

## Unix Hook Profile

On macOS/Linux, use the Unix hook profile:

```bash
cp plugins/agent-memory-cowork/hooks/hooks.unix.json plugins/agent-memory-cowork/hooks/hooks.json
```

Or generate a local starter with:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --include-plugin-adapter --plugin-hook-profile unix --verify
```

## Smoke Test

Inside the initialized host project:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\memory-doctor.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-host-install.ps1 -ProjectRoot .
```

## Rule

Plugins and runtime skills are adapters. The project's local Markdown remains the source of truth.
