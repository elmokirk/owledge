"""Gate set 6 - release-notes enforcement + command-reference coverage + pyproject version."""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

from conftest import REPO_ROOT


def test_command_reference_covers_all_subcommands():
    """P1-10: every argparse subcommand in tools/owledge.py has a docs/command-reference.md entry."""
    owledge_py = (REPO_ROOT / "tools" / "owledge.py").read_text(encoding="utf-8")
    cmd_ref = (REPO_ROOT / "docs" / "command-reference.md").read_text(encoding="utf-8")
    subcommands = re.findall(r'sub\.add_parser\("([^"]+)"', owledge_py)
    missing = [c for c in subcommands if c not in cmd_ref]
    assert not missing, f"subcommands missing from command-reference.md: {missing}"


def test_pyproject_version_matches_version_file():
    """Phase 6: pyproject.toml version must equal the VERSION file."""
    version_file = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    assert match, "no version field in pyproject.toml"
    pyproject_version = match.group(1)
    assert pyproject_version == version_file, f"pyproject version {pyproject_version} != VERSION file {version_file}"


def test_release_notes_required_on_schema_change():
    """E6: if templates/ or schemas/ changed, CHANGELOG.md must have '## Upgrade notes' (or '### Upgrade notes')."""
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "Upgrade notes" in changelog, "CHANGELOG.md missing '## Upgrade notes' section"
    assert re.search(r"breaking:\s*(yes|no|additive)", changelog, re.IGNORECASE), "CHANGELOG missing 'breaking: yes|no|additive' declaration"


def test_no_dead_flags():
    """P1-7: --since must NOT be a registered flag for concept-audit (removed); --format for upgrade must be present."""
    owledge_py = (REPO_ROOT / "tools" / "owledge.py").read_text(encoding="utf-8")
    concept_audit_idx = owledge_py.index('add_parser("concept-audit"')
    concept_audit_end = owledge_py.index("\n\n", concept_audit_idx)
    concept_audit_block = owledge_py[concept_audit_idx:concept_audit_end]
    assert "--since" not in concept_audit_block, "concept-audit still has dead --since flag"
    upgrade_idx = owledge_py.index('add_parser("upgrade"')
    upgrade_end = owledge_py.index("\n\n", upgrade_idx)
    upgrade_block = owledge_py[upgrade_idx:upgrade_end]
    assert "--format" in upgrade_block, "upgrade missing --format flag"