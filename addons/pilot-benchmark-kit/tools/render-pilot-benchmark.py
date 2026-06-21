#!/usr/bin/env python3
"""Render pilot benchmark JSON exports as Markdown, HTML, and SVG views."""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import sys
from dataclasses import dataclass
from typing import Any


DEFAULT_BENCHMARK = "benchmarks/results/latest.json"
DEFAULT_RETRIEVAL = "agent-memory/exports/retrieval-eval/retrieval-eval.json"
DEFAULT_FINALIZATION = "agent-memory/exports/finalization-gates/quality-ratchet-summary.json"
DEFAULT_FINALIZATION_ALT = "agent-memory/exports/finalization-gates/latest.json"
DEFAULT_OUT_DIR = "agent-memory/reports/pilot-benchmark"


@dataclass(frozen=True)
class JsonInput:
    label: str
    path: pathlib.Path
    payload: dict[str, Any] | None
    missing: bool


def load_json(label: str, path: pathlib.Path, strict: bool) -> JsonInput:
    if not path.exists():
        if strict:
            raise FileNotFoundError(f"{label} input not found: {path}")
        return JsonInput(label=label, path=path, payload=None, missing=True)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{label} input must contain a JSON object: {path}")
    return JsonInput(label=label, path=path, payload=payload, missing=False)


