from __future__ import annotations
import datetime as dt
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_research_memory as research  # noqa: E402

NOW = dt.datetime(2026, 8, 12, tzinfo=dt.timezone.utc)
def record(identifier, mutability, verified, scope="project_user"):
    return {"stable_id": identifier, "record_type": "source_record", "knowledge_scope": scope, "research_reason": "tool release compatibility", "context": "tool release", "source_revision": "v1", "source_mutability": mutability, "source_hash": "a" * 64, "lifecycle": "reviewed", "relations": [], "retrieved_at": "2026-01-01T00:00:00Z", "verified_at": verified}

class ResearchMemoryTests(unittest.TestCase):
    def test_mutability_freshness_and_reuse_are_distinct(self):
        records = [record("paper", "immutable", "2020-01-01T00:00:00Z"), record("release", "versioned", "2026-08-01T00:00:00Z"), record("docs", "mutable", "2026-07-01T00:00:00Z")]
        result = research.recall(records, query="tool release", allowed_scopes={"project_user"}, now=NOW)
        self.assertEqual(result["state"], "stale"); self.assertEqual(result["model_calls"], 0); self.assertEqual(result["external_search_calls"], 0)
        self.assertEqual({item["freshness"] for item in result["results"]}, {"current", "stale"})
    def test_scope_duplicate_missing_reason_and_unknown_mutability_fail_closed(self):
        private = record("private", "immutable", "2020-01-01T00:00:00Z", "enterprise")
        bad = record("bad", "unknown", "2026-08-01T00:00:00Z"); bad["research_reason"] = ""
        result = research.recall([private, bad], query="tool", allowed_scopes={"project_user"}, now=NOW)
        self.assertEqual(result["state"], "missing"); self.assertIn("research.reason", result["gaps"]); self.assertIn("research.source_mutability", result["gaps"])
        duplicate = record("same", "immutable", "2020-01-01T00:00:00Z")
        self.assertEqual(research.recall([duplicate, duplicate], query="tool", allowed_scopes={"project_user"}, now=NOW)["state"], "conflicted")
