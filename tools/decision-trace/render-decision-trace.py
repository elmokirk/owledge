#!/usr/bin/env python3
"""Render Owledge memory records as a read-only decision trace graph."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import re
from datetime import datetime, timezone


ORDER = [
    "project_context",
    "goal",
    "idea",
    "plan",
    "task",
    "evidence",
    "review",
    "qa",
    "adr",
    "decision",
    "lesson",
    "pattern",
    "compiled",
]

EXCLUDED_PARTS = {"reports", "sessions", "tmp", "exports", "indexes", "schemas", "templates"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    raw = text[4:end].splitlines()
    data: dict[str, object] = {}
    current_list: str | None = None
    current_edge: dict[str, object] | None = None

    for line in raw:
        if not line.strip():
            continue
        list_item = re.match(r"^\s*-\s*(.*)$", line)
        key_value = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        nested_key_value = re.match(r"^\s+([A-Za-z0-9_]+):\s*(.*)$", line)

        if list_item and current_list == "edges":
            value = list_item.group(1).strip()
            if ":" in value:
                key, edge_value = value.split(":", 1)
                current_edge = {key.strip(): clean_scalar(edge_value)}
                data.setdefault("edges", []).append(current_edge)
            else:
                current_edge = {"target": clean_scalar(value)}
                data.setdefault("edges", []).append(current_edge)
            continue
        if nested_key_value and current_list == "edges" and current_edge is not None:
            key, value = nested_key_value.groups()
            current_edge[key] = clean_scalar(value)
            continue
        if list_item and current_list:
            data.setdefault(current_list, []).append(clean_scalar(list_item.group(1)))
            continue
        if not key_value:
            continue

        key, value = key_value.groups()
        value = value.strip()
        if value == "[]":
            data[key] = []
            current_list = key
            current_edge = None
        elif value == "":
            data[key] = []
            current_list = key
            current_edge = None
        else:
            data[key] = clean_scalar(value)
            current_list = None
            current_edge = None
    return data


def clean_scalar(value: str) -> object:
    value = value.strip().strip('"').strip("'")
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value


def source_hash(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def candidate_paths(root: pathlib.Path) -> list[pathlib.Path]:
    paths = [root / "OWLEDGE.md"]
    memory_root = root / "owledge"
    if memory_root.exists():
        paths.extend(memory_root.rglob("*.md"))
    return [path for path in paths if path.exists() and not (EXCLUDED_PARTS & set(path.parts))]


def shared_allowed(meta: dict[str, object]) -> bool:
    visibility = str(meta.get("visibility", "private"))
    review_status = str(meta.get("review_status", "unreviewed"))
    sanitization_status = str(meta.get("sanitization_status", "not_required"))
    return visibility == "shared" and review_status in {"approved", "reviewed"} and sanitization_status in {"approved", "not_required"}


def collect_records(root: pathlib.Path, shared: bool) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    nodes: list[dict[str, object]] = []
    explicit_edges: list[dict[str, object]] = []
    for path in candidate_paths(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        if not meta:
            continue
        if shared and not shared_allowed(meta):
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        node_id = str(meta.get("memory_id", rel))
        doc_type = str(meta.get("doc_type", "unknown"))
        node = {
            "id": node_id,
            "doc_type": doc_type,
            "semantic_title": meta.get("semantic_title", path.stem),
            "summary": meta.get("summary", ""),
            "status": meta.get("status", ""),
            "visibility": meta.get("visibility", "private"),
            "review_status": meta.get("review_status", "unreviewed"),
            "sanitization_status": meta.get("sanitization_status", "not_required"),
            "source_path": rel,
            "source_hash": meta.get("source_hash") or source_hash(path),
            "phase_index": ORDER.index(doc_type) if doc_type in ORDER else 999,
        }
        nodes.append(node)
        for edge in meta.get("edges", []) if isinstance(meta.get("edges", []), list) else []:
            if not isinstance(edge, dict):
                continue
            target = str(edge.get("target", "")).strip()
            if not target:
                continue
            explicit_edges.append(
                {
                    "source": node_id,
                    "target": target,
                    "type": edge.get("type", "relates_to"),
                    "reason": edge.get("reason", ""),
                    "inferred": False,
                }
            )
    nodes = sorted(nodes, key=lambda row: (int(row["phase_index"]), str(row["source_path"])))
    return nodes, explicit_edges


def infer_phase_edges(nodes: list[dict[str, object]], explicit_edges: list[dict[str, object]]) -> list[dict[str, object]]:
    known = {(edge["source"], edge["target"]) for edge in explicit_edges}
    edges = list(explicit_edges)
    representative_by_phase: dict[str, dict[str, object]] = {}
    for node in nodes:
        representative_by_phase.setdefault(str(node["doc_type"]), node)
    ordered_representatives = [representative_by_phase[doc_type] for doc_type in ORDER if doc_type in representative_by_phase]
    for source, target in zip(ordered_representatives, ordered_representatives[1:]):
        key = (source["id"], target["id"])
        if key in known:
            continue
        edges.append(
            {
                "source": source["id"],
                "target": target["id"],
                "type": "phase_next",
                "reason": "Inferred read-only phase edge for visual trace continuity.",
                "inferred": True,
            }
        )
    return edges


def build_trace(root: pathlib.Path, shared: bool) -> dict[str, object]:
    nodes, explicit_edges = collect_records(root, shared)
    edges = infer_phase_edges(nodes, explicit_edges)
    return {
        "schema_version": "decision-trace-v2",
        "generated_at": utc_now(),
        "shared_mode": shared,
        "source": "Owledge Markdown frontmatter and typed edges",
        "linear_steps": nodes,
        "nodes": nodes,
        "edges": edges,
        "metrics": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "explicit_edge_count": len(explicit_edges),
            "inferred_edge_count": len(edges) - len(explicit_edges),
        },
    }


def render_tree_svg(trace: dict[str, object]) -> str:
    nodes = trace["nodes"]
    width = 1120
    row_h = 82
    height = max(180, 80 + len(nodes) * row_h)
    colors = {
        "project_context": "#334155",
        "goal": "#0f766e",
        "idea": "#7c3aed",
        "plan": "#2563eb",
        "task": "#0369a1",
        "evidence": "#15803d",
        "review": "#a16207",
        "qa": "#b45309",
        "adr": "#be123c",
        "decision": "#be123c",
        "lesson": "#4d7c0f",
        "pattern": "#4338ca",
        "compiled": "#475569",
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Decision trace tree">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="36" y="34" font-family="system-ui" font-size="20" font-weight="700" fill="#17202a">Decision Trace Tree</text>',
        '<text x="36" y="56" font-family="system-ui" font-size="12" fill="#52616f">Read-only generated view from trace.json. Markdown remains source of truth.</text>',
    ]
    for index, node in enumerate(nodes):
        y = 82 + index * row_h
        x = 54 + min(int(node["phase_index"]), 10) * 42
        color = colors.get(str(node["doc_type"]), "#64748b")
        if index:
            prev_y = 82 + (index - 1) * row_h + 24
            parts.append(f'<line x1="{x + 12}" y1="{prev_y}" x2="{x + 12}" y2="{y - 18}" stroke="#cbd5e1" stroke-width="2"/>')
        parts.append(f'<circle cx="{x + 12}" cy="{y}" r="12" fill="{color}"/>')
        parts.append(f'<rect x="{x + 34}" y="{y - 24}" width="840" height="58" rx="6" fill="#f8fafc" stroke="#d8dee7"/>')
        parts.append(f'<text x="{x + 48}" y="{y - 4}" font-family="system-ui" font-size="13" font-weight="700" fill="#17202a">{html.escape(str(node["doc_type"]))}: {html.escape(str(node["semantic_title"]))}</text>')
        parts.append(f'<text x="{x + 48}" y="{y + 17}" font-family="system-ui" font-size="11" fill="#52616f">{html.escape(str(node["source_path"]))}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def render_html(trace: dict[str, object]) -> str:
    rows = []
    for node in trace["linear_steps"]:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(node['doc_type']))}</td>"
            f"<td>{html.escape(str(node['semantic_title']))}</td>"
            f"<td><code>{html.escape(str(node['source_path']))}</code></td>"
            f"<td>{html.escape(str(node['review_status']))}</td>"
            f"<td>{html.escape(str(node['sanitization_status']))}</td>"
            "</tr>"
        )
    edges = []
    for edge in trace["edges"]:
        edges.append(
            "<tr>"
            f"<td><code>{html.escape(str(edge['source']))}</code></td>"
            f"<td>{html.escape(str(edge['type']))}</td>"
            f"<td><code>{html.escape(str(edge['target']))}</code></td>"
            f"<td>{'yes' if edge.get('inferred') else 'no'}</td>"
            "</tr>"
        )
    tree_svg = render_tree_svg(trace)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Decision Trace</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; background: #f5f7fa; color: #17202a; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 32px; }}
    header, section {{ background: #fff; border: 1px solid #d8dee7; margin: 0 0 18px; padding: 20px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #e3e8ef; padding: 8px; text-align: left; vertical-align: top; }}
    code {{ background: #eef2f6; padding: 2px 5px; }}
    .tree {{ overflow-x: auto; border: 1px solid #e3e8ef; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>Decision Trace</h1>
    <p>Read-only generated view. JSON is the trace artifact; Markdown memory remains source of truth.</p>
    <p>Nodes: {trace['metrics']['node_count']} Edges: {trace['metrics']['edge_count']} Explicit edges: {trace['metrics']['explicit_edge_count']} Shared mode: {str(trace['shared_mode']).lower()}</p>
  </header>
  <section>
    <h2>Visual Tree</h2>
    <div class="tree">{tree_svg}</div>
  </section>
  <section>
    <h2>Linear Steps</h2>
    <table><thead><tr><th>Type</th><th>Title</th><th>Source</th><th>Review</th><th>Sanitization</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
  </section>
  <section>
    <h2>Edges</h2>
    <table><thead><tr><th>Source</th><th>Type</th><th>Target</th><th>Inferred</th></tr></thead><tbody>{''.join(edges)}</tbody></table>
  </section>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render read-only Owledge decision trace JSON and HTML.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--shared", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.project_root).resolve()
    trace_dir = root / "owledge" / "decision-trace"
    report_dir = root / "owledge" / "reports" / "decision-trace"
    trace_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    trace = build_trace(root, args.shared)
    (trace_dir / "trace.json").write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    (report_dir / "index.html").write_text(render_html(trace), encoding="utf-8", newline="\n")
    print(json.dumps({"trace": ".owledge/decision-trace/trace.json", "html": ".owledge/reports/decision-trace/index.html", "nodes": trace["metrics"]["node_count"], "edges": trace["metrics"]["edge_count"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
