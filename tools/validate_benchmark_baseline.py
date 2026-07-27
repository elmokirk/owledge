#!/usr/bin/env python3
"""Validate the frozen, fixture-bounded Owledge benchmark baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = "benchmarks/v0.7.0/baseline-contract-v1.json"
PROFILES = ("metadata_scan", "owledge_context_pack", "oracle")
SCENARIOS = (
    "needle",
    "multi-hop",
    "stale-conflict",
    "privacy-trap",
    "distractor-heavy",
    "handoff-resume",
)
THRESHOLDS = {
    "min_avg_answer_correctness": 0.95,
    "min_avg_precision_at_k": 0.9,
    "min_avg_recall_at_k": 1.0,
    "min_avg_citation_accuracy": 1.0,
    "max_avg_irrelevant_token_ratio": 0.1,
    "max_privacy_failures": 0,
    "max_staleness_failures": 0,
    "min_avg_token_reduction_percent": 80.0,
}
FROZEN_HASHES = {
    "addons/benchmark-kit/fixtures/small.zip": "41bac27b61cd2907048b3822546777fcee1cfa56399e797a2acb77782d018af9",
    "benchmarks/v0.7.0/fixtures/small/fixture-manifest.json": "080095f8a46db0c063a8ca623b22facc289c0527354e638281bea1c576261b2f",
    "benchmarks/v0.7.0/fixtures/small/oracle.json": "95b9441472fc66ce062040cc53cadcca6b52ef1ef743a7789a0e7829363874e7",
    "benchmarks/v0.7.0/fixtures/small/queries.json": "ac731efe65295c7b906412095f51b332a4c0b6633b62605136f73a709ef07a4d",
    "benchmarks/v0.7.0/results/gemma4-latest/latest.json": "3aca9170f21fdc0a146af77d3f992864be69e70f050d45c3c3f9a038152f9c8d",
    "benchmarks/v0.7.0/results/glm-5-1-cloud/latest.json": "d70501287556ea3d10c968931f147f70a665dd9e00893f9ff3a54554163894a4",
    "benchmarks/v0.7.0/results/comparison/latest.json": "cc3875a732e8a1a594ca9b532338255664d3d8a70f7df3e24f3025c2477b97bb",
    "benchmarks/v0.7.0/held-out-journeys-v1.json": "52f973d4048c071e8c8e7dced084a4cc23cd5fd05beec5f03b0fe5f5988b6276",
}
REFERENCE_REPORTS = (
    "benchmarks/v0.7.0/results/gemma4-latest/latest.json",
    "benchmarks/v0.7.0/results/glm-5-1-cloud/latest.json",
)
EXCLUDED_REPORT = "benchmarks/v0.7.0/results/qwen3-5-4b/latest.json"


def _error(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def evaluate_metrics(
    metrics: dict[str, Any],
    thresholds: dict[str, Any] = THRESHOLDS,
) -> list[dict[str, str]]:
    """Return stable release-threshold failures for already separated metrics."""

    checks = (
        (
            "answer-quality",
            float(metrics.get("min_avg_answer_correctness", 0))
            >= float(thresholds["min_avg_answer_correctness"]),
        ),
        (
            "retrieval-precision",
            float(metrics.get("min_avg_precision_at_k", 0))
            >= float(thresholds["min_avg_precision_at_k"]),
        ),
        (
            "retrieval-recall",
            float(metrics.get("min_avg_recall_at_k", 0))
            >= float(thresholds["min_avg_recall_at_k"]),
        ),
        (
            "citation-accuracy",
            float(metrics.get("min_avg_citation_accuracy", 0))
            >= float(thresholds["min_avg_citation_accuracy"]),
        ),
        (
            "context-pollution",
            float(metrics.get("max_avg_irrelevant_token_ratio", 1))
            <= float(thresholds["max_avg_irrelevant_token_ratio"]),
        ),
        (
            "privacy",
            int(metrics.get("privacy_failures", 1))
            <= int(thresholds["max_privacy_failures"]),
        ),
        (
            "staleness",
            int(metrics.get("staleness_failures", 1))
            <= int(thresholds["max_staleness_failures"]),
        ),
        (
            "token-efficiency",
            float(metrics.get("avg_token_reduction_percent", 0))
            >= float(thresholds["min_avg_token_reduction_percent"]),
        ),
    )
    return [
        _error(code, f"{code} threshold failed")
        for code, passed in checks
        if not passed
    ]


def _read_json(path: pathlib.Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("top-level JSON must be an object")
    return payload


def _report_metrics(
    report: dict[str, Any],
    report_name: str,
) -> tuple[dict[str, float | int], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    if report.get("passed") is not True or report.get("errors"):
        errors.append(
            _error("incomplete-report", f"{report_name} is not a completed run")
        )
    profile_totals = report.get("profile_totals")
    if not isinstance(profile_totals, dict) or set(profile_totals) != set(PROFILES):
        errors.append(
            _error("profile-contract", f"{report_name} must contain three profiles")
        )
        return {}, errors
    records = report.get("records")
    if not isinstance(records, list):
        errors.append(_error("record-contract", f"{report_name} records missing"))
        return {}, errors
    matrix = [
        (str(row.get("profile") or ""), str(row.get("scenario") or ""))
        for row in records
        if isinstance(row, dict)
    ]
    expected_matrix = [(profile, scenario) for scenario in SCENARIOS for profile in PROFILES]
    if sorted(matrix) != sorted(expected_matrix):
        errors.append(
            _error(
                "record-matrix",
                f"{report_name} must contain each profile/scenario exactly once",
            )
        )
    owledge = [
        row
        for row in records
        if isinstance(row, dict) and row.get("profile") == "owledge_context_pack"
    ]
    baseline_totals = profile_totals["metadata_scan"]
    owledge_totals = profile_totals["owledge_context_pack"]
    before = float(baseline_totals.get("tokens_per_correct_answer") or 0)
    after = float(owledge_totals.get("tokens_per_correct_answer") or 0)
    reduction = ((before - after) / before) * 100 if before > 0 else 0.0
    metrics: dict[str, float | int] = {
        "avg_answer_correctness": _mean(
            [float(row.get("answer_correctness") or 0) for row in owledge]
        ),
        "avg_precision_at_k": _mean(
            [float(row.get("precision_at_k") or 0) for row in owledge]
        ),
        "avg_recall_at_k": _mean(
            [float(row.get("recall_at_k") or 0) for row in owledge]
        ),
        "avg_citation_accuracy": _mean(
            [float(row.get("citation_accuracy") or 0) for row in owledge]
        ),
        "avg_irrelevant_token_ratio": float(
            owledge_totals.get("avg_irrelevant_token_ratio") or 0
        ),
        "privacy_failures": int(owledge_totals.get("privacy_failures") or 0),
        "staleness_failures": int(
            owledge_totals.get("staleness_failures") or 0
        ),
        "token_reduction_percent": reduction,
    }
    return metrics, errors


def validate_benchmark_baseline(
    project_root: pathlib.Path | str = REPO_ROOT,
    *,
    contract_path: pathlib.Path | str | None = None,
) -> dict[str, Any]:
    root = pathlib.Path(project_root).resolve()
    contract_file = (
        pathlib.Path(contract_path).resolve()
        if contract_path is not None
        else root / CONTRACT_PATH
    )
    errors: list[dict[str, str]] = []
    metrics: dict[str, Any] = {}
    try:
        contract = _read_json(contract_file)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "schema_version": 1,
            "passed": False,
            "baseline_version": "",
            "metrics": {},
            "errors": [_error("contract-read", str(exc))],
        }

    if contract.get("baseline_version") != "1.0.0":
        errors.append(
            _error("baseline-version", "expected frozen baseline_version 1.0.0")
        )
    if contract.get("claim_scope") != "synthetic-fixture-bounded":
        errors.append(
            _error("claim-scope", "baseline claim must remain fixture-bounded")
        )
    if contract.get("reference_profiles") != list(PROFILES):
        errors.append(_error("profile-contract", "reference profiles changed"))
    if contract.get("expected_scenarios") != list(SCENARIOS):
        errors.append(_error("scenario-contract", "scenario inventory changed"))
    if contract.get("thresholds") != THRESHOLDS:
        errors.append(
            _error(
                "threshold-version",
                "threshold changes require a new baseline_version and decision",
            )
        )

    contract_hashes: dict[str, str] = {}
    fixture = contract.get("fixture") or {}
    if {
        "name": fixture.get("name"),
        "scale_mode": fixture.get("scale_mode"),
        "file_count": fixture.get("file_count"),
        "seed": fixture.get("seed"),
    } != {
        "name": "owledge-v0.7.0-small-seed42",
        "scale_mode": "small",
        "file_count": 100,
        "seed": 42,
    }:
        errors.append(_error("fixture-contract", "fixture identity changed"))
    expected_reference_hashes = {
        path: FROZEN_HASHES[path] for path in REFERENCE_REPORTS
    }
    if contract.get("reference_reports") != expected_reference_hashes:
        errors.append(
            _error("reference-contract", "reference report inventory changed")
        )
    excluded_reports = contract.get("excluded_reports")
    if (
        not isinstance(excluded_reports, dict)
        or set(excluded_reports) != {EXCLUDED_REPORT}
        or not str(excluded_reports.get(EXCLUDED_REPORT) or "").strip()
    ):
        errors.append(
            _error("excluded-contract", "excluded report disposition changed")
        )
    contract_hashes.update(fixture.get("artifacts") or {})
    contract_hashes.update(contract.get("reference_reports") or {})
    comparison = contract.get("comparison") or {}
    held_out = contract.get("held_out") or {}
    if comparison.get("path"):
        contract_hashes[str(comparison["path"])] = str(comparison.get("sha256") or "")
    if held_out.get("path"):
        contract_hashes[str(held_out["path"])] = str(held_out.get("sha256") or "")
    if contract_hashes != FROZEN_HASHES:
        errors.append(
            _error(
                "artifact-version",
                "artifact inventory or hashes changed without a new baseline_version",
            )
        )
    for relative, expected_hash in FROZEN_HASHES.items():
        path = root / relative
        if not path.is_file():
            errors.append(_error("artifact-missing", relative))
        elif _sha256(path) != expected_hash:
            errors.append(_error("artifact-hash", relative))

    report_metrics: list[dict[str, float | int]] = []
    for relative in REFERENCE_REPORTS:
        try:
            report = _read_json(root / relative)
            current, report_errors = _report_metrics(report, relative)
            errors.extend(report_errors)
            if current:
                report_metrics.append(current)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(_error("report-read", f"{relative}: {exc}"))
    if report_metrics:
        metrics = {
            "min_avg_answer_correctness": min(
                float(item["avg_answer_correctness"]) for item in report_metrics
            ),
            "min_avg_precision_at_k": min(
                float(item["avg_precision_at_k"]) for item in report_metrics
            ),
            "min_avg_recall_at_k": min(
                float(item["avg_recall_at_k"]) for item in report_metrics
            ),
            "min_avg_citation_accuracy": min(
                float(item["avg_citation_accuracy"]) for item in report_metrics
            ),
            "max_avg_irrelevant_token_ratio": max(
                float(item["avg_irrelevant_token_ratio"])
                for item in report_metrics
            ),
            "privacy_failures": sum(
                int(item["privacy_failures"]) for item in report_metrics
            ),
            "staleness_failures": sum(
                int(item["staleness_failures"]) for item in report_metrics
            ),
            "avg_token_reduction_percent": round(
                _mean(
                    [
                        float(item["token_reduction_percent"])
                        for item in report_metrics
                    ]
                ),
                2,
            ),
        }
        errors.extend(evaluate_metrics(metrics))

    try:
        excluded = _read_json(root / EXCLUDED_REPORT)
        if excluded.get("passed") is not False or not excluded.get("errors"):
            errors.append(
                _error(
                    "excluded-report",
                    "excluded Qwen artifact no longer proves an incomplete run",
                )
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(_error("excluded-report", str(exc)))

    try:
        comparison_payload = _read_json(root / str(comparison.get("path") or ""))
        if comparison_payload.get("inputs") != list(REFERENCE_REPORTS):
            errors.append(
                _error(
                    "comparison-inputs",
                    "comparison must use exactly the complete reference reports",
                )
            )
        executive = comparison_payload.get("executive") or {}
        if (
            executive.get("models_compared") != len(REFERENCE_REPORTS)
            or executive.get("release_proof_status") != "pass"
        ):
            errors.append(
                _error("comparison-verdict", "comparison release proof is invalid")
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(_error("comparison-read", str(exc)))

    try:
        held_payload = _read_json(root / str(held_out.get("path") or ""))
        journeys = held_payload.get("journeys")
        if not isinstance(journeys, list) or not journeys:
            errors.append(_error("held-out-contract", "held-out journeys missing"))
        else:
            for journey in journeys:
                failures = evaluate_metrics(journey.get("metrics") or {})
                actual = not failures
                if actual is not bool(journey.get("expected_pass")):
                    errors.append(
                        _error(
                            "held-out-verdict",
                            f"{journey.get('id')}: expected verdict mismatch",
                        )
                    )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(_error("held-out-read", str(exc)))

    stable_errors = sorted(
        errors, key=lambda item: (item["code"], item["message"])
    )
    return {
        "schema_version": 1,
        "passed": not stable_errors,
        "baseline_version": contract.get("baseline_version", ""),
        "claim_scope": contract.get("claim_scope", ""),
        "reference_profiles": list(PROFILES),
        "reference_reports": list(REFERENCE_REPORTS),
        "metrics": metrics,
        "errors": stable_errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the frozen Owledge benchmark baseline."
    )
    parser.add_argument("--project-root", default=str(REPO_ROOT))
    parser.add_argument("--contract", default=None)
    args = parser.parse_args(argv)
    result = validate_benchmark_baseline(
        args.project_root,
        contract_path=args.contract,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
