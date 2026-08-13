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
REVIEW_ACTIONS = {"promote", "park", "reject", "supersede"}
TERMINAL_STATES = {"rejected", "superseded"}
EXCLUDED_FROM_NORMAL_RECALL = {"candidate", "raw", "parked", "promoted", "rejected", "superseded", "tombstoned"}


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


def _review_paths(project_root: pathlib.Path, receipt_id: str) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    root = null_space._safe_local_directory(project_root, label="project_root")
    return (
        root / ".owledge" / "receipts" / "reviews" / f"{receipt_id}.json",
        root / ".owledge" / "tombstones" / f"{receipt_id}.json",
        root / ".owledge" / "candidates" / f"{receipt_id}.md",
    )


def _safe_write_target(project_root: pathlib.Path, path: pathlib.Path, *, label: str) -> pathlib.Path:
    root = null_space._safe_local_directory(project_root, label="project_root")
    return _safe_write_target_in_root(root, path, label=label)


def _safe_write_target_in_root(root: pathlib.Path, path: pathlib.Path, *, label: str) -> pathlib.Path:
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


def _safe_read_target(project_root: pathlib.Path, path: pathlib.Path, *, label: str) -> pathlib.Path:
    root = null_space._safe_local_directory(project_root, label="project_root")
    return null_space._safe_read_target(root, path, label=label)


def _file_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _candidate_id(value: str) -> str:
    candidate_id = str(value or "").removeprefix("mem:owledge:candidate:")
    if len(candidate_id) != 20 or any(char not in "0123456789abcdef" for char in candidate_id):
        raise ValueError("candidate_id_invalid")
    return candidate_id


def _load_candidate(project_root: pathlib.Path, candidate_id: str) -> dict[str, Any]:
    candidate_path, candidate_receipt_path = _paths(project_root, candidate_id)
    candidate_path = _safe_read_target(project_root, candidate_path, label="candidate")
    candidate_receipt_path = _safe_read_target(project_root, candidate_receipt_path, label="candidate_receipt")
    try:
        receipt = json.loads(candidate_receipt_path.read_text(encoding="utf-8"))
        payload = receipt.get("payload")
    except (OSError, ValueError) as exc:
        raise ValueError("candidate_receipt_corrupt") from exc
    if not isinstance(payload, dict) or receipt.get("receipt_id") != candidate_id:
        raise ValueError("candidate_receipt_corrupt")
    text = candidate_path.read_text(encoding="utf-8", errors="replace")
    metadata = null_space.core.parse_frontmatter(text)
    if (
        metadata.get("memory_id") != f"mem:owledge:candidate:{candidate_id}"
        or metadata.get("lifecycle") != payload.get("lifecycle")
        or metadata.get("summary") != payload.get("summary")
        or payload.get("lifecycle") not in {"candidate", "parked"}
        or payload.get("scope") != "project_user"
    ):
        raise ValueError("candidate_receipt_mismatch")
    return {
        "candidate_id": candidate_id,
        "candidate_path": candidate_path,
        "candidate_revision": _file_hash(candidate_path),
        "candidate_receipt_path": candidate_receipt_path,
        "payload": payload,
    }


