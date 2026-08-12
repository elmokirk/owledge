#!/usr/bin/env python3
"""Progressive-disclosure receipts and bounded active-tool profiles."""
from __future__ import annotations

import hashlib
from typing import Any

TOOL_PROFILES = {
    "orientation": ("owledge_read_entrypoint", "owledge_doctor"),
    "retrieval": ("owledge_search_memory", "owledge_context_synopsis", "owledge_build_context_pack"),
    "delivery": ("owledge_build_context_pack", "owledge_list_tasks", "owledge_list_reviews"),
}


def synopsis(body: str, summary: str, *, source_revision: str) -> dict[str, Any]:
    """Return a non-authoritative synopsis bound to an exact body revision."""
    return {"kind": "synopsis", "authority": "non_canonical", "summary": summary,
            "source_revision": source_revision,
            "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest()}


def validate_synopsis(value: dict[str, Any], body: str) -> dict[str, Any]:
    actual = hashlib.sha256(body.encode("utf-8")).hexdigest()
    fresh = value.get("body_sha256") == actual
    return {"fresh": fresh, "authority": "non_canonical", "reason": "current" if fresh else "stale_body"}


def active_tools(task_class: str, available_tools: set[str]) -> dict[str, Any]:
    if task_class not in TOOL_PROFILES:
        raise ValueError("tool_profile.unknown_task_class")
    selected = list(TOOL_PROFILES[task_class])
    unknown = [tool for tool in selected if tool not in available_tools]
    if unknown:
        raise ValueError("tool_profile.unknown_capability:" + ",".join(unknown))
    inactive = sorted(available_tools - set(selected))
    return {"task_class": task_class, "active_tools": selected, "inactive_tools": inactive,
            "reason": "explicit_task_class_allowlist"}
