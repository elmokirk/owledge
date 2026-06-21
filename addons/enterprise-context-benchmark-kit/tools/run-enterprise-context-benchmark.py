#!/usr/bin/env python3
"""Research-grade synthetic context hygiene benchmark for Owledge."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
import pathlib
import platform
import random
import shutil
import subprocess
import sys
import time
import tracemalloc
from dataclasses import dataclass
from datetime import datetime, timezone


PRICE_PER_1K_INPUT = 0.0025
TOKEN_METHOD = "deterministic-char4-estimate"
ENCODER = None

try:
    import tiktoken  # type: ignore

    ENCODER = tiktoken.get_encoding("cl100k_base")
    TOKEN_METHOD = "tiktoken-cl100k_base"
except Exception:
    ENCODER = None


PROFILE_SIZES = {
    "fresh": [48],
    "small": [240],
    "medium": [960],
    "long_running": [2400],
    "enterprise_default": [48, 240, 960, 2400, 4800],
    "enterprise_full": [48, 240, 960, 2400, 4800, 10000],
    "research_default": [48, 240, 960, 2400],
    "all": [48, 240, 960, 2400, 4800],
}

SCENARIO_NAMES = {
    48: "fresh",
    240: "small",
    960: "medium",
    2400: "long_running",
    4800: "enterprise_default",
    10000: "enterprise_full",
}

QUERY_TERMS = {
    "context",
    "hygiene",
    "token",
    "privacy",
    "evidence",
    "handoff",
    "decision",
    "launch",
    "memory",
    "review",
    "scope",
    "benchmark",
}

STRATEGY_ORDER = [
    "full_vault",
    "naive_paste",
    "keyword_search",
    "metadata_scan",
    "owledge_context_pack",
    "oracle",
]


@dataclass(frozen=True)
class Record:
    record_id: str
    path: pathlib.Path
    doc_type: str
    month: int
    area: str
    status: str
    visibility: str
    data_class: str
    review_status: str
    sanitization_status: str
    stale: bool
    duplicate: bool
    generated: bool
    relevant: bool
    body: str

    @property
    def safe_for_shared(self) -> bool:
        return (
            self.visibility in {"tenant", "customer", "shared"}
            and self.data_class in {"public", "internal"}
            and self.review_status in {"reviewed", "approved"}
            and self.sanitization_status in {"not_required", "approved"}
        )

    @property
    def metadata_line(self) -> str:
        flags = ",".join(
            flag
            for flag, enabled in [
                ("relevant", self.relevant),
                ("stale", self.stale),
                ("duplicate", self.duplicate),
                ("generated", self.generated),
                ("private", self.visibility == "private"),
            ]
            if enabled
        )
        return (
            f"{self.record_id}|{self.path.as_posix()}|{self.doc_type}|month={self.month}|"
            f"area={self.area}|review={self.review_status}|safe={str(self.safe_for_shared).lower()}|flags={flags}"
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    if ENCODER is not None:
        return max(1, len(ENCODER.encode(text)))
    return max(1, (len(text) + 3) // 4)


def git_commit(root: pathlib.Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return "unknown"


def stable_id(seed: int, scenario_size: int, index: int) -> str:
    digest = hashlib.sha1(f"{seed}:{scenario_size}:{index}".encode("utf-8")).hexdigest()[:10]
    return f"sim-{scenario_size:05d}-{index:05d}-{digest}"


def markdown_for(record: Record) -> str:
    title = f"{record.doc_type.title()} {record.record_id}"
    lines = [
        "---",
        f'memory_id: "mem:tenant-sim:customer-sim:enterprise-sim:{record.doc_type}:{record.record_id}"',
        'tenant_id: "tenant-sim"',
        'customer_id: "customer-sim"',
        'project_id: "enterprise-sim"',
        f'doc_type: "{record.doc_type}"',
        f'status: "{record.status}"',
        f'visibility: "{record.visibility}"',
        f'data_class: "{record.data_class}"',
        f'semantic_title: "{title}"',
        f'summary: "Synthetic {record.doc_type} record for context benchmark."',
        "concept_tags:",
        f'  - "{record.area}"',
        '  - "context-hygiene"',
        "stack_tags:",
        '  - "agent-memory"',
        "problem_patterns:",
        '  - "context-loss"',
        "architecture_patterns:",
        '  - "markdown-source-of-truth"',
        "failure_modes:",
        '  - "overfetching"',
        "reusable_lessons:",
        '  - "Use scoped evidence before planning."',
        'confidence: 0.82',
        f'review_status: "{record.review_status}"',
        f'sanitization_status: "{record.sanitization_status}"',
        f'created_at: "2025-{((record.month - 1) % 12) + 1:02d}-01T00:00:00Z"',
        f'updated_at: "2026-{((record.month - 1) % 12) + 1:02d}-15T00:00:00Z"',
        'source_hash: "synthetic"',
        "edges: []",
        "---",
        "",
        f"# {title}",
        "",
        record.body,
        "",
    ]
    return "\n".join(lines)


def write_corpus(base: pathlib.Path, count: int, seed: int) -> list[Record]:
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed + count)
    doc_types = ["plan", "evidence", "review", "adr", "handoff", "research", "task", "lesson", "pattern", "compiled"]
    areas = ["context", "privacy", "runtime", "ui", "billing", "auth", "analytics", "migration", "launch", "compliance"]
    records: list[Record] = []

    for index in range(count):
        doc_type = doc_types[index % len(doc_types)]
        area = areas[(index * 7 + seed) % len(areas)]
        month = 1 + (index % 24)
        stale = index % 17 == 0
        duplicate = index % 29 == 0
        generated = doc_type == "compiled" or index % 23 == 0
        private = index % 13 == 0
        confidential = index % 31 == 0
        reviewed = index % 5 != 0
        sanitized = not confidential or index % 4 != 0
        relevant = (
            area in {"context", "privacy", "runtime", "launch", "compliance"}
            and doc_type in {"plan", "evidence", "review", "adr", "handoff", "lesson", "pattern"}
            and not stale
            and not duplicate
        )
        if index % 43 == 0:
            relevant = True
        record_id = stable_id(seed, count, index)
        visibility = "private" if private else rng.choice(["tenant", "customer", "shared"])
        data_class = "confidential" if confidential else ("personal" if private and index % 2 == 0 else "internal")
        review_status = "reviewed" if reviewed else "unreviewed"
        sanitization_status = "approved" if sanitized else "pending"
        status = "reviewed" if reviewed else "draft"
        relevance_sentence = (
            "This record is directly relevant to the planning objective: token-efficient context hygiene, privacy-safe evidence, launch readiness, and cross-agent handoff continuity."
            if relevant
            else "This record is background project history for a different subsystem and should normally stay outside a scoped planning context."
        )
        body = "\n".join(
            [
                relevance_sentence,
                f"Objective terms: {' '.join(sorted(QUERY_TERMS if relevant else {'legacy', 'background', area, doc_type}))}.",
                f"Project area: {area}. Document kind: {doc_type}. Month in simulated two-year project: {month}.",
                "Evidence trail: design note, implementation review, QA gate, and handoff packet are modeled as durable Markdown records.",
                "Privacy note: shared benchmark strategies must avoid raw private or unsanitized records.",
            ]
        )
        relative = pathlib.Path("agent-memory") / doc_type / f"{record_id}.md"
        record = Record(
            record_id=record_id,
            path=relative,
            doc_type=doc_type,
            month=month,
            area=area,
            status=status,
            visibility=visibility,
            data_class=data_class,
            review_status=review_status,
            sanitization_status=sanitization_status,
            stale=stale,
            duplicate=duplicate,
            generated=generated,
            relevant=relevant,
            body=body,
        )
        target = base / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown_for(record), encoding="utf-8", newline="\n")
        records.append(record)
    return records


def record_text(record: Record, base: pathlib.Path) -> str:
    return (base / record.path).read_text(encoding="utf-8", errors="replace")


def score_record(record: Record) -> tuple[int, int, int, int, int]:
    query_hits = sum(1 for term in QUERY_TERMS if term in record.body.lower() or term in record.area)
    safety = 2 if record.safe_for_shared else -5
    freshness = -3 if record.stale else 2
    duplication = -2 if record.duplicate else 1
    relevance = 8 if record.relevant else 0
    return (relevance + query_hits + safety + freshness + duplication, record.month, -int(record.generated), -int(record.duplicate), -int(record.stale))


def select_records(strategy: str, records: list[Record]) -> tuple[list[Record], dict[str, int]]:
    relevant_safe = [record for record in records if record.relevant and record.safe_for_shared and not record.stale and not record.duplicate]
    oracle = sorted(relevant_safe, key=score_record, reverse=True)[:12]
    if not oracle:
        oracle = sorted([record for record in records if record.relevant], key=score_record, reverse=True)[:12]

    if strategy == "full_vault":
        return list(records), {}
    if strategy == "naive_paste":
        return sorted(records, key=lambda item: (item.month, item.record_id), reverse=True)[:80], {}
    if strategy == "keyword_search":
        scored = sorted(records, key=lambda item: (sum(1 for term in QUERY_TERMS if term in item.body.lower()), item.month), reverse=True)
        return scored[:80], {}
    if strategy == "metadata_scan":
        return list(records), {}
    if strategy == "owledge_context_pack":
        selected: list[Record] = []
        dropped = {"privacy_or_sanitization": 0, "stale_or_duplicate": 0, "low_relevance": 0, "token_budget": 0}
        for record in sorted(records, key=score_record, reverse=True):
            if not record.safe_for_shared:
                dropped["privacy_or_sanitization"] += 1
                continue
            if record.stale or record.duplicate:
                dropped["stale_or_duplicate"] += 1
                continue
            if not record.relevant:
                dropped["low_relevance"] += 1
                continue
            if len(selected) >= 24:
                dropped["token_budget"] += 1
                continue
            selected.append(record)
        return selected, dropped
    if strategy == "oracle":
        return oracle, {}
    raise ValueError(f"Unknown strategy: {strategy}")


def text_for_strategy(strategy: str, selected: list[Record], base: pathlib.Path) -> tuple[str, list[tuple[str, int, bool, bool]]]:
    chunks: list[str] = []
    token_rows: list[tuple[str, int, bool, bool]] = []
    for record in selected:
        text = record.metadata_line if strategy == "metadata_scan" else record_text(record, base)
        tokens = estimate_tokens(text)
        chunks.append(text)
        token_rows.append((record.record_id, tokens, record.relevant, record.visibility == "private" or record.data_class in {"confidential", "personal"} or record.sanitization_status in {"pending", "rejected"}))
    return "\n\n".join(chunks), token_rows


def evaluate_scenario(base: pathlib.Path, records: list[Record]) -> dict[str, object]:
    started = time.perf_counter()
    oracle_records, _ = select_records("oracle", records)
    oracle_ids = {record.record_id for record in oracle_records}
    rows: dict[str, object] = {}

    for strategy in STRATEGY_ORDER:
        selected, dropped = select_records(strategy, records)
        text, token_rows = text_for_strategy(strategy, selected, base)
        tokens = estimate_tokens(text)
        selected_ids = {record.record_id for record in selected}
        useful = selected_ids & oracle_ids
        precision = len(useful) / len(selected_ids) if selected_ids else 0.0
        recall = len(useful) / len(oracle_ids) if oracle_ids else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        irrelevant_tokens = sum(token_count for _, token_count, relevant, _ in token_rows if not relevant)
        privacy_leaks = sum(1 for _, _, _, leak in token_rows if leak)
        rows[strategy] = {
            "prompt_tokens": tokens,
            "estimated_cost_usd": round(tokens / 1000 * PRICE_PER_1K_INPUT, 6),
            "included_sources": len(selected),
            "useful_sources_included": len(useful),
            "useful_source_precision": round(precision, 4),
            "useful_source_recall": round(recall, 4),
            "useful_source_f1": round(f1, 4),
            "irrelevant_context_ratio": round(1 - precision, 4),
            "irrelevant_token_ratio": round(irrelevant_tokens / tokens, 4) if tokens else 0,
            "oracle_distance": round(1 - f1, 4),
            "privacy_leakage_count": privacy_leaks,
            "dropped_source_reasons": dropped,
        }
    return {
        "markdown_files": len(records),
        "ground_truth_relevant_records": sum(1 for record in records if record.relevant),
        "oracle_records": len(oracle_ids),
        "seconds": round(time.perf_counter() - started, 4),
        "strategies": rows,
    }


def measure_scenario(root: pathlib.Path, tmp: pathlib.Path, count: int, seed: int) -> dict[str, object]:
    scenario_name = SCENARIO_NAMES.get(count, f"scenario_{count}")
    scenario_dir = tmp / scenario_name
    tracemalloc.start()
    started = time.perf_counter()
    records = write_corpus(scenario_dir, count, seed)
    metrics = evaluate_scenario(scenario_dir, records)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    metrics["total_seconds"] = round(time.perf_counter() - started, 4)
    metrics["peak_python_bytes"] = peak
    metrics["corpus_path"] = str(scenario_dir.relative_to(root)).replace("\\", "/")
    return {"name": scenario_name, "size": count, "metrics": metrics}


def compute_growth(report: dict[str, object]) -> dict[str, object]:
    slopes: dict[str, float] = {}
    scenarios = report["scenarios"]
    for strategy in STRATEGY_ORDER:
        points = [(item["size"], item["metrics"]["strategies"][strategy]["prompt_tokens"]) for item in scenarios]
        if len(points) < 2:
            slopes[strategy] = 0
            continue
        first_size, first_tokens = points[0]
        last_size, last_tokens = points[-1]
        slopes[strategy] = round((last_tokens - first_tokens) / max(1, last_size - first_size), 4)
    return {"context_growth_slope_tokens_per_file": slopes}


def chart_payload(report: dict[str, object]) -> dict[str, object]:
    charts = {
        "tokens_by_project_size": [],
        "cost_by_strategy": [],
        "precision_recall": [],
        "irrelevant_context_ratio": [],
        "context_growth_curve": [],
        "oracle_distance": [],
    }
    for scenario in report["scenarios"]:
        for strategy, data in scenario["metrics"]["strategies"].items():
            charts["tokens_by_project_size"].append({"scenario": scenario["name"], "size": scenario["size"], "strategy": strategy, "value": data["prompt_tokens"]})
            charts["cost_by_strategy"].append({"scenario": scenario["name"], "size": scenario["size"], "strategy": strategy, "value": data["estimated_cost_usd"]})
            charts["precision_recall"].append(
                {
                    "scenario": scenario["name"],
                    "size": scenario["size"],
                    "strategy": strategy,
                    "precision": data["useful_source_precision"],
                    "recall": data["useful_source_recall"],
                }
            )
            charts["irrelevant_context_ratio"].append({"scenario": scenario["name"], "size": scenario["size"], "strategy": strategy, "value": data["irrelevant_context_ratio"]})
            charts["context_growth_curve"].append({"scenario": scenario["name"], "size": scenario["size"], "strategy": strategy, "value": data["prompt_tokens"]})
            charts["oracle_distance"].append({"scenario": scenario["name"], "size": scenario["size"], "strategy": strategy, "value": data["oracle_distance"]})
    return {
        "generated_at": report["generated_at"],
        "commit": report["commit"],
        "token_method": report["token_method"],
        "charts": charts,
        "growth": report["growth"],
    }


def svg_bar(title: str, rows: list[dict[str, object]], value_key: str, unit: str) -> str:
    width = 980
    height = 420
    margin = 54
    max_value = max([float(row[value_key]) for row in rows] + [1.0])
    bar_w = max(4, (width - 2 * margin) / max(1, len(rows)))
    colors = {
        "full_vault": "#8b1e3f",
        "naive_paste": "#b85c38",
        "keyword_search": "#d99b2b",
        "metadata_scan": "#397097",
        "owledge_context_pack": "#26734d",
        "oracle": "#4b5563",
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{margin}" y="30" font-family="system-ui" font-size="18" font-weight="700" fill="#17202a">{html.escape(title)}</text>',
        f'<text x="{margin}" y="52" font-family="system-ui" font-size="12" fill="#52616f">Unit: {html.escape(unit)}</text>',
        f'<line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#aab4c0"/>',
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#aab4c0"/>',
    ]
    for index, row in enumerate(rows):
        value = float(row[value_key])
        x = margin + index * bar_w
        h = (height - 2 * margin) * (value / max_value)
        y = height - margin - h
        strategy = str(row["strategy"])
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(3, bar_w - 2):.1f}" height="{h:.1f}" fill="{colors.get(strategy, "#52616f")}"/>')
    parts.append(f'<text x="{margin}" y="{height - 18}" font-family="system-ui" font-size="11" fill="#52616f">Bars are ordered by scenario and strategy. Exact values are in context-growth-charts.json.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def svg_line(title: str, rows: list[dict[str, object]], value_key: str, unit: str) -> str:
    width = 980
    height = 420
    margin = 58
    by_strategy: dict[str, list[dict[str, object]]] = {strategy: [] for strategy in STRATEGY_ORDER}
    for row in rows:
        by_strategy[str(row["strategy"])].append(row)
    sizes = sorted({int(row["size"]) for row in rows})
    max_x = max(sizes or [1])
    min_x = min(sizes or [0])
    max_y = max([float(row[value_key]) for row in rows] + [1.0])
    colors = {
        "full_vault": "#8b1e3f",
        "naive_paste": "#b85c38",
        "keyword_search": "#d99b2b",
        "metadata_scan": "#397097",
        "owledge_context_pack": "#26734d",
        "oracle": "#4b5563",
    }

    def point(row: dict[str, object]) -> tuple[float, float]:
        x_ratio = (int(row["size"]) - min_x) / max(1, max_x - min_x)
        y_ratio = float(row[value_key]) / max_y
        return margin + x_ratio * (width - 2 * margin), height - margin - y_ratio * (height - 2 * margin)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{margin}" y="30" font-family="system-ui" font-size="18" font-weight="700" fill="#17202a">{html.escape(title)}</text>',
        f'<text x="{margin}" y="52" font-family="system-ui" font-size="12" fill="#52616f">Unit: {html.escape(unit)}</text>',
        f'<line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#aab4c0"/>',
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#aab4c0"/>',
    ]
    legend_x = margin
    for strategy, strategy_rows in by_strategy.items():
        if not strategy_rows:
            continue
        strategy_rows = sorted(strategy_rows, key=lambda item: int(item["size"]))
        points = [point(row) for row in strategy_rows]
        polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        parts.append(f'<polyline points="{polyline}" fill="none" stroke="{colors[strategy]}" stroke-width="2.5"/>')
        for x, y in points:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{colors[strategy]}"/>')
        parts.append(f'<rect x="{legend_x}" y="{height - 34}" width="10" height="10" fill="{colors[strategy]}"/>')
        parts.append(f'<text x="{legend_x + 14}" y="{height - 25}" font-family="system-ui" font-size="10" fill="#17202a">{html.escape(strategy)}</text>')
        legend_x += 145
    parts.append("</svg>")
    return "\n".join(parts)


def write_charts(report_dir: pathlib.Path, charts: dict[str, object]) -> dict[str, str]:
    chart_rows = charts["charts"]
    files = {
        "tokens_by_project_size": svg_line("Prompt tokens by project size", chart_rows["tokens_by_project_size"], "value", "prompt tokens"),
        "cost_by_strategy": svg_bar("Estimated input cost by strategy", chart_rows["cost_by_strategy"], "value", "USD"),
        "precision_recall": svg_bar(
            "Useful-source precision by strategy",
            [{"scenario": row["scenario"], "size": row["size"], "strategy": row["strategy"], "value": row["precision"]} for row in chart_rows["precision_recall"]],
            "value",
            "precision 0-1",
        ),
        "irrelevant_context_ratio": svg_bar("Irrelevant-context ratio", chart_rows["irrelevant_context_ratio"], "value", "ratio 0-1"),
        "context_growth_curve": svg_line("Context growth curve", chart_rows["context_growth_curve"], "value", "prompt tokens"),
        "oracle_distance": svg_bar("Oracle-distance comparison", chart_rows["oracle_distance"], "value", "distance 0-1"),
    }
    written: dict[str, str] = {}
    for name, svg in files.items():
        filename = f"{name}.svg"
        (report_dir / filename).write_text(svg, encoding="utf-8", newline="\n")
        written[name] = filename
    return written


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Enterprise Context Benchmark",
        "",
        "## Benchmark Question",
        "",
        "How do context assembly strategies behave as a Markdown-first agent memory vault grows from a fresh project to a synthetic two-year enterprise project?",
        "",
        "## Hypotheses",
        "",
        "- H1: Scoped Owledge context packs grow sublinearly compared with full-vault prompting.",
        "- H2: Owledge context packs reduce irrelevant-context ratio compared with naive paste and keyword search.",
        "- H3: Metadata-first selection plus scoped context remains closer to the oracle set than full-vault prompting under a tighter token budget.",
        "",
        "## Reproducibility",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Commit: `{report['commit']}`",
        f"- Command: `{report['command']}`",
        f"- Token method: `{report['token_method']}`",
        f"- Cost assumption: `${report['price_per_1k_input_usd']}` per 1K input tokens",
        "",
        "## Results",
        "",
    ]
    for scenario in report["scenarios"]:
        lines.extend(
            [
                f"### {scenario['name']} ({scenario['size']} Markdown files)",
                "",
                "| Strategy | Prompt tokens | Cost USD | Precision | Recall | Irrelevant token ratio | Oracle distance | Privacy leaks |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for strategy in STRATEGY_ORDER:
            data = scenario["metrics"]["strategies"][strategy]
            lines.append(
                f"| {strategy} | {data['prompt_tokens']} | {data['estimated_cost_usd']} | "
                f"{data['useful_source_precision']} | {data['useful_source_recall']} | "
                f"{data['irrelevant_token_ratio']} | {data['oracle_distance']} | {data['privacy_leakage_count']} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Threats To Validity",
            "",
            "- The corpus is synthetic and controls ground truth; external validity requires real project vaults.",
            "- Token counts use `tiktoken` when available and a deterministic char/4 estimate otherwise.",
            "- Cost numbers are scenario estimates, not universal savings claims.",
            "- The oracle set is benchmark-defined and does not replace human review.",
            "",
            "## Interpretation Boundary",
            "",
            "Claims must be scoped to the generated corpus, commit, seed, tokenizer, and command above.",
            "",
        ]
    )
    return "\n".join(lines)


def render_html(report: dict[str, object], chart_files: dict[str, str]) -> str:
    rows = []
    for scenario in report["scenarios"]:
        for strategy in STRATEGY_ORDER:
            data = scenario["metrics"]["strategies"][strategy]
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(scenario['name']))}</td>"
                f"<td>{scenario['size']}</td>"
                f"<td>{html.escape(strategy)}</td>"
                f"<td>{data['prompt_tokens']}</td>"
                f"<td>{data['estimated_cost_usd']}</td>"
                f"<td>{data['useful_source_precision']}</td>"
                f"<td>{data['useful_source_recall']}</td>"
                f"<td>{data['irrelevant_token_ratio']}</td>"
                f"<td>{data['oracle_distance']}</td>"
                f"<td>{data['privacy_leakage_count']}</td>"
                "</tr>"
            )
    chart_imgs = "\n".join(
        f'<section><h2>{html.escape(name.replace("_", " ").title())}</h2><img src="{html.escape(filename)}" alt="{html.escape(name)} chart"></section>'
        for name, filename in chart_files.items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Enterprise Context Benchmark</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; background: #f5f7fa; color: #17202a; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 32px; }}
    header, section {{ background: #fff; border: 1px solid #d8dee7; padding: 20px; margin: 0 0 18px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #e3e8ef; padding: 8px; text-align: right; }}
    th:first-child, td:first-child, th:nth-child(3), td:nth-child(3) {{ text-align: left; }}
    code {{ background: #eef2f6; padding: 2px 5px; }}
    img {{ max-width: 100%; height: auto; border: 1px solid #e3e8ef; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>Enterprise Context Benchmark</h1>
    <p>Research-grade synthetic experiment. JSON is the source artifact; charts and tables are generated views.</p>
    <p><strong>Commit:</strong> <code>{html.escape(str(report['commit']))}</code> <strong>Tokenizer:</strong> <code>{html.escape(str(report['token_method']))}</code></p>
    <p><strong>Command:</strong> <code>{html.escape(str(report['command']))}</code></p>
  </header>
  <section>
    <h2>Hypotheses</h2>
    <ul>
      <li>H1: Scoped Owledge context packs grow sublinearly compared with full-vault prompting.</li>
      <li>H2: Owledge reduces irrelevant-context ratio compared with naive paste and keyword search.</li>
      <li>H3: Metadata-first selection plus scoped context remains closer to the oracle than full-vault prompting under tighter token budgets.</li>
    </ul>
  </section>
  {chart_imgs}
  <section>
    <h2>Final Data Table</h2>
    <table>
      <thead><tr><th>Scenario</th><th>Files</th><th>Strategy</th><th>Tokens</th><th>Cost USD</th><th>Precision</th><th>Recall</th><th>Irrelevant Tokens</th><th>Oracle Distance</th><th>Privacy Leaks</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </section>
  <section>
    <h2>Threats To Validity</h2>
    <p>The corpus is synthetic and controls ground truth. External validity requires runs against real project vaults. Cost numbers are scenario estimates, not universal savings claims.</p>
  </section>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Run research-grade synthetic context hygiene benchmarks.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--profile", default="research_default", choices=sorted(PROFILE_SIZES))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    root = pathlib.Path(args.project_root).resolve()
    tmp = root / ".agent-control" / "tmp" / "enterprise-context-benchmark" / f"{args.profile}-seed-{args.seed}"
    results_dir = root / "benchmarks" / "results"
    report_dir = root / "agent-memory" / "reports" / "enterprise-context-benchmark"
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    command = (
        "python tools/enterprise-context-benchmark/run-enterprise-context-benchmark.py "
        f"--project-root . --profile {args.profile} --seed {args.seed}"
    )
    report: dict[str, object] = {
        "schema_version": "enterprise-context-benchmark-v2",
        "generated_at": utc_now(),
        "commit": git_commit(root),
        "os": platform.platform(),
        "python": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "command": command,
        "profile": args.profile,
        "seed": args.seed,
        "token_method": TOKEN_METHOD,
        "price_per_1k_input_usd": PRICE_PER_1K_INPUT,
        "hypotheses": [
            "H1 scoped Owledge context packs grow sublinearly compared with full-vault prompting.",
            "H2 Owledge context packs reduce irrelevant-context ratio compared with naive paste and keyword search.",
            "H3 metadata-first selection plus scoped context remains closer to the oracle than full-vault prompting under a tighter token budget.",
        ],
        "scenarios": [],
    }
    for count in PROFILE_SIZES[args.profile]:
        report["scenarios"].append(measure_scenario(root, tmp, count, args.seed))
    report["growth"] = compute_growth(report)

    charts = chart_payload(report)
    chart_files = write_charts(report_dir, charts)
    markdown = render_markdown(report)

    (results_dir / "context-growth.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    (results_dir / "context-growth-charts.json").write_text(json.dumps(charts, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    (results_dir / "token-efficiency.md").write_text(markdown, encoding="utf-8", newline="\n")
    (report_dir / "index.html").write_text(render_html(report, chart_files), encoding="utf-8", newline="\n")

    print(
        json.dumps(
            {
                "report": "benchmarks/results/context-growth.json",
                "charts": "benchmarks/results/context-growth-charts.json",
                "markdown": "benchmarks/results/token-efficiency.md",
                "html": "agent-memory/reports/enterprise-context-benchmark/index.html",
                "profile": args.profile,
                "seed": args.seed,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
