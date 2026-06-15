# Plugin And Global Skill Install

## Goal

Use the kit globally while every project keeps its own Markdown memory.

For a quick status view across Codex, Claude Code, Claude/Cowork-compatible
runtimes, generic agents, Superpowers users, and Markdown/Obsidian KBs, see
`docs/harness-plugin-matrix.md`.

## Mental Model

| Layer | Location | Writes |
| --- | --- | --- |
| Kit | explicit `-KitRoot` or `AGENT_MEMORY_KIT_ROOT` fallback | Templates, tools, plugins, skills |
| Host project | active repo | `PROJECT_CONTEXT.md`, `agent-memory/`, reports, exports |
| Claude skills | `%USERPROFILE%\.claude\skills` | Skill instructions only |
| Codex skills | `%USERPROFILE%\.codex\skills` | Skill instructions only |

## Setup Paths

The kit supports two setup modes.

### Explicit Path, No Global Variable

Use this for one-off setup, CI checks, customer machines, or agent-driven bootstraps:

```powershell
$kitRoot = "C:\AgentMemoryKit"
powershell -NoProfile -ExecutionPolicy Bypass -File "$kitRoot\tools\bootstrap-agent-memory.ps1" -ProjectRoot "C:\path\to\your-project" -KitRoot $kitRoot
```

macOS/Linux project-folder-only equivalent:

```bash
python3 ~/AgentMemoryKit/tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

### Optional Convenience Environment

```powershell
[Environment]::SetEnvironmentVariable("AGENT_MEMORY_KIT_ROOT", "C:\AgentMemoryKit", "User")
$env:AGENT_MEMORY_KIT_ROOT = "C:\AgentMemoryKit"
```

Optional Python override:

```powershell
[Environment]::SetEnvironmentVariable("AGENT_MEMORY_PYTHON", "python", "User")
```

## Copy Skills Globally

Codex:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse -Force "$env:AGENT_MEMORY_KIT_ROOT\skills\*" "$env:USERPROFILE\.codex\skills\"
```

Claude:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "$env:AGENT_MEMORY_KIT_ROOT\skills\*" "$env:USERPROFILE\.claude\skills\"
```

## Use The Cowork Plugin Bundle

The plugin bundle lives at:

```text
plugins/agent-memory-cowork/
```

Use the runtime's plugin installer if available. If the runtime only supports manual plugin folders, copy the whole directory and keep the host project explicit:

```powershell
$env:AGENT_MEMORY_PROJECT_ROOT = "C:\path\to\your-project"
$env:AGENT_MEMORY_CAPTURE_MODE = "standard"
```

Set `AGENT_MEMORY_KIT_ROOT` only when the plugin must resolve tools from the global kit instead of the bootstrapped host project.

On macOS/Linux, use the Unix hook profile before installing or generate the
project folder with `--include-plugin-adapter --plugin-hook-profile unix`:

```bash
cp plugins/agent-memory-cowork/hooks/hooks.unix.json plugins/agent-memory-cowork/hooks/hooks.json
```

If Claude/Cowork starts from the initialized project root, the plugin hooks can
discover the root without `AGENT_MEMORY_PROJECT_ROOT`.

## Smoke Test In A Host Project

```powershell
cd C:\path\to\your-project
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\memory-doctor.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-host-install.ps1 -ProjectRoot .
```

macOS/Linux:

```bash
cd /path/to/your-project
bash tools/memory-doctor.sh --project-root .
bash tools/verify-host-install.sh --project-root .
```

## Available Skills

| Skill | Use |
| --- | --- |
| `bootstrap-agent-memory` | Initialize missing host-project memory |
| `agent-memory-principles` | Apply Agent Memory principles to existing Markdown KBs without forcing the preset folder structure |
| `agent-memory-runtime-bridge` | Tell agents how to read/write memory safely |
| `render-memory-report` | Create HTML reports from Markdown truth |
| `pi-agent-workspace-quality` | Workspace and planning quality checks |
| `pi-agent-global-intelligence` | Parallels, trends, recurring errors, central ideas |
| `pi-agent-red-team-evaluator` | 1-100 scorecards for PI reports and agent outputs |

## Rule

Global skills and plugins are adapters. The host project's Markdown remains the source of truth.
