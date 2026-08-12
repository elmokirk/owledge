from __future__ import annotations

import copy
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

sys.path.insert(0, str(REPO_ROOT / "tools"))
import owledge_contracts as contracts  # noqa: E402


def envelope() -> dict:
    return {
        "memory_id": "mem:tenant:customer:project:canonical:contract",
        "schema_version": "1.0", "profile_version": "1.0", "document_version": 1,
        "source_hash": "a" * 64, "knowledge_scope": "project_user",
        "server_project_scope": "project-001", "owner_user_id": "user-001",
        "lifecycle": "candidate", "visibility": "private", "data_class": "internal",
        "audience_ids": ["team-001"], "transferability": "project_only",
        "applies_to": ["project-001"], "edges": [{"type": "relates_to", "target": "mem:tenant:customer:project:canonical:other"}],
        "extensions": {"example.vendor": {"preserved": True}},
        "resource_refs": [{"resource_id": "resource-1", "relation": "derived_from", "locator": "opaque://source/1", "media_type": "text/plain", "content_hash": "b" * 64, "size_bytes": 12, "data_class": "internal", "availability": "available", "access_state": "authorized", "extraction_provenance": "manual"}],
    }


class ContractEnvelopeTests(unittest.TestCase):
    def test_valid_envelope_and_exact_revision_increment(self):
        first = envelope()
        self.assertEqual(contracts.validate_artifact_envelope(first), [])
        second = copy.deepcopy(first)
        second["summary"] = "material change"
        second["document_version"] = 2
        second["source_hash"] = "c" * 64
        self.assertEqual(contracts.validate_artifact_envelope(second, first), [])

    def test_rejects_unsafe_core_and_extension_shapes(self):
        value = envelope()
        value["made_up_core_key"] = True
        value["extensions"] = {"unnamespaced": True}
        value["visibility"] = "shared"
        value["data_class"] = "personal"
        errors = contracts.validate_artifact_envelope(value)
        self.assertIn("envelope.unknown_core_key:made_up_core_key", errors)
        self.assertIn("envelope.extensions_namespace", errors)
        self.assertIn("envelope.visibility_data_class", errors)

    def test_rejects_non_monotonic_revision_and_unsafe_resource_locator(self):
        first = envelope()
        second = copy.deepcopy(first)
        second["summary"] = "changed"
        second["resource_refs"][0]["locator"] = "../secret"
        errors = contracts.validate_artifact_envelope(second, first)
        self.assertIn("revision.non_monotonic", errors)
        self.assertIn("resource_ref.locator", errors)

    def test_denies_win_and_capability_receipts_are_typed(self):
        effective, receipt = contracts.resolve_settings([
            ("core", {"allow_cross_project": False, "max_context": 100}),
            ("project", {"allow_cross_project": True, "max_context": 80}),
        ])
        self.assertFalse(effective["allow_cross_project"])
        self.assertEqual(effective["max_context"], 80)
        self.assertTrue(receipt["denials"])
        capability = {"request_id": "request-1", "protocol_version": "1.0", "core_api_range": ">=1", "capability_id": "deep_dive", "operation_kind": "query", "requested_scopes": ["project_user"], "effective_permissions": ["read"], "data_class": "internal", "result": "denied", "reason_code": "scope_denied"}
        self.assertEqual(contracts.validate_capability_receipt(capability), [])


if __name__ == "__main__":
    unittest.main()
