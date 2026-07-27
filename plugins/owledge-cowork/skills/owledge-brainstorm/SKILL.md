---
name: owledge-brainstorm
description: Bounded expert brainstorm mode for Owledge planning. Generates evidence-aware candidate options and risks without mutating canonical memory, then returns to an MVP cutline. Use when a user explicitly asks to brainstorm strategy, product direction, architecture, release planning, or research-backed project moves.
version: 0.1.0
---

# Owledge Brainstorm

## Contract

Brainstorm output is candidate work only. It may create or suggest draft artifacts under `.owledge/research/`, `.owledge/audiences/`, `.owledge/reviews/`, or `.owledge/ideas/` when the user asks for persistence, but it must not update `OWLEDGE.md`, canonical memory, task status, release notes, or docs without explicit review.

This is a bounded divergent mode. Before implementation, return to the
`mvp-sparring` mode of `owledge-long-horizon-delivery`.

## Trigger Signals

Use this skill when the user asks for:

- brainstorm mode
- idea generation
- strategic options
- product positioning
- architecture alternatives
- release planning options
- research-backed opportunity mapping
- CEO review style sparring
- office-hours style critique

## Inputs To Read

1. `OWLEDGE.md`
2. `.owledge/indexes/memory-index.jsonl` when present
3. Relevant `.owledge/plans/`, `.owledge/tasks/`, `.owledge/reviews/`, `.owledge/audiences/`, and `.owledge/research/` records
4. `README.md`, `ROADMAP.md`, and docs only when public positioning or release scope matters

## Workflow

1. Restate the decision frame in one paragraph.
2. Identify the target audience and constraints.
3. Generate three candidate options by default. Generate more only when the
   user explicitly requests wider exploration.
4. For each option, score impact, effort, risk, confidence, and reversibility from 1-10.
5. Surface hidden assumptions and failure modes.
6. Recommend one primary path and one fallback path.
7. Classify non-selected value as roadmap, idea candidate, or reject/defer.
8. If persistence is useful, write a draft from `.owledge/templates/brainstorm-candidate-template.md`.
9. Hand the primary recommendation to `mvp-sparring` and stop when the user can
   choose `lock`, `adjust`, or `defer`.

## Output Shape

Use this structure:

```markdown
## Frame

## Options

| Option | Impact | Effort | Risk | Confidence | Reversibility | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |

## Blindspots

## Recommendation

## Candidate Artifacts
```

## Rules

- Do not treat brainstorm candidates as decisions.
- Prefer fewer high-quality options over broad lists.
- Do not continue option generation after the decision frame is sufficiently
  covered.
- Mark unsupported claims as assumptions.
- Cite memory records or local files when they materially influence the recommendation.
- Preserve contradictions instead of resolving them silently.
