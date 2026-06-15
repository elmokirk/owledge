# Agent And Subagent Rules

## Roles

| Role | May Write | Must Not Write |
| --- | --- | --- |
| Orchestrator | MVP plans, task breakdowns, handoffs | Shared/canonical memory without review |
| Worker | Task notes, evidence, handoffs, draft outputs | Canonical memory, shared lessons |
| Reviewer | Review artifacts, QA findings, scorecards | Productive task output as if approved |
| Curator | Promotion candidates, audit notes | Automatic approval without evidence |
| Subagent | Task-local evidence and handoff summary | Central KB state, shared memory, global lessons |

## Multi-Agent Loop

1. Orchestrator creates a scoped MVP plan.
2. Workers receive task-local context, not the whole vault.
3. Workers write evidence and handoffs when done or blocked.
4. Reviewers challenge outputs against sources, risks, and acceptance criteria.
5. Curators promote only reviewed and sanitized stable knowledge.

## Handoff Requirements

Every handoff should include:

- task objective
- current status
- source paths or memory IDs used
- decisions made
- unresolved questions
- next recommended action
- files written

## Subagent Constraints

- Give subagents only the minimum context required.
- Require subagents to return source-backed summaries.
- Never allow subagents to edit existing user vault notes unless explicitly authorized.
- Never let subagents promote drafts into shared/canonical memory.
