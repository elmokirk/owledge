---
memory_id: "mem:owledge:global:owledge:session:release-sparring-2026-06-26"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "session"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Release sparring for Owledge international launch"
summary: "Sparring notes covering uvx packaging, docs parity, add-ons, PI agents, hooks, swarm coordination, benchmark needs, naming, plugin readiness, parallel work, and release-critical gaps."
concept_tags:
  - "release-readiness"
  - "uvx"
  - "documentation"
  - "agent-swarms"
  - "pi-agent"
  - "benchmark-kit"
  - "plugin-marketplace"
  - "parallel-work"
stack_tags:
  - "python"
  - "typescript"
  - "markdown"
problem_patterns:
  - "docs-package-mismatch"
  - "addon-package-gap"
  - "swarm-write-conflicts"
  - "source-checkout-first-docs"
  - "contract-gate-root-mismatch"
  - "owledge-brand-drift"
architecture_patterns:
  - "markdown-first-memory"
  - "optional-adapter-layer"
  - "candidate-before-promotion"
failure_modes:
  - "public-docs-show-source-checkout-as-primary"
  - "uvx-addons-not-packaged"
  - "parallel-agents-overwrite-shared-plans"
  - "public-release-without-benchmark-proof"
  - "plugin-marketplace-claim-overreach"
reusable_lessons:
  - "Public launch requires uvx smoke tests, add-on packaging tests, and docs parity gates."
  - "Swarm support should use append-only per-agent deltas plus orchestrator-owned merges instead of shared-plan writes."
  - "Benchmark claims need model-aware local and frontier runs, not only tool runtime measurements."
confidence: 0.9
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "2026-06-26T14:32:30Z"
updated_at: "2026-06-26T15:15:00Z"
source_hash: ""
edges: []
---

# Release Sparring Notes - 2026-06-26

## Goal

Prepare Owledge for an international public release for power users, AI creators, and developer-tool evaluators.

## Step Log

1. Checked package state: local repo and PyPI currently show `0.6.0`, while the desired release story mentions `0.6.1`.
2. Verified `uvx owledge --help` works from PyPI and exposes the public Owledge CLI.
3. Verified `uvx owledge quickstart --target C:\tmp\owledge-uvx-smoke-20260626` creates a usable starter project.
4. Found a packaging gap: `uvx owledge install-addon --addon launch-demo-kit` fails with `Unknown add-on: launch-demo-kit`.
5. Found a docs parity gap: README and public docs still present `python tools/owledge.py` as the primary path.
6. Reviewed TS adapter, PI Agent setup, swarm coordination kit, benchmark docs, plugin hooks, and templates.
7. Identified release-critical gaps for docs, add-on authoring, benchmark credibility, swarm writing, and project abstract support.

## High-Signal Findings

- Public CLI exists and can be used through `uvx`.
- Add-ons are not fully usable through the PyPI/uvx install shape.
- PI Agent v1 is deterministic and local; no provider auth is needed.
- TS adapter is useful as CI validation for TypeScript/Node projects, not as a second runtime engine.
- Claude/Cowork hooks exist for session start, user prompt, post tool use, tool failure, compaction, stop, and session end.
- Codex plugin manifest currently exposes commands, agents, skills, and UI metadata, but not equivalent hook automation.
- Swarm coordination has role lanes and templates, but no write-claim, lock, blocker-escalation, or conflict-resolution protocol yet.
- Benchmarks exist but need a new token-efficiency and small/local-model trust benchmark before public power-user claims.

## Release Plan Inputs

- Make `uvx owledge quickstart` the public first-run path.
- Add an `owledge doctor` / `owledge validate` public wrapper or document the lower-level CLI clearly.
- Package add-ons as resources or create an add-on registry path that works from wheels.
- Add `.owledge/` only for state, config, cache, logs, add-on manifests, and runtime metadata; keep canonical memory visible.
- Add a project abstract field/file to every initialized project.
- Add brainstorm/ideation mode as a planning-layer workflow that writes idea cards and candidate plans, not canonical memory.
- Add swarm write protocol before marketing large multi-agent coordination.
- Replace old token benchmark with current context-pack, docs overhead, and local-model benchmark evidence.

## Follow-Up Artifact

Turn these notes into a release plan with phases:

1. Package and CLI parity.
2. README and docs parity.
3. Add-on authoring and registry contract.
4. Planning, brainstorm, and project abstract.
5. Swarm coordination hardening.
6. Benchmark and launch proof.

## Current-State Revalidation After Pull - 2026-06-26

### Evidence Commands

- `python tools/owledge.py test public-docs --project-root .` -> passed.
- `python tools/owledge.py test release-trust --project-root .` -> passed, version `0.6.1`.
- `python tools/owledge.py test launch-readiness --project-root .` -> passed.
- `python tools/owledge.py test runtime-adapters --project-root .` -> passed.
- `python tools/owledge.py test quality-ratchet --project-root .` -> passed.
- `python tools/owledge.py doctor --project-root . --mode kit` -> passed with score 95; warns that no root `kit-manifest.json` exists.
- `python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports` -> failed only because `contracts` failed.
- `python tools/owledge_core.py --project-root . test-contracts` -> failed because it still expects root `.owledge/` directories/files even though the refactor moved product source to `templates/owledge/` and dogfood to `internal/owledge/`.
- `python -m pytest tests\unit -q --tb=short` -> not run; current local Python lacks `pytest`.

### Status Of Previous Sparring Items

| Item | Current status | Release meaning |
| --- | --- | --- |
| Version mismatch 0.6.0 vs 0.6.1 | Fixed locally: `VERSION`, `pyproject.toml`, plugin manifests, README badge now show 0.6.1 | Good, but PyPI needs to be verified/published separately before public claims |
| `uvx owledge --help` | Previously verified; local package exposes `owledge` console script | Keep as primary install CTA |
| Add-ons from PyPI/uvx | Still not solved; `pyproject.toml` states `install-addon` and `build-project-kit` that need `addons/` or `plugins/` require source checkout | P0 for launch if 5-minute demo depends on add-ons |
| README/source checkout bias | Still present; README and docs still use `python tools/owledge.py` as primary path and public-doc gates expect that | P0 docs parity issue |
| Public gates | Mostly green | Good, but current gates encode old source-checkout assumptions |
| Contract gate | Broken in kit root because it expects root `.owledge/` | P0 gate correctness issue |
| Upgrade path | Shipped v0.6.1: version stamps, manifest, doctor drift, `upgrade` modes | Strong improvement |
| Global link | Shipped v0.6.1: `--link-global`, `global-link.json`, doctor check | Good foundation for global installs |
| Concept audit | Shipped v0.6.1 skill + CLI | Useful internal quality ratchet; not a public selling point yet |
| Session continuity | Shipped v0.6.1 planning-layer convention | Good for long-running agent work |
| Swarm support | Still templates/role-lanes only; no locking/conflict control | Do not market as robust swarm coordination yet |
| Benchmark proof | Existing benchmark measures tool runtime; enterprise add-on measures context hygiene. No model-aware benchmark for local/frontier model reliability yet | P0/P1 before influencer/power-user release |

## Plugin And Marketplace Readiness

### Claude / Cowork Adapter

Current plugin shape matches the broad Claude plugin structure: `.claude-plugin/plugin.json`, `commands/`, `agents/`, `skills/`, `hooks/`, `scripts/`, `LICENSE`, `CHANGELOG.md`.

Confirmed current Claude plugin reference supports manifest fields such as `displayName`, `commands`, `agents`, `skills`, `hooks`, `mcpServers`, `outputStyles`, `lspServers`, `settings.json`, `.mcp.json`, and `bin/`.

Owledge has:

- commands: yes
- agents: yes
- skills: yes
- hooks: yes for Claude/Cowork
- scripts: yes
- MCP server: no
- plugin `bin/`: no
- settings/default config: no
- marketplace-grade display fields: partial; `.claude-plugin/plugin.json` lacks `displayName` and richer metadata

Verdict: locally useful and structurally close, but not marketplace-grade yet. Do not claim marketplace readiness until metadata, MCP/server story, settings, install verification, and packaged distribution are finalized.

### Codex Plugin

The Codex manifest is versioned and has interface metadata, commands, agents, and skills. It explicitly does not package the Claude hook automation. That is acceptable if documented as "Codex commands/skills, Claude/Cowork hooks"; it is not equivalent runtime capture parity.

Release risk: Codex plugin standards and marketplace surface are less clearly codified in this repo than Claude's. Treat as local adapter support until there is a verified official marketplace publishing path.

