---
selected_report_design: "atlas-command"
design_catalog_version: "0.1.0"
status: "draft"
updated_at: "2026-05-12"
source_of_truth: "DESIGN.md"
applies_to:
  - decision
  - handoff
  - rag-readiness
  - agent-activity
  - project-dashboard
  - website-ui
---

# Report Design System

`DESIGN.md` is the central design decision file for all generated Agent Memory HTML reports. Markdown remains the source of truth. HTML files are generated views and must read this file before choosing colors, spacing, density, and report personality.

## Selected Design

| Field | Value |
| --- | --- |
| Selected design id | `atlas-command` |
| Selected design name | Atlas Command |
| Intended use | Dense enterprise dashboards, multi-agent status reports, RAG readiness views |
| Default density | Compact |
| Default mode | Light |

## Persistence Rule

When a user chooses a report style in `REPORT_DESIGN_SELECTOR.html`, persist the chosen style by updating `selected_report_design` in this file and keeping the selected row below unchanged. Generated reports should include the selected design id in their metadata.

## Branding Model

Current v0.2 behavior is intentionally simple: one global `selected_report_design` controls all generated reports in a project.

Future multi-brand behavior should add named profiles without breaking the current field:

```yaml
selected_report_design: "atlas-command"
brand_profiles:
  default: "atlas-command"
  internal: "signal-grid"
  customer_acme: "nordic-clarity"
  executive: "executive-ledger"
```

Report generation can then accept a future `brand_profile` option while still falling back to `selected_report_design`.

## Design Catalog

| ID | Name | Best For | Visual Character | Primary | Background | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `atlas-command` | Atlas Command | Enterprise operations, RAG readiness, multi-agent dashboards | Command-center clarity with restrained blue, graphite, and crisp tables | `#245c88` | `#f6f7f9` | Can feel too operational for client-facing brand reports |
| `glass-ledger` | Glass Ledger | Governance, audit trails, compliance-adjacent decisions | Translucent panels, precise borders, cool neutrals | `#317873` | `#eef5f3` | Needs careful contrast for dense tables |
| `signal-grid` | Signal Grid | Metrics, retrieval evals, performance reports | High-signal grids, amber accents, terminal-inspired density | `#b36b00` | `#111418` | Dark mode may be too intense for executive exports |
| `courtroom-brief` | Courtroom Brief | ADRs, decisions, risk tradeoffs, evidence chains | Formal legal brief styling with serif headings and warm paper | `#7a3b1f` | `#fbf7ef` | Less suitable for technical dashboards |
| `mission-control` | Mission Control | Agent orchestration, task flow, delegation reports | Dark control-room panels, cyan status accents, strong grouping | `#35b7d8` | `#071117` | Should not be used for printable reports |
| `blueprint-studio` | Blueprint Studio | Architecture, UI systems, implementation plans | Blueprint grid, technical annotations, crisp cyan lines | `#1178a8` | `#edf7fb` | Can overemphasize technical structure |
| `executive-ledger` | Executive Ledger | Client status, management updates, board-style summaries | Quiet premium editorial system with navy, ivory, and gold accents | `#9b7a2f` | `#faf8f1` | Lower visual energy for engineering teams |
| `graph-aurora` | Graph Aurora | GraphRAG, cross-project parallels, semantic maps | Layered graph feel, saturated accent pairs, soft dark canvas | `#78d6a3` | `#10151f` | Needs restraint to avoid decorative noise |
| `monolith-minimal` | Monolith Minimal | Dense technical review, source-heavy reports | Brutal clarity, monochrome, hard lines, compact cards | `#111111` | `#f3f3f0` | Too severe for customer storytelling |
| `workshop-canvas` | Workshop Canvas | PM to dev handoffs, planning sessions, collaborative reviews | Whiteboard structure, sticky-note accents, approachable hierarchy | `#d66a28` | `#fffaf2` | Can feel informal for compliance reports |
| `neon-console` | Neon Console | Runtime logs, agent activity, dev demos | Black console canvas, green/cyan highlights, monospace data blocks | `#39ff88` | `#050806` | Not ideal for long-form reading |
| `nordic-clarity` | Nordic Clarity | Customer-safe reports, documentation, handoffs | Calm light surfaces, cool grays, precise blue-green accents | `#3f8f95` | `#f7faf9` | May feel too quiet for brand selection |
| `evidence-vault` | Evidence Vault | Source provenance, QA gates, audit reports | Secure archive look, dark slate, red/orange status semantics | `#d24b35` | `#111820` | Strong security tone can make normal reports feel high-risk |
| `product-lab` | Product Lab | Website/UI decisions, design tokens, experiments | Modular design-board layout with vivid swatches and sliders | `#e24d7b` | `#fff6f8` | Needs token discipline to stay polished |
| `zeus-celestial` | Zeus Celestial | Vision decks, strategic narratives, Zeus-style AI agency reports | High-contrast cosmic editorial with electric blue and silver | `#65a9ff` | `#080b13` | Use sparingly for polished storytelling, not raw QA |

