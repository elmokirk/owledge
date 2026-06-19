from __future__ import annotations

import json
import pathlib
import time
from typing import Any

from . import core, modules, pi, skills


FORBIDDEN_CORE_SUFFIXES = {".ps1", ".sh", ".bat", ".cmd"}
FORBIDDEN_TEXT = [
    "power" + "shell",
    "execution" + "policy",
    "agent_memory_" + "kit_root",
    "agent_memory_" + "project_root",
]


def platform_neutral_scan(package_root: pathlib.Path) -> dict[str, Any]:
    violations = []
    for path in sorted(package_root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(package_root).as_posix()
        suffix = path.suffix.lower()
        if suffix in FORBIDDEN_CORE_SUFFIXES:
            violations.append({"path": rel, "reason": f"forbidden-wrapper:{suffix}"})
            continue
        if suffix not in {".py", ".md", ".toml", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for token in FORBIDDEN_TEXT:
            if token in text:
                violations.append({"path": rel, "reason": f"forbidden-text:{token}"})
    return {"passed": not violations, "violations": violations}


def doctor(library_root: pathlib.Path) -> dict[str, Any]:
    checks = []

    def add(name: str, passed: bool, details: str = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "details": details})

    add("library-root", library_root.exists(), str(library_root))
    add("config", (library_root / "owlib.yaml").exists(), "owlib.yaml exists")
    add("registry", (library_root / "registry" / "projects.jsonl").exists(), "registry/projects.jsonl exists")
    for relative in core.LIBRARY_DIRS:
        add(f"dir:{relative}", (library_root / relative).exists(), f"{relative} directory exists")
    failed = [check for check in checks if not check["passed"]]
    return {"passed": not failed, "failed": len(failed), "checks": checks}


def quality_gate(library_root: pathlib.Path, package_root: pathlib.Path) -> dict[str, Any]:
    gates = []

    def run(name: str, func: Any) -> None:
        started = time.perf_counter()
        try:
            payload = func()
            passed = bool(payload.get("passed", True)) if isinstance(payload, dict) else True
            gates.append({"name": name, "passed": passed, "seconds": round(time.perf_counter() - started, 3), "payload": payload})
        except Exception as exc:
            gates.append({"name": name, "passed": False, "seconds": round(time.perf_counter() - started, 3), "error": str(exc)})

    run("doctor", lambda: doctor(library_root))
    run("platform-neutral", lambda: platform_neutral_scan(package_root))
    run("module-catalog", lambda: modules.list_modules(library_root))
    run("skill-catalog", lambda: {"passed": len(skills.SKILL_NAMES) == 8, "skills": skills.SKILL_NAMES})
    run("growth-scan", lambda: core.growth_scan(library_root))
    run("pi-redteam", lambda: pi.redteam(library_root))
    failed = [gate for gate in gates if not gate["passed"]]
    summary = {
        "generated_at": core.utc_now(),
        "passed": not failed,
        "failed": len(failed),
        "gates": gates,
        "scores": {gate["name"]: 100 if gate["passed"] else 0 for gate in gates},
    }
    reports = library_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "quality-gate.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def benchmark(library_root: pathlib.Path, project_counts: list[int]) -> dict[str, Any]:
    results = []
    for count in project_counts:
        started = time.perf_counter()
        records = core.load_index_records(library_root)
        selected = records[: max(0, count)]
        tag_counts: dict[str, int] = {}
        for record in selected:
            for field in ["concept_tags", "problem_patterns", "architecture_patterns", "failure_modes"]:
                for tag in core.normalize_list(record.get("metadata", {}).get(field)):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        results.append(
            {
                "name": f"records-{count}",
                "seconds": round(time.perf_counter() - started, 6),
                "records_requested": count,
                "records_scanned": len(selected),
                "signals": len(tag_counts),
            }
        )
    payload = {"passed": True, "generated_at": core.utc_now(), "scenarios": results}
    out = library_root / "reports" / "benchmark.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