### PI Agent Workspace Plugin

`plugins/pi-agent-workspace` is still brand-drifted:

- version is `0.1.0`, not aligned to kit version.
- descriptions and author still say "Owledge".
- Codex interface uses snake_case keys (`display_name`, `short_description`, `default_prompt`) while `owledge-cowork` uses camelCase.

Verdict: useful internal/optional plugin, not release-polished.

## Claude Cowork Implementation Path

Owledge currently fits Claude Cowork as a host-project adapter:

1. User initializes a project with Owledge.
2. User installs/copies `plugins/owledge-cowork/` into the runtime's plugin directory.
3. Claude/Cowork hooks capture session events into private `.owledge/sessions/`.
4. Stop/session-end hook writes compact private summaries.
5. User/curator promotes only reviewed, sanitized material into canonical/compiled/pattern/lesson memory.

This makes sense for end users when:

- they run long Claude/Cowork coding sessions;
- they need handoffs across sessions or agents;
- they can tolerate local Python as the hook runtime;
- they want private session logs, not automatic shared memory.

It is overkill when a user only wants planning discipline; then the principles/planning-layer path should be first.

## Brainstorm Mode

Brainstorm should be a release-planned feature, but it must not mutate canonical memory directly.

Recommended shape:

- Skill: `owledge-brainstorm` or extend planning layer with a dedicated mode.
- Runtime command: `owledge brainstorm --project-root . --topic "..." --mode divergent|expert-panel|ceo|office-hours --write`.
- Inputs: `OWLEDGE.md`, project abstract, roadmap, ideas, decisions, patterns, lessons, relevant global-link records.
- Outputs:
  - project-local idea cards in `.owledge/ideas/`;
  - candidate plan in `.owledge/plans/`;
  - optional review prompt in `.owledge/reviews/`;
  - no canonical promotion.
- Quality bar: expert-lens routing, 1-100 scoring, source-backed assumptions, non-goals, next experiment, and explicit "what would invalidate this idea".

Release decision: include the design and maybe a first minimal skill before launch; the full runtime command can be P1 if benchmark/packaging are still open.

## Benchmark Kit V2 Requirement

The current benchmark harness is not enough for power users. It measures KB scan, context-pack generation, and runtime handoff mechanics. The enterprise context benchmark is closer, but it does not yet run local/frontier model tasks.

Benchmark Kit V2 should be standalone and installable by users. Required scenarios:

1. Chat-only baseline: full prompt/recent transcript/no Owledge.
2. Naive docs baseline: paste docs or full vault.
3. Owledge metadata-first context pack.
4. Owledge handoff resume.
5. Multi-agent/subagent handoff scenario.
6. Adversarial retrieval traps: stale records, contradictory decisions, similar names, private records, low-signal docs, intentionally misleading tags.

Required model matrix:

- Local Ollama models, including installed small/mid models such as Qwen 8B class and Gemma latest.
- Optional Ollama Cloud.
- Frontier models via provider adapters where users bring keys.
- No keys required for deterministic/token-only runs.

Required metrics:

- prompt tokens, completion tokens, total estimated tokens;
- wall-clock latency;
- cost estimate where pricing is configured;
- retrieval precision/recall against oracle source set;
- irrelevant-token ratio;
- stale/contradiction detection;
- task success score via rubric;
- handoff correctness;
- subagent coordination overhead;
- model failure categories.

Output:

- JSON results.
- Markdown summary.
- Static HTML report.
- SVG/chart template with unambiguous labels, units, model name, seed, commit, hardware, profile, and caveats.

Release decision: a credible deterministic + optional model-aware benchmark kit is P0/P1 before influencer traffic. Public token-saving claims should wait for this.

## Naming: `owledge` vs `owledge`

User preference: rename everything named `owledge` to `owledge`.

Assessment:

- Brand-clean argument is strong. "Owledge" is legacy/generic and weakens Owledge positioning.
- Blast radius is very high: paths, schemas, templates, tests, add-ons, plugin names, skills, docs, examples, generated fixtures, and existing user projects all depend on `.owledge/`.
- A hard rename before release would be cleaner long-term but would consume a major migration sprint.

Recommended compromise before broad release:

1. Public brand: Owledge everywhere.
2. Plugin package names: rename `owledge-cowork` to `owledge-cowork` or at least present it publicly as "Owledge Cowork Adapter".
3. Skill display names: prefer Owledge-branded names for new skills.
4. Keep `.owledge/` as the stable canonical data folder for now, but document it as "Owledge's memory root".
5. Add migration plan for `owledge/` memory root:
   - support both `owledge/` and `.owledge/`;
   - new installs can choose `--memory-root owledge`;
   - old projects auto-detect `.owledge/`;
   - `owledge migrate-root --to owledge` later.

Release decision needed: either accept a legacy folder name for v0.6.x, or pause launch for a breaking rename sprint.

## README Problem -> Solution Table

Add a first-screen table:

| Problem | Owledge solution |
| --- | --- |
| Agent forgets context between sessions | Durable Markdown project context, handoffs, and summaries |
| Plans disappear in chat | Plans live in repo/vault with evidence and acceptance criteria |
| Subagents duplicate work | Role lanes, task ownership, handoffs, and orchestrator-owned deltas |
| Full vaults burn tokens | Metadata-first scan and scoped context packs |
| Teams distrust memory tools | Git-diffable Markdown, review status, sanitization, privacy boundaries |
| RAG/vector DB becomes source of truth | Owledge keeps Markdown canonical and exports reviewed views |
| Parallel branches drift | Project manifests, upgrade drift checks, append-only evidence, merge protocol |

## Parallel Agents, Subagents, Branches, And Worktrees

Recommended SOTA compromise for token-efficient subagent work:

- Subagents do not edit shared plans directly.
- Each subagent writes a small append-only lane artifact:
  - `.owledge/workpackages/<wp>/lanes/<agent-id>.md`
  - or `.owledge/handoffs/agent-lanes/<agent-id>-<task>.md`
- Each artifact has strict sections: sources read, files touched, decisions requested, blocker, delta, confidence, next action.
- Orchestrator owns the plan/tasklist and merges deltas.
- After each phase, one integrator writes an orchestration delta:
  - accepted changes;
  - rejected/parked findings;
  - plan/tasklist updates;
  - conflicts and decisions.
- Keep lane artifacts short with token budgets and source refs instead of full prose.

Collision handling:

- Add `owner_agent_id`, `claimed_at`, `lease_expires_at`, `branch`, and `worktree` fields to task/workpackage templates.
- Use append-only evidence/handoff files for workers.
- Only orchestrator/curator updates shared plans.
- If a subagent finds a gap/error/blocker, it writes `.owledge/blockers/<timestamp>-<agent-id>.md` and references it in its lane handoff.
- The orchestrator must explicitly resolve blockers before marking a phase done.

Git/worktree protocol:

- One worktree/branch per major lane.
- Each branch writes mostly unique files under lane/task directories.
- Shared root files (`OWLEDGE.md`, main plan, task board) are orchestrator-owned.
- Use a "merge packet" before merging:
  - branch summary;
  - files touched;
  - memory deltas;
  - conflicts;
  - required plan updates;
  - validation commands.
- For multi-branch teams, avoid concurrent edits to the same Markdown plan by design, not by merge conflict heroics.

## Integration Report Recheck

Old report evaluated v0.5.0, but several findings remain valid.

Resolved or improved:

- Product/dogfood split is done.
- PyPI package metadata exists.
- Version stamping and upgrade path exist.
- Planning/session-continuity conventions improved.
- `AGENTS.template.md` and integration block exist.

Still critical:

- README does not present "two options, no thinking".
- Minimal ready-made kit is not present as a first-class public path.
- Public docs still overuse source-checkout commands.
- Add-ons are listed before many users understand the core.
- Session privacy and promotion rules exist but need more concrete onboarding language.
- Obsidian-first story remains underdeveloped.
- Demo is still mostly textual; needs visual "agent forgets -> Owledge handoff -> new agent resumes" artifact.

## External Agent Feedback: Priority Classification

Must be pre-release:

- 1-command install via `uvx`, `uv tool install`, `pipx` with docs parity.
- 5-minute killer demo with visual output.
- Positioning: "Git-native memory and handoff layer for serious agentic work."
- Agent runtime recipes for Codex, Claude Code, Cursor/OpenCode, and generic agents.
- Benchmark proof with before/after and token/context metrics.

