---
name: owledge-agentic-review
description: Evidence-linked review orchestration for red teaming, expert review, persona challenge, scenario simulation, scorecards, review gates, promotion readiness, autonomous reviewer workflows, subagent review, and turning findings into executable tasks. Use when a user asks to review or red-team a plan, PR, architecture, README/docs, memory/knowledgebase, release, agent workflow, or multi-agent implementation.
---

# Agentic Review

## Core Rule

Run reviews as evidence-linked engineering workflows, not as opinion prompts. Prefer project-local `REVIEW.md` for review policy; if missing, read `RED-TEAM.md`; if both exist, `REVIEW.md` is primary and `RED-TEAM.md` is a specialized addendum.

Owledge templates, CLIs, memory IDs, and review folders are optional accelerators. This skill must still work in a plain repo with only Markdown.

## Discovery

1. Identify the review subject: path, diff, PR, architecture, plan, release, memory candidate, workflow, or explicit user goal.
2. Read project review policy in this order when present: `REVIEW.md`, then `RED-TEAM.md`.
3. If the repo has Owledge tools/templates, use them only when they fit the task. Otherwise produce a self-contained Markdown review.
4. Collect evidence before scoring: source paths, line numbers, commands, logs, screenshots, hashes, memory IDs, or clearly marked assumptions.

## Mode Selection

Use the lightest mode that answers the user's decision.

- **Fast local review**: one agent, compact findings, no delegation.
- **Standard multi-perspective review**: 3-5 personas, independent findings, synthesis, score, verdict.
- **Deep autonomous review**: use subagents or background threads only when the user asks for autonomous, parallel, swarm, subagent, or thread-based review.
- **Review-to-tasks**: convert accepted findings into work items with acceptance criteria and QA gates.

Load `references/review-modes.md` when the mode choice is unclear or the user asks for a specific review type. Load `references/personas.md` when persona selection matters. Load `references/subagent-orchestration.md` before spawning or coordinating review agents.

## Autonomous Review Protocol

When delegation is authorized, keep review agents scoped and mostly read-only.

1. Spawn one reviewer per perspective or artifact slice.
2. Give each reviewer one question, one scope, required evidence format, and a clear no-mutation instruction unless fixes are explicitly requested.
3. Do not duplicate review scopes across agents.
4. Let reviewers disagree; synthesize instead of forcing consensus.
5. Use at most one follow-up round for contradictions, missing evidence, or unclear severity.
6. Convert fixes into explicit tasks only after synthesis.

If thread-spawning tools are available and the user requested autonomous/background review, use them for independent reviewer threads. If subagent tools are available, use subagents for bounded review lenses. Otherwise run the same protocol locally and state that no separate agent was spawned.

## Output Contract

Every review response or artifact must include:

- Subject and review question.
- Personas or expert lenses used.
- Evidence reviewed, including paths or commands where possible.
- Findings ordered by severity: P0, P1, P2, P3.
- Score from 1-100 and verdict: `block`, `revise`, `accept`, or `promote-candidate`.
- Concrete fixes or tasks with acceptance criteria.
- Residual risks and follow-up QA.

Promotion boundary: `promote-candidate` is never automatic approval. Canonical memory, shared exports, release publication, or main-branch merge still require owner or curator approval.

## Verdict Scale

- `block`: 0-69, or any P0/security/privacy/safety issue.
- `revise`: 70-84, material issues must be fixed and reviewed again.
- `accept`: 85-94, acceptable for the reviewed scope with documented residual risk.
- `promote-candidate`: 95-100, strong candidate but still needs explicit approval.

## Owledge Compatibility

When available, prefer Owledge's existing command for draft artifacts:

```bash
python tools/owledge_core.py --project-root . run-review-workflow --review-type multi-perspective-red-team --subject path/to/artifact.md --question "What should this review decide?"
```

If unavailable, preserve the same concepts manually: review subject, personas, evidence, scores, verdict, tasks, and promotion boundary.
