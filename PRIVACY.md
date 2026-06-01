# Privacy Notice

This project is a Markdown-first agent memory framework. It can store project context, agent sessions, evidence, handoffs, QA reports, and curated knowledge.

## Current Privacy Model

| Data Layer | Default Treatment |
| --- | --- |
| `agent-memory/sessions/` | Private working memory |
| `agent-memory/evidence/` | Private or scoped by metadata |
| `agent-memory/compiled/` | Draft until reviewed |
| `agent-memory/canonical/` | Reviewed project knowledge |
| `agent-memory/patterns/` | Reusable reviewed patterns |
| `agent-memory/lessons/` | Reusable lessons, shared only after sanitization |
| RAG exports | Generated consumer views |

## Important Limitation

This repository does not yet provide automated GDPR or AI Act compliance. It includes metadata fields and workflow rules that support compliance work, but production deployments still need legal review, retention policies, access controls, data processing documentation, and deletion/export procedures.

The optional Compliance Light add-on provides local templates and read-only
checks for this work. It is compliance support only and does not create a
certified or legally complete compliance program.

## Data Minimisation Rules

- Do not capture secrets or unnecessary personal data.
- Do not export raw sessions into shared RAG.
- Prefer summaries, source hashes, and evidence links over long logs.
- Use `visibility`, `data_class`, `review_status`, and `sanitization_status` consistently.
- Delete or anonymize data when it is no longer needed for the defined purpose.
