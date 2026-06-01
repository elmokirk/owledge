#!/usr/bin/env python3
"""Cross-platform project-folder-only generator for the Agent Memory Kit.

This mirrors the PowerShell generator but only requires Python. It is intended
for macOS/Linux users and agents that should not need global environment
variables or a separate kit install after the project folder is created.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import tempfile
from typing import Iterable


ROOT_FILES = [
    ("PROJECT_CONTEXT.template.md", "PROJECT_CONTEXT.md"),
    ("AGENTS.template.md", "AGENTS.md"),
    ("CLAUDE.template.md", "CLAUDE.md"),
    ("DESIGN.md", "DESIGN.md"),
    ("REPORT_DESIGN_SELECTOR.html", "REPORT_DESIGN_SELECTOR.html"),
    (".gitignore", ".gitignore"),
]

AGENT_EXCLUDES = [
    "exports/rag/*",
    "exports/lightrag/*",
    "exports/graphrag/*",
    "exports/retrieval-eval/*",
    "exports/compliance/*",
    "indexes/*.json*",
    "compliance/*",
    "templates/processing-activity-template.md",
    "templates/ai-system-template.md",
    "templates/provider-registry-template.md",
    "templates/dpia-trigger-template.md",
    "templates/data-subject-request-template.md",
    "templates/security-incident-template.md",
    "schemas/compliance-record.schema.json",
    "pi-agent/reports/*.md",
    "pi-agent/red-team/*.md",
    "pi-agent/evaluations/*.md",
    "pi-agent/scorecards/*.md",
    "tmp/*",
    "scratch/*",
    "sessions/*/events.jsonl",
    "sessions/*/session.md",
    "sessions/*/summary.md",
]

AGENT_DIRS = [
    "canonical",
    "compiled",
    "patterns",
    "lessons",
    "ideas",
    "decisions",
    "evidence",
    "evidence/promotions",
    "handoffs",
    "indexes",
    "exports/rag",
    "exports/lightrag",
    "exports/graphrag",
    "sessions",
    "pi-agent/reports",
    "pi-agent/parallels",
    "pi-agent/trends",
    "pi-agent/recurring-errors",
    "pi-agent/concepts",
    "pi-agent/red-team",
    "pi-agent/evaluations",
    "pi-agent/scorecards",
    "pi-agent/indexes",
]

GLOBAL_DIRS = [
    "preferences",
    "goals",
    "daily",
    "tasks",
    "ideas",
    "research",
    "patterns",
    "coach",
    "indexes",
    "exports/rag",
    "exports/lightrag",
    "exports/graphrag",
]

CORE_TOOLS = [
    "agent_memory_cli.py",
    "bootstrap-agent-memory.ps1",
    "build-context-pack.ps1",
    "build-context-pack.sh",
    "build-memory-index.ps1",
    "build-memory-index.sh",
    "build-project-folder-kit.ps1",
    "build-project-folder-kit.sh",
    "build_project_folder_kit.py",
    "compact-sessions.ps1",
    "eval-memory-retrieval.ps1",
    "export-graphrag.ps1",
    "export-lightrag.ps1",
    "export-rag-documents.ps1",
    "find-parallels.ps1",
    "init-agent-memory.ps1",
    "memory-doctor.ps1",
    "memory-doctor.sh",
    "promote-memory.ps1",
    "render-memory-report.ps1",
    "report-agent-memory-metrics.ps1",
    "run-memory-evals.ps1",
    "run-review-workflow.ps1",
    "start-agent-control-plane.ps1",
    "validate-memory.ps1",
    "validate-memory.sh",
    "verify-host-install.ps1",
    "verify-host-install.sh",
    "audit-retention.ps1",
    "review-memory-conflicts.ps1",
    "scan-memory-sensitive-data.ps1",
]

SKILL_DIRS = [
    "skills/agent-memory-runtime-bridge",
    "skills/review-evaluation-workflow",
    "skills/render-memory-report",
]


def copy_file(source: pathlib.Path, target: pathlib.Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_tree_filtered(source_root: pathlib.Path, target_root: pathlib.Path, excludes: Iterable[str] = ()) -> None:
    patterns = list(excludes)
    for source in source_root.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(source_root).as_posix()
        if any(fnmatch.fnmatch(relative, pattern) for pattern in patterns):
            continue
        copy_file(source, target_root / pathlib.Path(relative))


def ensure_gitkeep(root: pathlib.Path, relative_dirs: Iterable[str]) -> None:
    for relative in relative_dirs:
        directory = root / pathlib.Path(relative)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / ".gitkeep").touch()


def safe_replace_roots(source: pathlib.Path) -> list[pathlib.Path]:
    roots = [source / ".agent-control" / "tmp", pathlib.Path(tempfile.gettempdir())]
    if platform.system().lower() == "windows":
        roots.append(pathlib.Path("C:/tmp"))
    else:
        roots.append(pathlib.Path("/tmp"))
    return [root.resolve() for root in roots if root.exists() or root.parent.exists()]


def assert_safe_replace(target: pathlib.Path, source: pathlib.Path) -> None:
    resolved = target.resolve()
    for root in safe_replace_roots(source):
        try:
            resolved.relative_to(root)
            return
        except ValueError:
            continue
    raise SystemExit(f"Refusing to replace existing folder outside a temp root: {resolved}")


def install_compliance(source: pathlib.Path, target: pathlib.Path) -> None:
    manifest_path = source / "addons" / "compliance-light" / "addon.json"
    if not manifest_path.exists():
        raise SystemExit(f"Compliance Light add-on is missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    addon_root = manifest_path.parent
    for relative in manifest.get("install_directories", []):
        directory = target / pathlib.Path(relative)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / ".gitkeep").touch()
    for item in manifest.get("install_files", []):
        copy_file(addon_root / item["source"], target / pathlib.Path(item["target"]))
    gitignore = target / ".gitignore"
    text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    if "agent-memory/exports/compliance/" not in text.splitlines():
        with gitignore.open("a", encoding="utf-8") as handle:
            if text and not text.endswith("\n"):
                handle.write("\n")
            handle.write("agent-memory/exports/compliance/\n")


def apply_plugin_hook_profile(target: pathlib.Path, profile: str) -> str:
    if profile == "auto":
        profile = "windows" if platform.system().lower() == "windows" else "unix"
    if profile == "unix":
        unix_hooks = target / "plugins" / "agent-memory-cowork" / "hooks" / "hooks.unix.json"
        hooks = target / "plugins" / "agent-memory-cowork" / "hooks" / "hooks.json"
        if unix_hooks.exists():
            copy_file(unix_hooks, hooks)
    return profile


def write_local_readme(target: pathlib.Path, include_plugin: bool, hook_profile: str, include_compliance: bool) -> None:
    plugin_note = "Claude/Cowork plugin adapter is included." if include_plugin else "Claude/Cowork plugin adapter is not included."
    compliance_note = (
        "Compliance Light is included; run `python3 tools/agent_memory_cli.py --project-root . compliance-doctor`."
        if include_compliance
        else "Compliance Light is not included in this lean folder."
    )
    readme = f"""# Agent Memory Project Folder Kit

