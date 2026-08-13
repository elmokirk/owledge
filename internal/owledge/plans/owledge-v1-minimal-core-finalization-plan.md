---
memory_id: "mem:owledge:global:owledge:plan:v1-minimal-core-finalization"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "plan"
document_version: 3
plan_version: "1.0.2"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge V1 minimal core finalization plan"
summary: "Owner-approved scope-reduction plan that ships Owledge V1 as one small deterministic local knowledge kernel, a skill-only entry path, a minimal project/user-global profile, and thin Codex, Claude Code, and generic MCP/CLI adapters."
concept_tags: ["v1", "minimal-core", "scope-reduction", "parking-lot", "local-user-global"]
stack_tags: ["python", "markdown", "git", "mcp"]
problem_patterns: ["runtime-bloat", "default-install-bloat", "feature-creep", "lost-parked-ideas"]
architecture_patterns: ["functional-core-imperative-shell", "ports-and-adapters", "progressive-disclosure", "markdown-canonical"]
failure_modes: ["dogfood-surface-shipped-as-product", "skill-only-without-enforcement", "parked-idea-never-resurfaced", "public-api-sprawl"]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-13T17:20:00+02:00"
updated_at: "2026-08-13T17:20:00+02:00"
source_hash: ""
reusable_lessons:
  - "A complete small kernel is more valuable than a broad platform whose default path exposes internal machinery."
  - "Parked work remains product knowledge only when it has a reason, trigger, source, and deterministic resurfacing path."
edges:
  - type: "supersedes"
    target: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
    confidence: 1.0
    reason: "Narrows the remaining V1 train to the owner-approved minimal public product surface; completed evidence remains valid and is reused."
  - type: "relates_to"
    target: "mem:owledge:global:owledge:decision:skill-discovery-and-bounded-planning-2026-07-27"
    confidence: 1.0
    reason: "Makes bounded MVP planning and durable parked-idea routing part of the minimal V1 journey."
---

# Owledge V1 Minimal Core Finalization Plan

## Abstract: one product, five bounded surfaces

Owledge should remain **one product and one brand**, but not one undifferentiated
runtime. V1 ships one package with explicit surfaces:

| Surface | V1 role | Runtime |
| --- | --- | --- |
| Owledge Principles | Zero-install trial and behavioral contract | Skill/Markdown only |
| Owledge Core | Deterministic local knowledge lifecycle | On-demand Python CLI/library |
| Local Null-Space | Private cross-project user-global composition | Local files plus derived index |
| Runtime Adapters | Codex, Claude Code, generic MCP/CLI bridges | Thin translation only |
| Add-ons / Hub | Future optional products | Parked outside V1 |

Do not split these into separate repositories before V1. Keep one repository and
package, but enforce deep module and distribution boundaries. The future Hub may
become a separately deployable package after the local Core contract is stable.

## Owner outcome

Publish V1 quickly enough that the owner can install it once, link several local
projects, and use the same reviewed knowledge from Codex, Claude Code, and any
generic MCP/CLI harness without reloading full histories or repeating research.

V1 succeeds when this journey is real:

```text
skill-only trial
  -> minimal local install
  -> link explicit projects to private user-global Null-Space
  -> recall before research or planning
  -> produce bounded Research/Idea delta
  -> review: promote | park | reject | supersede
  -> resume from another supported harness
  -> upgrade safely
```

## Why another cut is required

The current product is operationally light but cognitively broad:

- current default quickstart audit: **210 files and 80 directories**;
- `tools/owledge_core.py`: about **7,100 lines**;
- `tools/owledge.py`: about **4,600 lines**;
- default CLI: more than **25 top-level commands**;
- repository: about **2,600 tracked files**, mostly Markdown, fixtures, dogfood,
  evidence, templates, and add-ons.

The wheel remains small and the standard-library Python runtime is a strength.
V1 therefore does **not** rewrite Owledge in another language or delete verified
capabilities. It reduces the default install, public surface, active context, and
Core authority while moving non-core behavior behind explicit profiles/add-ons.

