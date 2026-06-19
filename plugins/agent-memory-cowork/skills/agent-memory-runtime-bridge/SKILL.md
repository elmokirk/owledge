---
name: agent-memory-runtime-bridge
description: Use Markdown-first Agent Memory from Claude/Cowork, Codex, Hermes, OpenClaw/OpenCode, PI Agents, and generic agents.
version: 0.1.0
---

# Agent Memory Runtime Bridge

Use this skill when an agent needs to read project memory, create a compact context pack, write evidence, produce a handoff, propose canonical memory, or prepare RAG-ready summaries.

## Core Rule

Markdown frontmatter and typed edges are the source of truth. Runtime tools, databases, MCP servers, vector stores, dashboards, and plugins are adapters only.

## Read Order

1. `USER_CONTEXT.md` when present
2. Relevant global records in `global-memory/preferences/`, `global-memory/goals/`, and `global-memory/research/`
3. `PROJECT_CONTEXT.md`
4. `agent-memory/indexes/memory-index.jsonl`
5. Relevant files in `agent-memory/compiled/`
6. Relevant files in `agent-memory/canonical/`
7. Relevant ADRs in `agent-memory/decisions/`
8. Evidence, sessions, daily notes, personal tasks or onboarding profiles only for explicit deep dives

## Capture Rule

Claude/Cowork hooks may capture raw session events into private `agent-memory/sessions/` logs. Raw logs are working memory only. They must not be promoted to shared RAG directly.

## Write Rules

- Workers write only `agent-memory/sessions/`, `agent-memory/evidence/`, `agent-memory/handoffs/`, or task-local notes.
- Reviewers write QA/review artifacts.
- Orchestrators and memory curators propose or promote canonical, compiled, pattern, and lesson documents.
- Personal PI Agents write candidate global findings to `global-memory/coach/`, `global-memory/patterns/`, or `global-memory/ideas/` without automatic promotion.
- No agent writes shared lessons unless the content is sanitized and reviewed.
- Raw logs are not promoted to shared RAG.
- Private daily notes, personal tasks and onboarding profiles are never default shared RAG input.

## Required Output Shape

Every durable memory artifact must include stable `memory_id`, tenant/customer/project identifiers, `doc_type`, status, visibility, data class, semantic title, summary, normalized tags, typed edges, evidence links, and source hashes. Research needs source URL/date, retrieved date, valid-until date, version context and confidence. Preferences need last confirmed date. Coach reports need source memory IDs, recommendation confidence and next action.

## Runtime Profiles

- Claude/Cowork: use plugin hooks to capture events, then close sessions into private draft summaries.
- Codex: use the project-local Python CLI in `tools/` and respect `AGENTS.md`.
- Cowork/MCP: expose wrappers as MCP tools, but keep Markdown canonical.
- Hermes: map agent tasks to context packs and evidence writes.
- OpenClaw/OpenCode: use generic CLI profile.
- PI Agents: use generic CLI/HTTP profile and write markdown artifacts.

## Forbidden Actions

- Do not use Vector DB contents as canonical memory.
- Do not invent edges without evidence or a stated confidence.
- Do not export private, confidential, personal, or unsanitized documents to shared corpora.
- Do not overwrite contradictory history; add `contradicts` edges.
- Do not include long raw transcripts in context packs by default.
