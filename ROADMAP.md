# Roadmap

## Current Release Goal

Publish v0.5 as a project-ready Markdown-first Agent Memory Kit with lifecycle checks, retrieval calibration, runtime smoke tests, red-team QA, and a minimal project-folder-only setup path.

## Near-Term Roadmap

| Priority | Area | Outcome |
| --- | --- | --- |
| P0 | Publish readiness | GitHub repo with docs, license, privacy, security, examples |
| P0 | PyPI publishing | Publish `owledge` console script so users can `pip install owledge` instead of source checkout |
| P1 | HTML reports | Visual decision, handoff, RAG readiness, and activity reports |
| P1 | Project-folder setup | Implemented: minimal local folder generator with explicit copy manifest and verification |
| P1 | Runtime adapters | Implemented: Claude/Cowork fixtures and generic CLI runtime smoke wrapper |
| P1 | Incremental indexes | Implemented: full rebuild remains default; optional incremental mode writes `memory-index.jsonl`, `memory-index-manifest.json`, and optional `memory-index-tombstones.jsonl` |
| P1 | Agentic memory completeness | Implemented: architecture doc and gates for working, semantic, procedural, and episodic memory behavior |
| P1 | RAG readiness gate | Implemented for project-kit scope: retrieval fixtures, unsafe shared export checks, and raw-session exclusion |
| P1 | Episodic retention | Implemented for audit scope: retention classes, stale-memory audits, conflict review, and read-only purge/anonymization preview |
| P1 | LightRAG roundtrip | Optional adapter and eval for ingesting reviewed exports into Neo4j/Qdrant-backed LightRAG |
| P1/P2 | Global User Knowledge Layer | Optional private user-level memory for preferences, goals, daily work, tasks, ideas, research, patterns, coaching and onboarding |
| P2 | Compliance pack | DSGVO and AI Act implementation plan |
| P2 | Hub sync | Project-to-central-hub promotion and export workflow |
| P2 | Optional backend ownership | Leases, ownership journal, promotion queue while Markdown remains canonical |
| P3 | Capture daemon | Reduce process overhead for high-frequency hooks |
| P4 | Dashboard add-on | Optional read-only visual interface for health, retrieval, PI intelligence, QA, graph, reports, and later promotion workflows |
| P0 | Kit version stamping | Every shipped template carries `owledge_kit_version`; `kit-manifest.json` records per-file hashes | 
| P0 | Upgrade command | `owledge upgrade --dry-run/--apply` with safe/force-templates/manual modes; never-touch list; idempotent |
| P1 | Drift detection | `doctor` reports `version-drift` + `outdated_files` + `user_edited_files` |
| P1 | Global-layer registry | `init-project --link-global` writes `global-link.json`; `doctor` checks the link |
| P1 | Dogfood-sync gate | `dogfood-sync` finalization gate + `sync-dogfood` CLI; one-way mirror templates → internal |
| P1 | Concept blindspot skill | `concept-blindspot-audit` skill that stress-tests distribution, lifecycle, coherence (v0.6.1 Phase 5) |

## Feedback-Derived Roadmap (v0.5.x — 2026-06-23)

Collected from a structured feedback round covering integration, privacy,
planning discipline, cross-project intelligence, and publish readiness. See
`docs/feedback-round-2026-06.md` for the full ticket and `docs/roadmap-ideas-2026-06.md`
for idea log entries.

| Priority | Area | Outcome | Source question |
| --- | --- | --- | --- |
| P0 | Publish owledge to PyPI | `pip install owledge` works; refactor made sdist clean, now execute the publish | Q1, Q3, vibe-coder, influencer |
| P1 | AGENTS.md/CLAUDE.md copy-paste integration block | SOTA one-block paste for host projects that do not use the skills path; shipped in docs | Q3 |
| P1 | Token cost benchmark with tokenizer baselines | Add tokenizer-based token measurements to benchmarks; publish before/after token comparison | Q2 |
| P1 | Global privacy controls + folder whitelist | User controls which folders are scannable; per-project opt-in to global owlib registration with explicit consent prompt | Q6, Q10a |
| P1 | Project abstract + project mode (PoC/MVP/Side/SaaS) | Force a one-paragraph project abstract combining goals + roadmap; mode selector sets planning discipline depth | Q10b |
| P2 | Cross-project parallel notification | Owlib `find-parallels` writes a notification artifact the agent reads at session start; no background daemon in v1 | Q4, Q10a |
| P2 | PI Agent setup guide + provider auth | Document how to set up PI Agent; clarify it runs deterministic signals locally (no LLM provider auth needed for v1) and when provider auth is needed for semantic mode | Q5 |
| P2 | Plan completion detection contract | Standardize `status: done` + `acceptance_criteria` + `qa_gate_ids` as the harness-agnostic completion signal; document in planning-layer skill | Q7 |
| P2 | Idea-duplicate handling + permission modes | Add `planning_mode: supervised/approve-automatically/full-access` toggle; when an idea already exists, agent behavior depends on mode | Q8 |
| P2 | MVP goal/metric definition template | Add a `success_metrics` section to the MVP plan template with user-specific, measurable acceptance criteria | Q9 |
| P3 | Idea-to-project pipeline | Filter upcoming ideas (project-scoped and global-scoped), collect in priority order, and scaffold a new `PROJECT_CONTEXT.md` from a promoted idea | Q10c |
| P3 | Feedback round integration | Add a recurring feedback-round workflow to collect, triage, and promote user feedback into roadmap items | Q (meta) |

