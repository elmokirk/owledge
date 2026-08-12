#!/usr/bin/env python
"""Small deterministic validators for the Owledge v1 contract profiles.

The module deliberately avoids a JSON-Schema runtime dependency: schemas remain
portable interchange contracts and these checks provide the fail-closed runtime
rules needed by CLI, MCP, and future adapters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from typing import Any


KNOWLEDGE_SCOPES = {"project_user", "user_global", "enterprise"}
LIFECYCLES = {"candidate", "raw_inbox", "reviewed", "canonical", "superseded", "archived"}
VISIBILITIES = {"private", "tenant", "customer", "shared"}
DATA_CLASSES = {"public", "internal", "confidential", "personal", "special-category"}
TRANSFERABILITY = {"none", "project_only", "user_global_candidate", "enterprise_candidate", "reviewed_global"}
CAPABILITY_RESULTS = {"supported", "unsupported", "denied"}
_EXTENSION_KEY = re.compile(r"^[a-z0-9][a-z0-9_-]*(?:\.[a-z0-9][a-z0-9_-]*)+$")
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")

ENVELOPE_REQUIRED = {
    "memory_id", "schema_version", "profile_version", "document_version", "source_hash",
    "knowledge_scope", "server_project_scope", "owner_user_id", "lifecycle", "visibility",
    "data_class", "audience_ids", "transferability", "applies_to", "edges", "extensions",
}
ENVELOPE_OPTIONAL = {"resource_refs", "created_at", "updated_at", "profile", "summary", "title"}


def _error(errors: list[str], code: str) -> None:
    errors.append(code)


def _identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(_ID.fullmatch(value))


def semantic_fingerprint(document: dict[str, Any]) -> str:
    """Fingerprint material fields without revision/integrity bookkeeping."""
    material = {key: value for key, value in document.items() if key not in {"document_version", "source_hash", "updated_at"}}
    raw = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_resource_ref(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["resource_ref.type"]
    required = {"resource_id", "relation", "locator", "media_type", "content_hash", "size_bytes", "data_class", "availability", "access_state", "extraction_provenance"}
    for key in sorted(required - set(value)):
        _error(errors, f"resource_ref.missing:{key}")
    if not _identifier(value.get("resource_id")):
        _error(errors, "resource_ref.resource_id")
    if not isinstance(value.get("relation"), str) or not value.get("relation"):
        _error(errors, "resource_ref.relation")
    locator = value.get("locator")
    if not isinstance(locator, str) or not locator or locator.startswith(("/", "\\")) or ".." in locator.replace("\\", "/").split("/"):
        _error(errors, "resource_ref.locator")
    if value.get("data_class") not in DATA_CLASSES:
        _error(errors, "resource_ref.data_class")
    if not isinstance(value.get("size_bytes"), int) or value.get("size_bytes") < 0:
        _error(errors, "resource_ref.size_bytes")
    if value.get("availability") not in {"available", "unavailable", "withdrawn", "unknown"}:
        _error(errors, "resource_ref.availability")
    if value.get("access_state") not in {"authorized", "restricted", "revoked", "unknown"}:
        _error(errors, "resource_ref.access_state")
    return errors


def validate_artifact_envelope(document: Any, previous: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["envelope.type"]
    keys = set(document)
    for key in sorted(ENVELOPE_REQUIRED - keys):
        _error(errors, f"envelope.missing:{key}")
    for key in sorted(keys - ENVELOPE_REQUIRED - ENVELOPE_OPTIONAL):
        _error(errors, f"envelope.unknown_core_key:{key}")
    if not isinstance(document.get("memory_id"), str) or not document.get("memory_id", "").startswith("mem:"):
        _error(errors, "envelope.memory_id")
    for key in ("schema_version", "profile_version"):
        if not isinstance(document.get(key), str) or not document.get(key):
            _error(errors, f"envelope.{key}")
    if not isinstance(document.get("document_version"), int) or document.get("document_version", 0) < 1:
        _error(errors, "envelope.document_version")
    if not isinstance(document.get("source_hash"), str) or len(document.get("source_hash", "")) < 16:
        _error(errors, "envelope.source_hash")
    if document.get("knowledge_scope") not in KNOWLEDGE_SCOPES:
        _error(errors, "envelope.knowledge_scope")
    if not _identifier(document.get("server_project_scope")):
        _error(errors, "envelope.server_project_scope")
    if not _identifier(document.get("owner_user_id")):
        _error(errors, "envelope.owner_user_id")
    if document.get("lifecycle") not in LIFECYCLES:
        _error(errors, "envelope.lifecycle")
    if document.get("visibility") not in VISIBILITIES:
        _error(errors, "envelope.visibility")
    if document.get("data_class") not in DATA_CLASSES:
        _error(errors, "envelope.data_class")
    if document.get("visibility") == "shared" and document.get("data_class") not in {"public", "internal"}:
        _error(errors, "envelope.visibility_data_class")
    for key in ("audience_ids", "applies_to"):
        if not isinstance(document.get(key), list) or not all(_identifier(item) for item in document.get(key, [])):
            _error(errors, f"envelope.{key}")
    if document.get("transferability") not in TRANSFERABILITY:
        _error(errors, "envelope.transferability")
    if not isinstance(document.get("edges"), list):
        _error(errors, "envelope.edges")
    else:
        for edge in document["edges"]:
            if not isinstance(edge, dict) or not isinstance(edge.get("type"), str) or not _identifier(edge.get("target")):
                _error(errors, "envelope.edge")
                break
    extensions = document.get("extensions")
    if not isinstance(extensions, dict):
        _error(errors, "envelope.extensions")
    elif any(not _EXTENSION_KEY.fullmatch(key) for key in extensions):
        _error(errors, "envelope.extensions_namespace")
    refs = document.get("resource_refs", [])
    if not isinstance(refs, list):
        _error(errors, "envelope.resource_refs")
    else:
        for ref in refs:
            errors.extend(validate_resource_ref(ref))
    if previous is not None:
        if document.get("memory_id") != previous.get("memory_id"):
            _error(errors, "revision.memory_id_changed")
        previous_version = previous.get("document_version")
        if not isinstance(previous_version, int):
            _error(errors, "revision.previous_version")
        else:
            changed = semantic_fingerprint(document) != semantic_fingerprint(previous)
            expected = previous_version + 1 if changed else previous_version
            if document.get("document_version") != expected:
                _error(errors, "revision.non_monotonic")
    return sorted(set(errors))


def resolve_settings(layers: list[tuple[str, dict[str, Any]]]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Combine ordered settings. Any denial wins and grants never re-expand."""
    effective: dict[str, Any] = {}
    receipt: dict[str, Any] = {"layers": [], "denials": [], "accepted": []}
    deny_seen: set[str] = set()
    for layer_name, values in layers:
        if not isinstance(values, dict):
            raise ValueError(f"settings.layer_type:{layer_name}")
        for key, value in values.items():
            if key.startswith("allow_") and not isinstance(value, bool):
                raise ValueError(f"settings.allow_bool:{key}")
            if key.startswith("allow_") and value is False:
                effective[key] = False
                deny_seen.add(key)
                receipt["denials"].append({"layer": layer_name, "key": key})
            elif key in deny_seen:
                receipt["denials"].append({"layer": layer_name, "key": key, "reason": "prior_deny"})
            elif key.startswith("allow_") and effective.get(key) is False:
                receipt["denials"].append({"layer": layer_name, "key": key, "reason": "prior_deny"})
            else:
                effective[key] = value
                receipt["accepted"].append({"layer": layer_name, "key": key})
        receipt["layers"].append(layer_name)
    return effective, receipt


