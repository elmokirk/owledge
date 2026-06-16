# Cross-Platform Lean Setup

Use this path when the goal is a small, project-local Agent Memory install that
works without global environment variables. The generated project folder
contains its own `tools/agent_memory_cli.py`, local memory folders, and selected
skills.

## Current Answer

Yes, there is already a minimal configuration: Project Folder Only. It includes
the project files, `agent-memory/`, selected `skills/`, and local tools. It is
not skills-only, because agents need the local CLI and memory skeleton to verify,
index, and build context packs without a separate global kit.

For Hermes Agent and OpenClaw-style project leaders, this is a good fit when
they operate inside a project workspace and can run local commands. Use their
built-in memory for short status pointers and use this kit as durable project
truth. It is less optimal when the agent expects a native provider plugin or
hosted memory server, because this kit is intentionally file-first.

## Humans

### Windows

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build-project-folder-kit.ps1 -OutputPath C:\tmp\agent-memory-project-kit -Verify
```

Include the Claude/Cowork plugin adapter:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build-project-folder-kit.ps1 -OutputPath C:\tmp\agent-memory-project-kit -Verify -IncludePluginAdapter
```

### macOS And Linux

Generate the same lean folder with Python:

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

From inside the generated project:

```bash
bash tools/verify-host-install.sh --project-root .
bash tools/build-memory-index.sh --project-root .
```

Equivalent direct CLI commands:

```bash
python3 tools/agent_memory_cli.py --project-root . doctor --mode host
python3 tools/agent_memory_cli.py --project-root . validate-memory --strict
python3 tools/agent_memory_cli.py --project-root . build-memory-index
```

No global kit setting is required after generation. The generated project folder
contains its own CLI and wrappers.

## Agents

Agents should treat the generated folder as self-contained:

1. Read `PROJECT_CONTEXT.md`.
2. Follow `AGENTS.md` and `CLAUDE.md`.
3. Build a scoped context pack before non-trivial work:

```bash
python3 tools/agent_memory_cli.py \
  --project-root . \
  build-context-pack \
  --task-id "TASK-ID" \
  --agent-role worker \
  --objective "Short objective"
```

4. Write durable facts, decisions, patterns, and lessons to `agent-memory/`.
5. Rebuild indexes after edits:

```bash
bash tools/build-memory-index.sh --project-root .
```

6. Keep raw sessions private. Shared exports require reviewed and sanitized
records.

## Claude/Cowork On macOS And Linux

The plugin includes a Unix hook profile:

- Windows default: `plugins/agent-memory-cowork/hooks/hooks.json`
- Unix profile: `plugins/agent-memory-cowork/hooks/hooks.unix.json`

The Python project-folder generator automatically copies `hooks.unix.json` over
`hooks.json` when `--include-plugin-adapter --plugin-hook-profile unix` is used.
The Unix hooks call small shell launchers that use the project-local CLI.

Claude/Cowork sessions should be launched from the project root when possible.
If the runtime starts elsewhere, configure the project root in the harness or
hook profile rather than relying on OS-wide settings.

## Hermes Agent And OpenClaw Fit

Hermes Agent has bounded built-in memory and external provider support. Use that
for short status and routing pointers, then point back to this project-local
folder for canonical project decisions, context packs, retrieval exports, and
QA gates.

OpenClaw resolves agent workspaces and supports project-scoped persistence. This
matches the kit's model well: place the generated folder in the OpenClaw
workspace and let agents read/write Markdown plus run the local Python CLI.

Practical fit:

| Runtime | Fit | Best Use |
| --- | --- | --- |
| Claude/Cowork | High | Plugin hooks plus local Markdown memory |
| Codex/CLI agents | High | Direct `python3 tools/agent_memory_cli.py` commands |
| Hermes Agent | Good | Durable project memory beside Hermes bounded memory |
| OpenClaw | Good | Workspace-local memory and project leadership checks |

Remaining gap: Hermes/OpenClaw do not yet have native plugin manifests in this
repo. They should use the generic agent workflow until a dedicated adapter is
added.
