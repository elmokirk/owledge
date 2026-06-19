from __future__ import annotations

import json
import pathlib
import shutil
from typing import Any

from .core import ensure_library, utc_now


BUILTIN_MODULES: dict[str, dict[str, Any]] = {
    "pi-agent": {
        "name": "pi-agent",
        "version": "0.1.0",
        "description": "PI Agent roles for library maintenance, parallels, recurring errors, freshness, conflicts, and central project candidates.",
        "commands": ["owlib pi report", "owlib pi find-parallels", "owlib pi recurring-errors", "owlib pi suggest-central-projects", "owlib pi redteam"],
    },
    "obsidian-adapter": {
        "name": "obsidian-adapter",
        "version": "0.1.0",
        "description": "Vault mapping guidance for Obsidian-style Markdown knowledgebases without wiki-link rewrites.",
        "commands": ["owlib sync", "owlib growth scan"],
    },
    "lightrag-adapter": {
        "name": "lightrag-adapter",
        "version": "0.1.0",
        "description": "Reviewed export guidance for LightRAG consumers; Owlib remains source-adjacent, not the vector store.",
        "commands": ["owlib report"],
    },
    "graphrag-adapter": {
        "name": "graphrag-adapter",
        "version": "0.1.0",
        "description": "Graph-oriented export guidance for typed edges and cross-project parallel candidates.",
        "commands": ["owlib find-parallels"],
    },
    "dashboard": {
        "name": "dashboard",
        "version": "0.1.0",
        "description": "Local report bundle for reviewing candidates, modules, quality scores, and promotion queues.",
        "commands": ["owlib report", "owlib quality"],
    },
    "compliance": {
        "name": "compliance",
        "version": "0.1.0",
        "description": "Policy guidance for reviewed-only imports, unsafe shared records, retention, and candidate promotion.",
        "commands": ["owlib quality", "owlib sync --reviewed-only"],
    },
}


def module_root(library_root: pathlib.Path, module_name: str) -> pathlib.Path:
    return library_root / "modules" / module_name


def list_modules(library_root: pathlib.Path) -> dict[str, Any]:
    ensure_library(library_root)
    installed = {path.name for path in (library_root / "modules").iterdir() if path.is_dir()}
    modules = []
    for name, manifest in sorted(BUILTIN_MODULES.items()):
        modules.append({**manifest, "installed": name in installed})
    return {"passed": True, "modules": modules}


def install_module(library_root: pathlib.Path, module_name: str) -> dict[str, Any]:
    ensure_library(library_root)
    if module_name not in BUILTIN_MODULES:
        raise ValueError(f"Unknown module: {module_name}")
    target = module_root(library_root, module_name)
    target.mkdir(parents=True, exist_ok=True)
    manifest = {**BUILTIN_MODULES[module_name], "installed_at": utc_now(), "candidate_only": True}
    (target / "module.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target / "templates").mkdir(exist_ok=True)
    (target / "skills").mkdir(exist_ok=True)
    (target / "README.md").write_text(
        f"""# Owlib Module: {module_name}

{manifest["description"]}

This module is installed on demand. It may create candidate artifacts inside the
Owlib library, but it must not change registered Owledge projects directly.

## Commands

{chr(10).join(f"- `{command}`" for command in manifest.get("commands", [])) or "- No module-specific commands yet."}
""",
        encoding="utf-8",
    )
    if module_name == "pi-agent":
        (target / "templates" / "pi-report-template.md").write_text(
            "# PI Agent Report\n\nCandidate report. Cite source records and require curator review before promotion.\n",
            encoding="utf-8",
        )
        (target / "skills" / "owlib-pi-agent.md").write_text(
            "# Owlib PI Agent Skill\n\nUse `owlib pi report` when CLI is available; otherwise write candidate reports under library reports.\n",
            encoding="utf-8",
        )
    else:
        (target / "templates" / "candidate-template.md").write_text(
            f"# {module_name} Candidate\n\nUse reviewed Owlib sources. Keep this artifact candidate-only until curator review.\n",
            encoding="utf-8",
        )
        (target / "skills" / f"{module_name}.md").write_text(
            f"# {module_name} Skill\n\nUse this module only inside the Owlib library. Do not modify registered projects directly.\n",
            encoding="utf-8",
        )
    return {"passed": True, "module": module_name, "path": str(target)}


def remove_module(library_root: pathlib.Path, module_name: str) -> dict[str, Any]:
    target = module_root(library_root, module_name)
    if target.exists():
        shutil.rmtree(target)
    return {"passed": True, "module": module_name, "removed": True, "preserved_user_reports": True}


def module_status(library_root: pathlib.Path) -> dict[str, Any]:
    return list_modules(library_root)