def _load_review(project_root: pathlib.Path, candidate_id: str, candidate_revision: str) -> dict[str, Any] | None:
    review_path, _, _ = _review_paths(project_root, candidate_id)
    if not review_path.exists():
        return None
    review_path = _safe_read_target(project_root, review_path, label="review_receipt")
    try:
        review = json.loads(review_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("review_receipt_corrupt") from exc
    if (
        not isinstance(review, dict)
        or review.get("schema_version") != 1
        or review.get("candidate_id") != candidate_id
        or review.get("candidate_revision") != candidate_revision
        or not null_space._valid_review_contract(review, candidate_id, candidate_revision)
    ):
        raise ValueError("review_receipt_mismatch")
    return review


def _write_json(project_root: pathlib.Path, path: pathlib.Path, value: dict[str, Any], *, label: str) -> pathlib.Path:
    target = _safe_write_target(project_root, path, label=label)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def _global_review_path(global_root: pathlib.Path, project_id: str, candidate_id: str) -> pathlib.Path:
    return global_root / "reviewed" / f"{project_id}-{candidate_id}.md"


def _promote_to_global(project_root: pathlib.Path, candidate: dict[str, Any], review_path: pathlib.Path) -> dict[str, str]:
    global_root, link, _ = null_space._load_link(project_root)
    project = null_space._safe_local_directory(project_root, label="project_root")
    candidate_id = str(candidate["candidate_id"])
    canonical_path = _global_review_path(global_root, str(link["project_id"]), candidate_id)
    canonical_path = _safe_write_target_in_root(global_root, canonical_path, label="canonical")
    payload = candidate["payload"]
    canonical_id = f"mem:owledge:user-global:reviewed:{link['project_id']}:{candidate_id}"
    metadata = [
        "---",
        f"memory_id: {_yaml(canonical_id)}",
        "knowledge_scope: \"user_global\"",
        "visibility: \"private\"",
        "data_class: \"internal\"",
        "lifecycle: \"reviewed\"",
        f"summary: {_yaml(str(payload['summary']))}",
        f"source_refs: {json.dumps(payload['source_refs'], ensure_ascii=False)}",
        f"source_candidate_id: {_yaml(candidate_id)}",
        f"source_candidate_revision: {_yaml(str(candidate['candidate_revision']))}",
        f"source_project_id: {_yaml(str(link['project_id']))}",
        f"source_project_root: {_yaml(str(project))}",
        f"review_receipt: {_yaml('.owledge/receipts/reviews/' + candidate_id + '.json')}",
        "origin_contract: \"v1_candidate_review_v1\"",
        "network: \"disabled\"",
        "sync: \"disabled\"",
        "---",
        "",
        f"# {payload['summary']}",
        "",
        "Reviewed local essence. Source material remains private and revision-bound.",
    ]
    rendered = "\n".join(metadata) + "\n"
    if canonical_path.exists():
        existing = canonical_path.read_text(encoding="utf-8", errors="replace")
        if existing != rendered:
            raise ValueError("canonical_conflict")
    else:
        canonical_path.write_text(rendered, encoding="utf-8")
    return {
        "canonical_id": canonical_id,
        "canonical_path": "reviewed/" + canonical_path.name,
        "review_receipt": str(review_path.relative_to(project)).replace("\\", "/"),
    }


def _review_receipt(project_root: pathlib.Path, candidate: dict[str, Any], prior: dict[str, Any] | None, transition: dict[str, Any], next_state: str, canonical: dict[str, str]) -> dict[str, Any]:
    review = prior or {
        "schema_version": 1,
        "candidate_id": candidate["candidate_id"],
        "candidate_revision": candidate["candidate_revision"],
        "state": str(candidate["payload"]["lifecycle"]),
        "transitions": [],
        "network": "disabled",
    }
    review["transitions"] = [*review["transitions"], transition]
    review["state"] = next_state
    review["canonical"] = canonical
    review["updated_at"] = _now()
    return review


def review(
    project_root: pathlib.Path,
    *,
    candidate_id: str,
    action: str,
    expected_revision: str,
    reason: str = "",
    reconsider_when: str = "",
    superseded_by: str = "",
) -> dict[str, Any]:
    if action not in REVIEW_ACTIONS:
        return {"passed": False, "error": "review_action_unsupported"}
    try:
        resolved_id = _candidate_id(candidate_id)
        candidate = _load_candidate(project_root, resolved_id)
    except ValueError as exc:
        return {"passed": False, "error": str(exc)}
    if expected_revision != candidate["candidate_revision"]:
        return {"passed": False, "error": "candidate_revision_conflict", "candidate_id": resolved_id}
    try:
        prior = _load_review(project_root, resolved_id, candidate["candidate_revision"])
    except ValueError as exc:
        return {"passed": False, "error": str(exc), "candidate_id": resolved_id}
    state = str(prior.get("state")) if prior else str(candidate["payload"]["lifecycle"])
    if action == "park":
        try:
            reason = _safe_value(reason, field="review_reason")
            reconsider_when = _safe_value(reconsider_when, field="reconsider_when")
        except ValueError as exc:
            return {"passed": False, "error": str(exc), "candidate_id": resolved_id}
    if action == "supersede":
        try:
            superseded_by = _safe_value(superseded_by, field="superseded_by")
        except ValueError as exc:
            return {"passed": False, "error": str(exc), "candidate_id": resolved_id}
    if action in {"reject", "supersede"}:
        try:
            reason = _safe_value(reason, field="review_reason")
        except ValueError as exc:
            return {"passed": False, "error": str(exc), "candidate_id": resolved_id}
    next_state = {"promote": "reviewed", "park": "parked", "reject": "rejected", "supersede": "superseded"}[action]
    intent_id = hashlib.sha256(json.dumps({"candidate_id": resolved_id, "revision": candidate["candidate_revision"], "action": action, "reason": reason, "reconsider_when": reconsider_when, "superseded_by": superseded_by}, sort_keys=True).encode("utf-8")).hexdigest()[:20]
    if prior and prior["transitions"] and prior["transitions"][-1].get("id") == intent_id and state == next_state:
        return {"passed": True, "candidate_id": resolved_id, "candidate_revision": candidate["candidate_revision"], "state": state, "transition_id": intent_id, "idempotent": True, "canonical": dict(prior.get("canonical") or {}), "network": "disabled"}
    if state in TERMINAL_STATES:
        return {"passed": False, "error": "review_terminal_state", "candidate_id": resolved_id, "state": state}
    if action == "promote" and state not in {"candidate", "parked"}:
        return {"passed": False, "error": "review_transition_denied", "candidate_id": resolved_id, "state": state}
    if action == "park" and state not in {"candidate", "parked"}:
        return {"passed": False, "error": "review_transition_denied", "candidate_id": resolved_id, "state": state}
    transition = {
        "id": intent_id,
        "action": action,
        "from": state,
        "to": next_state,
        "reason": reason,
        "reconsider_when": reconsider_when,
        "superseded_by": superseded_by,
        "recorded_at": _now(),
    }
    review_path, tombstone_path, _ = _review_paths(project_root, resolved_id)
    canonical: dict[str, str] = dict(prior.get("canonical") or {}) if prior else {}
    created_canonical: pathlib.Path | None = None
    try:
        if action in {"reject", "supersede"}:
            # A terminal receipt is valid only with its local tombstone. Validate
            # that path before mutating the review state.
            _safe_write_target(project_root, tombstone_path, label="tombstone")
        if action == "promote":
            # Both local and global write targets must be safe before either write.
            _safe_write_target(project_root, review_path, label="review_receipt")
            global_root, link, _ = null_space._load_link(project_root)
            global_target = _safe_write_target_in_root(global_root, _global_review_path(global_root, str(link["project_id"]), resolved_id), label="canonical")
            if not global_target.exists():
                created_canonical = global_target
            canonical = _promote_to_global(project_root, candidate, review_path)
        review = _review_receipt(project_root, candidate, prior, transition, next_state, canonical)
        _write_json(project_root, review_path, review, label="review_receipt")
        if action in {"reject", "supersede"}:
            tombstone = {"schema_version": 1, "candidate_id": resolved_id, "candidate_revision": candidate["candidate_revision"], "state": next_state, "reason": reason, "superseded_by": superseded_by, "transition_id": transition["id"], "created_at": _now(), "network": "disabled"}
            _write_json(project_root, tombstone_path, tombstone, label="tombstone")
    except (OSError, ValueError) as exc:
        if created_canonical is not None and created_canonical.is_file():
            created_canonical.unlink()
        return {"passed": False, "error": str(exc), "candidate_id": resolved_id}
    return {"passed": True, "candidate_id": resolved_id, "candidate_revision": candidate["candidate_revision"], "state": next_state, "transition_id": transition["id"], "idempotent": False, "canonical": canonical, "network": "disabled"}


def _candidate_health(project_root: pathlib.Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    root = null_space._safe_local_directory(project_root, label="project_root")
    findings: list[dict[str, str]] = []
    candidates: list[dict[str, str]] = []
    candidate_dir = root / ".owledge" / "candidates"
    receipt_dir = root / ".owledge" / "receipts" / "candidates"
    review_dir = root / ".owledge" / "receipts" / "reviews"
    for directory, label in ((candidate_dir, "candidate_directory"), (receipt_dir, "candidate_receipt_directory"), (review_dir, "review_directory")):
        if directory.exists() or directory.is_symlink():
            null_space._safe_local_subdirectory(root, directory, label=label)
    candidate_ids = {path.stem for path in candidate_dir.glob("*.md")} if candidate_dir.is_dir() else set()
    receipt_ids = {path.stem for path in receipt_dir.glob("*.json")} if receipt_dir.is_dir() else set()
    for orphan in sorted(candidate_ids ^ receipt_ids):
        findings.append({"kind": "orphan_candidate_receipt", "severity": "warning", "id": orphan})
    for candidate_id in sorted(candidate_ids & receipt_ids):
        try:
            candidate = _load_candidate(root, candidate_id)
            review = _load_review(root, candidate_id, candidate["candidate_revision"])
            state = str(review.get("state")) if review else str(candidate["payload"]["lifecycle"])
            candidates.append({"id": candidate_id, "state": state})
            if state in TERMINAL_STATES:
                tombstone_path = root / ".owledge" / "tombstones" / f"{candidate_id}.json"
                if not tombstone_path.is_file():
                    findings.append({"kind": "missing_tombstone", "severity": "error", "id": candidate_id})
        except ValueError:
            findings.append({"kind": "invalid_candidate_revision", "severity": "error", "id": candidate_id})
    if review_dir.is_dir():
        for path in review_dir.glob("*.json"):
            if path.stem not in candidate_ids:
                findings.append({"kind": "orphan_review_receipt", "severity": "warning", "id": path.stem})
    return findings, candidates


def health(project_root: pathlib.Path, *, context_budget: int = 4000) -> dict[str, Any]:
    if context_budget <= 0:
        return {"passed": False, "error": "budget_invalid"}
    try:
        root = null_space._safe_local_directory(project_root, label="project_root")
        findings, candidates = _candidate_health(root)
    except ValueError as exc:
        return {"passed": False, "error": str(exc)}
    try:
        global_scan = null_space.scan_user_global(root)
    except ValueError as exc:
        return {"passed": False, "error": str(exc)}
    records = list(global_scan.get("records") or []) if global_scan.get("passed") else []
    if not global_scan.get("passed") and global_scan.get("error") != "unlinked_project":
        findings.append({"kind": "global_scan_denied", "severity": "error", "id": str(global_scan.get("error") or "unknown")})
    for record in records:
        if str(record.get("freshness") or "current") != "current":
            findings.append({"kind": "stale_source", "severity": "warning", "id": str(record.get("stable_id") or "unknown")})
    pending = [item for item in candidates if item["state"] == "candidate"]
    for item in pending:
        findings.append({"kind": "promotion_debt", "severity": "info", "id": item["id"]})
    used = 0
    overflow = 0
    for record in sorted(records, key=lambda item: (str(item.get("stable_id")), str(item.get("source")))):
        size = len(str(record.get("summary") or ""))
        if used + size > context_budget:
            overflow += 1
        else:
            used += size
    if overflow:
        findings.append({"kind": "context_overflow", "severity": "warning", "id": str(overflow)})
    index_path = root / ".owledge" / "indexes" / "user-global-index.jsonl"
    expected_index = "".join(json.dumps(record, sort_keys=True) + "\n" for record in records)
    actual_index = ""
    if index_path.exists() or index_path.is_symlink():
        try:
            actual_index = _safe_read_target(root, index_path, label="index").read_text(encoding="utf-8", errors="replace")
        except ValueError:
            findings.append({"kind": "index_path_invalid", "severity": "error", "id": "user_global"})
    if actual_index != expected_index:
        findings.append({"kind": "index_drift", "severity": "warning", "id": "user_global"})
    return {
        "passed": not any(item["severity"] == "error" for item in findings),
        "checks": sorted(findings, key=lambda item: (item["severity"], item["kind"], item["id"])),
        "counts": {"candidates": len(candidates), "reviewed_records": len(records), "promotion_debt": len(pending), "context_overflow": overflow},
        "network": "disabled",
        "body_telemetry": "excluded",
    }


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
            candidate_revision = _file_hash(candidate_path)
        except (OSError, ValueError):
            return {"passed": False, "error": "candidate_receipt_corrupt", "receipt_id": receipt_id}
        if existing.get("payload") != payload:
            return {"passed": False, "error": "candidate_replay_conflict", "receipt_id": receipt_id}
        return {"passed": True, "idempotent": True, "receipt_id": receipt_id, "candidate_revision": candidate_revision, "lifecycle": payload["lifecycle"], "candidate_path": ".owledge/candidates/" + candidate_path.name, "promotion": "not_available"}
    metadata = ["---", f"memory_id: {_yaml('mem:owledge:candidate:' + receipt_id)}", f"doc_type: {_yaml('brainstorm_candidate')}", f"knowledge_scope: {_yaml(scope)}", "visibility: \"private\"", "data_class: \"internal\"", f"lifecycle: {_yaml(payload['lifecycle'])}", f"item_kind: {_yaml(kind)}", f"summary: {_yaml(safe_summary)}", f"source_refs: {json.dumps(references, ensure_ascii=False)}"]
    if park:
        metadata.extend([f"park_reason: {_yaml(reason)}", f"reconsider_when: {_yaml(trigger)}"])
    metadata.extend(["---", "", f"# {safe_summary}", "", "Candidate only. Canonical promotion requires the later reviewed lifecycle."])
    candidate_path.write_text("\n".join(metadata) + "\n", encoding="utf-8")
    receipt = {"passed": True, "receipt_id": receipt_id, "idempotent": False, "created_at": _now(), "payload": payload, "candidate_path": ".owledge/candidates/" + candidate_path.name, "promotion": "not_available", "network": "disabled"}
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {key: value for key, value in receipt.items() if key != "payload"} | {"candidate_revision": _file_hash(candidate_path), "lifecycle": payload["lifecycle"]}
