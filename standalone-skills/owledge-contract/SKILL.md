---
name: owledge-contract
description: Apply Owledge's runtime-independent planning contract to product sparring, MVP definition, long-horizon work, implementation, recovery, review, or agent handoff. Use when an agent must persist a phased plan and checklist before implementation, protect MVP scope, create tickets or roadmap follow-ups, resume safely after interruption, or preserve durable project knowledge without the Owledge CLI or project kit.
---

# Owledge Contract

Use this as the standalone Owledge planning layer. It works without an Owledge
runtime, CLI, hooks, MCP, or project kit. Host project instructions always take
precedence.

## Non-negotiable execution rule

Before implementing any change, persist both a **plan** and its **checklist**.
This is the minimum Owledge artifact pair, including for MVP work. Do not use a
chat-only plan as permission to implement.

Read [references/artifact-contract.md](references/artifact-contract.md) before
creating, resuming, or recovering persistent artifacts. Use the host project's
existing planning location; if none exists, use `docs/owledge/plans/` and
`docs/owledge/checklists/`.

## Operating modes

1. **Sparring:** clarify the problem, constraints, alternatives, and desired
   outcome. Keep conclusions as candidates; do not implement.
2. **Plan:** define the smallest viable outcome, write the phased plan and its
   checklist, assign QA gates, and create tickets for independently executable
   work. This mode is mandatory before implementation.
3. **Execute:** work only on the active phase after its plan and checklist are
   present. Capture evidence and check the phase boxes only after its QA gate.
4. **Handoff:** write the exact next action, changed files, evidence, risks, and
   first unchecked checkbox. Do not require chat reconstruction.
5. **Recovery:** verify repository state and the active phase's evidence, then
   resume from the first unchecked checkbox. If verification fails, uncheck the
   stale item, record the failure, and repair only that phase.

## Planning contract

1. Read project instructions, current plans, decisions, evidence, and status
   before choosing scope.
2. Define the **MVP cutline**: outcome, must-have proof, explicit non-goals, and
   what makes the work useful now.
3. Put any valuable but non-essential discovery into the roadmap; do not fold it
   into the active MVP. Turn independent implementation units into tickets.
4. Persist a plan and checklist before any implementation write. Every plan has
   at least one phase; every phase has scope, deliverable, QA command/check,
   definition of done, and implementation/QA/review checkboxes.
5. Give workers bounded tickets and allowed write paths. Keep review and
   canonical promotion independent from implementation.
6. Record proof: source links, commands, tests, diffs, reviews, or reproducible
   outputs. Agent confidence is not evidence.
7. Keep candidate knowledge separate from canonical truth. Only an authorized
   owner can promote lessons, patterns, or decisions.

## MVP and roadmap gate

Ask of each discovered item: “Is it required to prove the defined MVP outcome?”

- If yes, add it as an explicit dependency or phase.
- If no, add a concise roadmap item with rationale, expected value, and trigger
  for reconsideration.
- If scope, authority, or architecture changes materially, stop and request an
  owner decision before proceeding.

## Recovery protocol

1. Read the plan, checklist, latest handoff, and only the evidence relevant to
   the active phase.
2. Inspect the working tree and rerun that phase's QA gate.
3. If the gate passes, continue at the first unchecked checkbox.
4. If it fails or evidence is missing, mark the phase blocked or uncheck the
   stale item, record the recovery finding, and repair the smallest failing unit.
5. Refresh the checklist and handoff before ending the session.

## Output

Always report: selected mode, plan/checklist paths, MVP cutline, active phase,
evidence, roadmap deferrals, risks, and exact next action. In Sparring mode,
state that no implementation has occurred. In Plan mode, state that execution
is blocked until the artifact pair is persisted.
