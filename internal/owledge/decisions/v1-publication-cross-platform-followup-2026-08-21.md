---
memory_id: "mem:owledge:global:owledge:decision:v1-publication-cross-platform-followup-2026-08-21"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "decision"
artifact_type: "release_decision"
document_version: 1
status: "accepted"
visibility: "private"
data_class: "internal"
semantic_title: "V1 publication authorization with cross-platform follow-up"
summary: "The owner authorizes publication of the verified local V1 candidate as package v0.8.0 while macOS/Linux wheel proof remains an explicit open follow-up, not a support claim."
concept_tags: ["v1", "publication", "cross-platform", "release"]
stack_tags: ["python", "wheel", "sdist", "github"]
confidence: 1.0
review_status: "owner_approved"
sanitization_status: "not_required"
created_at: "2026-08-21T00:00:00+02:00"
updated_at: "2026-08-21T00:00:00+02:00"
source_hash: ""
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:plan:v1-minimal-core-finalization"
    confidence: 1.0
    reason: "Records the V1M-11 owner decision."
---

# V1 publication authorization and cross-platform follow-up

## Owner decision

On 2026-08-21 the owner authorized V1M-11 external actions for the verified
Minimal Core candidate: push a `release/v0.8.0` branch, execute the existing
release workflow, then let its PyPI-confirmed promotion create the annotated
`v0.8.0` tag and public release. The package/tag stays `v0.8.0`; **V1** names
the product scope and GA capability boundary, not a semantic-version bump to
1.0.0.

## Explicit residual risk

Windows wheel-only proof is executed. macOS and Linux wheel-only proof is not
executed. This is tracked as open ticket `POST-V1-PLATFORM-001`; it does not
block this owner-authorized publication and does not justify any macOS/Linux
support claim. Public materials must retain that limitation until the ticket is
closed with executed evidence.

## Non-decisions

- No Hub, Pi, LightRAG, Documentation Compiler, enterprise scope, remote sync,
  or other parked capability is reactivated.
- No platform certification, marketplace certification, or broad benchmark
  claim is authorized.
- A failed remote authentication, upload, or release API call leaves V1M-11
  open; it is never treated as a successful publication.
