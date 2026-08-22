---
memory_id: "mem:owledge:global:owledge:workpackage:2026-08-21-ci-cli-pipeline-repair"
doc_type: "workpackage"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "CI, documentation, packaging and CLI pipeline repair checklist"
summary: "Resume state, root-cause matrix, phase gates, and evidence for the CI/Docs repair branch."
created_at: "2026-08-21T00:00:00+02:00"
updated_at: "2026-08-22T00:00:00+02:00"
branch: "codex/fix/ci-cli-pipeline"
base_commit: "2e82c93fc093ea1439ff1c0fc04eb1160abbca45"
---

# CI, Docs, Packaging and CLI Pipeline Repair Checklist

## Resume State

Current phase: Phase 4 - remote branch gates.

Last completed atomic action: resolved all four independent final-QA findings
with focused regression evidence and recorded the owner-mandated P0 cleanup and
expert-review tickets for the next start.

Next exact action: fetch `origin/main`, stop if it differs from the expected base,
otherwise push the branch, open a Draft PR, and observe CI and Docs without
dispatching Release.

Prohibited shortcuts: no skip, broad allowlist, relaxed assertion, release
dispatch, tag, publish, upload, merge, recursive Codex invocation, generated
artifact commit, or change to the protected migration files/skill.

## Phase Checklist

### Phase 1 - Baseline and evidence

- [x] Fetch and confirm `origin/main` equals `2e82c93fc093ea1439ff1c0fc04eb1160abbca45`.
- [x] Create isolated worktree and branch `codex/fix/ci-cli-pipeline`.
- [x] Confirm HEAD, merge-base, status, and empty diff to `origin/main`.
- [x] Read repository instructions and all workflow files completely.
- [x] Download current and prior-baseline CI/Docs job logs.
- [x] Record the first failing command and root cause for each failing job.
- [x] Reproduce each smallest red loop locally before changing implementation.

Phase 1 gate: passed; current and prior runs show the same failure classes.

### Phase 2 - Vertical repairs

- [x] Repair packaging/wheel-only smoke root cause and add regression coverage.
- [x] Repair or contract-correct full-release-gate unit failures by root cause.
- [x] Repair wikilink audit while preserving historical-document intent.
- [x] Repair Finalization memory validation without relaxing its schema.
- [x] Resolve the stale `launch-readiness` manifest contract after owner approval.
- [x] Commit each completed independent root cause atomically.

Phase 2 gate: passed; the V1 artifact boundary is stricter than the stale gate
and no check, exclusion, or product boundary was removed.

### Phase 3 - Cumulative local gates

- [x] Run `python -m unittest tests.unit.test_v1m10_ga_candidate -v`.
- [x] Run `python tools/validate_v1_delivery_plan.py`.
- [x] Run all currently reachable locally reproducible affected tests.
- [x] Run `git diff --check`.
- [x] Build wheel and Sdist from a committed clean temporary source boundary.
- [x] Run wheel-only smoke in a clean temporary environment.
- [x] Confirm no generated/build artifacts are tracked.

Phase 3 gate: package, unit, docs, clean-kit, Sdist, and Finalization evidence
is green; cumulative `publish-readiness` awaits the Phase 2 decision.

### Phase 4 - Independent and remote QA

- [x] Request one independent final QA subagent after implementation is complete.
- [x] Resolve all independent QA findings or record justified non-findings.
- [ ] Push the working branch.
- [ ] Observe CI and Docs without dispatching Release.
- [ ] Prepare exact merge proposal and stop before merge.

Phase 4 gate: pending.

## Root-Cause Matrix

