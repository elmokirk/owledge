from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_null_space as null_space
import owledge_v1_lifecycle as lifecycle
import owledge_v1_retrieval as retrieval


class V1M07LifecycleHealthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="v1m07-")
        base = pathlib.Path(self.temporary.name)
        self.project_a, self.project_b, self.global_root = base / "project-a", base / "project-b", base / "global"
        (self.project_a / ".owledge").mkdir(parents=True)
        (self.project_b / ".owledge").mkdir(parents=True)
        null_space.link_project(self.project_a, self.global_root, owner_id="owner-a")
        null_space.link_project(self.project_b, self.global_root, owner_id="owner-a")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _candidate(self, summary: str = "Reuse local reviewed evidence") -> dict[str, object]:
        result = lifecycle.propose(
            self.project_a, kind="research", summary=summary, source_refs=["decision:local-v1"],
        )
        self.assertTrue(result["passed"])
        return result

    def _promote(self, candidate: dict[str, object]) -> dict[str, object]:
        result = lifecycle.review(
            self.project_a, candidate_id=str(candidate["receipt_id"]), action="promote",
            expected_revision=str(candidate["candidate_revision"]),
        )
        self.assertTrue(result["passed"], result)
        return result

    def test_promotion_is_explicit_revision_bound_and_reusable_from_a_linked_project(self) -> None:
        candidate = self._candidate()
        promoted = self._promote(candidate)
        replay = lifecycle.review(
            self.project_a, candidate_id=str(candidate["receipt_id"]), action="promote",
            expected_revision=str(candidate["candidate_revision"]),
        )
        local = retrieval.recall(self.project_a, query="local reviewed evidence")
        shared = retrieval.recall(
            self.project_b, query="local reviewed evidence", scopes={"user_global"}, include_user_global=True,
        )
        self.assertFalse(local["results"])
        self.assertEqual(len(shared["results"]), 1)
        self.assertEqual(shared["results"][0]["lifecycle"], "reviewed")
        self.assertEqual(promoted["state"], "reviewed")
        self.assertTrue(replay["idempotent"])
        self.assertEqual(replay["transition_id"], promoted["transition_id"])
        self.assertTrue((self.global_root / str(promoted["canonical"]["canonical_path"])).is_file())

    def test_revision_conflict_and_withdrawn_source_do_not_mutate_or_reactivate_canonical_state(self) -> None:
        candidate = self._candidate()
        candidate_path = self.project_a / str(candidate["candidate_path"])
        candidate_path.write_text(candidate_path.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
        conflict = lifecycle.review(
            self.project_a, candidate_id=str(candidate["receipt_id"]), action="promote",
            expected_revision=str(candidate["candidate_revision"]),
        )
        self.assertEqual(conflict["error"], "candidate_revision_conflict")
        self.assertFalse((self.global_root / "reviewed").exists())

        fresh = self._candidate("Withdrawn source remains excluded")
        promoted = self._promote(fresh)
        (self.project_a / str(fresh["candidate_path"])).unlink()
        recalled = retrieval.recall(
            self.project_b, query="withdrawn source", scopes={"user_global"}, include_user_global=True,
        )
        self.assertFalse(recalled["results"])
        self.assertIn({"stable_id": promoted["canonical"]["canonical_id"], "reason": "freshness_withdrawn"}, recalled["exclusions"])
        self.assertTrue((self.global_root / str(promoted["canonical"]["canonical_path"])).is_file())

    def test_park_reject_and_supersede_create_explicit_terminal_state_and_tombstone(self) -> None:
        candidate = self._candidate("Park this local feature")
        parked = lifecycle.review(
            self.project_a, candidate_id=str(candidate["receipt_id"]), action="park",
            expected_revision=str(candidate["candidate_revision"]), reason="not in current MVP", reconsider_when="after GA",
        )
        self.assertTrue(parked["passed"])
        planning = retrieval.recall(self.project_a, query="local feature", purpose="planning")
        self.assertEqual(planning["results"][0]["park_reason"], "not in current MVP")

        promoted = self._promote(self._candidate("Supersede this local decision"))
        retired = lifecycle.review(
            self.project_a, candidate_id=str(promoted["candidate_id"]), action="supersede",
            expected_revision=str(promoted["candidate_revision"]), reason="replaced by local decision v2", superseded_by="decision:v2",
        )
        self.assertTrue(retired["passed"])
        tombstone = self.project_a / ".owledge" / "tombstones" / f"{promoted['candidate_id']}.json"
        self.assertTrue(tombstone.is_file())
        recalled = retrieval.recall(
            self.project_b, query="local decision", scopes={"user_global"}, include_user_global=True,
        )
        self.assertFalse(recalled["results"])
        self.assertIn({"stable_id": promoted["canonical"]["canonical_id"], "reason": "freshness_tombstoned"}, recalled["exclusions"])

    def test_health_reports_only_safe_ids_and_counts_then_local_sync_repairs_index_drift(self) -> None:
        candidate = self._candidate("Sensitive body must never appear in health")
        self._promote(candidate)
        debt = self._candidate("Pending private lifecycle review")
        health = lifecycle.health(self.project_a, context_budget=8)
        rendered = json.dumps(health)
        kinds = {item["kind"] for item in health["checks"]}
        self.assertIn("promotion_debt", kinds)
        self.assertIn("context_overflow", kinds)
        self.assertIn("index_drift", kinds)
        self.assertNotIn("Sensitive body must never appear in health", rendered)
        self.assertNotIn("Pending private lifecycle review", rendered)
        self.assertEqual(health["body_telemetry"], "excluded")

        synced = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "owledge.py"), "sync", "--project-root", str(self.project_a), "--rebuild-index"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(synced.returncode, 0, synced.stderr)
        self.assertTrue(json.loads(synced.stdout)["passed"])
        after = lifecycle.health(self.project_a, context_budget=8)
        self.assertNotIn("index_drift", {item["kind"] for item in after["checks"]})
        self.assertTrue(debt["candidate_path"])

    def test_public_review_requires_revision_and_doctor_exposes_privacy_safe_health(self) -> None:
        candidate = self._candidate("CLI review receipt")
        reviewed = subprocess.run(
            [
                sys.executable, str(ROOT / "tools" / "owledge.py"), "review", "--project-root", str(self.project_a),
                "--candidate-id", str(candidate["receipt_id"]), "--action", "promote",
                "--expected-revision", str(candidate["candidate_revision"]),
            ], capture_output=True, text=True, check=False,
        )
        self.assertEqual(reviewed.returncode, 0, reviewed.stderr)
        self.assertEqual(json.loads(reviewed.stdout)["state"], "reviewed")
        doctor = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "owledge.py"), "doctor", "--project-root", str(self.project_a)],
            capture_output=True, text=True, check=False,
        )
        body = json.loads(doctor.stdout)
        self.assertIn("v1_lifecycle_health", body)
        self.assertNotIn("CLI review receipt", json.dumps(body["v1_lifecycle_health"]))

    def test_index_rebuild_rejects_a_prepared_symlink_before_external_write(self) -> None:
        candidate = self._candidate("Index containment check")
        self._promote(candidate)
        outside = pathlib.Path(self.temporary.name) / "outside"
        outside.mkdir()
        indexes = self.project_a / ".owledge" / "indexes"
        try:
            indexes.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation is unavailable on this Windows host")
        rebuilt = null_space.rebuild_index(self.project_a)
        self.assertEqual(rebuilt["error"], "index_symlink_denied")
        self.assertFalse(list(outside.iterdir()))

    def test_tampered_review_receipt_cannot_activate_or_resurface_a_candidate(self) -> None:
        candidate = self._candidate("Receipt integrity remains local")
        parked = lifecycle.review(
            self.project_a, candidate_id=str(candidate["receipt_id"]), action="park",
            expected_revision=str(candidate["candidate_revision"]), reason="later", reconsider_when="after health",
        )
        self.assertTrue(parked["passed"])
        receipt_path = self.project_a / ".owledge" / "receipts" / "reviews" / f"{candidate['receipt_id']}.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["transitions"][-1]["reconsider_when"] = ""
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        planning = retrieval.recall(self.project_a, query="receipt integrity", purpose="planning")
        self.assertFalse(planning["results"])
        self.assertIn({"stable_id": "mem:owledge:candidate:" + str(candidate["receipt_id"]), "reason": "lifecycle_tombstoned"}, planning["exclusions"])

    def test_prepared_review_or_global_directory_symlink_fails_closed_without_external_read_or_write(self) -> None:
        candidate = self._candidate("No partial promote")
        outside = pathlib.Path(self.temporary.name) / "outside"
        outside.mkdir()
        review_parent = self.project_a / ".owledge" / "receipts" / "reviews"
        review_parent.parent.mkdir(parents=True, exist_ok=True)
        try:
            review_parent.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation is unavailable on this Windows host")
        denied = lifecycle.review(
            self.project_a, candidate_id=str(candidate["receipt_id"]), action="promote",
            expected_revision=str(candidate["candidate_revision"]),
        )
        self.assertFalse(denied["passed"])
        self.assertFalse((self.global_root / "reviewed").exists())
        self.assertFalse(list(outside.iterdir()))

    def test_health_rejects_prepared_index_symlink_without_external_read(self) -> None:
        candidate = self._candidate("No external health read")
        self._promote(candidate)
        outside = pathlib.Path(self.temporary.name) / "outside"
        outside.mkdir()
        index_path = self.project_a / ".owledge" / "indexes" / "user-global-index.jsonl"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            index_path.symlink_to(outside / "secret.txt")
        except OSError:
            self.skipTest("symlink creation is unavailable on this Windows host")
        health = lifecycle.health(self.project_a)
        self.assertIn({"kind": "index_path_invalid", "severity": "error", "id": "user_global"}, health["checks"])
        self.assertNotIn("secret", json.dumps(health))

    def test_global_scan_rejects_prepared_reviewed_directory_symlink(self) -> None:
        outside = pathlib.Path(self.temporary.name) / "outside"
        outside.mkdir()
        reviewed = self.global_root / "reviewed"
        try:
            reviewed.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation is unavailable on this Windows host")
        scanned = null_space.scan_user_global(self.project_a)
        self.assertFalse(scanned["passed"])
        self.assertEqual(scanned["error"], "global_reviewed_symlink_denied")

    def test_health_rejects_symlinked_candidate_directory_without_enumerating_external_names(self) -> None:
        outside = pathlib.Path(self.temporary.name) / "outside"
        outside.mkdir()
        (outside / "private-candidate-name.md").write_text("not local", encoding="utf-8")
        candidate_dir = self.project_a / ".owledge" / "candidates"
        try:
            candidate_dir.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation is unavailable on this Windows host")
        health = lifecycle.health(self.project_a)
        self.assertFalse(health["passed"])
        self.assertEqual(health["error"], "candidate_directory_symlink_denied")
        self.assertNotIn("private-candidate-name", json.dumps(health))

    def test_terminal_transition_preflights_tombstone_path_before_mutating_review_state(self) -> None:
        candidate = self._candidate("No partial terminal transition")
        outside = pathlib.Path(self.temporary.name) / "outside"
        outside.mkdir()
        tombstones = self.project_a / ".owledge" / "tombstones"
        try:
            tombstones.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation is unavailable on this Windows host")
        denied = lifecycle.review(
            self.project_a, candidate_id=str(candidate["receipt_id"]), action="reject",
            expected_revision=str(candidate["candidate_revision"]), reason="invalid source",
        )
        self.assertFalse(denied["passed"])
        receipt = self.project_a / ".owledge" / "receipts" / "reviews" / f"{candidate['receipt_id']}.json"
        self.assertFalse(receipt.exists())
        self.assertFalse(list(outside.iterdir()))


if __name__ == "__main__":
    unittest.main()
