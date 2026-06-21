#!/usr/bin/env python3
"""Build a lightweight cross-project learning map from shared Markdown files."""

from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    root = pathlib.Path(args.project_root).resolve()
    shared = root / "shared"
    out_dir = root / "agent-memory" / "cross-project-hub"
    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    if shared.exists():
        for path in sorted(shared.rglob("*.md")):
            records.append({"path": str(path.relative_to(root)), "kind": path.parent.name, "bytes": path.stat().st_size})
    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "records": records,
        "note": "Generated view. Shared Markdown remains the source of truth.",
    }
    (out_dir / "cross-project-map.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"path": "agent-memory/cross-project-hub/cross-project-map.json", "records": len(records)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

