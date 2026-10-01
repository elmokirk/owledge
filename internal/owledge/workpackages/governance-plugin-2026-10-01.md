---
title: Governance plugin release checklist
date: 2026-10-01
status: awaiting-host-acceptance
---

- [x] Read AGENTS.md/CONTRIBUTING.md and current plugin specifications.
- [x] Create isolated feat/owledge-governance-plugins branch from current main.
- [x] Implement one profile, manifests, catalogs, optional reminder and documentation.
- [x] Execute package/hook tests: 27 passed, 2 native-host checks skipped; see VALIDATION.md.
- [x] Commit frozen sources, verify the 11 published plugin blob identities and open draft PR #8.
- [x] Check dedicated GitHub CI: Ubuntu and Windows package/hook jobs and publish job all succeeded.
- [x] Verify community release, source commit and all three asset digests against local builds.
- [ ] Operator: native Claude Code/Codex installation and behavioral acceptance.
- [ ] Maintainer: full legacy repository preflight before merging the draft PR.
- [ ] Publisher: official directory submissions after identity and test review.

## Evidence

Source commit: 4699666b0471f008b7728dc5c74056c4c098db2a.
PR: https://github.com/elmokirk/owledge/pull/8
CI: https://github.com/elmokirk/owledge/actions/runs/36836008974
Release: https://github.com/elmokirk/owledge/releases/tag/owledge-governance-v0.1.0-rc.1

The standalone ZIP SHA-256 is
`2d9b169406e1ce3ecd69a390ef0509cd6fbdcfede433bbd6c2a86482975a1c16`.
The marketplace ZIP SHA-256 is
`4808d345b44381a6d29ad1384abb46bf11bf472f4d8a9295956982bd371771b7`.
The SHA256SUMS.txt SHA-256 is
`e1496a34d3ddff780a153cb0b047df8ae637ca3cfbdd0bddd5beb3c8848cdd9f`.

This checklist update does not change the already released plugin package.
Native host acceptance, real knowledge-system scenarios and official directory
publication remain unverified. No user knowledge or existing runtime was modified.
