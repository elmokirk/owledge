---
memory_id: "mem:owledge:global:owledge:decision:skill-discovery-and-bounded-planning-2026-07-27"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "adr"
artifact_type: "decision"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Reliable skill discovery and bounded long-horizon planning"
summary: "Adopts one mode-driven long-horizon skill, bounded MVP sparring, durable future-idea routing, and additive harness-discoverable skill mirrors."
concept_tags: ["skill-discovery", "mvp-sparring", "long-horizon-delivery", "idea-routing"]
stack_tags: ["markdown", "python", "codex", "claude-code"]
problem_patterns: ["endless-planning", "scope-creep", "undiscovered-project-skill"]
architecture_patterns: ["mode-driven-skill", "discovery-mirror", "compatibility-facade"]
failure_modes: ["root-skill-not-loaded", "roadmap-idea-dropped", "automatic-promotion"]
reusable_lessons:
  - "A shipped skill source and a harness discovery location are separate product contracts."
  - "Planning is complete when the smallest useful increment is decision-complete, not when ideation is exhausted."
confidence: 1.0
created_at: "2026-07-27T00:00:00Z"
updated_at: "2026-07-27T00:00:00Z"
review_status: "approved"
sanitization_status: "not_required"
source_hash: ""
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:long-horizon-modes-and-skill-discovery"
    confidence: 1.0
    reason: "Records the implemented mode and discovery architecture."
  - type: "relates_to"
    target: "mem:owledge:global:owledge:idea:pre-plan-idea-concept-harness-hooks"
    confidence: 0.98
    reason: "Separates the current skill/discovery MVP from later runtime hook automation."
---

# Reliable Skill Discovery and Bounded Long-Horizon Planning

## Decision

1. `owledge-long-horizon-delivery` is the canonical orchestration skill with
   `mvp-sparring`, `version-steering`, `ticket-execution`, `gate-review`, and
   `recovery` modes.
2. `owledge-planning-layer` remains a compatibility facade and defaults broad
   planning to bounded `mvp-sparring`.
3. Planning stops after one measurable smallest useful increment has an MVP
   cutline, explicit non-goals, first executable task, and QA gate. Additional
   value is classified and routed to roadmap, idea, decision, or defer/reject
   state.
4. Root `skills/` remains the Owledge source/vendor tree. `init-project` and
   project-kit builds create matching `.agents/skills/` mirrors for Codex.
   Plugin manifests continue to use their declared local `skills/` roots.
5. `.owledge/skills/` is not treated as an automatic harness discovery path.

## Rationale

A single skill with explicit modes preserves one coherent long-running
delivery contract while keeping each interaction bounded by a visible stop
condition. The additive discovery mirror avoids moving or weakening the
canonical source tree and lets manifests/upgrades detect user edits and drift.

## Authority Boundaries

- Existing ideas and concepts can influence a proposed cutline, but cannot
  become current scope automatically.
- Discovery never implies permission to write canonical memory.
- Technical readiness never bypasses version alignment.
- User-global installation is opt-in and is not performed by project init.

## Deferred Work

- `OW-080-03`: first-class MVP cutline and candidate-disposition fields.
- `OW-080-05`: deterministic pre-plan idea/concept capsule.
- `OW-081-01` through `OW-081-05`, plus `OW-081-13`: conformance and
  harness-specific pre-plan hooks.
- `OW-090-02` and `OW-090-04`: reviewed semantic linking and promotion.

## Verification

- Skill validator passes.
- Mode/discovery regression suite passes.
- Upgrade, generated-kit, standalone-skill, runtime-adapter, release-trust,
  and finalization gates provide the promotion evidence.
