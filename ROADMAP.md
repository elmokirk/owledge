# Roadmap

Roadmap version: **2.3.0**
Last updated: **2026-08-12T14:32:51+02:00**

## Current Release Goal

Prepare v0.7.1 as the adoption, truth, and compatibility release while
preserving v0.7.0 as the currently shipped package baseline.

The machine-readable
[`LIVE-WORK-REGISTER.yaml`](internal/owledge/workpackages/owledge-v1-autonomous-delivery/LIVE-WORK-REGISTER.yaml)
is the only live status source for feedback items FB-001 through FB-021.
Historical plans, feedback records, idea logs, and unchecked checkboxes remain
evidence; they do not create active work.

Public contract:

- `.owledge/` is the canonical project memory folder.
- `OWLEDGE.md` is the visible project and agent entrypoint.
- Public docs are uv-first.
- Read-only MCP, Wikilink Audit, Native Planning Layers, and Benchmark Kit V2 are P0.
- Harness benchmarks, write-enabled MCP, Research Memory recall, Pi integration,
  Single-Organization Hub Beta, RAG engine integrations, cloud/frontier benchmark
  matrices, and marketplace certification are roadmap items until implemented and benchmarked.
- The v1 target is Standalone Core GA plus a separately labelled Single-Organization
  Hub Beta. Hosted multi-tenant SaaS remains post-v1.
- Knowledge scopes are `project_user`, `user_global`, and `enterprise`; every
  cross-project query remains deny-by-default outside its authorized scope.
  `user_global` is private and local-first in v1; the Hub never uploads it implicitly.
- V0.8.1 must prove one private local `user_global` composition shared by at
  least two harnesses; remote private-global synchronization remains post-v1.
- Scope, knowledge abstraction, and lifecycle are independent. The promoted
  global Knowledge Base stores reviewed essences and preserves authorized
  drill-down to project/source revisions; Global Raw is only a private review queue.
- Material managed-document edits require a document revision bump distinct
  from schema/profile versions. Deterministic Knowledge Health is planned for
  Core; content-free Hub operations health remains separate from generic tracing.
- Semantic mutations use one revision-aware Core interface, and policy-driven
  source withdrawal propagates through promoted and derived surfaces.
- V1 defines managed-surface, module-manifest, resource-reference, transactional
  upgrade, and separated health-profile contracts without adding a plugin SDK,
  binary store, transcription pipeline, or privacy-management suite.
- A coverage-bounded personal-data erasure/DSAR control plane and PII
  detection/redaction adapters are relevant post-v1 enterprise modules. General
  tombstone and source-withdrawal hygiene remains in V1; masking is not deletion.
- V0.7.1 RC requires the clean aggregate finalization suite, including the
  generated-surface `upgrade-drift` gate. The diagnosed regression is routed
  into `OW-071-08` and does not authorize V0.8 work.

## Release Board

