# Feedback Round 2026-06

Date: 2026-06-23
Status: active
Owner: Kirk
Type: feedback-triage

## Purpose

Collect, triage, and promote user feedback into roadmap items and documentation
improvements. This is the first structured feedback round after the v0.5
refactor (`3440e30`).

## Feedback Tickets

### FB-001: Publish owledge to PyPI

- **Source:** Q1, Q3, vibe-coder persona, influencer persona
- **Problem:** The refactor made the sdist clean (zero `internal/` paths, zero
  root `.owledge/`), but `pip install owledge` does not work yet. Users must
  `git clone` and run from source. This is the single biggest adoption blocker.
- **Action:** Publish `owledge` to PyPI. The `pyproject.toml` already declares
  the `owledge` console script. `MANIFEST.in` includes `templates/` and excludes
  `internal/`.
- **Priority:** P0
- **Acceptance:** `pip install owledge && owledge --help` works on a clean
  Python 3.10+ environment without a source checkout.

### FB-002: AGENTS.md/CLAUDE.md copy-paste integration block

- **Source:** Q3
- **Problem:** When integrating Owledge into an existing project, there is no
  single SOTA copy-paste block a user can paste into their `AGENTS.md` or
  `CLAUDE.md`. The `owledge-principles` skill exists, but users who do not
  use the skills path need a self-contained block.
- **Action:** Create `docs/agents-md-integration-block.md` with a tested,
  self-contained paste block that covers: read order, memory layers, MVP plan
  structure, idea capture rule, and completion signal. Keep it under 60 lines.
- **Priority:** P1
- **Acceptance:** A user can paste the block into an empty `AGENTS.md`, point
  an agent at a project, and the agent follows Owledge rules without any other
  file.

### FB-003: Token cost benchmark with tokenizer baselines

- **Source:** Q2
- **Problem:** The benchmark (`benchmarks/results/baseline.json`) measures
  wall-clock, peak Python bytes, and `estimated_tokens` for context packs, but
  does not publish a tokenizer-based before/after comparison. The
  `performance-scale-notes.md` explicitly says "Treat this as a design rule until
  a benchmark report includes tokenizer-based baseline comparisons."
- **Action:** Add a tokenizer-based benchmark scenario comparing: (a) full vault
  prompt, (b) metadata-only scan, (c) generated context pack, (d) oracle scoped
  sources. Publish results in `docs/performance-scale-notes.md`.
- **Priority:** P1
- **Acceptance:** A public benchmark table shows token counts for all four
  scenarios with a reproducible command.

### FB-004: Global privacy controls + folder whitelist

- **Source:** Q6, Q10a
- **Problem:** When Owledge is installed globally (via `owlib`), the user has no
  control over which folders are scannable or which projects get registered to
  the central library. The user wants: (a) a whitelist of folders allowed to
  integrate Owledge, (b) an explicit consent prompt when a new project is
  registered to the global `owlib` instance, (c) per-project sync controls.
- **Action:** Add a `scan_allowlist` field to `owlib.yaml` and a per-project
  `owlib-registration.json` consent file. When an agent integrates Owledge into a
  new project, it asks the user whether to register/connect to the global owlib
  instance. Default is **not registered**.
- **Priority:** P1
- **Acceptance:** A user with 10 projects can whitelist 3 for global sync, and
  the other 7 are never scanned or registered.

### FB-005: Project abstract + project mode (PoC/MVP/Side/SaaS)

- **Source:** Q10b
- **Problem:** `OWLEDGE.md` has goals and a decision log, but no forced
  one-paragraph project abstract combining goals + roadmap. There is no project
  mode selector (PoC, MVP, side project, SaaS) to set planning discipline depth.
- **Action:** Add a `project_abstract` field and `project_mode` field to
  `OWLEDGE.md`. The mode determines planning rigor: PoC = minimal
  plan, MVP = full MVP cutline, side project = lightweight, SaaS = full abstract
  + metrics + compliance notes. The `mvp-plan-example.md` template gets a
  `## Project Abstract` section and a `## Success Metrics` section.
- **Priority:** P1
- **Acceptance:** A new project with `project_mode: saas` forces the agent to
  draft an abstract and success metrics before any plan is accepted.

