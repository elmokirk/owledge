from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]


class OW07104AdoptionDocsTests(unittest.TestCase):
    def test_five_second_first_screen_fixture(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        first_screen = readme.split("## Why It Exists", 1)[0]
        for required in [
            "Agentic Engineering Context & Planning Layer",
            "agents lose project context",
            "Markdown handoff",
            "not a hosted Team Hub",
            "read the [V1 Minimal Core boundary]",
        ]:
            self.assertIn(required, first_screen)
        self.assertNotIn("```bash", first_screen)

    def test_adoption_routes_follow_the_mental_model(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertLess(readme.index("## The mental model"), readme.index("## Install Or Try"))
        for target in [
            "docs/what-is-owledge.md",
            "docs/integration-decision-guide.md",
            "docs/quickstart.md",
            "docs/try-owledge-in-5-minutes.md",
        ]:
            self.assertIn(target, readme)

    def test_capability_registry_has_maturity_and_review_ownership(self) -> None:
        registry = json.loads((ROOT / "contracts" / "public-capabilities.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["release_owner_review"], "required")
        self.assertEqual(
            registry["maturity_values"],
            ["available", "local-experimental", "preview", "planned", "post-v1"],
        )
        for capability in registry["capabilities"]:
            self.assertIn(capability["maturity"], registry["maturity_values"])
            self.assertTrue(capability["evidence"])
            self.assertRegex(capability["source_retrieved_at"], r"^20\d{2}-\d{2}-\d{2}$")
            self.assertTrue(capability["release_owner"])


if __name__ == "__main__":
    unittest.main()
