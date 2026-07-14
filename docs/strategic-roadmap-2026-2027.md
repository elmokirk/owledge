---
title: "Owledge Strategic Roadmap 2026–2027"
date: "2026-07-10"
status: "decision-ready"
type: "product-strategy-and-execution-roadmap"
owner: "Kirk"
review_status: "multi-perspective-review-complete"
summary: "A status-normalized, evidence-linked roadmap that positions Owledge as a local-first, Git-native agentic project control plane and sequences the product, demo, interoperability, Git safety, documentation and ecosystem work."
---

# Owledge Strategic Roadmap 2026–2027

## Decision Summary

Owledge should not compete as another agent runtime, generic task manager, vector database, or prompt-based planning method. Its defensible category is:

> **A local-first, Git-native agentic project control plane that turns human intent into portable work contracts, evidence, decisions, and living project documentation across harnesses.**

The durable product loop is:

```text
Intent → Decision → Plan → Work contract → Run → Evidence → Gate
       → Review → Canonical knowledge → Living documentation → next intent
```

Markdown and typed frontmatter remain canonical. Indexes, databases, MCP servers, dashboards, graphs, and runtime hooks are replaceable adapters or generated views. Owledge must remain useful without a hosted service or model provider.

The first strategic move is a **truth reset**: reconcile roadmap, version, ticket, and implementation state before building further surface area. The existing product already contains a substantial CLI, promotion and privacy model, reports, evaluations, add-ons, upgrade/drift tooling, and several runtime bridges. The current planning documents do not represent that state consistently.

## Scope, Evidence, and Review Verdict

This roadmap synthesizes the current product sources, open feedback tickets, active and archived plans, CLI surface, README/demo, internal red-team material, and an independent competitor review. It treats generated dogfood material as evidence, not as the shipped product source.

Key repo evidence:

- `VERSION`, `pyproject.toml`, public README, GitHub `main`, and PyPI now align on `owledge==0.7.0`; older v0.6.x docs are historical evidence, not current release truth.
- `ROADMAP.md` still contains some legacy near-term rows beside the v0.7 release board and newer OKF work; the next reset should consolidate these into one live work register.
- `docs/v0.6.1-fix-up-plan.md` and `docs/v0.6.0-implementation-plan.md` remain useful historical context, but their unchecked items must not be treated as live backlog without explicit re-triage.
- The current code confirms that ticket board, `quick_read`, scan allowlist, parallel notice, and OKF CLI commands are not yet present.
- The current public demo proves artifact creation, but it installs prepared artifacts rather than demonstrating a live work-contract, interruption, gate failure, resume, and documentation update.

Multi-perspective strategic readiness score: **64/100 — REVISE**. The category thesis is a promote-candidate; broad expansion should wait for the P0 product contract, status reset, Git/multi-agent safety contract, and a credible golden demo.

## Product Boundary and North Star

### What Owledge owns

| Plane | Owledge responsibility | Canonical result |
| --- | --- | --- |
| Intent and policy | Goals, assumptions, scope, decisions, risks, acceptance rules | Project context, plans, decision records |
| Coordination | Work contracts, dependencies, claims, checkpoints, handoffs, gate definitions | Work packages and gate manifests |
| Evidence and knowledge | Runs, sources, test evidence, review, promotion, contradiction and supersession | Evidence ledger and reviewed Markdown knowledge |
| Documentation | Derive and verify project-facing documentation from reviewed truth | Source-linked docs and reports |

### What Owledge integrates but does not replace

- Agent execution, scheduling, model routing, sandbox provisioning, and remote-agent transport.
- Git hosting, CI, issue trackers, document systems, vector/graph databases, and dashboards.
- Any model's factual correctness or the security properties of a third-party sandbox.

### North-star metric

**Evidence-complete, cross-harness resumable feature increments:** the percentage of completed feature increments for which a new person or harness can reconstruct the original intent, decisions, work status, test evidence, documentation impact, and next valid action without chat history.

Initial product target: **90% of golden-path increments are evidence-complete and resumable across two Tier-1 harnesses.**

