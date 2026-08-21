# AdapterManifest v1

Runtime Conformance Kit makes local adapter support auditable; it does not make
marketplace-certification or untested runtime claims. The V1 profile set is
fixed: `codex`, `claude-code`, and `generic-mcp-cli`.
Each manifest declares only local `project_user` and `user_global` context,
read/control, checkpoint/handoff, and project-scoped Candidate writes. The
manifest explicitly reports unsupported automatic pre-plan inspection, durable
routing, direct Core storage access, enterprise scope, and orchestration.

`tools/owledge_adapter_contracts.py` validates and negotiates this boundary.
The add-on runner stays read-only and checks that all three shipped manifests
make equivalent declarations.

The generic MCP/CLI adapter exposes exactly five V1 tools: `capabilities`,
`recall`, `context`, `propose`, and `review`. Each delegates to the installed
project-local Core; it contains no separate storage, index, search or lifecycle
implementation. Initialize a Generic MCP/CLI host with explicit `--profile full`
so its project-local `tools/` Core exists; the minimal profile stays intentionally
tool-free. Codex and Claude Code use the same five operations through the
owner-invoked project-local CLI bridge; only the generic adapter exposes them as
MCP tools. No adapter has a separate storage or lifecycle surface.
