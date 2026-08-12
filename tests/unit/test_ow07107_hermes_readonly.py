"""Protocol and boundary checks for the OW-071-07 Hermes read-only profile."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "hermes-readonly-profile.md"
CONTRACT = ROOT / "addons" / "runtime-conformance-kit" / "contracts" / "hermes-readonly.json"
TRANSCRIPT = ROOT / "addons" / "runtime-conformance-kit" / "fixtures" / "hermes-readonly-transcript.json"


def fixture_project(root: Path) -> None:
    (root / "OWLEDGE.md").write_text("# Owledge\n", encoding="utf-8")
    (root / ".owledge" / "canonical").mkdir(parents=True)
    (root / ".owledge" / "canonical" / "request.md").write_text(
        "---\nstatus: reviewed\nsummary: bounded request\n---\n# Request\n", encoding="utf-8"
    )


def run_server(project: Path, messages: list[dict]) -> list[dict]:
    process = subprocess.run(
        [sys.executable, "tools/owledge_mcp.py", "--project-root", str(project)],
        cwd=ROOT,
        input="\n".join(json.dumps(message) for message in messages) + "\n",
        text=True,
        capture_output=True,
    )
    if process.returncode:
        raise AssertionError(process.stderr)
    return [json.loads(line) for line in process.stdout.splitlines() if line]


class HermesReadonlyProfileTests(unittest.TestCase):
    def test_docs_contract_and_fixture_state_boundaries(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        for phrase in ("hermes config show", "hermes mcp test owledge_readonly", "/reload-mcp", "Hermes conversation memory/compression is separate", "does not grant", "exactly these eight tools"):
            self.assertIn(phrase, text)
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        transcript = json.loads(TRANSCRIPT.read_text(encoding="utf-8"))
        self.assertEqual(contract["profile"], "tier-1-read-only")
        self.assertEqual(len(contract["required_tools"]), 8)
        self.assertEqual(transcript["expected"]["write_tools"], 0)

    def test_all_required_tools_are_read_only_and_bound(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ow07107-") as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            fixture_project(project)
            responses = run_server(project, [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "owledge_read_entrypoint", "arguments": {}}},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "owledge_search_memory", "arguments": {"query": "request"}}},
                {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "owledge_build_context_pack", "arguments": {"task_id": "OW-TEST", "objective": "bounded"}}},
                {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "owledge_list_tasks", "arguments": {}}},
                {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "owledge_list_reviews", "arguments": {}}},
            ])
            self.assertEqual(next(row for row in responses if row["id"] == 1)["result"]["serverInfo"]["version"], "0.7.1")
            tools = next(row for row in responses if row["id"] == 2)["result"]["tools"]
            self.assertEqual({tool["name"] for tool in tools}, set(json.loads(CONTRACT.read_text(encoding="utf-8"))["required_tools"]))
            self.assertTrue(all("write" not in f"{tool['name']} {tool['description']}".lower() for tool in tools))
            for identifier in range(3, 8):
                self.assertIn("result", next(row for row in responses if row["id"] == identifier))

    def test_unbound_path_mismatch_and_disabled_tool_fail_explicitly(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ow07107-") as temp_dir:
            project = Path(temp_dir) / "project"
            other = Path(temp_dir) / "other"
            project.mkdir()
            other.mkdir()
            fixture_project(project)
            responses = run_server(project, [
                {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "owledge_read_entrypoint", "arguments": {"project_root": str(other)}}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "owledge_write_evidence", "arguments": {}}},
            ])
            self.assertIn("bound", next(row for row in responses if row["id"] == 1)["error"]["message"])
            self.assertIn("Unknown tool", next(row for row in responses if row["id"] == 2)["error"]["message"])
            missing = subprocess.run([sys.executable, "tools/owledge_mcp.py", "--project-root", str(other)], cwd=ROOT, text=True, capture_output=True)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("Missing OWLEDGE.md", missing.stderr)

    def test_entrypoint_or_memory_path_outside_bound_project_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ow07107-") as temp_dir:
            root = Path(temp_dir)
            project = root / "project"
            project.mkdir()
            fixture_project(project)
            outside = root / "outside.md"
            outside.write_text("# outside\n", encoding="utf-8")
            self.assertRaisesRegex(ValueError, "outside the bound project", __import__("importlib").import_module("tools.owledge_mcp")._ensure_within, project, outside, "test")
            link = project / "OWLEDGE.md"
            try:
                link.unlink()
                link.symlink_to(outside)
            except OSError:
                return
            process = subprocess.run([sys.executable, "tools/owledge_mcp.py", "--project-root", str(project)], cwd=ROOT, text=True, capture_output=True)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("outside the bound project", process.stderr)


if __name__ == "__main__":
    unittest.main()
