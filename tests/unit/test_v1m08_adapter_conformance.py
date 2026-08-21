from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_adapter_contracts as contracts


PROFILES = ("codex", "claude-code", "generic-mcp-cli")
EXPECTED_MCP_TOOLS = {"owledge_capabilities", "owledge_recall", "owledge_context", "owledge_propose", "owledge_review"}
EXPECTED_CORE_OPERATIONS = ["capabilities", "recall", "context", "propose", "review"]


class V1M08AdapterConformanceTests(unittest.TestCase):
    def _prepare_full_host(self, project: pathlib.Path) -> None:
        initialized = subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project", "--target", str(project), "--source-root", str(ROOT), "--profile", "full"], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
        addon = subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "install-addon", "--project-root", str(project), "--addon", "runtime-conformance-kit", "--source-root", str(ROOT)], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(addon.returncode, 0, addon.stdout + addon.stderr)

    def _run_cli(self, project: pathlib.Path, *arguments: str, expected_returncode: int = 0) -> dict:
        result = subprocess.run([sys.executable, str(project / "tools" / "owledge.py"), *arguments, "--project-root", str(project)], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, expected_returncode, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def _assert_cli_lifecycle_journey(self, project: pathlib.Path, profile: str) -> None:
        query = f"v1m08-{profile}-candidate"
        proposed = self._run_cli(project, "propose", "--kind", "idea", "--summary", query, "--source-ref", "plan:v1m08")
        self.assertTrue(proposed["passed"])
        recalled = self._run_cli(project, "recall", "--query", query)
        self.assertFalse(recalled["results"])
        context = self._run_cli(project, "context", "--task-id", query, "--objective", "adapter journey", "--budget-chars", "40")
        self.assertLessEqual(context["included_chars"], 40)
        review = self._run_cli(project, "review", "--candidate-id", proposed["receipt_id"], "--action", "promote", "--expected-revision", proposed["candidate_revision"], expected_returncode=2)
        self.assertEqual(review["error"], "unlinked_project")

    def _generic_call(self, project: pathlib.Path, messages: list[dict]) -> list[dict]:
        result = subprocess.run([sys.executable, str(project / "tools" / "owledge_generic_adapter.py"), "--project-root", str(project)], input="\n".join(json.dumps(message) for message in messages) + "\n", cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return [json.loads(line) for line in result.stdout.splitlines() if line]

    def test_three_profiles_reuse_one_local_contract_with_identical_boundaries(self) -> None:
        contracts_dir = ROOT / "addons" / "runtime-conformance-kit" / "contracts"
        manifests = [json.loads((contracts_dir / f"{profile}.json").read_text(encoding="utf-8")) for profile in PROFILES]
        for manifest in manifests:
            self.assertFalse(contracts.validate_adapter_manifest(manifest))
            self.assertEqual(manifest["context_scopes"], ["project_user", "user_global"])
            self.assertEqual(manifest["granted_permissions"], ["read_project", "read_user_global", "write_candidate"])
        self.assertEqual({tuple(manifest["supported_capabilities"]) for manifest in manifests}, {("context.read", "control.read", "checkpoint.handoff", "candidate.write")})
        self.assertEqual({json.dumps(manifest["unsupported_capabilities"], sort_keys=True) for manifest in manifests}, {json.dumps(manifests[0]["unsupported_capabilities"], sort_keys=True)})

    def test_generic_adapter_has_exactly_five_tools_and_no_direct_storage_primitives(self) -> None:
        adapter = ROOT / "tools" / "owledge_generic_adapter.py"
        source = adapter.read_text(encoding="utf-8")
        self.assertNotIn("write_text(", source)
        self.assertNotIn("mkdir(", source)
        self.assertNotIn("rglob(", source)
        with tempfile.TemporaryDirectory(prefix="v1m08-") as temporary:
            project = pathlib.Path(temporary) / "host"
            self._prepare_full_host(project)
            listed = subprocess.run([sys.executable, str(project / "tools" / "owledge_generic_adapter.py"), "--project-root", str(project)], input=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\n", cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(listed.returncode, 0, listed.stderr)
            response = json.loads(listed.stdout)
            self.assertEqual({item["name"] for item in response["result"]["tools"]}, EXPECTED_MCP_TOOLS)

    def test_three_adapter_bridges_complete_the_same_candidate_lifecycle_journey(self) -> None:
        plugin = ROOT / "plugins" / "owledge-cowork"
        codex = json.loads((plugin / ".codex-plugin" / "adapter-manifest.json").read_text(encoding="utf-8"))
        claude = json.loads((plugin / "tests" / "fixtures" / "claude-code-tier1-conformance.json").read_text(encoding="utf-8"))
        for profile, declaration in (("codex", codex), ("claude-code", claude)):
            self.assertEqual(declaration["v1_core_bridge"], {"type": "project_local_cli", "operations": EXPECTED_CORE_OPERATIONS})
            with tempfile.TemporaryDirectory(prefix=f"v1m08-{profile}-") as temporary:
                project = pathlib.Path(temporary) / "host"
                self._prepare_full_host(project)
                self._assert_cli_lifecycle_journey(project, profile)
        with tempfile.TemporaryDirectory(prefix="v1m08-generic-") as temporary:
            project = pathlib.Path(temporary) / "host"
            self._prepare_full_host(project)
            query = "v1m08-generic-candidate"
            messages = self._generic_call(project, [
                {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "owledge_propose", "arguments": {"kind": "idea", "summary": query, "source_refs": ["plan:v1m08"]}}},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "owledge_recall", "arguments": {"query": query}}},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "owledge_context", "arguments": {"task_id": query, "objective": "adapter journey", "budget_chars": 40}}},
            ])
            self.assertEqual({item["name"] for item in messages[0]["result"]["tools"]}, EXPECTED_MCP_TOOLS)
            proposed = json.loads(messages[1]["result"]["content"][0]["text"])
            recalled = json.loads(messages[2]["result"]["content"][0]["text"])
            context = json.loads(messages[3]["result"]["content"][0]["text"])
            self.assertTrue(proposed["passed"])
            self.assertFalse(recalled["results"])
            self.assertLessEqual(context["included_chars"], 40)
            review = self._generic_call(project, [{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "owledge_review", "arguments": {"candidate_id": proposed["receipt_id"], "action": "promote", "expected_revision": proposed["candidate_revision"]}}}])
            self.assertEqual(json.loads(review[0]["result"]["content"][0]["text"])["error"], "unlinked_project")

    def test_codex_and_claude_fixtures_route_all_core_work_to_project_local_cli(self) -> None:
        plugin = ROOT / "plugins" / "owledge-cowork"
        codex = json.loads((plugin / ".codex-plugin" / "adapter-manifest.json").read_text(encoding="utf-8"))
        claude = json.loads((plugin / "tests" / "fixtures" / "claude-code-tier1-conformance.json").read_text(encoding="utf-8"))
        self.assertEqual(codex["storage_boundary"], "core_owned_no_direct_storage_access")
        self.assertEqual(codex["v1_core_bridge"]["operations"], EXPECTED_CORE_OPERATIONS)
        self.assertEqual(codex["routing"]["context_and_handoff"], "owner_invoked_project_local_cli")
        self.assertEqual(claude["handoff"]["persistence"], "core_owned")
        self.assertEqual(claude["v1_core_bridge"]["operations"], EXPECTED_CORE_OPERATIONS)
        self.assertFalse(claude["handoff"]["raw_transcript_promotion"])

    def test_generic_conformance_fixture_describes_only_core_delegation(self) -> None:
        fixture = json.loads((ROOT / "addons" / "runtime-conformance-kit" / "fixtures" / "generic-mcp-cli-tier1.json").read_text(encoding="utf-8"))
        self.assertEqual(set(fixture["required_tools"]), EXPECTED_MCP_TOOLS)
        self.assertEqual(fixture["core_delegation"]["context"], "bounded_receipt_from_project_local_core")
        self.assertNotIn("context_capsule", fixture)


if __name__ == "__main__":
    unittest.main()
