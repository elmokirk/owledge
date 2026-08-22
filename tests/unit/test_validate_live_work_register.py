from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "tools" / "validate_live_work_register.py"
REGISTER_PATH = (
    REPO_ROOT
    / "internal"
    / "owledge"
    / "workpackages"
    / "owledge-v1-autonomous-delivery"
    / "LIVE-WORK-REGISTER.yaml"
)
STALE_FIXTURE = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "live-work-register"
    / "stale-register-mutations.json"
)


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_live_work_register", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateLiveWorkRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_validator()
        cls.valid_register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))

    def validate_payload(
        self,
        payload,
        *,
        text_overrides=None,
        project_root=REPO_ROOT,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir) / "LIVE-WORK-REGISTER.yaml"
            path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return self.validator.validate_register(
                project_root,
                path,
                text_overrides=text_overrides,
            )

    def validate_cli_payload(self, payload):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir) / "LIVE-WORK-REGISTER.yaml"
            path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    str(VALIDATOR_PATH),
                    "--project-root",
                    str(REPO_ROOT),
                    "--register",
                    str(path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            return completed, json.loads(completed.stdout)

    def item(self, payload, item_id):
        return next(item for item in payload["items"] if item["id"] == item_id)

    def assert_has_error(self, result, fragment):
        self.assertFalse(result["passed"])
        self.assertTrue(
            any(fragment in error for error in result["errors"]),
            f"missing {fragment!r} in {result['errors']}",
        )

    def test_current_register_is_valid_and_finite(self) -> None:
        result = self.validate_payload(copy.deepcopy(self.valid_register))
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(result["counts"]["items"], 21)
        self.assertEqual(
            result["counts"]["states"],
            {"shipped": 8, "open": 1, "superseded": 11, "deferred": 1},
        )

    def test_missing_duplicate_and_extra_feedback_ids_fail(self) -> None:
        cases = {}

        missing = copy.deepcopy(self.valid_register)
        missing["items"] = [
            item for item in missing["items"] if item["id"] != "FB-021"
        ]
        cases["missing"] = (missing, "items: missing feedback ids ['FB-021']")

        duplicate = copy.deepcopy(self.valid_register)
        duplicate["items"].append(copy.deepcopy(duplicate["items"][0]))
        cases["duplicate"] = (duplicate, "items: duplicate feedback id FB-001")

        extra = copy.deepcopy(self.valid_register)
        extra_item = copy.deepcopy(extra["items"][0])
        extra_item["id"] = "FB-022"
        extra["items"].append(extra_item)
        cases["extra"] = (extra, "items: extra feedback ids ['FB-022']")

        for name, (payload, diagnostic) in cases.items():
            with self.subTest(name=name):
                self.assert_has_error(self.validate_payload(payload), diagnostic)

    def test_invalid_state_and_state_case_fail(self) -> None:
        for state in ("active", "Open", "SHIPPED", {}):
            payload = copy.deepcopy(self.valid_register)
            self.item(payload, "FB-003")["state"] = state
            with self.subTest(state=state):
                self.assert_has_error(
                    self.validate_payload(payload),
                    f"FB-003.state: invalid state {state!r}",
                )

    def test_malformed_container_types_fail_closed_without_traceback(self) -> None:
        cases = (
            (
                "allowed_states",
                lambda payload: payload.__setitem__("allowed_states", 1),
                "allowed_states: expected a list",
            ),
            (
                "source_documents",
                lambda payload: payload.__setitem__("source_documents", [{}]),
                "source_documents[0]: expected a string",
            ),
            (
                "live_status_sources",
                lambda payload: payload["authority"].__setitem__(
                    "live_status_sources", 1
                ),
                "authority.live_status_sources: expected a list",
            ),
            (
                "historical_sources",
                lambda payload: payload["authority"].__setitem__(
                    "historical_sources", 1
                ),
                "authority.historical_sources: expected a list",
            ),
        )
        for name, mutate, diagnostic in cases:
            payload = copy.deepcopy(self.valid_register)
            mutate(payload)
            with self.subTest(name=name):
                completed, result = self.validate_cli_payload(payload)
                self.assertEqual(completed.returncode, 1, completed.stdout)
                self.assertNotIn("Traceback", completed.stderr)
                self.assert_has_error(result, diagnostic)
                self.assertEqual(result["errors"], sorted(result["errors"]))

    def test_feedback_items_require_numeric_order(self) -> None:
        payload = copy.deepcopy(self.valid_register)
        payload["items"][1], payload["items"][9] = (
            payload["items"][9],
            payload["items"][1],
        )
        self.assert_has_error(
            self.validate_payload(payload),
            "items: feedback ids must be in numeric order FB-001..FB-021",
        )

    def test_shipped_item_requires_existing_evidence(self) -> None:
        payload = copy.deepcopy(self.valid_register)
        self.item(payload, "FB-001")["shipped_evidence"] = []
        result = self.validate_payload(payload)
        self.assert_has_error(
            result,
            "FB-001.shipped_evidence: shipped state requires existing evidence",
        )

    def test_open_item_requires_resolvable_ticket_not_historical_checkbox(self) -> None:
        payload = copy.deepcopy(self.valid_register)
        self.item(payload, "FB-004")["work_reference"] = "ticket:OW-999-99"
        self.assert_has_error(
            self.validate_payload(payload),
            "FB-004.work_reference: open state requires a resolvable ticket",
        )

    def test_missing_evidence_path_fails(self) -> None:
        payload = copy.deepcopy(self.valid_register)
        missing_path = "internal/owledge/workpackages/missing-proof.md"
        payload["source_documents"].append(missing_path)
        self.item(payload, "FB-001")["shipped_evidence"] = [missing_path]
        approved = (*self.validator.APPROVED_SOURCES, missing_path)
        with mock.patch.object(self.validator, "APPROVED_SOURCES", approved):
            result = self.validate_payload(payload)
        self.assert_has_error(
            result,
            f"FB-001.shipped_evidence[0]: source path does not exist: {missing_path}",
        )

    def test_supersession_self_reference_and_cycle_fail(self) -> None:
        self_reference = copy.deepcopy(self.valid_register)
        self.item(self_reference, "FB-005")[
            "replacement_reference"
        ] = "feedback:FB-005"
        self.assert_has_error(
            self.validate_payload(self_reference),
            "FB-005.replacement_reference: self-reference is forbidden",
        )

        cycle = copy.deepcopy(self.valid_register)
        self.item(cycle, "FB-005")["replacement_reference"] = "feedback:FB-006"
        self.item(cycle, "FB-006")["replacement_reference"] = "feedback:FB-005"
        self.assert_has_error(
            self.validate_payload(cycle),
            "replacement_reference: supersession cycle",
        )

    def test_deferred_item_requires_later_target_and_reason(self) -> None:
        payload = copy.deepcopy(self.valid_register)
        deferred = self.item(payload, "FB-011")
        deferred["target_release"] = "v0.7.1"
        deferred["deferred_reason"] = None
        result = self.validate_payload(payload)
        self.assert_has_error(
            result, "FB-011.deferred_reason: deferred state requires a reason"
        )
        self.assert_has_error(
            result, "FB-011.target_release: deferred target must be later than v0.8.0"
        )

    def test_unsafe_absolute_unapproved_and_missing_paths_fail(self) -> None:
        cases = (
            ("../CHANGELOG.md", "unsafe or non-normalized repository path"),
            ("Z:/outside/proof.md", "unsafe or non-normalized repository path"),
            ("/tmp/proof.md", "unsafe or non-normalized repository path"),
            ("README.md", "unapproved source path README.md"),
        )
        for value, diagnostic in cases:
            payload = copy.deepcopy(self.valid_register)
            self.item(payload, "FB-003")["evidence_links"] = [value]
            with self.subTest(value=value):
                self.assert_has_error(
                    self.validate_payload(payload),
                    diagnostic,
                )

    def test_version_mismatch_fails(self) -> None:
        payload = copy.deepcopy(self.valid_register)
        payload["current_product_version"] = "0.6.9"
        self.assert_has_error(
            self.validate_payload(payload),
            "version_truth: current_product_version, VERSION, and pyproject.toml disagree",
        )

    def test_historical_checkbox_cannot_reactivate_work(self) -> None:
        source = (
            REPO_ROOT / "docs" / "feedback-round-2026-06.md"
        ).read_text(encoding="utf-8")
        stale = source.replace("Status: historical", "Status: active", 1)
        stale += "\n- [ ] reactivate historical ticket\n"
        result = self.validate_payload(
            copy.deepcopy(self.valid_register),
            text_overrides={"docs/feedback-round-2026-06.md": stale},
        )
        self.assert_has_error(
            result,
            "historical_source: docs/feedback-round-2026-06.md reactivates historical work",
        )

    def test_duplicate_outstanding_artifact_cut_fails(self) -> None:
        source = (REPO_ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        stale = source + (
            "\n| P0 | Final release artifact cut | Run build and publish later. |\n"
        )
        result = self.validate_payload(
            copy.deepcopy(self.valid_register),
            text_overrides={"ROADMAP.md": stale},
        )
        self.assert_has_error(
            result,
            "active_source: ROADMAP.md retains a duplicate outstanding artifact cut",
        )

    def test_cli_simplification_wrong_release_fails(self) -> None:
        source = (REPO_ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        post_row = next(
            line for line in source.splitlines() if "| POST-002 / OW-100-05 |" in line
        )
        stale = source.replace(post_row, post_row.replace("| v1.0 |", "| v0.7.1 |"))
        result = self.validate_payload(
            copy.deepcopy(self.valid_register),
            text_overrides={"ROADMAP.md": stale},
        )
        self.assert_has_error(
            result,
            "active_source: ROADMAP.md POST-002 must map to OW-100-05 at v1.0",
        )

    def test_future_status_reset_wording_fails(self) -> None:
        path = REPO_ROOT / "docs" / "strategic-roadmap-2026-2027.md"
        source = path.read_text(encoding="utf-8")
        stale = source.replace(
            "truth reset is complete",
            "truth reset remains future",
            1,
        )
        stale += "\nThe next reset should consolidate these sources.\n"
        result = self.validate_payload(
            copy.deepcopy(self.valid_register),
            text_overrides={
                "docs/strategic-roadmap-2026-2027.md": stale,
            },
        )
        self.assert_has_error(
            result,
            "active_source: strategic roadmap must record the truth reset as complete",
        )
        self.assert_has_error(
            result,
            "active_source: strategic roadmap retains future reset wording "
            "'the next reset should consolidate'",
        )

    def test_stale_fixture_fails_with_expected_diagnostics(self) -> None:
        fixture = json.loads(STALE_FIXTURE.read_text(encoding="utf-8"))
        payload = copy.deepcopy(self.valid_register)
        for mutation in fixture["mutations"]:
            if "top_level_field" in mutation:
                payload[mutation["top_level_field"]] = mutation["value"]
            else:
                self.item(payload, mutation["item_id"])[mutation["field"]] = mutation[
                    "value"
                ]
        result = self.validate_payload(payload)
        for expected in fixture["expected_diagnostics"]:
            self.assert_has_error(result, expected)

    def test_diagnostics_are_sorted_and_deterministic(self) -> None:
        payload = copy.deepcopy(self.valid_register)
        payload["current_product_version"] = "0.0.1"
        self.item(payload, "FB-003")["state"] = "OPEN"
        self.item(payload, "FB-003")["evidence_links"] = ["../escape.md"]
        first = self.validate_payload(payload)
        second = self.validate_payload(payload)
        self.assertEqual(first["errors"], sorted(first["errors"]))
        self.assertEqual(first["errors"], second["errors"])


if __name__ == "__main__":
    unittest.main()
