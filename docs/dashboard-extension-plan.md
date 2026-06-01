# Dashboard Extension Plan

Date: 2026-05-16  
Status: planned P4 add-on  
Scope: optional visual interface for Agent Memory operations, retrieval, PI intelligence, logs, QA, and reports.

## Positioning

The dashboard is a later add-on. It must not block the Markdown-first v0.4.0 release and must never become the source of truth.

```text
Markdown remains canonical.
Indexes and exports are generated views.
The dashboard reads generated views first.
Write actions require explicit review and promotion workflows.
```

## Why This Exists

Obsidian is strong for vault navigation, manual editing, links, and human curation. It is weak for live operational views, retrieval evaluation, PI Agent intelligence, QA status, export freshness, and multi-project observability.

The dashboard should therefore become the operations and retrieval layer, while Obsidian remains the knowledge-editing layer.

## Recommended Architecture

| Layer | Role | Source |
| --- | --- | --- |
| Markdown vault | Canonical memory and reviewed truth | `PROJECT_CONTEXT.md`, `agent-memory/` |
| Generated indexes | Fast UI and filtering input | `agent-memory/indexes/*.jsonl` |
| RAG exports | Retrieval corpus and ingestion state | `agent-memory/exports/rag/`, `lightrag/`, `graphrag/` |
| PI workspace | Intelligence reports and scorecards | `agent-memory/pi-agent/` |
| HTML reports | Generated human-facing report artifacts | `agent-memory/reports/html/` |
| Dashboard | Read-only visual interface first; write workflows later | Generated views plus optional adapter |

## Non-Goals For First Version

| Non-Goal | Reason |
| --- | --- |
| Replacing Obsidian | Obsidian remains better for editing and vault-level navigation |
| Becoming canonical storage | Would break the Markdown-first architecture |
| Editing canonical memory directly | Promotion must remain reviewed and auditable |
| Building enterprise RBAC first | That belongs to a later hub/backend phase |
| Streaming every raw hook event by default | Raw logs are private and retention-sensitive |

## P4 Phases

### P4.0: Read-Only Local Dashboard

Goal: provide immediate visibility without adding security or consistency risk.

| Feature | Description |
| --- | --- |
| Project selector | Choose tenant, customer, project, and corpus scope |
| Memory health | Show doctor score, validation status, missing files, stale indexes |
| Export freshness | Show latest RAG, LightRAG, GraphRAG generation IDs and hashes |
| PI intelligence view | Show latest parallels, trends, recurring errors, central project candidates |
| Red-team scores | Show PI Red Team scores, verdicts, blockers, and recommendations |
| HTML report launcher | Open or generate existing report types |
| Source links | Every card links back to Markdown source paths and hashes |

Acceptance:

- Dashboard can run without a backend server.
- It reads only local generated files and Markdown metadata.
- It does not write canonical memory.
- It clearly marks stale or missing generated views.

### P4.1: Retrieval Console

Goal: ask short questions against project memory, PI libraries, lessons, and patterns.

| Feature | Description |
| --- | --- |
| Retrieval box | Ask focused questions against selected scope |
| Corpus selector | Project, customer, tenant, shared, PI-only, lessons-only |
| Evidence-first answers | Answers show source memory IDs, paths, hashes, and confidence |
| Retrieval trace | Show which documents/chunks/nodes were used |
| Query presets | Decisions, blockers, repeated errors, similar projects, reusable lessons |
| Eval capture | Save retrieval quality notes as evaluation artifacts |

Acceptance:

- Retrieval never uses raw sessions by default.
- Shared retrieval excludes private/confidential/personal/unsanitized records.
- Every answer contains source references.
- Low-confidence or no-source answers are visibly marked.

### P4.2: Graph And Parallel Discovery UI

Goal: make cross-project similarities and memory graph structure inspectable.

| Feature | Description |
| --- | --- |
| Graph view | Render memory nodes and typed frontmatter edges |
| Parallel candidates | Show deterministic and semantic candidate matches |
| Contradiction lane | Preserve and highlight `contradicts` edges |
| Pattern promotion queue | Show candidates that could become patterns or lessons |
| Filter controls | Filter by tags, failure modes, architecture patterns, confidence, status |

Acceptance:

- No inferred edge is promoted automatically.
- Candidate parallels remain drafts until curated.
- Node IDs remain stable across path changes.

### P4.3: Review And Promotion Queue

Goal: introduce limited write workflows after read-only views are stable.

| Feature | Description |
| --- | --- |
| Draft summary queue | Review generated compiled/session summaries |
| Promotion approval | Approve, reject, or request changes with evidence |
| Diff preview | Show source, target, metadata, source hash, and target path |
| Gate checklist | Require review status, sanitization, data class, and source hash checks |
| Audit manifest | Write promotion evidence via existing promotion tooling |

Acceptance:

- Dashboard writes only through existing CLI/API promotion workflows.
- Direct canonical edits are not available.
- Every mutation leaves an audit artifact.
- Multi-tenant actions require explicit tenant/customer/project scope.

### P4.4: Agent Operations View

