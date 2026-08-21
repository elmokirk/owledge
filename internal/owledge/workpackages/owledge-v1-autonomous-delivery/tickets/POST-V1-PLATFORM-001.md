---
memory_id: "mem:owledge:global:owledge:ticket:post-v1-platform-001"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "task"
artifact_type: "post_release_ticket"
document_version: 1
status: "active"
priority: "P1"
visibility: "private"
data_class: "internal"
semantic_title: "Execute macOS and Linux wheel-only proof for Owledge v0.8.0"
summary: "Run the verified V1 Minimal Core wheel journey on macOS and Linux and record platform-specific receipts without changing the release scope."
concept_tags: ["post-release", "macos", "linux", "wheel", "qa"]
stack_tags: ["python", "uv", "wheel"]
problem_patterns: ["cross-platform-claim-without-evidence", "source-smoke-substituted-for-wheel-proof"]
architecture_patterns: ["platform-specific-release-receipt", "wheel-only-install-smoke"]
failure_modes: ["unsupported-platform-claim", "network-dependent-install-proof"]
reusable_lessons:
  - "Cross-platform support claims require separate wheel-only receipts from every named host platform."
confidence: 0.99
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-08-21T00:00:00+02:00"
updated_at: "2026-08-21T00:00:00+02:00"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:decision:v1-publication-cross-platform-followup-2026-08-21"
    confidence: 1.0
    reason: "Carries the explicit non-blocking cross-platform follow-up."
---

# POST-V1-PLATFORM-001 — macOS and Linux wheel-only evidence

## Outcome

Produce separate macOS and Linux receipts for the published `v0.8.0` wheel:
offline install, imported-origin assertion, full init with explicit local
user-global link, Generic five-tool bridge, doctor, and artifact hash match.

## Boundary

- Status: **open**, post-release follow-up; it is not a V1M gate dependency.
- Do not add a macOS/Linux support claim until both receipts are accepted.
- Use the published release artifact or a byte-identical hash match; do not
  substitute a source checkout proof.
- Record capability-limited symlink/junction fixtures honestly per host.

## Acceptance evidence

1. macOS receipt and Linux receipt name OS, Python, artifact SHA-256 and all
   command exit codes.
2. Each proves no network dependency during the wheel journey.
3. Any failure becomes a bounded release finding; it does not rewrite release
   history or silently broaden support claims.