### FB-006: Cross-project parallel notification

- **Source:** Q4, Q10a
- **Problem:** `owlib find-parallels` exists (`owlib/src/owlib/core.py:337`) and
  writes `parallel-candidates.jsonl`, but there is no notification mechanism.
  The user does not know parallels exist until they manually run the command and
  read the file.
- **Action:** Add a `parallels-notice.md` artifact written to the library root
  after `find-parallels`. The agent reads this at session start (in the agent
  read order) and surfaces high-score parallels to the user. No background
  daemon in v1 — the agent calls `owlib find-parallels` on demand or when the
  user asks for cross-project intelligence.
- **Priority:** P2
- **Acceptance:** After running `owlib find-parallels`, the next agent session
  in any registered project surfaces the top parallel candidates to the user
  with source memory IDs.

### FB-007: PI Agent setup guide + provider auth

- **Source:** Q5
- **Problem:** There is no single documentation page explaining how to set up
  the PI Agent. The PI Agent currently runs **deterministic signals locally**
  (`owlib/src/owlib/pi.py` — frontmatter tag intersection, growth scans, recurring
  error counts). It does **not** require an LLM provider API key for v1. A
  future semantic mode would require provider auth, but that is not implemented.
- **Action:** Create `docs/pi-agent-setup.md` documenting: (a) what the PI Agent
  does today (deterministic only, no auth needed), (b) how to run it
  (`owlib pi report`, `owlib pi find-parallels`), (c) when provider auth would be
  needed (future semantic mode, not yet implemented), (d) guardrails
  (candidate-only, never auto-promote).
- **Priority:** P2
- **Acceptance:** A user can set up and run the PI Agent by following one doc
  page without guessing.

### FB-008: Plan completion detection contract

- **Source:** Q7
- **Problem:** Owledge does not have a harness-specific plan detection
  mechanism. It uses a Markdown contract: a plan is "done" when its task(s)
  reach `status: done` and the required `qa_gate_ids` have passing
  `gate_reports` (`owledge_core.py:1271-1279`). This is harness-agnostic but
  not documented as a contract.
- **Action:** Document the completion contract in the planning-layer skill and
  `docs/mvp-plan-example.md`: `status: done` + `acceptance_criteria` met + QA
  gates passed. Add a `completion_signal` field to the MVP plan template.
- **Priority:** P2
- **Acceptance:** Any harness (Claude Code, Codex, OpenCode, Cursor) writing
  `status: done` with passing gates is recognized as complete by Owledge.

### FB-009: Idea-duplicate handling + permission modes

- **Source:** Q8
- **Problem:** When an idea already exists (`.owledge/ideas/`), the
  `ideation-workflow.md` says agents should "check ideas before drafting new
  plans" and "add `similar_to` edges" but does not define whether the agent asks
  the user or just links it. There is no permission toggle.
- **Action:** Add a `planning_mode` field to `OWLEDGE.md` with three
  values: `supervised` (agent asks before linking/integrating existing ideas),
  `approve-automatically` (agent links and logs without asking), `full-access`
  (agent can promote ideas into tasks without asking). Default is `supervised`.
- **Priority:** P2
- **Acceptance:** In `supervised` mode, the agent says "I found a similar idea
  `idea-003` — link it to this plan?" before acting.

### FB-010: MVP goal/metric definition template

- **Source:** Q9
- **Problem:** The MVP plan template (`docs/mvp-plan-example.md`) has
  `## Acceptance Criteria` but no `## Success Metrics` section with user-specific,
  measurable metrics. Without metrics, Owledge cannot make proper decisions
  about whether a feature should be integrated into the plan or deferred to the
  roadmap.
- **Action:** Add a `## Success Metrics` section to the MVP plan template with
  fields: metric name, target value, measurement method, and decision rule
  (if metric met → integrate; if not → defer to roadmap). Update the planning
  skill to require this section when `project_mode` is `mvp` or `saas`.
- **Priority:** P2
- **Acceptance:** Every MVP plan has at least one measurable success metric with
  a decision rule.

### FB-011: Idea-to-project pipeline

