# HTML Reports

HTML reports are generated views for humans. They must not become canonical memory.

## Report Types

| Report | Use When | Source Files |
| --- | --- | --- |
| Decision report | User asks for visual explanation of decisions or ADRs | `decisions/`, `canonical/`, `evidence/` |
| Handoff report | PM, dev, QA, or agent handoff is requested | `handoffs/`, `sessions/`, `compiled/` |
| RAG readiness report | User asks whether the project is ready for RAG/LightRAG/GraphRAG | `indexes/`, `exports/`, schemas |
| Agent activity report | User asks what agents did or what changed | `sessions/`, `compiled/`, `evidence/` |
| Project dashboard | User asks for stakeholder status overview | `PROJECT_CONTEXT.md`, `canonical/`, `compiled/` |
| Website/UI report | User asks for visual UI, design, branding, or frontend decisions | website docs, decisions, evidence |

## Report Design System

`DESIGN.md` stores the selected report-design system for all generated HTML reports. `REPORT_DESIGN_SELECTOR.html` is a static helper for choosing a visual language and generating an updated `DESIGN.md` block.

The first catalog contains 15 styles:

| ID | Use When |
| --- | --- |
| `atlas-command` | Dense enterprise dashboards and RAG readiness |
| `glass-ledger` | Governance and audit-friendly reporting |
| `signal-grid` | Retrieval metrics and performance reports |
| `courtroom-brief` | ADRs and evidence-heavy decisions |
| `mission-control` | Agent orchestration and delegation |
| `blueprint-studio` | Architecture and implementation planning |
| `executive-ledger` | Client and management summaries |
| `graph-aurora` | GraphRAG and cross-project parallels |
| `monolith-minimal` | Dense technical review |
| `workshop-canvas` | PM/dev handoffs and planning |
| `neon-console` | Runtime and agent activity demos |
| `nordic-clarity` | Customer-safe documentation reports |
| `evidence-vault` | QA gates and provenance reporting |
| `product-lab` | UI and design-token decisions |
| `zeus-celestial` | Strategic narratives and Zeus-style reports |

## Required HTML Metadata

Every report must show:

- generated timestamp
- project id
- report type
- source files
- source hashes
- data class and visibility note
- statement that Markdown remains source of truth

## Interactive Controls

Reports may include client-side controls for:

- density
- font size
- contrast
- section visibility
- design-token sliders
- selected decision state

Interactive choices are presentation state unless an agent explicitly writes them back to Markdown through a reviewed follow-up change.

Persisted visual identity is the exception: selecting a global report style should update `selected_report_design` in `DESIGN.md`.