Strong P1:

- GitHub Action / CI recipe.
- MCP server minimal read/write wrapper.
- Obsidian-first template/story.
- Visual report polish.
- Real project case studies.

Later roadmap:

- `npx owledge`, unless a JS wrapper becomes strategically important.
- Deep Mem0/Graphiti/LlamaIndex integrations beyond exports.
- Community template gallery after the core demo works.

## Open Decisions For Owner

1. Memory root naming: keep `.owledge/` for v0.6.x or delay release for an `owledge/` migration path?
2. Public launch CTA: should the first command be `uvx owledge quickstart` or `uv tool install owledge && owledge init-project`?
3. Add-ons: should PyPI wheels include all add-ons/plugins, or should add-ons be fetched from GitHub/source registry?
4. Brainstorm: ship first as skill-only, or block release until CLI/runtime command exists?
5. Benchmark: which model set is mandatory for launch? Suggested: deterministic only + Ollama Qwen/Gemma + one frontier adapter.
6. Plugin marketplace: is "local adapter support" enough for launch, or should marketplace readiness become a P0 release gate?
7. MCP server: must it be pre-release, or can it be the first post-release integration?

## Updated Release Recommendation

Release should not be marketed broadly until these P0s are resolved:

1. Fix finalization/contracts drift for refactored `templates/` + `internal/` layout.
2. Make public install/docs `uvx`/`owledge`-first.
3. Decide and document naming strategy for `owledge`.
4. Fix add-on install shape for package users, or clearly gate add-ons as source-checkout only and remove them from first-run CTA.
5. Add Benchmark Kit V2 plan/spec and at least a deterministic standalone first implementation.
6. Add problem -> solution README table and 5-minute visual demo story.
7. Add subagent/parallel-work protocol to templates/docs before claiming swarm readiness.

Move to roadmap, not release blockers:

- Full MCP server marketplace polish.
- Full semantic PI Agent mode.
- Full TS runtime.
- Deep third-party memory/RAG integrations.
- Community gallery.

## Owner Decisions And Follow-Up Evaluation - 2026-06-26

Owner decisions:

1. `.owledge/` migration is considered essential for brand and long-term scalability.
2. Install-path tradeoffs need to be explained for release goals and user groups.
3. Add-on distribution needs a scored recommendation.
4. Brainstorm skill plus specification is sufficient for the release plan; full runtime can follow.
5. MCP needs effort/value scoring before making it a release blocker.

Additional idea:

- Owledge should support target audience profiles for product, SaaS, MVP, UX, and red-team planning.

### Decision 1: `.owledge/` Directory

| Option | Pros | Cons | Release Fit | Score |
| --- | --- | --- | --- | --- |
| Keep `.owledge/` only | Lowest implementation risk; current tests/templates expect it | Weak brand, old naming leaks everywhere, less credible for launch | Bad fit if branding is a core release goal | 4/10 |
| Rename fully to `.owledge/` with no compatibility | Cleanest brand and repo convention; matches `.claude`, `.codex`, `.github` style | High break risk; old projects and plugins break; hidden folder can reduce human discoverability | Too risky without migration tooling | 6/10 |
| New installs use `.owledge/`, old `.owledge/` auto-detected | Strong brand for launch, preserves existing users, allows gradual migration | More code paths and docs complexity; needs tests for both roots | Best fit for international release | 9/10 |
| `.owledge/` for runtime state plus visible `OWLEDGE.md` entrypoint | Keeps repo root clean while giving humans a visible project memory door | Requires clear layout rules | Best UX complement to dual-root migration | 9/10 |

Recommendation:

- Make `.owledge/` the canonical root for new installs before broad release.
- Keep backward-compatible read/write auto-detection for `.owledge/` during `0.6.x`.
- Add `owledge migrate-root --to .owledge` and a dry-run mode.
- Add top-level `OWLEDGE.md` or `OWLEDGE.md` as the visible human entrypoint so hidden folder branding does not hurt discoverability.
- Update package data, templates, plugins, docs, gates, and tests together; do not do a cosmetic rename only.

### Decision 2: Public Install Path

Context7 uv docs checked: `uvx` is an alias for `uv tool run` and runs a tool in an ephemeral environment; `uv tool install` installs a command-line tool persistently for user-wide use.

| Path | Best For | Pros | Cons | Score |
| --- | --- | --- | --- | --- |
| `uvx owledge ...` | Demos, first try, influencers, CI smoke tests | One-command, no persistent install, ideal for "try this now" | Re-resolves/caches tool; less clear for daily use | 9/10 |
| `uv tool install owledge` | Power users, daily global usage | Persistent `owledge` command, closer to pipx mental model, version pinning possible | One extra install step before use | 9/10 |
| `pipx install owledge` | Python CLI users not on uv | Familiar, persistent, broadly understood | Slower and less modern than uv; another path to test | 8/10 |
| `pip install owledge` | Python environments only | Familiar in Python projects | Pollutes envs; weaker CLI-tool story | 5/10 |
| Source checkout | Contributors and advanced debugging | Full repo, add-ons, tests, local development | Bad first impression for normal users | 4/10 |

Recommendation:

- README primary demo CTA: `uvx owledge init-project --target .` or `uvx owledge quickstart`.
- README daily install CTA: `uv tool install owledge`.
- Secondary: `pipx install owledge`.
- Source checkout belongs under "Contributing" and "Developing Owledge", not the top-level user path.

### Decision 3: Add-On And Plugin Distribution

| Model | Pros | Cons | Effort | User Value | Score |
| --- | --- | --- | --- | --- | --- |
| Bundle core add-ons/plugins in PyPI wheel | Works with `uvx`/`uv tool`; strongest first-run story; no source checkout | Larger package; package-data discipline needed | Medium | Very high | 9/10 |
| Separate PyPI packages per add-on | Clean modularity and versioning | Too much friction for early users; many packages to maintain | High | Medium | 6/10 |
| Remote registry fetched by `owledge addon install` | Scales well later; allows community registry | Needs trust, signing, caching, network failure handling | High | High later | 7/10 |
| Source checkout only | Simple for maintainers | Kills low-friction install; contradicts PyPI/uvx promise | Low | Low | 3/10 |

Recommendation:

- For release, bundle the small/core distribution set in the wheel: templates, core skills, cowork/plugin adapters, benchmark starter kit, docs snippets.
- Heavy/experimental add-ons can remain source-only but must be clearly labeled experimental.
- Add `owledge addons list` and `owledge addons install <name>` reading from a bundled manifest first.
- Defer remote registry/signing to P1.

### Decision 4: Brainstorm Mode

Owner decision accepted: skill plus spec is enough for release planning.

Release scope:

- Add `owledge-brainstorm` as a skill or planning-layer mode.
- Outputs: idea cards, audience assumptions, opportunity/risk score, challenge questions, candidate next steps.
- It must not directly mutate canonical memory unless explicitly promoted.
- Runtime command can be P1: `owledge brainstorm --topic ... --mode expert-panel|ceo|office-hours`.

Release score:

| Scope | Effort | Value | Risk | Recommendation |
| --- | --- | --- | --- | --- |
| Skill + spec | Low-medium | High | Low | Ship with release plan |
| CLI/runtime command | Medium | High | Medium | P1 unless launch positioning depends on it |
| Multi-agent brainstorm runtime | High | High | High | Later, after subagent protocol is stable |

### Decision 5: MCP Server

Context7 MCP docs checked: MCP servers expose tools/resources over standard transports; Python FastMCP stdio and JSON config patterns are documented in the official spec/source.

| Scope | Example Tools/Resources | Effort | Value | Release Risk | Score |
| --- | --- | --- | --- | --- | --- |
| No MCP before release | None | None | Low for power users | Low engineering risk, high adoption risk | 4/10 |
| Read-only local MCP | `read_project_context`, `search_memory`, `build_context_pack`, `doctor` | Medium | Very high for Claude/Cursor/Codex discovery | Manageable | 9/10 |
| Read/write MCP | Read-only plus `capture_decision`, `write_handoff`, `update_plan` | High | Very high | Needs permissions, conflict rules, audit logs | 7/10 |
| Polished marketplace MCP/app | Full docs, auth, UI/resources, packaging, examples | High-very high | Highest | Can delay release significantly | 7/10 |

Recommendation:

- Add a minimal read-only stdio MCP server as P0-lite if schedule allows.
- Do not make full write/promote MCP a release blocker.
- Make write operations P1 after `.owledge/` root, permissions, and subagent conflict protocols are stable.

