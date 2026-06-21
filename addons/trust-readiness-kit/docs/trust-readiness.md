# Trust Readiness

Owledge is a local Markdown-first memory kit. It is not a hosted enterprise
server, RBAC platform, encrypted vault, or regulated compliance system.

## What Teams Can Trust

| Area | Current boundary |
| --- | --- |
| Canonical memory | Markdown files in the project or knowledgebase. |
| Runtime capture | Private session artifacts, excluded from shared export by default. |
| Shared export | Requires reviewed and sanitized records. |
| Generated views | Rebuildable indexes, reports, and exports, not source of truth. |
| Scope | Tenant, customer, and project metadata on memory records. |

## What Teams Must Still Own

- Access control to the repository or vault.
- Encryption at rest.
- Backup and retention policy.
- Regulated compliance review.
- Customer-data handling and incident response.

## Evaluation Path

1. Run the five-minute demo.
2. Run `doctor` and `validate-memory --strict`.
3. Review private/shared artifact boundaries.
4. Decide whether runtime hooks are needed.
5. Run the team evaluation checklist before using real customer data.

