"""Shared fixtures for the owledge v0.6.1 fix-up test suite.

Every test that needs a fresh project uses the `fresh_project` fixture, which
runs `init-project` into a temp directory and yields the path. Tests that need
to simulate an old install edit the manifest's `kit_version` after init.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import hashlib

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="session")
def repo_root() -> pathlib.Path:
    return REPO_ROOT


@pytest.fixture()
def fresh_project(tmp_path) -> pathlib.Path:
    """Init a fresh project into a temp dir and yield its path."""
    target = tmp_path / "fresh-project"
    target.mkdir()
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "owledge.py"), "init-project", "--target", str(target)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"init-project failed: {result.stderr}"
    yield target
    shutil.rmtree(target, ignore_errors=True)


@pytest.fixture()
def fresh_project_with_old_manifest(fresh_project) -> pathlib.Path:
    """A fresh project whose manifest kit_version is forced to 0.6.0 (simulates an old install)."""
    man_path = fresh_project / "kit-manifest.json"
    data = json.loads(man_path.read_text(encoding="utf-8"))
    data["kit_version"] = "0.6.0"
    man_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return fresh_project


def run_owledge(args: list[str], project_root: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    """Run the owledge CLI with the given args; returns the CompletedProcess."""
    cmd = [sys.executable, str(REPO_ROOT / "tools" / "owledge.py")] + args
    if project_root is not None:
        cmd += ["--project-root", str(project_root)]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))


def run_cli(args: list[str], project_root: pathlib.Path) -> subprocess.CompletedProcess:
    """Run the owledge_core.py with the given args."""
    cmd = [sys.executable, str(REPO_ROOT / "tools" / "owledge_core.py"), "--project-root", str(project_root)] + args
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))


def set_manifest_kit_version(project: pathlib.Path, version: str) -> None:
    man = project / "kit-manifest.json"
    data = json.loads(man.read_text(encoding="utf-8"))
    data["kit_version"] = version
    man.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def write_file(project: pathlib.Path, rel: str, content: str) -> None:
    """Write content to project/<rel> without a BOM."""
    p = project / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")


def file_sha(project: pathlib.Path, rel: str) -> str:
    p = project / rel
    return _sha256_file(p) if p.is_file() else ""