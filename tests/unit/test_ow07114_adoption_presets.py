"""Contract checks for OW-071-14's bounded adoption preset guidance."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = (ROOT / "docs" / "adoption-presets.md").read_text(encoding="utf-8")
REGISTRY = json.loads((ROOT / "contracts" / "public-capabilities.json").read_text(encoding="utf-8"))


class AdoptionPresetContractTests(unittest.TestCase):
    def test_all_required_presets_are_selectable_with_boundaries(self) -> None:
        for preset in (
            "Principles-only", "Manual mini-kit", "Existing repository kit",
            "Standalone project folder", "Markdown knowledge-base module",
            "Local runtime adapter", "Private global layer", "Cross-project power-user hub",
        ):
            self.assertIn(f"| {preset} |", DOC)
        self.assertIn("| Preset | Choose it when | Maturity | Value | Authority and automation | Privacy | Prerequisites | Limits | Upgrade path |", DOC)

    def test_maturity_boundaries_do_not_conflate_local_and_future_capabilities(self) -> None:
        for phrase in (
            "Not Owlib, not remote sync, not a Team Hub",
            "`G-071-C-COMPAT` has not accepted compatibility",
            "Bounded loopback-only source-checkout experiments",
            "Write-enabled MCP, remote MCP service, promotion API, or sync layer",
            "Post-v1",
            "Do not relabel a local adapter as hosted functionality",
            "Reusable Hub-record boundary",
            "`audience_ids`",
            "`transferability`",
            "`visibility`",
            "`data_class`",
            "never overrides tenant/customer/project scope or grants access",
            "not automatic export permission",
            "When these fields disagree, keep the record private",
            "ask the responsible owner to decide",
        ):
            self.assertIn(phrase, DOC)

    def test_registry_exposes_documented_global_hub_and_future_maturity(self) -> None:
        rows = {row["id"]: row for row in REGISTRY["capabilities"]}
        self.assertEqual(rows["private-global-layer"]["maturity"], "preview")
        self.assertEqual(rows["cross-project-hub-kit"]["maturity"], "available")
        self.assertEqual(rows["owlib-compatibility"]["maturity"], "preview")
        self.assertEqual(rows["team-hub-and-sync"]["maturity"], "post-v1")
        for capability_id in (
            "private-global-layer",
            "cross-project-hub-kit",
            "owlib-compatibility",
            "team-hub-and-sync",
        ):
            self.assertTrue((ROOT / rows[capability_id]["evidence"]).is_file())
        for row in rows.values():
            self.assertTrue(row.get("documentation"))
            self.assertTrue(row.get("evidence"))
            self.assertLessEqual(row["source_retrieved_at"], "2026-07-29")

    def test_decision_examples_route_remote_team_need_to_roadmap(self) -> None:
        self.assertIn("A client wants a remote shared service", DOC)
        self.assertIn("Record it as post-v1 Team Hub/Sync roadmap work", DOC)


if __name__ == "__main__":
    unittest.main()
