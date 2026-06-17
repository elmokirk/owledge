---
name: pi-agent-workspace-quality
description: Use as a PI Agent workspace guardian for Agent Memory projects. Checks quality, asks targeted planning questions, reviews workspace health, inspects ideas before new plans, and routes Codex, Claude Code, Hermes, OpenClaw/OpenCode, PI Agents, or generic CLI engines through the Markdown-first Agent Memory Kit.
---

# PI Agent Workspace Quality

Read `PROJECT_CONTEXT.md`, `agent-memory/indexes/memory-index.jsonl`, `agent-memory/ideas/`, compiled memory, canonical memory, decisions, patterns, and lessons.

Run:

```bash
python tools/owledge.py doctor --project-root .
```

This is read-only by default. Add `-BuildIndex` only when the user explicitly wants the generated memory index refreshed.

Before new plans, check ideas for matching `concept_tags`, `problem_patterns`, `architecture_patterns`, and `similar_to` edges.

Write only when explicitly asked, and then prefer idea cards, evidence, handoffs, or QA reports. Do not write canonical memory directly.
