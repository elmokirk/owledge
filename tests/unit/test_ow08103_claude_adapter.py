from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins" / "owledge-cowork"
FIXTURES = PLUGIN / "tests" / "fixtures"


class ClaudeAdapterTests(unittest.TestCase):
    def test_fixture_matches_local_lifecycle_and_bounded_capsule_contract(self):
        fixture = json.loads((FIXTURES / "claude-code-tier1-conformance.json").read_text(encoding="utf-8"))
        hooks = json.loads((PLUGIN / "hooks" / "hooks.python.json").read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(fixture["profile"], "claude-code")
        self.assertTrue(all(name in hooks for name in fixture["lifecycle"]))
        self.assertEqual(fixture["context_capsule"]["sources"], ["OWLEDGE.md", ".owledge/indexes/memory-index.jsonl"])
        self.assertFalse(fixture["context_capsule"]["automatic_preplan_inspection"])
        self.assertEqual(fixture["handoff"]["persistence"], "core_owned")
        self.assertFalse(fixture["handoff"]["raw_transcript_promotion"])

    def test_bad_stop_payload_is_logged_and_never_claims_success(self):
        with tempfile.TemporaryDirectory() as temp:
            host = pathlib.Path(temp) / "host"
            init = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project", "--target", str(host),
                 "--include-plugin-adapter", "--source-root", str(ROOT)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            close = host / "plugins" / "owledge-cowork" / "scripts" / "close-runtime-session.py"
            result = subprocess.run([sys.executable, str(close)], cwd=host, input="{}", text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            error_log = host / ".agent-control" / "logs" / "plugin-errors.jsonl"
            self.assertTrue(error_log.is_file())
            rows = [json.loads(line) for line in error_log.read_text(encoding="utf-8").splitlines()]
            self.assertTrue(any("session_id" in row["message"] for row in rows))
            self.assertFalse((host / ".owledge" / "sessions" / "unknown" / "summary.md").exists())

    def test_installed_profile_negotiates_shared_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            host = pathlib.Path(temp) / "host"
            subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project", "--target", str(host), "--include-plugin-adapter", "--source-root", str(ROOT)], cwd=ROOT, capture_output=True, text=True, check=True)
            subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "install-addon", "--project-root", str(host), "--addon", "runtime-conformance-kit", "--source-root", str(ROOT)], cwd=ROOT, capture_output=True, text=True, check=True)
            command = [sys.executable, str(host / "tools" / "owledge_adapter_contracts.py"), "negotiate", "--manifest", str(host / ".owledge" / "runtime-conformance" / "claude-code.json"), "--capability", "checkpoint.handoff", "--scope", "project_user", "--permission", "read_project"]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["result"], "supported")


if __name__ == "__main__":
    unittest.main()
