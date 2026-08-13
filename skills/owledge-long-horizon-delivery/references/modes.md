# Long-Horizon Delivery Mode Contracts

## Contents

1. MVP Sparring
2. Version Steering
3. Ticket Execution
4. Gate Review
5. Recovery
6. Artifact Routing

## Goal-host harness evidence

When execution already occurs inside a Codex desktop Goal thread, that active
thread is the primary Codex `/goal` harness. Record its thread identity and
owner-visible transcript as evidence; do not recursively start Codex CLI only
to prove that Codex is running. A CLI `exec resume` receipt is supplemental
portable-contract evidence, not a replacement for the host Goal thread.

## MVP Sparring

### Purpose

Turn broad intent into one smallest useful, testable increment without losing
future ideas.

### Read Order

1. Host instructions and `OWLEDGE.md`.
2. Active plan, task, run state, and roadmap.
3. Metadata/index entries for relevant `.owledge/ideas/`,
   `.owledge/pi-agent/concepts/`, decisions, patterns, and lessons.
4. Full source artifacts only for candidates that can change the cutline.

### Question Budget

Ask at most three concise questions per decision round. Ask only when the
answer can change target user, outcome, acceptance, required dependency,
authority, or risk. Recommend a safe default with every question.

Do not ask preference questions that can be resolved by an existing decision,
local convention, or reversible implementation choice.

### Candidate Classification

| Class | Meaning | Route |
| --- | --- | --- |
| Required now | Without it the user outcome or acceptance cannot work. | MVP scope |
| Enabling dependency | Smallest technical prerequisite for required scope. | MVP dependency |
| Roadmap | Valuable and sufficiently understood, but not required now. | Existing backlog or `ROADMAP.md` |
| Idea candidate | Promising but unresolved, weakly evidenced, or cross-project. | `.owledge/ideas/` |
| Reject/defer | Low value, unsafe, contradictory, or intentionally postponed. | Decision/rejection record |

### MVP Lock Card

Produce:

- target user;
- problem and smallest useful outcome;
- one observable success signal;
- in-scope work;
- explicit non-goals;
- required dependencies only;
- first executable task;
- QA/promotion gate;
- roadmap and idea captures;
- remaining blockers or `None`.

### Completion Test

Stop planning when:

- one user-visible outcome is stable;
- acceptance is measurable;
- non-goals prevent obvious scope expansion;
- required dependencies are known;
- the first task is ready;
- every material risk is accepted or has a decision request;
- future ideas have a durable route.

Present `lock`, `adjust`, or `defer`. Do not generate another plan variant
unless the user chooses `adjust`.

## Version Steering

### During the Version

Append:

- questions to `alignment.open_questions`;
- problems, gaps, deviations, regressions, and risks to
  `alignment.findings`;
- decisions made or requested to `alignment.decisions`.

Use stable version-scoped IDs and include source, evidence, impact,
recommendation, safe default, authority, and status.

### At the Version Gate

Create the version update with:

1. Feature Update
2. User Benefits and Adoption Impact
3. Gate and Evidence Summary
4. Implementation Findings: Problems, Gaps, and Deviations
5. Decision Log
6. Compatibility, Migration, and Operations
7. Known Limitations and Deferred Work
8. Next-Version Plan Reflection
9. Questions and Decisions Required
10. Recommendation and Safe Default
11. Recorded User Decision

Reflect affected next-version tickets/gates as `keep`, `amend`, `defer`, or
`drop`. Stop for `approve`, `adjust`, or `defer`.

## Ticket Execution

1. Read run state, backlog row, active/ready ticket, gate, and referenced
   decisions.
2. Resume an in-progress checkpoint; otherwise select one dependency-ready
   ticket.
3. Record `in_progress` before implementation.
4. Stay inside allowed paths.
5. Run positive and negative checks.
6. Capture command, exit code, environment, changed files, and evidence.
7. Prepare independent QA handoff.
8. Stop when the ticket is ready for QA or blocked.

WIP is one ticket per agent unless the accepted control plane explicitly
authorizes isolated lanes.

## Gate Review

Verify:

- every included ticket is done;
- evidence manifests match the tested workspace/commit;
- cumulative positive, negative, security, recovery, and regression checks;
- known limitations and waivers;
- independence of QA where required.

Pass only on evidence. A failed gate creates a finding and the smallest
corrective ticket; never lower a threshold silently.

## Recovery

Read:

1. the bounded `resume-context-v1` capsule (session slice plus control-document hashes);
2. the active ticket/checkpoint and its compact backlog row;
3. the current gate section and directly referenced decisions/evidence;
4. the latest handoff: read it mandatorily for a baseline-reset runtime; for a
   persisted runtime verify its in-context hash first and do not re-read it
   when already retained;
5. a capped gate-result summary; reconstruct its sidecar only when triage
   requires the full payload.

For persisted runtimes, control documents already retained in context are
hash-verified and skipped. For baseline-reset runtimes, apply the hash delta
after the mandatory handoff read. Never load the full backlog, ticket catalog,
or gate catalog merely to resume one active ticket.

A valid recovery checkpoint includes last completed atomic action, changed
files, passed/failed commands with exit codes, workspace state, next exact
command, assumptions, blockers, and prohibited shortcuts.

Resume from the first unchecked or failed item. Do not restart completed work.

## Artifact Routing

| Material | Durable destination |
| --- | --- |
| Active MVP plan | `.owledge/plans/` |
| Executable work | `.owledge/tasks/` or `.owledge/workpackages/` |
| Accepted future work | `ROADMAP.md` or release backlog |
| Unresolved useful concept | `.owledge/ideas/` |
| Cross-project concept candidate | `.owledge/pi-agent/concepts/` |
| Architecture choice | `.owledge/decisions/` |
| Verification | `.owledge/evidence/` and gate report |
| Session transition | `.owledge/handoffs/` |

Candidate artifacts never become canonical solely because a skill created
them.
