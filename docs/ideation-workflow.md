# Ideation Workflow

## Purpose

The ideation layer captures project and product ideas while agents work. It prevents good ideas from being lost and helps planners detect overlap before drafting new work.

## Storage

| Path | Purpose |
| --- | --- |
| `agent-memory/ideas/` | Project-local idea cards |
| `agent-memory/templates/idea-card-template.md` | Copyable idea template |
| `shared/patterns/` | Promoted cross-project patterns |
| `shared/lessons/` | Promoted shared lessons |

## Idea Lifecycle

```text
captured -> triaged -> linked -> elaborated -> accepted | rejected | promoted
```

## Planning Rule

Before creating a new plan, agents must check:

1. `PROJECT_CONTEXT.md`
2. `agent-memory/indexes/memory-index.jsonl`
3. `agent-memory/ideas/`
4. `agent-memory/patterns/`
5. `agent-memory/lessons/`
6. relevant ADRs and compiled summaries

The agent should look for matching:

- `concept_tags`
- `problem_patterns`
- `architecture_patterns`
- `failure_modes`
- `similar_to` edges
- `shared_lesson_for` edges

## When To Capture An Idea

| Signal | Capture |
| --- | --- |
| "This could be a product" | New idea card |
| "We should reuse this later" | Idea or pattern draft |
| "This is a new agent workflow" | Idea card with architecture pattern |
| "This customer need appears again" | Idea card with problem pattern |
| "This does not belong in current scope" | Idea card with future-project fit |

## Promotion Paths

| If Idea Becomes | Move / Promote To |
| --- | --- |
| Implementation task | `task-card` / work package |
| Architecture decision | `decisions/` ADR |
| Reusable method | `patterns/` |
| Sanitized learning | `lessons/` |
| New standalone project | new `PROJECT_CONTEXT.md` in a new repo or hub entry |

## Human-Friendly Rule

Ideas should be short enough that a human can scan them. Store source links and hashes instead of long transcripts.
