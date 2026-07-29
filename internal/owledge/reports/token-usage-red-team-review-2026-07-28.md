---
id: token-usage-red-team-review-2026-07-28
type: red-team-review
title: "Token / Usage Waste — RED TEAM Review of the Long-Horizon Workflow"
status: complete
date: 2026-07-28
tenant: local
customer: local
project: owledge-standalone
scope: v0.7.0 (shipped) + v0.7.1 / OW-071 (in progress)
method: 4 finder subagents + 4 QA-verifier subagents (adversarial, re-read cited code)
---

# Token / Usage Waste — RED TEAM Review

> **Goal of owledge:** reduce token usage overall — development **and** deployment must be token-efficient (load only the necessary parts, maintain maximum quality). This review finds where the long-horizon workflow drains usage beyond what's needed, **without sacrificing quality or auditability**.
>
> **Status:** read-only review. No repo files were modified. The paused Codex `/goal` run on OW-071-13 is untouched and can resume exactly as before.

---

## 1. Executive summary

A swarm of 4 finder subagents (runtime, long-horizon skill, control-plane data-shape, product templates) plus 4 adversarial QA verifiers audited the last two long-horizon executions (**v0.7.0** shipped, **v0.7.1 / OW-071** in progress) and the workflow structure.

**The single most important finding (QA-corrected):** your `/goal` usage drain is **narrower and sharper** than the raw finder output suggested. The real resume contract (`CONTROL-PLANE-POLICY.md:36-46`, `ALIGNMENT-PROTOCOL.md:109`) loads **only**:

```
RUN-STATE.yaml  +  GOAL.md  +  CONTROL-PLANE-POLICY.md  +  ALIGNMENT-PROTOCOL.md
  + active ticket row  +  active gate  +  directly-referenced evidence manifests
```

The **plan and checklist are NOT loaded on resume** (loading the full plan is an explicit policy violation); QA/review reports are archived. So the **per-resume token drain is concentrated in `RUN-STATE.yaml` (loaded in full every resume) + the 3 unchanged control docs**. Everything else is archived storage or write-time/generation cost.

