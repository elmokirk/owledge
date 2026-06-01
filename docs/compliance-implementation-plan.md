# Compliance Implementation Plan

Date: 2026-05-16  
Status: implementation plan  
Depends on: `docs/compliance-roadmap.md`

## Goal

Turn the compliance roadmap into testable repository capabilities. The plan intentionally starts with metadata, schemas and doctor checks before adding enterprise runtime features.

## Phase 0: Baseline And Inventory

Objective: make compliance scope explicit per project.

Deliverables:

| Deliverable | Path |
| --- | --- |
| Compliance workspace directories | `agent-memory/compliance/`, `agent-memory/compliance/registers/`, `agent-memory/compliance/incidents/`, `agent-memory/compliance/dpia/`, `agent-memory/compliance/ai-systems/` |
| Processing activity template | `agent-memory/templates/processing-activity-template.md` |
| Provider registry template | `agent-memory/templates/provider-registry-template.md` |
| AI system inventory template | `agent-memory/templates/ai-system-template.md` |
| Compliance frontmatter schema | `agent-memory/schemas/compliance-record.schema.json` |
| Compliance command reference | `docs/compliance-operations.md` |

Acceptance tests:

- A new host project can create a processing inventory without manual folder setup.
- Validation fails when tenant/customer/project, owner, purpose, legal basis or retention class are missing.

## Phase 1: Data Protection Core

Objective: implement GDPR/BDSG operational workflows.

Deliverables:

| Deliverable | Path |
| --- | --- |
| DPIA/DSFA trigger template | `agent-memory/templates/dpia-trigger-template.md` |
| Data subject request template | `agent-memory/templates/data-subject-request-template.md` |
| Retention policy template | `agent-memory/templates/retention-policy-template.md` |
| Transfer assessment template | `agent-memory/templates/transfer-assessment-template.md` |
| Redaction policy | `agent-memory/compliance/redaction-policy.md` |
| Compliance doctor command | `tools/compliance-doctor.ps1` and CLI subcommand |
| PII/secret scan command | `tools/scan-memory-sensitive-data.ps1` and CLI subcommand |
| Retention audit command | `tools/audit-retention.ps1` and CLI subcommand |

Acceptance tests:

- Shared export is blocked when `data_class=personal`, `special-category`, `confidential`, or `sanitization_status!=approved`.
- DSAR export finds canonical, compiled, evidence and generated index references for a test subject.
- Retention audit reports expired raw sessions and can produce a purge/anonymization preview.

## Phase 2: AI Act Readiness

Objective: make agent and model use governable.

Deliverables:

| Deliverable | Path |
| --- | --- |
| AI risk classification template | `agent-memory/templates/ai-risk-classification-template.md` |
| AI literacy checklist | `agent-memory/templates/ai-literacy-checklist-template.md` |
| Prohibited-practice checklist | `agent-memory/templates/prohibited-ai-practice-checklist-template.md` |
| Model/provider registry schema | `agent-memory/schemas/provider.schema.json` |
| AI system schema | `agent-memory/schemas/ai-system.schema.json` |
| AI inventory command | `tools/build-ai-system-inventory.ps1` and CLI subcommand |

Acceptance tests:

- Any configured model/provider without data-use, region, logging and retention metadata is reported.
- High-impact workflows cannot promote outputs without a human review artifact.
- AI-generated customer report fixture includes required internal provenance and disclosure metadata.

## Phase 3: Incident, Security And Supply Chain

Objective: provide security evidence appropriate for agency and enterprise use.

Deliverables:

| Deliverable | Path |
| --- | --- |
| Incident template | `agent-memory/templates/security-incident-template.md` |
| Breach assessment template | `agent-memory/templates/breach-assessment-template.md` |
| Security baseline map | `agent-memory/compliance/security-baseline.md` |
| Vendor/sub-processor register | `agent-memory/compliance/registers/vendors.md` |
| Dependency and plugin provenance report | `agent-memory/compliance/registers/supply-chain.md` |
| Incident pack command | `tools/build-incident-pack.ps1` and CLI subcommand |

Acceptance tests:

