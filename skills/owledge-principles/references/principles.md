# Owledge Principles

## Canonical Principles

- Markdown is durable truth; tools, vector databases, dashboards, and RAG exports are adapters.
- Existing knowledgebase structure is respected. Agents adapt to the vault instead of forcing a taxonomy.
- Ideas are captured cheaply, then refined into MVP-oriented plans only when action is likely.
- Plans cite source notes, evidence paths, hashes, or explicit assumptions.
- Multi-agent work is coordinated through task-scoped context, evidence, reviews, and handoffs.
- Long raw transcripts are working memory, not shared knowledge.
- Stable knowledge is promoted only after review and sanitization.
- Contradictions are preserved as explicit review items; agents do not silently overwrite history.

## MVP Planning Standard

Every project plan should state:

- user or business outcome
- smallest useful MVP
- included and excluded scope
- source notes or assumptions
- tasks and owners/agents
- evidence required for done
- review and QA gates
- handoff location for the next agent/session

## Knowledge Types

| Type | Purpose | Default Handling |
| --- | --- | --- |
| Idea | Capture opportunity or project seed | Draft, low-friction, not automatically planned |
| Plan | Turn idea/context into execution | MVP-first, source-backed |
| Evidence | Preserve proof, source, result, command, or decision basis | Cited by plans/reviews |
| Handoff | Transfer state between agents/sessions | Short, actionable, source-linked |
| Review | Challenge plan/output before promotion | Required for shared/canonical use |
| Canonical memory | Durable truth | Curated and approved only |