## Alternatives considered

| Approach | Summary | Effort | Risk | Decision |
| --- | --- | ---: | ---: | --- |
| Skill-only Owledge | One skill plus Markdown and `rg`; no deterministic runtime | Small | Medium/High | Rejected as complete V1; retained as zero-install entry path |
| Continue broad platform | Ship the current large templates, commands, adapters and enterprise direction as one surface | Large | High | Rejected; delays direct use and exposes dogfood complexity |
| Minimal Core + Skills + thin adapters | Skills guide behavior; eight-operation Core enforces invariants; adapters translate only | Medium | Low/Medium | **Selected** |

The selected approach reuses existing verified code and avoids both extremes:
prompt-only reliability and premature platform scope.

## Twelve-month direction and V1 delta

```text
CURRENT
broad repository + large default kit + many public concepts
        |
        v
V1
one small local product journey + parked optional surfaces
        |
        v
12-MONTH OPTION
proven Core + independently chosen Hub/add-ons based on real adoption evidence
```

V1 intentionally preserves future seams without pre-building the future products.

## Locked V1 product boundary

### Must ship

1. Zero-install Principles skill with a clear upgrade path to Core.
2. Minimal project profile and private local user-global Null-Space.
3. Markdown/Git remains canonical; derived index is disposable and rebuildable.
4. Two scopes only: `project_user` and private local `user_global`.
5. Recall/search and token-bounded context packs.
6. Candidate writes for Research deltas, learnings, decisions, handoffs, ideas,
   and roadmap items; no raw transcript promotion.
7. Reviewed lifecycle with `promote`, `park`, `reject`, `supersede`, and
   deterministic tombstone/rebuild behavior.
8. Planning recall that resurfaces relevant parked ideas without loading the
   whole parking lot into normal working context.
9. Codex, Claude Code, and generic MCP/CLI reference adapters.
10. Deterministic schema validation, health, privacy boundary, upgrade, recovery,
    and GA artifact proof.

### Must not ship in V1

- remote Hub, enterprise scope, auth/RBAC/OIDC, hosted or multi-tenant service;
- Pi-specific adapter, Hermes/OpenCode-specific adapter, autonomous agent harness;
- LightRAG/vector/graph dependency, Documentation Compiler, generic observability;
- worktree/worker orchestration, model judge router, cron/automation builder;
- universal erasure/DSAR connector suite or compliance certification;
- mandatory daemon, database, network, LLM, embedding model, or cloud provider.

All excluded concepts are preserved in
[[post-v1-feature-parking-lot]] with triggers and source links.

## Complexity budget

| Contract | V1 hard limit |
| --- | ---: |
| Default public CLI verbs | 8 |
| Default MCP tools | 5 |
| Knowledge scopes | 2 |
| Tier-1/reference adapters | 3 |
| Required databases/vector stores | 0 |
| Required network/model calls | 0 |
| Fresh minimal profile files | <= 15 |
| Fresh minimal profile directories | <= 8 |
| Default wheel target | <= 500 KB unless evidence justifies growth |

No new public verb, MCP tool, scope, adapter, or required service may be added
without an explicit `AMEND GOAL BOUNDARY` owner decision. Lines of code are not
the primary metric; public concepts and required moving parts are.

## Public V1 operations

| Operation | Responsibility | Explicit non-responsibility |
| --- | --- | --- |
| `init` | Create/link minimal project or local user-global profile | No full template/add-on install by default |
| `doctor` | Validate schema, links, health, privacy, revisions | No content telemetry or LLM judgment |
| `recall` | Search by scope, purpose, freshness, lifecycle | No implicit all-project scan or web search |
| `context` | Build deterministic budgeted context pack | No raw vault/history injection |
| `propose` | Write Candidate/Research/Idea/Handoff delta | No canonical promotion |
| `review` | Promote, park, reject, supersede with receipt | No self-approval where policy requires review |
| `sync` | Rebuild/reconcile local derived indexes/tombstones | No remote sync |
| `upgrade` | Preview/apply/recover managed changes | No overwrite of user-managed Markdown |

