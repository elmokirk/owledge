"""Executable acceptance checks for OW-071-12 agent integration contracts."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "skills-and-agent-integrations.md"


def _doctor_check(payload: dict, name: str) -> dict:
    return next(row for row in payload["checks"] if row["name"] == name)


class AgentIntegrationContractTests(unittest.TestCase):
    def test_public_registry_covers_required_boundaries(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        for phrase in (
            "| Skill or integration | Class | Trigger | Inputs | Effects | Dependencies | Runtime support | Stability |",
            "`owledge-contract`",
            "`owledge-long-horizon-delivery`",
            "`tools/owledge_mcp.py`",
            "`plugins/owledge-cowork/`",
            "`concept-blindspot-audit`",
            "`render-memory-report`",
            "`.owledge/skills/` is **not** an automatic discovery root",
            "MCP profile is read-only",
            "does not authenticate that its caller is a human or owner",
            "Treat a drifting mirror as user-edited",
            "```mermaid",
            "Human accepts promotion?",
            "Agent execution contract",
            "Happy path and variants",
            "Agent-choice scenarios",
            "## Recovery",
        ):
            self.assertIn(phrase, text)

    def test_agent_choice_scenarios_have_safe_non_choices(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        for phrase in (
            "existing repository without installing anything",
            "initialized Codex project",
            "existing Markdown vault preserved",
            "parallel delivery",
            "MCP client needs context",
            "Do not infer write, promotion, or remote sync capability",
        ):
            self.assertIn(phrase, text)

    def test_long_horizon_modes_and_contract_default_are_real(self) -> None:
        long_horizon = (ROOT / "skills" / "owledge-long-horizon-delivery" / "SKILL.md").read_text(encoding="utf-8")
        modes = (ROOT / "skills" / "owledge-long-horizon-delivery" / "references" / "modes.md").read_text(encoding="utf-8")
        contract = (ROOT / "standalone-skills" / "owledge-contract" / "SKILL.md").read_text(encoding="utf-8")
        for mode in ("mvp-sparring", "version-steering", "ticket-execution", "gate-review", "recovery"):
            self.assertIn(mode, f"{long_horizon}\n{modes}")
        self.assertIn("works without an Owledge\nruntime, CLI, hooks, MCP, or project kit", contract)

    def test_fresh_host_has_hash_matching_discovery_mirrors_and_doctor_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ow07112-host-") as temp_dir:
            target = Path(temp_dir) / "host"
            init = subprocess.run([sys.executable, "tools/owledge.py", "init-project", "--target", str(target)], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(init.returncode, 0, init.stderr)
            manifest = json.loads((target / "kit-manifest.json").read_text(encoding="utf-8"))
            rows = {row["path"]: row for row in manifest["files"]}
            source = target / "skills" / "owledge-long-horizon-delivery" / "SKILL.md"
            mirror = target / ".agents" / "skills" / "owledge-long-horizon-delivery" / "SKILL.md"
            self.assertEqual(source.read_bytes(), mirror.read_bytes())
            self.assertEqual(rows[".agents/skills/owledge-long-horizon-delivery/SKILL.md"]["sha256_installed"], hashlib.sha256(mirror.read_bytes()).hexdigest())

            doctor = subprocess.run([sys.executable, "tools/owledge.py", "doctor", "--project-root", str(target), "--mode", "host"], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(doctor.returncode, 0, doctor.stderr)
            self.assertTrue(_doctor_check(json.loads(doctor.stdout), "agent-skill-discovery")["passed"])

            mirror.write_text(mirror.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
            drift_doctor = subprocess.run([sys.executable, "tools/owledge.py", "doctor", "--project-root", str(target), "--mode", "host"], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(drift_doctor.returncode, 0, drift_doctor.stderr)
            discovery = _doctor_check(json.loads(drift_doctor.stdout), "agent-skill-discovery")
            self.assertFalse(discovery["passed"])
            self.assertIn("owledge-long-horizon-delivery", discovery["details"])

    def test_running_mcp_tool_surface_has_only_the_read_only_allowlist(self) -> None:
        process = subprocess.run(
            [sys.executable, "tools/owledge_mcp.py"],
            cwd=ROOT,
            input='{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n',
            text=True,
            capture_output=True,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        tools = json.loads(process.stdout)["result"]["tools"]
        names = {tool["name"] for tool in tools}
        self.assertEqual(names, {
            "owledge_read_entrypoint",
            "owledge_doctor",
            "owledge_search_memory",
            "owledge_build_context_pack",
            "owledge_list_tasks",
            "owledge_list_reviews",
        })
        for tool in tools:
            self.assertNotRegex(f"{tool['name']} {tool['description']}", r"(?i)write|promote|sync")


if __name__ == "__main__":
    unittest.main()
