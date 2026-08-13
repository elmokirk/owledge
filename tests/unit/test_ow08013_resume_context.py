from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge


class ResumeContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.temp.name)
        self.state = root / "RUN-STATE.yaml"
        self.state.write_text(
            "current_release: v0.8.0\nactive_ticket: OW-080-13\ncheckpoint:\n"
            "  last_completed_action: source committed\n"
            "  next_exact_action: run deterministic resume proof\n",
            encoding="utf-8",
        )
        self.controls = [root / "policy.md", root / "alignment.md"]
        for path in self.controls:
            path.write_text("# control\nThis is bounded control text.\n", encoding="utf-8")
        self.handoff = root / "handoff.md"
        self.handoff.write_text("# handoff\nNext action is deterministic.\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_persisted_runtime_skips_already_loaded_controls(self) -> None:
        result = owledge.resume_context_v1(
            self.state,
            self.controls,
            "persisted",
            {path.as_posix() for path in self.controls},
            self.handoff,
            handoff_in_context=True,
        )
        self.assertTrue(result["passed"])
        self.assertEqual("OW-080-13", result["session_slice"]["active_ticket"])
        self.assertTrue(all(not row["loaded"] for row in result["controls"]))
        self.assertFalse(result["handoff"]["loaded"])
        self.assertLess(result["warm_resume_drain"], result["cold_resume_drain"])

    def test_reset_baseline_requires_handoff_and_reloads_controls(self) -> None:
        missing = owledge.resume_context_v1(self.state, self.controls, "reset_baseline")
        self.assertEqual("resume_context.missing_handoff", missing["error"])
        result = owledge.resume_context_v1(self.state, self.controls, "reset_baseline", handoff_path=self.handoff)
        self.assertTrue(result["passed"])
        self.assertTrue(all(row["loaded"] for row in result["controls"]))
        self.assertTrue(result["handoff"]["loaded"])

    def test_invalid_runtime_fails_closed(self) -> None:
        result = owledge.resume_context_v1(self.state, self.controls, "unknown")
        self.assertEqual("resume_context.invalid_runtime_model", result["error"])

    def test_gate_payload_is_capped_but_preserves_audit_payload(self) -> None:
        payload = {"passed": False, "errors": [f"failure-{index}" for index in range(7)]}
        summary = owledge.capped_gate_payload(payload)
        self.assertEqual(5, len(summary["first_failings"]))
        gate = owledge.run_gate("fixture", lambda: payload)
        self.assertFalse(gate["passed"])
        self.assertEqual(payload, gate["audit_payload"])
        self.assertEqual(summary, gate["summary"])


if __name__ == "__main__":
    unittest.main()
