#!/usr/bin/env python3
"""Validate the structured upgrade note for the current Owledge release."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
ALLOWED_BREAKING = ("yes", "no", "additive")
REQUIRED_FIELDS = ("breaking", "summary")


def _error(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _release_section(text: str, version: str) -> tuple[str | None, list[dict[str, str]]]:
    heading = re.compile(
        rf"^##\s+{re.escape(version)}(?:\s+\([^)]+\))?\s*$",
        re.MULTILINE,
    )
    matches = list(heading.finditer(text))
    if len(matches) != 1:
        return None, [
            _error(
                "release-section-count",
                f"expected exactly one release section for {version}; found {len(matches)}",
            )
        ]
    start = matches[0].end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end], []


def _upgrade_note_payload(
    section: str,
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    headings = list(
        re.finditer(r"^###\s+Upgrade notes\s*$", section, re.IGNORECASE | re.MULTILINE)
    )
    if len(headings) != 1:
        return None, [
            _error(
                "upgrade-heading-count",
                f"expected exactly one '### Upgrade notes' heading; found {len(headings)}",
            )
        ]
    note_start = headings[0].end()
    next_heading = re.search(r"^###\s+", section[note_start:], re.MULTILINE)
    note_end = note_start + next_heading.start() if next_heading else len(section)
    note_body = section[note_start:note_end]
    fences = re.findall(
        r"```json[ \t]*\r?\n(.*?)\r?\n```",
        note_body,
        re.IGNORECASE | re.DOTALL,
    )
    if len(fences) != 1:
        return None, [
            _error(
                "upgrade-json-fence-count",
                f"expected exactly one JSON fence in the current upgrade note; found {len(fences)}",
            )
        ]
    try:
        payload = json.loads(fences[0])
    except json.JSONDecodeError as exc:
        return None, [_error("upgrade-json-malformed", f"invalid JSON: {exc.msg}")]
    if not isinstance(payload, dict):
        return None, [_error("upgrade-note-type", "upgrade note JSON must be an object")]
    return payload, []


def _validate_payload(payload: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    keys = set(payload)
    for field in REQUIRED_FIELDS:
        if field not in payload:
            errors.append(_error(f"missing-{field}", f"required field is missing: {field}"))
    extras = sorted(keys - set(REQUIRED_FIELDS))
    if extras:
        errors.append(
            _error(
                "additional-properties",
                f"unknown fields are not allowed: {', '.join(extras)}",
            )
        )
    breaking = payload.get("breaking")
    if "breaking" in payload and breaking not in ALLOWED_BREAKING:
        errors.append(
            _error(
                "invalid-breaking",
                "breaking must be one of: yes, no, additive",
            )
        )
    summary = payload.get("summary")
    if "summary" in payload and (
        not isinstance(summary, str) or not summary.strip()
    ):
        errors.append(_error("invalid-summary", "summary must be a non-empty string"))
    return errors


def validate_upgrade_notes(
    project_root: pathlib.Path | str = REPO_ROOT,
    *,
    changelog_path: pathlib.Path | str | None = None,
    schema_path: pathlib.Path | str | None = None,
    version: str | None = None,
) -> dict[str, Any]:
    """Return deterministic structured validation for the current release note."""

    root = pathlib.Path(project_root).resolve()
    changelog = (
        pathlib.Path(changelog_path).resolve()
        if changelog_path is not None
        else root / "CHANGELOG.md"
    )
    schema = (
        pathlib.Path(schema_path).resolve()
        if schema_path is not None
        else root / "docs" / "upgrade-notes-schema.json"
    )
    errors: list[dict[str, str]] = []

    try:
        current_version = version or (root / "VERSION").read_text(
            encoding="utf-8"
        ).strip()
    except OSError as exc:
        current_version = ""
        errors.append(_error("version-read", f"unable to read VERSION: {exc}"))

    try:
        schema_payload = json.loads(schema.read_text(encoding="utf-8"))
        properties = schema_payload.get("properties", {})
        breaking_schema = properties.get("breaking", {})
        summary_schema = properties.get("summary", {})
        if (
            schema_payload.get("type") != "object"
            or schema_payload.get("required") != list(REQUIRED_FIELDS)
            or schema_payload.get("additionalProperties") is not False
            or set(properties) != set(REQUIRED_FIELDS)
            or breaking_schema.get("type") != "string"
            or breaking_schema.get("enum") != list(ALLOWED_BREAKING)
            or summary_schema.get("type") != "string"
            or summary_schema.get("minLength") != 1
        ):
            errors.append(
                _error(
                    "schema-contract",
                    "upgrade-notes schema does not match the frozen v1 contract",
                )
            )
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(_error("schema-read", f"unable to read schema: {exc}"))

    payload: dict[str, Any] | None = None
    if current_version:
        try:
            changelog_text = changelog.read_text(encoding="utf-8")
            section, section_errors = _release_section(
                changelog_text, current_version
            )
            errors.extend(section_errors)
            if section is not None:
                payload, payload_errors = _upgrade_note_payload(section)
                errors.extend(payload_errors)
                if payload is not None:
                    errors.extend(_validate_payload(payload))
        except OSError as exc:
            errors.append(_error("changelog-read", f"unable to read changelog: {exc}"))

    deterministic_errors = sorted(
        errors,
        key=lambda item: (item["code"], item["message"]),
    )
    return {
        "schema_version": 1,
        "passed": not deterministic_errors,
        "version": current_version,
        "changelog": "CHANGELOG.md" if changelog == root / "CHANGELOG.md" else changelog.name,
        "schema": (
            "docs/upgrade-notes-schema.json"
            if schema == root / "docs" / "upgrade-notes-schema.json"
            else schema.name
        ),
        "note": payload,
        "errors": deterministic_errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current structured Owledge upgrade note."
    )
    parser.add_argument("--project-root", default=str(REPO_ROOT))
    parser.add_argument("--changelog", default=None)
    parser.add_argument("--schema", default=None)
    parser.add_argument("--version", default=None)
    args = parser.parse_args(argv)
    result = validate_upgrade_notes(
        args.project_root,
        changelog_path=args.changelog,
        schema_path=args.schema,
        version=args.version,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
