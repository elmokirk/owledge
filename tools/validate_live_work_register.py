#!/usr/bin/env python3
"""Validate the finite FB-001..FB-021 live-work register.

The register is JSON-compatible YAML so this release-critical validator remains
standard-library-only and can run before development dependencies are present.
"""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import sys
import tomllib
from typing import Any, Mapping


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTER_REL = (
    "internal/owledge/workpackages/owledge-v1-autonomous-delivery/"
    "LIVE-WORK-REGISTER.yaml"
)
BACKLOG_REL = (
    "internal/owledge/workpackages/owledge-v1-autonomous-delivery/BACKLOG.yaml"
)

EXPECTED_IDS = tuple(f"FB-{number:03d}" for number in range(1, 22))
ALLOWED_STATES = ("shipped", "open", "superseded", "deferred")
ACTIVE_SOURCES = (
    "ROADMAP.md",
    "docs/strategic-roadmap-2026-2027.md",
)
HISTORICAL_SOURCES = (
    "docs/feedback-round-2026-06.md",
    "docs/roadmap-ideas-2026-06.md",
    "docs/v0.6.0-implementation-plan.md",
)
PRIMARY_SOURCES = (
    *ACTIVE_SOURCES,
    *HISTORICAL_SOURCES,
    "VERSION",
    "pyproject.toml",
    "CHANGELOG.md",
)
CHECKLIST_SOURCES = (
    "internal/owledge/workpackages/v0.7.1-release-execution-orchestration-checklist.md",
    "internal/owledge/workpackages/v0.7.1-public-docs-adoption-checklist.md",
    "internal/owledge/workpackages/v0.7.1-docs-merge-runbook.md",
    "internal/owledge/workpackages/v0.7.0-post-release-documentation-integrity-checklist.md",
    "internal/owledge/workpackages/owledge-v0.7.0-pre-release-agent-tasklist.md",
    "internal/owledge/workpackages/owledge-v0.7.0-final-publishing-quality-checklist.md",
    "internal/owledge/workpackages/owledge-v0.7.0-final-publishing-95-release-checklist.md",
    "internal/owledge/workpackages/owledge-v0.7.0-benchmark-kit-addon-real-fixtures-checklist.md",
    "internal/owledge/workpackages/owledge-v0.7.0-benchmark-comparison-publishing-proof-checklist.md",
)
APPROVED_SOURCES = (*PRIMARY_SOURCES, *CHECKLIST_SOURCES)

TICKET_ID_RE = re.compile(r"^  - \{id: (OW-\d{3}-\d{2}),", re.MULTILINE)
FEEDBACK_HEADING_RE = re.compile(r"^### (FB-\d{3}):", re.MULTILINE)
VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)(?:\.(\d+))?$")


def _read_text(
    root: pathlib.Path,
    relative_path: str,
    overrides: Mapping[str, str] | None,
) -> str:
    if overrides and relative_path in overrides:
        return overrides[relative_path]
    return (root / relative_path).read_text(encoding="utf-8")


def _is_nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().lower() != "tbd"


def _safe_relative_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    if re.match(r"^[A-Za-z]:", value) or value.startswith(("/", "~")):
        return None
    candidate = pathlib.PurePosixPath(value)
    if candidate.is_absolute() or ".." in candidate.parts or "." in candidate.parts:
        return None
    return candidate.as_posix()


