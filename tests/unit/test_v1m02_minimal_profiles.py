from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
CLI = ROOT / "tools" / "owledge.py"


def run_cli(*args: str) -> dict:
    result = subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"CLI failed: {result.stderr}\n{result.stdout}")
    return json.loads(result.stdout)


class V1M02MinimalProfileTests(unittest.TestCase):
    def test_default_minimal_profile_is_within_budget_and_uses_no_copied_schema_or_tool(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m02-") as temporary:
            target = pathlib.Path(temporary) / "project"
            result = run_cli("init-project", "--target", str(target))
            files = [path for path in target.rglob("*") if path.is_file()]
            directories = [path for path in target.rglob("*") if path.is_dir()]
            self.assertEqual(result["profile"], "minimal")
            self.assertLessEqual(len(files), 15)
            self.assertLessEqual(len(directories), 8)
            self.assertTrue((target / "OWLEDGE.md").is_file())
            self.assertTrue((target / ".owledge" / "config.yaml").is_file())
            self.assertFalse((target / "tools").exists())
            self.assertFalse((target / ".owledge" / "schemas").exists())
            doctor = run_cli("doctor", "--project-root", str(target))
            self.assertTrue(doctor["passed"])
            self.assertEqual(doctor["user_edited_files"], [])

    def test_principles_profile_is_zero_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m02-") as temporary:
            target = pathlib.Path(temporary) / "absent-project"
            result = run_cli("init-project", "--target", str(target), "--profile", "principles")
            self.assertEqual(result["created"], [])
            self.assertFalse(target.exists())

    def test_full_profile_remains_explicit_and_minimal_upgrade_preserves_user_router(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m02-") as temporary:
            target = pathlib.Path(temporary) / "project"
            full = run_cli("init-project", "--target", str(target), "--profile", "full")
            self.assertEqual(full["profile"], "full")
            self.assertTrue((target / "tools" / "owledge.py").is_file())
            router = target / "OWLEDGE.md"
            router.write_text("# user-owned router\n", encoding="utf-8")
            report = run_cli("upgrade", "--project-root", str(target), "--source-root", str(ROOT), "--apply", "--mode", "safe")
            self.assertTrue(report["passed"])
            self.assertEqual(router.read_text(encoding="utf-8"), "# user-owned router\n")


if __name__ == "__main__":
    unittest.main()
