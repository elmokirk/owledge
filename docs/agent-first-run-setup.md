# Agent First-Run Setup

## Goal

Give an agent a repository and the Agent Memory Kit path. The agent initializes all required host-project files, verifies the install, and reports any manual runtime wiring that cannot be done safely from inside the repo.

## Inputs For The Agent

| Input | Required | Example |
| --- | --- | --- |
| Host project root | Yes | `C:\work\customer-app` |
| Kit root | Yes | `C:\AgentMemoryKit` |
| Force overwrite | No | Only when the owner explicitly asks |

Do not require a system-wide environment variable. Use the explicit `-KitRoot`
argument for one-off setup.

## Agent Procedure

1. Inspect the host project for:
   - `PROJECT_CONTEXT.md`
   - `USER_CONTEXT.md` when the private user layer is enabled
   - `AGENTS.md`
   - `CLAUDE.md`
   - `DESIGN.md`
   - `agent-memory/`
   - `global-memory/`
   - `tools/agent_memory_cli.py`
2. If anything is missing, run:

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\AgentMemoryKit\tools\bootstrap-agent-memory.ps1" -ProjectRoot "C:\work\customer-app" -KitRoot "C:\AgentMemoryKit"
```

macOS/Linux project-folder-only alternative:

```bash
python3 ~/AgentMemoryKit/tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

3. Verify the host project:

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\work\customer-app\tools\verify-host-install.ps1" -ProjectRoot "C:\work\customer-app"
```

macOS/Linux:

```bash
bash tools/verify-host-install.sh --project-root .
```

4. Build the first generated index:

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\work\customer-app\tools\build-memory-index.ps1" -ProjectRoot "C:\work\customer-app"
```

macOS/Linux:

```bash
bash tools/build-memory-index.sh --project-root .
```

5. Report:
   - files created
   - files already present
   - verification score
   - placeholders the user must fill in, especially `PROJECT_CONTEXT.md` and optionally private `USER_CONTEXT.md`
   - manual runtime steps below

## Manual Runtime Steps To Report

Some operations are outside the project repository and should be shown to the user instead of hidden:

| Runtime | Manual Step |
| --- | --- |
| Codex | Install or copy the `skills/` folder into the configured Codex skills directory when global skills are desired. |
| Claude/Cowork | Install or copy `plugins/agent-memory-cowork/` into the runtime's plugin folder if the runtime does not have a plugin installer. |
| Claude/Cowork hooks | Launch from the initialized project root when possible. Use `hooks.unix.json` on macOS/Linux. |
| Shared machine | Keep tenant/customer/project IDs filled in before exports or customer reports. |
| Personal/global layer | Keep `USER_CONTEXT.md` and `global-memory/**/*.md` private unless the user explicitly creates a private global vault. |

For a bootstrapped project, the plugin should use local `tools/agent_memory_cli.py`.

## Smoke Test Prompt

After setup, ask an agent:

```text
Run memory-doctor for this project, build the memory index, then summarize which memory files should be filled in before the next coding task.
```

The expected result is a passing doctor/validation run and a concrete list of missing project-specific content, not automatic promotion of placeholders.
