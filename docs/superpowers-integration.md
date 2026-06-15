# Owledge Kit And Superpowers

## Positioning

`obra/superpowers` is a strong execution methodology for coding agents. It
focuses on brainstorming, implementation plans, TDD, debugging, review loops,
branch finishing, and subagent-driven development.

Owledge Kit is the complementary persistent memory layer. It keeps plans,
evidence, reviews, handoffs, session continuity, and project knowledge durable
inside Markdown projects, Obsidian vaults, LLM wikis, or mapped knowledgebase
folders.

## Comparison

| Area | Superpowers | Owledge Kit |
| --- | --- | --- |
| Primary job | Execute software work through agent workflows | Preserve project knowledge and planning context |
| Core unit | Skill-driven development process | Markdown memory, evidence, handoffs, reviews |
| Planning | Detailed implementation plans and task steps | MVP plans, evidence-backed planning, durable project continuity |
| Subagents | Fresh subagent per task plus review loops | Role boundaries, handoff records, evidence summaries |
| Storage | Plans usually under `docs/superpowers/plans/` | Project-local Markdown memory or existing KB folders |
| Existing KBs | Not the main focus | Drop-in Markdown/Obsidian/LLM-wiki integration |
| Canonical truth | Workflow artifacts | Markdown source-of-truth records |

Use Superpowers to execute. Use Owledge Kit to remember, audit, hand off,
and keep project knowledge durable.

## Recommended Combined Flow

1. Use Superpowers to brainstorm, write implementation plans, run TDD, dispatch
   subagents, and finish branches.
2. Let Owledge Kit scan Superpowers plans read-only, especially
   `docs/superpowers/plans/*.md`.
3. Write Owledge evidence, reviews, handoffs, decisions, and MVP follow-up
   plans in `agent-memory-module/`, project `agent-memory/`, or mapped KB
   folders.
4. Do not rewrite Superpowers artifacts unless the user explicitly asks.
5. Promote only reviewed and sanitized Agent Memory records to shared exports.

## Agent Instruction

```text
Use Superpowers for coding execution workflows.
Use Owledge Kit as the durable Markdown memory layer.

When you see docs/superpowers/plans/*.md:
- read them as source evidence
- do not rewrite them
- cite their paths in Owledge plans, evidence, handoffs, or reviews
- keep Owledge writes inside agent-memory-module/, project agent-memory/,
  or validated mapped folders
```

## Release Test Expectation

The Superpowers coexistence gate should verify:

- Superpowers plan files remain byte-identical.
- Owledge indexes include Superpowers plan source paths.
- Generated Owledge handoffs can cite Superpowers plans as evidence.
- Existing markdown is not rewritten.
- Mapped mode still avoids root-level module files.
