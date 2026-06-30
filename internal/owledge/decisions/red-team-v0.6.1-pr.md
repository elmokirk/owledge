---
memory_id: "mem:dogfood:owledge:decision:red-team-v0-6-1-pr"
doc_type: "decision"
status: "active"
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "2026-06-25T00:00:00Z"
updated_at: "2026-06-25T00:00:00Z"
source_review: "PR feat/v0.6.1-upgrade-foundation (commits 23f46a9..de383b3)"
target_score: 95
edges:
  - "docs/v0.6.1-upgrade-foundation-plan.md"
  - "docs/v0.6.1-fix-up-plan.md"
---

# Red-Team Review - PR `feat/v0.6.1-upgrade-foundation`

**Subject:** v0.6.1 "Upgrade Foundation & Concept Audit" - 6 commits, 94 files,
+5232/-153.
**Plan:** `docs/v0.6.1-upgrade-foundation-plan.md` (377 lines, 6 workstreams
E1-E6 + Phase 5 skill).
**Question:** Are the made changes conceptually sound, mechanically complete,
and safe to merge?
**Personas:** Senior AI Agent Engineer, Scalability/Systems Reviewer,
Security/Privacy Reviewer, UX/DX Adopter, QA Gate Owner, Compliance/Audit
Reviewer, Product/Scope Strategist.
**Evidence basis:** `tools/owledge.py` (2540 lines), `tools/owledge_core.py`,
`skills/concept-blindspot-audit/`, `docs/upgrading.md`, `CHANGELOG.md`,
`.github/workflows/{ci,release}.yml`, runtime probes (`init-project` into temp
dirs, `git apply --check` against generated patch, manifest inspection).
**Mode:** standard multi-perspective red-team (REVIEW.md: minimum_accept_score
85).

## Source Review

| Field | Value |
| --- | --- |
| Source review | PR `feat/v0.6.1-upgrade-foundation` (HEAD `de383b3`) |
| Current score | 71 (composite) |
| Target score | 95 |
| Recommendation | `block` (effective; REVIEW.md blocking conditions triggered) |

## P0 - Blockers (merge-blocking)

### P0-1. Skills are silently non-upgradable AND the flagship skill is not installable. The "no parallel inventory" rule is violated.

**Corrected finding (sharper than first reported).** `HOST_SKILL_DIRS`
(`tools/owledge.py:112-117`) lists only 4 skills
(`owledge-principles`, `owledge-runtime-bridge`,
`review-evaluation-workflow`, `render-memory-report`). It does **NOT** include
`skills/concept-blindspot-audit` - the headline feature skill shipped in this
PR. Combined with `_collect_kit_files` (`:241-280`) never walking
`HOST_SKILL_DIRS` or `skills/**`, the skill is: (a) not installed by
`init-project`, (b) not recorded in `kit-manifest.json`, (c) not drift-detected
by `doctor`, (d) not upgradable by `upgrade`. The skill exists only in the
source repo. **Empirically verified:** `init-project` into a temp dir produces
a `skills/` tree containing only the 4 pre-existing skills; the manifest's
`files[]` array has zero `skills/*` entries.

**Why P0:** the entire feature shipping in this PR (the
`concept-blindspot-audit` skill) is invisible to its own lifecycle machinery.
This is a self-defeating foundation. The plan (`docs/v0.6.1-upgrade-foundation-plan.md:169`)
explicitly mandates: *"Updatable allow-list = runtime union of ROOT_FILE_MAP +
HOST_TOOL_FILES + HOST_SKILL_DIRS + `templates/owledge/**` + `skills/**`.
Computed from the SAME constants `init_project` uses - no parallel
inventory."* The manifest IS a de-facto parallel inventory and it omits
skills.

**Fix:** (1) extend `HOST_SKILL_DIRS` to include
`"skills/concept-blindspot-audit"`; (2) extend `_collect_kit_files` to walk
`HOST_SKILL_DIRS` and emit `skills/<rel>` entries; (3) add the skill to
`pyproject.toml` `[tool.setuptools.package-data]` so pip-installed users get
it. **QA gate:** `skills-in-manifest-and-upgradable` (new).

### P0-2. `upgrade --apply --mode=manual` writes files - directly contradicts the plan's "No writes" guarantee.

`dry_run = not args.apply` (`owledge.py:2512`). Manual mode's `select_targets`
(`:612-620`) returns real `update_targets`/`create_targets`. With `--apply`,
the apply block (`:675-708`) runs `shutil.copy2` on every target. The plan
(`docs/...plan.md:174`) is unambiguous: *"manual: emit per-file unified diffs
+ single `git apply`-able patch to stdout /
`.owledge/exports/upgrade-pending.patch`. **No writes.**"* Manual mode is
supposed to be the safe "show me what would change" path; instead
`--apply --mode=manual` is a less-protected `force-templates` that bypasses
the `--yes` requirement (`:570-571` only gates `force-templates`).