- **Source:** Q10c
- **Problem:** Ideas are captured in `.owledge/ideas/` and
  `global-memory/ideas/`, but there is no pipeline to filter, prioritize, and
  scaffold a new project from a promoted idea.
- **Action:** Add an `owlib ideas` subcommand that lists ideas across project
  and global scope, sorted by signal strength. Add an `owlib ideas promote`
  command that scaffolds a new `OWLEDGE.md` from a promoted idea with
  the idea's `concept_tags`, `problem_patterns`, and source links pre-filled.
- **Priority:** P3
- **Acceptance:** A user can run `owlib ideas --scope global` and see a
  prioritized list, then promote one into a new project scaffold.

### FB-012: Recurring feedback round

- **Source:** Meta (this conversation)
- **Problem:** Feedback is collected ad-hoc. There is no recurring workflow to
  triage and promote feedback into roadmap items.
- **Action:** Add a `docs/feedback-round-YYYY-MM.md` template and a triage
  workflow: collect → triage (P0-P3) → promote to roadmap → log rejected items
  with reason. Run quarterly or after major refactors.
- **Priority:** P3
- **Acceptance:** A feedback round produces a dated file with triaged tickets,
  each linked to a roadmap item or a rejection reason.

## Round 2: Feature Ideas (2026-06-23, continued)

### FB-013: Minimal ticket board with timeline + priorities + frontmatter sync

- **Source:** Feature idea 1
- **Connects to:** FB-008 (completion contract), existing `task-card.schema.json`
  (already has `status`, `priority`, `qa_gate_ids`), existing
  `execution-dashboard.md` reference (already mentions "ticket counts")
- **Problem:** The `TaskCard` schema exists with `status` (backlog/ready/claimed/
  in_progress/blocked/review/qa/done/rejected/archived) and `priority`
  (low/normal/high/critical), but there is no minimal ticket-board view with
  timeline and priority columns. Frontmatter status actualization after
  finishing a ticket is not automated as a script or Owledge hook — agents must
  manually update frontmatter, which is unreliable.
- **Action:**
  1. Add a `ticket-board` command to `owledge.py` that renders a read-only
     Markdown board grouped by `status` column with priority sorting within each
     column. Source: all `task-card` frontmatter in `.owledge/`.
  2. Add a timeline view (tasks sorted by `updated_at` or due date).
  3. Add a frontmatter sync hook/script that reliably updates `status` → `done`
     when acceptance criteria + QA gates pass. Wire it as an Owledge hook for
     harnesses (Claude Code `Stop`, Codex session end).
  4. Reuse the existing `execution-dashboard.md` reference as the board layout.
- **Priority:** P1
- **Acceptance:** `python tools/owledge.py ticket-board --project-root .`
  renders a Markdown board with columns (Backlog, Ready, In Progress, Blocked,
  Review, Done) and priority-sorted rows. The frontmatter sync hook updates
  `status: done` automatically when `qa_gate_ids` all pass.

### FB-014: Harness hook layer for Codex and Claude Code as plugin

- **Source:** Feature idea 2
- **Connects to:** Already partially implemented —
  `plugins/owledge-cowork/.claude-plugin/plugin.json` and
  `.codex-plugin/plugin.json` both exist with `hooks`, `commands`, `agents`,
  `skills`. `hooks.json` wires 8 lifecycle hooks (SessionStart, UserPromptSubmit,
  PostToolUse, PostToolUseFailure, PreCompact, PostCompact, Stop, SessionEnd).
- **Problem:** The hook layer exists for Claude/Cowork-compatible and Codex, but
  it only captures session events. It does not sync ticket status, surface
  parallels, or run QA gates on session end. The hook layer is a runtime adapter,
  not a planning hook.
- **Action:**
  1. Extend `hooks.json` with a `PostToolUse` matcher for ticket/task files so
     frontmatter status is validated after edits.
  2. Add a `Stop`/`SessionEnd` hook that runs `validate-memory --strict` and
     surfaces any failing gates as a session-close summary.
  3. Document the hook extension points in `docs/install-plugin.md` so users can
     add custom hooks without forking the plugin.
- **Priority:** P2
- **Acceptance:** A Claude Code or Codex session that edits a task-card file
  triggers a frontmatter validation hook; session end runs validation and
  surfaces a pass/fail summary.

