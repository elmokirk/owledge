---
memory_id: "mem:TENANT_ID:CUSTOMER_ID:PROJECT_ID:qa:evaluation-persona-pack-SLUG"
tenant_id: "TENANT_ID"
customer_id: "CUSTOMER_ID"
project_id: "PROJECT_ID"
doc_type: "qa"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "Evaluation Persona Pack"
summary: "Reusable persona pack for dynamically injecting review perspectives into red-team, expert evaluation, and scenario simulation templates."
concept_tags:
  - "persona-pack"
  - "evaluation"
  - "red-team"
stack_tags: []
problem_patterns: []
architecture_patterns: []
failure_modes: []
reusable_lessons: []
confidence: 0.7
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "YYYY-MM-DDT00:00:00Z"
updated_at: "YYYY-MM-DDT00:00:00Z"
source_hash: ""
recommended_for:
  - "multi-perspective-red-team-review-template.md"
  - "expert-lens-evaluation-template.md"
  - "scenario-simulation-evaluation-template.md"
edges: []
---

# Evaluation Persona Pack

## How To Use

Pick 3-5 personas that match the artifact under review. Each persona must define what it optimizes for, what it distrusts, and which metric proves success.

## Default Persona Library

| Persona | Use When | Optimizes For | Hunts For | Success Metric |
| --- | --- | --- | --- | --- |
| Senior AI Agent Engineer | Agent harnesses, memory systems, delegation, RAG pipelines | Durable coordination and low repeated context cost | Agents reread everything, weak handoffs, unsafe promotion | Agents can resume with correct context and evidence |
| RAG / GraphRAG Engineer | Retrieval, LightRAG, vector DB, graph exports | Stable IDs, good metadata, source-grounded answers | Raw logs in corpus, unstable chunks, weak edges | Retrieval precision >= 85 and all answers cite sources |
| Scalability Engineer | 50-100+ agents, multi-project hubs, long-running vaults | Boundaries, growth rules, performance, maintainability | Index bloat, race conditions, unclear ownership | System remains usable after sustained writes |
| Enterprise Readiness Reviewer | Agency/team usage, client work, compliance-sensitive contexts | Governance, privacy, audit, data classification | Private leakage, missing retention, unclear roles | No unsafe shared export or unreviewed promotion |
| UX / DX Midlevel Developer | First install, daily use, repo handoff | Clear mental model and low setup friction | Too many scripts, hidden assumptions, bad docs | New user succeeds from README and examples |
| Product Strategist | Ideas, positioning, roadmap, business fit | Clear scope, prioritization, customer value | Overbuilding, weak ICP, roadmap drift | Plan maps to measurable business outcomes |
| Design Systems Reviewer | HTML reports, UI templates, design tokens | Consistent tokens, accessible visual decisions | One-off visuals, untraceable design choices | DESIGN.md contains reusable decisions |
| Security Reviewer | Runtime capture, secrets, plugins, exports | Least privilege and safe defaults | Secret capture, overbroad access, unsafe logs | No secrets or sensitive records in shared outputs |
| QA Gate Owner | Release readiness, acceptance gates, validation | Deterministic checks and reproducible evidence | Vague acceptance, no commands, missing reports | Required gates pass with linked evidence |

## Persona Injection Block

Copy this block into a review template for each selected persona.

```markdown
### Persona: PERSONA_NAME

- Role:
- Optimizes for:
- Distrusts:
- Required evidence:
- Success metric:
- Confidence threshold:

| Finding | Severity | Evidence | Impact | Recommendation |
| --- | --- | --- | --- | --- |
| | P0/P1/P2/P3 | | | |

Score: 0/100
Confidence: 0.0
```

## Persona Selection Rules

- Use at least one systems/scalability lens for architecture or agent orchestration work.
- Use at least one UX/DX lens for install, plugin, or onboarding work.
- Use at least one RAG/memory lens for retrieval, LightRAG, GraphRAG, or knowledge-layer work.
- Use a security/compliance lens when data classes, runtime capture, shared exports, or customer data are involved.
- Do not let personas invent facts. Every claim needs a source path, memory ID, command result, hash, or clearly marked assumption.
