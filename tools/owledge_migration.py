#!/usr/bin/env python3
"""Preview-first, recoverable kit migration without knowledge-body reporting."""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import uuid
from typing import Any

import owledge_health

NEVER_TOUCH = {"OWLEDGE.md", "AGENTS.md", "CLAUDE.md", "USER_CONTEXT.md"}

def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def safe_relative(value: str) -> pathlib.Path:
    path = pathlib.PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or not path.parts: raise ValueError("migration.unsafe_path")
    return pathlib.Path(path.as_posix())

def never_touch(rel: str) -> bool:
    return rel in NEVER_TOUCH or rel.startswith("global-memory/") or any(rel.startswith(f".owledge/{part}/") for part in ("decisions", "plans", "sessions", "evidence", "handoffs"))

def source_for(rel: str, source_root: pathlib.Path) -> pathlib.Path:
    return source_root / "templates" / "owledge" / rel[len(".owledge/"):] if rel.startswith(".owledge/") else source_root / rel

def preview(root: pathlib.Path, source_root: pathlib.Path) -> dict[str, Any]:
    manifest_path = root / "kit-manifest.json"
    if not manifest_path.is_file(): return {"passed": False, "error": "migration.manifest_missing"}
    try: manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except ValueError: return {"passed": False, "error": "migration.manifest_invalid"}
    if not isinstance(manifest.get("files"), list): return {"passed": False, "error": "migration.manifest_files"}
    seen: set[str] = set(); collisions: list[dict[str, str]] = []; writes: list[dict[str, str]] = []; never: list[str] = []
    for entry in manifest["files"]:
        rel = str(entry.get("path") or "")
        try: safe_relative(rel)
        except ValueError: collisions.append({"path": rel, "reason": "unsafe_path"}); continue
        if rel in seen: collisions.append({"path": rel, "reason": "ambiguous_ownership"}); continue
        seen.add(rel)
        target = root / rel; delivery = str(entry.get("sha256_original") or "")
        if never_touch(rel): never.append(rel); continue
        source = source_for(rel, source_root)
        if not source.is_file(): collisions.append({"path": rel, "reason": "source_missing"}); continue
        current = digest(target) if target.is_file() else ""
        if target.is_file() and delivery and current != delivery:
            collisions.append({"path": rel, "reason": "edited_template_collision"}); continue
        if target.is_file() and current == digest(source): continue
        writes.append({"target": rel, "source": str(source.relative_to(source_root)).replace("\\", "/"), "expected_current_hash": current, "delivery_hash": digest(source)})
    health = owledge_health.knowledge_health(root)
    plan_id = uuid.uuid4().hex
    return {"passed": not collisions, "mode": "dry-run", "plan_id": plan_id, "preflight": {"doctor": "required_before_apply", "health_passed": health["passed"], "health_issue_codes": sorted({item["code"] for item in health["issues"]})}, "writes": writes, "collisions": collisions, "never_touch": sorted(never), "recovery": f".owledge/migrations/{plan_id}/receipt.json", "knowledge_bodies": "excluded"}

def apply(root: pathlib.Path, source_root: pathlib.Path, plan: dict[str, Any], *, simulate_postflight_failure: bool = False) -> dict[str, Any]:
    if plan.get("mode") != "dry-run" or not isinstance(plan.get("writes"), list): return {"passed": False, "error": "migration.invalid_plan"}
    if plan.get("collisions"): return {"passed": False, "error": "migration.collisions_present"}
    plan_id = str(plan.get("plan_id") or "")
    try: safe_relative(plan_id)
    except ValueError: return {"passed": False, "error": "migration.plan_id"}
    transaction = root / ".owledge" / "migrations" / plan_id; receipt_path = transaction / "receipt.json"
    if receipt_path.is_file():
        prior = json.loads(receipt_path.read_text(encoding="utf-8"))
        if prior.get("status") == "applied": return {"passed": True, "idempotent": True, "receipt": str(receipt_path.relative_to(root)).replace("\\", "/")}
    backup = transaction / "backup"; backup.mkdir(parents=True, exist_ok=True); changed: list[str] = []
    try:
        for row in plan["writes"]:
            rel = str(row.get("target") or ""); safe_relative(rel)
            if never_touch(rel): raise ValueError("migration.never_touch")
            target = root / rel; source = source_root / str(row.get("source") or "")
            if not source.is_file(): raise ValueError("migration.source_missing")
            current = digest(target) if target.is_file() else ""
            if current != str(row.get("expected_current_hash") or ""): raise ValueError("migration.concurrent_change")
            if target.is_file():
                backup_path = backup / rel; backup_path.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(target, backup_path)
            target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target); changed.append(rel)
        postflight = owledge_health.knowledge_health(root)
        if simulate_postflight_failure or not postflight["passed"]: raise RuntimeError("migration.postflight_failed")
        receipt = {"status": "applied", "plan_id": plan_id, "changed": changed, "postflight": "passed", "recovery": str(receipt_path.relative_to(root)).replace("\\", "/")}
    except Exception as exc:
        for rel in reversed(changed):
            target = root / rel; saved = backup / rel
            if saved.is_file(): shutil.copy2(saved, target)
            else: target.unlink(missing_ok=True)
        receipt = {"status": "recovered", "plan_id": plan_id, "changed": changed, "postflight": "failed", "error": str(exc), "recovery": str(receipt_path.relative_to(root)).replace("\\", "/")}
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"passed": receipt["status"] == "applied", "idempotent": False, "receipt": receipt["recovery"], "changed": changed, "recovered": receipt["status"] == "recovered"}
