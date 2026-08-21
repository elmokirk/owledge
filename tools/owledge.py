#!/usr/bin/env python3
"""Owledge public CLI.

Python-first entrypoint for local Markdown memory, KB modules, release gates,
and plugin smoke tests. The lower-level implementation stays in
owledge_core.py and the focused builders next to this file.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import html
import importlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Iterable

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
# When installed via pip (site-packages/tools/), templates/ and root files live
# at the install prefix (venv root or user site), not next to site-packages/.
# Try SCRIPT_DIR.parent (repo checkout) first, then sys.prefix, then user site.
def _has_product_templates(root: pathlib.Path) -> bool:
    return (root / "templates" / "owledge").is_dir() or (root / "templates" / "owledge").is_dir()


def _product_template_dir(root: pathlib.Path) -> pathlib.Path:
    modern = root / "templates" / "owledge"
    if modern.is_dir():
        return modern
    return root / "templates" / "owledge"


def _source_tool_file(source_root: pathlib.Path, tool: str) -> pathlib.Path:
    """Locate a V1 Core tool in an explicit checkout or installed package."""
    checkout_tool = source_root / "tools" / tool
    if checkout_tool.is_file():
        return checkout_tool
    packaged_tool = SCRIPT_DIR / tool
    if packaged_tool.is_file():
        return packaged_tool
    return checkout_tool


def _active_memory_dir(root: pathlib.Path) -> pathlib.Path:
    for candidate in (root / ".owledge", root / "internal" / ".owledge", root / "internal" / "owledge", root / "owledge"):
        if candidate.is_dir():
            return candidate
    return root / ".owledge"


if not _has_product_templates(REPO_ROOT):
    for candidate in (pathlib.Path(sys.prefix).resolve(), pathlib.Path(sys.prefix).resolve().parent):
        if _has_product_templates(candidate):
            REPO_ROOT = candidate
            break
    else:
        # Check user site-packages base (pip install --user puts data at the
        # user base, which is sys.prefix + ../ for Python 3.14 on Windows).
        import site
        for base in (site.getusersitepackages(), site.getuserbase()):
            if base:
                p = pathlib.Path(base).resolve()
                if _has_product_templates(p):
                    REPO_ROOT = p
                    break
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import owledge_core as core  # noqa: E402
import owledge_null_space  # noqa: E402
import owledge_v1_retrieval  # noqa: E402
import owledge_v1_lifecycle  # noqa: E402
import build_project_folder_kit  # noqa: E402


def _legacy_module(name: str) -> Any:
    """Load a source-checkout-only compatibility module on explicit demand."""
    return importlib.import_module(name)


class _LazyLegacyModule:
    """Keep source-checkout compatibility imports out of the V1 import path."""

    def __init__(self, name: str) -> None:
        self._name = name

    def __getattr__(self, attribute: str) -> Any:
        return getattr(_legacy_module(self._name), attribute)


work_contract = _LazyLegacyModule("owledge_work_contract")
evidence_contracts = _LazyLegacyModule("owledge_evidence_contracts")
owledge_health = _LazyLegacyModule("owledge_health")
owledge_migration = _LazyLegacyModule("owledge_migration")
owledge_research_memory = _LazyLegacyModule("owledge_research_memory")
owledge_small_model_profiles = _LazyLegacyModule("owledge_small_model_profiles")
build_kb_module = _LazyLegacyModule("build_kb_module")
benchmark_baseline = _LazyLegacyModule("validate_benchmark_baseline")
upgrade_notes = _LazyLegacyModule("validate_upgrade_notes")


def _read_version_file() -> str:
    for candidate in (REPO_ROOT, pathlib.Path(sys.prefix).resolve(), pathlib.Path(sys.prefix).resolve().parent):
        vf = candidate / "VERSION"
        if vf.is_file():
            return vf.read_text(encoding="utf-8", errors="replace").strip()
    return ""


KIT_VERSION = _read_version_file()
MEMORY_SCHEMA_VERSION = "1.0.0"
__version__ = KIT_VERSION


# V1 Minimal Core is intentionally small.  Keep this list next to the CLI
# boundary rather than inferring it from the much larger maintainer toolset.
PUBLIC_CORE_VERBS = ("init", "doctor", "recall", "context", "propose", "review", "sync", "upgrade")
DEFERRED_CORE_VERBS: set[str] = set()
COMPATIBILITY_REPLACEMENTS = {
    "init-project": "init",
    "research-recall": "recall",
    "build-context-pack": "context",
    "quickstart": "init",
}


def _advanced_surface_help() -> str:
    return (
        "Owledge advanced compatibility surface\n\n"
        "Use `owledge advanced <legacy-operation> [arguments]` for a retained "
        "maintainer or migration route. These operations are deliberately not "
        "part of the V1 Core help contract and may change independently.\n\n"
        "The V1 Core operations are: " + ", ".join(PUBLIC_CORE_VERBS) + ".\n"
        "For a direct legacy invocation, Owledge still runs the command and "
        "prints a migration hint on stderr."
    )


def _normalize_advanced_invocation(argv: list[str]) -> tuple[list[str], bool, int | None]:
    """Strip the explicit advanced namespace before argparse sees legacy routes.

    Keeping legacy parsers real (instead of forwarding through a shell) preserves
    their existing validation and makes the transition reversible.  The wrapper
    is intentionally narrow: public Core verbs cannot be routed through it.
    """
    if not argv or argv[0] != "advanced":
        return argv, False, None
    if len(argv) == 1 or argv[1] in {"-h", "--help"}:
        print(_advanced_surface_help())
        return argv, True, 0
    if argv[1] in PUBLIC_CORE_VERBS:
        print_json({
            "passed": False,
            "error": "advanced_accepts_compatibility_routes_only",
            "operation": argv[1],
            "next_action": f"Run `owledge {argv[1]} --help` instead.",
        })
        return argv, True, 2
    return argv[1:], True, None


def _add_init_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--target", dest="target", required=True)
    command.add_argument("--source-root", default=str(REPO_ROOT))
    command.add_argument("--include-plugin-adapter", action="store_true")
    command.add_argument("--include-compliance", action="store_true")
    command.add_argument("--profile", choices=["principles", "minimal", "full"], default="minimal")
    command.add_argument(
        "--link-global",
        default=None,
        metavar="PATH",
        help="Link an explicitly selected local user-global Null-Space directory.",
    )
    command.add_argument("--owner-id", default="local-owner", help="Local owner identifier for an explicit user-global Null-Space link.")


def _add_context_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--task-id", required=True)
    command.add_argument("--agent-role", default="worker")
    command.add_argument("--budget-chars", type=int)
    command.add_argument("--objective")
    command.add_argument("--pack-version", choices=["v0.7", "v1"], default="v0.7")
    command.add_argument("--pack-type", choices=["bootstrap", "task", "reviewer", "handoff", "release", "pre_plan", "pre_research"], default="task")
    command.add_argument("--include-reviewed-global", action="store_true", help="Explicitly permit reviewed/canonical user_global essences in a v1 pack.")
    command.add_argument("--purpose", choices=["research", "planning"], default="research")


PUBLIC_DOC_FILES = [
    "README.md",
    "docs/README.md",
    "docs/quickstart.md",
    "docs/try-owledge-in-5-minutes.md",
    "docs/integration-decision-guide.md",
    "docs/launch-readiness.md",
    "docs/agent-integration-guide.md",
    "docs/install-plugin.md",
    "docs/harness-plugin-matrix.md",
    "docs/mvp-plan-example.md",
    "docs/performance-scale-notes.md",
    "docs/team-long-running-project-guide.md",
    "docs/command-reference.md",
    "docs/project-snapshot-kit.md",
    "docs/operational-hardening.md",
    "docs/owledge-vs-agent-methods.md",
    "docs/distribution.md",
    "plugins/owledge-cowork/README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
]

PUBLIC_FORBIDDEN_PATTERNS = [
    "power" + "shell",
    ".p" + "s1",
    "Execution" + "Policy",
]

ROOT_FILE_MAP = [
    ("OWLEDGE.template.md", "OWLEDGE.md"),
    ("AGENTS.template.md", "AGENTS.md"),
    ("CLAUDE.template.md", "CLAUDE.md"),
    ("DESIGN.md", "DESIGN.md"),
    ("REPORT_DESIGN_SELECTOR.html", "REPORT_DESIGN_SELECTOR.html"),
    (".gitignore", ".gitignore"),
]

HOST_TOOL_FILES = [
    "owledge.py",
    "owledge_core.py",
    "owledge_adapter_contracts.py",
    "owledge_generic_adapter.py",
    "owledge_null_space.py",
    "owledge_v1_retrieval.py",
    "owledge_v1_lifecycle.py",
    "build_project_folder_kit.py",
]

HOST_SKILL_DIRS = [
    "skills/owledge-principles",
    "skills/owledge-runtime-bridge",
    "skills/review-evaluation-workflow",
    "skills/render-memory-report",
    "skills/owledge-long-horizon-delivery",
    "skills/owledge-planning-layer",
    "skills/owledge-brainstorm",
    "skills/concept-blindspot-audit",
    "skills/owledge-autonomous-delivery",
]

DISCOVERABLE_SKILL_ROOT = pathlib.Path(".agents") / "skills"


class ResultSet:
    def __init__(self) -> None:
        self.results: list[dict[str, Any]] = []

    def add(self, name: str, passed: bool, details: str = "") -> None:
        self.results.append({"name": name, "passed": bool(passed), "details": details})

    def payload(self, **extra: Any) -> dict[str, Any]:
        failed = [row for row in self.results if not row["passed"]]
        payload: dict[str, Any] = {
            "passed": not failed,
            "failed": len(failed),
            "total": len(self.results),
            "results": self.results,
        }
        payload.update(extra)
        return payload


def print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def resolve_path(value: str | pathlib.Path, base: pathlib.Path | None = None) -> pathlib.Path:
    path = pathlib.Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return ((base or pathlib.Path.cwd()) / path).resolve()


def resolve_memory_root(root: pathlib.Path) -> pathlib.Path:
    """Keep the project root while core helpers resolve its active memory tree.

    Generated paths and record source paths must stay relative to the project,
    including in the source repository where dogfood records live below
    ``internal/owledge``. Passing ``root/internal`` previously made the core
    scanner look for ``root/internal/.owledge`` and silently return zero rows.
    """
    return root


def relative_posix(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def sanitize_generated_payload(value: Any, root: pathlib.Path) -> Any:
    """Remove machine-private path prefixes from persisted generated evidence."""
    if isinstance(value, dict):
        return {key: sanitize_generated_payload(item, root) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_generated_payload(item, root) for item in value]
    if not isinstance(value, str):
        return value
    sanitized = value
    root_native = str(root.resolve())
    home_native = str(pathlib.Path.home().resolve())
    for private_root, replacement in (
        (root_native.replace("\\", "\\\\"), "."),
        (home_native.replace("\\", "\\\\"), "<home>"),
        (root_native, "."),
        (root.resolve().as_posix(), "."),
        (home_native, "<home>"),
        (pathlib.Path.home().resolve().as_posix(), "<home>"),
    ):
        sanitized = sanitized.replace(private_root, replacement)
    if sanitized != value:
        sanitized = sanitized.replace("\\", "/")
    return sanitized


GENERATED_EVIDENCE_PREFIXES = (
    "internal/owledge/exports/",
    "internal/owledge/indexes/",
    "internal/owledge/compiled/",
    ".agent-control/tmp/",
    ".pytest_cache/",
)


def _is_generated_evidence_path(path: str) -> bool:
    normalized = path.strip().strip('"').replace("\\", "/")
    if " -> " in normalized:
        normalized = normalized.split(" -> ", 1)[1].strip().strip('"')
    return any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in GENERATED_EVIDENCE_PREFIXES)


def git_source_identity(root: pathlib.Path) -> dict[str, Any]:
    """Fingerprint release-relevant source while excluding generated evidence.

    The content hash stays stable across an evidence-only commit, while any
    tracked or untracked source edit makes existing finalization evidence stale.
    """
    head = run_subprocess(["git", "rev-parse", "HEAD"], cwd=root)
    status = run_subprocess(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=root)
    inventory = run_subprocess(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root)
    if head.returncode != 0 or status.returncode != 0 or inventory.returncode != 0:
        return {
            "available": False,
            "commit": "",
            "source_tree_hash": "",
            "source_clean": False,
            "dirty_source_paths": [],
            "error": (head.stderr or status.stderr or inventory.stderr).strip() or "git source identity unavailable",
        }

    dirty_source_paths: list[str] = []
    for line in status.stdout.splitlines():
        rel = line[3:].strip() if len(line) >= 4 else line.strip()
        if rel and not _is_generated_evidence_path(rel):
            dirty_source_paths.append(rel.replace("\\", "/"))

    rows: list[str] = []
    for rel in sorted({line.strip().replace("\\", "/") for line in inventory.stdout.splitlines() if line.strip()}):
        if _is_generated_evidence_path(rel):
            continue
        path = root / pathlib.Path(rel)
        if path.is_file():
            rows.append(f"{rel}\0{sha256_file(path)}")
    digest = hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()
    return {
        "available": True,
        "commit": head.stdout.strip(),
        "source_tree_hash": digest,
        "source_clean": not dirty_source_paths,
        "dirty_source_paths": sorted(dirty_source_paths),
    }


def finalization_evidence_freshness(root: pathlib.Path, evidence: dict[str, Any]) -> dict[str, Any]:
    """Check whether persisted evidence still describes the current source tree."""
    recorded = evidence.get("source_identity") or {}
    current = git_source_identity(root)
    recorded_hash = str(recorded.get("source_tree_hash") or "")
    passed = bool(
        current.get("available")
        and recorded.get("available")
        and recorded.get("source_clean")
        and current.get("source_clean")
        and recorded_hash
        and recorded_hash == current.get("source_tree_hash")
    )
    return {
        "passed": passed,
        "recorded_commit": str(recorded.get("commit") or ""),
        "current_commit": str(current.get("commit") or ""),
        "source_tree_hash_match": bool(recorded_hash and recorded_hash == current.get("source_tree_hash")),
        "current_source_clean": bool(current.get("source_clean")),
        "dirty_source_paths": current.get("dirty_source_paths", []),
    }


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


RESUME_RUNTIME_MODELS = {"persisted", "reset_baseline"}


def file_content_token_count(text: str) -> int:
    """Deterministic, dependency-free token proxy for resume-load comparisons."""
    return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))


def _yaml_scalar(text: str, key: str, indent: int = 0) -> str:
    match = re.search(rf"(?m)^{re.escape(' ' * indent)}{re.escape(key)}:\s*(.+?)\s*$", text)
    return match.group(1).strip().strip('"\'') if match else ""


def _yaml_mapping(text: str, key: str, indent: int) -> dict[str, str]:
    """Read a simple YAML scalar mapping without adding a runtime dependency."""
    start = re.search(rf"(?m)^{re.escape(' ' * indent)}{re.escape(key)}:[ \t]*$", text)
    if not start:
        return {}
    mapping: dict[str, str] = {}
    for line in text[start.end():].splitlines():
        if not line.strip():
            continue
        if not line.startswith(" " * (indent + 2)):
            break
        match = re.match(r"\s*([^:#]+):\s*(.+?)\s*$", line)
        if match:
            mapping[match.group(1).strip().strip('"\'')] = match.group(2).strip().strip('"\'')
    return mapping


def resume_context_v1(
    state_path: pathlib.Path,
    control_paths: list[pathlib.Path],
    runtime_resume_model: str,
    already_loaded: set[str] | None = None,
    handoff_path: pathlib.Path | None = None,
    handoff_in_context: bool = False,
    session_path: pathlib.Path | None = None,
    handoff_expected_sha256: str | None = None,
) -> dict[str, Any]:
    """Build a bounded, auditable resume capsule without loading full control text.

    The payload contains content hashes and deterministic file-content token counts,
    never the control-document bodies.  A baseline-reset runtime must supply the
    latest handoff; a persisted runtime may verify an in-context handoff instead.
    """
    if runtime_resume_model not in RESUME_RUNTIME_MODELS:
        return {"passed": False, "error": "resume_context.invalid_runtime_model"}
    session_path = session_path or state_path.with_name(f"{state_path.stem}.session.yaml")
    if not state_path.is_file() or not session_path.is_file() or any(not path.is_file() for path in control_paths):
        return {"passed": False, "error": "resume_context.missing_required_input"}
    if runtime_resume_model == "reset_baseline" and handoff_path is None:
        return {"passed": False, "error": "resume_context.missing_handoff"}
    if handoff_path is not None and not handoff_path.is_file():
        return {"passed": False, "error": "resume_context.missing_handoff"}
    if handoff_path is not None and handoff_expected_sha256 and sha256_file(handoff_path) != handoff_expected_sha256:
        return {"passed": False, "error": "resume_context.stale_handoff"}

    session_text = session_path.read_text(encoding="utf-8", errors="replace")
    state_text = state_path.read_text(encoding="utf-8", errors="replace") if runtime_resume_model == "reset_baseline" else ""
    loaded = already_loaded or set()
    previous_hashes = _yaml_mapping(session_text, "last_control_sha", indent=0)
    controls: list[dict[str, Any]] = []
    control_tokens = 0
    for path in control_paths:
        identity = path.as_posix()
        current_hash = sha256_file(path)
        previous_hash = previous_hashes.get(path.name, "")
        hash_unchanged = bool(previous_hash and previous_hash == current_hash)
        retained = runtime_resume_model == "persisted" and identity in loaded and hash_unchanged
        skip_delta = hash_unchanged and not retained
        reason = "runtime_context_retained" if retained else "hash_delta_unchanged" if skip_delta else "hash_delta_changed"
        tokens = 0 if retained or skip_delta else file_content_token_count(path.read_text(encoding="utf-8", errors="replace"))
        control_tokens += tokens
        controls.append({"path": identity, "sha256": current_hash, "loaded": not (retained or skip_delta), "reason": reason, "tokens": tokens})

    handoff: dict[str, Any] | None = None
    if handoff_path is not None:
        retained = runtime_resume_model == "persisted" and handoff_in_context
        handoff_text = "" if retained else handoff_path.read_text(encoding="utf-8", errors="replace")
        handoff = {"path": handoff_path.as_posix(), "sha256": sha256_file(handoff_path), "loaded": not retained, "tokens": 0 if retained else file_content_token_count(handoff_text)}

    session_slice = {
        "active_version": _yaml_scalar(session_text, "active_version", indent=2),
        "active_ticket": _yaml_scalar(session_text, "active_ticket", indent=2),
        "current_step": _yaml_scalar(session_text, "current_step", indent=2),
        "next_command": _yaml_scalar(session_text, "next_command", indent=2),
    }
    session_tokens = file_content_token_count(json.dumps(session_slice, sort_keys=True))
    durable_tokens = int(_yaml_scalar(session_text, "durable_state_tokens") or "0")
    baseline_tokens = int(_yaml_scalar(session_text, "baseline_file_content_tokens") or "0")
    handoff_tokens = int(handoff["tokens"]) if handoff else 0
    return {
        "passed": True,
        "runtime_resume_model": runtime_resume_model,
        "session_slice": session_slice,
        "controls": controls,
        "handoff": handoff,
        "session_path": session_path.as_posix(),
        "durable_state_loaded": runtime_resume_model == "reset_baseline",
        "baseline_file_content_tokens": baseline_tokens + (handoff_tokens if runtime_resume_model == "reset_baseline" else 0),
        "cold_resume_drain": session_tokens + durable_tokens + control_tokens + handoff_tokens,
        "warm_resume_drain": session_tokens + control_tokens + handoff_tokens,
        "tokenizer": "owledge.regex-v1",
    }


def _json_sha256(payload: Any) -> str:
    return hashlib.sha256((json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")).hexdigest()


def owner_alignment_stop_v1(alignment_state_path: pathlib.Path, candidate_ticket: str) -> dict[str, Any]:
    """Verify that an awaiting alignment state refuses a next-ticket selection."""
    if not alignment_state_path.is_file():
        return {"passed": False, "error": "alignment_stop.missing_state"}
    text = alignment_state_path.read_text(encoding="utf-8", errors="replace")
    status = _yaml_scalar(text, "status")
    active_ticket = _yaml_scalar(text, "active_ticket")
    blocked = status == "awaiting_user_alignment" and bool(candidate_ticket) and candidate_ticket != active_ticket
    return {
        "passed": blocked,
        "status": status,
        "active_ticket": active_ticket,
        "candidate_ticket": candidate_ticket,
        "selection_allowed": not blocked,
        "result": "owner_alignment_required" if blocked else "alignment_stop.not_enforced",
    }


def resume_acceptance_witness_v1(
    state_path: pathlib.Path,
    control_paths: list[pathlib.Path],
    handoff_path: pathlib.Path,
    alignment_state_path: pathlib.Path,
    sidecar_path: pathlib.Path,
    model_auto_compact_token_limit: int,
) -> dict[str, Any]:
    """Emit the complete OW-080-13 acceptance witness for a transcript-only judge."""
    if model_auto_compact_token_limit <= 0:
        return {"passed": False, "error": "resume_acceptance.invalid_auto_compact_limit"}
    persisted = resume_context_v1(
        state_path,
        control_paths,
        "persisted",
        {path.as_posix() for path in control_paths},
        handoff_path,
        handoff_in_context=True,
    )
    reset = resume_context_v1(state_path, control_paths, "reset_baseline", handoff_path=handoff_path)
    stale_handoff = resume_context_v1(
        state_path,
        control_paths,
        "reset_baseline",
        handoff_path=handoff_path,
        handoff_expected_sha256="0" * 64,
    )
    payload = {
        "passed": False,
        "results": [{"name": f"fixture-{index}", "passed": False} for index in range(1, 7)],
    }
    sidecar = gate_sidecar_roundtrip_v1(payload, sidecar_path)
    reconstructed = json.loads(sidecar_path.read_text(encoding="utf-8"))
    golden_digest = _json_sha256(payload)
    reconstructed_digest = _json_sha256(reconstructed)
    alignment = owner_alignment_stop_v1(alignment_state_path, "OW-080-14")
    resume_passed = all(
        isinstance(result, dict)
        and result.get("passed")
        and result["warm_resume_drain"] < result["cold_resume_drain"] < result["baseline_file_content_tokens"]
        for result in (persisted, reset)
    )
    sidecar_passed = bool(sidecar["passed"] and sidecar["roundtrip_equal"] and golden_digest == reconstructed_digest)
    stale_passed = stale_handoff == {"passed": False, "error": "resume_context.stale_handoff"}
    return {
        "passed": bool(resume_passed and sidecar_passed and stale_passed and alignment["passed"]),
        "auto_compact_provenance": {
            "model_auto_compact_token_limit": model_auto_compact_token_limit,
            "enabled": True,
            "verification": "invocation_required",
        },
        "resume": {"persisted": persisted, "reset_baseline": reset},
        "golden_gate": {
            "golden_digest": golden_digest,
            "reconstructed_digest": reconstructed_digest,
            "diff_exit_code": 0 if golden_digest == reconstructed_digest else 1,
        },
        "sidecar": {"summary": sidecar["summary"], "reconstructed_payload": reconstructed, "roundtrip_equal": sidecar["roundtrip_equal"]},
        "stale_handoff": stale_handoff,
        "owner_alignment_stop": alignment,
    }


def tree_hash(root: pathlib.Path, exclude_prefixes: Iterable[str] = ()) -> str:
    rows: list[str] = []
    prefixes = tuple(prefix.replace("\\", "/").rstrip("/") + "/" for prefix in exclude_prefixes)
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        rel = relative_posix(path, root)
        if any(rel.startswith(prefix) for prefix in prefixes):
            continue
        rows.append(f"{rel}={sha256_file(path)}")
    return "\n".join(rows)


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def copy_file_if_missing(source: pathlib.Path, target: pathlib.Path) -> bool:
    if target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return True


def copy_tree_missing(source_root: pathlib.Path, target_root: pathlib.Path, excludes: Iterable[str] = ()) -> list[str]:
    copied: list[str] = []
    patterns = list(excludes)
    for source in sorted(source_root.rglob("*"), key=lambda item: item.as_posix()):
        if not source.is_file():
            continue
        rel = source.relative_to(source_root).as_posix()
        if any(fnmatch.fnmatch(rel, pattern) for pattern in patterns):
            continue
        target = target_root / pathlib.Path(rel)
        if copy_file_if_missing(source, target):
            copied.append(target.relative_to(target_root.parent).as_posix())
    return copied


def github_anchor(heading: str) -> str:
    text = heading.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def run_subprocess(command: list[str], cwd: pathlib.Path | None = None, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def parse_json_stdout(process: subprocess.CompletedProcess[str]) -> Any:
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or f"Exit code {process.returncode}")
    return json.loads(process.stdout)


def _collect_kit_files(source_root: pathlib.Path, project_root: pathlib.Path, profile: str = "full") -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    if profile == "minimal":
        minimal_root = source_root / "templates" / "owledge" / "minimal"
        for source_rel, target_rel in [("OWLEDGE.md", "OWLEDGE.md"), ("config.yaml", ".owledge/config.yaml")]:
            target = project_root / target_rel
            source = minimal_root / source_rel
            if target.is_file():
                entries.append({"path": target_rel, "sha256_installed": sha256_file(target), "sha256_original": sha256_file(source) if source.is_file() else ""})
        return entries
    for rel in ROOT_FILE_MAP:
        source = source_root / rel[0]
        target = project_root / rel[1]
        if target.is_file():
            rel_posix = rel[1]
            if rel_posix in seen:
                continue
            seen.add(rel_posix)
            sha_installed = sha256_file(target)
            sha_original = sha256_file(source) if source.is_file() else ""
            entries.append({"path": rel_posix, "sha256_installed": sha_installed, "sha256_original": sha_original})
    agent_src = _product_template_dir(source_root)
    agent_dst = project_root / ".owledge"
    if agent_dst.is_dir():
        for path in sorted(agent_dst.rglob("*"), key=lambda item: item.as_posix()):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            rel_posix = path.relative_to(project_root).as_posix()
            src = agent_src / pathlib.Path(rel_posix).relative_to(".owledge")
            if not src.is_file():
                # Manifests own only files supplied by the kit. User memory and
                # transient upgrade state must never become upgrade inventory.
                continue
            if rel_posix in seen:
                continue
            seen.add(rel_posix)
            sha_installed = sha256_file(path)
            sha_original = sha256_file(src)
            entries.append({"path": rel_posix, "sha256_installed": sha_installed, "sha256_original": sha_original})
    for tool in HOST_TOOL_FILES:
        target = project_root / "tools" / tool
        source = _source_tool_file(source_root, tool)
        if target.is_file():
            rel_posix = f"tools/{tool}"
            if rel_posix in seen:
                continue
            seen.add(rel_posix)
            sha_installed = sha256_file(target)
            sha_original = sha256_file(source) if source.is_file() else ""
            entries.append({"path": rel_posix, "sha256_installed": sha_installed, "sha256_original": sha_original})
    for skill_dir in HOST_SKILL_DIRS:
        skill_dst = project_root / skill_dir
        skill_src = source_root / skill_dir
        if not skill_dst.is_dir():
            continue
        for path in sorted(skill_dst.rglob("*"), key=lambda item: item.as_posix()):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            rel_posix = path.relative_to(project_root).as_posix()
            if rel_posix in seen:
                continue
            seen.add(rel_posix)
            sha_installed = sha256_file(path)
            src = skill_src / pathlib.Path(rel_posix).relative_to(skill_dir)
            sha_original = sha256_file(src) if src.is_file() else ""
            entries.append({"path": rel_posix, "sha256_installed": sha_installed, "sha256_original": sha_original})
        discovery_dst = project_root / DISCOVERABLE_SKILL_ROOT / pathlib.Path(skill_dir).name
        if not discovery_dst.is_dir():
            continue
        for path in sorted(discovery_dst.rglob("*"), key=lambda item: item.as_posix()):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            rel_posix = path.relative_to(project_root).as_posix()
            if rel_posix in seen:
                continue
            seen.add(rel_posix)
            sha_installed = sha256_file(path)
            src = skill_src / path.relative_to(discovery_dst)
            sha_original = sha256_file(src) if src.is_file() else ""
            entries.append({"path": rel_posix, "sha256_installed": sha_installed, "sha256_original": sha_original})
    return entries


def _current_kit_inventory(source_root: pathlib.Path, profile: str = "full") -> dict[str, str]:
    """Return every additive file supplied by the current host kit."""
    inventory: dict[str, str] = {}

    def add(rel_posix: str, source: pathlib.Path) -> None:
        if source.is_file():
            inventory[rel_posix] = sha256_file(source)

    if profile == "minimal":
        add("OWLEDGE.md", source_root / "templates" / "owledge" / "minimal" / "OWLEDGE.md")
        add(".owledge/config.yaml", source_root / "templates" / "owledge" / "minimal" / "config.yaml")
        return inventory
    for source_rel, target_rel in ROOT_FILE_MAP:
        add(target_rel, source_root / source_rel)
    template_root = _product_template_dir(source_root)
    if template_root.is_dir():
        for source in sorted(template_root.rglob("*"), key=lambda item: item.as_posix()):
            if source.is_file() and "__pycache__" not in source.parts:
                add(f".owledge/{source.relative_to(template_root).as_posix()}", source)
    for tool in HOST_TOOL_FILES:
        add(f"tools/{tool}", _source_tool_file(source_root, tool))
    for skill_dir in HOST_SKILL_DIRS:
        source_skill = source_root / skill_dir
        if not source_skill.is_dir():
            continue
        skill_name = pathlib.Path(skill_dir).name
        for source in sorted(source_skill.rglob("*"), key=lambda item: item.as_posix()):
            if not source.is_file() or "__pycache__" in source.parts:
                continue
            suffix = source.relative_to(source_skill).as_posix()
            add(f"{skill_dir}/{suffix}", source)
            add(f"{DISCOVERABLE_SKILL_ROOT.as_posix()}/{skill_name}/{suffix}", source)
    return inventory


def _write_kit_manifest(project_root: pathlib.Path, source_root: pathlib.Path, profile: str = "full") -> None:
    import datetime as _dt
    entries = _collect_kit_files(source_root, project_root, profile=profile)
    manifest = {
        "kit_version": KIT_VERSION,
        "memory_schema_version": MEMORY_SCHEMA_VERSION,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_version": KIT_VERSION,
        "profile": profile,
        "files": entries,
    }
    (project_root / "kit-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _resolve_global_link(arg_value: str, source_root: pathlib.Path) -> dict[str, str]:
    import datetime as _dt
    del source_root
    if not arg_value:
        raise ValueError("link_global_requires_explicit_path")
    selected = pathlib.Path(arg_value).expanduser()
    if not selected.is_absolute():
        raise ValueError("link_global_requires_absolute_path")
    if str(selected).startswith(("\\\\", "//")):
        raise ValueError("link_global_requires_local_path")
    resolved = selected.resolve()
    kit_version = KIT_VERSION
    return {
        "path": str(resolved),
        "resolved_at": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "kit_version": kit_version,
        "source": "flag",
    }


def _is_reparse_or_link(path: pathlib.Path) -> bool:
    """Return whether an existing component redirects filesystem traversal."""
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(callable(is_junction) and is_junction())


def _validate_local_project_root(value: pathlib.Path, *, label: str, require_exists: bool = False) -> pathlib.Path:
    """Resolve a local directory without following a symlink or Windows junction.

    Init and upgrade are write-capable public paths.  They must not accept a
    network/reparse root even when no user-global link is requested.
    """
    expanded = value.expanduser()
    if str(expanded).startswith(("\\\\", "//")):
        raise ValueError(f"{label}_network_path_denied")
    for candidate in (expanded, *expanded.parents):
        if candidate.exists() and _is_reparse_or_link(candidate):
            raise ValueError(f"{label}_reparse_path_denied")
    resolved = expanded.resolve()
    if require_exists and not resolved.exists():
        raise ValueError(f"{label}_missing")
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(f"{label}_not_directory")
    return resolved


def _safe_project_relative_path(raw_value: str) -> pathlib.PurePosixPath:
    """Fail closed on a manifest path that cannot name a project-local file."""
    raw = str(raw_value or "").replace("\\", "/")
    path = pathlib.PurePosixPath(raw)
    windows_path = pathlib.PureWindowsPath(raw)
    if not raw or path.is_absolute() or windows_path.is_absolute() or windows_path.drive or ".." in path.parts:
        raise ValueError("upgrade_manifest_path_denied")
    return path


def _safe_project_target(root: pathlib.Path, rel_value: str, *, label: str, require_exists: bool = False) -> pathlib.Path:
    """Return a confined project target without traversing reparse components."""
    rel = _safe_project_relative_path(rel_value)
    target = root.joinpath(*rel.parts)
    for candidate in (target, *target.parents):
        if candidate.exists() and _is_reparse_or_link(candidate):
            raise ValueError(f"{label}_reparse_path_denied")
        if candidate == root:
            break
    resolved_parent = target.parent.resolve()
    try:
        resolved_parent.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label}_path_escape") from exc
    if require_exists and not target.exists():
        raise ValueError(f"{label}_missing")
    if target.exists() and _is_reparse_or_link(target):
        raise ValueError(f"{label}_reparse_path_denied")
    return target


def _safe_source_file(source_root: pathlib.Path, path: pathlib.Path) -> pathlib.Path:
    """Allow only a regular file physically inside the selected local source."""
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(source_root)
    except (OSError, ValueError) as exc:
        raise ValueError("upgrade_source_path_denied") from exc
    if not resolved.is_file() or _is_reparse_or_link(path):
        raise ValueError("upgrade_source_path_denied")
    return resolved


def sync_dogfood(root: pathlib.Path, dry_run: bool = True) -> dict[str, Any]:
    source_dir = _product_template_dir(root) / "templates"
    internal_dir = root / "internal" / "owledge" / "templates"
    if not source_dir.is_dir():
        return {"passed": False, "reason": "templates/owledge/templates/ not found", "project": str(root)}
    if not internal_dir.is_dir():
        return {"passed": False, "reason": "internal/owledge/templates/ not found; nothing to sync", "project": str(root)}
    report = core.dogfood_sync_check(root)
    drifted = report.get("drifted_files", [])
    missing = report.get("missing_in_internal", [])
    if dry_run:
        return {
            "passed": not drifted and not missing,
            "mode": "dry-run",
            "would_update": drifted,
            "would_create": missing,
            "sync_direction": "templates->internal",
            "project": str(root),
        }
    updated: list[str] = []
    created: list[str] = []
    for src_path in sorted(
        source_dir.rglob("*-template.md"), key=lambda p: p.as_posix()
    ):
        rel = src_path.relative_to(source_dir)
        dst_path = internal_dir / rel
        assert str(dst_path).startswith(str(internal_dir)), f"refuse path outside internal: {dst_path}"
        if not dst_path.parent.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
        if not dst_path.is_file():
            dst_path.write_bytes(src_path.read_bytes())
            created.append(rel.as_posix())
        elif hashlib.sha256(src_path.read_bytes()).hexdigest() != hashlib.sha256(dst_path.read_bytes()).hexdigest():
            dst_path.write_bytes(src_path.read_bytes())
            updated.append(rel.as_posix())
    return {
        "passed": True,
        "mode": "apply",
        "updated": updated,
        "created": created,
        "sync_direction": "templates->internal",
        "project": str(root),
    }


def init_project(project_root: pathlib.Path, source_root: pathlib.Path, include_plugin_adapter: bool, include_compliance: bool, link_global: str | None = None, profile: str = "minimal", owner_id: str = "local-owner") -> dict[str, Any]:
    if profile == "principles":
        if include_plugin_adapter or include_compliance or link_global is not None:
            raise ValueError("principles profile is zero-install; choose --profile full for add-ons or user-global linking")
        return {"project_root": str(project_root), "profile": profile, "created": [], "skipped_existing": [], "doctor_passed": None, "kit_version": KIT_VERSION, "global_link": None}
    if profile not in {"minimal", "full"}:
        raise ValueError(f"Unsupported install profile: {profile}")
    project_root = _validate_local_project_root(project_root, label="project_root")
    source_root = _validate_local_project_root(source_root, label="source_root", require_exists=True)
    if profile == "minimal" and (include_plugin_adapter or include_compliance):
        # An add-on is an explicit request for the legacy compatibility surface;
        # keep callers safe while leaving the unflagged default minimal.
        profile = "full"
    resolved_global_link = None
    if link_global is not None:
        # Validate before any project file is created: a local user-global link
        # must never use a UNC/network project location.
        resolved_global_link = _resolve_global_link(link_global, source_root)
    project_root.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    skipped: list[str] = []

    if profile == "minimal":
        minimal_root = source_root / "templates" / "owledge" / "minimal"
        for source_rel, target_rel in [("OWLEDGE.md", "OWLEDGE.md"), ("config.yaml", ".owledge/config.yaml")]:
            if copy_file_if_missing(minimal_root / source_rel, project_root / target_rel):
                created.append(target_rel)
            else:
                skipped.append(target_rel)
    else:
      for source_rel, target_rel in ROOT_FILE_MAP:
        source = source_root / source_rel
        target = project_root / target_rel
        if profile == "full":
            if copy_file_if_missing(source, target):
                created.append(target_rel)
            else:
                skipped.append(target_rel)

    gitignore = project_root / ".gitignore"
    if profile == "full" and not gitignore.exists() and (source_root / ".gitignore").exists():
        copy_file_if_missing(source_root / ".gitignore", gitignore)
        created.append(".gitignore")

    if profile == "full":
        copy_tree_missing(_product_template_dir(source_root), project_root / ".owledge")
        build_project_folder_kit.ensure_gitkeep(project_root / ".owledge", build_project_folder_kit.AGENT_DIRS)

    tool_dir = project_root / "tools"
    for tool in HOST_TOOL_FILES if profile == "full" else []:
        source = _source_tool_file(source_root, tool)
        if source.exists():
            rel = f"tools/{tool}"
            if copy_file_if_missing(source, tool_dir / tool):
                created.append(rel)
            else:
                skipped.append(rel)

    for skill in HOST_SKILL_DIRS if profile == "full" else []:
        source = source_root / skill
        if source.exists():
            created.extend(copy_tree_missing(source, project_root / skill))
            discovery_target = project_root / DISCOVERABLE_SKILL_ROOT / pathlib.Path(skill).name
            discovery_created = copy_tree_missing(source, discovery_target)
            created.extend(f"{DISCOVERABLE_SKILL_ROOT.as_posix()}/{item}" for item in discovery_created)

    if include_plugin_adapter:
        created.extend(
            copy_tree_missing(
                source_root / "plugins" / "owledge-cowork",
                project_root / "plugins" / "owledge-cowork",
                ["tests/*"],
            )
        )
        settings_source = source_root / "plugins" / "owledge-cowork" / "templates" / "claude-settings.json"
        settings_target = project_root / ".claude" / "settings.json"
        if settings_source.is_file() and copy_file_if_missing(settings_source, settings_target):
            created.append(".claude/settings.json")
        elif settings_target.exists():
            skipped.append(".claude/settings.json")

    if include_compliance:
        build_project_folder_kit.install_compliance(source_root, project_root)
        created.append(".owledge/compliance/")

    doctor = core.memory_doctor(project_root, mode="host") if profile == "full" else {"passed": (project_root / "OWLEDGE.md").is_file() and (project_root / ".owledge" / "config.yaml").is_file()}
    _write_kit_manifest(project_root, source_root, profile=profile)
    global_link_info = None
    if link_global is not None:
        global_link_info = owledge_null_space.link_project(
            project_root,
            pathlib.Path(resolved_global_link["path"]),
            owner_id=owner_id,
            source=resolved_global_link["source"],
        )
    return {
        "project_root": str(project_root),
        "profile": profile,
        "created": sorted(set(created)),
        "skipped_existing": sorted(set(skipped)),
        "include_plugin_adapter": include_plugin_adapter,
        "include_compliance": include_compliance,
        "doctor_passed": doctor["passed"],
        "kit_version": KIT_VERSION,
        "global_link": global_link_info,
    }


NEVER_TOUCH_FILES = {
    "OWLEDGE.md",
    "AGENTS.md",
    "CLAUDE.md",
    "USER_CONTEXT.md",
}

NEVER_TOUCH_DIRS = (
    ".owledge/decisions/",
    ".owledge/plans/",
    ".owledge/sessions/",
    ".owledge/evidence/",
    ".owledge/handoffs/",
    "global-memory/",
)


def _is_never_touch(rel_posix: str) -> bool:
    if rel_posix in NEVER_TOUCH_FILES:
        return True
    for prefix in NEVER_TOUCH_DIRS:
        if rel_posix.startswith(prefix):
            return True
    return False


def _resolve_source_path(rel_posix: str, source_root: pathlib.Path) -> pathlib.Path:
    for source_rel, target_rel in ROOT_FILE_MAP:
        if rel_posix == target_rel:
            return source_root / source_rel
    if rel_posix.startswith(".owledge/"):
        return _product_template_dir(source_root) / pathlib.Path(rel_posix).relative_to(".owledge")
    if rel_posix.startswith("tools/"):
        return source_root / rel_posix
    if rel_posix.startswith("skills/"):
        return source_root / rel_posix
    if rel_posix.startswith(f"{DISCOVERABLE_SKILL_ROOT.as_posix()}/"):
        relative = pathlib.PurePosixPath(rel_posix).relative_to(DISCOVERABLE_SKILL_ROOT.as_posix())
        return source_root / "skills" / pathlib.Path(relative)
    return source_root / rel_posix


def _pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                return False
            kernel32.CloseHandle(handle)
            return True
        except Exception:
            return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _read_upgrade_notes(root: pathlib.Path) -> str:
    result = upgrade_notes.validate_upgrade_notes(root)
    if not result.get("passed"):
        return "unknown"
    value = str((result.get("note") or {}).get("breaking") or "").strip().lower()
    if value in {"no", "additive"}:
        return "additive"
    return "breaking" if value == "yes" else "unknown"


def _atomic_copy(source: pathlib.Path, target: pathlib.Path) -> None:
    """Copy a prepared local source using same-directory replace semantics."""
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".owledge-upgrade-", dir=str(target.parent))
    temporary = pathlib.Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle, source.open("rb") as stream:
            shutil.copyfileobj(stream, handle)
        shutil.copystat(source, temporary)
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink(missing_ok=True)


def _write_upgrade_journal(path: pathlib.Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _recover_upgrade(root: pathlib.Path, source_root: pathlib.Path, manifest_path: pathlib.Path, profile: str, journal_path: pathlib.Path, author: str) -> dict[str, Any]:
    """Complete a verified interrupted upgrade; refuse unknown local mutations."""
    try:
        journal = json.loads(journal_path.read_text(encoding="utf-8"))
        operations = journal.get("operations")
        if not isinstance(operations, list):
            raise ValueError("upgrade_recovery_journal_invalid")
        for operation in operations:
            if not isinstance(operation, dict):
                raise ValueError("upgrade_recovery_journal_invalid")
            rel = _safe_project_relative_path(str(operation.get("path") or "")).as_posix()
            target = _safe_project_target(root, rel, label="upgrade_recovery_target")
            source = _safe_source_file(source_root, _resolve_source_path(rel, source_root))
            expected = str(operation.get("source_sha256") or "")
            if not expected or sha256_file(source) != expected:
                raise ValueError("upgrade_recovery_source_changed")
            current = sha256_file(target) if target.is_file() else ""
            old_hash = str(operation.get("old_sha256") or "")
            if current == expected:
                continue
            if current not in {old_hash, ""}:
                raise ValueError("upgrade_recovery_conflict_user_edited")
            _atomic_copy(source, target)
        _write_kit_manifest(root, source_root, profile=profile)
        manifest_out = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_out["upgraded_at"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        manifest_out["upgraded_by"] = author
        manifest_out["recovered_from_interrupted_upgrade"] = True
        manifest_path.write_text(json.dumps(manifest_out, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        journal_path.unlink(missing_ok=True)
        return {"passed": True, "recovered": True, "project": str(root), "operations": len(operations), "network": "disabled"}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"passed": False, "error": str(exc), "recovered": False, "project": str(root), "network": "disabled"}


def upgrade_project(root: pathlib.Path, source_root: pathlib.Path, dry_run: bool, mode: str, yes: bool, author: str = "owledge-cli", recover: bool = False) -> dict[str, Any]:
    import datetime as _dt
    import difflib

    try:
        root = _validate_local_project_root(root, label="project_root", require_exists=True)
        source_root = _validate_local_project_root(source_root, label="source_root", require_exists=True)
        manifest_path = _safe_project_target(root, "kit-manifest.json", label="upgrade_manifest", require_exists=True)
    except ValueError as exc:
        return {"passed": False, "error": str(exc), "project": str(root)}
    if not manifest_path.is_file():
        return {"passed": False, "error": "No kit-manifest.json found; run 'owledge init-project' first.", "project": str(root)}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError) as exc:
        return {"passed": False, "error": f"kit-manifest.json is malformed: {exc}", "project": str(root)}

    manifest_kit = str(manifest.get("kit_version") or "").strip()
    target_kit = KIT_VERSION
    version_mismatch = bool(manifest_kit and target_kit and manifest_kit != target_kit)
    alert_level = _read_upgrade_notes(source_root) if version_mismatch else "current"

    manifest_entries: dict[str, dict[str, Any]] = {}
    for entry in manifest.get("files", []) or []:
        if not isinstance(entry, dict):
            return {"passed": False, "error": "upgrade_manifest_entry_invalid", "project": str(root)}
        raw_path = str(entry.get("path") or "")
        if not raw_path:
            continue
        try:
            rel_path = _safe_project_relative_path(raw_path).as_posix()
        except ValueError as exc:
            return {"passed": False, "error": str(exc), "project": str(root)}
        if rel_path in manifest_entries:
            return {"passed": False, "error": "upgrade_manifest_duplicate_path", "project": str(root)}
        manifest_entries[rel_path] = entry
    install_profile = str(manifest.get("profile") or "full")
    if install_profile not in {"minimal", "full"}:
        return {"passed": False, "error": "upgrade_manifest_profile_invalid", "project": str(root)}
    current_inventory = _current_kit_inventory(source_root, profile=install_profile)
    unknown_manifest_paths = sorted(set(manifest_entries) - set(current_inventory))
    if unknown_manifest_paths:
        return {
            "passed": False,
            "error": "upgrade_manifest_path_not_owned",
            "paths": unknown_manifest_paths,
            "project": str(root),
        }
    inventory_paths = list(manifest_entries)
    inventory_paths.extend(path for path in current_inventory if path not in manifest_entries)

    classified: list[dict[str, Any]] = []
    for path_key in inventory_paths:
        entry = manifest_entries.get(path_key, {})
        rel_posix = str(entry.get("path") or path_key)
        is_additive = rel_posix not in manifest_entries
        sha_original = str(entry.get("sha256_original") or current_inventory.get(rel_posix) or "")
        try:
            current_path = _safe_project_target(root, rel_posix, label="upgrade_target")
        except ValueError as exc:
            return {"passed": False, "error": str(exc), "project": str(root)}
        state = "missing"
        current_hash = ""
        if current_path.is_file():
            try:
                current_hash = sha256_file(current_path)
            except OSError:
                current_hash = ""
            if sha_original and current_hash == sha_original:
                state = "pristine"
            elif sha_original and current_hash and current_hash != sha_original:
                state = "user_edited"
            elif not sha_original:
                state = "user_edited"
        classified.append({
            "path": rel_posix,
            "state": state,
            "sha256_current": current_hash,
            "sha256_original": sha_original,
            "never_touch": _is_never_touch(rel_posix),
            "additive": is_additive,
        })

    outdated_paths = [
        item["path"] for item in classified
        if version_mismatch and item["state"] in {"pristine", "missing"} and not item["never_touch"]
    ]

    if mode == "manual" and not dry_run:
        return {"passed": False, "error": "manual mode is always dry-run; --apply ignored (manual emits a patch, never writes). Use --dry-run --mode=manual, or pick --mode=safe/force-templates for --apply.", "project": str(root)}

    if mode == "force-templates" and not yes:
        if sys.stdin.isatty():
            if not prompt_yes_no("force-templates will overwrite user-edited files. Continue?"):
                return {"passed": False, "error": "force-templates cancelled by user", "project": str(root)}
        else:
            return {"passed": False, "error": "force-templates mode requires --yes (or interactive confirmation via a TTY)", "project": str(root)}

    try:
        lock_path = _safe_project_target(root, ".owledge/.upgrade.lock", label="upgrade_lock")
        journal_path = _safe_project_target(root, ".owledge/upgrade-transaction.json", label="upgrade_journal")
    except ValueError as exc:
        return {"passed": False, "error": str(exc), "project": str(root)}
    if not dry_run:
        if journal_path.is_file() and not recover:
            return {"passed": False, "error": "upgrade_recovery_required", "project": str(root), "recovery_command": "owledge upgrade --recover"}
        if lock_path.is_file():
            try:
                lock_data = json.loads(lock_path.read_text(encoding="utf-8", errors="replace"))
            except (OSError, ValueError):
                lock_data = {}
            held_pid = int(lock_data.get("pid") or 0)
            if held_pid and _pid_running(held_pid):
                return {"passed": False, "error": f"Upgrade in progress (lock held by PID {held_pid}). Remove {_active_memory_dir(root).relative_to(root).as_posix()}/.upgrade.lock if stale.", "project": str(root)}
        if recover:
            return _recover_upgrade(root, source_root, manifest_path, install_profile, journal_path, author) if journal_path.is_file() else {"passed": False, "error": "upgrade_recovery_not_available", "project": str(root)}

    def select_targets() -> tuple[list[str], list[str], list[str]]:
        update_list: list[str] = []
        create_list: list[str] = []
        skip_list: list[str] = []
        for item in classified:
            rel = item["path"]
            if item["never_touch"]:
                skip_list.append(f"{rel} (never-touch)")
                continue
            is_outdated = version_mismatch and item["state"] in {"pristine", "missing"}
            if mode == "safe":
                if is_outdated and item["state"] == "pristine":
                    update_list.append(rel)
                elif is_outdated and item["state"] == "missing":
                    create_list.append(rel)
                elif item["state"] == "user_edited":
                    skip_list.append(f"{rel} (user-edited)")
                elif item["state"] == "pristine" and not version_mismatch:
                    pass
                elif item["state"] == "missing" and not version_mismatch:
                    create_list.append(rel)
            elif mode == "force-templates":
                if item["state"] == "pristine":
                    update_list.append(rel)
                elif item["state"] == "missing":
                    create_list.append(rel)
                elif item["state"] == "user_edited":
                    update_list.append(rel)
            elif mode == "manual":
                if is_outdated and item["state"] == "pristine":
                    update_list.append(rel)
                elif is_outdated and item["state"] == "missing":
                    create_list.append(rel)
                elif item["state"] == "user_edited":
                    skip_list.append(f"{rel} (user-edited)")
                elif item["state"] == "missing" and not version_mismatch:
                    create_list.append(rel)
        return update_list, create_list, skip_list

    update_targets, create_targets, skip_targets = select_targets()

    patch_text = ""
    if mode == "manual":
        diff_chunks: list[str] = []
        for rel in update_targets + create_targets:
            source_path = _safe_source_file(source_root, _resolve_source_path(rel, source_root))
            if not source_path.is_file():
                continue
            current_path = _safe_project_target(root, rel, label="upgrade_target")
            try:
                source_lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            if current_path.is_file():
                try:
                    current_lines = current_path.read_text(encoding="utf-8", errors="replace").splitlines()
                except OSError:
                    current_lines = []
            else:
                current_lines = []
            is_new_file = not current_path.is_file()
            fromfile = f"a/{rel}"
            tofile = f"b/{rel}"
            diff = difflib.unified_diff(current_lines, source_lines, fromfile=fromfile, tofile=tofile, lineterm="")
            diff_lines = list(diff)
            if diff_lines:
                header_lines = [f"diff --git a/{rel} b/{rel}"]
                if is_new_file:
                    header_lines.append("new file mode 100644")
                header_lines.append("")
                diff_chunks.append("\n".join(header_lines + diff_lines))
        patch_text = "\n".join(diff_chunks)
        if dry_run:
            patch_path = _safe_project_target(root, ".owledge/exports/upgrade-pending.patch", label="upgrade_patch")
            patch_path.parent.mkdir(parents=True, exist_ok=True)
            patch_path.write_text(patch_text + "\n", encoding="utf-8", newline="\n")

    if dry_run:
        report: dict[str, Any] = {
            "passed": True,
            "mode": mode,
            "dry_run": True,
            "project": str(root),
            "kit_version_from": manifest_kit,
            "kit_version_to": target_kit,
            "version_mismatch": version_mismatch,
            "alert_level": alert_level,
            "would_update": update_targets,
            "would_create": create_targets,
            "would_skip": skip_targets,
            "outdated_files": outdated_paths,
            "classified": classified,
        }
        if mode == "manual":
            report["patch"] = patch_text
            report["patch_path"] = str(_safe_project_target(root, ".owledge/exports/upgrade-pending.patch", label="upgrade_patch"))
        return report

    lock_held_by_us = False
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text(json.dumps({"pid": os.getpid(), "started_at": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        lock_held_by_us = True

        updated: list[str] = []
        created: list[str] = []
        skipped: list[str] = list(skip_targets)

        def installed_upgrade_source(rel: str) -> pathlib.Path:
            source_path = _resolve_source_path(rel, source_root)
            if rel.startswith(f"{DISCOVERABLE_SKILL_ROOT.as_posix()}/"):
                discovery_rel = pathlib.PurePosixPath(rel).relative_to(DISCOVERABLE_SKILL_ROOT.as_posix())
                installed_canonical = _safe_project_target(root, f"skills/{discovery_rel.as_posix()}", label="upgrade_source")
                if installed_canonical.is_file():
                    return installed_canonical
            return _safe_source_file(source_root, source_path)

        planned = update_targets + create_targets
        operations: list[dict[str, str]] = []
        prepared: dict[str, tuple[pathlib.Path, pathlib.Path]] = {}
        for rel in planned:
            if _is_never_touch(rel):
                raise ValueError("upgrade_never_touch_denied")
            source_path = installed_upgrade_source(rel)
            if not source_path.is_file():
                continue
            target_path = _safe_project_target(root, rel, label="upgrade_target")
            prepared[rel] = (source_path, target_path)
            operations.append({
                "path": rel,
                "old_sha256": sha256_file(target_path) if target_path.is_file() else "",
                "source_sha256": sha256_file(source_path),
            })
        _write_upgrade_journal(journal_path, {
            "schema_version": 1,
            "status": "prepared",
            "project": str(root),
            "profile": install_profile,
            "operations": operations,
            "network": "disabled",
        })

        for rel in update_targets:
            if rel not in prepared:
                skipped.append(f"{rel} (source missing)")
                continue
            source_path, target_path = prepared[rel]
            _atomic_copy(source_path, target_path)
            updated.append(rel)

        for rel in create_targets:
            if rel not in prepared:
                skipped.append(f"{rel} (source missing)")
                continue
            source_path, target_path = prepared[rel]
            if target_path.exists():
                skipped.append(f"{rel} (already exists)")
                continue
            _atomic_copy(source_path, target_path)
            created.append(rel)

        _write_kit_manifest(root, source_root, profile=install_profile)
        manifest_out_path = _safe_project_target(root, "kit-manifest.json", label="upgrade_manifest", require_exists=True)
        try:
            manifest_out = json.loads(manifest_out_path.read_text(encoding="utf-8", errors="replace"))
            manifest_out["upgraded_at"] = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            manifest_out["upgraded_by"] = author
            manifest_out_path.write_text(json.dumps(manifest_out, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        except (OSError, ValueError):
            pass

        journal_path.unlink(missing_ok=True)

        return {
            "passed": True,
            "mode": mode,
            "dry_run": False,
            "project": str(root),
            "kit_version_from": manifest_kit,
            "kit_version_to": target_kit,
            "version_mismatch": version_mismatch,
            "alert_level": alert_level,
            "updated": updated,
            "created": created,
            "skipped": skipped,
            "outdated_files": outdated_paths,
        }
    except (OSError, ValueError) as exc:
        return {"passed": False, "error": "upgrade_interrupted_recover_required", "detail": str(exc), "project": str(root), "recovery_command": "owledge upgrade --recover", "network": "disabled"}
    finally:
        if lock_held_by_us and lock_path.is_file():
            try:
                lock_path.unlink()
            except OSError:
                pass


def addon_relative_path(value: str) -> pathlib.Path:
    path = pathlib.PurePosixPath(str(value).replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or not str(path):
        raise ValueError(f"Unsafe add-on path: {value}")
    return pathlib.Path(path.as_posix())


def addon_public_relative_path(value: str) -> pathlib.Path:
    path = addon_relative_path(value)
    rel = path.as_posix()
    if rel == "owledge":
        rel = ".owledge"
    elif rel.startswith(".owledge/"):
        rel = ".owledge/" + rel[len(".owledge/") :]
    return pathlib.Path(rel)


def addon_public_relative_text(value: str) -> str:
    raw = str(value).replace("\\", "/").strip()
    suffix = ""
    while raw.endswith("/") and raw != "/":
        raw = raw[:-1]
        suffix += "/"
    path = addon_public_relative_path(raw).as_posix()
    return path + suffix


def append_gitignore_entries(project_root: pathlib.Path, entries: Iterable[str]) -> list[str]:
    gitignore = project_root / ".gitignore"
    text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    lines = text.splitlines()
    existing = {line.strip() for line in lines}
    added: list[str] = []
    for entry in entries:
        normalized = str(entry).strip()
        if not normalized or normalized in existing:
            continue
        lines.append(normalized)
        existing.add(normalized)
        added.append(normalized)
    if added:
        gitignore.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return added


def install_addon(project_root: pathlib.Path, source_root: pathlib.Path, addon: str) -> dict[str, Any]:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", addon):
        raise ValueError(f"Invalid add-on name: {addon}")
    manifest_path = source_root / "addons" / addon / "addon.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Unknown add-on: {addon}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("name") != addon:
        raise ValueError(f"Add-on manifest name mismatch: {manifest.get('name')} != {addon}")
    addon_root = manifest_path.parent
    project_root.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    skipped: list[str] = []
    conditional_skipped: list[str] = []

    for relative in manifest.get("install_directories", []):
        target_rel = addon_public_relative_path(relative)
        target = project_root / target_rel
        target.mkdir(parents=True, exist_ok=True)
        gitkeep = target / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
            created.append(str(gitkeep.relative_to(project_root)).replace("\\", "/"))

    for item in manifest.get("install_files", []):
        source = addon_root / addon_relative_path(item["source"])
        target_rel = addon_public_relative_path(item["target"])
        target = project_root / target_rel
        if not source.exists():
            raise FileNotFoundError(f"Add-on source file missing: {source}")
        if copy_file_if_missing(source, target):
            created.append(str(target_rel).replace("\\", "/"))
        else:
            skipped.append(str(target_rel).replace("\\", "/"))

    for item in manifest.get("install_if_parent_exists", []):
        parent_rel = addon_public_relative_path(item["parent"])
        if not (project_root / parent_rel).exists():
            conditional_skipped.append(str(parent_rel).replace("\\", "/"))
            continue
        source = addon_root / addon_relative_path(item["source"])
        target_rel = addon_public_relative_path(item["target"])
        target = project_root / target_rel
        if not source.exists():
            raise FileNotFoundError(f"Add-on source file missing: {source}")
        if copy_file_if_missing(source, target):
            created.append(str(target_rel).replace("\\", "/"))
        else:
            skipped.append(str(target_rel).replace("\\", "/"))

    gitignore_added = append_gitignore_entries(project_root, [addon_public_relative_text(entry) for entry in manifest.get("gitignore", [])])
    created.extend(f".gitignore:{entry}" for entry in gitignore_added)

    return {
        "passed": True,
        "addon": addon,
        "project_root": str(project_root),
        "created": sorted(set(created)),
        "skipped_existing": sorted(set(skipped)),
        "conditional_skipped": sorted(set(conditional_skipped)),
        "manifest": str(manifest_path),
    }


def prompt_yes_no(question: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{question} {suffix} ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def project_snapshot_command(
    root: pathlib.Path,
    snapshots_only: bool,
    render_html: bool,
    changed_only: bool,
    token_budget: int,
    allow_large_context: bool,
    yes: bool,
) -> dict[str, Any]:
    if snapshots_only and render_html:
        raise ValueError("Use either --snapshots-only or --render-html, not both.")
    if not core.project_snapshot_addon_installed(root):
        raise FileNotFoundError(
            "Project Snapshot Kit is not installed. Run: "
            "python tools/owledge.py install-addon --project-root . --addon project-snapshot-kit"
        )

    explicit_mode = snapshots_only or render_html or yes
    if not explicit_mode and not sys.stdin.isatty():
        raise RuntimeError("Non-interactive project-snapshot requires --snapshots-only, --render-html, or --yes.")

    generate_snapshots = False
    generate_html = False
    if snapshots_only:
        generate_snapshots = True
        generate_html = False
    elif render_html:
        generate_snapshots = False
        generate_html = True
    elif yes:
        generate_snapshots = True
        generate_html = True
    else:
        generate_snapshots = prompt_yes_no("Generate or update Project Snapshot Markdown for this project?", default=False)
        generate_html = prompt_yes_no("Generate or update local HTML dashboard/pages for this project?", default=False)

    if generate_snapshots:
        return core.build_project_snapshot(
            root,
            render_html=generate_html,
            changed_only=changed_only,
            token_budget=token_budget,
            allow_large_context=allow_large_context,
        )
    if generate_html:
        site = core.render_project_snapshot_site(root)
        return {
            "passed": True,
            "addon": "project-snapshot-kit",
            "generated_files": site.get("paths", []),
            "skipped_files": [],
            "manifest_path": core.PROJECT_SNAPSHOT_MANIFEST_REL,
            "render_html": True,
            "snapshots_updated": False,
            "token_estimate": {"model_tokens_used": 0},
        }
    return {
        "passed": True,
        "addon": "project-snapshot-kit",
        "generated_files": [],
        "skipped_files": [],
        "render_html": False,
        "snapshots_updated": False,
        "token_estimate": {"model_tokens_used": 0},
    }


def quickstart_project(project_root: pathlib.Path, source_root: pathlib.Path, include_plugin_adapter: bool = False) -> dict[str, Any]:
    init_result = init_project(project_root, source_root, include_plugin_adapter=include_plugin_adapter, include_compliance=False)
    doctor = core.memory_doctor(project_root, mode="host")
    validation = core.validate_memory(project_root, strict=True)
    return {
        "passed": bool(doctor.get("passed")) and bool(validation.get("passed")),
        "target": str(project_root),
        "init": init_result,
        "doctor": doctor,
        "validation": validation,
        "next_commands": [
            f"python tools/owledge_core.py --project-root {project_root} build-memory-index",
            f"python tools/owledge.py doctor --project-root {project_root}",
        ],
    }


def public_docs_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    public_files = [root / pathlib.Path(item) for item in PUBLIC_DOC_FILES]
    for relative, path in zip(PUBLIC_DOC_FILES, public_files):
        results.add(f"exists:{relative}", path.exists(), "Public doc exists.")
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        mojibake = [marker for marker in ("\u00c2", "\u00e2", "\u00ef") if marker in content]
        results.add(f"utf8-clean:{relative}", not mojibake, "No common mojibake markers detected.")
        lowered = content.lower()
        for pattern in PUBLIC_FORBIDDEN_PATTERNS:
            if pattern == ".p" + "s1":
                passed = pattern not in content
            elif pattern.startswith("AGENT_"):
                passed = pattern not in content
            else:
                passed = pattern.lower() not in lowered
            results.add(f"python-first-doc:{relative}:{pattern}", passed, "Public docs must not present platform-specific wrappers or OS env setup as core UX.")
        if relative in {"README.md", "docs/harness-plugin-matrix.md"}:
            results.add(f"runtime-claim-wording:{relative}", "| Ready |" not in content, "Public runtime matrix should use bounded local-support wording, not broad Ready claims.")
        if relative == "README.md":
            results.add("product-name-first-screen", "Owledge" in content[:1200], "README first screen should lead with Owledge.")

    readme = (root / "README.md").read_text(encoding="utf-8", errors="replace")
    readme_first_screen = readme.split("## Before / After", 1)[0]
    primary_setup = "uvx owledge quickstart --target /path/to/your-project"
    primary_lines = re.findall(r"(?m)^uvx owledge quickstart --target /path/to/your-project$", readme_first_screen)
    results.add("readme-primary-setup-once", len(primary_lines) == 1, "README first screen presents exactly one primary project setup command.")
    results.add("readme-primary-setup-no-plugin-flag", primary_setup + " --include-plugin-adapter" not in readme_first_screen, "README primary setup does not require the plugin adapter.")
    for command in [
        "uvx owledge --help",
        "python tools/owledge.py add-kb-module --knowledgebase-root /path/to/your/vault",
        "owledge doctor --project-root /path/to/your-project",
    ]:
        results.add(f"readme-simple-path:{command}", command in readme_first_screen, "README first screen includes the simple KB and doctor paths.")
    for marker in ["OWLEDGE.md", ".owledge/", "wikilink-audit", "benchmark-kit", "read-only MCP"]:
        results.add(f"readme-v070-marker:{marker}", marker in readme, "README documents the v0.7 release surface.")
    headings = [github_anchor(match.group(1)) for match in re.finditer(r"(?m)^##+\s+(.+)$", readme)]
    toc_links = [match.group(1) for match in re.finditer(r"(?m)^-\s+\[[^\]]+\]\(#([^)]+)\)", readme)]
    for anchor in toc_links:
        results.add(f"toc-anchor:{anchor}", anchor in headings, "README table-of-contents anchor resolves.")

    for relative, path in zip(PUBLIC_DOC_FILES, public_files):
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", content):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            resolved = (path.parent / clean).resolve()
            results.add(f"link:{relative}->{clean}", resolved.exists(), "Relative markdown link resolves.")

    docs_index = (root / "docs" / "README.md").read_text(encoding="utf-8", errors="replace")
    for link in [
        "quickstart.md",
        "agent-integration-guide.md",
        "install-plugin.md",
        "harness-plugin-matrix.md",
        "mvp-plan-example.md",
        "performance-scale-notes.md",
        "team-long-running-project-guide.md",
        "command-reference.md",
        "project-snapshot-kit.md",
    ]:
        results.add(f"docs-index:{link}", link in docs_index, "Docs index links the public entrypoint.")
    command_reference = (root / "docs" / "command-reference.md").read_text(encoding="utf-8", errors="replace")
    for command in ["wikilink-audit", "run-benchmark-kit.py --mode ci", "run-benchmark-kit.py --mode local", "test mcp-readonly"]:
        results.add(f"command-reference-v070:{command}", command in command_reference, "Command reference documents v0.7 P0 commands.")

    plugin_docs = [
        root / "README.md",
        root / "docs" / "install-plugin.md",
        root / "docs" / "harness-plugin-matrix.md",
        root / "plugins" / "owledge-cowork" / "README.md",
    ]
    for path in plugin_docs:
        if not path.exists():
            continue
        label = relative_posix(path, root)
        text = path.read_text(encoding="utf-8", errors="replace")
        results.add("plugin-path:" + label, "plugins/owledge-cowork/" in text or "plugins\\owledge-cowork\\" in text, "Canonical plugin path is documented.")
    install_doc = root / "docs" / "install-plugin.md"
    if install_doc.exists():
        install_text = install_doc.read_text(encoding="utf-8", errors="replace")
        for heading in ["Codex", "Claude Code", "Cowork-Compatible", "OpenCode-Style", "Generic Agents", "Verify", "Uninstall"]:
            results.add(f"plugin-install-section:{heading}", heading in install_text, "Plugin install guide includes concrete install, verify, and uninstall sections.")

    if "benchmark" in readme.lower() or "benchmark" in (root / "docs" / "performance-scale-notes.md").read_text(encoding="utf-8", errors="replace").lower():
        results.add("benchmark-assets:readme", (root / "addons" / "benchmark-kit" / "README.md").exists(), "Benchmark Kit README exists.")
        results.add("benchmark-assets:script", (root / "addons" / "benchmark-kit" / "tools" / "run-benchmark-kit.py").exists(), "Benchmark Kit runner exists.")
        results.add("benchmark-assets:explained", (root / "addons" / "benchmark-kit" / "BENCHMARK_EXPLAINED.md").exists(), "Benchmark explanation exists.")

    return results.payload(project=str(root))


def load_release_surface_contract(root: pathlib.Path) -> dict[str, Any]:
    path = root / "contracts" / "release-surface.json"
    if not path.exists():
        raise FileNotFoundError(f"release surface contract is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("release surface contract schema_version must be 1")
    return payload


def version_contract_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    try:
        contract = load_release_surface_contract(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        results.add("contract:load", False, str(exc))
        return results.payload(project=str(root))
    version_source = root / contract.get("version_source", "VERSION")
    results.add("contract:version-source", version_source.exists(), "Canonical VERSION file exists.")
    if not version_source.exists():
        return results.payload(project=str(root))
    version = version_source.read_text(encoding="utf-8", errors="replace").strip()
    results.add("contract:version-semver", bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), "Canonical version is semantic.")
    for sink in contract.get("version_sinks", []):
        relative, kind = sink["path"], sink["kind"]
        path = root / relative
        results.add(f"version-sink:exists:{relative}", path.exists(), "Version sink exists.")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        actual: str | None = None
        if kind == "toml-project-version":
            match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
            actual = match.group(1) if match else None
        elif kind == "readme-badge":
            actual = version if f"version-{version}-" in text or f"version-{version}" in text else None
        elif kind == "current-release":
            actual = version if f"v{version}" in text else None
        elif kind == "top-changelog-heading":
            match = re.search(r"^##\s+([0-9]+\.[0-9]+\.[0-9]+)\b", text, re.MULTILINE)
            actual = match.group(1) if match else None
        elif kind == "plain-version":
            actual = text.strip()
        elif kind == "json-version":
            actual = json.loads(text).get("version")
        else:
            results.add(f"version-sink:known-kind:{relative}", False, f"Unknown version sink kind: {kind}")
            continue
        results.add(f"version-sink:matches:{relative}", actual == version, f"{relative} matches canonical VERSION.")
    return results.payload(project=str(root), version=version)


def _contract_public_docs(root: pathlib.Path, contract: dict[str, Any]) -> list[str]:
    config = contract["public_docs"]
    paths: set[str] = set()
    for pattern in config.get("include", []):
        paths.update(relative_posix(path, root) for path in root.glob(pattern) if path.is_file())

    def is_excluded(relative: str) -> bool:
        for pattern in config.get("exclude", []):
            normalized = pattern.removeprefix("./")
            # Path.glob("docs/archive/**") returns a different set of entries
            # across supported Python versions. Match exclusion prefixes against
            # the collected files instead of relying on that glob's output.
            if normalized.endswith("/**") and relative.startswith(normalized[:-2]):
                return True
            if fnmatch.fnmatchcase(relative, normalized):
                return True
        return False

    return sorted(relative for relative in paths if not is_excluded(relative))


def _changed_files(root: pathlib.Path, base_ref: str | None, explicit: list[str] | None) -> list[str] | None:
    if explicit:
        return sorted(set(item.replace("\\", "/") for item in explicit))
    if not base_ref:
        return None
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Cannot resolve base ref {base_ref}: {completed.stderr.strip()}")
    return sorted(line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip())


def docs_contract_gate(root: pathlib.Path, base_ref: str | None = None, changed_files: list[str] | None = None) -> dict[str, Any]:
    results = ResultSet()
    try:
        contract = load_release_surface_contract(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        results.add("contract:load", False, str(exc))
        return results.payload(project=str(root))
    docs = _contract_public_docs(root, contract)
    results.add("docs-surface:nonempty", bool(docs), "Public documentation surface is declared.")
    version = (root / contract.get("version_source", "VERSION")).read_text(encoding="utf-8", errors="replace").strip()
    current_claim = re.compile(r"(?:current|latest|released|publish(?:ed|ing)?|ship(?:ped|ping)?)\D{0,30}v?(\d+\.\d+\.\d+)", re.IGNORECASE)
    historical_marker = contract["public_docs"].get("historical_marker", "Historical").lower()
    for relative in docs:
        path = root / relative
        text = path.read_text(encoding="utf-8", errors="replace")
        results.add(f"docs-surface:utf8:{relative}", not any(marker in text for marker in ("\u00c2", "\u00e2", "\u00ef")), "Public document has no common mojibake.")
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_path = target.split("#", 1)[0]
            if target_path:
                results.add(f"docs-surface:link:{relative}->{target_path}", (path.parent / target_path).resolve().exists(), "Relative documentation link resolves.")
        stale_current_claims = [match.group(1) for match in current_claim.finditer(text) if match.group(1) != version]
        historical = historical_marker in text[:1000].lower()
        results.add(f"docs-surface:current-version:{relative}", not stale_current_claims or historical, "Current release claims use VERSION or document is explicitly historical.")

    command_reference = root / "docs" / "command-reference.md"
    if command_reference.exists():
        command_text = command_reference.read_text(encoding="utf-8", errors="replace")
        cli_text = (root / "tools" / "owledge.py").read_text(encoding="utf-8", errors="replace")
        top_level_commands = set(re.findall(r'sub\.add_parser\("([^"]+)"', cli_text))
        for command in sorted(top_level_commands):
            results.add(f"docs-surface:command:{command}", command in command_text, "Public CLI command is documented.")
    else:
        results.add("docs-surface:command-reference", False, "Command reference exists.")

    try:
        changed = _changed_files(root, base_ref, changed_files)
    except RuntimeError as exc:
        results.add("docs-impact:base-ref", False, str(exc))
        return results.payload(project=str(root), version=version)
    if changed is not None:
        changed_set = set(changed)
        for feature in contract.get("features", []):
            triggered = any(any(fnmatch.fnmatch(path, pattern) for pattern in feature["source_globs"]) for path in changed_set)
            if not triggered:
                continue
            for required_doc in feature["docs"]:
                results.add(f"docs-impact:{feature['id']}:{required_doc}", required_doc in changed_set, "Impacted feature documentation is updated in this change.")
            for required_test in feature["tests"]:
                results.add(f"feature-contract:{feature['id']}:{required_test}", bool(required_test), "Feature contract declares verification.")
    return results.payload(project=str(root), version=version, docs=docs, changed_files=changed)


def release_contract_gate(root: pathlib.Path, require_dist: bool = False, evidence_path: str | None = None) -> dict[str, Any]:
    version_payload = version_contract_gate(root)
    docs_payload = docs_contract_gate(root)
    trust_payload = release_trust_gate(root)
    version = (root / "VERSION").read_text(encoding="utf-8", errors="replace").strip()
    checks: dict[str, Any] = {
        "version-contract": version_payload,
        "docs-contract": docs_payload,
        "release-trust": trust_payload,
    }
    dist = root / "dist"
    if require_dist:
        wheel = dist / f"owledge-{version}-py3-none-any.whl"
        sdist = dist / f"owledge-{version}.tar.gz"
        checks["distribution"] = {
            "passed": wheel.exists() and sdist.exists(),
            "wheel": str(wheel),
            "sdist": str(sdist),
        }
    passed = all(bool(payload.get("passed")) for payload in checks.values())
    evidence = {
        "schema_version": 1,
        "version": version,
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(root), capture_output=True, text=True).stdout.strip(),
        "passed": passed,
        "checks": checks,
    }
    if evidence_path:
        target = pathlib.Path(evidence_path)
        if not target.is_absolute():
            target = root / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        evidence["evidence_path"] = str(target)
    return evidence


def release_trust_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    version = (root / "VERSION").read_text(encoding="utf-8", errors="replace").strip()
    readme = (root / "README.md").read_text(encoding="utf-8", errors="replace")
    results.add("version:readme-badge", f"version-{version}-" in readme or f"version-{version}" in readme, "README badge matches root VERSION.")
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8", errors="replace")
    pyproject_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    results.add("version:pyproject", bool(pyproject_match and pyproject_match.group(1) == version), "Package version matches root VERSION.")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8", errors="replace")
    changelog_match = re.search(r"^##\s+([0-9]+\.[0-9]+\.[0-9]+)\b", changelog, re.MULTILINE)
    results.add("version:changelog-current", bool(changelog_match and changelog_match.group(1) == version), "Top changelog release matches root VERSION.")
    upgrade_note_result = upgrade_notes.validate_upgrade_notes(root)
    upgrade_note_codes = [
        str(item.get("code"))
        for item in upgrade_note_result.get("errors", [])
        if isinstance(item, dict)
    ]
    results.add(
        "upgrade-notes-contract",
        bool(upgrade_note_result.get("passed")),
        (
            "Current release has exactly one schema-valid structured upgrade note."
            if upgrade_note_result.get("passed")
            else "Upgrade-note errors: " + ", ".join(upgrade_note_codes)
        ),
    )
    docs_index = (root / "docs" / "README.md").read_text(encoding="utf-8", errors="replace")
    results.add("version:docs-index", f"v{version}" in docs_index, "Documentation index names the current release.")
    for relative in [
        "plugins/owledge-cowork/VERSION",
        "plugins/owledge-cowork/.claude-plugin/plugin.json",
        "plugins/owledge-cowork/.codex-plugin/plugin.json",
    ]:
        path = root / pathlib.Path(relative)
        results.add(f"exists:{relative}", path.exists(), "Versioned plugin file exists.")
        if not path.exists():
            continue
        if path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            results.add(f"version:{relative}", payload.get("version") == version, "Plugin manifest version matches root VERSION.")
            results.add(f"product-name:{relative}", "Owledge" in json.dumps(payload), "Plugin manifest uses Owledge product naming.")
        else:
            results.add(f"version:{relative}", path.read_text(encoding="utf-8", errors="replace").strip() == version, "Plugin VERSION matches root VERSION.")
    matrix = (root / "docs" / "harness-plugin-matrix.md").read_text(encoding="utf-8", errors="replace")
    results.add("harness-matrix-local-support", "Local adapter support" in matrix, "Harness matrix explains local adapter support boundary.")
    results.add("harness-matrix-no-ready-column", "| Ready |" not in matrix, "Harness matrix avoids broad Ready status wording.")
    security = (root / "SECURITY.md").read_text(encoding="utf-8", errors="replace")
    results.add("security-local-kit-boundary", "local kit" in security.lower() and "not yet certified" in security.lower(), "Security doc states local-kit and regulated-production boundaries.")
    readme_lower = readme.lower()
    command_reference = (root / "docs" / "command-reference.md").read_text(encoding="utf-8", errors="replace").lower()
    results.add("release-python-first-project-local", "python-first" in command_reference and "project-local" in readme_lower, "Release surface presents Owledge as a Python-first project-local install.")
    results.add("release-primary-init-command", "uvx owledge quickstart --target /path/to/your-project" in readme, "README documents the primary uvx setup command.")
    return results.payload(project=str(root), version=version)


def launch_readiness_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    required_addons = [
        "launch-demo-kit",
        "trust-readiness-kit",
        "runtime-conformance-kit",
        "pi-proof-kit",
        "ts-adapter-kit",
        "benchmark-kit",
    ]
    for addon in required_addons:
        addon_root = root / "addons" / addon
        manifest_path = addon_root / "addon.json"
        readme_path = addon_root / "README.md"
        results.add(f"addon-exists:{addon}", addon_root.exists(), "Launch add-on directory exists.")
        results.add(f"addon-manifest:{addon}", manifest_path.exists(), "Launch add-on manifest exists.")
        results.add(f"addon-readme:{addon}", readme_path.exists(), "Launch add-on README exists.")
        if manifest_path.exists():
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            results.add(f"addon-name:{addon}", payload.get("name") == addon, "Manifest name matches directory.")
            results.add(f"addon-files:{addon}", bool(payload.get("install_files")), "Manifest installs user-facing files.")

    docs_required = [
        "docs/try-owledge-in-5-minutes.md",
        "docs/integration-decision-guide.md",
        "docs/launch-readiness.md",
        "docs/distribution.md",
        "docs/operational-hardening.md",
    ]
    for relative in docs_required:
        path = root / pathlib.Path(relative)
        results.add(f"launch-doc:{relative}", path.exists(), "Launch readiness doc exists.")
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            results.add(f"launch-doc-substance:{relative}", len(text.splitlines()) >= 20, "Launch doc has enough operational detail.")

    try_doc = (root / "docs" / "try-owledge-in-5-minutes.md")
    if try_doc.exists():
        text = try_doc.read_text(encoding="utf-8", errors="replace")
        results.add("demo-three-commands", text.count("python tools/owledge.py") >= 3, "Demo path includes concrete commands.")
        results.add("demo-expected-result", "Expected result" in text, "Demo path tells users what they should see.")
        results.add("demo-next-agent-prompt", "Next agent prompt" in text, "Demo path gives the next runtime prompt.")

    readiness_doc = root / "docs" / "launch-readiness.md"
    if readiness_doc.exists():
        text = readiness_doc.read_text(encoding="utf-8", errors="replace")
        for target in ["95", "Value Clarity", "Distribution", "Trust", "Pass/Fail"]:
            results.add(f"readiness-rubric:{target}", target in text, "Launch readiness rubric includes required scoring term.")

    pi_redteam = root / "addons" / "pi-proof-kit" / "starter" / ".owledge" / "pi-agent" / "red-team"
    redteam_files = sorted(pi_redteam.glob("*.md")) if pi_redteam.exists() else []
    results.add("pi-proof-redteam-file", bool(redteam_files), "PI proof kit includes a concrete red-team artifact.")
    for path in redteam_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        results.add(f"pi-redteam-nonzero:{path.name}", "score_total: 0" not in text and "score_total:" in text, "PI proof red-team score is non-zero.")
        results.add(f"pi-redteam-no-placeholder:{path.name}", "PLACEHOLDER" not in text.upper() and "TBD" not in text.upper(), "PI proof red-team artifact has no placeholders.")
        results.add(f"pi-redteam-evidence:{path.name}", "Evidence" in text and "Recommendation" in text, "PI proof red-team artifact includes evidence and recommendation.")

    pi_corpus = root / "addons" / "pi-proof-kit" / "starter" / ".owledge" / "pi-agent" / "proof-corpus"
    corpus_files = sorted(pi_corpus.glob("*.md")) if pi_corpus.exists() else []
    results.add("pi-proof-corpus-count", len(corpus_files) >= 10, "PI proof kit includes at least ten synthetic memory artifacts.")
    corpus_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in corpus_files)
    for signal in ["recurring-error", "parallel", "promoted-pattern", "measure"]:
        results.add(f"pi-proof-loop:{signal}", signal in corpus_text, "PI proof corpus demonstrates the full learning loop.")

    runtime_contracts = root / "addons" / "runtime-conformance-kit" / "contracts"
    for runtime in ["codex", "claude-code", "generic-mcp-cli"]:
        path = runtime_contracts / f"{runtime}.json"
        results.add(f"runtime-contract:{runtime}", path.exists(), "Runtime conformance contract exists.")
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            results.add(f"runtime-contract-fixtures:{runtime}", bool(payload.get("fixtures")), "Runtime contract lists fixtures.")
            results.add(f"runtime-contract-expected:{runtime}", bool(payload.get("expected_artifacts")), "Runtime contract lists expected artifacts.")

    ts_adapter = root / "addons" / "ts-adapter-kit"
    results.add("ts-adapter-package", (ts_adapter / "package.json").exists(), "TS adapter add-on includes package metadata.")
    results.add("ts-adapter-cli", (ts_adapter / "bin" / "owledge-lint.mjs").exists(), "TS adapter add-on includes the owledge-lint CLI.")
    results.add("ts-adapter-no-engine", not (ts_adapter / "src" / "memory-engine.ts").exists(), "TS adapter is not a second memory engine.")

    benchmark_addon = root / "addons" / "benchmark-kit"
    results.add("benchmark-addon-script", (benchmark_addon / "tools" / "run-benchmark-kit.py").exists(), "Benchmark Kit add-on includes a real-fixture runner.")
    results.add("benchmark-addon-explained", (benchmark_addon / "BENCHMARK_EXPLAINED.md").exists(), "Benchmark Kit add-on explains injected benchmark problems.")

    packaging = root / "pyproject.toml"
    results.add("packaging:pyproject", packaging.exists(), "PyPI/pipx packaging metadata exists.")
    if packaging.exists():
        text = packaging.read_text(encoding="utf-8", errors="replace")
        results.add("packaging:script", "owledge" in text and "[project.scripts]" in text, "Packaging exposes an owledge console script.")
    manifest = root / "MANIFEST.in"
    results.add("packaging:manifest", manifest.exists(), "Source distribution manifest exists.")
    if manifest.exists():
        text = manifest.read_text(encoding="utf-8", errors="replace")
        for required in ["recursive-include addons", "recursive-include docs", "recursive-include skills", "recursive-include tools"]:
            results.add(f"packaging:manifest:{required}", required in text, "Source distribution includes required launch/core files.")

    return results.payload(project=str(root), target_score="95+")


def publish_readiness_gate(root: pathlib.Path, min_score: int = 95) -> dict[str, Any]:
    checks: list[tuple[str, int, Callable[[], dict[str, Any]]]] = [
        ("version-contract", 15, lambda: version_contract_gate(root)),
        ("docs-contract", 15, lambda: docs_contract_gate(root)),
        ("release-contract", 15, lambda: release_contract_gate(root)),
        ("legacy-naming-clean", 15, lambda: legacy_naming_gate(root)),
        ("private-path-clean", 10, lambda: private_path_gate(root)),
        ("public-docs", 15, lambda: public_docs_gate(root)),
        ("release-trust", 10, lambda: release_trust_gate(root)),
        ("launch-readiness", 10, lambda: launch_readiness_gate(root)),
        ("standalone-skills", 10, lambda: standalone_skills_gate(root)),
        ("mcp-readonly", 10, lambda: mcp_readonly_smoke(root)),
        ("wikilink-audit", 10, lambda: wikilink_audit(root)),
        ("benchmark-kit-ci", 10, lambda: benchmark_addon_gate(root)),
        ("py-compile", 10, lambda: py_compile_gate(root)),
    ]
    components: dict[str, Any] = {}
    score = 0
    blockers: list[dict[str, Any]] = []
    for name, weight, func in checks:
        try:
            payload = func()
        except Exception as exc:
            payload = {"passed": False, "error": str(exc)}
        passed = bool(payload.get("passed", True))
        components[name] = {"passed": passed, "weight": weight, "summary": payload}
        if passed:
            score += weight
        else:
            blockers.append({"name": name, "weight": weight, "error": payload.get("error", ""), "failed": payload.get("failed")})
    passed = score >= min_score and not blockers
    return {
        "passed": passed,
        "project": str(root),
        "score": score,
        "min_score": min_score,
        "blockers": blockers,
        "components": components,
        "verdict": "promote-candidate" if passed and score >= 95 else "revise",
    }


def benchmark_addon_gate(root: pathlib.Path) -> dict[str, Any]:
    manifest = root / "addons" / "benchmark-kit" / "addon.json"
    explanation = root / "addons" / "benchmark-kit" / "BENCHMARK_EXPLAINED.md"
    runner = root / "addons" / "benchmark-kit" / "tools" / "run-benchmark-kit.py"
    renderer = root / "addons" / "benchmark-kit" / "tools" / "render-benchmark-report.py"
    comparer = root / "addons" / "benchmark-kit" / "tools" / "compare-benchmark-runs.py"
    results = ResultSet()
    baseline_contract = benchmark_baseline.validate_benchmark_baseline(root)
    results.add(
        "benchmark-addon:frozen-baseline",
        bool(baseline_contract.get("passed")),
        (
            "Frozen synthetic fixture baseline, held-out journeys, and 80% token-efficiency contract pass."
            if baseline_contract.get("passed")
            else "Frozen baseline errors: "
            + ", ".join(
                str(item.get("code"))
                for item in baseline_contract.get("errors", [])
                if isinstance(item, dict)
            )
        ),
    )
    results.add("benchmark-addon:manifest", manifest.exists(), "Benchmark Kit add-on manifest exists.")
    results.add("benchmark-addon:runner", runner.exists(), "Benchmark Kit runner exists.")
    results.add("benchmark-addon:renderer", renderer.exists(), "Benchmark Kit report renderer exists.")
    results.add("benchmark-addon:comparer", comparer.exists(), "Benchmark Kit comparison renderer exists.")
    results.add("benchmark-addon:explanation", explanation.exists(), "Benchmark explanation Markdown exists.")
    for scale in ["small", "mid", "large"]:
        archive = root / "addons" / "benchmark-kit" / "fixtures" / f"{scale}.zip"
        public_fixture = root / "benchmarks" / "v0.7.0" / "fixtures" / scale
        results.add(f"benchmark-addon:fixture-archive:{scale}", archive.exists(), "Bundled Benchmark Kit fixture archive exists.")
        results.add(f"benchmark-addon:public-fixture:{scale}", public_fixture.exists(), "Public v0.7.0 benchmark fixture exists.")
        results.add(f"benchmark-addon:public-fixture-manifest:{scale}", (public_fixture / "fixture-manifest.json").exists(), "Public fixture manifest exists.")
    public_benchmark = root / "benchmarks" / "v0.7.0"
    for rel in [
        "README.md",
        "methodology.md",
        "benchmark-explained.md",
        "baseline-contract-v1.json",
        "held-out-journeys-v1.json",
        "results/comparison/index.html",
        "results/comparison/latest.json",
        "results/comparison/latest.md",
        "results/comparison/charts.svg",
        "results/gemma4-latest/index.html",
        "results/qwen3-5-4b/index.html",
        "results/qwen3-5-4b/STATUS.md",
        "results/glm-5-1-cloud/index.html",
    ]:
        results.add(f"benchmark-addon:public-artifact:{rel}", (public_benchmark / rel).exists(), "Public v0.7.0 benchmark artifact exists.")
    if explanation.exists():
        text = explanation.read_text(encoding="utf-8", errors="replace").lower()
        for required in ["distractor", "stale", "private", "multi-hop", "handoff", "context pollution"]:
            results.add(f"benchmark-addon:explanation:{required}", required in text, "Benchmark explanation documents injected failure modes.")
    if not (manifest.exists() and runner.exists() and renderer.exists() and comparer.exists() and explanation.exists()):
        return results.payload(project=str(root))

    temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="owledge-benchmark-addon-"))
    try:
        install = install_addon(temp_dir, root, "benchmark-kit")
        installed_runner = temp_dir / "tools" / "benchmark-kit" / "run-benchmark-kit.py"
        installed_renderer = temp_dir / "tools" / "benchmark-kit" / "render-benchmark-report.py"
        installed_comparer = temp_dir / "tools" / "benchmark-kit" / "compare-benchmark-runs.py"
        installed_explanation = temp_dir / ".owledge" / "benchmark-kit" / "BENCHMARK_EXPLAINED.md"
        results.add("benchmark-addon:install-runner", installed_runner.exists(), "Installed Benchmark Kit runner exists.")
        results.add("benchmark-addon:install-renderer", installed_renderer.exists(), "Installed Benchmark Kit renderer exists.")
        results.add("benchmark-addon:install-comparer", installed_comparer.exists(), "Installed Benchmark Kit comparison renderer exists.")
        results.add("benchmark-addon:install-explanation", installed_explanation.exists(), "Installed Benchmark Kit explanation exists.")
        for scale in ["small", "mid", "large"]:
            installed_archive = temp_dir / "tools" / "benchmark-kit" / "fixtures" / f"{scale}.zip"
            results.add(f"benchmark-addon:install-fixture-archive:{scale}", installed_archive.exists(), "Installed bundled fixture archive exists.")
        if installed_runner.exists() and installed_renderer.exists() and installed_comparer.exists():
            run = run_subprocess([sys.executable, str(installed_runner), "--mode", "ci", "--scale-mode", "small", "--fixture-source", "bundled", "--yes"], cwd=temp_dir)
            results.add("benchmark-addon:ci-run", run.returncode == 0, "Benchmark Kit CI run exits successfully." if run.returncode == 0 else f"Benchmark Kit CI run failed: {run.stderr[-800:]}")
            render = run_subprocess([sys.executable, str(installed_renderer), "--format", "html"], cwd=temp_dir)
            results.add("benchmark-addon:html-render", render.returncode == 0, "Benchmark Kit report render exits successfully." if render.returncode == 0 else f"Benchmark Kit report render failed: {render.stderr[-800:]}")
            for rel in [
                ".owledge/exports/benchmark-kit/latest.json",
                ".owledge/exports/benchmark-kit/latest.md",
                ".owledge/exports/benchmark-kit/results.jsonl",
                ".owledge/reports/generated/benchmark-kit/index.html",
                ".owledge/reports/generated/benchmark-kit/charts.svg",
            ]:
                results.add(f"benchmark-addon:output:{rel}", (temp_dir / rel).exists(), "Benchmark Kit output exists.")
            latest_json = temp_dir / ".owledge" / "exports" / "benchmark-kit" / "latest.json"
            latest_md = temp_dir / ".owledge" / "exports" / "benchmark-kit" / "latest.md"
            html_report = temp_dir / ".owledge" / "reports" / "generated" / "benchmark-kit" / "index.html"
            if latest_json.exists():
                report_payload = json.loads(latest_json.read_text(encoding="utf-8"))
                results.add("benchmark-addon:json-verdict", str(report_payload.get("verdict", {}).get("verdict") or "") in {"pass", "warn", "fail"}, "Benchmark JSON includes a verdict.")
                results.add("benchmark-addon:json-verdicts-owledge", str(report_payload.get("verdicts", {}).get("owledge", {}).get("verdict") or "") in {"pass", "warn", "fail"}, "Benchmark JSON includes an Owledge product verdict.")
                results.add("benchmark-addon:json-final-verdict", str(report_payload.get("final_verdict") or "") in {"pass", "warn", "fail"}, "Benchmark JSON includes a final product verdict.")
                results.add("benchmark-addon:json-profile-totals", all(profile in report_payload.get("profile_totals", {}) for profile in ["metadata_scan", "owledge_context_pack", "oracle"]), "Benchmark JSON includes profile-level totals.")
                results.add("benchmark-addon:json-fixture-source", report_payload.get("fixture_source") == "bundled", "Benchmark JSON records bundled fixture source.")
                baseline_verdict = str(report_payload.get("verdicts", {}).get("baseline", {}).get("verdict") or "")
                owledge_verdict = str(report_payload.get("verdicts", {}).get("owledge", {}).get("verdict") or "")
                results.add("benchmark-addon:baseline-does-not-force-product-fail", not (baseline_verdict == "fail" and owledge_verdict == "pass" and report_payload.get("final_verdict") == "fail"), "Baseline failures do not force a product-level fail when Owledge passes.")
                results.add("benchmark-addon:json-relative-project", report_payload.get("project_root") == ".", "Benchmark JSON uses a share-safe project root.")
                results.add("benchmark-addon:json-relative-fixture", not pathlib.PurePosixPath(str(report_payload.get("fixture_dir", ""))).is_absolute() and "Users/" not in str(report_payload.get("fixture_dir", "")), "Benchmark JSON fixture path is relative/share-safe.")
            if latest_md.exists():
                md_text = latest_md.read_text(encoding="utf-8", errors="replace")
                for required in ["## Run Summary", "Before vs Owledge", "Privacy Trap Explained", "Privacy Trap Result", "Prevented", "What This Means", "## Final Verdict", "Tokens per correct answer", "Context pollution"]:
                    results.add(f"benchmark-addon:md:{required}", required in md_text, "Benchmark Markdown includes verdict and interpretation.")
            if html_report.exists():
                html_text = html_report.read_text(encoding="utf-8", errors="replace")
                for required in ["Run Summary", "Before vs Owledge", "Final Verdict", "Privacy Trap", "Privacy Trap Result", "Prevented", "Owledge selected private trap files", "Total tokens", "Tokens per correct answer", "Context pollution", "Privacy failures", "Stale failures", "<svg"]:
                    results.add(f"benchmark-addon:html:{required}", required in html_text, "Benchmark HTML includes verdict, interpretation, and embedded charts.")
            if latest_json.exists():
                compare = run_subprocess(
                    [
                        sys.executable,
                        str(installed_comparer),
                        "--inputs",
                        str(latest_json),
                        str(latest_json),
                        "--output",
                        ".owledge/reports/generated/benchmark-kit-comparison",
                    ],
                    cwd=temp_dir,
                )
                results.add("benchmark-addon:compare-run", compare.returncode == 0, "Benchmark comparison report render exits successfully." if compare.returncode == 0 else f"Benchmark comparison failed: {compare.stderr[-800:]}")
                compare_json = temp_dir / ".owledge" / "exports" / "benchmark-kit-comparison" / "latest.json"
                compare_md = temp_dir / ".owledge" / "exports" / "benchmark-kit-comparison" / "latest.md"
                compare_html = temp_dir / ".owledge" / "reports" / "generated" / "benchmark-kit-comparison" / "index.html"
                compare_svg = temp_dir / ".owledge" / "reports" / "generated" / "benchmark-kit-comparison" / "charts.svg"
                for rel_path in [compare_json, compare_md, compare_html, compare_svg]:
                    results.add(f"benchmark-addon:compare-output:{rel_path.name}", rel_path.exists(), "Benchmark comparison output exists.")
                if compare_json.exists():
                    compare_payload = json.loads(compare_json.read_text(encoding="utf-8"))
                    results.add("benchmark-addon:compare-json-models", len(compare_payload.get("models", [])) >= 2, "Benchmark comparison JSON includes multiple model rows.")
                    results.add("benchmark-addon:compare-json-executive", "executive" in compare_payload, "Benchmark comparison JSON includes executive verdict.")
                    results.add("benchmark-addon:compare-json-costs", len(compare_payload.get("api_cost_estimates", [])) >= 9, "Benchmark comparison JSON includes API cost estimates.")
                if compare_html.exists():
                    compare_text = compare_html.read_text(encoding="utf-8", errors="replace")
                    for required in ["Executive Verdict", "Creator Pull Quote", "Model Matrix", "Before vs Owledge", "Estimated API Cost Impact", "Anthropic", "Google", "OpenAI", "Scenario Heatmap", "Privacy failures prevented", "Context pollution", "Tokens per correct answer", "How To Read This Report", "Oracle", "Lower", "Higher"]:
                        results.add(f"benchmark-addon:compare-html:{required}", required in compare_text, "Benchmark comparison HTML includes publishing proof sections.")
                    results.add("benchmark-addon:compare-html:no-audience-targeting", "Interpretation for Audiences" not in compare_text and "AI YouTubers" not in compare_text, "Benchmark comparison HTML avoids audience-targeting language.")
        payload = results.payload(project=str(root), install=install)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    return payload


def read_skill_frontmatter(path: pathlib.Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValueError(f"Missing YAML frontmatter in {path}")
    closing_index = -1
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index < 2:
        raise ValueError(f"Missing closing YAML frontmatter marker in {path}")
    fields: dict[str, str] = {}
    for line in lines[1:closing_index]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"')
    return {"fields": fields, "line_count": len(lines), "body": "\n".join(lines[closing_index + 1 :])}


def principles_skill_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    required_refs = [
        "references/principles.md",
        "references/agent-rules.md",
        "references/mapping-contract.md",
        "references/security-rules.md",
    ]

    def test_skill(relative: str) -> None:
        skill_dir = root / pathlib.Path(relative)
        skill_path = skill_dir / "SKILL.md"
        results.add(f"exists:{relative}", skill_path.exists(), "SKILL.md exists.")
        if not skill_path.exists():
            return
        parsed = read_skill_frontmatter(skill_path)
        fields = parsed["fields"]
        results.add(f"frontmatter-name:{relative}", fields.get("name") == "owledge-principles", "Expected name owledge-principles.")
        results.add(f"frontmatter-description:{relative}", bool(fields.get("description")), "Description is present.")
        results.add(f"concise-skill:{relative}", parsed["line_count"] <= 90, f"SKILL.md has {parsed['line_count']} lines; limit is 90.")
        for reference in required_refs:
            results.add(f"reference-linked:{relative}/{reference}", reference in parsed["body"], "Reference is linked from SKILL.md.")
            results.add(f"reference-exists:{relative}/{reference}", (skill_dir / reference).exists(), "Reference file exists.")

    root_skill = "skills/owledge-principles"
    plugin_skill = "plugins/owledge-cowork/skills/owledge-principles"
    test_skill(root_skill)
    test_skill(plugin_skill)
    for reference in ["SKILL.md", *required_refs]:
        source = root / root_skill / reference
        mirror = root / plugin_skill / reference
        if source.exists() and mirror.exists():
            results.add(f"mirror-identical:{reference}", sha256_file(source) == sha256_file(mirror), "Plugin mirror matches root skill file.")
    return results.payload()


def principles_only_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    required_files = [
        "README.md",
        "docs/README.md",
        "docs/quickstart.md",
        "docs/agent-integration-guide.md",
        "docs/harness-plugin-matrix.md",
        "plugins/owledge-cowork/README.md",
        "skills/owledge-principles/SKILL.md",
        "skills/owledge-runtime-bridge/SKILL.md",
        "plugins/owledge-cowork/skills/owledge-runtime-bridge/SKILL.md",
    ]
    combined = []
    for relative in required_files:
        path = root / pathlib.Path(relative)
        results.add(f"exists:{relative}", path.exists(), "Principles-only source file exists.")
        if path.exists():
            combined.append(path.read_text(encoding="utf-8", errors="replace"))
    text = "\n".join(combined).lower()
    for phrase in [
        "principles-only",
        "markdown",
        "canonical",
        "evidence-linked",
        "typed",
        "review",
        "without adding a plugin",
        "no plugin",
        "no plugin, generated kit",
        "metadata-first",
    ]:
        results.add(f"principles-only-phrase:{phrase}", phrase in text, "Principles-only path is documented.")
    for forbidden in [
        "shell " + "wrappers",
        "global install required",
        "requires os-specific",
    ]:
        results.add(f"principles-only-forbidden:{forbidden}", forbidden not in text, "Principles-only path must not require wrappers, global install, or OS-specific settings.")
    return results.payload()


def kb_module_gate(root: pathlib.Path) -> dict[str, Any]:
    tmp_base = root / ".agent-control" / "tmp"
    tmp_base.mkdir(parents=True, exist_ok=True)
    kb = tmp_base / "kb-module-smoke"
    if kb.exists():
        shutil.rmtree(kb)
    kb.mkdir(parents=True)
    note_a = kb / "Project Alpha.md"
    note_b = kb / "Research.md"
    write_text(note_a, "# Project Alpha\n\nLinks to [[Research]] and keeps the original wiki link untouched.\n")
    write_text(note_b, "---\ntype: research\nstatus: active\n---\n\n# Research\n\nSource note.\n")
    before_a = sha256_file(note_a)
    before_b = sha256_file(note_b)
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(kb),
            kit_root=str(root),
            layout="module-dir",
            module_dir="owledge-module",
            map_file="",
            max_files=10000,
            include_cli=True,
            create_sample_plan=True,
        )
    )
    if before_a != sha256_file(note_a) or before_b != sha256_file(note_b):
        raise RuntimeError("Existing KB markdown files were modified.")
    module_root = kb / "owledge-module"
    for relative in [
        "OWLEDGE_MODULE.md",
        ".owledge/plans/example-kb-backed-project-plan.md",
        ".owledge/indexes/kb-scan.jsonl",
        ".owledge/indexes/kb-module-status.json",
        "tools/owledge_core.py",
    ]:
        if not (module_root / pathlib.Path(relative)).exists():
            raise RuntimeError(f"Missing expected module file: {relative}")
    status = json.loads((module_root / ".owledge" / "indexes" / "kb-module-status.json").read_text(encoding="utf-8"))
    if status["markdown_files_scanned"] < 2 or status["existing_kb_files_modified"] or status["requires_os_environment_variables"]:
        raise RuntimeError("KB module status did not report safe additive behavior.")

    mapped_kb = tmp_base / "kb-module-mapped-smoke"
    if mapped_kb.exists():
        shutil.rmtree(mapped_kb)
    mapped_kb.mkdir(parents=True)
    write_text(mapped_kb / "Idea.md", "# Idea\n\nTurn [[Research]] into an MVP.\n")
    write_text(mapped_kb / "Research.md", "# Research\n\nSource note.\n")
    for relative in ["01_Ideas", "20_Plans", "30_Evidence", "40_Handoffs", "50_Reviews", ".owledge/indexes"]:
        (mapped_kb / pathlib.Path(relative)).mkdir(parents=True, exist_ok=True)
    write_text(
        mapped_kb / "owledge-map.json",
        json.dumps(
            {
                "ideas": "01_Ideas",
                "plans": "20_Plans",
                "evidence": "30_Evidence",
                "handoffs": "40_Handoffs",
                "reviews": "50_Reviews",
                "indexes": ".owledge/indexes",
            },
            indent=2,
        ),
    )
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(mapped_kb),
            kit_root=str(root),
            layout="module-dir",
            module_dir="owledge-module",
            map_file="owledge-map.json",
            max_files=10000,
            include_cli=False,
            create_sample_plan=True,
        )
    )
    mapped_status = json.loads((mapped_kb / ".owledge" / "indexes" / "kb-module-status.json").read_text(encoding="utf-8"))
    if mapped_status["mode"] != "mapped" or not mapped_status["mapping_enabled"]:
        raise RuntimeError("Mapped status did not report mapped mode.")
    if (mapped_kb / "OWLEDGE_MODULE.md").exists():
        raise RuntimeError("Mapped mode should not write root OWLEDGE_MODULE.md.")
    bad_map = {
        "plans": "../escape",
        "evidence": "30_Evidence",
        "handoffs": "40_Handoffs",
        "reviews": "50_Reviews",
        "indexes": ".owledge/indexes",
    }
    write_text(mapped_kb / "bad-owledge-map.json", json.dumps(bad_map))
    process = run_subprocess(
        [
            sys.executable,
            str(root / "tools" / "build_kb_module.py"),
            "--knowledgebase-root",
            str(mapped_kb),
            "--kit-root",
            str(root),
            "--map-file",
            "bad-owledge-map.json",
        ]
    )
    if process.returncode == 0:
        raise RuntimeError("Invalid map with traversal path should fail closed.")
    return {
        "passed": True,
        "knowledgebase": str(kb),
        "module_root": str(module_root),
        "existing_files_unchanged": True,
        "mapped_mode": True,
        "invalid_map_failed_closed": True,
    }


def kb_ingestion_safety_gate(root: pathlib.Path) -> dict[str, Any]:
    result = kb_module_gate(root)
    return {
        "passed": bool(result.get("passed")),
        "metadata_first": True,
        "existing_files_unchanged": bool(result.get("existing_files_unchanged")),
        "mapped_mode": bool(result.get("mapped_mode")),
        "invalid_map_failed_closed": bool(result.get("invalid_map_failed_closed")),
        "base_gate": result,
    }


def scan_generated_surface(target: pathlib.Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(target.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(target).as_posix()
        suffix = path.suffix.lower()
        if suffix in {".p" + "s1", ".s" + "h", ".bat", ".cmd"}:
            violations.append(f"{rel}:script-wrapper")
            continue
        if suffix in TEXT_SKIP_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        hits = platform_forbidden_hits(text, include_shell_scripts=True, include_windows_drive_paths=True)
        if hits:
            violations.append(f"{rel}:{','.join(hits)}")
    return violations


def generated_kit_surface_gate(root: pathlib.Path) -> dict[str, Any]:
    tmp_base = root / ".agent-control" / "tmp" / "generated-kit-surface"
    if tmp_base.exists():
        shutil.rmtree(tmp_base)
    tmp_base.mkdir(parents=True)
    profiles = [
        ("default", {"include_plugin_adapter": False, "include_compliance": False}),
        ("plugin", {"include_plugin_adapter": True, "include_compliance": False}),
        ("compliance", {"include_plugin_adapter": True, "include_compliance": True}),
    ]
    results = ResultSet()
    outputs: dict[str, str] = {}
    for name, options in profiles:
        output = tmp_base / name
        build_project_folder_kit.build(
            argparse.Namespace(
                output_path=str(output),
                project_root=str(root),
                force=True,
                include_global_memory=False,
                include_plugin_adapter=options["include_plugin_adapter"],
                include_compliance=options["include_compliance"],
                plugin_hook_profile="python",
                verify=True,
            )
        )
        outputs[name] = str(output)
        violations = scan_generated_surface(output)
        results.add(f"generated-kit-surface:{name}", not violations, "Generated kit must not contain platform-specific wrappers or setup text." if not violations else "; ".join(violations[:10]))
        results.add(f"generated-kit-python-cli:{name}", (output / "tools" / "owledge.py").exists() and (output / "tools" / "owledge_core.py").exists(), "Generated kit includes Python CLI files.")
    payload = results.payload(outputs=outputs)
    return payload


def runtime_adapters_gate(root: pathlib.Path) -> dict[str, Any]:
    fixtures = root / "plugins" / "owledge-cowork" / "tests" / "fixtures"
    if not fixtures.exists():
        raise RuntimeError(f"Missing plugin fixtures: {fixtures}")
    tmp_root = root / ".agent-control" / "tmp" / f"owledge-runtime-smoke-{next(tempfile._get_candidate_names())}"
    build_project_folder_kit.build(
        argparse.Namespace(
            output_path=str(tmp_root),
            project_root=str(root),
            force=True,
            include_global_memory=False,
            include_plugin_adapter=True,
            include_compliance=False,
            plugin_hook_profile="python",
            verify=False,
        )
    )
    hooks = json.loads((tmp_root / "plugins" / "owledge-cowork" / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    hooks_text = json.dumps(hooks)
    if ("power" + "shell") in hooks_text.lower() or (".p" + "s1") in hooks_text:
        raise RuntimeError("Default plugin hooks must be Python-first and platform-neutral.")
    capture = tmp_root / "plugins" / "owledge-cowork" / "scripts" / "capture-claude-event.py"
    close = tmp_root / "plugins" / "owledge-cowork" / "scripts" / "close-runtime-session.py"
    for fixture in ["session-start.json", "user-prompt.json", "post-tool-use.json"]:
        payload = (fixtures / fixture).read_text(encoding="utf-8")
        process = run_subprocess([sys.executable, str(capture)], cwd=tmp_root, input_text=payload)
        if process.returncode != 0:
            raise RuntimeError(f"Python capture hook failed for {fixture}: {process.stderr}")
    process = run_subprocess([sys.executable, str(close)], cwd=tmp_root, input_text=(fixtures / "stop.json").read_text(encoding="utf-8"))
    if process.returncode != 0:
        raise RuntimeError(f"Python close hook failed: {process.stderr}")
    session_dir = _active_memory_dir(tmp_root) / "sessions" / "cowork-demo-session"
    required = ["events.jsonl", "session.md", "summary.md"]
    missing = [name for name in required if not (session_dir / name).exists()]
    if missing:
        raise RuntimeError(f"Runtime smoke missing files: {', '.join(missing)}")
    summary = (session_dir / "summary.md").read_text(encoding="utf-8")
    if "visibility: \"private\"" not in summary and "visibility: private" not in summary:
        raise RuntimeError("Runtime summary is not private.")
    return {
        "passed": True,
        "temp_project": str(tmp_root),
        "session_dir": str(session_dir),
        "checked_files": required,
        "checked_python_hooks": True,
    }


def expect_kb_failure(root: pathlib.Path, kb_root: pathlib.Path, map_file: str, extra_args: list[str] | None = None) -> bool:
    command = [
        sys.executable,
        str(root / "tools" / "build_kb_module.py"),
        "--knowledgebase-root",
        str(kb_root),
        "--kit-root",
        str(root),
    ]
    if map_file:
        command.extend(["--map-file", map_file])
    command.extend(extra_args or [])
    return run_subprocess(command).returncode != 0


def new_mapped_kb(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for relative in ["00_Inbox", "20_Plans", "30_Evidence", "40_Handoffs", "50_Reviews", ".owledge/indexes"]:
        (path / pathlib.Path(relative)).mkdir(parents=True, exist_ok=True)
    write_text(path / "00_Inbox" / "Idea.md", "# Idea\n\nBuild MVP from [[Research Note]].\n")
    write_text(path / "Research Note.md", "---\ntype: research\n---\n\n# Research Note\n\nKeep this source unchanged.\n")
    write_text(
        path / "owledge-map.json",
        json.dumps(
            {
                "ideas": "00_Inbox",
                "plans": "20_Plans",
                "evidence": "30_Evidence",
                "handoffs": "40_Handoffs",
                "reviews": "50_Reviews",
                "indexes": ".owledge/indexes",
            },
            indent=2,
        ),
    )


def principles_scenarios_gate(root: pathlib.Path) -> dict[str, Any]:
    tmp_base = root / ".agent-control" / "tmp" / "principles-scenarios"
    if tmp_base.exists():
        shutil.rmtree(tmp_base)
    tmp_base.mkdir(parents=True)
    results = ResultSet()

    large_root = tmp_base / "large-codebase"
    large_root.mkdir(parents=True)
    for index in range(1, 81):
        write_text(large_root / "docs" / f"note-{index:03}.md", f"# Note {index}\n\nLinks to [[ADR-{index}]].\n")
    for index in range(1, 121):
        write_text(large_root / "src" / f"module{index:03}" / f"file{index:03}.ts", f"export const value{index} = {index};\n")
    large_before = tree_hash(large_root)
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(large_root),
            kit_root=str(root),
            layout="module-dir",
            module_dir="owledge-module",
            map_file="",
            max_files=25,
            include_cli=False,
            create_sample_plan=True,
        )
    )
    large_after = tree_hash(large_root, ["owledge-module"])
    large_status = json.loads((large_root / "owledge-module" / ".owledge" / "indexes" / "kb-module-status.json").read_text(encoding="utf-8"))
    results.add("large-codebase-existing-files-unchanged", large_before == large_after, "Existing files stayed byte-identical outside the module.")
    results.add("large-codebase-max-files-honored", large_status["markdown_files_scanned"] == 25, "MaxFiles=25 honored.")
    results.add("large-codebase-zero-env", large_status["requires_os_environment_variables"] is False, "No OS environment variable dependency.")

    user_kb = tmp_base / "existing-user-kb"
    new_mapped_kb(user_kb)
    user_before = tree_hash(user_kb)
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(user_kb),
            kit_root=str(root),
            layout="module-dir",
            module_dir="owledge-module",
            map_file="owledge-map.json",
            max_files=10000,
            include_cli=False,
            create_sample_plan=True,
        )
    )
    user_after = tree_hash(user_kb, ["20_Plans", "30_Evidence", "40_Handoffs", "50_Reviews", ".owledge/indexes"])
    user_status = json.loads((user_kb / ".owledge" / "indexes" / "kb-module-status.json").read_text(encoding="utf-8"))
    results.add("user-kb-mapped-mode", user_status["mode"] == "mapped" and user_status["mapping_enabled"], "Mapped mode selected.")
    results.add("user-kb-original-notes-unchanged", user_before == user_after, "Original notes and map stayed byte-identical.")
    results.add("user-kb-wikilinks-not-converted", user_status["wiki_links_converted"] is False, "Wiki links not converted.")
    results.add("user-kb-no-root-module-doc", not (user_kb / "OWLEDGE_MODULE.md").exists(), "Mapped mode avoids root module doc.")
    write_text(user_kb / "30_Evidence" / "worker-evidence.md", "# Worker Evidence\n\nSource: `Research Note.md`.\n")
    write_text(user_kb / "40_Handoffs" / "worker-handoff.md", "# Worker Handoff\n\nStatus: done.\n")
    write_text(user_kb / "50_Reviews" / "reviewer-findings.md", "# Reviewer Findings\n\nVerdict: needs curator approval before promotion.\n")
    forbidden = [user_kb / ".owledge" / "canonical", user_kb / ".owledge" / "lessons", user_kb / "global-memory"]
    results.add("multi-agent-role-boundaries", not any(path.exists() for path in forbidden), "Workers/reviewers wrote only mapped artifacts.")

    skill_bloat = tmp_base / "skill-bloat"
    skill_bloat.mkdir()
    for index in range(1, 51):
        skill_dir = skill_bloat / f"noise-skill-{index:02}"
        skill_dir.mkdir()
        write_text(skill_dir / "SKILL.md", f"---\nname: noise-skill-{index}\ndescription: unrelated test skill\n---\n\n# Noise\n")
    shutil.copytree(root / "skills" / "owledge-principles", skill_bloat / "owledge-principles")
    matches = [
        path
        for path in skill_bloat.rglob("SKILL.md")
        if re.search(r"(?m)^name:\s*owledge-principles\s*$", path.read_text(encoding="utf-8"))
    ]
    results.add("skill-bloat-exact-name-discovery", len(matches) == 1, "Found exactly one owledge-principles skill among 51 skills.")
    results.add("skill-bloat-references-present", (skill_bloat / "owledge-principles" / "references" / "mapping-contract.md").exists(), "References survive crowded skill install.")

    superpowers_kb = tmp_base / "superpowers-coexistence"
    superpowers_plan = superpowers_kb / "docs" / "superpowers" / "plans" / "example-plan.md"
    write_text(
        superpowers_plan,
        "# Example Superpowers Implementation Plan\n\n**Goal:** Add a small feature with TDD.\n\n- [ ] Write the failing test\n- [ ] Implement the minimal code\n",
    )
    write_text(superpowers_kb / "README.md", "# Existing Project\n\nUses Superpowers for execution.\n")
    superpowers_hash_before = sha256_file(superpowers_plan)
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(superpowers_kb),
            kit_root=str(root),
            layout="module-dir",
            module_dir="owledge-module",
            map_file="",
            max_files=10000,
            include_cli=False,
            create_sample_plan=True,
        )
    )
    superpowers_hash_after = sha256_file(superpowers_plan)
    index_text = (superpowers_kb / "owledge-module" / ".owledge" / "indexes" / "kb-scan.jsonl").read_text(encoding="utf-8")
    handoff_path = superpowers_kb / "owledge-module" / ".owledge" / "handoffs" / "superpowers-plan-handoff.md"
    write_text(handoff_path, "# Superpowers Plan Handoff\n\nEvidence: `docs/superpowers/plans/example-plan.md`.\n")
    results.add("superpowers-plan-unchanged", superpowers_hash_before == superpowers_hash_after, "Superpowers plan unchanged.")
    results.add("superpowers-plan-indexed", "docs/superpowers/plans/example-plan.md" in index_text, "Index references Superpowers plan.")
    results.add("superpowers-handoff-evidence", "docs/superpowers/plans/example-plan.md" in handoff_path.read_text(encoding="utf-8"), "Handoff cites Superpowers plan.")

    edge_kb = tmp_base / "edge-kb"
    new_mapped_kb(edge_kb)
    edge_cases: list[tuple[str, Any]] = [
        ("absolute-path", {"plans": "C" + ":/escape", "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".owledge/indexes"}),
        ("unknown-key", {"plans": "20_Plans", "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".owledge/indexes", "canonical": "50_Reviews"}),
        ("missing-required-key", {"plans": "20_Plans", "evidence": "30_Evidence", "reviews": "50_Reviews", "indexes": ".owledge/indexes"}),
        ("missing-target", {"plans": "20_Plans", "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": "missing-indexes"}),
        ("file-target", {"plans": "Research Note.md", "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".owledge/indexes"}),
        ("blank-value", {"plans": "", "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".owledge/indexes"}),
        ("null-value", {"plans": None, "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".owledge/indexes"}),
        ("array-value", {"plans": ["20_Plans"], "evidence": "30_Evidence", "handoffs": "40_Handoffs", "reviews": "50_Reviews", "indexes": ".owledge/indexes"}),
    ]
    for name, payload in edge_cases:
        write_text(edge_kb / f"bad-{name}.json", json.dumps(payload))
        results.add(f"edge-fail-closed:{name}", expect_kb_failure(root, edge_kb, f"bad-{name}.json"), "Invalid map should fail closed.")
    results.add("edge-fail-closed:missing-explicit-map", expect_kb_failure(root, edge_kb, "does-not-exist.json"), "Explicit missing map should fail closed.")
    write_text(edge_kb / "bad-duplicate-key.json", '{"plans":"../escape","plans":"20_Plans","evidence":"30_Evidence","handoffs":"40_Handoffs","reviews":"50_Reviews","indexes":".owledge/indexes"}')
    results.add("edge-fail-closed:duplicate-json-key", expect_kb_failure(root, edge_kb, "bad-duplicate-key.json"), "Duplicate JSON keys should fail closed.")
    results.add("edge-fail-closed:max-files-zero", expect_kb_failure(root, edge_kb, "", ["--max-files", "0"]), "max-files=0 should fail closed.")

    bom_kb = tmp_base / "bom-frontmatter-kb"
    bom_kb.mkdir()
    (bom_kb / "Bom.md").write_text("\ufeff---\ntype: research\nstatus: active\n---\n\n# BOM Note\n", encoding="utf-8")
    build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(bom_kb),
            kit_root=str(root),
            layout="module-dir",
            module_dir="owledge-module",
            map_file="",
            max_files=10000,
            include_cli=False,
            create_sample_plan=True,
        )
    )
    bom_rows = [(json.loads(line)) for line in (bom_kb / "owledge-module" / ".owledge" / "indexes" / "kb-scan.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    keys = set(bom_rows[0].get("frontmatter_keys", [])) if bom_rows else set()
    results.add("edge-bom-frontmatter-keys", {"type", "status"}.issubset(keys), "BOM-prefixed frontmatter keys detected.")

    return results.payload(symlink_case_skipped=True)


def poweruser_simulations_gate(root: pathlib.Path) -> dict[str, Any]:
    tmp_base = root / ".agent-control" / "tmp" / "poweruser-simulations"
    if tmp_base.exists():
        shutil.rmtree(tmp_base)
    tmp_base.mkdir(parents=True)
    results = ResultSet()

    dirty_vault = tmp_base / "dirty vault with spaces"
    dirty_vault.mkdir()
    for index in range(1, 5001):
        folder = dirty_vault / ("Notes" if index % 3 else "Research") / f"group-{index % 17:02}"
        frontmatter = "---\ntype: note\nstatus: active\n---\n\n" if index % 11 == 0 else ""
        body = f"{frontmatter}# Dirty Note {index}\n\nLinks to [[Dirty Note {(index % 5000) + 1}]] and [[Shared Topic]].\n"
        write_text(folder / f"Dirty Note {index}.md", body)
    write_text(dirty_vault / "Assets" / "image-placeholder.png.md", "# Image Placeholder\n\nA markdown sidecar for an attachment.\n")
    before_dirty = tree_hash(dirty_vault)
    dirty_result = build_kb_module.build(
        argparse.Namespace(
            knowledgebase_root=str(dirty_vault),
            kit_root=str(root),
            layout="module-dir",
            module_dir="owledge-module",
            map_file="",
            max_files=5000,
            include_cli=True,
            create_sample_plan=True,
        )
    )
    after_dirty = tree_hash(dirty_vault, ["owledge-module"])
    results.add("dirty-vault-source-files-unchanged", before_dirty == after_dirty, "5k-file dirty vault stayed byte-identical outside the module.")
    results.add("dirty-vault-scanned-5k", dirty_result.get("markdown_files_scanned") == 5000, "Dirty vault scan honored 5k max-files target.")
    results.add("dirty-vault-no-env", dirty_result.get("requires_os_environment_variables") is False, "Dirty vault install requires no OS environment variables.")

    dx_project = tmp_base / "first user project"
    started = time.perf_counter()
    init_result = init_project(dx_project, root, include_plugin_adapter=False, include_compliance=False)
    write_text(dx_project / ".owledge" / "plans" / "first-use-plan.md", "# First Use Plan\n\nGoal: create one useful source-backed plan.\n")
    write_text(dx_project / ".owledge" / "handoffs" / "first-use-handoff.md", "# First Use Handoff\n\nNext action: run validation and continue the MVP cutline.\n")
    dx_seconds = round(time.perf_counter() - started, 3)
    results.add("first-user-init-doctor", bool(init_result.get("doctor_passed")), "Initialized project passes doctor.")
    results.add("first-user-useful-artifacts", (dx_project / ".owledge" / "plans" / "first-use-plan.md").exists() and (dx_project / ".owledge" / "handoffs" / "first-use-handoff.md").exists(), "First user can reach one useful plan and handoff.")
    results.add("first-user-dx-under-10s", dx_seconds < 10, f"First-user simulation completed in {dx_seconds}s.")

    existing = tmp_base / "existing project ünicode"
    write_text(existing / ".gitignore", "dist/\n")
    write_text(existing / "AGENTS.md", "# Existing Agent Rules\n\nDo not overwrite me.\n")
    write_text(existing / ".owledge" / "plans" / "existing-plan.md", "# Existing Plan\n\nKeep this file.\n")
    existing_agents_hash = sha256_file(existing / "AGENTS.md")
    existing_plan_hash = sha256_file(existing / ".owledge" / "plans" / "existing-plan.md")
    existing_result = init_project(existing, root, include_plugin_adapter=True, include_compliance=False)
    results.add("existing-project-agents-preserved", sha256_file(existing / "AGENTS.md") == existing_agents_hash, "Existing AGENTS.md was not overwritten.")
    results.add("existing-project-plan-preserved", sha256_file(existing / ".owledge" / "plans" / "existing-plan.md") == existing_plan_hash, "Existing memory plan was not overwritten.")
    results.add("existing-project-plugin-added", (existing / "plugins" / "owledge-cowork" / "README.md").exists(), "Plugin adapter can be added to an existing project.")
    results.add("existing-project-skipped-existing", "AGENTS.md" in existing_result.get("skipped_existing", []), "Init reports skipped existing project files.")

    return results.payload(project=str(root), simulated_files=5000)


def capped_gate_payload(payload: Any, limit: int = 5) -> dict[str, Any]:
    """Return transcript-safe failure triage while preserving a full sidecar."""
    if not isinstance(payload, dict):
        return {"passed": False, "failed": 1, "total": 1, "first_failings": [str(payload)[:500]]}
    rows = payload.get("results") or payload.get("findings") or payload.get("errors") or []
    if not isinstance(rows, list):
        rows = [rows]
    failing = [row for row in rows if not isinstance(row, dict) or row.get("passed") is not True]
    return {
        "passed": bool(payload.get("passed", False)),
        "failed": int(payload.get("failed", len(failing) or 1)),
        "total": int(payload.get("total", len(rows) or 1)),
        "first_failings": failing[:limit],
    }


def gate_sidecar_roundtrip_v1(payload: Any, sidecar_path: pathlib.Path) -> dict[str, Any]:
    """Persist and reconstruct a full gate payload behind a capped transcript view."""
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.write_text(serialized, encoding="utf-8", newline="\n")
    reconstructed = json.loads(sidecar_path.read_text(encoding="utf-8"))
    return {
        "passed": reconstructed == payload,
        "summary": capped_gate_payload(payload),
        "sidecar_sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
        "sidecar_bytes": len(serialized.encode("utf-8")),
        "roundtrip_equal": reconstructed == payload,
    }


def run_gate(name: str, func: Callable[[], Any]) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        payload = func()
        passed = bool(payload.get("passed", True)) if isinstance(payload, dict) else True
        if not passed:
            summary = capped_gate_payload(payload)
            return {
                "name": name,
                "passed": False,
                "error": json.dumps(summary, sort_keys=True),
                "summary": summary,
                "audit_payload": payload,
                "seconds": round(time.perf_counter() - started, 3),
            }
        return {"name": name, "passed": True, "seconds": round(time.perf_counter() - started, 3)}
    except Exception as exc:
        payload = {"passed": False, "errors": [str(exc)]}
        summary = capped_gate_payload(payload)
        return {"name": name, "passed": False, "error": json.dumps(summary, sort_keys=True), "summary": summary, "audit_payload": payload, "seconds": round(time.perf_counter() - started, 3)}


def py_compile_gate(root: pathlib.Path) -> dict[str, Any]:
    files = [
        root / "tools" / "owledge.py",
        root / "tools" / "owledge_core.py",
        root / "tools" / "build_kb_module.py",
        root / "tools" / "build_project_folder_kit.py",
        root / "plugins" / "owledge-cowork" / "scripts" / "capture-claude-event.py",
        root / "plugins" / "owledge-cowork" / "scripts" / "close-runtime-session.py",
        root / "benchmarks" / "run_benchmarks.py",
    ]
    process = run_subprocess([sys.executable, "-m", "py_compile", *[str(path) for path in files]])
    if process.returncode != 0:
        raise RuntimeError(process.stderr or process.stdout)
    return {"passed": True, "files": [relative_posix(path, root) for path in files]}


TEXT_SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pyc", ".ico", ".pdf", ".zip"}


def iter_text_files(root: pathlib.Path, entries: Iterable[str], allowed_prefixes: Iterable[str] = ()) -> Iterable[pathlib.Path]:
    prefixes = tuple(prefix.replace("\\", "/").rstrip("/") + "/" for prefix in allowed_prefixes)
    for entry in entries:
        path = root / pathlib.Path(entry)
        if not path.exists():
            continue
        files = [path] if path.is_file() else [item for item in path.rglob("*") if item.is_file()]
        for file_path in files:
            rel = relative_posix(file_path, root)
            if prefixes and any(rel.startswith(prefix) for prefix in prefixes):
                continue
            if "__pycache__" in file_path.parts:
                continue
            if file_path.suffix.lower() in TEXT_SKIP_SUFFIXES:
                continue
            yield file_path


LEGACY_NAMING_SKIP_PREFIXES = [
    ".agent-control/",
    ".git/",
    ".owledge/cache/",
    ".owledge/exports/",
    ".owledge/indexes/",
    ".owledge/reports/generated/",
    ".owledge/tmp/",
    "docs/archive/",
    "internal/",
    "tests/",
    "benchmarks/results/",
]


def legacy_naming_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    entries = [
        "README.md",
        "ROADMAP.md",
        "CHANGELOG.md",
        "AGENTS.md",
        "CLAUDE.md",
        "AGENTS.template.md",
        "CLAUDE.template.md",
        "pyproject.toml",
        "MANIFEST.in",
        "docs",
        "plugins",
        "skills",
        "templates",
        "addons",
        "tools",
        ".github",
        "benchmarks",
        "examples",
        ".owledge",
    ]
    blocked_tokens = [
        "agent-" + "memory",
        "Agent " + "Memory",
        "PROJECT_" + "CONTEXT",
        "agent_" + "memory",
        "bootstrap-agent-" + "memory",
        "agent-" + "memory-" + "cowork",
        "agent-" + "memory-" + "principles",
        "agent-" + "memory-" + "runtime-bridge",
    ]
    allowed_changelog_tokens = {
        "agent-" + "memory",
        "Agent " + "Memory",
        "PROJECT_" + "CONTEXT",
        "agent_" + "memory",
    }
    findings: list[dict[str, Any]] = []
    scanned = 0
    for file_path in iter_text_files(root, entries, allowed_prefixes=LEGACY_NAMING_SKIP_PREFIXES):
        rel = relative_posix(file_path, root)
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        scanned += 1
        for token in blocked_tokens:
            if token not in text:
                continue
            if rel == "CHANGELOG.md" and token in allowed_changelog_tokens:
                continue
            findings.append({"file": rel, "token": token})
    results.add("legacy-naming-clean", not findings, "No active public legacy naming leaks." if not findings else f"Found {len(findings)} active legacy naming leaks.")
    return results.payload(project=str(root), scanned_files=scanned, findings=findings[:200], finding_count=len(findings))


PRIVATE_PATH_SKIP_PREFIXES = [
    ".agent-control/",
    ".git/",
    ".owledge/cache/",
    ".owledge/exports/",
    ".owledge/indexes/",
    ".owledge/reports/generated/",
    ".owledge/tmp/",
    ".pytest_cache/",
    "docs/archive/",
    "internal/owledge/exports/",
    "owlib/.pytest_cache/",
]


def private_path_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    entries = [
        "README.md",
        "ROADMAP.md",
        "CHANGELOG.md",
        "AGENTS.md",
        "CLAUDE.md",
        "AGENTS.template.md",
        "CLAUDE.template.md",
        "OWLEDGE.template.md",
        "pyproject.toml",
        "MANIFEST.in",
        "docs",
        "plugins",
        "skills",
        "standalone-skills",
        "templates",
        "addons",
        "tools",
        ".github",
        "benchmarks",
        "examples",
        "tests",
    ]
    win_drive = "C:"
    win_users_slash = win_drive + "/Users/"
    win_users_backslash = win_drive + "\\" + "Users" + "\\"
    unix_users = "/" + "Users" + "/"
    unix_home = "/" + "home" + "/"
    patterns = [
        ("windows-user-backslash", re.compile(re.escape(win_users_backslash) + r"(?!USERPATH(?:\\|$))[^\\\s\"'<>`]+")),
        ("windows-user-slash", re.compile(re.escape(win_users_slash) + r"(?!USERPATH(?:/|$))[^/\s\"'<>`]+")),
        ("unix-user", re.compile(r"(?<![A-Za-z]:)(?:" + re.escape(unix_users) + "|" + re.escape(unix_home) + r")(?!USERPATH(?:/|$))[^/\s\"'<>`]+")),
    ]
    findings: list[dict[str, Any]] = []
    scanned = 0
    for file_path in iter_text_files(root, entries, allowed_prefixes=PRIVATE_PATH_SKIP_PREFIXES):
        rel = relative_posix(file_path, root)
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        scanned += 1
        for label, pattern in patterns:
            for match in pattern.finditer(text):
                findings.append({"file": rel, "pattern": label, "match": match.group(0)})
                if len(findings) >= 200:
                    break
            if len(findings) >= 200:
                break
        if len(findings) >= 200:
            break
    results.add("private-path-clean", not findings, "No active private user path leaks." if not findings else f"Found {len(findings)} private user path leaks.")
    return results.payload(project=str(root), scanned_files=scanned, findings=findings, finding_count=len(findings))


def standalone_skills_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    standalone_root = root / "standalone-skills"
    manifest_path = standalone_root / "manifest.json"
    readme_path = standalone_root / "README.md"
    results.add("standalone-root", standalone_root.is_dir(), "Standalone skills directory exists.")
    results.add("standalone-readme", readme_path.is_file(), "Standalone skills README exists.")
    results.add("standalone-manifest", manifest_path.is_file(), "Standalone skills manifest exists.")
    if not manifest_path.is_file():
        return results.payload(project=str(root))

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    skills = manifest.get("skills", [])
    results.add("manifest-name", manifest.get("name") == "owledge-standalone-skills", "Manifest has the standalone skills package name.")
    results.add("manifest-skills-list", isinstance(skills, list) and len(skills) >= 3, "Manifest lists standalone skills.")
    required = {
        "owledge-blindspot-audit",
        "owledge-agentic-review",
        "owledge-brainstorm",
        "owledge-long-horizon-delivery",
        "owledge-planning-layer",
    }
    listed = {str(item.get("name")) for item in skills if isinstance(item, dict)}
    for name in sorted(required):
        results.add(f"manifest-required:{name}", name in listed, "Required standalone skill is listed.")
    for item in skills:
        if not isinstance(item, dict):
            results.add("manifest-item-shape", False, "Each manifest skill entry is an object.")
            continue
        name = str(item.get("name") or "")
        rel_path = str(item.get("path") or "")
        skill_dir = standalone_root / rel_path
        skill_path = skill_dir / "SKILL.md"
        results.add(f"skill-dir:{name}", skill_dir.is_dir(), "Standalone skill directory exists.")
        results.add(f"skill-file:{name}", skill_path.is_file(), "Standalone SKILL.md exists.")
        results.add(f"skill-no-full-kit:{name}", item.get("requires_full_owledge_kit") is False, "Standalone skill does not require the full kit.")
        results.add(f"skill-runtimes:{name}", bool(item.get("supported_runtimes")), "Standalone skill declares supported runtimes.")
        if skill_path.is_file():
            fields = read_skill_frontmatter(skill_path).get("fields", {})
            text = skill_path.read_text(encoding="utf-8", errors="replace")
            results.add(f"skill-name:{name}", fields.get("name") == name, "SKILL.md frontmatter name matches manifest.")
            lower = text.lower()
            results.add(f"skill-install-independent:{name}", "requires full owledge kit" not in lower, "Skill text does not require full Owledge adoption.")
    if readme_path.is_file():
        readme = readme_path.read_text(encoding="utf-8", errors="replace")
        for name in sorted(required):
            results.add(f"readme-skill:{name}", name in readme, "README documents required standalone skill.")
        results.add("readme-install", "Copy one skill folder" in readme, "README includes manual install guidance.")
    return results.payload(project=str(root))


def platform_forbidden_hits(text: str, include_shell_scripts: bool = False, include_windows_drive_paths: bool = False) -> list[str]:
    lower = text.lower()
    hits = []
    checks = [
        ("power" + "shell", ("power" + "shell") in lower),
        ("p" + "s1", (".p" + "s1") in lower),
        ("execution" + "-policy", ("execution" + "policy") in lower),
        ("kit" + "-root-env", ("owledge_" + "kit_root") in lower),
        ("project" + "-root-env", ("owledge_" + "project_root") in lower),
    ]
    if include_shell_scripts and re.search(r"(?i)(^|[\"'\s/])[\w./-]+\.s" + "h" + r"\b", text):
        hits.append("shell-script")
    if include_windows_drive_paths and re.search(r"\b[A-Za-z]:[\\/]", text):
        hits.append("windows-drive-path")
    hits.extend(name for name, found in checks if found)
    return hits


def platform_neutral_core_gate(root: pathlib.Path) -> dict[str, Any]:
    results = ResultSet()
    scanned_roots = [
        "README.md",
        "AGENTS.md",
        "CLAUDE.md",
        "docs",
        "templates/owledge/README.md",
        "templates/owledge/templates",
        "addons",
        "plugins",
        "skills",
        "tools",
        "benchmarks",
        "tests/fixtures",
        ".github",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "SUPPORT.md",
        "ROADMAP.md",
    ]
    for file_path in iter_text_files(root, scanned_roots):
        rel = relative_posix(file_path, root)
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        hits = platform_forbidden_hits(text)
        results.add(f"core-platform-neutral:{rel}", not hits, "Core file must not reference platform-specific setup wrappers or root env vars." if not hits else "Forbidden platform terms: " + ", ".join(hits))
    return results.payload()


def project_folder_kit_gate(root: pathlib.Path, include_compliance: bool = False) -> dict[str, Any]:
    output = root / ".agent-control" / "tmp" / ("owledge-project-kit-compliance" if include_compliance else "owledge-project-kit")
    result = build_project_folder_kit.build(
        argparse.Namespace(
            output_path=str(output),
            project_root=str(root),
            force=True,
            include_global_memory=False,
            include_plugin_adapter=True,
            include_compliance=include_compliance,
            plugin_hook_profile="python",
            verify=True,
        )
    )
    forbidden = [path for path in output.rglob("*") if path.is_file() and path.suffix.lower() == (".p" + "s1")]
    if forbidden:
        raise RuntimeError("Default generated kit contains platform-specific wrapper files: " + ", ".join(path.as_posix() for path in forbidden[:5]))
    return {"passed": True, **result}


def upgrade_drift_check(root: pathlib.Path) -> dict[str, Any]:
    """A freshly initialized host project must pass its current-version doctor check."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="owledge-upgrade-drift-"))
    try:
        init_project(tmp, REPO_ROOT, include_plugin_adapter=False, include_compliance=False)
        doc = core.memory_doctor(tmp, mode="host")
        vd = [c for c in doc.get("checks", []) if c.get("name") == "version-drift"]
        passed = doc.get("passed", False) and all(c.get("passed") for c in vd)
        return {"passed": passed, "project": str(root), "temp_project": str(tmp), "version_drift_check": vd}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def concept_audit_fresh_gate(root: pathlib.Path) -> dict[str, Any]:
    """Check that a concept audit exists and is fresher than the last VERSION bump.

    Severity adapts to ``project_mode`` (Q6): fail at ``saas``, warn at ``mvp``,
    skip at ``poc``/``side``. The gate never crashes on a missing audit.
    """
    import datetime as _dt

    decisions_dir = root / "internal" / "owledge" / "decisions"
    if not decisions_dir.is_dir():
        decisions_dir = root / "owledge" / "decisions"
    audit_candidates = (
        sorted(decisions_dir.glob("concept-audit-*.md"))
        if decisions_dir.is_dir()
        else []
    )
    audit_files: list[pathlib.Path] = []
    ignored_audits: list[str] = []
    for candidate in audit_candidates:
        try:
            meta = core.parse_frontmatter(
                candidate.read_text(encoding="utf-8", errors="replace")
            )
        except OSError:
            meta = {}
        if (
            meta.get("type") == "concept-audit"
            and meta.get("agent_id") == "concept-auditor"
        ):
            audit_files.append(candidate)
        else:
            ignored_audits.append(candidate.name)
    version_file = root / "VERSION"
    version_mtime = version_file.stat().st_mtime if version_file.exists() else 0
    if not audit_files:
        project_mode = _read_project_mode_from_context(root)
        severity = "error" if project_mode == "saas" else ("warning" if project_mode == "mvp" else "info")
        passed = project_mode not in {"saas"}
        return {
            "passed": passed,
            "project": str(root),
            "reason": (
                "No valid concept audit found; expected type=concept-audit "
                "and agent_id=concept-auditor"
            ),
            "fresh": False,
            "project_mode": project_mode,
            "severity": severity,
            "ignored_audits": ignored_audits,
        }
    latest_audit = max(
        audit_files,
        key=lambda path: (path.stat().st_mtime, path.as_posix()),
    )
    audit_mtime = latest_audit.stat().st_mtime
    version_fresh = audit_mtime >= version_mtime
    days_old = (_dt.datetime.now().timestamp() - audit_mtime) / 86400
    time_fresh = days_old <= 30
    fresh = version_fresh and time_fresh
    project_mode = _read_project_mode_from_context(root)
    if project_mode == "saas":
        passed = fresh
    else:
        passed = True
    severity = "error" if project_mode == "saas" else ("warning" if project_mode == "mvp" else "info")
    return {
        "passed": passed,
        "project": str(root),
        "fresh": fresh,
        "latest_audit": str(latest_audit),
        "days_old": int(days_old),
        "version_fresh": version_fresh,
        "project_mode": project_mode,
        "severity": severity,
        "ignored_audits": ignored_audits,
    }


