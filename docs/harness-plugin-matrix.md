# Harness And Plugin Matrix

Owledge is a memory and planning layer around agent runtimes. The release
boundary is **local adapter support**: repo-installable files, skills, hooks,
and Python commands that can be verified locally. It is not a marketplace
certification for every runtime.

| Harness | Status | Install path | Notes |
| --- | --- | --- | --- |
| Principles-only coding agents | First-class support | Instructions or `owledge-principles` skill | No plugin, generated kit, wrapper, or OS-specific setup required. |
| Codex | Local adapter support | `.codex-plugin` plus local CLI | Repo-installable; verify with local gates. |
| Claude Code | Local adapter support | `.claude-plugin` or skills copy path | Start from project root when possible. |
| Cowork / Claude-compatible | Local adapter support | `plugins/owledge-cowork/` | Private runtime capture and durable summaries. |
| OpenCode-style agents | Instruction-based support | Repo link plus local instructions | No marketplace dependency required. |
| Generic agents | Instruction-based support | `AGENTS.md` plus local scripts | Good fit for repo-link onboarding. |
| MCP-compatible agents | Read-only P0 support | `tools/owledge_mcp.py` | Exposes entrypoint, doctor, search, context pack, tasks, and reviews; no write tools. |
| Existing Markdown / Obsidian KBs | Primary supported path | `tools/build_kb_module.py` or `owledge-map.json` | Additive by default, no wiki-link rewrite. |
| PI agents | Advanced optional path | PI skills and candidate artifacts | Candidate-only checks; never auto-promotes. |
| Superpowers users | Companion | Read-only coexistence | Superpowers executes, Owledge keeps durable memory. |
| Ponytail users | Companion | Works alongside existing runtime setup | Ponytail reduces code; Owledge preserves planning and memory. |

## Release Boundary

- Local adapter support means repo-installable and covered by local smoke or
  scenario gates.
- Marketplace listing is not required for this release.
- The Markdown source-of-truth model does not change across harnesses.
- Harness benchmarks for Claude Code, Codex, OpenCode, Cursor, and Zed are roadmap work, not a v0.7.0 claim.
- Write-enabled MCP is roadmap work. v0.7.0 intentionally ships read-only MCP first.