### New Concept: Audience Profiles

This is a strong fit for release positioning because it connects Owledge memory to product decisions, UX, MVP scope, and red-team reviews.

Recommended minimal implementation:

- Add `.owledge/audiences/<audience-id>.md` templates.
- Add fields: segment, job-to-be-done, current workflow, pain, buying trigger, skepticism, success criteria, non-goals, accessibility/UX constraints.
- Let plans reference `audience_ids`.
- Let red-team reviews declare which audience they are challenging for.
- Add a README example: "Build for solo founder power users" vs "Build for enterprise team leads" changes the plan and risk review.

Release scope:

| Scope | Effort | Value | Recommendation |
| --- | --- | --- | --- |
| Markdown template only | Low | High | Include pre-release |
| CLI `owledge audience create/list` | Medium | High | P1 or pre-release if quick |
| Audience-aware brainstorm/red-team runtime | Medium-high | Very high | P1 after brainstorm skill lands |

Updated P0 list with owner decisions:

1. Implement `.owledge/` root for new installs with backward compatibility for `.owledge/`.
2. Fix gates/contracts for the new root layout.
3. Make README and docs `uvx`/`uv tool install` first.
4. Bundle core add-ons/plugins required for the promised first-run experience.
5. Ship Brainstorm skill/spec, not full runtime.
6. Decide whether read-only MCP P0-lite fits the schedule.
7. Add Audience Profiles as a low-effort/high-value planning layer template.

## Release Plan Finalization After Owner Feedback - 2026-06-26

Owner clarifications:

- There are no external users yet. The `.owledge/` migration can be direct for the public product.
- A visible `OWLEDGE.md` is desirable and should simplify `AGENTS.md` integration.
- Owledge should be primarily agent/harness usable. `uvx` and `uv tool install` remain the professional install story, but the first run must feel clear to humans.
- Core add-ons/plugins should be bundled; heavy/experimental distribution paths go to roadmap.
- Brainstorm ships as skill + spec.
- Read-only MCP should be implemented; write MCP remains roadmap.
- Audience profiles are strategically strong for product teams, SaaS builders, UX planning, and red-team reviews.
- Agentic research needs a native project layer, especially for subagent-driven market and planning research.
- Hermes adapter should be planned explicitly.

### Direct `.owledge/` Migration Decision

Because no external user base exists, direct public migration is now the recommended path.

Implementation stance:

- New public template root: `.owledge/`.
- Visible entry file: `OWLEDGE.md`.
- Keep `OWLEDGE.md` only if needed for existing agent compatibility, but route humans and agents through `OWLEDGE.md` first.
- Internally migrate `templates/owledge/` to `templates/.owledge/` or equivalent package source path.
- Rename public plugins, commands, examples, and docs away from `owledge`.
- Use temporary internal compatibility only where required to keep existing dogfood artifacts readable during the migration; do not market `.owledge/` as the public folder.

Recommended `.owledge/` shape:

```text
.owledge/
  context/
  plans/
  tasks/
  workpackages/
  sessions/
  evidence/
  handoffs/
  decisions/
  reviews/
  audiences/
  research/
  brainstorm/
  integrations/
  mcp/
  indexes/
  exports/
  tmp/
```

Visible root files:

```text
OWLEDGE.md       # human + agent entrypoint
AGENTS.md        # agent runtime integration and rules
CLAUDE.md        # Claude-specific bridge when present
REVIEW.md        # review/red-team policy
```

### Native Agentic Review Fit

Evidence checked:

- `REVIEW.md` already defines Owledge review defaults, persona library, gates, verdict thresholds, and promotion boundaries.
- `skills/agentic-review/SKILL.md` is Owledge-compatible and requires evidence-linked findings, personas, scores, verdicts, and task conversion.
- `internal/owledge/decisions/red-team-v0.6.1-pr.md` proves this review pattern already exists in dogfood form.
- `skills/review-evaluation-workflow/SKILL.md` already maps review artifacts to Markdown templates.

Verdict:

- `agentic-review` is a strong native Owledge capability and should become part of the public positioning, not just a hidden maintainer workflow.

Native integration recommendation:

- Move/rebrand review artifacts to `.owledge/reviews/`.
- Add `.owledge/reviews/policies/` or keep root `REVIEW.md` as the review policy.
- Add `audience_ids` to review templates so Red Team reviews explicitly state who the review protects.
- Add `source_research_ids` to reviews so strategy and market claims cite research cards.
- Add README section: "Owledge turns Red Team review into durable tasks."

### Native Audience Layer

Recommended release scope:

- Add `.owledge/audiences/<audience-id>.md`.
- Add `audience_ids` to plans, reviews, brainstorm outputs, and research briefs.
- Use audiences for MVP scope, UX decisions, market positioning, and red-team lenses.

Minimal audience template fields:

- segment
- job_to_be_done
- workflow_context
- pain_points
- buying_or_adoption_trigger
- skepticism
- success_criteria
- non_goals
- ux_constraints
- risk_sensitivity
- evidence_links

### Native Agentic Research Layer

Current state:

- A `research-card-template.md` exists, but it is framed as `global-user-memory` and personal/private by default.
- Runtime bridge already requires research freshness fields: source URL, source date, retrieved date, valid-until date, version context, and confidence.
- There is no clear first-class project research folder for subagents.

Recommended release scope:

```text
.owledge/research/
  briefs/
  sources/
  findings/
  claims/
  syntheses/
  lanes/
  reviews/
```

Subagent protocol:

- Research subagents write append-only lane files under `.owledge/research/lanes/<agent-id>-<topic>.md`.
- Source cards live under `.owledge/research/sources/`.
- Findings are short, source-backed, and carry freshness metadata.
- A synthesizer writes `.owledge/research/syntheses/<topic>.md`.
- Plans and README claims cite synthesis IDs, not raw research dumps.

Research template must include:

- source_url
- source_type
- source_date
- retrieved_at
- valid_until
- license_or_usage_notes
- claim_supported
- counterevidence
- confidence
- audience_ids
- related_plan_ids
- source_hash

Release recommendation:

- Add the folder and templates pre-release.
- Defer full `owledge research` CLI until P1 unless implementation is trivial after the `.owledge/` migration.

### Hermes Adapter Planning

Context checked with Context7 against `/nousresearch/hermes-agent/v2026.4.16`:

- Hermes uses `~/.hermes/` with `config.yaml`, `.env`, `SOUL.md`, `memories/`, `skills/`, `sessions/`, and `logs/`.
- Hermes exposes CLI commands for tools and skills such as `hermes tools list`, `hermes tools enable NAME`, `hermes skills list`, `hermes skills install ID`, and `hermes skills publish PATH`.
- Hermes can run as a persistent Docker gateway with `~/.hermes` mounted and API port `8642`.

| Adapter Shape | What It Does | Effort | Value | Release Timing |
| --- | --- | --- | --- | --- |
| Hermes instruction bridge | Adds `SOUL.md`/skill instructions telling Hermes to read `OWLEDGE.md`, use context packs, and write evidence/handoffs | Low | Medium-high | P0-lite docs |
| Hermes skill package | Publish/install an Owledge skill into `~/.hermes/skills/` that wraps the Owledge contract | Medium | High | P1 or late P0 if fast |
| Hermes toolset wrapper | Expose commands like `owledge doctor`, `build-context-pack`, `write-evidence`, `write-handoff` as Hermes tools | Medium-high | Very high | P1 |
| Hermes gateway integration | Docker/gateway deployment with mounted project `.owledge/` and scheduled checks | High | High for teams/always-on agents | P2 |
| Hermes + MCP bridge | Let Hermes consume Owledge through MCP if/when the runtime path is clean | Medium | High | P1 after read-only MCP |

Recommendation:

- Pre-release: document the Hermes instruction bridge and include Hermes in the runtime recipe matrix.
- P1: build a Hermes skill package plus toolset wrapper.
- Do not let Hermes adapter block `.owledge/`, README, benchmark, MCP, and docs parity.

### Concept Blindspot Audit - Current Release Plan

Mechanical command run:

```bash
python tools/owledge.py concept-audit --project-root . --format summary
```

Result:

| Dimension | Score | Interpretation |
| --- | ---: | --- |
| lifecycle | 7 | Commands exist, but source repo upgrade dry-run/manifest behavior still warns |
| distribution | 7 | Version and README match, but sdist/build proof is incomplete in local check |
| dogfood | 10 | Dogfood sync is healthy |
| contracts | 5 | `test-contracts` fails with 89 checks due old root expectations |
| cross_layer | guided | Needs human-guided validation |
| failure_modes | guided | Needs explicit failure-mode table |
| coherence | guided | Needs naming/glossary pass after `.owledge/` migration |
| self_description | guided | README/docs claims must match actual `uvx`, MCP, benchmark, add-on behavior |

