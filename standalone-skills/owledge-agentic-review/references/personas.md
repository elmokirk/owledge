# Persona Selection

Use 3-5 personas for standard reviews. Add specialized personas only when the artifact needs them.

| Persona | Use When | Optimizes For | Distrusts | Required Evidence | Success Metric |
| --- | --- | --- | --- | --- | --- |
| Senior AI Agent Engineer | Agent harnesses, memory systems, delegation, RAG pipelines, autonomous engineering | Durable coordination, low repeated context cost, clean handoffs | Agents reread everything, weak ownership, hidden prompt coupling, unsafe promotion | Plans, handoffs, runtime constraints, source paths, command results | Agents can resume and coordinate with correct context |
| Scalability / Systems Reviewer | Architecture, long-running repos, multi-agent plans, data growth | Boundaries, performance, maintainability, clear ownership | Index bloat, race conditions, shared mutable state, unclear write lanes | File structure, scale assumptions, bottlenecks, test data | Design remains usable under expected growth |
| Security / Privacy Reviewer | Runtime capture, logs, exports, customer data, secrets, compliance | Least privilege, safe defaults, privacy boundaries | Secret leakage, raw logs in shared corpora, overbroad access | Data classes, ignored files, logs, export rules, auth boundaries | No sensitive or unreviewed data escapes intended scope |
| UX / DX Adopter | README, onboarding, CLI, install path, docs, first-run workflow | Clear mental model and low adoption friction | Hidden prerequisites, confusing commands, conceptual overload | Quickstart, examples, screenshots, command output | New user succeeds without private knowledge |
| Product / Scope Strategist | Roadmap, MVP, feature plan, public positioning | Tight scope, measurable value, anti-overengineering | Monolith drift, vague user value, unprioritized features | Goals, target users, acceptance criteria, usage scenarios | Plan maps to a clear outcome and cutoff |
| QA Gate Owner | Release readiness, test plans, launch gates, validation | Deterministic checks and reproducible evidence | Vague acceptance, no commands, missing negative tests | Test output, CI status, repro steps, fixtures | Required gates pass or blockers are explicit |
| Compliance / Audit Reviewer | Regulated workflows, AI Act traceability, enterprise records | Traceability, retention, review status, approval boundaries | Missing provenance, unverifiable decisions, unapproved promotion | Decision trace, evidence, reviewer identity, timestamps | Decisions are auditable and source-linked |

Persona requirements:

- Every persona must state what it optimizes for, what it distrusts, required evidence, success metric, score, confidence, and findings.
- Personas may not invent facts. Missing evidence becomes a finding or assumption.
- Use project-local `REVIEW.md` personas before this default library.
