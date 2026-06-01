# Roadmap

## Current Release Goal

Publish v0.5 as a project-ready Markdown-first Agent Memory Kit with lifecycle checks, retrieval calibration, runtime smoke tests, red-team QA, and a minimal project-folder-only setup path.

## Near-Term Roadmap

| Priority | Area | Outcome |
| --- | --- | --- |
| P0 | Publish readiness | GitHub repo with docs, license, privacy, security, examples |
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

## Compliance Roadmap

The compliance plan must be expanded before regulated production use. See `docs/compliance-roadmap.md`.

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

The dashboard is a later P4 extension and must not block the current Markdown-first release. It should start read-only and consume generated indexes, RAG exports, PI reports, red-team scorecards, and HTML reports. See `docs/dashboard-extension-plan.md`.

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
