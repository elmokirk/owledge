from __future__ import annotations

import copy
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_adapter_contracts as adapters  # noqa: E402


CONTRACTS = ROOT / "addons" / "runtime-conformance-kit" / "contracts"
SCHEMA = ROOT / "templates" / "owledge" / "schemas" / "adapter-manifest-v1.schema.json"


class AdapterManifestTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((CONTRACTS / f"{name}.json").read_text(encoding="utf-8"))

    def test_three_v1_profiles_validate_and_have_equivalent_capabilities(self):
        profiles = [self.load(name) for name in ("codex", "claude-code", "generic-mcp-cli")]
        self.assertTrue(SCHEMA.is_file())
        self.assertEqual(json.loads(SCHEMA.read_text(encoding="utf-8"))["title"], "Owledge AdapterManifest v1")
        for profile in profiles:
            self.assertEqual(adapters.validate_adapter_manifest(profile), [])
        self.assertEqual({tuple(profile["supported_capabilities"]) for profile in profiles}, {
            ("context.read", "control.read", "checkpoint.handoff", "candidate.write"),
        })

    def test_declared_capability_negotiates_with_local_scope_and_permission(self):
        receipt = adapters.negotiate(
            self.load("codex"), capability_id="candidate.write", scope="project_user",
            requested_permissions=["write_candidate"],
        )
        self.assertEqual(receipt["result"], "supported")
        self.assertEqual(receipt["reason_code"], "ok")
        self.assertEqual(receipt["effective_permissions"], ["write_candidate"])

    def test_context_read_requires_only_the_permission_for_its_local_scope(self):
        profile = self.load("codex")
        project = adapters.negotiate(profile, capability_id="context.read", scope="project_user", requested_permissions=["read_project"])
        global_scope = adapters.negotiate(profile, capability_id="context.read", scope="user_global", requested_permissions=["read_user_global"])
        missing = adapters.negotiate(profile, capability_id="context.read", scope="user_global", requested_permissions=["read_project"])
        self.assertEqual(project["result"], "supported")
        self.assertEqual(global_scope["result"], "supported")
        self.assertEqual(missing["reason_code"], "permission_denied")

    def test_unsupported_and_undeclared_capabilities_fail_explicitly(self):
        profile = self.load("generic-mcp-cli")
        unsupported = adapters.negotiate(
            profile, capability_id="routing.durable", scope="project_user",
            requested_permissions=["read_project"],
        )
        undeclared = adapters.negotiate(
            profile, capability_id="made.up", scope="project_user",
            requested_permissions=["read_project"],
        )
        self.assertEqual((unsupported["result"], unsupported["reason_code"]), ("unsupported", "core_owned"))
        self.assertEqual((undeclared["result"], undeclared["reason_code"]), ("unsupported", "undeclared_capability"))

    def test_bad_version_permission_profile_and_direct_storage_fail_closed(self):
        profile = self.load("claude-code")
        version = adapters.negotiate(
            profile, capability_id="context.read", scope="project_user",
            requested_permissions=["read_project"], core_api_version="2.0.0",
        )
        permission = adapters.negotiate(
            profile, capability_id="candidate.write", scope="project_user", requested_permissions=[],
        )
        direct_storage = adapters.negotiate(
            profile, capability_id="core.storage.direct", scope="project_user",
            requested_permissions=["read_project"],
        )
        malformed = copy.deepcopy(profile)
        malformed["adapter_id"] = "pi"
        malformed["unsupported_capabilities"] = malformed["unsupported_capabilities"][:-1]
        self.assertEqual(version["reason_code"], "core_api_incompatible")
        self.assertEqual(permission["reason_code"], "permission_denied")
        self.assertEqual((direct_storage["result"], direct_storage["reason_code"]), ("unsupported", "core_owned"))
        self.assertIn("manifest.adapter_id", adapters.validate_adapter_manifest(malformed))
        self.assertIn("manifest.capability_unclassified", adapters.validate_adapter_manifest(malformed))

    def test_cli_and_installed_addon_runner_reject_no_profile_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            initialized = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "owledge.py"), "init-project", "--target", str(root),
                 "--source-root", str(ROOT)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            install = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "owledge.py"), "install-addon", "--project-root", str(root),
                 "--addon", "runtime-conformance-kit", "--source-root", str(ROOT)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            runner = subprocess.run(
                [sys.executable, str(root / "tools" / "runtime-conformance" / "run-runtime-conformance.py"),
                 "--project-root", str(root)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(runner.returncode, 0, runner.stdout + runner.stderr)
            self.assertIn('"generic-mcp-cli"', runner.stdout)
            installed_manifest = root / ".owledge" / "runtime-conformance" / "generic-mcp-cli.json"
            broken = json.loads(installed_manifest.read_text(encoding="utf-8"))
            broken["core_api_range"] = ">=broken"
            installed_manifest.write_text(json.dumps(broken), encoding="utf-8")
            rejected_runner = subprocess.run(
                [sys.executable, str(root / "tools" / "runtime-conformance" / "run-runtime-conformance.py"),
                 "--project-root", str(root)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(rejected_runner.returncode, 1)
            self.assertIn("manifest.core_api_range", rejected_runner.stdout)
            cli = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "owledge_adapter_contracts.py"), "negotiate",
                 "--manifest", str(CONTRACTS / "codex.json"), "--capability", "scope.enterprise",
                 "--scope", "project_user", "--permission", "read_project"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(cli.returncode, 1)
            self.assertIn('"result": "unsupported"', cli.stdout)


if __name__ == "__main__":
    unittest.main()
