"""Regression tests for bounded planning modes and harness skill discovery."""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

from conftest import REPO_ROOT, run_cli
from tools.owledge import HOST_SKILL_DIRS


PLANNING_SKILLS = (
    "owledge-long-horizon-delivery",
    "owledge-planning-layer",
    "owledge-brainstorm",
)


def _tree_hash(root: pathlib.Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _doctor_check(payload: dict, name: str) -> dict:
    return next(row for row in payload["checks"] if row["name"] == name)


def test_long_horizon_skill_defines_bounded_modes_and_mvp_stop():
    skill = (
        REPO_ROOT / "skills" / "owledge-long-horizon-delivery" / "SKILL.md"
    ).read_text(encoding="utf-8")
    modes = (
        REPO_ROOT
        / "skills"
        / "owledge-long-horizon-delivery"
        / "references"
        / "modes.md"
    ).read_text(encoding="utf-8")
    combined = f"{skill}\n{modes}".lower()

    assert skill.startswith("---\nname: owledge-long-horizon-delivery\n")
    for mode in (
        "mvp-sparring",
        "version-steering",
        "ticket-execution",
        "gate-review",
        "recovery",
    ):
        assert mode in combined
    for contract_term in (
        "mvp lock card",
        "roadmap",
        "idea candidate",
        "lock",
        "adjust",
        "defer",
    ):
        assert contract_term in combined
    assert "do not generate another plan variant" in combined


def test_planning_skill_is_bounded_compatibility_facade():
    planning = (
        REPO_ROOT / "skills" / "owledge-planning-layer" / "SKILL.md"
    ).read_text(encoding="utf-8").lower()
    brainstorm = (
        REPO_ROOT / "skills" / "owledge-brainstorm" / "SKILL.md"
    ).read_text(encoding="utf-8").lower()

    assert "mvp-sparring" in planning
    assert "owledge-long-horizon-delivery" in planning
    assert "stop" in planning
    assert ".owledge/ideas" in planning
    assert "mvp-sparring" in brainstorm


def test_planning_plugin_mirrors_match_canonical_sources():
    for skill_name in PLANNING_SKILLS:
        canonical = REPO_ROOT / "skills" / skill_name
        plugin = REPO_ROOT / "plugins" / "owledge-cowork" / "skills" / skill_name
        assert plugin.is_dir(), f"missing plugin mirror: {skill_name}"
        assert _tree_hash(plugin) == _tree_hash(canonical), (
            f"plugin mirror drifted from canonical skill: {skill_name}"
        )


def test_standalone_planning_mirrors_match_canonical_sources():
    for skill_name in PLANNING_SKILLS:
        canonical = REPO_ROOT / "skills" / skill_name
        standalone = REPO_ROOT / "standalone-skills" / skill_name
        assert standalone.is_dir(), f"missing standalone mirror: {skill_name}"
        assert _tree_hash(standalone) == _tree_hash(canonical), (
            f"standalone mirror drifted from canonical skill: {skill_name}"
        )


def test_init_materializes_codex_discovery_mirrors(fresh_project):
    manifest = json.loads(
        (fresh_project / "kit-manifest.json").read_text(encoding="utf-8")
    )
    manifest_rows = {row["path"]: row for row in manifest["files"]}

    for skill_name in PLANNING_SKILLS:
        canonical = fresh_project / "skills" / skill_name
        discoverable = fresh_project / ".agents" / "skills" / skill_name
        assert (canonical / "SKILL.md").is_file()
        assert (discoverable / "SKILL.md").is_file()
        assert _tree_hash(canonical) == _tree_hash(discoverable)

    manifest_path = (
        ".agents/skills/owledge-long-horizon-delivery/SKILL.md"
    )
    assert manifest_path in manifest_rows
    assert manifest_rows[manifest_path]["sha256_original"]

    doctor = run_cli(["doctor", "--mode", "host"], fresh_project)
    assert doctor.returncode == 0, doctor.stderr
    discovery = _doctor_check(json.loads(doctor.stdout), "agent-skill-discovery")
    assert discovery["passed"] is True


def test_every_host_skill_has_canonical_discovery_and_manifest_hashes(fresh_project):
    manifest = json.loads(
        (fresh_project / "kit-manifest.json").read_text(encoding="utf-8")
    )
    rows = {row["path"]: row for row in manifest["files"]}

    for skill_dir in HOST_SKILL_DIRS:
        skill_name = pathlib.PurePosixPath(skill_dir).name
        canonical_rel = f"{skill_dir}/SKILL.md"
        discovery_rel = f".agents/skills/{skill_name}/SKILL.md"
        canonical = fresh_project / canonical_rel
        discoverable = fresh_project / discovery_rel
        assert canonical.is_file(), canonical_rel
        assert discoverable.is_file(), discovery_rel
        assert canonical.read_bytes() == discoverable.read_bytes()
        for rel in (canonical_rel, discovery_rel):
            assert rel in rows
            assert rows[rel]["sha256_original"]
            assert rows[rel]["sha256_installed"] == hashlib.sha256(
                (fresh_project / rel).read_bytes()
            ).hexdigest()


def test_doctor_warns_when_discovery_mirror_is_missing(fresh_project):
    missing = (
        fresh_project
        / ".agents"
        / "skills"
        / "owledge-long-horizon-delivery"
        / "SKILL.md"
    )
    missing.unlink()

    doctor = run_cli(["doctor", "--mode", "host"], fresh_project)
    payload = json.loads(doctor.stdout)
    discovery = _doctor_check(payload, "agent-skill-discovery")
    assert discovery["passed"] is False
    assert discovery["severity"] == "warning"
    assert "owledge-long-horizon-delivery" in discovery["details"]


def test_project_folder_builder_materializes_discovery_mirrors(tmp_path):
    target = tmp_path / "project-folder-kit"
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools" / "build_project_folder_kit.py"),
            "--project-root",
            str(REPO_ROOT),
            "--output-path",
            str(target),
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, result.stderr

    canonical = target / "skills" / "owledge-long-horizon-delivery"
    discoverable = (
        target / ".agents" / "skills" / "owledge-long-horizon-delivery"
    )
    assert _tree_hash(canonical) == _tree_hash(discoverable)
    manifest = json.loads(
        (target / "kit-manifest.json").read_text(encoding="utf-8")
    )
    rows = {row["path"]: row for row in manifest["files"]}
    row = rows[".agents/skills/owledge-long-horizon-delivery/SKILL.md"]
    assert row["sha256_original"]
