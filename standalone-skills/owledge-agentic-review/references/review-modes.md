# Review Modes

## Fast Local Review

Use for small docs, simple plans, or quick preflight checks.

Output: concise findings, score, verdict, next actions.

## Standard Multi-Perspective Review

Use when the user asks for red team, poweruser critique, expert review, or when the artifact affects architecture, public docs, launch, memory, or multi-agent behavior.

Process:

1. Select 3-5 personas.
2. Collect evidence.
3. Score each persona.
4. Synthesize disagreements and shared blockers.
5. Return verdict and tasks.

## Scenario Simulation

Use when behavior must be validated across realistic situations.

Recommended scenarios:

- Fresh install / new user.
- Dirty existing repo.
- Multi-agent handoff.
- Private/shared boundary.
- Long-running project growth.
- Release or public docs path.

## Deep Autonomous Review

Use only when the user requests autonomous, parallel, thread, subagent, or swarm review.

The orchestrator owns scope, reviewer assignment, synthesis, task conversion, and final verdict. Reviewers own evidence-backed findings for their assigned perspective only.

## Review-To-Tasks

Use after any review with unresolved findings. Each task must include:

- finding source
- owner or role
- change required
- acceptance criteria
- QA gate
- follow-up review condition