| Status | Ticket | Feature | DoD | Target |
| --- | --- | --- | --- | --- |
| Done | REL-001 | `.owledge/` foundation | New quickstarts and generated kits create `.owledge/` plus `OWLEDGE.md`; contracts validate the v0.7 surface. | v0.7.0 |
| Done | REL-002 | Package-first install | Wheel/sdist package data includes templates, tools, plugins, add-ons, and standalone skills; `uvx`/wheel smoke paths are documented. | v0.7.0 |
| Done | REL-003 | Owledge naming cut | Active public docs, plugin paths, skills, package metadata, and workflows use Owledge naming; legacy names are only migration/archive context. | v0.7.0 |
| Done | REL-004 | Read-only MCP | `tools/owledge_mcp.py` exposes entrypoint, doctor, search, context-pack, tasks, and reviews without write tools; MCP smoke gate passes. | v0.7.0 |
| Done | REL-005 | Wikilink Audit | `owledge wikilink-audit --check` reports valid, broken, and ambiguous wiki links without rewriting Markdown. | v0.7.0 |
| Done | REL-006 | Native planning layers | Reviews, audiences, research, and brainstorm candidate layers exist under `.owledge/` and ship with templates/skills. | v0.7.0 |
| Done | REL-007 | Benchmark Kit Add-on | Optional `benchmark-kit` add-on supports `small`, `mid`, and `large` real Markdown fixture simulations, retrieval challenge scenarios, sequential Ollama local runs, single-run reports, and multi-model comparison proof reports. | v0.7.0 |
| Done | REL-008 | Standalone skills | `standalone-skills/` ships independently usable blindspot audit, agentic review, brainstorm, and planning-layer skills with manifest and install notes. | v0.7.0 |
| Done | REL-009 | Release gates and CI | CI and local gates check naming, public docs, release trust, launch readiness, MCP read-only, Wikilinks, Benchmark Kit CI, standalone skills, contracts, and publish readiness. | v0.7.0 |
| Done | REL-010 | Final publishing docs | README, docs index, quickstart, command reference, roadmap, changelog, troubleshooting, Mermaid workflows, plugin docs, and benchmark docs match the implemented v0.7 surface. | v0.7.0 |
| Done | POST-001 | Final release artifact cut | v0.7.0 package publication is retained as release evidence; future cuts use the active release control plane. | v0.7.0 final |
| Planned | POST-002 / OW-100-05 | CLI UX simplification | Add short lifecycle commands such as `owledge init`, `owledge add benchmark-kit`, and `owledge benchmark local` while preserving explicit script paths and recovery behavior. | v1.0 |
| Planned | POST-003 | Agent-native runtime contract | Define a compact runtime contract for session start, context-pack loading, task/handoff discovery, hook events, and token-aware read order across harnesses. | v0.8.0 |
| Planned | POST-004 | PI Agent runtime adapter | Evaluate and implement PI Agent as a lightweight Owledge runtime lane only if it can preserve `.owledge/` as source of truth and pass conformance gates. | v0.8.0 |
| Planned | POST-005 | Harness benchmarks | Benchmark Claude Code, Codex, OpenCode, Cursor, and Zed with local/cloud model setups and clear caveats. | v0.8.x |
| Planned | POST-006 | Own-vault benchmark mode | Extend the optional Benchmark Kit to run privacy-safe measurements against a user's existing Owledge vault. | v0.8.x |
| Planned | POST-007 | Write-enabled MCP | Add scoped write tools with locks, privacy checks, review requirements, and audit artifacts. | v0.9.0 |
| Planned | POST-008 | Cloud/frontier benchmark matrix | Extend Benchmark Kit to Ollama Cloud/frontier/local-hosted models with cost and resource warnings. | v0.9.x |
| Planned | POST-009 | RAG integrations | Export Owledge's canonical Markdown layer to Mem0, Graphiti, LlamaIndex, vector DBs, or enterprise RAG systems. | v0.9.x |
| Planned | POST-012 | OKF interchange profile | Validate, export, and import Google Open Knowledge Format bundles without weakening Owledge's stricter lifecycle, privacy, and promotion model. | v0.8.x |
| Planned | POST-013 / OW-080-16 | Research Memory recall | Deepen the existing research folders and templates into stable source/finding/synthesis contracts with recall-first deduplication, source mutability, freshness, research reason/context, delta-only refresh, and settings-controlled autonomous capture. | v0.8.0-v0.9.0 |
| Planned | POST-014 / OW-081-04 | Pi reference adapter | Ship `@owledge/pi` as a thin reference adapter for bootstrap, scoped retrieval, structured Session Recap/Handoff, and controlled Candidate writes over shared Owledge capabilities. | v0.8.1 |
| Planned | POST-015 / OW-100-11 | Single-Organization Hub Beta | Support one organization per deployment with OAuth/OIDC remote MCP, project registry, three knowledge scopes, server-side authorization, audit receipts, backup/restore of Hub state, and read/propose profiles. Private user-global promotion follows raw-inbox -> reviewed promotion or reasoned rejection/archive and is not implicitly uploaded. | v1.0 Beta |
| Planned | POST-016 | Structured Session Recap | Deepen existing capture/compact-session behavior into Decisions, Learnings, Gotchas, open questions, Evidence, affected artifacts, and Promotion Candidates without raw transcript promotion. | v0.8.1 |
| Planned | POST-017 / OW-080-09 | Knowledge Health | Deterministically report schema/document revisions, duplicate IDs/claims, broken edges, stale Research, unresolved source drill-down, context-budget pollution, raw-inbox debt, and projection drift without an LLM or knowledge-body telemetry. | v0.8.0-v1.0 |
| Planned | POST-018 / OW-081-09 / OW-090-02 | Global Essence and Deep Retrieval | Centralize reviewed Research essences, learnings, patterns, and transferable concepts in the global Knowledge Base while retaining permission-checked expansion to exact project and Evidence revisions. | v0.8.1-v0.9.0 |
| Planned | POST-019 / OW-080-01 / OW-100-03 | Modular extension foundation | Define a managed-surface manifest and a permissioned module manifest with Core compatibility, profiles, migrations, health, cleanup, and uninstall declarations; a public plugin SDK or marketplace remains post-v1. | v0.8.0-v1.0 |
| Planned | POST-020 / OW-080-02 / OW-080-16 | External ResourceRef contract | Link text artifacts to source files through stable, media-neutral references, hashes, data class, availability, access state, and extraction provenance without storing binary blobs in canonical Owledge. | v0.8.0 |
| Planned | POST-021 / OW-080-09 / OW-100-05 / OW-100-09 | Transactional multi-surface upgrades | Classify Core/user/generated/extension-managed files and prove preflight, dry-run, checkpoint, apply, postflight health, receipt, and recovery across Standalone, user-global, and Hub surfaces. | v0.8.0-v1.0 |
| Deferred | POST-022 | Media and voice-ingestion adapters | Add file/media import and external transcription adapters over `ResourceRef` only after the text/provenance contract is stable; Owledge remains no binary warehouse. | Post-v1 |
| Deferred | POST-023 | Bounded enterprise erasure/DSAR module | Orchestrate coverage-bounded subject resolution, policy actions, connector propagation, restore guards, and receipts only after V1; PII masking may assist detection/redaction but cannot prove deletion. | Post-v1 enterprise |
| Planned | POST-010 | Hermes/OpenCode generic compatibility | Prove the generic MCP/CLI contract first; add dedicated adapters only where runtime hooks create measurable additional value. | v0.8.1+ |
| Planned | POST-011 | Marketplace certification | Claim marketplace readiness only after standards, manifests, screenshots, install flows, and review gates are complete. | Post-v0.9 |