| Run / job | First failing command | Classification | Root cause | Owner file | Repair | Regression test / evidence |
| --- | --- | --- | --- | --- | --- | --- |
| CI `32509171812` / 9 core matrix lanes | `python -m unittest tests.unit.test_ow07110_package_install_smoke` | defective packaging test environment | Temporary source fixture omitted the PEP 517 backend `owledge_build.py`, so every OS failed during build-requirements discovery with `ModuleNotFoundError` before install. | `tests/unit/test_ow07110_package_install_smoke.py` | Copy the declared backend into the isolated source fixture. | `d474139`; focused wheel smoke 2/2; clean artifact smoke. |
| CI `32509171812` / same wheel command after backend repair | second package smoke journey | stale CLI/demo contract | Golden demo invoked deprecated `build-context-pack`, which now correctly enforces tenant scope; V1 exposes `context`. | demo docs and package/golden tests | Exercise the public V1 `context` operation and its structured sources. | `51fdd52`; golden 4/4 and wheel smoke 2/2. |
| CI `32509171812` / `full-release-gates` | `python -m pytest tests/unit/ -q --tb=short` | mixed product regression and stale tests | Upgrade manifest captured lock/journal/user state; missing-manifest path failed too early; full-profile legacy tests assumed the new minimal default; several frozen assertions contradicted V1 decisions; skill mirrors drifted; UNC classification differed by host; historical register validation used only the active backlog. | CLI, validators, skill mirrors, focused tests | Repair product behavior and explicitly select legacy full profile; update only decision-proven stale expectations. | `4c0ca09` through `83cd8fa`; 277 passed, 8 Windows capability skips, 45 subtests passed. |
| CI / `publish-readiness` reached locally | `python tools/owledge.py test publish-readiness --project-root .` | stale release-gate contract | June `launch-readiness` searched for recursive full-payload manifest strings; August V1 intentionally prunes add-ons/all docs/all tools. | `tools/owledge.py` plus GA regression | Require exact V1 inputs/exclusions and reject unapproved `include`, recursive include, `graft`, or `global-include` population of bounded surfaces. | `6db5455`, `7b5c04a`; launch readiness 105/105; injected reopen directives rejected. |
| Independent QA / live register | `python tools/validate_live_work_register.py` | stale active truth | The live register still declared 0.7.0/0.7.1 while `VERSION` and package metadata declare 0.8.0; a synthetic test hid the real mismatch. | live register, `ROADMAP.md`, validator test | Restore validation against repository truth and align the active product/release baseline. | `869d084`; validator passed 21/21 records; 18 focused validator tests pass. |
| Independent QA / public package wording | Wheel member inspection | stale documentation | README claimed direct V1 docs were in both wheel and Sdist, while those direct docs are Sdist inputs. | `README.md` | Distinguish wheel runtime data from the Sdist's additional direct documentation. | `abb5c1c`; package boundary remains unchanged. |
| Independent QA / platform ticket | frontmatter/body comparison | ambiguous lifecycle wording | `status=active` and `review_status=reviewed` described the ticket contract, but “Status: open” could be read as contradictory platform acceptance. | `POST-V1-PLATFORM-001.md` | Separate ticket lifecycle, contract review, and still-open platform evidence acceptance. | `abb5c1c`; no macOS/Linux claim added. |
| CI / `finalization-gates` reached locally | internal memory `validate` subgate | invalid current-document metadata | Six current V1/KEOS records used non-schema statuses/edge types or lacked mandatory pattern fields; one personal historical record was marked shared without approval metadata. | three ADRs, two post-V1 tickets, KEOS pain-points record | Supply meaningful required metadata, use valid lifecycle/edge vocabulary, and keep the personal historical record private. | `aa46fcd`; non-strict validator 214 checks, 0 failed; all 38 Finalization gates pass. |
| Docs `32509171664` / `docs-integrity` | `python tools/owledge.py wikilink-audit --project-root . --check` | historical external document references | 13 wikilinks pointed into the separate KEOS vault, not missing Owledge documents. | two 2026-07-31 KEOS history files | Preserve names while classifying them as external KEOS-vault references; no ignore or allowlist. | `95ecd6a`; 2,167 files, 0 unresolved, 0 ambiguous. |
| CI/Docs prior runs `32493768585` / `32493768708` | same first commands | pre-existing baseline | Same wheel/full-suite/Wikilink classes already fail on `c1eac58`; they were not introduced by the PyPI hotfix. | same owners | Same vertical repairs. | Downloaded prior logs and compared job conclusions. |

