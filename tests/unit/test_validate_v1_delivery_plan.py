from __future__ import annotations

import importlib.util
import pathlib
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "tools" / "validate_v1_delivery_plan.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_v1_delivery_plan", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateV1DeliveryPlanTests(unittest.TestCase):

    def test_post_v1_ticket_is_not_required_in_active_gate_or_wave(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        self.assertIn("id: OW-081-04, release: v0.8.1, phase: post-v1, status: post_v1", current)
        self.assertNotIn("OW-081-04]", current.split("G-081-A-ADAPTERS:", 1)[1].splitlines()[0])
        result = self.validate_backlog(current)
        self.assertTrue(result["passed"], result["errors"])

    def test_post_v1_ticket_in_active_gate_fails_closed(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        mutated = current.replace(
            "G-081-A-ADAPTERS: [OW-081-01, OW-081-02, OW-081-03, OW-081-05]",
            "G-081-A-ADAPTERS: [OW-081-01, OW-081-02, OW-081-03, OW-081-04, OW-081-05]",
            1,
        )
        result = self.validate_backlog(mutated)
        self.assertIn("OW-081-04: post_v1 ticket cannot belong to an active gate", result["errors"])

    def test_active_ticket_dependency_on_post_v1_fails_closed(self) -> None:
        current = self.validator.read(self.validator.BACKLOG)
        mutated = current.replace(
            "depends_on: [OW-081-01], gate: G-081-A-ADAPTERS, path: \"tickets/ALL-TICKETS.md#ow-081-02\"",
            "depends_on: [OW-081-01, OW-081-04], gate: G-081-A-ADAPTERS, path: \"tickets/ALL-TICKETS.md#ow-081-02\"",
            1,
        )
        result = self.validate_backlog(mutated)
        self.assertIn("OW-081-02: active ticket depends on post_v1 ['OW-081-04']", result["errors"])
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_validator()

    def test_current_control_plane_is_valid(self) -> None:
        result = self.validator.validate()
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(result["warnings"], [])

    def validate_backlog(self, backlog_text: str):
        original_path = self.validator.BACKLOG
        with tempfile.TemporaryDirectory() as temp_dir:
            temporary_backlog = pathlib.Path(temp_dir) / "BACKLOG.yaml"
            temporary_backlog.write_text(backlog_text, encoding="utf-8")
            self.validator.BACKLOG = temporary_backlog
            try:
                return self.validator.validate()
            finally:
                self.validator.BACKLOG = original_path

    def replace_wave_tickets(
        self,
        backlog_text: str,
        wave_id: str,
        tickets: list[str],
    ) -> str:
        replacement_count = 0

        def replace(match):
            nonlocal replacement_count
            replacement_count += 1
            return f"{match.group(1)}[{', '.join(tickets)}]{match.group(2)}"

        updated = self.validator.re.sub(
            rf"(^  - \{{id: {self.validator.re.escape(wave_id)}, release: [^,]+, tickets: )"
            rf"\[[^\]]*\](, policy: [^,}}]+\}}$)",
            replace,
            backlog_text,
            count=1,
            flags=self.validator.re.MULTILINE,
        )
        self.assertEqual(replacement_count, 1, f"wave not found: {wave_id}")
        return updated

    def swap_wave_lines(
        self,
        backlog_text: str,
        first_wave_id: str,
        second_wave_id: str,
    ) -> str:
        pattern = self.validator.re.compile(
            rf"^  - \{{id: (?:{self.validator.re.escape(first_wave_id)}|"
            rf"{self.validator.re.escape(second_wave_id)}),[^\r\n]+$",
            self.validator.re.MULTILINE,
        )
        matches = list(pattern.finditer(backlog_text))
        self.assertEqual(len(matches), 2)
        first, second = sorted(matches, key=lambda item: item.start())
        return (
            backlog_text[: first.start()]
            + second.group(0)
            + backlog_text[first.end() : second.start()]
            + first.group(0)
            + backlog_text[second.end() :]
        )

    def test_dependency_cannot_share_a_parallel_wave_with_dependent(self) -> None:
        current = self.validator.BACKLOG.read_text(encoding="utf-8")
        rows = self.validator.parse_ticket_rows(current)
        waves = self.validator.parse_execution_waves(current)
        locations = {
            ticket_id: (index, wave)
            for index, wave in enumerate(waves)
            for ticket_id in wave["tickets"]
        }
        candidate = next(
            (
                (row["id"], dependency, locations[row["id"]], locations[dependency])
                for row in rows
                for dependency in row["depends_on"]
                if row["id"] in locations
                and dependency in locations
                and locations[row["id"]][1]["policy"] == "parallel_non_overlapping"
                and locations[dependency][0] < locations[row["id"]][0]
                and locations[dependency][1]["release"] == locations[row["id"]][1]["release"]
            ),
            None,
        )
        self.assertIsNotNone(candidate, "no eligible parallel-wave dependency edge")
        dependent_id, dependency_id, (_, dependent_wave), (_, dependency_wave) = candidate

        mutated = self.replace_wave_tickets(
            current,
            dependency_wave["id"],
            [item for item in dependency_wave["tickets"] if item != dependency_id],
        )
        mutated = self.replace_wave_tickets(
            mutated,
            dependent_wave["id"],
            [*dependent_wave["tickets"], dependency_id],
        )
        result = self.validate_backlog(mutated)

        self.assertFalse(result["passed"])
        self.assertIn(
            f"{dependent_id}: dependency {dependency_id} cannot share parallel wave "
            f"{dependent_wave['id']}; dependencies must be in an earlier wave",
            result["errors"],
        )

    def test_dependency_cannot_be_scheduled_after_dependent(self) -> None:
        current = self.validator.BACKLOG.read_text(encoding="utf-8")
        rows = self.validator.parse_ticket_rows(current)
        waves = self.validator.parse_execution_waves(current)
        locations = {
            ticket_id: (index, wave)
            for index, wave in enumerate(waves)
            for ticket_id in wave["tickets"]
        }
        candidate = next(
            (
                (row["id"], dependency, locations[row["id"]], locations[dependency])
                for row in rows
                for dependency in row["depends_on"]
                if row["id"] in locations
                and dependency in locations
                and locations[dependency][0] < locations[row["id"]][0]
                and locations[dependency][1]["release"] == locations[row["id"]][1]["release"]
            ),
            None,
        )
        self.assertIsNotNone(candidate, "no eligible dependency edge")
        dependent_id, dependency_id, (_, dependent_wave), (_, dependency_wave) = candidate

        mutated = self.replace_wave_tickets(
            current,
            dependency_wave["id"],
            [
                dependent_id if item == dependency_id else item
                for item in dependency_wave["tickets"]
            ],
        )
        mutated = self.replace_wave_tickets(
            mutated,
            dependent_wave["id"],
            [
                dependency_id if item == dependent_id else item
                for item in dependent_wave["tickets"]
            ],
        )
        result = self.validate_backlog(mutated)

        self.assertFalse(result["passed"])
        self.assertIn(
            f"{dependent_id}: dependency {dependency_id} is scheduled in later wave "
            f"{dependent_wave['id']}; it must precede {dependency_wave['id']}",
            result["errors"],
        )

    def test_execution_waves_must_follow_release_order(self) -> None:
        current = self.validator.BACKLOG.read_text(encoding="utf-8")
        waves = self.validator.parse_execution_waves(current)
        first_later_release_wave = next(
            wave
            for wave in waves
            if wave["release"] != waves[0]["release"]
        )
        mutated = self.swap_wave_lines(
            current,
            waves[0]["id"],
            first_later_release_wave["id"],
        )
        result = self.validate_backlog(mutated)

        self.assertFalse(result["passed"])
        self.assertTrue(
            any(
                error.endswith("execution waves must follow release_order")
                for error in result["errors"]
            ),
            result["errors"],
        )

    def test_alignment_stop_must_be_final_wave_for_release(self) -> None:
        current = self.validator.BACKLOG.read_text(encoding="utf-8")
        waves = self.validator.parse_execution_waves(current)
        alignment_wave = next(
            wave
            for wave in waves
            if wave["policy"] == "user_alignment_stop"
        )
        prior_same_release_wave = [
            wave
            for wave in waves
            if wave["release"] == alignment_wave["release"]
            and wave["id"] != alignment_wave["id"]
        ][-1]
        mutated = self.swap_wave_lines(
            current,
            prior_same_release_wave["id"],
            alignment_wave["id"],
        )
        result = self.validate_backlog(mutated)

        self.assertFalse(result["passed"])
        self.assertTrue(
            any(
                error.startswith(
                    f"{alignment_wave['id']}: alignment stop must be the final wave"
                )
                for error in result["errors"]
            ),
            result["errors"],
        )

    def test_merged_orchestration_workspace_key_is_rejected(self) -> None:
        original_path = self.validator.RUN_STATE
        current = original_path.read_text(encoding="utf-8")
        malformed = current.replace(
            "workspace:\n",
            "nullworkspace:\n",
            1,
        )
        self.assertNotEqual(current, malformed)

        with tempfile.TemporaryDirectory() as temp_dir:
            temporary_run_state = pathlib.Path(temp_dir) / "RUN-STATE.yaml"
            temporary_run_state.write_text(malformed, encoding="utf-8")
            self.validator.RUN_STATE = temporary_run_state
            try:
                result = self.validator.validate()
            finally:
                self.validator.RUN_STATE = original_path

        self.assertFalse(result["passed"])
        self.assertIn(
            "RUN-STATE.yaml: malformed merged orchestration/workspace key",
            result["errors"],
        )
        self.assertIn(
            "RUN-STATE.yaml: missing top-level key workspace",
            result["errors"],
        )


if __name__ == "__main__":
    unittest.main()
