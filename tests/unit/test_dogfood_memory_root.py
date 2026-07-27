from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

import pytest

from conftest import REPO_ROOT
from tools import owledge
from tools import owledge_core


def _seed_dogfood_record(repo: pathlib.Path) -> None:
    target = repo / "internal" / "owledge" / "canonical" / "memory.md"
    target.parent.mkdir(parents=True)
    source = (
        REPO_ROOT
        / "tests"
        / "fixtures"
        / "retrieval-corpus"
        / ".owledge"
        / "canonical"
        / "context-pack-objective.md"
    )
    shutil.copy2(source, target)


def test_dogfood_scan_gate_rejects_empty_internal_memory(tmp_path):
    repo = tmp_path / "repo"
    (repo / "internal" / "owledge").mkdir(parents=True)

    with pytest.raises(RuntimeError, match="vacuous"):
        owledge.dogfood_memory_scan_gate(repo)


def test_dogfood_validate_and_index_scan_internal_records(tmp_path):
    repo = tmp_path / "repo"
    _seed_dogfood_record(repo)

    assert owledge.resolve_memory_root(repo) == repo
    scan = owledge.dogfood_memory_scan_gate(repo)
    assert scan["memory_dir"] == "internal/owledge"
    assert scan["markdown_files"] == 1
    assert scan["indexed_records"] == 1

    validation = owledge_core.validate_memory(repo, strict=False)
    assert validation["totalChecks"] > 0
    index = owledge_core.build_memory_index(repo)
    assert index["rows"] == 1
    assert index["path"].startswith("internal/owledge/indexes/")


def test_retrieval_and_finalization_payloads_do_not_persist_private_paths(tmp_path):
    repo = tmp_path / "private-user" / "repo"
    _seed_dogfood_record(repo)
    result = owledge_core.evaluate_memory_retrieval(
        repo,
        [repo],
        output_dir=repo / "internal" / "owledge" / "exports" / "retrieval-eval",
    )

    assert result["project_roots"] == ["."]
    assert result["outputs"]["json"].startswith("internal/owledge/")
    output = repo / "internal" / "owledge" / "exports" / "retrieval-eval" / "retrieval-eval.json"
    persisted = output.read_text(encoding="utf-8")
    assert str(repo) not in persisted
    assert repo.as_posix() not in persisted

    sanitized = owledge.sanitize_generated_payload(
        {"project": str(repo), "nested": {"path": str(repo / "internal" / "owledge")}},
        repo,
    )
    assert sanitized == {"project": ".", "nested": {"path": "./internal/owledge"}}
    assert str(pathlib.Path.home()) not in json.dumps(sanitized)


def test_finalization_evidence_becomes_stale_after_source_edit(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "owledge-test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Owledge Test"], cwd=repo, check=True)
    source = repo / "OWLEDGE.md"
    source.write_text("# Project truth\n", encoding="utf-8")
    subprocess.run(["git", "add", "OWLEDGE.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True)

    recorded = owledge.git_source_identity(repo)
    assert recorded["source_clean"] is True
    evidence = {"source_identity": recorded}

    generated = repo / "internal" / "owledge" / "exports" / "finalization-gates" / "latest.json"
    generated.parent.mkdir(parents=True)
    generated.write_text("{}\n", encoding="utf-8")
    assert owledge.finalization_evidence_freshness(repo, evidence)["passed"] is True

    source.write_text("# Changed project truth\n", encoding="utf-8")
    freshness = owledge.finalization_evidence_freshness(repo, evidence)
    assert freshness["passed"] is False
    assert freshness["source_tree_hash_match"] is False
    assert freshness["dirty_source_paths"] == ["OWLEDGE.md"]
    with pytest.raises(RuntimeError, match="source tree is dirty"):
        owledge.clean_source_gate(repo)


def test_generated_evidence_private_path_gate_rejects_and_accepts_sanitized_payload(tmp_path):
    repo = tmp_path / "private-user" / "repo"
    report = repo / "internal" / "owledge" / "exports" / "finalization-gates" / "latest.json"
    report.parent.mkdir(parents=True)
    report.write_text(json.dumps({"project": str(repo)}), encoding="utf-8")

    with pytest.raises(RuntimeError, match="machine-private paths"):
        owledge.generated_evidence_private_path_gate(repo)

    payload = owledge.sanitize_generated_payload({"project": str(repo)}, repo)
    report.write_text(json.dumps(payload), encoding="utf-8")
    result = owledge.generated_evidence_private_path_gate(repo)
    assert result["passed"] is True
    assert result["scanned_files"] == 1