Existing advanced commands remain compatibility shims or move behind explicit
`addon`/`dev` surfaces. They are not listed in the default beginner help and do
not expand the Core contract.

## Default MCP surface

1. `capabilities`
2. `recall`
3. `context`
4. `propose`
5. `review`

`sync`, `doctor`, and `upgrade` stay operator CLI operations in V1. MCP never
exposes arbitrary file writes, process execution, project registration, or remote
administration.

## Module boundaries

```text
Skills / AGENTS rules
        |
        v
Codex adapter   Claude adapter   Generic MCP/CLI
        \            |             /
         +---- thin capability port ----+
                        |
                        v
                Owledge public facade
       init doctor recall context propose review sync upgrade
                        |
          +-------------+--------------+
          |             |              |
       contracts     retrieval      lifecycle
          |             |              |
          +--------- local store -------+
                        |
             Markdown/Git + derived index
```

Logical modules and ownership:

| Module | Owns | Must not own |
| --- | --- | --- |
| `contracts` | envelope/profile/settings validation | storage, adapter policy |
| `store` | safe paths, atomic Markdown writes, hashes | retrieval ranking, prompts |
| `retrieval` | filters, recall reasons, context budgets | canonical mutations |
| `lifecycle` | Candidate/review/park/promotion state machine | arbitrary filesystem writes |
| `index` | disposable local index and tombstones | source of truth |
| `health` | deterministic diagnostics and receipts | raw-body telemetry |
| `migration` | preview/apply/recover managed surfaces | user-owned content rewrite |
| `adapters` | capability translation and degradation | duplicated Core semantics |

Do not require a wholesale pre-V1 rewrite of the two existing large Python
modules. Introduce or enforce the public facade first, then move only touched
logic behind these seams. Untouched verified legacy functions may remain behind
compatibility shims until post-V1 modularization.

## Minimal installation profiles

### `principles`

- no project files required;
- one discoverable skill/instruction contract;
- uses existing Markdown and `rg`/filesystem search;
- offers Core installation only when deterministic validation, global recall,
  promotion, health, or MCP is needed.

### `minimal` (default)

- `OWLEDGE.md` router;
- minimal `AGENTS.md`/runtime bridge only when explicitly requested;
- `.owledge/config.yaml`;
- lazily created `candidates/`, `research/`, `handoffs/`, `decisions/`, `evidence/`;
- schemas remain package resources rather than copied per project;
- skills remain package/global/plugin resources rather than copied wholesale;
- no Pi, report design, benchmark, RAG, compliance, or orchestration trees.

### `user-global`

- one explicit local Null-Space root;
- project registry with resolved paths, owner, allowlist, and last-seen revision;
- separate local project/user-global namespaces;
- raw inbox excluded from ordinary recall;
- no network or implicit project discovery.

### `full` / `maintainer`

Preserves current large templates, dogfood, benchmarks, internal review tools,
and optional add-ons. It is never the default user installation or V1 mental
model.

## Park and resurface contract

V1 reuses the existing Candidate/Idea machinery; it does not create a second
task tracker.

Required parked-item fields:

- stable `memory_id` and semantic title;
- `item_kind`: idea, feature, research, integration, product, risk, or debt;
- `lifecycle: parked`;
- `park_reason`;
- `source_refs` and originating context;
- `related_projects` and concept tags;
- `earliest_horizon`;
- `reconsider_when` trigger;
- dependencies and expected value;
- last reviewed date.

Normal `recall` excludes parked/raw items. `recall --purpose planning` may return
only matching parked essences with the reason they matched and a link to full
detail. Moving a parked item into active scope always requires an explicit plan
decision; a skill or adapter cannot do so silently.