## Evidence Log

- 2026-08-21: `git fetch origin main --prune` exit 0.
- 2026-08-21: `git rev-parse origin/main` returned
  `2e82c93fc093ea1439ff1c0fc04eb1160abbca45`.
- 2026-08-21: worktree creation exit 0; branch tracks `origin/main`.
- 2026-08-21: initial `git status --short --branch` showed no branch changes.
- Environment note: root `OWLEDGE.md` and root `.owledge/` are absent in this
  source repository; the instruction-named `bootstrap-owledge` skill is not
  available in this Codex session, so no bootstrap or overwrite was performed.
- Remote logs: CI `32509171812` and Docs `32509171664` at `2e82c93`; prior CI
  `32493768585` and Docs `32493768708` at `c1eac58` show matching first failures.
- Atomic repair commits: `d474139`, `51fdd52`, `4c0ca09`, `5666ade`,
  `91fe481`, `adf91e9`, `e01875c`, `f9e303f`, `83cd8fa`, `95ecd6a`, `aa46fcd`.
- Unit suite: 277 passed, 8 skipped because Windows symlink creation is
  unavailable, 45 subtests passed; no skip was added by this branch.
- Required V1 gates: GA candidate 5/5; delivery-plan validator passed with 11
  tickets, 11 execution waves, and 7 gates.
- Docs audit: 2,167 files, 23 repository links, 0 unresolved, 0 ambiguous.
- Packaging: focused clean-source wheel smoke 2/2; committed clean archive built
  `owledge-0.8.0-py3-none-any.whl` and `owledge-0.8.0.tar.gz`; `sdist-clean`
  checked 274 files with no leak/missing-tree violation; offline install,
  quickstart, doctor, and isolated import-origin checks passed on Windows.
- Artifact hashes (local Windows evidence only): wheel
  `BFC44B849AEABED38FDFCDBF75732360674C105C3E240F676876A41363D4D41A`;
  Sdist `FEBCB0E153506FCAC07D4F5718A7A077F9CFE756E8F92F29964E59E1D2AE031F`.
- Clean-kit build verified; kit-integrity checked 128 files; add-on boundary had
  0 violations; source-vs-target audit passed.
- Finalization: all 38 reported subgates passed after metadata repair; generated
  export deltas were restored and were not staged or committed.
- Owner approval applied: `6db5455` aligned launch readiness with the Minimal
  Core and `7b5c04a` added fail-closed coverage for all manifest population
  directives that could reopen bounded paths.
- Independent final QA identified four findings; `869d084`, `7b5c04a`, and
  `abb5c1c` resolve them. Focused QA rerun: 24 tests passed; live register passed
  with 21 items; launch readiness passed 105/105; memory validation passed
  224 checks with zero failures.
- Next-start P0 tickets: `POST-V1-REPOSITORY-CONSOLIDATION-001` and
  `POST-V1-CODE-ARCHITECTURE-REVIEW-001`. They require cleanup, canonical truth,
  layered CI, expert review, and bounded refactoring before feature work.

## Independent QA Lane

Single lane only, final phase only: review the complete branch diff, failure
classification, V1 boundary preservation, packaging smoke design, docs-link
intent, and gate evidence. The QA agent must not implement feature work unless
the orchestrator explicitly requests a bounded follow-up after findings.

Completed: the single read-only QA lane found live-register version drift,
manifest reopen gaps, inaccurate wheel/Sdist wording, and ambiguous platform
ticket lifecycle wording. All four were corrected with focused evidence; no
second QA lane was started.
