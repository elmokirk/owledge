from __future__ import annotations
import copy
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_evidence_contracts as evidence  # noqa: E402


def manifest() -> dict:
    return {"checkpoint": {"ticket_id": "OW-080-04", "tested_commit": "a" * 40, "input_hash": "b" * 64, "next_action": "resume exact action", "command_results": [{"command": "python -m unittest", "exit_code": 0}], "side_effects": [], "idempotency": "replay-safe"}, "gate_result": {"gate_id": "G-080-A-CONTRACTS", "tested_commit": "a" * 40, "input_hash": "b" * 64, "passed": True, "thresholds": ["all checks"], "evidence_refs": ["evidence/OW-080-04"], "reviewer": "independent-qa", "limitations": []}, "artifacts": ["evidence/OW-080-04/manifest.yaml"]}


class EvidenceContractTests(unittest.TestCase):
    def test_recovery_contract_binds_exact_action_commit_and_input(self):
        value = manifest()
        self.assertEqual(evidence.validate_evidence_manifest(value, expected_commit="a" * 40, expected_input_hash="b" * 64, owner_actor="worker"), [])

    def test_missing_exit_code_self_only_qa_stale_and_mismatch_fail(self):
        value = manifest(); value["checkpoint"]["command_results"] = [{"command": "test"}]
        self.assertIn("checkpoint.command_result", evidence.validate_evidence_manifest(value))
        value = manifest(); value["gate_result"]["reviewer"] = "worker"
        self.assertIn("gate.self_only_qa", evidence.validate_evidence_manifest(value, owner_actor="worker"))
        value = manifest(); value["gate_result"]["tested_commit"] = "c" * 40
        self.assertIn("evidence.checkpoint_gate_mismatch", evidence.validate_evidence_manifest(value))
        value = manifest()
        self.assertIn("evidence.stale_commit", evidence.validate_evidence_manifest(value, expected_commit="c" * 40))
        self.assertIn("evidence.stale_input_hash", evidence.validate_evidence_manifest(value, expected_input_hash="d" * 64))
