from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_run_state as run_state


class RunStateShardingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.legacy = self.root / "RUN-STATE.yaml"
        self.legacy.write_text(
            "current_release: v0.8.0\nactive_ticket: OW-080-14\nlast_green_gate: G-080-B-CONTEXT\n"
            "alignment:\n  findings:\n    - id: F-080-01\n      status: resolved\n      evidence: receipt-a\n"
            "    - id: F-071-03\n      status: routed\n      evidence: receipt-b\n"
            "  decisions:\n    - id: D-080-01\n      authority: owner\n      decision: bounded\n"
            "    - id: D-071-03\n      authority: owner\n      decision: legacy\n"
            + "historical_checkpoint: retained historical context " * 250,
            encoding="utf-8",
        )
        self.before = hashlib.sha256(self.legacy.read_bytes()).hexdigest()
        self.result = run_state.migrate_legacy_run_state(self.legacy, self.root / "sharded")
        self.manifest = pathlib.Path(self.result["manifest_path"])

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_migration_is_copy_only_and_pointer_is_compact(self) -> None:
        self.assertTrue(self.result["legacy_unchanged"])
        self.assertEqual(self.before, hashlib.sha256(self.legacy.read_bytes()).hexdigest())
        self.assertLess(self.result["manifest_bytes"], 2048)
        self.assertEqual({"active_version", "active_ticket", "active_gate", "register_index", "last_checkpoint_sha", "path"}, set(run_state.parse_pointer_manifest(self.manifest)))

    def test_cold_load_reads_only_pointer_and_active_register(self) -> None:
        loaded = run_state.load_active_register(self.manifest)
        self.assertEqual(2, len(loaded["loaded_paths"]))
        self.assertTrue(loaded["loaded_paths"][1].endswith("v0.8.0.json"))
        self.assertLess(loaded["loaded_file_content_tokens"], run_state.token_count(self.legacy.read_text(encoding="utf-8")))
        self.assertEqual(["F-080-01", "F-071-03"], [row["id"] for row in loaded["register"]["findings"]])

    def test_explicit_historical_lookup_preserves_identifier_and_sha(self) -> None:
        legacy_entry = run_state._yaml_list_entries(self.legacy.read_text(encoding="utf-8"), "findings")[1]
        resolved = run_state.resolve_register_entry(self.manifest, "v0.7.1", "F-071-03")
        self.assertEqual(legacy_entry["id"], resolved["id"])
        self.assertEqual(legacy_entry["sha256"], resolved["sha256"])

    def test_traversal_and_missing_active_register_fail_closed(self) -> None:
        text = self.manifest.read_text(encoding="utf-8")
        self.manifest.write_text(text.replace("registers/v0.8.0.json", "../escape.json"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid_path"):
            run_state.load_active_register(self.manifest)
        self.manifest.write_text(text.replace("registers/v0.8.0.json", "registers/missing.json"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "active_register_missing"):
            run_state.load_active_register(self.manifest)

    def test_repeated_migration_is_idempotent_and_legacy_flat_is_unaffected(self) -> None:
        second = run_state.migrate_legacy_run_state(self.legacy, self.root / "sharded")
        self.assertTrue(second["legacy_unchanged"])
        self.assertEqual(self.result["register_index"], second["register_index"])
        self.assertEqual(self.before, hashlib.sha256(self.legacy.read_bytes()).hexdigest())

    def test_explicit_tool_cli_is_copy_only(self) -> None:
        output = self.root / "cli-output"
        process = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "owledge_run_state.py"), "--legacy-state", str(self.legacy), "--output-path", str(output)],
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertTrue(__import__("json").loads(process.stdout)["legacy_unchanged"])
        self.assertEqual(self.before, hashlib.sha256(self.legacy.read_bytes()).hexdigest())

    def test_project_kit_includes_explicit_migration_tool(self) -> None:
        import build_project_folder_kit
        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp) / "kit"
            build_project_folder_kit.build(__import__("argparse").Namespace(
                output_path=str(output), project_root=str(ROOT), force=True,
                include_global_memory=False, include_plugin_adapter=False,
                include_compliance=False, plugin_hook_profile="python", verify=True,
            ))
            self.assertTrue((output / "tools" / "owledge_run_state.py").is_file())


if __name__ == "__main__":
    unittest.main()