def rel_path(path: pathlib.Path, root: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def number(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    return default


def pct_metric(value: Any) -> float:
    metric = number(value)
    if 0 <= metric <= 1:
        return metric * 100
    return metric


def fmt(value: Any, digits: int = 2) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        text = f"{value:.{digits}f}"
        return text.rstrip("0").rstrip(".")
    if value is None:
        return "n/a"
    return str(value)


def status_text(value: Any) -> str:
    if value is True:
        return "passed"
    if value is False:
        return "failed"
    return "unknown"


def score_rows(retrieval: dict[str, Any] | None, finalization: dict[str, Any] | None) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    if retrieval:
        metrics = retrieval.get("metrics", {})
        if isinstance(metrics, dict):
            candidates = [
                ("Retrieval overall", metrics.get("overall_score")),
                ("Precision", metrics.get("precision_score", metrics.get("avg_precision_at_k"))),
                ("Recall", metrics.get("avg_recall_at_k")),
                ("nDCG", metrics.get("avg_ndcg_at_k")),
                ("Safety", metrics.get("safety_score")),
                ("Parallel", metrics.get("parallel_score")),
            ]
            for label, value in candidates:
                if value is not None:
                    rows.append((label, max(0.0, min(100.0, pct_metric(value)))))
    if finalization:
        scores = finalization.get("scores") or finalization.get("quality_ratchet_scores") or {}
        if isinstance(scores, dict):
            for key in sorted(scores):
                rows.append((f"Gate {key}", max(0.0, min(100.0, pct_metric(scores[key])))))
    return rows


def time_rows(benchmark: dict[str, Any] | None, finalization: dict[str, Any] | None) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    if benchmark:
        scenarios = benchmark.get("scenarios", [])
        if isinstance(scenarios, list):
            for item in scenarios:
                if isinstance(item, dict):
                    rows.append((f"Benchmark {item.get('name', 'scenario')}", number(item.get("seconds"))))
    if finalization:
        gates = finalization.get("gates", [])
        if isinstance(gates, list):
            for item in gates:
                if isinstance(item, dict):
                    rows.append((f"Gate {item.get('name', 'gate')}", number(item.get("seconds"))))
    return rows


def render_bar_group(
    title: str,
    rows: list[tuple[str, float]],
    *,
    y_start: int,
    width: int,
    max_value: float,
    suffix: str,
    color: str,
) -> tuple[str, int]:
    if not rows:
        return "", y_start
    label_x = 28
    chart_x = 240
    chart_width = width - chart_x - 96
    y = y_start
    parts = [
        f'<text x="{label_x}" y="{y}" class="section">{html.escape(title)}</text>'
    ]
    y += 26
    for label, value in rows:
        bar_width = 0 if max_value <= 0 else int((value / max_value) * chart_width)
        safe_label = html.escape(label[:44])
        safe_value = html.escape(fmt(value))
        parts.extend(
            [
                f'<text x="{label_x}" y="{y + 15}" class="label">{safe_label}</text>',
                f'<rect x="{chart_x}" y="{y}" width="{chart_width}" height="18" rx="3" class="track"/>',
                f'<rect x="{chart_x}" y="{y}" width="{bar_width}" height="18" rx="3" fill="{color}"/>',
                f'<text x="{chart_x + chart_width + 12}" y="{y + 15}" class="value">{safe_value}{suffix}</text>',
            ]
        )
        y += 31
    return "\n".join(parts), y + 16


def render_svg(scores: list[tuple[str, float]], times: list[tuple[str, float]]) -> str:
    width = 960
    score_rows_limited = scores[:12]
    time_rows_limited = times[:14]
    height = 120 + (len(score_rows_limited) * 31) + (len(time_rows_limited) * 31)
    if score_rows_limited and time_rows_limited:
        height += 54
    max_seconds = max([value for _, value in time_rows_limited] + [1.0])
    score_svg, y = render_bar_group(
        "Score View",
        score_rows_limited,
        y_start=82,
        width=width,
        max_value=100,
        suffix="",
        color="#2563eb",
    )
    time_svg, y = render_bar_group(
        "Runtime View",
        time_rows_limited,
        y_start=y,
        width=width,
        max_value=max_seconds,
        suffix="s",
        color="#0f766e",
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Pilot benchmark chart">
  <style>
    .bg {{ fill: #f8fafc; }}
    .title {{ fill: #0f172a; font: 700 24px Arial, sans-serif; }}
    .subtitle {{ fill: #475569; font: 13px Arial, sans-serif; }}
    .section {{ fill: #111827; font: 700 16px Arial, sans-serif; }}
    .label {{ fill: #334155; font: 12px Arial, sans-serif; }}
    .value {{ fill: #0f172a; font: 700 12px Arial, sans-serif; }}
    .track {{ fill: #e2e8f0; }}
  </style>
  <rect width="100%" height="100%" class="bg"/>
  <text x="28" y="38" class="title">Pilot Benchmark Proof View</text>
  <text x="28" y="60" class="subtitle">Generated chart view only. Canonical memory remains the reviewed Markdown and source JSON exports.</text>
  {score_svg}
  {time_svg}
</svg>
"""


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return lines


def render_markdown(inputs: list[JsonInput], scores: list[tuple[str, float]], times: list[tuple[str, float]]) -> str:
    by_label = {item.label: item.payload for item in inputs}
    benchmark = by_label.get("benchmark")
    retrieval = by_label.get("retrieval")
    finalization = by_label.get("finalization")
    lines = [
        "# Pilot Benchmark Report",
        "",
        "> Generated view only. This report is not canonical memory.",
        "",
        "## Inputs",
        "",
    ]
    lines.extend(
        markdown_table(
            ["Input", "Path", "Status"],
            [[item.label, f"`{item.path.as_posix()}`", "missing" if item.missing else "loaded"] for item in inputs],
        )
    )
    lines.extend(["", "## Summary", ""])
    summary_rows: list[list[Any]] = []
    if benchmark:
        summary_rows.append(["Benchmark scenarios", len(benchmark.get("scenarios", []))])
        summary_rows.append(["Benchmark generated", benchmark.get("generated_at", "n/a")])
    if retrieval:
        metrics = retrieval.get("metrics", {})
        summary_rows.append(["Retrieval status", status_text(retrieval.get("passed"))])
        if isinstance(metrics, dict):
            summary_rows.append(["Retrieval overall score", fmt(metrics.get("overall_score"))])
            summary_rows.append(["Retrieval p95 latency", f"{fmt(metrics.get('p95_query_latency_ms'))} ms"])
            summary_rows.append(["Unsafe shared docs", fmt(metrics.get("unsafe_shared_docs"))])
    if finalization:
        summary_rows.append(["Finalization status", status_text(finalization.get("passed"))])
        summary_rows.append(["Finalization failed gates", fmt(finalization.get("failed"))])
    if summary_rows:
        lines.extend(markdown_table(["Metric", "Value"], summary_rows))
    else:
        lines.append("No inputs were loaded.")

    if scores:
        lines.extend(["", "## Score Bars", ""])
        lines.extend(markdown_table(["Label", "Score"], [[label, fmt(value)] for label, value in scores]))
    if times:
        lines.extend(["", "## Runtime Bars", ""])
        lines.extend(markdown_table(["Label", "Seconds"], [[label, fmt(value, 3)] for label, value in times]))

    if retrieval and isinstance(retrieval.get("queries"), list):
        lines.extend(["", "## Retrieval Queries", ""])
        query_rows = []
        for query in retrieval["queries"]:
            if isinstance(query, dict):
                query_rows.append(
                    [
                        query.get("name", "query"),
                        fmt(query.get("precision_at_k")),
                        fmt(query.get("recall_at_k")),
                        fmt(query.get("mrr")),
                        f"{fmt(query.get('latency_ms'))} ms",
                    ]
                )
        if query_rows:
            lines.extend(markdown_table(["Query", "Precision", "Recall", "MRR", "Latency"], query_rows))

    lines.extend(["", "## Chart", "", "See `pilot-benchmark.svg` and `pilot-benchmark.html` in this directory."])
    return "\n".join(lines).rstrip() + "\n"


def html_table(headers: list[str], rows: list[list[Any]]) -> str:
    head = "".join(f"<th>{html.escape(str(header))}</th>" for header in headers)
    body_rows = []
    for row in rows:
        body_rows.append("<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def render_html(markdown_summary: str, svg: str, scores: list[tuple[str, float]], times: list[tuple[str, float]]) -> str:
    score_table = html_table(["Label", "Score"], [[label, fmt(value)] for label, value in scores]) if scores else "<p>No score rows.</p>"
    time_table = html_table(["Label", "Seconds"], [[label, fmt(value, 3)] for label, value in times]) if times else "<p>No runtime rows.</p>"
    summary_excerpt = "\n".join(markdown_summary.splitlines()[:24])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pilot Benchmark Report</title>
  <style>
    :root {{ color-scheme: light; font-family: Arial, sans-serif; }}
    body {{ margin: 0; background: #f8fafc; color: #0f172a; }}
    main {{ max-width: 1060px; margin: 0 auto; padding: 32px 20px 48px; }}
    h1 {{ margin: 0 0 8px; font-size: 32px; }}
    h2 {{ margin-top: 28px; }}
    .note {{ color: #475569; margin-bottom: 24px; }}
    .chart {{ overflow-x: auto; border: 1px solid #cbd5e1; background: white; }}
    table {{ width: 100%; border-collapse: collapse; background: white; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; font-size: 14px; }}
    th {{ background: #e2e8f0; }}
    pre {{ white-space: pre-wrap; background: #0f172a; color: #e2e8f0; padding: 16px; overflow-x: auto; }}
  </style>
</head>
<body>
  <main>
    <h1>Pilot Benchmark Report</h1>
    <p class="note">Generated view only. Canonical memory remains reviewed Markdown and source JSON exports.</p>
    <section class="chart">{svg}</section>
    <h2>Scores</h2>
    {score_table}
    <h2>Runtimes</h2>
    {time_table}
    <h2>Markdown Summary Excerpt</h2>
    <pre>{html.escape(summary_excerpt)}</pre>
  </main>
</body>
</html>
"""


def choose_finalization_path(root: pathlib.Path, explicit: str | None) -> pathlib.Path:
    if explicit:
        return root / explicit
    primary = root / DEFAULT_FINALIZATION
    if primary.exists():
        return primary
    return root / DEFAULT_FINALIZATION_ALT


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Owledge pilot benchmark proof views.")
    parser.add_argument("--project-root", default=".", help="Project root containing Owledge outputs.")
    parser.add_argument("--benchmark", default=DEFAULT_BENCHMARK, help="Benchmark JSON path, relative to project root unless absolute.")
    parser.add_argument("--retrieval", default=DEFAULT_RETRIEVAL, help="Retrieval eval JSON path, relative to project root unless absolute.")
    parser.add_argument("--finalization", default=None, help="Finalization or quality-ratchet JSON path, relative to project root unless absolute.")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Output directory, relative to project root unless absolute.")
    parser.add_argument("--strict", action="store_true", help="Fail when an input path is missing.")
    args = parser.parse_args()

    root = pathlib.Path(args.project_root).resolve()

    def resolve_path(value: str) -> pathlib.Path:
        path = pathlib.Path(value)
        return path if path.is_absolute() else root / path

    benchmark_path = resolve_path(args.benchmark)
    retrieval_path = resolve_path(args.retrieval)
    finalization_path = choose_finalization_path(root, args.finalization)
    out_dir = resolve_path(args.out_dir)

    inputs = [
        load_json("benchmark", benchmark_path, args.strict),
        load_json("retrieval", retrieval_path, args.strict),
        load_json("finalization", finalization_path, args.strict),
    ]
    benchmark = inputs[0].payload
    retrieval = inputs[1].payload
    finalization = inputs[2].payload
    if args.strict and not any(item.payload for item in inputs):
        raise FileNotFoundError("No pilot benchmark inputs were loaded.")

    scores = score_rows(retrieval, finalization)
    times = time_rows(benchmark, finalization)
    svg = render_svg(scores, times)
    markdown = render_markdown(inputs, scores, times)
    html_doc = render_html(markdown, svg, scores, times)

    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "pilot-benchmark.md"
    html_path = out_dir / "pilot-benchmark.html"
    svg_path = out_dir / "pilot-benchmark.svg"
    markdown_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(html_doc, encoding="utf-8")
    svg_path.write_text(svg, encoding="utf-8")

    result = {
        "loaded": [item.label for item in inputs if item.payload is not None],
        "missing": [item.label for item in inputs if item.missing],
        "outputs": [rel_path(markdown_path, root), rel_path(html_path, root), rel_path(svg_path, root)],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
