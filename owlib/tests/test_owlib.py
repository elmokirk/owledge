from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

from owlib import core, modules, pi, quality, skills


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_project(root: pathlib.Path, project_id: str, tag: str, reviewed: bool = True) -> pathlib.Path:
    project = root / project_id
    write(
        project / "OWLEDGE.md",
        f"""---
memory_id: "mem:test:test:{project_id}:project_context:root"
project_id: "{project_id}"
doc_type: "project_context"
status: "active"
visibility: "private"
semantic_title: "{project_id}"
summary: "Project context for {project_id}."
review_status: "approved"
sanitization_status: "not_required"
---

# {project_id}
""",
    )
    status = "reviewed" if reviewed else "draft"
    review_status = "approved" if reviewed else "unreviewed"
    write(
        project / ".owledge" / "patterns" / f"{tag}.md",
        f"""---
memory_id: "mem:test:test:{project_id}:pattern:{tag}"
project_id: "{project_id}"
doc_type: "pattern"
status: "{status}"
visibility: "private"
data_class: "internal"
semantic_title: "{tag} pattern"
summary: "Reusable {tag} pattern."
concept_tags:
  - "{tag}"
problem_patterns:
  - "{tag}"
architecture_patterns:
  - "markdown-hub"
failure_modes:
  - "context-loss"
reusable_lessons:
  - "Keep candidate reports reviewed before promotion."
review_status: "{review_status}"
sanitization_status: "not_required"
---

# {tag}
""",
    )
    write(
        project / ".owledge" / "sessions" / "raw" / "session.md",
        "---\ndoc_type: \"session\"\n---\n\n# Raw session\n",
    )
    write(
        project / ".owledge" / "lessons" / "unsafe-shared.md",
        f"""---
memory_id: "mem:test:test:{project_id}:lesson:unsafe"
project_id: "{project_id}"
doc_type: "lesson"
status: "reviewed"
visibility: "shared"
data_class: "internal"
semantic_title: "Unsafe shared lesson"
summary: "Missing sanitization."
review_status: "approved"
sanitization_status: "not_required"
---

# Unsafe
""",
    )
    return project


def make_legacy_project(root: pathlib.Path, project_id: str) -> pathlib.Path:
    project = make_project(root, project_id, "legacy")
    (project / "OWLEDGE.md").rename(project / "PROJECT_CONTEXT.md")
    (project / ".owledge").rename(project / "agent-memory")
    return project


