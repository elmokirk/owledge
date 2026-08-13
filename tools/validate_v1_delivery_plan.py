#!/usr/bin/env python3
"""Validate the single active Owledge V1 Minimal Core control plane."""

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
POLICY = CONTROL_ROOT / "CONTROL-PLANE-POLICY.md"
TRACEABILITY = CONTROL_ROOT / "TRACEABILITY.md"
EXECUTION_MATRIX = CONTROL_ROOT / "AGENT-EXECUTION-MATRIX.yaml"
ACTIVE_PLAN = REPO_ROOT / "internal" / "owledge" / "plans" / "owledge-v1-minimal-core-finalization-plan.md"
HANDOFF = REPO_ROOT / "internal" / "owledge" / "workpackages" / "owledge-v1-minimal-core-goal-handoff.md"
DECISION = REPO_ROOT / "internal" / "owledge" / "decisions" / "v1-minimal-core-and-product-surfaces-2026-08-13.md"
PARKING = REPO_ROOT / "internal" / "owledge" / "ideas" / "post-v1-feature-parking-lot.md"
CHECKLIST = REPO_ROOT / "internal" / "owledge" / "workpackages" / "owledge-v1-minimal-core-finalization-checklist.md"
HISTORICAL_PLAN = REPO_ROOT / "internal" / "owledge" / "plans" / "owledge-v1-autonomous-delivery-master-plan.md"

TICKET_ID = r"V1M-\d{2}"
TICKET_ROW = re.compile(
    rf"^  - \{{id: (?P<id>{TICKET_ID}), release: (?P<release>[^,]+), phase: (?P<phase>[^,]+), "
    r"status: (?P<status>[^,]+), priority: (?P<priority>[^,]+), owner_role: (?P<owner>[^,]+), "
    r"qa_role: (?P<qa>[^,]+), estimated_turns: (?P<turns>\d+), depends_on: \[(?P<deps>[^\]]*)\], "
    r"gate: (?P<gate>[^,]+), path: \"(?P<path>[^\"]+)\"\}$",
    re.MULTILINE,
)
EXECUTION_ROW = re.compile(
    rf"^  - \{{id: (?P<id>{TICKET_ID}), blockers: (?P<blockers>false|\[[^\]]*\]), "
    r"subagent: (?P<subagent>true|false), orchestrator: (?P<orchestrator>[^,]+), "
    r"model_profile: (?P<model>[^,]+), qa_checker: (?P<qa>true|false), "
    r"red_team: (?P<red>true|false), approval_mode: (?P<approval>[^,]+), "
    r"git_lane: (?P<lane>[^,]+), max_parallelism: (?P<parallel>\d+)\}$",
    re.MULTILINE,
)
WAVE_ROW = re.compile(
    r"^  - \{id: (?P<id>W-V1M-[^,]+), release: (?P<release>[^,]+), tickets: \[(?P<tickets>[^\]]*)\], policy: (?P<policy>[^}]+)\}$",
    re.MULTILINE,
)
EXPECTED_LEGACY_UNSTARTED = {
    "OW-081-04", "OW-081-07", "OW-081-08", "OW-081-09", "OW-081-10", "OW-081-11",
    "OW-090-01", "OW-090-02", "OW-090-03", "OW-090-04", "OW-090-05", "OW-090-06",
    "OW-090-07", "OW-090-08", "OW-090-09", "OW-090-10", "OW-090-11", "OW-100-01",
    "OW-100-02", "OW-100-03", "OW-100-04", "OW-100-05", "OW-100-06", "OW-100-07",
    "OW-100-08", "OW-100-09", "OW-100-10", "OW-100-11",
}
EXPECTED_BUDGET = {
    "public_cli_verbs": ["init", "doctor", "recall", "context", "propose", "review", "sync", "upgrade"],
    "mcp_tools": ["capabilities", "recall", "context", "propose", "review"],
    "scopes": ["project_user", "user_global"],
    "reference_adapters": ["codex", "claude_code", "generic_mcp_cli"],
}
REQUIRED_TICKET_LABELS = ["Priority/dependencies:", "Outcome:", "Allowed paths:", "Implement:", "Accept:", "Verify/evidence:", "Negative QA:"]
REQUIRED_GATE_LABELS = ["Tickets:", "Commands:", "Thresholds:", "Demonstrable increment:", "Promotion:"]


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


def parse_execution_rows(text: str) -> list[dict[str, str]]:
    return [match.groupdict() for match in EXECUTION_ROW.finditer(text)]


def parse_execution_waves(text: str) -> list[dict[str, Any]]:
    return [{**match.groupdict(), "tickets": split_csv(match.group("tickets"))} for match in WAVE_ROW.finditer(text)]


