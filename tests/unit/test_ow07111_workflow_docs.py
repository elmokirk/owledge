"""Contract tests for OW-071-11's beginner workflow and authority documentation."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / "docs" / "how-owledge-works.md"


class WorkflowDocumentationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_canonical_workflow_page_has_diagram_and_prose_fallback(self) -> None:
        self.assertIn("```mermaid", self.text)
        self.assertIn("The same flow in words", self.text)
        for phrase in (
            "intent and permitted scope",
            "reviewed project Markdown",
            "Evidence and handoff",
            "Independent review",
            "human curator",
            "rebuilt",
        ):
            self.assertIn(phrase, self.text)

    def test_authority_matrix_covers_required_actors_and_columns(self) -> None:
        header = "| Action | Actor | Trigger | Default | Side effect | Authority | Recovery |"
        self.assertIn(header, self.text)
        for actor in (
            "project instructions",
            "Owledge skill",
            "optional hook",
            "CLI command",
            "MCP",
            "Curate a proposal",
            "Synchronize between machines or teams",
            "background automation",
        ):
            self.assertIn(actor, self.text)

    def test_privacy_and_authority_claims_are_explicitly_bounded(self) -> None:
        for claim in (
            "Raw session capture and private user context",
            "not shared project truth",
            "no write-enabled promotion tools",
            "Only the designated curator can promote",
            "No hosted remote synchronization in v0.7.1",
            "No autonomous background scheduler",
        ):
            self.assertIn(claim, self.text)

    def test_primary_docs_route_to_workflow_page(self) -> None:
        self.assertIn("how-owledge-works.md", (ROOT / "docs" / "what-is-owledge.md").read_text(encoding="utf-8"))
        self.assertIn("how-owledge-works.md", (ROOT / "docs" / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