**Consequence for effort allocation:**
- **Runtime (Python tools):** 13 gaps found, but QA confirmed **only 1** (`run_gate` error-payload cap) cuts per-session tokens; the other 12 are CPU/IO/disk hygiene.
- **Long-horizon skill:** 8 gaps; **3 are real per-resume token drain** (delta-load control docs, RUN-STATE slice, handoff-first recovery).
- **Control-plane data-shape:** the live drain is **in-file duplication inside `RUN-STATE.yaml`** (findings block, `last_completed_actions`, `last_commands`). Cross-file duplication (plan/checklist/reports) is archived, not a resume cost.
- **Product templates:** 10 gaps, all **future-project only** (don't touch the current Codex drain) — except skill triplication, which has already drifted in this repo.

**Conservative win:** the 7 dogfood fixes in §9 save **~8–20k tokens per `/goal` resume**, with auditability fully preserved.

---

## 2. Context & scope

| | v0.7.0 (shipped) | v0.7.1 / OW-071 (in progress) |
|---|---|---|
| Plans | 8 plan files | 5 plan files (incl. 20 KB v1 master plan) |
| Checklists | 7 (~38 phases) | 5 (8 orchestration phases) |
| Control plane | flat workpackages + decision trace | dedicated workpackage dir, 11+ control files, 32 KB `RUN-STATE.yaml` |
| Evidence | benchmark results, decision trace | `evidence/OW-071-{01,02,03}/` manifest+review pairs |
| Reflections | sparring + red-team PR doc | 4 `docs(phase): reflect...` commits + 6 QA/red-team reports |

The v0.7.1 execution carries materially heavier control-plane scaffolding per phase than v0.7.0 — a structural observation that motivated this review.

**Root cause (one sentence):** the workflow treats every finding, decision, SHA, and command list as a row that must be **copied into every layer it touches** (manifest → integration-review → QA report → rereview report → `RUN-STATE` → checklist reflection → release update), so the same text is written and re-loaded 3–5×.

---

## 3. The QA-corrected drain picture (read this first)

The early finder rounds overstated several drains by assuming the plan, checklist, and QA reports are loaded each `/goal` resume. **They are not.** The QA gate re-read `CONTROL-PLANE-POLICY.md:36-46` and confirmed the resume load set is the narrow one above.

| Artifact | Produced by | Loaded on /goal resume? | Drain type |
|---|---|---|---|
| `RUN-STATE.yaml` (32 KB, in-file duplication) | current v0.7.1 run | **YES (in full)** | **Active per-session token drain** |
| `GOAL.md` + `CONTROL-PLANE-POLICY.md` + `ALIGNMENT-PROTOCOL.md` | control plane | **YES (unchanged docs re-read every session)** | **Active per-session token drain (fixable via delta-load)** |
| Active ticket row + active gate + referenced evidence manifest | per phase | **YES** | Necessary (right-sized already) |
| 28 export dirs (~175 KB) + finalization `latest.md` re-emit ×4 | current run | No | Generation-cost waste (rebuilt each finalization) |
| Plan ↔ checklist duplicate (18 KB) | current run | **No (policy forbids loading plan)** | Archived storage, not resume drain |
| QA / rereview reports (findings re-embedded) | current run | No (archived) | Archived storage |
| 2 stale compiled snapshots (2026-06-19, 4× bullet bug) | previous v0.7.0 | No | Disk leftover, latent |
| 8-file decision-trace stub (2026-06-21) | previous v0.7.0 | No | Disk leftover |

---

## 4. Runtime gaps — owledge as a runtime (13 found)

**Yes, there are clear runtime gaps.** QA verdicts below. Critical nuance: **only #2 reduces per-session tokens the agent consumes**; #1, #3–#13 are CPU/IO/disk efficiency (still valuable — faster gates → fewer agent loop iterations during dev/deploy — but not direct token drain).

| # | Gap (file:line) | QA verdict | Drain | Fix (audit-safe) |
|---|---|---|---|---|
| 1 | `finalization_gates` re-reads every memory file 7–10× (`owledge.py:2837-2844`; each gate calls `load_memory_records`) | CONFIRMED | CPU/IO | shared mtime+size-keyed record cache across gates ✅ |
| 2 | `run_gate` embeds full JSON payload in `error`, persisted to `latest.json` AND `latest.md` (`owledge.py:2334-2343`, `2910-2916`) | CONFIRMED | **Per-session tokens (~2-5k/failed gate)** | cap error to `{passed,failed,total,first_failings[:5]}` + sidecar full payload (**sidecar mandatory** for audit) ✅ |
| 3 | `build_context_pack_markdown` loads full content to score 2KB (`owledge_core.py:1576`, `:1534`,`:1634`) | PARTIAL | IO/RAM | metadata-only loader — **QA: as-stated changes scoring semantics** ⚠️ needs body-aware design |
| 4 | `load_memory_records` always computes `sha256_file` even when unused (`owledge_core.py:1995`) | CONFIRMED | CPU | lazy `source_hash` / `include_hash=False` ✅ |
| 5 | `build_memory_index` full + incremental back-to-back (`owledge.py:2840-2841`) | CONFIRMED | CPU/IO | incremental first, full only on missing/corrupt manifest ✅ |
| 6 | `public_docs_gate`/`release_trust_gate` re-read same files repeatedly (`owledge.py:1171,1188,1210,1248,1256`) | CONFIRMED | CPU/IO | read-once-into-local-var + shared read cache ✅ |
| 7 | `export_lightrag` re-reads the RAG jsonl it just wrote (`owledge_core.py:2961-2970`; rows already in memory `:2896-2905`) | CONFIRMED | disk/IO | `export_rag_documents` returns in-memory `rows` for reuse ✅ |
| 8 | `build_context_pack` reads full text before budget check (`owledge_core.py:1496-1504`) | PARTIAL | IO | **QA: naïve `os.path.getsize` breaks multibyte (bytes vs chars)** ⚠️ needs char-aware stat |
| 9 | `close_runtime_session` parses every event as JSON to count + 5 prompts + tool-names (`owledge_core.py:5044`) | PARTIAL | CPU/RAM | single streaming pass (also needs last_event + append) ✅ |
| 10 | `validate_v1_delivery_plan` calls `section()` twice per aligned ticket (`validate_v1_delivery_plan.py:263`,`:328`) | CONFIRMED | CPU | memoize `section()` by `(ticket_text, ticket_id)` ✅ |
| 11 | `validate_benchmark_baseline` re-hashes then re-reads same reference files (`validate_benchmark_baseline.py:285-301`) | CONFIRMED | CPU/IO | hash the in-memory bytes after a single read ✅ |
| 12 | `compliance_doctor` full content+hash load for 4 metadata fields (`owledge_core.py:2603`) | CONFIRMED | CPU/IO | metadata-only loader for this check ✅ |
| 13 | `audit_retention`/`scan_sensitive_data`/`validate_memory` 3 independent passes (`owledge_core.py:2058, 2212-2222, 2011-2018`) | CONFIRMED | disk/IO | shared loader/cache (covers #1) ✅ |

**Top runtime fixes:** (a) **#2** — the only real per-session token cut; (b) **#1 + #13** — shared cache (biggest wall-clock win); (c) **#7** — reuse in-memory export rows.

---

## 5. Long-horizon skill gaps (8 found; 3 real per-resume drain)

**Yes, the findings relate directly to the long-horizon skill.** QA separated per-resume drain from write-time cost.

| # | Gap (file:line) | QA verdict | Real per-resume drain? | Fix (audit-safe) |
|---|---|---|---|---|
| 1 | Resume prompt loads 5 named control docs every session, no delta/SHA mechanism (`ALIGNMENT-PROTOCOL.md:109`) | CONFIRMED | **YES ~1-3k** | hash-delta load via `RUN-STATE.session.last_control_sha`; load only changed docs ✅ |
| 2 | "Read current run state" = whole `RUN-STATE.yaml`, not active slice (`SKILL.md:26-27`; `modes.md:142`) | CONFIRMED | **YES ~0.5-2k** | slice to active-version section + `active_slice:` anchor ✅ |
| 3 | Reflection forces all 11 headings + explicit `None` for empty registers (`ALIGNMENT-PROTOCOL.md:44-58,58,76-77`; template `:114-144`) | PARTIAL | gate-only re-read (~0.1-0.3k) | omit empty headings + `## Omitted Sections` list ⚠️ preserve "no silent omission" rule |
| 4 | Every finding carries full 9-field schema AND duplicated into version update (`ALIGNMENT-PROTOCOL.md:69-73,75-76`) | PARTIAL | gate-only re-read (~0.5-2k) | pointer-form `F-NN — summary — ref:` ⚠️ update is user-facing approval doc; refs-only may weaken owner review |
| 5 | Same material routed to 3+ destinations (`modes.md:154-165`; `:75-76`) | PARTIAL | **write-time only** (resume prompt doesn't load routed artifacts) | write-once to canonical register + pointers ✅ |
| 6 | Context-pack restates `Accepted Decisions` + `Active Risks` (`context-pack-template.md:19-25`) | CONFIRMED | **write-time only** (packs generated per-task, not loaded on resume) | pointer lists ⚠️ isolated workers may need self-contained packs |
| 7 | Recovery re-derives full context, no "since last handoff" SHA slice (`modes.md:140-146`) | CONFIRMED | **YES ~1-4k** | read `.owledge/handoffs/<latest>` first; SHA-gate the 5 items ✅ |
| 8 | Step 2 re-inspects all 6 index types every session (`SKILL.md:28-29`; `modes.md:22-24`) | CONFIRMED | mode-conditional (~0.5-2k) | gate step 2 by mode (skip for ticket-execution/recovery unless ticket refs an idea) ✅ |

**Top skill fixes:** (a) **#1** delta-load control docs (largest per-resume hit, every resume); (b) **#7** handoff-first recovery (most frequent resume scenario); (c) **#2** RUN-STATE slice.

---

## 6. Control-plane data-shape gaps (8 found; live drain is in-file)

QA confirmed protocol docs (`CONTROL-PLANE-POLICY.md`, `ALIGNMENT-PROTOCOL.md`, `ORCHESTRATION-PROTOCOL.md`) contain **no** commit SHAs and **no** test/gate counts — the drain is `RUN-STATE.yaml` ↔ evidence manifests ↔ QA reports, not protocols. The live resume drain is the **in-file** duplication inside `RUN-STATE.yaml`; cross-file duplication (plan/checklist/reports) is archived storage.

| # | Gap (file:line) | QA verdict | Loaded on resume? | Fix (audit-safe) |
|---|---|---|---|---|
| 1 | Accepted commit SHA `86871c6…0a04d5` stored 5× (`RUN-STATE.yaml:289,359`; `integration-review.yaml:5`; rereview `:8,:20`; `checklist:75`) | CONFIRMED | RUN-STATE:289 yes; others archived | keep canonical SHA in `integration-review.yaml`; others → short SHA + ref ✅ |
| 2 | Test/gate counts repeated 4–6× (103/103, 233, 11/11, score 155…) across RUN-STATE + manifests + reviews + plan/checklist | CONFIRMED (minor line imprecision) | RUN-STATE:392-396 yes; rest archived | counts canonical in per-ticket manifest; RUN-STATE references ✅ |
| 3 | Replay command lists duplicated 2–3× within one manifest (`commands` + `qa_handoff.required_replay`) | PARTIAL | prior-ticket manifests not referenced by active OW-071-13 | required_replay is a deliberate QA-handoff subset; dedup risks losing the explicit replay contract ⚠️ |
| 4 | Per-ticket findings (F-071-12/13/14/15…) duplicated in RUN-STATE + worker manifest + QA reports | CONFIRMED | RUN-STATE findings block yes; reports archived | RUN-STATE keeps `id/status/source/see:<manifest>`; manifest is canonical body ✅ |
| 5 | Decisions D-071-07/10/11 restated in `last_completed_actions` (NOT verbatim — summary phrasing) | PARTIAL | **both in RUN-STATE → loaded every resume** | `last_completed_actions` → decision-ID refs ("D-071-07 applied") ✅ |
| 6 | Plan ↔ checklist duplicate phase content (SHAs + counts) | CONFIRMED | **No (both archived)** | checklist references plan's Resume State; low-priority (archived) ✅ |
| 7 | RUN-STATE `last_commands` (11) vs `checkpoint.passed_commands` (6) overlap | **REJECTED** | — | no literal overlap; internal `last_commands` redundancy (3 finalization runs) is a separate minor issue |
| 8 | Worker manifest `PENDING_COHESIVE_WORKER_COMMIT` placeholder + binding note duplicated | CONFIRMED | manifest loaded only if referenced by active ticket | placeholder is a **deliberate auditability feature**; dedup low-priority, preserve binding contract ⚠️ |

**Top data-shape fixes (live resume drain):** (a) slim the `findings` block (220 lines) to `id+status+ref`; (b) compress `last_completed_actions` to decision-ID refs; (c) trim `last_commands` to current-ticket-relevant.

---

## 7. Product template gaps (10 found; all future-project only)

QA confirmed every gap below lives in `templates/`/`addons/`/build code and affects **future bootstrapped projects, not the current Codex drain** — except #8, which has already drifted in this repo.

| # | Gap (file) | QA verdict | Fix |
|---|---|---|---|
| 1 | Two frontmatter dialects; `memory_id` style forces ~27-31 empty YAML lines per memory doc | CONFIRMED | converge onto slim `id/type` dialect (~9 lines) ✅ |
| 2 | `handoff-packet-template.md` vs `handoff-template.md` ~90% duplicate (4/5 headers identical) | PARTIAL | merge into one `handoff-template.md` with `handoff_kind:` enum ✅ |
| 3 | `gate-report-template.md` vs `qa-gate-template.md` overlap, no cross-ref | CONFIRMED | make `qa-gate` canonical; deprecate `gate-report` ✅ |
| 4 | `context-pack-template.md` restates `Accepted Decisions` + `Active Risks` | CONFIRMED | replace with source pointers ✅ |
| 5 | `compiled-memory-template.md` Retrieval Header restates its own frontmatter | CONFIRMED | drop the body section ✅ |
| 6 | `project-execution-snapshot-template.md` re-aggregates 9 sections already in epic/workpackage/gate | PARTIAL | pointer-style snapshot ✅ |
| 7 | `workpackage-template.md` + `phase-tasklist-template.md` share identical 3-line checklist | CONFIRMED | single shared checklist ✅ |
| 8 | **3 identical SKILL.md copies; build duplicates each into `target/skills` + `target/.agents/skills`; mirror gate checks `owledge-principles` only** (`owledge.py:1824`) | CONFIRMED + drift already real | single-source; extend `mirror-identical` to all 8 skills; drop `.agents/skills` dupe ✅ |
| 9 | `trace-profile.md` ships 8-node default chain steering toward 8 stub docs | PARTIAL | change default chain to `decision+evidence+lesson` (3); full 8-node as optional ⚠️ |
| 10 | `.owledge/` ships 56 templates + 20 schemas flat, no core/optional split (`build_project_folder_kit.py:283`) | CONFIRMED | core/optional split via addons ✅ |

**Verified negative finding:** the 8-file-per-decision stub is **not** baked into shipped templates — only `trace-profile.md` ships; the dogfood's 9-file explosion was a behavioral choice, not a template mandate.

---

## 8. What NOT to change (preserve for quality/audit)

- **Stable finding IDs + evidence SHAs + gate independence + QA ≠ owner + owner-alignment stop.** The pointer-based store preserves all of these — it changes *where text lives*, not *what's auditable*.
- **The 11-heading version-update doc** (`ALIGNMENT-PROTOCOL.md:112-144`) is the owner-facing alignment artifact; keep its completeness contract there. Delta-only rules apply to **per-phase reflections**, not this doc.
- **Validator enforcement at gates** — keep `validate_v1_delivery_plan.py` running at gates; just stop feeding its full multi-doc output back into context.
- **Worker manifest `PENDING_COHESIVE_WORKER_COMMIT` placeholder** — deliberate non-self-referential proof; preserve the binding contract.
- **`qa_handoff.required_replay`** — a deliberate QA-handoff subset; dedup carefully or not at all.

---

## 9. The real drain — ranked fixes that cut per-resume tokens

These are the **only** changes that directly shrink Codex `/goal` usage. All are dogfood (`internal/`) or skill-rule edits, all audit-safe.

| # | Fix | Source | Where | Est. save/resume |
|---|---|---|---|---|
| R1 | Slim `RUN-STATE.yaml` `findings` block (220 lines) → `id + status + manifest ref` | control-plane QA | `internal/.../RUN-STATE.yaml:16-236` | **~4-6k** |
| R2 | Compress `last_completed_actions` → decision-ID refs | control-plane QA | `RUN-STATE.yaml:353-363` | ~0.5-1k |
| R3 | Trim `last_commands` (11) → current-ticket-relevant | control-plane QA | `RUN-STATE.yaml:368-379` | ~0.5k |
| R4 | Delta/SHA-gated load of the 3 control docs | skill #1 | `ALIGNMENT-PROTOCOL.md:109` | ~1-3k |
| R5 | `RUN-STATE` active-slice load | skill #2 | `SKILL.md:26-27`, `modes.md:142` | ~0.5-2k |
| R6 | Handoff-first SHA-gated Recovery | skill #7 | `modes.md:140-146` | ~1-4k |
| R7 | Cap `run_gate` error payload + sidecar (failed-gate triage reads) | runtime #2 | `owledge.py:2334-2343` | ~2-5k per failed gate |

**Conservative total: ~8–20k tokens per `/goal` resume**, auditability preserved.

**NOT worth chasing for per-resume tokens** (QA downgraded — storage/audit hygiene, fine to fix later, won't move the Codex number): plan↔checklist duplicate (archived), QA report duplication (archived), context-pack decision restatement (write-time), reflection 11-heading mandate (gate-only ~0.1-0.3k), artifact multi-destination routing (write-time), product template gaps 1–7,9,10 (future-project only).

---

## 10. Recommended application order (for Codex integration)

**Phase A — lowest risk, biggest per-resume win (pure data-shape, no tooling changes):**
1. R1 + R2 + R3 — slim `RUN-STATE.yaml` in-file duplication into pointer/index form.
2. R6 — rewrite Recovery read list (`modes.md:140-146`) to handoff-first + SHA-gated.

**Phase B — skill-rule + one runtime change (still dogfood, audit-safe):**
3. R4 — add `RUN-STATE.session.last_control_sha`; update resume prompt (`ALIGNMENT-PROTOCOL.md:109`) to delta-load.
4. R5 — slice RUN-STATE in Universal Workflow step 1 + Recovery item 1.
5. R7 — cap `run_gate` error payload + mandatory sidecar.

**Phase C — runtime hygiene (wall-clock, not tokens; do when convenient):**
6. runtime #1 + #13 — shared record cache. #7 — reuse export rows. #4, #10, #11, #12 — lazy hash / memoize / single-pass.

**Phase D — product (future-project leverage, separate from your Codex drain):**
7. template #8 (skill single-source + mirror gate — drift is already real, fix soon regardless).
8. template #1, #2, #3, #10 — frontmatter convergence, merge handoff/gate templates, core/optional split.

**Gate re-validation after each phase:** `python tools/validate_v1_delivery_plan.py` + `python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports`.

---

## 11. Verification

1. `python tools/validate_v1_delivery_plan.py` — plan/ticket/gate structure valid.
2. `python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports` — gates green.
3. `python tools/owledge_core.py --project-root . doctor --mode kit` — product health.
4. Resume a `/goal` session and compare loaded-context token count before vs after — the direct measure of drain reduction.

---

## 12. Swarm provenance & QA verdicts

- **Finders:** runtime (13 gaps), long-horizon skill (8), control-plane data-shape (8), product templates (10).
- **QA gate:** 4 adversarial verifiers re-read every cited file.
  - Rejected 1 control-plane claim (#7 — no `last_commands`/`passed_commands` overlap).
  - Downgraded 8 claims to PARTIAL (3 runtime, 2 skill, 2 control-plane, 3 product) — mostly "fix as-stated breaks semantics/multibyte/scoring" or "overstated as per-resume when actually write-time/gate-only."
  - Corrected the resume-load contract: **plan + checklist are NOT loaded on /goal resume** (policy `CONTROL-PLANE-POLICY.md:36-46`).
  - Confirmed runtime drain is mostly CPU/IO — **only runtime #2 = per-session tokens**.
  - Confirmed all 10 product gaps are future-project only; skill triplication (#8) has already drifted.

---

## 13. Addendum (2026-07-28) — `/goal` runtime evolution corrections

This review was authored against the Codex `/goal` resume contract as it existed before Apr 30 2026. Both `/goal` runtimes have since shipped changes that reshape (not invalidate) several findings above. A QA-gated re-audit (3 finders + 1 skeptic verifier, all re-reading cited files) confirmed the corrections below; the original §1–§12 findings stand as the cold-resume baseline.

**Current runtimes:**
- **Codex `/goal` v0.128.0** (Apr 30 2026): persisted goal state across restarts + laptop sleep; native auto-compact (`model_auto_compact_token_limit`); self-judged evidence-based completion; subagents, `/plan`, `/side`, `/fork`.
- **Claude Code `/goal` v2.1.139+** (May 11 2026): worker-vs-Haiku-JUDGE — a separate Haiku evaluator judges completion from the transcript and CANNOT run commands or open files; verifiable-command condition; `--resume`/`--continue` restores the goal but RESETS turn count + token baseline; plan mode + effort levels; `/loop`, stop hooks, Agent View.

**Verified corrections to the filed ticket OW-080-13 (ranked, 8 confirmed / 1 refuted):**

1. **Claude Code Haiku-judge portability (most material).** §11 Verify/evidence and gate G-080-B-CONTEXT Commands assumed a single command-running actor. Under Claude Code the Haiku judge cannot run commands or read sidecars — every acceptance property must be re-expressed as a verifiable command with transcript-visible output (capped + reconstructed payloads, equality digest + diff, REJECT results printed to the transcript). The owner-alignment stop must be verifiable by a command, not protocol assertion alone.
2. **R1 hash-delta needs a runtime branch.** Under Codex v0.128 warm resume, the 3 control docs are already in persisted context, so the unconditional `ALIGNMENT-PROTOCOL.md:109` "Read …" re-injects redundant double-bookkeeping; hash-delta doesn't catch "already in context." Fix: branch on `RUN-STATE.session.runtime_resume_model` — `persisted` (Codex) skips re-read when content is in context (hash-delta fallback); `reset_baseline` (Claude Code `--resume`) applies hash-delta as the primary saving every resume.
3. **R3 handoff-first needs a runtime branch + list reconciliation.** `modes.md:140-146` Recovery list (5 items) and `ALIGNMENT-PROTOCOL.md:109` resume list (different set) drift — a Recovery-triggered resume loads the union, not the intersection. Codex warm resume may already hold the handoff in-context (skip re-read); Claude Code `--resume` must read it mandatorily (baseline reset discards prior turn state).
4. **Token-delta metric is gameable under Claude Code `--resume`.** §11 step 4 and ticket Accept "before/after loaded-context token count" yields `after ≈ 0` because `--resume` resets the baseline. Fix: measure with a file-content tokenizer (`sum token_count(loaded_file_content)`), not harness-reported context tokens; report `cold_resume_drain` and `warm_resume_drain` separately.
5. **"8–20k tokens/resume" is the COLD-resume ceiling; warm Codex resume is materially smaller.** Under Codex v0.128 persistence + auto-compact + ~94% cache hit, R1/R2/R3 savings shrink on warm resume (the slimmed content is cache-resident). The cold/warm distinction is CONFIRMED; the specific "~0.5–3k warm" estimate is UNVERIFIED (must be measured with `model_auto_compact_token_limit` ON, not assumed). R1/R2/R3 effort should be calibrated against warm-resume savings.
6. **Single-runtime framing.** The ticket and this report were Codex-focused; Accept must explicitly require runtime-neutral pass on BOTH runtimes with evidence in each.
7. **Matrix row is Codex-shaped.** `model_profile: frontier_orchestrator` (free-form per `validate_v1_delivery_plan.py:88`, not an enum) maps to Claude Code effort `xhigh`/`max`; `qa_role: evaluation-reviewer` and `per_ticket_approval` approver differ per runtime (Codex worker-self-judge / Claude Code Haiku judge). A `runtime_mapping` note was added to the OW-080-13 matrix row.
8. **R2 needs a two-tier split, not a single slice (R2 is NOT obsolete).** Split RUN-STATE into `session_slice` (warm-resume minimum, <1KB) and `durable_state` (registers/SHAs/evidence/decisions, cold-resume only). Warm resume loads only `session_slice`; cold resume loads both.

**Refuted:** a suggestion to use Claude Code stop hooks / `/loop` / plan mode as alternative enforcement surfaces for R4/R7 — scope creep; the Haiku-judge portability fix (correction 1) already covers verification.

**Bottom line:** OW-080-13 is sound in core intent; it needs amendment, not a split. All amendments were applied to the ticket (`tickets/ALL-TICKETS.md#ow-080-13`), gate `G-080-B-CONTEXT` (`gates/ALL-GATES.md`), and the matrix row (`AGENT-EXECUTION-MATRIX.yaml`), and re-validated green. The R1–R7 drain targets remain correct as the cold-resume baseline; warm-resume savings must be measured per runtime at execution time.
- **No files modified.** This report is the only artifact written.

---

## 14. Addendum (2026-07-29) — 3-layer expert review: does the "token & usage efficient, load only essentials" core principle hold for expert agentic engineers / powerusers as a harness-integrated runtime?

> **Scope expansion.** §1–§13 audited the *dogfood drain* (Codex/Claude Code `/goal` resume cost). This §14 steps back to the *principle itself*: does Owledge's stated core principle — context- and token-efficiency by loading only what is essential — meet SOTA criteria for expert-level agentic engineers and powerusers when integrated natively into Claude Code, Codex, OpenCode, and peers? **Audit-safe append:** §1–§13 are preserved verbatim; this section is the only addition.
>
> **Method:** a 3-layer QA-gated subagent swarm — 3 filter agents (stated-concept / load-mechanics / prior-findings), 3 red-team agents (context-engineering, multi-harness-portability, token-economy), 1 synthesis agent that adjudicated conflicts and argued the ranked report. One post-synthesis investigation (RPT-16) was added after the user flagged a harness-acceptance friction. Findings carry stable IDs `RPT-NN`; refutations are listed so effort is not re-spent on them.

### 14.1 Verdict

**No — not yet, and the gap is structural, not cosmetic.** Owledge discovered and documented a genuine SOTA load contract *internally* (`CONTROL-PLANE-POLICY.md`, `ALIGNMENT-PROTOCOL.md`, the validator, gate-gated reflection, stable IDs + SHAs), but shipped only the *prose* of that contract to users and kept the *enforcement* in `internal/`. The shipped `templates/owledge/` runtime markets "load only essentials" while `build_context_pack` actually enforces a **size** cap (`budget_chars`, `excluded_sources` with `reason:"context_budget"`, tenant-boundary guard) with **no selection** contract — it globs up to 120 files first-fit and trims by bytes, never by relevance. The result:

- cold-resume drain is **real** (~16k tokens ≈ 8% of a 200k reasoning window at the zero-working-state moment),
- warm-resume win is **asserted but unmeasured** (no tokenizer pinned, no magnitude column),
- the 7-runtime portability claim is **instrumented for only 2**,
- the own dogfood **already violates** the AGENTS↔CLAUDE mirror invariant it mandates.

The auditable backbone (independent QA, gate-gated reflection, stable SHAs, canonical-vs-generated boundary) is strong enough that aggressive cuts are safe — but the contract those cuts must serve is **not yet shipped**.

### 14.2 The one structural problem

**The SOTA load contract was discovered and documented internally but never shipped.** Everything cascades from this asymmetry:

- The **Core Rule** ("Markdown is source of truth; plugins/skills are runtime bridges") lives in `CLAUDE.md` but is absent from `OWLEDGE.template.md` (a blank skeleton) → shipped users have no invariant to anchor on (RPT-9).
- The **"load only essentials" + "policy violation"** hard-stop lives in `CONTROL-PLANE-POLICY.md`, which is `internal/`-only → shipped users get a README "keep artifacts compact" line and a size cap, but **no selection contract** and no validator that rejects an out-of-contract prompt (RPT-1).
- The **alignment protocol** that brakes scope-creep is internal-only and its validator is hardcoded to the internal path → shipped users have no scope-creep brake (folded into RPT-1).
- The R1–R7 trims, per-version sharding, runtime-capabilities manifest, pinned tokenizer — none are shipped. They are dogfood artifacts.

Fix RPT-1 and the downstream findings become enforceable; fix downstream findings without RPT-1 and they remain internal-only optimizations that never reach the poweruser the runtime claims to serve.

### 14.3 Ranked findings

| ID | Lens | Sev | Claim | Recommendation |
|----|------|-----|-------|----------------|
| RPT-1 | CE | HIGH | Shipped runtime markets "load only essentials" but ships a SIZE contract with no SELECTION contract; alignment protocol + validator internal-only. | Ship `schemas/load-contract.schema.json` + `validate_context_pack_usage.py` (reject when consumed-path set ⊄ allow-list); bake alignment hard-stop into `templates/owledge/`. |
| RPT-2 | TE | HIGH | RUN-STATE grows O(releases×findings) append-only (~220 lines/22 F-071 + ~88/11 D-071); R5 trims per-entry size, **not count**. Unfiled: per-version sharding. | Shard `RUN-STATE.yaml` into a <2KB pointer manifest + `registers/<v>/` per-version files; load active-version register only. |
| RPT-3 | MH | HIGH | Tokenizer unspecified + warm-savings metric gameable; gate can ship green without proving the warm win. | Pin `tiktoken==X` / `encoding=o200k_base` in the gate; require `cold_resume_drain` AND `warm_resume_drain` magnitude columns; reject `warm="TBD"`. |
| RPT-4 | MH | HIGH | R-numbering collision (report R1=slim-findings vs ticket R1=delta-load) is a traceability-breaking permutation. | Renumber ticket to match report, or move to globally-unique IDs; add validator cross-check (report↔ticket R-set equality). |
| RPT-5 | TE | HIGH | Recovery union-loads two divergent resume read-lists and re-opens `BACKLOG.yaml` (~6k tok) via "backlog dependencies." | One-line spec fix: replace "backlog dependencies" with "backlog row for active ticket only" (pointer-form, not full file). |
| RPT-6 | MH | HIGH | `runtime_resume_model` is a 2-value field (persisted/reset_baseline) masquerading as an abstraction; "runtime-neutral" isn't. | Introduce `runtime-capabilities.yaml` {resume_model, judge_model, command_execution, auto_compact, tokenizer_id}; enum-source `runtime_resume_model` from it. |
| RPT-7 | MH | HIGH | OW-080-13 is a 2-runtime fix in a 7-runtime costume; PI Agents has no ticket/gate/fixture. | Reword `SKILL.md` into tiers: Tier-1 instrumented (Codex, Claude Code) / Tier-1 adapter (Hermes, OpenCode, generic-MCP) / prose-only (PI Agents); give Cowork its own matrix row; deliver a PI Agents fixture or strike from `SKILL.md`. |
| RPT-8 | CE | HIGH | AGENTS.md↔CLAUDE.md mirror mandated but **already violated** in the repo's own dogfood (47-line drift). | Generate both from one source in `build_project_folder_kit.py` + add a CI diff assertion. |
| RPT-9 | CE | MED-HIGH | Core Rule not propagated into shipped `OWLEDGE.template.md` (blank skeleton). | Bake Core Rule verbatim into `OWLEDGE.template.md` as a non-optional Invariants section. |
| RPT-10 | MH | MED | Report body §1/§9/§11 stale (Codex-only framing, "for Codex integration", gameable metric) never revised despite §13 addendum; cold/warm headline uncaveated. | Inline cold/warm caveat into §1 headline; add "Superseded by §13/§14" banners at §9/§11; amend OW-080-13 to fix body, not just append. |
| RPT-11 | TE | MED | `run_gate` full JSON error payload persisted to `latest.json` AND `latest.md`; sidecar may not be transcript-visible under Claude Code Haiku judge. | Guarantee the error sidecar is transcript-visible to the Haiku judge (R4/R7 cover payload; this closes visibility). |
| RPT-12 | CE | MED | Root `DESIGN.md` is a report-styling catalog, not architecture — name misleads. | Rename `DESIGN.md` → `REPORT_DESIGN.md`. |
| RPT-13 | TE | MED | R6/R7 leave 3 duplicate `finalization-gates` entries; cross-field "overlaps checkpoint.passed_commands" claim was refuted. | Dedup the 3 finalization-gates entries; keep R6/R7 scope; drop the cross-field claim. |
| RPT-14 | TE | MED-LOW | Haiku-judge transcript-flood risk from large gate payloads. | Add `validator --summarize` flag; tier below R1–R7. |
| RPT-15 | TE | MED-LOW | `ALL-TICKETS.md` (70KB) + `ALL-GATES.md` (22.8KB) monolithic — 92KB blast radius on misread. | Per-version split when v0.8.x lands; not urgent. |
| RPT-16 | MH | HIGH | Native harness integration half-built: external absolute path in hook command (`${CLAUDE_PLUGIN_ROOT}`) under global-plugin install prompts every fire; **no `.claude/settings.json` allow-list ships**; `resolve_cli` silently walks to an external checkout; **capture hooks exist, the `SessionStart` context-injection hook does not** — so "use Owledge without calling it manually" is only half-served. LLM re-issuance (kimi-k2.7-code) compounds it. | Ship project-local `.claude/settings.json` allow-list; offer project-local plugin install so `${CLAUDE_PLUGIN_ROOT}` resolves inside the project; guard `resolve_cli` behind `OWLEDGE_ALLOW_GLOBAL_KIT`; add a `SessionStart` context-injection hook (`inject-owledge-context.py`) emitting a compact capsule to stdout. |

### 14.4 Refuted / dropped (do not spend effort here)

- **"Gemini" runtime claim** — FILTER FABRICATION; "Gemini" appears nowhere in the repo. Drop entirely.
- **"No contract ships" overclaim** — a SIZE contract DOES ship (`build_context_pack` `budget_chars`, `excluded_sources`). The real gap is SELECTION, not SIZE. RPT-1 is narrowed; do not re-assert "no contract."
- **SKILL.md step-2 6-index inspection** — non-issue: fires only in planning modes, reads index entries not full artifacts.
- **C10 CPU-only / `section()` double-call** — refuted as a token-economy survivor; pure CPU.
- **Cross-field "overlaps checkpoint.passed_commands"** — QA already rejected (§6 #7); do not re-litigate.
- **88.36%/83.54% headline as generalization evidence** — policy correctly forbids using the fixture as evidence for general repos; keep the disclaimer, do not promote the headline.
- **"Project-scoped forces global scope"** (the user's original RPT-16 framing) — REFUTED: `init-project` is self-contained by default (`tools/owledge.py:558-627`), `--link-global` is opt-in, `doctor` reports a missing global link as `info` not error (`owledge_core.py:2371-2387`). The friction is real but localized — see RPT-16.

### 14.5 SOTA target architecture (end-state)

1. **<2KB `RUN-STATE.yaml` pointer manifest** — only `{active_version, active_ticket, active_gate, register_index, last_checkpoint_sha}`. No findings/decisions bodies. (Closes RPT-2.)
2. **Per-version registers** at `registers/<v>/{findings,decisions,tickets,gates}.yaml` — load **active-version only** on cold resume; historical versions pointer-reachable, not auto-loaded. (Closes RPT-2, RPT-15.)
3. **`runtime-capabilities.yaml`** at the kit root — `{resume_model, judge_model, command_execution, auto_compact, tokenizer_id}` per runtime. `runtime_resume_model` becomes an enum sourced from it, not a 2-value free-form string. (Closes RPT-6.)
4. **`schemas/load-contract.schema.json` + `validate_context_pack_usage.py`** — REJECT a context pack when the consumed-path set ⊄ the contract allow-list. `build_context_pack` keeps its size cap but adds a selection layer. (Closes RPT-1.)
5. **Pinned tokenizer** in the gate — `tiktoken==X`, `encoding=o200k_base`; emit `cold_resume_drain` and `warm_resume_drain` magnitude columns; `warm="TBD"` fails the gate. (Closes RPT-3.)
6. **Canonical-source mirror generator** in `build_project_folder_kit.py` — `AGENTS.md` and `CLAUDE.md` generated from one source; CI diff assertion blocks drift. `OWLEDGE.template.md` ships a non-optional Invariants section carrying the Core Rule verbatim. (Closes RPT-8, RPT-9.)
7. **Alignment hard-stop** shipped to `templates/owledge/` (not just `internal/`). (Folded into RPT-1.)
8. **Tiered runtime matrix** in `SKILL.md` — Tier-1 instrumented / Tier-1 adapter / prose-only, with PI Agents either fixture-backed or struck. (Closes RPT-7.)
9. **Globally-unique R-IDs** (or renumbered ticket) + validator cross-check that report R-set == ticket R-set. (Closes RPT-4.)
10. **Native, self-contained harness integration** — project-local `.claude/settings.json` allow-list + project-local plugin install + `resolve_cli` env-var guard + `SessionStart` context-injection hook, so Owledge works as a structured layer (project and global scoped) without manual calls and without per-run acceptance prompts. (Closes RPT-16.)

This end-state is what makes "load only essentials" an **enforceable contract** instead of marketing.

### 14.6 Actionable workstreams

**WS-A — Ship the Selection Contract** (amends OW-080-13 + shipped-template change): add `schemas/load-contract.schema.json` + `validate_context_pack_usage.py`; bake the alignment hard-stop into `templates/owledge/`; ship the Core Rule verbatim into `OWLEDGE.template.md` Invariants section. Closes RPT-1, RPT-9 (structural root). Folds RPT-5 (one-line "backlog row, not backlog file" fix in the shipped recovery contract). Non-interference: touches `templates/owledge/` and the OW-080-13 ticket only — does not touch `RUN-STATE.yaml`, the active plan, or paused Codex OW-071-13.

**WS-B — Per-Version Register Sharding** (NEW ticket, **blocked on OW-071-09** per owner decision): refactor `RUN-STATE.yaml` into a <2KB pointer manifest + `registers/<v>/` per-version files; load active-version only. Closes RPT-2, defers RPT-15. Non-interference: new ticket, new schema; must **not** mutate the live `internal/owledge/.../RUN-STATE.yaml` used by paused OW-071-13 — ship behind a flag; migrate dogfood in a separate phase.

**WS-C — Pin Tokenizer + Honest Gate** (amends OW-080-13): pin `tiktoken==X` / `o200k_base`; add `cold_resume_drain` + `warm_resume_drain` magnitude columns; reject `warm="TBD"`; inline the cold/warm caveat into §1 headline; add "Superseded by §13/§14" banners at §9/§11. Folds RPT-11 (transcript-visible sidecar) and RPT-13 (dedup finalization-gates). Closes RPT-3, RPT-10, RPT-11, RPT-13. Non-interference: amends the gate harness and OW-080-13 report body only.

**WS-D — Capabilities Manifest + Runtime Tiers** (NEW ticket): introduce `runtime-capabilities.yaml`; enum-source `runtime_resume_model` from it; reword `SKILL.md` into Tier-1 instrumented / Tier-1 adapter / prose-only; deliver a PI Agents fixture or strike from `SKILL.md`; give Cowork its own matrix row. Closes RPT-6, RPT-7. Non-interference: new file + `SKILL.md` edit only.

**WS-E — Mirror Generator + R-ID Hygiene** (amends OW-080-13 + build-tooling change): generate `AGENTS.md`/`CLAUDE.md` from one source in `build_project_folder_kit.py`; add a CI diff assertion; renumber the OW-080-13 ticket R-set to match the report (or move to globally-unique IDs) + validator cross-check. Closes RPT-8, RPT-4. Non-interference: build-tooling + OW-080-13 ticket body only; the repo's existing 47-line drift is reconciled in a separate dogfood commit, the generator prevents *future* drift.

**WS-F — Native Hook Integration, Self-Contained Project Scope, No Manual Calls** (NEW ticket): (1) ship a project-local `.claude/settings.json` allow-list alongside `init-project --include-plugin-adapter`; (2) document/offer a project-local plugin install so `${CLAUDE_PLUGIN_ROOT}` resolves inside the project — update `docs/install-plugin.md:67-80`; (3) guard `resolve_cli` (`capture-claude-event.py:48-57`) behind `OWLEDGE_ALLOW_GLOBAL_KIT`, fail-soft with a "run init-project" doctor hint otherwise; (4) add a `SessionStart` context-injection hook (`inject-owledge-context.py`) reading project-local `OWLEDGE.md` + `.owledge/indexes/memory-index.jsonl` and emitting a compact capsule to stdout — promote the registered idea `internal/owledge/ideas/pre-plan-idea-concept-harness-hooks.md`. Closes RPT-16. Non-interference: new files + docs + plugin-adapter edits only — pure additive shipped-product surface; does not touch `RUN-STATE.yaml`, the active plan, or paused Codex OW-071-13.

**RPT-12** (DESIGN.md → REPORT_DESIGN.md rename) is deferred to v0.8.0 as a coordinated breaking change (~30 reference sites; shipped filename — see §14.9 decision 3). **RPT-14/RPT-15** defer to v0.8.x.

### 14.7 Strengths to protect (the auditability backbone that makes aggressive cuts safe)

- **F11 / Independent QA + no-self-approval** — validator and judge ≠ the authoring agent. Preserve under all workstreams.
- **C12 / Stable IDs + SHAs** — every finding/decision has a stable ID and content SHA. Sharding (RPT-2) must preserve these, not renumber them.
- **C13 / Alignment hard stop** — the gate that blocks progression on misalignment. Ship it (RPT-1), do not soften it.
- **C14 / Small-model capsule** — the Haiku-class judge is what makes transcript-flood (RPT-14) a real risk worth a `--summarize` flag. Keep the capsule, add the flag.
- **C15 / Serial default, no routine subagents** — keeps the cold-resume drain bounded. Per-version sharding relies on this staying default.
- **C16 / Validator enforces contract** — the spine of RPT-1. Extending it to selection is additive, not a rewrite.
- **C20 / Gate-gated reflection** — reflection cannot close until the gate passes. RPT-3 (pinned tokenizer) makes this gate *meaningful*. Keep both.
- **F14 / Canonical-vs-generated boundary** — generated artifacts never written into `templates/`. WS-B's register sharding must respect this: registers are generated, templates stay pristine.

### 14.8 The one-line reframing (adopt in README/marketing)

> **Owledge is a reasoning-displacement runtime: it keeps the agent's working window clear at the zero-context moment, so the model reasons about your code — not about 16k tokens of stale release state.**

Drop the "$0.48–6/release" cost framing — it is noise and invites the gameable-metric failure RPT-3 guards against. The honest value proposition is that an 8% reasoning-window reclaim at the cold-resume inflection point is the difference between a model that re-derives your architecture and one that re-reads its own backlog.

### 14.9 Owner decisions locked (2026-07-29)

1. **First move = this §14 append** (audit-safe; §1–§13 preserved).
2. **WS-B gating = block on OW-071-09** — the per-version-sharding ticket cannot start until the paused Codex OW-071-13 run is owner-approved and closed (same non-interference pattern as OW-080-13).
3. **RPT-12 = deferred to v0.8.0** (revised after blast-radius check). The plan framed the `DESIGN.md` → `REPORT_DESIGN.md` rename as "small, isolated." A grep revealed ~30 reference sites across packaging (`pyproject.toml`, `MANIFEST.in`, `SOURCES.txt`), copy-tooling (`owledge.py:122`, `build_project_folder_kit.py:24` both ship `("DESIGN.md","DESIGN.md")` to users), the doctor check (`owledge_core.py:218,2286,3614`), unit tests (`test_upgrade.py:58,64,65,77,132` assert DESIGN.md is never modified and list it as a shipped artifact), skills, docs, and plugins. It is a **shipped filename** — a full rename breaks every existing bootstrapped project's expectation. Owner decision (2026-07-29): execute the coordinated breaking rename (file + tooling + packaging + tests + skills + docs + migration note) as part of the v0.8.0 workstream, **not** as a standalone PR now.
4. **WS-F filed** as a new ticket parallel to OW-080-13 (native hooks / allow-list / injection), capturing the harness-integration investigation verdict.

### 14.10 Verification (when workstreams execute)

- `python tools/validate_v1_delivery_plan.py` stays green for every OW-080-13 amendment (RPT-4 R-set cross-check, RPT-6 enum check once added).
- `python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports` stays all-100 for shipped-template changes.
- `validate_context_pack_usage.py` (new) rejects an out-of-contract pack fixture; passes an in-contract one.
- `git diff -- internal/owledge/workpackages/.../RUN-STATE.yaml` remains empty through WS-A/C/E/F (non-interference with paused Codex OW-071-13).
- Gate emits both `cold_resume_drain` and `warm_resume_drain` magnitude columns with the pinned tokenizer; `warm="TBD"` fails.
- For RPT-16: a project-local `init-project`-ed host runs a full session with **zero** external-path approval prompts; the `SessionStart` injection hook emits a capsule without a manual call.

### 14.11 Provenance

3-layer QA-gated subagent swarm: 3 filter agents (Explore) → 3 red-team agents (adversarial, refutation-first) → 1 synthesis agent (adjudicated conflicts, argued the ranked report). One post-synthesis investigation (RPT-16) commissioned after the owner flagged the harness-acceptance friction. §1–§13 stand as the cold-resume dogfood baseline; §14 is the principle-level review. **No live control-plane files were modified to produce §14; this report file is the only artifact written for this section.**