This folder is a minimal project-local Agent Memory install.

Markdown is the source of truth. Generated indexes and exports are rebuildable
views. No global `AGENT_MEMORY_KIT_ROOT` variable is required because this folder
contains its own `tools/agent_memory_cli.py`.

## Humans

Windows:

```powershell
tools\\verify-host-install.ps1 -ProjectRoot .
tools\\build-memory-index.ps1 -ProjectRoot .
```

macOS/Linux:

```bash
python3 tools/agent_memory_cli.py --project-root . doctor --mode host
python3 tools/agent_memory_cli.py --project-root . validate-memory --strict
python3 tools/agent_memory_cli.py --project-root . build-memory-index
```

Shell wrappers are also included for convenience:

```bash
bash tools/verify-host-install.sh --project-root .
bash tools/build-memory-index.sh --project-root .
```

## Agents

1. Read `PROJECT_CONTEXT.md`.
2. Use `AGENTS.md` / `CLAUDE.md` for local operating rules.
3. Build task context with:

```bash
python3 tools/agent_memory_cli.py --project-root . build-context-pack --task-id "<task-id>" --agent-role worker
```

4. Write durable findings to `agent-memory/` using the templates; do not treat
generated indexes or exports as canonical memory.

## Optional Adapters

{plugin_note}
Plugin hook profile: `{hook_profile}`.

