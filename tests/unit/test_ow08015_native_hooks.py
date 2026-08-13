from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
INJECT = ROOT / "plugins" / "owledge-cowork" / "scripts" / "inject-owledge-context.py"
CAPTURE = ROOT / "plugins" / "owledge-cowork" / "scripts" / "capture-claude-event.py"
CLOSE = ROOT / "plugins" / "owledge-cowork" / "scripts" / "close-runtime-session.py"
FIXTURES = ROOT / "plugins" / "owledge-cowork" / "tests" / "fixtures"


def load_capture():
    spec = importlib.util.spec_from_file_location("ow08015_capture", CAPTURE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NativeHookTests(unittest.TestCase):
    def test_session_start_capsule_reads_only_allowed_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / ".owledge" / "indexes").mkdir(parents=True)
            (root / "OWLEDGE.md").write_text("# Local Owledge\n", encoding="utf-8")
            (root / ".owledge" / "indexes" / "memory-index.jsonl").write_text('{"id":"m-1"}\n', encoding="utf-8")
            (root / "RUN-STATE.yaml").write_text("private register", encoding="utf-8")
            result = subprocess.run([sys.executable, str(INJECT)], cwd=root, text=True, capture_output=True, check=True)
            capsule = json.loads(result.stdout)
            self.assertEqual(["OWLEDGE.md", ".owledge/indexes/memory-index.jsonl"], capsule["loaded_sources"])
            self.assertNotIn("private register", result.stdout)

    def test_session_start_missing_owledge_fails_soft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, str(INJECT)], cwd=tmp, text=True, capture_output=True, check=True)
            self.assertEqual("unavailable", json.loads(result.stdout)["owledge"])

    def test_resolve_cli_refuses_external_fallback_without_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            module = load_capture()
            old = __import__("os").environ.pop("OWLEDGE_ALLOW_GLOBAL_KIT", None)
            try:
                with self.assertRaisesRegex(RuntimeError, "init-project"):
                    module.resolve_cli(root)
            finally:
                if old is not None:
                    __import__("os").environ["OWLEDGE_ALLOW_GLOBAL_KIT"] = old

    def test_resolve_cli_allows_explicit_global_kit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            module = load_capture()
            os = __import__("os")
            old = os.environ.get("OWLEDGE_ALLOW_GLOBAL_KIT")
            os.environ["OWLEDGE_ALLOW_GLOBAL_KIT"] = "1"
            try:
                self.assertEqual(ROOT / "tools" / "owledge_core.py", module.resolve_cli(pathlib.Path(tmp)))
            finally:
                if old is None:
                    os.environ.pop("OWLEDGE_ALLOW_GLOBAL_KIT", None)
                else:
                    os.environ["OWLEDGE_ALLOW_GLOBAL_KIT"] = old

    def test_hook_commands_are_project_relative(self) -> None:
        for name in ("hooks.json", "hooks.python.json"):
            payload = json.loads((ROOT / "plugins" / "owledge-cowork" / "hooks" / name).read_text(encoding="utf-8"))
            commands = [item["command"] for group in payload["hooks"].values() for row in group for item in row["hooks"]]
            self.assertTrue(all(":/" not in command and not command.startswith("/") for command in commands))
            self.assertTrue(any("inject-owledge-context.py" in command for command in commands))

    def test_init_project_writes_local_allowlist_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "host"
            first = subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project", "--target", str(target), "--include-plugin-adapter"], cwd=ROOT, text=True, capture_output=True, check=True)
            settings = target / ".claude" / "settings.json"
            payload = json.loads(settings.read_text(encoding="utf-8"))
            self.assertIn("Bash(python tools/owledge_core.py *)", payload["permissions"]["allow"])
            settings.write_text('{"user":"kept"}\n', encoding="utf-8")
            subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project", "--target", str(target), "--include-plugin-adapter"], cwd=ROOT, text=True, capture_output=True, check=True)
            self.assertEqual('{"user":"kept"}\n', settings.read_text(encoding="utf-8"))
            self.assertIn("include_plugin_adapter", first.stdout)

    def test_full_project_local_hook_session_has_zero_external_path_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = pathlib.Path(tmp) / "host"
            subprocess.run([sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project", "--target", str(host), "--include-plugin-adapter"], cwd=ROOT, text=True, capture_output=True, check=True)
            commands = [
                ([sys.executable, str(host / "plugins" / "owledge-cowork" / "scripts" / "inject-owledge-context.py")], None),
                ([sys.executable, str(host / "plugins" / "owledge-cowork" / "scripts" / "capture-claude-event.py")], (FIXTURES / "session-start.json").read_text(encoding="utf-8")),
                ([sys.executable, str(host / "plugins" / "owledge-cowork" / "scripts" / "capture-claude-event.py")], (FIXTURES / "user-prompt.json").read_text(encoding="utf-8")),
                ([sys.executable, str(host / "plugins" / "owledge-cowork" / "scripts" / "capture-claude-event.py")], (FIXTURES / "post-tool-use.json").read_text(encoding="utf-8")),
                ([sys.executable, str(host / "plugins" / "owledge-cowork" / "scripts" / "close-runtime-session.py")], (FIXTURES / "stop.json").read_text(encoding="utf-8")),
            ]
            outputs = [subprocess.run(command, cwd=host, input=payload, text=True, capture_output=True, check=True) for command, payload in commands]
            self.assertEqual(0, sum("external-path approval" in (row.stdout + row.stderr).lower() for row in outputs))
            self.assertTrue((host / ".owledge" / "sessions" / "cowork-demo-session" / "summary.md").is_file())


if __name__ == "__main__":
    unittest.main()
