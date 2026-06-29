#!/usr/bin/env python3
"""Read-only MCP-style stdio server for Owledge.

This intentionally uses only the Python standard library. It implements the
small JSON-RPC surface needed for read-only agent discovery while keeping
Markdown as the source of truth.
"""

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import owledge_core as core  # noqa: E402


TOOLS = [
    {
        "name": "owledge_read_entrypoint",
        "description": "Read OWLEDGE.md, falling back to OWLEDGE.md for legacy projects.",
        "inputSchema": {"type": "object", "properties": {"project_root": {"type": "string"}}, "required": []},
    },
    {
        "name": "owledge_doctor",
        "description": "Run read-only Owledge doctor checks.",
        "inputSchema": {"type": "object", "properties": {"project_root": {"type": "string"}}, "required": []},
    },
    {
        "name": "owledge_search_memory",
        "description": "Search reviewed/tracked Markdown memory records.",
        "inputSchema": {"type": "object", "properties": {"project_root": {"type": "string"}, "query": {"type": "string"}}, "required": ["query"]},
    },
    {
        "name": "owledge_build_context_pack",
        "description": "Build a scoped context pack for a task without writing files.",
        "inputSchema": {"type": "object", "properties": {"project_root": {"type": "string"}, "task_id": {"type": "string"}, "objective": {"type": "string"}}, "required": ["task_id"]},
    },
    {
        "name": "owledge_list_tasks",
        "description": "List task and workpackage Markdown artifacts.",
        "inputSchema": {"type": "object", "properties": {"project_root": {"type": "string"}}, "required": []},
    },
    {
        "name": "owledge_list_reviews",
        "description": "List review Markdown artifacts.",
        "inputSchema": {"type": "object", "properties": {"project_root": {"type": "string"}}, "required": []},
    },
]


def _root(args: dict[str, Any]) -> pathlib.Path:
    return pathlib.Path(str(args.get("project_root") or ".")).expanduser().resolve()


def _content(payload: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, indent=2, sort_keys=True)}]}


def _list_markdown(root: pathlib.Path, rels: list[str]) -> list[str]:
    rows: list[str] = []
    for rel in rels:
        base = root / rel
        if base.is_file():
            rows.append(base.relative_to(root).as_posix())
        elif base.is_dir():
            rows.extend(path.relative_to(root).as_posix() for path in sorted(base.rglob("*.md")))
    return rows


def call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    root = _root(args)
    if name == "owledge_read_entrypoint":
        path = root / "OWLEDGE.md"
        if not path.is_file():
            path = root / "OWLEDGE.md"
        if not path.is_file():
            return _content({"passed": False, "error": "No OWLEDGE.md entrypoint found."})
        return _content({"path": path.relative_to(root).as_posix(), "text": path.read_text(encoding="utf-8", errors="replace")})
    if name == "owledge_doctor":
        return _content(core.memory_doctor(root, mode="auto"))
    if name == "owledge_search_memory":
        query = str(args.get("query") or "").lower()
        rows = []
        for record in core.load_memory_records(root, include_sessions=False):
            haystack = " ".join(
                [
                    str(record["metadata"].get("semantic_title", "")),
                    str(record["metadata"].get("summary", "")),
                    record["body"][:2000],
                ]
            ).lower()
            if query in haystack:
                rows.append({"source_path": record["source_path"], "memory_id": record["metadata"].get("memory_id"), "summary": record["metadata"].get("summary", "")})
        return _content({"query": query, "results": rows[:25]})
    if name == "owledge_build_context_pack":
        return _content(core.build_context_pack_markdown(root, str(args["task_id"]), objective=args.get("objective")))
    if name == "owledge_list_tasks":
        return _content({"tasks": _list_markdown(root, [".owledge/tasks", ".owledge/workpackages", ".owledge/plans"])})
    if name == "owledge_list_reviews":
        return _content({"reviews": _list_markdown(root, [".owledge/reviews", ".owledge/pi-agent/red-team", ".owledge/pi-agent/evaluations"])})
    raise ValueError(f"Unknown tool: {name}")


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    msg_id = message.get("id")
    try:
        if method == "initialize":
            result = {"protocolVersion": "2024-11-05", "serverInfo": {"name": "owledge-readonly", "version": "0.7.0"}, "capabilities": {"tools": {}}}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            params = message.get("params") or {}
            result = call_tool(str(params.get("name")), params.get("arguments") or {})
        elif method == "notifications/initialized":
            return None
        else:
            raise ValueError(f"Unsupported method: {method}")
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}
    except Exception as exc:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32000, "message": str(exc)}}


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = handle(json.loads(line))
        if response is not None:
            sys.stdout.write(json.dumps(response, sort_keys=True) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

