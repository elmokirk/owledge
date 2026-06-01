# Agent Memory Cowork Adapter

Host-project adapter for the Markdown-first Agent Memory Kit.

## Purpose

This plugin is globally installable, but it writes to the active host project. It is not a second memory store.

```text
Global plugin = skills, commands, Claude/Cowork hooks
Host project = PROJECT_CONTEXT.md, DESIGN.md, agent-memory/
Enterprise hub = later aggregation of reviewed/promoted knowledge
RAG/LightRAG = consumers of reviewed exports
```

## Requirements

- PowerShell on Windows.
- Python available as `python` on Windows or `python3` on macOS/Linux. `AGENT_MEMORY_PYTHON` is only an optional override.
- A host project initialized with `agent-memory/` and `PROJECT_CONTEXT.md`.
- Either local `tools/agent_memory_cli.py` in the host project or `AGENT_MEMORY_KIT_ROOT` pointing to the Agent Memory Kit root.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `AGENT_MEMORY_PROJECT_ROOT` | Explicit host project root. Recommended for Claude/Cowork sessions. |
| `AGENT_MEMORY_KIT_ROOT` | Fallback root that contains `tools/agent_memory_cli.py`. |
| `AGENT_MEMORY_PYTHON` | Optional Python executable override. |
| `AGENT_MEMORY_CAPTURE_MODE` | `minimal`, `standard`, or `full-private`. Default: `standard`. |
| `AGENT_MEMORY_STRICT_HOOKS` | Set `1` only when hook failures should fail the runtime. Default hooks are fail-soft. |

## Capture Policy

- Raw hook events are private working memory.
- Capture defaults to redacted `standard` mode.
- Hook errors are logged to `.agent-control/logs/plugin-errors.jsonl` and do not break Claude sessions.
- Runtime session artifacts are expected to be private and gitignored by default: `events.jsonl`, `session.md`, and `summary.md`.
- Runtime summaries remain private session artifacts until curated.
- Shared exports require approved review and sanitization.

## Install Shape

```text
plugins/agent-memory-cowork/
|-- .claude-plugin/plugin.json
|-- .codex-plugin/plugin.json
|-- commands/
|   |-- memory-init.md
|   |-- memory-status.md
|   |-- memory-doctor.md
|   `-- memory-report.md
|-- agents/
|   `-- memory-curator.md
|-- skills/
|   |-- agent-memory-runtime-bridge/
|   `-- render-memory-report/
|-- hooks/hooks.json
|-- hooks/hooks.unix.json
|-- scripts/
|   |-- capture-claude-event.ps1
|   |-- close-runtime-session.ps1
|   |-- capture-claude-event.py
|   |-- close-runtime-session.py
|   |-- capture-claude-event.sh
|   `-- close-runtime-session.sh
|-- tests/fixtures/
|-- LICENSE
|-- VERSION
`-- CHANGELOG.md
```

Claude/Cowork uses hooks. Codex uses the skills and commands; Claude hook wiring is intentionally not advertised through the Codex manifest.

## macOS And Linux

The default `hooks/hooks.json` is Windows PowerShell-first. For macOS/Linux,
use the Unix hook profile:

```bash
cp plugins/agent-memory-cowork/hooks/hooks.unix.json plugins/agent-memory-cowork/hooks/hooks.json
```

The cross-platform project-folder generator does this automatically:

```bash
python3 tools/build_project_folder_kit.py \
  --output-path /tmp/agent-memory-project-kit \
  --include-plugin-adapter \
  --plugin-hook-profile unix \
  --verify
```

The Unix hooks use shell launchers that try `AGENT_MEMORY_PYTHON`, then
`python3`, then `python`. When Claude/Cowork runs from the initialized project
root, no `AGENT_MEMORY_PROJECT_ROOT` or `AGENT_MEMORY_KIT_ROOT` variable is
required because the hook finds `PROJECT_CONTEXT.md`, `agent-memory/`, and the
local CLI by walking upward from the current directory.

## Commands

| Command | Writes? | Use |
| --- | --- | --- |
| `memory-init` | Yes | Initialize a host project without overwriting existing memory. |
| `memory-status` | No | Read-only project status. |
| `memory-doctor` | No | Read-only install, privacy, schema, and adapter diagnosis. |
| `memory-report` | Yes | Generate local HTML report views. Markdown remains canonical. |

For enterprise hubs, pass tenant/customer/project scope to exports and reports whenever the project root aggregates multiple customers.

## Manual Smoke Test

Use a temporary copy or a private test project.

```powershell
$env:AGENT_MEMORY_PROJECT_ROOT = (Get-Location).Path
$env:AGENT_MEMORY_KIT_ROOT = (Get-Location).Path

Get-Content plugins\agent-memory-cowork\tests\fixtures\session-start.json -Raw |
  powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File plugins\agent-memory-cowork\scripts\capture-claude-event.ps1

Get-Content plugins\agent-memory-cowork\tests\fixtures\stop.json -Raw |
  powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File plugins\agent-memory-cowork\scripts\close-runtime-session.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File tools\memory-doctor.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File tools\verify-host-install.ps1 -ProjectRoot .
```
