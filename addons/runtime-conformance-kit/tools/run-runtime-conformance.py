#!/usr/bin/env python3
"""Read-only AdapterManifest v1 conformance contract checker."""

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
    sys.path.insert(0, str(root / "tools"))
    try:
        import owledge_adapter_contracts as adapter_contracts
    except ImportError as exc:
        print(json.dumps({"passed": False, "failed": 1, "results": [{"name": "shared-validator", "passed": False, "details": str(exc)}]}, indent=2, sort_keys=True))
        return 1
    contract_dir = root / ".owledge" / "runtime-conformance"
    fixture_dir = contract_dir / "fixtures"
    results = []
    for name in ["codex", "claude-code", "generic-mcp-cli"]:
        path = contract_dir / f"{name}.json"
        passed = path.exists()
        details = "contract exists" if passed else "missing contract"
        if passed:
            payload = json.loads(path.read_text(encoding="utf-8"))
            errors = adapter_contracts.validate_adapter_manifest(payload)
            fixtures = payload.get("fixtures", [])
            expected = payload.get("expected_artifacts", [])
            passed = not errors and payload.get("adapter_id") == name
            for fixture in fixtures:
                fixture_name = pathlib.PurePosixPath(fixture).name
                passed = passed and (fixture_dir / fixture_name).exists()
            for artifact in expected:
                passed = passed and (root / artifact).exists()
            details = "valid AdapterManifest v1" if passed else "; ".join(errors) or "missing fixture or expected artifact"
        results.append({"name": name, "passed": passed, "details": details})
    failed = [item for item in results if not item["passed"]]
    print(json.dumps({"passed": not failed, "failed": len(failed), "results": results}, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
