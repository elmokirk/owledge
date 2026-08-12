#!/usr/bin/env python3
"""Deterministic, metadata-only Research Memory contracts and recall-first lookup."""
from __future__ import annotations
import datetime as dt
import json
import pathlib
import re
from typing import Any

TYPES = {"research_brief", "source_record", "atomic_finding", "synthesis", "research_task_index"}
MUTABILITY = {"immutable", "versioned", "mutable"}
SCOPES = {"project_user", "user_global", "enterprise"}
SHA = re.compile(r"^[a-f0-9]{64}$")
REQUIRED = {"stable_id", "record_type", "knowledge_scope", "research_reason", "source_revision", "source_mutability", "source_hash", "lifecycle", "relations", "retrieved_at", "verified_at"}
OPTIONAL = {"context", "summary", "source_ref", "publication_at", "search_at"}
PROFILE_FIELDS = {"research_brief": {"context"}, "source_record": {"source_ref"}, "atomic_finding": {"summary"}, "synthesis": {"summary"}, "research_task_index": {"context"}}

def validate_record(value: Any) -> list[str]:
    if not isinstance(value, dict): return ["research.type"]
    errors = [f"research.missing:{key}" for key in sorted(REQUIRED - set(value))]
    errors.extend(f"research.unknown_field:{key}" for key in sorted(set(value) - REQUIRED - OPTIONAL))
    if not isinstance(value.get("stable_id"), str) or not value.get("stable_id"): errors.append("research.stable_id")
    if value.get("record_type") not in TYPES: errors.append("research.record_type")
    if value.get("knowledge_scope") not in SCOPES: errors.append("research.scope")
    if not isinstance(value.get("research_reason"), str) or not value.get("research_reason"): errors.append("research.reason")
    if value.get("source_mutability") not in MUTABILITY: errors.append("research.source_mutability")
    if not isinstance(value.get("source_revision"), str) or not value.get("source_revision"): errors.append("research.source_revision")
    if not isinstance(value.get("source_hash"), str) or not SHA.fullmatch(value.get("source_hash", "")): errors.append("research.source_hash")
    if not isinstance(value.get("lifecycle"), str) or not value.get("lifecycle"): errors.append("research.lifecycle")
    if not isinstance(value.get("relations"), list): errors.append("research.relations")
    for key in ("retrieved_at", "verified_at"):
        try: dt.datetime.fromisoformat(str(value.get(key)).replace("Z", "+00:00"))
        except ValueError: errors.append(f"research.{key}")
    for key in PROFILE_FIELDS.get(value.get("record_type"), set()):
        if not isinstance(value.get(key), str) or not value.get(key): errors.append(f"research.profile:{key}")
    for key in OPTIONAL:
        if key in value and not isinstance(value[key], str): errors.append(f"research.{key}")
    return sorted(set(errors))

def freshness(record: dict[str, Any], now: dt.datetime) -> str:
    mutability = record["source_mutability"]
    verified = dt.datetime.fromisoformat(str(record["verified_at"]).replace("Z", "+00:00"))
    age = (now - verified).days
    if mutability == "immutable": return "current"
    limit = 90 if mutability == "versioned" else 7
    return "current" if age <= limit else "stale"

def recall(records: list[dict[str, Any]], *, query: str, allowed_scopes: set[str], now: dt.datetime | None = None) -> dict[str, Any]:
    now = now or dt.datetime.now(dt.timezone.utc); seen: set[str] = set(); candidates: list[dict[str, Any]] = []; gaps: list[str] = []; conflicts: list[str] = []; delta: list[dict[str, str]] = []
    for record in records:
        errors = validate_record(record)
        if errors: gaps.extend(errors); delta.append({"stable_id": str(record.get("stable_id") or "unknown"), "reason": "missing_or_invalid_source_contract"}); continue
        if record["stable_id"] in seen: conflicts.append(record["stable_id"]); continue
        seen.add(record["stable_id"])
        if record["knowledge_scope"] not in allowed_scopes: continue
        haystack = " ".join(str(record.get(key, "")) for key in ("research_reason", "context", "summary", "source_revision")).lower()
        if query.lower() not in haystack and not set(query.lower().split()) & set(haystack.split()): continue
        state = freshness(record, now)
        candidates.append({"stable_id": record["stable_id"], "scope": record["knowledge_scope"], "source_revision": record["source_revision"], "source_hash": record["source_hash"], "source_ref": str(record.get("source_ref") or ""), "freshness": state, "reason": record["research_reason"]})
        if state == "stale": delta.append({"stable_id": record["stable_id"], "reason": "stale_source_revision"})
    if conflicts: state = "conflicted"
    elif not candidates: state = "missing"
    elif all(item["freshness"] == "current" for item in candidates) and not gaps: state = "sufficient_current"
    elif any(item["freshness"] == "stale" for item in candidates): state = "stale"
    else: state = "partial"
    if conflicts: delta.extend({"stable_id": item, "reason": "duplicate_stable_id"} for item in sorted(set(conflicts)))
    return {"state": state, "model_calls": 0, "external_search_calls": 0, "results": candidates, "contradictions": sorted(set(conflicts)), "gaps": sorted(set(gaps)), "delta_brief": [] if state == "sufficient_current" else delta, "read_policy": "metadata-only deterministic recall"}

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