## Status Normalization: Existing Work to Preserve, Complete, or Retire

The following is the authoritative triage target for the next planning reset. “Partially covered” means a related capability exists but the stated acceptance criteria are not met.

| Existing item | Current reading | Proposed disposition | Roadmap home |
| --- | --- | --- | --- |
| FB-001 PyPI publishing | `owledge==0.7.0` is published on PyPI and works through `uvx` | Mark shipped and retain release/publish-readiness regression checks | Baseline |
| FB-002 copy-paste integration | Shipped as docs-only | Mark shipped and retain regression check | Baseline |
| FB-003 tokenizer benchmark | Related enterprise benchmark exists; exact public four-scenario baseline is not proven | Consolidate into one reproducible context/evidence benchmark | Phase 1 |
| FB-004 global scan allowlist and consent | No `scan_allowlist` implementation found | Keep; broaden to privacy-policy contract | Phase 3 |
| FB-005 + FB-017 project abstract/modes | Concept-audit reads modes, but shipped project template/plan contract is incomplete | Re-scope as Project Manifest v1 | Phase 1 |
| FB-006 parallel notification | `find-parallels` exists; notice artifact does not | Fold into context compiler and cross-project signal contract | Phase 3 |
| FB-007 PI setup guide | Docs-only delivered | Mark shipped; revisit only with a governed PI loop | Phase 5 |
| FB-008 completion contract | Task fields exist, but no portable end-to-end contract | Fold into Work Contract v1 | Phase 1 |
| FB-009 permission modes | Concept-audit recognizes values; planning behavior is incomplete | Fold into policy and promotion model | Phase 1 |
| FB-010 success metrics | Template-level feature remains open | Fold into outcome/evaluation card | Phase 1 |
| FB-011 idea-to-project | No governed promotion pipeline | Keep as optional portfolio workflow, not core | Phase 5 |
| FB-012 feedback rounds | No public reusable template found | Deliver with roadmap governance | Phase 0 |
| FB-013 ticket board | No CLI implementation found | Replace with Work Graph / status view, after contract schema | Phase 1 |
| FB-014 hook validation | Capture hooks exist; validation-on-stop acceptance is not proven | Fold into adapter conformance | Phase 2 |
| FB-015 supervised summary | No implementation found | Deliver as planner UX after work records exist | Phase 1 |
| FB-016 `quick_read` | No schema/CLI implementation found | Recast as generated context synopsis with freshness contract | Phase 1 |
| FB-018 continuity checklists | Shipped convention; plans have drifted | Preserve and repair stale plans | Phase 0 |
| FB-019 deferred polish | Open P2/P3 correctness batch | Complete or explicitly retract | Phase 0 |
| FB-020 `concept-audit --since` | Parser flag remains but dispatch is not wired | Fix or remove; never expose dead flags | Phase 0 |
| FB-021 release upgrade-notes schema | Open release-trust hardening | Complete before schema-heavy releases | Phase 0 |
| LightRAG, reports, snapshots, hub, swarm add-ons | Related add-ons/CLI are already present | Mark shipped experimental/add-on, define support tier rather than rebuild | Baseline / Phase 2 |
| OKF roadmap | Preserved as `docs/okf-integration-plan.md` | Treat as a standards-bound interchange profile, not as generated output | Phase 3 |

### Required status-reset deliverable

Create one machine-readable work register from the above table with: `id`, `title`, `state`, `source`, `implementation_evidence`, `acceptance_gap`, `target_phase`, `owner`, and `supersedes`. Historical plans remain evidence; the register becomes the live backlog source. No feature may be shown as “shipped” without a linked gate or release proof.

## Gap and Blindspot Analysis

