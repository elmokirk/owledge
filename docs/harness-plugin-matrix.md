# Harness And Plugin Matrix

Owledge is a memory and planning layer around agent runtimes. **Local adapter support**
is the V1 release boundary: project-local files and Python
commands that can be verified locally. It is not a marketplace certification
for every runtime.

| Harness | Status | Install path | Notes |
| --- | --- | --- | --- |
| Principles-only coding agents | First-class support | Instructions or `owledge-principles` skill | No plugin, generated kit, wrapper, or OS-specific setup required. |
| Codex | V1 reference adapter | `.agents/skills/` or `.codex-plugin` plus local Core CLI | Uses the project-local Core contract; no direct storage. |
| Claude Code | V1 reference adapter | `.claude-plugin` or configured skills copy path | Uses the project-local Core contract; no direct storage. |
| Generic MCP/CLI | V1 reference adapter | `tools/owledge_generic_adapter.py` | Exactly five Core tools; explicit Candidate-only write. |
| Cowork / Claude-compatible | Post-V1/legacy add-on | `plugins/owledge-cowork/` | Not a V1 reference-adapter claim. |
| OpenCode-style agents | Post-V1 instruction integration | Repo link plus local instructions | May use the generic contract; no V1 Tier-1 claim. |
| Generic agents | Generic contract consumer | `AGENTS.md` plus local scripts | Must implement the bounded generic MCP/CLI contract. |
| Legacy read-only MCP | Advanced compatibility route | `tools/owledge_mcp.py` | Not the V1 generic MCP/CLI contract. |
| Existing Markdown / Obsidian KBs | Primary supported path | `tools/build_kb_module.py` or `owledge-map.json` | Additive by default, no wiki-link rewrite. |
| PI agents | Advanced optional path | PI skills and candidate artifacts | Candidate-only checks; never auto-promotes. |
| Superpowers users | Companion | Read-only coexistence | Superpowers executes, Owledge keeps durable memory. |
| Ponytail users | Companion | Works alongside existing runtime setup | Ponytail reduces code; Owledge preserves planning and memory. |

## Release Boundary

- V1 reference-adapter support means project-local and covered by controlled
  local conformance evidence.
- Marketplace listing is not required for this release.
- The Markdown source-of-truth model does not change across harnesses.
- Project-root `skills/` is a shipped source/vendor bundle, not a universal
  automatic discovery path. `.owledge/skills/` is not used for discovery.
- The [skills and agent integrations guide](skills-and-agent-integrations.md)
  defines skill selection, instruction/hook/CLI precedence, host proof, and
  recovery for missing or drifting mirrors.
- Harness benchmarks and marketplace certification remain post-V1 work.
- The V1 generic MCP/CLI bridge has one bounded Candidate write; it is not a
  direct storage, promotion, remote-sync, or hosted-service API.
