#!/usr/bin/env python3
"""Deterministic V1 recall and bounded context over local Owledge namespaces."""
from __future__ import annotations

import pathlib
from typing import Any

import owledge_core as core
import owledge_null_space as null_space


PURPOSES = {"research", "planning"}
EXCLUDED_LIFECYCLES = {"candidate", "raw", "parked", "promoted", "rejected", "superseded", "tombstoned"}


def _requested_scopes(scopes: set[str] | None, include_user_global: bool) -> tuple[set[str] | None, dict[str, Any] | None]:
    selected = set(scopes or {"project_user"})
    if not selected.issubset(set(null_space.ALLOWED_SCOPES)):
        return None, {"passed": False, "error": "scope_unsupported", "scopes": sorted(selected)}
    if "user_global" in selected and not include_user_global:
        return None, {"passed": False, "error": "user_global_requires_explicit_opt_in"}
    return selected, None


def _matches(record: dict[str, Any], query: str) -> tuple[bool, int]:
    terms = {part.lower() for part in query.split() if part.strip()}
    haystack = " ".join(str(record.get(field) or "") for field in ("summary", "source_reason", "source", "stable_id")).lower()
    score = sum(term in haystack for term in terms)
    return score > 0, score


def _records(project_root: pathlib.Path, scopes: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if "project_user" in scopes:
        project = null_space.scan_project_user(project_root)
        if project.get("passed"):
            records.extend(project["records"])
        else:
            errors.append(project)
    if "user_global" in scopes:
        global_scan = null_space.scan_user_global(project_root)
        if global_scan.get("passed"):
            records.extend(global_scan["records"])
        else:
            errors.append(global_scan)
    return records, errors


def recall(project_root: pathlib.Path, *, query: str, purpose: str = "research", scopes: set[str] | None = None, include_user_global: bool = False, limit: int = 12) -> dict[str, Any]:
    if not query or not query.strip():
        return {"passed": False, "error": "empty_query", "results": [], "exclusions": []}
    if purpose not in PURPOSES:
        return {"passed": False, "error": "purpose_unsupported", "purpose": purpose, "results": [], "exclusions": []}
    selected, scope_error = _requested_scopes(scopes, include_user_global)
    if scope_error:
        return scope_error
    records, scan_errors = _records(project_root, selected or set())
    if scan_errors:
        return {"passed": False, "error": "scope_scan_denied", "scan_errors": scan_errors, "results": [], "exclusions": []}
    results: list[dict[str, Any]] = []
    exclusions: list[dict[str, str]] = []
    for record in records:
        stable_id = str(record.get("stable_id") or "unknown")
        scope = str(record.get("scope") or "")
        lifecycle = str(record.get("lifecycle") or "reviewed")
        freshness = str(record.get("freshness") or "unknown")
        if lifecycle == "parked" and purpose == "planning" and freshness == "current":
            matched, score = _matches(record, query)
            if matched:
                results.append({
                    "detail_id": f"{scope}/{stable_id}", "stable_id": stable_id, "scope": scope,
                    "summary": str(record.get("summary") or ""), "source": str(record.get("source") or ""),
                    "source_reason": str(record.get("source_reason") or ""),
                    "source_revision": str(record.get("source_revision") or record.get("source_hash") or ""),
                    "freshness": freshness, "lifecycle": lifecycle, "match_score": score,
                    "park_reason": str(record.get("park_reason") or ""), "reconsider_when": str(record.get("reconsider_when") or ""),
                })
                continue
        if lifecycle in EXCLUDED_LIFECYCLES:
            exclusions.append({"stable_id": stable_id, "reason": f"lifecycle_{lifecycle}"})
            continue
        if freshness != "current":
            exclusions.append({"stable_id": stable_id, "reason": f"freshness_{freshness}"})
            continue
        matched, score = _matches(record, query)
        if not matched:
            exclusions.append({"stable_id": stable_id, "reason": "query_not_matched"})
            continue
        results.append({
            "detail_id": f"{scope}/{stable_id}", "stable_id": stable_id, "scope": scope,
            "summary": str(record.get("summary") or ""), "source": str(record.get("source") or ""),
            "source_reason": str(record.get("source_reason") or ""),
            "source_revision": str(record.get("source_revision") or record.get("source_hash") or ""),
            "freshness": freshness, "lifecycle": lifecycle, "match_score": score,
        })
    results.sort(key=lambda item: (-int(item["match_score"]), item["scope"], item["stable_id"], item["source"]))
    selected_results = results[:max(1, limit)]
    exclusions.extend({"stable_id": item["stable_id"], "reason": "result_limit"} for item in results[len(selected_results):])
    return {"passed": True, "purpose": purpose, "query": query.strip(), "scopes": sorted(selected or set()), "results": selected_results, "exclusions": sorted(exclusions, key=lambda item: (item["stable_id"], item["reason"])), "progressive_disclosure": "essence_first_permission_checked_detail", "network": "disabled", "implicit_discovery": False}


def _detail_path(project_root: pathlib.Path, record: dict[str, Any]) -> pathlib.Path:
    source = str(record["source"])
    if source.startswith("project_user/"):
        root = project_root.resolve()
        candidate = (root / source.removeprefix("project_user/")).resolve()
        candidate.relative_to(root)
        return candidate
    if source.startswith("user_global/"):
        global_root, _, _ = null_space._load_link(project_root)
        candidate = (global_root / source.removeprefix("user_global/")).resolve()
        candidate.relative_to(global_root)
        return candidate
    raise ValueError("detail_source_invalid")


def detail(project_root: pathlib.Path, *, detail_id: str, scopes: set[str] | None = None, include_user_global: bool = False) -> dict[str, Any]:
    selected, scope_error = _requested_scopes(scopes, include_user_global)
    if scope_error:
        return scope_error
    records, scan_errors = _records(project_root, selected or set())
    if scan_errors:
        return {"passed": False, "error": "scope_scan_denied", "scan_errors": scan_errors}
    for record in records:
        if f"{record.get('scope')}/{record.get('stable_id')}" != detail_id:
            continue
        if str(record.get("freshness") or "unknown") != "current" or str(record.get("lifecycle") or "reviewed") in EXCLUDED_LIFECYCLES:
            return {"passed": False, "error": "detail_source_not_authorized", "detail_id": detail_id}
        try:
            path = _detail_path(project_root, record)
            text = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            return {"passed": False, "error": "detail_source_unavailable", "detail_id": detail_id}
        body = core.markdown_body(text)
        return {"passed": True, "detail_id": detail_id, "scope": record["scope"], "source": record["source"], "source_revision": record.get("source_revision") or record.get("source_hash"), "content": body[:4000], "truncated": len(body) > 4000}
    return {"passed": False, "error": "detail_not_authorized", "detail_id": detail_id}


def build_context_pack(project_root: pathlib.Path, *, task_id: str, objective: str = "", purpose: str = "research", budget_chars: int = 4000, scopes: set[str] | None = None, include_user_global: bool = False) -> dict[str, Any]:
    if budget_chars <= 0:
        return {"passed": False, "error": "budget_invalid", "budget_chars": budget_chars}
    query = " ".join(part for part in (task_id, objective) if part).strip()
    recalled = recall(project_root, query=query, purpose=purpose, scopes=scopes, include_user_global=include_user_global)
    if not recalled.get("passed"):
        return {**recalled, "context": [], "included_chars": 0}
    context: list[dict[str, Any]] = []
    exclusions = list(recalled["exclusions"])
    used = 0
    for record in recalled["results"]:
        essence = f"[{record['scope']}] {record['summary']}"
        remaining = budget_chars - used
        if remaining <= 0:
            exclusions.append({"stable_id": record["stable_id"], "reason": "context_budget"})
            continue
        text = essence[:remaining]
        context.append({"detail_id": record["detail_id"], "text": text, "source": record["source"], "source_revision": record["source_revision"], "reason": record["source_reason"], "truncated": len(text) < len(essence)})
        used += len(text)
        if len(text) < len(essence):
            exclusions.append({"stable_id": record["stable_id"], "reason": "context_budget"})
            break
    return {"passed": True, "task_id": task_id, "objective": objective, "purpose": purpose, "budget_chars": budget_chars, "included_chars": used, "context": context, "source_receipts": [{"detail_id": item["detail_id"], "source": item["source"], "source_revision": item["source_revision"]} for item in context], "exclusions": sorted(exclusions, key=lambda item: (item["stable_id"], item["reason"])), "network": "disabled", "implicit_discovery": False}
