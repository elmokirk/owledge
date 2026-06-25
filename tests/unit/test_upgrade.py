"""Gate set 1 - upgrade command P0/P1 stress tests.

Tests the three P0 fixes (skills in manifest, manual never writes, git-apply-able
patch) plus the plan's named E3 acceptance tests.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import shutil
import os

from conftest import run_owledge, set_manifest_kit_version, write_file, file_sha, REPO_ROOT


def test_skills_listed_in_manifest(fresh_project):
    """P0-1: a freshly init'd project's manifest contains skills/concept-blindspot-audit entries."""
    man = json.loads((fresh_project / "kit-manifest.json").read_text(encoding="utf-8"))
    skill_entries = [f for f in man["files"] if f["path"].startswith("skills/concept-blindspot-audit/")]
    assert len(skill_entries) >= 3, f"expected >=3 skill entries, got {len(skill_entries)}"
    paths = {f["path"] for f in skill_entries}
    assert "skills/concept-blindspot-audit/SKILL.md" in paths
    assert "skills/concept-blindspot-audit/references/audit-dimensions.md" in paths
    assert "skills/concept-blindspot-audit/references/profile-template.json" in paths


def test_skill_copied_to_target(fresh_project):
    """P0-1: the concept-blindspot-audit skill is physically installed by init-project."""
    assert (fresh_project / "skills" / "concept-blindspot-audit" / "SKILL.md").is_file()


def test_skills_upgradable(fresh_project_with_old_manifest):
    """P0-1: a tampered skill file is classified user_edited by doctor (detected, not silently ignored).

    Safe mode preserves user edits (does not overwrite), so we verify detection
    rather than restoration. force-templates --yes restores it to pristine.
    """
    project = fresh_project_with_old_manifest
    skill_rel = "skills/concept-blindspot-audit/SKILL.md"
    original_sha = file_sha(project, skill_rel)
    write_file(project, skill_rel, "# tampered skill content\n")
    doctor = run_owledge(["doctor"], project)
    doctor_json = json.loads(doctor.stdout)
    assert doctor_json["passed"] is False
    assert skill_rel in doctor_json.get("user_edited_files", []), f"skill edit not detected by doctor: {doctor_json.get('user_edited_files')}"
    upgrade = run_owledge(["upgrade", "--apply", "--mode=force-templates", "--yes"], project)
    assert upgrade.returncode == 0, f"force-templates failed: {upgrade.stderr}"
    after_sha = file_sha(project, skill_rel)
    assert after_sha == original_sha, f"skill not restored to pristine by force-templates: {after_sha} != {original_sha}"


def test_manual_mode_never_writes(fresh_project_with_old_manifest):
    """P0-2: upgrade --apply --mode=manual is rejected with exit 2 and writes nothing."""
    project = fresh_project_with_old_manifest
    design_before = file_sha(project, "DESIGN.md")
    result = run_owledge(["upgrade", "--apply", "--mode=manual"], project)
    assert result.returncode == 2, f"expected exit 2, got {result.returncode}"
    out = json.loads(result.stdout)
    assert out["passed"] is False
    assert "manual mode is always dry-run" in out["error"]
    design_after = file_sha(project, "DESIGN.md")
    assert design_before == design_after, "DESIGN.md was modified by manual+apply (must never write)"


def test_manual_patch_is_git_applyable(tmp_path):
    """P0-3: upgrade --dry-run --mode=manual emits a patch that `git apply --check` accepts.

    Build a fake old source (VERSION=0.6.0, one tampered template), init from it,
    then upgrade against the REAL source. The diff for the tampered file is
    non-empty and git-apply-able.
    """
    fake_src = tmp_path / "fake-old-src"
    fake_src.mkdir()
    for item in ["VERSION", "AGENTS.template.md", "CLAUDE.template.md", "PROJECT_CONTEXT.template.md", "USER_CONTEXT.template.md", "DESIGN.md", "REPORT_DESIGN_SELECTOR.html", ".gitignore"]:
        src = REPO_ROOT / item
        if src.is_file():
            shutil.copy2(src, fake_src / item)
    shutil.copytree(REPO_ROOT / "templates", fake_src / "templates")
    shutil.copytree(REPO_ROOT / "skills", fake_src / "skills", dirs_exist_ok=True)
    fake_tools = fake_src / "tools"
    fake_tools.mkdir(exist_ok=True)
    for tool in ["owledge.py", "agent_memory_cli.py", "build_kb_module.py", "build_project_folder_kit.py"]:
        shutil.copy2(REPO_ROOT / "tools" / tool, fake_tools / tool)
    (fake_src / "VERSION").write_text("0.6.0\n", encoding="utf-8")
    old_template = "# Old v0.6.0 task card\n\nThis is the old version.\n"
    (fake_src / "templates" / "agent-memory" / "templates" / "task-card-template.md").write_text(old_template, encoding="utf-8", newline="\n")
    project = tmp_path / "patch-project"
    project.mkdir()
    init = run_owledge(["init-project", "--target", str(project), "--source-root", str(fake_src)])
    assert init.returncode == 0, f"init from fake source failed: {init.stderr}"
    set_manifest_kit_version(project, "0.6.0")
    result = run_owledge(["upgrade", "--dry-run", "--mode=manual", "--source-root", str(REPO_ROOT)], project)
    assert result.returncode == 0, f"upgrade --dry-run --mode=manual failed: {result.stderr}"
    out = json.loads(result.stdout)
    patch_text = out.get("patch", "")
    assert "diff --git" in patch_text, f"patch missing diff --git header: {patch_text[:200]}"
    assert "a/" in patch_text and "b/" in patch_text, "patch missing a/ b/ prefixes"
    patch_path = project / "agent-memory" / "exports" / "upgrade-pending.patch"
    assert patch_path.is_file(), "patch file not written"
    git_check = subprocess.run(
        ["git", "-C", str(project), "apply", "--check", str(patch_path)],
        capture_output=True, text=True,
    )
    assert git_check.returncode == 0, f"git apply --check failed: {git_check.stderr}\npatch:\n{patch_text[:500]}"


def test_safe_preserves_edits(fresh_project_with_old_manifest):
    """Plan: edit an installed template AFTER init, bump version, upgrade --apply --mode=safe -> edited file unchanged.

    The file is user_edited (installed hash != manifest's sha256_original), so
    safe mode must skip it. We verify the file is byte-identical before/after.
    """
    project = fresh_project_with_old_manifest
    editable_rel = "agent-memory/templates/task-card-template.md"
    write_file(project, editable_rel, "# user-edited content\n")
    editable_sha_before = file_sha(project, editable_rel)
    result = run_owledge(["upgrade", "--apply", "--mode=safe"], project)
    assert result.returncode == 0, f"upgrade failed: {result.stderr}"
    out = json.loads(result.stdout)
    skipped = out.get("skipped", [])
    assert any(editable_rel in entry for entry in skipped), f"user-edited file not in skipped list: {skipped}"
    editable_sha_after = file_sha(project, editable_rel)
    assert editable_sha_before == editable_sha_after, "user-edited file was modified by safe mode"


def test_force_templates_respects_never_touch(fresh_project_with_old_manifest):
    """Plan: all 4 never-touch files byte-identical before/after force-templates --yes."""
    project = fresh_project_with_old_manifest
    never_touch = ["PROJECT_CONTEXT.md", "AGENTS.md", "CLAUDE.md", "DESIGN.md"]
    shas_before = {rel: file_sha(project, rel) for rel in never_touch}
    result = run_owledge(["upgrade", "--apply", "--mode=force-templates", "--yes"], project)
    assert result.returncode == 0, f"force-templates failed: {result.stderr}"
    shas_after = {rel: file_sha(project, rel) for rel in never_touch}
    for rel in never_touch:
        assert shas_before[rel] == shas_after[rel], f"never-touch file {rel} was modified by force-templates"


def test_idempotent(fresh_project):
    """Plan: second --apply reports zero updated/created."""
    project = fresh_project
    set_manifest_kit_version(project, "0.6.0")
    first = run_owledge(["upgrade", "--apply", "--mode=safe"], project)
    assert first.returncode == 0
    first_json = json.loads(first.stdout)
    second = run_owledge(["upgrade", "--apply", "--mode=safe"], project)
    assert second.returncode == 0
    second_json = json.loads(second.stdout)
    assert len(second_json.get("updated", [])) == 0, f"second run updated files: {second_json.get('updated')}"
    assert len(second_json.get("created", [])) == 0, f"second run created files: {second_json.get('created')}"


def test_manifest_deleted_graceful(fresh_project):
    """Plan: delete kit-manifest.json, upgrade -> friendly error, no crash."""
    project = fresh_project
    (project / "kit-manifest.json").unlink()
    result = run_owledge(["upgrade", "--dry-run"], project)
    out = json.loads(result.stdout)
    assert out["passed"] is False
    assert "kit-manifest" in out.get("error", "").lower() or "init-project" in out.get("error", "").lower()


def test_concurrent_run_blocked(fresh_project_with_old_manifest):
    """Plan: hold .upgrade.lock with a live PID, second --apply -> refused."""
    project = fresh_project_with_old_manifest
    lock_path = project / "agent-memory" / ".upgrade.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    live_pid = os.getpid()
    lock_path.write_text(json.dumps({"pid": live_pid, "started_at": "2026-01-01T00:00:00Z"}), encoding="utf-8")
    result = run_owledge(["upgrade", "--apply", "--mode=safe"], project)
    out = json.loads(result.stdout)
    assert out["passed"] is False
    assert "lock" in out.get("error", "").lower() or "pid" in out.get("error", "").lower()