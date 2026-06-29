# Subagent Orchestration

Use this reference before spawning subagents or background threads for review.

## Delegation Rules

- Spawn review agents only when the user asks for autonomous, parallel, swarm, subagent, or thread-based review.
- Prefer one reviewer per perspective or artifact slice.
- Reviewers are read-only unless the user explicitly asks for fixes.
- Assign disjoint scopes to avoid duplicate work and conflicting edits.
- Do not let reviewers promote memory, merge branches, publish releases, or rewrite canonical docs.

## Reviewer Prompt Shape

Give each reviewer:

- review subject and exact scope
- one persona or expert lens
- project `REVIEW.md` / `RED-TEAM.md` policy if relevant
- required evidence format
- severity scale P0-P3
- score and verdict scale
- no-mutation instruction unless fixes are requested

Example:

```text
Use $agentic-review to review SUBJECT from the Security / Privacy perspective only. Read project REVIEW.md if present. Do not edit files. Return P0-P3 findings with file/line evidence, score, verdict, and required fixes.
```

## Synthesis Rules

The orchestrator must:

- deduplicate findings by root cause
- preserve meaningful disagreement
- escalate any P0 as a blocking verdict
- mark unsupported claims as assumptions or discard them
- convert accepted findings into tasks only after synthesis
- state which agents or threads contributed

## Follow-Up Round

Use at most one follow-up round, and only for:

- contradictory findings
- missing evidence for a serious claim
- unclear severity
- an omitted required perspective

If evidence remains missing, keep the risk as unresolved rather than inventing certainty.
