---
title: "Hermes Read-Only Owledge Profile"
version: "0.8.0"
document_version: 1
status: active
---

# Hermes Read-Only Owledge Profile

This is the v0.8.0 Tier-1 **read-only** profile for Hermes Agent. It binds one
Hermes MCP server process to one local Owledge project. It does not grant
Owledge write, promotion, Git, network, synchronization, or Hermes memory
authority.

## Install and bind

Use a Python executable and absolute project path that the Hermes host can
read. The path must contain `OWLEDGE.md`.

```yaml
mcp_servers:
  owledge_readonly:
    command: "python"
    args: ["/absolute/path/to/tools/owledge_mcp.py", "--project-root", "/absolute/path/to/project"]
    timeout: 30
    connect_timeout: 45
```

After saving the Hermes configuration, inspect the configured block with
`hermes config show` and restart with `hermes chat`. If the installed Hermes
version exposes MCP management commands, it may additionally support
`hermes mcp test owledge_readonly`, `hermes mcp list`, and `/reload-mcp`; verify
those optional commands against that installed version before using them.
Do not add a filesystem or Git MCP server merely to make this profile work.

## Required tool proof

The server offers exactly these eight tools:

1. `owledge_read_entrypoint`
2. `owledge_doctor`
3. `owledge_search_memory`
4. `owledge_build_context_pack`
5. `owledge_context_synopsis`
6. `owledge_active_tools`
5. `owledge_list_tasks`
6. `owledge_list_reviews`

Run the entrypoint, one scoped search, and one context-pack request first.
Use tasks or reviews only when needed. All responses are local reads or
in-memory context construction. A caller-supplied `project_root` must match the
server's startup binding; a different path fails explicitly. Start another
server process for another project.

## Boundaries and recovery

Hermes conversation memory/compression is separate from `.owledge/` artifacts.
This profile never writes evidence or handoffs; create those through the normal
reviewed Markdown workflow. An unavailable MCP server, missing `OWLEDGE.md`,
unbound project, path mismatch, or disabled tool is a clear failure; do not
fall back to broad filesystem access or claim that a write tool exists.

This fixture proves the local read-only profile only. It does not make
Hermes-specific token, performance, VPS, or persistent-memory claims.
