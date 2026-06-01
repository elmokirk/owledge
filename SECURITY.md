# Security Policy

## Supported Status

This repository is currently a concept-validated standalone kit. It is not yet certified for regulated production use.

| Area | Status |
| --- | --- |
| Markdown memory contracts | Implemented |
| Private/shared corpus separation | Implemented |
| Raw session exclusion from shared RAG | Implemented |
| Tenant/customer/project metadata | Implemented |
| Automated PII detection | Roadmap |
| Secret scanning | Roadmap |
| Encryption at rest | Roadmap |
| Role-based access control | Roadmap |
| Audit-grade promotion logs | Roadmap |

The optional Compliance Light add-on adds local evidence templates and read-only
checks. It does not implement RBAC, encryption, secure MCP, tamper-proof audit
logs, or regulated enterprise controls.

## Reporting

Do not include secrets, customer data, personal data, or private transcripts in public issues.

For now, report security issues privately to the repository owner. A dedicated security contact should be added before public production adoption.

## Current Safe-Use Rules

- Do not commit `.agent-control/secrets/`, runtime databases, raw scratch files, or customer secrets.
- Treat `agent-memory/sessions/` as private working memory.
- Export shared RAG only from reviewed and sanitized artifacts.
- Keep customer-specific memory scoped by `tenant_id`, `customer_id`, and `project_id`.
- Run validation before export or promotion.