## Shipped In v0.7.0 Pre-Release

The Release Board above is the only active roadmap table. Sections below are
historical release evidence or thematic inventories and do not assign current
work status; current FB dispositions remain in the live work register.

| Priority | Area | Outcome |
| --- | --- | --- |
| P0 | `.owledge` foundation | New quickstarts and generated kits create `.owledge/` plus `OWLEDGE.md`; contracts validate the v0.7 surface. |
| P0 | Package-first install | Docs and release workflows validate `uvx`/wheel smoke paths. |
| P0 | Read-only MCP | `tools/owledge_mcp.py` exposes entrypoint, doctor, search, context-pack, tasks, and reviews without write tools. |
| P0 | Wikilink Audit | `owledge wikilink-audit --check` validates valid, broken, and ambiguous wiki links without rewriting Markdown. |
| P0 | Native planning layers | Reviews, audiences, research, and brainstorm candidate templates are first-class `.owledge` layers. |
| P0 | Benchmark Kit Add-on | Optional deterministic CI mode and opt-in sequential Ollama local mode emit JSON/MD/HTML/SVG reports with stable metrics from real synthetic Markdown fixtures. |
| P0 | CI release gates | CI now checks v0.7 contracts, Wikilink Audit, Benchmark Kit CI, read-only MCP, and fresh `.owledge` installs. |

## Deferred After v0.7.0

This former parallel backlog is retired. Use the Release Board for release
sequencing and the live work register for FB-001 through FB-021. POST-001 is
complete; no outstanding v0.7.0 artifact cut remains.

## Historical Capability Inventory

| Priority | Area | Outcome |
| --- | --- | --- |
| P0 | Publish readiness | GitHub repo with docs, license, privacy, security, examples |
| P0 | PyPI publishing | Shipped: `owledge==0.7.0` is published and installable through `uvx owledge` |
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
| P0 | Kit version stamping | Every shipped template carries `owledge_kit_version`; `kit-manifest.json` records per-file hashes. **Shipped v0.6.1 (with fix-up).** | 
| P0 | Upgrade command | `owledge upgrade --dry-run/--apply` with safe/force-templates/manual modes; never-touch list; idempotent. **Shipped v0.6.1 (with fix-up: skills enrolled in manifest; manual mode always dry-run; git-apply-able patch).** |
| P1 | Drift detection | `doctor` reports `version-drift` + `outdated_files` + `user_edited_files`. **Shipped v0.6.1.** |
| P1 | Global-layer registry | `init-project --link-global` writes `global-link.json`; `doctor` checks the link. **Shipped v0.6.1.** |
| P1 | Dogfood-sync gate | `dogfood-sync` finalization gate + `sync-dogfood` CLI; one-way mirror templates -> internal. **Shipped v0.6.1.** |
| P1 | Concept blindspot skill | `concept-blindspot-audit` skill that stress-tests distribution, lifecycle, coherence (v0.6.1 Phase 5). **Shipped v0.6.1 (with fix-up: skill now installable + in manifest + upgradable).** |
| P1 | Session-continuity checklists | Per-phase checkboxes (implementation/QA/review done) in multi-phase plans; resume rule; gate. **Shipped v0.6.1 fix-up (FB-018).** |

## Feedback-Derived Roadmap (v0.5.x - 2026-06-23)

Collected from a structured feedback round covering integration, privacy,
planning discipline, cross-project intelligence, and publish readiness. See
`docs/feedback-round-2026-06.md` for the full ticket and `docs/roadmap-ideas-2026-06.md`
for idea log entries. This table records the original proposals and is not an
active backlog. Current state, replacement, target, and evidence are defined
only in the live work register linked above.

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
| P3 | Idea-to-project pipeline | Filter upcoming ideas (project-scoped and global-scoped), collect in priority order, and scaffold a new `OWLEDGE.md` from a promoted idea | Q10c |
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
| P1 | Cleanly defined project abstract + modes | Define 4 project modes (`poc`, `mvp`, `side`, `saas`) with intuitive definitions and per-mode planning discipline in `OWLEDGE.template.md` | Feature idea 5 (FB-017) |
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
