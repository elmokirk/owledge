from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVER = ROOT / "tools" / "owledge_generic_adapter.py"


def run_server(project: pathlib.Path, messages: list[object], *, server: pathlib.Path = SERVER, manifest: pathlib.Path | None = None) -> list[dict]:
    command = [sys.executable, str(server), "--project-root", str(project)]
    if manifest is not None:
        command.extend(["--manifest", str(manifest)])
    process = subprocess.run(
        command, cwd=ROOT,
        input="\n".join(json.dumps(message) if not isinstance(message, str) else message for message in messages) + "\n",
        text=True, capture_output=True, check=False,
    )
    if process.returncode:
        raise AssertionError(process.stdout + process.stderr)
    return [json.loads(line) for line in process.stdout.splitlines() if line]


class GenericAdapterTests(unittest.TestCase):
    def prepare(self, project: pathlib.Path) -> None:
        subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project", "--target", str(project), "--source-root", str(ROOT), "--profile", "full"], cwd=ROOT, check=True, capture_output=True, text=True)
        subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "install-addon", "--project-root", str(project), "--addon", "runtime-conformance-kit", "--source-root", str(ROOT)], cwd=ROOT, check=True, capture_output=True, text=True)

    def test_generic_client_exposes_exactly_five_core_delegations(self):
        with tempfile.TemporaryDirectory() as temp:
            project = pathlib.Path(temp) / "host"
            self.prepare(project)
            responses = run_server(project, [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "owledge_capabilities", "arguments": {}}},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "owledge_propose", "arguments": {"kind": "idea", "summary": "zephyrquartz unlisted lifecycle note", "source_refs": ["plan:v1m08"]}}},
                {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "owledge_recall", "arguments": {"query": "zephyrquartz"}}},
                {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "owledge_context", "arguments": {"task_id": "zephyrquartz", "objective": "candidate", "budget_chars": 40}}},
            ], server=project / "tools" / "owledge_generic_adapter.py")
            tools = {item["name"] for item in next(row for row in responses if row["id"] == 2)["result"]["tools"]}
            self.assertEqual(tools, {"owledge_capabilities", "owledge_recall", "owledge_context", "owledge_propose", "owledge_review"})
            capabilities = json.loads(next(row for row in responses if row["id"] == 3)["result"]["content"][0]["text"])
            proposed = json.loads(next(row for row in responses if row["id"] == 4)["result"]["content"][0]["text"])
            recalled = json.loads(next(row for row in responses if row["id"] == 5)["result"]["content"][0]["text"])
            context = json.loads(next(row for row in responses if row["id"] == 6)["result"]["content"][0]["text"])
            self.assertEqual(capabilities["mcp_tools"], ["capabilities", "recall", "context", "propose", "review"])
            self.assertTrue(proposed["passed"])
            self.assertFalse(recalled["results"])
            self.assertLessEqual(context["included_chars"], 40)
            reviewed = run_server(project, [
                {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "owledge_review", "arguments": {"candidate_id": proposed["receipt_id"], "action": "promote", "expected_revision": proposed["candidate_revision"]}}},
            ], server=project / "tools" / "owledge_generic_adapter.py")
            review_receipt = json.loads(reviewed[0]["result"]["content"][0]["text"])
            self.assertEqual(review_receipt["error"], "unlinked_project")

    def test_malformed_unknown_and_project_mismatch_requests_are_structured_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            project = pathlib.Path(temp) / "host"
            self.prepare(project)
            responses = run_server(project, [
                "not-json",
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "unknown", "arguments": {}}},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "owledge_recall", "arguments": {"query": "local", "scopes": ["enterprise"]}}},
            ])
            self.assertEqual(len(responses), 3)
            self.assertIn("malformed_json_rpc", responses[0]["error"]["message"])
            self.assertIn("tool_mismatch", responses[1]["error"]["message"])
            receipt = json.loads(responses[2]["result"]["content"][0]["text"])
            self.assertEqual(receipt["error"], "scope_unsupported")

    def test_external_or_incompatible_manifest_override_is_rejected_before_serving(self):
        with tempfile.TemporaryDirectory() as temp:
            project = pathlib.Path(temp) / "host"
            self.prepare(project)
            external = pathlib.Path(temp) / "generic.json"
            source = project / ".owledge" / "runtime-conformance" / "generic-mcp-cli.json"
            payload = json.loads(source.read_text(encoding="utf-8"))
            payload["core_api_range"] = ">=9.0.0,<10.0.0"
            external.write_text(json.dumps(payload), encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(project / "tools" / "owledge_generic_adapter.py"), "--project-root", str(project), "--manifest", str(external)],
                cwd=ROOT, input="", text=True, capture_output=True, check=False,
            )
            self.assertEqual(process.returncode, 2)
            self.assertIn("manifest_override_denied", process.stderr)
            source.write_text(json.dumps(payload), encoding="utf-8")
            incompatible = subprocess.run(
                [sys.executable, str(project / "tools" / "owledge_generic_adapter.py"), "--project-root", str(project)],
                cwd=ROOT, input="", text=True, capture_output=True, check=False,
            )
            self.assertEqual(incompatible.returncode, 2)
            self.assertIn("core_api_incompatible", incompatible.stderr)


if __name__ == "__main__":
    unittest.main()