### FB-015: Ticket summary/render when asking user to integrate into plan

- **Source:** Feature idea 3
- **Connects to:** FB-009 (idea-duplicate handling + permission modes), FB-013
  (ticket board)
- **Problem:** When an agent asks the user to integrate a ticket/idea into a
  plan (in `supervised` mode), it only shows the idea ID. The user does not see
  the ticket content and cannot make an informed decision.
- **Action:**
  1. In `supervised` planning mode, when an agent finds a matching ticket/idea,
     it renders a compact summary (title, priority, status, 2-line description,
     source links) inline in the chat before asking for approval.
  2. If the Project Snapshot Kit is installed, also render the ticket in the
     dashboard so the user can click through.
  3. The summary uses the `quick_read` section (see FB-016) so it stays under
     5 lines.
- **Priority:** P2
- **Acceptance:** In `supervised` mode, the agent's prompt to integrate a
  ticket includes a 5-line summary with title, priority, status, description,
  and source link — not just an ID.

### FB-016: Quick-read section on all tickets for fast context gathering

- **Source:** Feature idea 4
- **Connects to:** FB-013 (ticket board), FB-015 (ticket summary), existing
  `task-card.schema.json` (supports `additionalProperties: true` so new fields
  are schema-legal)
- **Problem:** Tickets have full descriptions but no "quick read" summary. Users
  need fast context; agents need less to read initially. A weak concept here
  breaks the system (stale quick-reads, divergence from full description, agent
  confusion about which is canonical).
- **Action:**
  1. Add a `quick_read` field to the `TaskCard` schema — a 1-3 sentence summary
     with `priority`, `status`, and `next_action`. Must be under 300 chars.
  2. The canonical source of truth is the full ticket body; `quick_read` is a
     generated/maintained view. The agent that updates a ticket must also refresh
     `quick_read`.
  3. Add a validation gate: `quick_read` must not diverge from the full body's
     first paragraph by more than 50% word overlap (detect stale quick-reads).
  4. The ticket board (FB-013) uses `quick_read` for row content, not the full
     body.
- **Priority:** P1
- **Acceptance:** Every TaskCard has a `quick_read` field under 300 chars. The
  validation gate catches stale quick-reads when the full body changes without
  a quick_read refresh. The ticket board renders quick_read, not full bodies.

### FB-017: Cleanly define project abstract + modes with intuitive definitions

- **Source:** Feature idea 5
- **Connects to:** FB-005 (project abstract + mode selector — currently
  placeholder/braindump)
- **Problem:** The `project_abstract` and `project_mode` fields proposed in
  FB-005 were placeholders. Users need intuitive definitions to understand what
  each mode means and what planning discipline it enforces.
- **Action:** Define the modes cleanly:
  - **`poc` (Proof of Concept):** Prove a concept works. Minimal plan, no
    cutline required. Abstract optional. No success metrics required. Target:
    "does this work at all?"
  - **`mvp` (Minimum Viable Product):** Ship the smallest useful version for
    one real user. Full MVP cutline (in-scope/out-of-scope), evidence links,
    acceptance criteria, and at least one success metric with a decision rule.
    Abstract required (1-3 sentences). Target: "one user gets value."
  - **`side` (Side Project):** Personal/low-stakes project. Lightweight plan
    with goals and non-goals. Abstract recommended. Success metrics optional.
    Target: "keep it fun and bounded."
  - **`saas` (SaaS/Product):** Ship to paying users. Full abstract required
    (combines goals + roadmap + target user in one paragraph), success metrics
    required (at least 3 with decision rules), compliance notes, and trust
    readiness check. Target: "ship and charge for it."
- **Priority:** P1
- **Acceptance:** `OWLEDGE.template.md` has a `project_mode` field with
  the 4 modes documented inline. A new user reading the template understands
  which mode to pick without external docs.

### FB-018: Session-continuity checklists in plans (shipped in v0.6.1 fix-up)

- **Source:** v0.6.1 red-team session (2026-06-25)
- **Connects to:** IDEA-2026-006-17
- **Problem:** Agent sessions break mid-plan and the next agent restarts the
  whole plan, wasting context and re-doing completed phases. There is no
  per-phase checkpoint convention that lets a new agent resume from the exact
  last-completed step.
