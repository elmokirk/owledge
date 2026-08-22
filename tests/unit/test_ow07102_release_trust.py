from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import os
import pathlib
import sys
import tempfile
import time
import unittest
from unittest import mock


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "tools"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "upgrade-notes"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


UPGRADE_NOTES = load_module(
    "ow07102_validate_upgrade_notes",
    TOOLS_DIR / "validate_upgrade_notes.py",
)
OWLEDGE = load_module("ow07102_owledge", TOOLS_DIR / "owledge.py")
CORE = OWLEDGE.core


class UpgradeNotesContractTests(unittest.TestCase):
    def validate_fixture(self, name: str, *, version: str = "0.7.1"):
        return UPGRADE_NOTES.validate_upgrade_notes(
            REPO_ROOT,
            changelog_path=FIXTURES / name,
            schema_path=REPO_ROOT / "docs" / "upgrade-notes-schema.json",
            version=version,
        )

    def error_codes(self, result):
        return [item["code"] for item in result["errors"]]

    def test_valid_current_note_accepts_all_breaking_values(self) -> None:
        original = (FIXTURES / "valid-current.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temp_dir:
            target = pathlib.Path(temp_dir) / "CHANGELOG.md"
            for value in ("yes", "no", "additive"):
                with self.subTest(value=value):
                    target.write_text(
                        original.replace('"additive"', f'"{value}"', 1),
                        encoding="utf-8",
                    )
                    result = UPGRADE_NOTES.validate_upgrade_notes(
                        REPO_ROOT,
                        changelog_path=target,
                        schema_path=REPO_ROOT / "docs" / "upgrade-notes-schema.json",
                        version="0.7.1",
                    )
                    self.assertTrue(result["passed"], result["errors"])
                    self.assertEqual(result["note"]["breaking"], value)

    def test_missing_breaking_fails(self) -> None:
        result = self.validate_fixture("missing-breaking.md")
        self.assertFalse(result["passed"])
        self.assertIn("missing-breaking", self.error_codes(result))

    def test_malformed_json_fails(self) -> None:
        result = self.validate_fixture("malformed-json.md")
        self.assertFalse(result["passed"])
        self.assertIn("upgrade-json-malformed", self.error_codes(result))

    def test_old_release_note_cannot_satisfy_current_release(self) -> None:
        result = self.validate_fixture("old-release-only.md")
        self.assertFalse(result["passed"])
        self.assertIn("upgrade-heading-count", self.error_codes(result))

    def test_duplicate_current_note_fails(self) -> None:
        result = self.validate_fixture("duplicate-note.md")
        self.assertFalse(result["passed"])
        self.assertIn("upgrade-heading-count", self.error_codes(result))

    def test_invalid_fields_and_diagnostics_are_deterministic(self) -> None:
        valid = (FIXTURES / "valid-current.md").read_text(encoding="utf-8")
        invalid = valid.replace(
            '"breaking": "additive",',
            '"breaking": "sometimes",\n  "extra": true,',
        ).replace(
            '"summary": "Adds a validated release contract."',
            '"summary": ""',
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            target = pathlib.Path(temp_dir) / "CHANGELOG.md"
            target.write_text(invalid, encoding="utf-8")
            kwargs = {
                "changelog_path": target,
                "schema_path": REPO_ROOT / "docs" / "upgrade-notes-schema.json",
                "version": "0.7.1",
            }
            first = UPGRADE_NOTES.validate_upgrade_notes(REPO_ROOT, **kwargs)
            second = UPGRADE_NOTES.validate_upgrade_notes(REPO_ROOT, **kwargs)
        self.assertEqual(first, second)
        self.assertEqual(
            self.error_codes(first),
            ["additional-properties", "invalid-breaking", "invalid-summary"],
        )

    def test_schema_contract_rejects_semantic_drift(self) -> None:
        schema = json.loads(
            (REPO_ROOT / "docs" / "upgrade-notes-schema.json").read_text(
                encoding="utf-8"
            )
        )
        schema["properties"]["summary"]["minLength"] = 0
        with tempfile.TemporaryDirectory() as temp_dir:
            drifted_schema = pathlib.Path(temp_dir) / "schema.json"
            drifted_schema.write_text(
                json.dumps(schema),
                encoding="utf-8",
            )
            result = UPGRADE_NOTES.validate_upgrade_notes(
                REPO_ROOT,
                changelog_path=FIXTURES / "valid-current.md",
                schema_path=drifted_schema,
                version="0.7.1",
            )
        self.assertFalse(result["passed"])
        self.assertIn("schema-contract", self.error_codes(result))

    def test_current_repository_note_and_release_trust_gate_pass(self) -> None:
        direct = UPGRADE_NOTES.validate_upgrade_notes(REPO_ROOT)
        self.assertTrue(direct["passed"], direct["errors"])
        self.assertEqual(OWLEDGE._read_upgrade_notes(REPO_ROOT), "additive")
        gate = OWLEDGE.release_trust_gate(REPO_ROOT)
        matching = [
            row for row in gate["results"] if row["name"] == "upgrade-notes-contract"
        ]
        self.assertEqual(len(matching), 1)
        self.assertTrue(matching[0]["passed"], matching[0])

    def test_upgrade_reads_release_metadata_from_source_not_target(self) -> None:
        source_note = mock.Mock(return_value="additive")
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            OWLEDGE, "_read_upgrade_notes", source_note
        ):
            target = pathlib.Path(temp_dir)
            (target / "kit-manifest.json").write_text(
                json.dumps({"kit_version": "0.6.1", "files": []}),
                encoding="utf-8",
            )
            result = OWLEDGE.upgrade_project(
                target,
                REPO_ROOT,
                dry_run=True,
                mode="safe",
                yes=False,
            )
        self.assertEqual(result["alert_level"], "additive")
        source_note.assert_called_once_with(REPO_ROOT)


class CliDispatchContractTests(unittest.TestCase):
    def upgrade_result(self, *, dry_run: bool):
        return {
            "passed": True,
            "mode": "safe",
            "dry_run": dry_run,
            "kit_version_from": "0.6.1",
            "kit_version_to": "0.7.0",
            "version_mismatch": True,
            "alert_level": "additive",
            "would_update": ["one"],
            "would_create": ["two"],
            "would_skip": [],
        }

    def test_upgrade_dry_run_apply_and_summary_dispatch(self) -> None:
        calls: list[bool] = []

        def fake_upgrade(*args, **kwargs):
            calls.append(bool(kwargs["dry_run"]))
            return self.upgrade_result(dry_run=bool(kwargs["dry_run"]))

        with mock.patch.object(OWLEDGE, "upgrade_project", side_effect=fake_upgrade):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    OWLEDGE.main(
                        [
                            "upgrade",
                            "--project-root",
                            str(REPO_ROOT),
                            "--source-root",
                            str(REPO_ROOT),
                            "--dry-run",
                        ]
                    ),
                    0,
                )
                self.assertEqual(
                    OWLEDGE.main(
                        [
                            "upgrade",
                            "--project-root",
                            str(REPO_ROOT),
                            "--source-root",
                            str(REPO_ROOT),
                            "--apply",
                        ]
                    ),
                    0,
                )
            summary = io.StringIO()
            with contextlib.redirect_stdout(summary):
                self.assertEqual(
                    OWLEDGE.main(
                        [
                            "upgrade",
                            "--project-root",
                            str(REPO_ROOT),
                            "--source-root",
                            str(REPO_ROOT),
                            "--format",
                            "summary",
                        ]
                    ),
                    0,
                )
        self.assertEqual(calls, [True, False, True])
        self.assertIn("would_update: 1", summary.getvalue())

    def test_dry_run_and_apply_are_mutually_exclusive(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as ctx:
            OWLEDGE.main(
                [
                    "upgrade",
                    "--project-root",
                    str(REPO_ROOT),
                    "--dry-run",
                    "--apply",
                ]
            )
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("not allowed with argument", stderr.getvalue())

    def test_sync_dogfood_dry_run_and_apply_dispatch(self) -> None:
        calls: list[bool] = []

        def fake_sync(root, *, dry_run):
            calls.append(bool(dry_run))
            return {"passed": True, "dry_run": dry_run}

        with mock.patch.object(OWLEDGE, "sync_dogfood", side_effect=fake_sync):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    OWLEDGE.main(
                        ["sync-dogfood", "--project-root", str(REPO_ROOT), "--dry-run"]
                    ),
                    0,
                )
                self.assertEqual(
                    OWLEDGE.main(
                        ["sync-dogfood", "--project-root", str(REPO_ROOT), "--apply"]
                    ),
                    0,
                )
        self.assertEqual(calls, [True, False])

    def test_since_flag_is_rejected_by_both_entrypoints(self) -> None:
        for entrypoint in (OWLEDGE.main, CORE.main):
            with self.subTest(entrypoint=entrypoint.__module__):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(
                    SystemExit
                ) as ctx:
                    entrypoint(
                        [
                            "--project-root",
                            str(REPO_ROOT),
                            "concept-audit",
                            "--since",
                            "2026-06-01",
                        ]
                    )
                self.assertEqual(ctx.exception.code, 2)

    def test_concept_audit_dimension_profile_and_summary_dispatch(self) -> None:
        payload = {
            "passed": True,
            "dimensions": [
                {"name": "one", "score": 90, "mode": "mechanical", "findings": []},
                {"name": "two", "score": 80, "mode": "guided", "findings": []},
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            profile = pathlib.Path(temp_dir) / "profile.json"
            profile.write_text('{"mode": "test"}\n', encoding="utf-8")
            with mock.patch.object(
                OWLEDGE.core, "concept_audit", return_value=copy.deepcopy(payload)
            ) as audited:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = OWLEDGE.main(
                        [
                            "concept-audit",
                            "--project-root",
                            str(REPO_ROOT),
                            "--dimension",
                            "one",
                            "--profile",
                            str(profile),
                            "--format",
                            "summary",
                        ]
                    )
        self.assertEqual(code, 0)
        self.assertEqual(audited.call_args.kwargs["profile"], {"mode": "test"})
        self.assertIn("one: 90", output.getvalue())
        self.assertNotIn("two: 80", output.getvalue())


class ReleasePolishRegressionTests(unittest.TestCase):
    @staticmethod
    def audit_text(*, valid: bool) -> str:
        agent = "concept-auditor" if valid else "untrusted-agent"
        return (
            "---\n"
            "type: concept-audit\n"
            f"agent_id: {agent}\n"
            "---\n"
            "# Audit\n"
        )

    def test_concept_audit_fresh_requires_canonical_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            decisions = root / "internal" / "owledge" / "decisions"
            decisions.mkdir(parents=True)
            (root / "VERSION").write_text("0.7.0\n", encoding="utf-8")
            (root / "OWLEDGE.md").write_text(
                'project_mode: "saas"\n', encoding="utf-8"
            )
            invalid = decisions / "concept-audit-2026-07-27.md"
            invalid.write_text(self.audit_text(valid=False), encoding="utf-8")
            now = time.time()
            os.utime(root / "VERSION", (now - 10, now - 10))
            os.utime(invalid, (now, now))
            rejected = OWLEDGE.concept_audit_fresh_gate(root)
            self.assertFalse(rejected["passed"])
            self.assertIn(invalid.name, rejected["ignored_audits"])

            valid = decisions / "concept-audit-2026-07-28.md"
            valid.write_text(self.audit_text(valid=True), encoding="utf-8")
            os.utime(valid, (now + 1, now + 1))
            accepted = OWLEDGE.concept_audit_fresh_gate(root)
            self.assertTrue(accepted["passed"], accepted)
            self.assertEqual(pathlib.Path(accepted["latest_audit"]).name, valid.name)

    def test_dogfood_sync_ignores_non_markdown_template_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            source = root / "templates" / "owledge" / "templates"
            internal = root / "internal" / "owledge" / "templates"
            source.mkdir(parents=True)
            internal.mkdir(parents=True)
            (source / "one-template.md").write_text("same\n", encoding="utf-8")
            (internal / "one-template.md").write_text("same\n", encoding="utf-8")
            (source / "rag-export-manifest-template.json").write_text(
                '{"source": true}\n', encoding="utf-8"
            )
            (internal / "rag-export-manifest-template.json").write_text(
                '{"internal": true}\n', encoding="utf-8"
            )
            result = CORE.dogfood_sync_check(root)
            self.assertTrue(result["passed"], result)
            (source / "one-template.md").write_text("changed\n", encoding="utf-8")
            changed = CORE.dogfood_sync_check(root)
            self.assertFalse(changed["passed"])
            self.assertEqual(changed["drifted_files"], ["one-template.md"])

    def test_upgrade_drift_uses_host_doctor_mode(self) -> None:
        with mock.patch.object(OWLEDGE, "init_project", return_value={}), mock.patch.object(
            OWLEDGE.core,
            "memory_doctor",
            return_value={
                "passed": True,
                "checks": [{"name": "version-drift", "passed": True}],
            },
        ) as doctor:
            result = OWLEDGE.upgrade_drift_check(REPO_ROOT)
        self.assertTrue(result["passed"], result)
        self.assertEqual(doctor.call_args.kwargs["mode"], "host")


if __name__ == "__main__":
    unittest.main()
