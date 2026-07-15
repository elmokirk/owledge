"""Regression tests for the release QA contract surface."""

from __future__ import annotations

import json
import pathlib
import sys

from conftest import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
import owledge  # noqa: E402


def make_contract_root(tmp_path: pathlib.Path) -> pathlib.Path:
    root = tmp_path / "contract-root"
    (root / "contracts").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "tools").mkdir()
    (root / "plugins" / "test-plugin" / ".claude-plugin").mkdir(parents=True)
    (root / "plugins" / "test-plugin" / ".codex-plugin").mkdir(parents=True)
    (root / "plugins" / "owledge-cowork" / ".claude-plugin").mkdir(parents=True)
    (root / "plugins" / "owledge-cowork" / ".codex-plugin").mkdir(parents=True)
    (root / "VERSION").write_text("1.2.3\n", encoding="utf-8")
    (root / "pyproject.toml").write_text('[project]\nversion = "1.2.3"\n', encoding="utf-8")
    (root / "README.md").write_text("[![Version](https://x/version-1.2.3-blue)]\nproject-local\nuvx owledge quickstart --target /path/to/your-project\n", encoding="utf-8")
    (root / "CHANGELOG.md").write_text("## 1.2.3\n", encoding="utf-8")
    (root / "docs" / "README.md").write_text("Current release v1.2.3\n", encoding="utf-8")
    (root / "docs" / "command-reference.md").write_text("doctor\nPython-first\n", encoding="utf-8")
    (root / "tools" / "owledge.py").write_text('sub.add_parser("doctor")\n', encoding="utf-8")
    (root / "docs" / "harness-plugin-matrix.md").write_text("Local adapter support\n", encoding="utf-8")
    (root / "SECURITY.md").write_text("This local kit is not yet certified.\n", encoding="utf-8")
    (root / "plugins" / "test-plugin" / "VERSION").write_text("1.2.3\n", encoding="utf-8")
    for manifest in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        (root / "plugins" / "test-plugin" / manifest).write_text('{"version": "1.2.3"}\n', encoding="utf-8")
        (root / "plugins" / "owledge-cowork" / manifest).write_text('{"name": "Owledge", "version": "1.2.3"}\n', encoding="utf-8")
    (root / "plugins" / "owledge-cowork" / "VERSION").write_text("1.2.3\n", encoding="utf-8")
    contract = {
        "schema_version": 1,
        "version_source": "VERSION",
        "version_sinks": [
            {"path": "pyproject.toml", "kind": "toml-project-version"},
            {"path": "README.md", "kind": "readme-badge"},
            {"path": "docs/README.md", "kind": "current-release"},
            {"path": "CHANGELOG.md", "kind": "top-changelog-heading"},
            {"path": "plugins/test-plugin/VERSION", "kind": "plain-version"},
            {"path": "plugins/test-plugin/.claude-plugin/plugin.json", "kind": "json-version"},
            {"path": "plugins/test-plugin/.codex-plugin/plugin.json", "kind": "json-version"},
        ],
        "public_docs": {"include": ["README.md", "docs/**/*.md"], "exclude": [], "historical_marker": "Historical"},
        "features": [{"id": "cli", "source_globs": ["tools/owledge.py"], "docs": ["README.md", "docs/command-reference.md"], "tests": ["contracts"]}],
    }
    (root / "contracts" / "release-surface.json").write_text(json.dumps(contract), encoding="utf-8")
    return root


def test_version_contract_rejects_each_mutated_version_sink(tmp_path):
    root = make_contract_root(tmp_path)
    assert owledge.version_contract_gate(root)["passed"] is True
    mutations = {
        "pyproject.toml": '[project]\nversion = "9.9.9"\n',
        "README.md": "[![Version](https://x/version-9.9.9-blue)]\nproject-local\nuvx owledge quickstart --target /path/to/your-project\n",
        "docs/README.md": "Current release v9.9.9\n",
        "CHANGELOG.md": "## 9.9.9\n",
        "plugins/test-plugin/VERSION": "9.9.9\n",
        "plugins/test-plugin/.claude-plugin/plugin.json": '{"version": "9.9.9"}\n',
        "plugins/test-plugin/.codex-plugin/plugin.json": '{"version": "9.9.9"}\n',
    }
    for path, mutation in mutations.items():
        candidate = make_contract_root(tmp_path / path.replace("/", "_"))
        (candidate / path).write_text(mutation, encoding="utf-8")
        assert owledge.version_contract_gate(candidate)["passed"] is False, path


def test_docs_contract_requires_docs_for_an_impacted_feature(tmp_path):
    root = make_contract_root(tmp_path)
    missing_docs = owledge.docs_contract_gate(root, changed_files=["tools/owledge.py"])
    assert missing_docs["passed"] is False
    complete_docs = owledge.docs_contract_gate(
        root,
        changed_files=["tools/owledge.py", "README.md", "docs/command-reference.md"],
    )
    assert complete_docs["passed"] is True


def test_release_contract_writes_machine_readable_evidence(tmp_path):
    root = make_contract_root(tmp_path)
    evidence_path = root / "dist" / "release-evidence.json"
    result = owledge.release_contract_gate(root, evidence_path=str(evidence_path))
    assert result["passed"] is True
    assert json.loads(evidence_path.read_text(encoding="utf-8"))["version"] == "1.2.3"
