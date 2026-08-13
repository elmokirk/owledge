---
memory_id: "mem:owledge:global:owledge:task:v1-minimal-core-finalization-checklist"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "task"
artifact_type: "workpackage"
document_version: 7
workpackage_version: "1.0.2"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge V1 minimal core finalization checklist"
summary: "Resume-oriented checklist for reconciling the active V1 control plane with the minimal Core plan and delivering the compact GA journey without reactivating parked work."
concept_tags: ["v1", "execution-checklist", "minimal-core", "ga"]
stack_tags: ["python", "markdown", "git", "mcp"]
problem_patterns: ["plan-execution-drift", "parked-feature-reactivation", "parallel-writer-conflict"]
architecture_patterns: ["single-writer", "gate-driven-delivery", "atomic-ticket"]
failure_modes: ["planning-branch-overwrites-active-run", "completed-evidence-repeated", "publish-without-owner"]
confidence: 0.97
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-13T17:20:00+02:00"
updated_at: "2026-08-13T20:10:00+02:00"
source_hash: ""
reusable_lessons:
  - "A new plan enters an active release train only at a clean ticket/gate boundary."
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:v1-minimal-core-finalization"
    confidence: 1.0
    reason: "Turns the final scope-reduction plan into resumable execution phases."
---

# V1 Minimal Core Finalization Checklist

## Resume state

- Planning branch: `codex/v1-core-final-plan`
- Planning base: `734ea7d` (`OW-081-05` implementation commit)
- Active delivery branch: `codex/v071-integration`
- Integration rule: do not cherry-pick or merge this planning commit while the
  delivery checkout has an active/uncommitted ticket.
- First safe integration point: clean `G-081-A-ADAPTERS` checkpoint, before
  selecting `OW-081-07` or any later ticket.
- Completed adapter work must be reused, not repeated.

## Phase 0 — Planning artifact QA

- [x] Validate frontmatter and unique memory IDs for all five new artifacts.
- [x] Validate internal edge targets and wiki-link/file targets.
- [x] Run `git diff --check`.
- [x] Review the plan for contradictions with the approved Hub/Pi/LightRAG cut.
- [x] Commit only the plan, decision, parking register, checklist, and handoff.

Evidence:

- Plan: `internal/owledge/plans/owledge-v1-minimal-core-finalization-plan.md`
- Decision: `internal/owledge/decisions/v1-minimal-core-and-product-surfaces-2026-08-13.md`
- Park register: `internal/owledge/ideas/post-v1-feature-parking-lot.md`
- Goal handoff: `internal/owledge/workpackages/owledge-v1-minimal-core-goal-handoff.md`
- QA: target frontmatter/ID/edge failures `0`; wikilink unresolved `0`,
  ambiguous `0`; public operations `8`; MCP tools `5`; V1M tickets `11`;
  parked concepts `24`; diff check clean.

## Phase 1 — Reconcile, do not restart

- [x] Confirm delivery checkout is clean and no ticket is `in_progress`.
- [x] Cherry-pick the planning commit onto the delivery branch.
- [x] Re-read live `RUN-STATE.yaml`, `BACKLOG.yaml`, current gate and completed
  adapter evidence after cherry-pick.
- [x] Execute only `V1M-01` first.
- [x] Amend existing master plan/control plane rather than creating a parallel
  active execution truth.
- [x] Mark superseded unstarted tickets `post_v1` or map them to one V1M ticket.
- [x] Remove all V1 DAG dependencies on parked tickets.
- [x] Add complexity-budget validation and run the full plan validator.
- [x] Gate `G-V1M-PLAN` green before runtime changes.

Evidence: V1M-01 commit `5272dcf`; G-V1M-PLAN independent QA accepted after
canonical `PARK-*` reference resolution and 10/10 validator regressions.

## Phase 2 — Minimal surface

