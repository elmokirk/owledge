---
name: agent-memory-runtime-bridge
description: Framework-agnostic workflow for Codex, Claude Code, Cowork/MCP, Hermes, OpenClaw/OpenCode, PI Agents, and generic agents to use Owledge's Markdown-first memory contract.
version: 0.1.0
---

# Agent Memory Runtime Bridge

Use this skill when an agent needs to read project memory, create a compact context pack, write evidence, produce a handoff, propose canonical memory, or prepare RAG-ready summaries.

## Core Rule

Markdown frontmatter and typed edges are the source of truth. Runtime tools, databases, MCP servers, vector stores, and dashboards are adapters only.

## Read Order

1. `USER_CONTEXT.md` when present
2. Relevant global records in `global-memory/preferences/`, `global-memory/goals/`, and `global-memory/research/`
3. `PROJECT_CONTEXT.md`
4. `agent-memory/indexes/memory-index.jsonl`
5. Relevant files in `agent-memory/compiled/`
6. Relevant files in `agent-memory/canonical/`
7. Relevant ADRs in `agent-memory/decisions/`
8. Evidence, sessions, daily notes, personal tasks or onboarding profiles only for explicit deep dives

## Write Rules

- Workers write only `agent-memory/sessions/`, `agent-memory/evidence/`, `agent-memory/handoffs/`, or task-local notes.
- Reviewers write QA/review artifacts.
- Orchestrators and memory curators propose or promote canonical, compiled, pattern, and lesson documents.
- Personal PI Agents write candidate global findings to `global-memory/coach/`, `global-memory/patterns/`, or `global-memory/ideas/` without automatic promotion.
- No agent writes shared lessons unless the content is sanitized and reviewed.
- Raw logs are not promoted to shared RAG.
- Private daily notes, personal tasks and onboarding profiles are never default shared RAG input.

## Runtime Capture

- Claude/Cowork plugin hooks may capture raw events into private session logs.
- Closing a runtime session may create a draft compiled summary.
- A memory curator must review and promote draft summaries before RAG or shared export.

## Required Output Shape

Every durable memory artifact must include:

- stable `memory_id`
- tenant/customer/project identifiers
- `doc_type`, `status`, `visibility`, `data_class`
- `semantic_title` and short `summary`
- normalized tags and pattern fields
- `edges` targeting `memory_id`s
- evidence links or source hashes
- for research: source URL, source date, retrieved date, valid-until date, version context and confidence
- for preferences: last confirmed date and confidence
- for coach reports: source memory IDs, recommendation confidence and next action

## Runtime Profiles

- Codex: use shell wrappers in `tools/` and respect AGENTS.md.
- Claude Code: use CLAUDE.md plus the same markdown contracts.
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
