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
import owledge_context_profiles as context_profiles  # noqa: E402


TOOLS = [
    {
        "name": "owledge_read_entrypoint",
        "description": "Read the bound project's OWLEDGE.md entrypoint.",
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
    {"name": "owledge_context_synopsis", "description": "Return a bounded, non-canonical synopsis for a selected memory record.", "inputSchema": {"type": "object", "properties": {"project_root": {"type": "string"}, "memory_id": {"type": "string"}}, "required": ["memory_id"]}},
    {"name": "owledge_active_tools", "description": "Return only the allowlisted tools for an explicit task class.", "inputSchema": {"type": "object", "properties": {"project_root": {"type": "string"}, "task_class": {"enum": ["orientation", "retrieval", "delivery"]}}, "required": ["task_class"]}},
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


def _root(args: dict[str, Any], bound_root: pathlib.Path) -> pathlib.Path:
    requested = args.get("project_root")
    if requested is None:
        return bound_root
    candidate = pathlib.Path(str(requested)).expanduser().resolve()
    if candidate != bound_root:
        raise ValueError("project_root is bound when the Owledge MCP server starts; restart the server for a different project.")
    return bound_root


def _ensure_within(bound_root: pathlib.Path, candidate: pathlib.Path, label: str) -> None:
    try:
        candidate.resolve().relative_to(bound_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} resolves outside the bound project and is not readable through this MCP server.") from exc


def _validate_bound_project(bound_root: pathlib.Path) -> None:
    entrypoint = bound_root / "OWLEDGE.md"
    if not entrypoint.is_file():
        raise ValueError(f"Missing OWLEDGE.md in bound project: {bound_root}")
    _ensure_within(bound_root, entrypoint, "OWLEDGE.md")
    memory = bound_root / ".owledge"
    if memory.exists():
        _ensure_within(bound_root, memory, ".owledge")
        for path in memory.rglob("*"):
            _ensure_within(bound_root, path, path.relative_to(bound_root).as_posix())


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


def call_tool(name: str, args: dict[str, Any], bound_root: pathlib.Path) -> dict[str, Any]:
    root = _root(args, bound_root)
    _validate_bound_project(root)
    if name == "owledge_read_entrypoint":
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
    if name == "owledge_context_synopsis":
        for record in core.load_memory_records(root, include_sessions=False):
            if record["metadata"].get("memory_id") == args["memory_id"]:
                return _content(context_profiles.synopsis(record["body"], str(record["metadata"].get("summary", "")), source_revision=str(record.get("source_hash") or record["metadata"].get("source_hash") or "unknown")))
        return _content({"passed": False, "error": "memory_id.not_found"})
    if name == "owledge_active_tools":
        return _content(context_profiles.active_tools(str(args["task_class"]), {item["name"] for item in TOOLS}))
    if name == "owledge_list_tasks":
        return _content({"tasks": _list_markdown(root, [".owledge/tasks", ".owledge/workpackages", ".owledge/plans"])})
    if name == "owledge_list_reviews":
        return _content({"reviews": _list_markdown(root, [".owledge/reviews", ".owledge/pi-agent/red-team", ".owledge/pi-agent/evaluations"])})
    raise ValueError(f"Unknown tool: {name}")


def handle(message: dict[str, Any], bound_root: pathlib.Path) -> dict[str, Any] | None:
    method = message.get("method")
    msg_id = message.get("id")
    try:
        if method == "initialize":
            result = {"protocolVersion": "2024-11-05", "serverInfo": {"name": "owledge-readonly", "version": "0.7.1"}, "capabilities": {"tools": {}}}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            params = message.get("params") or {}
            result = call_tool(str(params.get("name")), params.get("arguments") or {}, bound_root)
        elif method == "notifications/initialized":
            return None
        else:
            raise ValueError(f"Unsupported method: {method}")
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}
    except Exception as exc:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32000, "message": str(exc)}}


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Read-only Owledge MCP stdio server")
    parser.add_argument("--project-root", required=True, help="Bind this server instance to exactly one Owledge project.")
    args = parser.parse_args(argv)
    bound_root = pathlib.Path(args.project_root).expanduser().resolve()
    try:
        _validate_bound_project(bound_root)
    except ValueError as exc:
        parser.error(str(exc))
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = handle(json.loads(line), bound_root)
        if response is not None:
            sys.stdout.write(json.dumps(response, sort_keys=True) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
