# Finalization Report

## Status

The v0.5.0 finalization pass closes the Project Kit readiness gaps for the standalone Markdown-first Agent Memory Kit.

Release scope is frozen for v0.5.0. No new feature work should be added before
publishing; only documentation corrections, packaging hygiene, and release-gate
fixes are in scope.

## Implemented Fixes

| Area | Fix |
| --- | --- |
| Scanner coverage | Memory scanner now includes `ideas/` and PI Agent workspaces |
| Kit vs host diagnosis | `doctor --mode kit|host|auto` separates kit validation from host validation |
| Atomic writes | Indexes, exports, reports, compaction, retrieval eval, and HTML reports use locked/atomic writes |
| Export snapshots | RAG, LightRAG, and GraphRAG write generation folders plus `latest.json` pointers |
| Collision safety | Ideas, PI reports, and red-team reports use timestamp, PID, and random suffixes |
| Promotion hardening | Promotion checks tenant/customer/project, source status, review status, target policy, source hash, review approval, and writes an audit manifest |
| Context safety | Markdown context packs require explicit tenant scope when multiple real tenants are present |
| UX/DX | Quickstart, plugin install, and command reference now describe a GitHub-link-to-working path |
| Python-first setup | Core commands use local Python entrypoints |
| PI check safety | `pi-agent-check` is read-only by default; index generation requires `-BuildIndex` |
| Versioning | Kit version aligned to `0.5.0` |
| Generated report quality | Validation rejects disallowed control characters; PI intelligence and PI red-team report generators now preserve Markdown code ticks and concrete evidence paths |
| LightRAG snapshot safety | LightRAG export reads immutable RAG generation documents and manifests the exact RAG generation ID |
| Publish hygiene | Generated indexes, export snapshots, PI reports, red-team reports, raw sessions, tests, and local runtime state are ignored; publishing docs use selective staging instead of `git add .` |
| PI report scoring | PI intelligence counters now count real candidates before fallback text is rendered |
| Runtime docs consistency | Plugin command docs use direct Python CLI calls |
| Agentic memory architecture | Working, semantic, procedural, and episodic memory are now explicitly mapped to kit layers, production boundaries, and SoTA gaps |
| Reusable review workflow | Red-team, expert-review, scenario-simulation, persona-pack, and review-to-task templates now have a documented workflow, runtime skill, CLI wrapper, and QA-gated finalization sprint |
| Incremental indexes | Memory index builds now support optional incremental mode with manifest metadata and tombstones for deleted source records |
| Memory lifecycle | Templates and validation support retention classes, stale dates, expiry dates, review cycles, and last-review metadata |
| Read-only safety checks | Added `audit-retention`, `review-memory-conflicts`, and `scan-memory-sensitive-data` wrappers |
| Context-pack retrieval | Context packs accept an optional objective and report score breakdowns, freshness warnings, and exclusion reasons |
| Retrieval calibration | Added fixture corpus, query-file support, minimum score thresholds, and a non-empty-corpus gate |
| Project-folder-only setup | Added an explicit-manifest minimal folder generator and quickstart |
| Runtime smoke tests | Added Claude/Cowork capture fixtures plus a project-local runtime smoke wrapper |
| Final release gates | Added Python-first finalization and red-team QA flows |
| Optional Compliance Light | Added opt-in compliance-support add-on validation without adding compliance files to the default minimal kit |

## Red-Team QA Closure

| Finding | Status |
| --- | --- |
| LightRAG could read mutable latest RAG export under concurrency | Closed |
| Publish workflow could accidentally stage generated export/report artifacts | Closed |
| PI report fallback text counted as one signal | Closed |
| First-run setup doc was linked but not tracked | Closed |
| Plugin memory-doctor command hardcoded `python` in examples | Closed |
| Repeated red-team/evaluation work had templates but no executable workflow | Closed |
| Review workflow automation had path handling and threshold wording gaps | Closed |
| Full-only index rebuilds lacked deletion visibility for hub sync and RAG freshness | Closed |
| Retention/stale/conflict memory had no deterministic gate | Closed |
| Retrieval eval had no protected fixture corpus or threshold gate | Closed |
| Minimal project-only setup path was unclear and too broad | Closed |
| Runtime adapter smoke testing was not part of the final release chain | Closed |

## Final Smoke Matrix

| Scenario | Status | Evidence |
| --- | --- | --- |
| Project-folder generation | Passed | Python generator verified a lean project folder |
| macOS/Linux project-folder generation | Passed | Python generator verified a lean project folder |
| Lean default kit excludes optional surfaces | Passed | No compliance folder, no Compliance Light tools, no plugin adapter by default |
| Lean + Claude/Cowork plugin on Unix | Passed | Unix hook profile replaces `hooks.json` with shell/Python hook commands |
| Lean + Compliance Light | Passed | Opt-in project folder passed `compliance-doctor` with score 100 |
| Runtime adapter smoke | Passed | Claude/Cowork Python hook scripts create private session artifacts |

The `.sh` wrappers were not executed directly in the Windows release
environment because `bash` resolves to WSL and no Linux distribution is
installed. The underlying Python CLI paths used by those wrappers were verified
through the Python generator, local CLI checks, and runtime hook smoke tests.

## Remaining Roadmap

| Priority | Item |
| --- | --- |
| P1 | Deeper RAG readiness gate for chunking and oversized docs |
| P1 | Plugin lifecycle and permission documentation for each runtime |
| P1 | Calibrate reusable review scorecards and retrieval evals against real project outcomes |
| P2 | Compliance pack: deletion/export workflows and encrypted private vault options |
| P2 | Optional backend ownership/promotion queue while Markdown remains canonical |

## Positioning

v0.5.0 should be published as a project-ready local Agent Memory Kit. Optional
Compliance Light can be described as local compliance support with read-only
checks. It should not be marketed as a regulated Enterprise Server or complete
compliance solution.
