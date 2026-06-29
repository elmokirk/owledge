---
title: "Owledge Workflow"
date: "YYYY-MM-DD"
version: "1.0.0"
owledge_kit_version: "0.7.0"
status: "active"
owner: "OWNER"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project: "PROJECT_NAME"
project_id: "PROJECT_ID"
type: "memory-readme"
session_id: "bootstrap"
agent_id: "orchestrator"
parent_session: ""
related_files:
  - "../OWLEDGE.md"
  - "../AGENTS.md"
  - "../CLAUDE.md"
tags:
  - owledge
  - multi-agent
  - control-plane
---

# Owledge Workflow

This folder stores durable agent memory. Markdown files with frontmatter and typed edges are the source of truth. Runtime databases, HTTP APIs, vector stores, and RAG systems are optional generated views or adapters.

Project memory lives here. Private user-level memory lives one layer up in `USER_CONTEXT.md` and `global-memory/` when enabled.

## Core Model

```text
Session / Evidence
  -> Review / QA
  -> Canonical / Compiled / Pattern / Lesson
  -> Index / RAG / GraphRAG exports
```

## Folder Roles

| Path | Role |
| --- | --- |
| `templates/` | Copyable specs for tasks, QA, handoffs, sessions, deltas, reviews, and ADRs |
| `schemas/` | JSON schemas consumed by harness checks and agents |
| `sessions/` | Stable session summaries, subagent sheets, deltas, and reviews |
| `decisions/` | Architecture decision records |
| `canonical/` | Reviewed project memory that should survive sessions |
| `compiled/` | Retrieval-friendly summaries for RATS/LightRAG |
| `patterns/` | Cross-project problem and solution patterns |
| `lessons/` | Sanitized reusable lessons |
| `ideas/` | Captured project ideas, opportunity drafts, and planning inputs |
| `pi-agent/` | PI Agent candidate reports, parallels, trends, recurring errors, and central project concepts |
| `pi-agent/red-team/` | QA Red Team PI Agent evaluations and challenge reports |
| `pi-agent/evaluations/` | Project/task-specific evaluation frameworks and results |
| `pi-agent/scorecards/` | 1-100 agent quality scorecards |
| `evidence/` | Human-readable evidence summaries and links |
| `handoffs/` | Agent-to-agent handoff packets |
| `indexes/` | JSONL indices built from reviewed/promoted memory |
| `exports/rag/` | Neutral RAG JSONL export |
| `exports/lightrag/` | LightRAG-ready arrays and manifest |
| `exports/graphrag/` | GraphRAG nodes and edges |
| `tmp/`, `scratch/` | Ignored scratch space |

Incremental index files, specifically `memory-index.jsonl`, `memory-index-manifest.json`, and `memory-index-tombstones.jsonl`, are generated operational metadata for freshness, QA, and hub sync. Markdown remains canonical, and tombstones do not enter shared RAG by default. See `../docs/incremental-index-workflow.md`.

## Scale Rules

- Keep Markdown artifacts compact and evidence-linked.
- Do not store raw chat transcripts in canonical memory.
- Promote only reviewed stable information.
- Preserve tenant boundaries in every artifact and export.
- Use stable `memory_id` values for relationships and RAG ids.
- Express relationships through frontmatter `edges`.
- Export shared knowledge only after sanitization approval.

## Promotion Workflow

1. Worker writes a session, evidence, or handoff artifact.
2. QA or reviewer creates a gate/review artifact.
3. Orchestrator summarizes stable deltas.
4. Memory curator promotes stable findings to canonical, compiled, patterns, or lessons.
5. Index and export tools regenerate machine-readable views.

## Ideation Workflow

Agents may capture new product, project, or implementation ideas in `.owledge/ideas/`. During planning, agents should check ideas for matching `problem_patterns`, `concept_tags`, `architecture_patterns`, and `similar_to` edges before drafting a new plan. Ideas remain drafts until reviewed; promoted ideas can become tasks, ADRs, patterns, lessons, or new project proposals.

## PI Agent Intelligence Workflow

The optional PI Agent global intelligence layer writes candidate artifacts under `.owledge/pi-agent/`. It scans frontmatter signals, idea cards, decisions, lessons, patterns, and QA reports to find parallels, trends, recurring agent errors, and central project candidates. PI Agent output is never canonical by default; a curator or owner must review it before promoting stable findings into `patterns/`, `lessons/`, `compiled/`, or `canonical/`.

```bash
python tools/owledge_core.py --project-root . run-review-workflow --review-type expert-lens --subject .owledge/pi-agent/reports --question "What intelligence should be curated?"
```

The QA Red Team PI Agent evaluates PI reports with a 1-100 scorecard. Scores below 85 require revision before the report should guide planning; scores above 95 are promotion candidates, not automatic approvals.

```bash
python tools/owledge_core.py --project-root . run-review-workflow --review-type multi-perspective-red-team --subject .owledge/pi-agent/reports --question "Evaluate PI intelligence quality."
```

## Reusable Review Templates

Repeated red-team reviews, senior expert evaluations, scenario simulations, and finalization reviews should use reusable templates in `.owledge/templates/`.

| Template | Use |
| --- | --- |
| `multi-perspective-red-team-review-template.md` | 3-5 dynamic personas challenge one artifact |
| `expert-lens-evaluation-template.md` | senior expert critique with metrics and evidence |
| `scenario-simulation-evaluation-template.md` | realistic usage simulations and stress cases |
| `evaluation-persona-pack-template.md` | reusable persona library and injection blocks |
| `review-to-task-plan-template.md` | convert findings into tasks, gates, and acceptance criteria |

See `docs/reusable-review-evaluation-templates.md` for selection rules and default metrics.

Create a draft review artifact with:

```bash
python tools/owledge_core.py --project-root . run-review-workflow --review-type expert-lens --subject docs/reusable-review-evaluation-templates.md --question "What should this review decide?"
```

The command writes candidate QA memory only. A score of 95 or above is still a promotion candidate, not automatic approval.

## Context Strategy

Agents should request or build a generated context pack per task. Context packs include user context when present, index summaries, relevant compiled/canonical docs, accepted decisions, validation commands, current blockers, and scoped evidence links. They must not copy long logs, private daily notes, personal tasks, onboarding profiles, or unrelated tenant data.

## Global User Knowledge Layer

The optional global layer stores private user preferences, goals, daily work, tasks, ideas, research, personal patterns, and coach reports outside project-specific memory. It is designed to help agents plan and execute across multiple projects while preserving project boundaries.

Default paths:

- `USER_CONTEXT.md`
- `global-memory/preferences/`
- `global-memory/goals/`
- `global-memory/daily/`
- `global-memory/tasks/`
- `global-memory/ideas/`
- `global-memory/research/`
- `global-memory/patterns/`
- `global-memory/coach/`

Daily notes, personal tasks and onboarding profiles are private deep-dive sources only. They are not default RAG input and must not enter shared exports.
