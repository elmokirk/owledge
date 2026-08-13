from __future__ import annotations

import importlib.util
import pathlib
import re
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "tools" / "validate_v1_delivery_plan.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_v1_delivery_plan", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load delivery validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateV1MinimalCorePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_validator()

    def validate_backlog(self, value: str):
        original = self.validator.BACKLOG
        with tempfile.TemporaryDirectory() as directory:
            temporary = pathlib.Path(directory) / "BACKLOG.yaml"
            temporary.write_text(value, encoding="utf-8")
            self.validator.BACKLOG = temporary
            try:
                return self.validator.validate()
            finally:
                self.validator.BACKLOG = original

    def validate_run_state(self, value: str):
        original = self.validator.RUN_STATE
        with tempfile.TemporaryDirectory() as directory:
            temporary = pathlib.Path(directory) / "RUN-STATE.yaml"
            temporary.write_text(value, encoding="utf-8")
            self.validator.RUN_STATE = temporary
            try:
                return self.validator.validate()
            finally:
                self.validator.RUN_STATE = original

    def test_current_control_plane_is_valid(self) -> None:
        result = self.validator.validate()
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(result["tickets"], 11)
        self.assertEqual(result["gates"], 7)

    def test_parked_legacy_ticket_cannot_become_active_dependency(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        mutated = current.replace(
            "depends_on: [V1M-01], gate: G-V1M-SURFACE",
            "depends_on: [V1M-01, OW-081-04], gate: G-V1M-SURFACE",
            1,
        )
        result = self.validate_backlog(mutated)
        self.assertFalse(result["passed"])
        self.assertIn("V1M-02: missing dependencies ['OW-081-04']", result["errors"])

    def test_missing_legacy_disposition_fails_closed(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        line = '  - {id: OW-090-08, disposition: post_v1, park_ref: PARK-015, reason: "LightRAG adapter is an add-on."}\n'
        self.assertIn(line, current)
        result = self.validate_backlog(current.replace(line, "", 1))
        self.assertFalse(result["passed"])
        self.assertTrue(any(error.startswith("BACKLOG.yaml: legacy disposition coverage mismatch") for error in result["errors"]), result["errors"])

    def test_unknown_park_reference_fails_closed(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        result = self.validate_backlog(current.replace("park_ref: PARK-007", "park_ref: PARK-999", 1))
        self.assertFalse(result["passed"])
        self.assertIn("OW-081-04: park_ref PARK-999 is not present in the canonical parking lot", result["errors"])

    def test_ninth_public_verb_fails_closed(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        result = self.validate_backlog(current.replace(
            "[init, doctor, recall, context, propose, review, sync, upgrade]",
            "[init, doctor, recall, context, propose, review, sync, upgrade, export]",
            1,
        ))
        self.assertFalse(result["passed"])
        self.assertTrue(any(error.startswith("complexity_budget.public_cli_verbs") for error in result["errors"]), result["errors"])

    def test_sixth_mcp_tool_fails_closed(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        result = self.validate_backlog(current.replace(
            "[capabilities, recall, context, propose, review]",
            "[capabilities, recall, context, propose, review, sync]",
            1,
        ))
        self.assertFalse(result["passed"])
        self.assertTrue(any(error.startswith("complexity_budget.mcp_tools") for error in result["errors"]), result["errors"])

    def test_third_scope_and_fourth_adapter_fail_closed(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        with_scope = self.validate_backlog(current.replace("[project_user, user_global]", "[project_user, user_global, enterprise]", 1))
        with_adapter = self.validate_backlog(current.replace("[codex, claude_code, generic_mcp_cli]", "[codex, claude_code, generic_mcp_cli, pi]", 1))
        self.assertFalse(with_scope["passed"])
        self.assertFalse(with_adapter["passed"])
        self.assertTrue(any(error.startswith("complexity_budget.scopes") for error in with_scope["errors"]), with_scope["errors"])
        self.assertTrue(any(error.startswith("complexity_budget.reference_adapters") for error in with_adapter["errors"]), with_adapter["errors"])

    def test_minimal_profile_over_budget_fails_closed(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        result = self.validate_backlog(current.replace("max_files: 15, max_directories: 8", "max_files: 16, max_directories: 9", 1))
        self.assertFalse(result["passed"])
        self.assertIn("complexity_budget.minimal_profile must be max_files=15 and max_directories=8", result["errors"])

    def test_parked_ticket_cannot_become_gate_member(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        result = self.validate_backlog(current.replace("G-V1M-PLAN: [V1M-01]", "G-V1M-PLAN: [V1M-01, OW-081-04]", 1))
        self.assertFalse(result["passed"])
        self.assertIn("G-V1M-PLAN: unknown active ticket OW-081-04", result["errors"])

    def test_v1m11_must_remain_authorization_stop(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        result = self.validate_backlog(current.replace("policy: user_authorization_stop", "policy: sequential", 1))
        self.assertFalse(result["passed"])
        self.assertIn("BACKLOG.yaml: V1M-11 must be the final user_authorization_stop wave", result["errors"])

    def test_clean_surface_gate_stop_requires_done_members_and_exact_next_action(self) -> None:
        current = self.validator.read(self.validator.RUN_STATE)
        clean_stop = re.sub(r"^active_ticket: [^\n]+$", "active_ticket: null", current, count=1, flags=re.MULTILINE)
        clean_stop = re.sub(r"^current_phase: [^\n]+$", "current_phase: V1M-GATE-SURFACE", clean_stop, count=1, flags=re.MULTILINE)
        clean_stop = re.sub(
            r'^  next_exact_action: ".*"$',
            '  next_exact_action: "Select V1M-04 after the completed G-V1M-SURFACE gate."',
            clean_stop,
            count=1,
            flags=re.MULTILINE,
        )
        self.assertIn("active_ticket: null", clean_stop)
        self.assertIn("last_green_gate: G-V1M-SURFACE", clean_stop)
        self.assertIn("Select V1M-04", clean_stop)
        result = self.validate_run_state(clean_stop)
        self.assertTrue(result["passed"], result["errors"])
        invalid = self.validate_run_state(clean_stop.replace("Select V1M-04", "Select V1M-05", 1))
        self.assertFalse(invalid["passed"])
        self.assertIn("RUN-STATE.yaml: active_ticket must be active V1M ticket, got null", invalid["errors"])
        stale_gate = self.validate_run_state(clean_stop.replace("last_green_gate: G-V1M-SURFACE", "last_green_gate: G-V1M-PLAN", 1))
        self.assertFalse(stale_gate["passed"])
        self.assertIn("RUN-STATE.yaml: last_green_gate must be latest completed gate G-V1M-SURFACE, got G-V1M-PLAN", stale_gate["errors"])


if __name__ == "__main__":
    unittest.main()
