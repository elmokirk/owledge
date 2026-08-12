#!/usr/bin/env python3
"""Deterministic v1 context selection with complete decision receipts.

This is deliberately dependency-free and operates on metadata-shaped records.
Callers supply the scope they are allowed to read; the compiler never widens it.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


PACK_TYPES = {
    "bootstrap", "task", "reviewer", "handoff", "release", "pre_plan", "pre_research",
}
CAPSULE_TYPES = {
    "idea", "concept", "decision", "pattern", "lesson", "research_synthesis",
    "research_finding", "roadmap",
}
PRIVATE_CLASSES = {"personal", "special-category", "secret"}
STALE_VALUES = {"stale", "expired", "outdated"}


def _identifier(record: dict[str, Any]) -> str:
    return str(record.get("stable_id") or record.get("memory_id") or record.get("source_path") or "unknown")


def _excluded(identifier: str, reason: str) -> dict[str, str]:
    return {"stable_id": identifier, "reason": reason}


def _terms(text: str) -> set[str]:
    return {term for term in text.lower().split() if term}


def _sort_key(record: dict[str, Any]) -> tuple[int, str]:
    reviewed_global = (
        record.get("knowledge_scope") == "user_global"
        and str(record.get("lifecycle", "")).lower() in {"reviewed", "canonical"}
    )
    return (0 if reviewed_global else 1, _identifier(record))


def expansion_receipt(record: dict[str, Any], *, action: str, allowed_scopes: set[str]) -> dict[str, Any]:
    """Explain a bounded expansion without returning a source body implicitly."""
    identifier = _identifier(record)
    if action not in {"explain", "deep_dive", "refresh"}:
        raise ValueError("context.expansion_action")
    scope = str(record.get("knowledge_scope") or "project_user")
    if scope not in allowed_scopes:
        return {"stable_id": identifier, "action": action, "allowed": False, "reason": "scope"}
    if action == "deep_dive" and not bool(record.get("source_available", True)):
        return {"stable_id": identifier, "action": action, "allowed": False, "reason": "unavailable_source"}
    if action == "deep_dive" and not bool(record.get("material", True)):
        return {"stable_id": identifier, "action": action, "allowed": False, "reason": "not_material"}
    return {
        "stable_id": identifier,
        "action": action,
        "allowed": True,
        "reason": "explicit_request",
        "source_revision": str(record.get("source_revision") or record.get("source_hash") or "unknown"),
    }


def compile_pack(
    records: list[dict[str, Any]], *, pack_type: str, query: str,
    budget_chars: int, allowed_scopes: set[str],
) -> dict[str, Any]:
    """Select a bounded pack and account for every candidate deterministically."""
    if pack_type not in PACK_TYPES:
        raise ValueError("context.pack_type")
    if budget_chars <= 0:
        raise ValueError("context.budget")
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    remaining = budget_chars
    query_terms = _terms(query)
    for record in sorted(records, key=_sort_key):
        identifier = _identifier(record)
        scope = str(record.get("knowledge_scope") or "project_user")
        privacy = str(record.get("data_class") or "internal").lower()
        capsule_type = str(record.get("capsule_type") or record.get("doc_type") or "")
        text = str(record.get("summary") or record.get("context") or "")
        if scope not in allowed_scopes:
            excluded.append(_excluded(identifier, "scope")); continue
        if scope == "user_global" and str(record.get("lifecycle", "")).lower() not in {"reviewed", "canonical"}:
            excluded.append(_excluded(identifier, "unreviewed_global")); continue
        if privacy in PRIVATE_CLASSES:
            excluded.append(_excluded(identifier, "privacy")); continue
        if record.get("conflicted") or str(record.get("freshness", "")).lower() == "conflicted":
            excluded.append(_excluded(identifier, "conflict")); continue
        freshness_reason = next((
            reason for field, reason in (
                ("source_freshness", "stale_source"),
                ("research_freshness", "stale_research"),
                ("review_freshness", "stale_review"),
                ("freshness", "stale_source"),
            ) if str(record.get(field, "")).lower() in STALE_VALUES
        ), None)
        if freshness_reason:
            excluded.append(_excluded(identifier, freshness_reason)); continue
        if pack_type in {"pre_plan", "pre_research"} and capsule_type not in CAPSULE_TYPES:
            excluded.append(_excluded(identifier, "not_capsule_type")); continue
        if not text or (query_terms and not (query_terms & _terms(text))):
            excluded.append(_excluded(identifier, "unrelated")); continue
        if len(text) > remaining:
            excluded.append(_excluded(identifier, "over_budget")); continue
        global_essence = scope == "user_global" and str(record.get("lifecycle", "")).lower() in {"reviewed", "canonical"}
        included.append({
            "stable_id": identifier,
            "summary": text,
            "reason": "reviewed_global_essence" if global_essence else "relevant_current",
            "chars": len(text),
            "source_revision": str(record.get("source_revision") or record.get("source_hash") or "unknown"),
        })
        remaining -= len(text)
    research_reuse = [item["stable_id"] for item in included if any(
        str(record.get("stable_id") or record.get("memory_id") or record.get("source_path") or "") == item["stable_id"]
        and str(record.get("research_freshness", "")).lower() in {"current", "fresh"}
        for record in records
    )]
    payload: dict[str, Any] = {
        "pack_version": "1.0",
        "pack_type": pack_type,
        "query": query,
        "budget_chars": budget_chars,
        "included": included,
        "excluded": excluded,
        "dropped_sources": len(excluded),
        "remaining_chars": remaining,
        "research_action": "reuse_research_memory" if research_reuse else "refresh_if_needed",
        "reusable_research_ids": research_reuse,
    }
    payload["digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return payload
