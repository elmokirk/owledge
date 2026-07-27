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
ALIGNMENT_PROTOCOL = CONTROL_ROOT / "ALIGNMENT-PROTOCOL.md"
CONTROL_POLICY = CONTROL_ROOT / "CONTROL-PLANE-POLICY.md"
GOAL = CONTROL_ROOT / "GOAL.md"
ORCHESTRATION_PROTOCOL = CONTROL_ROOT / "ORCHESTRATION-PROTOCOL.md"
EXECUTION_MATRIX = CONTROL_ROOT / "AGENT-EXECUTION-MATRIX.yaml"

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

REQUIRED_ALIGNMENT_HEADINGS = [
    "## Feature Update",
    "## User Benefits and Adoption Impact",
    "## Gate and Evidence Summary",
    "## Implementation Findings: Problems, Gaps, and Deviations",
    "## Decision Log",
    "## Compatibility, Migration, and Operations",
    "## Known Limitations and Deferred Work",
    "## Next-Version Plan Reflection",
    "## Questions and Decisions Required",
    "## Recommendation and Safe Default",
    "## Recorded User Decision",
]

REQUIRED_ALIGNMENT_PROTOCOL_SECTIONS = [
    "## Hard Stop",
    "## Finding, Decision, and Question Capture During a Version",
    "## Next-Version Plan Reflection",
    "## Copy-Ready `/goal` Resume Prompt",
    "## Version Update Template",
]

ALIGNMENT_ROW = re.compile(
    r'^  - \{release: (?P<release>[^,]+), ticket: (?P<ticket>OW-[^,]+), gate: (?P<gate>G-[^,]+), '
    r'release_gate: (?P<release_gate>G-[^,]+), next_release: (?P<next_release>[^,]+), report: "(?P<report>[^"]+)"\}$',
    re.MULTILINE,
)


EXECUTION_ROW = re.compile(
    r"^  - \{id: (?P<id>OW-[^,]+), blockers: (?P<blockers>false|\[[^\]]*\]), "
    r"subagent: (?P<subagent>true|false), orchestrator: (?P<orchestrator>[^,]+), "
    r"model_profile: (?P<model>[^,]+), qa_checker: (?P<qa>true|false), "
    r"red_team: (?P<red>true|false), approval_mode: (?P<approval>[^,]+), "
    r"git_lane: (?P<lane>[^,]+), max_parallelism: (?P<parallel>\d+)\}$",
    re.MULTILINE,
)

EXECUTION_WAVE_ROW = re.compile(
    r"^  - \{id: (?P<id>W-[^,]+), release: (?P<release>[^,]+), "
    r"tickets: \[(?P<tickets>[^\]]*)\], policy: (?P<policy>[^,}]+)\}$",
    re.MULTILINE,
)


def parse_execution_rows(text: str) -> list[dict[str, str]]:
    return [match.groupdict() for match in EXECUTION_ROW.finditer(text)]


def parse_execution_waves(text: str) -> list[dict[str, Any]]:
    waves: list[dict[str, Any]] = []
    for match in EXECUTION_WAVE_ROW.finditer(text):
        wave = match.groupdict()
        wave["tickets"] = split_csv(wave["tickets"])
        waves.append(wave)
    return waves


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


def parse_alignment_rows(text: str) -> list[dict[str, str]]:
    return [match.groupdict() for match in ALIGNMENT_ROW.finditer(text)]


