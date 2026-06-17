# Agent First-Run Setup

## Goal

Give an agent the Owledge repository link and the target project path. The
agent initializes required host-project files, verifies the install, and reports
any manual runtime wiring that cannot be done safely from inside the repo.

## Inputs For The Agent

| Input | Required | Example |
| --- | --- | --- |
| Host project root | Yes | `/work/customer-app` |
| Owledge repo checkout | Yes | `/work/owledge` |
| Force overwrite | No | Only when the owner explicitly asks |

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
2. If anything is missing, run from the Owledge checkout:

```bash
python tools/owledge.py init-project --target /work/customer-app --include-plugin-adapter
```

3. Verify the host project:

```bash
python tools/owledge.py doctor --project-root /work/customer-app
python tools/agent_memory_cli.py --project-root /work/customer-app validate-memory --strict
```

4. Build the first generated index:

```bash
python tools/agent_memory_cli.py --project-root /work/customer-app build-memory-index
```

5. Report:
   - files created
   - files already present
   - verification score
   - placeholders the user must fill in, especially `PROJECT_CONTEXT.md`
   - manual runtime steps below

## Manual Runtime Steps To Report

| Runtime | Manual Step |
| --- | --- |
| Codex | Install or copy the `skills/` folder into the configured Codex skills directory when global skills are desired. |
| Claude/Cowork | Install or copy `plugins/agent-memory-cowork/` into the runtime's plugin folder if the runtime does not have a plugin installer. |
| Claude/Cowork hooks | Launch from the initialized project root when possible. |
| Shared machine | Keep tenant/customer/project IDs filled in before exports or customer reports. |
| Personal/global layer | Keep `USER_CONTEXT.md` and `global-memory/**/*.md` private unless the user explicitly creates a private global vault. |

For an initialized project, the plugin should use local
`tools/agent_memory_cli.py`.

## Smoke Test Prompt

After setup, ask an agent:

```text
Run memory doctor for this project, build the memory index, then summarize which memory files should be filled in before the next coding task.
```

The expected result is a passing doctor/validation run and a concrete list of
missing project-specific content, not automatic promotion of placeholders.
