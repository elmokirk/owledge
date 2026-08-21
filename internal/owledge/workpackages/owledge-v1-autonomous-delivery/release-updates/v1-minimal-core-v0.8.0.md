---
memory_id: "mem:owledge:global:owledge:release:v1-minimal-core-v0.8.0"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "release_update"
artifact_type: "release_notes"
document_version: 1
status: "approved_for_publication"
visibility: "public"
data_class: "public"
semantic_title: "Owledge V1 Minimal Core — v0.8.0"
summary: "Local-first Owledge V1 Minimal Core: deterministic project and private user-global knowledge, bounded lifecycle and three thin adapters."
concept_tags: ["v1", "v0.8.0", "release", "local-first"]
stack_tags: ["python", "markdown", "mcp", "codex", "claude-code"]
confidence: 0.98
review_status: "owner_approved"
sanitization_status: "verified"
created_at: "2026-08-21T00:00:00+02:00"
updated_at: "2026-08-21T00:00:00+02:00"
source_hash: ""
---

# Owledge V1 Minimal Core — v0.8.0

`v0.8.0` is the package/tag version. **V1 Minimal Core** is the shipped product
boundary: a standalone local knowledge Core, a private local user-global
Null-Space, and thin Codex, Claude Code, and generic MCP/CLI adapters.

## What ships

- Principles-only entry path and a small default install; the public Core has
  eight operations: `init`, `doctor`, `recall`, `context`, `propose`, `review`,
  `sync`, and `upgrade`.
- Explicit local project linking to a two-scope model: `project_user` and
  allowlisted local `user_global`; no implicit discovery, remote sync, cloud,
  model, vector database, or enterprise scope.
- Deterministic recall and budgeted context with source, revision, exclusion and
  untrusted-content provenance receipts.
- Candidate-only proposal, parking/resurfacing for planning, reviewed promotion,
  reject/supersede/tombstone propagation, health and recovery.
- Codex, Claude Code and generic MCP/CLI bridges; the generic default exposes
  exactly five tools and all adapters use the same Core lifecycle.
- Safe local init/upgrade/recovery, local-only path boundaries, offline Core
  journey, and reproducible Core-only wheel/sdist artifacts.

## Release evidence

- Candidate source: `ec28349`; gate record: `230fc0f`.
- Normalized wheel SHA-256: `8e36323a565a9ffd04cdd8635ed6c1bd074ebadf6f38f678e270c56b98a79a91`.
- Normalized sdist SHA-256: `8e634a58d2e918d4607462add8120e77fe29109cab0597d971a1b312be8a458e`.
- Independent GA QA: accepted, 95/100, no P0/P1/P2 findings.

## Scope and platform limits

This release makes no Hub, Pi, LightRAG, Documentation Compiler, enterprise,
remote-sync, marketplace, benchmark, macOS or Linux support claim. Windows
wheel proof is executed; macOS/Linux evidence is tracked openly in
`POST-V1-PLATFORM-001`.
