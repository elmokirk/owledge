# Ideation Workflow

## Purpose

The ideation layer captures project and product ideas while agents work. It prevents good ideas from being lost and helps planners detect overlap before drafting new work.

## Storage

| Path | Purpose |
| --- | --- |
| `.owledge/ideas/` | Project-local idea cards |
| `.owledge/templates/idea-card-template.md` | Copyable idea template |
| `shared/patterns/` | Promoted cross-project patterns |
| `shared/lessons/` | Promoted shared lessons |

## Idea Lifecycle

```text
captured -> triaged -> linked -> elaborated -> accepted | rejected | promoted
```

## Planning Rule

Before creating a new plan, agents use the bounded `mvp-sparring` mode and
check:

1. `OWLEDGE.md`
2. `.owledge/indexes/memory-index.jsonl`
3. `.owledge/ideas/`
4. `.owledge/patterns/`
5. `.owledge/lessons/`
6. relevant ADRs and compiled summaries

Read metadata and indexes first. Expand only candidates that can change the
current target user, success signal, required dependency, risk, or MVP
cutline. Classify every relevant candidate as:

- required now;
- enabling dependency;
- roadmap;
- idea candidate;
- reject/defer with reason.

Stop planning once one smallest useful increment has measurable acceptance,
explicit non-goals, a first executable task, and a QA gate. Do not create
another plan variant unless the owner chooses `adjust`.

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

Accepted, sufficiently understood future scope belongs in `ROADMAP.md` or the
release backlog. Unresolved but useful material stays in `.owledge/ideas/`.
Neither route changes current scope without owner approval.

## Promotion Paths

| If Idea Becomes | Move / Promote To |
| --- | --- |
| Implementation task | `task-card` / work package |
| Architecture decision | `decisions/` ADR |
| Reusable method | `patterns/` |
| Sanitized learning | `lessons/` |
| New standalone project | new `OWLEDGE.md` in a new repo or hub entry |

## Human-Friendly Rule

Ideas should be short enough that a human can scan them. Store source links and hashes instead of long transcripts.
