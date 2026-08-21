---
memory_id: "mem:owledge:global:owledge:task:versioned-migration-hybrid-checklist"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "task"
artifact_type: "workpackage"
document_version: 1
status: "proposed"
visibility: "private"
data_class: "internal"
semantic_title: "Versioned migration hybrid delivery checklist"
summary: "Resume-oriented execution checklist for the Owledge migration skill, version catalog and deterministic engine."
concept_tags: ["migration", "checklist", "post-v1"]
stack_tags: ["python", "markdown", "json"]
confidence: 0.96
review_status: "owner_requested"
sanitization_status: "not_required"
created_at: "2026-08-21T00:00:00+02:00"
updated_at: "2026-08-21T00:00:00+02:00"
source_hash: ""
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:versioned-migration-hybrid"
    confidence: 1.0
    reason: "Turns the approved hybrid plan into resumable tickets and gates."
---

# Versioned migration hybrid checklist

## Start boundary

- [ ] Owner approves the proposed scope, especially the v0.7 custom-vault
  mapping boundary and the no-delete default.
- [ ] Create one active control-plane ticket per `MIG-*` row. Do not modify the
  completed V1M control plane.
- [ ] Lock the source and target catalog versions before implementation.

## Contract and engine

- [ ] Implement catalog and plan schemas with invalid, future and tampered
  version fixtures.
- [ ] Add metadata-only inspection and canonical dry-run plans.
- [ ] Bind plan, catalog and engine hashes before apply.
- [ ] Add atomic staging, journal, recovery and rollback tests.
- [ ] Prove never-touch, user-edited, path-escape, UNC, symlink and junction
  negatives.

## Skill and routing

- [ ] Keep `SKILL.md` below 120 lines and move conditional material to three
  routed references.
- [ ] Install the discoverable `.agents/skills` mirror through normal project
  init/upgrade.
- [ ] Add `allow`, `deny`, `needs_user_decision` classification for legacy
  lessons, handoffs, candidates, decisions and user-global records.
- [ ] Forward-test a constrained-context agent against an ambiguous learning
  versus handoff fixture.

## Compatibility gate

- [ ] Execute v0.7 managed-kit, edited-kit, custom-vault and explicit
  user-global migration fixtures.
- [ ] Record environment, source/target version, plan hash, receipt and rollback
  result without content bodies.
- [ ] Run independent QA for version catalog, privacy paths and recovery.
- [ ] Stop for owner approval before any future publish, tag or destructive
  migration scope change.
