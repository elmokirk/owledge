---
memory_id: "mem:owledge:global:owledge:task:versioned-migration-hybrid-checklist"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "task"
artifact_type: "workpackage"
document_version: 2
status: "ready_for_execution"
visibility: "private"
data_class: "internal"
semantic_title: "Versioned migration hybrid delivery checklist"
summary: "Gate-oriented checklist for the migration skill, version catalog, deterministic engine, compatibility journeys and release evidence."
concept_tags: ["migration", "checklist", "skills", "post-v1"]
stack_tags: ["python", "markdown", "json"]
confidence: 0.98
review_status: "owner_requested"
sanitization_status: "not_required"
created_at: "2026-08-21T00:00:00+02:00"
updated_at: "2026-08-21T18:00:00+02:00"
source_hash: ""
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:versioned-migration-hybrid"
    confidence: 1.0
    reason: "Turns the migration plan into resumable phases and gates."
  - type: "uses"
    target: "mem:owledge:global:owledge:handoff:skill-authoring-guidance"
    confidence: 1.0
    reason: "Applies the compact-router authoring contract."
---

# Versioned migration hybrid checklist

## Phase 0, execution boundary

- [ ] Record owner approval for the v0.7 custom-vault mapping and no-delete default.
- [ ] Create a separate post-V1 control plane with WIP 1. Preserve completed V1M state.
- [ ] Lock source branch, base SHA, catalog schema and allowed paths.
- [ ] Add `MIG-01` through `MIG-07` as atomic tickets with rollback and QA handoffs.

Reflection required: confirm the first supported version pair and whether any
fixture exposes a missing owner decision before engine work starts.

## Phase 1, contract and sealed plan

- [ ] Add catalog, fingerprint, inventory and sealed-plan schemas.
- [ ] Add v0.7 managed, edited, custom, v0.8 and unknown fixtures.
- [ ] Implement metadata-only inspect and canonical plan output.
- [ ] Bind source, catalog, engine and skill hashes.
- [ ] Prove unsupported, future and tampered inputs fail before writes.
- [ ] Record G-MIG-01-CONTRACT evidence and independent contract QA.

Reflection required: log detection gaps, catalog changes and the exact next
supported pair. Stop if classification requires content interpretation.

## Phase 2, apply and recovery

- [ ] Preflight all source and target paths before mutation.
- [ ] Stage replacements in the target directory and journal before each write.
- [ ] Add idempotent apply, recover and rollback receipts.
- [ ] Inject failure after every managed write and during receipt creation.
- [ ] Prove user files, never-touch paths and legacy folders remain unchanged.
- [ ] Cover parent, absolute, UNC, network, symlink and junction paths.
- [ ] Record G-MIG-02-RECOVERY evidence and independent security QA.

Reflection required: list every partial-state case found and whether recovery
completed or rolled back. No waiver can convert an unverified state to green.

## Phase 3, compact skill and routing

- [ ] Create a `SKILL.md` router of at most 90 lines.
- [ ] Include one routing table with signal, mode, load, action, done and route.
- [ ] Put version, approval and recovery detail behind conditional pointers.
- [ ] Add `agents/openai.yaml` with a precise trigger and invocation policy.
- [ ] Add a validator script for structure, links, budgets and duplicate meaning.
- [ ] Add one compact maintainer-instruction pointer to the authoring handoff.
- [ ] Install canonical and `.agents/skills` mirrors through init and upgrade.
- [ ] Implement pure `allow`, `deny`, `needs_user_decision` knowledge routing.
- [ ] Forward-test ambiguous lessons, handoffs and global promotion.
- [ ] Record G-MIG-03-SKILL evidence and small-context behavioral QA.

Reflection required: report context load, wrong-route cases, unused references
and any instruction removed by the no-op test.

## Phase 4, compatibility

- [ ] Run full journeys for managed v0.7, edited v0.7, custom vault and v0.8.
- [ ] Run explicit local Null-Space and denied implicit-global cases.
- [ ] Verify sealed-plan invalidation after source, catalog, engine or skill change.
- [ ] Record hashes and outcomes without content bodies.
- [ ] Record G-MIG-04-COMPAT evidence and independent privacy QA.

Reflection required: update the version matrix with only executed evidence.
Unsupported platforms and version pairs stay explicit.

## Phase 5, readiness

- [ ] Verify skill, engine and catalog package inventory and hash parity.
- [ ] Run offline install, discovery, upgrade and doctor checks.
- [ ] Update migration guide, breaking-change matrix and recovery docs.
- [ ] Run one small-context and one frontier-model fixture suite.
- [ ] Run plan, frontmatter, link, diff and package checks from clean source.
- [ ] Record G-MIG-05-READY evidence and final independent QA.
- [ ] Create a ranked follow-up backlog for existing skills. Do not bulk-rewrite them.
- [ ] Stop for owner authorization before push, tag, publish or real vault migration.

Reflection required: report changed scope, open risks, disproved assumptions,
gate evidence and the exact next owner decision.
