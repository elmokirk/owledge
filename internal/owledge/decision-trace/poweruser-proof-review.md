---
memory_id: "mem:tenant-local:customer-local:owledge-standalone:review:poweruser-proof-qa"
tenant_id: "tenant-local"
customer_id: "customer-local"
project_id: "owledge-standalone"
doc_type: "review"
status: "passed"
visibility: "private"
data_class: "internal"
semantic_title: "Poweruser Proof QA"
summary: "QA validates that installed proof-layer tools compile, render, and keep generated outputs separate from canonical Markdown."
concept_tags:
  - "qa"
  - "red-team"
  - "privacy-safety"
stack_tags:
  - "python"
problem_patterns:
  - "generated views must not become canonical truth"
architecture_patterns:
  - "strict validation gates"
failure_modes:
  - "private output accidentally shared"
reusable_lessons: []
confidence: 0.88
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
  - target: "mem:tenant-local:customer-local:owledge-standalone:decision:poweruser-proof-layer-ships-as-addons"
    type: "supports"
    reason: "QA passing supports shipping these capabilities as optional add-ons and skills."
---

# Poweruser Proof QA

Required checks:

- Python compile for installed tools.
- Memory validation.
- Kit doctor.
- Public docs test.
- Launch-readiness and quality-ratchet tests where relevant.

Generated reports remain generated views and are ignored unless intentionally promoted.