{compliance_note}
"""
    (target / "README.md").write_text(readme, encoding="utf-8")


def run_verify(target: pathlib.Path, include_compliance: bool) -> None:
    cli = target / "tools" / "agent_memory_cli.py"
    commands = [
        [sys.executable, str(cli), "--project-root", str(target), "doctor", "--mode", "host"],
        [sys.executable, str(cli), "--project-root", str(target), "validate-memory", "--strict"],
    ]
    if include_compliance:
        commands.append([sys.executable, str(cli), "--project-root", str(target), "compliance-doctor"])
    for command in commands:
        subprocess.run(command, check=True)


def build(args: argparse.Namespace) -> dict[str, object]:
    script_root = pathlib.Path(__file__).resolve().parent
    source = pathlib.Path(args.project_root).resolve() if args.project_root else script_root.parent.resolve()
    target = pathlib.Path(args.output_path).expanduser()
    if not target.is_absolute():
        target = (pathlib.Path.cwd() / target).resolve()
    else:
        target = target.resolve()

    if target.exists():
        if not args.force:
            raise SystemExit(f"OutputPath already exists. Pass --force to replace: {target}")
        assert_safe_replace(target, source)
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    for source_rel, target_rel in ROOT_FILES:
        copy_file(source / source_rel, target / target_rel)

    copy_tree_filtered(source / "agent-memory", target / "agent-memory", AGENT_EXCLUDES)
    ensure_gitkeep(target / "agent-memory", AGENT_DIRS)

    if args.include_global_memory:
        copy_tree_filtered(source / "global-memory", target / "global-memory", ["exports/*", "indexes/*.json*"])
    else:
        ensure_gitkeep(target / "global-memory", GLOBAL_DIRS)

    for tool in CORE_TOOLS:
        copy_file(source / "tools" / tool, target / "tools" / tool)

    for skill in SKILL_DIRS:
        copy_tree_filtered(source / skill, target / skill)

    hook_profile = "none"
    if args.include_plugin_adapter:
        copy_tree_filtered(
            source / "plugins" / "agent-memory-cowork",
            target / "plugins" / "agent-memory-cowork",
            ["tests/*"],
        )
        hook_profile = apply_plugin_hook_profile(target, args.plugin_hook_profile)

    if args.include_compliance:
        install_compliance(source, target)

    write_local_readme(target, args.include_plugin_adapter, hook_profile, args.include_compliance)

    result: dict[str, object] = {
        "output_path": str(target),
        "include_global_memory": bool(args.include_global_memory),
        "include_plugin_adapter": bool(args.include_plugin_adapter),
        "plugin_hook_profile": hook_profile,
        "include_compliance": bool(args.include_compliance),
        "verified": False,
    }
    if args.verify:
        run_verify(target, args.include_compliance)
        result["verified"] = True
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a minimal project-local Agent Memory folder.")
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--project-root", default="")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--include-global-memory", action="store_true")
    parser.add_argument("--include-plugin-adapter", action="store_true")
    parser.add_argument("--include-compliance", action="store_true")
    parser.add_argument("--plugin-hook-profile", choices=["auto", "windows", "unix"], default="auto")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    result = build(args)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
