from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
CLI = ROOT / "tools" / "owledge.py"
PUBLIC_VERBS = ("init", "doctor", "recall", "context", "propose", "review", "sync", "upgrade")


def invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, text=True, capture_output=True, check=False)


class V1M03PublicFacadeTests(unittest.TestCase):
    def test_default_help_exposes_exactly_the_eight_core_verbs(self) -> None:
        result = invoke("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("{init,doctor,recall,context,propose,review,sync,upgrade}", result.stdout)
        for verb in PUBLIC_VERBS:
            self.assertRegex(result.stdout, rf"(?m)^    {verb}\s")
        for legacy in ("init-project", "research-recall", "build-context-pack", "quickstart", "benchmark-kit"):
            self.assertNotIn(legacy, result.stdout)

    def test_aliases_work_and_legacy_route_is_actionably_deprecated(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m03-") as temporary:
            target = pathlib.Path(temporary) / "project"
            public_result = invoke("init", "--target", str(target))
            self.assertEqual(public_result.returncode, 0, public_result.stderr)
            self.assertEqual(json.loads(public_result.stdout)["profile"], "minimal")

            legacy_result = invoke("init-project", "--target", str(pathlib.Path(temporary) / "legacy"))
            self.assertEqual(legacy_result.returncode, 0, legacy_result.stderr)
            self.assertIn("DEPRECATION", legacy_result.stderr)
            self.assertIn("owledge init", legacy_result.stderr)

            advanced_result = invoke("advanced", "research-recall", "--project-root", str(target), "--query", "minimal")
            self.assertEqual(advanced_result.returncode, 0, advanced_result.stderr)
            self.assertNotIn("DEPRECATION", advanced_result.stderr)

    def test_remaining_unavailable_lifecycle_verbs_and_unknown_ninth_verb_fail_without_dispatch(self) -> None:
        for operation in ("review", "sync"):
            deferred = invoke(operation)
            self.assertEqual(deferred.returncode, 2)
            body = json.loads(deferred.stdout)
            self.assertEqual(body["error"], "operation_not_available_yet")
            self.assertEqual(body["operation"], operation)

        unknown = invoke("ninth-verb")
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("invalid choice", unknown.stderr)


if __name__ == "__main__":
    unittest.main()
