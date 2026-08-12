from __future__ import annotations
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_health as health  # noqa: E402

class HealthTests(unittest.TestCase):
    def test_metadata_only_health_classifies_seeded_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary); index = root / ".owledge" / "indexes"; index.mkdir(parents=True)
            rows = [{"memory_id": "mem:duplicate", "source_hash": "a", "document_version": 1}, {"memory_id": "mem:duplicate", "freshness": "stale"}, {"memory_id": "mem:missing"}]
            (index / "memory-index.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            result = health.knowledge_health(root, context_budget_chars=1)
            self.assertFalse(result["passed"]); self.assertTrue(result["read_only"]); self.assertEqual(result["model_calls"], 0)
            self.assertEqual({item["code"] for item in result["issues"]}, {"duplicate_id", "stale_source", "missing_source_hash", "missing_document_revision", "context_budget_exceeded"})

    def test_managed_surface_separates_core_user_and_generated(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary); (root / "tools").mkdir(); path = root / "tools" / "a.py"; path.write_text("x", encoding="utf-8")
            (root / "OWLEDGE.md").write_text("user", encoding="utf-8"); (root / ".owledge" / "indexes").mkdir(parents=True)
            (root / "kit-manifest.json").write_text(json.dumps({"kit_version": "1", "files": [{"path": "tools/a.py", "sha256_original": "delivery"}]}), encoding="utf-8")
            rows = health.managed_surface(root)["files"]
            self.assertIn("core-managed", {row["classification"] for row in rows}); self.assertIn("user-managed", {row["classification"] for row in rows}); self.assertIn("generated", {row["classification"] for row in rows})
