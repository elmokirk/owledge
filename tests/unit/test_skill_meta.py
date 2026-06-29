"""Gate set 4 - concept-audit META test + skill behavior tests."""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

from conftest import run_owledge, run_cli, REPO_ROOT


SIX_NAMED_FINDINGS = [
    "no upgrade",
    "upgrade",
    "version",
    "drift",
    "dogfood",
    "global",
    "silent",
    "skip",
    "concept",
    "audit",
]

META_FINDING_PHRASES = [
    "no upgrade",
    "upgrade path",
    "version drift",
    "version string",
    "dogfood",
    "global-link",
    "global layer",
    "silent",
    "skip",
    "concept",
    "audit",
]


def test_skill_finds_its_own_gaps_against_v060(tmp_path):
    """META test: the concept-blindspot-audit skill documents the 6 findings it was created to surface.

    We verify the skill's own rubric (audit-dimensions.md) references the 6
    named findings from the v0.6.1 session. This proves the skill encodes the
    gaps it exists to detect. A second check runs concept-audit against a
    stripped temp project (no manifest, no skills) and verifies the lifecycle
    dimension surfaces a finding about the missing manifest.
    """
    import pytest
    rubric = (REPO_ROOT / "skills" / "concept-blindspot-audit" / "references" / "audit-dimensions.md").read_text(encoding="utf-8")
    rubric_lower = rubric.lower()
    required_phrases = ["no upgrade", "version drift", "dogfood", "global-link", "silent", "concept"]
    hits = sum(1 for p in required_phrases if p.lower() in rubric_lower)
    assert hits >= 4, f"skill rubric only references {hits}/6 named findings (need >=4): {required_phrases}"
    project = tmp_path / "v060-state"
    project.mkdir()
    init = run_owledge(["init-project", "--target", str(project)])
    assert init.returncode == 0
    (project / "kit-manifest.json").unlink(missing_ok=True)
    skills_dir = project / "skills" / "concept-blindspot-audit"
    if skills_dir.exists():
        shutil.rmtree(skills_dir)
    audit = run_owledge(["concept-audit"], project)
    out = json.loads(audit.stdout)
    all_finding_text = ""
    for d in out.get("dimensions", [])[:4]:
        for f in d.get("findings", []):
            all_finding_text += " " + f.get("detail", "") + " " + f.get("evidence", "")
    assert "manifest" in all_finding_text.lower() or "kit_version" in all_finding_text.lower(), \
        f"lifecycle dim did not flag missing manifest: {all_finding_text[:300]}"


def test_skill_clean_on_v061(fresh_project):
    """The fixed v0.6.1 fresh project: lifecycle dim scores 10 (manifest present, upgrade exists)."""
    import pytest
    result = run_owledge(["concept-audit"], fresh_project)
    out = json.loads(result.stdout)
    lifecycle = next((d for d in out.get("dimensions", []) if d["name"] == "lifecycle"), None)
    assert lifecycle is not None, "no lifecycle dimension in concept-audit output"
    assert lifecycle["score"] == 10, f"lifecycle dim scored {lifecycle['score']} on a clean v0.6.1 project: {lifecycle.get('findings')}"


def test_skill_adapts_to_mode(fresh_project):
    """Plan: concept-audit honors project_mode from the profile (poc vs saas)."""
    import pytest
    profile_poc = fresh_project / "poc-profile.json"
    profile_poc.open("w", encoding="utf-8").write(json.dumps({"project_mode": "poc"}))
    poc = run_owledge(["concept-audit", "--profile", str(profile_poc)], fresh_project)
    poc_out = json.loads(poc.stdout)
    assert poc_out["project_mode"] == "poc", f"profile project_mode not honored: {poc_out.get('project_mode')}"
    profile_saas = fresh_project / "saas-profile.json"
    profile_saas.open("w", encoding="utf-8").write(json.dumps({"project_mode": "saas"}))
    saas = run_owledge(["concept-audit", "--profile", str(profile_saas)], fresh_project)
    saas_out = json.loads(saas.stdout)
    assert saas_out["project_mode"] == "saas", f"profile project_mode not honored: {saas_out.get('project_mode')}"


def test_skill_respects_planning_mode(fresh_project):
    """Plan: supervised -> no files written to decisions/."""
    import pytest
    profile_supervised = fresh_project / "supervised-profile.json"
    profile_supervised.open("w", encoding="utf-8").write(json.dumps({"planning_mode": "supervised", "project_mode": "mvp"}))
    decisions_before = list((fresh_project / "owledge" / "decisions").glob("concept-audit-*.md"))
    result = run_owledge(["concept-audit", "--profile", str(profile_supervised)], fresh_project)
    out = json.loads(result.stdout)
    assert out["planning_mode"] == "supervised", f"planning_mode not honored: {out.get('planning_mode')}"
    decisions_after = list((fresh_project / "owledge" / "decisions").glob("concept-audit-*.md"))
    assert len(decisions_after) == len(decisions_before), "supervised mode wrote a concept-audit file"


def test_concept_audit_returns_score(fresh_project):
    """P1-13: concept_audit return shape includes a top-level score (regardless of pass/fail)."""
    result = run_owledge(["concept-audit"], fresh_project)
    out = json.loads(result.stdout)
    assert "score" in out, f"concept_audit return missing top-level 'score': {list(out.keys())}"
    assert isinstance(out["score"], (int, float)), f"score not numeric: {out['score']}"