from __future__ import annotations

import pathlib
import json
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_v1_lifecycle as lifecycle
import owledge_v1_retrieval as retrieval


class V1M06LifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="v1m06-")
        self.project = pathlib.Path(self.temporary.name) / "project"
        self.project.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_candidate_replay_is_idempotent_and_never_claims_promotion(self) -> None:
        first = lifecycle.propose(self.project, kind="idea", summary="Use local evidence", source_refs=["decision:local"])
        replay = lifecycle.propose(self.project, kind="idea", summary="Use local evidence", source_refs=["decision:local"])
        self.assertTrue(first["passed"])
        self.assertFalse(first["idempotent"])
        self.assertTrue(replay["idempotent"])
        self.assertEqual(first["receipt_id"], replay["receipt_id"])
        self.assertEqual(first["promotion"], "not_available")
        normal = retrieval.recall(self.project, query="local evidence")
        self.assertFalse(normal["results"])
        self.assertIn({"stable_id": "mem:owledge:candidate:" + first["receipt_id"], "reason": "lifecycle_candidate"}, normal["exclusions"])

    def test_parked_idea_is_excluded_normally_and_resurfaces_only_for_planning(self) -> None:
        parked = lifecycle.propose(
            self.project, kind="idea", summary="Use local evidence", source_refs=["decision:local"],
            park=True, park_reason="Not needed for current MVP", reconsider_when="when local lifecycle ships",
        )
        normal = retrieval.recall(self.project, query="local evidence")
        planning = retrieval.recall(self.project, query="local evidence", purpose="planning")
        self.assertFalse(normal["results"])
        self.assertTrue(planning["results"])
        item = planning["results"][0]
        self.assertEqual(item["lifecycle"], "parked")
        self.assertEqual(item["park_reason"], "Not needed for current MVP")
        self.assertEqual(item["reconsider_when"], "when local lifecycle ships")
        self.assertEqual(parked["promotion"], "not_available")

    def test_incomplete_parked_fields_and_scope_escalation_fail_closed(self) -> None:
        missing = lifecycle.propose(self.project, kind="idea", summary="Need later", source_refs=["source:a"], park=True)
        enterprise = lifecycle.propose(self.project, kind="idea", summary="Need later", source_refs=["source:a"], scope="enterprise")
        self.assertEqual(missing["error"], "missing_park_reason")
        self.assertEqual(enterprise["error"], "candidate_scope_unsupported")
        self.assertFalse((self.project / ".owledge" / "candidates").exists())

    def test_public_propose_writes_only_a_private_candidate(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "owledge.py"), "propose", "--project-root", str(self.project), "--kind", "idea", "--summary", "Later local lifecycle", "--source-ref", "plan:v1m06", "--park", "--park-reason", "defer MVP", "--reconsider-when", "after lifecycle gate"],
            capture_output=True, text=True, check=False,
        )
        body = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(body["lifecycle"], "parked")
        self.assertEqual(body["promotion"], "not_available")

    def test_symlinked_candidate_parent_fails_before_any_external_write(self) -> None:
        outside = pathlib.Path(self.temporary.name) / "outside"
        outside.mkdir()
        (self.project / ".owledge").mkdir()
        try:
            (self.project / ".owledge" / "candidates").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation is unavailable on this Windows host")
        result = lifecycle.propose(self.project, kind="idea", summary="Stay local", source_refs=["source:local"])
        self.assertEqual(result["error"], "candidate_symlink_denied")
        self.assertFalse(list(outside.iterdir()))

    def test_tampered_candidate_lifecycle_never_enters_normal_or_planning_recall(self) -> None:
        created = lifecycle.propose(self.project, kind="idea", summary="Stay parked", source_refs=["source:local"], park=True, park_reason="later", reconsider_when="planning")
        path = self.project / created["candidate_path"]
        path.write_text(path.read_text(encoding="utf-8").replace('lifecycle: "parked"', 'lifecycle: "reviewed"'), encoding="utf-8")
        normal = retrieval.recall(self.project, query="stay parked")
        planning = retrieval.recall(self.project, query="stay parked", purpose="planning")
        self.assertFalse(normal["results"])
        self.assertFalse(planning["results"])
        self.assertIn({"stable_id": "mem:owledge:candidate:" + created["receipt_id"], "reason": "lifecycle_tombstoned"}, normal["exclusions"])


if __name__ == "__main__":
    unittest.main()
