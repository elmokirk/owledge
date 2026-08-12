from __future__ import annotations
import datetime as dt
import pathlib
import sys
import json
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_research_memory as research  # noqa: E402

NOW = dt.datetime(2026, 8, 12, tzinfo=dt.timezone.utc)
def record(identifier, mutability, verified, scope="project_user"):
    return {"stable_id": identifier, "record_type": "source_record", "knowledge_scope": scope, "research_reason": "tool release compatibility", "context": "tool release", "source_ref": "source:tool", "source_revision": "v1", "source_mutability": mutability, "source_hash": "a" * 64, "lifecycle": "reviewed", "relations": [], "retrieved_at": "2026-01-01T00:00:00Z", "verified_at": verified}

class ResearchMemoryTests(unittest.TestCase):
    def test_mutability_freshness_and_reuse_are_distinct(self):
        records = [record("paper", "immutable", "2020-01-01T00:00:00Z"), record("release", "versioned", "2026-08-01T00:00:00Z"), record("docs", "mutable", "2026-07-01T00:00:00Z")]
        result = research.recall(records, query="tool release", allowed_scopes={"project_user"}, now=NOW)
        self.assertEqual(result["state"], "stale"); self.assertEqual(result["model_calls"], 0); self.assertEqual(result["external_search_calls"], 0)
        self.assertEqual({item["freshness"] for item in result["results"]}, {"current", "stale"})
        self.assertIn({"stable_id": "docs", "reason": "stale_source_revision"}, result["delta_brief"])
    def test_scope_duplicate_missing_reason_and_unknown_mutability_fail_closed(self):
        private = record("private", "immutable", "2020-01-01T00:00:00Z", "enterprise")
        bad = record("bad", "unknown", "2026-08-01T00:00:00Z"); bad["research_reason"] = ""
        result = research.recall([private, bad], query="tool", allowed_scopes={"project_user"}, now=NOW)
        self.assertEqual(result["state"], "missing"); self.assertIn("research.reason", result["gaps"]); self.assertIn("research.source_mutability", result["gaps"])
        duplicate = record("same", "immutable", "2020-01-01T00:00:00Z")
        self.assertEqual(research.recall([duplicate, duplicate], query="tool", allowed_scopes={"project_user"}, now=NOW)["state"], "conflicted")

    def test_rename_stability_uses_stable_id_not_source_ref(self):
        before = record("stable", "immutable", "2020-01-01T00:00:00Z"); after = dict(before); after["source_ref"] = "renamed/source"
        self.assertEqual(research.recall([after], query="tool", allowed_scopes={"project_user"}, now=NOW)["results"][0]["stable_id"], before["stable_id"])

    def test_optional_schema_fields_are_runtime_typed(self):
        value = record("typed", "immutable", "2020-01-01T00:00:00Z"); value["source_ref"] = 1
        self.assertIn("research.source_ref", research.validate_record(value))

    def test_supported_research_layout_and_schema_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary); directory = root / ".owledge" / "research" / "sources"; directory.mkdir(parents=True)
            (directory / "records.jsonl").write_text(json.dumps(record("local", "immutable", "2020-01-01T00:00:00Z")) + "\n", encoding="utf-8")
            self.assertEqual(research.load_local_records(root)[0]["stable_id"], "local")
        schema = json.loads((ROOT / "templates" / "owledge" / "schemas" / "research-memory-v1.schema.json").read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"]); self.assertIn("research_brief", schema["properties"]["record_type"]["enum"])
