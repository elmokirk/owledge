---
memory_id: "mem:owledge:global:owledge:plan:release-qa-contract-hardening"
doc_type: "plan"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Release QA contract hardening"
summary: "Implement version, documentation, feature-surface, and release-promotion contracts."
created_at: "2026-07-15T00:00:00Z"
updated_at: "2026-07-15T00:00:00Z"
branch: "main"
---

# Release QA Contract Hardening

## Goal

Prevent public documentation, feature claims, package metadata, main, and
PyPI from silently drifting apart.

## Phases

- [x] Define the release-surface contract and CLI gates.
- [x] Enforce contract coverage in PR CI and release CI.
- [x] Add release-branch promotion and PyPI reconciliation.
- [x] Add regression tests and run the release gate matrix.

## Definition of Done

Every public release claim has contract-backed documentation and verification;
release promotion verifies PyPI before fast-forwarding main; and a failed
promotion is visible and blocks a later release.
