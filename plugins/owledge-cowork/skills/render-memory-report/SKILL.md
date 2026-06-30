---
name: render-memory-report
description: Create visual HTML reports from Owledge Markdown when the user asks for a visual report, HTML report, decision visualization, handoff visualization, PM/dev report, RAG readiness report, agent activity report, website/UI decision report, design-token decision view, stakeholder summary, or a more readable alternative to Markdown.
---

# Render Memory Report

Use this skill only for generated visual reporting. Markdown remains the source of truth.

## Core Workflow

1. Identify the requested report type.
2. Read only the matching reference file below.
3. Load source Markdown/JSONL files from the project memory.
4. Read `DESIGN.md` when a report style, design system, or visual treatment is relevant.
5. Generate HTML that links all source files and displays source hashes.
6. Add interactive controls only as local presentation state unless the user asks to persist decisions.
7. Never treat HTML as canonical memory.

## Report Routing

| User asks for | Read |
| --- | --- |
| decision, ADR, tradeoff, architecture explanation | `references/decision-report.md` |
| handoff, PM to dev, dev to QA, agent transition | `references/handoff-report.md` |
| RAG, LightRAG, GraphRAG, corpus, ingestion readiness | `references/rag-readiness-report.md` |
| what agents did, session summary, multi-agent work | `references/agent-activity-report.md` |
| stakeholder overview, project status, executive summary | `references/project-dashboard.md` |
| website, UI, design system, branding, visual decisions, design tokens | `references/website-ui-report.md` |
| report style, visual theme, HTML template design, design selector | `references/report-design-systems.md` |
| optional project cockpit, pitch site, workflows, implementation pages | `references/project-site.md` from Project Snapshot Kit |
| optional MVP, roadmap, local tickets, blockers, QA dashboard | `references/execution-dashboard.md` from Project Snapshot Kit |

The `project-site` and `execution-dashboard` report types are available only
when the optional `project-snapshot-kit` add-on is installed in the project.

## Required Output Rules

- Put source links and hashes at the top or in a clearly visible appendix.
- Include generated timestamp, project id, report type, visibility, and data class.
- Keep private data out of customer/shared reports.
- Use semantic HTML, responsive CSS, accessible contrast, no external CDN dependencies.
- Apply the selected design id from `DESIGN.md` when present.
- Include controls for density, font size, contrast, and section toggles when useful.
- For design-token decisions, include sliders/switches and an exportable JSON decision block.

## Done Criteria

The user can open the HTML report, understand the decision or handoff without reading raw Markdown, trace every claim back to source files, and copy any explicit visual settings back into a follow-up agent task.
