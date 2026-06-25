---
title: "PROJECT_NAME Project Context"
date: "YYYY-MM-DD"
version: "1.0.0"
owledge_kit_version: "0.6.1"
status: "active"
owner: "OWNER"
memory_id: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:project_context:project-router"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project: "PROJECT_NAME"
project_id: "PROJECT_ID"
doc_type: "project_context"
visibility: "private"
data_class: "internal"
semantic_title: "PROJECT_NAME project context router"
summary: "Project router for goals, architecture, memory locations, QA gates, and agent operating model."
concept_tags:
  - "project-context"
  - "agent-memory"
stack_tags: []
problem_patterns: []
architecture_patterns:
  - "markdown-first-memory"
failure_modes: []
reusable_lessons: []
confidence: 1.0
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "YYYY-MM-DDT00:00:00Z"
updated_at: "YYYY-MM-DDT00:00:00Z"
source_hash: ""
edges: []
type: "project-context"
session_id: "YYYY-MM-DD-short-task-title"
agent_id: "orchestrator"
parent_session: ""
related_files:
  - "AGENTS.md"
  - "CLAUDE.md"
  - "README.md"
tags:
  - project-context
---

# PROJECT_NAME Project Context

## Project Vision

Describe the product, project, or system vision.

## Current State

Describe what works today and what is verified.

## Current Tech Stack

| Component | Purpose | Why It Exists | Status |
| --- | --- | --- | --- |

## Painpoints To Solve

- Painpoint 1

## Solved Painpoints

- Solved item 1

## Target Architecture

```text
User -> System -> Result
```

## Stack Mapping

| Stack | Use When | Key Files |
| --- | --- | --- |

## Setup Routes

- Route 1

## Agent Operating Model

Describe how agents and subagents should document work.

## Tenant / Access Model

| Field | Value |
| --- | --- |
| Tenant ID | TENANT_ID |
| Customer ID | CUSTOMER_ID |
| Project ID | PROJECT_ID |
| Default Data Class | internal |
| Shared Scope | none |

## Markdown Memory Core

| Setting | Value |
| --- | --- |
| Source Of Truth | Markdown frontmatter and typed edges |
| Project Router | `PROJECT_CONTEXT.md` |
| Canonical Memory | `agent-memory/canonical/` |
| Compiled Memory | `agent-memory/compiled/` |
| Pattern Memory | `agent-memory/patterns/` |
| Shared Lessons | `agent-memory/lessons/` |
| Idea Memory | `agent-memory/ideas/` |
| PI Intelligence | `agent-memory/pi-agent/` |
| PI Red Team | `agent-memory/pi-agent/red-team/` |
| Machine Index | `agent-memory/indexes/memory-index.jsonl` |
| RAG Exports | `agent-memory/exports/` |

## QA Gates

| Gate | Required | Evidence |
| --- | --- | --- |
| Tests | Yes | Gate report |
| Build / Type Safety | Yes | Gate report |
| Security | Yes | Gate report |
| Performance | Project-specific | Gate report |
| Accessibility | UI projects | Gate report |

## Active Plans

| Plan | Status | Location |
| --- | --- | --- |

## Idea Backlog

Agents should check `agent-memory/ideas/` before drafting new plans. Related ideas should be linked through `similar_to`, `relates_to`, `derived_from`, or `shared_lesson_for` edges.

| Idea | Status | Relevance | Location |
| --- | --- | --- | --- |

## PI Agent Intelligence

PI Agent reports are candidate intelligence for parallels, trends, repeated agent errors, and central project opportunities. They help planning and memory curation, but require review before promotion.

| Artifact | Status | Signal | Location |
| --- | --- | --- | --- |

## Evaluation Frameworks

Use 1-100 scorecards for important agent outputs, PI reports, plans, QA findings, and promotion candidates.

| Framework | Target | Accept Score | Location |
| --- | --- | ---: | --- |
| PI Red Team Evaluation | PI intelligence reports | 85 | `agent-memory/pi-agent/red-team/` |

## Session Log

| Date | Session | Outcome |
| --- | --- | --- |

## Decision Log

- Decision 1

## Validation / QA Status

- QA state

## Next Best Actions

1. Next action

## Open Questions

- Question 1
