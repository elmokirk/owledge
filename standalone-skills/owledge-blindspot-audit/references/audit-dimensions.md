# Concept Blindspot Audit Dimensions

This is the full rubric for the 8-dimension concept audit. Dimensions 1-4 are
mechanical (run by the `concept_audit` function in
`tools/owledge_core.py`). Dimensions 5-8 are guided: the function emits a
checklist and the agent/user works through it, scores it, and records evidence.

Depth scales with `project_mode`:

| Mode | Depth |
| --- | --- |
| `poc` | Shallow — check existence only |
| `mvp` | + basic checks (commands run, files parse) |
| `side` | + consistency checks (cross-source agreement) |
| `saas` | + rollback, multi-env, SBOM, provenance, chaos drill, traceability matrix |

Scoring guide (applies to every dimension):

| Score | Meaning |
| --- | --- |
| 0 | Critical functionality missing |
| 5 | Partial — some checks fail but core functionality works |
| 7 | All critical checks pass, 1-2 warnings |
| 10 | All checks pass, no findings |

---

## Dimension 1 — Lifecycle & upgrade (mechanical)

**What it checks:** Does the kit have a working install → upgrade → doctor →
uninstall lifecycle? Is there a version stamp that survives across install
shapes? Does `kit-manifest.json` exist with a `kit_version` field?

**Mechanical checks:**

- `owledge upgrade --help` exits 0 (the subcommand exists).
- `owledge doctor --help` exits 0.
- `owledge init-project --help` exits 0.
- `kit-manifest.json` exists at the project root. In a fresh-init project it is
  written by `init-project`; in the Owledge source repo it is absent at root
  (the source repo is the producer, not a consumer) — the check passes if
  `init-project` writes it on a temp project.
- At `project_mode >= mvp`: `owledge upgrade --dry-run` runs without error on a
  temp-init'd project.
- At `project_mode >= saas`: look for rollback capability (a `--rollback` flag
  or equivalent). If absent, emit a `warning` finding.

**Depth scales:**

| Mode | Required |
| --- | --- |
| `poc` | `upgrade`/`doctor`/`init-project --help` exit 0 |
| `mvp` | + `upgrade --dry-run` on a temp project succeeds |
| `side` | + `kit-manifest.json` `kit_version` matches `VERSION` |
| `saas` | + rollback capability present |

**Scoring:**

- 10 = all checks pass, manifest present with matching version.
- 7 = commands exist, manifest present, version mismatch or 1 warning.
- 5 = a command is missing OR manifest is absent.
- 0 = no upgrade path at all.

