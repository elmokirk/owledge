---
title: "G-071-C Compatibility Gate Evidence"
date: "2026-08-12"
status: passed
type: gate-evidence
gate: G-071-C-COMPAT
release: v0.7.1
tested_commit: pending
---

# G-071-C Compatibility Gate Evidence

`G-071-C-COMPAT` passes for the bounded v0.7.1 scope. Owlib 0.2 accepts the
current project contract by default, isolates legacy migration, and rejects
unsafe/unreviewed records. Hermes is a local, project-bound read-only MCP
profile with six tools and explicit failures for unbound startup, path mismatch,
disabled tools, and resolved-path escape.

| Verification | Result |
| --- | --- |
| Owlib unit/quality suite | Exit 0; 10 tests, one Windows symlink integration skip. |
| Hermes profile plus integration regression | Exit 0; 9 tests. |
| `mcp-readonly` | Exit 0; six read-only tools, no write-like tools. |
| `runtime-adapters` | Exit 0. |
| Delivery-plan validator | Exit 0; 61 tickets, 25 gates, 43 waves, 0 errors. |

The Windows symlink limitation remains evidence follow-up for a symlink-capable
Linux/macOS CI lane. It is not hidden and does not expand v0.7.1 platform or
runtime claims. This gate labels Owlib preview and Hermes read-only profile
only; it does not claim Hermes plugin, write, VPS, or performance support.