### Round 2: Feature Ideas

Feature ideas collected in the same 2026-06 round, focused on ticket board,
harness hooks, supervised-mode UX, and schema extensions. See
`docs/feedback-round-2026-06.md` tickets FB-013 through FB-017 and
`docs/roadmap-ideas-2026-06.md` idea cards IDEA-2026-006-12 through -16.

| Priority | Area | Outcome | Source |
| --- | --- | --- | --- |
| P1 | Minimal ticket board with timeline + frontmatter sync | `owledge ticket-board` renders a Markdown board grouped by `status` with priority sorting; frontmatter sync hook updates `status: done` when QA gates pass | Feature idea 1 (FB-013) |
| P1 | Quick-read section on all tickets | Add a `quick_read` field (under 300 chars) to `TaskCard` schema as a maintained view; validation gate detects stale quick-reads; board uses `quick_read`, not full bodies | Feature idea 4 (FB-016) |
| P1 | Cleanly defined project abstract + modes | Define 4 project modes (`poc`, `mvp`, `side`, `saas`) with intuitive definitions and per-mode planning discipline in `PROJECT_CONTEXT.template.md` | Feature idea 5 (FB-017) |
| P2 | Harness hook extensions for Codex/Claude | Extend existing hook layer with `PostToolUse` frontmatter validation and `Stop`/`SessionEnd` `validate-memory --strict`; document extension points | Feature idea 2 (FB-014) |
| P2 | Ticket summary in supervised approval | In `supervised` mode, render a compact 5-line ticket summary (title, priority, status, description, source link) inline before asking for approval | Feature idea 3 (FB-015) |

## Compliance Roadmap

The compliance plan must be expanded before regulated production use. See `docs/archive/compliance-roadmap.md`.

## Global User Knowledge Layer Roadmap

The global user layer is optional and privacy-first. It sits above project memory and gives agents durable user context without making project repositories the canonical store for personal data. See `docs/global-user-knowledge-layer.md`.

| Phase | Goal |
| --- | --- |
| P1 | Structure, templates, onboarding, read order, privacy defaults and validation |
| P2 | Global indexes, metrics, stale-knowledge checks and Personal PI reports |
| P3 | Coach layer and runtime integration for Codex, Claude, Hermes, OpenClaw/OpenCode and PI Agents |
| P4 | Personal cockpit/dashboard for goals, ideas, daily work, research freshness and project carryover |
| P5 | Compliance, retention, PII scanning and encrypted private vault options |

## Dashboard Add-On Roadmap

The dashboard is a later P4 extension and must not block the current Markdown-first release. It should start read-only and consume generated indexes, RAG exports, PI reports, red-team scorecards, and HTML reports. See `docs/archive/dashboard-extension-plan.md`.

| Phase | Goal |
| --- | --- |
| P4.0 | Read-only local dashboard for memory health, export freshness, PI reports, red-team scores, and source links |
| P4.1 | Retrieval console for short questions against scoped project, shared, lessons, patterns, and PI corpora |
| P4.2 | Graph and parallel discovery UI from typed frontmatter edges and candidate parallels |
| P4.3 | Review and promotion queue using existing promotion tooling and audit manifests |
| P4.4 | Agent operations view for sessions, compaction, hook failures, context-pack metrics, and runtime status |
| P4.5 | Enterprise hub dashboard with tenant/customer views, compliance status, and customer-safe reports |

## HTML Reporting Roadmap

| Phase | Templates |
| --- | --- |
| 1 | Decision, handoff, RAG readiness |
| 2 | Agent activity, project dashboard |
| 3 | Website/UI decision report with design-token controls |
| 4 | Hub-wide executive reports and customer-safe exports |
