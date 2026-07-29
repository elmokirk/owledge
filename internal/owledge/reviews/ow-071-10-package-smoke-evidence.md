---
title: "OW-071-10 package-install evidence"
date: "2026-07-29"
status: "partial"
ticket: "OW-071-10"
release: "v0.7.1"
tested_commit: "0c86550"
---

# OW-071-10 package-install evidence

## Scope

This record covers the package-artifact portion of the canonical Installation
Hub contract. It does not accept OW-071-10 or promote `G-071-B-ADOPTION`.

## Implemented control

Commit `0c86550` adds
`tests/unit/test_ow07110_package_install_smoke.py` and executes it in the
existing `core-matrix` CI job for Windows, macOS, and Linux on Python 3.10,
3.11, and 3.12.

The fixture:

1. copies only the declared package inputs into a temporary build source;
2. builds one wheel with `pip wheel --no-deps`;
3. removes that source before installation;
4. installs the wheel into a fresh virtual environment; and
5. invokes the installed `owledge` entrypoint for `quickstart` and
   host-mode `doctor`.

Removing the build source before invoking the entrypoint prevents the test
from treating an available checkout as proof of the package recipe.
Each fixture subprocess also removes `PYTHONPATH` and `PYTHONHOME`, and the
fixture proves that `tools.owledge` resolves beneath the fresh virtual
environment before invoking the installed entrypoint.

## Local Windows evidence

| Field | Result |
| --- | --- |
| Platform | Windows |
| Python | CPython 3.12.11 |
| Artifact | freshly built `owledge-0.7.0-py3-none-any.whl` |
| Entry point | installed `owledge`, not `python tools/owledge.py` |
| Commands | `quickstart --target <temporary-host-project>`; `doctor --project-root <temporary-host-project> --mode host` |
| Result | pass; both JSON payloads report `passed: true` |
| Duration | 12.581 seconds for the package-only smoke |

Focused replay at the tested commit:

```text
python -m unittest tests.unit.test_ow07110_install_contract \
  tests.unit.test_ow07110_package_install_smoke -v
# exit 0; 5 tests passed

python tools/validate_v1_delivery_plan.py
# exit 0; 64 tickets, 25 gates, 44 waves, 0 errors
```

## Known limitation and next action

The CI matrix has not run remotely for `0c86550`; therefore macOS and Linux
are **configured test lanes, not execution evidence**. The current workflow
does not trigger on this branch push alone; it runs on `main` pushes and pull
requests.

`D-071-24` records the product-owner decision to defer actual macOS/Linux
execution to the Stable/GA gate. Do not claim cross-platform acceptance in
v0.7.1; `OW-100-09` must attach the corresponding CI job URLs/logs or clean
runner transcripts before `G-100-GA` can pass.

The fixture originally copied the whole repository and exceeded the local
timeout because it included the benchmark corpus. The final fixture copies
only the package inputs declared in `pyproject.toml`, reducing the local
Windows replay to about thirteen seconds without weakening the wheel-only
boundary.

## Decision log

- Decision: treat the configured CI matrix as incomplete evidence, never as a
  completed macOS/Linux result.
- Decision: use the standard-library test harness plus `pip`; no new runtime
  dependency is introduced.
- Required next action: complete independent OW-071-10 install-fixture review;
  retain actual cross-platform execution as a Stable/GA prerequisite.

## Independent QA

Independent review reported `pass_with_concerns` (91/100): no P0/P1 findings;
the only P2 noted that a caller-supplied `PYTHONPATH` or `PYTHONHOME` could
obscure the import origin. The fixture now clears both variables and asserts
the installed module path before the acceptance transition.
