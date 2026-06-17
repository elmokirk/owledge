---
name: pi-agent-workspace-quality
description: Use as a PI Agent workspace guardian for Owledge projects. Checks quality, asks targeted planning questions, reviews workspace health, inspects ideas before new plans, and routes Codex, Claude Code, Hermes, OpenClaw/OpenCode, PI Agents, or generic CLI engines through Owledge's Markdown-first memory contract.
---

# PI Agent Workspace Quality

Use this skill when the user asks for workspace quality, PI Agent review, planning sparring, project health, idea overlap, or a question-answering agent over the project knowledge base.

## Read Order

1. `PROJECT_CONTEXT.md`
2. `agent-memory/indexes/memory-index.jsonl`
3. `agent-memory/ideas/`
4. `agent-memory/compiled/`
5. `agent-memory/canonical/`
6. `agent-memory/decisions/`
7. `agent-memory/patterns/` and `agent-memory/lessons/`

## Default Check

Run:

```bash
python tools/owledge.py doctor --project-root .
```

This is read-only by default. Add `-BuildIndex` only when the user explicitly wants the generated memory index refreshed.

Then answer with:

- workspace health
- missing context
- relevant ideas
- relevant decisions/patterns/lessons
- risks
- next best action

## Ideation Rule

Before a new plan, inspect `agent-memory/ideas/` for matching `concept_tags`, `problem_patterns`, `architecture_patterns`, and `similar_to` edges.

When the user captures a new idea, use:

```bash
python tools/agent_memory_cli.py --project-root . run-review-workflow --review-type review-to-task-plan --subject agent-memory/ideas --question "Idea title: Short summary"
```

## Write Rules

- Read-only by default.
- Write only idea cards, evidence, handoffs, QA reports, or explicit review artifacts.
- Do not write canonical memory directly.
- Do not promote ideas without review.
- Keep answers short and question-driven.

## Engine Bridge

| Engine | Use |
| --- | --- |
| Codex | Run shell tools and update project-local memory |
| Claude Code | Use plugin command/skill and ask targeted questions |
| Hermes | Map questions to context packs and evidence reads |
| OpenClaw/OpenCode | Use generic CLI commands |
| PI Agents | Use this skill as the policy and Owledge doctor/review workflows as diagnostics |

## Done Criteria

The user gets a clear answer, a workspace quality state, matching ideas if any, and the next action without reading raw logs.
