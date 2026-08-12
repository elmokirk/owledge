---
title: "OW-071-06 Owlib Project Contract Acceptance Evidence"
date: "2026-08-12"
status: accepted
type: qa-evidence
ticket: OW-071-06
release: v0.7.1
tested_commit: pending
---

# OW-071-06 Owlib Project Contract Acceptance Evidence

## Delivered contract

Owlib 0.2 now treats `OWLEDGE.md` plus `.owledge/` as the current project
contract. `PROJECT_CONTEXT.md` plus `agent-memory/` remains readable only for
an explicitly registered legacy-only project via `--legacy-layout`, and emits a
deprecation warning. A project containing both layouts always fails closed,
including when that legacy flag is supplied.

Sync is reviewed-only by default. Unsafe shared records remain rejected
independently of that default; `--include-unreviewed` is an explicit override
and is mutually exclusive with `--reviewed-only`. Imported records retain a
project/path-derived stable source ID and a content hash. Candidate paths must
resolve inside the registered project before import.

## Verification

| Command | Result |
| --- | --- |
| `PYTHONPATH=owlib/src python -m unittest discover -s owlib/tests -v` | Exit 0; 10 tests passed, one Windows symlink integration test skipped because symlink creation is unavailable. |
| `PYTHONPATH=owlib/src python -m owlib --help` | Exit 0; CLI entry point loads. |
| `git diff --check` | Exit 0. |

The suite covers current-default registration, explicit legacy migration and
warning, mixed-layout rejection with and without the legacy flag, missing
entrypoint rejection, reviewed-only default, unsafe shared rejection, stable
source IDs, raw-session exclusion, conflicting CLI review-scope flags, and
platform-independent containment logic.

## Independent privacy/migration QA

The first review returned `revise` at 82/100. It found that a legacy flag could
admit a mixed layout and that conflicting review-scope flags were silently
resolved. Both were fixed and covered by regressions. Re-review returned
`accept` at 94/100 with no P0 or P1 findings.

## Remaining evidence limitation

The real filesystem symlink walk is implemented and has an integration test,
but that test is skipped on this Windows runner because symlink creation is not
available. The same containment logic is exercised without a symlink. A
symlink-capable Linux or macOS CI lane must retain and execute the integration
test; this is evidence follow-up, not a v0.7.1 runtime-support claim.
