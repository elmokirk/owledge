---
memory_id: "mem:owledge:global:owledge:plan:2026-08-21-ci-cli-pipeline-repair"
doc_type: "plan"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "CI, documentation, packaging and CLI pipeline repair"
summary: "Root-cause repair plan for the general CI and Docs workflows after the v0.8.0 PyPI artifact hotfix."
created_at: "2026-08-21T00:00:00+02:00"
updated_at: "2026-08-22T00:00:00+02:00"
branch: "codex/fix/ci-cli-pipeline"
base_commit: "2e82c93fc093ea1439ff1c0fc04eb1160abbca45"
---

# CI, Docs, Packaging and CLI Pipeline Repair

## Goal

Make the general CI and Docs pipelines green from `origin/main` commit
`2e82c93fc093ea1439ff1c0fc04eb1160abbca45` without weakening product
contracts, security boundaries, assertions, or release gates. The release
workflow remains `workflow_dispatch`-only and is not executed.

## Promotion Boundary

This work may repair CI configuration, packaging metadata and implementation,
directly affected CLI modules and contracts, tests whose expectations are
proved stale against the V1 Minimal Core decision, and broken or intentionally
historical documentation links. It does not authorize merge, tag, publish,
release creation, artifact upload, release-workflow dispatch, platform claims
without executed evidence, or expansion beyond the two-scope/eight-CLI/five-MCP
V1 boundary.

## Root-Cause Classification

Every failure is classified before repair as one of:

1. product regression;
2. stale test expectation;
3. defective CI or packaging environment; or
4. historical documentation link with an archived or external target.

The working root-cause matrix is maintained in the paired workpackage and must
name the failing job, first failing command, root cause, owner file, repair, and
regression test.

## Phases and QA Gates

### Phase 1 - Baseline and remote evidence

- Confirm the fetched `origin/main` commit and empty branch diff.
- Read all workflows and download logs for CI runs `32509171812` and
  `32493768585`, plus Docs runs `32509171664` and `32493768708`.
- Identify the first real failure per platform/job and reproduce the smallest
  red loop locally.

Gate: the root-cause matrix contains evidence for every currently failing job;
no follow-on failure is treated as the cause.

### Phase 2 - Vertical root-cause repairs

- Repair one root cause at a time.
- Add or correct the narrow regression contract for each repair.
- Compare every behavioral change with the V1 Minimal Core boundary.
- Commit atomic slices using `fix(ci)`, `fix(cli)`, `fix(package)`, or `docs`.

Gate: each focused reproducer passes before the next root cause is changed;
forbidden migration files and product/security boundaries remain unchanged.

### Phase 3 - Cumulative local release confidence

- Run all directly affected tests and both required V1 gates.
- Run `git diff --check`.
- Build a wheel from clean source and run a wheel-only smoke in a clean
  temporary environment/source boundary.
- Verify no generated files or build artifacts are tracked.

Gate: all locally reproducible affected gates are green and evidence records
commands, exit codes, environment, and limitations.

### Phase 4 - Independent QA and remote branch gates

- After implementation is complete, use one independent QA subagent only for
  final review, as authorized by the task.
- Push `codex/fix/ci-cli-pipeline` only after local gates are green.
- Observe CI and Docs for the branch/PR context; do not dispatch Release.

Gate: CI and Docs are green, or every remaining failure has branch-independent
evidence and an explicit risk statement.

## Definition of Done

- The root-cause matrix is complete and evidence-linked.
- Wheel-only installation is green in every executed CI platform lane; claims
  are limited to that evidence.
- Full release-gate unit failures are fixed by product repair or contract-
  justified test updates, never skips or loosened assertions.
- Wikilink audit is green with historical intent preserved.
- Required V1 plan and GA-candidate tests, affected suites, clean wheel build
  and smoke, and `git diff --check` pass.
- Changes are atomic, pushed to the working branch, and accompanied by an exact
  merge proposal while merge/tag/publish/dispatch remain unperformed.

## Resume Rule

Resume from the first unchecked item in the paired checklist. If interrupted
mid-phase, rerun that phase's gate before continuing and record fresh evidence.

## Current Decision Gate

The owner approved the V1-aligned release-gate correction. Launch readiness now
requires the direct Minimal Core inputs and all exclusion rules, rejects every
unapproved population directive that could reopen a pruned surface, and retains
the existing negative checks. Independent QA findings were repaired with
focused regressions; the remaining boundary is remote branch validation after a
fresh base-commit check.

## Mandatory Next-Start Work

Feature work after this repair is blocked on two owner-prioritized P0 tickets:

- `POST-V1-REPOSITORY-CONSOLIDATION-001`: repository truth, lifecycle, package,
  and CI cleanup.
- `POST-V1-CODE-ARCHITECTURE-REVIEW-001`: expert-level source and architecture
  review followed by small evidence-backed refactoring packages.

These tickets record the next session's scope; they do not authorize an
unbounded cleanup inside this CI repair.
