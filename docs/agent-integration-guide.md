# Agent Integration Guide: Drop-In KB Module

Use this guide when a user wants an agent to add Agent Memory planning support
to an existing Markdown knowledgebase, Obsidian vault, or LLM wiki.

## Copy-Paste Prompt For Agents

```text
Use this repo as an Agent Memory and project planning module:
<repo-url>

Integrate it additively into my existing Markdown knowledgebase:
<path-to-knowledgebase>

Rules:
- Do not modify existing knowledgebase files.
- Do not rewrite or convert existing [[Wiki Links]].
- Do not set OS environment variables.
- Do not require a global install.
- Use agent-memory-map.json if present; otherwise create only a small local module structure.
- After installation, produce a short status report and one example project plan.
```

## What The Agent Should Do

1. Read or clone the Owledge repo.
2. Inspect the target knowledgebase root.
3. If `agent-memory-map.json` exists, validate it and use its mapped folders.
4. Run the local drop-in builder from the kit repo:

```bash
python tools/owledge.py add-kb-module --knowledgebase-root /path/to/knowledgebase --include-cli
```

If the user provides a map:

```bash
python tools/owledge.py add-kb-module --knowledgebase-root /path/to/knowledgebase --map-file agent-memory-map.json
```

5. Confirm that the module was created under:

```text
agent-memory-module/
```

or, when mapped mode is active, confirm writes went only to the mapped `plans`
and `indexes` folders. In mapped mode the local start file is written to the
mapped `indexes` folder as `AGENT_MEMORY_MODULE.md`.

6. Read:

```text
agent-memory-module/AGENT_MEMORY_MODULE.md
```

or, in mapped mode:

```text
<mapped-indexes-folder>/AGENT_MEMORY_MODULE.md
```

7. Use the generated index for source discovery:

```text
agent-memory-module/agent-memory/indexes/kb-scan.jsonl
```

or, in mapped mode:

```text
<mapped-indexes-folder>/kb-scan.jsonl
```

8. Write new project plans, evidence, reviews, and handoffs only inside:

```text
agent-memory-module/agent-memory/
```

or the validated mapped folders.

## Default Install Shape

```text
agent-memory-module/
|-- AGENT_MEMORY_MODULE.md
|-- agent-memory/
|   |-- plans/
|   |-- handoffs/
|   |-- evidence/
|   |-- reviews/
|   `-- indexes/
`-- tools/
    `-- agent_memory_cli.py    optional with --include-cli
```

The default module directory avoids collisions with existing `agent-memory/`
folders or custom vault taxonomies. Use `--layout flat` only when the user
explicitly wants the module files at the knowledgebase root.

In mapped mode no root-level `AGENT_MEMORY_MODULE.md` is created. The start file,
scan index, and status file stay under the mapped `indexes` directory.

## Optional Principles Mapping

Use `agent-memory-map.json` when the user wants to keep an existing vault
taxonomy:

```json
{
  "ideas": "01_Inbox/Ideas",
  "plans": "20_Projects/Plans",
  "evidence": "30_Research/Evidence",
  "handoffs": "40_Agent-Handoffs",
  "reviews": "50_Reviews",
  "indexes": ".agent-memory/indexes"
}
```

All mapped paths must be relative, already existing directories inside the KB.
Absolute paths, `..`, symlinks, junctions, missing folders, or unknown keys must
fail closed.

## Safety Rules

- Existing Markdown notes are scanned read-only.
- Existing `[[Wiki Links]]` are preserved exactly.
- The generated index records wiki-link metadata, but does not convert links.
- Module-owned indexes may be refreshed on rerun.
- Existing KB files must stay byte-identical unless the user explicitly asks for
  edits.
- Shared or central exports remain optional and must use reviewed/sanitized
  records only.
- Use the `agent-memory-principles` skill as the policy layer when coordinating
  Codex, Cowork, Claude, or subagents.

## Status Report Template

After running the builder, report:

```text
Agent Memory module installed:
- Module root: <path>
- Markdown files scanned: <count>
- Existing KB files modified: false
- Wiki links converted: false
- OS environment variables required: false
- Example plan: agent-memory/plans/example-kb-backed-project-plan.md
```

## When To Use Standalone Project Kit Instead

Use the normal project-folder kit when the user is starting a new coding
project and wants the full Agent Memory structure at the project root.

Use this drop-in KB module when the user already has a Markdown knowledgebase
and wants planning, handoffs, evidence, reviews, and agent memory without
changing the existing vault.

## If The User Already Uses Superpowers

Use Superpowers for coding execution workflows and Owledge for durable
project memory.

Agent behavior:

1. Treat `docs/superpowers/plans/*.md` as read-only source evidence.
2. Do not rewrite Superpowers plans, skills, hooks, or plugin files.
3. Cite Superpowers plan paths from Agent Memory plans, evidence, handoffs, or
   reviews when they explain implementation intent.
4. Keep Agent Memory writes inside `agent-memory-module/`, project
   `agent-memory/`, or validated mapped folders.
5. Use `docs/superpowers-integration.md` when the user asks how the two systems
   should work together.
