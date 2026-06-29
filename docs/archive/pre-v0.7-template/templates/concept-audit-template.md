---
memory_id: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:concept_audit:YYYY-MM-DD"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project_id: "PROJECT_ID"
title: "Concept Audit YYYY-MM-DD"
status: "draft"
type: "concept-audit"
date: "YYYY-MM-DD"
owledge_kit_version: "0.6.1"
version: "1.0.0"
owner: "OWNER"
session_id: "YYYY-MM-DD-concept-audit"
agent_id: "concept-auditor"
parent_session: ""
related_files: []
tags:
  - concept-audit
  - blindspot
  - self-description
---

# Concept Audit YYYY-MM-DD

## Summary

One-paragraph summary of what was audited, the `project_mode`, the
`planning_mode`, the overall pass state, and the headline finding.

- Project mode: `poc | mvp | side | saas`
- Planning mode: `supervised | approve-automatically | full-access`
- Overall passed: `true | false`
- Dimensions scored: `N of 8`
- Next audit due: `YYYY-MM-DD` (audit date + `freshness_days`)

## Dimension Scores

| # | Dimension | Type | Score | Findings |
| --- | --- | --- | --- | --- |
| 1 | Lifecycle & upgrade | mechanical | 0-10 | count |
| 2 | Distribution integrity | mechanical | 0-10 | count |
| 3 | Dogfood fidelity | mechanical | 0-10 | count |
| 4 | Contract completeness | mechanical | 0-10 | count |
| 5 | Cross-layer integrity | guided | 0-10 | count |
| 6 | Failure-mode coverage | guided | 0-10 | count |
| 7 | Conceptual coherence | guided | 0-10 | count |
| 8 | Self-description accuracy | guided | 0-10 | count |

Weighted total: `N` (computed from `concept-audit-profile.json` weights).

## Findings

### Dimension 1 — Lifecycle & upgrade

For each finding:

- **Severity:** `error | warning | info`
- **Detail:** what was found
- **Evidence:** command output, file path, or frontmatter snippet
- **Recommendation:** the concrete fix

### Dimension 2 — Distribution integrity

(Repeat the per-finding structure above.)

### Dimension 3 — Dogfood fidelity

(Repeat the per-finding structure above.)

### Dimension 4 — Contract completeness

(Repeat the per-finding structure above.)

### Dimension 5 — Cross-layer integrity (guided)

Worked checklist with evidence per item and the dimension score.

### Dimension 6 — Failure-mode coverage (guided)

Worked checklist with evidence per item and the dimension score.

### Dimension 7 — Conceptual coherence (guided)

Glossary, term-frequency table, synonym audit, version-string comparison, and
the dimension score.

### Dimension 8 — Self-description accuracy (guided)

Claim → file → behavior mapping, self-audit-loop presence, and the dimension
score.

## Suggested Actions

Prioritized list of concrete next actions, one per `error` or `warning`
finding. Each action links back to its finding by dimension number.

1. [P0] Action text (dim N)
2. [P1] Action text (dim N)

## Next Audit Due

- Next audit due: `YYYY-MM-DD`
- Freshness rule: the `concept-audit-fresh` finalization gate warns (or fails
  at `saas`) if no `concept-audit-*.md` is newer than the last `VERSION` bump
  and within `freshness_days`.
- Reminder: this audit is a candidate artifact. Promote findings into
  `canonical/`, `compiled/`, `patterns/`, or `lessons/` only after curator
  review.