- Incident fixture produces severity, affected data, notification clock, owner and postmortem fields.
- Vendor registry blocks production readiness when a provider lacks DPA/transfer metadata.
- Supply-chain report lists plugins, scripts and model/provider dependencies.

## Phase 4: Enterprise Hub And Multi-Team Controls

Objective: support multiple developers, tenants, customers and agents safely.

Deliverables:

| Deliverable | Path |
| --- | --- |
| Tenant registry schema | extend `agent-memory/schemas/tenant.schema.json` |
| Access policy template | `agent-memory/templates/access-policy-template.md` |
| Enterprise hub layout doc | `docs/enterprise-hub.md` |
| Promotion audit hardening | extend `tools/promote-memory.ps1` and CLI subcommand |
| Scoped export defaults | extend RAG/LightRAG/GraphRAG export commands |
| Compliance dashboard report | extend `tools/render-memory-report.ps1` |

Acceptance tests:

- Exports require tenant/customer/project scope when multiple projects exist.
- Cross-tenant shared export is blocked unless records are approved, sanitized and explicitly shared.
- Promotion evidence records reviewer, timestamp, source hash, target hash and reason.

## Phase 5: Secure MCP And External Agent Access

Objective: make VPS/external agents useful without direct vault access.

Deliverables:

| Deliverable | Path |
| --- | --- |
| MCP adapter design | `docs/mcp-compliance-adapter.md` |
| Resource permission map | `agent-memory/compliance/mcp-resource-policy.md` |
| Read-only context-pack endpoint/tool | adapter implementation |
| Append-only evidence/handoff endpoint/tool | adapter implementation |
| OAuth/token and local stdio profiles | adapter configuration |
| MCP audit log schema | `agent-memory/schemas/mcp-audit-event.schema.json` |

Acceptance tests:

- MCP resources reject path traversal and unknown tenant/customer/project scopes.
- HTTP transport requires authentication and logs every read/write.
- External agents can read approved context packs and append evidence, but cannot edit canonical memory.

## Phase 6: Release Assurance

Objective: make compliance claims repeatable.

Deliverables:

| Deliverable | Path |
| --- | --- |
| Compliance fixture suite | `tests/compliance/` |
| Release gate command | `tools/run-compliance-gates.ps1` |
| Customer compliance pack report | report renderer extension |
| Legal sign-off artifact template | `agent-memory/templates/legal-signoff-template.md` |

Acceptance tests:

- `run-compliance-gates` runs doctor, validation, sensitive-data scan, export safety, retention audit and AI inventory checks.
- Customer compliance pack includes scope, exclusions, evidence, open risks and version hashes.
- Roadmap watch artifacts are present and dated.

## Recommended Build Order

1. Phase 0 and Phase 1 first. They convert compliance from aspiration into testable metadata.
2. Phase 2 before any customer-facing AI/RAG automation claim.
3. Phase 3 before agency production use.
4. Phase 4 before multiple developers or multiple customers use a shared hub.
5. Phase 5 before external VPS agents, MCP, or third-party orchestration.
6. Phase 6 before public production-ready positioning.

## Initial Task Backlog

| Priority | Task |
| --- | --- |
| P0 | Add `agent-memory/compliance/` directory structure and templates |
| P0 | Add compliance schemas for processing activity, provider registry, AI system, DPIA and DSAR |
| P0 | Add `compliance-doctor` read-only checks |
| P1 | Add sensitive-data scanner with redaction policy |
| P1 | Add retention audit and purge/anonymization preview |
| P1 | Add DSAR export/delete preview workflow |
| P1 | Harden shared export checks with compliance metadata |
| P2 | Add AI system inventory and AI Act risk classification |
| P2 | Add provider registry and transfer assessment checks |
| P2 | Add incident pack and security baseline evidence |
| P3 | Add enterprise hub scoped exports and access policy |
| P3 | Design and implement secure MCP adapter |
| P3 | Add compliance release gate and customer pack report |

## Final Review Checklist

Before calling the roadmap implemented:

- Every phase has at least one automated test or fixture.
- No compliance-critical command mutates data without preview or explicit confirmation.
- Shared exports are denied by default unless review and sanitization are approved.
- Legal counsel or the project owner has reviewed regulated deployment assumptions.
- The regulatory watch artifact has a current review date.
