---
title: "OW-071-05 Golden Demo Acceptance Evidence"
date: "2026-08-12"
status: accepted
type: qa-evidence
ticket: OW-071-05
release: v0.7.1
tested_commit: cb741d3
---

# OW-071-05 Golden Demo Acceptance Evidence

## Delivered bounded journey

The public journey in `docs/vibecoding-golden-demo.md` has three deliberately
separate routes:

1. A 30-second, read-only proof with no install, API call, account, or write.
2. A package-only five-minute journey that creates the three bounded project
   artifacts for `filter-request` and shows the exact resume prompt.
3. A visibly separate source-only add-on demonstration; it is not part of the
   package quickstart claim.

The seed artifacts are examples only. The package journey asks the user or
agent to author their equivalents after `owledge quickstart`; an acceptance
check uses the supported `doc_type: qa` value even though it is stored in the
`evidence/` folder.

## Reproducibility and boundary checks

`test_wheel_only_golden_demo_resumes_without_a_runtime_or_checkout` builds a
wheel from a temporary source copy, deletes that copy before installation,
clears source import variables through the shared wheel helper, and executes
only the installed CLI from a fresh virtual environment. It then simulates the
three bounded agent-authored artifacts, runs `quickstart` again, checks its
additive `skipped_existing` behavior, runs `doctor` and `build-context-pack`,
and verifies that no runtime/plugin target was introduced.

The focused fresh-resume test verifies the exact scope, all three acceptance
checks, the next safe action, and the explicit prohibition against inferring
sync, deletion, or account work from a new chat.

## Commands and results

| Command | Result |
| --- | --- |
| `python -m unittest tests.unit.test_ow07105_golden_demo tests.unit.test_ow07110_package_install_smoke -v` | Exit 0; 6 tests passed on Windows CPython 3.12. |
| `python tools/owledge.py test public-docs --project-root .` | Exit 0; zero failures. |
| `python tools/owledge.py test docs-contract --project-root .` | Exit 0; 473 checks. |
| `python tools/validate_v1_delivery_plan.py` | Exit 0; 61 tickets, 25 gates, 43 waves, 0 errors. |

## Independent QA

The independent beginner QA first returned `revise` at 78/100: the package
proof used the repository CLI, idempotence/runtime absence was not enforced,
and the resume proof was link-only. The follow-up increment added the
wheel-only installed-CLI test, rerun/footprint assertions, and semantic resume
assertions. Re-review returned `accept` at 89/100 with no P0 or P1 findings.

The reviewer recorded a P2-only local sandbox failure while its own isolated
pip build attempted to fetch build dependencies. This does not replace the
successful authorized Windows wheel execution above and must not be presented
as macOS or Linux evidence.

## Scope limitations

Per `D-071-24`, actual macOS and Linux wheel execution remains a Stable/GA
requirement in `OW-100-09`. The configured three-OS CI fixture is a contract,
not completed cross-platform execution evidence; v0.7.1 makes no such support
claim.