**Why P0:** silent data loss class. A user reading `docs/upgrading.md:21`
("manual: emits a patch, no writes") who runs `upgrade --apply --mode=manual`
will overwrite files they expected to review first. The doc and the code
contradict each other on a destructive operation.

**Fix:** reject `--apply` with `--mode=manual` ("manual mode is always
dry-run; --apply ignored"), exit code 2. **QA gate:**
`upgrade-manual-never-writes`.

### P0-3. The manual-mode patch is NOT `git apply`-able. Plan acceptance test `upgrade-manual-emits-patch` will fail.

**Empirically tested:** ran `upgrade --dry-run --mode=manual` against a temp
project, then `git apply --check` against the generated
`.owledge/exports/upgrade-pending.patch` -> `error: No valid patches in
input (allow with "--allow-empty")`, exit 128. Root cause (`owledge.py:644`):
`difflib.unified_diff(..., fromfile=rel, tofile=rel, lineterm="")` emits
headers like `--- AGENTS.md` / `+++ AGENTS.md` with **no `a/`/`b/` prefixes
and no `diff --git` header**. `git apply` defaults to `-p1` and rejects this.

**Why P0:** this is the plan's named acceptance test for E3
(`docs/...plan.md:198`). It is listed as a required stress test. The PR ships
with this gate unverified - and empirically failing.

**Fix:** emit `a/<rel>` and `b/<rel>` and prepend `diff --git a/<rel> b/<rel>`.
For new files, emit `new file mode 10066`. Re-run `git apply --check`.
**QA gate:** `upgrade-manual-emits-patch` (the plan's named test).

### P0-4. Zero of the 19 named stress tests exist. The plan's per-phase acceptance gates were never run.

The plan defines 19 named stress tests as the acceptance gates for E1-E6 and
Phase 5. Comprehensive grep across the repo returns **zero** `def <test_name>`
matches for any of them. There is no `tests/test_*.py`, no `conftest.py`, no
`pytest.ini`, no `[tool.pytest]` in any `pyproject.toml`. The only Python test
file is `owlib/tests/test_owlib.py` (182 lines, 5 tests) for a different
package.

**Why P0:** the plan's recap checkpoints ("Print: stress test results") and
gate blocks ("E3 gate: ... all 6 stress tests") **cannot have run** - there is
nothing to run. The PR claims phase completion without the phase's own
acceptance criteria being satisfiable. This is the QA Gate Owner persona's
hard block (REVIEW.md: "failed required QA gate" -> block).

**Fix:** create `tests/test_upgrade.py`, `tests/test_doctor.py`,
`tests/test_dogfood_sync.py`, `tests/test_global_link.py`,
`tests/test_concept_audit.py`, `tests/test_skill_meta.py` + `conftest.py` +
`pytest.ini`. Wire into CI. **QA gate:** the 19 named tests exist, run, and
pass in CI.

### P0-5. The META acceptance test `skill-finds-its-own-gaps` is not enforced anywhere - the skill's own gate is unverified.

The plan calls this *"the META test (most important)"*
(`docs/...plan.md:283-285`): `concept-audit` run against owledge itself at
`project_mode: mvp` MUST surface >=4 of 6 specific findings. Grep for the
finding strings and for `>=4`/`>= 4` in all `.py` files: zero hits.
`concept_audit` (`owledge_core.py:5962`) returns findings but asserts
nothing about which must appear. The skill could ship returning zero of the 6
and nothing would fail.

**Why P0:** this is the skill's *reason for existing*. Shipping the skill
without verifying it reproduces the gaps it was created to find is a
self-description-accuracy failure (Dimension 8 of the skill's own rubric).

**Fix:** `tests/test_skill_meta.py::test_skill_finds_its_own_gaps_against_v060`
must run `concept_audit` against a temp v0.6.0-state project and assert >=4 of
the 6 finding strings appear. **QA gate:** the META test runs in CI and gates
merge.

## P1 - Material issues (revise before merge)

### P1-6. `release_trust_gate` does NOT recognize `owledge_kit_version` - plan E1 Files line 70 and Risk Register line 354 unmet.

`owledge.py:1015-1044` reads VERSION, README, plugin manifests, harness
matrix, SECURITY.md, command-reference - it never parses template frontmatter.
Repo-wide grep: `owledge_kit_version` appears 0 times in `tools/owledge.py`.
**Net effect today:** harmless (the gate is frontmatter-agnostic so it doesn't
*break*), but the letter of the plan is unmet. **Fix:** retraction - update
the plan/red-team to note "gate is frontmatter-agnostic by design; no code
change required."

### P1-7. `--format summary` is a dead flag for `upgrade`; `--since` is a dead flag for `concept-audit`.

`owledge.py:2388` defines `upgrade ... --format json|summary`, but the dispatch
(`:2512-2514`) always calls `print_json(result)`. `owledge.py:2392` defines
`concept-audit ... --since`, but dispatch (`:2515-2532`) never reads
`args.since`. Two CLI flags that parse but do nothing. **Fix:** implement
`--format summary` for upgrade (10-line summary printer); remove `--since`
(log as FB-020).

### P1-8. `force-templates` lacks interactive confirmation. Plan contract half-met.

Plan (`:173`): *"`force-templates`: ... Requires interactive confirmation
**or** `--yes`."* Code (`:570-571`): only `--yes` is accepted. A
`prompt_yes_no` helper exists (`:830`) but upgrade never calls it. **Fix:**
before erroring, if not `yes` and stdin is a TTY, call `prompt_yes_no`.

### P1-9. CHANGELOG omits Phase 5 entirely and under-reports E6. Self-description accuracy violation.

`CHANGELOG.md:3-12` (the `## 0.6.1` block) lists E1-E5 + FB-016 amendment.
**Zero mention** of: the `concept-blindspot-audit` skill, the `concept-audit`
subcommand, the 8-dimension rubric, `docs/upgrading.md`, the PR template
checkbox, the `release.yml` upgrade-notes step, or the 6 ROADMAP rows. The
"New CLI subcommands" line (`:11`) lists `upgrade`, `sync-dogfood`,
`dogfood-sync-check` - omitting `concept-audit`. A user reading only the
CHANGELOG would not know the headline feature of this PR exists.

**Also:** `## Upgrade notes` (`:14-18`) is positioned as a peer `## ` heading
between `## 0.6.1` and `## 0.6.0`, not nested under `## 0.6.1`. Structurally
awkward.

**Fix:** add CHANGELOG bullets for Phase 5 + E6 + the fix-up. Move
`## Upgrade notes` to `### Upgrade notes` under `## 0.6.1`.

### P1-10. `command-reference.md` omits `concept-audit` - contract-completeness gap the skill itself would flag.

`docs/command-reference.md:43-48,66` documents `upgrade`, `sync-dogfood`,
`dogfood-sync-check`. **No `concept-audit` entry.** The skill's own
`audit-dimensions.md:191-194` acknowledges this gap. **Fix:** add 4 rows for
`concept-audit`.

### P1-11. Fresh-install cycle (inter-step gates 9-12) NOT wired into CI. The exact gap the plan said it would close remains open.

Plan (`:320`): *"Gate 9-12 (the fresh-install cycle) is **new** - the existing
`ci.yml` builds + checks `sdist-clean` but never installs the just-built
package into a fresh project and runs `doctor`. This closes the gap that let a
broken `init-project` slip through."* Verified: `.github/workflows/ci.yml` has
zero references to `init-project`, `doctor`, or `uvx`. **Fix:** add a
`fresh-install-cycle` CI job.

### P1-12. `release.yml` upgrade-notes diff-base uses `HEAD~1 HEAD`, not the prior tag.

`release.yml:46` runs `git diff --name-only HEAD~1 HEAD -- templates/ schemas/`.
On a release with intermediate commits, `HEAD~1` walks back only one commit -
if the schema change is not in the tip commit, the diff comes up empty and the
upgrade-notes check is skipped. **Fix:** `BASE=$(git describe --tags --abbrev=0
HEAD 2>/dev/null || echo HEAD~1); git diff --name-only $BASE HEAD -- templates/
schemas/`.

### P1-13. `concept_audit` return shape diverges from plan spec - no top-level `score`.

Plan (`:257`): `concept_audit(root, profile) -> {passed, score, dimensions,
suggested_actions}`. Actual (`owledge_core.py:6006-6014`): per-dimension
`score` exists, top-level aggregate `score` does not. **Fix:** add top-level
`score: round(mean(all_dim_scores), 1)`.

### P1-14. Working tree has uncommitted dogfood export churn + untracked `exports/rag/` - PR is not clean.

`git status` shows 9 modified files under `internal/owledge/exports/` and
3 untracked files under `internal/owledge/exports/rag/`. **Fix:** commit
the regenerated exports as a `chore(dogfood)` commit (final commit in the PR).

## P2 - Polish (accept with documentation; deferred to FB-019)

### P2-15. Manifest author field named `upgraded_by`, not `author`.

Plan (`:185`) says "`--author` field." Code writes `upgraded_by` +
`upgraded_at` (`:714-716`). Functionally better. **Fix in Phase 2 (cheap):**
update `docs/upgrading.md` to say `upgraded_by`. No code change.

### P2-16. Additive-change awareness is metadata-only, not behavioral.

Plan (`:186`): *"`--dry-run` only reports informationally, doesn't alert"* when
`breaking: no|additive`. Code sets `alert_level` but does NOT suppress
`would_update`/`would_create`. **Deferred to FB-019.**

### P2-17. `dogfood_sync_check` compares ALL files under `templates/owledge/templates/`, not just `*-template.md`.

Code (`owledge_core.py:5455`) uses `source_dir.rglob("*")`. In practice
only templates live there today. **Deferred to FB-019.**

### P2-18. `concept-audit-fresh` gate checks ANY `concept-audit-*.md`, not specifically a self-audit by the skill.

Plan red-team #5 (`:330`) says the gate should "ALSO fail if skill's own last
self-audit is stale." **Deferred to FB-019.**

### P2-19. Report template path deviates from plan.

Plan (`:255`): `templates/owledge/decisions/concept-audit-YYYY-MM-DD.template.md`.
Actual: `templates/owledge/templates/concept-audit-template.md`. The
actual path matches the established convention. **Fix:** amend the plan text
(no code change). Done in `docs/v0.6.1-fix-up-plan.md`.

### P2-20. `upgrade_drift_check` uses `doctor --mode host` on a temp project with no host context.

`owledge.py:1827`. Low risk; the gate reports PASS today. **Deferred to
FB-019.**

### P2-21. Line numbers in the plan are stale.

Not a defect; expected after implementation. **No fix needed.**

## Conceptual-Layer Findings (the blindspot angle)

- **C-1.** The kit's self-audit loop is untested (P0-5). The skill ships, but
  the META test that proves it works is missing. The kit claims to be
  self-auditing but cannot prove it self-audits.
- **C-2.** "No parallel inventory" is violated by the manifest (P0-1). The
  manifest IS a parallel inventory, and it diverges from `init_project`'s
  actual copy set.
- **C-3.** "No writes" for manual mode is violated (P0-2). Conceptually a
  trust-boundary violation, not just a bug.
- **C-4.** The plan's "acceptance gates" are aspirational, not enforced
  (P0-4). The plan describes a QA regime that does not exist.
- **C-5.** The CHANGELOG does not describe the release (P1-9). Dimension 8
  scores 5.
- **C-6.** CI does not close the gap the plan said it would (P1-11). The fix
  is built but not installed where it would catch regressions.
- **C-7.** The skill documents its own gaps as deferred findings (P1-10).
  Intellectually honest but operationally a known-ship-with-known-gap.

## Score

| Persona | Score (0-100) | Reasoning |
| --- | --- | --- |
| Senior AI Agent Engineer | 70 | Core machinery real and correct; manifest divergence (P0-1) and manual writes (P0-2) are agent-trust-breaking. |
| Scalability / Systems Reviewer | 75 | One-way dogfood sync, lock, idempotency sound; loses points for un-wired CI (P1-11). |
| Security / Privacy Reviewer | 82 | Never-touch asserts before every write; loses points for manual-mode writes (P0-2). |
| UX / DX Adopter | 68 | `docs/upgrading.md` excellent; loses heavily for dead flags (P1-7), missing `concept-audit` doc (P1-10), CHANGELOG (P1-9). |
| QA Gate Owner | 45 | 0 of 19 named stress tests exist (P0-4); META missing (P0-5); `git apply --check` fails (P0-3); CI gap not closed (P1-11). |
| Compliance / Audit Reviewer | 72 | Decision traces, stamps, hashes present; loses points for unverified META + CHANGELOG under-reporting. |
| Product / Scope Strategist | 88 | Scope tight; loses points for shipping the skill without proving it works. |

**Composite (weighted): 71**

## Verdict

REVIEW.md verdict scale: 0-69 = block, 70-84 = revise, 85-94 = accept,
95-100 = promote-candidate.

**Composite: 71** -> nominal `revise`.

**Effective verdict: `block`** until P0-1 through P0-5 are resolved (REVIEW.md
blocking_conditions: "failed required QA gate" + "missing evidence for a
critical claim"); then `revise` for P1-6 through P1-14.

## Finding Triage

| Finding | Severity | Source Evidence | Root Cause | Task Needed |
| --- | --- | --- | --- | --- |
| P0-1 | P0 | `owledge.py:112-117,241-280` + empirical `init-project` | `HOST_SKILL_DIRS` + `_collect_kit_files` both incomplete | Fix in `docs/v0.6.1-fix-up-plan.md` Phase 1 |
| P0-2 | P0 | `owledge.py:570-571,612-620,675-708,2511-2514` | `dry_run = not args.apply` lets manual+apply write | Fix in Phase 1 |
| P0-3 | P0 | `owledge.py:644` + empirical `git apply --check` exit 128 | No `a/`/`b/` prefixes, no `diff --git` header | Fix in Phase 1 |
| P0-4 | P0 | repo-wide grep: 0 `def <test_name>` | Tests never written | Fix in Phase 3 |
| P0-5 | P0 | `owledge_core.py:5962-6014` + grep `>=4`: 0 hits | META test not enforced | Fix in Phase 3 |
| P1-6 | P1 | `owledge.py:1015-1044` | Plan claim not required (gate agnostic) | Retract in Phase 2 |
| P1-7 | P1 | `owledge.py:2388,2392,2512-2532` | Flags parsed, ignored | Fix in Phase 1 |
| P1-8 | P1 | `owledge.py:570-571` vs `:830` | `prompt_yes_no` not called | Fix in Phase 1 |
| P1-9 | P1 | `CHANGELOG.md:3-18` | Phase 5 + E6 omitted | Fix in Phase 2 |
| P1-10 | P1 | `docs/command-reference.md` grep | `concept-audit` row missing | Fix in Phase 2 |
| P1-11 | P1 | `.github/workflows/ci.yml` grep | Fresh-install cycle absent | Fix in Phase 4 |
| P1-12 | P1 | `release.yml:46` | `HEAD~1` not prior tag | Fix in Phase 2 |
| P1-13 | P1 | `owledge_core.py:6006-6014` | No top-level `score` | Fix in Phase 2 |
| P1-14 | P1 | `git status` | Export churn + untracked rag/ | Fix in Phase 2/6 |
| P2-15..P2-21 | P2 | various | Polish | Deferred to FB-019 |

## Success Metrics

| Metric | Baseline | Target | Measurement |
| --- | ---: | ---: | --- |
| Review score (composite) | 71 | >= 95 | Re-run this red-team after fix-up |
| Blocking findings (P0) | 5 | 0 | This report |
| Material findings (P1) | 9 | 0 | This report |
| Stress tests existing | 0 | 22 | `pytest tests/ --collect-only` |
| META test passing | no | yes | `pytest tests/test_skill_meta.py` |
| CI fresh-install cycle | absent | present + green | `.github/workflows/ci.yml` |

## QA Gates

| Gate | Command / Review | Pass Rule | Evidence Path |
| --- | --- | --- | --- |
| Contract tests | `python tools/owledge_core.py --project-root . test-contracts` | 0 failed checks | |
| Public docs | `python tools/owledge.py test public-docs --project-root .` | green | |
| Release trust | `python tools/owledge.py test release-trust --project-root .` | green | |
| Finalization gates | `python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports` | green | |
| Full test suite | `pytest tests/ -q` | all pass | |
| META test | `pytest tests/test_skill_meta.py::test_skill_finds_its_own_gaps_against_v060` | asserts >=4 of 6 | |
| Manual patch | `upgrade --dry-run --mode=manual` then `git apply --check` | exit 0 | |
| Fresh-install cycle | CI job `fresh-install-cycle` | green | |
| Working tree clean | `git status --porcelain` | empty | |

## Promotion Decision

- **Decision:** `block` (effective) until P0-1..P0-5 resolved; then `revise`
  for P1-6..P1-14; target `promote-candidate` (95+) after
  `docs/v0.6.1-fix-up-plan.md` completes.
- **Owner:** Kirk
- **Evidence:** this report + `docs/v0.6.1-fix-up-plan.md` + (after fix-up)
  regenerated `internal/owledge/exports/finalization-gates/latest.md`
  + `pytest tests/ -q` output.
- **Follow-up review date:** after `docs/v0.6.1-fix-up-plan.md` Phase 6
  completes.

## Residual Risks

- **R-1.** Test suite runtime. Target <60s. Mitigation: session-scoped
  fixture.
- **R-2.** META test pinning. Pin substrings from `audit-dimensions.md`
  worked examples.
- **R-3.** Session-continuity gate false positives on legacy plans. Gate
  enforces only on >=2 phase headings.
- **R-4.** The pyproject `version = "0.6.0"` bug (found during grounding)
  suggests release-trust may have a gap. New
  `test_pyproject_version_matches_version_file` closes it.