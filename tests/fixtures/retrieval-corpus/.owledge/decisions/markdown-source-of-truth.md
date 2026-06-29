---
memory_id: "mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth"
tenant_id: "fixture"
customer_id: "demo"
project_id: "retrieval-reference"
doc_type: "adr"
status: "reviewed"
visibility: "tenant"
data_class: "internal"
semantic_title: "ADR: Markdown remains canonical memory"
summary: "Vector databases, dashboards, MCP servers, and runtime plugins are adapters; Markdown frontmatter and typed edges remain canonical."
concept_tags:
  - "owledge"
  - "architecture"
  - "retrieval-calibration"
  - "production-ready"
stack_tags:
  - "markdown"
  - "mcp"
problem_patterns:
  - "adapter-drift"
  - "contradictory-memory"
architecture_patterns:
  - "markdown-source-of-truth"
  - "runtime-bridge"
failure_modes:
  - "database-as-canonical"
  - "stale-memory"
reusable_lessons:
  - "Do not treat vector-store contents as canonical project memory."
  - "Use typed edges and source hashes to reconnect retrieval output to Markdown."
confidence: 0.92
review_status: "approved"
sanitization_status: "approved"
created_at: "2026-05-20T00:00:00Z"
updated_at: "2026-05-26T00:00:00Z"
retention_class: "archive"
stale_after: "2026-11-26T00:00:00Z"
expires_at: ""
last_reviewed_at: "2026-05-26T00:00:00Z"
review_cycle: "semiannual"
source_hash: "fixture"
edges:
  - type: "relates_to"
    target: "mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime"
    confidence: 0.8
    reason: "Runtime bridges must preserve Markdown as source of truth."
---

# ADR: Markdown Remains Canonical Memory

Decision: keep Markdown frontmatter and typed edges as the durable source of
truth. Databases, dashboards, vector stores, MCP servers, and plugins can
accelerate runtime use, but they remain adapters.
