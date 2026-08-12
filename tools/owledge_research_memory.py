#!/usr/bin/env python3
"""Deterministic, metadata-only Research Memory contracts and recall-first lookup."""
from __future__ import annotations
import datetime as dt
import json
import pathlib
from typing import Any

TYPES = {"research_brief", "source_record", "atomic_finding", "synthesis", "research_task_index"}
MUTABILITY = {"immutable", "versioned", "mutable"}
SCOPES = {"project_user", "user_global", "enterprise"}

def validate_record(value: Any) -> list[str]:
    if not isinstance(value, dict): return ["research.type"]
    required = {"stable_id", "record_type", "knowledge_scope", "research_reason", "source_revision", "source_mutability", "source_hash", "lifecycle", "relations", "retrieved_at", "verified_at"}
    errors = [f"research.missing:{key}" for key in sorted(required - set(value))]
    if not isinstance(value.get("stable_id"), str) or not value.get("stable_id"): errors.append("research.stable_id")
    if value.get("record_type") not in TYPES: errors.append("research.record_type")
    if value.get("knowledge_scope") not in SCOPES: errors.append("research.scope")
    if not isinstance(value.get("research_reason"), str) or not value.get("research_reason"): errors.append("research.reason")
    if value.get("source_mutability") not in MUTABILITY: errors.append("research.source_mutability")
    if not isinstance(value.get("source_revision"), str) or not value.get("source_revision"): errors.append("research.source_revision")
    if not isinstance(value.get("source_hash"), str) or not value.get("source_hash"): errors.append("research.source_hash")
    if not isinstance(value.get("relations"), list): errors.append("research.relations")
    return sorted(set(errors))

def freshness(record: dict[str, Any], now: dt.datetime) -> str:
    mutability = record["source_mutability"]
    verified = dt.datetime.fromisoformat(str(record["verified_at"]).replace("Z", "+00:00"))
    age = (now - verified).days
    if mutability == "immutable": return "current"
    limit = 90 if mutability == "versioned" else 7
    return "current" if age <= limit else "stale"

def recall(records: list[dict[str, Any]], *, query: str, allowed_scopes: set[str], now: dt.datetime | None = None) -> dict[str, Any]:
    now = now or dt.datetime.now(dt.timezone.utc); seen: set[str] = set(); candidates: list[dict[str, Any]] = []; gaps: list[str] = []; conflicts: list[str] = []
    for record in records:
        errors = validate_record(record)
        if errors: gaps.extend(errors); continue
        if record["stable_id"] in seen: conflicts.append(record["stable_id"]); continue
        seen.add(record["stable_id"])
        if record["knowledge_scope"] not in allowed_scopes: continue
        haystack = " ".join(str(record.get(key, "")) for key in ("research_reason", "context", "summary", "source_revision")).lower()
        if query.lower() not in haystack and not set(query.lower().split()) & set(haystack.split()): continue
        candidates.append({"stable_id": record["stable_id"], "scope": record["knowledge_scope"], "source_revision": record["source_revision"], "freshness": freshness(record, now), "reason": record["research_reason"]})
    if conflicts: state = "conflicted"
    elif not candidates: state = "missing"
    elif all(item["freshness"] == "current" for item in candidates) and not gaps: state = "sufficient_current"
    elif any(item["freshness"] == "stale" for item in candidates): state = "stale"
    else: state = "partial"
    return {"state": state, "model_calls": 0, "external_search_calls": 0, "results": candidates, "contradictions": sorted(set(conflicts)), "gaps": sorted(set(gaps)), "delta_brief": [] if state == "sufficient_current" else ["Refresh only missing, stale, or conflicted source revisions."], "read_policy": "metadata-only deterministic recall"}

def load_local_records(root: pathlib.Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for directory in (root / ".owledge" / "research", root / "global-memory" / "research"):
        if not directory.is_dir(): continue
        for path in sorted(directory.rglob("*.jsonl")):
            try: path.resolve().relative_to(directory.resolve())
            except ValueError: continue
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    item = json.loads(line)
                    if isinstance(item, dict): records.append(item)
                except ValueError: continue
    return records