- [x] V1M-02 passes skill-only and minimal-profile footprint tests.
- [x] Default fresh profile <=15 files and <=8 directories.
- [x] Existing large install remains explicit `full`/`maintainer`, never default.
- [x] V1M-03 exposes exactly eight public Core verbs.
- [x] Existing aliases either route safely or emit actionable deprecation output.
- [x] No user-owned Markdown is removed or overwritten during upgrade.
- [x] Gate `G-V1M-SURFACE` green.

## Phase 3 — Local read path

- [x] V1M-04 links explicit projects to the private local Null-Space.
- [x] Only `project_user` and local `user_global` exist in V1 execution paths.
- [x] Direct scan is correct for small vaults; derived index is disposable.
- [ ] V1M-05 proves recall-before-research and recall-before-planning.
- [ ] Context packs include budgets, reasons, exclusions, revisions, and source
  drill-down without full-vault injection.
- [ ] Gate `G-V1M-READ` green.

Evidence: V1M-04 is accepted with two-project allowlist, direct-scan/index
equivalence and privacy receipts. Bare, relative and UNC/network link inputs,
unlinked projects, enterprise scope and network/sync tamper fail closed; the
symlink fixture remains a stable-platform follow-up because this Windows host
cannot create symlinks.

## Phase 4 — Knowledge lifecycle and parking

- [ ] V1M-06 writes typed Candidate deltas through one proposal contract.
- [ ] Parked records contain reason, sources, horizon, trigger and related project.
- [ ] Ordinary recall excludes raw and parked records.
- [ ] Planning-purpose recall resurfaces only relevant parked essences.
- [ ] V1M-07 proves promote/park/reject/supersede and tombstone propagation.
- [ ] Health catches stale sources, broken links, promotion debt and index drift.
- [ ] Gate `G-V1M-LIFECYCLE` green.

## Phase 5 — Thin adapters

- [ ] Reuse `OW-081-01/02/03/05` evidence.
- [ ] V1M-08 limits default MCP to five tools.
- [ ] Codex, Claude Code and generic MCP/CLI pass the same common journey.
- [ ] Search, storage, lifecycle and migration logic exist only in Core.
- [ ] Unsupported capabilities degrade explicitly.
- [ ] Gate `G-V1M-ADAPTERS` green.

## Phase 6 — GA hardening

- [ ] V1M-09 passes clean install, upgrade, interrupted recovery, offline and
  security-negative tests.
- [ ] V1M-10 passes the owner daily journey including park/resurface and
  cross-harness resume without chat history.
- [ ] Default wheel stays <=500 KB or an explicit owner-reviewed exception exists.
- [ ] Windows, macOS and Linux wheel-only GA evidence is executed, not inferred.
- [ ] Public docs show Principles, minimal project, and local user-global paths;
  internal dogfood and parked products are not presented as default features.
- [ ] Build wheel/sdist from a clean source commit and inspect artifact contents.
- [ ] Gate `G-V1M-GA` green.

## Phase 7 — Publication stop

- [ ] Present exact candidate commit and artifact hashes.
- [ ] Present shipped scope, known limitations, support window and parking lot.
- [ ] Confirm no personal/private paths, prompts, transcripts or credentials.
- [ ] Wait for explicit owner authorization naming push/tag/publish/release.
- [ ] V1M-11 performs only the authorized external actions.
- [ ] Record publication receipts and final closeout.

## Global safeguards

- [ ] One writer per checkout.
- [ ] WIP limit one ticket unless the live control plane explicitly proves
  non-overlapping paths and the owner has allowed parallel execution.
- [ ] Every material Owledge-managed document edit bumps `document_version`.
- [ ] Positive, negative and recovery checks are evidence-linked.
- [ ] Reversible local implementation details are autonomous; scope, privacy,
  destructive migration, credentials/cost and publication escalate.
- [ ] No parked item re-enters V1 without `AMEND GOAL BOUNDARY`.
- [ ] No personal workflow review/checklist is created or committed in this repo.