| Severity | Gap / blindspot | Why it matters | Resolution principle |
| --- | --- | --- | --- |
| P0 | Historical naming ambiguity | Weak discovery, demo clarity, and expectation setting | Keep Owledge as the public name and maintain one-sentence category discipline |
| P0 | Roadmap state is not implementation state | Agents will build duplicates or sequence work from stale assumptions | Live work register plus CI status checks and archival policy |
| P0 | No versioned cross-harness work/run contract | Harness files and chat state become accidental truth | Canonical schemas with migrations and capability negotiation |
| P0 | Parallel agent safety is convention-only | Conflicting writes, duplicate work, and invalid completion are likely | Claims, file scopes, worktrees, evidence gates, deterministic integration manifest |
| P0 | Demo proves prepared artifacts rather than delivery | A prospect cannot see the product’s differentiated loop | Offline golden demo: plan, dispatch, fail, resume, review, compile docs, switch harness |
| P1 | Promotion/provenance is rich but not surfaced as a product loop | Users do not understand why Owledge is safer than generic memory | Candidate → reviewed → canonical → superseded lifecycle in CLI, reports, and demo |
| P1 | Context packs lack an explainable compiler contract | Token control and retrieval trust cannot be verified | Deterministic pack types, budgets, source reasons, exclusion reasons, digest |
| P1 | Adapter claims can drift faster than the core | Harness support becomes a fragile marketing list | Capability manifest, golden fixtures, conformance suite, clear Tier labels |
| P1 | Documentation is a report feature, not yet a verified compiler | “Living documentation” risks creating stale generated prose | Source hashes, impact analysis, draft/review/publish lifecycle |
| P1 | Privacy boundary is not an end-to-end ingestion policy | Global memory and remote adapters can leak private data | Deny-by-default scope, consent, redaction, provenance and negative fixtures |
| P2 | No authority-resolution rule between code, issue, ADR, and memory | Contradictions silently degrade trust | Explicit authority/supersession policy and conflict review |
| P2 | Resume is checkbox-led rather than side-effect-aware | Interrupted work can repeat writes or tests | Checkpoint hashes, idempotency keys, reconciliation before resume |
| P2 | Evaluation measures components more than delivery outcomes | Benchmarks can optimize the wrong thing | Measure resume, portability, stale-doc detection, false-pass rate, rework |
| P2 | Dashboard may become a second source of truth | Visual convenience can break Git-native trust | Views must be rebuildable and link every claim to artifacts |
| P3 | Plugin/skill supply chain is not a first-class contract | Third-party skills can introduce unsafe behavior or hidden permissions | Signed/versioned manifests, permission declarations, update diffs |
| P3 | Enterprise scope can precede a strong local wedge | Compliance/server work could dilute adoption | Local-first golden path before team server or regulated claims |

## Competitive Positioning

The market is crowded in individual layers: Spec Kit and OpenSpec own specification-to-implementation workflows; Beads and Gas Town emphasize operational multi-agent coordination; LangGraph, CrewAI, Mastra, and the OpenAI Agents SDK run agents; Mem0, Graphiti, Letta, and agentmemory handle long-lived memory. Owledge should interoperate with these systems rather than imitate their runtimes.

