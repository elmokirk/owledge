#!/usr/bin/env python3
"""Reproducible local Owledge benchmark harness."""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import agent_memory_cli as core  # noqa: E402
import build_kb_module  # noqa: E402
import owledge  # noqa: E402


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def measure(name: str, action):
    started = time.perf_counter()
    data = action()
    return {"name": name, "seconds": round(time.perf_counter() - started, 3), "data": data}


def new_synthetic_vault(path: pathlib.Path, count: int) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for index in range(1, count + 1):
        next_link = f"[[note-{index + 1}]]" if index < count else "[[note-1]]"
        write_text(path / f"note-{index}.md", f"# Note {index}\n\nThis is a benchmark note.\n\n- link: {next_link}\n- tag: benchmark\n")


def run(project_root: pathlib.Path) -> dict:
    project_root = project_root.resolve()
    results_dir = project_root / "benchmarks" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    tmp_root = project_root / ".agent-control" / "tmp" / f"owledge-benchmarks-{next(tempfile._get_candidate_names())}"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True)
    try:
        vault_root = tmp_root / "vault"
        new_synthetic_vault(vault_root, 100)

        kb_step = measure(
            "kb-scan",
            lambda: {
                key: value
                for key, value in build_kb_module.build(
                    argparse.Namespace(
                        knowledgebase_root=str(vault_root),
                        kit_root=str(project_root),
                        layout="module-dir",
                        module_dir="agent-memory-module",
                        map_file="",
                        max_files=1000,
                        include_cli=True,
                        create_sample_plan=True,
                    )
                ).items()
                if key in {"markdown_files_scanned", "existing_kb_files_modified", "index_path", "module_root"}
            },
        )

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

        report = {
            "generated_at": core.utc_now(),
            "project": str(project_root),
            "scenarios": [kb_step, context_step, runtime_step],
        }
        json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        (results_dir / "latest.json").write_text(json_text, encoding="utf-8")
        lines = [
            "# Benchmark Results",
            "",
            f"- Generated at: {report['generated_at']}",
            "",
            "## Scenarios",
            "",
        ]
        for scenario in report["scenarios"]:
            lines.append(f"- {scenario['name']}: {scenario['seconds']}s")
        (results_dir / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report
    finally:
        if tmp_root.exists():
            shutil.rmtree(tmp_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local Owledge benchmark scenarios.")
    parser.add_argument("--project-root", default=str(ROOT))
    args = parser.parse_args(argv)
    print(json.dumps(run(pathlib.Path(args.project_root)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