### Red Team / Blindspot Findings Table

| Problem | Solution Options | Recommendation | Importance |
| --- | --- | --- | ---: |
| Public folder still says `owledge` while product is Owledge | Keep old name; dual support; direct `.owledge/` migration | Direct `.owledge/` migration now, because no external users exist | 10 |
| Hidden `.owledge/` can reduce human discoverability | Root README only; visible `OWLEDGE.md`; mirror context in AGENTS | Add `OWLEDGE.md` as first-class entrypoint and have AGENTS/CLAUDE point to it | 9 |
| Contract gate expects old root structure | Patch contracts only; migrate all required dirs/files; support both roots | Update gates/tests/templates/package data to `.owledge/`; keep temporary internal adapter only if needed | 10 |
| README still risks source-checkout mental model | Keep old docs; add uv section; rewrite first screen | Rewrite first screen around `uvx`, `uv tool install`, 5-minute demo, problem-solution table | 10 |
| Add-ons from PyPI/uvx may not work as promised | Source-only; bundle core; remote registry | Bundle core add-ons/plugins in wheel and mark heavy add-ons experimental | 9 |
| Brainstorm could become uncontrolled idea spam | Runtime first; skill-only; no promotion boundary | Ship skill/spec with candidate-only outputs and explicit promotion path | 8 |
| Read-only MCP is highly valuable but can sprawl | No MCP; read-only MCP; full write MCP | Ship read-only stdio MCP if schedule allows; defer write/promote MCP | 8 |
| Audience assumptions are implicit | Leave in plans; add audience templates; full persona runtime | Add `.owledge/audiences/` template now; wire IDs into plans/reviews/research | 8 |
| Research is not a native project layer | Use global research cards; add research folder; full CLI | Add `.owledge/research/` structure and templates pre-release; CLI P1 | 9 |
| Subagent research can bloat tokens and conflict | Shared doc; lane files; database | Use append-only research lanes plus synthesizer summaries | 9 |
| `agentic-review` exists but is not productized | Keep as internal skill; public workflow; native CLI | Productize as Owledge review layer with `.owledge/reviews/`, audience IDs, task conversion | 8 |
| Hermes adapter could distract from core launch | Build full adapter now; docs only; skill package later | Add Hermes recipe now; build Hermes skill/toolset in P1 | 6 |
| Benchmarks can overclaim token savings | Skip; synthetic only; model-aware benchmark kit | Keep Benchmark Kit V2 as P0 for public credibility | 10 |
| Self-description may drift during migration | Manual review; concept audit; traceability matrix | Re-run concept audit and release gates after `.owledge/` migration before publish | 10 |

Review verdict:

- Score: 78/100
- Verdict: revise
- Blocking issue: contracts/gates still fail against the current refactored layout.
- Promotion boundary: this release plan is strong enough to become the execution plan after owner approval, but not yet publish-ready.

### Final Release Realization Plan

P0 release blockers:

1. Migrate public root to `.owledge/` and add `OWLEDGE.md`.
2. Fix contracts/finalization gates against the new root.
3. Rewrite README first screen around positioning, problem-solution table, `uvx`, `uv tool install`, and 5-minute demo.
4. Bundle core add-ons/plugins in the PyPI wheel or remove unbundled promises from first-run docs.
5. Add Benchmark Kit V2 spec and deterministic standalone first implementation.
6. Add `.owledge/audiences/` and `.owledge/research/` templates.
7. Add Brainstorm skill/spec with candidate-only outputs.
8. Add read-only MCP server if it fits schedule; otherwise document exact P1 scope and do not claim MCP support.
9. Productize `agentic-review` as the native review/red-team layer.
10. Re-run concept audit, finalization gates, public docs, release trust, launch readiness, runtime adapters, and quality ratchet.

P1 immediately after release:

1. Hermes skill package and toolset wrapper.
2. Write/promote MCP operations with permissions and audit logs.
3. Audience-aware brainstorm and red-team runtime.
4. `owledge research` CLI.
5. Remote add-on registry and signing.
6. Obsidian-first demo and visual report polish.

Open owner decisions:

1. Should `OWLEDGE.md` remain in public templates as a compatibility alias, or should `OWLEDGE.md` fully replace it?
2. Should `.owledge/tmp/`, `.owledge/exports/`, and `.owledge/sessions/raw/` be gitignored by default while reviewed artifacts remain tracked?
3. Should read-only MCP be a hard P0 or a P0-lite that can slip only if docs clearly avoid the claim?
4. Which Benchmark Kit V2 first-run models are mandatory: deterministic only, local Ollama Qwen/Gemma, or one frontier model too?
5. Should Hermes adapter be documented as "recipe only" for launch or included as an experimental bundled skill?

## Owner Answers And Final Scope Tightening - 2026-06-26

Owner answers:

1. `OWLEDGE.md` should fully replace `OWLEDGE.md` for public templates. `OWLEDGE.md` is too generic and weak for external users.
2. Ignore `tmp` by default. Need a clear policy for exports and sessions.
3. Read-only MCP is a hard P0 because it creates immediate trust and agent/harness discoverability.
4. Benchmark Kit V2 should extract the useful old plan, but stay minimal for local models. Recommended local models: `gemma4:latest` and `qwen3.5:9b` or `qwen3:8b` depending on installed tags.
5. Hermes adapter moves fully to roadmap. A partial `SOUL.md` recipe would feel unfinished.

### Contracts And Gates: Direct `.owledge/` Adjustment

Yes, the contracts and gates can be directly adjusted from `.owledge/` to `.owledge/`. This is not just a review wording change; it is a product contract migration.

Required implementation areas:

- Required dirs/files constants in `tools/owledge_core.py` and `tools/owledge.py`.
- Product template source path, currently `templates/owledge/`.
- Dogfood path, currently `internal/owledge/`.
- Add-on fixtures and starter folders.
- Plugin scripts and runtime bridge paths.
- Gitignore rules for generated state.
- Docs and README examples.
- Contract tests, finalization gates, runtime adapter smoke tests, release trust checks, and build-project-kit verification.

Estimated plan score if contracts/gates are correctly migrated:

| State | Score | Verdict | Reason |
| --- | ---: | --- | --- |
| Current plan before root migration | 78 | revise | Good concept, but contracts fail and naming remains incoherent |
| Contracts/gates fixed but README/install still old | 84 | revise/near accept | Mechanical blocker gone, but self-description still weak |
| `.owledge/` + `OWLEDGE.md` + gates + README uv-first | 90 | accept | Core release story becomes coherent |
| Above + Benchmark Kit V2 + read-only MCP | 94 | accept/high-confidence | Strong enough for international release push |
| Above + public demo artifacts/case study | 96 | promote-candidate | Credible launch package, still owner-approved |

### Root Naming Options

| Option | Pros | Cons | Recommendation |
| --- | --- | --- | --- |
| Keep `.owledge/` | Least work; current gates closer | Weak brand; contradicts Owledge release; old mental model persists | Reject for public release |
| Rename to visible `owledge/` | Visible in file explorers; strong brand; less hidden-state concern | Less conventional for agent/tool config; more visual clutter in repos | Acceptable fallback if hidden folder is unacceptable |
| Use `.owledge/` only | Tool-native; matches `.claude`, `.codex`, `.github`; clean project root | Hidden in Unix-style views unless users know to look; needs visible entrypoint | Recommended if paired with `OWLEDGE.md` |
| `.owledge/` + `OWLEDGE.md` | Best of both: tool state hidden, human/agent entrypoint visible | Requires strict docs so users know where durable artifacts live | Strong recommendation |
| `.owledge/` + optional `owledge/README.md` mirror | Maximum discoverability | Duplicates concepts; risks drift | Avoid unless user testing shows discoverability issues |

Final recommendation:

- Use `.owledge/` as the canonical machine/tool root.
- Use `OWLEDGE.md` as the canonical human/agent entrypoint.
- Remove `OWLEDGE.md` from public templates. If internal dogfood still needs it during migration, treat it as temporary compatibility only.

### Gitignore Policy For `.owledge/`

Recommended tracked by default:

