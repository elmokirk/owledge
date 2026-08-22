from __future__ import annotations

import pathlib
import sys
import unittest
import json

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_context_compiler as compiler  # noqa: E402
import owledge_core as core  # noqa: E402
import build_project_folder_kit as project_kit  # noqa: E402


class ContextCompilerTests(unittest.TestCase):
    def test_deterministic_receipts_and_reasoned_exclusions(self) -> None:
        records = [
            {"stable_id": "b", "summary": "tool compatibility", "knowledge_scope": "project_user", "capsule_type": "idea"},
            {"stable_id": "a", "summary": "tool compatibility", "knowledge_scope": "user_global", "lifecycle": "reviewed", "capsule_type": "pattern", "research_freshness": "current"},
            {"stable_id": "c", "summary": "tool compatibility", "knowledge_scope": "enterprise", "capsule_type": "idea"},
            {"stable_id": "d", "summary": "tool compatibility", "knowledge_scope": "project_user", "capsule_type": "idea", "source_freshness": "stale"},
            {"stable_id": "e", "summary": "tool compatibility", "knowledge_scope": "project_user", "capsule_type": "idea", "data_class": "personal"},
            {"stable_id": "f", "summary": "tool compatibility", "knowledge_scope": "project_user", "capsule_type": "idea", "review_freshness": "stale"},
            {"stable_id": "g", "summary": "tool compatibility", "knowledge_scope": "project_user", "capsule_type": "idea", "research_freshness": "stale"},
            {"stable_id": "h", "summary": "tool compatibility", "knowledge_scope": "project_user", "capsule_type": "idea", "conflicted": True},
            {"stable_id": "i", "summary": "tool compatibility that cannot fit", "knowledge_scope": "project_user", "capsule_type": "idea"},
            {"stable_id": "j", "summary": "tool compatibility", "knowledge_scope": "user_global", "lifecycle": "candidate", "capsule_type": "idea"},
        ]
        kwargs = {"pack_type": "pre_research", "query": "tool", "budget_chars": 40, "allowed_scopes": {"project_user", "user_global"}}
        first = compiler.compile_pack(records, **kwargs)
        second = compiler.compile_pack(list(reversed(records)), **kwargs)
        self.assertEqual(first["digest"], second["digest"])
        self.assertEqual([item["stable_id"] for item in first["included"]], ["a", "b"])
        self.assertEqual(first["research_action"], "reuse_research_memory")
        self.assertEqual({item["reason"] for item in first["excluded"]}, {"scope", "stale_source", "privacy", "stale_review", "stale_research", "conflict", "over_budget", "unreviewed_global"})

    def test_expansion_never_bypasses_scope_or_unavailable_source(self) -> None:
        source = {"stable_id": "private", "knowledge_scope": "project_user", "source_available": False}
        self.assertEqual(compiler.expansion_receipt(source, action="deep_dive", allowed_scopes={"user_global"})["reason"], "scope")
        self.assertEqual(compiler.expansion_receipt(source, action="deep_dive", allowed_scopes={"project_user"})["reason"], "unavailable_source")

    def test_v1_core_path_is_additive_and_returns_a_receipt(self) -> None:
        result = core.build_context_pack_v1(ROOT, "OW-080-05", objective="context compiler", pack_type="task", budget_chars=4000)
        self.assertEqual(result["pack_version"], "1.0")
        self.assertEqual(len(result["digest"]), 64)
        schema = json.loads((ROOT / "templates/owledge/schemas/context-pack-v1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["pack_version"]["const"], result["pack_version"])

    def test_generated_v1_project_kits_exclude_parked_maintainer_tools(self) -> None:
        self.assertNotIn("owledge_context_compiler.py", project_kit.CORE_TOOLS)
        self.assertNotIn("validate_benchmark_baseline.py", project_kit.CORE_TOOLS)
        self.assertNotIn("validate_upgrade_notes.py", project_kit.CORE_TOOLS)


if __name__ == "__main__":
    unittest.main()
