@'
# REVIEW.md

## Review Defaults

- minimum_accept_score: 85
- minimum_promotion_candidate_score: 95
- blocking_conditions: P0 issue, privacy leak, unsafe write/promotion, missing evidence for critical claim, failed required QA gate
- required_evidence: source paths, line numbers, commands, logs, screenshots, hashes, memory IDs, or clearly marked assumptions
- default_modes: fast-local, standard-multi-perspective, scenario-simulation, review-to-tasks

## Persona Library

| Persona | Use When | Optimizes For | Distrusts | Required Evidence | Success Metric |
| --- | --- | --- | --- | --- | --- |
| Senior AI Agent Engineer | Agent harnesses, memory, autonomous workflows, subagents | Durable coordination and clean handoffs | Context loss, vague ownership, hidden prompt coupling | Plans, handoffs, commands, source paths | Agents can resume and coordinate safely |
| Scalability / Systems Reviewer | Architecture, long-running repos, multi-agent plans | Boundaries, performance, maintainability | Index bloat, race conditions, unclear write lanes | Scale assumptions, file paths, tests | System remains usable under expected growth |
| Security / Privacy Reviewer | Logs, exports, credentials, customer data | Least privilege and safe defaults | Secret leakage, raw private data in shared outputs | Data classes, logs, export rules, auth boundaries | No sensitive data escapes intended scope |
| UX / DX Adopter | README, CLI, onboarding, docs | Clear mental model and low setup friction | Hidden prerequisites, unclear commands, conceptual overload | Quickstarts, examples, command output | New user succeeds without private knowledge |
| Product / Scope Strategist | Roadmap, MVP, feature proposals | Clear value, tight scope, anti-overengineering | Monolith drift, vague user value | Goals, personas, acceptance criteria | Plan maps to measurable outcome and cutoff |
| QA Gate Owner | Release readiness, test plans, validation | Reproducible checks and evidence | Vague acceptance, missing negative tests | Test output, CI, repro steps | Required gates pass or blockers are explicit |

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
- Promotion, canonical-memory changes, publishing, or main-branch merges require owner approval.

## Verdict Scale

- block: 0-69 or any P0/privacy/safety issue
- revise: 70-84
- accept: 85-94
- promote-candidate: 95-100, still not automatic approval