- `.owledge/context/`
- `.owledge/plans/`
- `.owledge/tasks/`
- `.owledge/workpackages/`
- `.owledge/evidence/` when evidence is intentionally project-relevant
- `.owledge/handoffs/`
- `.owledge/decisions/`
- `.owledge/reviews/`
- `.owledge/audiences/`
- `.owledge/research/briefs/`
- `.owledge/research/sources/`
- `.owledge/research/findings/`
- `.owledge/research/syntheses/`

Recommended ignored by default:

- `.owledge/tmp/`
- `.owledge/cache/`
- `.owledge/exports/`
- `.owledge/reports/generated/`
- `.owledge/indexes/generated/`
- `.owledge/sessions/raw/`
- `.owledge/sessions/drafts/`
- `.owledge/mcp/cache/`

Policy:

- Handoffs are the durable resumable artifact, not raw sessions.
- Exports are generated views and should be ignored unless explicitly published into `docs/`, `assets/`, or a release artifact.
- Raw sessions are private by default and should not enter normal git history.

### Wikilinks And Internal Linking

Current state:

- Owledge explicitly preserves existing `[[Wiki Links]]` and does not rewrite or convert them in KB mode.
- Current QA includes checks that user KB wiki links are not converted.
- Current canonical graph relation model is frontmatter `edges`, validated by `edge.schema.json`.
- `edge.schema.json` supports typed relations such as `relates_to`, `depends_on`, `implements`, `blocks`, `validates`, `contradicts`, and `similar_to`.

Release gap:

- Owledge does not yet appear to have a first-class gate that resolves Wikilinks, reports broken Wikilinks, or proposes candidate typed edges from Wikilinks.

Recommended model:

- Preserve Wikilinks as human-facing navigation.
- Use frontmatter `edges` as machine/audit truth.
- Add optional `related` or `related_files` field for lightweight path-level links if needed, but do not let it replace typed edges.
- Add `wikilink-audit` gate:
  - extract `[[Target]]` links;
  - resolve target candidates by filename/title/memory_id alias;
  - report unresolved or ambiguous links;
  - optionally propose candidate `edges` but never auto-write them.

Planning benefit:

- Plans can include both:
  - frontmatter `edges` to task IDs, evidence, reviews, research syntheses, and decisions;
  - body Wikilinks for human navigation, e.g. `[[P0 Benchmark Kit V2]]`, `[[Audience: SaaS Builder]]`.
- Agents can retrieve graph-accurate related work from typed edges while humans can navigate naturally in Obsidian-style editors.

Recommended plan/task metadata:

```yaml
audience_ids:
  - "aud:saas-builder"
related:
  - ".owledge/tasks/p0-benchmark-kit-v2.md"
  - ".owledge/research/syntheses/local-model-benchmark.md"
edges:
  - type: "implements"
    target: "mem:owledge:task:p0-benchmark-kit-v2"
    reason: "Plan phase implements this task"
  - type: "derived_from"
    target: "mem:owledge:research:local-model-benchmark"
    reason: "Benchmark scope comes from research synthesis"
```

### Benchmark Kit V2 Recommendation

Old benchmark plan remains directionally correct:

- Existing deterministic benchmark measures assembly/retrieval strategy, not real model behavior.
- Model-aware benchmark should measure whether the model can use scoped context, not whether the whole vault fits into a prompt.
- Scale should mean "vault size to retrieve from", not "tokens sent to the model".
- 100k is a retrieval-pipeline stress test, not a normal local-model inference test.
- Metrics should include tokens, latency, correctness, retrieval quality, hallucination, privacy/staleness handling, and failure frontier.

Current checks:

- Local shell did not find `ollama` in PATH, so installed local models could not be verified from this Codex environment.
- Official Ollama pages currently list `gemma4` with `gemma4:latest`, `gemma4:e2b`, `gemma4:e4b`, `gemma4:12b`, `gemma4:26b`, `gemma4:31b`.
- Official Ollama pages currently list `qwen3.5` with `qwen3.5:latest`, `qwen3.5:0.8b`, `qwen3.5:2b`, `qwen3.5:4b`, `qwen3.5:9b`, `qwen3.5:27b`, `qwen3.5:35b`, and larger/cloud variants.
- Official Ollama pages list `qwen3:8b` as a valid local model. If the user has "qwen3.5 8b", verify the exact tag locally; official page indicates `qwen3.5:9b`, not `8b`.
- Ollama API exposes `/api/chat` with `prompt_eval_count`, `eval_count`, `total_duration`, `load_duration`, `prompt_eval_duration`, and `eval_duration`; these are enough for token and speed metrics.

Recommended first-run matrix:

| Tier | Models | Reason |
| --- | --- | --- |
| Deterministic baseline | no model | Always runnable in CI and by users without Ollama |
| Local default | `gemma4:latest` | User has it; strong current local baseline |
| Local reasoning/agent baseline | `qwen3.5:9b` if installed, else `qwen3:8b` | Popular Qwen local family; strong agent/retrieval behavior |
| Optional frontier | one provider adapter, opt-in only | Allows comparison without making API keys required |

Scales:

- `10`, `100`, `1000`, `10000` for local model runs.
- `100000` only as retrieval-pipeline stress, no model call by default.

Question categories:

- single fact lookup
- multi-hop evidence
- stale/contradictory records
- private/unsafe record exclusion
- similar-name ambiguity
- plan-to-ticket linkage
- subagent handoff resume

Outputs:

- JSONL raw cell results.
- `latest.json` aggregate.
- `latest.md` summary.
- Static HTML/SVG chart with labels:
  - model tag and digest;
  - scale;
  - profile;
  - prompt tokens;
  - completion tokens;
  - total duration;
  - tokens/sec;
  - retrieval precision/recall;
  - correctness score;
  - privacy/staleness failures;
  - failure frontier.

### Read-Only MCP Hard P0

Read-only MCP is now a hard release requirement.

P0 tool scope:

- `owledge_read_entrypoint` -> returns `OWLEDGE.md`.
- `owledge_doctor` -> read-only health output.
- `owledge_search_memory` -> searches reviewed/tracked artifacts.
- `owledge_build_context_pack` -> returns scoped context pack.
- `owledge_list_tasks` -> lists task/workpackage status.
- `owledge_list_reviews` -> lists review artifacts and verdicts.

Excluded from P0:

- write evidence;
- write handoff;
- promote memory;
- mutate plan/task status.

### Hermes Roadmap Change

Hermes is moved fully out of release scope.

Reason:

- A partial `SOUL.md` recipe without a real skill/toolset would look unfinished.
- Hermes deserves a complete adapter: skill package, toolset wrapper, and clear gateway behavior.

Roadmap target:

- P1/P2: full Hermes adapter with `SOUL.md` guidance, Hermes skill package, tool wrappers, and optional MCP bridge.

### Updated Final P0

1. Direct `.owledge/` migration plus `OWLEDGE.md` replacement for `OWLEDGE.md`.
2. Contracts/gates updated to `.owledge/` and green.
3. README first screen rewritten around Owledge, `uvx`, `uv tool install`, and problem-solution positioning.
4. Core add-ons/plugins bundled or claims reduced.
5. Read-only MCP server implemented and documented.
6. Benchmark Kit V2: deterministic baseline plus minimal Ollama model matrix.
7. Native `.owledge/audiences/`, `.owledge/research/`, `.owledge/reviews/`, and Brainstorm skill/spec.
8. Wikilink audit/proposed-edge model added as a release feature or explicitly documented as P1 if too large.
9. Hermes removed from release scope and placed in roadmap as full adapter.

## Final Benchmark Kit Pre-Release Plan - 2026-06-26

Owner benchmark additions:

- Benchmarking should eventually cover top coding harnesses: Claude Code, Codex, Cursor, Zed, and OpenCode.
- Initial harness focus, if needed, should be Claude Code, Codex, and OpenCode.
- Harness benchmarking is primarily an Owledge plugin/adapter benchmark, not the same thing as core Owledge retrieval/model benchmarking.
- Pre-release should focus on validating Owledge with local/smaller models for reliability, context pollution, retrieval quality, and large documentation sets.
- The kit should be easy to run as a standalone simulation in a user environment.
- Local model list from screenshot includes `gemma4:latest`, `qwen3.5:4b`, `qwen3.5:9b`, `qwen3:latest`, `qwen3:0.6b`, `llama3.2:latest`, `llama3.1:8b`, `deepseek-r1:latest`, `command-r7b:latest`, `hermes3:latest`, `bge-m3:latest`, and several cloud tags.
- Cloud models are out of pre-release scope but should be recorded for later enterprise/local-hosted validation.

