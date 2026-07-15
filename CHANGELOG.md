# Changelog

## Unreleased

- Release QA hardening: machine-readable version, documentation, and feature
  contracts now block incomplete public changes; future releases promote a
  tested release branch to main only after PyPI confirms the package.

## 0.7.0 (2026-06-26)

- Public contract: `.owledge/` is the canonical project memory folder and `OWLEDGE.md` is the visible agent/project entrypoint.
- Packaging: wheel/sdist data now ships `templates/owledge/`, `OWLEDGE.template.md`, native planning templates, and the new `owledge-brainstorm` skill.
- CLI: added `wikilink-audit` and read-only MCP smoke coverage.
- MCP: added `tools/owledge_mcp.py` with read-only entrypoint, doctor, search, context-pack, task, and review tools.
- Planning: added first-class reviews, audiences, research, and brainstorm candidate layers.
- Benchmark Kit: consolidated benchmark proof into the optional `benchmark-kit` add-on with real synthetic Markdown fixtures, injected distractor/stale/private/multi-hop/handoff problems, and JSON/MD/HTML/SVG outputs.
- CI: release gates now validate v0.7 contracts, `.owledge` fresh installs, Wikilink Audit, Benchmark Kit CI, read-only MCP, wheel smoke, and `uvx --from dist/<wheel>`.
- Docs: README, quickstart, command reference, performance notes, harness matrix, and roadmap now present the uv-first v0.7 surface and roadmap deferrals.

### Upgrade notes

breaking: yes

v0.7.0 renames the old public memory surface. Pre-v0.7 docs and installs may mention `agent-memory/` and `PROJECT_CONTEXT.md`; those names are legacy. New projects use `OWLEDGE.md` plus `.owledge/`. Compatibility fallbacks may exist inside selected tools, but active docs, contracts, quickstarts, package data, and generated kits target the v0.7 surface. Existing pre-v0.7 local installs should regenerate from v0.7 or migrate manually before relying on v0.7 release gates.

## 0.6.1 (2026-06-24)

- E1: Version stamp every shipped file. Added `owledge_kit_version` frontmatter field to all shipped templates; formalized `version:` as `MEMORY_SCHEMA_VERSION` (1.0.0). `init-project` now writes `kit-manifest.json` with `kit_version`, `memory_schema_version`, and per-file `sha256_installed` + `sha256_original`.
- E2: `doctor` gained a `version-drift` check comparing the manifest's `kit_version` against the running CLI's `KIT_VERSION`. Return shape extended with `outdated_files` and `user_edited_files`.
- E3: New `owledge upgrade` command with `--dry-run`/`--apply` and `--mode=safe|force-templates|manual`. Safe mode preserves user-edited files; force-templates respects a hardcoded never-touch list; manual emits a `git apply`-able patch. File lock prevents concurrent runs. Idempotent.
- E4: `init-project` gained `--link-global [<path>]` flag. Writes `.owledge/global-link.json` resolving via flag -> `OWLEDGE_GLOBAL_HOME` env -> `~/.owledge/global` default. `doctor` gained a `global-link` check.
- E5: New `dogfood-sync` finalization gate + `sync-dogfood` CLI subcommand. One-way mirror: `templates/owledge/templates/` -> `internal/owledge/templates/`. Asserts one-way direction in code.
- E6: Added `docs/upgrading.md` (full upgrade guide: stamping, mode matrix, never-touch guarantee, recovery, additive-vs-breaking semantics). Added the schema-change contract to `CONTRIBUTING.md` (bump VERSION + `## Upgrade notes` + paste `upgrade --dry-run` output). Added the release-notes verification step to `release.yml`. Added the PR template checkbox. Amended `docs/v0.6.0-implementation-plan.md:259` (FB-016 stays `warning` until E3 ships). Added 6 ROADMAP rows.
- Phase 5: New `concept-blindspot-audit` skill with an 8-dimension rubric (dims 1-4 mechanical, 5-8 guided), `references/audit-dimensions.md`, `references/profile-template.json`, and the `concept-audit-template.md` report template. New `concept-audit` CLI subcommand (`--dimension`, `--profile`, `--format`). New `concept-audit-fresh` finalization gate (warns at `mvp`, fails at `saas`). The skill ships in `skills/concept-blindspot-audit/` and is installed by `init-project` into user projects.
- New finalization gates: `dogfood-sync`, `upgrade-drift`, `concept-audit-fresh`.
- New CLI subcommands: `upgrade`, `sync-dogfood`, `dogfood-sync-check`, `concept-audit`.
- FB-016 amendment: `quick_read` stale-detection stays `warning` until `owledge upgrade` (E3) ships; tracked via `ROADMAP.md`. See `docs/v0.6.0-implementation-plan.md` line 259.
- Fix-up (red-team `internal/owledge/decisions/red-team-v0.6.1-pr.md`): `HOST_SKILL_DIRS` now includes `skills/concept-blindspot-audit` and `_collect_kit_files` walks `HOST_SKILL_DIRS`, so skills are installable, manifest-tracked, drift-detected, and upgradable. `upgrade --apply --mode=manual` is now rejected (manual mode is always dry-run; never writes). The manual-mode patch now emits `diff --git a/<rel> b/<rel>` headers with `a/`/`b/` prefixes and `new file mode 100644` for new files, so `git apply --check` succeeds. `upgrade --format summary` is now honored. `concept-audit --since` (dead flag) removed. `force-templates` now prompts interactively on a TTY when `--yes` is omitted. `concept_audit` return shape now includes a top-level `score` (mean of scored dimensions). `release.yml` upgrade-notes diff-base now uses the prior tag (`git describe --tags --abbrev=0`) instead of `HEAD~1`. Added `docs/v0.6.1-fix-up-plan.md`. Added `docs/command-reference.md` entries for `concept-audit`. Added 22 stress tests under `tests/` + `pytest.ini` + `conftest.py`. Added a CI `fresh-install-cycle` job. Added session-continuity checklists to the planning layer (FB-018). Logged follow-ups FB-018..FB-021 and IDEA-2026-006-17/18.
- Fix: `pyproject.toml` `version` was `0.6.0` while `VERSION` was `0.6.1`; corrected to `0.6.1` and added `test_pyproject_version_matches_version_file`.

