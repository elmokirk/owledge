from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_null_space as null_space
import build_project_folder_kit


def write_global_record(root: pathlib.Path, name: str, summary: str) -> None:
    path = root / "reviewed" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"memory_id: mem:user:global:{name[:-3]}\n"
        "knowledge_scope: user_global\n"
        "visibility: private\n"
        f"summary: {summary}\n"
        "---\n\n"
        f"# {summary}\n",
        encoding="utf-8",
    )


class V1M04NullSpaceTests(unittest.TestCase):
    def test_full_kit_copies_the_shared_null_space_boundary(self) -> None:
        self.assertIn("owledge_null_space.py", build_project_folder_kit.CORE_TOOLS)

    def test_cli_rejects_bare_global_link_flag_even_when_environment_is_set(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m04-") as temporary:
            base = pathlib.Path(temporary)
            project, global_root = base / "project", base / "environment-global"
            environment = dict(__import__("os").environ, OWLEDGE_GLOBAL_HOME=str(global_root))
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "owledge.py"), "init", "--target", str(project), "--link-global"],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertFalse((project / null_space.LINK_RELATIVE_PATH).exists())

    def test_network_namespace_is_rejected_before_any_link_io(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m04-") as temporary:
            project = pathlib.Path(temporary) / "project"
            (project / ".owledge").mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "global_root_network_path_denied"):
                null_space.link_project(project, pathlib.Path(r"\\server\share"))

    def test_cli_rejects_network_global_before_creating_the_project(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m04-") as temporary:
            project = pathlib.Path(temporary) / "not-created"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "owledge.py"),
                    "init",
                    "--target",
                    str(project),
                    "--link-global",
                    r"\\server\share",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("link_global_requires_local_path", result.stdout + result.stderr)
            self.assertFalse(project.exists())

    def test_two_explicit_projects_share_only_allowlisted_local_null_space(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m04-") as temporary:
            base = pathlib.Path(temporary)
            global_root = base / "null-space"
            alpha, beta, unlinked = base / "alpha", base / "beta", base / "unlinked"
            for project in (alpha, beta, unlinked):
                (project / ".owledge").mkdir(parents=True)
            first = null_space.link_project(alpha, global_root, owner_id="owner-a")
            second = null_space.link_project(beta, global_root, owner_id="owner-a")
            self.assertEqual(first["scopes"], ["project_user", "user_global"])
            self.assertEqual(second["allowlisted_projects"], 2)
            write_global_record(global_root, "lesson.md", "Prefer explicit local links")
            alpha_scan = null_space.scan_user_global(alpha)
            beta_scan = null_space.scan_user_global(beta)
            project_scan = null_space.scan_user_global(alpha, requested_scope="project_user")
            self.assertTrue(alpha_scan["passed"])
            self.assertEqual(alpha_scan["records"], beta_scan["records"])
            self.assertEqual(alpha_scan["records"][0]["source"], "user_global/reviewed/lesson.md")
            self.assertEqual(project_scan["scope"], "project_user")
            self.assertTrue(all(record["scope"] == "project_user" for record in project_scan["records"]))
            self.assertNotIn(str(global_root), json.dumps(alpha_scan))
            self.assertEqual(null_space.scan_user_global(unlinked)["error"], "unlinked_project")

    def test_direct_scan_and_rebuilt_index_are_equivalent_and_disposable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m04-") as temporary:
            base = pathlib.Path(temporary)
            project, global_root = base / "project", base / "global"
            (project / ".owledge").mkdir(parents=True)
            null_space.link_project(project, global_root)
            write_global_record(global_root, "fact.md", "A reviewed local fact")
            direct = null_space.scan_user_global(project)
            rebuilt = null_space.rebuild_index(project)
            index = project / ".owledge" / "indexes" / "user-global-index.jsonl"
            self.assertTrue(rebuilt["rebuildable"])
            self.assertEqual(direct["records"], rebuilt["records"])
            self.assertEqual([json.loads(line) for line in index.read_text(encoding="utf-8").splitlines()], direct["records"])

    def test_scope_network_registry_and_symlink_escapes_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m04-") as temporary:
            base = pathlib.Path(temporary)
            project, global_root = base / "project", base / "global"
            (project / ".owledge").mkdir(parents=True)
            null_space.link_project(project, global_root)
            self.assertEqual(null_space.scan_user_global(project, requested_scope="enterprise")["error"], "scope_unsupported")
            link_path = project / null_space.LINK_RELATIVE_PATH
            link = json.loads(link_path.read_text(encoding="utf-8"))
            link["network"] = "enabled"
            link_path.write_text(json.dumps(link), encoding="utf-8")
            self.assertEqual(null_space.scan_user_global(project)["error"], "link_remote_or_sync_denied")

            link["network"] = "disabled"
            link_path.write_text(json.dumps(link), encoding="utf-8")
            outside = base / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            escape = global_root / "reviewed" / "escape.md"
            escape.parent.mkdir(parents=True, exist_ok=True)
            try:
                escape.symlink_to(outside)
            except OSError:
                self.skipTest("symlink creation is unavailable on this Windows host")
            self.assertEqual(null_space.scan_user_global(project)["error"], "global_symlink_escape")


if __name__ == "__main__":
    unittest.main()
