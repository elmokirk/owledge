# Team And Long-Running Project Guide

Use this guide for projects that already have months of history or multiple
developers and agents.

## Operating Rules

- Keep existing project and vault structure intact.
- Use `agent-memory-map.json` when the team already has folder conventions.
- Require handoffs at the end of agent sessions and developer work blocks.
- Use reviews before promotion to canonical/shared memory.
- Run stale, conflict, sensitive-data, and finalization gates before releases.

## Suggested Team Workflow

1. Orchestrator creates or updates an MVP plan with evidence paths.
2. Developers or worker agents execute bounded tasks.
3. Each worker writes evidence and a handoff.
4. Reviewer records quality, risks, and missing evidence.
5. Curator proposes promotion only for reviewed and sanitized records.

## What Scales

- Project plans stay small and source-backed.
- Generated indexes are disposable views.
- Context packs and handoffs replace large chat-history reloads.
- Shared exports include only reviewed and sanitized records.

## What Is Still Later-Phase

- RBAC.
- Central hub sync.
- Retention enforcement.
- Dashboard-driven promotion workflows.
