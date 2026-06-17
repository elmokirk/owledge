# Agentic Memory Architecture

This project implements the four practical memory types used by agentic systems while keeping Markdown as the canonical store.

The goal is not to turn a vector database, dashboard, or runtime plugin into the source of truth. Those systems are generated views and adapters. Durable memory remains reviewable, portable, diffable Markdown with typed frontmatter and evidence links.

## Memory Type Map

| Memory type | What it means for agents | Current implementation | Production boundary |
| --- | --- | --- | --- |
| Working memory | The scoped context an agent sees while doing one task | Runtime context window, generated context packs, private session logs, evidence links, handoffs | Keep compact, task-scoped, and disposable. Do not promote raw transcripts directly. |
| Semantic memory | Stable facts, policies, decisions, project knowledge, and retrieval summaries | `PROJECT_CONTEXT.md`, `USER_CONTEXT.md`, `agent-memory/canonical/`, `agent-memory/compiled/`, `patterns/`, `lessons/`, typed edges, generated indexes | Promote only reviewed stable knowledge. Markdown is canonical; RAG is a consumer. |
| Procedural memory | How agents should do work | `AGENTS.md`, `CLAUDE.md`, `skills/*/SKILL.md`, plugin commands, Python CLI, templates, command reference | Use progressive disclosure: skill index first, full skill only when relevant. Runtime tools adapt to the contract. |
| Episodic memory | What happened, what was decided, what worked, what failed, and what should be learned | `agent-memory/sessions/`, `evidence/`, `handoffs/`, review artifacts, PI reports, red-team scorecards, `compact-sessions`, promotion manifests | Raw episodes stay private. Stable deltas are distilled into compiled/canonical/pattern/lesson records after review. |

## Current Handling

### Working Memory

Working memory is represented by context packs and private session artifacts.

- `python tools/owledge.py build-context-pack` creates a scoped pack from project and memory records.
- Context packs use a character budget and list dropped sources so agents can see what was excluded.
- Runtime plugin hooks can write private events under `agent-memory/sessions/`.
- Handoffs and evidence records keep task state outside the model context window.

This is release-ready for local/project use when agents treat generated context as disposable and rebuild it from Markdown.

### Semantic Memory

Semantic memory is the strongest part of the kit.

- `PROJECT_CONTEXT.md` routes project-level truth.
- `USER_CONTEXT.md` and `global-memory/` hold optional private user context.
- `canonical/` stores approved stable project knowledge.
- `compiled/` stores retrieval-optimized summaries.
- `patterns/` and `lessons/` carry reusable knowledge.
- Frontmatter gives every exportable record stable IDs, scope, review status, sanitization status, confidence, tags, and typed edges.
- RAG, LightRAG, and GraphRAG exports are generated from reviewed/promoted memory.

The core rule is already correct for production: Markdown is truth; indexes and exports are rebuildable views.

### Procedural Memory

Procedural memory is implemented through runtime-neutral instructions and progressive-disclosure skills.

- `AGENTS.md` and `CLAUDE.md` define global operating rules for coding agents.
- `skills/*/SKILL.md` files describe reusable procedures such as bootstrap, runtime bridge, report rendering, PI intelligence, and review workflows.
- `plugins/agent-memory-cowork/` packages commands, hooks, and skills for Claude/Cowork and Codex-compatible use.
- `tools/owledge.py` and `tools/agent_memory_cli.py` expose repeatable procedures for validation, indexing, promotion, reports, exports, and evals.

This is a local adapter model. The important boundary is that skills and plugins do not own memory; they operate on the Markdown contract.

### Episodic Memory

Episodic memory now has deterministic project-kit gates, while destructive
retention enforcement remains out of scope for this local release.

- Runtime hooks can capture session events.
- `compact-sessions` converts session records into private draft compiled summaries.
- QA/review workflows produce scored review artifacts.
- Promotion requires review approval, source hash checks, tenant/customer/project scope, and target policy checks.
- Promotion writes audit manifests under `agent-memory/evidence/promotions/`.
- `audit-retention`, `review-memory-conflicts`, and `scan-memory-sensitive-data` are read-only gates for stale, contradictory, expired, and sensitive memory.

The implementation correctly avoids raw transcript promotion. For publish, call
this a project-ready episodic workflow with audit previews, not an autonomous
long-term learning system with destructive deletion.

## Missing Or Underdeveloped Aspects

| Gap | Why it matters | v0.5.0 publish stance | Implementation path |
| --- | --- | --- | --- |
| Explicit memory-type documentation | Users need to understand why folders, skills, and exports exist | Implemented | Keep this as the conceptual map for publish and onboarding |
| Context pack relevance scoring | Working memory quality depends on selecting the right subset, not just fitting a budget | Implemented for project-kit scope | Keep calibrating weights against real project outcomes |
| Retention and forgetting | Episodic memory can become stale, private, or misleading | Implemented as read-only audit and preview | Add explicit purge/anonymize workflow only after separate approval design |
| Contradiction handling | Agents must not silently overwrite old truth | Implemented via conflict-review report | Add curator workflow for resolving P1 conflicts into supersession records |
| Runtime adapter parity | Claude/Cowork capture exists; Codex and other runtimes are more skill/CLI-based | Smoke-tested for project-kit release | Add per-runtime permission/lifecycle docs |
| Retrieval quality calibration | Evals exist but need real benchmark corpora | Implemented with protected fixture corpus and thresholds | Add larger customer-like benchmark corpora after publish |
| Promotion queue UX | Promotion is hardened but CLI-centric | Acceptable for technical users | Later read-only dashboard plus reviewed promotion queue |
| Compliance depth | Data classification exists, but regulated production needs more | Do not market as regulated enterprise compliance | Implement processing inventory, provider registry, DSAR/export/delete flows, and encrypted vault options |

## Recommended Release Scope

Ship v0.5.0 as:

- Markdown-first Owledge memory for coding and multi-agent projects.
- Local/project memory architecture with optional private global user layer.
- Project-ready support for all four memory types.
- Safe by default for raw sessions, private user context, and shared exports.
- RAG/LightRAG/GraphRAG export-ready after review and sanitization.
- Minimal project-folder-only quick setup for local evaluation.

Do not ship it as:

- A regulated enterprise compliance platform.
- A fully autonomous memory curator.
- A hosted memory server with RBAC, audit UI, and retention enforcement.
- A guaranteed SoTA retrieval engine without project-specific eval calibration.

## Publish Gate

Before publishing, run:

```bash
python tools/owledge.py finalization-gates --project-root .
python tools/owledge.py redteam-qa --project-root .
```

For shared export/report validation, add `--include-exports` to the finalization
gate. The individual commands are listed in `docs/command-reference.md`.

## Implementation Sequence After Publish

1. Calibrate retrieval fixtures against real project outcomes.
2. Add curator workflows for conflict resolution and supersession promotion.
3. Add per-runtime permission and lifecycle docs.
4. Add a read-only dashboard over generated indexes, reports, evals, and promotion candidates.
5. Add optional backend leases and promotion queue without replacing Markdown as canonical truth.