Goal: make multi-agent work observable without turning raw logs into default memory.

| Feature | Description |
| --- | --- |
| Session timeline | Show private sessions, summaries, event counts, compaction state |
| Agent activity | Show latest runs by runtime, role, status, and project |
| Failure monitor | Surface hook failures, tool failures, stale sessions, repeated errors |
| Context-pack metrics | Show included chars, compression ratio, dropped sources |
| Runtime adapters | Show Claude/Cowork, Codex, Hermes, OpenClaw/OpenCode, PI Agent status |

Acceptance:

- Raw logs are hidden by default.
- Raw session access is private and scoped.
- The UI summarizes high-frequency logs instead of embedding them into shared retrieval.

### P4.5: Enterprise Hub Dashboard

Goal: support agency-scale overview after compliance and access controls exist.

| Feature | Description |
| --- | --- |
| Tenant/customer map | Hub-level overview across hundreds of projects |
| Shared corpus monitor | Show approved shared lessons and patterns |
| Compliance status | Show retention, DSAR, provider registry, DPIA, AI inventory readiness |
| Role-aware views | PM, developer, QA, curator, owner, customer-safe modes |
| Audit and export packs | Produce customer-safe reports and evidence packs |

Acceptance:

- Requires compliance pack and scoped access model.
- No cross-tenant visibility without explicit authorization.
- Customer-safe views only show sanitized approved artifacts.

## Suggested UI Structure

```text
Dashboard Shell
├─ Project / Tenant Switcher
├─ Memory Health
├─ Retrieval Console
├─ PI Intelligence
├─ QA / Red Team Scores
├─ Graph / Parallels
├─ Promotion Queue
├─ Agent Activity
├─ Reports
└─ Compliance / Audit
```

## MVP Screen Sketch

| Region | Content |
| --- | --- |
| Top bar | Project selector, corpus selector, freshness indicator |
| Left navigation | Health, Retrieval, PI, Graph, QA, Reports, Settings |
| Main panel | Current selected view |
| Right inspector | Source paths, hashes, related memories, actions |
| Bottom status | Last index build, last export, validation score |

## Data Contracts

The dashboard should consume these files before any backend exists:

| Input | Purpose |
| --- | --- |
| `agent-memory/indexes/memory-index.jsonl` | Search, filters, status, doc metadata |
| `agent-memory/exports/rag/latest.json` | RAG corpus freshness |
| `agent-memory/exports/lightrag/manifest.json` | LightRAG ingestion contract |
| `agent-memory/exports/graphrag/latest.json` | Graph node/edge freshness |
| `agent-memory/pi-agent/reports/*.md` | PI intelligence |
| `agent-memory/pi-agent/red-team/*.md` | Red-team evaluations |
| `agent-memory/pi-agent/scorecards/*.md` | Quality scoring |
| `agent-memory/reports/html/*.html` | Existing visual reports |
| `DESIGN.md` | Dashboard/report theme selection |

## Retrieval Requirements

| Requirement | Rule |
| --- | --- |
| Source-backed answers | Every answer must cite memory IDs and paths |
| Scope-aware queries | Tenant/customer/project/corpus scope is mandatory in hub mode |
| Private by default | Raw sessions are excluded unless deep-dive mode is explicit |
| Shared-safe mode | Requires `visibility=shared`, `review_status=approved`, `sanitization_status=approved` |
| Traceable retrieval | Store optional eval notes, query, selected sources, and answer quality |
| No silent hallucination | If sources are weak, the UI must say so |

## Technology Options

| Option | Fit | Notes |
| --- | --- | --- |
| Static HTML + local JSON | Best first step | Zero backend, reads generated artifacts |
| Tauri desktop app | Strong local UX | Good for vault browsing and local filesystem access |
| Next.js local dashboard | Strong web UX | Useful once API/MCP exists |
| Obsidian plugin | Good editor integration | Better for vault-native users, weaker for agent operations |
| MCP-backed UI | Strong future path | Needs secure access model first |

Recommended sequence:

1. Static/local read-only dashboard.
2. Optional Tauri or local web app.
3. MCP/backend integration after compliance and access controls.

## Risks

| Risk | Mitigation |
| --- | --- |
| Dashboard becomes second source of truth | Read generated views first; write only via existing promotion commands |
| Sensitive logs become too visible | Private scope defaults, redaction, raw-log opt-in, retention gates |
| Retrieval gives confident wrong answers | Source citations, confidence display, no-source warnings, eval capture |
| UI encourages premature promotion | Gate checklist, diff preview, curator-only actions |
| Enterprise scope arrives too early | Keep P4.5 blocked by compliance and access-control milestones |

## Definition Of Done

The dashboard add-on is ready when:

- It can run against a bootstrapped project without changing files.
- It shows health, PI reports, red-team scores, export freshness, and source links.
- Retrieval answers include sources, scopes, and confidence.
- Shared mode cannot expose private, confidential, personal, unreviewed, or unsanitized records.
- Promotion actions, if enabled, use existing promotion tooling and write audit evidence.
- Obsidian remains optional but compatible.
- Markdown remains canonical.

