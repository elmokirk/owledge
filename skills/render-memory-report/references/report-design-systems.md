# Report Design Systems

Use this reference when the user asks to choose, compare, persist, or apply a visual report style.

## Source Of Truth

- `DESIGN.md` is the canonical report-design decision file.
- `REPORT_DESIGN_SELECTOR.html` is a static visual selector and export helper.
- Generated report HTML must include the selected design id and must not become canonical memory.

## Workflow

1. Read `DESIGN.md`.
2. If the user asks to choose a design, open or modify `REPORT_DESIGN_SELECTOR.html`.
3. Persist the chosen design by setting `selected_report_design` in `DESIGN.md`.
4. Apply the selected design tokens to generated reports.
5. Link sources and hashes in every report.

## Design Options

| ID | Name | Use |
| --- | --- | --- |
| `atlas-command` | Atlas Command | Enterprise operations and RAG readiness |
| `glass-ledger` | Glass Ledger | Governance and audit-friendly reporting |
| `signal-grid` | Signal Grid | Metrics, retrieval evals, and performance |
| `courtroom-brief` | Courtroom Brief | ADRs and evidence-heavy decisions |
| `mission-control` | Mission Control | Agent orchestration and delegation |
| `blueprint-studio` | Blueprint Studio | Architecture and implementation plans |
| `executive-ledger` | Executive Ledger | Client and management summaries |
| `graph-aurora` | Graph Aurora | GraphRAG and cross-project parallels |
| `monolith-minimal` | Monolith Minimal | Dense technical review |
| `workshop-canvas` | Workshop Canvas | PM/dev collaboration and handoffs |
| `neon-console` | Neon Console | Runtime and agent activity demos |
| `nordic-clarity` | Nordic Clarity | Customer-safe readable reports |
| `evidence-vault` | Evidence Vault | QA gates, provenance, and audit views |
| `product-lab` | Product Lab | UI decisions and design-token experiments |
| `zeus-celestial` | Zeus Celestial | Strategic narrative and Zeus-style reports |

## Quality Rules

- Keep CSS local and dependency-free.
- Avoid generic one-note palettes.
- Keep text readable on mobile and desktop.
- Include a machine-readable decision block for design-token reports.
- Never expose private raw sessions in shared visual reports.
