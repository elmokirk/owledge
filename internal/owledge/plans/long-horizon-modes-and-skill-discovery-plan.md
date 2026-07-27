---
memory_id: "mem:owledge:global:owledge:plan:long-horizon-modes-and-skill-discovery"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "project_context"
artifact_type: "plan"
status: "reviewed"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge long-horizon modes and reliable agent skill discovery"
summary: "Implementation plan for version-steering and minimum-MVP sparring modes, idea-to-roadmap routing, and reliable project/plugin skill discovery across agent harnesses."
concept_tags: ["long-horizon-delivery", "mvp-sparring", "skill-discovery", "incremental-shipping"]
stack_tags: ["python", "markdown", "yaml", "codex", "claude-code"]
problem_patterns: ["endless-planning", "scope-creep", "undiscovered-project-skill", "idea-loss"]
architecture_patterns: ["mode-driven-skill", "compatibility-facade", "discovery-mirror", "human-in-the-loop-gate"]
failure_modes: ["plan-without-cutline", "roadmap-idea-dropped", "root-skill-not-loaded", "plugin-mirror-drift"]
reusable_lessons:
  - "Project-local skill source and harness-discoverable skill installation are separate contracts."
  - "Planning should stop when the smallest useful increment is decision-complete, not when no more ideas exist."
confidence: 0.96
review_status: "reviewed"
sanitization_status: "not_required"
created_at: "2026-07-27T00:00:00Z"
updated_at: "2026-07-27T14:21:00Z"
source_hash: ""
edges:
  - type: "implements"
    target: "mem:owledge:global:owledge:decision:v0.7.1-v1-version-reflection-contract-2026-07-27"
    confidence: 1.0
    reason: "Turns the accepted version-reflection behavior into a reusable Owledge skill mode."
  - type: "relates_to"
    target: "mem:owledge:global:owledge:plan:v1-autonomous-delivery"
    confidence: 0.95
    reason: "Maps the immediate skill/discovery MVP to v0.7.1 and later harness hooks to v0.8.1."
---

# Long-Horizon Modes and Skill Discovery Plan

## Outcome

Initialized Owledge projects expose one reliable long-horizon planning and
delivery skill with explicit modes. Planning conversations can intentionally
enter a bounded MVP sparring mode, while release work can enter the accepted
version-steering mode. Codex discovers project skills from `.agents/skills`;
plugin-capable harnesses discover the mirrored plugin skills; generic agents
receive explicit routing from `AGENTS.md`.

## Current-State Evaluation

Already implemented:

- `owledge-planning-layer` requires an MVP cutline, non-goals, evidence, gates,
  handoffs, and idea routing for scope expansion.
- `owledge-brainstorm` keeps brainstorm output candidate-only.
- `pi-agent-workspace-quality` inspects ideas before a new plan.
- `docs/ideation-workflow.md` defines idea storage, matching signals, and
  promotion paths.
- the v1 control plane now has mandatory per-version findings, decisions,
  next-plan reflection, and owner alignment.
- `init-project` copies Owledge skills into a project-root `skills/` directory.

Missing or unreliable:

- no single mode contract joins MVP sparring, version steering, execution,
  gate review, and recovery;
- no hard planning stop prevents repeated option expansion after the MVP
  cutline is decision-complete;
- idea inspection is distributed across skills and is not a required pre-plan
  protocol for every harness;
- a project-root `skills/` bundle is not automatically discoverable by Codex;
- `.owledge/skills` is not a supported Codex discovery path and must not be
  presented as one;
- the Cowork plugin does not mirror the planning/brainstorm skills;
- doctor and generated-kit gates do not prove skill discovery or mirror parity.

Current Codex source evidence, retrieved 2026-07-27: repository skills are
loaded from `.agents/skills`, user skills from `$HOME/.agents/skills` and the
legacy `$CODEX_HOME/skills`, while plugin manifests load declared or default
plugin `skills/` roots. Source:
`https://github.com/openai/codex/blob/main/codex-rs/core-skills/src/loader.rs`.

## Product Decisions

### One canonical skill

Create `owledge-long-horizon-delivery` with these modes:

| Mode | Purpose | Stop condition |
| --- | --- | --- |
| `mvp-sparring` | Reduce a broad request to one smallest useful increment. | Goal, user, success signal, cutline, non-goals, first task, and roadmap routing are explicit. |
| `version-steering` | Execute the post-version reflection contract. | Findings, decisions, questions, next-plan reflection, and owner decision are complete. |
| `ticket-execution` | Execute one ready bounded ticket. | Ticket evidence and QA handoff are complete. |
| `gate-review` | Independently verify a promotion gate. | Passed or failed gate report exists; no silent waiver. |
| `recovery` | Resume from durable state. | Exact active ticket/checkpoint and next command are restored. |

`owledge-planning-layer` remains a compatibility facade and routes multi-step
planning to `mvp-sparring` by default. `owledge-brainstorm` remains optional
divergent ideation; it must return to MVP sparring before implementation.

### Planning stop rule

MVP sparring asks only questions whose answers can change the current cutline.
After the cutline is decision-complete, stop generating alternatives. Route
useful non-MVP material to:

- `.owledge/ideas/` for unresolved concepts;
- `ROADMAP.md` or an existing release backlog for accepted future scope;
- `.owledge/decisions/` for architecture decisions;
- explicit rejection/defer records when no future value is established.

No captured idea becomes current scope without owner approval.

### Discovery contract

- Keep project-root `skills/` as the installed Owledge source/vendor bundle for
  generic agents and upgrades.
- Materialize an additive mirror under `.agents/skills/` during
  `init-project` and project-kit builds for Codex repository discovery.
