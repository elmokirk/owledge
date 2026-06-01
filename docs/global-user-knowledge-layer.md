# Global User Knowledge Layer

Date: 2026-05-18  
Status: planned opt-in layer  
Scope: global personal knowledge, preferences, goals, daily work, tasks, ideas, research, patterns, coaching, and agent onboarding.

## Positioning

The Global User Knowledge Layer expands the kit beyond project memory. It gives agents a private, user-level memory that can guide planning and execution across many projects without mixing project truth or leaking personal data.

```text
USER_CONTEXT.md
-> global-memory/preferences/
-> global-memory/goals/
-> global-memory/daily/
-> global-memory/tasks/
-> global-memory/ideas/
-> global-memory/research/
-> global-memory/patterns/
-> global-memory/coach/
-> project-local agent-memory/
-> reviewed RAG / GraphRAG / LightRAG adapters
```

Markdown remains canonical. RAG, dashboards, MCP, LightRAG, GraphRAG and vector databases are consumers.

## Layer Model

| Layer | Purpose | Default Export |
| --- | --- | --- |
| Onboarding | Seed user profile, privacy defaults, tool preferences and goals | Never shared |
| Plan | Pull goals, preferences, similar ideas and project context into planning | Private only |
| Execution | Track daily focus, personal tasks, follow-ups and project handoffs | Not RAG by default |
| Pattern Detection | Detect repeated ideas, failures, preferences, goals and project opportunities | Candidate only |
| Coach | Provide sourced recommendations with confidence and next action | Private only |
| Project Memory | Keep project-local truth isolated | Existing rules |

## Folder Contract

| Path | Role |
| --- | --- |
| `USER_CONTEXT.md` | Private profile and operating defaults for agents |
| `global-memory/preferences/` | Confirmed preferences with `last_confirmed_at` |
| `global-memory/goals/` | Long-term, quarterly, project and personal goals |
| `global-memory/daily/` | Daily notes, focus, review and raw private context |
| `global-memory/tasks/` | Personal tasks, follow-ups and non-project actions |
| `global-memory/ideas/` | Cross-project ideas and product opportunities |
| `global-memory/research/` | Dated research cards with freshness and version context |
| `global-memory/patterns/` | Personal and cross-project patterns |
| `global-memory/coach/` | Coach reports and sourced recommendations |
| `global-memory/indexes/` | Generated indexes |
| `global-memory/exports/` | Generated private retrieval exports |

## Agent Read Order

1. `USER_CONTEXT.md`
2. Relevant `global-memory/preferences/`
3. Relevant `global-memory/goals/`
4. Relevant `global-memory/research/`
5. Active `PROJECT_CONTEXT.md`
6. Project `agent-memory/indexes/memory-index.jsonl`
7. Project compiled, canonical, decisions, lessons and patterns

Daily notes, personal tasks and onboarding profiles are deep-dive sources only.

## Lifecycle Rules

| Artifact | Lifecycle |
| --- | --- |
| Preference | `captured -> confirmed -> active -> stale -> updated | archived` |
| Goal | `draft -> active -> reviewed -> completed | changed | archived` |
| Idea | `captured -> clustered -> scored -> linked -> planned | archived | promoted` |
| Research | `captured -> reviewed -> valid -> stale -> rechecked | superseded` |
| Pattern | `candidate -> reviewed -> active -> promoted | archived` |
| Coach report | `draft -> reviewed -> accepted | rejected | archived` |

## Hard Rules

- Global personal records default to `visibility=private`.
- `USER_CONTEXT.md` and `global-memory/**/*.md` are ignored by default when bootstrapped into normal project repos.
- Daily notes, personal tasks and onboarding profiles are never default RAG input.
- Shared export requires explicit `visibility=shared`, `review_status=approved`, `sanitization_status=approved` and safe `data_class`.
- Research cards require `source_url`, `source_date`, `retrieved_at`, `valid_until`, `version_context` and `confidence`.
- Preferences require `last_confirmed_at`; stale preferences must be reconfirmed instead of silently reused.
- Coach reports must include `source_memory_ids`, `recommendation_confidence` and `next_action`.
- Personal PI Agent findings are candidates and never auto-promote to canonical memory.

## Personal PI Agent

The Personal PI Agent is an optional global knowledge assistant. It should:

- cluster ideas and detect duplicates
- find goal conflicts and missing next actions
- mark stale preferences and research
- generate daily or weekly review candidates
- detect repeated user-agent workflow failures
- compare new project plans against goals, preferences, ideas and prior project patterns
- produce coach reports with source memory IDs and confidence

It must not edit project canonical memory directly.

## Metrics

| Metric | Meaning | Target |
| --- | --- | --- |
| Memory Freshness | Share of active preferences/research with valid confirmation or freshness dates | 90%+ |
| Retrieval Precision | Share of answered questions with correct cited memory IDs | 85%+ |
| Idea Reuse Rate | Captured ideas later linked to plans, projects or patterns | Increasing trend |
| Project Carryover Rate | Global lessons or patterns reused in project work | Increasing trend |
| Staleness Debt | Expired research, goals and preferences needing review | Downward trend |
| Agent Context Efficiency | Relevant included chars divided by total available chars | Improve per release |
| Consistency Score | Goal/preference/project contradictions resolved or tracked | 90%+ |
| Coach Actionability Score | Coach reports with clear next action and owner | 90%+ |

## Test Plan

| Test Area | Scenario | Acceptance |
| --- | --- | --- |
| Scale | 1 user, 1,000 ideas, 365 daily notes, 200 research cards, 50 projects | Indexing completes without scope mixing |
| Maintainability | Missing IDs, missing research source fields, missing preference confirmation | Validation fails clearly |
| Performance | Indexing uses frontmatter and summaries first | Context packs stay under budget |
| Privacy | Shared export with private daily notes or personal tasks | Records are rejected |
| Quality | New plan checks goals, preferences, similar ideas and research | Relevant global sources are cited |
| Coach | Coach report without source IDs or next action | Validation fails |

## Roadmap

| Phase | Outcome |
| --- | --- |
| P1 | Structure, templates, onboarding, read order and validation |
| P2 | Global indexing, metrics and Personal PI reports |
| P3 | Coach layer and runtime integration for Hermes/OpenClaw/Codex/Claude |
| P4 | Personal cockpit/dashboard view |
| P5 | Compliance, retention, PII scanning and encrypted private vault options |