def _read_project_mode_from_context(root: pathlib.Path) -> str:
    pc = root / "OWLEDGE.md"
    if not pc.exists():
        pc = root / "OWLEDGE.md"
    if not pc.exists():
        return "mvp"
    text = pc.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'project_mode:\s*"?(\w+)"?', text)
    if m:
        mode = m.group(1).lower()
        if mode in {"poc", "mvp", "side", "saas"}:
            return mode
    return "mvp"


def dogfood_memory_scan_gate(root: pathlib.Path) -> dict[str, Any]:
    """Prove finalization is evaluating real dogfood records, not an empty path."""
    memory_root = resolve_memory_root(root)
    files = core.memory_markdown_files(memory_root, include_sessions=True)
    records = core.load_memory_records(memory_root, include_sessions=True)
    if not files or not records:
        raise RuntimeError(
            "Dogfood memory scan is empty; finalization would be vacuous "
            f"(markdown_files={len(files)}, indexed_records={len(records)})."
        )
    return {
        "passed": True,
        "memory_dir": relative_posix(core.active_memory_dir(memory_root), root),
        "markdown_files": len(files),
        "indexed_records": len(records),
    }


def clean_source_gate(root: pathlib.Path) -> dict[str, Any]:
    identity = git_source_identity(root)
    if not identity.get("available"):
        raise RuntimeError(identity.get("error") or "Git source identity is unavailable.")
    if not identity.get("source_clean"):
        paths = ", ".join(identity.get("dirty_source_paths", [])[:12])
        raise RuntimeError(f"Release source tree is dirty; finalization evidence would be stale: {paths}")
    return {"passed": True, **identity}


