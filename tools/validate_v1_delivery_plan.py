#!/usr/bin/env python3
"""Validate and selectively read the Owledge v1 autonomous delivery plan.

This tool intentionally uses only the Python standard library so the planning
control plane can be checked before project dependencies are installed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTROL_ROOT = REPO_ROOT / "internal" / "owledge" / "workpackages" / "owledge-v1-autonomous-delivery"
BACKLOG = CONTROL_ROOT / "BACKLOG.yaml"
TICKETS = CONTROL_ROOT / "tickets" / "ALL-TICKETS.md"
GATES = CONTROL_ROOT / "gates" / "ALL-GATES.md"
RUN_STATE = CONTROL_ROOT / "RUN-STATE.yaml"

TICKET_ROW = re.compile(
    r"^  - \{id: (?P<id>OW-[^,]+), release: (?P<release>[^,]+), phase: (?P<phase>[^,]+), "
    r"status: (?P<status>[^,]+), priority: (?P<priority>[^,]+), owner_role: (?P<owner>[^,]+), "
    r"qa_role: (?P<qa>[^,]+), estimated_turns: (?P<turns>\d+), depends_on: \[(?P<deps>[^\]]*)\], "
    r"gate: (?P<gate>[^,]+), path: \"(?P<path>[^\"]+)\"\}$",
    re.MULTILINE,
)

REQUIRED_TICKET_LABELS = [
    "Priority/dependencies:",
    "Outcome:",
    "Allowed paths:",
    "Implement:",
    "Accept:",
    "Verify/evidence:",
    "Negative QA:",
]

REQUIRED_GATE_LABELS = [
    "Tickets:",
    "Commands:",
    "Thresholds:",
    "Demonstrable increment:",
    "Promotion:",
]


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def section(text: str, item_id: str) -> str:
    match = re.search(rf"^### {re.escape(item_id)}(?:\s+-|\s|$).*?(?=^### |^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"No section found for {item_id}")
    return match.group(0).rstrip() + "\n"


def parse_ticket_rows(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match in TICKET_ROW.finditer(text):
        row = match.groupdict()
        row["depends_on"] = split_csv(row.pop("deps"))
        row["estimated_turns"] = int(row.pop("turns"))
        rows.append(row)
    return rows


def parse_gate_map(text: str) -> dict[str, list[str]]:
    return {
        gate: split_csv(ticket_ids)
        for gate, ticket_ids in re.findall(r"^  (G-[^:]+): \[([^\]]*)\]$", text, re.MULTILINE)
    }


def validate_frontmatter(errors: list[str]) -> None:
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    import owledge_core as core  # type: ignore

    paths = [
        REPO_ROOT / "internal" / "owledge" / "plans" / "owledge-v1-autonomous-delivery-master-plan.md",
        REPO_ROOT / "internal" / "owledge" / "workpackages" / "owledge-v1-autonomous-delivery-checklist.md",
        REPO_ROOT / "internal" / "owledge" / "reports" / "owledge-v1-roadmap-blindspot-analysis.md",
        CONTROL_ROOT / "GOAL.md",
        CONTROL_ROOT / "TRACEABILITY.md",
        CONTROL_ROOT / "CONTROL-PLANE-POLICY.md",
        TICKETS,
        GATES,
    ]
    memory_ids: set[str] = set()
    for path in paths:
        meta = core.parse_frontmatter(read(path))
        errors.extend(core.frontmatter_errors(meta, path.relative_to(REPO_ROOT).as_posix(), exportable_only=False))
        memory_id = str(meta.get("memory_id") or "")
        if not memory_id:
            errors.append(f"{path.name}: missing memory_id")
        elif memory_id in memory_ids:
            errors.append(f"{path.name}: duplicate memory_id={memory_id}")
        memory_ids.add(memory_id)


def validate() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    backlog_text = read(BACKLOG)
    ticket_text = read(TICKETS)
    gate_text = read(GATES)
    rows = parse_ticket_rows(backlog_text)
    if not rows:
        errors.append("BACKLOG.yaml: no ticket rows matched the required contract")
        return {"passed": False, "errors": errors, "warnings": warnings}

    ids = [row["id"] for row in rows]
    known = set(ids)
    if len(ids) != len(known):
        errors.append("BACKLOG.yaml: duplicate ticket ids")

    gate_map = parse_gate_map(backlog_text)
    if not gate_map:
        errors.append("BACKLOG.yaml: no gates found")

    assigned_to_gate: dict[str, list[str]] = {}
    for gate, ticket_ids in gate_map.items():
        for ticket_id in ticket_ids:
            assigned_to_gate.setdefault(ticket_id, []).append(gate)
            if ticket_id not in known:
                errors.append(f"{gate}: unknown ticket {ticket_id}")

    release_match = re.search(r"^release_order: \[([^\]]+)\]$", backlog_text, re.MULTILINE)
    release_order = split_csv(release_match.group(1)) if release_match else []
    release_rank = {release: index for index, release in enumerate(release_order)}
    if not release_order:
        errors.append("BACKLOG.yaml: release_order is missing")

    dependencies: dict[str, list[str]] = {}
    release_by_id = {row["id"]: row["release"] for row in rows}
    for row in rows:
        ticket_id = row["id"]
        dependencies[ticket_id] = row["depends_on"]
        missing = [item for item in row["depends_on"] if item not in known]
        if missing:
            errors.append(f"{ticket_id}: missing dependencies {missing}")
        for dependency in row["depends_on"]:
            if dependency in release_by_id and release_rank.get(release_by_id[dependency], 999) > release_rank.get(row["release"], -1):
                errors.append(f"{ticket_id}: depends on later release ticket {dependency}")
        if row["owner"] == row["qa"]:
            errors.append(f"{ticket_id}: owner_role and qa_role must differ")
        if not 1 <= row["estimated_turns"] <= 3:
            errors.append(f"{ticket_id}: estimated_turns must be 1..3")
        if row["gate"] not in gate_map:
            errors.append(f"{ticket_id}: unknown gate {row['gate']}")
        if assigned_to_gate.get(ticket_id) != [row["gate"]]:
            errors.append(f"{ticket_id}: gate membership disagrees with ticket row")
        if row["path"] != f"tickets/ALL-TICKETS.md#{ticket_id.lower()}":
            errors.append(f"{ticket_id}: invalid selective-read path {row['path']}")
        try:
            ticket_section = section(ticket_text, ticket_id)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for label in REQUIRED_TICKET_LABELS:
            if label not in ticket_section:
                errors.append(f"{ticket_id}: missing {label}")
        priority_line = re.search(r"^- Priority/dependencies:\s*([^;]+);(.*)$", ticket_section, re.MULTILINE)
        if not priority_line:
            errors.append(f"{ticket_id}: malformed Priority/dependencies line")
        else:
            if priority_line.group(1).strip() != row["priority"]:
                errors.append(f"{ticket_id}: priority disagrees with BACKLOG.yaml")
            section_deps = re.findall(r"`(OW-[^`]+)`", priority_line.group(2))
            if section_deps != row["depends_on"]:
                errors.append(f"{ticket_id}: dependency text disagrees with BACKLOG.yaml")
        allowed = re.search(r"^- Allowed paths:\s*(.+)$", ticket_section, re.MULTILINE)
        if not allowed or not allowed.group(1).strip():
            errors.append(f"{ticket_id}: Allowed paths must be non-empty")

    complete: set[str] = set()
    while True:
        previous = len(complete)
        complete.update(ticket_id for ticket_id, deps in dependencies.items() if set(deps) <= complete)
        if len(complete) == previous:
            break
    if complete != known:
        errors.append(f"BACKLOG.yaml: cyclic or unreachable tickets {sorted(known - complete)}")

    gate_headings = set(re.findall(r"^### (G-[^ ]+) ", gate_text, re.MULTILINE))
    if gate_headings != set(gate_map):
        errors.append(f"Gate heading mismatch: missing={sorted(set(gate_map)-gate_headings)} extra={sorted(gate_headings-set(gate_map))}")
    for gate in gate_map:
        try:
            gate_section = section(gate_text, gate)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for label in REQUIRED_GATE_LABELS:
            if label not in gate_section:
                errors.append(f"{gate}: missing {label}")
        tickets_line = re.search(r"^- Tickets:\s*(.+)$", gate_section, re.MULTILINE)
        references = set(re.findall(r"OW-\d{3}-\d{2}", tickets_line.group(1) if tickets_line else ""))
        if tickets_line:
            for start, end in re.findall(r"(OW-\d{3}-\d{2})`?\s+through\s+`?(OW-\d{3}-\d{2})", tickets_line.group(1)):
                if start in ids and end in ids:
                    references.update(ids[ids.index(start) : ids.index(end) + 1])
        missing_gate_refs = set(gate_map[gate]) - references
        if missing_gate_refs:
            errors.append(f"{gate}: Tickets line omits {sorted(missing_gate_refs)}")

    wave_tickets: list[str] = []
    for raw in re.findall(r"^  - \{id: W-[^}]+tickets: \[([^\]]*)\]", backlog_text, re.MULTILINE):
        wave_tickets.extend(split_csv(raw))
    if set(wave_tickets) != known:
        errors.append(f"Execution-wave coverage mismatch: missing={sorted(known-set(wave_tickets))} extra={sorted(set(wave_tickets)-known)}")
    duplicates = sorted({item for item in wave_tickets if wave_tickets.count(item) > 1})
    if duplicates:
        errors.append(f"Tickets occur in multiple execution waves: {duplicates}")

    ready = [row["id"] for row in rows if row["status"] == "ready"]
    run_state_text = read(RUN_STATE)
    active_match = re.search(r"^active_ticket:\s*(.+)$", run_state_text, re.MULTILINE)
    active = active_match.group(1).strip() if active_match else ""
    if active in {"", "null", "None"} and ready != ["OW-071-01"]:
        errors.append(f"Initial ready set must be ['OW-071-01'], got {ready}")
    if active not in {"", "null", "None"} and active not in known:
        errors.append(f"RUN-STATE.yaml: unknown active_ticket={active}")
    if active in {"", "null", "None"} and ready and ready[0] not in run_state_text:
        errors.append(f"RUN-STATE.yaml: next action does not identify ready ticket {ready[0]}")

    validate_frontmatter(errors)

    for row in rows:
        if row["estimated_turns"] == 3:
            warnings.append(f"{row['id']}: three-turn ticket requires an internal checkpoint after each atomic result")

    return {
        "passed": not errors,
        "tickets": len(rows),
        "gates": len(gate_map),
        "execution_waves": len(re.findall(r"^  - \{id: W-", backlog_text, re.MULTILINE)),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or selectively read the Owledge v1 delivery control plane")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ticket-id")
    group.add_argument("--gate-id")
    args = parser.parse_args()
    if args.ticket_id:
        rows = parse_ticket_rows(read(BACKLOG))
        row = next((item for item in rows if item["id"] == args.ticket_id), None)
        if row is None:
            raise SystemExit(f"Unknown ticket: {args.ticket_id}")
        print(
            "Assignment contract: "
            f"owner_role={row['owner']}; qa_role={row['qa']}; estimated_turns={row['estimated_turns']}; "
            f"gate={row['gate']}; depends_on={row['depends_on']}\n\n"
        )
        print(section(read(TICKETS), args.ticket_id), end="")
        return 0
    if args.gate_id:
        print(section(read(GATES), args.gate_id), end="")
        return 0
    payload = validate()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
