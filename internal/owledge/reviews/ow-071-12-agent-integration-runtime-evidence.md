---
memory_id: "mem:owledge:global:owledge:evidence:ow-071-12-agent-integration-runtime"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "evidence"
artifact_type: "ticket-evidence"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "OW-071-12 agent integration and runtime conformance evidence"
summary: "Binds registry, host-mirror fixture, MCP allowlist, runtime smoke, and independent review to c900379, 25b91d8, and a658e2e."
concept_tags: ["v0.7.1", "skills", "agent-integration", "runtime", "mcp"]
stack_tags: ["markdown", "python", "mcp", "git"]
problem_patterns: ["undiscoverable-project-skill", "write-enabled-mcp-inference", "unsafe-mirror-recovery", "unauthenticated-promotion-claim"]
architecture_patterns: ["source-and-discovery-mirror", "read-only-mcp", "owner-controlled-promotion"]
failure_modes: ["maintainer-as-host-proof", "automatic-mirror-overwrite", "workflow-policy-as-technical-authentication"]
reusable_lessons: ["Fresh host fixtures prove discovery; owner approval is workflow policy, not CLI authentication."]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-30T00:15:00+02:00"
updated_at: "2026-07-30T00:15:00+02:00"
retention_class: "standard"
last_reviewed_at: "2026-07-30T00:15:00+02:00"
review_cycle: "per-release"
source_hash: "a658e2e"
edges:
  - type: "evidence_for"
    target: "OW-071-12"
    confidence: 1.0
    reason: "Binds source commits, executable host fixture, runtime checks, and independent review."
---

# OW-071-12 agent integration and runtime conformance evidence

## Accepted source

| Commit | Purpose |
| --- | --- |
| `c900379` | Registry, precedence/execution contract, scenario guide, host-mirror/drift fixture, and docs routes. |
| `25b91d8` | Recovery/promotion truth bounds, full host registry, and live MCP allowlist. |
| `a658e2e` | Final recovery distinction between missing and drifting mirrors. |

## Verification

| Check | Result |
| --- | --- |
| OW-071-12 focused unit suite | pass, 5/5 |
| OW-071-11 + OW-071-12 authority suites | pass, 11/11 |
| Public docs | pass, 254/254 |
| Docs contract, MCP read-only, runtime adapters | pass |
| Independent runtime-conformance QA | pass, 96/100; no open P0/P1/P2 |

Negative contract: `.owledge/skills/` is not automatic discovery; root `skills/` is source/vendor material, not host proof; a missing mirror differs from a user-edited drift; MCP has no write/promotion/sync operation; hooks do not promote; owner approval is workflow policy, not CLI authentication.

## Reflection and next-plan effect

Initial independent QA scored 72/100: recovery and promotion claims overreached; registry and MCP negative proof were incomplete. `25b91d8` closed those P1/P2 findings. A 91/100 re-review found one short-form recovery contradiction; `a658e2e` closed it. Final QA accepted at 96/100. Keep overwrite explicit and owner-approved; do not add automatic repair. `OW-071-12` is done. `OW-071-10` remains externally blocked only on package/cross-platform evidence. `OW-071-14` is next and must not broaden Owlib, local HTTP, MCP, Global/Hub, or Team Hub maturity claims.