- Keep plugin-local `plugins/owledge-cowork/skills/` as the plugin discovery
  root and mirror the long-horizon, planning, and brainstorm skills there.
- Do not use `.owledge/skills` as an agent discovery location.
- Track installed mirrors in `kit-manifest.json`; upgrades remain
  preview-first and do not overwrite user-edited skill files silently.
- Add doctor and test coverage for missing/disagreeing discovery mirrors.

## MVP Cutline

In scope now:

- canonical long-horizon skill and mode reference;
- bounded MVP sparring and version-steering contracts;
- routing from existing planning/brainstorm skills;
- Codex `.agents/skills` materialization in both initialization paths;
- plugin mirrors for planning-related skills;
- AGENTS/CLAUDE and install documentation truth;
- doctor, manifest, packaging, and regression tests.

Out of scope now:

- automatic semantic idea selection;
- background hooks that modify plans;
- automatic roadmap promotion;
- global installation into a user's home directory;
- marketplace installation/certification;
- write-enabled MCP;
- harness-specific pre-prompt injection.

Later roadmap mapping:

- deterministic pre-plan idea/concept capsule: `OW-080-05`;
- WorkContract cutline/roadmap fields: `OW-080-03`;
- harness capability and pre-plan hook contract: `OW-081-01` through
  `OW-081-05`, plus `OW-081-13`;
- semantic idea linking/promotion: `OW-090-02` and `OW-090-04`.

## Implementation Stages

### Stage 1 - Mode and planning contracts

Create the new skill, mode reference, UI metadata, compatibility routing, and
MVP stop rule.

QA gate:

```bash
python -m pytest tests/unit/test_skill_discovery_and_modes.py -q
python tools/owledge.py test standalone-skills --project-root .
```

- [x] implementation done
- [x] QA checks done
- [x] quick review done

### Stage 2 - Discoverable installation

Install root skills and `.agents/skills` mirrors, track both in the manifest,
and include the same shape in generated project kits.

QA gate:

```bash
python -m pytest tests/unit/test_skill_discovery_and_modes.py tests/unit/test_upgrade.py -q
python tools/owledge.py test generated-kit-surface --project-root .
```

- [x] implementation done
- [x] QA checks done
- [x] quick review done

### Stage 3 - Plugin and harness routing

Add planning-related plugin mirrors, update agent templates and docs, and make
current/later harness boundaries explicit.

QA gate:

```bash
python tools/owledge.py test runtime-adapters --project-root .
python tools/owledge.py test release-trust --project-root .
```

- [x] implementation done
- [x] QA checks done
- [x] quick review done

### Stage 4 - Cumulative validation and handoff

Run plan validation, targeted tests, finalization gates, record findings, and
leave the next exact v0.7.1 action.

QA gate:

```bash
python tools/validate_v1_delivery_plan.py
python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports
```

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Stage Reflection Log

### Stage 1 Reflection

- Keep: one canonical mode-driven skill and the existing planning skill as a
  compatibility facade.
- Finding: unconstrained brainstorming can still expand scope unless it
  explicitly returns to the MVP cutline.
- Decision: default broad planning to `mvp-sparring`; stop with
  `lock`, `adjust`, or `defer`.
- Next-plan effect: first-class cutline/disposition fields remain mapped to
  `OW-080-03`.

### Stage 2 Reflection

- Keep: additive discovery mirrors rather than moving the canonical source.
- Finding: root `skills/` and `.owledge/skills/` are not reliable Codex
  repository discovery locations.
- Decision: initialize `.agents/skills/`, track it in the manifest, protect
  edits during upgrades, and diagnose missing/drifting copies.
- Next-plan effect: exact harness discovery/conformance remains part of
  `OW-071-12` and `OW-081-01` through `OW-081-05`.

### Stage 3 Reflection

- Keep: plugin-local declared skill roots and standalone distribution.
- Finding: skill-guided pre-plan inspection works now, but no portable
  lifecycle hook guarantees it across harnesses.
- Decision: capture the hook as an idea and map read-only capsule work to
  `OW-080-05`, adapter contracts to `OW-081-01` through `OW-081-05`, and
  harness hooks to `OW-081-13`.
- Next-plan effect: no background hook or automatic promotion enters the
  current MVP.

### Stage 4 Reflection

- Evidence: skill validation passed; 24 targeted regression/upgrade tests
  passed; delivery-plan validation passed with 61 tickets, 25 gates, and 34
  execution waves; all 35 finalization gates passed with every quality-ratchet
  dimension at 100.
- Finding: the bare system Python lacks development-only PyYAML/pytest.
- Decision: preserve the standard-library-only runtime and use an isolated
  development QA environment.
- Next exact action: keep the v0.7.1 train unchanged and start `OW-071-01`
  only after Definition-of-Ready, scoped-worktree, and base-SHA checks.

## Definition of Done

- Fresh initialized and generated-kit projects contain matching
  `skills/<name>` and `.agents/skills/<name>` files for every host skill.
- Codex-oriented docs identify `.agents/skills` and plugin `skills/` as
  discovery roots and explicitly reject `.owledge/skills` as automatic
  discovery.
- The new skill exposes the five named modes and defaults planning requests to
  bounded `mvp-sparring`.
- Useful out-of-cutline concepts are routed, never silently discarded or added
  to current scope.
- Existing project skill edits remain protected during upgrade.
- Targeted and cumulative gates are green.

## Resume State

This workpackage is complete. Resume the main delivery train at `OW-071-01`.
Do not implement automatic harness hooks before the mapped v0.8/v0.8.1
contracts and owner-approved version boundaries.
