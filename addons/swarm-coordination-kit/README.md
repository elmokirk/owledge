# Swarm Coordination Kit

Optional add-on for coordinating multi-agent work through Owledge memory.

## Role Lanes

| Role | Writes |
| --- | --- |
| Orchestrator | plans, work packages, context packs |
| Worker | evidence, handoffs, task-local notes |
| Reviewer | reviews, QA gates, risk reports |
| Curator | promotion proposals, canonical drafts, lessons, patterns |

## Guardrails

- No distributed locking in v1.
- No autonomous conflict resolution.
- No runtime replacement for Codex, Claude Code, Hermes, or custom harnesses.
- Workers do not promote memory.

