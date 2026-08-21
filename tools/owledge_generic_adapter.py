#!/usr/bin/env python3
"""Thin stdio JSON-RPC reference adapter for generic Owledge V1 harnesses.

It exposes exactly the five V1 MCP operations and delegates every read or
lifecycle request to the local Core. It owns no storage, index or transition.
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
import owledge_v1_lifecycle as lifecycle  # noqa: E402
import owledge_v1_retrieval as retrieval  # noqa: E402


TOOLS = [
    {"name": "owledge_capabilities", "description": "Read the bound V1 Core capabilities and adapter manifest.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "owledge_recall", "description": "Delegate deterministic scoped recall to the local Core.", "inputSchema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}, "purpose": {"type": "string", "enum": ["research", "planning"]}, "scopes": {"type": "array", "items": {"type": "string"}}, "include_user_global": {"type": "boolean"}}}},
    {"name": "owledge_context", "description": "Delegate a bounded local context pack to the Core.", "inputSchema": {"type": "object", "required": ["task_id"], "properties": {"task_id": {"type": "string"}, "objective": {"type": "string"}, "purpose": {"type": "string", "enum": ["research", "planning"]}, "budget_chars": {"type": "integer"}, "scopes": {"type": "array", "items": {"type": "string"}}, "include_user_global": {"type": "boolean"}}}},
    {"name": "owledge_propose", "description": "Delegate one explicit private project Candidate to the Core.", "inputSchema": {"type": "object", "required": ["kind", "summary", "source_refs"], "properties": {"kind": {"type": "string"}, "summary": {"type": "string"}, "source_refs": {"type": "array", "items": {"type": "string"}}, "park": {"type": "boolean"}, "park_reason": {"type": "string"}, "reconsider_when": {"type": "string"}}}},
    {"name": "owledge_review", "description": "Delegate an explicit revision-bound Candidate review to the Core.", "inputSchema": {"type": "object", "required": ["candidate_id", "action", "expected_revision"], "properties": {"candidate_id": {"type": "string"}, "action": {"type": "string", "enum": sorted(lifecycle.REVIEW_ACTIONS)}, "expected_revision": {"type": "string"}, "reason": {"type": "string"}, "reconsider_when": {"type": "string"}, "superseded_by": {"type": "string"}}}},
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
    if not contracts.core_version_compatible(payload["core_api_range"]):
        raise ValueError("core_api_incompatible")
    return payload


def _scopes(arguments: dict[str, Any]) -> set[str] | None:
    value = arguments.get("scopes")
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("invalid_scopes")
    return set(value)


def call_tool(name: str, arguments: dict[str, Any], root: pathlib.Path, manifest: dict[str, Any]) -> dict[str, Any]:
    if name == "owledge_capabilities":
        return _content({"passed": True, "manifest": manifest, "mcp_tools": [item["name"].removeprefix("owledge_") for item in TOOLS], "scopes": ["project_user", "user_global"], "delegation": "core_owned", "network": "disabled"})
    if name == "owledge_recall":
        return _content(retrieval.recall(root, query=str(arguments.get("query") or ""), purpose=str(arguments.get("purpose") or "research"), scopes=_scopes(arguments), include_user_global=bool(arguments.get("include_user_global", False))))
    if name == "owledge_context":
        budget = arguments.get("budget_chars", 4000)
        if not isinstance(budget, int):
            raise ValueError("invalid_budget_chars")
        return _content(retrieval.build_context_pack(root, task_id=str(arguments.get("task_id") or ""), objective=str(arguments.get("objective") or ""), purpose=str(arguments.get("purpose") or "research"), budget_chars=budget, scopes=_scopes(arguments), include_user_global=bool(arguments.get("include_user_global", False))))
    if name == "owledge_propose":
        source_refs = arguments.get("source_refs")
        if not isinstance(source_refs, list) or not all(isinstance(item, str) for item in source_refs):
            raise ValueError("invalid_source_refs")
        return _content(lifecycle.propose(root, kind=str(arguments.get("kind") or ""), summary=str(arguments.get("summary") or ""), source_refs=source_refs, park=bool(arguments.get("park", False)), park_reason=str(arguments.get("park_reason") or ""), reconsider_when=str(arguments.get("reconsider_when") or "")))
    if name == "owledge_review":
        return _content(lifecycle.review(root, candidate_id=str(arguments.get("candidate_id") or ""), action=str(arguments.get("action") or ""), expected_revision=str(arguments.get("expected_revision") or ""), reason=str(arguments.get("reason") or ""), reconsider_when=str(arguments.get("reconsider_when") or ""), superseded_by=str(arguments.get("superseded_by") or "")))
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
    parser = argparse.ArgumentParser(description="Generic Owledge MCP/CLI stdio adapter with Candidate-only writes")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--manifest", default=None)
    args = parser.parse_args(argv)
    root = pathlib.Path(args.project_root).expanduser().resolve()
    try:
        _ensure_bound_project(root)
        manifest_path = (root / ".owledge" / "runtime-conformance" / "generic-mcp-cli.json").resolve()
        if args.manifest and pathlib.Path(args.manifest).expanduser().resolve() != manifest_path:
            raise ValueError("manifest_override_denied")
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
