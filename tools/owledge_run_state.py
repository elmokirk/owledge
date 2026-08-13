#!/usr/bin/env python3
"""Dependency-free RUN-STATE sharding primitives for OW-080-14.

The legacy flat state remains the default format.  These helpers only create
and consume the pointer/register format when an explicit caller asks for it;
they never rewrite the legacy source file.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import argparse
from typing import Any


_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_VERSION = re.compile(r"^v\d+\.\d+(?:\.\d+)?$")
_ID = re.compile(r"^[A-Z]-\d{3}-\d{2}$")
_MANIFEST_KEYS = {"active_version", "active_ticket", "active_gate", "register_index", "last_checkpoint_sha"}


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token_count(text: str) -> int:
    return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))


def _scalar(text: str, key: str, indent: int = 0) -> str:
    found = re.search(rf"(?m)^{re.escape(' ' * indent)}{re.escape(key)}:\s*(.+?)\s*$", text)
    return found.group(1).strip().strip("\"'") if found else ""


def _mapping(text: str, key: str, indent: int = 0) -> dict[str, str]:
    start = re.search(rf"(?m)^{re.escape(' ' * indent)}{re.escape(key)}:\s*$", text)
    if not start:
        return {}
    rows: dict[str, str] = {}
    for line in text[start.end():].splitlines():
        if not line.strip():
            continue
        if len(line) - len(line.lstrip(" ")) <= indent:
            break
        match = re.match(r"^\s{2,}([^:#]+):\s*(.+?)\s*$", line)
        if match:
            rows[match.group(1).strip().strip("\"'")] = match.group(2).strip().strip("\"'")
    return rows


def _yaml_list_entries(text: str, key: str, indent: int = 2) -> list[dict[str, str]]:
    """Extract simple YAML list entries without making PyYAML a runtime dependency."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    start = re.search(rf"(?m)^{re.escape(' ' * indent)}{re.escape(key)}:\s*$", text)
    if not start:
        return []
    block = text[start.end():]
    next_section = re.search(rf"(?m)^{re.escape(' ' * indent)}[^\s-][^:]*:\s*$", block)
    if next_section:
        block = block[:next_section.start()]
    entries: list[dict[str, str]] = []
    for item in re.split(r"(?m)^\s{4}-\s+", block):
        item = item.strip()
        if not item:
            continue
        identifier = _scalar(item, "id")
        if not _ID.fullmatch(identifier):
            continue
        status_match = re.search(r"(?m)^\s*status:\s*(.+?)\s*$", item)
        status = status_match.group(1).strip().strip("\"'") if status_match else ""
        entries.append({"id": identifier, "content": item + "\n", "sha256": hashlib.sha256((item + "\n").encode("utf-8")).hexdigest(), "status": status})
    return entries


def _version_of(identifier: str) -> str:
    match = re.fullmatch(r"[FD]-(\d{3})-\d{2}", identifier)
    if not match:
        return ""
    series = match.group(1)
    return f"v{series[0]}.{series[1]}.{series[2]}"


def _contained_register_path(root: pathlib.Path, relative: str) -> pathlib.Path:
    path = pathlib.PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "registers":
        raise ValueError("run_state.register_index_invalid_path")
    candidate = (root / pathlib.Path(*path.parts)).resolve()
    root_resolved = root.resolve()
    if root_resolved not in candidate.parents:
        raise ValueError("run_state.register_index_invalid_path")
    return candidate


