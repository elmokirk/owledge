# REVIEW.md

Project-local review policy for Owledge and for agents using the `agentic-review` skill.

This file is a portable convention, not a runtime dependency. It defines how agents should red-team plans, docs, add-ons, memory changes, releases, and multi-agent work in this repo. If another project has its own review policy, adapt these roles and thresholds there.

## Review Defaults

- minimum_accept_score: 85
- minimum_promotion_candidate_score: 95
- blocking_conditions: P0 issue, privacy leak, unsafe promotion, missing evidence for a critical claim, failed required QA gate, unapproved canonical/shared-memory change
- required_evidence: source paths, line numbers, commands, logs, screenshots, hashes, memory IDs, or clearly marked assumptions
- default_modes: fast-local, standard-multi-perspective, scenario-simulation, review-to-tasks

## Persona Library

| Persona | Use When | Optimizes For | Distrusts | Required Evidence | Success Metric |
| --- | --- | --- | --- | --- | --- |
| Senior AI Agent Engineer | Agent harnesses, runtime adapters, planning layers, subagents | Durable coordination, low repeated context cost, clean handoffs | Agents reread everything, weak ownership, prompt-only memory | Plans, handoffs, source paths, command results | Agents can resume with correct scoped context |
| Scalability / Systems Reviewer | Long-running vaults, multi-project hubs, indexes, swarms | Boundaries, growth rules, performance, maintainability | Index bloat, race conditions, unclear write lanes | Scale assumptions, file paths, benchmarks, test output | System remains usable under expected growth |
| Security / Privacy Reviewer | Runtime capture, exports, shared views, customer data | Least privilege, safe defaults, private raw logs | Secret leakage, raw private data in shared outputs, unsafe promotion | Data classes, ignore rules, export policy, scan results | No sensitive or unreviewed data escapes intended scope |
| UX / DX Adopter | README, quickstart, install paths, public docs | Clear mental model and low adoption friction | Hidden prerequisites, vague commands, conceptual overload | Quickstarts, examples, command output, docs paths | New user succeeds without private project knowledge |
| Product / Scope Strategist | Roadmap, add-ons, MVP scope, positioning | Clear value, tight scope, anti-overengineering | Monolith drift, vague user value, feature sprawl | Goals, critique records, acceptance criteria | Plan maps to measurable outcome and cutoff |
| QA Gate Owner | Release readiness, launch gates, benchmark claims | Reproducible checks and evidence-backed claims | Vague acceptance, hardcoded results, missing negative tests | Test output, generated data, repro commands | Required gates pass or blockers are explicit |
| Compliance / Audit Reviewer | Decision traces, AI-assisted development records, shared exports | Traceability, retention, review status, approval boundaries | Missing provenance, unverifiable decisions, unapproved publication | Decision trace, evidence links, timestamps, reviewer notes | Decisions are auditable and source-linked |

## Agentic Review Protocol

| Role | Responsibility | Write Access | Output |
| --- | --- | --- | --- |
| Working Agent | Implements or plans work | Normal project scope | Change summary and evidence |
| Review Orchestrator | Spawns or coordinates reviews | Review artifacts only | Final synthesis |
| Persona Reviewer | Reviews one lens | Read-only by default | Findings and score |
| Integrator | Converts accepted findings into tasks | Explicitly scoped | Task plan |

## Subagent / Thread Rules

- Review agents are read-only unless the user explicitly asks for fixes.
- Each spawned reviewer gets one perspective and one artifact scope.
- Reviewers must cite file paths, commands, hashes, screenshots, memory IDs, or marked assumptions.
- The orchestrator synthesizes; reviewers do not overwrite each other.
- Promotion, canonical-memory changes, shared exports, publishing, or main-branch merges require owner approval.
- Use at most one follow-up round for contradictions, missing evidence, unclear severity, or omitted required perspective.

## Verdict Scale

- block: 0-69 or any P0/privacy/safety issue
- revise: 70-84
- accept: 85-94
- promote-candidate: 95-100, still not automatic approval

## Owledge Gates

When available, run the smallest relevant gate set for the review:

```bash
python tools/agent_memory_cli.py --project-root . doctor --mode kit
python tools/agent_memory_cli.py --project-root . validate-memory --strict
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py test launch-readiness --project-root .
python tools/owledge.py test quality-ratchet --project-root .
```

Benchmark, decision-trace, and positioning claims must cite generated JSON, Markdown tables, command output, or reviewed records. Do not publish global token/cost or quality claims from one scenario.
