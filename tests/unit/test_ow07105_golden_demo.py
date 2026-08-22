from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
CLI = ROOT / "tools" / "owledge.py"
SEED = ROOT / "examples" / "vibecoding-golden-demo" / "seed"


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


class OW07105GoldenDemoTests(unittest.TestCase):
    def test_no_install_proof_is_read_only_and_has_one_success_signal(self) -> None:
        proof = (ROOT / "examples" / "vibecoding-golden-demo" / "30-second-proof.md").read_text(encoding="utf-8")
        self.assertIn("writes **zero files**", proof)
        self.assertIn("**Success signal:**", proof)
        self.assertNotIn("```bash", proof)

    def test_package_demo_contract_does_not_mix_source_only_addon(self) -> None:
        demo = (ROOT / "docs" / "vibecoding-golden-demo.md").read_text(encoding="utf-8")
        package_section = demo.split("## Proof 2:", 1)[1].split("## Proof 3:", 1)[0]
        self.assertIn("uvx owledge quickstart", package_section)
        self.assertIn("owledge doctor", package_section)
        self.assertIn("owledge context", package_section)
        self.assertNotIn("install-addon", package_section)
        self.assertIn("source-checkout add-on", demo)

    def test_seeded_feature_request_produces_context_and_resumable_links(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ow07105-") as temporary:
            target = pathlib.Path(temporary) / "project"
            quickstart = run_cli("quickstart", "--target", str(target))
            destinations = {
                "filter-request.md": target / ".owledge" / "canonical" / "filter-request.md",
                "filter-request-check.md": target / ".owledge" / "evidence" / "filter-request-check.md",
                "filter-request-resume.md": target / ".owledge" / "handoffs" / "filter-request-resume.md",
            }
            for name, destination in destinations.items():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(SEED / name, destination)

            context = run_cli(
                "context",
                "--project-root",
                str(target),
                "--task-id",
                "filter-request",
                "--agent-role",
                "worker",
                "--objective",
                "Verify the completed-item filter without widening scope",
            )
            validation = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "owledge_core.py"), "--project-root", str(target), "validate-memory", "--strict"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertTrue(quickstart["passed"])
            self.assertEqual(0, validation.returncode, f"{validation.stderr}\n{validation.stdout}")
            context_sources = {item["source"] for item in context["context"]}
            self.assertTrue(any(source.endswith("filter-request.md") for source in context_sources))
            self.assertIn("filter-request-check.md", (destinations["filter-request-resume.md"]).read_text(encoding="utf-8"))
            self.assertIn("filter-request.md", (destinations["filter-request-check.md"]).read_text(encoding="utf-8"))

    def test_fresh_resume_artifacts_state_scope_checks_and_next_safe_action(self) -> None:
        request = (SEED / "filter-request.md").read_text(encoding="utf-8")
        evidence = (SEED / "filter-request-check.md").read_text(encoding="utf-8")
        handoff = " ".join((SEED / "filter-request-resume.md").read_text(encoding="utf-8").split())
        self.assertIn("without changing stored data", request)
        for check in ["Unfinished item remains visible", "Completed item is hidden", "Stored items are unchanged"]:
            self.assertIn(check, evidence)
        self.assertIn("Confirm the three checks are still applicable", handoff)
        self.assertIn("Do not infer sync, deletion, or account work", handoff)


if __name__ == "__main__":
    unittest.main()
