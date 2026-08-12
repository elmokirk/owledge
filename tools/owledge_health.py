#!/usr/bin/env python3
"""Deterministic read-only Knowledge Health and Managed Surface reports."""
from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any


MANAGED_CLASSES = {"core-managed", "user-managed", "generated", "extension-managed"}


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def managed_surface(root: pathlib.Path) -> dict[str, Any]:
    manifest_path = root / "kit-manifest.json"
    install = {}
    if manifest_path.is_file():
        try:
            install = json.loads(manifest_path.read_text(encoding="utf-8"))
        except ValueError:
            install = {}
    rows: list[dict[str, str]] = []
    for entry in install.get("files", []) if isinstance(install, dict) else []:
        rel = str(entry.get("path") or "")
        if not rel: continue
        current = root / rel
        rows.append({"path": rel, "classification": "core-managed", "installed_version": str(install.get("kit_version") or ""), "delivery_hash": str(entry.get("sha256_original") or ""), "current_hash": sha256(current) if current.is_file() else "", "state": "present" if current.is_file() else "missing"})
    for rel, classification in [("OWLEDGE.md", "user-managed"), ("AGENTS.md", "user-managed"), ("CLAUDE.md", "user-managed")]:
        path = root / rel
        if path.is_file(): rows.append({"path": rel, "classification": classification, "installed_version": "", "delivery_hash": "", "current_hash": sha256(path), "state": "present"})
    memory = root / ".owledge"
    if memory.is_dir():
        for part in ("indexes", "exports", "reports"):
            path = memory / part
            if path.is_dir(): rows.append({"path": f".owledge/{part}", "classification": "generated", "installed_version": "", "delivery_hash": "", "current_hash": "", "state": "directory"})
    return {"schema_version": "1.0", "read_only": True, "files": rows, "classes": sorted(MANAGED_CLASSES)}


def knowledge_health(root: pathlib.Path, *, context_budget_chars: int = 24000) -> dict[str, Any]:
    """Inspect index metadata only; never load knowledge bodies or invoke a model."""
    index = root / ".owledge" / "indexes" / "memory-index.jsonl"
    records: list[dict[str, Any]] = []
    if index.is_file():
        for line in index.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                item = json.loads(line)
                if isinstance(item, dict): records.append(item)
            except ValueError: pass
    issues: list[dict[str, str]] = []
    ids: dict[str, int] = {}
    for item in records:
        identifier = str(item.get("memory_id") or "")
        if identifier: ids[identifier] = ids.get(identifier, 0) + 1
        if not item.get("source_hash"): issues.append({"code": "missing_source_hash", "id": identifier, "remediation": "rebuild or repair source metadata"})
        if item.get("document_version") in {None, ""}: issues.append({"code": "missing_document_revision", "id": identifier, "remediation": "run preview migration"})
        if item.get("freshness") == "stale": issues.append({"code": "stale_source", "id": identifier, "remediation": "refresh the linked source"})
    for identifier, count in ids.items():
        if count > 1: issues.append({"code": "duplicate_id", "id": identifier, "remediation": "resolve duplicate ownership before promotion"})
    estimated = sum(len(json.dumps(item, sort_keys=True)) for item in records)
    if estimated > context_budget_chars: issues.append({"code": "context_budget_exceeded", "id": "memory-index", "remediation": "use scoped context pack or reduce loaded records"})
    return {"passed": not issues, "read_only": True, "model_calls": 0, "records_scanned": len(records), "projection_watermark": index.stat().st_mtime_ns if index.exists() else 0, "issues": issues, "surface": managed_surface(root)}
