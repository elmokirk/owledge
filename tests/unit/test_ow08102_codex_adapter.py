from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins" / "owledge-cowork"


class CodexAdapterTests(unittest.TestCase):
    def test_project_local_bootstrap_discovers_skill_and_passes_codex_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            project = pathlib.Path(temp)
            init = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project", "--target", str(project),
                 "--source-root", str(ROOT)], cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            self.assertTrue((project / "AGENTS.md").is_file())
            self.assertTrue((project / ".agents" / "skills" / "owledge-runtime-bridge" / "SKILL.md").is_file())
            self.assertFalse((project / ".owledge" / "skills").exists())
            installed = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "owledge.py"), "install-addon", "--project-root", str(project),
                 "--addon", "runtime-conformance-kit", "--source-root", str(ROOT)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            negotiated = subprocess.run(
                [sys.executable, str(project / "tools" / "owledge_adapter_contracts.py"), "negotiate",
                 "--manifest", str(project / ".owledge" / "runtime-conformance" / "codex.json"),
                 "--capability", "context.read", "--scope", "project_user", "--permission", "read_project"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(negotiated.returncode, 0, negotiated.stdout + negotiated.stderr)
            self.assertEqual(json.loads(negotiated.stdout)["result"], "supported")

    def test_fixture_declares_bounded_owner_invocation_and_visible_missing_hook(self):
        fixture = json.loads((PLUGIN / "tests" / "fixtures" / "codex-tier1-conformance.json").read_text(encoding="utf-8"))
        adapter = json.loads((PLUGIN / ".codex-plugin" / "adapter-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(fixture["context_capsule"]["sources"], ["OWLEDGE.md", ".owledge/indexes/memory-index.jsonl"])
        self.assertEqual(fixture["context_capsule"]["max_sources"], 2)
        self.assertFalse(fixture["context_capsule"]["automatic_preplan_inspection"])
        self.assertEqual(fixture["hooks"]["result"], "unsupported")
        self.assertEqual(adapter["hook_capability"], fixture["hooks"])
        self.assertEqual(adapter["discovery_root"], ".agents/skills")
        self.assertEqual(adapter["storage_boundary"], "core_owned_no_direct_storage_access")
        self.assertTrue((PLUGIN / ".codex-plugin" / adapter["adapter_manifest"]).resolve().is_file())


if __name__ == "__main__":
    unittest.main()
