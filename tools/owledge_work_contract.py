#!/usr/bin/env python3
"""Portable, fail-closed WorkContract v1 validation and state transitions."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import tempfile
from typing import Any


STATUSES = {"backlog", "ready", "claimed", "in_progress", "review", "qa", "blocked", "accepted", "done"}
TERMINAL = {"done"}
TRANSITIONS = {
    "backlog": {"ready", "blocked"}, "ready": {"claimed", "blocked"},
    "claimed": {"in_progress", "ready", "blocked"}, "in_progress": {"review", "blocked"},
    "review": {"qa", "in_progress", "blocked"}, "qa": {"accepted", "in_progress", "blocked"},
    "accepted": {"done", "in_progress"}, "blocked": {"ready", "in_progress"}, "done": set(),
}
REQUIRED = {"id", "goal", "target_user", "smallest_useful_outcome", "success_signal", "mvp_cutline", "definition_of_done", "qa_gates", "out_of_scope", "evidence_refs", "handoff", "unresolved_questions", "roadmap_dispositions", "dependencies", "status"}
OPTIONAL = {"claimed_by", "gate_refs"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_contract(contract: Any) -> list[str]:
    if not isinstance(contract, dict):
        return ["contract.type"]
    errors = [f"contract.missing:{key}" for key in sorted(REQUIRED - set(contract))]
    errors.extend(f"contract.unknown_field:{key}" for key in sorted(set(contract) - REQUIRED - OPTIONAL))
    if not _nonempty(contract.get("id")):
        errors.append("contract.id")
    for key in ("goal", "target_user", "smallest_useful_outcome", "success_signal", "mvp_cutline", "definition_of_done", "handoff"):
        if not _nonempty(contract.get(key)):
            errors.append(f"contract.{key}")
    for key in ("qa_gates", "out_of_scope", "evidence_refs", "unresolved_questions", "roadmap_dispositions", "dependencies"):
        if not isinstance(contract.get(key), list):
            errors.append(f"contract.{key}")
    if contract.get("status") not in STATUSES:
        errors.append("contract.status")
    return sorted(set(errors))


def validate_dag(contracts: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids = [item.get("id") for item in contracts if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        errors.append("dag.duplicate_id")
    known = set(ids)
    graph: dict[str, list[str]] = {}
    for item in contracts:
        errors.extend(validate_contract(item))
        item_id = item.get("id") if isinstance(item, dict) else None
        dependencies = item.get("dependencies", []) if isinstance(item, dict) else []
        if not isinstance(dependencies, list):
            continue
        graph[str(item_id)] = [str(dep) for dep in dependencies]
        for dependency in dependencies:
            if dependency not in known:
                errors.append(f"dag.missing_dependency:{item_id}:{dependency}")
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting:
            errors.append("dag.cycle")
            return
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph.get(node, []):
            visit(dependency)
        visiting.remove(node)
        visited.add(node)
    for item_id in graph:
        visit(item_id)
    return sorted(set(errors))


def transition(contract: dict[str, Any], target: str, *, actor: str, dependency_statuses: dict[str, str] | None = None, gate_refs: list[str] | None = None, evidence_refs: list[str] | None = None) -> dict[str, Any]:
    errors = validate_contract(contract)
    if errors:
        raise ValueError(",".join(errors))
    current = contract["status"]
    if target == "claimed" and contract.get("claimed_by") not in {None, actor}:
        raise ValueError("transition.double_claim")
    if target == "claimed" and any((dependency_statuses or {}).get(dependency) != "done" for dependency in contract["dependencies"]):
        raise ValueError("transition.dependencies_not_ready")
    if current in {"claimed", "in_progress", "review"} and contract.get("claimed_by") not in {None, actor}:
        raise ValueError("transition.actor_mismatch")
    if target not in TRANSITIONS[current]:
        raise ValueError("transition.not_allowed")
    if target in {"accepted", "done"}:
        if not gate_refs or not evidence_refs:
            raise ValueError("transition.gate_and_evidence_required")
        if not set(gate_refs).issubset(set(contract["qa_gates"])) or not set(evidence_refs).issubset(set(contract["evidence_refs"])):
            raise ValueError("transition.unrecognized_gate_or_evidence")
    updated = dict(contract)
    updated["status"] = target
    updated["claimed_by"] = actor if target == "claimed" else (None if target == "ready" else contract.get("claimed_by"))
    updated["gate_refs"] = gate_refs or contract.get("gate_refs", [])
    updated["evidence_refs"] = evidence_refs or contract["evidence_refs"]
    return updated


def atomic_transition(path: pathlib.Path, expected_status: str, target: str, *, actor: str, dependency_statuses: dict[str, str] | None = None, gate_refs: list[str] | None = None, evidence_refs: list[str] | None = None) -> dict[str, Any]:
    """Atomic single-file CAS; mismatched state leaves the original bytes untouched."""
    raw = path.read_text(encoding="utf-8")
    contract = json.loads(raw)
    if contract.get("status") != expected_status:
        raise ValueError("transition.compare_and_swap_failed")
    updated = transition(contract, target, actor=actor, dependency_statuses=dependency_statuses, gate_refs=gate_refs, evidence_refs=evidence_refs)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(updated, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except Exception:
        pathlib.Path(temporary).unlink(missing_ok=True)
        raise
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or atomically transition an Owledge WorkContract v1 JSON file.")
    parser.add_argument("contract")
    parser.add_argument("--contracts", nargs="*", default=[])
    parser.add_argument("--transition")
    parser.add_argument("--expected-status")
    parser.add_argument("--actor")
    parser.add_argument("--gate-ref", action="append", default=[])
    parser.add_argument("--evidence-ref", action="append", default=[])
    args = parser.parse_args()
    path = pathlib.Path(args.contract)
    contract = json.loads(path.read_text(encoding="utf-8"))
    contracts = [contract] + [json.loads(pathlib.Path(other).read_text(encoding="utf-8")) for other in args.contracts]
    errors = validate_dag(contracts)
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, indent=2))
        return 1
    if args.transition:
        if not args.expected_status or not args.actor:
            parser.error("--transition requires --expected-status and --actor")
        dependency_statuses = {item["id"]: item["status"] for item in contracts}
        contract = atomic_transition(path, args.expected_status, args.transition, actor=args.actor, dependency_statuses=dependency_statuses, gate_refs=args.gate_ref, evidence_refs=args.evidence_ref)
    print(json.dumps({"passed": True, "contract": contract}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
