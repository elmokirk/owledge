"""Gate set 3 - dogfood sync one-way stress tests."""

from __future__ import annotations

import json
import pathlib

from conftest import run_owledge, run_cli, write_file, REPO_ROOT


def test_dogfood_sync_one_way(fresh_project):
    """E5: sync-dogfood reconciles internal->templates; reverse-edit internal leaves templates unchanged.

    Uses the repo root (maintainer context) since dogfood-sync operates on
    templates/agent-memory/templates vs internal/agent-memory/templates.
    """
    repo = REPO_ROOT
    internal_template = repo / "internal" / "agent-memory" / "templates" / "task-card-template.md"
    product_template = repo / "templates" / "agent-memory" / "templates" / "task-card-template.md"
    if not internal_template.is_file() or not product_template.is_file():
        import pytest
        pytest.skip("dogfood templates not present in this checkout")
    original_product = product_template.read_bytes()
    original_internal = internal_template.read_bytes()
    try:
        internal_template.write_text("# tampered internal\n", encoding="utf-8")
        sync_result = run_owledge(["sync-dogfood", "--apply"], repo)
        assert sync_result.returncode == 0, f"sync-dogfood failed: {sync_result.stderr}"
        assert internal_template.read_bytes() == original_product, "internal not reconciled to product"
        product_template.write_text("# reverse tampered product\n", encoding="utf-8")
        run_owledge(["sync-dogfood", "--apply"], repo)
        assert product_template.read_bytes() != b"# tampered internal\n", "sync wrote to product tree (must be one-way)"
    finally:
        product_template.write_bytes(original_product)
        internal_template.write_bytes(original_internal)


def test_dogfood_sync_ignores_dogfood_only(fresh_project):
    """E5: editing internal/agent-memory/decision-trace/* leaves dogfood-sync gate passed=True."""
    repo = REPO_ROOT
    decision_trace_dir = repo / "internal" / "agent-memory" / "decision-trace"
    if not decision_trace_dir.is_dir():
        import pytest
        pytest.skip("internal/agent-memory/decision-trace not present")
    sentinel = decision_trace_dir / "_test_sentinel.md"
    sentinel_existed = sentinel.exists()
    original = sentinel.read_bytes() if sentinel_existed else None
    try:
        sentinel.write_text("# test sentinel - dogfood only\n", encoding="utf-8")
        check = run_cli(["dogfood-sync-check"], repo)
        out = json.loads(check.stdout)
        assert out["passed"] is True, f"dogfood-sync-check failed after editing dogfood-only file: {out}"
    finally:
        if sentinel_existed:
            sentinel.write_bytes(original)
        else:
            sentinel.unlink(missing_ok=True)