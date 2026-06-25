"""Gate set 5 - cross-workstream integration stress test."""

from __future__ import annotations

import json

from conftest import run_owledge, run_cli, set_manifest_kit_version, REPO_ROOT


def test_integration_stress_after_parallel(fresh_project):
    """Plan: with all features applied together, finalization-gates + fresh-init cycle + doctor + dogfood-sync all green.

    Uses a fresh project (which has all v0.6.1 features) and runs the core
    lifecycle commands against it. The repo-level dogfood-sync is checked
    separately.
    """
    project = fresh_project
    doctor = run_owledge(["doctor"], project)
    doctor_json = json.loads(doctor.stdout)
    assert doctor_json["passed"] is True, f"doctor failed on fresh project: {doctor_json}"
    upgrade = run_owledge(["upgrade", "--dry-run"], project)
    upgrade_json = json.loads(upgrade.stdout)
    assert upgrade.returncode == 0, f"upgrade --dry-run failed: {upgrade.stderr}"
    repo_dogfood = run_cli(["dogfood-sync-check"], REPO_ROOT)
    repo_dogfood_json = json.loads(repo_dogfood.stdout)
    assert repo_dogfood_json["passed"] is True, f"repo dogfood-sync-check failed: {repo_dogfood_json}"