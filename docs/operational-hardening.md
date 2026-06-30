# Operational Hardening Guide

Owledge hardening is intentionally small. The core remains a local
Markdown-first kit; operational checks are read-only or additive unless a human
explicitly promotes or edits memory.

## Parallel Agent Writes

Use separate files for separate agents whenever possible:

- session events under each agent's own `.owledge/sessions/<id>/`
- handoffs under `.owledge/handoffs/`
- evidence under `.owledge/evidence/`
- reviews or QA reports under `.owledge/reviews/` or `.owledge/qa/`

The Python tools use locked atomic writes for generated indexes, exports,
reports, promotion manifests, and runtime session artifacts. That protects
single-file updates, but it is not a substitute for task ownership.

## Conflict Review

When two records disagree, do not overwrite one with the other.

1. Keep both Markdown records.
2. Run `python tools/owledge_core.py --project-root . review-memory-conflicts`.
3. Add a review artifact describing the conflict.
4. Promote a supersession or canonical record only after review approval.

Contradictions are useful evidence. Flattening them too early hides project
history.

## Schema Migration Preview

Schema changes should start as dry-run reports.

- Detect records with missing or old fields.
- Report the proposed field mapping.
- Keep the original Markdown untouched.
- Require owner approval before any rewrite tool exists.

Recommended migration preview fields:

| Field | Purpose |
| --- | --- |
| `schema_version` | Version of the target frontmatter contract |
| `source_path` | Markdown file being evaluated |
| `current_fields` | Fields detected in the source record |
| `proposed_changes` | Non-destructive mapping proposal |
| `requires_review` | Whether a human must resolve ambiguity |

## Red-Team Metrics During Work

Use these gates during implementation:

```bash
python tools/owledge.py test retrieval --project-root .
python tools/owledge.py test quality-ratchet --project-root .
python tools/owledge.py test launch-readiness --project-root .
```

Target metrics:

- Red-team average: `95+`
- Weakest reviewer: `90+`
- Safety/privacy: `100`
- Retrieval safety score: `100`
- Raw session documents in shared retrieval: `0`

## What Not To Add

Do not add a server, RBAC layer, background migration daemon, required vector
database, or autonomous promotion worker as part of hardening. Those are
separate product decisions and would change the core shape of Owledge.
