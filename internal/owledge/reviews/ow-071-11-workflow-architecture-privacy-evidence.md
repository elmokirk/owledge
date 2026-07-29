---
memory_id: "mem:owledge:global:owledge:evidence:ow-071-11-workflow-architecture-privacy"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "evidence"
artifact_type: "ticket-evidence"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "OW-071-11 workflow, architecture, and privacy acceptance evidence"
summary: "Evidence binding the canonical lifecycle guide and independent architecture/privacy QA to commits 75c1336, ced989d, and 175a737."
concept_tags: ["v0.7.1", "workflow", "privacy", "authority", "adoption"]
stack_tags: ["markdown", "mermaid", "python", "git"]
problem_patterns: ["automatic-promotion-claim", "unmapped-lifecycle-diagram", "privacy-boundary-ambiguity"]
architecture_patterns: ["markdown-canonical-truth", "human-curated-promotion", "read-only-mcp"]
failure_modes: ["generated-view-as-authority", "hosted-sync-overclaim", "harness-discovery-overclaim"]
reusable_lessons:
  - "A lifecycle diagram needs a checked node-to-artifact mapping, not only explanatory prose."
  - "Automation documentation must distinguish an event hook or harness discovery from authority to promote truth."
confidence: 0.97
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-29T23:00:00+02:00"
updated_at: "2026-07-29T23:00:00+02:00"
retention_class: "standard"
last_reviewed_at: "2026-07-29T23:00:00+02:00"
review_cycle: "per-release"
source_hash: "175a737"
edges:
  - type: "evidence_for"
    target: "OW-071-11"
    confidence: 1.0
    reason: "Binds focused tests, docs gates, and independent acceptance to the accepted source commits."
---

# OW-071-11 workflow, architecture, and privacy acceptance evidence

## Accepted source

| Commit | Purpose |
| --- | --- |
| `75c1336` | Adds the canonical lifecycle page, authority matrix, routes, and initial contract fixture. |
| `ced989d` | Adds explicit setup, plan/resume, KB, multi-agent workflows, glossary, and node traceability. |
| `175a737` | Closes the final diagram-node mapping gap and removes glossary mojibake. |

The canonical public page is `docs/how-owledge-works.md`; it is routed from
`docs/what-is-owledge.md` and `docs/README.md`.

## Positive and negative verification

| Check | Result | Scope |
| --- | --- | --- |
| `python -m unittest tests.unit.test_ow07111_workflow_docs -v` | pass, 6/6 | Mermaid/prose fallback, all diagram nodes, matrix, privacy boundaries, routing, workflow variants, glossary |
| `python tools/owledge.py test public-docs --project-root .` | pass, 252/252 | public documentation surface and encoding/claim checks |
| `python tools/owledge.py test docs-contract --project-root .` | pass | relative links and public documentation contract |
| `git diff --check` | pass | whitespace safety before each source commit |
| Independent architecture/privacy QA | pass, 97/100 | no open P0/P1/P2 after two focused re-reviews |

The negative contract is explicit: Owledge is not described as a runtime,
hosted store, automatic truth engine, automatic promoter, required vector
database, hosted synchronization service, or autonomous background scheduler.
MCP remains a read-only P0 profile; hooks and harness discovery do not confer
promotion authority.

## Review history and reflection

The first independent review scored the initial commit 82/100 and identified
two P1 gaps: missing explicit setup/plan/resume/KB/glossary workflows and an
incomplete diagram-node-to-artifact mapping. `ced989d` closed the first P1 and
most of the second. The re-review (90/100) found one omitted candidate/revise
node plus mojibake in the glossary. `175a737` added the missing mapping and
replaced the corrupted characters; the final re-review accepted the ticket at
97/100.

Decision: keep authority language fail-closed. A person remains the promotion
authority, and generated artifacts remain rebuildable views. This does not
broaden the local HTTP, Team Hub, remote sync, or write-enabled MCP surface.

## Next-plan effect

`OW-071-11` is done. `OW-071-10` remains externally blocked only on supported
Python package-artifact and cross-platform evidence. The next sole active
non-overlapping Phase 071-B2 lane is `OW-071-12`; it must preserve the skill
discovery boundary documented here and cannot claim generic discovery from
`.owledge/skills`.
