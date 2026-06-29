---
memory_id: "mem:tenant-demo:customer-demo:owledge-pi-proof:qa:redteam-finding"
tenant_id: "tenant-demo"
customer_id: "customer-demo"
project_id: "owledge-pi-proof"
doc_type: "qa"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Red-team finding"
summary: "Red-team finding that empty templates must not count as proof."
concept_tags: ["pi-agent", "red-team"]
stack_tags: ["markdown"]
problem_patterns: ["performative-redteam"]
architecture_patterns: ["review-before-promotion"]
failure_modes: ["empty-template-passed"]
reusable_lessons: ["Red-team artifacts need non-zero score, findings, evidence, and recommendation."]
confidence: 0.9
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-06-19T00:00:00Z"
updated_at: "2026-06-19T00:00:00Z"
retention_class: "standard"
stale_after: ""
expires_at: ""
last_reviewed_at: "2026-06-19T00:00:00Z"
review_cycle: "quarterly"
source_hash: ""
edges: []
---

# Red-Team Finding

Finding: score zero and placeholder files are not acceptable launch evidence.

