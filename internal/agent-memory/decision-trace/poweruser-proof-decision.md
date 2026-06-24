---
memory_id: "mem:tenant-local:customer-local:agent-memory-standalone:decision:poweruser-proof-layer-ships-as-addons"
tenant_id: "tenant-local"
customer_id: "customer-local"
project_id: "agent-memory-standalone"
doc_type: "decision"
status: "accepted"
visibility: "private"
data_class: "internal"
semantic_title: "Ship Poweruser Proof Layer As Add-ons"
summary: "Keep Owledge core lean and ship benchmark, trace, hub, swarm, and positioning capabilities as optional add-on and skill layers."
concept_tags:
  - "architecture-decision"
  - "optional-layer"
stack_tags:
  - "python"
problem_patterns:
  - "power features can overwhelm default adoption"
architecture_patterns:
  - "core plus optional proof layer"
failure_modes:
  - "forced migration"
  - "core runtime dependency creep"
reusable_lessons: []
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-21T18:30:00Z"
updated_at: "2026-06-21T18:30:00Z"
retention_class: "standard"
stale_after: ""
expires_at: ""
last_reviewed_at: "2026-06-21T18:30:00Z"
review_cycle: "monthly"
source_hash: ""
edges:
  - target: "mem:tenant-local:customer-local:agent-memory-standalone:lesson:proof-before-claims"
    type: "teaches"
    reason: "The decision establishes the reusable project lesson for future pitches and roadmap work."
---

# Ship Poweruser Proof Layer As Add-ons

Decision: keep the core unchanged and expose advanced proof features through optional kits and skills.

This preserves the adoption story: Owledge can sit beside Codex, Claude Code, Hermes, Graphify-style visualizers, LLM Wiki, Obsidian, Superpowers-style workflows, and custom harnesses.