### Critical Benchmark Scope Decision

Pre-release must not try to benchmark everything.

| Scope | Pre-Release? | Reason |
| --- | --- | --- |
| Deterministic Owledge retrieval/assembly baseline | Yes | Always runnable, CI-safe, proves the pipeline without model variance |
| Local Ollama model benchmark | Yes | Core claim: Owledge remains useful with smaller/local models |
| HTML report with stable charts | Yes | Needed for power-user trust and shareable evidence |
| Stable result schema | Yes | Enables future regression comparisons |
| Harness benchmark across Claude Code/Codex/OpenCode | No, plan only | Tests plugin/harness behavior, not core Owledge; too many moving parts for final pre-release gate |
| Frontier/cloud model benchmark | No, opt-in/post-release | Costs/usage and model drift; not required for local value proof |
| 100k model inference | No | Meaningful as retrieval-pipeline stress only; local models should not read raw 100k docs |
| Cursor/Zed harness automation | No | Better as plugin/adapter track after core launch |

### Benchmark Modes

CLI should support explicit modes and prompt before expensive execution when interactive.

| Mode | Behavior | Requires | Prompt |
| --- | --- | --- | --- |
| `ci` / `deterministic` | Synthetic corpus, retrieval/assembly scoring, no LLM call | Python only | No |
| `local` | Runs deterministic baseline plus selected local Ollama models | Ollama running, model tags installed | Yes unless `--yes` |
| `frontier` | Optional provider adapters for hosted frontier comparison | API keys and cost consent | Yes, hard confirmation |
| `harness` | Later: launches/uses Claude Code, Codex, OpenCode with same Owledge scenarios | Installed harnesses and adapters | Yes |
| `all` | Runs every available mode | Everything above | Yes, with cost/time warning |

Recommended command shape:

```bash
owledge benchmark-kit run --mode ci --output .owledge/reports/generated/benchmark
owledge benchmark-kit run --mode local --models gemma4:latest,qwen3.5:4b --scales 10,100,1000 --yes
owledge benchmark-kit report --input .owledge/exports/benchmark/latest.json --format html
```

Interactive warning for `local`, `frontier`, `harness`, and `all`:

```text
This benchmark may consume local CPU/GPU/VRAM, run for a long time, or use paid API/model usage.
Mode: local
Models: gemma4:latest, qwen3.5:4b
Scales: 10, 100, 1000
Continue? [y/N]
```

### Pre-Release Local Model Matrix

Minimal recommended model set:

| Model | Why | Local Screenshot Status |
| --- | --- | --- |
| `gemma4:latest` | Strong current local baseline; 128K context; official Ollama page marks it as agentic/coding capable | Installed, 9.6GB |
| `qwen3.5:4b` | Small local model; good stress test for "does Owledge help weaker models?" | Installed, 3.4GB |
| `qwen3.5:9b` | Optional stronger Qwen local tier; useful if runtime budget allows | Installed, 6.6GB |
| `qwen3:latest` or `qwen3:8b` | Fallback if Qwen3.5 tags are unavailable on a user machine | Installed as `qwen3:latest`, 5.2GB |

Pre-release default:

- `ci`: no model.
- `local`: `gemma4:latest,qwen3.5:4b`.
- Optional `--extended-local`: add `qwen3.5:9b`.

Do not require users to download many models. The benchmark should detect installed models via Ollama `/api/tags`, then recommend the closest supported profile.

### Future Cloud / Enterprise Model Track

Hold for post-release:

| Model | Why It Matters Later | Source Notes |
| --- | --- | --- |
| `gemma4:31b-cloud` / `gemma4:cloud` | Larger Gemma tier, 256K context, good workstation/cloud comparison | Ollama lists Gemma 4 cloud variants |
| `qwen3.5:cloud` / `qwen3.5:397b-cloud` | Enterprise-scale Qwen comparison with 256K context | Ollama lists Qwen3.5 cloud variants |
| `minimax-m2.7:cloud` | Agentic coding/productivity cloud model, 200K context | Ollama lists medium usage cloud model |
| `glm-5.1:cloud` | Agentic engineering cloud model, 198K context | Ollama lists high usage cloud model |
| `kimi-k2.5:cloud` | Large multimodal agentic model, 256K context | Ollama lists high usage cloud model |
| `nemotron-3-super:cloud` | Agentic MoE, 120B total/12B active, 256K context | Ollama lists cloud variant and local 87GB variant |
| `nemotron-3-ultra:cloud` | Long-running agent workflows, 256K listed; readme claims very long context | Ollama lists high usage cloud model |

Purpose later:

- Enterprise/cloud-hosted validation across 8GB, 16GB, 24GB, 48GB, 96GB+ VRAM profiles.
- Harness adapter comparison with Claude Code, Codex, OpenCode, Cursor, and Zed.
- RAG integration preparation for company-wide knowledge.

### Harness Benchmark Track

Harness benchmarks should be a separate track because they test:

- Owledge plugin/adapter installation;
- whether the harness respects `OWLEDGE.md` and `.owledge/`;
- whether the harness causes context pollution;
- whether the harness writes to allowed lanes only;
- whether handoff/resume works in that harness;
- whether local model behavior changes through the harness wrapper.

Later harness matrix:

| Harness | Initial Priority | Why |
| --- | ---: | --- |
| Claude Code | 1 | Large audience, plugin/hook relevance, common power-user path |
| Codex | 1 | Native target user base for this repo |
| OpenCode | 1 | Open/local-friendly harness and official Ollama launch examples |
| Cursor | 2 | Important developer audience but adapter surface differs |
| Zed | 2 | Strong developer editor story, but should not block initial proof |

Pre-release action:

- Document the harness track as roadmap.
- Do not include it in the final pre-release benchmark gate.

### Benchmark Scenarios

Scales:

- `10` files: sanity and edge behavior.
- `100` files: small real project.
- `1000` files: large documentation/codebase proof.
- `10000` files: retrieval pipeline stress.
- `100000` files: deterministic retrieval stress only, no model call by default.

Profiles:

- `no_owledge_full_prompt`: baseline where context is poorly scoped.
- `metadata_scan`: filenames, titles, hashes, tags, wikilinks, frontmatter.
- `owledge_context_pack`: scoped context pack with reviewed artifacts only.
- `oracle`: ideal source set for scoring, not a usable runtime mode.

Probe categories:

- single fact lookup;
- multi-hop evidence;
- similar-name ambiguity;
- stale record detection;
- contradiction detection;
- private/unsafe record exclusion;
- plan-to-ticket linkage;
- subagent handoff resume;
- research-source freshness;
- wikilink-to-edge candidate resolution.

### Stable Metrics Contract

These metrics should remain stable post-release:

| Metric | Meaning |
| --- | --- |
| `retrieval_precision_at_k` | Share of retrieved sources that are truly relevant |
| `retrieval_recall_at_k` | Share of oracle-relevant sources retrieved |
| `context_pack_tokens` | Prompt/context size before model call |
| `irrelevant_token_ratio` | Estimated irrelevant tokens / total context tokens |
| `answer_correctness` | Rule-based score against oracle answer |
| `citation_accuracy` | Whether answer cites required source IDs/paths |
| `privacy_failure_count` | Private/unsafe source leaked or used |
| `staleness_failure_count` | Stale source treated as current |
| `contradiction_handling_score` | Correctly flags conflict instead of flattening history |
| `handoff_resume_score` | New agent/model resumes from scoped handoff |
| `prompt_eval_count` | Ollama prompt tokens from API |
| `eval_count` | Ollama generated tokens from API |
| `total_duration_ms` | End-to-end model request duration |
| `tokens_per_second` | Eval throughput |
| `failure_frontier_scale` | First scale where quality drops below threshold |

### HTML Report Requirements

Output files:

```text
.owledge/exports/benchmark/latest.json
.owledge/exports/benchmark/results.jsonl
.owledge/exports/benchmark/latest.md
.owledge/reports/generated/benchmark/index.html
.owledge/reports/generated/benchmark/charts.svg
```

Required charts:

- Quality by scale: model/profile vs `answer_correctness`.
- Retrieval by scale: precision/recall grouped bars.
- Token efficiency: context tokens vs correctness.
- Context pollution: irrelevant-token ratio by profile.
- Safety failures: privacy/staleness/contradiction counts.
- Speed: total duration and tokens/sec.
- Failure frontier: first failing scale per model/profile.

Chart labeling rules:

