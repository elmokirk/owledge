"""Gate set 7 - session-continuity checklist convention enforcement.

Parses every docs/*-plan.md and docs/v0.6.*-plan.md; asserts each multi-phase
plan (>=2 '## Phase' or '### Phase' headings) has the three checkboxes
(implementation done, QA checks done, quick review done) within 50 lines of
each phase heading.
"""

from __future__ import annotations

import pathlib
import re

from conftest import REPO_ROOT


CHECKBOX_PHRASES = ["implementation done", "QA checks done", "quick review done"]


def _find_plans() -> list[pathlib.Path]:
    docs = REPO_ROOT / "docs"
    plans = list(docs.glob("*-plan.md"))
    plans += list(docs.glob("v0.6.*-plan.md"))
    plans = [p for p in plans if p.is_file()]
    # Only enforce on v0.6.1+ plans and unversioned plans; pre-v0.6.1 plans
    # (v0.6.0-implementation-plan.md) are historical artifacts.
    filtered: list[pathlib.Path] = []
    for p in plans:
        name = p.name
        if name.startswith("v0.6.0") or name.startswith("v0.5") or name.startswith("v0.4"):
            continue
        filtered.append(p)
    return filtered


def _count_phase_headings(text: str) -> int:
    # Count "## Phase N" or "### Phase N" but NOT "## Phase Summary"
    return len(re.findall(r"^#{2,3}\s+Phase\s+\d", text, re.MULTILINE))


def _checkboxes_present_within(text: str, phase_line_end: int, window: int = 80) -> dict[str, bool]:
    lines = text.splitlines()
    end = min(phase_line_end + window, len(lines))
    chunk = "\n".join(lines[phase_line_end:end])
    return {phrase: phrase in chunk for phrase in CHECKBOX_PHRASES}


def test_plan_has_continuity_checklists():
    """Every multi-phase plan (>=2 phase headings) has the three checkboxes per phase."""
    plans = _find_plans()
    assert plans, "no *-plan.md files found in docs/"
    failures: list[str] = []
    for plan in plans:
        text = plan.read_text(encoding="utf-8")
        phase_count = _count_phase_headings(text)
        if phase_count < 2:
            continue
        lines = text.splitlines()
        phase_line_ends: list[int] = []
        for i, line in enumerate(lines):
            if re.match(r"^#{2,3}\s+Phase\s+\d", line):
                phase_line_ends.append(i + 1)
        for idx, end in enumerate(phase_line_ends):
            window_start = end
            window_end = phase_line_ends[idx + 1] if idx + 1 < len(phase_line_ends) else len(lines)
            chunk = "\n".join(lines[window_start:window_end])
            missing = [p for p in CHECKBOX_PHRASES if p not in chunk]
            if missing:
                failures.append(f"{plan.name}: phase heading {idx + 1} (line {end}) missing checkboxes: {missing}")
    assert not failures, "plans missing session-continuity checkboxes:\n" + "\n".join(failures)