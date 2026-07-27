# Owledge Standalone Skills

Use these skills individually when you want Owledge-style durable work,
review, brainstorm, or planning behavior without adopting the full project kit.

## Install

Copy one skill folder into the skill directory used by your agent runtime.

```text
standalone-skills/
|-- owledge-contract/
|-- owledge-agentic-review/
|-- owledge-blindspot-audit/
|-- owledge-brainstorm/
|-- owledge-long-horizon-delivery/
`-- owledge-planning-layer/
```

Each folder is self-contained unless its `SKILL.md` explicitly says an Owledge
CLI command is optional.

## Skills

| Skill | Use | Requires full Owledge kit? |
| --- | --- | --- |
| `owledge-contract` | Apply the compact long-horizon, evidence, resume, handoff, and knowledge-promotion contract. | No. No Owledge runtime or CLI is required. |
| `owledge-blindspot-audit` | Stress-test concepts, release plans, docs, and product foundations. | No. Owledge CLI is optional for mechanical checks. |
| `owledge-agentic-review` | Evidence-linked red-team, expert review, persona review, and review-to-task workflows. | No. |
| `owledge-brainstorm` | Candidate-only strategy, architecture, product, release, and research brainstorming. | No. |
| `owledge-long-horizon-delivery` | Bound MVP sparring, version steering, ticket execution, gate review, and recovery with durable idea routing. | No, but it can persist richer state when `.owledge/` exists. |
| `owledge-planning-layer` | Add Owledge planning discipline to an existing project. | No, but it works best when `.owledge/` exists. |

## Runtime Notes

- Codex: copy the selected folder to `.agents/skills/<skill-name>/` in the
  repository or `$HOME/.agents/skills/<skill-name>/` for a user install, then
  start a new session. `.owledge/skills/` is not an automatic discovery path.
- Claude Code: copy the selected folder into the local skills
  directory supported by the runtime.
- OpenCode: copy the selected folder into its configured skill or instruction
  directory; the v1 support contract will pin and test the exact destination.
- Generic agents: paste the `SKILL.md` into the agent instruction layer or use
  it as a local review checklist.

Standalone skills do not mutate canonical project memory unless the user asks
for persistence and the target runtime permits file edits.
