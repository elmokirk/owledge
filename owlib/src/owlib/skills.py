from __future__ import annotations

import pathlib
from typing import Any


RUNTIME_FILES = {
    "codex": "AGENTS.md",
    "claude": "CLAUDE.md",
    "hermes": "HERMES_SKILLS.md",
    "generic": "OWLIB_SKILLS.md",
}


SKILL_NAMES = [
    "owlib-core",
    "owlib-library-curator",
    "owlib-pi-agent",
    "owlib-parallel-scout",
    "owlib-freshness-auditor",
    "owlib-conflict-reviewer",
    "owlib-idea-synthesizer",
    "owlib-growth-planner",
]


def skill_text(skill_name: str) -> str:
    if skill_name not in SKILL_NAMES:
        raise ValueError(f"Unknown skill: {skill_name}")
    title = skill_name.replace("-", " ").title()
    focus = {
        "owlib-core": "Use Owlib as a read-only central hub over reviewed Owledge project memory.",
        "owlib-library-curator": "Review candidates and decide whether they should become patterns, lessons, ideas, or stay rejected.",
        "owlib-pi-agent": "Generate candidate intelligence reports for parallels, stale knowledge, recurring failures, and central projects.",
        "owlib-parallel-scout": "Find repeated concepts across projects without rewriting source projects.",
        "owlib-freshness-auditor": "Mark stale research, assumptions, preferences, and decisions for review.",
        "owlib-conflict-reviewer": "Detect contradictory decisions or patterns and create review candidates.",
        "owlib-idea-synthesizer": "Cluster repeated ideas into central project candidates.",
        "owlib-growth-planner": "Suggest new modules, templates, tags, and skills from repeated library signals.",
    }[skill_name]
    return f"""---
name: {skill_name}
description: {focus} Use when an agent works with OwlLibrary/Owlib, cross-project knowledge, PI agents, growth suggestions, or skill-only integration for Codex, Claude Code, Hermes, or generic agents.
---

# {title}

## Core Rule

{focus}

Read project memory and imported Owlib records as evidence. Write only candidate artifacts inside the Owlib library unless a human explicitly requests a reviewed promotion workflow.

## Read Sources

- `owlib.yaml`
- `registry/projects.jsonl`
- `imports/*/records.jsonl`
- `indexes/records.jsonl`
- reviewed Owledge source files when the user grants project access

Do not treat raw sessions, private global memory, or unsafe shared records as source truth.

## Write Targets

- `reports/`
- `parallels/`
- `conflicts/`
- `ideas/`
- module-owned candidate folders

Never modify registered project `canonical/`, `patterns/`, `lessons/`, or `decisions/` directly.

## Optional CLI

If Owlib CLI is available, prefer deterministic commands:

```bash
owlib sync --reviewed-only
owlib index
owlib find-parallels
owlib report
owlib pi report
owlib growth suggest
```

If the CLI is unavailable, follow these rules manually and produce a candidate Markdown report with cited source paths.
"""


def export_skills(runtime: str, output_dir: pathlib.Path) -> dict[str, Any]:
    if runtime not in RUNTIME_FILES:
        raise ValueError(f"Unsupported runtime: {runtime}")
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / RUNTIME_FILES[runtime]
    intro = {
        "codex": "# Owlib Skills For Codex\n\nPaste or reference this from `AGENTS.md`.",
        "claude": "# Owlib Skills For Claude Code\n\nPaste or reference this from `CLAUDE.md`.",
        "hermes": "# Owlib Skills For Hermes\n\nUse this as a tool-agnostic Hermes skill pack.",
        "generic": "# Owlib Generic Skill Pack\n\nUse this with any agent runtime.",
    }[runtime]
    sections = [intro, "Owlib is optional. Use skill-only mode when no CLI or plugin is installed."]
    for name in SKILL_NAMES:
        sections.append(skill_text(name))
    target.write_text("\n\n---\n\n".join(sections) + "\n", encoding="utf-8")
    for name in SKILL_NAMES:
        skill_dir = output_dir / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(skill_text(name), encoding="utf-8")
    return {"passed": True, "runtime": runtime, "path": str(target), "skills": SKILL_NAMES}

