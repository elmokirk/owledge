# Local Kit Threat Model

## Assets

- Project memory and decisions.
- Private session logs.
- Customer or personal data accidentally written to Markdown.
- Generated exports that may enter retrieval systems.

## Main Risks

| Risk | Current mitigation |
| --- | --- |
| Raw runtime logs exported to shared RAG | Shared export gates exclude private and unsanitized records. |
| Sensitive data committed | Sensitive-data scan and `.gitignore` defaults reduce risk. |
| Generated report treated as truth | Docs state Markdown is canonical and generated views are rebuildable. |
| Cross-customer leakage | Tenant/customer/project metadata is required on memory records. |
| Overclaiming compliance | Security docs state that regulated production controls are not implemented. |

## Out Of Scope

- RBAC.
- Encryption at rest.
- Tamper-proof audit logs.
- Hosted policy enforcement.
- Regulated compliance certification.