def validate_frontmatter(errors: list[str]) -> None:
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    import owledge_core as core  # type: ignore

    paths = [
        REPO_ROOT / "internal" / "owledge" / "plans" / "owledge-v1-autonomous-delivery-master-plan.md",
        REPO_ROOT / "internal" / "owledge" / "decisions" / "v0.7.1-v1-version-reflection-contract-2026-07-27.md",
        REPO_ROOT / "internal" / "owledge" / "workpackages" / "owledge-v1-autonomous-delivery-checklist.md",
        REPO_ROOT / "internal" / "owledge" / "reports" / "owledge-v1-roadmap-blindspot-analysis.md",
        CONTROL_ROOT / "GOAL.md",
        CONTROL_ROOT / "TRACEABILITY.md",
        CONTROL_POLICY,
        ALIGNMENT_PROTOCOL,
        TICKETS,
        GATES,
        ORCHESTRATION_PROTOCOL,
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
    alignment_text = read(ALIGNMENT_PROTOCOL)
    policy_text = read(CONTROL_POLICY)
    goal_text = read(GOAL)
    protocol_text = read(ORCHESTRATION_PROTOCOL)
    matrix_text = read(EXECUTION_MATRIX)
    rows = parse_ticket_rows(backlog_text)
    if not rows:
        errors.append("BACKLOG.yaml: no ticket rows matched the required contract")
        return {"passed": False, "errors": errors, "warnings": warnings}

    ids = [row["id"] for row in rows]
    known = set(ids)
    if len(ids) != len(known):
        errors.append("BACKLOG.yaml: duplicate ticket ids")

    execution_rows = parse_execution_rows(matrix_text)
    execution_by_id = {row["id"]: row for row in execution_rows}
    if len(execution_rows) != len(execution_by_id):
        errors.append("AGENT-EXECUTION-MATRIX.yaml: duplicate ticket ids")
    if set(execution_by_id) != known:
        errors.append(f"AGENT-EXECUTION-MATRIX.yaml: ticket coverage mismatch missing={sorted(known-set(execution_by_id))} extra={sorted(set(execution_by_id)-known)}")
    for row in rows:
        execution = execution_by_id.get(row["id"])
        if not execution:
            continue
        expected_blockers = "false" if not row["depends_on"] else "[" + ", ".join(row["depends_on"]) + "]"
        if execution["blockers"] != expected_blockers:
            errors.append(f"{row['id']}: execution-matrix blockers disagree with BACKLOG.yaml")
        if execution["subagent"] == "true" and execution["approval"] == "off":
            errors.append(f"{row['id']}: delegable ticket cannot have approval_mode=off")
        if execution["red"] == "true" and execution["qa"] != "true":
            errors.append(f"{row['id']}: Red Team requires QA")
        if int(execution["parallel"]) != 1:
            errors.append(f"{row['id']}: max_parallelism must remain 1 per ticket")
    gate_map = parse_gate_map(backlog_text)
    if not gate_map:
        errors.append("BACKLOG.yaml: no gates found")
    alignment_rows = parse_alignment_rows(backlog_text)

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
    if {row["release"] for row in alignment_rows} != set(release_order):
        errors.append("BACKLOG.yaml: version_alignment must contain exactly one row per release")
    if len(alignment_rows) != len({row["release"] for row in alignment_rows}):
        errors.append("BACKLOG.yaml: duplicate version_alignment release")

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

    row_by_id = {row["id"]: row for row in rows}

    def reaches(ticket_id: str, target_id: str, visited: set[str] | None = None) -> bool:
        if ticket_id == target_id:
            return True
        seen = visited or set()
        if ticket_id in seen:
            return False
        seen.add(ticket_id)
        return any(reaches(dep, target_id, seen.copy()) for dep in dependencies.get(ticket_id, []))

    for alignment in alignment_rows:
        release = alignment["release"]
        ticket_id = alignment["ticket"]
        gate = alignment["gate"]
        release_gate = alignment["release_gate"]
        next_release = alignment["next_release"]
        if ticket_id not in row_by_id:
            errors.append(f"version_alignment {release}: unknown ticket {ticket_id}")
            continue
        ticket_row = row_by_id[ticket_id]
        if ticket_row["release"] != release:
            errors.append(f"version_alignment {release}: ticket belongs to {ticket_row['release']}")
        if gate not in gate_map or gate_map[gate] != [ticket_id]:
            errors.append(f"version_alignment {release}: gate must contain only {ticket_id}")
        if release_gate not in gate_map:
            errors.append(f"version_alignment {release}: unknown release_gate {release_gate}")
        elif not set(ticket_row["depends_on"]) & set(gate_map[release_gate]):
            errors.append(f"version_alignment {release}: ticket must depend on its release-gate ticket")
        expected_report = f"release-updates/{release}.md"
        if alignment["report"] != expected_report:
            errors.append(f"version_alignment {release}: report must be {expected_report}")
        expected_next = "null" if release == release_order[-1] else release_order[release_rank[release] + 1]
        if next_release != expected_next:
            errors.append(f"version_alignment {release}: next_release must be {expected_next}")
        try:
            alignment_section = section(ticket_text, ticket_id)
        except ValueError:
            alignment_section = ""
        for phrase in [
            "awaiting_user_alignment",
            "approve",
            "adjust",
            "defer",
            "finding",
            "decision",
            "plan reflection",
        ]:
            if phrase not in alignment_section:
                errors.append(f"{ticket_id}: missing alignment action {phrase}")
        if next_release != "null":
            for next_ticket in (row for row in rows if row["release"] == next_release):
                if not reaches(next_ticket["id"], ticket_id):
                    errors.append(f"{next_ticket['id']}: is not blocked by prior alignment {ticket_id}")

    for heading in REQUIRED_ALIGNMENT_HEADINGS:
        if heading not in alignment_text:
            errors.append(f"ALIGNMENT-PROTOCOL.md: missing {heading}")
    for heading in REQUIRED_ALIGNMENT_PROTOCOL_SECTIONS:
        if heading not in alignment_text:
            errors.append(f"ALIGNMENT-PROTOCOL.md: missing {heading}")
    if "## Optional Autonomous Delivery" not in policy_text or "`subagent: true` is eligibility only" not in policy_text:
        errors.append("CONTROL-PLANE-POLICY.md: missing optional-delivery consent rule")
    if "# Optional Autonomous Delivery Protocol" not in protocol_text or "## Classification and Consent" not in protocol_text:
        errors.append("ORCHESTRATION-PROTOCOL.md: missing classification or consent protocol")
    if not (REPO_ROOT / "skills" / "owledge-autonomous-delivery" / "SKILL.md").is_file():
        errors.append("skills/owledge-autonomous-delivery/SKILL.md: missing")
    if (
        "## Version Alignment and User Authority" not in policy_text
        or "## Version Finding, Decision, and Question Registers" not in policy_text
        or "## Next-Version Reflection" not in policy_text
    ):
        errors.append("CONTROL-PLANE-POLICY.md: missing version-alignment, register, or next-version-reflection policy")
    if "## `/goal` Version-Stop Protocol" not in goal_text or "awaiting_user_alignment" not in goal_text:
        errors.append("GOAL.md: missing /goal version-stop contract")

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
        if gate in {item["gate"] for item in alignment_rows} and "User alignment:" not in gate_section:
            errors.append(f"{gate}: missing User alignment")
        tickets_line = re.search(r"^- Tickets:\s*(.+)$", gate_section, re.MULTILINE)
        references = set(re.findall(r"OW-\d{3}-\d{2}", tickets_line.group(1) if tickets_line else ""))
        if tickets_line:
            for start, end in re.findall(r"(OW-\d{3}-\d{2})`?\s+through\s+`?(OW-\d{3}-\d{2})", tickets_line.group(1)):
                if start in ids and end in ids:
                    references.update(ids[ids.index(start) : ids.index(end) + 1])
        missing_gate_refs = set(gate_map[gate]) - references
        if missing_gate_refs:
            errors.append(f"{gate}: Tickets line omits {sorted(missing_gate_refs)}")

    execution_waves = parse_execution_waves(backlog_text)
    wave_tickets = [
        ticket_id
        for wave in execution_waves
        for ticket_id in wave["tickets"]
    ]
    if set(wave_tickets) != known:
        errors.append(f"Execution-wave coverage mismatch: missing={sorted(known-set(wave_tickets))} extra={sorted(set(wave_tickets)-known)}")
    duplicates = sorted({item for item in wave_tickets if wave_tickets.count(item) > 1})
    if duplicates:
        errors.append(f"Tickets occur in multiple execution waves: {duplicates}")

    wave_by_ticket: dict[str, tuple[int, dict[str, Any]]] = {}
    previous_release_rank = -1
    for wave_index, wave in enumerate(execution_waves):
        wave_release = wave["release"]
        current_release_rank = release_rank.get(wave_release)
        if current_release_rank is None:
            errors.append(f"{wave['id']}: unknown execution-wave release {wave_release}")
        else:
            if current_release_rank < previous_release_rank:
                errors.append(
                    f"{wave['id']}: execution waves must follow release_order"
                )
            previous_release_rank = max(previous_release_rank, current_release_rank)
        for ticket_id in wave["tickets"]:
            if ticket_id in wave_by_ticket:
                continue
            wave_by_ticket[ticket_id] = (wave_index, wave)
            ticket_release = release_by_id.get(ticket_id)
            if ticket_release is not None and ticket_release != wave_release:
                errors.append(
                    f"{wave['id']}: ticket {ticket_id} belongs to {ticket_release}, not {wave_release}"
                )

    for ticket_id, ticket_dependencies in dependencies.items():
        dependent_location = wave_by_ticket.get(ticket_id)
        if dependent_location is None:
            continue
        dependent_index, dependent_wave = dependent_location
        for dependency_id in ticket_dependencies:
            dependency_location = wave_by_ticket.get(dependency_id)
            if dependency_location is None:
                continue
            dependency_index, dependency_wave = dependency_location
            if dependency_index == dependent_index:
                wave_kind = (
                    "parallel wave"
                    if dependent_wave["policy"] == "parallel_non_overlapping"
                    else "execution wave"
                )
                errors.append(
                    f"{ticket_id}: dependency {dependency_id} cannot share {wave_kind} "
                    f"{dependent_wave['id']}; dependencies must be in an earlier wave"
                )
            elif dependency_index > dependent_index:
                errors.append(
                    f"{ticket_id}: dependency {dependency_id} is scheduled in later wave "
                    f"{dependency_wave['id']}; it must precede {dependent_wave['id']}"
                )

    alignment_by_release = {
        alignment["release"]: alignment["ticket"]
        for alignment in alignment_rows
    }
    for wave_index, wave in enumerate(execution_waves):
        alignment_ticket = alignment_by_release.get(wave["release"])
        if wave["policy"] == "user_alignment_stop":
            if alignment_ticket is None or wave["tickets"] != [alignment_ticket]:
                errors.append(
                    f"{wave['id']}: user_alignment_stop must contain only the "
                    f"alignment ticket for {wave['release']}"
                )
        if alignment_ticket not in wave["tickets"]:
            continue
        if wave["policy"] != "user_alignment_stop":
            errors.append(
                f"{wave['id']}: alignment ticket {alignment_ticket} requires "
                "policy=user_alignment_stop"
            )
        later_same_release = [
            later_wave["id"]
            for later_wave in execution_waves[wave_index + 1 :]
            if later_wave["release"] == wave["release"]
        ]
        if later_same_release:
            errors.append(
                f"{wave['id']}: alignment stop must be the final wave for "
                f"{wave['release']}; later={later_same_release}"
            )

    ready = [row["id"] for row in rows if row["status"] == "ready"]
    run_state_text = read(RUN_STATE)
    for key in [
        "schema_version",
        "project",
        "plan",
        "objective",
        "status",
        "current_release",
        "current_phase",
        "active_ticket",
        "alignment",
        "execution_mode",
        "orchestration",
        "workspace",
        "blockers",
        "last_completed_actions",
        "next_actions",
        "last_commands",
        "updated_at",
        "updated_by",
    ]:
        if not re.search(rf"^{re.escape(key)}:", run_state_text, re.MULTILINE):
            errors.append(f"RUN-STATE.yaml: missing top-level key {key}")
    if "nullworkspace:" in run_state_text:
        errors.append("RUN-STATE.yaml: malformed merged orchestration/workspace key")
    active_match = re.search(r"^active_ticket:\s*(.+)$", run_state_text, re.MULTILINE)
    active = active_match.group(1).strip() if active_match else ""
    if active in {"", "null", "None"} and ready != ["OW-071-01"]:
        errors.append(f"Initial ready set must be ['OW-071-01'], got {ready}")
    if active not in {"", "null", "None"} and active not in known:
        errors.append(f"RUN-STATE.yaml: unknown active_ticket={active}")
    if active in {"", "null", "None"} and ready and ready[0] not in run_state_text:
        errors.append(f"RUN-STATE.yaml: next action does not identify ready ticket {ready[0]}")
    for key in [
        "state",
        "awaiting_release",
        "active_alignment_ticket",
        "user_decision",
        "open_questions",
        "findings",
        "decisions",
        "next_plan_reflection",
        "update_path",
    ]:
        if not re.search(rf"^  {re.escape(key)}:", run_state_text, re.MULTILINE):
            errors.append(f"RUN-STATE.yaml: missing alignment field {key}")
    for key in ["status", "target_release", "items"]:
        if not re.search(rf"^    {re.escape(key)}:", run_state_text, re.MULTILINE):
            errors.append(f"RUN-STATE.yaml: missing next_plan_reflection field {key}")

    validate_frontmatter(errors)

    for row in rows:
        if row["estimated_turns"] == 3:
            try:
                ticket_section = section(ticket_text, row["id"])
            except ValueError:
                continue
            checkpoint_line = re.search(r"^- Execution checkpoints:\s*(.+)$", ticket_section, re.MULTILINE)
            if not checkpoint_line:
                warnings.append(f"{row['id']}: three-turn ticket requires an internal checkpoint after each atomic result")

    return {
        "passed": not errors,
        "tickets": len(rows),
        "gates": len(gate_map),
        "execution_waves": len(execution_waves),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or selectively read the Owledge v1 delivery control plane")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ticket-id")
    group.add_argument("--gate-id")
    group.add_argument("--alignment-release")
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
        execution_rows = parse_execution_rows(read(EXECUTION_MATRIX))
        execution = next((item for item in execution_rows if item["id"] == args.ticket_id), None)
        if execution is None:
            raise SystemExit(f"Missing execution guidance for ticket: {args.ticket_id}")
        print(
            "Execution guidance: "
            f"blockers={execution['blockers']}; subagent={execution['subagent']}; "
            f"orchestrator={execution['orchestrator']}; model_profile={execution['model']}; "
            f"qa_checker={execution['qa']}; red_team={execution['red']}; "
            f"approval_mode={execution['approval']}; git_lane={execution['lane']}; "
            f"max_parallelism={execution['parallel']}\n\n"
        )
        print(section(read(TICKETS), args.ticket_id), end="")
        return 0
    if args.gate_id:
        print(section(read(GATES), args.gate_id), end="")
        return 0
    if args.alignment_release:
        alignment = next((item for item in parse_alignment_rows(read(BACKLOG)) if item["release"] == args.alignment_release), None)
        if alignment is None:
            raise SystemExit(f"Unknown alignment release: {args.alignment_release}")
        print(f"Alignment handoff: release={alignment['release']}; report={alignment['report']}; next_release={alignment['next_release']}\n\n")
        print(read(ALIGNMENT_PROTOCOL), end="\n")
        print(section(read(TICKETS), alignment["ticket"]), end="")
        print(section(read(GATES), alignment["gate"]), end="")
        return 0
    payload = validate()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