class OwlibTests(unittest.TestCase):
    def test_core_sync_index_and_parallel_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            library = base / "owl-library"
            project_a = make_project(base, "project-a", "agent-memory")
            project_b = make_project(base, "project-b", "agent-memory")

            core.init_library(library)
            core.register_project(library, project_a)
            core.register_project(library, project_b)
            sync = core.sync_library(library, reviewed_only=True)
            self.assertEqual(sync["projects"][0]["rejected"], 1)
            self.assertEqual(sync["projects"][1]["rejected"], 1)

            index = core.build_index(library)
            self.assertEqual(index["records"], 4)
            records = core.read_jsonl(library / "indexes" / "records.jsonl")
            self.assertFalse(any("sessions" in row["source_path"] for row in records))
            self.assertFalse(any("unsafe-shared" in row["source_path"] for row in records))
            self.assertTrue(all(row["source_id"].startswith("owlib-source:") for row in records))

            parallels = core.find_parallel_candidates(library)
            self.assertGreaterEqual(parallels["candidates"], 1)

    def test_current_layout_is_default_and_legacy_requires_explicit_migration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            library = base / "owl-library"
            current = make_project(base, "current", "current")
            legacy = make_legacy_project(base, "legacy")
            core.init_library(library)

            registered = core.register_project(library, current)
            self.assertEqual(registered["project"]["layout"], "current")
            with self.assertRaisesRegex(ValueError, "requires explicit --legacy-layout"):
                core.register_project(library, legacy)

            with self.assertWarnsRegex(DeprecationWarning, "legacy PROJECT_CONTEXT"):
                migrated = core.register_project(library, legacy, allow_legacy=True)
            self.assertEqual(migrated["project"]["layout"], "legacy")
            sync = core.sync_library(library)
            self.assertEqual({row["layout"] for row in sync["projects"]}, {"current", "legacy"})

    def test_rejects_mixed_layout_missing_entrypoint_and_unreviewed_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            project = make_project(base, "current", "current", reviewed=False)
            with self.assertRaisesRegex(ValueError, "Project path does not exist"):
                core.validate_owledge_project(base / "missing")
            write(project / "PROJECT_CONTEXT.md", "# legacy entrypoint\n")
            (project / ".owledge").rename(project / "agent-memory")
            (project / ".owledge").mkdir()
            with self.assertRaisesRegex(ValueError, "Mixed current/legacy"):
                core.validate_owledge_project(project)
            with self.assertRaisesRegex(ValueError, "Mixed current/legacy"):
                core.validate_owledge_project(project, allow_legacy=True)

            project = make_project(base, "safe-current", "draft", reviewed=False)
            records, rejected = core.iter_importable_records(project)
            self.assertEqual(len(records), 1)
            self.assertIn("not-reviewed", {row["reason"] for row in rejected})
            self.assertFalse(any("/sessions/" in row["source_path"] for row in records))

    def test_path_escape_is_rejected_when_a_markdown_symlink_is_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            project = make_project(base, "current", "current")
            external = base / "outside.md"
            write(external, "---\nstatus: reviewed\n---\n# outside\n")
            link = project / ".owledge" / "patterns" / "outside.md"
            try:
                link.symlink_to(external)
            except OSError:
                self.skipTest("symlink creation is unavailable on this platform")
            records, rejected = core.iter_importable_records(project)
            self.assertFalse(any(row["source_path"].endswith("outside.md") for row in records))
            self.assertIn("path-escape", {row["reason"] for row in rejected})

    def test_path_containment_rejects_an_external_resolved_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            project = make_project(base, "current", "current")
            external = base / "outside.md"
            write(external, "# outside\n")
            self.assertFalse(core.is_within_project(project, external))
            self.assertTrue(core.is_within_project(project, project / "OWLEDGE.md"))

    def test_sync_cli_rejects_conflicting_review_scope_flags(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "owlib", "sync", "--reviewed-only", "--include-unreviewed"],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(pathlib.Path(__file__).resolve().parents[1] / "src")},
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("not allowed with argument", completed.stderr)

    def test_skill_export_all_runtimes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp)
            for runtime, file_name in skills.RUNTIME_FILES.items():
                result = skills.export_skills(runtime, out / runtime)
                self.assertTrue(result["passed"])
                text = (out / runtime / file_name).read_text(encoding="utf-8")
                self.assertIn("owlib-pi-agent", text)
                self.assertTrue((out / runtime / "skills" / "owlib-core" / "SKILL.md").exists())

    def test_module_install_remove_preserves_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            library = pathlib.Path(tmp) / "owl-library"
            core.init_library(library)
            report = library / "reports" / "pi-agent" / "user-report.md"
            write(report, "# keep me\n")
            for module_name in modules.BUILTIN_MODULES:
                modules.install_module(library, module_name)
                self.assertTrue((library / "modules" / module_name / "module.json").exists())
                self.assertTrue((library / "modules" / module_name / "README.md").exists())
            modules.remove_module(library, "pi-agent")
            self.assertFalse((library / "modules" / "pi-agent").exists())
            self.assertTrue(report.exists())

    def test_growth_and_pi_outputs_are_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            library = base / "owl-library"
            project_a = make_project(base, "project-a", "agent-memory")
            project_b = make_project(base, "project-b", "agent-memory")
            core.init_library(library)
            core.register_project(library, project_a)
            core.register_project(library, project_b)
            core.sync_library(library, reviewed_only=True)
            core.build_index(library)

            candidate = core.growth_promote_candidate(library, "Reusable Memory Hub", "test-source")
            self.assertIn("candidate", pathlib.Path(candidate["path"]).read_text(encoding="utf-8"))

            report = pi.pi_report(library)
            redteam = pi.redteam(library)
            self.assertTrue(pathlib.Path(report["path"]).exists())
            self.assertEqual(redteam["score"], 95)
            self.assertTrue(redteam["passed"])

    def test_quality_and_benchmark_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            library = base / "owl-library"
            project_a = make_project(base, "project-a", "agent-memory")
            project_b = make_project(base, "project-b", "agent-memory")
            core.init_library(library)
            core.register_project(library, project_a)
            core.register_project(library, project_b)
            core.sync_library(library, reviewed_only=True)
            core.build_index(library)

            doctor = quality.doctor(library)
            self.assertTrue(doctor["passed"])
            gate = quality.quality_gate(library, pathlib.Path(__file__).resolve().parents[1])
            self.assertTrue(gate["passed"])
            self.assertEqual(gate["scores"]["platform-neutral"], 100)
            bench = quality.benchmark(library, [1, 10, 100])
            self.assertTrue(bench["passed"])
            self.assertEqual(len(bench["scenarios"]), 3)


if __name__ == "__main__":
    unittest.main()
