#!/usr/bin/env python3
"""Bounded stdio JSON-RPC reference adapter for generic Owledge harnesses.

The adapter is intentionally read-only.  It exposes capability negotiation and
an owner-invoked pre-plan capsule; Candidate writes remain a Core-owned,
reviewed boundary even though the shared manifest can declare that capability.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import owledge_adapter_contracts as contracts  # noqa: E402


TOOLS = [
    {"name": "owledge_capability_discovery", "description": "Read the bound generic MCP/CLI AdapterManifest v1.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "owledge_negotiate_capability", "description": "Negotiate one declared capability without granting implicit authority.", "inputSchema": {"type": "object", "required": ["capability_id", "scope", "permissions"], "properties": {"capability_id": {"type": "string"}, "scope": {"type": "string"}, "permissions": {"type": "array", "items": {"type": "string"}}}}},
    {"name": "owledge_preplan_capsule", "description": "Read a bounded owner-invoked project capsule; this does not inspect or route a plan automatically.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "owledge_candidate_boundary", "description": "Describe the explicit Candidate and promotion boundary without performing a write.", "inputSchema": {"type": "object", "properties": {}}},
]


def _content(payload: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, sort_keys=True)}]}


def _ensure_bound_project(root: pathlib.Path) -> None:
    if not (root / "OWLEDGE.md").is_file() or not (root / ".owledge").is_dir():
        raise ValueError("unknown_project: bound project must contain OWLEDGE.md and .owledge/")


def _load_manifest(path: pathlib.Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"manifest_unavailable: {exc}") from exc
    errors = contracts.validate_adapter_manifest(payload)
    if errors:
        raise ValueError("manifest_invalid: " + ",".join(errors))
    if payload.get("adapter_id") != "generic-mcp-cli":
        raise ValueError("manifest_profile_mismatch")
    return payload


def _capsule(root: pathlib.Path) -> dict[str, Any]:
    sources = [root / "OWLEDGE.md", root / ".owledge" / "indexes" / "memory-index.jsonl"]
    rows: list[dict[str, str]] = []
    for source in sources:
        if source.is_file():
            text = source.read_text(encoding="utf-8", errors="replace")[:2000]
            rows.append({"path": source.relative_to(root).as_posix(), "text": text})
    return {
        "result": "supported",
        "reason_code": "owner_invoked_read_only",
        "automatic_preplan_inspection": False,
        "loaded_sources": [row["path"] for row in rows],
        "sources": rows,
    }


def call_tool(name: str, arguments: dict[str, Any], root: pathlib.Path, manifest: dict[str, Any]) -> dict[str, Any]:
    if name == "owledge_capability_discovery":
        return _content({"manifest": manifest, "write_enabled": False})
    if name == "owledge_negotiate_capability":
        permissions = arguments.get("permissions")
        if not isinstance(permissions, list) or not all(isinstance(value, str) for value in permissions):
            raise ValueError("invalid_permissions")
        return _content(contracts.negotiate(manifest, capability_id=str(arguments.get("capability_id", "")), scope=str(arguments.get("scope", "")), requested_permissions=permissions))
    if name == "owledge_preplan_capsule":
        return _content(_capsule(root))
    if name == "owledge_candidate_boundary":
        return _content({"result": "unsupported", "reason_code": "candidate_write_requires_core_review_flow", "write_enabled": False, "promotion": "not_available"})
    raise ValueError(f"tool_mismatch: {name}")


def handle(message: Any, root: pathlib.Path, manifest: dict[str, Any]) -> dict[str, Any] | None:
    msg_id = message.get("id") if isinstance(message, dict) else None
    try:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            raise ValueError("malformed_json_rpc")
        method = message.get("method")
        if method == "initialize":
            result: Any = {"protocolVersion": "2024-11-05", "serverInfo": {"name": "owledge-generic-adapter", "version": "1.0"}, "capabilities": {"tools": {}}}
        elif method == "notifications/initialized":
            return None
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            params = message.get("params")
            if not isinstance(params, dict) or not isinstance(params.get("arguments", {}), dict):
                raise ValueError("malformed_tool_call")
            result = call_tool(str(params.get("name", "")), params.get("arguments", {}), root, manifest)
        else:
            raise ValueError(f"unsupported_method: {method}")
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}
    except Exception as exc:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32000, "message": str(exc)}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generic read-only Owledge MCP/CLI stdio adapter")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--manifest", default=None)
    args = parser.parse_args(argv)
    root = pathlib.Path(args.project_root).expanduser().resolve()
    try:
        _ensure_bound_project(root)
        manifest_path = pathlib.Path(args.manifest).resolve() if args.manifest else root / ".owledge" / "runtime-conformance" / "generic-mcp-cli.json"
        manifest = _load_manifest(manifest_path)
    except ValueError as exc:
        parser.error(str(exc))
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message: Any = json.loads(raw)
        except json.JSONDecodeError:
            message = None
        response = handle(message, root, manifest)
        if response is not None:
            sys.stdout.write(json.dumps(response, sort_keys=True) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
