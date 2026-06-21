#!/usr/bin/env python3
"""Read-only runtime conformance contract checker."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Owledge runtime conformance contracts.")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    root = pathlib.Path(args.project_root).resolve()
    contract_dir = root / "agent-memory" / "runtime-conformance"
    fixture_dir = contract_dir / "fixtures"
    results = []
    for name in ["codex", "claude-code", "cowork-compatible"]:
        path = contract_dir / f"{name}.json"
        passed = path.exists()
        details = "contract exists" if passed else "missing contract"
        if passed:
            payload = json.loads(path.read_text(encoding="utf-8"))
            fixtures = payload.get("fixtures", [])
            expected = payload.get("expected_artifacts", [])
            passed = bool(fixtures) and bool(expected)
            for fixture in fixtures:
                fixture_name = pathlib.PurePosixPath(fixture).name
                passed = passed and (fixture_dir / fixture_name).exists()
            details = f"{len(fixtures)} fixtures, {len(expected)} expected artifacts"
        results.append({"name": name, "passed": passed, "details": details})
    failed = [item for item in results if not item["passed"]]
    print(json.dumps({"passed": not failed, "failed": len(failed), "results": results}, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