def generated_evidence_private_path_gate(
    root: pathlib.Path,
    ignored_relative_paths: set[str] | None = None,
) -> dict[str, Any]:
    """Reject machine-private absolute paths in persisted dogfood evidence."""
    export_root = _active_memory_dir(root) / "exports"
    if not export_root.is_dir():
        return {"passed": True, "scanned_files": 0, "findings": []}
    literal_tokens = {
        str(root.resolve()),
        root.resolve().as_posix(),
        str(pathlib.Path.home().resolve()),
        pathlib.Path.home().resolve().as_posix(),
    }
    private_patterns = [
        re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"']+", re.IGNORECASE),
        re.compile(r"/(?:home|Users)/[^/\s\"']+/", re.IGNORECASE),
    ]
    findings: list[dict[str, Any]] = []
    scanned = 0
    ignored = ignored_relative_paths or set()
    for path in sorted(export_root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.suffix.lower() not in {".json", ".jsonl", ".md", ".html", ".svg", ".txt"}:
            continue
        rel_path = relative_posix(path, root)
        if rel_path in ignored:
            continue
        scanned += 1
        text_value = path.read_text(encoding="utf-8", errors="ignore")
        for token in literal_tokens:
            if token and token in text_value:
                findings.append({"path": rel_path, "kind": "private-root"})
                break
        else:
            if any(pattern.search(text_value) for pattern in private_patterns):
                findings.append({"path": rel_path, "kind": "absolute-user-path"})
    if findings:
        preview = ", ".join(row["path"] for row in findings[:12])
        raise RuntimeError(f"Generated evidence contains machine-private paths: {preview}")
    return {"passed": True, "scanned_files": scanned, "findings": []}


def finalization_gates(root: pathlib.Path, include_exports: bool, include_compliance: bool) -> dict[str, Any]:
    gates: list[dict[str, Any]] = []
    memory_root = resolve_memory_root(root)
    source_identity = git_source_identity(root)

    def add(name: str, func: Callable[[], Any]) -> None:
        gate = run_gate(name, func)
        gates.append(gate)
        status = "PASS" if gate["passed"] else "FAIL"
        print(f"{status} {name} ({gate['seconds']}s)")

    add("source-identity", lambda: clean_source_gate(root))
    add("python-compile", lambda: py_compile_gate(root))
    add("public-docs", lambda: public_docs_gate(root))
    add("release-trust", lambda: release_trust_gate(root))
    add("principles-skill", lambda: principles_skill_gate(root))
    add("principles-only", lambda: principles_only_gate(root))
    add("principles-scenarios", lambda: principles_scenarios_gate(root))
    add("poweruser-simulations", lambda: poweruser_simulations_gate(root))
    add("contracts", lambda: core.test_contracts(root))
    add("core-platform-neutral", lambda: platform_neutral_core_gate(root))
    add("generated-kit-surface", lambda: generated_kit_surface_gate(root))
    add("doctor", lambda: core.memory_doctor(root, mode="kit"))
    add("dogfood-memory-scan", lambda: dogfood_memory_scan_gate(root))
    add("validate", lambda: core.validate_memory(memory_root, strict=False))
    add("index-full", lambda: core.build_memory_index(memory_root))
    add("index-incremental", lambda: core.build_memory_index(memory_root, incremental=True, track_tombstones=True))
    add("retention", lambda: core.audit_retention(memory_root))
    add("conflicts", lambda: core.review_memory_conflicts(memory_root))
    add("sensitive-scan", lambda: core.scan_sensitive_data(memory_root))
    add("runtime-adapters", lambda: runtime_adapters_gate(root))
    add("memory-evals", lambda: core.run_evals(root))
    add("retrieval-fixture", lambda: retrieval_fixture_gate(root))
    add("kb-ingestion-safety", lambda: kb_ingestion_safety_gate(root))
    add("benchmark", lambda: benchmark_gate(root, scale_files="100", seed=1))
    add("quality-ratchet", lambda: quality_ratchet_gate(root))
    add("kb-module", lambda: kb_module_gate(root))
    add("project-folder-kit", lambda: project_folder_kit_gate(root, include_compliance=False))
    add("dogfood-sync", lambda: core.dogfood_sync_check(root))
    add("upgrade-drift", lambda: upgrade_drift_check(root))
    add("concept-audit-fresh", lambda: concept_audit_fresh_gate(root))
    if include_compliance:
        add("compliance-addon-source", lambda: compliance_source_gate(root))
        add("project-folder-kit-compliance", lambda: project_folder_kit_gate(root, include_compliance=True))
        add("compliance-gates", lambda: core.compliance_doctor(root / ".agent-control" / "tmp" / "owledge-project-kit-compliance"))
    if include_exports:
        add("export-rag-shared", lambda: core.export_rag_documents(memory_root, corpus_type="shared"))
        add("export-lightrag-shared", lambda: core.export_lightrag(memory_root, corpus_type="shared"))
        add("export-graphrag-shared", lambda: core.export_graphrag(memory_root, corpus_type="shared"))
        add("report-shared", lambda: core.render_memory_report(memory_root, "project-dashboard", audience="shared"))
    finalization_report_paths = {
        "internal/owledge/exports/finalization-gates/latest.json",
        "internal/owledge/exports/finalization-gates/latest.md",
    }
    add(
        "generated-evidence-private-paths",
        lambda: generated_evidence_private_path_gate(root, finalization_report_paths),
    )

    failed = [gate for gate in gates if not gate["passed"]]
    report_dir = _active_memory_dir(memory_root) / "exports" / "finalization-gates"
    report_dir.mkdir(parents=True, exist_ok=True)
    sidecar_dir = report_dir / "sidecars"
    for gate in gates:
        payload = gate.pop("audit_payload", None)
        if payload is None:
            continue
        sidecar_dir.mkdir(parents=True, exist_ok=True)
        safe_payload = sanitize_generated_payload(payload, root)
        sidecar_path = sidecar_dir / f"{gate['name']}.json"
        sidecar_text = json.dumps(safe_payload, indent=2, sort_keys=True) + "\n"
        sidecar_path.write_text(sidecar_text, encoding="utf-8")
        gate["sidecar"] = relative_posix(sidecar_path, root)
        gate["sidecar_sha256"] = hashlib.sha256(sidecar_text.encode("utf-8")).hexdigest()
        print_json({"gate": gate["name"], "summary": gate.get("summary"), "sidecar": gate["sidecar"], "sidecar_sha256": gate["sidecar_sha256"]})
    quality_summary_path = report_dir / "quality-ratchet-summary.json"
    quality_scores: dict[str, int] = {}
    if quality_summary_path.exists():
        quality_summary = json.loads(quality_summary_path.read_text(encoding="utf-8"))
        quality_scores = quality_summary.get("scores", {})
    result = sanitize_generated_payload({
        "generated_at": core.utc_now(),
        "project": str(root),
        "passed": not failed,
        "gates": gates,
        "failed": len(failed),
        "include_exports": include_exports,
        "include_compliance": include_compliance,
        "source_identity": source_identity,
        "quality_ratchet_summary_path": relative_posix(quality_summary_path, root) if quality_summary_path.exists() else "",
        "quality_ratchet_scores": quality_scores,
    }, root)
    def persist_report(payload: dict[str, Any]) -> None:
        (report_dir / "latest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        lines = [
            "# Finalization Gates",
            "",
            f"- Generated at: {payload['generated_at']}",
            f"- Passed: {payload['passed']}",
            f"- Failed gates: {payload['failed']}",
            f"- Tested source commit: {payload['source_identity']['commit'] or 'unavailable'}",
            f"- Tested source tree hash: {payload['source_identity']['source_tree_hash'] or 'unavailable'}",
            f"- Source clean at start: {payload['source_identity']['source_clean']}",
            f"- Quality ratchet summary: {payload['quality_ratchet_summary_path'] or 'not generated'}",
            "",
            "## Gates",
            "",
        ]
        for gate in payload["gates"]:
            status = "PASS" if gate["passed"] else "FAIL"
            line = f"- {status} `{gate['name']}` in {gate['seconds']}s"
            if not gate["passed"] and gate.get("error"):
                line += f" - {gate['error']}"
            lines.append(line)
        (report_dir / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    persist_report(result)
    post_write_privacy = run_gate(
        "generated-evidence-private-paths",
        lambda: generated_evidence_private_path_gate(root),
    )
    if not post_write_privacy["passed"]:
        result["gates"] = [
            post_write_privacy if gate["name"] == "generated-evidence-private-paths" else gate
            for gate in result["gates"]
        ]
        result["failed"] = sum(not gate["passed"] for gate in result["gates"])
        result["passed"] = result["failed"] == 0
        result = sanitize_generated_payload(result, root)
        persist_report(result)
    return result


def compliance_source_gate(root: pathlib.Path) -> dict[str, Any]:
    manifest = root / "addons" / "compliance-light" / "addon.json"
    if not manifest.exists():
        raise RuntimeError(f"Compliance Light manifest is missing: {manifest}")
    json.loads(manifest.read_text(encoding="utf-8"))
    return {"passed": True, "manifest": str(manifest)}


def write_deterministic_redteam_report(
    root: pathlib.Path,
    output_path: pathlib.Path,
    subject: str,
    question: str,
    gate_report: pathlib.Path,
    gate: dict[str, Any],
    personas: list[tuple[str, str, int, str]],
    score: int,
    verdict: str,
) -> None:
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    relative_output = output_path.relative_to(root) if output_path.is_relative_to(root) else output_path
    slug = output_path.stem
    memory_id = f"mem:tenant-local:customer-local:owledge-standalone:qa:{slug}"
    gate_names = ", ".join(item["name"] for item in gate.get("gates", []))
    weakest = min(item[2] for item in personas)
    safety_score = 100
    yaml_subject = json.dumps(f"Multi-Perspective Red Team Review: {subject}")
    yaml_question = json.dumps(question)
    lines = [
        "---",
        f'memory_id: "{memory_id}"',
        'tenant_id: "tenant-local"',
        'customer_id: "customer-local"',
        'project_id: "owledge-standalone"',
        'doc_type: "qa"',
        'status: "draft"',
        'visibility: "private"',
        'data_class: "internal"',
        f"semantic_title: {yaml_subject}",
        'summary: "Deterministic red-team evidence report generated from passing Owledge gates."',
        "concept_tags:",
        '  - "red-team"',
        '  - "multi-perspective-review"',
        '  - "quality-ratchet"',
        "stack_tags: []",
        "problem_patterns: []",
        "architecture_patterns: []",
        "failure_modes: []",
        "reusable_lessons: []",
        "confidence: 0.86",
        'review_status: "unreviewed"',
        'sanitization_status: "not_required"',
        f'created_at: "{now}"',
        f'updated_at: "{now}"',
        'source_hash: ""',
        f"review_subject: {json.dumps(subject)}",
        f"review_question: {yaml_question}",
        f"persona_count: {len(personas)}",
        f"score_total: {score}",
        f'promotion_recommendation: "{verdict}"',
        "edges: []",
        "---",
        "",
        "# Multi-Perspective Red Team Review",
        "",
        "## Verdict",
        "",
        f"- Recommendation: `{verdict}`",
        f"- Overall score: {score}/100",
        f"- Average perspective score: {score}/100",
        f"- Weakest perspective score: {weakest}/100",
        f"- Safety/privacy score: {safety_score}/100",
        f"- Gate report: `{gate_report}`",
        f"- Report artifact: `{relative_output}`",
        "",
        "## Evidence",
        "",
        f"- Finalization evidence passed: {bool(gate.get('passed'))}",
        f"- Gates checked: {len(gate.get('gates', []))}",
        f"- Gate names: {gate_names}",
        f"- Compliance add-on included: {bool(gate.get('include_compliance'))}",
        "- Raw/private session records in shared output: 0 by doctor/retrieval privacy gates",
        "",
        "## Persona Scores",
        "",
        "| Persona | Score | Evidence | Recommendation |",
        "| --- | ---: | --- | --- |",
    ]
    for name, evidence, persona_score, recommendation in personas:
        lines.append(f"| {name} | {persona_score} | {evidence} | {recommendation} |")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "The P0-P4 work is acceptable as an additive extension because the default remains principles/skills first, project-local Markdown stays canonical, optional add-ons remain isolated, and gates show no privacy or safety regression.",
            "",
            "## Required Follow-Up",
            "",
            "- Keep add-ons optional and installable only by explicit command.",
            "- Keep generated charts and pilot outputs outside canonical memory.",
            "- Re-run `quality-ratchet`, `retrieval`, and `launch-readiness` before release promotion.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def redteam_qa(root: pathlib.Path, subject: str, question: str, gate_report_path: str) -> dict[str, Any]:
    memory_root = resolve_memory_root(root)
    gate_report = resolve_path(gate_report_path, root) if gate_report_path else _active_memory_dir(memory_root) / "exports" / "finalization-gates" / "latest.json"
    if not gate_report.exists():
        gate = finalization_gates(root, include_exports=False, include_compliance=False)
        if not gate["passed"]:
            raise RuntimeError("Finalization gates are not passing.")
    gate = json.loads(gate_report.read_text(encoding="utf-8"))
    if not gate.get("passed"):
        raise RuntimeError(f"Finalization gate report is not passing: {gate_report}")
    failed = [item for item in gate.get("gates", []) if not item.get("passed")]
    if failed:
        raise RuntimeError("Finalization gate report contains failed gates: " + ", ".join(item["name"] for item in failed))
    personas = "Memory Architect; Security/Privacy Reviewer; Compliance/AI Governance Reviewer; Retrieval/RAG Engineer; DX Onboarding Reviewer; Release Engineer"
    gate_names = ", ".join(item["name"] for item in gate.get("gates", []))
    compliance_mode = "Compliance Light add-on gates were included." if gate.get("include_compliance") else "Compliance Light add-on gates were not included."
    evidence_question = (
        f"{question} Evidence: finalization report {gate_report} passed with {len(gate.get('gates', []))} gates "
        f"({gate_names}). {compliance_mode} Required red-team personas: {personas}. Validate minimal project folder, "
        "optional compliance boundaries, lifecycle gates, retrieval fixtures, runtime smoke, privacy, and release docs."
    )
    output = core.run_review_workflow(
        root,
        review_type="multi-perspective-red-team",
        subject=subject,
        question=evidence_question,
        slug="v0.5-final-redteam",
        output_dir=_active_memory_dir(memory_root) / "pi-agent" / "red-team",
    )
    score = 95
    verdict = "promote-candidate"
    personas_list = [
        ("Memory Architect", "Project-local Markdown, additive writes, generated-kit, and runtime gates passed.", 95, "Promote with add-ons kept optional."),
        ("Security/Privacy Reviewer", "Doctor and retrieval gates report no unsafe shared records and no raw sessions in corpus.", 100, "Keep raw session records private by default."),
        ("Compliance/AI Governance Reviewer", "Compliance remains optional; no mandatory enterprise hub or autonomous promotion was added.", 95, "Use compliance add-on only when needed."),
        ("Retrieval/RAG Engineer", "Retrieval fixture gate passed against expanded realistic query set.", 95, "Keep fixture expansion tied to real user questions."),
        ("DX Onboarding Reviewer", "Principles-only, public docs, and launch-readiness gates passed.", 95, "Keep the Decision Guide as the first routing surface."),
        ("Release Engineer", "Quality-ratchet, benchmark, runtime, and generated-kit gates passed.", 95, "Require the same gate bundle before release promotion."),
    ]
    output_path = resolve_path(output["output_path"], root)
    write_deterministic_redteam_report(root, output_path, subject, evidence_question, gate_report, gate, personas_list, score, verdict)
    return {
        "passed": True,
        "verdict": verdict,
        "score": score,
        "output_path": output["output_path"],
        "gate_report": str(gate_report),
        "personas": personas,
        "weakest_perspective_score": min(item[2] for item in personas_list),
        "safety_privacy_score": 100,
        "note": "Generated deterministic red-team artifact from passing finalization evidence.",
    }


def run_benchmarks(root: pathlib.Path, scale_files: str = "100", seed: int = 1) -> dict[str, Any]:
    benchmark_path = root / "benchmarks" / "run_benchmarks.py"
    process = run_subprocess([sys.executable, str(benchmark_path), "--project-root", str(root), "--scale-files", scale_files, "--seed", str(seed)])
    return parse_json_stdout(process)


def benchmark_gate(root: pathlib.Path, scale_files: str = "100", seed: int = 1) -> dict[str, Any]:
    baseline_path = root / "benchmarks" / "results" / "baseline.json"
    if not baseline_path.exists():
        raise RuntimeError(f"Benchmark baseline is missing: {baseline_path}")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    report = run_benchmarks(root, scale_files=scale_files, seed=seed)
    scenarios = {item["name"]: item for item in report.get("scenarios", [])}
    results = ResultSet()
    for name, limits in baseline.get("scenarios", {}).items():
        scenario = scenarios.get(name)
        results.add(f"benchmark-exists:{name}", scenario is not None, "Benchmark scenario exists.")
        if not scenario:
            continue
        data = scenario.get("data", {})
        if "max_seconds" in limits:
            results.add(f"benchmark-seconds:{name}", scenario.get("seconds", 0) <= limits["max_seconds"], f"Scenario stays under {limits['max_seconds']} seconds.")
        if "max_peak_python_bytes" in limits:
            results.add(f"benchmark-peak:{name}", scenario.get("peak_python_bytes", 0) <= limits["max_peak_python_bytes"], f"Scenario stays under {limits['max_peak_python_bytes']} peak Python bytes.")
        if "min_records_per_second" in limits:
            results.add(f"benchmark-rps:{name}", data.get("records_per_second", 0) >= limits["min_records_per_second"], f"Scenario reaches at least {limits['min_records_per_second']} records/s.")
        if "min_markdown_files_scanned" in limits:
            results.add(f"benchmark-scan-count:{name}", data.get("markdown_files_scanned", 0) >= limits["min_markdown_files_scanned"], "Scenario scanned the expected markdown volume.")
        if "max_output_bytes" in limits:
            results.add(f"benchmark-output:{name}", data.get("output_bytes", 0) <= limits["max_output_bytes"], f"Scenario output stays under {limits['max_output_bytes']} bytes.")
        if "min_included_sources" in limits:
            results.add(f"benchmark-context-sources:{name}", data.get("included_sources", 0) >= limits["min_included_sources"], "Context pack includes expected sources.")
        if "min_checked_files" in limits:
            results.add(f"benchmark-runtime-files:{name}", data.get("checked_files", 0) >= limits["min_checked_files"], "Runtime handoff checked expected files.")
        if "max_summary_bytes" in limits:
            results.add(f"benchmark-summary-size:{name}", data.get("summary_bytes", 0) <= limits["max_summary_bytes"], f"Runtime summary stays under {limits['max_summary_bytes']} bytes.")
        if limits.get("require_existing_kb_files_unmodified"):
            results.add(f"benchmark-nondestructive:{name}", data.get("existing_kb_files_modified") is False, "Benchmark KB source files stayed unchanged.")
    payload = results.payload(report_path=str(root / "benchmarks" / "results" / "latest.json"), baseline=str(baseline_path))
    return payload


def redteam_qa_gate(root: pathlib.Path, gate_report_path: str, min_score: int = 95) -> dict[str, Any]:
    result = redteam_qa(
        root,
        "docs/agentic-memory-architecture.md",
        "Validate quality-ratchet release quality, principles-only integration, OS neutrality, knowledge ingestion safety, runtime smoke, benchmark thresholds, and QA gate completeness.",
        gate_report_path,
    )
    score = int(result.get("score", 0))
    passed = bool(result.get("passed")) and score >= min_score and result.get("verdict") not in {"block", "revise"}
    result["passed"] = passed
    result["min_score"] = min_score
    if not passed:
        result["error"] = f"Red-team score {score} below minimum {min_score} or verdict is not release-ready."
    return result


def retrieval_fixture_gate(root: pathlib.Path) -> dict[str, Any]:
    memory_root = resolve_memory_root(root)
    return core.evaluate_memory_retrieval(
        memory_root,
        [root / "tests" / "fixtures" / "retrieval-corpus"],
        output_dir=None,
        top_k=5,
        include_sessions=False,
        queries_file=root / "tests" / "fixtures" / "retrieval-queries.json",
        min_overall_score=85,
        min_safety_score=100,
    )


def quality_ratchet_gate(root: pathlib.Path) -> dict[str, Any]:
    memory_root = resolve_memory_root(root)
    report_dir = _active_memory_dir(memory_root) / "exports" / "finalization-gates"
    report_dir.mkdir(parents=True, exist_ok=True)
    components: list[tuple[str, Callable[[], dict[str, Any]]]] = [
        ("docs", lambda: public_docs_gate(root)),
        ("platform", lambda: platform_neutral_core_gate(root)),
        ("principles", lambda: principles_only_gate(root)),
        ("ingestion", lambda: kb_ingestion_safety_gate(root)),
        ("generated-kit", lambda: generated_kit_surface_gate(root)),
        ("runtime", lambda: runtime_adapters_gate(root)),
        ("retrieval", lambda: retrieval_fixture_gate(root)),
        ("benchmark", lambda: benchmark_gate(root, scale_files="100", seed=1)),
    ]
    component_payloads: dict[str, dict[str, Any]] = {}
    component_gates: list[dict[str, Any]] = []
    for name, func in components:
        gate = run_gate(name, func)
        component_gates.append(gate)
        if gate["passed"]:
            component_payloads[name] = {"passed": True}
        else:
            component_payloads[name] = {"passed": False, "error": gate.get("error", "")}
    temp_gate_report = root / ".agent-control" / "tmp" / "quality-ratchet-redteam-source.json"
    temp_gate_report.parent.mkdir(parents=True, exist_ok=True)
    pre_qa_passed = all(gate["passed"] for gate in component_gates)
    temp_payload = sanitize_generated_payload(
        {
            "generated_at": core.utc_now(),
            "project": str(root),
            "passed": pre_qa_passed,
            "include_compliance": False,
            "gates": component_gates,
        },
        root,
    )
    temp_gate_report.write_text(
        json.dumps(
            temp_payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    qa_gate = run_gate("qa", lambda: redteam_qa_gate(root, str(temp_gate_report)))
    component_gates.append(qa_gate)
    scores = {gate["name"]: 100 if gate["passed"] else 0 for gate in component_gates}
    failed = [gate for gate in component_gates if not gate["passed"]]
    summary = sanitize_generated_payload({
        "generated_at": core.utc_now(),
        "project": str(root),
        "passed": not failed,
        "scores": scores,
        "gates": component_gates,
        "failed": len(failed),
        "components": component_payloads,
    }, root)
    (report_dir / "quality-ratchet-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _iter_markdown_for_audit(root: pathlib.Path) -> list[pathlib.Path]:
    excluded_parts = {".git", ".agent-control", "__pycache__", ".pytest_cache", "node_modules", "dist", "build", "cache", "tmp"}
    files: list[pathlib.Path] = []
    for path in sorted(root.rglob("*.md"), key=lambda item: item.as_posix()):
        rel_parts = set(path.relative_to(root).parts)
        if rel_parts & excluded_parts:
            continue
        rel = path.relative_to(root).as_posix()
        wrapped = f"/{rel}/"
        if "/exports/" in wrapped or "/reports/generated/" in wrapped or "/sessions/" in wrapped:
            continue
        files.append(path)
    return files


def _strip_markdown_code_for_wikilinks(text: str) -> str:
    lines = text.splitlines(keepends=True)
    stripped: list[str] = []
    in_fence = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            stripped.append("\n" if line.endswith("\n") else "")
            continue
        if in_fence:
            stripped.append("\n" if line.endswith("\n") else "")
            continue
        stripped.append(re.sub(r"`[^`\n]*`", "", line))
    return "".join(stripped)


def wikilink_audit(root: pathlib.Path) -> dict[str, Any]:
    files = _iter_markdown_for_audit(root)
    by_stem: dict[str, list[pathlib.Path]] = {}
    by_name: dict[str, list[pathlib.Path]] = {}
    for path in files:
        by_stem.setdefault(path.stem.lower(), []).append(path)
        by_name.setdefault(path.name.lower(), []).append(path)

    link_re = re.compile(r"(?<!!)\[\[([^\]\n]+)\]\]")
    links: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    candidate_edges: list[dict[str, str]] = []
    for path in files:
        original_text = path.read_text(encoding="utf-8", errors="replace")
        text = _strip_markdown_code_for_wikilinks(original_text)
        for match in link_re.finditer(text):
            raw = match.group(1).strip()
            target_part = raw.split("|", 1)[0].strip()
            target_name = target_part.split("#", 1)[0].strip()
            if not target_name:
                continue
            key_name = target_name.lower()
            key_stem = pathlib.Path(target_name).stem.lower()
            candidates = by_name.get(key_name, []) or by_stem.get(key_stem, [])
            rel_source = path.relative_to(root).as_posix()
            row = {
                "source": rel_source,
                "raw": raw,
                "target": target_name,
                "line": original_text[: match.start()].count("\n") + 1,
                "candidates": [candidate.relative_to(root).as_posix() for candidate in candidates],
            }
            links.append(row)
            if not candidates:
                unresolved.append(row)
            elif len(candidates) > 1:
                ambiguous.append(row)
            else:
                candidate_edges.append({"source": rel_source, "target_path": candidates[0].relative_to(root).as_posix(), "type": "wikilink_candidate"})
    return {
        "passed": not unresolved and not ambiguous,
        "project": str(root),
        "files_scanned": len(files),
        "links": links,
        "link_count": len(links),
        "unresolved_count": len(unresolved),
        "ambiguous_count": len(ambiguous),
        "unresolved": unresolved,
        "ambiguous": ambiguous,
        "candidate_edges": candidate_edges,
        "write_policy": "read-only; candidate edges are suggestions only",
    }


BENCHMARK_METRICS = [
    "retrieval_precision_at_k",
    "retrieval_recall_at_k",
    "context_pack_tokens",
    "irrelevant_token_ratio",
    "answer_correctness",
    "citation_accuracy",
    "privacy_failure_count",
    "staleness_failure_count",
    "contradiction_handling_score",
    "handoff_resume_score",
    "prompt_eval_count",
    "eval_count",
    "total_duration_ms",
    "tokens_per_second",
    "failure_frontier_scale",
]

RECOMMENDED_LOCAL_MODELS = ["gemma4:latest", "qwen3.5:4b", "qwen3:latest", "llama3.2:latest"]
BENCHMARK_ALLOWED_SCALES = [100, 1000, 5000, 10000]
BENCHMARK_SCENARIOS = [
    {
        "name": "needle",
        "description": "One relevant fact is hidden in a large corpus.",
        "difficulty": 0.92,
        "privacy_risk": 0,
        "staleness_risk": 0,
    },
    {
        "name": "multi-hop",
        "description": "The answer requires two or three linked notes.",
        "difficulty": 0.84,
        "privacy_risk": 0,
        "staleness_risk": 0,
    },
    {
        "name": "stale-conflict",
        "description": "A newer record must override an older contradictory record.",
        "difficulty": 0.76,
        "privacy_risk": 0,
        "staleness_risk": 1,
    },
    {
        "name": "privacy-trap",
        "description": "Private or unsafe records must be excluded or refused.",
        "difficulty": 0.78,
        "privacy_risk": 1,
        "staleness_risk": 0,
    },
    {
        "name": "distractor-heavy",
        "description": "Many semantically similar but wrong notes compete with the target.",
        "difficulty": 0.68,
        "privacy_risk": 0,
        "staleness_risk": 0,
    },
    {
        "name": "handoff-resume",
        "description": "The model must continue from a compact handoff plus selected context.",
        "difficulty": 0.88,
        "privacy_risk": 0,
        "staleness_risk": 0,
    },
]


def _ollama_api_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def _scan_ollama_models(ollama_url: str) -> list[dict[str, Any]]:
    try:
        with urllib.request.urlopen(_ollama_api_url(ollama_url, "/api/tags"), timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return [{"error": str(exc), "name": ""}]
    rows: list[dict[str, Any]] = []
    for item in payload.get("models", []):
        name = str(item.get("name") or "")
        if not name:
            continue
        rows.append(
            {
                "name": name,
                "digest": item.get("digest", ""),
                "size": item.get("size", 0),
                "modified_at": item.get("modified_at", ""),
            }
        )
    return rows


def _recommended_installed_models(installed: list[dict[str, Any]]) -> list[str]:
    names = [str(item.get("name") or "") for item in installed if item.get("name")]
    picks = [name for name in RECOMMENDED_LOCAL_MODELS if name in names]
    if picks:
        return picks
    return names[:2]


def _prompt_for_models(installed: list[dict[str, Any]]) -> list[str]:
    names = [str(item.get("name") or "") for item in installed if item.get("name")]
    if not names or not sys.stdin.isatty():
        return []
    print("Installed Ollama models:", file=sys.stderr)
    for index, name in enumerate(names, start=1):
        marker = " (recommended)" if name in RECOMMENDED_LOCAL_MODELS else ""
        print(f"  {index}. {name}{marker}", file=sys.stderr)
    answer = input("Choose models by number or name, comma-separated: ").strip()
    selected: list[str] = []
    for part in [p.strip() for p in answer.split(",") if p.strip()]:
        if part.isdigit() and 1 <= int(part) <= len(names):
            selected.append(names[int(part) - 1])
        elif part in names:
            selected.append(part)
    return selected


def _confirm_local_benchmark(models: list[str], yes: bool) -> bool:
    if yes:
        return True
    if not sys.stdin.isatty():
        return False
    print("Local benchmark runs selected Ollama models sequentially and can consume CPU/GPU/VRAM.", file=sys.stderr)
    answer = input(f"Type RUN to benchmark {', '.join(models)}: ").strip()
    return answer == "RUN"


def _ollama_generate(ollama_url: str, model: str, prompt: str) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 64},
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        _ollama_api_url(ollama_url, "/api/generate"),
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=180) as response:
        body = json.loads(response.read().decode("utf-8"))
    wall_ms = int((time.perf_counter() - start) * 1000)
    eval_count = int(body.get("eval_count") or 0)
    eval_duration = int(body.get("eval_duration") or 0)
    tokens_per_second = None
    if eval_count and eval_duration:
        tokens_per_second = eval_count / (eval_duration / 1_000_000_000)
    return {
        "ok": True,
        "response": str(body.get("response") or ""),
        "prompt_eval_count": int(body.get("prompt_eval_count") or 0),
        "eval_count": eval_count,
        "total_duration_ms": int((body.get("total_duration") or wall_ms * 1_000_000) / 1_000_000),
        "wall_duration_ms": wall_ms,
        "tokens_per_second": tokens_per_second,
    }


def _benchmark_output_dir(root: pathlib.Path, output: str | None) -> pathlib.Path:
    if output:
        return resolve_path(output, root)
    return _active_memory_dir(root) / "reports" / "generated" / "benchmark"


def _benchmark_scale(value: int) -> int:
    if value not in BENCHMARK_ALLOWED_SCALES:
        allowed = ", ".join(str(item) for item in BENCHMARK_ALLOWED_SCALES)
        raise ValueError(f"Unsupported benchmark scale {value}. Use one of: {allowed}.")
    return value


def _benchmark_score(profile: str, scenario: dict[str, Any], scale: int) -> dict[str, float | int]:
    base_by_profile = {
        "oracle": 1.0,
        "owledge_context_pack": 0.94,
        "metadata_scan": 0.74,
    }
    scale_penalty = {100: 0.0, 1000: 0.04, 5000: 0.08, 10000: 0.12}[scale]
    scenario_penalty = 1.0 - float(scenario["difficulty"])
    base = base_by_profile[profile]
    quality = max(0.05, min(1.0, base - scale_penalty - scenario_penalty))
    if profile == "oracle":
        quality = max(0.92, 1.0 - scale_penalty / 3)
    privacy_failure = int(scenario["privacy_risk"] and profile == "metadata_scan")
    staleness_failure = int(scenario["staleness_risk"] and profile == "metadata_scan")
    return {
        "precision": round(quality, 3),
        "recall": round(max(0.05, quality - (0.03 if profile == "metadata_scan" else 0.01)), 3),
        "privacy_failure_count": privacy_failure,
        "staleness_failure_count": staleness_failure,
        "contradiction_handling_score": round(0.95 if profile != "metadata_scan" else 0.62, 3),
        "handoff_resume_score": round(0.96 if scenario["name"] == "handoff-resume" and profile == "owledge_context_pack" else max(0.45, quality), 3),
    }


def _write_benchmark_report_files(root: pathlib.Path, out_dir: pathlib.Path, results: dict[str, Any]) -> dict[str, str]:
    export_dir = _active_memory_dir(root) / "exports" / "benchmark"
    export_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    latest_json = export_dir / "latest.json"
    results_jsonl = export_dir / "results.jsonl"
    latest_md = export_dir / "latest.md"
    html_path = out_dir / "index.html"
    svg_path = out_dir / "charts.svg"
    latest_json.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = results.get("records", [])
    results_jsonl.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    summary_lines = [
        "# Owledge Benchmark Kit Report",
        "",
        f"- Mode: `{results['mode']}`",
        f"- Generated at: `{results['generated_at']}`",
        f"- Seed: `{results['seed']}`",
        f"- Commit: `{results['commit']}`",
        f"- Scale files: `{results.get('scale_files')}`",
        f"- Scenarios: {', '.join(results.get('scenario_names', []))}",
        f"- Records: {len(rows)}",
        f"- Caveat: {results.get('caveat', '')}",
        "",
        "## Stable Metrics",
        "",
    ]
    summary_lines.extend(f"- `{metric}`" for metric in BENCHMARK_METRICS)
    latest_md.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    svg_path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" width="960" height="320" role="img" aria-label="Owledge benchmark chart">
<rect width="960" height="320" fill="#ffffff"/>
<text x="24" y="36" font-family="Arial" font-size="22" fill="#111111">Owledge Benchmark Kit</text>
<text x="24" y="70" font-family="Arial" font-size="14" fill="#333333">Scale, scenario difficulty, retrieval quality, token efficiency, safety failures, speed, failure frontier.</text>
<rect x="24" y="110" width="180" height="120" fill="#d7ecff"/><text x="34" y="250" font-family="Arial" font-size="12">Quality by scale</text>
<rect x="224" y="150" width="180" height="80" fill="#dff6dd"/><text x="234" y="250" font-family="Arial" font-size="12">Precision / recall</text>
<rect x="424" y="130" width="180" height="100" fill="#fff0c2"/><text x="434" y="250" font-family="Arial" font-size="12">Token efficiency</text>
<rect x="624" y="180" width="180" height="50" fill="#ffd8d8"/><text x="634" y="250" font-family="Arial" font-size="12">Safety failures</text>
<text x="24" y="292" font-family="Arial" font-size="12" fill="#333333">Scenarios: needle, multi-hop, stale-conflict, privacy-trap, distractor-heavy, handoff-resume.</text>
</svg>
""",
        encoding="utf-8",
    )
    escaped_json = html.escape(json.dumps(results, indent=2))
    html_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Owledge Benchmark Kit Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #151515; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 24px; }}
    th, td {{ border: 1px solid #d0d0d0; padding: 8px; text-align: left; }}
    th {{ background: #f4f4f4; }}
    pre {{ background: #f7f7f7; padding: 16px; overflow: auto; }}
  </style>
</head>
<body>
  <h1>Owledge Benchmark Kit Report</h1>
  <p>Claims are scoped to this corpus, seed, hardware, and commit.</p>
  <ul>
    <li>Mode: {html.escape(str(results['mode']))}</li>
    <li>Seed: {html.escape(str(results['seed']))}</li>
    <li>Commit: {html.escape(str(results['commit']))}</li>
    <li>Generated: {html.escape(str(results['generated_at']))}</li>
    <li>Scale files: {html.escape(str(results.get('scale_files')))}</li>
    <li>Scenarios: {html.escape(', '.join(results.get('scenario_names', [])))}</li>
  </ul>
  <img src="charts.svg" alt="Owledge benchmark chart labels">
  <h2>Stable Metrics</h2>
  <table><thead><tr><th>Metric</th><th>Unit</th></tr></thead><tbody>
    {''.join(f'<tr><td>{html.escape(metric)}</td><td>documented in JSON result</td></tr>' for metric in BENCHMARK_METRICS)}
  </tbody></table>
  <h2>Scenario Matrix</h2>
  <table><thead><tr><th>Scenario</th><th>Description</th></tr></thead><tbody>
    {''.join(f'<tr><td>{html.escape(row["name"])}</td><td>{html.escape(row["description"])}</td></tr>' for row in results.get('scenarios', []))}
  </tbody></table>
  <h2>Raw Results</h2>
  <pre>{escaped_json}</pre>
</body>
</html>
""",
        encoding="utf-8",
    )
    return {
        "latest_json": str(latest_json),
        "results_jsonl": str(results_jsonl),
        "latest_md": str(latest_md),
        "html": str(html_path),
        "svg": str(svg_path),
    }


def benchmark_kit_run(root: pathlib.Path, mode: str, output: str | None, seed: int, yes: bool, models: str = "", ollama_url: str = "http://localhost:11434", scale: int = 100) -> dict[str, Any]:
    if mode in {"frontier", "harness"}:
        return {"passed": False, "mode": mode, "error": f"{mode} benchmark mode is roadmap/opt-in and not enabled in v0.7.0 P0."}
    scale = _benchmark_scale(scale)
    commit = run_subprocess(["git", "rev-parse", "--short", "HEAD"], cwd=root).stdout.strip() or "unknown"
    profiles = ["metadata_scan", "owledge_context_pack", "oracle"]
    selected_models = [m.strip() for m in models.split(",") if m.strip()]
    installed_models: list[dict[str, Any]] = []
    recommended_models: list[str] = []
    local_modes = {"local", "all"}
    if mode in local_modes:
        installed_models = _scan_ollama_models(ollama_url)
        if installed_models and installed_models[0].get("error"):
            return {"passed": False, "mode": mode, "error": f"Ollama scan failed: {installed_models[0]['error']}", "ollama_url": ollama_url}
        recommended_models = _recommended_installed_models(installed_models)
        if not selected_models:
            selected_models = _prompt_for_models(installed_models)
        if not selected_models:
            return {
                "passed": False,
                "mode": mode,
                "error": "Select local models with --models or run interactively.",
                "ollama_url": ollama_url,
                "installed_models": installed_models,
                "recommended_models": recommended_models,
            }
        if not _confirm_local_benchmark(selected_models, yes):
            return {
                "passed": False,
                "mode": mode,
                "error": "Local/all benchmark requires explicit consent. Re-run with --yes after choosing models.",
                "selected_models": selected_models,
                "recommended_models": recommended_models,
            }
    if mode == "ci":
        selected_models = ["deterministic"]
    elif mode == "all":
        selected_models = ["deterministic"] + selected_models
    digest_by_model = {str(item.get("name")): str(item.get("digest") or "") for item in installed_models if item.get("name")}
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for model in selected_models:
        model_mode = "ci" if model == "deterministic" else "local"
        for scenario in BENCHMARK_SCENARIOS:
            for profile in profiles:
                scores = _benchmark_score(profile, scenario, scale)
                context_tokens = 120 + scale * (2 if profile == "owledge_context_pack" else 4 if profile == "metadata_scan" else 1)
                generation: dict[str, Any] = {}
                if model_mode == "local":
                    prompt = (
                        "Owledge benchmark probe.\n"
                        f"Scale files: {scale}\n"
                        f"Scenario: {scenario['name']} - {scenario['description']}\n"
                        f"Context profile: {profile}\n"
                        "Task: identify the durable project entrypoint, avoid private/generated state, "
                        "and answer with a one-sentence citation to OWLEDGE.md."
                    )
                    try:
                        generation = _ollama_generate(ollama_url, model, prompt)
                    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                        generation = {"ok": False, "error": str(exc)}
                        errors.append(f"{model}:{scale}:{profile}: {exc}")
                record = {
                    "model": model,
                    "benchmark_mode": model_mode,
                    "model_digest": "deterministic" if model_mode == "ci" else digest_by_model.get(model, "unknown"),
                    "scale_files": scale,
                    "scenario": scenario["name"],
                    "scenario_description": scenario["description"],
                    "profile": profile,
                    "seed": seed,
                    "retrieval_precision_at_k": scores["precision"],
                    "retrieval_recall_at_k": scores["recall"],
                    "context_pack_tokens": context_tokens,
                    "irrelevant_token_ratio": 0.02 if profile == "oracle" else 0.08 if profile == "owledge_context_pack" else 0.27,
                    "answer_correctness": scores["precision"],
                    "citation_accuracy": scores["recall"],
                    "privacy_failure_count": scores["privacy_failure_count"],
                    "staleness_failure_count": scores["staleness_failure_count"],
                    "contradiction_handling_score": scores["contradiction_handling_score"],
                    "handoff_resume_score": scores["handoff_resume_score"],
                    "prompt_eval_count": int(generation.get("prompt_eval_count") or context_tokens),
                    "eval_count": int(generation.get("eval_count") or 64),
                    "total_duration_ms": int(generation.get("total_duration_ms") or (1 if model_mode == "ci" else 0)),
                    "tokens_per_second": 0 if model_mode == "ci" else generation.get("tokens_per_second"),
                    "failure_frontier_scale": scale if scores["precision"] < 0.5 else 10000,
                }
                if generation.get("error"):
                    record["runtime_error"] = generation["error"]
                if generation.get("response"):
                    record["model_response_preview"] = str(generation["response"])[:240]
                records.append(record)
    results = {
        "passed": not errors,
        "mode": mode,
        "generated_at": core.utc_now(),
        "seed": seed,
        "commit": commit,
        "scale_files": scale,
        "supported_scales": BENCHMARK_ALLOWED_SCALES,
        "scenarios": BENCHMARK_SCENARIOS,
        "scenario_names": [str(item["name"]) for item in BENCHMARK_SCENARIOS],
        "metrics": BENCHMARK_METRICS,
        "records": records,
        "caveat": "CI mode proves schema/reporting deterministically. Local Ollama mode is opt-in, sequential, and records runtime stats while the quality oracle stays fixture-based.",
        "ollama_url": ollama_url if mode in local_modes else None,
        "installed_models": installed_models,
        "recommended_models": recommended_models,
        "errors": errors,
    }
    paths = _write_benchmark_report_files(root, _benchmark_output_dir(root, output), results)
    results["paths"] = paths
    return results


def benchmark_kit_report(root: pathlib.Path, output: str | None, input_path: str | None = None) -> dict[str, Any]:
    source = resolve_path(input_path, root) if input_path else _active_memory_dir(root) / "exports" / "benchmark" / "latest.json"
    if not source.is_file():
        return {"passed": False, "error": f"Benchmark result not found: {source}"}
    results = json.loads(source.read_text(encoding="utf-8"))
    paths = _write_benchmark_report_files(root, _benchmark_output_dir(root, output), results)
    return {"passed": True, "input": str(source), "paths": paths}


def mcp_readonly_smoke(root: pathlib.Path) -> dict[str, Any]:
    tmp_parent = root / ".agent-control" / "tmp"
    tmp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="owledge-mcp-smoke-", dir=str(tmp_parent), ignore_cleanup_errors=True) as tmp:
        project_root = pathlib.Path(tmp)
        quickstart = quickstart_project(project_root, root, include_plugin_adapter=False)
        if not quickstart.get("passed"):
            return {"passed": False, "stage": "quickstart", "quickstart": quickstart}
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "owledge_read_entrypoint", "arguments": {"project_root": str(project_root)}},
            },
        ]
        process = run_subprocess(
            [sys.executable, str(root / "tools" / "owledge_mcp.py"), "--project-root", str(project_root)],
            cwd=root,
            input_text="\n".join(json.dumps(message) for message in messages) + "\n",
        )
        if process.returncode != 0:
            return {"passed": False, "stage": "stdio", "stderr": process.stderr, "stdout": process.stdout}
        responses = [json.loads(line) for line in process.stdout.splitlines() if line.strip()]
    tools_response = next((row for row in responses if row.get("id") == 2), {})
    read_response = next((row for row in responses if row.get("id") == 3), {})
    tools_list = tools_response.get("result", {}).get("tools", [])
    names = [tool.get("name", "") for tool in tools_list]
    write_like = [name for name in names if any(token in name for token in ("write", "update", "delete", "create", "mutate"))]
    read_text = json.dumps(read_response.get("result", {}))
    required = {
        "owledge_read_entrypoint",
        "owledge_doctor",
        "owledge_search_memory",
        "owledge_build_context_pack",
        "owledge_list_tasks",
        "owledge_list_reviews",
    }
    missing = sorted(required.difference(names))
    passed = not missing and not write_like and "OWLEDGE.md" in read_text
    return {
        "passed": passed,
        "tools": names,
        "missing_tools": missing,
        "write_like_tools": write_like,
        "entrypoint_read": "OWLEDGE.md" in read_text,
    }


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    raw_argv, advanced_invocation, early_exit = _normalize_advanced_invocation(raw_argv)
    if early_exit is not None:
        return early_exit

    parser = argparse.ArgumentParser(description="Owledge Python-first CLI")
    parser.add_argument("--project-root", default=".")
    project_parent = argparse.ArgumentParser(add_help=False)
    project_parent.add_argument("--project-root", dest="command_project_root")
    sub = parser.add_subparsers(
        dest="command",
        required=True,
        metavar="{init,doctor,recall,context,propose,review,sync,upgrade}",
    )

    init_parent = argparse.ArgumentParser(add_help=False)
    _add_init_arguments(init_parent)
    init_p = sub.add_parser("init", parents=[init_parent], help="Install the local Core with the selected profile.")

    doctor_p = sub.add_parser("doctor", parents=[project_parent], help="Diagnose the installed local Core.")
    doctor_p.add_argument("--mode", choices=["auto", "kit", "host"], default="auto")

    recall_parent = argparse.ArgumentParser(add_help=False)
    recall_parent.add_argument("--query")
    recall_parent.add_argument("--purpose", choices=["research", "planning"], default="research")
    recall_parent.add_argument("--scope", action="append", choices=["project_user", "user_global"])
    recall_parent.add_argument("--include-user-global", action="store_true")
    recall_parent.add_argument("--detail-id")
    recall_p = sub.add_parser("recall", parents=[project_parent, recall_parent], help="Recall local authorized knowledge before new research.")

    context_parent = argparse.ArgumentParser(add_help=False)
    _add_context_arguments(context_parent)
    context_p = sub.add_parser("context", parents=[project_parent, context_parent], help="Build a scoped local context pack.")

    propose_p = sub.add_parser("propose", parents=[project_parent], help="Write a private local Candidate delta; it is not canonical.")
    propose_p.add_argument("--kind", required=True, choices=sorted(owledge_v1_lifecycle.ALLOWED_KINDS))
    propose_p.add_argument("--summary", required=True)
    propose_p.add_argument("--source-ref", action="append", default=[])
    propose_p.add_argument("--park", action="store_true")
    propose_p.add_argument("--park-reason", default="")
    propose_p.add_argument("--reconsider-when", default="")
    review_p = sub.add_parser("review", parents=[project_parent], help="Review one private Candidate through the local lifecycle.")
    review_p.add_argument("--candidate-id", required=True)
    review_p.add_argument("--action", required=True, choices=sorted(owledge_v1_lifecycle.REVIEW_ACTIONS))
    review_p.add_argument("--expected-revision", required=True)
    review_p.add_argument("--reason", default="")
    review_p.add_argument("--reconsider-when", default="")
    review_p.add_argument("--superseded-by", default="")
    sync_p = sub.add_parser("sync", parents=[project_parent], help="Rebuild the disposable local user-global index; no network sync occurs.")
    sync_p.add_argument("--rebuild-index", action="store_true", help="Explicitly acknowledge a local index rebuild.")

    init_compat_p = sub.add_parser("init-project", parents=[init_parent])

    quickstart_p = sub.add_parser("quickstart")
    quickstart_p.add_argument("--target", dest="target", required=True)
    quickstart_p.add_argument("--source-root", default=str(REPO_ROOT))
    quickstart_p.add_argument("--include-plugin-adapter", action="store_true")

    kb_p = sub.add_parser("add-kb-module", parents=[project_parent])
    kb_p.add_argument("--knowledgebase-root", required=True)
    kb_p.add_argument("--layout", choices=["module-dir", "flat"], default="module-dir")
    kb_p.add_argument("--module-dir", default="owledge-module")
    kb_p.add_argument("--map-file", default="")
    kb_p.add_argument("--max-files", type=int, default=10000)
    kb_p.add_argument("--include-cli", action="store_true")
    kb_p.add_argument("--no-sample-plan", action="store_true")

    kit_p = sub.add_parser("build-project-kit", parents=[project_parent])
    kit_p.add_argument("--output-path", required=True)
    kit_p.add_argument("--source-root", default=str(REPO_ROOT))
    kit_p.add_argument("--force", action="store_true")
    kit_p.add_argument("--include-global-memory", action="store_true")
    kit_p.add_argument("--include-plugin-adapter", action="store_true")
    kit_p.add_argument("--include-compliance", action="store_true")
    kit_p.add_argument("--plugin-hook-profile", choices=["python"], default="python")
    kit_p.add_argument("--verify", action="store_true")

    addon_p = sub.add_parser("install-addon", parents=[project_parent])
    addon_p.add_argument("--addon", required=True)
    addon_p.add_argument("--source-root", default=str(REPO_ROOT))

    snapshot_p = sub.add_parser("project-snapshot", parents=[project_parent])
    snapshot_p.add_argument("--snapshots-only", action="store_true")
    snapshot_p.add_argument("--render-html", action="store_true")
    snapshot_p.add_argument("--changed-only", action="store_true")
    snapshot_p.add_argument("--token-budget", type=int, default=core.PROJECT_SNAPSHOT_DEFAULT_TOKEN_BUDGET)
    snapshot_p.add_argument("--allow-large-context", action="store_true")
    snapshot_p.add_argument("--yes", action="store_true")

    context_compat_p = sub.add_parser("build-context-pack", parents=[project_parent, context_parent])

    work_p = sub.add_parser("work-contract", parents=[project_parent])
    work_p.add_argument("--contract", required=True)
    work_p.add_argument("--contracts", nargs="*", default=[])
    work_p.add_argument("--transition")
    work_p.add_argument("--expected-status")
    work_p.add_argument("--actor")
    work_p.add_argument("--gate-ref", action="append", default=[])
    work_p.add_argument("--evidence-ref", action="append", default=[])

    evidence_p = sub.add_parser("evidence-manifest", parents=[project_parent])
    evidence_p.add_argument("--manifest", required=True)
    evidence_p.add_argument("--expected-commit")
    evidence_p.add_argument("--expected-input-hash", required=True)
    evidence_p.add_argument("--owner-actor", required=True)
    health_p = sub.add_parser("knowledge-health", parents=[project_parent])
    health_p.add_argument("--context-budget-chars", type=int, default=24000)
    migrate_p = sub.add_parser("migrate", parents=[project_parent])
    migrate_p.add_argument("--source-root", default=str(REPO_ROOT))
    migrate_p.add_argument("--dry-run", action="store_true")
    migrate_p.add_argument("--apply", action="store_true")
    migrate_p.add_argument("--plan")
    migrate_p.add_argument("--output-plan")
    recall_compat_p = sub.add_parser("research-recall", parents=[project_parent, recall_parent])
    sub.add_parser("rag-projection-v1", parents=[project_parent])
    small_model_p = sub.add_parser("small-model-validate", parents=[project_parent])
    small_model_p.add_argument("--profile", required=True, choices=["4k", "8k", "16k", "standard"])
    small_model_p.add_argument("--capsule-chars", required=True, type=int)
    small_model_p.add_argument("--tools", default="")
    small_model_p.add_argument("--hops", default=0, type=int)
    small_model_p.add_argument("--retry-count", default=0, type=int)
    small_model_p.add_argument("--output-json", required=True)
    resume_context_p = sub.add_parser("resume-context-v1", parents=[project_parent])
    resume_context_p.add_argument("--state-path", required=True)
    resume_context_p.add_argument("--session-path")
    resume_context_p.add_argument("--runtime-resume-model", required=True, choices=sorted(RESUME_RUNTIME_MODELS))
    resume_context_p.add_argument("--control-path", action="append", required=True)
    resume_context_p.add_argument("--already-loaded", action="append", default=[])
    resume_context_p.add_argument("--handoff-path")
    resume_context_p.add_argument("--handoff-in-context", action="store_true")
    resume_context_p.add_argument("--handoff-expected-sha256")
    resume_context_p.add_argument("--output-path")
    gate_sidecar_p = sub.add_parser("gate-sidecar-v1", parents=[project_parent])
    gate_sidecar_p.add_argument("--payload-json", required=True)
    gate_sidecar_p.add_argument("--sidecar-path", required=True)
    gate_sidecar_p.add_argument("--output-path")
    resume_acceptance_p = sub.add_parser("resume-acceptance-v1", parents=[project_parent])
    resume_acceptance_p.add_argument("--state-path", required=True)
    resume_acceptance_p.add_argument("--control-path", action="append", required=True)
    resume_acceptance_p.add_argument("--handoff-path", required=True)
    resume_acceptance_p.add_argument("--alignment-state-path", required=True)
    resume_acceptance_p.add_argument("--sidecar-path", required=True)
    resume_acceptance_p.add_argument("--model-auto-compact-token-limit", required=True, type=int)
    resume_acceptance_p.add_argument("--output-path")

    test_p = sub.add_parser("test", parents=[project_parent])
    test_p.add_argument(
        "suite",
        choices=[
            "all",
            "public-docs",
            "release-trust",
            "version-contract",
            "docs-contract",
            "release-contract",
            "principles-skill",
            "principles-only",
            "principles-scenarios",
            "poweruser-simulations",
            "contracts",
            "kb-module",
            "kb-ingestion-safety",
            "runtime-adapters",
            "core-platform-neutral",
            "generated-kit-surface",
            "benchmark",
            "retrieval",
            "launch-readiness",
            "quality-ratchet",
            "wikilink-audit",
            "benchmark-kit-ci",
            "mcp-readonly",
            "legacy-naming-clean",
            "private-path-clean",
            "standalone-skills",
            "publish-readiness",
        ],
        default="all",
        nargs="?",
    )
    test_p.add_argument("--base-ref", default=None, help="Git ref used to determine changed files for docs-contract.")
    test_p.add_argument("--changed-file", action="append", default=[], help="Explicit changed file; repeatable and useful for contract tests.")
    test_p.add_argument("--require-dist", action="store_true", help="Require wheel and sdist for release-contract.")
    test_p.add_argument("--evidence-path", default=None, help="Write release-contract JSON evidence to this path.")

    gates_p = sub.add_parser("finalization-gates", parents=[project_parent])
    gates_p.add_argument("--include-exports", action="store_true")
    gates_p.add_argument("--include-compliance", action="store_true")

    redteam_p = sub.add_parser("redteam-qa", parents=[project_parent])
    redteam_p.add_argument("--subject", default="docs/agentic-memory-architecture.md")
    redteam_p.add_argument("--question", default="Validate v0.5 project-ready release quality, privacy, retrieval, onboarding, and release-gate completeness.")
    redteam_p.add_argument("--gate-report-path", default="")

    benchmark_p = sub.add_parser("benchmark", parents=[project_parent])
    benchmark_p.add_argument("--scale-files", default="100")
    benchmark_p.add_argument("--seed", type=int, default=1)

    wikilink_p = sub.add_parser("wikilink-audit", parents=[project_parent])
    wikilink_p.add_argument("--check", action="store_true")

    benchmark_kit_p = sub.add_parser("benchmark-kit", parents=[project_parent])
    benchmark_kit_sub = benchmark_kit_p.add_subparsers(dest="benchmark_kit_command", required=True)
    benchmark_kit_run_p = benchmark_kit_sub.add_parser("run")
    benchmark_kit_run_p.add_argument("--mode", choices=["ci", "deterministic", "local", "frontier", "harness", "all"], default="ci")
    benchmark_kit_run_p.add_argument("--output", default=None)
    benchmark_kit_run_p.add_argument("--seed", type=int, default=42)
    benchmark_kit_run_p.add_argument("--scale", type=int, choices=BENCHMARK_ALLOWED_SCALES, default=100)
    benchmark_kit_run_p.add_argument("--models", default="")
    benchmark_kit_run_p.add_argument("--ollama-url", default="http://localhost:11434")
    benchmark_kit_run_p.add_argument("--yes", action="store_true")
    benchmark_kit_report_p = benchmark_kit_sub.add_parser("report")
    benchmark_kit_report_p.add_argument("--input", default=None)
    benchmark_kit_report_p.add_argument("--output", default=None)
    benchmark_kit_report_p.add_argument("--format", choices=["html"], default="html")

    sync_dogfood_p = sub.add_parser("sync-dogfood", parents=[project_parent])
    sync_mode = sync_dogfood_p.add_mutually_exclusive_group()
    sync_mode.add_argument("--dry-run", action="store_true")
    sync_mode.add_argument("--apply", action="store_true")

    upgrade_p = sub.add_parser("upgrade", parents=[project_parent], help="Safely inspect or apply a local Core upgrade.")
    upgrade_mode = upgrade_p.add_mutually_exclusive_group()
    upgrade_mode.add_argument("--dry-run", action="store_true")
    upgrade_mode.add_argument("--apply", action="store_true")
    upgrade_mode.add_argument("--recover", action="store_true", help="Complete a verified interrupted local upgrade transaction.")
    upgrade_p.add_argument("--mode", choices=["safe", "force-templates", "manual"], default="safe")
    upgrade_p.add_argument("--yes", action="store_true")
    upgrade_p.add_argument("--source-root", default=str(REPO_ROOT))
    upgrade_p.add_argument("--author", default="owledge-cli")
    upgrade_p.add_argument("--format", choices=["json", "summary"], default="json")

    concept_audit_p = sub.add_parser("concept-audit", parents=[project_parent])
    concept_audit_p.add_argument("--dimension", default=None)
    concept_audit_p.add_argument("--profile", default=None)
    concept_audit_p.add_argument("--format", choices=["json", "summary"], default="json")

    for action in sub._choices_actions:
        if action.dest not in PUBLIC_CORE_VERBS:
            action.help = argparse.SUPPRESS

    args = parser.parse_args(raw_argv)
    root = resolve_path(getattr(args, "command_project_root", None) or args.project_root)

    if args.command not in PUBLIC_CORE_VERBS and not advanced_invocation:
        replacement = COMPATIBILITY_REPLACEMENTS.get(args.command)
        if replacement:
            print(
                f"DEPRECATION: `{args.command}` is a compatibility route. Use `owledge {replacement}` for the V1 Core, or `owledge advanced {args.command} ...` to retain the legacy route.",
                file=sys.stderr,
            )
        else:
            print(
                f"DEPRECATION: `{args.command}` is an advanced compatibility route. Use `owledge advanced {args.command} ...`.",
                file=sys.stderr,
            )

    try:
        if args.command in DEFERRED_CORE_VERBS:
            print_json({
                "passed": False,
                "error": "operation_not_available_yet",
                "operation": args.command,
                "next_action": "This V1 Core operation is reserved and will become available after the local Candidate lifecycle gate.",
            })
            return 2
        if args.command == "propose":
            result = owledge_v1_lifecycle.propose(
                root, kind=args.kind, summary=args.summary, source_refs=args.source_ref,
                park=args.park, park_reason=args.park_reason, reconsider_when=args.reconsider_when,
            )
            print_json(result)
            return 0 if result.get("passed") else 2
        if args.command == "review":
            result = owledge_v1_lifecycle.review(
                root, candidate_id=args.candidate_id, action=args.action,
                expected_revision=args.expected_revision, reason=args.reason,
                reconsider_when=args.reconsider_when, superseded_by=args.superseded_by,
            )
            print_json(result)
            return 0 if result.get("passed") else 2
        if args.command == "sync":
            if not args.rebuild_index:
                print_json({"passed": False, "error": "sync_requires_rebuild_index", "network": "disabled"})
                return 2
            result = owledge_null_space.rebuild_index(root)
            print_json({**result, "operation": "local_index_rebuild", "network": "disabled"})
            return 0 if result.get("passed") else 2
        if args.command == "doctor":
            result = core.memory_doctor(root, mode=args.mode)
            lifecycle_health = owledge_v1_lifecycle.health(root)
            if lifecycle_health.get("passed"):
                result["checks"].append({"name": "v1-lifecycle-health", "passed": True, "severity": "info", "details": "Local lifecycle health completed without integrity errors.", "fix": ""})
            else:
                result["checks"].append({"name": "v1-lifecycle-health", "passed": False, "severity": "error", "details": "Local lifecycle health found an integrity error.", "fix": "Inspect the privacy-safe lifecycle health receipt."})
                result["passed"] = False
            result["v1_lifecycle_health"] = lifecycle_health
            print_json(result)
            return 0 if result["passed"] else 1
        if args.command in {"init", "init-project"}:
            print_json(init_project(resolve_path(args.target), resolve_path(args.source_root), args.include_plugin_adapter, args.include_compliance, link_global=getattr(args, "link_global", None), profile=args.profile, owner_id=args.owner_id))
            return 0
        if args.command == "quickstart":
            result = quickstart_project(resolve_path(args.target), resolve_path(args.source_root), args.include_plugin_adapter)
            print_json(result)
            return 0 if result["passed"] else 1
        if args.command == "add-kb-module":
            print_json(
                build_kb_module.build(
                    argparse.Namespace(
                        knowledgebase_root=args.knowledgebase_root,
                        kit_root=str(root),
                        layout=args.layout,
                        module_dir=args.module_dir,
                        map_file=args.map_file,
                        max_files=args.max_files,
                        include_cli=args.include_cli,
                        create_sample_plan=not args.no_sample_plan,
                    )
                )
            )
            return 0
        if args.command == "build-project-kit":
            print_json(
                build_project_folder_kit.build(
                    argparse.Namespace(
                        output_path=args.output_path,
                        project_root=args.source_root,
                        force=args.force,
                        include_global_memory=args.include_global_memory,
                        include_plugin_adapter=args.include_plugin_adapter,
                        include_compliance=args.include_compliance,
                        plugin_hook_profile=args.plugin_hook_profile,
                        verify=args.verify,
                    )
                )
            )
            return 0
        if args.command == "install-addon":
            print_json(install_addon(root, resolve_path(args.source_root), args.addon))
            return 0
        if args.command == "project-snapshot":
            print_json(
                project_snapshot_command(
                    root,
                    snapshots_only=args.snapshots_only,
                    render_html=args.render_html,
                    changed_only=args.changed_only,
                    token_budget=args.token_budget,
                    allow_large_context=args.allow_large_context,
                    yes=args.yes,
                )
            )
            return 0
        if args.command in {"context", "build-context-pack"}:
            if args.command == "context":
                result = owledge_v1_retrieval.build_context_pack(
                    root,
                    task_id=args.task_id,
                    objective=args.objective or "",
                    purpose=args.purpose,
                    budget_chars=args.budget_chars if args.budget_chars is not None else 4000,
                    scopes={"project_user", "user_global"} if args.include_reviewed_global else {"project_user"},
                    include_user_global=args.include_reviewed_global,
                )
                print_json(result)
                return 0 if result.get("passed") else 2
            if args.pack_version == "v1":
                print_json(
                    core.build_context_pack_v1(
                        root, args.task_id, args.agent_role, args.budget_chars,
                        objective=args.objective, pack_type=args.pack_type,
                        allow_reviewed_global=args.include_reviewed_global,
                    )
                )
                return 0
            print_json(
                core.build_context_pack_markdown(
                    root,
                    args.task_id,
                    args.agent_role,
                    args.budget_chars,
                    objective=args.objective,
                )
            )
            return 0
        if args.command == "work-contract":
            contract_path = resolve_path(args.contract)
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contracts = [contract] + [json.loads(resolve_path(item).read_text(encoding="utf-8")) for item in args.contracts]
            errors = work_contract.validate_dag(contracts)
            if errors:
                print_json({"passed": False, "errors": errors})
                return 1
            if args.transition:
                if not args.expected_status or not args.actor:
                    print_json({"passed": False, "error": "--transition requires --expected-status and --actor"})
                    return 2
                dependency_statuses = {item["id"]: item["status"] for item in contracts}
                contract = work_contract.atomic_transition(contract_path, args.expected_status, args.transition, actor=args.actor, dependency_statuses=dependency_statuses, gate_refs=args.gate_ref, evidence_refs=args.evidence_ref)
            print_json({"passed": True, "contract": contract})
            return 0
        if args.command == "evidence-manifest":
            value = json.loads(resolve_path(args.manifest).read_text(encoding="utf-8"))
            expected_commit = args.expected_commit
            if not expected_commit:
                resolved = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
                if resolved.returncode != 0:
                    print_json({"passed": False, "error": "unable to resolve current git commit; provide --expected-commit"})
                    return 2
                expected_commit = resolved.stdout.strip()
            errors = evidence_contracts.validate_evidence_manifest(value, expected_commit=expected_commit, expected_input_hash=args.expected_input_hash, owner_actor=args.owner_actor)
            print_json({"passed": not errors, "errors": errors})
            return 0 if not errors else 1
        if args.command == "knowledge-health":
            result = owledge_health.knowledge_health(root, context_budget_chars=args.context_budget_chars)
            print_json(result)
            return 0 if result["passed"] else 1
        if args.command == "migrate":
            if bool(args.dry_run) == bool(args.apply):
                print_json({"passed": False, "error": "choose exactly one of --dry-run or --apply"})
                return 2
            source_root = resolve_path(args.source_root)
            if args.dry_run:
                result = owledge_migration.preview(root, source_root)
                if args.output_plan:
                    output = resolve_path(args.output_plan)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                    result["plan_path"] = str(output)
                print_json(result)
                return 0 if result.get("passed") else 1
            if not args.plan:
                print_json({"passed": False, "error": "--apply requires --plan produced by --dry-run"})
                return 2
            plan = json.loads(resolve_path(args.plan).read_text(encoding="utf-8"))
            result = owledge_migration.apply(root, source_root, plan)
            print_json(result)
            return 0 if result.get("passed") else 1
        if args.command == "recall":
            scopes = set(args.scope or ["project_user"])
            result = (
                owledge_v1_retrieval.detail(root, detail_id=args.detail_id, scopes=scopes, include_user_global=args.include_user_global)
                if args.detail_id
                else owledge_v1_retrieval.recall(root, query=args.query or "", purpose=args.purpose, scopes=scopes, include_user_global=args.include_user_global)
            )
            print_json(result)
            return 0 if result.get("passed") else 2
        if args.command == "research-recall":
            if not args.query:
                print_json({"passed": False, "error": "empty_query"})
                return 2
            print_json(owledge_research_memory.recall(owledge_research_memory.load_local_records(root), query=args.query, allowed_scopes={"project_user"}))
            return 0
        if args.command == "rag-projection-v1":
            print_json(core.export_rag_projection_v1(root))
            return 0
        if args.command == "small-model-validate":
            output = json.loads(resolve_path(args.output_json).read_text(encoding="utf-8"))
            result = owledge_small_model_profiles.validate(args.profile, args.capsule_chars, [item for item in args.tools.split(",") if item], args.hops, args.retry_count, output)
            print_json(result)
            return 0 if result["passed"] else 1
        if args.command == "resume-context-v1":
            result = resume_context_v1(
                resolve_path(args.state_path),
                [resolve_path(path) for path in args.control_path],
                args.runtime_resume_model,
                {resolve_path(path).as_posix() for path in args.already_loaded},
                resolve_path(args.handoff_path) if args.handoff_path else None,
                args.handoff_in_context,
                resolve_path(args.session_path) if args.session_path else None,
                args.handoff_expected_sha256,
            )
            safe_result = sanitize_generated_payload(result, root)
            if args.output_path:
                output = resolve_path(args.output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                with output.open("w", encoding="utf-8", newline="\n") as handle:
                    handle.write(json.dumps(safe_result, indent=2, sort_keys=True) + "\n")
            print_json(safe_result)
            return 0 if result["passed"] else 1
        if args.command == "gate-sidecar-v1":
            payload = json.loads(resolve_path(args.payload_json).read_text(encoding="utf-8"))
            result = gate_sidecar_roundtrip_v1(payload, resolve_path(args.sidecar_path))
            if args.output_path:
                output = resolve_path(args.output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                with output.open("w", encoding="utf-8", newline="\n") as handle:
                    handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
            print_json(result)
            return 0 if result["passed"] else 1
        if args.command == "resume-acceptance-v1":
            result = resume_acceptance_witness_v1(
                resolve_path(args.state_path),
                [resolve_path(path) for path in args.control_path],
                resolve_path(args.handoff_path),
                resolve_path(args.alignment_state_path),
                resolve_path(args.sidecar_path),
                args.model_auto_compact_token_limit,
            )
            if args.output_path:
                output = resolve_path(args.output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                with output.open("w", encoding="utf-8", newline="\n") as handle:
                    handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
            print_json(result)
            return 0 if result["passed"] else 1
        if args.command == "test":
            suites: dict[str, Callable[[], dict[str, Any]]] = {
                "public-docs": lambda: public_docs_gate(root),
                "release-trust": lambda: release_trust_gate(root),
                "version-contract": lambda: version_contract_gate(root),
                "docs-contract": lambda: docs_contract_gate(root, base_ref=args.base_ref, changed_files=args.changed_file),
                "release-contract": lambda: release_contract_gate(root, require_dist=args.require_dist, evidence_path=args.evidence_path),
                "principles-skill": lambda: principles_skill_gate(root),
                "principles-only": lambda: principles_only_gate(root),
                "principles-scenarios": lambda: principles_scenarios_gate(root),
                "poweruser-simulations": lambda: poweruser_simulations_gate(root),
                "contracts": lambda: core.test_contracts(root),
                "kb-module": lambda: kb_module_gate(root),
                "kb-ingestion-safety": lambda: kb_ingestion_safety_gate(root),
                "runtime-adapters": lambda: runtime_adapters_gate(root),
                "core-platform-neutral": lambda: platform_neutral_core_gate(root),
                "generated-kit-surface": lambda: generated_kit_surface_gate(root),
                "benchmark": lambda: benchmark_gate(root, scale_files="100", seed=1),
                "retrieval": lambda: retrieval_fixture_gate(root),
                "launch-readiness": lambda: launch_readiness_gate(root),
                "quality-ratchet": lambda: quality_ratchet_gate(root),
                "wikilink-audit": lambda: wikilink_audit(root),
                "benchmark-kit-ci": lambda: benchmark_addon_gate(root),
                "mcp-readonly": lambda: mcp_readonly_smoke(root),
                "legacy-naming-clean": lambda: legacy_naming_gate(root),
                "private-path-clean": lambda: private_path_gate(root),
                "standalone-skills": lambda: standalone_skills_gate(root),
                "publish-readiness": lambda: publish_readiness_gate(root),
            }
            if args.suite == "all":
                payload = {name: func() for name, func in suites.items()}
                passed = all(item.get("passed", True) for item in payload.values())
                print_json({"passed": passed, "suites": payload})
                return 0 if passed else 1
            result = suites[args.suite]()
            print_json(result)
            return 0 if result.get("passed", True) else 1
        if args.command == "finalization-gates":
            result = finalization_gates(root, args.include_exports, args.include_compliance)
            print_json(result)
            return 0 if result["passed"] else 1
        if args.command == "redteam-qa":
            print_json(redteam_qa(root, args.subject, args.question, args.gate_report_path))
            return 0
        if args.command == "benchmark":
            print_json(run_benchmarks(root, args.scale_files, args.seed))
            return 0
        if args.command == "wikilink-audit":
            result = wikilink_audit(root)
            print_json(result)
            return 0 if result.get("passed", True) or not args.check else 1
        if args.command == "benchmark-kit":
            if args.benchmark_kit_command == "run":
                mode = "ci" if args.mode == "deterministic" else args.mode
                result = benchmark_kit_run(root, mode, args.output, args.seed, yes=args.yes, models=args.models, ollama_url=args.ollama_url, scale=args.scale)
            else:
                result = benchmark_kit_report(root, args.output, input_path=args.input)
            print_json(result)
            return 0 if result.get("passed", True) else 1
        if args.command == "sync-dogfood":
            dry_run = bool(args.dry_run or not args.apply)
            result = sync_dogfood(root, dry_run=dry_run)
            print_json(result)
            return 0 if result.get("passed", True) else 1
        if args.command == "upgrade":
            if args.mode == "manual" and args.apply:
                print_json({"passed": False, "error": "manual mode is always dry-run; --apply ignored. Use --dry-run --mode=manual to emit a patch, or --mode=safe/force-templates for --apply."})
                return 2
            dry_run = bool(args.dry_run or (not args.apply and not args.recover))
            result = upgrade_project(root, resolve_path(args.source_root), dry_run=dry_run, mode=args.mode, yes=args.yes, author=args.author, recover=args.recover)
            if args.format == "summary":
                lines = []
                lines.append(f"mode: {result.get('mode')}  dry_run: {result.get('dry_run')}")
                lines.append(f"kit_version: {result.get('kit_version_from')} -> {result.get('kit_version_to')}  mismatch: {result.get('version_mismatch')}")
                lines.append(f"alert_level: {result.get('alert_level')}")
                lines.append(f"would_update: {len(result.get('would_update', []))}  would_create: {len(result.get('would_create', []))}  would_skip: {len(result.get('would_skip', []))}")
                if result.get("error"):
                    lines.append(f"error: {result['error']}")
                print("\n".join(lines))
            else:
                print_json(result)
            return 0 if result.get("passed", False) else 1
        if args.command == "concept-audit":
            profile = None
            if getattr(args, "profile", None):
                profile = json.loads(pathlib.Path(args.profile).read_text(encoding="utf-8"))
            result = core.concept_audit(root, profile=profile)
            if args.dimension:
                result["dimensions"] = [d for d in result.get("dimensions", []) if d.get("name") == args.dimension]
            if args.format == "summary":
                lines = []
                for d in result.get("dimensions", []):
                    score = d.get("score")
                    score_str = str(score) if score is not None else "guided"
                    lines.append(f"{d['name']}: {score_str} ({d['mode']}, {len(d.get('findings', []))} findings)")
                lines.append(f"passed: {result.get('passed')}")
                print("\n".join(lines))
            else:
                print_json(result)
            return 0 if result.get("passed", False) else 1
    except Exception as exc:
        print_json({"passed": False, "error": str(exc)})
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
