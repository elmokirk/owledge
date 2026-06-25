# Roadmap Ideas 2026-06

Date: 2026-06-23
Status: active
Type: idea-log

## Purpose

Idea cards captured during the 2026-06 feedback round. Each idea has a
`feedback_ticket` edge linking back to `docs/feedback-round-2026-06.md`. Ideas
follow the standard lifecycle: `captured -> triaged -> linked -> elaborated ->
accepted | rejected | promoted`.

## Project-Scoped Ideas

### IDEA-2026-006-01: PyPI publishing

- concept_tags: publishing, pypi, distribution
- problem_patterns: source-checkout-friction
- architecture_patterns: python-package
- feedback_ticket: FB-001
- status: captured
- source: feedback round Q1/Q3
- summary: Publish `owledge` to PyPI so users can `pip install owledge` instead
  of cloning the repo. The refactor made the sdist clean; execute the publish.

### IDEA-2026-006-02: AGENTS.md copy-paste block

- concept_tags: integration, agents-md, copy-paste, sota
- problem_patterns: integration-friction, no-self-contained-block
- architecture_patterns: markdown-instructions
- feedback_ticket: FB-002
- status: captured
- source: feedback round Q3
- summary: Create a single self-contained paste block for `AGENTS.md`/`CLAUDE.md`
  that gives an agent all Owledge rules without the skills path. Under 60 lines.

### IDEA-2026-006-03: Tokenizer-based benchmark

- concept_tags: benchmark, token-cost, tokenizer
- problem_patterns: no-token-baseline, vague-token-claims
- architecture_patterns: benchmark-harness
- feedback_ticket: FB-003
- status: captured
- source: feedback round Q2
- summary: Add tokenizer-based token measurements to benchmarks. Compare full
  vault vs metadata scan vs context pack vs oracle scoped. Publish results.

### IDEA-2026-006-04: Folder whitelist for global scan

- concept_tags: privacy, whitelist, global, consent
- problem_patterns: no-scan-consent, global-scan-uncontrolled
- architecture_patterns: allowlist-config
- feedback_ticket: FB-004
- status: captured
- source: feedback round Q6, Q10a
- summary: Add `scan_allowlist` to `owlib.yaml` and per-project consent files.
  User controls which folders integrate Owledge and which register to owlib.

### IDEA-2026-006-05: Project abstract + mode selector

- concept_tags: project-context, abstract, project-mode
- problem_patterns: no-project-abstract, no-mode-selector
- architecture_patterns: project-context-extension
- feedback_ticket: FB-005
- status: captured
- source: feedback round Q10b
- summary: Force a one-paragraph project abstract combining goals + roadmap.
  Add `project_mode` (PoC/MVP/side/SaaS) to set planning discipline depth.

### IDEA-2026-006-06: Cross-project parallel notification

- concept_tags: cross-project, parallels, notification
- problem_patterns: no-parallel-notification
- architecture_patterns: notification-artifact
- feedback_ticket: FB-006
- status: captured
- source: feedback round Q4, Q10a
- summary: Write a `parallels-notice.md` after `owlib find-parallels`. Agent reads
  it at session start and surfaces high-score parallels. No daemon in v1.

### IDEA-2026-006-07: PI Agent setup guide

- concept_tags: pi-agent, setup, documentation
- problem_patterns: no-setup-guide, unclear-auth-requirements
- architecture_patterns: documentation
- feedback_ticket: FB-007
- status: captured
- source: feedback round Q5
- summary: Document PI Agent setup. Clarify: deterministic mode needs no LLM
  auth; future semantic mode would need provider auth. One doc page.

### IDEA-2026-006-08: Plan completion contract

- concept_tags: plan, completion, contract, harness-agnostic
- problem_patterns: no-completion-contract, harness-detection-unclear
- architecture_patterns: markdown-contract
- feedback_ticket: FB-008
- status: captured
- source: feedback round Q7
- summary: Standardize `status: done` + `acceptance_criteria` + `qa_gate_ids` as
  the harness-agnostic completion signal. Document in planning skill.

### IDEA-2026-006-09: Planning permission modes

- concept_tags: planning, permission, mode, supervised
- problem_patterns: no-permission-toggle, idea-duplicate-ambiguous
- architecture_patterns: project-context-extension
- feedback_ticket: FB-009
- status: captured
- source: feedback round Q8
- summary: Add `planning_mode: supervised/approve-automatically/full-access` to
  `PROJECT_CONTEXT.md`. When idea exists, behavior depends on mode.

### IDEA-2026-006-10: Success metrics in MVP plan

- concept_tags: mvp, metrics, success-criteria, decision-rule
- problem_patterns: no-success-metrics, vague-acceptance
- architecture_patterns: plan-template-extension
- feedback_ticket: FB-010
- status: captured
- source: feedback round Q9
- summary: Add `## Success Metrics` to MVP plan template with measurable metrics
  and decision rules (met → integrate; not met → defer to roadmap).

### IDEA-2026-006-11: Idea-to-project pipeline

- concept_tags: ideas, pipeline, project-scaffold, prioritization
- problem_patterns: no-idea-pipeline, ideas-stuck-in-log
- architecture_patterns: owlib-subcommand
- feedback_ticket: FB-011
- status: captured
- source: feedback round Q10c
- summary: `owlib ideas --scope global` lists ideas sorted by signal. `owlib ideas
  promote` scaffolds a new `PROJECT_CONTEXT.md` from a promoted idea.

## Promotion Paths

