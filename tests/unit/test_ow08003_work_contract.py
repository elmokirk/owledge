from __future__ import annotations

import copy
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
import owledge_work_contract as work  # noqa: E402


def contract(identifier: str = "OW-TEST-01", dependencies: list[str] | None = None) -> dict:
    return {"id": identifier, "goal": "Ship a bounded outcome", "target_user": "maintainer", "smallest_useful_outcome": "validated contract", "success_signal": "focused tests pass", "mvp_cutline": "no runtime dispatch", "definition_of_done": "QA accepts", "qa_gates": ["G-test"], "out_of_scope": ["publish"], "evidence_refs": ["evidence/test"], "handoff": "next ticket", "unresolved_questions": [], "roadmap_dispositions": ["defer extras"], "dependencies": dependencies or [], "status": "ready"}


class WorkContractTests(unittest.TestCase):
    def test_dependency_dag_and_required_intent_are_fail_closed(self):
        parent = contract("OW-01")
        child = contract("OW-02", ["OW-01"])
        self.assertEqual(work.validate_dag([parent, child]), [])
        prose = {"id": "OW-bad", "status": "done"}
        self.assertIn("contract.goal", work.validate_contract(prose))
        cycle = [contract("OW-01", ["OW-02"]), contract("OW-02", ["OW-01"])]
        self.assertIn("dag.cycle", work.validate_dag(cycle))
        self.assertIn("dag.missing_dependency:OW-02:OW-missing", work.validate_dag([contract("OW-02", ["OW-missing"])]))

    def test_acceptance_requires_evidence_gates_and_single_claim(self):
        value = contract()
        claimed = work.transition(value, "claimed", actor="agent-a")
        with self.assertRaisesRegex(ValueError, "double_claim"):
            work.transition(claimed, "claimed", actor="agent-b")
        running = work.transition(claimed, "in_progress", actor="agent-a")
        review = work.transition(running, "review", actor="agent-a")
        qa = work.transition(review, "qa", actor="agent-a")
        with self.assertRaisesRegex(ValueError, "gate_and_evidence_required"):
            work.transition(qa, "accepted", actor="reviewer")
        accepted = work.transition(qa, "accepted", actor="reviewer", gate_refs=["G-test"], evidence_refs=["evidence/test"])
        self.assertEqual(accepted["status"], "accepted")

    def test_atomic_compare_and_swap_preserves_original_on_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "contract.json"
            original = contract()
            path.write_text(json.dumps(original), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "compare_and_swap_failed"):
                work.atomic_transition(path, "claimed", "in_progress", actor="agent-a")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)
            claimed = work.atomic_transition(path, "ready", "claimed", actor="agent-a")
            self.assertEqual(claimed["status"], "claimed")

    def test_public_cli_exposes_atomic_transition(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "contract.json"
            path.write_text(json.dumps(contract()), encoding="utf-8")
            result = subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "owledge.py"), "work-contract", "--contract", str(path), "--transition", "claimed", "--expected-status", "ready", "--actor", "agent-a"], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["status"], "claimed")


if __name__ == "__main__":
    unittest.main()
