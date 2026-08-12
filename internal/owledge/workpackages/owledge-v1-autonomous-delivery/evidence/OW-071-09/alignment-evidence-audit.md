---
title: "OW-071-09 v0.7.1 Alignment Evidence Audit"
date: "2026-08-12"
status: pending_independent_recheck
type: release-alignment-evidence
release: v0.7.1
ticket: OW-071-09
document_version: 2
---

# OW-071-09 v0.7.1 Alignment Evidence Audit

This audit verifies the technical and documentary prerequisites for
`G-071-ALIGNMENT`. It does not substitute for the required explicit owner
decision; that decision remains pending in the release update.

## Commands

| Check | Result | Scope |
| --- | --- | --- |
| `python tools/validate_v1_delivery_plan.py` | Exit 0; 61 tickets, 25 gates, 43 waves, 0 errors | Control-plane consistency after the alignment handoff. |
| Required-heading check | Exit 0; all 11 protocol headings present | `release-updates/v0.7.1.md`. |
| Relative evidence-link check | Exit 0; all referenced local sources resolve | This update and its cited gate/decision sources. |
| `git diff --check` | Exit 0 | Alignment documents before commit. |

## Gate and claim sources

| Claim | Evidence or source | Provenance |
| --- | --- | --- |
| G-071-A truth scope | `internal/owledge/reviews/v0.7.1-docs-adoption-external-user-review.md` and `RUN-STATE.yaml` gate register | Promoted prior to the bounded adoption phase. |
| G-071-B adoption | `internal/owledge/reviews/g-071-b-adoption-gate-evidence.md` | `cb741d3`; 28 focused tests plus cumulative checks. |
| G-071-C compatibility | `internal/owledge/reviews/g-071-c-compat-gate-evidence.md` | Owlib/Hermes bounded compatibility evidence. |
| G-071-RC | clean finalization run on source commit `1475ff6` | 38/38; release-trust 18/18; docs-contract 341 checks. |
| Cross-platform limitation | `internal/owledge/decisions/v0.7.1-cross-platform-stable-gate-2026-07-30.md` | D-071-24 defers executed macOS/Linux proof to OW-100-09. |
| v0.8 lock | `RUN-STATE.yaml` alignment register and `BACKLOG.yaml` dependencies | D-071-29 remains active; OW-080-01 depends on OW-071-09. |

## Implementation Findings

| Finding | Evidence | Resolution |
| --- | --- | --- |
| F-071-32 | `eee8c19` changes `upgrade-drift` to validate the generated project in Host mode | Replayed green in the clean RC finalization run. |
| F-071-33 | `eacc3c6` and `1475ff6` reconcile v0.7.1 release/plugin metadata | Clean RC finalization run follows the reconciliation. |

## Remaining gate condition

The technical/documentary audit is green. `G-071-ALIGNMENT` itself remains
unpromoted because its threshold requires an explicit owner `approve`,
`adjust`, or `defer` decision with constraints recorded in
`release-updates/v0.7.1.md`.

## Independent QA checkpoint

The first independent alignment review rejected the update because it had not
transferred the full finding/decision registers and replaced the registered
next-version reflection with a blanket keep statement. Those P0 omissions were
corrected in document version 2. A narrow recheck is required before the
technical/documentary portion can be accepted; the owner-decision condition
remains separate and pending.
