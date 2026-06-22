# Integration Decision Guide

Owledge is minimal by default. Start with the smallest integration that solves
the current problem, then add files or add-ons only when there is a concrete
reason.

## Default Rule

Use this order:

1. Principles-only / Skills
2. Project-local kit
3. Knowledgebase module
4. Runtime adapter
5. Optional add-ons

The first working option is usually the right option.

## Choose A Path

| Path | Use When | What It Adds | Avoid When |
| --- | --- | --- | --- |
| Principles-only / Skills | One user or one agent needs the Owledge memory rules inside an existing workflow | Instructions and skills only | You need local validation, indexes, or durable project artifacts |
| Project-local kit | A project needs durable plans, evidence, handoffs, indexes, and validation in-repo | `PROJECT_CONTEXT.md`, `agent-memory/`, local Python tools, optional skills | The team only wants a portable operating rule |
| Knowledgebase module | An existing Markdown or Obsidian-style vault should be scanned without migration | An additive Owledge-owned module or mapped indexes | You want Owledge to own or rewrite the vault taxonomy |
| Runtime adapter | A runtime should capture private session events, handoffs, or command wrappers | Optional hooks, plugin files, and runtime contracts | Skills and manual handoffs are enough |
| Add-ons | A team needs proof, demo, trust review, conformance, TypeScript eval, or benchmark charts | Optional docs, fixtures, generated-view tools, and scorecards | The add-on would become a default dependency |

## Skillset-Only Minimal Path

For the smallest possible setup, use only:

- `skills/agent-memory-principles`
- `AGENTS.md` or the equivalent runtime instruction file
- the rule that Markdown artifacts are canonical and generated views are
  disposable

This path is enough when an agent can create evidence-linked plans, handoffs,
and reviews in the host system without local tooling.

## Add-On Rule

Add-ons must be optional and additive. They can provide proof, QA, charts,
runtime contracts, or distribution assets, but they must not:

- replace Markdown as canonical memory
- require a hosted service
- require a vector database
- auto-promote memory
- change the default project setup

## Current Add-Ons

| Add-on | Purpose |
| --- | --- |
| `launch-demo-kit` | Five-minute proof with evidence, handoff, and static report |
| `trust-readiness-kit` | Team evaluation, data-flow, threat-model, and security-readiness docs |
| `runtime-conformance-kit` | Read-only runtime contract fixtures |
| `pi-proof-kit` | Synthetic observe, detect, red-team, promote, and measure loop |
| `ts-adapter-kit` | Optional Node/TypeScript CI validation of the Markdown contract |
| `pilot-benchmark-kit` | Optional pilot metrics, benchmark summaries, and static chart views |

## Decision Checklist

- If a user asks "how do I try the idea?", use principles-only or the
  five-minute demo.
- If a repo needs durable local state, use the project-local kit.
- If a vault already exists, use the knowledgebase module.
- If runtime events matter, add a runtime adapter.
- If a team needs proof or release evidence, install only the matching add-on.
