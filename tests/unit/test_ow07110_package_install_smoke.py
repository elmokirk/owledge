from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PACKAGE_ROOT_FILES = (
    "pyproject.toml",
    "README.md",
    "OWLEDGE.template.md",
    "AGENTS.template.md",
    "CLAUDE.template.md",
    "USER_CONTEXT.template.md",
    "DESIGN.md",
    "REPORT_DESIGN_SELECTOR.html",
    ".gitignore",
    "VERSION",
    "CHANGELOG.md",
)


def copy_package_source(destination: pathlib.Path) -> None:
    destination.mkdir()
    for name in PACKAGE_ROOT_FILES:
        shutil.copy2(ROOT / name, destination / name)
    for directory in ("templates", "skills", "standalone-skills"):
        shutil.copytree(ROOT / directory, destination / directory)
    tools = destination / "tools"
    tools.mkdir()
    for source in (ROOT / "tools").glob("*.py"):
        shutil.copy2(source, tools / source.name)
    docs = destination / "docs"
    docs.mkdir()
    shutil.copy2(ROOT / "docs" / "upgrade-notes-schema.json", docs / "upgrade-notes-schema.json")


def run(command: list[str], *, cwd: pathlib.Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise AssertionError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


class OW07110PackageInstallSmokeTests(unittest.TestCase):
    def test_wheel_only_quickstart_and_doctor_do_not_need_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ow07110-wheel-") as temporary:
            temporary_root = pathlib.Path(temporary)
            source_copy = temporary_root / "source"
            wheel_dir = temporary_root / "wheel"
            environment = temporary_root / "venv"
            target = temporary_root / "host-project"

            copy_package_source(source_copy)
            run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "wheel",
                    "--no-deps",
                    "--wheel-dir",
                    str(wheel_dir),
                    str(source_copy),
                ],
                cwd=temporary_root,
            )
            wheels = sorted(wheel_dir.glob("owledge-*.whl"))
            self.assertEqual(1, len(wheels), "wheel build must produce exactly one Owledge wheel")

            shutil.rmtree(source_copy)
            run([sys.executable, "-m", "venv", str(environment)], cwd=temporary_root)
            python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
            cli = environment / ("Scripts/owledge.exe" if sys.platform == "win32" else "bin/owledge")
            run([str(python), "-m", "pip", "install", "--no-deps", str(wheels[0])], cwd=temporary_root)

            quickstart = run([str(cli), "quickstart", "--target", str(target)], cwd=temporary_root)
            doctor = run([str(cli), "doctor", "--project-root", str(target), "--mode", "host"], cwd=temporary_root)

            self.assertTrue((target / "OWLEDGE.md").is_file())
            self.assertTrue((target / ".owledge").is_dir())
            self.assertTrue(json.loads(quickstart.stdout)["passed"])
            self.assertTrue(json.loads(doctor.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
