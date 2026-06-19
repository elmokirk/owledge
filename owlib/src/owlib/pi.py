from __future__ import annotations

import pathlib
from typing import Any

from . import core


def pi_report(library_root: pathlib.Path) -> dict[str, Any]:
    records = core.load_index_records(library_root)
    parallels = core.find_parallel_candidates(library_root)
    growth = core.growth_scan(library_root)
    report_dir = library_root / "reports" / "pi-agent"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"pi-report-{core.slugify(core.utc_now())}.md"
    lines = [
        "---",
        f'generated_at: "{core.utc_now()}"',
        'status: "candidate"',
        'review_status: "unreviewed"',
        'semantic_title: "Owlib PI Agent Report"',
        "---",
        "",
        "# Owlib PI Agent Report",
        "",
        "## Executive Summary",
        "",
        f"- Imported records: {len(records)}",
        f"- Parallel candidates: {parallels['candidates']}",
        f"- Growth signals: {len(growth['top_signals'])}",
        f"- Stale records: {len(growth['stale_records'])}",
        "",
        "## Parallel Candidates",
        "",
    ]
    for item in core.read_jsonl(library_root / "parallels" / "parallel-candidates.jsonl")[:10]:
        lines.append(f"- `{item['left']}` <-> `{item['right']}` score={item['score']}")
    lines.extend(["", "## Growth Signals", ""])
    for tag, count in growth["top_signals"][:10]:
        lines.append(f"- `{tag}`: {count}")
    lines.extend(["", "## Recommended Actions", "", "- Curator should review high-score candidates before promotion."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"passed": True, "path": str(path), "records": len(records), "parallel_candidates": parallels["candidates"]}


def recurring_errors(library_root: pathlib.Path) -> dict[str, Any]:
    records = core.load_index_records(library_root)
    counts: dict[str, int] = {}
    for record in records:
        for failure in core.normalize_list(record.get("metadata", {}).get("failure_modes")):
            counts[failure] = counts.get(failure, 0) + 1
    rows = [{"failure_mode": name, "count": count, "status": "recurring-error-candidate"} for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])) if count >= 1]
    core.write_jsonl(library_root / "reports" / "pi-agent" / "recurring-errors.jsonl", rows)
    return {"passed": True, "candidates": len(rows), "path": str(library_root / "reports" / "pi-agent" / "recurring-errors.jsonl")}


def central_project_candidates(library_root: pathlib.Path) -> dict[str, Any]:
    scan = core.growth_scan(library_root)
    rows = []
    for tag, count in scan["top_signals"]:
        if count >= 2:
            rows.append({"title": f"Central capability for {tag}", "signal": tag, "count": count, "status": "central-project-candidate"})
    core.write_jsonl(library_root / "reports" / "pi-agent" / "central-project-candidates.jsonl", rows)
    return {"passed": True, "candidates": len(rows), "path": str(library_root / "reports" / "pi-agent" / "central-project-candidates.jsonl")}


def redteam(library_root: pathlib.Path) -> dict[str, Any]:
    reports = sorted((library_root / "reports" / "pi-agent").glob("pi-report-*.md"))
    latest = reports[-1] if reports else None
    if latest is None:
        report = pi_report(library_root)
        latest = pathlib.Path(report["path"])
    text = latest.read_text(encoding="utf-8")
    score = 95
    if "Parallel Candidates" not in text:
        score -= 15
    if "Recommended Actions" not in text:
        score -= 15
    if "candidate" not in text.lower():
        score -= 20
    verdict = "promotion-candidate" if score >= 95 else "revise"
    path = library_root / "reports" / "pi-agent" / f"pi-redteam-{core.slugify(core.utc_now())}.md"
    path.write_text(
        f"""---
generated_at: "{core.utc_now()}"
status: "candidate"
review_status: "unreviewed"
score: {score}
verdict: "{verdict}"
evaluated_artifact: "{latest}"
---

# PI Agent Red Team

- Score: {score}
- Verdict: {verdict}
- Minimum promotion recommendation score: 95

Findings below 95 require report revision before curator promotion.
""",
        encoding="utf-8",
    )
    return {"passed": score >= 95, "score": score, "verdict": verdict, "path": str(path), "evaluated_artifact": str(latest)}

