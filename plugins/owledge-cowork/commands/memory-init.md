---
description: Initialize Owledge in the host project without overwriting existing memory.
---

Bootstrap the current repository as an Owledge host project.

Before running anything, inspect whether these exist:

- `OWLEDGE.md`
- `AGENTS.md`
- `CLAUDE.md`
- `DESIGN.md`
- `.owledge/`
- `tools/owledge_core.py`

If the project already has Owledge memory, do not overwrite it. From an Owledge
repo checkout, run:

```bash
python tools/owledge.py init-project --target /path/to/project --include-plugin-adapter
```

After init, verify:

```bash
python tools/owledge.py doctor --project-root /path/to/project
```

Report what was created, what already existed, and what the user must still fill
in manually.
