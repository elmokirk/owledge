# Critique-Derived Add-Ons Roadmap

Date: 2026-06-21  
Status: planning  
Scope: optional add-ons and skills derived from senior AI engineer feedback.

## Product Boundary

Owledge core must stay small:

- Markdown remains canonical.
- Existing project and knowledgebase structure stays unchanged by default.
- Indexes, graphs, dashboards, benchmarks, and runtime coordination are generated views or optional adapters.
- Skills provide portable operating rules without requiring users to replace project-specific `AGENTS.md`.

The following features should ship as add-ons or skills, not as default core behavior.

## Critique Review

| Critique | Product reading | Response |
| --- | --- | --- |
| "I already have projects outside my central knowledgebase." | Cross-project memory needs a clear local-to-central promotion path. | Add a Cross-Project Hub add-on that exports reviewed lessons, patterns, decisions, and project summaries from project-local memory into a central KB module. |
| "I use Superpowers, Graphify, LLM Wiki, custom harnesses, and hooks." | Owledge should connect systems through a common memory contract, not replace them. | Add integration skills and adapter docs that map external systems to plans, evidence, handoffs, decisions, and graph exports. |
| "I need a visual decision tree." | The graph is a high-value trust and compliance surface. | Add a Decision Trace add-on that renders goal -> plan -> task -> evidence -> review -> decision -> lesson links. |
| "I want real token and context benchmarks." | Current smoke benchmarks are not enough for enterprise adoption. | Add an Enterprise Context Benchmark add-on with realistic corpora, tokenizer metrics, cost estimates, and growth curves. |
| "I run Codex, Claude Code, and Hermes swarms." | Multi-agent coordination needs explicit ownership, write lanes, and handoffs. | Add a Swarm Coordination add-on and skill that define worker lanes, reviewer lanes, curator promotion, and conflict checks. |
| "This may be overengineered." | Adoption should start with principles-only and prove value before installing add-ons. | Keep every feature optional. Default to the smallest working integration. |

## Add-On Candidates

### 1. Cross-Project Hub Kit

Purpose: connect project-local Owledge installs with a central knowledgebase without making the central KB own project truth.

Install shape:

```text
.owledge/cross-project-hub/
global-memory/
shared/lessons/
shared/patterns/
shared/decisions/
```

Capabilities:

- Import reviewed project summaries from external project folders.
- Keep external project paths as source references.
- Promote only approved and sanitized lessons, patterns, and decisions.
- Generate central context packs for new projects.
- Produce a "source project -> shared lesson -> reused project" trace.

Non-goals:

- No automatic central truth overwrite.
- No raw session import.
- No mandatory shared vault taxonomy.

### 2. Decision Trace Kit

Purpose: visual traceability for project reasoning, review, and compliance support.

Generated views:

- Decision tree: initial goal -> plan -> work packages -> evidence -> review -> ADR -> lesson.
- Idea graph: idea -> related plans -> accepted/rejected/promoted state.
- Compliance trace: AI-assisted change -> evidence -> reviewer -> decision -> retained artifact.

Data source:

- Existing typed frontmatter edges.
- `OWLEDGE.md`.
- Plans, tasks, evidence, reviews, ADRs, lessons, and patterns.

Output:

```text
.owledge/reports/decision-trace/
```

Guardrails:

- Read-only generated HTML/JSON.
- No promotion from the visual view.
- Private and unsanitized records excluded from shared exports by default.

### 3. Enterprise Context Benchmark Kit

Purpose: prove token hygiene and cost behavior with realistic project growth.

Benchmark matrix:

| Scenario | Scale |
| --- | --- |
| Fresh project | 10-50 Markdown artifacts |
| Growing project | 500-2,000 artifacts |
| Long-running project | 10,000+ artifacts |
| Enterprise simulation | 2 years of ADRs, plans, issues, reviews, handoffs, research, and generated outputs |

Comparisons:

1. Full vault prompt.
2. Naive search plus manual paste.
3. Metadata-only scan.
4. Owledge scoped context pack.
5. Oracle hand-picked source set.

Metrics:

- Prompt tokens.
- Useful included source ratio.
- Irrelevant context ratio.
- Dropped source count and reasons.
- Wall-clock runtime.
- Estimated model cost per planning run.
- Context growth curve by project age.
- Retrieval precision against fixture questions.

Output:

```text
.owledge/reports/enterprise-context-benchmark/
benchmarks/results/context-growth.json
benchmarks/results/token-efficiency.md
```

Acceptance bar before public claims:

- Claims must cite tokenizer-based measurements.
- Benchmarks must include commit SHA, OS, Python version, corpus generation method, and command.
- Cost claims must be presented as scenario estimates, not universal savings.

### 4. Swarm Coordination Kit

Purpose: coordinate multi-runtime and multi-layer agent work without turning Owledge into an execution framework.

Capabilities:

- Orchestrator plan with MVP cutline and non-goals.
- Worker lanes for Codex, Claude Code, Hermes, or generic agents.
- Per-agent handoff packets.
- Evidence append lanes.
- Reviewer lane for quality findings.
- Curator lane for promotion proposals.
- Conflict review before promotion.

Write lanes:

| Role | Allowed writes |
| --- | --- |
| Orchestrator | plans, work packages, context packs |
| Worker | evidence, handoffs, task-local notes |
| Reviewer | reviews, QA gates, risk reports |
| Curator | promotion proposals, canonical drafts, lessons, patterns |

Non-goals:

- No distributed locking in core.
- No autonomous conflict resolution.
- No runtime-specific execution replacement.

Later extension:

- Optional lease files and ownership journal as an adapter, not core.

### 5. Integration Adapter Notes

Purpose: make Owledge useful beside existing power-user systems.

Recommended docs or skills:

- Superpowers adapter: cite Superpowers plans as source evidence; keep execution there.
- Graphify adapter: render typed Owledge edges as visual graph inputs.
- LLM Wiki adapter: scan metadata-first and preserve wiki links.
- Custom harness adapter: map hooks to session events, evidence, and handoffs.
- Runtime bridge profiles: Codex, Claude Code, Hermes, Cowork-compatible, OpenCode-style agents.

## Skill Candidate: `owledge-planning-layer`

Problem: many users already have project-specific `AGENTS.md` files. Owledge should not replace those instructions.

Goal: provide a portable planning layer that an agent can invoke on top of any existing project rules.

Behavior:

1. Read and obey the host project's existing instructions first.
2. Detect whether Owledge is installed, mapped, or should run principles-only.
3. Build an MVP-first plan with explicit goal, non-goals, cutline, source evidence, and task lanes.
4. Load only scoped context by default.
5. Write only to approved memory locations.
6. Produce a handoff-ready plan that can be used by Codex, Claude Code, Hermes, or generic agents.

Non-goal:

- Do not install Owledge automatically.
- Do not overwrite host `AGENTS.md`.
- Do not force folder structure.

## Proposed Implementation Order

1. Add `owledge-planning-layer` skill.
2. Add Decision Trace Kit specification and generated-view prototype.
3. Add Enterprise Context Benchmark Kit with tokenizer metrics.
4. Add Cross-Project Hub Kit import/export workflow.
5. Add Swarm Coordination Kit write lanes and handoff templates.
6. Add adapter notes for Superpowers, Graphify, LLM Wiki, and custom harnesses.

## Readiness Criteria

Before marking any add-on stable:

- It must be optional and additive.
- It must not alter existing user files unless explicitly requested.
- It must document exact write paths.
- It must exclude raw/private records from shared exports.
- It must have a small demo and one scale test.
- It must pass `python tools/owledge.py doctor --project-root .`.