- **Action:**
  1. Every multi-phase plan (`docs/*-plan.md` with >=2 `## Phase` headings)
     must include three checkboxes per phase: `- [ ] implementation done`,
     `- [ ] QA checks done`, `- [ ] quick review done`.
  2. The resume rule: a new agent reads the plan, finds the first unchecked
     box, and continues from there. Never restart a completed phase. If a
     session breaks mid-phase, re-run that phase's QA gate; if it fails,
     uncheck and redo the phase.
  3. Subagents check their own boxes before returning to the orchestrator.
  4. The checkbox is a navigation aid, not an audit record; the phase's QA
     gate output (committed to `internal/owledge/exports/`) is the
     durable evidence.
  5. A new gate `test_planning_conventions.py::test_plan_has_continuity_checklists`
     enforces the convention on multi-phase plans.
- **Priority:** P1
- **Acceptance:** `docs/v0.6.1-fix-up-plan.md` and
  `docs/v0.6.1-upgrade-foundation-plan.md` both have per-phase checklists.
  `AGENTS.md`, `AGENTS.template.md`, `CLAUDE.template.md` have a
  `## Session Continuity` section. The planning-layer skill workflow includes
  the checklist step. `test_planning_conventions.py` passes.

### FB-019: Deferred P2 polish batch from v0.6.1 red-team

- **Source:** v0.6.1 red-team `internal/owledge/decisions/red-team-v0.6.1-pr.md`
  (P2-16..P2-21)
- **Connects to:** IDEA-2026-006-18
- **Problem:** Six P2 polish items were identified but deferred to keep the
  v0.6.1 fix-up tightly scoped to P0/P1.
- **Action:** Batch into a v0.6.2 "polish" release:
  1. P2-16: additive-change awareness should suppress `would_update` lists
     for `breaking: no|additive` (currently metadata-only).
  2. P2-17: `dogfood_sync_check` should restrict to `*-template.md` glob,
     not `rglob("*")` over `templates/`.
  3. P2-18: `concept-audit-fresh` gate should require the report's frontmatter
     `auditor: concept-blindspot-audit` to count, not just any
     `concept-audit-*.md`.
  4. P2-20: `upgrade_drift_check` should use `doctor --mode kit` on temp
     projects (no host context), not `--mode host`.
  5. P2-21: stale line numbers in `docs/v0.6.1-upgrade-foundation-plan.md`
     (historical artifact; no fix needed).
- **Priority:** P3
- **Acceptance:** Each P2 item is either fixed in v0.6.2 or explicitly
  retracted with a recorded reason in the CHANGELOG.

### FB-020: `concept-audit --since` date filter

- **Source:** v0.6.1 red-team P1-7 (dead flag)
- **Connects to:** none
- **Problem:** `concept-audit --since` is parsed by argparse but never read by
  the dispatch. The v0.6.1 fix-up removes the dead flag rather than
  half-implementing it.
- **Action:** Implement `--since YYYY-MM-DD` in v0.6.2 to filter
  `concept-audit` findings by date (e.g. only findings newer than the last
  audit). Re-add the flag with working dispatch logic.
- **Priority:** P3
- **Acceptance:** `concept-audit --since 2026-06-01` returns only findings
  dated on or after 2026-06-01. A new test
  `test_concept_audit_since_filter` passes.

### FB-021: `release.yml` upgrade-notes contract -> JSON schema

- **Source:** v0.6.1 red-team R-3
- **Connects to:** none
- **Problem:** The `release.yml` upgrade-notes step greps
  `## Upgrade notes` in `CHANGELOG.md`. This is brittle (depends on exact
  heading text) and does not validate the `breaking: yes|no|additive` field
  structure.
- **Action:** Replace the grep with a JSON-schema contract: a
  `docs/upgrade-notes-schema.json` that declares the required fields
  (`breaking`, `summary`). The release step validates the latest
  `## Upgrade notes` block against the schema. Keep the grep as a fallback.
- **Priority:** P2
- **Acceptance:** `release.yml` validates the upgrade-notes block against
  `docs/upgrade-notes-schema.json`. A malformed block (missing `breaking`)
  fails the job.