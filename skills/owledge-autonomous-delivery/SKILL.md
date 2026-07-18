---
name: owledge-autonomous-delivery
description: Assess and propose Owledge's optional consent-first multi-agent delivery workflow for a ticket, refactor, merge, migration, MCP change, or release. Use when a user asks to delegate work, use subagents, run parallel lanes, plan a safe merge, or execute a constrained local-model task.
---

# Owledge Autonomous Delivery

Use this skill to recommend a delivery workflow. Do not begin execution, create a worktree, spawn an agent, write files, merge, or invoke an external runtime until the user has approved the displayed plan.

## Hard Rule

`subagent: true` means delegation is eligible only. It never authorizes spawning an agent, creating a worktree, writing files, merging code, or external runtime calls. Record user approval before every such action.

## Workflow

1. Read the local `AGENTS.md`, `OWLEDGE.md`, control-plane policy, backlog, active ticket, and current gate. Respect stricter host-project instructions.
2. Classify the ticket:
   - **Small:** one outcome, at most three implementation files, and no public contract, migration, security/privacy, MCP, release, cross-project, or concurrent-write impact. Recommend one agent and no delivery profile.
   - **Medium:** more than three files or useful independent QA, without a high-risk boundary. Propose one Worker plus independent QA after phase approval.
   - **High-risk:** refactor, merge, migration, public API/schema, MCP, security/privacy, release, cross-project, or concurrent-write work. Propose a dry-run plan and require per-ticket approval; add isolated QA and a Red Team.
3. Present a compact risk brief before execution: ticket, dependencies, model profiles, write scopes, worktrees/branches, commands, network/cost exposure, evidence retention, rollback target, and the safe default if declined.
4. On approval, create at most one write-capable Worker lane per ticket. Give QA an independent context. Give Red Team an adversarial brief, never the Worker's hidden reasoning or unreviewed result.
5. Require path claims, isolated worktrees, a merge manifest, positive and negative QA evidence, and an integration-owner review before any merge.
6. Stop at every version alignment gate and present collected questions to the user.

## Model Profiles

- `frontier_orchestrator`: dependency decisions, architecture, release coordination.
- `balanced_worker`: bounded implementation and documentation.
- `independent_qa`: separate verification context.
- `adversarial_reviewer`: security, privacy, MCP, migration, and release challenge.
- `edge_small`: deterministic, bounded tasks only; never architecture, merge authority, security sign-off, or cross-project coordination.

## Edge / Local Model Constraints

Give an edge-small model only a task capsule: one objective, allowed paths, acceptance criteria, dependency summaries, required commands, and a strict output format. Enforce a context budget and progressive disclosure. Require deterministic validation; clearly mark unsupported work instead of letting the model improvise.

## Required Output Before Approval

Return the ticket classification, recommended lanes, dependency links, model profiles, exact approval required, risks, Git plan, QA/Red-Team plan, and the safe single-agent fallback. Do not present a dispatch as already running.