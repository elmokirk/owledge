# Review Workflow Finalization Sprint

Date: 2026-05-23  
Status: active  
Scope: finalize reusable red-team, expert-review, scenario-simulation, and review-to-task workflows for the Markdown-first Agent Memory Kit.

## Operating Model

The orchestration agent owns integration, scope control, and final QA. Each implementation task has a worker slice and a QA checker. Workers must use disjoint write scopes and must not revert other edits.

## Task Matrix

| Task | Worker Scope | QA Checker Scope | Definition Of Done | Quality Checks |
| --- | --- | --- | --- | --- |
| T1 Review workflow tooling | `tools/agent_memory_cli.py` | Generated artifact quality, placeholder replacement | CLI can create concrete review artifacts from all reusable templates without overwriting files | Python compile, no unresolved tenant/customer/project placeholders, JSON output includes paths and QA commands |
| T2 Workflow skill and docs | `skills/review-evaluation-workflow/`, plugin mirror, command docs, README references | Skill trigger clarity, workflow completeness, path accuracy | Agents can choose a template, inject personas, collect evidence, score, classify, create tasks, and rerun review | Markdown paths exist, promotion boundary stated, Markdown remains source of truth |
| T3 Contract integration | `tools/agent_memory_cli.py` required files list and release docs | Contract checks include new command/skill/docs | New workflow assets are protected by `test-agent-memory-contracts` | Contract test passes, no stale references |
| T4 End-to-end validation | generated sample review artifact, validation commands | QA reviews generated output and overall release state | A sample review workflow can run locally and produce a valid private draft artifact | `validate-memory`, `test-agent-memory-contracts`, `memory-doctor`, generated artifact review |

## Review Workflow Definition

1. Select the artifact or decision to evaluate.
2. Select the review template:
   - multi-perspective red team
   - expert lens evaluation
   - scenario simulation
   - evaluation persona pack
   - review-to-task plan
3. Inject 3-5 relevant personas when the review requires multiple perspectives.
4. Collect evidence from Markdown paths, memory IDs, command output, hashes, or explicit assumptions.
5. Score all required dimensions from 1-100.
6. Classify the verdict:
   - `block`: below 70 or serious safety/privacy issue
   - `revise`: 70-84
   - `accept`: 85-94
   - `promote-candidate`: 95-100, still requiring owner or curator approval
7. Convert material findings into tasks with owners, write scopes, acceptance criteria, and QA gates.
8. Re-run the relevant review after fixes.

## Shared Quality Bar

| Metric | Target |
| --- | ---: |
| Evidence quality | >= 85 |
| Actionability | >= 85 |
| Coverage | >= 90 |
| Safety / privacy | 100 |
| Context efficiency | >= 80 |
| Reusability | >= 80 |
| Contract health | 100% pass |

## Promotion Boundary

Review workflow artifacts are candidate QA memory. They may guide planning and fixes, but they do not approve canonical memory, shared lessons, RAG export, or customer-facing reports by themselves.
