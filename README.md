# Owledge Kit

**Durable Markdown project memory for AI agents.**

[![Version](https://img.shields.io/badge/version-0.5.0-blue)](VERSION)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Markdown-first](https://img.shields.io/badge/storage-Markdown-black)](#why-owledge-kit)
[![Agent workflows](https://img.shields.io/badge/workflows-Codex%20%7C%20Claude%20%7C%20Cowork%20%7C%20Superpowers-orange)](#use-with-superpowers)

Owledge Kit gives AI agents a project memory they can actually use: plans,
evidence, reviews, handoffs, and decisions are written as local Markdown records
so context survives across sessions, tools, teams, and existing knowledgebases.

Use it alongside Codex, Claude/Cowork, Claude Code, Obsidian, existing LLM wikis,
or Superpowers-style execution when you want agents to keep MVP plans grounded,
handoff work cleanly, and make project progress auditable without adopting a
hosted platform or migrating your vault.

## Why Owledge Kit

- **Keep context durable:** Agents can resume from reviewed Markdown records
  instead of rebuilding project state from chat history.
- **Stay MVP-focused:** Plans track goals, non-goals, evidence, acceptance
  criteria, reviews, and handoffs.
- **Fit existing knowledgebases:** Use the default module folder or map writes
  into an existing Markdown, Obsidian, or LLM-wiki structure.
- **Work with agent stacks:** Use it as a memory layer around Codex, Claude,
  Cowork, Claude Code, generic CLI agents, and Superpowers workflows.
- **Stay local and inspectable:** No hosted database, no forced environment
  variables, and no automatic rewrite of existing notes or wiki links.

This release is a **concept-validated local/project utility kit**. It is not a regulated Enterprise Server, RBAC platform, hosted RAG database, or DSGVO/AI-Act-certified system.

If you already use `obra/superpowers`, treat Owledge Kit as the complementary
memory layer: Superpowers helps agents execute coding work with planning, TDD,
review, and subagents; Owledge keeps project knowledge, evidence, handoffs, and
reviews durable across sessions, agents, teams, and Markdown knowledgebases.

## Start In 5 Minutes

### 1. Clone the kit

Windows:

```powershell
git clone <repo-url> C:\AgentMemoryKit
$kitRoot = "C:\AgentMemoryKit"
```

macOS/Linux:

```bash
git clone <repo-url> ~/AgentMemoryKit
cd ~/AgentMemoryKit
```

### 2. Bootstrap an existing project

Windows:

```powershell
cd C:\path\to\your-project
powershell -NoProfile -ExecutionPolicy Bypass -File "$kitRoot\tools\bootstrap-agent-memory.ps1" -ProjectRoot . -KitRoot $kitRoot
```

macOS/Linux lean path:

```bash
python3 ~/AgentMemoryKit/tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

Then use or copy the generated folder as the project-local kit. It contains its
own CLI, so no global environment variable is required.

### 3. Verify the host project

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-host-install.ps1 -ProjectRoot .
```

macOS/Linux:

```bash
bash tools/verify-host-install.sh --project-root .
```

### Minimal Project Folder Only

For a project-local smoke test without plugins or release assets:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$kitRoot\tools\build-project-folder-kit.ps1" -OutputPath C:\tmp\agent-memory-project-kit -Verify
```

macOS/Linux:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

With Claude/Cowork plugin adapter and Unix hooks:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --include-plugin-adapter --plugin-hook-profile unix --verify
```

Then copy or use that generated folder as the project-local memory kit. It contains only `PROJECT_CONTEXT.md`, runtime instruction files, `agent-memory/`, `global-memory/`, core tools, selected skills, and a short local `README.md`.
Use another disposable output path if `C:\tmp` is not writable.

Optional Compliance Light support is available as an add-on, not part of the
default minimal kit:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$kitRoot\tools\build-project-folder-kit.ps1" -OutputPath C:\tmp\agent-memory-project-kit-compliance -Verify -IncludeCompliance
```

Compliance Light provides local compliance-support templates and read-only
checks. It does not make a project GDPR, AI Act, ISO, or enterprise compliant.

Optional next docs:

- Project-folder-only setup: `docs/project-folder-only-quickstart.md`
- Plugin setup: `docs/install-plugin.md`
- Agent first-run setup: `docs/agent-first-run-setup.md`
- Compliance roadmap: `docs/compliance-roadmap.md`
- Compliance implementation plan: `docs/compliance-implementation-plan.md`
- Optional Compliance Light add-on: `addons/compliance-light/README.md`
- Cross-platform lean setup: `docs/cross-platform-lean-setup.md`
- Agent integration guide for existing Markdown KBs: `docs/agent-integration-guide.md`
- Superpowers comparison and integration: `docs/superpowers-integration.md`
- Harness and plugin matrix: `docs/harness-plugin-matrix.md`
- MVP plan example: `docs/mvp-plan-example.md`
- Team and long-running project guide: `docs/team-long-running-project-guide.md`
- Performance and scale notes: `docs/performance-scale-notes.md`
- Global user knowledge layer: `docs/global-user-knowledge-layer.md`
- Agentic memory architecture: `docs/agentic-memory-architecture.md`
- Reusable review and evaluation templates: `docs/reusable-review-evaluation-templates.md`
- Dashboard extension plan: `docs/dashboard-extension-plan.md`
- LightRAG + Neo4j + Qdrant setup: `docs/lightrag-neo4j-qdrant-setup.md`
- Command reference: `docs/command-reference.md`
- Incremental index workflow: `docs/incremental-index-workflow.md`
- Publish checklist: `docs/publishing.md`

## Architecture

```text
Source of truth   -> Markdown + frontmatter + typed edges
User context      -> USER_CONTEXT.md plus optional global-memory/
Project router    -> PROJECT_CONTEXT.md
Durable memory    -> agent-memory/canonical/, compiled/, patterns/, lessons/
Ideation memory   -> agent-memory/ideas/ captured project and product ideas
PI intelligence   -> agent-memory/pi-agent/ candidate reports, parallels, trends, errors, concepts
PI red team       -> agent-memory/pi-agent/red-team/, evaluations/, scorecards/
Working memory    -> agent-memory/sessions/, evidence/, handoffs/
Machine indexes   -> agent-memory/indexes/ memory-index.jsonl, memory-index-manifest.json, memory-index-tombstones.jsonl
RAG exports       -> agent-memory/exports/rag/, lightrag/, graphrag/
HTML reports      -> agent-memory/reports/html/ generated visual views
Future dashboard  -> optional P4 read-only UI over indexes, exports, PI reports, QA, retrieval
Optional runtime  -> .agent-control/ adapters, never canonical truth
```

The operating principle is:

```text
Markdown is truth
Indexes and exports are generated views
RAG systems are consumers, not canonical storage
```

The kit maps directly to the four practical agentic memory types:

| Memory type | Kit layer |
| --- | --- |
| Working memory | context packs, private session captures, evidence links, handoffs |
| Semantic memory | `PROJECT_CONTEXT.md`, `USER_CONTEXT.md`, `canonical/`, `compiled/`, `patterns/`, `lessons/` |
| Procedural memory | `AGENTS.md`, `CLAUDE.md`, `skills/`, plugin commands, tool wrappers |
| Episodic memory | session records, reviews, QA gates, PI reports, compaction, promotion manifests |

See `docs/agentic-memory-architecture.md` for the production boundaries and remaining SoTA gaps.

Incremental indexing keeps generated indexes fresh without changing the source-of-truth model. `memory-index.jsonl`, `memory-index-manifest.json`, and `memory-index-tombstones.jsonl` are generated operational metadata for QA, RAG freshness, and hub sync; they are not canonical memory.

## What To Copy

```text
PROJECT_CONTEXT.template.md -> PROJECT_CONTEXT.md
USER_CONTEXT.template.md    -> USER_CONTEXT.md (private, ignored by default)
AGENTS.template.md -> AGENTS.md
CLAUDE.template.md -> CLAUDE.md
agent-memory/ -> agent-memory/
global-memory/ -> global-memory/ (private opt-in user layer)
tools/ -> tools/
plugins/agent-memory-cowork/ -> optional Claude/Cowork + Codex plugin adapter
skills/agent-memory-principles/ -> principles-first planning and vault integration skill
skills/render-memory-report/ -> optional visual HTML reporting skill
skills/pi-agent-workspace-quality/ -> optional PI Agent workspace quality skill
skills/pi-agent-global-intelligence/ -> optional PI Agent global knowledge skill
skills/pi-agent-red-team-evaluator/ -> optional PI Agent QA red-team skill
skills/review-evaluation-workflow/ -> optional reusable review, scorecard, simulation, and task-conversion workflow skill
skills/personal-pi-agent/ -> optional private user-memory coach and pattern skill
agent-memory/templates/*review* -> reusable red-team, expert-review, simulation, and review-to-task templates
DESIGN.md                    -> central report design-system selection
REPORT_DESIGN_SELECTOR.html  -> local visual selector for report styles
.gitignore entries -> target .gitignore
```

Also create:

```text
agent-memory/sessions/
agent-memory/decisions/
agent-memory/canonical/
agent-memory/compiled/
agent-memory/patterns/
agent-memory/lessons/
agent-memory/ideas/
agent-memory/pi-agent/reports/
agent-memory/pi-agent/parallels/
agent-memory/pi-agent/trends/
agent-memory/pi-agent/recurring-errors/
agent-memory/pi-agent/concepts/
agent-memory/pi-agent/red-team/
agent-memory/pi-agent/evaluations/
agent-memory/pi-agent/scorecards/
agent-memory/pi-agent/indexes/
agent-memory/evidence/
agent-memory/handoffs/
agent-memory/indexes/
agent-memory/exports/rag/
agent-memory/exports/lightrag/
agent-memory/exports/graphrag/
agent-memory/tmp/
agent-memory/scratch/
global-memory/preferences/
global-memory/goals/
global-memory/daily/
global-memory/tasks/
global-memory/ideas/
global-memory/research/
global-memory/patterns/
global-memory/coach/
global-memory/indexes/
global-memory/exports/rag/
global-memory/exports/lightrag/
global-memory/exports/graphrag/
agent-plans/
```

## Gitignore

Use this in the target project's `.gitignore`:

```gitignore
USER_CONTEXT.md
global-memory/**/*.md
global-memory/indexes/*.jsonl
global-memory/exports/rag/*.json
global-memory/exports/rag/*.jsonl
global-memory/exports/rag/*/
global-memory/exports/lightrag/*.json
global-memory/exports/lightrag/*.jsonl
global-memory/exports/lightrag/*/
global-memory/exports/graphrag/*.json
global-memory/exports/graphrag/*.jsonl
global-memory/exports/graphrag/*/
agent-plans/
agent-memory/tmp/
agent-memory/scratch/
agent-memory/sessions/**/events.jsonl
agent-memory/sessions/**/session.md
agent-memory/sessions/**/summary.md
agent-memory/sessions/**/.session.lock
```

Do not ignore:

```text
PROJECT_CONTEXT.md
AGENTS.md
CLAUDE.md
agent-memory/README.md
agent-memory/templates/
agent-memory/sessions/
agent-memory/decisions/
agent-memory/canonical/
agent-memory/compiled/
agent-memory/patterns/
agent-memory/lessons/
agent-memory/evidence/
agent-memory/handoffs/
agent-memory/indexes/
agent-memory/exports/rag/
agent-memory/exports/lightrag/
agent-memory/exports/graphrag/
```

Runtime capture creates private session artifacts under `agent-memory/sessions/`; keep the directories and templates versioned, but keep raw captured events and generated runtime summaries out of Git unless a reviewer intentionally promotes sanitized knowledge.

## How To Run A Session

### Global Bootstrap

You can bootstrap without writing a system-wide environment variable:

```powershell
$kitRoot="C:\AgentMemoryKit"
powershell -NoProfile -ExecutionPolicy Bypass -File "$kitRoot\tools\bootstrap-agent-memory.ps1" -ProjectRoot . -KitRoot $kitRoot
```

Optional convenience for repeated use:

```powershell
$env:AGENT_MEMORY_KIT_ROOT="C:\AgentMemoryKit"
```

At the beginning of a session, agents should use the `bootstrap-agent-memory` skill. It checks the active repo and, if needed, initializes:

```text
USER_CONTEXT.md
PROJECT_CONTEXT.md
AGENTS.md
CLAUDE.md
DESIGN.md
REPORT_DESIGN_SELECTOR.html
agent-memory/
global-memory/
tools/
```

Manual equivalent:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:AGENT_MEMORY_KIT_ROOT\tools\bootstrap-agent-memory.ps1" -ProjectRoot .
```

### PI Agent Workspace Check

Use the optional PI Agent adapter when you want a workspace-quality pass, planning sparring, or idea overlap check:

```powershell
tools\pi-agent-check.ps1 -ProjectRoot . -Question "What should be checked before this plan?"
```

Capture project ideas during work:

```powershell
tools\capture-idea.ps1 -ProjectRoot . -Title "Idea title" -Summary "Short practical summary"
```

Generate a PI Agent global intelligence report for parallels, trends, recurring errors, and central project candidates:

```powershell
tools\pi-intelligence-report.ps1 -ProjectRoot .
```

PI intelligence reports are candidate artifacts. They should inform planning and curator review, but they do not become canonical truth without explicit promotion.

Challenge the latest PI report with the QA Red Team PI Agent scorecard:

```powershell
tools\pi-redteam-evaluate.ps1 -ProjectRoot .
```

Every Red Team evaluation returns a 1-100 score and one of `block`, `revise`, `accept`, or `promote-candidate`. Even 95+ remains a promotion candidate until a curator or owner approves it.

Use the `review-evaluation-workflow` skill for reusable red-team reviews, expert evaluations, scenario simulations, scorecards, and converting review findings into tasks. It selects a Markdown template from `agent-memory/templates/`, injects explicit personas, collects evidence, scores dimensions from 1-100, classifies the verdict, creates a review artifact, converts unresolved findings to tasks, and defines the QA rerun. Runtime commands or plugins may automate this later, but Markdown remains the source of truth and runtime tools are adapters.

1. Initialize the target project structure:

```powershell
tools\init-agent-memory.ps1 -ProjectRoot .
```

2. Validate Markdown memory contracts:

```powershell
tools\validate-memory.ps1 -ProjectRoot .
```

3. Build the memory index:

```powershell
tools\build-memory-index.ps1 -ProjectRoot .
```

4. Agents read `USER_CONTEXT.md` when present, then relevant `global-memory/` preferences/goals/research, then `PROJECT_CONTEXT.md`, then `agent-memory/indexes/memory-index.jsonl`, then relevant compiled/canonical docs.
5. Workers write sessions, evidence, handoffs, and task notes.
6. Reviewers and QA agents write gate reports.
7. Orchestrators or memory curators promote stable findings into canonical, compiled, patterns, or lessons.
8. Export reviewed/promoted knowledge to RAG, LightRAG, GraphRAG, or RATS.
9. Generate visual HTML reports on request when humans need a more readable decision, handoff, dashboard, RAG readiness, or UI report.

## Scale Rules

- One writer per file.
- Subagents never edit canonical docs.
- Orchestrators summarize.
- Reviewers review.
- Deep delegation summarizes at every layer.
- Wide delegation uses deterministic numbered filenames.
- Raw scratch work goes to ignored folders.
- Every task must have a `tenant_id`, `customer_id`, and `project_id`.
- No worker may mark a task `done` unless required QA gates have passing reports.
- Context packs reference evidence by path and hash instead of copying long logs.
- Every exportable memory file has a stable `memory_id`.
- Relationships use typed `edges` in frontmatter and target `memory_id`, not file paths.
- Shared exports include only `visibility=shared` and `sanitization_status=approved`.
- Shared exports also require `review_status=approved`.
- RAG exports include only reviewed or promoted knowledge by default.

## Core Frontmatter

Every exportable memory file uses this shape:

```yaml
memory_id: "mem:<tenant>:<customer>:<project>:<doc_type>:<slug>"
tenant_id: "tenant-..."
customer_id: "customer-..."
project_id: "project-..."
doc_type: "canonical | compiled | pattern | lesson | adr | session | evidence | qa | task | handoff | idea"
status: "draft | active | reviewed | promoted | superseded | archived"
visibility: "private | tenant | customer | shared"
data_class: "public | internal | confidential | personal | special-category"
semantic_title: ""
summary: ""
concept_tags: []
stack_tags: []
problem_patterns: []
architecture_patterns: []
failure_modes: []
reusable_lessons: []
confidence: 0.0
review_status: "unreviewed | reviewed | approved | rejected"
sanitization_status: "not_required | pending | approved | rejected"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
source_hash: ""
edges:
  - type: "relates_to"
    target: "mem:..."
    reason: ""
    confidence: 0.0
```

Global user-memory records additionally use doc types such as `user_context`, `preference`, `goal`, `daily`, `personal_task`, `research`, `personal_pattern`, `coach_report`, and `onboarding_profile`. Daily notes, personal tasks and onboarding profiles are private deep-dive sources and are not default RAG input.

Supported edge types: `relates_to`, `depends_on`, `supersedes`, `superseded_by`, `derived_from`, `evidence_for`, `implements`, `blocks`, `unblocks`, `validates`, `contradicts`, `similar_to`, `shared_lesson_for`.

## RAG Strategy

- Neutral export: `agent-memory/exports/rag/documents.jsonl`.
- LightRAG export: `texts.json`, `ids.json`, `file_paths.json`, and `manifest.json`.
- GraphRAG export: `nodes.jsonl` and `edges.jsonl`.
- Vector exports prefer `compiled`, `canonical`, `patterns`, and `lessons`.
- Raw sessions and evidence are deep-dive sources, not default shared corpus.
- Cross-project parallels are found by tags, pattern fields, summaries, and explicit edges.
- Existing LightRAG installations can ingest the generated LightRAG export into Neo4j/Qdrant-backed workspaces. See `docs/lightrag-neo4j-qdrant-setup.md`.

Global user-memory export is privacy-first: reviewed `user_context`, `preference`, `goal`, `research`, and `personal_pattern` records can support private retrieval, while daily notes, personal tasks and onboarding profiles are excluded from default RAG.

## Optional Runtime Adapters

SQLite, HTTP APIs, leases, MCP servers, and runtime plugins can be built on top of this core. They must treat Markdown files as canonical and generated indexes/exports as disposable views.

### Drop-In Module For Existing Markdown Knowledgebases

Power users with an existing Markdown knowledgebase, Obsidian vault, or LLM wiki
can add a small local planning module without changing their current structure,
frontmatter, wiki links, or OS environment variables.

Windows:

```powershell
tools\build-kb-module.ps1 -KnowledgebaseRoot C:\path\to\knowledgebase -IncludeCli
```

macOS/Linux:

```bash
python3 tools/build_kb_module.py --knowledgebase-root /path/to/knowledgebase --include-cli
```

The default output is `agent-memory-module/` inside the target KB. It contains
`AGENT_MEMORY_MODULE.md`, planning/handoff/evidence/review folders, and a
generated read-only scan index. Existing notes and `[[Wiki Links]]` are not
rewritten. See `docs/agent-integration-guide.md`.

For power users who already have a mature vault taxonomy, use the
`agent-memory-principles` skill with an optional `agent-memory-map.json` to map
plans, evidence, handoffs, reviews, and indexes to existing folders. Invalid
map paths fail closed. In mapped mode, generated module docs and indexes stay
inside the mapped `indexes` folder rather than adding a new root-level start
file.

### Use With Superpowers

`obra/superpowers` is a software-development methodology and skills framework
for planning, TDD, debugging, review, branch finishing, and subagent-driven
execution. Owledge Kit is the persistent Markdown memory layer around that work.
It can index Superpowers plans under `docs/superpowers/plans/` read-only,
reference them as evidence, and write Owledge handoffs, reviews, and project
continuity records without rewriting Superpowers artifacts. See
`docs/superpowers-integration.md`.

### Claude/Cowork Plugin

The standalone plugin lives at `plugins/agent-memory-cowork/` and includes Claude/Cowork and Codex manifests. Its hooks capture private raw runtime events into `agent-memory/sessions/`, then create draft compiled summaries on session close.

Raw events are not RAG input by default. A memory curator must review and promote stable summaries before they enter canonical memory, LightRAG, GraphRAG, shared lessons, or any shared corpus.

## Visual HTML Reports

HTML reports are generated presentation views only. Markdown remains the source of truth.

Choose the global report style with `REPORT_DESIGN_SELECTOR.html`; persist the chosen id in `DESIGN.md`. The renderer reads `selected_report_design` and applies the matching tokens to every generated report.

```powershell
tools\render-memory-report.ps1 -ProjectRoot . -ReportType project-dashboard
tools\render-memory-report.ps1 -ProjectRoot . -ReportType decision
tools\render-memory-report.ps1 -ProjectRoot . -ReportType rag-readiness
tools\render-memory-report.ps1 -ProjectRoot . -ReportType website-ui
```

Reports include source paths, source hashes, generated timestamps, project metadata, and interactive presentation controls. Website/UI reports can include design-token sliders and an exportable JSON transfer block for a follow-up agent task.

Available report types: `decision`, `handoff`, `rag-readiness`, `agent-activity`, `project-dashboard`, `website-ui`.

Available design ids: `atlas-command`, `glass-ledger`, `signal-grid`, `courtroom-brief`, `mission-control`, `blueprint-studio`, `executive-ledger`, `graph-aurora`, `monolith-minimal`, `workshop-canvas`, `neon-console`, `nordic-clarity`, `evidence-vault`, `product-lab`, `zeus-celestial`.

## Future Dashboard Add-On

A visual dashboard is planned as a P4 add-on, not as part of the current core. It should start as a read-only interface over generated indexes, RAG exports, PI Agent reports, Red Team scorecards, graph edges, and HTML reports.

The dashboard must not replace Obsidian or Markdown. Obsidian remains useful for vault editing and curation; the dashboard is for operations, retrieval, QA, graph inspection, and later reviewed promotion workflows. See `docs/dashboard-extension-plan.md`.

## Minimal Project Boot

After copying the templates:

1. Replace all placeholders.
2. Fill `PROJECT_CONTEXT.md` with vision, current state, stack map, painpoints, active plans, decisions, and next actions.
3. Keep `AGENTS.md` and `CLAUDE.md` identical.
4. Run `tools\validate-memory.ps1`.
5. Run `tools\build-memory-index.ps1`.
6. Promote only reviewed, stable information into canonical, compiled, patterns, or lessons.