### Upgrade notes

breaking: no

This release is additive: it adds version stamping, drift detection, an upgrade command, a global-layer registry, a dogfood-sync gate, and the concept-blindspot-audit skill. No existing memory records, frontmatter fields, or schemas are removed or renamed. The `version:` frontmatter field is repurposed as `MEMORY_SCHEMA_VERSION` (was previously inconsistent: 0.1.0 on some templates, 0.4.0 on others); it is now consistently 1.0.0 everywhere. Users who pinned logic to the old inconsistent values should read `docs/upgrading.md`.

The fix-up corrects three P0 issues from the red-team review: skills are now enrolled in `kit-manifest.json` (re-run `init-project` on a v0.6.0 install to enroll skills), `manual` mode is always dry-run, and the manual-mode patch is now `git apply`-able.

## 0.6.0 (2026-06-24)

- Refactor: split development dogfood from product deliverables (commit `3440e30`).
  Moved product source to `templates/owledge/`, moved all dogfood to
  `internal/owledge/`, removed root `.owledge/` entirely.
- Added 4 integrity gates: `kit-integrity`, `addon-boundary-check`,
  `source-vs-target-audit`, `sdist-clean`.
- Updated `MANIFEST.in` to include `templates/` and exclude `internal/` (clean
  sdist with zero dogfood paths).
- Updated `CONTRIBUTING.md` with Dogfooding vs. Product section.
- Fixed `finalization-gates` invocation to use `--project-root .` (auto-detects
  `internal/owledge/` for memory operations) in CI, AGENTS.md, CLAUDE.md,
  and internal/README.md.
- Mirrored `.gitignore` patterns for `internal/owledge/` so generated
  dogfood artifacts (shared-* exports, red-team reports, tmp, indexes) are no
  longer tracked; latest snapshots remain tracked as evidence.
- Added `docs/feedback-round-2026-06.md` with 17 feedback tickets (FB-001 through
  FB-017, including Round 2 feature ideas FB-013 through FB-017).
- Added `docs/roadmap-ideas-2026-06.md` with 16 idea cards (IDEA-2026-006-01
  through -16, including Round 2 feature ideas -12 through -16).
- Added `docs/agents-md-integration-block.md` - SOTA copy-paste block for
  integrating Owledge into existing AGENTS.md/CLAUDE.md.
- Added `docs/pi-agent-setup.md` - PI Agent setup guide.
- Added `docs/v0.6.0-implementation-plan.md` - detailed plan for landing the
  12 remaining feedback features in a future release.
- Updated `ROADMAP.md` with feedback-derived roadmap section.

## 0.5.0

- Added retention lifecycle fields, read-only retention audit, conflict review, and sensitive-data scan wrappers.
- Added objective-aware context-pack scoring with `score_breakdown`, `freshness_warnings`, and explicit exclusion reasons.
- Added retrieval calibration fixtures, query-file support, and minimum score thresholds for release gates.
- Added minimal project-folder-only generator and quickstart docs.
- Added runtime adapter smoke tests, finalization gate runner, and red-team QA wrapper.
- Added Agentic Memory architecture docs mapping working, semantic, procedural, and episodic memory.

## 0.4.0

- Added global/project memory kit instructions and expanded PI Agent memory folders.
- Added reusable review workflows, HTML report rendering, and publishing docs.
- Added incremental indexing and host verification hardening.

## 0.3.0

- Added Markdown-first Owledge core.
- Added strict frontmatter, stable `memory_id`s, typed edges, templates, and schemas.
- Added validation, memory index, context pack, RAG, LightRAG, GraphRAG, and retrieval eval tools.
- Added optional Claude/Cowork and Codex plugin adapter.
- Added private runtime capture and draft session summaries.
- Added ignored dogfood projects for multi-agent and Zeus simulations.
- Added publish preparation, privacy/security docs, and compliance roadmap.
