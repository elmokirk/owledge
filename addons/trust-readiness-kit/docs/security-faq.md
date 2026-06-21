# Security FAQ

## Does Owledge send memory to a hosted service?

No. The core kit is local and file-based. External agents or retrieval systems
may consume exports only when the user configures them.

## Are raw session logs shared?

No. Raw runtime session artifacts are private working memory and are excluded
from shared exports by default.

## Is Owledge enterprise-compliance-ready?

No. Owledge provides local memory contracts, privacy defaults, validation, and
Compliance Light templates. It does not provide RBAC, encryption at rest,
tamper-proof audit logs, or regulated certification.

## What should teams run before sharing memory?

Run validation, sensitive-data scan, and export gates. Share only reviewed and
sanitized artifacts.

