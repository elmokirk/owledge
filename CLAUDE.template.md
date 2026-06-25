---
title: "Agent Operating Notes Template"
date: "YYYY-MM-DD"
version: "1.0.0"
owledge_kit_version: "0.6.1"
status: "template"
owner: "OWNER"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project: "PROJECT_NAME"
project_id: "PROJECT_ID"
type: "template"
session_id: "YYYY-MM-DD-short-task-title"
agent_id: "orchestrator"
parent_session: ""
related_files:
  - "PROJECT_CONTEXT.md"
tags:
  - agents
  - runtime-instructions
---

# Agent Operating Notes

This file is intentionally mirrored with the sibling runtime instruction file. Keep `AGENTS.md` and `CLAUDE.md` in sync.

## Start Here

1. Read `USER_CONTEXT.md` when present for private user preferences, goals, and agent collaboration defaults.
2. Read `PROJECT_CONTEXT.md` before starting substantial project work.
3. Check `global-memory/preferences/`, `global-memory/goals/`, and `global-memory/research/` when planning or personal context matters.
4. Check `agent-memory/README.md` for the multi-agent documentation workflow.
5. Check active local plans in `agent-plans/` if the task references planning, architecture, or handoff context.
6. Check `agent-memory/ideas/` and `global-memory/ideas/` before drafting new plans or proposing new projects.
7. Use `agent-memory/pi-agent/` reports when the task asks about trends, parallels, recurring errors, or central project candidates.
8. Use `agent-memory/pi-agent/red-team/` scorecards when PI findings or agent outputs need quality challenge.
9. Use `README.md` and `docs/` for user-facing setup details.

## Memory Layers

| Layer | Path | Tracked | Purpose |
| --- | --- | --- | --- |
| Global user context | `USER_CONTEXT.md` | No by default | Private user profile, preferences, goals, and agent collaboration defaults |
| Global user memory | `global-memory/` | No by default | Private preferences, goals, daily notes, tasks, ideas, research, patterns, and coach reports |
| Canonical project router | `PROJECT_CONTEXT.md` | Yes | Current vision, state, architecture, plans, decisions, and next actions |
| Stable agent memory | `agent-memory/` | Yes | Session summaries, ADRs, templates, and reusable workflow documentation |
| Idea memory | `agent-memory/ideas/` | Yes | Captured ideas and future project opportunities |
| PI intelligence | `agent-memory/pi-agent/` | Yes | Candidate reports, parallels, trends, recurring errors, and central project concepts |
| PI red team | `agent-memory/pi-agent/red-team/` | Yes | Scorecards and challenge reports for PI findings |
| Local working plans | `agent-plans/` | No | Volatile task plans and scratch planning notes |
| User-facing docs | `README.md`, `docs/` | Yes | Setup, operations, release, and deployment guides |

## Multi-Agent Session Rules

- One writer per file.
- Subagents never edit canonical docs.
- Orchestrators own deltas.
- Reviewers own reviews.
- Stable findings are promoted only after review.

## Markdown Memory Rules

- Treat Markdown frontmatter and typed edges as the durable source of truth.
- Use stable `memory_id` values for links, graph edges, and RAG ids.
- Read `USER_CONTEXT.md`, relevant global preferences/goals/research, `PROJECT_CONTEXT.md`, then `agent-memory/indexes/memory-index.jsonl`, then relevant compiled/canonical docs.
- Workers write only sessions, evidence, handoffs, and task notes.
- Ideas are captured in `agent-memory/ideas/` as drafts and checked before new plans.
- Global ideas, preferences, goals, daily notes, tasks, research and coach reports live under `global-memory/` and remain private by default.
- Daily notes, personal tasks, and onboarding profiles are deep-dive sources only and are not default RAG input.
- Research cards must include source URL, source date, retrieval date, version context, valid-until date, and confidence.
- Coach recommendations must cite source memory IDs and include a next action.
- PI Agent findings are candidate intelligence in `agent-memory/pi-agent/` and require review before promotion.
- PI Red Team evaluations score outputs from 1-100 and classify them as `block`, `revise`, `accept`, or `promote-candidate`.
- Orchestrators and memory curators own promotion into canonical, compiled, patterns, and lessons.
- Attach evidence and gate reports before requesting promotion.
- Do not mark work `done` unless the required QA gates pass.
- Build a task-specific context pack instead of pasting long transcripts.
- Do not export raw sessions to shared RAG by default.
- Preserve contradictions through `contradicts` edges instead of overwriting history.
- Do not read, claim, export, or promote artifacts from another `tenant_id` unless `shared_scope` explicitly allows it.

## Optional Runtime Adapters

SQLite, HTTP, MCP, or runtime plugins may coordinate work, but they must not become the canonical memory store. Generated indexes and RAG exports can always be rebuilt from Markdown.

The optional `plugins/agent-memory-cowork/` adapter can capture Claude/Cowork runtime events into private sessions and draft summaries. Treat those drafts as unreviewed until a memory curator promotes them.

The optional `plugins/pi-agent-workspace/` adapter can run workspace checks and PI intelligence reports. Treat generated PI reports as review inputs, not accepted memory.
The optional Red Team PI Agent challenges PI reports and agent outputs before promotion decisions.

## Global User Context

When the private user layer is enabled, `OWLEDGE_GLOBAL_HOME` points at the
global user-memory directory (default `~/.owledge/global`). The agent loads
preferences, goals, daily notes, and tasks from this layer at session start.
Project-local memory is the source of truth for project decisions; global user
memory must not override project decisions.