## Existing code to reuse

- Existing v0.8 contracts, context budgets, Research recall, health, migration,
  and retrieval projection remain the implementation base.
- Completed `OW-081-01`, `OW-081-02`, `OW-081-03`, and `OW-081-05` conformance
  work becomes adapter evidence; do not rebuild it.
- Existing `brainstorm-candidate`, idea, Research, handoff, evidence, promotion,
  and frontmatter templates provide the lifecycle vocabulary.
- Existing `quickstart`, `init-project`, `doctor`, `build-context-pack`,
  `research-recall`, `promote`, and `upgrade` behavior is consolidated behind the
  small public facade rather than reimplemented.
- Existing full kit remains a compatibility/maintainer profile.

## Replacement execution train

This train replaces remaining unstarted v0.8.1-v1 breadth after the current
adapter gate. Completed tickets and evidence are inputs, not work to repeat.

| Wave | Tickets | Demonstrable increment | Gate |
| --- | --- | --- | --- |
| W-MIN-0 | V1M-01 | Control plane reconciled; every surface classified | G-V1M-PLAN |
| W-MIN-1 | V1M-02, V1M-03 | Skill-only path, minimal install, eight-verb facade | G-V1M-SURFACE |
| W-MIN-2 | V1M-04, V1M-05 | Local Null-Space recall and bounded context | G-V1M-READ |
| W-MIN-3 | V1M-06, V1M-07 | Delta, park/resurface, review/promotion, health/tombstones | G-V1M-LIFECYCLE |
| W-MIN-4 | V1M-08 | Three thin adapters prove the same journey | G-V1M-ADAPTERS |
| W-MIN-5 | V1M-09, V1M-10 | Upgrade/security/docs/golden journey and GA candidate | G-V1M-GA |
| W-MIN-6 | V1M-11 | Owner-controlled publish/tag/release | G-V1M-PUBLISH |

## Ticket contracts

### V1M-01 — Reconcile the live control plane and classify every surface

- Rebase this plan onto the latest clean integration checkpoint.
- Map every public command, MCP tool, template family, skill, add-on, and runtime
  into `core`, `adapter`, `add-on`, `internal-only`, or `deprecate`.
- Replace remaining V1 gate dependencies on parked work.
- Add the complexity-budget validator.
- Do not change runtime behavior in this ticket.

### V1M-02 — Ship skill-only and minimal install profiles

- Make `principles` the zero-install entry path and `minimal` the default install.
- Keep fresh default footprint within 15 files and 8 directories.
- Load schemas from package resources; create content directories lazily.
- Preserve current behavior under explicit `full`/`maintainer` profile.
- Prove upgrade never deletes user-owned files.

### V1M-03 — Freeze the eight-operation public facade

- Make default help expose only the eight Core operations.
- Route existing compatible commands through the facade or document them under
  explicit advanced surfaces.
- Preserve machine-readable errors and compatibility aliases through V1.
- Add contract tests that reject a ninth verb without owner amendment.

### V1M-04 — Finish the private local user-global Null-Space

- Explicit project linking, allowlists, resolved-path safety, two namespaces,
  and no-sync policy.
- Small vaults scan Markdown directly; derived indexing activates only when
  configured or threshold-triggered and remains rebuildable.
- No enterprise scope, shared users, auth server, or implicit project scan.

### V1M-05 — Consolidate recall and bounded context

- Search by scope, purpose, lifecycle, freshness, project, and source reason.
- Recall-before-research and recall-before-planning are explicit purposes.
- Progressive disclosure returns essence first and permission-checked detail on
  demand.
- Enforce deterministic context budgets and source/exclusion receipts.

### V1M-06 — Add Candidate delta plus Park/Resurface lifecycle

- One proposal path for Research deltas, learnings, handoffs, decisions, ideas,
  and feature candidates.
- Validate the parked fields defined above.
- Exclude parked/raw from ordinary retrieval.
- Planning recall returns matching parked items and reevaluation triggers.
- Test that no adapter can silently activate a parked item.

