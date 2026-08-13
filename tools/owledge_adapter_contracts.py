#!/usr/bin/env python3
"""Fail-closed AdapterManifest v1 validation and capability negotiation.

This deliberately small, standard-library-only module is the shared adapter
boundary for Codex, Claude Code, and generic MCP/CLI.  It declares what an
adapter may ask the Core to do; it never grants access to Core storage paths.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any


CURRENT_CORE_API_VERSION = "0.8.1"
ADAPTER_IDS = {"codex", "claude-code", "generic-mcp-cli"}
LOCAL_SCOPES = {"project_user", "user_global"}
REQUIRED_PERMISSIONS = {"read_project", "read_user_global", "write_candidate"}
REQUIRED_CAPABILITIES = {"context.read", "control.read", "checkpoint.handoff", "candidate.write"}
UNSUPPORTED_CAPABILITIES = {
    "preplan.auto_inspect",
    "routing.durable",
    "core.storage.direct",
    "scope.enterprise",
    "orchestration.dispatch",
}
FIXTURE_PATHS = {"fixtures/session-start.json", "fixtures/user-prompt.json"}
CAPABILITY_PERMISSIONS = {
    "control.read": {"read_project"},
    "checkpoint.handoff": {"read_project"},
    "candidate.write": {"write_candidate"},
}
_RANGE = re.compile(r"^>=(\d+)\.(\d+)\.(\d+),<(\d+)\.(\d+)\.(\d+)$")


def _version(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def _error(errors: list[str], code: str) -> None:
    if code not in errors:
        errors.append(code)


def validate_adapter_manifest(document: Any) -> list[str]:
    """Return deterministic validation codes; unknown or missing declarations fail."""
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["manifest.type"]
    required = {
        "manifest_version", "adapter_id", "core_api_range", "granted_permissions",
        "context_scopes", "supported_capabilities", "unsupported_capabilities",
    }
    optional = {"fixtures", "expected_artifacts", "failure_modes"}
    for key in sorted(required - set(document)):
        _error(errors, f"manifest.missing:{key}")
    for key in sorted(set(document) - required - optional):
        _error(errors, f"manifest.unknown:{key}")
    if document.get("manifest_version") != "1.0":
        _error(errors, "manifest.version")
    if document.get("adapter_id") not in ADAPTER_IDS:
        _error(errors, "manifest.adapter_id")
    raw_range = document.get("core_api_range")
    if not isinstance(raw_range, str) or not _RANGE.fullmatch(raw_range):
        _error(errors, "manifest.core_api_range")
    for name, allowed, required_values in [
        ("granted_permissions", REQUIRED_PERMISSIONS, REQUIRED_PERMISSIONS),
        ("context_scopes", LOCAL_SCOPES, LOCAL_SCOPES),
        ("supported_capabilities", REQUIRED_CAPABILITIES, REQUIRED_CAPABILITIES),
    ]:
        value = document.get(name)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            _error(errors, f"manifest.{name}")
            continue
        items = set(value)
        if len(items) != len(value) or items != required_values or not items.issubset(allowed):
            _error(errors, f"manifest.{name}")
    unsupported = document.get("unsupported_capabilities")
    if not isinstance(unsupported, list):
        _error(errors, "manifest.unsupported_capabilities")
    else:
        ids: list[str] = []
        for entry in unsupported:
            if not isinstance(entry, dict) or set(entry) != {"capability_id", "reason_code"}:
                _error(errors, "manifest.unsupported_capabilities")
                continue
            capability_id = entry.get("capability_id")
            reason_code = entry.get("reason_code")
            if capability_id not in UNSUPPORTED_CAPABILITIES or not isinstance(reason_code, str) or not reason_code:
                _error(errors, "manifest.unsupported_capabilities")
                continue
            ids.append(capability_id)
        if len(set(ids)) != len(ids) or set(ids) != UNSUPPORTED_CAPABILITIES:
            _error(errors, "manifest.capability_unclassified")
    for name in optional:
        if name not in document:
            continue
        value = document[name]
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
            _error(errors, f"manifest.{name}")
            continue
        if len(set(value)) != len(value):
            _error(errors, f"manifest.{name}")
    fixtures = document.get("fixtures")
    if fixtures is not None and set(fixtures) != FIXTURE_PATHS:
        _error(errors, "manifest.fixtures")
    expected = document.get("expected_artifacts")
    if expected is not None and len(expected) < 3:
        _error(errors, "manifest.expected_artifacts")
    return sorted(errors)


def core_version_compatible(core_api_range: str, version: str = CURRENT_CORE_API_VERSION) -> bool:
    match = _RANGE.fullmatch(core_api_range)
    if not match:
        return False
    try:
        lower = tuple(int(part) for part in match.groups()[:3])
        upper = tuple(int(part) for part in match.groups()[3:])
        current = _version(version)
    except (TypeError, ValueError):
        return False
    return lower <= current < upper


def negotiate(
    manifest: Any,
    *,
    capability_id: str,
    scope: str,
    requested_permissions: list[str],
    core_api_version: str = CURRENT_CORE_API_VERSION,
) -> dict[str, Any]:
    """Return a structured result without falling back to implicit authority."""
    errors = validate_adapter_manifest(manifest)
    adapter_id = manifest.get("adapter_id") if isinstance(manifest, dict) else None
    receipt: dict[str, Any] = {
        "protocol_version": "1.0",
        "adapter_id": adapter_id,
        "capability_id": capability_id,
        "requested_scopes": [scope],
        "effective_permissions": [],
        "result": "denied",
        "reason_code": "invalid_manifest",
    }
    if errors:
        receipt["validation_errors"] = errors
        return receipt
    assert isinstance(manifest, dict)
    if not core_version_compatible(manifest["core_api_range"], core_api_version):
        receipt["reason_code"] = "core_api_incompatible"
        return receipt
    if scope not in LOCAL_SCOPES or scope not in manifest["context_scopes"]:
        receipt["reason_code"] = "scope_unsupported"
        return receipt
    if capability_id in UNSUPPORTED_CAPABILITIES:
        receipt["result"] = "unsupported"
        receipt["reason_code"] = next(
            entry["reason_code"] for entry in manifest["unsupported_capabilities"]
            if entry["capability_id"] == capability_id
        )
        return receipt
    if capability_id not in manifest["supported_capabilities"]:
        receipt["result"] = "unsupported"
        receipt["reason_code"] = "undeclared_capability"
        return receipt
    permissions = set(requested_permissions)
    required = (
        {"read_project"} if capability_id == "context.read" and scope == "project_user"
        else {"read_user_global"} if capability_id == "context.read" and scope == "user_global"
        else CAPABILITY_PERMISSIONS.get(capability_id, set())
    )
    granted = set(manifest["granted_permissions"])
    if not required.issubset(permissions) or not permissions.issubset(granted):
        receipt["reason_code"] = "permission_denied"
        return receipt
    if capability_id == "candidate.write" and scope != "project_user":
        receipt["reason_code"] = "candidate_write_scope_denied"
        return receipt
    receipt["effective_permissions"] = sorted(permissions)
    receipt["result"] = "supported"
    receipt["reason_code"] = "ok"
    return receipt


def _load_json(path: str) -> Any:
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and negotiate Owledge AdapterManifest v1 contracts.")
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--manifest", required=True)
    negotiate_parser = sub.add_parser("negotiate")
    negotiate_parser.add_argument("--manifest", required=True)
    negotiate_parser.add_argument("--capability", required=True)
    negotiate_parser.add_argument("--scope", required=True)
    negotiate_parser.add_argument("--permission", action="append", default=[])
    negotiate_parser.add_argument("--core-api-version", default=CURRENT_CORE_API_VERSION)
    args = parser.parse_args(argv)
    try:
        manifest = _load_json(args.manifest)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"passed": False, "errors": ["manifest.unreadable"], "detail": str(exc)}, sort_keys=True))
        return 1
    if args.command == "validate":
        errors = validate_adapter_manifest(manifest)
        print(json.dumps({"passed": not errors, "errors": errors}, sort_keys=True))
        return 0 if not errors else 1
    receipt = negotiate(
        manifest,
        capability_id=args.capability,
        scope=args.scope,
        requested_permissions=args.permission,
        core_api_version=args.core_api_version,
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["result"] == "supported" else 1


if __name__ == "__main__":
    raise SystemExit(main())
