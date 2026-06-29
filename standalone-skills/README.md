# Owledge Standalone Skills

Use these skills individually when you want Owledge-style review, brainstorm,
or planning behavior without adopting the full project kit.

## Install

Copy one skill folder into the skill directory used by your agent runtime.

```text
standalone-skills/
|-- owledge-agentic-review/
|-- owledge-blindspot-audit/
|-- owledge-brainstorm/
`-- owledge-planning-layer/
```

Each folder is self-contained unless its `SKILL.md` explicitly says an Owledge
CLI command is optional.

## Skills

| Skill | Use | Requires full Owledge kit? |
| --- | --- | --- |
| `owledge-blindspot-audit` | Stress-test concepts, release plans, docs, and product foundations. | No. Owledge CLI is optional for mechanical checks. |
| `owledge-agentic-review` | Evidence-linked red-team, expert review, persona review, and review-to-task workflows. | No. |
| `owledge-brainstorm` | Candidate-only strategy, architecture, product, release, and research brainstorming. | No. |
| `owledge-planning-layer` | Add Owledge planning discipline to an existing project. | No, but it works best when `.owledge/` exists. |

## Runtime Notes

- Codex-style runtimes: copy the selected folder into the configured skills
  directory and start a new session.
- Claude-style runtimes: copy the selected folder into the local skills
  directory supported by the runtime.
- Generic agents: paste the `SKILL.md` into the agent instruction layer or use
  it as a local review checklist.

Standalone skills do not mutate canonical project memory unless the user asks
for persistence and the target runtime permits file edits.

