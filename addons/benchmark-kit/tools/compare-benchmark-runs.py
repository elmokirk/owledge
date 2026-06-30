#!/usr/bin/env python3
"""Compare completed Owledge Benchmark Kit runs without running models."""

from __future__ import annotations

import argparse
import html
import json
import pathlib
from typing import Any


PROFILES = ("metadata_scan", "owledge_context_pack", "oracle")
API_PRICE_CATALOG = [
    {"provider": "Anthropic", "model": "Claude Opus 4.8", "input_per_mtok": 5.00, "output_per_mtok": 25.00},
    {"provider": "Anthropic", "model": "Claude Sonnet 4.6", "input_per_mtok": 3.00, "output_per_mtok": 15.00},
    {"provider": "Anthropic", "model": "Claude Haiku 4.5", "input_per_mtok": 1.00, "output_per_mtok": 5.00},
    {"provider": "Google", "model": "Gemini 3 Pro", "input_per_mtok": 2.00, "output_per_mtok": 12.00},
    {"provider": "Google", "model": "Gemini 2.5 Pro", "input_per_mtok": 1.25, "output_per_mtok": 10.00},
    {"provider": "Google", "model": "Gemini 2.5 Flash", "input_per_mtok": 0.30, "output_per_mtok": 2.50},
    {"provider": "OpenAI", "model": "gpt-5.5", "input_per_mtok": 5.00, "output_per_mtok": 30.00},
    {"provider": "OpenAI", "model": "gpt-5.5-pro", "input_per_mtok": 30.00, "output_per_mtok": 180.00},
    {"provider": "OpenAI", "model": "gpt-5.4", "input_per_mtok": 2.50, "output_per_mtok": 15.00},
]
PRICE_SOURCE_NOTE = (
    "Illustrative API prices per 1M tokens. Verify current provider pricing before using these numbers for budgets. "
    "Sources checked: Anthropic Claude pricing (docs.anthropic.com/en/docs/about-claude/pricing), "
    "Google Gemini API pricing (ai.google.dev/gemini-api/docs/pricing), "
    "and OpenAI API pricing (platform.openai.com/docs/pricing)."
)


def pct_reduction(before: float, after: float) -> float:
    if before <= 0:
        return 0.0
    return round(((before - after) / before) * 100, 2)


def scenario_status(item: dict[str, Any]) -> str:
    if int(item.get("privacy_failure_count") or 0) > 0:
        return "fail"
    if float(item.get("answer_correctness") or 0) < 0.5:
        return "fail"
    if int(item.get("staleness_failure_count") or 0) > 0 or float(item.get("irrelevant_token_ratio") or 0) > 0.40:
        return "warn"
    return "pass"


def unique_label(base: str, used: set[str]) -> str:
    label = base
    index = 2
    while label in used:
        label = f"{base} #{index}"
        index += 1
    used.add(label)
    return label


