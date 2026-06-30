---
name: bootstrap-owledge
description: Initialize Owledge in a host project using project-local Python files and additive writes.
---

# Bootstrap Owledge

Use this skill when a user asks to add Owledge to an existing coding project.

## Workflow

1. Inspect the host project for `OWLEDGE.md`, `AGENTS.md`,
   `CLAUDE.md`, `DESIGN.md`, `.owledge/`, and `tools/owledge_core.py`.
2. Do not overwrite existing memory files unless the user explicitly asks.
3. From an Owledge repo checkout, run:

```bash
python tools/owledge.py init-project --target /path/to/project --include-plugin-adapter
```

Optional: link a global user-memory layer so preferences and goals persist across projects:
`python tools/owledge.py init-project --target /path/to/project --link-global`
With no path argument, uses `OWLEDGE_GLOBAL_HOME` env var or `~/.owledge/global` default.

4. Verify:

```bash
python tools/owledge.py doctor --project-root /path/to/project
python tools/owledge_core.py --project-root /path/to/project validate-memory --strict
```

5. Report created files, skipped existing files, and placeholders the user still
   needs to fill.

## Rules

- Use local files and local Python tools.
- Keep existing project memory intact.
- Do not rewrite existing Markdown, wiki links, or frontmatter unless requested.
- Keep generated indexes and runtime sessions private by default.