- Every chart includes model tag, model digest when available, scale, profile, seed, commit SHA, hardware summary, and generated timestamp.
- Units must be explicit: tokens, ms, tok/s, files, percent.
- Claims must say "on this corpus/seed/hardware/commit".

### Final Pre-Release Todo Overview

| Order | Todo | Goal | DoD |
| ---: | --- | --- | --- |
| 1 | Direct `.owledge/` migration | Brand and root contract become coherent | New installs create `.owledge/`; `OWLEDGE.md` exists; no public `OWLEDGE.md` dependency |
| 2 | Contracts/gates migration | Remove current release blocker | `test-contracts` and `finalization-gates` pass against `.owledge/` |
| 3 | Gitignore/generated-state policy | Keep repo clean and private | Raw sessions/tmp/exports ignored; durable plans/reviews/handoffs tracked |
| 4 | README first-screen rewrite | International first impression | uv-first quickstart, abstract, problem-solution table, 5-minute demo story |
| 5 | Core add-ons/plugins bundled | Make `uvx`/PyPI promise real | Wheel contains core templates/skills/plugins/benchmark starter or docs avoid the claim |
| 6 | Read-only MCP P0 | Agent/harness discoverability and trust | MCP exposes entrypoint, doctor, search, context pack, tasks, reviews; no write tools |
| 7 | Native review layer | Productize `agentic-review` | `.owledge/reviews/` templates include audience/research refs and task conversion |
| 8 | Audience layer | Better product/UX/red-team planning | `.owledge/audiences/` templates and `audience_ids` in plans/reviews/research |
| 9 | Research layer | Support agentic research and market planning | `.owledge/research/` structure with source/finding/synthesis/lane templates |
| 10 | Brainstorm skill/spec | High-quality ideation without memory pollution | Candidate-only brainstorm outputs with promotion boundary |
| 11 | Wikilink audit | Bridge Obsidian navigation and typed edges | Read-only audit reports unresolved/ambiguous links and candidate edges |
| 12 | Benchmark Kit V2 | Prove retrieval/context efficiency with local models | `ci` and `local` modes, stable schema, JSON/MD/HTML/SVG outputs |
| 13 | Release verification | Publish readiness evidence | concept-audit, public-docs, release-trust, launch-readiness, runtime-adapters, quality-ratchet all pass |
| 14 | Final demo artifact | Make the value legible | 5-minute demo script/GIF or report showing forget -> handoff -> resume |

Final pre-release reality check:

- The core story is not "memory" in the abstract. It is: Owledge gives agents a Git-native, reviewable, scoped context layer that keeps local and weaker models useful in large projects.
- The release should avoid claiming full swarm/harness/cloud/RAG maturity before the benchmark and adapters prove it.
- The strongest launch proof is a clean `.owledge/` install, read-only MCP, local benchmark report, and a visual handoff demo.

Resolved decisions, answered in the next section:

1. Should `wikilink-audit` be P0 implementation or P1 documented roadmap?
2. Should Benchmark `local` default run both `gemma4:latest` and `qwen3.5:4b`, or should it ask users to choose one by default to avoid long runs?
3. Should the final demo artifact be HTML report-first, GIF/video-first, or both?

## Final Owner Decisions Before Plan Mode - 2026-06-26

Owner decisions:

1. `wikilink-audit` is P0 because Owledge claims Markdown/Obsidian-first support.
2. Benchmark local mode must scan locally installed Ollama models and let the user select from a supported list.
3. Benchmark models must run one after another, not in parallel, to preserve resources and avoid polluted performance numbers.
4. HTML report is the first demo artifact. GIF/video can follow from the report/demo later.
5. Harness benchmarks should be explicitly added to roadmap.
6. Benchmark Kit V2 should be designed so Ollama cloud/frontier models can use the same runtime path later.
7. `all` mode must run sequentially, not in parallel, and clearly warn about local resource use and possible usage/cost.

### Final Benchmark Execution Rules

- `ci` mode is non-interactive and model-free.
- `local` mode:
  - calls Ollama `/api/tags`;
  - filters installed models against supported profiles;
  - recommends `gemma4:latest` and `qwen3.5:4b` when present;
  - lets the user choose one or more models;
  - runs selected models sequentially;
  - records model name, digest, size, seed, scale, profile, hardware summary, and commit SHA.
- `frontier` mode:
  - remains post-release/opt-in;
  - can use the same Ollama API path when models are exposed through Ollama Cloud;
  - requires explicit usage/cost confirmation.
- `harness` mode:
  - roadmap only for pre-release;
  - tests Claude Code, Codex, OpenCode first, then Cursor and Zed;
  - validates adapter behavior, allowed write lanes, context pollution, and handoff/resume.
- `all` mode:
  - sequential orchestration only;
  - runs `ci`, then selected local models, then opt-in frontier/harness tracks only when explicitly enabled;
  - never parallelizes model inference by default.

### Harness Benchmark Roadmap

Harness benchmarks are now a named roadmap track, separate from Benchmark Kit V2 P0.

| Phase | Harnesses | Goal | DoD |
| --- | --- | --- | --- |
| P1-H1 | Claude Code, Codex, OpenCode | Validate core agent harness behavior | Each harness reads `OWLEDGE.md`, respects `.owledge/`, writes only allowed artifacts, and can resume from a handoff |
| P1-H2 | Claude Code/Codex local-vs-cloud | Compare same Owledge scenario across local Ollama and cloud models | Report separates model failures from harness/plugin failures |
| P2-H3 | Cursor, Zed | Editor-harness coverage | Adapter recipe or plugin path documented and benchmarked |
| P2-H4 | Team/swarm harness scenarios | Multi-agent plan and lane collision tests | Orchestrator/lane protocol holds under concurrent task simulation |

### Pre-Release Plan Completeness Check

The sparring document now covers all material decisions from this session:

- `.owledge/` direct migration and `OWLEDGE.md` replacement for `OWLEDGE.md`.
- Contracts/gates migration and expected score impact.
- README/uvx/uv tool install first-run strategy.
- Core add-on/plugin bundling strategy.
- Read-only MCP as hard P0.
- Brainstorm skill/spec as release scope, runtime later.
- Native `agentic-review` productization under `.owledge/reviews/`.
- Audience profiles for strategic planning, UX, MVP, and Red Team.
- Agentic research layer with sources/findings/syntheses/lanes.
- Subagent lane protocol and orchestrator delta model.
- Branch/worktree conflict mitigation.
- Wikilink preservation plus P0 `wikilink-audit`.
- Benchmark Kit V2 modes, local model matrix, stable metrics, HTML report, sequential execution, and future Ollama Cloud path.
- Harness benchmarks moved to roadmap with Claude Code, Codex, OpenCode first.
- Hermes adapter moved out of pre-release into full-adapter roadmap.
- Final pre-release todo table with order, goal, and DoD.

### Recommended ASAP Execution Flow

1. Foundation migration: `.owledge/`, `OWLEDGE.md`, gitignore policy, template paths.
2. Gates/contracts: make `test-contracts`, `finalization-gates`, runtime adapters, and release trust green.
3. Public surface: README first screen, command reference, install docs, problem-solution table.
4. Runtime trust: read-only MCP P0.
5. Native planning layers: reviews, audiences, research, brainstorm, wikilink-audit.
6. Benchmark Kit V2: deterministic first, local Ollama sequential mode, HTML report.
7. Final verification: concept audit, release gates, local benchmark, HTML demo report.

### Subagent-Friendly Work Split

These tasks can run in parallel with lane ownership:

| Lane | Good Subagent Task | Why It Can Be Parallel |
| --- | --- | --- |
| Migration | Rename/template path inventory and patch plan | Mostly mechanical, clear file ownership |
| Gates | Update tests/contracts/finalization gates | Separate from docs and README |
| Docs | README/command-reference/install rewrite | Can proceed against agreed target commands |
| MCP | Read-only server API/tool contract | Bounded surface, no write semantics |
| Benchmark | Schema/scenario/report design and implementation | Separate module, clear outputs |
| Wikilinks | `wikilink-audit` extraction/resolution logic | Independent read-only feature |
| Reviews/Audiences/Research | Templates and docs | Mostly template work |

Coordination rule:

- Each subagent writes a short lane handoff under `.owledge/workpackages/<wp>/lanes/<agent-id>.md`.
- Only the orchestrator edits the central plan/task list.
- Any issue discovered by a subagent becomes a blocker artifact, not an uncoordinated shared-plan edit.
