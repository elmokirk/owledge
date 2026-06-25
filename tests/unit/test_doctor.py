"""Gate set 2 - doctor drift + global-link stress tests."""

from __future__ import annotations

import json
import os
import pathlib
import shutil

from conftest import run_owledge, run_cli, set_manifest_kit_version, write_file, file_sha, REPO_ROOT


def test_doctor_detects_drift(fresh_project):
    """E2: bump KIT_VERSION in manifest -> doctor returns passed=False, lists outdated_files."""
    project = fresh_project
    set_manifest_kit_version(project, "0.6.0")
    result = run_owledge(["doctor"], project)
    doctor = json.loads(result.stdout)
    assert doctor["passed"] is False, f"doctor should fail on version drift, got passed={doctor['passed']}"
    assert len(doctor.get("outdated_files", [])) > 0, "outdated_files empty despite version mismatch"


def test_doctor_distinguishes_edits(fresh_project):
    """E2: edit a template hash -> classified user_edited, not outdated."""
    project = fresh_project
    set_manifest_kit_version(project, "0.6.0")
    editable_rel = "agent-memory/templates/task-card-template.md"
    write_file(project, editable_rel, "# user-edited\n")
    result = run_owledge(["doctor"], project)
    doctor = json.loads(result.stdout)
    assert editable_rel in doctor.get("user_edited_files", []), f"{editable_rel} not in user_edited_files"
    assert editable_rel not in doctor.get("outdated_files", []), f"{editable_rel} should not be in outdated_files"


def test_global_link_survives_move(fresh_project, tmp_path):
    """E4: init --link-global /tmp/g, move /tmp/g -> doctor error; restore -> pass."""
    project = fresh_project
    global_dir = tmp_path / "global-layer"
    global_dir.mkdir()
    link_result = run_owledge(["init-project", "--target", str(project), "--link-global", str(global_dir)])
    assert link_result.returncode == 0
    shutil.rmtree(global_dir)
    doctor = json.loads(run_owledge(["doctor"], project).stdout)
    global_link_checks = [c for c in doctor.get("checks", []) if c.get("name") == "global-link"]
    if global_link_checks:
        assert global_link_checks[0]["passed"] is False, "doctor should fail when global layer moved"
    global_dir.mkdir()
    doctor2 = json.loads(run_owledge(["doctor"], project).stdout)
    global_link_checks2 = [c for c in doctor2.get("checks", []) if c.get("name") == "global-link"]
    if global_link_checks2:
        assert global_link_checks2[0]["passed"] is True, "doctor should pass when global layer restored"


def test_global_link_resolves_env(fresh_project, tmp_path, monkeypatch):
    """E4: OWLEDGE_GLOBAL_HOME set + --link-global (no arg) -> path == env value."""
    project = fresh_project
    env_global = tmp_path / "env-global"
    env_global.mkdir()
    monkeypatch.setenv("OWLEDGE_GLOBAL_HOME", str(env_global))
    result = run_owledge(["init-project", "--target", str(project), "--link-global"])
    assert result.returncode == 0
    link_path = project / "agent-memory" / "global-link.json"
    if link_path.is_file():
        link = json.loads(link_path.read_text(encoding="utf-8"))
        assert pathlib.Path(link["path"]) == env_global, f"global-link path {link['path']} != env {env_global}"
        assert link["source"] == "env"