**Worked example (v0.6.1 finding #1, now fixed):** Before E3, `init-project`
used `copy_file_if_missing` which silently skipped existing files. Re-running on
an installed project returned `skipped_existing` and updated nothing. No
`upgrade` subcommand existed among the 12 registered. This dimension would have
scored 5 (commands existed, but no upgrade path) and emitted an `error` finding:
"no `owledge upgrade` subcommand; `init-project` silently skips existing files."

**Worked example (v0.6.1 finding #2, now fixed):** Before E1, no
`KIT_VERSION`/`owledge_kit_version` stamp existed anywhere. `kit-manifest.json`
had no `kit_version` field. This dimension would have scored 5 and emitted an
`error` finding: "`kit-manifest.json` has no `kit_version` field."

**Worked example (v0.6.1 finding #4, now fixed):** Before E2/E4,
`source_vs_target_audit` audited `templates/owledge/` inside the repo, not
user projects. `doctor` could not see a broken global-layer reference. This
dimension would have scored 7 and emitted a `warning` finding: "drift detection
only covers the maintainer tree; `doctor` cannot see a broken global-link."

---

## Dimension 2 — Distribution integrity (mechanical)

**What it checks:** Are all install shapes (PyPI sdist, source checkout,
project-folder kit) consistent? Does `sdist-clean` pass? Does `release-trust`
pass (VERSION matches README badge and plugin manifests)?

**Mechanical checks:**

- `sdist_clean_check(root)` passes (no `internal/` leak, no decision-trace leak,
  required root docs and core trees present in the sdist).
- `release_trust_gate` equivalent: `VERSION` exists and the README badge
  matches.
- At `project_mode >= saas`: look for SBOM/provenance (e.g.
  `addons/trust-readiness-kit/` or a CycloneDX/SLSA file). If absent, emit a
  `warning` finding.

**Depth scales:**

| Mode | Required |
| --- | --- |
| `poc` | `VERSION` exists; README badge matches |
| `mvp` | + `sdist-clean` passes |
| `side` | + plugin manifest versions match `VERSION` |
| `saas` | + SBOM/provenance artifact present |

**Scoring:**

- 10 = sdist clean, release-trust passes, SBOM present.
- 7 = sdist clean, release-trust passes, no SBOM (warning).
- 5 = sdist or release-trust fails.
- 0 = no `VERSION` file and no badge match.

**Worked example:** In a healthy v0.6.0+ repo, `sdist-clean` passes and the
README badge matches `VERSION`. This dimension scores 10 at `mvp` and 7 at
`saas` (no SBOM yet). The `info` finding records that SBOM is absent but not
required below `saas`.

---

## Dimension 3 — Dogfood fidelity (mechanical)

**What it checks:** Does the maintainer dogfood tree mirror the product
templates? Is there a gate that catches drift before it ships?

**Mechanical checks:**

- `dogfood_sync_check(root)` passes (`drifted_files` empty).
- `internal/owledge/templates/` mirrors
  `templates/owledge/templates/` (covered by `dogfood_sync_check`).
- At `project_mode >= saas`: check for telemetry parity between dogfood and
  product installs. No current mechanism exists; emit an `info` finding.

**Depth scales:**

| Mode | Required |
| --- | --- |
| `poc` | `dogfood-sync-check` runs (may report drift) |
| `mvp` | + `dogfood-sync-check` passes (zero drift) |
| `side` | + skill-content hash gate (if present) |
| `saas` | + telemetry parity |

**Scoring:**

- 10 = zero drift, parity mechanism present.
- 7 = zero drift, no parity mechanism (info).
- 5 = drift detected but gate exists.
- 0 = no dogfood-sync gate at all.

**Worked example (v0.6.1 finding #5, now fixed):** Before E5, no gate compared
`internal/owledge/templates/` against
`templates/owledge/templates/`. Edits to product templates did not
propagate to dogfood. This dimension would have scored 0 and emitted an
`error` finding: "no dogfood-sync gate; product template edits do not propagate
to `internal/owledge/templates/`."

---

## Dimension 4 — Contract completeness (mechanical)

**What it checks:** Does every CLI subcommand have a test, a doc reference, and
a gate? Are `REQUIRED_DIRS`/`REQUIRED_FILES` complete?

**Mechanical checks:**

- `test_contracts(root)` passes (0 `failedChecks`).
- Count CLI subcommands in `tools/owledge.py` (parse the argparse subparsers).
  Check each has a doc reference in `docs/command-reference.md` (grep for the
  subcommand name).
- At `project_mode >= saas`: heuristic — count test functions vs CLI
  subcommands. If the ratio is low, emit a `warning` finding.

**Depth scales:**

| Mode | Required |
| --- | --- |
| `poc` | `test-contracts` runs |
| `mvp` | + `test-contracts` passes (0 failed) |
| `side` | + every CLI subcommand has a `command-reference.md` entry |
| `saas` | + every public API has a test |

**Scoring:**

- 10 = contracts pass, every subcommand documented, every API tested.
- 7 = contracts pass, 1-2 subcommands undocumented.
- 5 = contracts fail.
- 0 = no contract check exists.

**Worked example:** Adding the `concept-audit` subcommand to `tools/owledge.py`
requires a matching entry in `docs/command-reference.md` (out of scope for this
skill's own implementation; tracked as a `side`-depth finding if absent). The
`test_contracts` gate enforces `REQUIRED_DIRS`/`REQUIRED_FILES` for the new
skill folder, so a missing skill file fails this dimension at `mvp`.

---

## Dimension 5 — Cross-layer integrity (guided)

**What it checks:** Does the global layer link work? Are never-touch files
respected? Is consent present when the global user-memory layer is enabled?

**Guided checklist:**

1. If `global-link.json` exists, does the linked path resolve and is it
   readable? Run `python tools/owledge_core.py --project-root . doctor` and
   inspect the `global-link` check.
2. Are the never-touch files (`OWLEDGE.md`, `AGENTS.md`, `CLAUDE.md`,
   `USER_CONTEXT.md`) byte-identical before and after an
   `upgrade --apply --mode=force-templates --yes`?
3. If the global user-memory layer is enabled, is there an explicit consent
   record (a `global-link.json` with a non-empty path counts)?
4. Does `USER_CONTEXT.md` stay private (not exported into shared RAG) unless
   explicitly approved?
5. Are PI Agent intelligence and Red Team evaluations treated as candidate
   artifacts (not canonical) until promoted?

**Depth scales:**

| Mode | Required |
| --- | --- |
| `poc` | n/a (skip) |
| `mvp` | work through items 1-2 |
| `side` | + items 3-4 |
| `saas` | + item 5 + consent audit log |

**Scoring:**

- 10 = all items pass with evidence.
- 7 = 1-2 items unresolved.
- 5 = global-link broken or never-touch violated.
- 0 = no cross-layer boundary defined.

**Worked example (v0.6.1 finding #4, now fixed):** Before E4, `doctor` could
not see a broken global-layer reference. This guided dimension would have
surfaced it via checklist item 1: "run `doctor`; the `global-link` check is
absent — a moved/unmounted global layer is invisible."

---

## Dimension 6 — Failure-mode coverage (guided)

**What it checks:** For each dependency, path, and consent boundary, what
breaks? Are the breakages enumerated per audience (maintainer, contributor,
end user)?

**Guided checklist:**

1. List the kit's external dependencies (Python stdlib only, per the
   bootstrap rule). For each, what happens if it is absent? (Should be nothing
   — the kit is stdlib-only.)
2. List the install paths (PyPI, source, project-folder kit, plugin adapter).
   For each, what breakage would a user see if `init-project` silently skipped
   files? (This is the v0.6.1 finding #1.)
3. List the consent boundaries (global user-memory, shared RAG export, PI
   promotion). For each, what is the failure mode if consent is missing?
4. For each audience (maintainer, contributor, end user), which failure modes
   are visible to them and which are silent?
5. At `saas`: run a chaos drill — delete `kit-manifest.json`, move the global
   layer, corrupt a template — and verify each is caught with a friendly
   error.

**Depth scales:**

| Mode | Required |
| --- | --- |
| `poc` | list the failure modes |
| `mvp` | + enumerate per install path |
| `side` | + enumerate per audience |
| `saas` | + chaos drill |

**Scoring:**

- 10 = every failure mode enumerated with a documented mitigation.
- 7 = most failure modes enumerated, 1-2 gaps.
- 5 = silent-skip or silent-drift failure mode exists with no detection.
- 0 = no failure-mode analysis exists.

**Worked example (v0.6.1 finding #1, now fixed):** `init-project`'s
`copy_file_if_missing` silently skipped existing files. The failure mode
"re-running init on an installed project updates nothing" was invisible to the
user. This dimension would have scored 5 and surfaced the silent-skip path.

---

## Dimension 7 — Conceptual coherence (guided)

**What it checks:** Is the glossary consistent across README, AGENTS, and
CHANGELOG? Are term frequency and synonyms stable? Do the same concepts use the
same words everywhere?

**Guided checklist:**

1. Build a glossary from `AGENTS.md`, `README.md`, and `CHANGELOG.md` headers.
2. For each term, count occurrences across the three files. A term that appears
   in only one file is a coherence risk.
3. List synonyms (e.g. "kit" vs "Owledge" vs "Owledge"). Are they
   used consistently or do they drift?
4. Check version strings: `VERSION`, `templates/owledge/README.md`
   version, `OWLEDGE.template.md` version, plugin `VERSION` files. Do
   they agree?
5. At `saas`: is there a cross-team term contract (a reviewed glossary file)?

**Depth scales:**

| Mode | Required |
| --- | --- |
| `poc` | glossary exists |
| `mvp` | + term-frequency count |
| `side` | + synonym audit |
| `saas` | + cross-team term contract |

**Scoring:**

- 10 = all version strings agree, glossary consistent, synonyms intentional.
- 7 = 1-2 version strings drift or 1 synonym mismatch.
- 5 = multiple version strings disagree.
- 0 = no shared vocabulary across the three files.

**Worked example (v0.6.1 finding #3, now fixed):** Before E1, `VERSION`=0.6.0,
`templates/owledge/README.md`=0.4.0,
`OWLEDGE.template.md`=0.1.0 - four independent version strings. This
dimension would have scored 5 and surfaced the drift via checklist item 4.

---

## Dimension 8 — Self-description accuracy (guided)

**What it checks:** Do README, AGENTS, and CHANGELOG claims match actual
behavior? Is there a self-audit loop (this skill)?

**Guided checklist:**

1. List every claim in `README.md`'s first screen (commands, install shapes,
   platform support). For each, run the command or check the file. Does the
   claim hold?
2. List every "Owledge does X" statement in `AGENTS.md`. For each, does the
   behavior match?
3. List every `##` heading in `CHANGELOG.md`. For each, does the described
   change actually exist in the codebase?
4. Is there a skill that stress-tests the kit's own concepts (this one)? If
   absent, this is a self-description gap — the kit claims to be self-auditing
   but has no self-audit loop.
5. At `saas`: build a traceability matrix (claim → file → test → gate).

**Depth scales:**

| Mode | Required |
| --- | --- |
| `poc` | spot-check 3 README claims |
| `mvp` | + check every README first-screen claim |
| `side` | + check every AGENTS "Owledge does X" statement |
| `saas` | + traceability matrix |

**Scoring:**

- 10 = every claim holds, self-audit loop present.
- 7 = 1-2 claims drift.
- 5 = a claim is false or the self-audit loop is absent.
- 0 = no claims map to behavior.

**Worked example (v0.6.1 finding #6, now fixed by this skill):** Before Phase 5,
no skill stress-tested the kit's own concepts. The kit described itself as
self-curating but had no self-audit loop. This dimension would have scored 5
and surfaced the gap via checklist item 4: "no conceptual audit loop exists."
