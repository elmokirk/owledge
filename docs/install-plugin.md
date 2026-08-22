# Plugin Install

Use this when you want Owledge attached to an agent runtime instead of only
using the local file/folder kit.

Plugins are optional adapters. If the runtime can follow project instructions,
the principles-only path in [agent-integration-guide.md](agent-integration-guide.md)
is enough.

The canonical plugin bundle is:

```text
plugins/owledge-cowork/
```

The plugin is a local adapter. It does not replace the runtime, and it does not
make Markdown memory global or hosted.

## Prerequisites

Initialize the host project first:

```bash
python tools/owledge.py init-project --target /path/to/project
python tools/owledge.py init-project --target /path/to/project --include-plugin-adapter
```

The first command is the standard project setup. The second command is the
optional adapter step when the runtime should load local Python hooks.

Then run all runtime commands from the initialized project root when possible.
The hooks discover:

- `OWLEDGE.md`
- `.owledge/`
- `tools/owledge_core.py`

Standard initialization also materializes project-local Codex skills under
`.agents/skills/`. The project-root `skills/` tree remains the Owledge
source/vendor bundle. `.owledge/skills/` is not an automatic discovery path.

When a shared skill reference is present in the canonical `skills/` tree, the
legacy plugin, and `standalone-skills/`, those copies are distribution mirrors
and must remain synchronized. The project-local Markdown and canonical skill
contract remain authoritative; synchronizing a mirror does not widen plugin
permissions or change its V1 maturity classification.

## Codex

Install shape:

```text
plugins/owledge-cowork/.codex-plugin/plugin.json
plugins/owledge-cowork/skills/
plugins/owledge-cowork/commands/
```

Use the Codex plugin flow when available. For manual setup, copy the full
`plugins/owledge-cowork/` directory into the plugin area that your Codex
runtime reads from, then start Codex from the initialized project root.

Without the plugin, Codex can still discover the initialized project skills
from `.agents/skills/`. Do not copy project skills into a user-global directory
unless the user explicitly wants cross-project installation.

Verify:

```bash
python tools/owledge.py doctor --project-root .
python tools/owledge.py test release-trust --project-root .
```

## Claude Code

Install shape:

```text
plugins/owledge-cowork/.claude-plugin/plugin.json
plugins/owledge-cowork/hooks/hooks.json
plugins/owledge-cowork/scripts/
```

For the project-local path, initialize with the adapter:

```bash
python tools/owledge.py init-project --target . --include-plugin-adapter
```

This writes `plugins/owledge-cowork/` and a non-overwriting
`.claude/settings.json` allow-list in the host project. Install that local
plugin folder through Claude Code so `${CLAUDE_PLUGIN_ROOT}` resolves inside
the project, then start Claude Code from the project root. `SessionStart`
emits a compact capsule from only `OWLEDGE.md` and
`.owledge/indexes/memory-index.jsonl`; it does not load project registers.

Hooks require project-local `tools/owledge_core.py`. If the local tool is
absent they fail soft with an `init-project` doctor hint. A global kit is used
only when `OWLEDGE_ALLOW_GLOBAL_KIT=1` is explicitly set.

Verify:

```bash
python tools/owledge.py test runtime-adapters --project-root .
python tools/owledge_core.py --project-root . validate-memory --strict
```

## Cowork-Compatible

Use the same bundle as Claude Code. The default hook profile is Python-first:

```text
plugins/owledge-cowork/hooks/hooks.json
```

Hook errors are fail-soft and logged under:

```text
.agent-control/logs/plugin-errors.jsonl
```

Verify hook health:

```bash
python tools/owledge.py doctor --project-root .
python tools/owledge.py test runtime-adapters --project-root .
```

## OpenCode-Style

Use instruction-based integration:

1. Initialize the project with Owledge.
2. Give the agent the repo link and project root.
3. Ask it to follow `AGENTS.md` and use local Python commands.

Verify:

```bash
python tools/owledge.py doctor --project-root .
python tools/owledge.py build-context-pack --project-root . --task-id opencode-smoke
```

## Generic Agents

Use the repo-link flow when the runtime has no plugin system:

```text
Use Owledge from this repo and this project root.
Read AGENTS.md first.
Write only plans, evidence, reviews, and handoffs into Owledge-owned folders.
Do not rewrite existing knowledgebase files.
```

Verify:

```bash
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py test kb-module --project-root .
```

## Verify

For a release-quality local install, run:

```bash
python tools/owledge.py finalization-gates --project-root . --include-compliance
python tools/owledge.py benchmark --project-root .
```

For a plugin-only smoke test, run:

```bash
python tools/owledge.py test runtime-adapters --project-root .
```

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Hooks do not write session files | Run `python tools/owledge.py doctor --project-root .` and inspect `.agent-control/logs/plugin-errors.jsonl`. |
| Runtime starts outside the project root | Start from the initialized project root or copy `tools/owledge_core.py` into the host project. |
| Session logs grow too large | Close/compact sessions and keep raw event files private. |
| Agent cannot find commands | Confirm the runtime loaded `plugins/owledge-cowork/commands/`. |
| Agent cannot find project skills | Confirm `.agents/skills/<skill>/SKILL.md` exists and run `doctor`; do not move skills into `.owledge/skills/`. |

## Uninstall

Remove the copied plugin folder from the runtime plugin area. In the host
project, remove `plugins/owledge-cowork/` only if the project no longer
uses the local adapter.

Do not delete `.owledge/` unless you intentionally want to remove project
memory. Raw private session logs can be cleaned separately after summaries have
been reviewed.

## Rule

Plugins and runtime skills are adapters. The project's local Markdown remains
the source of truth.
