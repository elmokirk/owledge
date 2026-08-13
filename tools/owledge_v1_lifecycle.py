#!/usr/bin/env python3
"""Local Candidate and Park/Resurface lifecycle boundary for Owledge V1."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
from typing import Any

import owledge_null_space as null_space


ALLOWED_KINDS = {"idea", "research", "learning", "decision", "handoff", "feature"}
ALLOWED_SCOPES = {"project_user"}
EXCLUDED_FROM_NORMAL_RECALL = {"candidate", "raw", "parked", "rejected", "superseded", "tombstoned"}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_value(value: str, *, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"missing_{field}")
    if "\x00" in text or "\r" in text:
        raise ValueError(f"invalid_{field}")
    return text


def _yaml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _paths(project_root: pathlib.Path, receipt_id: str) -> tuple[pathlib.Path, pathlib.Path]:
    root = null_space._safe_local_directory(project_root, label="project_root")
    return root / ".owledge" / "candidates" / f"{receipt_id}.md", root / ".owledge" / "receipts" / "candidates" / f"{receipt_id}.json"


def _safe_write_target(project_root: pathlib.Path, path: pathlib.Path, *, label: str) -> pathlib.Path:
    root = null_space._safe_local_directory(project_root, label="project_root")
    for ancestor in (path, *path.parents):
        if ancestor.exists() and ancestor.is_symlink():
            raise ValueError(f"{label}_symlink_denied")
        if ancestor == root:
            break
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.resolve().relative_to(root)
        if path.exists() and path.is_symlink():
            raise ValueError(f"{label}_symlink_denied")
        path.resolve().relative_to(root)
    except ValueError as exc:
        if str(exc).endswith("_symlink_denied"):
            raise
        raise ValueError(f"{label}_path_escape") from exc
    return path


def propose(project_root: pathlib.Path, *, kind: str, summary: str, source_refs: list[str], park: bool = False, park_reason: str = "", reconsider_when: str = "", scope: str = "project_user") -> dict[str, Any]:
    if kind not in ALLOWED_KINDS:
        return {"passed": False, "error": "candidate_kind_unsupported"}
    if scope not in ALLOWED_SCOPES:
        return {"passed": False, "error": "candidate_scope_unsupported"}
    try:
        safe_summary = _safe_value(summary, field="summary")
        references = sorted({_safe_value(item, field="source_ref") for item in source_refs})
        if not references:
            raise ValueError("missing_source_refs")
        reason = _safe_value(park_reason, field="park_reason") if park else ""
        trigger = _safe_value(reconsider_when, field="reconsider_when") if park else ""
    except ValueError as exc:
        return {"passed": False, "error": str(exc)}
    payload = {"kind": kind, "summary": safe_summary, "source_refs": references, "scope": scope, "lifecycle": "parked" if park else "candidate", "park_reason": reason, "reconsider_when": trigger}
    receipt_id = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()[:20]
    candidate_path, receipt_path = _paths(project_root, receipt_id)
    try:
        candidate_path = _safe_write_target(project_root, candidate_path, label="candidate")
        receipt_path = _safe_write_target(project_root, receipt_path, label="candidate_receipt")
    except ValueError as exc:
        return {"passed": False, "error": str(exc)}
    if receipt_path.exists() or candidate_path.exists():
        try:
            existing = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"passed": False, "error": "candidate_receipt_corrupt", "receipt_id": receipt_id}
        if existing.get("payload") != payload:
            return {"passed": False, "error": "candidate_replay_conflict", "receipt_id": receipt_id}
        return {"passed": True, "idempotent": True, "receipt_id": receipt_id, "lifecycle": payload["lifecycle"], "candidate_path": ".owledge/candidates/" + candidate_path.name, "promotion": "not_available"}
    metadata = ["---", f"memory_id: {_yaml('mem:owledge:candidate:' + receipt_id)}", f"doc_type: {_yaml('brainstorm_candidate')}", f"knowledge_scope: {_yaml(scope)}", "visibility: \"private\"", "data_class: \"internal\"", f"lifecycle: {_yaml(payload['lifecycle'])}", f"item_kind: {_yaml(kind)}", f"summary: {_yaml(safe_summary)}", f"source_refs: {json.dumps(references, ensure_ascii=False)}"]
    if park:
        metadata.extend([f"park_reason: {_yaml(reason)}", f"reconsider_when: {_yaml(trigger)}"])
    metadata.extend(["---", "", f"# {safe_summary}", "", "Candidate only. Canonical promotion requires the later reviewed lifecycle."])
    candidate_path.write_text("\n".join(metadata) + "\n", encoding="utf-8")
    receipt = {"passed": True, "receipt_id": receipt_id, "idempotent": False, "created_at": _now(), "payload": payload, "candidate_path": ".owledge/candidates/" + candidate_path.name, "promotion": "not_available", "network": "disabled"}
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {key: value for key, value in receipt.items() if key != "payload"} | {"lifecycle": payload["lifecycle"]}