def parse_gate_map(text: str) -> dict[str, list[str]]:
    return {gate: split_csv(ids) for gate, ids in re.findall(r"^  (G-V1M-[^:]+): \[([^\]]*)\]$", text, re.MULTILINE)}


def parse_inline_list(text: str, key: str) -> list[str] | None:
    match = re.search(rf"^  {re.escape(key)}: \[([^\]]*)\]$", text, re.MULTILINE)
    return split_csv(match.group(1)) if match else None


def validate_frontmatter(errors: list[str]) -> None:
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    import owledge_core as core  # type: ignore

    memory_ids: set[str] = set()
    for path in [ACTIVE_PLAN, DECISION, PARKING, CHECKLIST, HANDOFF, HISTORICAL_PLAN, TICKETS, GATES, TRACEABILITY, POLICY, CONTROL_ROOT / "GOAL.md"]:
        metadata = core.parse_frontmatter(read(path))
        errors.extend(core.frontmatter_errors(metadata, path.relative_to(REPO_ROOT).as_posix(), exportable_only=False))
        if not metadata.get("document_version"):
            errors.append(f"{path.name}: missing document_version")
        memory_id = str(metadata.get("memory_id") or "")
        if not memory_id:
            errors.append(f"{path.name}: missing memory_id")
        elif memory_id in memory_ids:
            errors.append(f"{path.name}: duplicate memory_id={memory_id}")
        memory_ids.add(memory_id)


def validate_backlog(backlog_text: str) -> dict[str, Any]:
    errors: list[str] = []
    rows = parse_ticket_rows(backlog_text)
    ids = [row["id"] for row in rows]
    known = set(ids)
    if not rows:
        errors.append("BACKLOG.yaml: no active V1M ticket rows matched")
        return {"passed": False, "errors": errors, "warnings": []}
    if len(ids) != len(known):
        errors.append("BACKLOG.yaml: duplicate active ticket ids")
    if ids != [f"V1M-{index:02d}" for index in range(1, 12)]:
        errors.append("BACKLOG.yaml: active V1M tickets must be V1M-01 through V1M-11 in order")
    if "active_train: v1-minimal-core" not in backlog_text:
        errors.append("BACKLOG.yaml: active_train must be v1-minimal-core")
    allowed_match = re.search(r"^status_values: \[([^\]]+)\]$", backlog_text, re.MULTILINE)
    allowed = set(split_csv(allowed_match.group(1))) if allowed_match else set()
    if not allowed:
        errors.append("BACKLOG.yaml: status_values is missing")
    for row in rows:
        if row["status"] not in allowed:
            errors.append(f"{row['id']}: unknown status {row['status']}")
        if row["owner"] == row["qa"]:
            errors.append(f"{row['id']}: owner_role and qa_role must differ")
        if not 1 <= row["estimated_turns"] <= 3:
            errors.append(f"{row['id']}: estimated_turns must be 1..3")
        if row["path"] != f"tickets/ALL-TICKETS.md#{row['id'].lower()}":
            errors.append(f"{row['id']}: invalid selective-read path {row['path']}")

    gate_map = parse_gate_map(backlog_text)
    expected_gates = {"G-V1M-PLAN", "G-V1M-SURFACE", "G-V1M-READ", "G-V1M-LIFECYCLE", "G-V1M-ADAPTERS", "G-V1M-GA", "G-V1M-PUBLISH"}
    if set(gate_map) != expected_gates:
        errors.append(f"BACKLOG.yaml: active gate set mismatch missing={sorted(expected_gates-set(gate_map))} extra={sorted(set(gate_map)-expected_gates)}")
    assigned: dict[str, list[str]] = {}
    for gate, tickets in gate_map.items():
        for ticket_id in tickets:
            assigned.setdefault(ticket_id, []).append(gate)
            if ticket_id not in known:
                errors.append(f"{gate}: unknown active ticket {ticket_id}")
    dependencies = {row["id"]: row["depends_on"] for row in rows}
    for row in rows:
        missing = [dep for dep in row["depends_on"] if dep not in known]
        if missing:
            errors.append(f"{row['id']}: missing dependencies {missing}")
        if row["gate"] not in gate_map or assigned.get(row["id"]) != [row["gate"]]:
            errors.append(f"{row['id']}: gate membership disagrees with ticket row")
    complete: set[str] = set()
    while True:
        before = len(complete)
        complete.update(ticket_id for ticket_id, deps in dependencies.items() if set(deps) <= complete)
        if len(complete) == before:
            break
    if complete != known:
        errors.append(f"BACKLOG.yaml: cyclic or unreachable tickets {sorted(known-complete)}")

    dispositions = re.findall(r"^  - \{id: (OW-\d{3}-\d{2}), disposition: (mapped|post_v1), (?:v1m: (V1M-\d{2})|park_ref: (PARK-\d{3})), reason: \"[^\"]+\"\}$", backlog_text, re.MULTILINE)
    found_legacy = {item[0] for item in dispositions}
    if found_legacy != EXPECTED_LEGACY_UNSTARTED:
        errors.append(f"BACKLOG.yaml: legacy disposition coverage mismatch missing={sorted(EXPECTED_LEGACY_UNSTARTED-found_legacy)} extra={sorted(found_legacy-EXPECTED_LEGACY_UNSTARTED)}")
    parking_ids = set(re.findall(r"^\| (PARK-\d{3}) \|", read(PARKING), re.MULTILINE))
    for legacy_id, disposition, v1m, park in dispositions:
        if disposition == "mapped" and v1m not in known:
            errors.append(f"{legacy_id}: mapped V1M ticket must exist")
        if disposition == "post_v1" and not park:
            errors.append(f"{legacy_id}: post_v1 disposition requires PARK-* reference")
        if disposition == "post_v1" and park not in parking_ids:
            errors.append(f"{legacy_id}: park_ref {park} is not present in the canonical parking lot")

    for key, expected in EXPECTED_BUDGET.items():
        actual = parse_inline_list(backlog_text, key)
        if actual != expected:
            errors.append(f"complexity_budget.{key} must equal {expected}, got {actual}")
    files = re.search(r"^  minimal_profile: \{max_files: (\d+), max_directories: (\d+)\}$", backlog_text, re.MULTILINE)
    if not files or files.group(1) != "15" or files.group(2) != "8":
        errors.append("complexity_budget.minimal_profile must be max_files=15 and max_directories=8")

    waves = parse_execution_waves(backlog_text)
    wave_ids = [ticket for wave in waves for ticket in wave["tickets"]]
    if set(wave_ids) != known or len(wave_ids) != len(set(wave_ids)):
        errors.append("BACKLOG.yaml: execution waves must cover every active V1M ticket exactly once")
    locations = {ticket: (index, wave) for index, wave in enumerate(waves) for ticket in wave["tickets"]}
    for row in rows:
        for dep in row["depends_on"]:
            if dep in locations and row["id"] in locations and locations[dep][0] >= locations[row["id"]][0]:
                errors.append(f"{row['id']}: dependency {dep} must be in an earlier execution wave")
    if waves and (waves[-1]["policy"] != "user_authorization_stop" or waves[-1]["tickets"] != ["V1M-11"]):
        errors.append("BACKLOG.yaml: V1M-11 must be the final user_authorization_stop wave")
    return {"passed": not errors, "tickets": len(rows), "gates": len(gate_map), "execution_waves": len(waves), "errors": errors, "warnings": []}


