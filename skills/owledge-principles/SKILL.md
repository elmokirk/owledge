---
name: owledge-principles
description: Principles-first Owledge workflow for existing Markdown knowledgebases, Obsidian vaults, LLM wikis, MVP planning, project memory continuity, Superpowers coexistence, multi-agent/session coordination, handoffs, evidence, reviews, and secure drop-in integration without forcing the preset folder structure.
---

# Owledge Principles

Use this skill as the first entrypoint when a user wants Owledge behavior
without adopting the full preset folder structure.

## Core Workflow

1. Discover the knowledgebase or project root.
2. Read `owledge-map.json` if it exists; otherwise use `owledge-module/` as the safe fallback.
3. Collect relevant ideas, source notes, constraints, decisions, and prior plans.
4. Convert the goal into an MVP-first plan with evidence links.
5. Assign work through handoffs and task-local context.
6. Require reviews before promotion, shared export, or central reuse.

Trigger strongly when the user mentions an existing KB, Obsidian, LLM wiki,
MVP plan, multi-agent handoff, project memory continuity, or Superpowers
coexistence.

## Read References

- Read `references/principles.md` when defining or explaining the system principles.
- Read `references/mapping-contract.md` before using or creating `owledge-map.json`.
- Read `references/agent-rules.md` before coordinating workers, reviewers, curators, or subagents.
- Read `references/security-rules.md` before scanning, indexing, writing files, exporting, or running tools.

## Hard Rules

- Do not reorganize a user's existing vault or rewrite wiki links/frontmatter unless explicitly requested.
- Do not require OS environment variables; prefer local paths, CLI args, and local map files.
- Treat generated indexes and retrieval exports as views, not canonical memory.
- Workers write plans, evidence, handoffs, task notes, and drafts only.
- Reviewers write review artifacts only.
- Curators may propose promotion; they do not auto-approve shared/canonical memory.
- Subagents receive task-local context and return handoff/evidence summaries.
- Raw logs, private notes, personal data, and unsanitized records never enter shared RAG by default.

## Default Output

Return:

- selected root and mode: mapped or module fallback
- sources consulted
- MVP plan or next action
- write locations used
- risks, missing context, and QA gates
