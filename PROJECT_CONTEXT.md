---
title: "Owledge Project Context"
date: "2026-06-23"
version: "0.6.0"
status: "active"
owner: "Kirk"
memory_id: "mem:owledge:global:owledge:project_context:project-router"
tenant_id: "owledge"
customer_id: "global"
project: "owledge"
project_id: "owledge"
doc_type: "project_context"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge global agent memory kit project router"
summary: "Project router for the Owledge kit: durable Markdown memory, runtime adapters, launch add-ons, and agent coordination surface."
concept_tags:
  - "project-context"
  - "agent-memory"
  - "markdown-first"
stack_tags:
  - "python"
  - "markdown"
  - "obsidian-compatible"
architecture_patterns:
  - "markdown-first-memory"
  - "additive-module-install"
  - "metadata-first-scan"
problem_patterns: []
failure_modes: []
reusable_lessons: []
confidence: 1.0
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-23T00:00:00Z"
updated_at: "2026-06-23T00:00:00Z"
source_hash: ""
edges: []
type: "project-context"
session_id: "20260623-bootstrap-context"
agent_id: "orchestrator"
parent_session: ""
related_files:
  - "AGENTS.md"
  - "CLAUDE.md"
  - "DESIGN.md"
  - "README.md"
  - "REVIEW.md"
tags:
  - project-context
---

# Owledge Project Context

## Project Vision

Drop-in durable project memory for existing Markdown repos and Obsidian-style vaults: no migration, no vector DB, no wiki-link rewrite. Agents get plans, evidence, handoffs, and decisions that stay readable across sessions, tools, and teams.

## Current State

- Core kit is at v0.6.0 and release-ready.
- `tools/agent_memory_cli.py` and `tools/owledge.py` provide local Python-first commands.
- 11 launch add-ons are packaged (demo, trust, conformance, PI proof, TS adapter, benchmark kits, decision trace, cross-project hub, swarm coordination, poweruser positioning, compliance light).
- Runtime adapters exist for Codex, Claude Code, Cowork-compatible, and OpenCode-style agents.
- CI passes on Windows, Linux, and macOS via platform-neutral Python gates.

## Current Tech Stack

| Component | Purpose | Status |
| --- | --- | --- |
| Python 3.10+ | CLI tools, validation, gates | Active |
| Markdown + YAML frontmatter | Canonical memory format | Active |
| JSONL indexes | Machine-readable memory indexes | Active |
| Optional TypeScript | `addons/ts-adapter-kit` for Node CI | Active |
| GitHub Actions | CI (`ci.yml`) and docs (`docs.yml`) | Active |

## Markdown Memory Core

| Layer | Location | Purpose |
| --- | --- | --- |
| Project router | `PROJECT_CONTEXT.md` | Durable project truth and next actions |
| Agent instructions | `AGENTS.md`, `CLAUDE.md` | Runtime session-start rules |
| Design system | `DESIGN.md` | Report design tokens |
| Review policy | `REVIEW.md` | Agentic review defaults and gates |
| Canonical memory | `agent-memory/canonical/` | Reviewed stable knowledge |
| Compiled memory | `agent-memory/compiled/` | Generated summaries and snapshots |
| Patterns | `agent-memory/patterns/` | Reusable architecture patterns |
| Lessons | `agent-memory/lessons/` | Cross-session shared lessons |
| PI intelligence | `agent-memory/pi-agent/` | Candidate parallels and trends |
| PI red team | `agent-memory/pi-agent/red-team/` | 1-100 scorecards |
| Machine index | `agent-memory/indexes/memory-index.jsonl` | Metadata-first scan output |
| User memory | `global-memory/` | Private goals, tasks, daily notes |

## QA Gates

| Gate | Required | Evidence |
| --- | --- | --- |
| Kit doctor | Yes | `python tools/agent_memory_cli.py --project-root . doctor --mode kit` |
| Memory validation | Yes | `python tools/agent_memory_cli.py --project-root . validate-memory --strict` |
| Public docs | Yes | `python tools/owledge.py test public-docs --project-root .` |
| Launch readiness | Yes | `python tools/owledge.py test launch-readiness --project-root .` |
| Quality ratchet | Yes | `python tools/owledge.py test quality-ratchet --project-root .` |

## Active Plans

| Plan | Status | Location |
| --- | --- | --- |
| Bootstrap completeness (PROJECT_CONTEXT.md + REVIEW.md) | In progress | This file, `REVIEW.md` |

## Decision Log

- Markdown is the canonical source of truth; indexes and HTML reports are generated views.
- Additive by default: existing vaults and repos are never rewritten on install.
- Private runtime capture and user memory must not leak into shared RAG without review.

## Validation / QA Status

- All Owledge gates pass locally.
- CI badges are green on `main`.
- No P0 blockers or privacy leaks are open.

## Next Best Actions

1. Complete bootstrap by committing `PROJECT_CONTEXT.md` and `REVIEW.md`.
2. Verify `main` fast-forwards cleanly after commit.
