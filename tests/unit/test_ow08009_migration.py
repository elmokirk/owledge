from __future__ import annotations
import json
import pathlib
import sys
import tempfile
import unittest
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_migration as migration  # noqa: E402

class MigrationTests(unittest.TestCase):
    def host(self):
        temp = tempfile.TemporaryDirectory(); root = pathlib.Path(temp.name) / "host"; source = pathlib.Path(temp.name) / "source"; root.mkdir(); (source / "tools").mkdir(parents=True); (root / "tools").mkdir()
        target = root / "tools" / "tool.py"; src = source / "tools" / "tool.py"; target.write_text("old", encoding="utf-8"); src.write_text("new", encoding="utf-8")
        (root / "kit-manifest.json").write_text(json.dumps({"files": [{"path": "tools/tool.py", "sha256_original": migration.digest(target)}]}), encoding="utf-8")
        return temp, root, source, target
    def test_preview_lists_writes_without_mutation_and_apply_is_idempotent(self):
        temp, root, source, target = self.host()
        with temp:
            plan = migration.preview(root, source); self.assertTrue(plan["passed"]); self.assertEqual(target.read_text(), "old")
            applied = migration.apply(root, source, plan); self.assertTrue(applied["passed"]); self.assertEqual(target.read_text(), "new")
            self.assertTrue(migration.apply(root, source, plan)["idempotent"])
    def test_collision_and_failed_postflight_recover(self):
        temp, root, source, target = self.host()
        with temp:
            target.write_text("edited", encoding="utf-8"); plan = migration.preview(root, source); self.assertFalse(plan["passed"]); self.assertEqual(plan["collisions"][0]["reason"], "edited_template_collision")
        temp, root, source, target = self.host()
        with temp:
            plan = migration.preview(root, source); result = migration.apply(root, source, plan, simulate_postflight_failure=True)
            self.assertFalse(result["passed"]); self.assertTrue(result["recovered"]); self.assertEqual(target.read_text(), "old")

    def test_public_cli_requires_explicit_preview_then_plan_apply(self):
        temp, root, source, target = self.host()
        with temp:
            plan = root / ".owledge" / "migrations" / "preview.json"
            command = [sys.executable, str(ROOT / "tools" / "owledge.py"), "migrate", "--project-root", str(root), "--source-root", str(source), "--dry-run", "--output-plan", str(plan)]
            self.assertEqual(subprocess.run(command, capture_output=True, text=True).returncode, 0)
            self.assertEqual(target.read_text(), "old")
            apply = [sys.executable, str(ROOT / "tools" / "owledge.py"), "migrate", "--project-root", str(root), "--source-root", str(source), "--apply", "--plan", str(plan)]
            self.assertEqual(subprocess.run(apply, capture_output=True, text=True).returncode, 0)
            self.assertEqual(target.read_text(), "new")