## Token Contract

Each design must resolve to these tokens:

| Token | Meaning |
| --- | --- |
| `report.background` | Page background |
| `report.panel` | Card and section surface |
| `report.foreground` | Primary text |
| `report.ink` | Legacy alias for primary text |
| `report.muted` | Secondary text |
| `report.line` | Borders and dividers |
| `report.accent` | Primary action and emphasis color |
| `report.accent_2` | Secondary accent for charts, graph edges, or visual contrast |
| `report.radius` | Card and control radius |
| `report.density` | Density in pixels or compact/balanced/spacious alias |
| `report.border_width` | Standard report border width |
| `report.border_style` | `solid`, `dashed`, `dotted`, or `double` |
| `report.font_mode` | System, editorial, mono, or hybrid |
| `button.primary_bg` | Primary button background |
| `button.primary_fg` | Primary button text |
| `button.secondary_bg` | Secondary button background |
| `button.secondary_fg` | Secondary button text |
| `button.radius` | Button radius |
| `button.weight` | Button font weight |
| `button.case` | Button text transform |
| `ornament.mode` | Optional visual motif: none, grid, beam, ledger, radial |
| `shadow.color` | Shadow color source |
| `shadow.strength` | Shadow depth/intensity |

## Merge Note For AI-WorkOS Obsidian Vault

The uploaded AI-WorkOS Obsidian Vault should not replace Agent Memory Kit. It is best treated as an upstream concept library and migration source.

| Vault Concept | Merge Target | Decision |
| --- | --- | --- |
| `00_SYSTEM/MERGE_MAP.md` scoring | `find-parallels` and future merge assessment docs | Merge as a cross-project evaluation rubric |
| `00_SYSTEM/FRONTMATTER_SCHEMA.md` flat Obsidian fields | `agent-memory/schemas/frontmatter.schema.json` | Map concepts, keep stricter Agent Memory fields |
| `00_SYSTEM/GRAPH_SCHEMA.md` node/edge vocabulary | `agent-memory/schemas/graphrag-*.schema.json` | Merge vocabulary as aliases, keep typed frontmatter edges |
| `00_SYSTEM/INGEST_PIPELINE.md` raw to reviewed flow | runtime capture and session compaction docs | Merge as lifecycle documentation |
| `00_SYSTEM/RAG_INDEXING_POLICY.md` tier model | RAG export policy | Merge as index priority tiers |
| Obsidian folder taxonomy | Optional enterprise hub adapter | Keep separate, do not force into project-local core |

Recommendation: keep the vault as a second-system adapter until a migration tool can map its `type/id/canonical/kb_ready/confidentiality` fields into Agent Memory `memory_id/doc_type/status/review_status/sanitization_status/data_class/edges`.