### V1M-07 — Complete local review, promotion, tombstones, and health

- Review transitions: promote, park, reject, supersede.
- Raw inbox remains private and excluded.
- Withdrawn/deleted sources invalidate essences and derived indexes.
- `doctor` reports stale sources, invalid revisions, orphan links, promotion debt,
  context overflow, and index drift without content telemetry.

### V1M-08 — Prove thin Codex, Claude Code, and generic MCP/CLI adapters

- Reuse completed adapter manifests and fixtures.
- Restrict MCP to the five tools in this plan.
- Prove identical scopes, lifecycle semantics, errors, and explicit degradation.
- Adapter packages contain no search, storage, promotion, or migration fork.

### V1M-09 — Finalize install, upgrade, recovery, and security

- One-command `uvx` trial and repeat-use install.
- Preview-first upgrade with checkpoint, postflight doctor, receipt, and recovery.
- Safe path/symlink handling, no implicit network, secret/PII warnings, and
  retrieved-instruction provenance.
- Windows executed proof; macOS/Linux wheel-only proof before GA publication.

### V1M-10 — Prove the compact daily journey and cut GA candidate

- Fresh minimal install and explicit user-global setup.
- Project A Research reuse in Project B through a reviewed essence.
- Park a feature idea, verify ordinary recall excludes it, then resurface it in a
  later planning-purpose recall.
- Switch between Codex and Claude or generic MCP without chat history.
- Build clean wheel/sdist; docs and capability claims match executed evidence.

### V1M-11 — Owner-controlled V1 publication

- Present shipped scope, evidence, residual risks, parked register, migrations,
  support window, and post-V1 recommendation.
- Publication, tag, push, and release remain blocked until the owner explicitly
  approves the exact candidate commit and artifacts.

## Gate thresholds

### G-V1M-PLAN

- Every existing surface has one classification and one owner.
- No V1 ticket depends on a parked ticket.
- Complexity budget and ticket DAG validate.
- Current completed adapter evidence is referenced, not repeated.

### G-V1M-SURFACE

- Minimal profile <=15 files and <=8 directories.
- Default help has exactly the eight public verbs.
- Principles path works without installing Core.
- Full/maintainer profile remains opt-in and existing user files survive upgrade.

### G-V1M-READ

- Two scopes only; no implicit project discovery or network.
- Recall and context packs are deterministic, source-linked, budgeted, and
  progressive.
- Small-vault direct scan and rebuilt-index results are contract-equivalent.

### G-V1M-LIFECYCLE

- Raw/parked content cannot enter ordinary recall.
- Planning recall resurfaces relevant parked items with reason and trigger.
- Promotion/rejection/supersession/deletion are evidenced and idempotent.
- Health exposes stale or broken state without leaking bodies.

### G-V1M-ADAPTERS

- Codex, Claude Code, and generic MCP/CLI pass one common conformance journey.
- Default MCP surface has exactly five tools.
- No adapter duplicates Core semantics or claims unsupported behavior.

### G-V1M-GA

- Fresh install, upgrade, recovery, offline smoke, security negative corpus,
  cross-harness journey, and parking/resurfacing journey are green.
- Wheel/sdist are reproducible, within the package budget or have an explicit
  evidence-backed exception, and contain no personal/private paths.
- No unresolved P0/P1 and no V1 claim depends on parked work.

### G-V1M-PUBLISH

- Owner approves the candidate commit, artifacts, version, release notes, and
  exact publication action.

## Error and recovery contract

