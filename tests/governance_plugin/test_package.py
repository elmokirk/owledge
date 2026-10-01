"""Offline package/hook checks, not model evaluations or host certification."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("governance_build", ROOT / "tools/build_governance_plugin.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
PLUGIN = ROOT / builder.PLUGIN
NODE = shutil.which("node")


class PackageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="owledge package ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.plugin = self.root / builder.PLUGIN
        shutil.copytree(PLUGIN, self.plugin)
        for name in builder.CATALOGS:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def change_json(self, path, mutate):
        doc = builder.load_json(path)
        mutate(doc)
        path.write_text(json.dumps(doc), encoding="utf-8")

    def invalid(self):
        with self.assertRaises(ValueError):
            builder.validate(self.root)

    def test_valid_package(self):
        self.assertEqual(builder.validate(self.root), "0.1.0-rc.1")

    def test_manifest_identity(self):
        for name in ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            doc = builder.load_json(self.plugin / name)
            self.assertEqual(doc["name"], "owledge-governance")
            self.assertEqual(doc["license"], "MIT")
            self.assertEqual(doc["author"]["name"], "elmokirk")

    def test_version_drift(self):
        self.change_json(self.plugin / ".codex-plugin/plugin.json", lambda d: d.update(version="9.9.9"))
        self.invalid()

    def test_duplicate_json_key(self):
        (self.plugin / "plugin.json").write_text('{"name":"a","name":"b"}', encoding="utf-8")
        self.invalid()

    def test_catalog_escape(self):
        self.change_json(self.root / builder.CATALOGS[0], lambda d: d["plugins"][0].update(source="../private"))
        self.invalid()

    def test_unexpected_secret(self):
        (self.plugin / ".env").write_text("SECRET=fixture", encoding="utf-8")
        self.invalid()

    def test_active_hook_excluded(self):
        shutil.copyfile(self.plugin / "hooks/hooks.example.json", self.plugin / "hooks/hooks.json")
        self.invalid()

    def test_mcp_excluded(self):
        self.change_json(self.plugin / "plugin.json", lambda d: d.update(mcpServers={"unexpected": {}}))
        self.invalid()

    def test_missing_rule(self):
        path = self.plugin / "skills/governance/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8").replace("| W06 |", "| MISSING |"), encoding="utf-8")
        self.invalid()

    def test_symlink_rejected(self):
        path = self.plugin / "PRIVACY.md"
        path.unlink()
        try:
            path.symlink_to(self.plugin / "README.md")
        except OSError as exc:
            self.skipTest(str(exc))
        self.invalid()

    def test_traversal_rejected(self):
        with self.assertRaises(ValueError):
            builder.safe_file(self.root, "../private")

    def test_archives_and_checksums(self):
        files = builder.build(self.root, self.root / "out")
        with zipfile.ZipFile(files[0]) as archive:
            self.assertEqual(set(archive.namelist()), set(builder.FILES))
            self.assertIsNone(archive.testzip())
        with zipfile.ZipFile(files[1]) as archive:
            for name in builder.CATALOGS:
                self.assertIn(name, archive.namelist())
            self.assertFalse(any("internal/" in n or "local-core/" in n for n in archive.namelist()))
        for line in files[2].read_text().splitlines():
            digest, name = line.split("  ")
            self.assertEqual(digest, hashlib.sha256((files[2].parent / name).read_bytes()).hexdigest())

    def test_reproducible_build(self):
        a = builder.build(self.root, self.root / "a")
        b = builder.build(self.root, self.root / "b")
        self.assertEqual([p.read_bytes() for p in a], [p.read_bytes() for p in b])

    def test_existing_artifacts_preserved(self):
        builder.build(self.root, self.root / "out")
        with self.assertRaises(ValueError):
            builder.build(self.root, self.root / "out")

    def test_output_inside_plugin_rejected(self):
        with self.assertRaises(ValueError):
            builder.build(self.root, self.plugin / "dist")

    def test_single_skill(self):
        self.assertEqual(len(list(self.plugin.rglob("SKILL.md"))), 1)

    def test_no_runtime_folders(self):
        for name in (".owledge", "global-memory", "local-core", "OWLEDGE.md", ".mcp.json"):
            self.assertFalse((self.plugin / name).exists())


@unittest.skipUnless(NODE, "Node.js missing; optional hook tests not run")
class HookTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="owledge hook spaces ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.plugin = self.root / "plugin with spaces"
        shutil.copytree(PLUGIN, self.plugin)
        (self.root / "customer-secret.txt").write_text("DO_NOT_DISCLOSE_123", encoding="utf-8")

    def run_hook(self, data, **kwargs):
        return subprocess.run([NODE, str(self.plugin / "hooks/session-start.cjs")], input=data,
                              capture_output=True, cwd=self.root, timeout=5, **kwargs)

    def test_reference_and_hash(self):
        result = self.run_hook(b'{"hook_event_name":"SessionStart"}')
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["hookEventName"], "SessionStart")
        digest = hashlib.sha256((self.plugin / "skills/governance/SKILL.md").read_bytes()).hexdigest()
        self.assertIn(digest, output["additionalContext"])
        self.assertEqual(result.stderr, b"")

    def test_other_event(self):
        result = self.run_hook(b'{"hook_event_name":"PreToolUse"}')
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.returncode, 0)

    def test_malformed_input(self):
        result = self.run_hook(b"not-json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"Owledge", result.stderr)

    def test_oversize_input(self):
        result = self.run_hook(b"private" * 12000)
        self.assertEqual(result.stdout, b"")
        self.assertNotIn(b"private", result.stderr)

    def test_invalid_utf8(self):
        result = self.run_hook(b"\xff\xfe")
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.returncode, 0)

    def test_missing_profile(self):
        (self.plugin / "skills/governance/SKILL.md").unlink()
        result = self.run_hook(b'{"hook_event_name":"SessionStart"}')
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"nicht geladen", result.stderr)

    def test_no_secret_echo(self):
        event = {"hook_event_name": "SessionStart", "cwd": "/private/customer",
                 "transcript_path": "customer-secret.txt", "secret": "DO_NOT_DISCLOSE_123"}
        result = self.run_hook(json.dumps(event).encode())
        self.assertNotIn(b"DO_NOT_DISCLOSE_123", result.stdout + result.stderr)
        self.assertNotIn(b"/private/customer", result.stdout + result.stderr)

    def test_no_file_changes(self):
        def snapshot():
            return {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        before = snapshot()
        self.run_hook(b'{"hook_event_name":"SessionStart"}')
        self.assertEqual(before, snapshot())

    def test_environment_cannot_redirect(self):
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT="/private", PLUGIN_ROOT="/private")
        result = self.run_hook(b'{"hook_event_name":"SessionStart"}', env=env)
        self.assertIn(b"additionalContext", result.stdout)
        self.assertNotIn(b"/private", result.stdout)

    def test_linked_profile_rejected(self):
        path = self.plugin / "skills/governance/SKILL.md"
        path.unlink()
        try:
            path.symlink_to(self.root / "customer-secret.txt")
        except OSError as exc:
            self.skipTest(str(exc))
        result = self.run_hook(b'{"hook_event_name":"SessionStart"}')
        self.assertEqual(result.stdout, b"")
        self.assertNotIn(b"DO_NOT_DISCLOSE_123", result.stderr)


class NativeHostTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("claude"), "Claude Code absent; native validation NOT run")
    def test_claude_validator(self):
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, CLAUDE_CONFIG_DIR=home)
            for path in (PLUGIN, ROOT):
                result = subprocess.run(["claude", "plugin", "validate", "--strict", str(path)],
                                        capture_output=True, env=env, timeout=60)
                self.assertEqual(result.returncode, 0, (result.stdout + result.stderr).decode(errors="replace"))

    @unittest.skipUnless(shutil.which("codex"), "Codex absent; native catalog discovery NOT run")
    def test_codex_catalog(self):
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, HOME=home, USERPROFILE=home, CODEX_HOME=str(Path(home) / ".codex"))
            result = subprocess.run(["codex", "plugin", "marketplace", "add", str(ROOT)],
                                    capture_output=True, env=env, timeout=60)
            self.assertEqual(result.returncode, 0, (result.stdout + result.stderr).decode(errors="replace"))
            result = subprocess.run(["codex", "plugin", "marketplace", "list"], capture_output=True, env=env, timeout=60)
            self.assertEqual(result.returncode, 0)
            self.assertIn(b"owledge-labs", result.stdout)


if __name__ == "__main__":
    unittest.main()