| Idea | If accepted, promote to |
| --- | --- |
| IDEA-006-01 | P0 roadmap item (publish) |
| IDEA-006-02 | P1 roadmap item + new doc file |
| IDEA-006-03 | P1 roadmap item + benchmark extension |
| IDEA-006-04 | P1 roadmap item + owlib.yaml extension |
| IDEA-006-05 | P1 roadmap item + PROJECT_CONTEXT.md template update |
| IDEA-006-06 | P2 roadmap item + owlib notification artifact |
| IDEA-006-07 | P2 roadmap item + new doc file |
| IDEA-006-08 | P2 roadmap item + planning skill update |
| IDEA-006-09 | P2 roadmap item + PROJECT_CONTEXT.md template update |
| IDEA-006-10 | P2 roadmap item + MVP plan template update |
| IDEA-006-11 | P3 roadmap item + owlib subcommand |

## Triage Status

All ideas are `captured`. Next triage step: review each against current scope
and either `elaborate` (accept into near-term roadmap) or `reject` with reason.

## Round 2 Ideas (Feature Ideas)

### IDEA-2026-006-12: Minimal ticket board

- concept_tags: ticket-board, timeline, priority, frontmatter-sync
- problem_patterns: no-board-view, manual-frontmatter-updates
- architecture_patterns: markdown-board, hook-sync
- feedback_ticket: FB-013
- similar_to: FB-008 (completion contract), execution-dashboard.md
- status: captured
- source: feature idea 1
- summary: Render a minimal Markdown ticket board grouped by status with
  priority sorting. Add a frontmatter sync hook so `status: done` is set
  reliably when QA gates pass. Reuse existing `task-card.schema.json`.

### IDEA-2026-006-13: Harness hook extensions for Codex/Claude

- concept_tags: hooks, plugin, codex, claude-code, harness
- problem_patterns: hooks-only-capture, no-validation-on-stop
- architecture_patterns: hook-extension-points
- feedback_ticket: FB-014
- similar_to: existing `plugins/agent-memory-cowork/` (already has 8 hooks)
- status: captured
- source: feature idea 2
- summary: Extend the existing hook layer to validate ticket frontmatter on
  PostToolUse and run `validate-memory --strict` on session end. Document hook
  extension points for custom hooks.

### IDEA-2026-006-14: Ticket summary in supervised approval

- concept_tags: ticket-summary, supervised-mode, approval, dashboard
- problem_patterns: id-only-approval-prompt, user-cant-see-ticket
- architecture_patterns: inline-render
- feedback_ticket: FB-015
- similar_to: FB-009 (permission modes), FB-013 (ticket board)
- status: captured
- source: feature idea 3
- summary: When asking user to integrate a ticket/idea into a plan in
  supervised mode, render a compact 5-line summary (title, priority, status,
  description, source link) inline. Optionally render in dashboard.

### IDEA-2026-006-15: Quick-read field on all tickets

- concept_tags: quick-read, summary, token-efficiency, validation
- problem_patterns: no-quick-context, stale-summaries, agents-read-too-much
- architecture_patterns: schema-extension, generated-view
- feedback_ticket: FB-016
- similar_to: FB-013 (ticket board), FB-015 (ticket summary)
- status: captured
- source: feature idea 4
- summary: Add a `quick_read` field (under 300 chars) to TaskCard schema. It is
  a maintained view, not canonical. Add a validation gate to detect stale
  quick-reads. Board and summaries use quick_read, not full bodies.

### IDEA-2026-006-16: Cleanly defined project modes

- concept_tags: project-mode, abstract, intuitive, definition
- problem_patterns: placeholder-modes, unclear-mode-semantics
- architecture_patterns: template-extension
- feedback_ticket: FB-017
- similar_to: FB-005 (project abstract + mode selector)
- status: captured
- source: feature idea 5
- summary: Define 4 project modes cleanly: poc (prove it works), mvp (one user
  gets value), side (fun and bounded), saas (ship and charge). Each mode sets
  planning discipline depth and required fields.

### IDEA-2026-006-17: Session-continuity checklists in plans

- concept_tags: session-continuity, checklists, resume, subagents
- problem_patterns: session-break-restart, lost-context, repeated-work
- architecture_patterns: per-phase-checkboxes, resume-rule
- feedback_ticket: FB-018
- similar_to: none
- status: captured
- source: v0.6.1 red-team session (2026-06-25)
- summary: Every multi-phase plan embeds three checkboxes per phase
  (implementation done, QA checks done, quick review done). A new agent
  resumes from the first unchecked box, never restarting completed phases.
  Subagents check their own boxes before returning. The checkbox is a
  navigation aid; the QA gate output is the durable evidence. Shipped in the
  v0.6.1 fix-up; track adoption and harden the gate if plans drift.

### IDEA-2026-006-18: Deferred P2 polish batch from v0.6.1 red-team

- concept_tags: polish, deferred-fixes, v0.6.2
- problem_patterns: metadata-only-behavior, over-broad-glob, stale-gate-logic
- architecture_patterns: batch-fix-release
- feedback_ticket: FB-019
- similar_to: none
- status: captured
- source: v0.6.1 red-team P2-16..P2-21
- summary: Batch of six P2 polish items deferred from the v0.6.1 fix-up to
  keep scope tight: additive-change behavioral suppression (P2-16),
  dogfood_sync glob restriction (P2-17), concept-audit-fresh self-audit
  specificity (P2-18), upgrade_drift_check mode (P2-20), and historical
  plan line-number staleness (P2-21). Target v0.6.2 "polish" release.