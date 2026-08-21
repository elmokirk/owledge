from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_TOOLS = {
    "owledge_capabilities",
    "owledge_recall",
    "owledge_context",
    "owledge_propose",
    "owledge_review",
}


class V1M10CandidateJourneyTests(unittest.TestCase):
    def _run(self, args: list[str], *, expected_returncode: int = 0, input_text: str | None = None) -> dict:
        process = subprocess.run(
            args,
            cwd=ROOT,
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(process.returncode, expected_returncode, process.stdout + process.stderr)
        return json.loads(process.stdout)

    def _init_full(self, project: pathlib.Path, global_root: pathlib.Path) -> None:
        result = self._run([
            sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project",
            "--target", str(project), "--source-root", str(ROOT), "--profile", "full",
            "--link-global", str(global_root), "--owner-id", "v1m10-owner",
        ])
        self.assertNotIn("error", result)

    def _host_cli(self, project: pathlib.Path, *arguments: str) -> dict:
        return self._run([
            sys.executable, str(project / "tools" / "owledge.py"), *arguments,
            "--project-root", str(project),
        ])

    def _generic_call(self, project: pathlib.Path, message: dict) -> dict:
        response = self._run(
            [sys.executable, str(project / "tools" / "owledge_generic_adapter.py"), "--project-root", str(project)],
            input_text=json.dumps(message) + "\n",
        )
        return response

    def test_daily_journey_proves_cross_project_reuse_park_resurface_and_stateless_bridges(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m10-") as temporary:
            base = pathlib.Path(temporary)
            project_a, project_b, global_root = base / "project-a", base / "project-b", base / "null-space"

            minimal = self._run([
                sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project",
                "--target", str(project_a), "--source-root", str(ROOT), "--profile", "minimal",
            ])
            self.assertEqual(minimal["profile"], "minimal")
            self.assertFalse((project_a / "tools").exists())

            self._init_full(project_a, global_root)
            self._init_full(project_b, global_root)
            addon = self._run([
                sys.executable, str(ROOT / "tools" / "owledge.py"), "install-addon",
                "--project-root", str(project_b), "--addon", "runtime-conformance-kit", "--source-root", str(ROOT),
            ])
            self.assertTrue(addon["passed"])

            research = "v1m10 reviewed research reuse"
            proposed = self._host_cli(project_a, "propose", "--kind", "research", "--summary", research, "--source-ref", "research:local-v1m10")
            self.assertTrue(proposed["passed"])
            promoted = self._host_cli(
                project_a, "review", "--candidate-id", proposed["receipt_id"], "--action", "promote",
                "--expected-revision", proposed["candidate_revision"],
            )
            self.assertTrue(promoted["passed"])

            # Each bridge begins as a fresh process and receives only the project-local Core state.
            codex_recall = self._host_cli(project_b, "recall", "--query", research, "--scope", "user_global", "--include-user-global")
            claude_context = self._host_cli(project_b, "context", "--task-id", "v1m10", "--objective", research, "--include-reviewed-global", "--budget-chars", "320")
            self.assertEqual(codex_recall["results"][0]["scope"], "user_global")
            self.assertEqual(claude_context["source_receipts"][0]["source"], codex_recall["results"][0]["source"])

            generic_list = self._generic_call(project_b, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
            self.assertEqual({item["name"] for item in generic_list["result"]["tools"]}, EXPECTED_TOOLS)
            generic_recall = self._generic_call(project_b, {
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "owledge_recall", "arguments": {"query": research, "scopes": ["user_global"], "include_user_global": True}},
            })
            generic_body = json.loads(generic_recall["result"]["content"][0]["text"])
            self.assertEqual(generic_body["results"][0]["source"], codex_recall["results"][0]["source"])
            self.assertEqual(generic_body["results"][0]["instruction_provenance"]["execution"], "never_auto_execute")

            parked_summary = "v1m10 deferred feature idea"
            parked = self._host_cli(
                project_b, "propose", "--kind", "idea", "--summary", parked_summary,
                "--source-ref", "idea:v1m10", "--park", "--park-reason", "not in the current MVP",
                "--reconsider-when", "when local user-global workflow needs it",
            )
            self.assertEqual(parked["lifecycle"], "parked")
            ordinary = self._host_cli(project_b, "recall", "--query", parked_summary)
            planning = self._host_cli(project_b, "recall", "--query", parked_summary, "--purpose", "planning")
            self.assertFalse(ordinary["results"])
            self.assertEqual(planning["results"][0]["lifecycle"], "parked")
            self.assertEqual(planning["results"][0]["park_reason"], "not in the current MVP")
            self.assertEqual(planning["results"][0]["reconsider_when"], "when local user-global workflow needs it")

    def test_public_claims_keep_v1_local_and_platform_bounded(self) -> None:
        candidate_doc = (ROOT / "docs" / "v1-minimal-core.md").read_text(encoding="utf-8")
        matrix = (ROOT / "docs" / "harness-plugin-matrix.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        registry = json.loads((ROOT / "contracts" / "public-capabilities.json").read_text(encoding="utf-8"))
        capabilities = {item["id"]: item for item in registry["capabilities"]}

        self.assertIn("exactly eight public CLI operations", candidate_doc)
        self.assertIn("exactly five MCP tools", candidate_doc)
        self.assertIn("macOS/Linux support", candidate_doc)
        self.assertIn("not an announcement that a package has been published", candidate_doc)
        self.assertIn("Generic MCP/CLI | V1 reference adapter", matrix)
        self.assertIn("Cowork / Claude-compatible | Post-V1/legacy add-on", matrix)
        self.assertIn("V1 boundary", readme)
        self.assertNotIn("Owledge ships a read-only MCP surface in v0.8.0", readme)
        self.assertEqual(capabilities["generic-mcp-cli-core-bridge"]["maturity"], "available")
        self.assertEqual(capabilities["cross-project-hub-kit"]["maturity"], "post-v1")
        self.assertEqual(capabilities["private-global-layer"]["maturity"], "available")
        self.assertIn('license = "MIT"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
