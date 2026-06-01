---
memory_id: "mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime"
tenant_id: "fixture"
customer_id: "demo"
project_id: "retrieval-fixture"
doc_type: "pattern"
status: "reviewed"
visibility: "tenant"
data_class: "internal"
semantic_title: "Progressive disclosure runtime bridge"
summary: "Runtime adapters expose a small skill index first, then load detailed Markdown procedures only when task descriptions match."
concept_tags:
  - "agent-memory"
  - "runtime-bridge"
  - "retrieval-calibration"
  - "production-ready"
stack_tags:
  - "codex"
  - "claude"
  - "cowork"
problem_patterns:
  - "context-budget"
  - "agent-skill-selection"
architecture_patterns:
  - "progressive-disclosure"
  - "markdown-source-of-truth"
failure_modes:
  - "skill-overload"
  - "raw-session-export"
reusable_lessons:
  - "Procedural memory should be indexed by name and description before full skill loading."
  - "Runtime adapters are bridges, not canonical memory stores."
confidence: 0.9
review_status: "approved"
sanitization_status: "approved"
created_at: "2026-05-20T00:00:00Z"
updated_at: "2026-05-26T00:00:00Z"
retention_class: "long"
stale_after: "2026-08-26T00:00:00Z"
expires_at: ""
last_reviewed_at: "2026-05-26T00:00:00Z"
review_cycle: "quarterly"
source_hash: "fixture"
edges:
  - type: "relates_to"
    target: "mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring"
    confidence: 0.8
    reason: "Both records keep working memory under budget."
---

# Progressive Disclosure Runtime Bridge

This pattern covers procedural memory. Codex, Claude, Cowork, and generic CLI
agents should discover concise skill descriptions before reading detailed
instructions, scripts, or report templates.

The bridge keeps agent memory project kit retrieval calibrated without loading
every runtime adapter into working memory.
