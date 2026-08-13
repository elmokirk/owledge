#!/usr/bin/env python3
"""Emit a compact, project-local Owledge capsule for Claude SessionStart."""

from __future__ import annotations

import json
import pathlib
import sys


def find_project_root(start: pathlib.Path) -> pathlib.Path | None:
    current = start.resolve()
    while True:
        if (current / "OWLEDGE.md").is_file() and (current / ".owledge").is_dir():
            return current
        if current.parent == current:
            return None
        current = current.parent


def compact_text(path: pathlib.Path, limit: int) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[:limit].strip()


def main() -> int:
    try:
        root = find_project_root(pathlib.Path.cwd())
        if root is None:
            print(json.dumps({"owledge": "unavailable", "hint": "Run init-project from the host project."}))
            return 0
        owledge = compact_text(root / "OWLEDGE.md", 1200)
        index = compact_text(root / ".owledge" / "indexes" / "memory-index.jsonl", 1200)
        payload = {
            "owledge": "project_local_capsule",
            "project_root": ".",
            "owledge_md": owledge,
            "memory_index": index,
            "loaded_sources": [name for name, value in (("OWLEDGE.md", owledge), (".owledge/indexes/memory-index.jsonl", index)) if value],
        }
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    except Exception:
        print(json.dumps({"owledge": "unavailable", "hint": "Run init-project from the host project."}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