| Category | Representative projects | Owledge response |
| --- | --- | --- |
| Spec / planning | [GitHub Spec Kit](https://github.com/github/spec-kit), [OpenSpec](https://github.com/Fission-AI/OpenSpec), [BMAD](https://github.com/bmad-code-org/BMAD-METHOD) | Import/export specifications; differentiate with evidence, cross-harness continuity, Git safety, and documentation provenance |
| Work tracking / coordination | [Beads](https://github.com/gastownhall/beads), [Gas Town](https://github.com/gastownhall/gastown), [Task Master](https://github.com/eyaltoledano/claude-task-master) | Offer a portable work contract and optional bridges; do not become another task database |
| Agent runtimes | [LangGraph](https://github.com/langchain-ai/langgraph), [CrewAI](https://github.com/crewAIInc/crewAI), [Mastra](https://github.com/mastra-ai/mastra), [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | Be the repository-local intent/evidence layer beneath or beside execution |
| Memory systems | [agentmemory](https://github.com/rohitg00/agentmemory), [Mem0](https://github.com/mem0ai/mem0), [Graphiti](https://github.com/getzep/graphiti), [Letta](https://github.com/letta-ai/letta) | Compete on trustworthy project knowledge: lifecycle, provenance, promotion, portability, documentation impact |

### Build, integrate, and explicitly avoid

| Build as core | Integrate through versioned adapters | Do not build |
| --- | --- | --- |
| Artifact/work/run/gate contracts; provenance ledger; context and documentation compiler; drift/impact; Git coordination contract; conformance/evals | MCP, Agent Skills, A2A, ACP, OpenTelemetry, GitHub/GitLab/Jira, Spec Kit/OpenSpec, Beads, Graphiti, memory providers, agent runtimes | LLM abstraction layer, generic scheduler, vector/graph DB, IDE, hosted issue tracker, proprietary agent protocol |

Standards are adapter boundaries, not the canonical store: [MCP](https://modelcontextprotocol.io/docs/getting-started/intro), [Agent Skills](https://agentskills.io/specification), [A2A](https://github.com/a2aproject/A2A), [ACP](https://agentclientprotocol.com/get-started/introduction), and [OpenTelemetry GenAI conventions](https://github.com/open-telemetry/semantic-conventions-genai) should be version-pinned and capability-gated.

## Non-Negotiable Feature Baseline

Before Owledge claims to be a user-friendly, harness-neutral ecosystem, it must cover the following end-to-end. A feature is complete only when it works in the golden demo, has a stable contract, has negative tests, and has a support tier.

1. **Project Manifest:** project identity, schema version, canonical roots, privacy policy, adapter support, and gate profile.
2. **Artifact Envelope:** stable ID, status, visibility, data class, title, summary, source references/hashes, validity, revision, and typed edges (`supports`, `implements`, `depends_on`, `supersedes`, `contradicts`, `derived_from`, `validated_by`).
3. **Work Contract:** objective, inputs, outputs, dependencies, owner role, path claims, permissions, budget, acceptance criteria, required evidence, gates, handoff, and completion state.
4. **Run and Evidence Ledger:** run parentage, harness/agent, worktree/branch, input digest, permission snapshot, outputs, commit references, test outputs, cost/timing, and termination reason.
5. **Validated state machines:** draft → ready → claimed → running → review → blocked/failed → accepted → promoted, with idempotent transitions.
6. **Context compiler:** task, review, handoff, release, onboarding, and incident packs; token budget; privacy filter; source selection/exclusion explanation; deterministic digest.
7. **Promotion and contradiction workflow:** no automatic canonical promotion; explicit review and supersession; private data cannot enter shared contexts.
8. **Git-safe concurrency:** claim/lease, allowed paths, one branch/worktree per independent work unit, overlap detection, independent review, integration order, and abort/recovery rules.
9. **Adapter capability contract:** detect, install, inject, capture, execute, resume, health, cleanup; degradation is explicit rather than silent.
10. **Documentation compiler:** source-linked ADRs, architecture, runbooks, release notes, onboarding, and capability catalog; source-hash drift/impact alerts.
11. **Operable CLI:** `init`, `doctor`, `plan`, `context`, `why`, `status`, `resume`, `validate`, `promote`, `export`, and `uninstall`, all with `--dry-run`, JSON output, and useful failure messages.
12. **Evaluation, security, and demo:** deterministic fixture demo, portability/recovery tests, evidence quality tests, secret/PII negative tests, and a public support matrix.

## Canonical Contract Direction

The present Markdown model is retained; these are schema contracts, not a mandate for a database.

| Contract | Minimum responsibility |
| --- | --- |
| `ProjectManifest` | project/schema identity, canonical paths, privacy policy, adapter capabilities, gate profile |
| `WorkContract` | task objective, dependencies, scopes/claims, permissions, outputs, QA and handoff |
| `RunManifest` | run/harness/worktree/input digest/permissions/output/commit/cost/termination evidence |
| `ArtifactEnvelope` | portable Markdown frontmatter with stable identity, lifecycle, provenance and typed edges |
| `ContextPack` | ordered artifact refs, source reasons, exclusions, budget, digest and compiler version |
| `GateResult` | gate/version, input digest, result, evidence refs, reviewer and residual risks |
| `Checkpoint` | completed state, claims, output hashes, dependencies, idempotency/reconciliation data |
| `AdapterManifest` | stated capabilities, versions, setup requirements, limits and degrade behavior |

## Delivery Roadmap

Time labels are relative sequencing, not calendar commitments. Each phase is an independently shippable increment. The next agent must start at the first unchecked item; a checked box is valid only when its linked QA evidence passes.

## Phase 0 — Truth Reset, Product Contract, and Proof of Value (post-v0.7.0)

**Outcome:** one truthful backlog, a crisp category, a support policy, and a prospect-ready demo using what exists today plus clearly scoped missing work.

**Feature group:** roadmap governance, naming/positioning RFC, release hygiene, demo v2, public onboarding, status view.

**Deliverables:**

- Product Contract RFC: public name, category, one-sentence promise, ICP hypothesis, three non-goals, canonical-source rule, and support tiers.
- Live work register that supersedes scattered “open” tables without deleting historical plans.
- Reconcile v0.6.x historical plans and stale continuity boxes against the live v0.7.0 release; record explicit dispositions for FB-001 through FB-021.
- Complete or retract FB-019/FB-020/FB-021, including a test for every retained flag/claim.
- Keep PyPI/`uvx` release proof linked from release gates; any future publish issue must be tracked as release operations, not as an open product feature.
- Golden demo v1: a static, offline, fixture-backed 8-minute flow that starts from a real feature request and visibly produces plan, evidence, gate, handoff, and source-linked report.
- README first-screen rewrite and one-page ICP-specific landing path for solo power users and agent-native OSS teams.

**Acceptance / QA gates:**

- No active plan contradicts `VERSION`, `pyproject.toml`, or the live work register.
- Every open item has an owner, state, source, acceptance gap, and phase.
- `python tools/owledge.py --project-root . doctor --mode kit`
- `python tools/owledge.py --project-root . validate-memory --strict`
- `python tools/owledge.py test public-docs --project-root .`
- `python tools/owledge.py test quality-ratchet --project-root .`
- Fresh-user demo dry run succeeds on Windows, macOS, and Linux without an API key.

### Checklist

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done

## Phase 1 — Portable Planning and Work Contracts (v0.8 candidate)

**Outcome:** a user can turn an intent into a validated, resumable, harness-neutral work graph instead of a prose-only plan.

**Feature group:** Project Manifest v1, Work Contract v1, task status model, outcome metrics, generated synopses, board/status view, context compiler v1.

**Deliverables:**

- Project modes, abstract, `planning_mode`, scope/non-goal, and success-metric requirements become a schema-validated Project Manifest.
- Work Contract and TaskCard schema with objective, files/scopes, dependency DAG, owner role, acceptance criteria, gate IDs, required evidence, budget, risk and handoff fields.
- Completion state machine and machine-readable `status`/gate semantics; agents cannot mark a task complete merely by prose.
- Generated `quick_read` / synopsis contract with freshness evidence; it is a view, never canonical truth.
- `owledge status` / board view that reads contracts and does not mutate them by default; explicit `--sync` must record evidence for every transition.
- Context compiler pack types (bootstrap, task, reviewer, handoff, release) with token/file budget, selection reasons, exclusions and digest.
- Supervised planner summaries that show the user the relevant ticket/idea before requesting a decision.
- Baseline benchmark that compares full-vault, metadata scan, context pack and oracle sources using versioned fixture data.

**Acceptance / QA gates:**

- Schema migration and upgrade round-trip between two fixture versions preserves IDs, typed edges and unknown extension fields.
- No task reaches `accepted` without all required gate results and evidence references.
- Context output is deterministic for the same inputs and explains each included/excluded artifact.
- Board/status view succeeds on a project with 1,000 fixture records within an agreed budget.
- Benchmark reports fixture version, commit, OS, command and limitations; no universal token/cost claim is published.

### Checklist

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done

## Phase 2 — Harness-Neutral Coordination and Git Safety (v0.8)

**Outcome:** independently scoped agents can work in parallel and a human can integrate their results without reconstructing chat history or risking silent file clobbering.

**Feature group:** claims/leases, worktrees, checkpoints, resume, adapter manifests, conformance suite, Git integration manifest.

**Deliverables:**

- Work Package Manifest with work ID, dependency graph, branch/worktree, permitted paths, claim TTL, reviewer role, gates, evidence and merge order.
- File/component scope conflict detection before dispatch; a claim is advisory but enforced by validation and integration gates.
- Checkpoint/Resume protocol using input/output hashes, idempotency keys, and reconciliation of side effects after interruption.
- Reference Git workflow: one `codex/<work-id>` branch and worktree per independent work package; no direct worker commits to the integration branch.
- Tier-1 capability manifests and fixtures for Codex, Claude Code, and one generic MCP/CLI bridge. Hermes/OpenCode remain Tier-2 until they pass the same suite.
- Runtime hook validation at capture/stop where the harness supports it; unsupported capability yields an explicit warning.
- Integration manifest records branch, commits, changed scopes, gate results, review outcome, conflicts and residual risks.

**Acceptance / QA gates:**

- Eight parallel fixture workers with non-overlapping scopes produce no clobbered files.
- Overlapping claims block or require an explicit owner decision before execution.
- Kill/retry tests at every checkpoint create no duplicate canonical records or side effects.
- A second harness can resume a fixture work package from its ContextPack and Checkpoint.
- Adapter conformance produces a capability matrix and negative-test evidence; unsupported functions never silently pass.

### Checklist

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done

## Phase 3 — Provenance, Interchange, and Living Documentation (v0.9)

**Outcome:** reviewed project truth can cross tool boundaries and compile into documentation without becoming untraceable generated prose.

**Feature group:** evidence ledger, promotion UX, documentation compiler, drift/impact analysis, OKF profile, issue/PR bridges, privacy ingestion policy.

**Deliverables:**

- Append-only evidence ledger and GateResult contract; every public claim can point to source artifact, test/gate, commit and reviewer.
- Candidate → reviewed → canonical → superseded/rejected promotion workflow, including explicit `contradicts` and authority-resolution rules.
- Documentation compiler for ADRs, architecture snapshots, runbooks, onboarding packs, release notes and capability catalog; outputs carry source hashes and refresh state.
- `owledge drift` / impact analysis detects changed source hashes, stale decisions, missing acceptance evidence and affected documents.
- OKF compatibility profile: field mapping, `validate-okf`, safe `export-okf`, quarantined private draft import, and readiness report. Owledge governance remains stricter than interchange.
- GitHub Issues/Projects/PR and Spec Kit/OpenSpec bridges as sync targets; their records remain external references, not hidden second truth.
- Global/cross-project privacy policy: consent, allowlist, data-class enforcement, redaction and negative fixtures before any shared export.

**Acceptance / QA gates:**

- Every compiled document sentence/section in the golden fixture links to source artifacts or is labelled as generated interpretation.
- Deliberately stale source hashes and conflicting decisions are detected and blocked from “current” reports.
- Shared export negative tests reject personal, confidential, unsanitized and unreviewed records.
- OKF round-trip preserves stable Owledge IDs and typed edges through extensions; a consumer without extensions receives a safe portable projection.
- Issue/PR import cannot override canonical state without an explicit reviewed promotion.

### Checklist

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done

## Phase 4 — Trust, Evaluation, and Team-Scale Readiness (v1.0)

**Outcome:** the control plane is measurable, secure by default, and defensible for small teams without requiring a hosted platform.

**Feature group:** evaluation suite, observability adapter, security/privacy hardening, long-running scale, support policy.

**Deliverables:**

- Portable evaluation suite for provenance accuracy, resume correctness, context relevance, stale-document detection, harness portability, merge-conflict rate, false gate passes, and user-visible rework.
- Optional OpenTelemetry-compatible trace export for runs/gates; the canonical evidence ledger remains local Markdown/JSONL.
- Secret/PII detection, prompt-injection labelling for ingested external content, permission manifests for skills/plugins, retention and audit package export.
- Scale fixtures for 10, 1,000, and 10,000 artifacts, with rebuild, incremental index, context compile and drift timing targets.
- Public support/lifecycle policy: core compatibility window, Tier-1 harness commitment, experimental add-on disclaimer, migration support and deprecation process.
- Team policy packs for role separation and protected scopes; defer an actual team server unless pilots prove Git-backed coordination insufficient.

**Acceptance / QA gates:**

- 100% of golden shared records pass review/sanitization/provenance requirements.
- No private-to-shared leak in redaction/ingestion fixtures.
- Three Tier-1 harnesses achieve at least 95% contract/artifact equivalence on the same fixture.
- p95 context compile and drift checks meet published targets on the 10,000-artifact fixture.
- Evidence bundle can reconstruct the golden demo without chat history or a generated dashboard.

### Checklist

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done

## Phase 5 — Ecosystem, Cross-Project Intelligence, and Optional Scale (v1.x)

**Outcome:** Owledge grows by becoming the trusted interoperability layer, not by absorbing every adjacent product category.

**Feature group:** adapter SDK, registry, optional MCP app/dashboard, governed cross-project learning, optional team sync.

**Deliverables:**

- Adapter/template/gate SDK and registry with versioned manifests, provenance, permissions and conformance fixtures.
- Read-only MCP app/static explorer for work graph, evidence chain, contradictions, promotion queue and documentation impact.
- Cross-project intelligence that proposes patterns, risks and context candidates as review-required artifacts only.
- Optional team synchronization/lease backend only after a documented pilot threshold; portable on-disk format remains exportable.
- Ecosystem recipes for Spec Kit, OpenSpec, Beads, Graphiti, agentmemory, GitHub, GitLab, Jira/Linear, Notion/Confluence and supported runtimes.

**Acceptance / QA gates:**

- Third-party adapter passes its declared compatibility suite and cannot request undeclared write scopes.
- Explorer is fully rebuildable from local canonical artifacts.
- Cross-project recommendations cite sources, confidence and policy scope; none auto-promote.
- Any optional server can be disabled without loss of canonical project knowledge.

### Checklist

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done

## Autonomous Codex / Sub-Agent Delivery Model

Use phases as release trains and work packages as the unit of delegated implementation. Do not delegate “implement Phase 2” as a single task.

### Required work-package contract

Every work package must state:

- one outcome and explicit non-goals;
- allowed write paths and forbidden paths;
- dependencies and conflict/claim set;
- branch/worktree name and integration order;
- required tests/gates and expected artifacts;
- handoff packet with changed paths, evidence, residual risk, and exact next action.

### Git operating model

```text
main
 └─ integration/<phase>
     ├─ codex/<phase>-schema
     ├─ codex/<phase>-cli
     ├─ codex/<phase>-fixtures
     └─ codex/<phase>-docs
```

1. The orchestrator creates a phase integration branch from a clean, current base.
2. Each independent work package gets a separate worktree and `codex/<phase>-<slice>` branch.
3. A worker changes only its allowed paths and commits cohesive, reviewable changes with tests.
4. A separate reviewer checks the diff, gates, public-documentation impact, privacy boundary, and scope creep. The author does not approve its own work.
5. The integrator merges in dependency order, re-runs the phase gate bundle, then creates a release candidate commit. Do not squash away evidence-bearing commits until the owner chooses a release policy.
6. Any failing cross-package gate reopens the smallest affected work package; do not restart completed packages.
7. `main` advances only after all phase gates and a final evidence manifest pass.

### Suggested autonomous lanes

| Lane | Owns | May write | Must not do |
| --- | --- | --- | --- |
| Orchestrator | cutline, dependencies, claims, integration manifest | plans/work packages/context packs | implement unrelated features or promote by default |
| Schema worker | schemas, templates, migrations | scoped schema/template paths | change runtime adapters |
| CLI worker | parser, validators, compiler commands | scoped tool/test paths | rewrite canonical docs without source evidence |
| Adapter worker | one harness manifest/fixture | one adapter and fixtures | claim universal support |
| Documentation worker | public docs, demo, examples | docs/examples only | redefine runtime behavior |
| Reviewer | findings, gate evidence | review artifacts only | overwrite implementation |
| Curator | promotion proposal | canonical drafts/proposals | auto-promote raw session data |

## Golden Demo and Sales Narrative

### 30-second pitch

> Agenten schreiben schnell, aber ihre Pläne, Entscheidungen und Beweise verschwinden oft in einzelnen Sessions oder Harnesses. Owledge macht daraus einen portablen, Git-nativen Delivery Record: Es verbindet Ziel, Work Contract, parallele Arbeit, Tests, Entscheidungen und Dokumentation. Du kannst mit Codex starten, mit Claude weiterarbeiten und jederzeit nachvollziehen, was geändert wurde, warum, womit es geprüft wurde und was als Nächstes gültig ist.

### Current demo: what it proves today

The current repository demo creates a project-local context router, durable evidence, a next-agent handoff, index, and static report without rewriting host source files. It is useful for the first conversation because it is offline and concrete. Its limitation must be stated plainly: it installs demonstration artifacts and therefore does not yet prove live orchestration, Git claims, interruption/recovery, or cross-harness execution.

### Golden demo to ship in Phase 0

1. Start with a real feature request in a fixture repository.
2. Compile an intent into three work contracts with scopes, gates and non-goals.
3. Show dry-run dispatch, claims and branch/worktree plan.
4. Complete two fixture runs; deliberately interrupt the third.
5. Resume from checkpoint in a different harness fixture without duplicate writes.
6. Fail a reviewer gate due to missing test evidence; show that promotion is blocked.
7. Add the evidence, pass the gate, and compile an ADR/release-note/documentation update.
8. Open the static timeline/report and show source links from intent to commit/test/decision/documentation.

The demo must be offline, deterministic, CI-tested, copy-pasteable, and runnable in less than ten minutes. Record a three-minute walkthrough and publish expected terminal/report output alongside it.

## Product, Adoption, and Outcome Gates

| Signal | Phase 0–1 target | Phase 2–4 target |
| --- | --- | --- |
| Fresh-user time to first visible value | under 5 minutes | under 5 minutes across Tier-1 adapters |
| Demo completion without maintainer help | 80% in moderated tests | 90% |
| Evidence-complete increments | golden fixture only | 90% of pilot increments |
| Context re-briefing reduction | establish baseline | at least 50% against baseline |
| Resume time after session/harness switch | establish baseline | at least 25% faster |
| Source-linked public documentation | demo docs only | 100% of compiled golden docs |
| Private/shared leakage | 0 in fixtures | 0 in fixtures and release gates |
| Harness parity | one clear support matrix | 95% on Tier-1 fixture equivalence |

Claims about tokens, cost, productivity, or quality must always name the fixture, command, environment, limitations, and comparison. Do not publish universal savings claims.

## Owner Decisions Required Before Phase 0 Exit

1. Which ICP has priority for the next two releases: solo power users, agent-native OSS teams, or enterprise platform teams?
2. Which three harnesses receive Tier-1 support and CI commitment?
3. Is the reference Git/worktree orchestrator a core product feature or a documented adapter/example?
4. Which authority wins when code, issue tracker, ADR, and memory disagree?
5. Are any artifacts eligible for automatic promotion? Recommended default: no.
6. Is a future team-sync service in scope only after pilot proof, as recommended here?
7. Which concrete feature scenario should be used for the public golden demo?

## Resume Rule

For this roadmap and its downstream phase plans: a new agent reads the document, finds the first unchecked checklist item, and continues there. It does not restart a completed phase. If a checked item is suspected to be stale, re-run that phase’s gate bundle; if it fails, uncheck the item and redo the smallest affected scope. Gate output, not the checkbox, is the durable audit evidence.
