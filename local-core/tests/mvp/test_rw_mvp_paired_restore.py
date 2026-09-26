"""A fixed linked pair publishes at one new parent with suspended readers."""
from __future__ import annotations

import io
import json
from hashlib import sha256
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from owledge_adapters.cli import main
from owledge_adapters import workspace_archive
from owledge_core.artifacts import parse_managed_markdown
from owledge_core.project_io import (_render_metadata_document, _reuse_json, local_connection_principal,
                                     relocate_fixed_project_global_pair)


class PairedRestoreTests(unittest.TestCase):
    def call(self, *args):
        output = io.StringIO()
        code = main([*map(str, args), "--json"], output_stream=output)
        return code, json.loads(output.getvalue())

    def test_native_pair_round_trip_and_occupied_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            project, global_workspace = base / "old-project", base / "old-global"
            self.assertEqual(self.call("setup", project, "--profile", "project", "--project-id", "paired", "--yes")[0], 0)
            self.assertEqual(self.call("setup", global_workspace, "--profile", "knowledge", "--yes")[0], 0)
            self.assertEqual(self.call("link", "--workspace", project, "--global-workspace", global_workspace, "--yes")[0], 0)
            for workspace, name in ((project, "project-reader"), (global_workspace, "global-reader")):
                connection = self.call("connect", name, "--workspace", workspace)[1]
                self.assertEqual(self.call("connect", name, "--workspace", workspace,
                    "--expected-sha256", connection["expected_sha256"], "--yes")[1]["status"], "ready")
            forward = self.call("global-read", "--workspace", project, "--connection", "project-reader",
                                "--action", "grant")[1]
            self.assertEqual(self.call("global-read", "--workspace", project, "--connection", "project-reader",
                "--action", "grant", "--expected-sha256", forward["expected_sha256"], "--yes")[1]["status"], "ready")
            reverse = self.call("project-read", "--workspace", global_workspace, "--project-id", "project:paired",
                                "--project-workspace", project, "--connection", "global-reader", "--action", "grant")[1]
            self.assertEqual(self.call("project-read", "--workspace", global_workspace, "--project-id", "project:paired",
                "--project-workspace", project, "--connection", "global-reader", "--action", "grant",
                "--expected-sha256", reverse["expected_sha256"], "--yes")[1]["status"], "ready")
            archive = base / "pair.zip"
            self.assertEqual(self.call("backup", "--workspace", project, "--archive",
                global_workspace / "inside.zip", "--linked")[1]["status"], "needs_attention")
            preview = self.call("backup", "--workspace", project, "--archive", archive, "--linked")[1]
            self.assertEqual(preview["status"], "preview", preview)
            self.assertEqual(self.call("backup", "--workspace", project, "--archive", archive, "--linked",
                                       "--expected-sha256", preview["expected_sha256"], "--yes")[1]["status"], "ready")
            with zipfile.ZipFile(archive) as packaged:
                archived = {name.removeprefix("files/"): packaged.read(name)
                            for name in packaged.namelist() if name.startswith("files/")}
            external_id = "project:another"
            external_name = "another-reader"
            external_principal = local_connection_principal(external_id, external_name)
            external_project = str(base / "another-project")
            suffix = sha256(_reuse_json({"project": external_project, "global": str(global_workspace),
                                        "authority_id": external_id}).encode()).hexdigest()[:24]
            key = "Global/global/.owledge/authority.md"
            authority = parse_managed_markdown(key, archived[key].decode(), encoded_document=archived[key])
            metadata = dict(authority.metadata)
            metadata["actor_grants"] = {**metadata["actor_grants"], external_principal: ["retrieve"]}
            metadata["named_project_readers"] = {**metadata["named_project_readers"], external_principal: {
                "project_workspace": external_project, "project_authority_id": external_id,
                "connection": external_name, "principal_id": external_principal,
                "contribution_link_id": "link:project-global-contribute-" + suffix,
                "registration_receipt_id": "receipt:project-global-link-" + suffix,
                "profile_generation": "a" * 64}}
            archived[key] = _render_metadata_document(metadata, authority.body).encode()
            relocated = relocate_fixed_project_global_pair(archived, old_project=project,
                old_global=global_workspace, new_project=base / "probe/Project", new_global=base / "probe/Global")
            self.assertIn(external_id, relocated["external_projects_unavailable"])
            self.assertIn(external_principal, relocated["suspended_readers"])
            target = base / "restored"
            restore = self.call("restore", "--archive", archive, "--target", target)[1]
            self.assertEqual(restore["status"], "preview", restore)
            self.assertEqual(len(restore["pair"]["suspended_readers"]), 2)
            applied = self.call("restore", "--archive", archive, "--target", target,
                                "--expected-sha256", restore["expected_sha256"], "--yes")[1]
            self.assertEqual(applied["status"], "ready", applied)
            self.assertTrue((target / "Project/workspace.json").exists())
            self.assertTrue((target / "Global/workspace.json").exists())
            self.assertEqual(self.call("status", "--workspace", target / "Project")[1]["status"], "healthy")
            self.assertEqual(self.call("status", "--workspace", target / "Global")[1]["status"], "healthy")
            restored_project, restored_global = target / "Project", target / "Global"
            forward = self.call("global-read", "--workspace", restored_project,
                                "--connection", "project-reader", "--action", "grant")[1]
            self.assertEqual(forward["status"], "preview", forward)
            self.assertEqual(self.call("global-read", "--workspace", restored_project,
                "--connection", "project-reader", "--action", "grant",
                "--expected-sha256", forward["expected_sha256"], "--yes")[1]["status"], "ready")
            reverse = self.call("project-read", "--workspace", restored_global,
                "--project-id", "project:paired", "--project-workspace", restored_project,
                "--connection", "global-reader",
                "--action", "grant")[1]
            self.assertEqual(reverse["status"], "preview", reverse)
            self.assertEqual(self.call("project-read", "--workspace", restored_global,
                "--project-id", "project:paired", "--project-workspace", restored_project,
                "--connection", "global-reader",
                "--action", "grant", "--expected-sha256", reverse["expected_sha256"],
                "--yes")[1]["status"], "ready")
            self.assertEqual(self.call("restore", "--archive", archive, "--target", target)[1]["status"], "needs_attention")
            interrupted = base / "interrupted"
            pending = self.call("restore", "--archive", archive, "--target", interrupted)[1]
            with patch.object(Path, "rename", side_effect=OSError("injected publish interruption")):
                failed = self.call("restore", "--archive", archive, "--target", interrupted,
                                   "--expected-sha256", pending["expected_sha256"], "--yes")[1]
            self.assertEqual(failed["status"], "needs_attention", failed)
            self.assertFalse(interrupted.exists())
            recovered = self.call("restore", "--archive", archive, "--target", interrupted,
                                  "--recover", "--yes")[1]
            self.assertEqual(recovered["status"], "ready", recovered)
            self.assertEqual(self.call("status", "--workspace", interrupted / "Project")[1]["status"], "healthy")
            published = base / "published"
            pending = self.call("restore", "--archive", archive, "--target", published)[1]
            original_unlink = Path.unlink
            def interrupt_marker(path, *args, **kwargs):
                if path.name == "paired-restore.json":
                    raise OSError("injected post-publication interruption")
                return original_unlink(path, *args, **kwargs)
            with patch.object(Path, "unlink", interrupt_marker):
                failed = self.call("restore", "--archive", archive, "--target", published,
                                   "--expected-sha256", pending["expected_sha256"], "--yes")[1]
            self.assertEqual(failed["status"], "needs_attention", failed)
            self.assertEqual(self.call("status", "--workspace", published / "Project")[1]["status"], "needs_attention")
            self.assertEqual(self.call("status", "--workspace", published / "Global")[1]["status"], "needs_attention")
            self.assertEqual(self.call("restore", "--archive", archive, "--target", published,
                                       "--recover", "--yes")[1]["status"], "ready")
            before_marker = base / "before-marker"
            pending = self.call("restore", "--archive", archive, "--target", before_marker)[1]
            real_replace = workspace_archive.os.replace
            def interrupt_marker_install(source, destination):
                if Path(destination).name == "paired-restore.json":
                    raise OSError("injected marker install interruption")
                return real_replace(source, destination)
            with patch.object(workspace_archive.os, "replace", interrupt_marker_install):
                failed = self.call("restore", "--archive", archive, "--target", before_marker,
                                   "--expected-sha256", pending["expected_sha256"], "--yes")[1]
            self.assertEqual(failed["status"], "needs_attention", failed)
            self.assertFalse(before_marker.exists())
            self.assertEqual(self.call("restore", "--archive", archive, "--target", before_marker,
                                       "--recover", "--yes")[1]["status"], "ready")

    def test_self_consistent_invalid_pair_stays_guarded_during_recovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            project, global_workspace = base / "old-project", base / "old-global"
            self.assertEqual(self.call("setup", project, "--profile", "project", "--project-id", "paired", "--yes")[0], 0)
            self.assertEqual(self.call("setup", global_workspace, "--profile", "knowledge", "--yes")[0], 0)
            self.assertEqual(self.call("link", "--workspace", project, "--global-workspace", global_workspace, "--yes")[0], 0)
            archive = base / "good.zip"
            preview = self.call("backup", "--workspace", project, "--archive", archive, "--linked")[1]
            self.assertEqual(self.call("backup", "--workspace", project, "--archive", archive, "--linked",
                "--expected-sha256", preview["expected_sha256"], "--yes")[1]["status"], "ready")
            with zipfile.ZipFile(archive) as packaged:
                original = {name: packaged.read(name) for name in packaged.namelist()}
            for case in ("workspace", "settings"):
                with self.subTest(case=case):
                    files = {name.removeprefix("files/"): value for name, value in original.items()
                             if name.startswith("files/")}
                    if case == "workspace":
                        files["Global/workspace.json"] = b'{"schema": "invalid"}\n'
                    else:
                        files["Global/global/.owledge/settings.md"] = b'---\nschema: "invalid"\n---\n'
                    manifest = json.loads(original["manifest.json"])
                    manifest["files"] = {name: {"sha256": sha256(data).hexdigest(), "size": len(data),
                         "readonly": manifest["files"].get(name, {}).get("readonly", False)}
                         for name, data in files.items()}
                    forged = base / f"forged-{case}.zip"
                    with zipfile.ZipFile(forged, "w") as output:
                        output.writestr("manifest.json", json.dumps(manifest, sort_keys=True))
                        for name, data in files.items():
                            output.writestr("files/" + name, data)
                    target = base / f"restored-{case}"
                    restore = self.call("restore", "--archive", forged, "--target", target)[1]
                    self.assertEqual(restore["status"], "preview", restore)
                    failed = self.call("restore", "--archive", forged, "--target", target,
                        "--expected-sha256", restore["expected_sha256"], "--yes")[1]
                    self.assertEqual(failed["status"], "needs_attention", failed)
                    self.assertTrue((target / ".owledge/paired-restore.json").exists())
                    self.assertEqual(self.call("status", "--workspace", target / "Project")[1]["status"], "needs_attention")
                    self.assertEqual(self.call("restore", "--archive", forged, "--target", target,
                        "--recover", "--yes")[1]["status"], "needs_attention")


if __name__ == "__main__":
    unittest.main()
