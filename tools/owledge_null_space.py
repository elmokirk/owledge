#!/usr/bin/env python3
"""Private, explicit local user-global Null-Space boundary for Owledge V1."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
from typing import Any

import owledge_core as core


SCHEMA_VERSION = 1
ALLOWED_SCOPES = ("project_user", "user_global")
LINK_RELATIVE_PATH = pathlib.Path(".owledge") / "global-link.json"
REGISTRY_RELATIVE_PATH = pathlib.Path(".owledge") / "null-space-registry.json"
GLOBAL_RECORD_DIRECTORIES = ("reviewed", "canonical")


def _timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_local_directory(value: pathlib.Path, *, label: str) -> pathlib.Path:
    expanded = value.expanduser()
    if str(expanded).startswith(("\\\\", "//")):
        raise ValueError(f"{label}_network_path_denied")
    for candidate in (expanded, *expanded.parents):
        if candidate.exists() and candidate.is_symlink():
            raise ValueError(f"{label}_symlink_denied")
    resolved = expanded.resolve()
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(f"{label}_not_directory")
    return resolved


def _is_nested(left: pathlib.Path, right: pathlib.Path) -> bool:
    try:
        left.relative_to(right)
        return True
    except ValueError:
        return False


def _project_id(project_root: pathlib.Path) -> str:
    return hashlib.sha256(str(project_root).encode("utf-8")).hexdigest()[:20]


def _read_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"invalid_json:{path.name}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"invalid_object:{path.name}")
    return value


def _write_json(path: pathlib.Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _registry_path(global_root: pathlib.Path) -> pathlib.Path:
    return global_root / REGISTRY_RELATIVE_PATH


def _default_registry(owner_id: str) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "owner_id": owner_id, "network": "disabled", "sync": "disabled", "allowed_projects": []}


def _validate_registry(value: dict[str, Any], *, owner_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if value.get("schema_version") != SCHEMA_VERSION:
        errors.append("registry_schema")
    if not isinstance(value.get("owner_id"), str) or not value["owner_id"].strip():
        errors.append("registry_owner")
    elif owner_id is not None and value["owner_id"] != owner_id:
        errors.append("registry_owner_mismatch")
    if value.get("network") != "disabled":
        errors.append("registry_network")
    if value.get("sync") != "disabled":
        errors.append("registry_sync")
    projects = value.get("allowed_projects")
    if not isinstance(projects, list):
        errors.append("registry_allowed_projects")
    else:
        for item in projects:
            if not isinstance(item, dict) or not isinstance(item.get("project_id"), str) or not isinstance(item.get("project_root"), str):
                errors.append("registry_project_entry")
                break
    return errors


def link_project(project_root: pathlib.Path, global_root: pathlib.Path, *, owner_id: str = "local-owner", source: str = "flag") -> dict[str, Any]:
    project = _safe_local_directory(project_root, label="project_root")
    global_space = _safe_local_directory(global_root, label="global_root")
    if _is_nested(project, global_space) or _is_nested(global_space, project):
        raise ValueError("project_and_global_root_must_be_separate")
    global_space.mkdir(parents=True, exist_ok=True)
    registry_path = _registry_path(global_space)
    registry = _read_json(registry_path) if registry_path.exists() else _default_registry(owner_id)
    errors = _validate_registry(registry, owner_id=owner_id)
    if errors:
        raise ValueError(";".join(errors))
    project_id = _project_id(project)
    entry = {"project_id": project_id, "project_root": str(project), "linked_at": _timestamp()}
    projects = [item for item in registry["allowed_projects"] if item.get("project_id") != project_id]
    projects.append(entry)
    registry["allowed_projects"] = sorted(projects, key=lambda item: str(item["project_id"]))
    _write_json(registry_path, registry)
    link = {"schema_version": SCHEMA_VERSION, "scope": "user_global", "project_id": project_id, "owner_id": owner_id, "global_root": str(global_space), "network": "disabled", "sync": "disabled", "source": source, "linked_at": _timestamp()}
    _write_json(project / LINK_RELATIVE_PATH, link)
    return privacy_receipt(project)


def _load_link(project_root: pathlib.Path) -> tuple[pathlib.Path, dict[str, Any], dict[str, Any]]:
    project = _safe_local_directory(project_root, label="project_root")
    link_path = project / LINK_RELATIVE_PATH
    if not link_path.is_file():
        raise ValueError("unlinked_project")
    link = _read_json(link_path)
    if link.get("schema_version") != SCHEMA_VERSION or link.get("scope") != "user_global":
        raise ValueError("invalid_link_contract")
    if link.get("network") != "disabled" or link.get("sync") != "disabled":
        raise ValueError("link_remote_or_sync_denied")
    if not isinstance(link.get("global_root"), str) or not link["global_root"]:
        raise ValueError("link_global_root")
    if not isinstance(link.get("owner_id"), str) or not link["owner_id"]:
        raise ValueError("link_owner")
    global_space = _safe_local_directory(pathlib.Path(link["global_root"]), label="global_root")
    if not global_space.is_dir() or _is_nested(project, global_space) or _is_nested(global_space, project):
        raise ValueError("invalid_global_root")
    registry_path = _registry_path(global_space)
    if not registry_path.is_file():
        raise ValueError("missing_owner_registry")
    registry = _read_json(registry_path)
    errors = _validate_registry(registry, owner_id=link["owner_id"])
    if errors:
        raise ValueError(";".join(errors))
    expected_id = _project_id(project)
    if link.get("project_id") != expected_id:
        raise ValueError("link_project_identity")
    registered = [item for item in registry["allowed_projects"] if item.get("project_id") == expected_id and item.get("project_root") == str(project)]
    if len(registered) != 1:
        raise ValueError("project_not_allowlisted")
    return global_space, link, registry


def privacy_receipt(project_root: pathlib.Path) -> dict[str, Any]:
    global_space, link, registry = _load_link(project_root)
    return {"passed": True, "scopes": list(ALLOWED_SCOPES), "global_scope": link["scope"], "project_id": link["project_id"], "owner_id": link["owner_id"], "allowlisted_projects": len(registry["allowed_projects"]), "network": "disabled", "sync": "disabled", "implicit_discovery": False, "global_root_name": global_space.name}


def scan_project_user(project_root: pathlib.Path) -> dict[str, Any]:
    project = _safe_local_directory(project_root, label="project_root")
    records: list[dict[str, str]] = []
    for record in core.load_memory_records(project, include_sessions=False):
        source = str(record["source_path"]).replace("\\", "/")
        if source.startswith("global-memory/"):
            continue
        meta = record["metadata"]
        if meta.get("knowledge_scope") not in {None, "project_user"}:
            continue
        records.append({
            "stable_id": str(meta.get("memory_id") or record["source_hash"][:20]),
            "scope": "project_user",
            "source": f"project_user/{source}",
            "summary": str(meta.get("summary") or core.first_markdown_heading(record["content"], pathlib.Path(source).stem)),
            "source_hash": str(record["source_hash"]),
            "source_revision": str(meta.get("source_revision") or meta.get("source_hash") or record["source_hash"]),
            "freshness": str(meta.get("source_freshness") or meta.get("freshness") or "current"),
            "lifecycle": str(meta.get("lifecycle") or meta.get("status") or "reviewed"),
            "source_reason": str(meta.get("research_reason") or meta.get("reason") or meta.get("semantic_title") or meta.get("summary") or "project memory"),
            "park_reason": str(meta.get("park_reason") or ""),
            "reconsider_when": str(meta.get("reconsider_when") or ""),
        })
    candidate_dir = project / ".owledge" / "candidates"
    if candidate_dir.is_dir():
        for path in sorted(candidate_dir.glob("*.md")):
            if path.is_symlink():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            meta = core.parse_frontmatter(text)
            if meta.get("knowledge_scope") != "project_user":
                continue
            receipt_path = project / ".owledge" / "receipts" / "candidates" / f"{path.stem}.json"
            try:
                receipt = _read_json(receipt_path)
                payload = receipt.get("payload")
                receipt_lifecycle = payload.get("lifecycle") if isinstance(payload, dict) else None
                receipt_matches = (
                    receipt_lifecycle in {"candidate", "parked"}
                    and receipt_lifecycle == meta.get("lifecycle")
                    and payload.get("summary") == meta.get("summary")
                    and payload.get("scope") == "project_user"
                )
            except ValueError:
                receipt_matches = False
            source = str(path.relative_to(project)).replace("\\", "/")
            source_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            records.append({
                "stable_id": str(meta.get("memory_id") or source_hash[:20]), "scope": "project_user",
                "source": f"project_user/{source}", "summary": str(meta.get("summary") or core.first_markdown_heading(text, path.stem)),
                "source_hash": source_hash, "source_revision": str(meta.get("source_revision") or source_hash),
                "freshness": str(meta.get("source_freshness") or meta.get("freshness") or "current"),
                "lifecycle": str(meta.get("lifecycle")) if receipt_matches else "tombstoned",
                "source_reason": str(meta.get("reason") or meta.get("summary") or "candidate proposal"),
                "park_reason": str(meta.get("park_reason") or ""), "reconsider_when": str(meta.get("reconsider_when") or ""),
            })
    return {"passed": True, "scope": "project_user", "records": sorted(records, key=lambda item: (item["stable_id"], item["source"])), "network": "disabled", "sync": "disabled", "implicit_discovery": False}


def scan_user_global(project_root: pathlib.Path, *, requested_scope: str = "user_global") -> dict[str, Any]:
    if requested_scope not in ALLOWED_SCOPES:
        return {"passed": False, "error": "scope_unsupported", "requested_scope": requested_scope}
    if requested_scope == "project_user":
        return scan_project_user(project_root)
    try:
        global_space, link, _ = _load_link(project_root)
    except ValueError as exc:
        return {"passed": False, "error": str(exc), "requested_scope": requested_scope}
    records: list[dict[str, str]] = []
    for directory_name in GLOBAL_RECORD_DIRECTORIES:
        directory = global_space / directory_name
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.md")):
            try:
                resolved = path.resolve()
                resolved.relative_to(directory.resolve())
            except ValueError:
                return {"passed": False, "error": "global_symlink_escape", "requested_scope": requested_scope}
            text = path.read_text(encoding="utf-8", errors="replace")
            meta = core.parse_frontmatter(text)
            if meta.get("knowledge_scope") not in {None, "user_global"}:
                continue
            if meta.get("visibility", "private") != "private":
                continue
            records.append({
                "stable_id": str(meta.get("memory_id") or hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]),
                "scope": "user_global",
                "source": f"user_global/{directory_name}/{path.relative_to(directory).as_posix()}",
                "summary": str(meta.get("summary") or core.first_markdown_heading(text, path.stem)),
                "source_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "source_revision": str(meta.get("source_revision") or meta.get("source_hash") or hashlib.sha256(text.encode("utf-8")).hexdigest()),
                "freshness": str(meta.get("source_freshness") or meta.get("freshness") or "current"),
                "lifecycle": str(meta.get("lifecycle") or meta.get("status") or "reviewed"),
                "source_reason": str(meta.get("research_reason") or meta.get("reason") or meta.get("semantic_title") or meta.get("summary") or "reviewed local essence"),
            })
    return {"passed": True, "scope": "user_global", "records": sorted(records, key=lambda item: (item["stable_id"], item["source"])), "project_id": link["project_id"], "network": "disabled", "sync": "disabled", "implicit_discovery": False}


def rebuild_index(project_root: pathlib.Path) -> dict[str, Any]:
    scan = scan_user_global(project_root)
    if not scan.get("passed"):
        return scan
    project = _safe_local_directory(project_root, label="project_root")
    index_path = project / ".owledge" / "indexes" / "user-global-index.jsonl"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(record, sort_keys=True) + "\n" for record in scan["records"])
    index_path.write_text(payload, encoding="utf-8")
    return {**scan, "index": ".owledge/indexes/user-global-index.jsonl", "rebuildable": True}
