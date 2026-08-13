from __future__ import annotations

import pathlib
import json
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import owledge_null_space as null_space
import owledge_v1_retrieval as retrieval


def write_record(root: pathlib.Path, name: str, *, freshness: str = "current") -> None:
    target = root / "reviewed" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "---\n"
        f"memory_id: mem:user:global:{name[:-3]}\n"
        "knowledge_scope: user_global\n"
        "visibility: private\n"
        "summary: Local recall avoids duplicate research\n"
        "research_reason: Reuse a reviewed local source before research\n"
        f"source_freshness: {freshness}\n"
        "lifecycle: reviewed\n"
        "---\n\n"
        "# Local recall\n\nUse this reviewed essence first.\n",
        encoding="utf-8",
    )


class V1M05RetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="v1m05-")
        base = pathlib.Path(self.temporary.name)
        self.project, self.global_root = base / "project", base / "global"
        (self.project / ".owledge").mkdir(parents=True)
        null_space.link_project(self.project, self.global_root, owner_id="owner-a")
        write_record(self.global_root, "fresh.md")
        write_record(self.global_root, "stale.md", freshness="stale")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_recall_returns_essence_first_with_source_and_stale_receipts(self) -> None:
        result = retrieval.recall(
            self.project,
            query="local research",
            purpose="research",
            scopes={"user_global"},
            include_user_global=True,
        )
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["source"], "user_global/reviewed/fresh.md")
        self.assertEqual(result["progressive_disclosure"], "essence_first_permission_checked_detail")
        self.assertIn({"stable_id": "mem:user:global:stale", "reason": "freshness_stale"}, result["exclusions"])

    def test_detail_requires_explicit_scope_permission(self) -> None:
        detail_id = "user_global/mem:user:global:fresh"
        denied = retrieval.detail(self.project, detail_id=detail_id, scopes={"project_user"})
        allowed = retrieval.detail(self.project, detail_id=detail_id, scopes={"user_global"}, include_user_global=True)
        self.assertEqual(denied["error"], "detail_not_authorized")
        self.assertTrue(allowed["passed"])
        self.assertIn("Use this reviewed essence first.", allowed["content"])

    def test_empty_query_scope_opt_in_and_budget_overflow_fail_safely(self) -> None:
        self.assertEqual(retrieval.recall(self.project, query="")["error"], "empty_query")
        denied_scope = retrieval.recall(self.project, query="local", scopes={"user_global"})
        self.assertEqual(denied_scope["error"], "user_global_requires_explicit_opt_in")
        context = retrieval.build_context_pack(
            self.project,
            task_id="local",
            objective="research",
            budget_chars=12,
            scopes={"user_global"},
            include_user_global=True,
        )
        self.assertTrue(context["passed"])
        self.assertLessEqual(context["included_chars"], 12)
        self.assertTrue(context["source_receipts"])
        self.assertIn({"stable_id": "mem:user:global:fresh", "reason": "context_budget"}, context["exclusions"])

    def test_public_cli_routes_recall_and_context_through_the_local_contract(self) -> None:
        recall = subprocess.run(
            [
                sys.executable, str(ROOT / "tools" / "owledge.py"), "recall",
                "--project-root", str(self.project), "--query", "local research",
                "--scope", "user_global", "--include-user-global",
            ],
            capture_output=True, text=True, check=False,
        )
        context = subprocess.run(
            [
                sys.executable, str(ROOT / "tools" / "owledge.py"), "context",
                "--project-root", str(self.project), "--task-id", "local",
                "--objective", "research", "--budget-chars", "48", "--include-reviewed-global",
            ],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(recall.returncode, 0, recall.stderr)
        self.assertEqual(context.returncode, 0, context.stderr)
        self.assertTrue(json.loads(recall.stdout)["results"])
        self.assertLessEqual(json.loads(context.stdout)["included_chars"], 48)

        zero_budget = subprocess.run(
            [
                sys.executable, str(ROOT / "tools" / "owledge.py"), "context",
                "--project-root", str(self.project), "--task-id", "local",
                "--budget-chars", "0", "--include-reviewed-global",
            ],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(zero_budget.returncode, 2)
        self.assertEqual(json.loads(zero_budget.stdout)["error"], "budget_invalid")

        detail_id = json.loads(recall.stdout)["results"][0]["detail_id"]
        detail = subprocess.run(
            [
                sys.executable, str(ROOT / "tools" / "owledge.py"), "recall",
                "--project-root", str(self.project), "--detail-id", detail_id,
                "--scope", "user_global", "--include-user-global",
            ],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(detail.returncode, 0, detail.stderr)
        self.assertTrue(json.loads(detail.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
