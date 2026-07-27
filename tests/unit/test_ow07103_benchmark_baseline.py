from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import shutil
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "tools"
COMPARE_PATH = (
    REPO_ROOT
    / "addons"
    / "benchmark-kit"
    / "tools"
    / "compare-benchmark-runs.py"
)


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASELINE = load_module(
    "ow07103_validate_benchmark_baseline",
    TOOLS_DIR / "validate_benchmark_baseline.py",
)
COMPARER = load_module("ow07103_compare_benchmark_runs", COMPARE_PATH)


class FrozenBaselineTests(unittest.TestCase):
    def test_current_baseline_passes_with_separate_metrics(self) -> None:
        result = BASELINE.validate_benchmark_baseline(REPO_ROOT)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(
            result["reference_profiles"],
            ["metadata_scan", "owledge_context_pack", "oracle"],
        )
        self.assertGreaterEqual(
            result["metrics"]["min_avg_answer_correctness"],
            0.95,
        )
        self.assertGreaterEqual(
            result["metrics"]["min_avg_precision_at_k"],
            0.90,
        )
        self.assertGreaterEqual(
            result["metrics"]["avg_token_reduction_percent"],
            80.0,
        )

    def test_exact_threshold_boundary_passes(self) -> None:
        metrics = {
            "min_avg_answer_correctness": 0.95,
            "min_avg_precision_at_k": 0.9,
            "min_avg_recall_at_k": 1.0,
            "min_avg_citation_accuracy": 1.0,
            "max_avg_irrelevant_token_ratio": 0.1,
            "privacy_failures": 0,
            "staleness_failures": 0,
            "avg_token_reduction_percent": 80.0,
        }
        self.assertEqual(BASELINE.evaluate_metrics(metrics), [])

    def test_79_99_token_reduction_fails(self) -> None:
        metrics = self.passing_metrics()
        metrics["avg_token_reduction_percent"] = 79.99
        self.assertIn(
            "token-efficiency",
            self.error_codes(BASELINE.evaluate_metrics(metrics)),
        )

    def test_privacy_staleness_quality_and_pollution_fail_independently(self) -> None:
        cases = [
            ("privacy_failures", 1, "privacy"),
            ("staleness_failures", 1, "staleness"),
            ("min_avg_answer_correctness", 0.9499, "answer-quality"),
            (
                "max_avg_irrelevant_token_ratio",
                0.1001,
                "context-pollution",
            ),
        ]
        for field, value, expected_code in cases:
            with self.subTest(field=field):
                metrics = self.passing_metrics()
                metrics[field] = value
                self.assertIn(
                    expected_code,
                    self.error_codes(BASELINE.evaluate_metrics(metrics)),
                )

    def test_threshold_change_requires_new_baseline_version(self) -> None:
        contract = json.loads(
            (REPO_ROOT / BASELINE.CONTRACT_PATH).read_text(encoding="utf-8")
        )
        contract["thresholds"]["min_avg_token_reduction_percent"] = 79.99
        with tempfile.TemporaryDirectory() as temp_dir:
            changed = pathlib.Path(temp_dir) / "contract.json"
            changed.write_text(json.dumps(contract), encoding="utf-8")
            result = BASELINE.validate_benchmark_baseline(
                REPO_ROOT,
                contract_path=changed,
            )
        self.assertFalse(result["passed"])
        self.assertIn("threshold-version", self.error_codes(result["errors"]))

    def test_fixture_hash_change_fails_closed(self) -> None:
        contract = json.loads(
            (REPO_ROOT / BASELINE.CONTRACT_PATH).read_text(encoding="utf-8")
        )
        first = next(iter(contract["fixture"]["artifacts"]))
        contract["fixture"]["artifacts"][first] = "0" * 64
        with tempfile.TemporaryDirectory() as temp_dir:
            changed = pathlib.Path(temp_dir) / "contract.json"
            changed.write_text(json.dumps(contract), encoding="utf-8")
            result = BASELINE.validate_benchmark_baseline(
                REPO_ROOT,
                contract_path=changed,
            )
        self.assertFalse(result["passed"])
        self.assertIn("artifact-version", self.error_codes(result["errors"]))

    def test_reference_and_exclusion_inventory_are_frozen(self) -> None:
        original = json.loads(
            (REPO_ROOT / BASELINE.CONTRACT_PATH).read_text(encoding="utf-8")
        )
        mutations = [
            (
                "reference-contract",
                lambda payload: payload["reference_reports"].pop(
                    "benchmarks/v0.7.0/results/glm-5-1-cloud/latest.json"
                ),
            ),
            (
                "excluded-contract",
                lambda payload: payload.update({"excluded_reports": {}}),
            ),
        ]
        for expected, mutate in mutations:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temp_dir:
                changed_payload = copy.deepcopy(original)
                mutate(changed_payload)
                changed = pathlib.Path(temp_dir) / "contract.json"
                changed.write_text(json.dumps(changed_payload), encoding="utf-8")
                result = BASELINE.validate_benchmark_baseline(
                    REPO_ROOT,
                    contract_path=changed,
                )
                self.assertFalse(result["passed"])
                self.assertIn(expected, self.error_codes(result["errors"]))

    def test_held_out_journeys_match_expected_verdicts(self) -> None:
        payload = json.loads(
            (
                REPO_ROOT
                / "benchmarks"
                / "v0.7.0"
                / "held-out-journeys-v1.json"
            ).read_text(encoding="utf-8")
        )
        self.assertGreaterEqual(len(payload["journeys"]), 6)
        for journey in payload["journeys"]:
            with self.subTest(journey=journey["id"]):
                actual = not BASELINE.evaluate_metrics(journey["metrics"])
                self.assertEqual(actual, journey["expected_pass"])

    def test_incomplete_qwen_report_is_rejected_by_comparer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            complete = root / "complete.json"
            incomplete = root / "incomplete.json"
            shutil.copyfile(
                REPO_ROOT
                / "benchmarks"
                / "v0.7.0"
                / "results"
                / "gemma4-latest"
                / "latest.json",
                complete,
            )
            shutil.copyfile(
                REPO_ROOT
                / "benchmarks"
                / "v0.7.0"
                / "results"
                / "qwen3-5-4b"
                / "latest.json",
                incomplete,
            )
            result = COMPARER.compare(
                root,
                ["complete.json", "incomplete.json"],
                "comparison",
            )
        self.assertFalse(result["passed"])
        self.assertIn("incomplete.json", result["incomplete_inputs"])

    def test_report_matrix_rejects_missing_profile_scenario(self) -> None:
        report = json.loads(
            (
                REPO_ROOT
                / "benchmarks"
                / "v0.7.0"
                / "results"
                / "gemma4-latest"
                / "latest.json"
            ).read_text(encoding="utf-8")
        )
        report["records"] = copy.deepcopy(report["records"][:-1])
        _, errors = BASELINE._report_metrics(report, "mutated-report")
        self.assertIn("record-matrix", self.error_codes(errors))

    def test_generated_comparison_artifacts_use_portable_lf(self) -> None:
        comparison = (
            REPO_ROOT / "benchmarks" / "v0.7.0" / "results" / "comparison"
        )
        for name in ("latest.json", "latest.md", "index.html", "charts.svg"):
            with self.subTest(name=name):
                self.assertNotIn(b"\r\n", (comparison / name).read_bytes())

    @staticmethod
    def passing_metrics() -> dict[str, float | int]:
        return {
            "min_avg_answer_correctness": 0.95,
            "min_avg_precision_at_k": 0.9,
            "min_avg_recall_at_k": 1.0,
            "min_avg_citation_accuracy": 1.0,
            "max_avg_irrelevant_token_ratio": 0.1,
            "privacy_failures": 0,
            "staleness_failures": 0,
            "avg_token_reduction_percent": 80.0,
        }

    @staticmethod
    def error_codes(errors) -> list[str]:
        return [item["code"] for item in errors]


if __name__ == "__main__":
    unittest.main()
