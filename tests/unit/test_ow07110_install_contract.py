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
    result = subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"CLI failed ({result.returncode}): {result.stderr}\n{result.stdout}")
    return json.loads(result.stdout)


class OW07110InstallContractTests(unittest.TestCase):
    def test_source_recipe_is_additive_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ow07110-") as temporary:
            target = pathlib.Path(temporary) / "project"
            first = run_cli("init-project", "--target", str(target))
            doctor = run_cli("doctor", "--project-root", str(target))
            second = run_cli("init-project", "--target", str(target))

            self.assertTrue(first["doctor_passed"])
            self.assertTrue(doctor["passed"])
            self.assertTrue((target / "OWLEDGE.md").is_file())
            self.assertTrue((target / ".owledge").is_dir())
            self.assertIn("OWLEDGE.md", second["skipped_existing"])

    def test_documented_delivery_boundaries_do_not_mix(self) -> None:
        project = (ROOT / "docs" / "install" / "project.md").read_text(encoding="utf-8")
        package = project.split("## Source recipe", 1)[0]
        source = project.split("## Source recipe", 1)[1]
        self.assertIn("uvx owledge quickstart", package)
        self.assertIn("uvx owledge doctor", package)
        self.assertNotIn("install-addon", package)
        self.assertIn("python tools/owledge.py init-project", source)
        self.assertIn("python tools/owledge.py install-addon", source)
        self.assertIn("source checkout", source.lower())

    def test_principles_only_has_no_host_install_commands(self) -> None:
        principles = (ROOT / "docs" / "install" / "principles-only.md").read_text(encoding="utf-8")
        self.assertIn("Host-project writes: **zero**", principles)
        self.assertNotIn("```bash", principles)


if __name__ == "__main__":
    unittest.main()
