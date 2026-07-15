---
memory_id: "mem:owledge:global:owledge:workpackage:release-qa-contract-hardening"
doc_type: "workpackage"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Release QA contract hardening checklist"
summary: "Implementation and evidence checklist for release QA hardening."
created_at: "2026-07-15T00:00:00Z"
updated_at: "2026-07-15T00:00:00Z"
---

# Release QA Contract Hardening Checklist

## Resume State

Current phase: Complete. Commit and CI handoff pending.

## Checklist

- [x] Add a machine-readable release surface and feature contract.
- [x] Implement version, docs, and release CLI contracts.
- [x] Require contracts in PR and release workflows.
- [x] Add a PyPI verification and fast-forward promotion transaction.
- [x] Add mutation and workflow-helper regression tests.
- [x] Run targeted gates and record evidence.

## Evidence

- `python -m py_compile tools/owledge.py tests/unit/test_release_contracts.py` completed successfully.
- `python tools/owledge.py test version-contract` completed successfully for `0.7.0`.
- `python tools/owledge.py test docs-contract --base-ref origin/main` completed successfully with no missing required documentation.
- `python tools/owledge.py test release-contract --evidence-path dist/release-contract-test-evidence.json` completed successfully and wrote machine-readable evidence.
- `python tools/owledge.py test public-docs` and `python tools/owledge.py test publish-readiness` completed successfully; the readiness score was 155.
- The local environment has no `pytest` package, so the new pytest regression module is syntax-checked here and will run in CI.
