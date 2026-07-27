---
memory_id: "mem:owledge:global:owledge:workpackage:long-horizon-modes-and-skill-discovery"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "task"
artifact_type: "workpackage"
status: "reviewed"
visibility: "private"
data_class: "internal"
semantic_title: "Long-horizon modes and skill discovery implementation checklist"
summary: "Resume-oriented checklist for the bounded planning modes, reliable skill installation, plugin mirrors, documentation, and validation."
concept_tags: ["long-horizon-delivery", "mvp-sparring", "skill-discovery"]
stack_tags: ["python", "markdown", "yaml"]
problem_patterns: ["endless-planning", "undiscovered-project-skill"]
architecture_patterns: ["mode-driven-skill", "discovery-mirror"]
failure_modes: ["scope-creep", "plugin-mirror-drift", "untracked-skill-copy"]
reusable_lessons: []
confidence: 0.95
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-27T00:00:00Z"
updated_at: "2026-07-27T14:21:00Z"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:plan:long-horizon-modes-and-skill-discovery"
    confidence: 1.0
    reason: "Operationalizes the accepted implementation stages and QA gates."
---

# Long-Horizon Modes and Skill Discovery Checklist

## Resume State

Current stage: **Complete**. Resume the v1 delivery train at `OW-071-01`.

## Stage 1 - Mode and planning contracts

- [x] `owledge-long-horizon-delivery` skill and mode reference created
- [x] `mvp-sparring` stop/cutline/roadmap routing contract implemented
- [x] `version-steering` finding/decision/reflection contract implemented
- [x] planning and brainstorm compatibility routing updated
- [x] skill validation and targeted tests pass
- [x] quick review done

Evidence: skill validator passed; mode/discovery tests passed. Reflection:
retain the compatibility facade and stop after one owner-lockable MVP cutline.

## Stage 2 - Discoverable installation

- [x] `init-project` materializes `.agents/skills` mirrors
- [x] project-folder kit materializes the same mirrors
- [x] manifest and upgrade source mapping cover discovery mirrors
- [x] doctor reports missing or drifting discovery mirrors
- [x] fresh-init, build-kit, and upgrade tests pass
- [x] quick review done

Evidence: fresh init and project-kit tree hashes match; doctor reports 8/8
discoverable skill mirrors; upgrade tests passed. Reflection: keep root
`skills/` canonical and `.agents/skills/` additive.

## Stage 3 - Plugin and harness routing

- [x] planning-related plugin mirrors are complete
- [x] AGENTS and CLAUDE templates route planning through the new skill
- [x] docs explain root source, `.agents/skills`, plugin roots, and unsupported `.owledge/skills`
- [x] future pre-plan hook work is mapped without implementing automatic writes
- [x] runtime-adapter and release-trust gates pass
- [x] quick review done

Evidence: plugin and standalone mirrors match canonical skill trees;
runtime-adapter, release-trust, public-docs, and standalone-skill gates passed.
Reflection: stage automatic hooks behind the v0.8/v0.8.1 contracts.

## Stage 4 - Cumulative validation and handoff

- [x] delivery-plan validator passes
- [x] targeted unit tests pass
- [x] finalization gates pass
- [x] implementation findings and decisions recorded
- [x] next exact v0.7.1 action recorded
- [x] quick review done

Evidence: validator passed with 61 tickets, 25 gates, and 34 waves; 24
targeted tests passed; the earlier 35/35 evidence is stale and the corrected 38/38 finalization set must pass; quality-ratchet scores
are 100 across all nine dimensions. Reflection: resume at `OW-071-01`; do not
start later release work before its alignment gate.

## Stop Rules

- Do not add discovered ideas to the MVP without owner approval.
- Do not install user-global skills automatically.
- Do not treat root `skills/` or `.owledge/skills` as guaranteed Codex discovery.
- Do not add background planning hooks before the v0.8.1 adapter contract.
