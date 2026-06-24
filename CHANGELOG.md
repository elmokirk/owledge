# Changelog

## 0.6.0 (2026-06-24)

- Refactor: split development dogfood from product deliverables (commit `3440e30`).
  Moved product source to `templates/agent-memory/`, moved all dogfood to
  `internal/agent-memory/`, removed root `agent-memory/` entirely.
- Added 4 integrity gates: `kit-integrity`, `addon-boundary-check`,
  `source-vs-target-audit`, `sdist-clean`.
- Updated `MANIFEST.in` to include `templates/` and exclude `internal/` (clean
  sdist with zero dogfood paths).
- Updated `CONTRIBUTING.md` with Dogfooding vs. Product section.
- Fixed `finalization-gates` invocation to use `--project-root .` (auto-detects
  `internal/agent-memory/` for memory operations) in CI, AGENTS.md, CLAUDE.md,
  and internal/README.md.
- Mirrored `.gitignore` patterns for `internal/agent-memory/` so generated
  dogfood artifacts (shared-* exports, red-team reports, tmp, indexes) are no
  longer tracked; latest snapshots remain tracked as evidence.
- Added `docs/feedback-round-2026-06.md` with 17 feedback tickets (FB-001 through
  FB-017, including Round 2 feature ideas FB-013 through FB-017).
- Added `docs/roadmap-ideas-2026-06.md` with 16 idea cards (IDEA-2026-006-01
  through -16, including Round 2 feature ideas -12 through -16).
- Added `docs/agents-md-integration-block.md` — SOTA copy-paste block for
  integrating Owledge into existing AGENTS.md/CLAUDE.md.
- Added `docs/pi-agent-setup.md` — PI Agent setup guide.
- Added `docs/v0.6.0-implementation-plan.md` — detailed plan for landing the
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

- Added Markdown-first Agent Memory core.
- Added strict frontmatter, stable `memory_id`s, typed edges, templates, and schemas.
- Added validation, memory index, context pack, RAG, LightRAG, GraphRAG, and retrieval eval tools.
- Added optional Claude/Cowork and Codex plugin adapter.
- Added private runtime capture and draft session summaries.
- Added ignored dogfood projects for multi-agent and Zeus simulations.
- Added publish preparation, privacy/security docs, and compliance roadmap.
