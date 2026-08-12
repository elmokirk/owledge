from __future__ import annotations
import json
import pathlib
import sys
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_health as health  # noqa: E402

class HealthTests(unittest.TestCase):
    def test_metadata_only_health_classifies_seeded_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary); index = root / ".owledge" / "indexes"; index.mkdir(parents=True)
            rows = [{"memory_id": "mem:duplicate", "source_hash": "a", "document_version": 1, "schema_version": "1", "profile_version": "1", "edges": [{"target": "mem:missing"}]}, {"memory_id": "mem:duplicate", "freshness": "stale", "schema_version": "1", "profile_version": "1", "resource_refs": [{"availability": "withdrawn"}]}, {"memory_id": "mem:missing", "schema_version": "1", "profile_version": "1", "context_pollution": True, "body": "must never appear"}]
            (index / "memory-index.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            result = health.knowledge_health(root, context_budget_chars=1)
            self.assertFalse(result["passed"]); self.assertTrue(result["read_only"]); self.assertEqual(result["model_calls"], 0)
            codes = {item["code"] for item in result["issues"]}
            self.assertTrue({"duplicate_id", "stale_source", "missing_source_hash", "missing_document_revision", "context_budget_exceeded", "unresolved_source_ref", "context_pollution"}.issubset(codes)); self.assertNotIn("must never appear", json.dumps(result))

    def test_managed_surface_separates_core_user_and_generated(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary); (root / "tools").mkdir(); path = root / "tools" / "a.py"; path.write_text("x", encoding="utf-8")
            (root / "OWLEDGE.md").write_text("user", encoding="utf-8"); (root / ".owledge" / "indexes").mkdir(parents=True)
            (root / "kit-manifest.json").write_text(json.dumps({"kit_version": "1", "files": [{"path": "tools/a.py", "sha256_original": "delivery"}, {"path": "plugins/example.py", "sha256_original": "delivery"}, {"path": "../outside", "sha256_original": "delivery"}, {"path": "C:\\Windows\\win.ini", "sha256_original": "delivery"}]}), encoding="utf-8")
            rows = health.managed_surface(root)["files"]
            self.assertIn("core-managed", {row["classification"] for row in rows}); self.assertIn("user-managed", {row["classification"] for row in rows}); self.assertIn("generated", {row["classification"] for row in rows}); self.assertIn("extension-managed", {row["classification"] for row in rows}); self.assertNotIn("../outside", {row["path"] for row in rows}); self.assertNotIn("C:\\Windows\\win.ini", {row["path"] for row in rows})
            self.assertTrue(health.contained(root, path)); self.assertFalse(health.contained(root, pathlib.Path(temporary).parent / "outside"))

    def test_one_thousand_metadata_records_remain_bounded(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary); index = root / ".owledge" / "indexes"; index.mkdir(parents=True)
            (index / "memory-index.jsonl").write_text("\n".join(json.dumps({"memory_id": f"mem:{i}", "source_hash": "a", "document_version": 1, "schema_version": "1", "profile_version": "1"}) for i in range(1000)), encoding="utf-8")
            started = time.perf_counter(); self.assertEqual(health.knowledge_health(root)["records_scanned"], 1000); self.assertLess(time.perf_counter() - started, 5.0)

    def test_ten_and_thousand_artifact_profiles_are_bounded(self):
        for count in (10, 1000):
            with tempfile.TemporaryDirectory() as temporary:
                root = pathlib.Path(temporary); index = root / ".owledge" / "indexes"; index.mkdir(parents=True)
                (index / "memory-index.jsonl").write_text("\n".join(json.dumps({"memory_id": f"mem:{i}", "source_hash": "a", "document_version": 1, "schema_version": "1", "profile_version": "1"}) for i in range(count)), encoding="utf-8")
                started = time.perf_counter(); self.assertEqual(health.knowledge_health(root)["records_scanned"], count); self.assertLess(time.perf_counter() - started, 5.0)
