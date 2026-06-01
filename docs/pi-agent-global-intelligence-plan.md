---
title: "PI Agent Global Intelligence Plan"
date: "2026-05-15"
version: "0.1.0"
status: "draft"
type: "implementation-plan"
---

# PI Agent Global Intelligence Plan

## Evaluation

The idea is high-value and fits the current Markdown-first architecture. The PI Agent should become the quality and portfolio intelligence assistant for the Agent Memory vault: it observes the memory graph, detects repeated patterns, and proposes improvements without becoming the source of truth.

| Dimension | Assessment | Decision |
| --- | --- | --- |
| Strategic fit | Strong; turns stored memory into reusable operational intelligence | Implement as optional adapter |
| Scalability | Good if reports are generated from indexes/frontmatter first | Use deterministic signals before semantic search |
| Quality risk | Medium; automated findings can be mistaken for truth | Keep all PI outputs as candidate artifacts |
| RAG readiness | Strong; outputs can later become reviewed patterns or lessons | Do not export unreviewed reports by default |
| Human usability | Strong; reports explain why signals matter | Add clear source links and next actions |

## Target Capability

The PI Agent should:

- find project and cross-project parallels
- detect repeated concepts, architecture patterns, problem patterns, and failure modes
- identify repeated agent errors and propose fixes
- derive central project candidates from goals, ideas, lessons, and patterns
- produce compact report artifacts in a dedicated workspace
- hand off promotion candidates to the memory curator

## Artifact Workspace

| Path | Artifact Type | Promotion Rule |
| --- | --- | --- |
| `agent-memory/pi-agent/reports/` | Full intelligence reports | Never auto-promote |
| `agent-memory/pi-agent/parallels/` | Parallel candidates | Promote to `patterns/` after review |
| `agent-memory/pi-agent/trends/` | Trend summaries | Promote to `compiled/` or planning docs after review |
| `agent-memory/pi-agent/recurring-errors/` | Repeated failure modes | Promote to QA gates, skills, or lessons after review |
| `agent-memory/pi-agent/concepts/` | Central project candidates | Promote to `ideas/` or planning specs after review |
| `agent-memory/pi-agent/indexes/` | Helper indexes | Generated only |

## Implementation Phases

| Phase | Scope | Definition of Done |
| --- | --- | --- |
| 1 | Add workspace, templates, skill, plugin command, and report script | PI report can be generated from Markdown memory |
| 2 | Add QA Red Team PI evaluation | PI reports receive 1-100 scores before promotion decisions |
| 3 | Add richer deterministic scoring | Signals rank by source count, reviewed status, recency, and edge quality |
| 4 | Add curated promotion workflow | PI candidates can become pattern, lesson, QA gate, or idea drafts |
| 5 | Add enterprise hub mode | Reports aggregate across `tenants/*/customers/*/projects/*` |
| 6 | Add optional RAG/GraphRAG assist | Semantic candidates supplement deterministic findings |

## Guardrails

- PI Agent findings are candidate knowledge.
- QA Red Team PI Agent scores are quality gates, not automatic approvals.
- Canonical memory remains curator-controlled.
- Raw chat logs are not a primary source.
- Private tenant data must not enter shared reports.
- Contradictions should be reported, not flattened.
- Every recommendation should cite source artifacts.

## Runtime Commands

```powershell
tools\pi-agent-check.ps1 -ProjectRoot . -Question "What should be checked before this plan?"
tools\pi-intelligence-report.ps1 -ProjectRoot .
tools\pi-redteam-evaluate.ps1 -ProjectRoot .
```

## Next Improvements

| Improvement | Reason |
| --- | --- |
| Add report-to-pattern conversion | Speeds up review while keeping approvals explicit |
| Add enterprise hub scanning | Enables global agency-level intelligence |
| Add recurring-error playbook generation | Turns repeated mistakes into operational improvements |
| Add graph export for PI signals | Makes centrality and project overlap visible |
| Add privacy classifier | Prevents accidental shared reporting of sensitive signals |
