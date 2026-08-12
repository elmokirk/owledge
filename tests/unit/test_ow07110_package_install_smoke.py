from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
GOLDEN_DEMO_SEED = ROOT / "examples" / "vibecoding-golden-demo" / "seed"
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
    environment = os.environ.copy()
    environment.pop("PYTHONHOME", None)
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env=environment,
    )
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
            module_path = run(
                [str(python), "-c", "import pathlib, tools.owledge; print(pathlib.Path(tools.owledge.__file__).resolve())"],
                cwd=temporary_root,
            )

            quickstart = run([str(cli), "quickstart", "--target", str(target)], cwd=temporary_root)
            doctor = run([str(cli), "doctor", "--project-root", str(target), "--mode", "host"], cwd=temporary_root)

            self.assertTrue((target / "OWLEDGE.md").is_file())
            self.assertTrue((target / ".owledge").is_dir())
            self.assertTrue(pathlib.Path(module_path.stdout.strip()).is_relative_to(environment.resolve()))
            self.assertTrue(json.loads(quickstart.stdout)["passed"])
            self.assertTrue(json.loads(doctor.stdout)["passed"])

    def test_wheel_only_golden_demo_resumes_without_a_runtime_or_checkout(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ow07105-wheel-") as temporary:
            temporary_root = pathlib.Path(temporary)
            source_copy = temporary_root / "source"
            wheel_dir = temporary_root / "wheel"
            environment = temporary_root / "venv"
            target = temporary_root / "host-project"

            copy_package_source(source_copy)
            run(
                [sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", str(wheel_dir), str(source_copy)],
                cwd=temporary_root,
            )
            wheel = next(wheel_dir.glob("owledge-*.whl"))
            shutil.rmtree(source_copy)
            run([sys.executable, "-m", "venv", str(environment)], cwd=temporary_root)
            python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
            cli = environment / ("Scripts/owledge.exe" if sys.platform == "win32" else "bin/owledge")
            run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)], cwd=temporary_root)

            first = run([str(cli), "quickstart", "--target", str(target)], cwd=temporary_root)
            for name, relative in {
                "filter-request.md": pathlib.Path(".owledge/canonical/filter-request.md"),
                "filter-request-check.md": pathlib.Path(".owledge/evidence/filter-request-check.md"),
                "filter-request-resume.md": pathlib.Path(".owledge/handoffs/filter-request-resume.md"),
            }.items():
                destination = target / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(GOLDEN_DEMO_SEED / name, destination)

            second = run([str(cli), "quickstart", "--target", str(target)], cwd=temporary_root)
            doctor = run([str(cli), "doctor", "--project-root", str(target), "--mode", "host"], cwd=temporary_root)
            context = run(
                [
                    str(cli), "build-context-pack", "--project-root", str(target),
                    "--task-id", "filter-request", "--agent-role", "worker",
                    "--objective", "Verify the completed-item filter without widening scope",
                ],
                cwd=temporary_root,
            )

            handoff = (target / ".owledge/handoffs/filter-request-resume.md").read_text(encoding="utf-8")
            evidence = (target / ".owledge/evidence/filter-request-check.md").read_text(encoding="utf-8")
            request = (target / ".owledge/canonical/filter-request.md").read_text(encoding="utf-8")
            self.assertTrue(json.loads(first.stdout)["passed"])
            self.assertTrue(json.loads(second.stdout)["init"]["skipped_existing"])
            self.assertTrue(json.loads(doctor.stdout)["passed"])
            self.assertIn("filter-request.md", json.loads(context.stdout)["content"])
            self.assertNotIn("plugins", {path.name for path in target.iterdir()})
            self.assertIn("without changing stored data", request)
            self.assertIn("Unfinished item remains visible", evidence)
            self.assertIn("Completed item is hidden", evidence)
            self.assertIn("Stored items are unchanged", evidence)
            self.assertIn("Do not infer sync, deletion, or account work", handoff)


if __name__ == "__main__":
    unittest.main()
