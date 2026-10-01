---
title: Standalone governance plugin prerelease
date: 2026-10-01
status: in-progress
branch: feat/owledge-governance-plugins
---

# Standalone governance plugin

Build one portable governance skill with Claude Code and Codex manifests and
repository marketplace catalogs. Keep runtime versions, data and existing
plugins unchanged. Base: 3836fc393aa8d8e2eadb1dee7934a4a72d6e6606.

## Phases and acceptance

1. Inspect repo instructions, pinned v0.9.0rc1 principles and official plugin docs.
2. Write profile, native manifests, optional reminder hook, documentation and tests.
3. Run local package/hook tests. Record missing native-host and full-runtime checks.
4. Publish the frozen source to the feature branch, verify remote file identities
   and open a draft PR. A dedicated CI job may publish a separate community RC
   after package tests. Official directory review remains external.

## Stop conditions

Do not overwrite the runtime or bypass branch protection. Do not claim official
listing or successful host tests without evidence. Do not accept publisher terms.
Node/Python are available locally; Claude/Codex are absent and shell networking
cannot reach GitHub. Use the connected GitHub API for repository operations.
