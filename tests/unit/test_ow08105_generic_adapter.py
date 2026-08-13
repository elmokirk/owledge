from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVER = ROOT / "tools" / "owledge_generic_adapter.py"


def run_server(project: pathlib.Path, messages: list[object]) -> list[dict]:
    process = subprocess.run(
        [sys.executable, str(SERVER), "--project-root", str(project)], cwd=ROOT,
        input="\n".join(json.dumps(message) if not isinstance(message, str) else message for message in messages) + "\n",
        text=True, capture_output=True, check=False,
    )
    if process.returncode:
        raise AssertionError(process.stdout + process.stderr)
    return [json.loads(line) for line in process.stdout.splitlines() if line]


class GenericAdapterTests(unittest.TestCase):
    def prepare(self, project: pathlib.Path) -> None:
        subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project", "--target", str(project), "--source-root", str(ROOT)], cwd=ROOT, check=True, capture_output=True, text=True)
        subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "install-addon", "--project-root", str(project), "--addon", "runtime-conformance-kit", "--source-root", str(ROOT)], cwd=ROOT, check=True, capture_output=True, text=True)

    def test_generic_client_passes_discovery_negotiation_and_bounded_capsule(self):
        with tempfile.TemporaryDirectory() as temp:
            project = pathlib.Path(temp) / "host"
            self.prepare(project)
            (project / ".owledge" / "indexes").mkdir(exist_ok=True)
            (project / ".owledge" / "indexes" / "memory-index.jsonl").write_text('{"id":"one"}\n', encoding="utf-8")
            responses = run_server(project, [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "owledge_capability_discovery", "arguments": {}}},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "owledge_negotiate_capability", "arguments": {"capability_id": "context.read", "scope": "project_user", "permissions": ["read_project"]}}},
                {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "owledge_preplan_capsule", "arguments": {}}},
                {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "owledge_candidate_boundary", "arguments": {}}},
            ])
            tools = {item["name"] for item in next(row for row in responses if row["id"] == 2)["result"]["tools"]}
            self.assertEqual(tools, {"owledge_capability_discovery", "owledge_negotiate_capability", "owledge_preplan_capsule", "owledge_candidate_boundary"})
            negotiated = json.loads(next(row for row in responses if row["id"] == 4)["result"]["content"][0]["text"])
            capsule = json.loads(next(row for row in responses if row["id"] == 5)["result"]["content"][0]["text"])
            boundary = json.loads(next(row for row in responses if row["id"] == 6)["result"]["content"][0]["text"])
            self.assertEqual(negotiated["result"], "supported")
            self.assertEqual(capsule["loaded_sources"], ["OWLEDGE.md", ".owledge/indexes/memory-index.jsonl"])
            self.assertFalse(capsule["automatic_preplan_inspection"])
            self.assertEqual((boundary["result"], boundary["write_enabled"]), ("unsupported", False))

    def test_malformed_unknown_and_project_mismatch_requests_are_structured_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            project = pathlib.Path(temp) / "host"
            self.prepare(project)
            responses = run_server(project, [
                "not-json",
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "unknown", "arguments": {}}},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "owledge_negotiate_capability", "arguments": {"capability_id": "context.read", "scope": "enterprise", "permissions": ["read_project"]}}},
            ])
            self.assertEqual(len(responses), 3)
            self.assertIn("malformed_json_rpc", responses[0]["error"]["message"])
            self.assertIn("tool_mismatch", responses[1]["error"]["message"])
            receipt = json.loads(responses[2]["result"]["content"][0]["text"])
            self.assertEqual((receipt["result"], receipt["reason_code"]), ("denied", "scope_unsupported"))


if __name__ == "__main__":
    unittest.main()
