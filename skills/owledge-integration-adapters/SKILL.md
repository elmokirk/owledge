---
name: owledge-integration-adapters
description: Map Superpowers, Graphify, LLM Wiki, Obsidian, custom harnesses, hooks, and runtime tools onto Owledge's Markdown-first memory contract without replacing those systems.
version: 0.1.0
---

# Owledge Integration Adapters

Use this skill when a user wants Owledge to coexist with existing power-user
systems such as Superpowers, Graphify, LLM Wiki, Obsidian, custom harnesses,
runtime hooks, Codex, Claude Code, or Hermes Agent.

## Core Rule

External systems keep their native job. Owledge supplies durable memory,
evidence, handoffs, reviews, typed edges, and generated views.

## Mapping

| System | Keep there | Put in Owledge |
| --- | --- | --- |
| Superpowers | execution method and implementation plans | evidence links, handoffs, reviews, lessons |
| Graphify | graph visualization and exploration | GraphRAG exports and typed edge source records |
| LLM Wiki / Obsidian | human notes and existing taxonomy | metadata-first indexes, mapped writes, plans, reviews |
| Custom harnesses | runtime execution and hooks | session summaries, evidence, handoffs |
| Codex / Claude / Hermes | agent execution | shared planning contract and write lanes |

## Hard Rules

- Do not rewrite external system files unless explicitly requested.
- Do not turn generated graph or vector data into canonical memory.
- Do not export private or unsanitized records to shared corpora.
- Prefer mapped folders or add-on modules over vault restructuring.

