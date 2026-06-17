# PI Agent Workspace Adapter Plan

## Purpose

The PI Agent is an optional workspace-quality and project-intelligence adapter for Agent Memory Kit. It does not become the source of truth. It inspects project health, asks targeted questions, checks memory quality, and helps agents decide what to do next.

## Core Role

| Capability | Description |
| --- | --- |
| Workspace quality | Check structure, missing docs, stale indexes, unsafe exports, and failed validation |
| Planning sparring | Ask concise questions before major plans, refactors, or new project proposals |
| Agent oversight | Review whether worker outputs have evidence, handoffs, QA gates, and promotion candidates |
| Knowledge retrieval | Search project memory, ideas, patterns, lessons, decisions, and compiled summaries |
| Ideation bridge | Capture ideas during work and compare them against current plans |
| Engine bridge | Expose the same checks to Codex, Claude Code, PI Agents, Hermes, OpenClaw/OpenCode, and generic CLIs |

## Architecture

```text
PI Agent Adapter
  -> reads PROJECT_CONTEXT.md
  -> checks agent-memory/indexes/
  -> checks agent-memory/ideas/
  -> runs validation and workspace diagnostics
  -> asks targeted questions
  -> writes evidence/handoff/review artifacts only when asked
```

## Adapter Shape

| Component | Path |
| --- | --- |
| Global skill | `skills/pi-agent-workspace-quality/` |
| Optional plugin | `plugins/pi-agent-workspace/` |
| CLI check workflow | `python tools/owledge.py doctor --project-root .` |
| Idea capture workflow | Markdown idea card plus Python review workflow |
| Idea storage | `agent-memory/ideas/` |
| Idea template | `agent-memory/templates/idea-card-template.md` |

## Implementation Phases

| Phase | Goal | Output |
| --- | --- | --- |
| 1 | Read-only PI Agent | Skill, command, diagnostics wrapper |
| 2 | Ideation capture | `ideas/` folder, template, capture tool |
| 3 | Planning integration | Agents check ideas before new plans |
| 4 | Engine adapters | Codex/Claude/Hermes/OpenClaw/PI command examples |
| 5 | Quality gates | PI Agent blocks promotion suggestions without evidence |

## PI Agent Questions

The PI Agent should ask short, high-signal questions:

| Trigger | Question |
| --- | --- |
| Missing context | "What is the current project objective and nearest success metric?" |
| New plan | "Does an existing idea, pattern, ADR, or lesson already cover this direction?" |
| Large refactor | "Which files are in scope and what validation command proves success?" |
| Promotion candidate | "What evidence path and source hash support this memory?" |
| Shared export | "Is review and sanitization approved for every shared item?" |

## Rules

- Do not write canonical memory directly.
- Prefer read-only diagnostics.
- Write ideas as `doc_type=idea`, `status=draft`.
- Convert ideas into plans only after similarity checks.
- Keep PI Agent outputs compact and evidence-linked.
- Do not store private raw transcripts in RAG-ready memory.

## Recommended Default

Use the PI Agent as a read-only workspace guardian by default. Enable write actions only for explicit idea capture, evidence, handoff, or QA/report generation.
