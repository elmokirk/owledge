# MVP Plan Example

Use this shape when an agent creates a project plan from an existing knowledge
base or codebase.

```markdown
# Example MVP Plan

## Goal

Ship the smallest useful version of the feature that proves the workflow works
for one real user.

## Non-Goals

- No dashboard.
- No multi-tenant hub.
- No automatic promotion to shared memory.

## MVP Cutline

In scope:

- Read existing source notes.
- Create one source-backed plan.
- Create one handoff and one review artifact.
- Run local QA gates.

Out of scope:

- Reorganizing the user's vault.
- Rewriting wiki links or frontmatter.
- Building an external service.

## Evidence

- `docs/superpowers/plans/example-plan.md`
- `Research.md`
- `agent-memory/indexes/memory-index.jsonl`

## Acceptance Criteria

- Existing source files remain byte-identical.
- Every planned task cites at least one source path.
- The handoff states status, decisions, unresolved questions, and next action.
- Review status is recorded before promotion or shared export.

## Next Actions

1. Create the smallest working task.
2. Run the relevant test or QA gate.
3. Write a handoff with evidence paths.
4. Ask for review before expanding scope.
```