def validate_capability_receipt(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["capability.type"]
    errors: list[str] = []
    required = {"request_id", "protocol_version", "core_api_range", "capability_id", "operation_kind", "requested_scopes", "effective_permissions", "data_class", "result", "reason_code"}
    for key in sorted(required - set(value)):
        _error(errors, f"capability.missing:{key}")
    if not _identifier(value.get("request_id")) or not _identifier(value.get("capability_id")):
        _error(errors, "capability.identity")
    if value.get("operation_kind") not in {"query", "command"}:
        _error(errors, "capability.operation_kind")
    if not isinstance(value.get("requested_scopes"), list) or not set(value.get("requested_scopes", [])).issubset(KNOWLEDGE_SCOPES):
        _error(errors, "capability.requested_scopes")
    if value.get("data_class") not in DATA_CLASSES or value.get("result") not in CAPABILITY_RESULTS:
        _error(errors, "capability.result")
    if not isinstance(value.get("reason_code"), str) or not value.get("reason_code"):
        _error(errors, "capability.reason_code")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Owledge v1 artifact envelope JSON document.")
    parser.add_argument("document")
    parser.add_argument("--previous")
    args = parser.parse_args()
    document = json.loads(open(args.document, encoding="utf-8").read())
    previous = json.loads(open(args.previous, encoding="utf-8").read()) if args.previous else None
    errors = validate_artifact_envelope(document, previous)
    print(json.dumps({"passed": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