def _version_tuple(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    match = VERSION_RE.fullmatch(value.strip())
    if not match:
        return None
    return tuple(int(part or 0) for part in match.groups())  # type: ignore[return-value]


def _load_register(path: pathlib.Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("top-level register must be an object")
    return payload


def _validate_reference_path(
    errors: list[str],
    root: pathlib.Path,
    item_id: str,
    field: str,
    value: Any,
) -> None:
    safe = _safe_relative_path(value)
    if safe is None:
        errors.append(f"{item_id}.{field}: unsafe or non-normalized repository path {value!r}")
        return
    if safe not in APPROVED_SOURCES:
        errors.append(f"{item_id}.{field}: unapproved source path {safe}")
        return
    if not (root / safe).is_file():
        errors.append(f"{item_id}.{field}: source path does not exist: {safe}")


def _validate_supersession_graph(
    errors: list[str],
    items_by_id: Mapping[str, dict[str, Any]],
    known_tickets: set[str],
) -> None:
    edges: dict[str, str] = {}
    for item_id, item in items_by_id.items():
        reference = item.get("replacement_reference")
        if item.get("state") != "superseded":
            if reference is not None:
                errors.append(
                    f"{item_id}.replacement_reference: only superseded items may define a replacement"
                )
            continue
        if not _is_nonempty(reference):
            errors.append(
                f"{item_id}.replacement_reference: superseded state requires a replacement"
            )
            continue
        prefix, separator, target = str(reference).partition(":")
        if not separator or prefix not in {"ticket", "feedback"}:
            errors.append(
                f"{item_id}.replacement_reference: expected ticket:OW-NNN-NN or feedback:FB-NNN"
            )
            continue
        if prefix == "ticket":
            if target not in known_tickets:
                errors.append(
                    f"{item_id}.replacement_reference: unknown ticket replacement {target}"
                )
        else:
            if target == item_id:
                errors.append(f"{item_id}.replacement_reference: self-reference is forbidden")
            elif target not in items_by_id:
                errors.append(
                    f"{item_id}.replacement_reference: unknown feedback replacement {target}"
                )
            else:
                edges[item_id] = target

    for start in sorted(edges):
        seen: list[str] = []
        current = start
        while current in edges:
            if current in seen:
                cycle = seen[seen.index(current) :] + [current]
                errors.append(
                    "replacement_reference: supersession cycle "
                    + " -> ".join(cycle)
                )
                break
            seen.append(current)
            current = edges[current]


def validate_register(
    project_root: pathlib.Path | str = REPO_ROOT,
    register_path: pathlib.Path | str | None = None,
    *,
    text_overrides: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Return a deterministic validation result for a project register."""

    root = pathlib.Path(project_root).resolve()
    path = (
        pathlib.Path(register_path).resolve()
        if register_path is not None
        else root / REGISTER_REL
    )
    errors: list[str] = []

    try:
        register = _load_register(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "passed": False,
            "errors": [f"register: unable to load JSON-compatible YAML: {exc}"],
            "counts": {},
        }

    if register.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if tuple(register.get("allowed_states") or ()) != ALLOWED_STATES:
        errors.append(
            "allowed_states: expected exactly shipped, open, superseded, deferred"
        )

    declared_sources = register.get("source_documents")
    if not isinstance(declared_sources, list):
        errors.append("source_documents: expected a list")
        declared_sources = []
    if (
        set(declared_sources) != set(APPROVED_SOURCES)
        or len(declared_sources) != len(APPROVED_SOURCES)
    ):
        missing = sorted(set(APPROVED_SOURCES) - set(declared_sources))
        extra = sorted(set(declared_sources) - set(APPROVED_SOURCES))
        errors.append(
            f"source_documents: finite source set mismatch missing={missing} extra={extra}"
        )
    for source in declared_sources:
        safe = _safe_relative_path(source)
        if safe is None:
            errors.append(f"source_documents: unsafe path {source!r}")
        elif not (root / safe).is_file():
            errors.append(f"source_documents: missing path {safe}")

    authority = register.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority: expected an object")
        authority = {}
    if tuple(authority.get("live_status_sources") or ()) != ACTIVE_SOURCES:
        errors.append("authority.live_status_sources: active truth set mismatch")
    if tuple(authority.get("historical_sources") or ()) != HISTORICAL_SOURCES:
        errors.append("authority.historical_sources: historical source set mismatch")
    if authority.get("historical_unchecked_boxes_are_active") is not False:
        errors.append(
            "authority.historical_unchecked_boxes_are_active: must be false"
        )

    items = register.get("items")
    if not isinstance(items, list):
        errors.append("items: expected a list")
        items = []
    item_ids = [item.get("id") for item in items if isinstance(item, dict)]
    duplicate_ids = sorted(
        {
            item_id
            for item_id in item_ids
            if isinstance(item_id, str) and item_ids.count(item_id) > 1
        }
    )
    for item_id in duplicate_ids:
        errors.append(f"items: duplicate feedback id {item_id}")
    actual_ids = {item_id for item_id in item_ids if isinstance(item_id, str)}
    missing_ids = sorted(set(EXPECTED_IDS) - actual_ids)
    extra_ids = sorted(actual_ids - set(EXPECTED_IDS))
    if missing_ids:
        errors.append(f"items: missing feedback ids {missing_ids}")
    if extra_ids:
        errors.append(f"items: extra feedback ids {extra_ids}")

    known_tickets: set[str] = set()
    try:
        known_tickets = set(
            TICKET_ID_RE.findall(_read_text(root, BACKLOG_REL, text_overrides))
        )
    except OSError as exc:
        errors.append(f"replacement_reference: unable to read ticket registry: {exc}")

    items_by_id: dict[str, dict[str, Any]] = {}
    state_counts = {state: 0 for state in ALLOWED_STATES}
    active_release = _version_tuple(register.get("active_delivery_release"))
    if active_release is None:
        errors.append("active_delivery_release: expected a concrete semantic version")

    for index, raw_item in enumerate(items):
        if not isinstance(raw_item, dict):
            errors.append(f"items[{index}]: expected an object")
            continue
        item = copy.deepcopy(raw_item)
        item_id = item.get("id")
        label = item_id if isinstance(item_id, str) else f"items[{index}]"
        if isinstance(item_id, str) and item_id not in items_by_id:
            items_by_id[item_id] = item
        for field in ("title", "source", "target_release", "owner_role"):
            if not _is_nonempty(item.get(field)):
                errors.append(f"{label}.{field}: required non-empty value")
        state = item.get("state")
        if state not in ALLOWED_STATES:
            errors.append(
                f"{label}.state: invalid state {state!r}; expected one of {list(ALLOWED_STATES)}"
            )
        else:
            state_counts[state] += 1
        _validate_reference_path(errors, root, label, "source", item.get("source"))

        evidence_links = item.get("evidence_links")
        if not isinstance(evidence_links, list) or not evidence_links:
            errors.append(f"{label}.evidence_links: requires at least one source")
        else:
            for evidence_index, evidence in enumerate(evidence_links):
                _validate_reference_path(
                    errors,
                    root,
                    label,
                    f"evidence_links[{evidence_index}]",
                    evidence,
                )

        shipped_evidence = item.get("shipped_evidence")
        if not isinstance(shipped_evidence, list):
            errors.append(f"{label}.shipped_evidence: expected a list")
            shipped_evidence = []
        for evidence_index, evidence in enumerate(shipped_evidence):
            _validate_reference_path(
                errors,
                root,
                label,
                f"shipped_evidence[{evidence_index}]",
                evidence,
            )

        if state == "shipped":
            if not shipped_evidence:
                errors.append(
                    f"{label}.shipped_evidence: shipped state requires existing evidence"
                )
            if item.get("acceptance_gap") not in (None, ""):
                errors.append(
                    f"{label}.acceptance_gap: shipped state cannot retain an acceptance gap"
                )
        elif state in {"open", "superseded", "deferred"}:
            if not _is_nonempty(item.get("acceptance_gap")):
                errors.append(
                    f"{label}.acceptance_gap: {state} state requires a concrete gap"
                )
        if state == "open":
            work_reference = item.get("work_reference")
            prefix, separator, target = (
                str(work_reference).partition(":")
                if _is_nonempty(work_reference)
                else ("", "", "")
            )
            if not separator or prefix != "ticket" or target not in known_tickets:
                errors.append(
                    f"{label}.work_reference: open state requires a resolvable ticket"
                )

        target_release = _version_tuple(item.get("target_release"))
        if target_release is None:
            errors.append(f"{label}.target_release: expected a concrete semantic version")
        if state == "deferred":
            if not _is_nonempty(item.get("deferred_reason")):
                errors.append(
                    f"{label}.deferred_reason: deferred state requires a reason"
                )
            if (
                target_release is not None
                and active_release is not None
                and target_release <= active_release
            ):
                errors.append(
                    f"{label}.target_release: deferred target must be later than "
                    f"{register.get('active_delivery_release')}"
                )
        elif item.get("deferred_reason") is not None:
            errors.append(
                f"{label}.deferred_reason: only deferred items may define a reason"
            )

    _validate_supersession_graph(errors, items_by_id, known_tickets)

    try:
        version_text = _read_text(root, "VERSION", text_overrides).strip()
        pyproject = tomllib.loads(_read_text(root, "pyproject.toml", text_overrides))
        package_version = str(pyproject["project"]["version"])
        register_version = str(register.get("current_product_version"))
        if not (register_version == version_text == package_version):
            errors.append(
                "version_truth: current_product_version, VERSION, and "
                f"pyproject.toml disagree ({register_version!r}, {version_text!r}, "
                f"{package_version!r})"
            )
    except (OSError, KeyError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"version_truth: unable to read version sources: {exc}")

    for historical in HISTORICAL_SOURCES:
        try:
            text = _read_text(root, historical, text_overrides)
        except OSError as exc:
            errors.append(f"historical_source: unable to read {historical}: {exc}")
            continue
        expected_marker = (
            'status: "historical"'
            if historical.endswith("v0.6.0-implementation-plan.md")
            else "Status: historical"
        )
        if expected_marker not in text:
            errors.append(
                f"historical_source: {historical} is not marked historical"
            )
        if "LIVE-WORK-REGISTER.yaml" not in text:
            errors.append(
                f"historical_source: {historical} does not point to live status"
            )
        if re.search(r"(?im)^Status:\s*(?:active|draft)\s*$", text):
            errors.append(
                f"historical_source: {historical} reactivates historical work"
            )
        if re.search(r'(?im)^status:\s*"(?:active|draft)"\s*$', text):
            errors.append(
                f"historical_source: {historical} reactivates historical work"
            )

    for active in ACTIVE_SOURCES:
        try:
            text = _read_text(root, active, text_overrides)
        except OSError as exc:
            errors.append(f"active_source: unable to read {active}: {exc}")
            continue
        if "LIVE-WORK-REGISTER.yaml" not in text:
            errors.append(f"active_source: {active} does not name the live register")
        if "unchecked" not in text.lower() or "active work" not in text.lower():
            errors.append(
                f"active_source: {active} does not prevent checkbox reactivation"
            )
    try:
        roadmap = _read_text(root, "ROADMAP.md", text_overrides)
        active_delivery = str(register.get("active_delivery_release"))
        if active_delivery not in roadmap.partition("## Release Board")[0]:
            errors.append(
                f"active_source: ROADMAP.md current goal omits {active_delivery}"
            )
    except OSError:
        pass

    try:
        feedback = _read_text(
            root, "docs/feedback-round-2026-06.md", text_overrides
        )
        source_ids = FEEDBACK_HEADING_RE.findall(feedback)
        duplicate_source_ids = sorted(
            {item for item in source_ids if source_ids.count(item) > 1}
        )
        if duplicate_source_ids:
            errors.append(
                f"feedback_source: duplicate headings {duplicate_source_ids}"
            )
        missing_source_ids = sorted(set(EXPECTED_IDS) - set(source_ids))
        extra_source_ids = sorted(set(source_ids) - set(EXPECTED_IDS))
        if missing_source_ids or extra_source_ids:
            errors.append(
                "feedback_source: coverage mismatch "
                f"missing={missing_source_ids} extra={extra_source_ids}"
            )
    except OSError:
        pass

    deterministic_errors = sorted(set(errors))
    return {
        "passed": not deterministic_errors,
        "errors": deterministic_errors,
        "counts": {
            "expected_items": len(EXPECTED_IDS),
            "items": len(items),
            "states": state_counts,
            "sources": len(declared_sources),
        },
        "register": path.as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=pathlib.Path, default=REPO_ROOT)
    parser.add_argument("--register", type=pathlib.Path)
    args = parser.parse_args()
    result = validate_register(args.project_root, args.register)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
