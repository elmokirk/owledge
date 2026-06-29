#!/usr/bin/env python3
"""Reproducible local Owledge benchmark harness."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import tracemalloc

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import owledge_core as core  # noqa: E402
import build_kb_module  # noqa: E402
import owledge  # noqa: E402


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def measure(name: str, action):
    tracemalloc.start()
    started = time.perf_counter()
    data = action()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "name": name,
        "seconds": round(time.perf_counter() - started, 3),
        "peak_python_bytes": peak,
        "data": data,
    }


def git_sha(project_root: pathlib.Path) -> str:
    process = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(project_root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return process.stdout.strip() if process.returncode == 0 else "unknown"


def new_synthetic_vault(path: pathlib.Path, count: int) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for index in range(1, count + 1):
        next_link = f"[[note-{index + 1}]]" if index < count else "[[note-1]]"
        write_text(path / f"note-{index}.md", f"# Note {index}\n\nThis is a benchmark note.\n\n- link: {next_link}\n- tag: benchmark\n")


def run(project_root: pathlib.Path, scale_files: list[int], seed: int) -> dict:
    project_root = project_root.resolve()
    results_dir = project_root / "benchmarks" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    tmp_root = project_root / ".agent-control" / "tmp" / f"owledge-benchmarks-{next(tempfile._get_candidate_names())}"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True)
    try:
        scenarios = []
        for count in scale_files:
            vault_root = tmp_root / f"vault-{count}"
            new_synthetic_vault(vault_root, count)

            def scan(vault=vault_root, count=count):
                result = {
                    key: value
                    for key, value in build_kb_module.build(
                        argparse.Namespace(
                            knowledgebase_root=str(vault),
                            kit_root=str(project_root),
                            layout="module-dir",
                            module_dir="owledge-module",
                            map_file="",
                            max_files=count,
                            include_cli=True,
                            create_sample_plan=True,
                        )
                    ).items()
                    if key in {"markdown_files_scanned", "existing_kb_files_modified", "index_path", "module_root", "markdown_scan_truncated"}
                }
                index_path = vault / "owledge-module" / "owledge" / "indexes" / "kb-scan.jsonl"
                result["output_bytes"] = index_path.stat().st_size if index_path.exists() else 0
                return result

            step = measure(f"kb-scan-{count}", scan)
            scanned = step["data"].get("markdown_files_scanned") or 0
            step["data"]["records_per_second"] = round(scanned / step["seconds"], 2) if step["seconds"] else scanned
            scenarios.append(step)

        context_step = measure(
            "context-pack",
            lambda: {
                key: value
                for key, value in core.build_context_pack_markdown(
                    project_root,
                    "benchmark-release",
                    "worker",
                    2400,
                    objective="Measure scoped context behavior",
                    tenant_id="owledge",
                    customer_id="global",
                    project_id="owledge",
                ).items()
                if key in {"estimated_tokens", "included_sources", "dropped_sources", "raw_chars_available"}
            },
        )
        context_data = context_step["data"]
        context_data["included_sources"] = len(context_data.get("included_sources") or [])

        runtime_step = measure(
            "runtime-handoff",
            lambda: owledge.runtime_adapters_gate(project_root),
        )
        runtime_data = runtime_step["data"]
        summary_path = pathlib.Path(runtime_data["session_dir"]) / "summary.md"
        runtime_step["data"] = {
            "passed": runtime_data["passed"],
            "checked_files": len(runtime_data["checked_files"]),
            "summary_bytes": summary_path.stat().st_size if summary_path.exists() else 0,
        }

        scenarios.extend([context_step, runtime_step])
        report = {
            "generated_at": core.utc_now(),
            "project": str(project_root),
            "metadata": {
                "commit": git_sha(project_root),
                "os": platform.platform(),
                "python": sys.version.split()[0],
                "cpu_count": os.cpu_count(),
                "command": f"python tools/owledge.py benchmark --project-root . --scale-files {','.join(str(item) for item in scale_files)} --seed {seed}",
                "seed": seed,
                "scale_files": scale_files,
            },
            "scenarios": scenarios,
        }
        json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        (results_dir / "latest.json").write_text(json_text, encoding="utf-8")
        lines = [
            "# Benchmark Results",
            "",
            f"- Generated at: {report['generated_at']}",
            f"- Commit: `{report['metadata']['commit']}`",
            f"- Python: `{report['metadata']['python']}`",
            f"- OS: `{report['metadata']['os']}`",
            "",
            "## Scenarios",
            "",
        ]
        for scenario in report["scenarios"]:
            lines.append(f"- {scenario['name']}: {scenario['seconds']}s, peak Python bytes {scenario['peak_python_bytes']}")
        (results_dir / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report
    finally:
        if tmp_root.exists():
            shutil.rmtree(tmp_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local Owledge benchmark scenarios.")
    parser.add_argument("--project-root", default=str(ROOT))
    parser.add_argument("--scale-files", default="100", help="Comma-separated synthetic vault sizes, for example 100,1000,10000.")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args(argv)
    scale_files = [int(item.strip()) for item in args.scale_files.split(",") if item.strip()]
    print(json.dumps(run(pathlib.Path(args.project_root), scale_files, args.seed), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
