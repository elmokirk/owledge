---
title: "G-071-B-ADOPTION Cumulative Gate Evidence"
date: "2026-08-12"
status: passed
type: gate-evidence
gate: G-071-B-ADOPTION
release: v0.7.1
tested_commit: cb741d3
---

# G-071-B-ADOPTION Cumulative Gate Evidence

## Decision

`G-071-B-ADOPTION` passes for the bounded v0.7.1 development scope. It permits
the compatibility work (`OW-071-06`, then `OW-071-07`) but does not authorize a
cross-platform package-support claim. `D-071-24` retains executed macOS and
Linux wheel transcripts as Stable/GA evidence in `OW-100-09`.

## Ticket evidence

| Ticket | Accepted evidence |
| --- | --- |
| `OW-071-04` | Five-second beginner comprehension, public-docs, and docs-contract checks; independent claim-governance re-review. |
| `OW-071-10` | Canonical installation routes and Windows CPython 3.12 wheel-only smoke; source-only boundary and D-071-24 stable-gate decision. |
| `OW-071-11` | Workflow architecture/privacy evidence with final independent review at 97/100. |
| `OW-071-12` | Fresh-host discovery, read-only MCP allowlist, runtime-adapter checks; final conformance review at 96/100. |
| `OW-071-14` | Preset-choice and maturity-boundary checks; final independent review at 100/100. |
| `OW-071-05` | `ow-071-05-golden-demo-evidence.md`: installed-wheel journey, idempotent resume, and independent beginner re-review at 89/100. |

## Cumulative replay

| Verification | Result |
| --- | --- |
| Seven focused ticket modules | Exit 0; 28 tests passed on Windows CPython 3.12. |
| `python tools/owledge.py test public-docs --project-root .` | Exit 0; 0 failures. |
| `python tools/owledge.py test docs-contract --project-root .` | Exit 0; 473 checks. |
| `python tools/owledge.py test mcp-readonly --project-root .` | Exit 0; six read-only tools and no write-like tools. |
| `python tools/owledge.py test runtime-adapters --project-root .` | Exit 0. |
| `python tools/validate_v1_delivery_plan.py` | Exit 0; 61 tickets, 25 gates, 43 waves, 0 errors. |
| `git diff --check` | Exit 0. |

## Threshold assessment

The replay supports the beginner narrative, bounded installation and
source-only add-on separation, host-project agent discovery, read-only runtime
boundary, selectable presets, no-write 30-second proof, package-only
five-minute and fresh-resume proof, and idempotent rerun. The public/document
contract checks found no unsupported privacy, Hub, or runtime claim.

The three-OS CI fixture remains configured as a contract. It is not presented
as completed macOS/Linux execution. This limitation is tracked, visible, and
does not block the owner-approved bounded v0.7.1 development gate under
`D-071-24`.
