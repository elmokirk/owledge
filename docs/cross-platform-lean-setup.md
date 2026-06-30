# Cross-Platform Lean Setup

Use this path when the goal is a small, project-local Owledge install. The
generated project folder contains its own Python CLI, local memory folders, and
selected skills.

## Current Answer

Yes, there is a minimal configuration: Project Folder Only. It includes the
project files, `.owledge/`, selected `skills/`, and local Python tools. It
is not skills-only, because agents need durable files plus a local CLI to
verify, index, and build context packs.

## Humans

Generate the lean folder:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --verify
```

Include the Claude/Cowork-compatible plugin adapter:

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit --include-plugin-adapter --verify
```

From inside the generated project:

```bash
python tools/owledge.py doctor --project-root .
python tools/owledge_core.py --project-root . validate-memory --strict
python tools/owledge_core.py --project-root . build-memory-index
```

## Agents

Agents should treat the generated folder as self-contained:

1. Read `OWLEDGE.md`.
2. Follow `AGENTS.md` and `CLAUDE.md`.
3. Build a scoped context pack before non-trivial work:

```bash
python tools/owledge.py build-context-pack --project-root . --task-id "TASK-ID" --agent-role worker --objective "Short objective"
```

4. Write durable facts, decisions, patterns, and lessons to `.owledge/`.
5. Rebuild indexes after edits.
6. Keep raw sessions private. Shared exports require reviewed and sanitized
   records.

## Harness Fit

| Runtime | Fit | Best Use |
| --- | --- | --- |
| Claude/Cowork | High | Plugin hooks plus local Markdown memory |
| Codex/CLI agents | High | Direct Python CLI commands |
| Hermes-style agents | Good | Durable project memory beside bounded runtime memory |
| OpenCode-style agents | Good | Workspace-local memory and project leadership checks |

Remaining gap: Hermes/OpenCode-style runtimes do not yet have native plugin
manifests in this repo. They should use the generic agent workflow until a
dedicated adapter is added.
