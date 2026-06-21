#!/usr/bin/env python3
"""Render a snapshot-first power-user positioning scorecard."""

from __future__ import annotations

import argparse
import html
import json
import pathlib
from datetime import datetime, timezone


AXES = [
    ("durable_source_of_truth", "Durable source of truth"),
    ("context_hygiene", "Context hygiene"),
    ("traceability", "Traceability"),
    ("multi_agent_handoff", "Multi-agent handoff"),
    ("integration_safety", "Integration safety"),
    ("benchmarkability", "Benchmarkability"),
    ("compliance_auditability", "Compliance/auditability"),
    ("adoption_friction", "Low adoption friction"),
]

COMPARATORS = [
    {
        "name": "Owledge",
        "category": "Markdown-first memory/proof layer",
        "scores": {
            "durable_source_of_truth": 5,
            "context_hygiene": 5,
            "traceability": 5,
            "multi_agent_handoff": 4,
            "integration_safety": 5,
            "benchmarkability": 4,
            "compliance_auditability": 5,
            "adoption_friction": 3,
        },
        "positioning": "Best when long-running projects need durable plans, evidence, reviews, handoffs, decisions, and proof artifacts across agents.",
        "limitation": "Not an execution runtime, graph database, vector store, or replacement for existing project-specific agent instructions.",
    },
    {
        "name": "Superpowers-style execution frameworks",
        "category": "Agent execution methodology",
        "scores": {
            "durable_source_of_truth": 2,
            "context_hygiene": 3,
            "traceability": 3,
            "multi_agent_handoff": 4,
            "integration_safety": 3,
            "benchmarkability": 3,
            "compliance_auditability": 2,
            "adoption_friction": 4,
        },
        "positioning": "Strong for coding workflow discipline, implementation flow, and agent execution structure.",
        "limitation": "Usually not a project-wide reviewed memory contract or cross-project proof layer.",
    },
    {
        "name": "Graphify-style graph visualizers",
        "category": "Graph visualization and exploration",
        "scores": {
            "durable_source_of_truth": 2,
            "context_hygiene": 3,
            "traceability": 4,
            "multi_agent_handoff": 2,
            "integration_safety": 3,
            "benchmarkability": 2,
            "compliance_auditability": 3,
            "adoption_friction": 3,
        },
        "positioning": "Strong for seeing relationships, dependencies, and clusters once clean source records exist.",
        "limitation": "A graph view should consume reviewed memory; it should not become the canonical truth by itself.",
    },
    {
        "name": "LLM Wiki / Obsidian-style knowledgebases",
        "category": "Human-curated notes and wiki structure",
        "scores": {
            "durable_source_of_truth": 4,
            "context_hygiene": 2,
            "traceability": 3,
            "multi_agent_handoff": 2,
            "integration_safety": 4,
            "benchmarkability": 2,
            "compliance_auditability": 3,
            "adoption_friction": 4,
        },
        "positioning": "Strong for human knowledge capture, linking, and existing taxonomy.",
        "limitation": "Needs explicit contracts, review status, and scoped context generation before agents can consume it reliably.",
    },
    {
        "name": "Claude Code / Codex-style agent runtimes",
        "category": "Agent runtime and coding execution",
        "scores": {
            "durable_source_of_truth": 2,
            "context_hygiene": 4,
            "traceability": 3,
            "multi_agent_handoff": 4,
            "integration_safety": 3,
            "benchmarkability": 3,
            "compliance_auditability": 3,
            "adoption_friction": 5,
        },
        "positioning": "Strong for executing tasks, editing files, running tests, and operating agent sessions.",
        "limitation": "Runtime memory and logs are not the same as reviewed project memory with reusable decisions and lessons.",
    },
    {
        "name": "Custom harnesses and hooks",
        "category": "Team-specific agent automation",
        "scores": {
            "durable_source_of_truth": 2,
            "context_hygiene": 3,
            "traceability": 3,
            "multi_agent_handoff": 4,
            "integration_safety": 2,
            "benchmarkability": 3,
            "compliance_auditability": 2,
            "adoption_friction": 2,
        },
        "positioning": "Strong for highly tailored orchestration and local automation.",
        "limitation": "Often depends on implicit team conventions unless paired with a stable memory and evidence contract.",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def total_score(row: dict[str, object]) -> int:
    scores = row["scores"]
    return int(round(sum(int(scores[axis]) for axis, _ in AXES) / (len(AXES) * 5) * 100))


def payload() -> dict[str, object]:
    rows = []
    for row in COMPARATORS:
        enriched = dict(row)
        enriched["score_100"] = total_score(row)
        rows.append(enriched)
    return {
        "schema_version": "poweruser-positioning-v1",
        "generated_at": utc_now(),
        "scoring_note": "Scores describe fit for Owledge's memory/proof positioning, not absolute product quality.",
        "axes": [{"id": key, "label": label, "scale": "1-5"} for key, label in AXES],
        "comparators": rows,
        "interpretation": "Owledge is strongest as a durable memory, evidence, context hygiene, and traceability layer beside execution runtimes, graph views, wikis, and harnesses.",
    }


def render_markdown(data: dict[str, object]) -> str:
    lines = [
        "# Poweruser Positioning Scorecard",
        "",
        data["scoring_note"],
        "",
        "| Comparator | Category | Score | Positioning | Limitation |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in data["comparators"]:
        lines.append(
            f"| {row['name']} | {row['category']} | {row['score_100']} | {row['positioning']} | {row['limitation']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            str(data["interpretation"]),
            "",
            "## Boundary",
            "",
            "This is a snapshot-first local scorecard. It should be updated when concrete comparator repositories, versions, or benchmark evidence are selected.",
            "",
        ]
    )
    return "\n".join(lines)


def render_html(data: dict[str, object]) -> str:
    headers = "".join(f"<th>{html.escape(label)}</th>" for _, label in AXES)
    rows = []
    for row in data["comparators"]:
        score_cells = "".join(f"<td>{row['scores'][axis]}</td>" for axis, _ in AXES)
        rows.append(
            "<tr>"
            f"<td>{html.escape(row['name'])}</td>"
            f"<td>{html.escape(row['category'])}</td>"
            f"<td>{row['score_100']}</td>"
            f"{score_cells}"
            f"<td>{html.escape(row['positioning'])}</td>"
            f"<td>{html.escape(row['limitation'])}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Poweruser Positioning Scorecard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; background: #f5f7fa; color: #17202a; }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 32px; }}
    header, section {{ background: white; border: 1px solid #d8dee7; padding: 20px; margin: 0 0 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ border-bottom: 1px solid #e3e8ef; padding: 8px; vertical-align: top; text-align: left; }}
    td:nth-child(n+3):nth-child(-n+11), th:nth-child(n+3):nth-child(-n+11) {{ text-align: right; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>Poweruser Positioning Scorecard</h1>
    <p>{html.escape(str(data['scoring_note']))}</p>
    <p>{html.escape(str(data['interpretation']))}</p>
  </header>
  <section>
    <table>
      <thead><tr><th>Comparator</th><th>Category</th><th>Score</th>{headers}<th>Positioning</th><th>Limitation</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </section>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Owledge poweruser positioning scorecard.")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    root = pathlib.Path(args.project_root).resolve()
    out = root / "agent-memory" / "reports" / "poweruser-positioning"
    out.mkdir(parents=True, exist_ok=True)
    data = payload()
    (out / "positioning.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    (out / "positioning.md").write_text(render_markdown(data), encoding="utf-8", newline="\n")
    (out / "index.html").write_text(render_html(data), encoding="utf-8", newline="\n")
    print(json.dumps({"json": "agent-memory/reports/poweruser-positioning/positioning.json", "html": "agent-memory/reports/poweruser-positioning/index.html"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
