---
memory_id: "mem:owledge:global:owledge:decision:v1-schema-global-knowledge-health-matrix-2026-08-12"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "decision_record"
document_version: 2
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v1 schema, global knowledge, health, and maturity decision matrix"
summary: "Owner-approved durable record of the evaluated architecture variants, locked 1B+/2C+/3B selection, and V1 cutline for document revision, hierarchical global knowledge, Knowledge Health, and product maturity."
concept_tags: ["decision-matrix", "schema-registry", "global-knowledge", "knowledge-health", "product-maturity"]
stack_tags: ["markdown", "python", "mcp", "git"]
problem_patterns: ["frontmatter-bloat", "global-copy-pollution", "lost-project-detail", "unhealthy-knowledge-base", "premature-enterprise-claim"]
architecture_patterns: ["artifact-profiles", "provenance-preserving-abstraction-dag", "orient-high-verify-low", "deep-health-module"]
failure_modes: ["material-edit-without-version-bump", "raw-inbox-used-as-knowledge-base", "unauthorized-project-drilldown", "monitoring-content-leak", "enterprise-ready-before-proof"]
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-12T01:47:18+02:00"
updated_at: "2026-08-12T13:59:20+02:00"
source_hash: ""
reusable_lessons:
  - "Scope, abstraction, and lifecycle must remain orthogonal or global knowledge becomes unmaintainable."
  - "A global essence is useful only when an authorized caller can verify its exact project and Evidence revisions."
  - "Enterprise architecture intent and proven enterprise operating maturity require separate claims."
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:plan:v1-federated-research-memory-pi-reprioritization"
    confidence: 1.0
    reason: "Records the alternatives and owner feedback that revise this plan."
  - type: "relates_to"
    target: "mem:owledge:global:owledge:research:hierarchical-memory-global-essence-source-drilldown-arxiv-2026-08-12"
    confidence: 0.95
    reason: "Primary arXiv sources support provenance-preserving hierarchical abstraction and source drill-down."
---

# Owledge V1 Decision Matrix: Schema, Global Knowledge, Health, and Maturity

## Decision Status

The product owner approved **`1B+ / 2C+ / 3B`** on 2026-08-12. The selection is
now the locked architecture baseline for V1 planning. It does not authorize
V0.8 implementation and does not change the current `OW-071-05` execution state
or `G-071-ALIGNMENT` stop.

### Owner Requirements Recorded

1. Every material edit to an Owledge-managed artifact requires an explicit
   document version bump.
2. Large and enterprise knowledge bases require a bounded Health and Monitoring
   layer for maintainability and scale.
3. Project-scoped details and initial Research files must remain discoverable
   during an authorized explicit deep dive.
4. The promoted global layer is a central Knowledge Base that condenses
   Research, learnings, patterns, and transferable concepts into reviewed essences.
5. Global Raw remains the pre-promotion review queue and must not be confused
   with the promoted global Knowledge Base.

### Locked Owner Selection

| ID | Revised recommendation | Status |
| --- | --- | --- |
| D1 | `1B+`: small common envelope plus versioned artifact profiles and required monotonic `document_version` | owner-approved; locked for V1 |
| D2 | `2C+`: bounded delta capsule by default, policy snapshot exception, promoted global essence, authorized project/Evidence drill-down | owner-approved; locked for V1 |
| D3 | `3B`: Standalone Core GA plus Single-Organization Hub Pilot/Beta; enterprise-viable architecture claim only | owner-approved; locked for V1 |

## Unified Scoring

Score weights are 25% Core Fit, 20% User Value, 20% Architecture Leverage,
15% Trust/Risk Reduction, 10% Adoption, and 10% inverse Complexity.

### D1 — Frontmatter and Document Revision

| Option | Description | Score | Reversibility | Main failure cost | Disposition |
| --- | --- | ---: | --- | --- | --- |
| 1A | Keep the current broad global required-field list | 55 | medium-low | dummy metadata, context pollution, schema ossification | not recommended |
| 1B+ | Small common envelope plus profiles; separate schema/profile/document versions and content hash | 96 | very high | one-time registry and compatibility work | recommended |
| 1C | Minimal envelope plus largely free namespaced extensions | 71 | low-medium | semantic dialects and adapter disagreement | preserve as extension mechanism only |
| 1D | Independent schemas without a shared envelope | 46 | low | inconsistent identity, scope, provenance, and lifecycle | reject |

`1B+` uses distinct facts:

- `schema_version`: common-envelope contract shape;
- `profile_version`: artifact-specific rules;
- `document_version`: positive monotonic revision, incremented by exactly one
  for every accepted material edit under the same stable `memory_id`;
- `source_hash`: exact content/integrity fact;
- `updated_at`: time of accepted revision.

Legacy domain aliases such as `plan_version` remain readable during the
compatibility window but cannot replace the generic document revision.

