---
memory_id: "mem:owledge:global:owledge:ticket:post-v1-repository-consolidation-001"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "task"
artifact_type: "post_release_ticket"
document_version: 1
status: "active"
priority: "P0"
visibility: "private"
data_class: "internal"
semantic_title: "Consolidate Owledge repository truth and CI boundaries"
summary: "Run the next-start cleanup session that separates V1 product code, legacy compatibility, dogfood memory, documentation, packaging, and release infrastructure."
concept_tags: ["p0", "cleanup", "repository", "ci", "architecture"]
stack_tags: ["python", "github-actions", "packaging"]
problem_patterns: ["multiple-sources-of-truth", "cross-layer-ci-cascade", "legacy-v1-contract-drift"]
architecture_patterns: ["single-source-of-truth", "layered-ci-gates", "explicit-product-boundary"]
failure_modes: ["small-change-wide-regression", "stale-contract-preservation", "expensive-release-diagnosis"]
reusable_lessons:
  - "A release repository stays operable only when product, compatibility, dogfood, and release contracts have explicit owners and non-overlapping gates."
confidence: 1.0
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-22T00:00:00+02:00"
updated_at: "2026-08-22T00:00:00+02:00"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:workpackage:2026-08-21-ci-cli-pipeline-repair"
    confidence: 1.0
    reason: "The CI repair exposed systemic truth and gate coupling that must be removed in a dedicated session."
---

# POST-V1-REPOSITORY-CONSOLIDATION-001 — P0 repository cleanup

## Next-start directive

Start the next Owledge work session with this ticket before feature work. This
ticket is deliberately recorded by the CI repair but is not implemented on the
CI repair branch.

## Outcome

Produce one explicit repository map and one canonical source for every active
version, product, packaging, documentation, compatibility, and release
contract. Separate V1 product code, legacy compatibility, maintainer dogfood,
historical evidence, and release infrastructure so that a change in one layer
does not silently redefine another.

## Required work

1. Inventory every top-level surface and assign an owner, lifecycle, publish
   boundary, and CI gate.
2. Identify duplicate or stale truth across version files, manifests, fixtures,
   generated memory, public docs, and workflow assertions.
3. Remove dead material or move intentionally historical material behind an
   explicit archive boundary; preserve evidence needed for auditability.
4. Split CI into fast pull-request contracts, bounded platform smokes, and full
   release gates while preserving all security and release requirements.
5. Make archive membership and installed-package behavior executable contracts
   against built artifacts rather than duplicated text assertions.

## Acceptance evidence

- One reviewed ownership/boundary map covers every retained repository surface.
- Active version and release state have one canonical machine-checked source.
- No active V1 assertion depends on an unexplained legacy fixture or historical
  document.
- PR gates identify one owning component per failure and complete without the
  full release suite when release-only surfaces are unchanged.
- Full unit, docs, packaging, security, and release gates remain green; no skip,
  allowlist broadening, or weakened assertion is accepted as cleanup.