def share_path(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def load_reports(inputs: list[str], root: pathlib.Path) -> tuple[list[dict[str, Any]], list[str]]:
    reports: list[dict[str, Any]] = []
    skipped: list[str] = []
    used: set[str] = set()
    for raw in inputs:
        path = pathlib.Path(raw)
        if not path.is_absolute():
            path = root / path
        if not path.exists():
            skipped.append(raw)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        model = str((data.get("models") or [path.parent.name])[0])
        data["_comparison_label"] = unique_label(model, used)
        data["_input"] = share_path(root, path)
        reports.append(data)
    return reports, skipped


def profile(report: dict[str, Any], name: str) -> dict[str, Any]:
    profiles = report.get("profile_totals") or {}
    return profiles.get(name) or {}


def verdict(report: dict[str, Any], name: str) -> str:
    verdicts = report.get("verdicts") or {}
    return str((verdicts.get(name) or {}).get("verdict") or "unknown")


def pass_rate(report: dict[str, Any], profile_name: str) -> float:
    records = [item for item in report.get("records", []) if item.get("profile") == profile_name]
    if not records:
        return 0.0
    passed = sum(1 for item in records if scenario_status(item) == "pass")
    return round(passed / len(records), 4)


def handoff_score(report: dict[str, Any], profile_name: str) -> float:
    records = [
        item
        for item in report.get("records", [])
        if item.get("profile") == profile_name and item.get("scenario") == "handoff-resume"
    ]
    if not records:
        return 0.0
    return round(sum(float(item.get("handoff_resume_score") or 0) for item in records) / len(records), 4)


def scenario_heatmap(report: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    records = report.get("records", [])
    for item in records:
        scenario = str(item.get("scenario") or "")
        if not scenario or scenario in seen:
            continue
        seen.add(scenario)
        baseline = next((r for r in records if r.get("scenario") == scenario and r.get("profile") == "metadata_scan"), {})
        owledge = next((r for r in records if r.get("scenario") == scenario and r.get("profile") == "owledge_context_pack"), {})
        rows.append(
            {
                "scenario": scenario,
                "baseline_status": scenario_status(baseline) if baseline else "missing",
                "owledge_status": scenario_status(owledge) if owledge else "missing",
            }
        )
    return rows


def comparison_row(report: dict[str, Any]) -> dict[str, Any]:
    baseline = profile(report, "metadata_scan")
    owledge = profile(report, "owledge_context_pack")
    oracle = profile(report, "oracle")
    privacy_prevented = max(0, int(baseline.get("privacy_failures") or 0) - int(owledge.get("privacy_failures") or 0))
    stale_prevented = max(0, int(baseline.get("staleness_failures") or 0) - int(owledge.get("staleness_failures") or 0))
    release_status = "pass" if verdict(report, "owledge") == "pass" else "warn" if verdict(report, "owledge") == "warn" else "fail"
    return {
        "model": report["_comparison_label"],
        "mode": report.get("mode", ""),
        "scale_mode": report.get("scale_mode", ""),
        "file_count": int(report.get("file_count") or 0),
        "baseline_verdict": verdict(report, "baseline"),
        "owledge_verdict": verdict(report, "owledge"),
        "oracle_verdict": verdict(report, "oracle"),
        "release_proof_status": release_status,
        "baseline_pollution": float(baseline.get("avg_irrelevant_token_ratio") or 0),
        "owledge_pollution": float(owledge.get("avg_irrelevant_token_ratio") or 0),
        "oracle_pollution": float(oracle.get("avg_irrelevant_token_ratio") or 0),
        "pollution_reduction_percent": pct_reduction(
            float(baseline.get("avg_irrelevant_token_ratio") or 0),
            float(owledge.get("avg_irrelevant_token_ratio") or 0),
        ),
        "baseline_tokens_per_correct_answer": float(baseline.get("tokens_per_correct_answer") or 0),
        "owledge_tokens_per_correct_answer": float(owledge.get("tokens_per_correct_answer") or 0),
        "oracle_tokens_per_correct_answer": float(oracle.get("tokens_per_correct_answer") or 0),
        "token_reduction_percent": pct_reduction(
            float(baseline.get("tokens_per_correct_answer") or 0),
            float(owledge.get("tokens_per_correct_answer") or 0),
        ),
        "baseline_total_tokens": int(baseline.get("total_tokens") or 0),
        "owledge_total_tokens": int(owledge.get("total_tokens") or 0),
        "baseline_prompt_tokens": int(baseline.get("prompt_tokens") or 0),
        "owledge_prompt_tokens": int(owledge.get("prompt_tokens") or 0),
        "baseline_completion_tokens": int(baseline.get("completion_tokens") or 0),
        "owledge_completion_tokens": int(owledge.get("completion_tokens") or 0),
        "total_token_reduction_percent": pct_reduction(
            float(baseline.get("total_tokens") or 0),
            float(owledge.get("total_tokens") or 0),
        ),
        "privacy_failures_prevented": privacy_prevented,
        "stale_failures_prevented": stale_prevented,
        "owledge_scenario_pass_rate": pass_rate(report, "owledge_context_pack"),
        "baseline_scenario_pass_rate": pass_rate(report, "metadata_scan"),
        "owledge_handoff_resume_score": handoff_score(report, "owledge_context_pack"),
        "owledge_tokens_per_second": float(owledge.get("avg_tokens_per_second") or 0),
        "heatmap": scenario_heatmap(report),
    }


def cost_for_tokens(input_tokens: int, output_tokens: int, price: dict[str, Any]) -> float:
    return round(
        (input_tokens / 1_000_000) * float(price["input_per_mtok"])
        + (output_tokens / 1_000_000) * float(price["output_per_mtok"]),
        6,
    )


def cost_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    baseline_prompt = sum(int(row["baseline_prompt_tokens"]) for row in rows)
    baseline_completion = sum(int(row["baseline_completion_tokens"]) for row in rows)
    owledge_prompt = sum(int(row["owledge_prompt_tokens"]) for row in rows)
    owledge_completion = sum(int(row["owledge_completion_tokens"]) for row in rows)
    items: list[dict[str, Any]] = []
    for price in API_PRICE_CATALOG:
        baseline_cost = cost_for_tokens(baseline_prompt, baseline_completion, price)
        owledge_cost = cost_for_tokens(owledge_prompt, owledge_completion, price)
        items.append(
            {
                "provider": price["provider"],
                "model": price["model"],
                "input_per_mtok": price["input_per_mtok"],
                "output_per_mtok": price["output_per_mtok"],
                "baseline_cost_usd": baseline_cost,
                "owledge_cost_usd": owledge_cost,
                "estimated_savings_usd": round(baseline_cost - owledge_cost, 6),
                "estimated_savings_percent": pct_reduction(baseline_cost, owledge_cost),
            }
        )
    return items


def executive(rows: list[dict[str, Any]], skipped: list[str]) -> dict[str, Any]:
    avg_pollution = round(sum(row["pollution_reduction_percent"] for row in rows) / len(rows), 2)
    avg_tokens = round(sum(row["token_reduction_percent"] for row in rows) / len(rows), 2)
    privacy = sum(int(row["privacy_failures_prevented"]) for row in rows)
    stale = sum(int(row["stale_failures_prevented"]) for row in rows)
    passed = sum(1 for row in rows if row["release_proof_status"] == "pass")
    status = "pass" if passed == len(rows) else "warn" if passed else "fail"
    return {
        "release_proof_status": status,
        "models_compared": len(rows),
        "models_passed": passed,
        "avg_pollution_reduction_percent": avg_pollution,
        "avg_token_reduction_percent": avg_tokens,
        "privacy_failures_prevented": privacy,
        "stale_failures_prevented": stale,
        "skipped_inputs": skipped,
        "summary": (
            f"Owledge compared {len(rows)} completed benchmark runs: {passed}/{len(rows)} Owledge profiles passed, "
            f"privacy failures prevented={privacy}, stale failures prevented={stale}, "
            f"average pollution reduction={avg_pollution}%, average tokens/correct reduction={avg_tokens}%."
        ),
    }


def render_svg(rows: list[dict[str, Any]]) -> str:
    metrics = [
        ("Pollution reduction %", "pollution_reduction_percent"),
        ("Token reduction %", "token_reduction_percent"),
        ("Owledge tokens/sec", "owledge_tokens_per_second"),
        ("Privacy prevented", "privacy_failures_prevented"),
        ("Stale prevented", "stale_failures_prevented"),
    ]
    width = 1120
    row_height = 34
    height = 92 + len(rows) * len(metrics) * row_height
    max_value = max([1.0] + [float(row[key]) for row in rows for _, key in metrics])
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Inter,Segoe UI,Arial,sans-serif}.title{font-size:22px;font-weight:700}.label{font-size:12px;fill:#475569}.value{font-size:12px;fill:#0f172a}.track{fill:#e2e8f0}.bar{fill:#2563eb}</style>",
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<text x="24" y="38" class="title">Before vs Owledge Comparison</text>',
        '<text x="24" y="62" class="label">Higher reduction/prevention is better. tokens/sec is shown in the model matrix.</text>',
    ]
    y = 86
    for row in rows:
        for label, key in metrics:
            value = float(row[key])
            bar_width = int((value / max_value) * 560)
            parts.extend(
                [
                    f'<text x="24" y="{y + 14}" class="label">{html.escape(str(row["model"]))} - {html.escape(label)}</text>',
                    f'<rect x="320" y="{y}" width="560" height="18" rx="4" class="track"/>',
                    f'<rect x="320" y="{y}" width="{bar_width}" height="18" rx="4" class="bar"/>',
                    f'<text x="896" y="{y + 14}" class="value">{value}</text>',
                ]
            )
            y += row_height
    parts.append("</svg>")
    return "\n".join(parts)


def render_markdown(payload: dict[str, Any]) -> str:
    rows = payload["models"]
    costs = payload["api_cost_estimates"]
    lines = [
        "# Owledge Benchmark Comparison Report",
        "",
        "## Executive Verdict",
        "",
        f"- Release proof status: `{payload['executive']['release_proof_status']}`",
        f"- {payload['executive']['summary']}",
        "",
        "## Creator Pull Quote",
        "",
        "> Owledge makes the context safer and cheaper before the model sees it.",
        "",
        "## Model Matrix",
        "",
        "| Model | Baseline | Owledge | Pollution reduction | Privacy prevented | Stale prevented | Token reduction | Pass rate | tokens/sec |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} | {row['baseline_verdict']} | {row['owledge_verdict']} | {row['pollution_reduction_percent']}% | {row['privacy_failures_prevented']} | {row['stale_failures_prevented']} | {row['token_reduction_percent']}% | {row['owledge_scenario_pass_rate']} | {row['owledge_tokens_per_second']} |"
        )
    lines.extend(
        [
            "",
            "## Before vs Owledge",
            "",
            "Lower privacy failures, stale failures, context pollution, and tokens per correct answer are better. Higher scenario pass rate, handoff score, and tokens/sec are better.",
            "",
            "## Estimated API Cost Impact",
            "",
            PRICE_SOURCE_NOTE,
            "",
            "| Provider | Model | Input $/1M | Output $/1M | Baseline cost | Owledge cost | Estimated savings | Savings |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in costs:
        lines.append(
            f"| {item['provider']} | {item['model']} | {item['input_per_mtok']} | {item['output_per_mtok']} | ${item['baseline_cost_usd']} | ${item['owledge_cost_usd']} | ${item['estimated_savings_usd']} | {item['estimated_savings_percent']}% |"
        )
    lines.extend(
        [
            "",
            "## Scenario Heatmap",
            "",
            "| Model | Scenario | Baseline | Owledge |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        for item in row["heatmap"]:
            lines.append(f"| {row['model']} | {item['scenario']} | {item['baseline_status']} | {item['owledge_status']} |")
    lines.extend(
        [
            "",
            "## How To Read This Report",
            "",
            "- Baseline shows what happens when retrieval over-selects noisy, stale, or private context.",
            "- Owledge shows the product behavior under test: cleaner selected context before model inference.",
            "- Token reduction estimates cost pressure avoided by cleaner context, not total project ROI.",
            "- tokens/sec is runtime throughput for the tested model and environment, not an Owledge quality score.",
            "- Oracle is the ground-truth reference ceiling from the fixture generator.",
            "",
            "## Caveats",
            "",
            "- Inputs are completed Benchmark Kit reports; this command does not run models.",
            "- Oracle is ground-truth reference, not a model or product claim.",
            "- API prices are illustrative snapshots and must be verified against provider pricing before budgeting.",
            "- Small scale is release proof for v0.7.0; larger scales and own-vault benchmarking are roadmap items.",
        ]
    )
    if payload["executive"].get("skipped_inputs"):
        lines.extend(["", "## Skipped Inputs", ""])
        for item in payload["executive"]["skipped_inputs"]:
            lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"


def pill(status: str) -> str:
    safe = html.escape(status)
    return f'<span class="pill {safe}">{safe.title()}</span>'


def render_html(payload: dict[str, Any], svg: str) -> str:
    rows = payload["models"]
    costs = payload["api_cost_estimates"]
    matrix = []
    for row in rows:
        matrix.append(
            "<tr>"
            f"<td>{html.escape(row['model'])}</td>"
            f"<td>{pill(row['baseline_verdict'])}</td>"
            f"<td>{pill(row['owledge_verdict'])}</td>"
            f"<td>{row['pollution_reduction_percent']}%</td>"
            f"<td>{row['privacy_failures_prevented']}</td>"
            f"<td>{row['stale_failures_prevented']}</td>"
            f"<td>{row['token_reduction_percent']}%</td>"
            f"<td>{row['owledge_scenario_pass_rate']}</td>"
            f"<td>{row['owledge_tokens_per_second']}</td>"
            "</tr>"
        )
    heatmap = []
    for row in rows:
        for item in row["heatmap"]:
            heatmap.append(
                "<tr>"
                f"<td>{html.escape(row['model'])}</td>"
                f"<td>{html.escape(item['scenario'])}</td>"
                f"<td>{pill(item['baseline_status'])}</td>"
                f"<td>{pill(item['owledge_status'])}</td>"
                "</tr>"
            )
    cost_table = []
    for item in costs:
        cost_table.append(
            "<tr>"
            f"<td>{html.escape(item['provider'])}</td>"
            f"<td>{html.escape(item['model'])}</td>"
            f"<td>${item['input_per_mtok']}</td>"
            f"<td>${item['output_per_mtok']}</td>"
            f"<td>${item['baseline_cost_usd']}</td>"
            f"<td>${item['owledge_cost_usd']}</td>"
            f"<td>${item['estimated_savings_usd']}</td>"
            f"<td>{item['estimated_savings_percent']}%</td>"
            "</tr>"
        )
    skipped = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in payload["executive"].get("skipped_inputs", []))
    skipped_section = f"<h2>Skipped Inputs</h2><ul>{skipped}</ul>" if skipped else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Owledge Benchmark Comparison Report</title>
  <style>
    body {{ font-family: Inter, Segoe UI, Arial, sans-serif; margin: 32px; color: #172033; background: #f8fafc; }}
    h1, h2 {{ color: #0f172a; }}
    .card {{ background: white; border: 1px solid #d8dee9; border-radius: 8px; padding: 16px; margin: 12px 0; }}
    .verdict {{ border-left: 6px solid #16a34a; }}
    .quote {{ font-size: 24px; font-weight: 800; line-height: 1.25; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; }}
    .value {{ font-size: 24px; font-weight: 800; }}
    .label {{ color: #64748b; font-size: 13px; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 2px 8px; font-size: 12px; font-weight: 700; }}
    .pill.pass {{ color: #166534; background: #dcfce7; }}
    .pill.warn {{ color: #92400e; background: #fef3c7; }}
    .pill.fail {{ color: #991b1b; background: #fee2e2; }}
    .pill.missing, .pill.unknown {{ color: #475569; background: #e2e8f0; }}
    table {{ width: 100%; border-collapse: collapse; background: white; margin-top: 12px; }}
    th, td {{ border-bottom: 1px solid #e2e8f0; padding: 8px; text-align: left; font-size: 14px; }}
    th {{ color: #475569; background: #f1f5f9; }}
    code {{ background: #e2e8f0; padding: 2px 4px; border-radius: 4px; }}
    .charts {{ background: white; border: 1px solid #d8dee9; border-radius: 8px; padding: 16px; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>Owledge Benchmark Comparison Report</h1>
  <section class="card verdict">
    <div class="label">Executive Verdict</div>
    <div class="value">{html.escape(payload['executive']['release_proof_status'].title())}</div>
    <p>{html.escape(payload['executive']['summary'])}</p>
  </section>
  <section class="card">
    <div class="label">Creator Pull Quote</div>
    <div class="quote">Owledge makes the context safer and cheaper before the model sees it.</div>
  </section>
  <div class="grid">
    <div class="card"><div class="label">Models compared</div><div class="value">{payload['executive']['models_compared']}</div></div>
    <div class="card"><div class="label">Privacy failures prevented</div><div class="value">{payload['executive']['privacy_failures_prevented']}</div></div>
    <div class="card"><div class="label">Stale failures prevented</div><div class="value">{payload['executive']['stale_failures_prevented']}</div></div>
    <div class="card"><div class="label">Avg pollution reduction</div><div class="value">{payload['executive']['avg_pollution_reduction_percent']}%</div></div>
    <div class="card"><div class="label">Avg tokens/correct reduction</div><div class="value">{payload['executive']['avg_token_reduction_percent']}%</div></div>
  </div>
  <h2>Model Matrix</h2>
  <table>
    <thead><tr><th>Model</th><th>Baseline</th><th>Owledge</th><th>Pollution reduction</th><th>Privacy prevented</th><th>Stale prevented</th><th>Token reduction</th><th>Pass rate</th><th>tokens/sec</th></tr></thead>
    <tbody>{''.join(matrix)}</tbody>
  </table>
  <h2>Before vs Owledge Charts</h2>
  <p>Lower privacy failures, stale failures, <strong>Context pollution</strong>, and <strong>Tokens per correct answer</strong> are better. Higher reduction/prevention is better in these charts.</p>
  <div class="charts">{svg}</div>
  <h2>Estimated API Cost Impact</h2>
  <p>{html.escape(PRICE_SOURCE_NOTE)}</p>
  <p>This table applies provider API prices to the measured baseline and Owledge token counts. It estimates cost pressure avoided by cleaner context; it is not a full project ROI calculation.</p>
  <table>
    <thead><tr><th>Provider</th><th>Model</th><th>Input $/1M</th><th>Output $/1M</th><th>Baseline cost</th><th>Owledge cost</th><th>Estimated savings</th><th>Savings</th></tr></thead>
    <tbody>{''.join(cost_table)}</tbody>
  </table>
  <h2>Scenario Heatmap</h2>
  <table>
    <thead><tr><th>Model</th><th>Scenario</th><th>Baseline</th><th>Owledge</th></tr></thead>
    <tbody>{''.join(heatmap)}</tbody>
  </table>
  <h2>How To Read This Report</h2>
  <table>
    <tbody>
      <tr><th>Baseline</th><td>Shows what happens when retrieval over-selects noisy, stale, or private context.</td></tr>
      <tr><th>Owledge</th><td>Shows the product behavior under test: cleaner selected context before model inference.</td></tr>
      <tr><th>Token reduction</th><td>Estimates cost pressure avoided by cleaner context, not total project ROI.</td></tr>
      <tr><th>tokens/sec</th><td>Runtime throughput for the tested model and environment, not an Owledge quality score.</td></tr>
      <tr><th>Oracle</th><td>Ground-truth reference ceiling from the fixture generator.</td></tr>
    </tbody>
  </table>
  <h2>Caveats</h2>
  <p>Inputs are completed Benchmark Kit reports; this command does not run models. Oracle is ground-truth reference, not a model or product claim. API prices are illustrative snapshots and must be verified against provider pricing before budgeting. Small scale is release proof for v0.7.0.</p>
  {skipped_section}
</body>
</html>
"""


def write_outputs(root: pathlib.Path, payload: dict[str, Any], output: pathlib.Path) -> dict[str, str]:
    report_dir = output if output.is_absolute() else root / output
    export_dir = root / ".owledge" / "exports" / "benchmark-kit-comparison"
    report_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)
    svg = render_svg(payload["models"])
    latest_json = export_dir / "latest.json"
    latest_md = export_dir / "latest.md"
    index_html = report_dir / "index.html"
    charts_svg = report_dir / "charts.svg"
    latest_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    latest_md.write_text(render_markdown(payload), encoding="utf-8")
    charts_svg.write_text(svg, encoding="utf-8")
    index_html.write_text(render_html(payload, svg), encoding="utf-8")
    return {
        "latest_json": latest_json.relative_to(root).as_posix(),
        "latest_md": latest_md.relative_to(root).as_posix(),
        "html": index_html.relative_to(root).as_posix(),
        "svg": charts_svg.relative_to(root).as_posix(),
    }


def compare(root: pathlib.Path, inputs: list[str], output: str) -> dict[str, Any]:
    reports, skipped = load_reports(inputs, root)
    if len(reports) < 2:
        return {"passed": False, "error": "At least two existing benchmark report JSON files are required.", "skipped_inputs": skipped}
    rows = [comparison_row(report) for report in reports]
    payload = {
        "passed": True,
        "report_type": "benchmark-kit-comparison",
        "inputs": [report["_input"] for report in reports],
        "executive": executive(rows, skipped),
        "models": rows,
        "api_price_source_note": PRICE_SOURCE_NOTE,
        "api_cost_estimates": cost_rows(rows),
    }
    payload["paths"] = write_outputs(root, payload, pathlib.Path(output))
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare completed Owledge Benchmark Kit reports.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", default=".owledge/reports/generated/benchmark-kit-comparison")
    args = parser.parse_args(argv)
    root = pathlib.Path(args.project_root).resolve()
    result = compare(root, args.inputs, args.output)
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