def parse_pointer_manifest(path: pathlib.Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError("run_state.pointer_missing")
    text = path.read_text(encoding="utf-8", errors="strict")
    values = {key: _scalar(text, key) for key in _MANIFEST_KEYS - {"register_index"}}
    index = _mapping(text, "register_index")
    if set(values) != _MANIFEST_KEYS - {"register_index"} or not index:
        raise ValueError("run_state.pointer_invalid")
    if not _VERSION.fullmatch(values["active_version"]) or not values["active_ticket"] or not values["active_gate"]:
        raise ValueError("run_state.pointer_invalid")
    if not _SHA256.fullmatch(values["last_checkpoint_sha"]):
        raise ValueError("run_state.pointer_invalid")
    if values["active_version"] not in index:
        raise ValueError("run_state.active_register_missing")
    for version, target in index.items():
        if not _VERSION.fullmatch(version):
            raise ValueError("run_state.register_index_invalid_version")
        _contained_register_path(path.parent, target)
    return {**values, "register_index": index, "path": path}


def load_active_register(path: pathlib.Path) -> dict[str, Any]:
    """Load exactly the pointer and active-version register, never history."""
    manifest = parse_pointer_manifest(path)
    register_path = _contained_register_path(path.parent, manifest["register_index"][manifest["active_version"]])
    if not register_path.is_file():
        raise ValueError("run_state.active_register_missing")
    register = json.loads(register_path.read_text(encoding="utf-8"))
    if register.get("version") != manifest["active_version"]:
        raise ValueError("run_state.active_register_version_mismatch")
    return {
        "passed": True,
        "manifest": {key: manifest[key] for key in _MANIFEST_KEYS},
        "register": register,
        "loaded_paths": [path.as_posix(), register_path.as_posix()],
        "loaded_file_content_tokens": token_count(path.read_text(encoding="utf-8")) + token_count(register_path.read_text(encoding="utf-8")),
    }


def resolve_register_entry(path: pathlib.Path, version: str, identifier: str) -> dict[str, Any]:
    """Explicit historical lookup; no historical register is read implicitly."""
    manifest = parse_pointer_manifest(path)
    if version not in manifest["register_index"]:
        raise ValueError("run_state.unknown_register_version")
    register_path = _contained_register_path(path.parent, manifest["register_index"][version])
    if not register_path.is_file():
        raise ValueError("run_state.register_missing")
    register = json.loads(register_path.read_text(encoding="utf-8"))
    for group in ("findings", "decisions", "tickets", "gates"):
        for entry in register.get(group, []):
            if entry.get("id") == identifier:
                return entry
    raise ValueError("run_state.identifier_not_found")


def migrate_legacy_run_state(legacy_path: pathlib.Path, output_root: pathlib.Path, active_version: str | None = None) -> dict[str, Any]:
    """Create sharded output under *output_root* without mutating *legacy_path*."""
    if not legacy_path.is_file():
        raise ValueError("run_state.legacy_missing")
    source_bytes = legacy_path.read_bytes()
    legacy_text = source_bytes.decode("utf-8")
    version = active_version or _scalar(legacy_text, "current_release")
    if not _VERSION.fullmatch(version):
        raise ValueError("run_state.invalid_active_version")
    active_ticket = _scalar(legacy_text, "active_ticket") or "OW-UNKNOWN"
    active_gate = _scalar(legacy_text, "last_green_gate") or "G-UNKNOWN"
    checkpoint_sha = hashlib.sha256(source_bytes).hexdigest()
    findings = _yaml_list_entries(legacy_text, "findings")
    decisions = _yaml_list_entries(legacy_text, "decisions")
    unresolved = {"open", "routed", "blocked", "in_progress", "awaiting_product_owner"}
    active_findings = [row for row in findings if _version_of(row["id"]) == version or row.get("status") in unresolved]
    active_decisions = [row for row in decisions if _version_of(row["id"]) == version]
    all_versions = sorted({version, *(_version_of(row["id"]) for row in findings + decisions if _version_of(row["id"]))})
    output_root.mkdir(parents=True, exist_ok=True)
    registers = output_root / "registers"
    registers.mkdir(parents=True, exist_ok=True)
    index: dict[str, str] = {}
    for register_version in all_versions:
        selected_findings = active_findings if register_version == version else [row for row in findings if _version_of(row["id"]) == register_version]
        selected_decisions = active_decisions if register_version == version else [row for row in decisions if _version_of(row["id"]) == register_version]
        register = {
            "schema_version": 1,
            "version": register_version,
            "legacy_state_sha256": checkpoint_sha,
            "findings": selected_findings,
            "decisions": selected_decisions,
            "tickets": [{"id": active_ticket, "sha256": hashlib.sha256(active_ticket.encode("utf-8")).hexdigest()}] if register_version == version else [],
            "gates": [{"id": active_gate, "sha256": hashlib.sha256(active_gate.encode("utf-8")).hexdigest()}] if register_version == version else [],
        }
        target = registers / f"{register_version}.json"
        target.write_text(json.dumps(register, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        index[register_version] = f"registers/{target.name}"
    manifest = output_root / "RUN-STATE.pointer.yaml"
    rows = [
        f"active_version: {version}",
        f"active_ticket: {active_ticket}",
        f"active_gate: {active_gate}",
        "register_index:",
        *[f"  {item_version}: {index[item_version]}" for item_version in sorted(index)],
        f"last_checkpoint_sha: {checkpoint_sha}",
    ]
    manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return {
        "passed": True,
        "legacy_path": legacy_path.as_posix(),
        "legacy_sha256_before": checkpoint_sha,
        "legacy_sha256_after": sha256_file(legacy_path),
        "legacy_unchanged": checkpoint_sha == sha256_file(legacy_path),
        "manifest_path": manifest.as_posix(),
        "manifest_bytes": manifest.stat().st_size,
        "manifest_tokens": token_count(manifest.read_text(encoding="utf-8")),
        "register_index": index,
        "active_version": version,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a copy-only sharded RUN-STATE fixture or migration output.")
    parser.add_argument("--legacy-state", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--active-version")
    args = parser.parse_args(argv)
    try:
        result = migrate_legacy_run_state(pathlib.Path(args.legacy_state), pathlib.Path(args.output_path), args.active_version)
    except (OSError, UnicodeError, ValueError) as exc:
        result = {"passed": False, "error": str(exc)}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
