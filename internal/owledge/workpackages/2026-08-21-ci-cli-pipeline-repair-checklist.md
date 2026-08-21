---
memory_id: "mem:owledge:global:owledge:workpackage:2026-08-21-ci-cli-pipeline-repair"
doc_type: "workpackage"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "CI, documentation, packaging and CLI pipeline repair checklist"
summary: "Resume state, root-cause matrix, phase gates, and evidence for the CI/Docs repair branch."
created_at: "2026-08-21T00:00:00+02:00"
updated_at: "2026-08-21T00:00:00+02:00"
branch: "codex/fix/ci-cli-pipeline"
base_commit: "2e82c93fc093ea1439ff1c0fc04eb1160abbca45"
---

# CI, Docs, Packaging and CLI Pipeline Repair Checklist

## Resume State

Current phase: Phase 1 - remote evidence and smallest red loops.

Last completed atomic action: created the isolated worktree from a freshly
fetched `origin/main` after confirming the expected base commit; read
`AGENTS.md`, `ci.yml`, `docs.yml`, and `release.yml` completely.

Next exact action: download job metadata and logs for the four named GitHub
Actions runs and populate the root-cause matrix from each first failing command.

Prohibited shortcuts: no skip, broad allowlist, relaxed assertion, release
dispatch, tag, publish, upload, merge, recursive Codex invocation, generated
artifact commit, or change to the protected migration files/skill.

## Phase Checklist

### Phase 1 - Baseline and evidence

- [x] Fetch and confirm `origin/main` equals `2e82c93fc093ea1439ff1c0fc04eb1160abbca45`.
- [x] Create isolated worktree and branch `codex/fix/ci-cli-pipeline`.
- [x] Confirm HEAD, merge-base, status, and empty diff to `origin/main`.
- [x] Read repository instructions and all workflow files completely.
- [ ] Download current and prior-baseline CI/Docs job logs.
- [ ] Record the first failing command and root cause for each failing job.
- [ ] Reproduce each smallest red loop locally before changing implementation.

Phase 1 gate: pending.

### Phase 2 - Vertical repairs

- [ ] Repair packaging/wheel-only smoke root cause and add regression coverage.
- [ ] Repair or contract-correct full-release-gate failures by root cause.
- [ ] Repair wikilink audit while preserving historical-document intent.
- [ ] Commit each independent root cause atomically.

Phase 2 gate: pending.

### Phase 3 - Cumulative local gates

- [ ] Run `python -m unittest tests.unit.test_v1m10_ga_candidate -v`.
- [ ] Run `python tools/validate_v1_delivery_plan.py`.
- [ ] Run all locally reproducible affected tests.
- [ ] Run `git diff --check`.
- [ ] Build wheel from a clean temporary source boundary.
- [ ] Run wheel-only smoke in a clean temporary environment.
- [ ] Confirm no generated/build artifacts are tracked.

Phase 3 gate: pending.

### Phase 4 - Independent and remote QA

- [ ] Request one independent final QA subagent after implementation is complete.
- [ ] Resolve all independent QA findings or record justified non-findings.
- [ ] Push the working branch.
- [ ] Observe CI and Docs without dispatching Release.
- [ ] Prepare exact merge proposal and stop before merge.

Phase 4 gate: pending.

## Root-Cause Matrix

| Run / job | First failing command | Classification | Root cause | Owner file | Repair | Regression test / evidence |
| --- | --- | --- | --- | --- | --- | --- |
| CI `32509171812` / pending | pending | pending | pending | pending | pending | pending |
| Docs `32509171664` / `docs-integrity` | `python tools/owledge.py wikilink-audit --project-root . --check` | pending | 13 existing unresolved/ambiguous links reported remotely; exact target intent pending log and source inspection | pending | pending | current + prior Docs logs; focused audit |
| CI `32493768585` / prior baseline | pending | pending | pending | pending | pending | pending |
| Docs `32493768708` / prior baseline | pending | pending | pending | pending | pending | pending |

## Evidence Log

- 2026-08-21: `git fetch origin main --prune` exit 0.
- 2026-08-21: `git rev-parse origin/main` returned
  `2e82c93fc093ea1439ff1c0fc04eb1160abbca45`.
- 2026-08-21: worktree creation exit 0; branch tracks `origin/main`.
- 2026-08-21: initial `git status --short --branch` showed no branch changes.
- Environment note: root `OWLEDGE.md` and root `.owledge/` are absent in this
  source repository; the instruction-named `bootstrap-owledge` skill is not
  available in this Codex session, so no bootstrap or overwrite was performed.

## Independent QA Lane

Single lane only, final phase only: review the complete branch diff, failure
classification, V1 boundary preservation, packaging smoke design, docs-link
intent, and gate evidence. The QA agent must not implement feature work unless
the orchestrator explicitly requests a bounded follow-up after findings.