def validate() -> dict[str, Any]:
    backlog_text = read(BACKLOG)
    result = validate_backlog(backlog_text)
    errors: list[str] = result["errors"]
    rows = parse_ticket_rows(backlog_text)
    known = {row["id"] for row in rows}
    ticket_text = read(TICKETS)
    for row in rows:
        try:
            ticket = section(ticket_text, row["id"])
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for label in REQUIRED_TICKET_LABELS:
            if label not in ticket:
                errors.append(f"{row['id']}: missing {label}")
        priority = re.search(r"^- Priority/dependencies:\s*([^;]+);(.*)$", ticket, re.MULTILINE)
        if not priority or priority.group(1).strip() != row["priority"]:
            errors.append(f"{row['id']}: priority disagrees with BACKLOG.yaml")
        elif re.findall(r"`(V1M-\d{2})`", priority.group(2)) != row["depends_on"]:
            errors.append(f"{row['id']}: dependency text disagrees with BACKLOG.yaml")

    gates_text = read(GATES)
    gate_map = parse_gate_map(backlog_text)
    for gate, ticket_ids in gate_map.items():
        try:
            gate_text = section(gates_text, gate)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for label in REQUIRED_GATE_LABELS:
            if label not in gate_text:
                errors.append(f"{gate}: missing {label}")
        references = set(re.findall(TICKET_ID, re.search(r"^- Tickets:\s*(.+)$", gate_text, re.MULTILINE).group(1) if re.search(r"^- Tickets:\s*(.+)$", gate_text, re.MULTILINE) else ""))
        if set(ticket_ids) - references:
            errors.append(f"{gate}: Tickets line omits {sorted(set(ticket_ids)-references)}")

    execution = parse_execution_rows(read(EXECUTION_MATRIX))
    by_execution = {row["id"]: row for row in execution}
    if set(by_execution) != known or len(execution) != len(by_execution):
        errors.append("AGENT-EXECUTION-MATRIX.yaml: active V1M ticket coverage mismatch")
    for row in rows:
        current = by_execution.get(row["id"])
        if not current:
            continue
        expected = "false" if not row["depends_on"] else "[" + ", ".join(row["depends_on"]) + "]"
        if current["blockers"] != expected:
            errors.append(f"{row['id']}: execution-matrix blockers disagree with BACKLOG.yaml")
        if current["subagent"] == "true" and current["approval"] == "off":
            errors.append(f"{row['id']}: delegable ticket cannot have approval_mode=off")
        if current["red"] == "true" and current["qa"] != "true":
            errors.append(f"{row['id']}: Red Team requires QA")
        if current["parallel"] != "1":
            errors.append(f"{row['id']}: max_parallelism must remain 1")

    run_state = read(RUN_STATE)
    for key in ["schema_version", "document_version", "project", "plan", "objective", "status", "current_release", "current_phase", "active_ticket", "alignment", "execution_mode", "orchestration", "workspace", "blockers", "last_completed_actions", "next_actions", "last_commands", "updated_at", "updated_by"]:
        if not re.search(rf"^{re.escape(key)}:", run_state, re.MULTILINE):
            errors.append(f"RUN-STATE.yaml: missing top-level key {key}")
    if "plan: internal/owledge/plans/owledge-v1-minimal-core-finalization-plan.md" not in run_state:
        errors.append("RUN-STATE.yaml: active plan must be the V1 Minimal Core plan")
    active_match = re.search(r"^active_ticket:\s*(.+)$", run_state, re.MULTILINE)
    active = active_match.group(1).strip() if active_match else ""
    clean_gate_stop = active in {"", "null", "None"} and "last_green_gate: G-V1M-PLAN" in run_state and "Select V1M-02" in run_state
    if active not in known and not clean_gate_stop:
        errors.append(f"RUN-STATE.yaml: active_ticket must be active V1M ticket, got {active}")
    if active == "V1M-01" and next(row["status"] for row in rows if row["id"] == active) != "in_progress":
        errors.append("RUN-STATE.yaml: V1M-01 must be in_progress while plan gate is open")
    v1m01 = next(row for row in rows if row["id"] == "V1M-01")
    if v1m01["status"] == "done":
        manifest = CONTROL_ROOT / "evidence" / "G-V1M-PLAN" / "manifest.yaml"
        if not manifest.is_file():
            errors.append("G-V1M-PLAN: missing gate evidence manifest after V1M-01 completion")
        else:
            manifest_text = read(manifest)
            if "status: accepted_independent_qa" not in manifest_text:
                errors.append("G-V1M-PLAN: completed V1M-01 requires accepted_independent_qa manifest")
        if "last_green_gate: G-V1M-PLAN" not in run_state:
            errors.append("RUN-STATE.yaml: completed V1M-01 requires last_green_gate G-V1M-PLAN")
        if next((row["status"] for row in rows if row["id"] == "V1M-02"), None) != "ready":
            errors.append("BACKLOG.yaml: green G-V1M-PLAN requires V1M-02 ready")

    traceability = read(TRACEABILITY)
    for ticket_id in known:
        if ticket_id not in traceability:
            errors.append(f"TRACEABILITY.md: missing active {ticket_id}")
    active_trace = traceability.split("## Appendix A", 1)[0]
    if re.search(r"\b(?:OW-081-07|OW-090-05|OW-100-11)\b", active_trace):
        errors.append("TRACEABILITY.md: active V1M matrix leaks legacy/parked ticket references")
    if "G-081-A-ADAPTERS evidence" not in traceability:
        errors.append("TRACEABILITY.md: missing reused G-081-A evidence reference")
    for path in [ACTIVE_PLAN, DECISION, PARKING, CHECKLIST, HANDOFF]:
        if not path.is_file():
            errors.append(f"missing immutable V1M envelope artifact: {path.relative_to(REPO_ROOT)}")
    validate_frontmatter(errors)
    result["errors"] = errors
    result["passed"] = not errors
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or selectively read the active Owledge V1 Minimal Core control plane")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ticket-id")
    group.add_argument("--gate-id")
    args = parser.parse_args()
    if args.ticket_id:
        row = next((item for item in parse_ticket_rows(read(BACKLOG)) if item["id"] == args.ticket_id), None)
        if row is None:
            raise SystemExit(f"Unknown active ticket: {args.ticket_id}")
        print(f"Assignment contract: owner_role={row['owner']}; qa_role={row['qa']}; estimated_turns={row['estimated_turns']}; gate={row['gate']}; depends_on={row['depends_on']}\n")
        print(section(read(TICKETS), args.ticket_id), end="")
        return 0
    if args.gate_id:
        if args.gate_id not in parse_gate_map(read(BACKLOG)):
            raise SystemExit(f"Unknown active gate: {args.gate_id}")
        print(section(read(GATES), args.gate_id), end="")
        return 0
    payload = validate()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
