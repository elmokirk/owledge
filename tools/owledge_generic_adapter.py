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


CURRENT_PROTOCOL_VERSION = "2026-07-28"
LEGACY_PROTOCOL_VERSION = "2024-11-05"
PROTOCOL_VERSION_META_KEY = "io.modelcontextprotocol/protocolVersion"


TOOLS = [
    {"name": "owledge_capabilities", "description": "Read the bound V1 Core capabilities and adapter manifest.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "owledge_recall", "description": "Delegate deterministic scoped recall to the local Core.", "inputSchema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}, "purpose": {"type": "string", "enum": ["research", "planning"]}, "scopes": {"type": "array", "items": {"type": "string"}}, "include_user_global": {"type": "boolean"}}}},
    {"name": "owledge_context", "description": "Delegate a bounded local context pack to the Core.", "inputSchema": {"type": "object", "required": ["task_id"], "properties": {"task_id": {"type": "string"}, "objective": {"type": "string"}, "purpose": {"type": "string", "enum": ["research", "planning"]}, "budget_chars": {"type": "integer"}, "scopes": {"type": "array", "items": {"type": "string"}}, "include_user_global": {"type": "boolean"}}}},
    {"name": "owledge_propose", "description": "Delegate one explicit private project Candidate to the Core.", "inputSchema": {"type": "object", "required": ["kind", "summary", "source_refs"], "properties": {"kind": {"type": "string"}, "summary": {"type": "string"}, "source_refs": {"type": "array", "items": {"type": "string"}}, "park": {"type": "boolean"}, "park_reason": {"type": "string"}, "reconsider_when": {"type": "string"}}}},
    {"name": "owledge_review", "description": "Delegate an explicit revision-bound Candidate review to the Core.", "inputSchema": {"type": "object", "required": ["candidate_id", "action", "expected_revision"], "properties": {"candidate_id": {"type": "string"}, "action": {"type": "string", "enum": sorted(lifecycle.REVIEW_ACTIONS)}, "expected_revision": {"type": "string"}, "reason": {"type": "string"}, "reconsider_when": {"type": "string"}, "superseded_by": {"type": "string"}}}},
]


def _content(payload: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, sort_keys=True)}]}


class ProtocolVersionError(ValueError):
    """A protocol-version refusal with the MCP-defined error code."""

    def __init__(self, requested: str | None) -> None:
        self.requested = requested
        super().__init__("unsupported_protocol_version" if requested else "protocol_version_required")


def _request_protocol_version(message: dict[str, Any]) -> str | None:
    params = message.get("params", {})
    if not isinstance(params, dict):
        return None
    meta = params.get("_meta", {})
    if not isinstance(meta, dict):
        raise ValueError("malformed_request_metadata")
    value = meta.get(PROTOCOL_VERSION_META_KEY)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("malformed_protocol_version")
    return value


def _modern_discovery() -> dict[str, Any]:
    return {
        "resultType": "complete",
        "supportedVersions": [CURRENT_PROTOCOL_VERSION],
        "capabilities": {"tools": {}},
        "_meta": {"io.modelcontextprotocol/serverInfo": {"name": "owledge-generic-adapter", "version": "1.0"}},
        "instructions": "Local Owledge V1 Core only. Network access and direct storage access are disabled.",
        "ttlMs": 3600000,
        "cacheScope": "private",
    }


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


def handle(message: Any, root: pathlib.Path, manifest: dict[str, Any], session: dict[str, str | None] | None = None) -> dict[str, Any] | None:
    session = session if session is not None else {"protocol_version": None}
    msg_id = message.get("id") if isinstance(message, dict) else None
    try:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            raise ValueError("malformed_json_rpc")
        method = message.get("method")
        if method == "server/discover":
            requested = _request_protocol_version(message)
            if requested != CURRENT_PROTOCOL_VERSION:
                raise ProtocolVersionError(requested)
            session["protocol_version"] = CURRENT_PROTOCOL_VERSION
            result: Any = _modern_discovery()
        elif method == "initialize":
            params = message.get("params", {})
            requested = params.get("protocolVersion") if isinstance(params, dict) else None
            if requested not in (None, LEGACY_PROTOCOL_VERSION):
                raise ProtocolVersionError(requested if isinstance(requested, str) else None)
            session["protocol_version"] = LEGACY_PROTOCOL_VERSION
            result = {"protocolVersion": LEGACY_PROTOCOL_VERSION, "serverInfo": {"name": "owledge-generic-adapter", "version": "1.0"}, "capabilities": {"tools": {}}}
        elif method == "notifications/initialized":
            return None
        else:
            requested = _request_protocol_version(message)
            if requested is not None:
                if requested != CURRENT_PROTOCOL_VERSION:
                    raise ProtocolVersionError(requested)
                session["protocol_version"] = CURRENT_PROTOCOL_VERSION
            elif session["protocol_version"] == CURRENT_PROTOCOL_VERSION:
                raise ProtocolVersionError(None)
            else:
                # Old 2024-11-05 clients did not attach request metadata. Keep
                # their isolated stdio flow working without advertising it as
                # the current protocol path.
                session["protocol_version"] = LEGACY_PROTOCOL_VERSION
            if method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                params = message.get("params")
                if not isinstance(params, dict) or not isinstance(params.get("arguments", {}), dict):
                    raise ValueError("malformed_tool_call")
                result = call_tool(str(params.get("name", "")), params.get("arguments", {}), root, manifest)
            else:
                raise ValueError(f"unsupported_method: {method}")
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}
    except ProtocolVersionError as exc:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32022, "message": "Unsupported protocol version", "data": {"supported": [CURRENT_PROTOCOL_VERSION, LEGACY_PROTOCOL_VERSION], "requested": exc.requested}}}
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
    session: dict[str, str | None] = {"protocol_version": None}
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message: Any = json.loads(raw)
        except json.JSONDecodeError:
            message = None
        response = handle(message, root, manifest, session)
        if response is not None:
            sys.stdout.write(json.dumps(response, sort_keys=True) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
