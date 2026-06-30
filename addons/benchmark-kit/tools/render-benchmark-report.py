#!/usr/bin/env python3
"""Re-render Owledge Benchmark Kit HTML/SVG/Markdown outputs from latest JSON."""

from __future__ import annotations

import argparse
import json
import pathlib
import runpy
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the latest Owledge Benchmark Kit report.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--input", default="")
    parser.add_argument("--format", choices=["html"], default="html")
    args = parser.parse_args(argv)
    root = pathlib.Path(args.project_root).resolve()
    input_path = pathlib.Path(args.input).resolve() if args.input else root / ".owledge" / "exports" / "benchmark-kit" / "latest.json"
    if not input_path.exists():
        print(json.dumps({"passed": False, "error": f"Benchmark input not found: {input_path}"}, indent=2))
        return 1
    runner_path = pathlib.Path(__file__).resolve().parent / "run-benchmark-kit.py"
    namespace = runpy.run_path(str(runner_path))
    results = json.loads(input_path.read_text(encoding="utf-8"))
    paths = namespace["write_reports"](root, results)
    print(json.dumps({"passed": True, "input": str(input_path), "paths": paths}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