| Failure | Safe behavior | User-visible result | Required test |
| --- | --- | --- | --- |
| Missing project/global root | Fail closed with init/link instruction | Structured not-configured error | yes |
| Empty query or zero results | No fallback all-vault dump | Empty result plus filters used | yes |
| Unauthorized/unlinked project | Reject before read | Scope-denied result | yes |
| Invalid/stale source revision | Exclude from current result | Stale reason and deep-link | yes |
| Context budget exceeded | Deterministic truncation/exclusions | Budget receipt | yes |
| Duplicate/replayed proposal | Return prior idempotent receipt | No second artifact | yes |
| Conflicting review revision | Do not mutate | Conflict plus current revision | yes |
| Interrupted sync/upgrade | Preserve prior valid state | Recovery command and receipt | yes |
| Adapter lacks capability | Explicit degradation | Unsupported result | yes |
| Index missing/corrupt | Rebuild or direct-scan fallback | Health warning, never false current | yes |

## Failure-mode registry

| Codepath | Failure mode | Rescued? | Test | User sees | Logged/receipt |
| --- | --- | ---: | ---: | --- | ---: |
| minimal init | partial file creation | yes | integration | recovery/rollback instruction | yes |
| project link | path escape or missing root | yes | security | explicit invalid-project error | yes |
| recall | empty, stale, unauthorized or corrupt source | yes | unit/integration | exclusions and reasons | yes |
| context | source set exceeds budget | yes | unit | deterministic truncation receipt | yes |
| propose | replay, invalid schema or unsafe target | yes | negative | structured rejection/prior receipt | yes |
| review | stale revision or forbidden transition | yes | state-machine | conflict/transition error | yes |
| sync | interrupted index swap | yes | recovery | prior index retained/rebuild action | yes |
| upgrade | failed postflight | yes | migration | checkpoint and recovery action | yes |
| adapter | unsupported or malformed call | yes | conformance | explicit degradation/error | yes |

No V1 failure path may silently broaden search, promote content, fall back to a
network/model, or claim current knowledge after a failed validation.

## Deployment and rollback sequence

```text
clean source -> build wheel/sdist -> inspect -> fresh install -> upgrade fixture
     -> offline/core journey -> adapter journey -> G-V1M-GA -> owner approval
     -> publish/tag

failure before publish -> fix/rebuild; no external state changed
failure after install   -> restore managed checkpoint; keep user Markdown
failure after publish   -> yank/patch release; never rewrite user knowledge
```

## Autonomous handoff boundary

The execution agent may make reversible implementation choices inside these
contracts. It must stop for:

- any ninth public verb, sixth MCP tool, third knowledge scope, or fourth adapter;
- relaxing privacy, canonical-promotion, context-budget, or no-network defaults;
- removing compatibility behavior without an upgrade path;
- external credentials/cost, destructive migration, publish/tag/push/release;
- any proposal to pull a parked item into V1.

The copy-ready execution prompt is in
[[owledge-v1-minimal-core-goal-handoff]].

## Definition of V1 done

V1 is done only when a new user can choose Principles or a minimal install,
reach first value without understanding the dogfood control plane, use local
project/user-global recall and reviewed deltas from three reference adapters,
park and later resurface ideas, upgrade safely, and reproduce the complete
journey from clean artifacts. Everything else remains discoverable in the
parking lot and does not block publication.

## Planning review result

- Mode: Scope Reduction.
- Product/CEO verdict: accept the minimal-Core direction; no unresolved product
  decision remains inside the approved V1 envelope.
- Engineering readiness: ready for `V1M-01` reconciliation at a clean gate
  boundary; runtime implementation remains gated.
- Deterministic plan checks: eight public operations, five MCP tools, eleven
  execution tickets, and 24 parked concepts.
- Frontmatter/identity/edge checks for all new artifacts: green.
- Wikilink audit: zero unresolved or ambiguous links.
- Diff hygiene: green.
- Repository-wide strict validation still contains pre-existing legacy metadata
  failures; none originate from these artifacts. `V1M-01` must not silently fold
  unrelated legacy normalization into the Core scope.
- Independent subagent review was not run because the active repository policy
  prohibits unrequested subagent delegation; risk is bounded by the deterministic
  checks and the required engineering review at `G-V1M-PLAN`.
