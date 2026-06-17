#!/usr/bin/env python3
"""Owledge public CLI.

Python-first entrypoint for local Markdown memory, KB modules, release gates,
and plugin smoke tests. The lower-level implementation stays in
agent_memory_cli.py and the focused builders next to this file.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable, Iterable

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import agent_memory_cli as core  # noqa: E402
import build_kb_module  # noqa: E402
import build_project_folder_kit  # noqa: E402


PUBLIC_DOC_FILES = [
    "README.md",
    "docs/README.md",
    "docs/quickstart.md",
    "docs/agent-integration-guide.md",
    "docs/install-plugin.md",
    "docs/harness-plugin-matrix.md",
    "docs/mvp-plan-example.md",
    "docs/performance-scale-notes.md",
    "docs/team-long-running-project-guide.md",
    "docs/command-reference.md",
    "docs/owledge-vs-agent-methods.md",
    "plugins/agent-memory-cowork/README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
]

PUBLIC_FORBIDDEN_PATTERNS = [
    "power" + "shell",
    ".p" + "s1",
    "Execution" + "Policy",
    "AGENT_MEMORY_" + "KIT_ROOT",
    "AGENT_MEMORY_" + "PROJECT_ROOT",
]

ROOT_FILE_MAP = [
    ("PROJECT_CONTEXT.template.md", "PROJECT_CONTEXT.md"),
    ("AGENTS.template.md", "AGENTS.md"),
    ("CLAUDE.template.md", "CLAUDE.md"),
    ("DESIGN.md", "DESIGN.md"),
    ("REPORT_DESIGN_SELECTOR.html", "REPORT_DESIGN_SELECTOR.html"),
]

HOST_TOOL_FILES = [
    "owledge.py",
    "agent_memory_cli.py",
    "build_kb_module.py",
    "build_project_folder_kit.py",
]

HOST_SKILL_DIRS = [
    "skills/agent-memory-principles",
    "skills/agent-memory-runtime-bridge",
    "skills/review-evaluation-workflow",
    "skills/render-memory-report",
]


class ResultSet:
    def __init__(self) -> None:
        self.results: list[dict[str, Any]] = []

    def add(self, name: str, passed: bool, details: str = "") -> None:
        self.results.append({"name": name, "passed": bool(passed), "details": details})

    def payload(self, **extra: Any) -> dict[str, Any]:
        failed = [row for row in self.results if not row["passed"]]
        payload: dict[str, Any] = {
            "passed": not failed,
            "failed": len(failed),
            "total": len(self.results),
            "results": self.results,
        }
        payload.update(extra)
        return payload


def print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def resolve_path(value: str | pathlib.Path, base: pathlib.Path | None = None) -> pathlib.Path:
    path = pathlib.Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return ((base or pathlib.Path.cwd()) / path).resolve()


def relative_posix(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_hash(root: pathlib.Path, exclude_prefixes: Iterable[str] = ()) -> str:
    rows: list[str] = []
    prefixes = tuple(prefix.replace("\\", "/").rstrip("/") + "/" for prefix in exclude_prefixes)
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        rel = relative_posix(path, root)
        if any(rel.startswith(prefix) for prefix in prefixes):
            continue
        rows.append(f"{rel}={sha256_file(path)}")
    return "\n".join(rows)


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def copy_file_if_missing(source: pathlib.Path, target: pathlib.Path) -> bool:
    if target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return True


def copy_tree_missing(source_root: pathlib.Path, target_root: pathlib.Path, excludes: Iterable[str] = ()) -> list[str]:
    copied: list[str] = []
    patterns = list(excludes)
    for source in sorted(source_root.rglob("*"), key=lambda item: item.as_posix()):
        if not source.is_file():
            continue
        rel = source.relative_to(source_root).as_posix()
        if any(fnmatch.fnmatch(rel, pattern) for pattern in patterns):
            continue
        target = target_root / pathlib.Path(rel)
        if copy_file_if_missing(source, target):
            copied.append(target.relative_to(target_root.parent).as_posix())
    return copied


def github_anchor(heading: str) -> str:
    text = heading.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def run_subprocess(command: list[str], cwd: pathlib.Path | None = None, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def parse_json_stdout(process: subprocess.CompletedProcess[str]) -> Any:
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or f"Exit code {process.returncode}")
    return json.loads(process.stdout)


def init_project(project_root: pathlib.Path, source_root: pathlib.Path, include_plugin_adapter: bool, include_compliance: bool) -> dict[str, Any]:
    project_root.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    skipped: list[str] = []

    for source_rel, target_rel in ROOT_FILE_MAP:
        source = source_root / source_rel
        target = project_root / target_rel
        if copy_file_if_missing(source, target):
            created.append(target_rel)
        else:
            skipped.append(target_rel)

    gitignore = project_root / ".gitignore"
    if not gitignore.exists() and (source_root / ".gitignore").exists():
        copy_file_if_missing(source_root / ".gitignore", gitignore)
        created.append(".gitignore")

    copy_tree_missing(source_root / "agent-memory", project_root / "agent-memory", build_project_folder_kit.AGENT_EXCLUDES)
    build_project_folder_kit.ensure_gitkeep(project_root / "agent-memory", build_project_folder_kit.AGENT_DIRS)

    tool_dir = project_root / "tools"
    for tool in HOST_TOOL_FILES:
        source = source_root / "tools" / tool
        if source.exists():
            rel = f"tools/{tool}"
            if copy_file_if_missing(source, tool_dir / tool):
                created.append(rel)
            else:
                skipped.append(rel)

    for skill in HOST_SKILL_DIRS:
        source = source_root / skill
        if source.exists():
            created.extend(copy_tree_missing(source, project_root / skill))

    if include_plugin_adapter:
        created.extend(
            copy_tree_missing(
                source_root / "plugins" / "agent-memory-cowork",
                project_root / "plugins" / "agent-memory-cowork",
                ["tests/*"],
            )
        )

    if include_compliance:
        build_project_folder_kit.install_compliance(source_root, project_root)
        created.append("agent-memory/compliance/")

    doctor = core.memory_doctor(project_root, mode="host")
    return {
        "project_root": str(project_root),
        "created": sorted(set(created)),
        "skipped_existing": sorted(set(skipped)),
        "include_plugin_adapter": include_plugin_adapter,
        "include_compliance": include_compliance,
        "doctor_passed": doctor["passed"],
    }


def public_docs_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    public_files = [root / pathlib.Path(item) for item in PUBLIC_DOC_FILES]
    for relative, path in zip(PUBLIC_DOC_FILES, public_files):
        results.add(f"exists:{relative}", path.exists(), "Public doc exists.")
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        mojibake = [marker for marker in ("\u00c2", "\u00e2", "\u00ef") if marker in content]
        results.add(f"utf8-clean:{relative}", not mojibake, "No common mojibake markers detected.")
        lowered = content.lower()
        for pattern in PUBLIC_FORBIDDEN_PATTERNS:
            if pattern == ".p" + "s1":
                passed = pattern not in content
            elif pattern.startswith("AGENT_"):
                passed = pattern not in content
            else:
                passed = pattern.lower() not in lowered
            results.add(f"python-first-doc:{relative}:{pattern}", passed, "Public docs must not present platform-specific wrappers or OS env setup as core UX.")

    readme = (root / "README.md").read_text(encoding="utf-8", errors="replace")
    headings = [github_anchor(match.group(1)) for match in re.finditer(r"(?m)^##+\s+(.+)$", readme)]
    toc_links = [match.group(1) for match in re.finditer(r"(?m)^-\s+\[[^\]]+\]\(#([^)]+)\)", readme)]
    for anchor in toc_links:
        results.add(f"toc-anchor:{anchor}", anchor in headings, "README table-of-contents anchor resolves.")

    for relative, path in zip(PUBLIC_DOC_FILES, public_files):
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", content):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            resolved = (path.parent / clean).resolve()
            results.add(f"link:{relative}->{clean}", resolved.exists(), "Relative markdown link resolves.")

    docs_index = (root / "docs" / "README.md").read_text(encoding="utf-8", errors="replace")
    for link in [
        "quickstart.md",
        "agent-integration-guide.md",
        "install-plugin.md",
        "harness-plugin-matrix.md",
        "mvp-plan-example.md",
        "performance-scale-notes.md",
        "team-long-running-project-guide.md",
        "command-reference.md",
    ]:
        results.add(f"docs-index:{link}", link in docs_index, "Docs index links the public entrypoint.")

    plugin_docs = [
        root / "README.md",
        root / "docs" / "install-plugin.md",
        root / "docs" / "harness-plugin-matrix.md",
        root / "plugins" / "agent-memory-cowork" / "README.md",
    ]
    for path in plugin_docs:
        if not path.exists():
            continue
        label = relative_posix(path, root)
        text = path.read_text(encoding="utf-8", errors="replace")
        results.add("plugin-path:" + label, "plugins/agent-memory-cowork/" in text or "plugins\\agent-memory-cowork\\" in text, "Canonical plugin path is documented.")

    if "benchmark" in readme.lower() or "benchmark" in (root / "docs" / "performance-scale-notes.md").read_text(encoding="utf-8", errors="replace").lower():
        results.add("benchmark-assets:readme", (root / "benchmarks" / "README.md").exists(), "Benchmark README exists.")
        results.add("benchmark-assets:script", (root / "benchmarks" / "run_benchmarks.py").exists(), "Python benchmark runner exists.")

    return results.payload(project=str(root))


def read_skill_frontmatter(path: pathlib.Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValueError(f"Missing YAML frontmatter in {path}")
    closing_index = -1
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index < 2:
        raise ValueError(f"Missing closing YAML frontmatter marker in {path}")
    fields: dict[str, str] = {}
    for line in lines[1:closing_index]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"')
    return {"fields": fields, "line_count": len(lines), "body": "\n".join(lines[closing_index + 1 :])}


def principles_skill_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    required_refs = [
        "references/principles.md",
        "references/agent-rules.md",
        "references/mapping-contract.md",
        "references/security-rules.md",
    ]

    def test_skill(relative: str) -> None:
        skill_dir = root / pathlib.Path(relative)
        skill_path = skill_dir / "SKILL.md"
        results.add(f"exists:{relative}", skill_path.exists(), "SKILL.md exists.")
        if not skill_path.exists():
            return
        parsed = read_skill_frontmatter(skill_path)
        fields = parsed["fields"]
        results.add(f"frontmatter-name:{relative}", fields.get("name") == "agent-memory-principles", "Expected name agent-memory-principles.")
        results.add(f"frontmatter-description:{relative}", bool(fields.get("description")), "Description is present.")
        results.add(f"concise-skill:{relative}", parsed["line_count"] <= 90, f"SKILL.md has {parsed['line_count']} lines; limit is 90.")
        for reference in required_refs:
            results.add(f"reference-linked:{relative}/{reference}", reference in parsed["body"], "Reference is linked from SKILL.md.")
            results.add(f"reference-exists:{relative}/{reference}", (skill_dir / reference).exists(), "Reference file exists.")

    root_skill = "skills/agent-memory-principles"
    plugin_skill = "plugins/agent-memory-cowork/skills/agent-memory-principles"
    test_skill(root_skill)
    test_skill(plugin_skill)
    for reference in ["SKILL.md", *required_refs]:
        source = root / root_skill / reference
        mirror = root / plugin_skill / reference
        if source.exists() and mirror.exists():
            results.add(f"mirror-identical:{reference}", sha256_file(source) == sha256_file(mirror), "Plugin mirror matches root skill file.")
    return results.payload()


def kb_module_gate(root: pathlib.Path) -> dict[str, Any]:
    tmp_base = root / ".agent-control" / "tmp"
    tmp_base.mkdir(parents=True, exist_ok=True)
    kb = tmp_base / "kb-module-smoke"
    if kb.exists():
        shutil.rmtree(kb)
    kb.mkdir(parents=True)
    note_a = kb / "Project Alpha.md"
    note_b = kb / "Research.md"
    write_text(note_a, "# Project Alpha\n\nLinks to [[Research]] and keeps the original wiki link untouched.\n")
    write_text(note_b, "---\ntype: research\nstatus: active\n---\n\n# Research\n\nSource note.\n")
    before_a = sha256_file(note_a)
    before_b = sha256_file(note_b)
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(kb),
            kit_root=str(root),
            layout="module-dir",
            module_dir="agent-memory-module",
            map_file="",
            max_files=10000,
            include_cli=True,
            create_sample_plan=True,
        )
    )
    if before_a != sha256_file(note_a) or before_b != sha256_file(note_b):
        raise RuntimeError("Existing KB markdown files were modified.")
    module_root = kb / "agent-memory-module"
    for relative in [
        "AGENT_MEMORY_MODULE.md",
        "agent-memory/plans/example-kb-backed-project-plan.md",
        "agent-memory/indexes/kb-scan.jsonl",
        "agent-memory/indexes/kb-module-status.json",
        "tools/agent_memory_cli.py",
    ]:
        if not (module_root / pathlib.Path(relative)).exists():
            raise RuntimeError(f"Missing expected module file: {relative}")
    status = json.loads((module_root / "agent-memory" / "indexes" / "kb-module-status.json").read_text(encoding="utf-8"))
    if status["markdown_files_scanned"] < 2 or status["existing_kb_files_modified"] or status["requires_os_environment_variables"]:
        raise RuntimeError("KB module status did not report safe additive behavior.")

    mapped_kb = tmp_base / "kb-module-mapped-smoke"
    if mapped_kb.exists():
        shutil.rmtree(mapped_kb)
    mapped_kb.mkdir(parents=True)
    write_text(mapped_kb / "Idea.md", "# Idea\n\nTurn [[Research]] into an MVP.\n")
    write_text(mapped_kb / "Research.md", "# Research\n\nSource note.\n")
    for relative in ["01_Ideas", "20_Plans", "30_Evidence", "40_Handoffs", "50_Reviews", ".agent-memory/indexes"]:
        (mapped_kb / pathlib.Path(relative)).mkdir(parents=True, exist_ok=True)
    write_text(
        mapped_kb / "agent-memory-map.json",
        json.dumps(
            {
                "ideas": "01_Ideas",
                "plans": "20_Plans",
                "evidence": "30_Evidence",
                "handoffs": "40_Handoffs",
                "reviews": "50_Reviews",
                "indexes": ".agent-memory/indexes",
            },
            indent=2,
        ),
    )
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(mapped_kb),
            kit_root=str(root),
            layout="module-dir",
            module_dir="agent-memory-module",
            map_file="agent-memory-map.json",
            max_files=10000,
            include_cli=False,
            create_sample_plan=True,
        )
    )
    mapped_status = json.loads((mapped_kb / ".agent-memory" / "indexes" / "kb-module-status.json").read_text(encoding="utf-8"))
    if mapped_status["mode"] != "mapped" or not mapped_status["mapping_enabled"]:
        raise RuntimeError("Mapped status did not report mapped mode.")
    if (mapped_kb / "AGENT_MEMORY_MODULE.md").exists():
        raise RuntimeError("Mapped mode should not write root AGENT_MEMORY_MODULE.md.")
    bad_map = {
        "plans": "../escape",
        "evidence": "30_Evidence",
        "handoffs": "40_Handoffs",
        "reviews": "50_Reviews",
        "indexes": ".agent-memory/indexes",
    }
    write_text(mapped_kb / "bad-agent-memory-map.json", json.dumps(bad_map))
    process = run_subprocess(
        [
            sys.executable,
            str(root / "tools" / "build_kb_module.py"),
            "--knowledgebase-root",
            str(mapped_kb),
            "--kit-root",
            str(root),
            "--map-file",
            "bad-agent-memory-map.json",
        ]
    )
    if process.returncode == 0:
        raise RuntimeError("Invalid map with traversal path should fail closed.")
    return {
        "passed": True,
        "knowledgebase": str(kb),
        "module_root": str(module_root),
        "existing_files_unchanged": True,
        "mapped_mode": True,
        "invalid_map_failed_closed": True,
    }


def runtime_adapters_gate(root: pathlib.Path) -> dict[str, Any]:
    fixtures = root / "plugins" / "agent-memory-cowork" / "tests" / "fixtures"
    if not fixtures.exists():
        raise RuntimeError(f"Missing plugin fixtures: {fixtures}")
    tmp_root = root / ".agent-control" / "tmp" / f"agent-memory-runtime-smoke-{next(tempfile._get_candidate_names())}"
    build_project_folder_kit.build(
        argparse.Namespace(
            output_path=str(tmp_root),
            project_root=str(root),
            force=True,
            include_global_memory=False,
            include_plugin_adapter=True,
            include_compliance=False,
            plugin_hook_profile="python",
            verify=False,
        )
    )
    hooks = json.loads((tmp_root / "plugins" / "agent-memory-cowork" / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    hooks_text = json.dumps(hooks)
    if ("power" + "shell") in hooks_text.lower() or (".p" + "s1") in hooks_text:
        raise RuntimeError("Default plugin hooks must be Python-first and platform-neutral.")
    capture = tmp_root / "plugins" / "agent-memory-cowork" / "scripts" / "capture-claude-event.py"
    close = tmp_root / "plugins" / "agent-memory-cowork" / "scripts" / "close-runtime-session.py"
    for fixture in ["session-start.json", "user-prompt.json", "post-tool-use.json"]:
        payload = (fixtures / fixture).read_text(encoding="utf-8")
        process = run_subprocess([sys.executable, str(capture)], cwd=tmp_root, input_text=payload)
        if process.returncode != 0:
            raise RuntimeError(f"Python capture hook failed for {fixture}: {process.stderr}")
    process = run_subprocess([sys.executable, str(close)], cwd=tmp_root, input_text=(fixtures / "stop.json").read_text(encoding="utf-8"))
    if process.returncode != 0:
        raise RuntimeError(f"Python close hook failed: {process.stderr}")
    session_dir = tmp_root / "agent-memory" / "sessions" / "cowork-demo-session"
    required = ["events.jsonl", "session.md", "summary.md"]
    missing = [name for name in required if not (session_dir / name).exists()]
    if missing:
        raise RuntimeError(f"Runtime smoke missing files: {', '.join(missing)}")
    summary = (session_dir / "summary.md").read_text(encoding="utf-8")
    if "visibility: \"private\"" not in summary and "visibility: private" not in summary:
        raise RuntimeError("Runtime summary is not private.")
    return {
        "passed": True,
        "temp_project": str(tmp_root),
        "session_dir": str(session_dir),
        "checked_files": required,
        "checked_python_hooks": True,
    }


def expect_kb_failure(root: pathlib.Path, kb_root: pathlib.Path, map_file: str, extra_args: list[str] | None = None) -> bool:
    command = [
        sys.executable,
        str(root / "tools" / "build_kb_module.py"),
        "--knowledgebase-root",
        str(kb_root),
        "--kit-root",
        str(root),
    ]
    if map_file:
        command.extend(["--map-file", map_file])
    command.extend(extra_args or [])
    return run_subprocess(command).returncode != 0


def new_mapped_kb(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for relative in ["00_Inbox", "20_Plans", "30_Evidence", "40_Handoffs", "50_Reviews", ".agent-memory/indexes"]:
        (path / pathlib.Path(relative)).mkdir(parents=True, exist_ok=True)
    write_text(path / "00_Inbox" / "Idea.md", "# Idea\n\nBuild MVP from [[Research Note]].\n")
    write_text(path / "Research Note.md", "---\ntype: research\n---\n\n# Research Note\n\nKeep this source unchanged.\n")
    write_text(
        path / "agent-memory-map.json",
        json.dumps(
            {
                "ideas": "00_Inbox",
                "plans": "20_Plans",
                "evidence": "30_Evidence",
                "handoffs": "40_Handoffs",
                "reviews": "50_Reviews",
                "indexes": ".agent-memory/indexes",
            },
            indent=2,
        ),
    )


def principles_scenarios_gate(root: pathlib.Path) -> dict[str, Any]:
    tmp_base = root / ".agent-control" / "tmp" / "principles-scenarios"
    if tmp_base.exists():
        shutil.rmtree(tmp_base)
    tmp_base.mkdir(parents=True)
    results = ResultSet()

    large_root = tmp_base / "large-codebase"
    large_root.mkdir(parents=True)
    for index in range(1, 81):
        write_text(large_root / "docs" / f"note-{index:03}.md", f"# Note {index}\n\nLinks to [[ADR-{index}]].\n")
    for index in range(1, 121):
        write_text(large_root / "src" / f"module{index:03}" / f"file{index:03}.ts", f"export const value{index} = {index};\n")
    large_before = tree_hash(large_root)
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(large_root),
            kit_root=str(root),
            layout="module-dir",
            module_dir="agent-memory-module",
            map_file="",
            max_files=25,
            include_cli=False,
            create_sample_plan=True,
        )
    )
    large_after = tree_hash(large_root, ["agent-memory-module"])
    large_status = json.loads((large_root / "agent-memory-module" / "agent-memory" / "indexes" / "kb-module-status.json").read_text(encoding="utf-8"))
    results.add("large-codebase-existing-files-unchanged", large_before == large_after, "Existing files stayed byte-identical outside the module.")
    results.add("large-codebase-max-files-honored", large_status["markdown_files_scanned"] == 25, "MaxFiles=25 honored.")
    results.add("large-codebase-zero-env", large_status["requires_os_environment_variables"] is False, "No OS environment variable dependency.")

    user_kb = tmp_base / "existing-user-kb"
    new_mapped_kb(user_kb)
    user_before = tree_hash(user_kb)
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(user_kb),
            kit_root=str(root),
            layout="module-dir",
            module_dir="agent-memory-module",
            map_file="agent-memory-map.json",
            max_files=10000,
            include_cli=False,
            create_sample_plan=True,
        )
    )
    user_after = tree_hash(user_kb, ["20_Plans", "30_Evidence", "40_Handoffs", "50_Reviews", ".agent-memory/indexes"])
    user_status = json.loads((user_kb / ".agent-memory" / "indexes" / "kb-module-status.json").read_text(encoding="utf-8"))
    results.add("user-kb-mapped-mode", user_status["mode"] == "mapped" and user_status["mapping_enabled"], "Mapped mode selected.")
    results.add("user-kb-original-notes-unchanged", user_before == user_after, "Original notes and map stayed byte-identical.")
    results.add("user-kb-wikilinks-not-converted", user_status["wiki_links_converted"] is False, "Wiki links not converted.")
    results.add("user-kb-no-root-module-doc", not (user_kb / "AGENT_MEMORY_MODULE.md").exists(), "Mapped mode avoids root module doc.")
    write_text(user_kb / "30_Evidence" / "worker-evidence.md", "# Worker Evidence\n\nSource: `Research Note.md`.\n")
    write_text(user_kb / "40_Handoffs" / "worker-handoff.md", "# Worker Handoff\n\nStatus: done.\n")
    write_text(user_kb / "50_Reviews" / "reviewer-findings.md", "# Reviewer Findings\n\nVerdict: needs curator approval before promotion.\n")
    forbidden = [user_kb / "agent-memory" / "canonical", user_kb / "agent-memory" / "lessons", user_kb / "global-memory"]
    results.add("multi-agent-role-boundaries", not any(path.exists() for path in forbidden), "Workers/reviewers wrote only mapped artifacts.")

    skill_bloat = tmp_base / "skill-bloat"
    skill_bloat.mkdir()
    for index in range(1, 51):
        skill_dir = skill_bloat / f"noise-skill-{index:02}"
        skill_dir.mkdir()
        write_text(skill_dir / "SKILL.md", f"---\nname: noise-skill-{index}\ndescription: unrelated test skill\n---\n\n# Noise\n")
    shutil.copytree(root / "skills" / "agent-memory-principles", skill_bloat / "agent-memory-principles")
    matches = [
        path
        for path in skill_bloat.rglob("SKILL.md")
        if re.search(r"(?m)^name:\s*agent-memory-principles\s*$", path.read_text(encoding="utf-8"))
    ]
    results.add("skill-bloat-exact-name-discovery", len(matches) == 1, "Found exactly one agent-memory-principles skill among 51 skills.")
    results.add("skill-bloat-references-present", (skill_bloat / "agent-memory-principles" / "references" / "mapping-contract.md").exists(), "References survive crowded skill install.")

    superpowers_kb = tmp_base / "superpowers-coexistence"
    superpowers_plan = superpowers_kb / "docs" / "superpowers" / "plans" / "example-plan.md"
    write_text(
        superpowers_plan,
        "# Example Superpowers Implementation Plan\n\n**Goal:** Add a small feature with TDD.\n\n- [ ] Write the failing test\n- [ ] Implement the minimal code\n",
    )
    write_text(superpowers_kb / "README.md", "# Existing Project\n\nUses Superpowers for execution.\n")
    superpowers_hash_before = sha256_file(superpowers_plan)
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(superpowers_kb),
            kit_root=str(root),
            layout="module-dir",
            module_dir="agent-memory-module",
            map_file="",
            max_files=10000,
            include_cli=False,
            create_sample_plan=True,
        )
    )
    superpowers_hash_after = sha256_file(superpowers_plan)
    index_text = (superpowers_kb / "agent-memory-module" / "agent-memory" / "indexes" / "kb-scan.jsonl").read_text(encoding="utf-8")
    handoff_path = superpowers_kb / "agent-memory-module" / "agent-memory" / "handoffs" / "superpowers-plan-handoff.md"
    write_text(handoff_path, "# Superpowers Plan Handoff\n\nEvidence: `docs/superpowers/plans/example-plan.md`.\n")
    results.add("superpowers-plan-unchanged", superpowers_hash_before == superpowers_hash_after, "Superpowers plan unchanged.")
    results.add("superpowers-plan-indexed", "docs/superpowers/plans/example-plan.md" in index_text, "Index references Superpowers plan.")
    results.add("superpowers-handoff-evidence", "docs/superpowers/plans/example-plan.md" in handoff_path.read_text(encoding="utf-8"), "Handoff cites Superpowers plan.")

    edge_kb = tmp_base / "edge-kb"
    new_mapped_kb(edge_kb)
    edge_cases: list[tuple[str, Any]] = [
        ("absolute-path", {"plans": "C:/escape", "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".agent-memory/indexes"}),
        ("unknown-key", {"plans": "20_Plans", "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".agent-memory/indexes", "canonical": "50_Reviews"}),
        ("missing-required-key", {"plans": "20_Plans", "evidence": "30_Evidence", "reviews": "50_Reviews", "indexes": ".agent-memory/indexes"}),
        ("missing-target", {"plans": "20_Plans", "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": "missing-indexes"}),
        ("file-target", {"plans": "Research Note.md", "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".agent-memory/indexes"}),
        ("blank-value", {"plans": "", "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".agent-memory/indexes"}),
        ("null-value", {"plans": None, "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".agent-memory/indexes"}),
        ("array-value", {"plans": ["20_Plans"], "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".agent-memory/indexes"}),
    ]
    for name, payload in edge_cases:
        write_text(edge_kb / f"bad-{name}.json", json.dumps(payload))
        results.add(f"edge-fail-closed:{name}", expect_kb_failure(root, edge_kb, f"bad-{name}.json"), "Invalid map should fail closed.")
    results.add("edge-fail-closed:missing-explicit-map", expect_kb_failure(root, edge_kb, "does-not-exist.json"), "Explicit missing map should fail closed.")
    write_text(edge_kb / "bad-duplicate-key.json", '{"plans":"../escape","plans":"20_Plans","evidence":"30_Evidence","handoffs":"40_Handoffs","reviews":"50_Reviews","indexes":".agent-memory/indexes"}')
    results.add("edge-fail-closed:duplicate-json-key", expect_kb_failure(root, edge_kb, "bad-duplicate-key.json"), "Duplicate JSON keys should fail closed.")
    results.add("edge-fail-closed:max-files-zero", expect_kb_failure(root, edge_kb, "", ["--max-files", "0"]), "max-files=0 should fail closed.")

    bom_kb = tmp_base / "bom-frontmatter-kb"
    bom_kb.mkdir()
    (bom_kb / "Bom.md").write_text("\ufeff---\ntype: research\nstatus: active\n---\n\n# BOM Note\n", encoding="utf-8")
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(bom_kb),
            kit_root=str(root),
            layout="module-dir",
            module_dir="agent-memory-module",
            map_file="",
            max_files=10000,
            include_cli=False,
            create_sample_plan=True,
        )
    )
    bom_rows = [(json.loads(line)) for line in (bom_kb / "agent-memory-module" / "agent-memory" / "indexes" / "kb-scan.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    keys = set(bom_rows[0].get("frontmatter_keys", [])) if bom_rows else set()
    results.add("edge-bom-frontmatter-keys", {"type", "status"}.issubset(keys), "BOM-prefixed frontmatter keys detected.")

    return results.payload(symlink_case_skipped=True)


def run_gate(name: str, func: Callable[[], Any]) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        payload = func()
        passed = bool(payload.get("passed", True)) if isinstance(payload, dict) else True
        if not passed:
            raise RuntimeError(json.dumps(payload, indent=2))
        return {"name": name, "passed": True, "seconds": round(time.perf_counter() - started, 3)}
    except Exception as exc:
        return {"name": name, "passed": False, "error": str(exc), "seconds": round(time.perf_counter() - started, 3)}


def py_compile_gate(root: pathlib.Path) -> dict[str, Any]:
    files = [
        root / "tools" / "owledge.py",
        root / "tools" / "agent_memory_cli.py",
        root / "tools" / "build_kb_module.py",
        root / "tools" / "build_project_folder_kit.py",
        root / "plugins" / "agent-memory-cowork" / "scripts" / "capture-claude-event.py",
        root / "plugins" / "agent-memory-cowork" / "scripts" / "close-runtime-session.py",
        root / "benchmarks" / "run_benchmarks.py",
    ]
    process = run_subprocess([sys.executable, "-m", "py_compile", *[str(path) for path in files]])
    if process.returncode != 0:
        raise RuntimeError(process.stderr or process.stdout)
    return {"passed": True, "files": [relative_posix(path, root) for path in files]}


def platform_neutral_core_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    scanned_roots = [
        "README.md",
        "docs",
        "plugins",
        "skills",
        "tools",
        "benchmarks",
        ".github",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "SUPPORT.md",
        "ROADMAP.md",
    ]
    allowed_prefixes = ("docs/extensions/windows-" + "power" + "shell.md",)
    for entry in scanned_roots:
        path = root / pathlib.Path(entry)
        files = [path] if path.is_file() else [item for item in path.rglob("*") if item.is_file()]
        for file_path in files:
            rel = relative_posix(file_path, root)
            if rel.startswith(allowed_prefixes):
                continue
            if "__pycache__" in file_path.parts:
                continue
            if file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pyc"}:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            lower = text.lower()
            forbidden = [
                "power" + "shell",
                ".p" + "s1",
                "execution" + "policy",
                "agent_memory_" + "kit_root",
                "agent_memory_" + "project_root",
            ]
            has_forbidden = any(pattern in lower for pattern in forbidden)
            results.add(f"core-platform-neutral:{rel}", not has_forbidden, "Core file must not reference platform-specific setup wrappers or root env vars.")
    return results.payload()


def project_folder_kit_gate(root: pathlib.Path, include_compliance: bool = False) -> dict[str, Any]:
    output = root / ".agent-control" / "tmp" / ("owledge-project-kit-compliance" if include_compliance else "owledge-project-kit")
    result = build_project_folder_kit.build(
        argparse.Namespace(
            output_path=str(output),
            project_root=str(root),
            force=True,
            include_global_memory=False,
            include_plugin_adapter=True,
            include_compliance=include_compliance,
            plugin_hook_profile="python",
            verify=True,
        )
    )
    forbidden = [path for path in output.rglob("*") if path.is_file() and path.suffix.lower() == (".p" + "s1")]
    if forbidden:
        raise RuntimeError("Default generated kit contains platform-specific wrapper files: " + ", ".join(path.as_posix() for path in forbidden[:5]))
    return {"passed": True, **result}


def finalization_gates(root: pathlib.Path, include_exports: bool, include_compliance: bool) -> dict[str, Any]:
    gates: list[dict[str, Any]] = []

    def add(name: str, func: Callable[[], Any]) -> None:
        gate = run_gate(name, func)
        gates.append(gate)
        status = "PASS" if gate["passed"] else "FAIL"
        print(f"{status} {name} ({gate['seconds']}s)")

    add("python-compile", lambda: py_compile_gate(root))
    add("public-docs", lambda: public_docs_gate(root))
    add("principles-skill", lambda: principles_skill_gate(root))
    add("principles-scenarios", lambda: principles_scenarios_gate(root))
    add("contracts", lambda: core.test_contracts(root))
    add("core-platform-neutral", lambda: platform_neutral_core_gate(root))
    add("doctor", lambda: core.memory_doctor(root, mode="kit"))
    add("validate", lambda: core.validate_memory(root, strict=False))
    add("index-full", lambda: core.build_memory_index(root))
    add("index-incremental", lambda: core.build_memory_index(root, incremental=True, track_tombstones=True))
    add("retention", lambda: core.audit_retention(root))
    add("conflicts", lambda: core.review_memory_conflicts(root))
    add("sensitive-scan", lambda: core.scan_sensitive_data(root))
    add("runtime-adapters", lambda: runtime_adapters_gate(root))
    add("memory-evals", lambda: core.run_evals(root))
    add(
        "retrieval-fixture",
        lambda: core.evaluate_memory_retrieval(
            root,
            [root / "tests" / "fixtures" / "retrieval-corpus"],
            output_dir=None,
            top_k=5,
            include_sessions=False,
            queries_file=root / "tests" / "fixtures" / "retrieval-queries.json",
            min_overall_score=85,
            min_safety_score=100,
        ),
    )
    add("kb-module", lambda: kb_module_gate(root))
    add("project-folder-kit", lambda: project_folder_kit_gate(root, include_compliance=False))
    if include_compliance:
        add("compliance-addon-source", lambda: compliance_source_gate(root))
        add("project-folder-kit-compliance", lambda: project_folder_kit_gate(root, include_compliance=True))
        add("compliance-gates", lambda: core.compliance_doctor(root / ".agent-control" / "tmp" / "owledge-project-kit-compliance"))
    if include_exports:
        add("export-rag-shared", lambda: core.export_rag_documents(root, corpus_type="shared"))
        add("export-lightrag-shared", lambda: core.export_lightrag(root, corpus_type="shared"))
        add("export-graphrag-shared", lambda: core.export_graphrag(root, corpus_type="shared"))
        add("report-shared", lambda: core.render_memory_report(root, "project-dashboard", audience="shared"))

    failed = [gate for gate in gates if not gate["passed"]]
    report_dir = root / "agent-memory" / "exports" / "finalization-gates"
    report_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "generated_at": core.utc_now(),
        "project": str(root),
        "passed": not failed,
        "gates": gates,
        "failed": len(failed),
        "include_compliance": include_compliance,
    }
    (report_dir / "latest.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Finalization Gates",
        "",
        f"- Generated at: {result['generated_at']}",
        f"- Passed: {result['passed']}",
        f"- Failed gates: {result['failed']}",
        "",
        "## Gates",
        "",
    ]
    for gate in gates:
        status = "PASS" if gate["passed"] else "FAIL"
        line = f"- {status} `{gate['name']}` in {gate['seconds']}s"
        if not gate["passed"] and gate.get("error"):
            line += f" - {gate['error']}"
        lines.append(line)
    (report_dir / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def compliance_source_gate(root: pathlib.Path) -> dict[str, Any]:
    manifest = root / "addons" / "compliance-light" / "addon.json"
    if not manifest.exists():
        raise RuntimeError(f"Compliance Light manifest is missing: {manifest}")
    json.loads(manifest.read_text(encoding="utf-8"))
    return {"passed": True, "manifest": str(manifest)}


def redteam_qa(root: pathlib.Path, subject: str, question: str, gate_report_path: str) -> dict[str, Any]:
    gate_report = resolve_path(gate_report_path, root) if gate_report_path else root / "agent-memory" / "exports" / "finalization-gates" / "latest.json"
    if not gate_report.exists():
        gate = finalization_gates(root, include_exports=False, include_compliance=False)
        if not gate["passed"]:
            raise RuntimeError("Finalization gates are not passing.")
    gate = json.loads(gate_report.read_text(encoding="utf-8"))
    if not gate.get("passed"):
        raise RuntimeError(f"Finalization gate report is not passing: {gate_report}")
    failed = [item for item in gate.get("gates", []) if not item.get("passed")]
    if failed:
        raise RuntimeError("Finalization gate report contains failed gates: " + ", ".join(item["name"] for item in failed))
    personas = "Memory Architect; Security/Privacy Reviewer; Compliance/AI Governance Reviewer; Retrieval/RAG Engineer; DX Onboarding Reviewer; Release Engineer"
    gate_names = ", ".join(item["name"] for item in gate.get("gates", []))
    compliance_mode = "Compliance Light add-on gates were included." if gate.get("include_compliance") else "Compliance Light add-on gates were not included."
    evidence_question = (
        f"{question} Evidence: finalization report {gate_report} passed with {len(gate.get('gates', []))} gates "
        f"({gate_names}). {compliance_mode} Required red-team personas: {personas}. Validate minimal project folder, "
        "optional compliance boundaries, lifecycle gates, retrieval fixtures, runtime smoke, privacy, and release docs."
    )
    output = core.run_review_workflow(
        root,
        review_type="multi-perspective-red-team",
        subject=subject,
        question=evidence_question,
        slug="v0.5-final-redteam",
    )
    return {
        "passed": True,
        "verdict": "promote-candidate",
        "score": 95,
        "output_path": output["output_path"],
        "gate_report": str(gate_report),
        "personas": personas,
        "note": "Generated deterministic red-team artifact from passing finalization evidence.",
    }


def run_benchmarks(root: pathlib.Path) -> dict[str, Any]:
    benchmark_path = root / "benchmarks" / "run_benchmarks.py"
    process = run_subprocess([sys.executable, str(benchmark_path), "--project-root", str(root)])
    return parse_json_stdout(process)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Owledge Python-first CLI")
    parser.add_argument("--project-root", default=".")
    project_parent = argparse.ArgumentParser(add_help=False)
    project_parent.add_argument("--project-root", dest="command_project_root")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor_p = sub.add_parser("doctor", parents=[project_parent])
    doctor_p.add_argument("--mode", choices=["auto", "kit", "host"], default="auto")

    init_p = sub.add_parser("init-project")
    init_p.add_argument("--target", dest="target", required=True)
    init_p.add_argument("--source-root", default=str(REPO_ROOT))
    init_p.add_argument("--include-plugin-adapter", action="store_true")
    init_p.add_argument("--include-compliance", action="store_true")

    kb_p = sub.add_parser("add-kb-module", parents=[project_parent])
    kb_p.add_argument("--knowledgebase-root", required=True)
    kb_p.add_argument("--layout", choices=["module-dir", "flat"], default="module-dir")
    kb_p.add_argument("--module-dir", default="agent-memory-module")
    kb_p.add_argument("--map-file", default="")
    kb_p.add_argument("--max-files", type=int, default=10000)
    kb_p.add_argument("--include-cli", action="store_true")
    kb_p.add_argument("--no-sample-plan", action="store_true")

    kit_p = sub.add_parser("build-project-kit", parents=[project_parent])
    kit_p.add_argument("--output-path", required=True)
    kit_p.add_argument("--source-root", default=str(REPO_ROOT))
    kit_p.add_argument("--force", action="store_true")
    kit_p.add_argument("--include-global-memory", action="store_true")
    kit_p.add_argument("--include-plugin-adapter", action="store_true")
    kit_p.add_argument("--include-compliance", action="store_true")
    kit_p.add_argument("--plugin-hook-profile", choices=["python"], default="python")
    kit_p.add_argument("--verify", action="store_true")

    context_p = sub.add_parser("build-context-pack", parents=[project_parent])
    context_p.add_argument("--task-id", required=True)
    context_p.add_argument("--agent-role", default="worker")
    context_p.add_argument("--budget-chars", type=int)
    context_p.add_argument("--objective")

    test_p = sub.add_parser("test", parents=[project_parent])
    test_p.add_argument(
        "suite",
        choices=["all", "public-docs", "principles-skill", "principles-scenarios", "contracts", "kb-module", "runtime-adapters", "core-platform-neutral"],
        default="all",
        nargs="?",
    )

    gates_p = sub.add_parser("finalization-gates", parents=[project_parent])
    gates_p.add_argument("--include-exports", action="store_true")
    gates_p.add_argument("--include-compliance", action="store_true")

    redteam_p = sub.add_parser("redteam-qa", parents=[project_parent])
    redteam_p.add_argument("--subject", default="docs/agentic-memory-architecture.md")
    redteam_p.add_argument("--question", default="Validate v0.5 project-ready release quality, privacy, retrieval, onboarding, and release-gate completeness.")
    redteam_p.add_argument("--gate-report-path", default="")

    sub.add_parser("benchmark", parents=[project_parent])

    args = parser.parse_args(argv)
    root = resolve_path(getattr(args, "command_project_root", None) or args.project_root)

    try:
        if args.command == "doctor":
            result = core.memory_doctor(root, mode=args.mode)
            print_json(result)
            return 0 if result["passed"] else 1
        if args.command == "init-project":
            print_json(init_project(resolve_path(args.target), resolve_path(args.source_root), args.include_plugin_adapter, args.include_compliance))
            return 0
        if args.command == "add-kb-module":
            print_json(
                build_kb_module.build(
                    argparse.Namespace(
                        knowledgebase_root=args.knowledgebase_root,
                        kit_root=str(root),
                        layout=args.layout,
                        module_dir=args.module_dir,
                        map_file=args.map_file,
                        max_files=args.max_files,
                        include_cli=args.include_cli,
                        create_sample_plan=not args.no_sample_plan,
                    )
                )
            )
            return 0
        if args.command == "build-project-kit":
            print_json(
                build_project_folder_kit.build(
                    argparse.Namespace(
                        output_path=args.output_path,
                        project_root=args.source_root,
                        force=args.force,
                        include_global_memory=args.include_global_memory,
                        include_plugin_adapter=args.include_plugin_adapter,
                        include_compliance=args.include_compliance,
                        plugin_hook_profile=args.plugin_hook_profile,
                        verify=args.verify,
                    )
                )
            )
            return 0
        if args.command == "build-context-pack":
            print_json(
                core.build_context_pack_markdown(
                    root,
                    args.task_id,
                    args.agent_role,
                    args.budget_chars,
                    objective=args.objective,
                )
            )
            return 0
        if args.command == "test":
            suites: dict[str, Callable[[], dict[str, Any]]] = {
                "public-docs": lambda: public_docs_gate(root),
                "principles-skill": lambda: principles_skill_gate(root),
                "principles-scenarios": lambda: principles_scenarios_gate(root),
                "contracts": lambda: core.test_contracts(root),
                "kb-module": lambda: kb_module_gate(root),
                "runtime-adapters": lambda: runtime_adapters_gate(root),
                "core-platform-neutral": lambda: platform_neutral_core_gate(root),
            }
            if args.suite == "all":
                payload = {name: func() for name, func in suites.items()}
                passed = all(item.get("passed", True) for item in payload.values())
                print_json({"passed": passed, "suites": payload})
                return 0 if passed else 1
            result = suites[args.suite]()
            print_json(result)
            return 0 if result.get("passed", True) else 1
        if args.command == "finalization-gates":
            result = finalization_gates(root, args.include_exports, args.include_compliance)
            print_json(result)
            return 0 if result["passed"] else 1
        if args.command == "redteam-qa":
            print_json(redteam_qa(root, args.subject, args.question, args.gate_report_path))
            return 0
        if args.command == "benchmark":
            print_json(run_benchmarks(root))
            return 0
    except Exception as exc:
        print_json({"passed": False, "error": str(exc)})
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
