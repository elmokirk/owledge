---
title: "OW-071-07 Hermes Read-Only Profile Acceptance Evidence"
date: "2026-08-12"
status: accepted
type: qa-evidence
ticket: OW-071-07
release: v0.7.1
tested_commit: pending
---

# OW-071-07 Hermes Read-Only Profile Acceptance Evidence

## Delivered profile

The Hermes profile binds each stdio MCP server process to a single current
Owledge project at startup. It exposes exactly six read-only tools, rejects a
caller path that differs from that binding, and rejects unknown/write-like tool
names. The server validates that `OWLEDGE.md`, `.owledge`, and all discovered
paths resolve inside the bound project before each tool call.

`docs/hermes-readonly-profile.md` provides the bounded YAML configuration,
verified configuration/restart baseline, version-dependent optional MCP command
guidance, tool order, and recovery boundaries. Hermes memory/compression stays
separate from Owledge Markdown artifacts. The runtime contract and transcript
contain no write, promotion, sync, filesystem, Git, performance, or VPS claim.

## Verification

| Command | Result |
| --- | --- |
| `python -m unittest tests.unit.test_ow07107_hermes_readonly tests.unit.test_ow07112_agent_integrations -v` | Exit 0; 9 tests passed. |
| `python tools/owledge.py test mcp-readonly --project-root .` | Exit 0; exactly six read-only tools, no write-like tools. |
| `python tools/owledge.py test public-docs --project-root .` | Exit 0; 0 failures. |
| `python tools/owledge.py test docs-contract --project-root .` | Exit 0; 473 checks. |
| `python tools/validate_v1_delivery_plan.py` | Exit 0; 61 tickets, 25 gates, 43 waves, 0 errors. |

The protocol fixture covers initialize/version, all six tools, missing bound
entrypoint, path mismatch, disabled tool, and containment of an external
resolved path. A real symlink entrypoint is additionally tested where the host
permits symlink creation.

## Independent review

The first independent runtime/security review returned `revise` at 72/100 and
found symlink entrypoint escape plus a server/document version mismatch. Both
were fixed. The second review confirmed those technical fixes; documentation
was then narrowed to version-dependent optional Hermes commands and plain ASCII
failure wording. No unresolved P0 or P1 remains.

## Limits

This is a local read-only MCP profile. It is not a Hermes plugin, does not
measure Hermes token/performance behavior, and does not prove VPS deployment or
write authority.