### D2 — Global Raw, Global Knowledge Base, and Project Drill-Down

| Option | Description | Score | Reversibility | Main failure cost | Disposition |
| --- | --- | ---: | --- | --- | --- |
| 2A | Source pointer only | 75 | medium | lost context when source is missing; weak review value | reject as default |
| 2B | Self-explanatory reusable delta capsule plus source refs; never snapshot | 86 | high | volatile source may become unverifiable | safe minimal profile |
| 2C+ | Delta capsule default; policy snapshot exception; reviewed global essence with authorized drill-down | 96 | very high | bounded policy and resolver implementation | recommended |
| 2D | Copy complete project/source content into global storage by default | 45 | very low | leakage, stale shadows, deletion/retention burden, context pollution | reject |

`2C+` is a provenance-preserving abstraction DAG:

```text
project source/Evidence
  -> project finding or canonical detail
  -> cross-project essence candidate in Global Raw
  -> reviewed user-global or enterprise essence
```

Retrieval follows `orient high, verify low`:

1. Answer bounded orientation questions from reviewed global essences.
2. Use `explain` to expand cited canonical detail.
3. Use `deep_dive` to resolve the exact project/source revision only after a
   fresh principal, project, scope, data-class, availability, freshness, and
   token-budget check.
4. Use `refresh` only for a stale or missing delta.

A caller allowed to read a global essence is not automatically allowed to learn
the existence, title, path, or content of every project source behind it.

### D3 — Product Maturity Claim

| Option | Description | Score | Reversibility | Main failure cost | Disposition |
| --- | --- | ---: | --- | --- | --- |
| 3A | Label the entire product Pilot/Beta | 79 | high | understates a stable Standalone Core | acceptable but too broad |
| 3B | Standalone Core GA plus Single-Organization Hub Pilot/Beta | 97 | very high | requires precise split messaging | recommended |
| 3C | Self-hosted Team-ready GA | 78 | medium | raises support/recovery expectations before proof | promotion stage after gates |
| 3D | Market V1 as Enterprise-ready | 43 | very low | security, contractual, support, and reputation exposure | reject until exit evidence |

Paid self-hosted setup, integration, migration, and support may be sold under
`3B`; an Enterprise-ready claim remains evidence-gated.

## Knowledge Model: Three Independent Axes

| Axis | Examples | Meaning |
| --- | --- | --- |
| Authority scope | `project_user`, `user_global`, `enterprise` | who may act |
| Abstraction | `source_evidence`, `canonical_detail`, `compiled_context`, `global_essence` | how condensed the knowledge is |
| Lifecycle | `candidate`, `raw_inbox`, `reviewed`, `canonical`, `superseded`, `archived` | how trusted/retrievable it is |

The global Knowledge Base is therefore not a fourth authorization scope and
Global Raw is not a lower semantic knowledge level. Conflating these axes would
make permission checks, freshness, promotion, and retrieval ambiguous.

## Health and Monitoring Cutline

| Module/interface | V1 responsibility | Explicit non-goal |
| --- | --- | --- |
| Knowledge Health | deterministic schema/revision, identity, edge, source, freshness, conflict, promotion-debt, projection, context-budget, and scope-integrity report | no LLM judge and no content rewriting |
| Hub Operations Health | readiness, latency/error, queue, auth-failure, storage, backup-age, index-lag, restore status | no knowledge bodies, raw prompts, or raw outputs in telemetry |
| Monitoring adapter | export privacy-safe metrics and stable artifact/run/receipt IDs | no mandatory vendor and no canonical state |
| Dashboard | optional read-only consumer after the report contracts are proven | not a V1 proof dependency |

## Paper Evidence and Identification Limit

The owner did not provide a title or arXiv ID, so the intended paper must not be
guessed. The strongest plausible primary sources are:

- [HORMA](https://arxiv.org/abs/2606.11680): structured hierarchical notes with
  references to timestamped raw trajectories;
- [H-MEM](https://arxiv.org/abs/2507.22925): Domain, Category, Memory Trace, and
  Episode levels with top-down child traversal;
- [HiGMem](https://arxiv.org/abs/2604.18349): bidirectionally linked Event
  summaries and raw Turn evidence;
- [Generative Agents](https://arxiv.org/abs/2304.03442): recursive reflections
  that retain citations to supporting memories.

The durable comparison is captured in
`internal/owledge/research/hierarchical-memory-global-essence-source-drilldown-arxiv-2026-08-12.md`.
These papers support hierarchical abstraction and evidence traversal, not
Owledge's authorization, promotion, privacy, or canonical-Markdown policies.

## Owner Decision

The product owner selected **`1B+ / 2C+ / 3B`** on 2026-08-12. This combination
adds document revision, global essence plus project drill-down, and bounded
health while preserving the lean Standalone Core and a truthful Hub maturity
claim. Any future deviation requires a new versioned owner decision rather than
an implicit implementation change.
