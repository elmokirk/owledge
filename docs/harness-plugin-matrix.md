# Harness And Plugin Matrix

Owledge Kit is a local/project utility kit. Marketplace distribution is a future
packaging step; the current release supports repo-based installation, plugin
folders, skills, hooks, and CLI wrappers.

| Harness | Current status | Install shape | Notes |
| --- | --- | --- | --- |
| Codex | Ready | `.codex-plugin` manifest, skills, local CLI | Use `plugins/agent-memory-cowork/.codex-plugin/plugin.json` plus project-local tools. |
| Claude Code | Manual plugin or skill copy | `.claude-plugin`, `skills/`, hooks | Install the plugin folder or copy skills into the Claude skills directory. |
| Claude/Cowork-compatible | Ready | Plugin folder with hooks | Hooks capture private runtime events and close sessions into draft summaries. |
| Generic agents | Ready | Repo link plus `docs/agent-integration-guide.md` | Agent reads the guide and runs local scripts with explicit paths. |
| Superpowers users | Ready as companion | Read-only scan of Superpowers plans | Superpowers executes; Owledge keeps durable memory and handoffs. |
| Obsidian / Markdown KB | Ready | Drop-in module or `agent-memory-map.json` | No wiki-link rewrite and no OS environment variables required. |

## Release Boundary

- Ready means repo-installable and covered by local smoke or scenario gates.
- Manual install means no official marketplace listing is required for v0.5.0.
- Future marketplace listings should not change the Markdown source-of-truth
  model.
