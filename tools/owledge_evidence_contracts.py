#!/usr/bin/env python3
"""Fail-closed Checkpoint, GateResult, and EvidenceManifest v1 validators."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Any

SHA = re.compile(r"^[a-f0-9]{7,64}$")


def _errors(value: Any, required: set[str], prefix: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{prefix}.type"]
    return [f"{prefix}.missing:{key}" for key in sorted(required - set(value))]


def validate_checkpoint(value: Any) -> list[str]:
    errors = _errors(value, {"ticket_id", "tested_commit", "input_hash", "next_action", "command_results", "side_effects", "idempotency"}, "checkpoint")
    if not isinstance(value, dict): return errors
    if not isinstance(value.get("ticket_id"), str) or not value.get("ticket_id"): errors.append("checkpoint.ticket_id")
    if not isinstance(value.get("tested_commit"), str) or not SHA.fullmatch(value["tested_commit"]): errors.append("checkpoint.tested_commit")
    if not isinstance(value.get("input_hash"), str) or not SHA.fullmatch(value["input_hash"]): errors.append("checkpoint.input_hash")
    if not isinstance(value.get("next_action"), str) or not value.get("next_action").strip(): errors.append("checkpoint.next_action")
    if not isinstance(value.get("side_effects"), list): errors.append("checkpoint.side_effects")
    if not isinstance(value.get("idempotency"), str) or not value.get("idempotency").strip(): errors.append("checkpoint.idempotency")
    results = value.get("command_results")
    if not isinstance(results, list) or not results: errors.append("checkpoint.command_results")
    elif any(not isinstance(row, dict) or not isinstance(row.get("command"), str) or not isinstance(row.get("exit_code"), int) for row in results): errors.append("checkpoint.command_result")
    return sorted(set(errors))


def validate_gate_result(value: Any, *, owner_actor: str | None = None) -> list[str]:
    errors = _errors(value, {"gate_id", "tested_commit", "input_hash", "passed", "thresholds", "evidence_refs", "reviewer", "limitations"}, "gate")
    if not isinstance(value, dict): return errors
    for key in ("gate_id", "reviewer"):
        if not isinstance(value.get(key), str) or not value.get(key): errors.append(f"gate.{key}")
    for key in ("tested_commit", "input_hash"):
        if not isinstance(value.get(key), str) or not SHA.fullmatch(value[key]): errors.append(f"gate.{key}")
    if value.get("passed") is not True: errors.append("gate.not_passed")
    for key in ("thresholds", "evidence_refs", "limitations"):
        if not isinstance(value.get(key), list): errors.append(f"gate.{key}")
    if not value.get("evidence_refs"): errors.append("gate.evidence_refs")
    if owner_actor and value.get("reviewer") == owner_actor: errors.append("gate.self_only_qa")
    return sorted(set(errors))


def validate_evidence_manifest(value: Any, *, expected_commit: str | None = None, expected_input_hash: str | None = None, owner_actor: str | None = None) -> list[str]:
    errors = _errors(value, {"checkpoint", "gate_result", "artifacts"}, "evidence")
    if not isinstance(value, dict): return errors
    checkpoint, gate = value.get("checkpoint"), value.get("gate_result")
    errors.extend(validate_checkpoint(checkpoint))
    errors.extend(validate_gate_result(gate, owner_actor=owner_actor))
    if isinstance(checkpoint, dict) and isinstance(gate, dict):
        if checkpoint.get("tested_commit") != gate.get("tested_commit") or checkpoint.get("input_hash") != gate.get("input_hash"): errors.append("evidence.checkpoint_gate_mismatch")
        if expected_commit and checkpoint.get("tested_commit") != expected_commit: errors.append("evidence.stale_commit")
        if expected_input_hash and checkpoint.get("input_hash") != expected_input_hash: errors.append("evidence.stale_input_hash")
    if not isinstance(value.get("artifacts"), list) or not value.get("artifacts"): errors.append("evidence.artifacts")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Owledge EvidenceManifest v1 JSON file.")
    parser.add_argument("manifest")
    parser.add_argument("--expected-commit")
    parser.add_argument("--expected-input-hash")
    parser.add_argument("--owner-actor")
    args = parser.parse_args()
    value = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
    errors = validate_evidence_manifest(value, expected_commit=args.expected_commit, expected_input_hash=args.expected_input_hash, owner_actor=args.owner_actor)
    print(json.dumps({"passed": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__": raise SystemExit(main())
