# Harness And Plugin Matrix

Owledge is a memory and planning layer around agent runtimes.

| Harness | Status | Install path | Notes |
| --- | --- | --- | --- |
| Codex | Ready | `.codex-plugin` plus local CLI | Repo-installable today. |
| Claude Code | Ready | `.claude-plugin` or skills copy path | Start from project root when possible. |
| Cowork / Claude-compatible | Ready | `plugins/agent-memory-cowork/` | Private runtime capture and durable summaries. |
| OpenCode-style agents | Ready | Repo link plus local instructions | No marketplace dependency required. |
| Generic agents | Ready | `AGENTS.md` plus local scripts | Good fit for repo-link onboarding. |
| Existing Markdown / Obsidian KBs | Ready | `tools/build_kb_module.py` or `agent-memory-map.json` | Additive by default, no wiki-link rewrite. |
| PI agents | Optional | PI skills and candidate artifacts | Candidate-only checks; never auto-promotes. |
| Superpowers users | Companion | Read-only coexistence | Superpowers executes, Owledge keeps durable memory. |
| Ponytail users | Companion | Works alongside existing runtime setup | Ponytail reduces code; Owledge preserves planning and memory. |

## Release Boundary

- `Ready` means repo-installable and covered by local smoke or scenario gates.
- Marketplace listing is not required for this release.
- The Markdown source-of-truth model does not change across harnesses.
