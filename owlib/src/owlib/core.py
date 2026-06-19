from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import pathlib
import re
import shutil
from typing import Any, Iterable


LIBRARY_DIRS = [
    "registry",
    "imports",
    "indexes",
    "parallels",
    "conflicts",
    "ideas",
    "patterns",
    "reports",
    "modules",
    "skills",
]

ALLOWED_AGENT_MEMORY_DIRS = {
    "canonical",
    "compiled",
    "patterns",
    "lessons",
    "decisions",
    "ideas",
    "handoffs",
    "evidence",
}

LIST_FIELDS = {
    "concept_tags",
    "stack_tags",
    "problem_patterns",
    "architecture_patterns",
    "failure_modes",
    "reusable_lessons",
    "planning_relevance",
}

REVIEWED_STATUSES = {"active", "approved", "promoted", "reviewed"}
SHARED_ALLOWED_DATA_CLASSES = {"public", "internal"}
PARALLEL_FIELDS = [
    "concept_tags",
    "stack_tags",
    "problem_patterns",
    "architecture_patterns",
    "failure_modes",
    "reusable_lessons",
]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "item"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_library(root: pathlib.Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for relative in LIBRARY_DIRS:
        (root / relative).mkdir(parents=True, exist_ok=True)


def init_library(root: pathlib.Path) -> dict[str, Any]:
    ensure_library(root)
    config = root / "owlib.yaml"
    if not config.exists():
        config.write_text(
            json.dumps(
                {
                    "schema": "owlib-v0.1",
                    "created_at": utc_now(),
                    "storage": "markdown-jsonl",
                    "promotion_policy": "candidate-only",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    registry = root / "registry" / "projects.jsonl"
    registry.touch(exist_ok=True)
    return {"passed": True, "library_root": str(root), "config": str(config)}


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    meta: dict[str, Any] = {}
    current_key = ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("  - ") and current_key:
            meta.setdefault(current_key, []).append(strip_quotes(line[4:]))
            continue
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        value = strip_quotes(raw.strip())
        if key in LIST_FIELDS and value == "":
            meta[key] = []
            current_key = key
        elif value == "":
            meta[key] = ""
            current_key = key
        else:
            meta[key] = value
            current_key = key if key in LIST_FIELDS else ""
    return meta


def markdown_body(text: str) -> str:
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    return parts[2].strip() if len(parts) >= 3 else text


def read_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: pathlib.Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def registry_path(library_root: pathlib.Path) -> pathlib.Path:
    return library_root / "registry" / "projects.jsonl"


def read_registry(library_root: pathlib.Path) -> list[dict[str, Any]]:
    return read_jsonl(registry_path(library_root))


def project_id_from_context(project_root: pathlib.Path) -> str:
    context = project_root / "PROJECT_CONTEXT.md"
    if context.exists():
        meta = parse_frontmatter(context.read_text(encoding="utf-8", errors="replace"))
        project_id = str(meta.get("project_id") or "").strip()
        if project_id and project_id != "PROJECT_ID":
            return slugify(project_id)
    return slugify(project_root.name)


def validate_owledge_project(project_root: pathlib.Path) -> None:
    if not project_root.exists():
        raise ValueError(f"Project path does not exist: {project_root}")
    if not (project_root / "PROJECT_CONTEXT.md").exists():
        raise ValueError(f"Missing PROJECT_CONTEXT.md: {project_root}")
    if not (project_root / "agent-memory").exists():
        raise ValueError(f"Missing agent-memory directory: {project_root}")


def register_project(library_root: pathlib.Path, project_path: pathlib.Path, name: str | None = None) -> dict[str, Any]:
    ensure_library(library_root)
    project_root = project_path.resolve()
    validate_owledge_project(project_root)
    project_id = project_id_from_context(project_root)
    rows = read_registry(library_root)
    kept = [row for row in rows if row.get("project_id") != project_id and pathlib.Path(row.get("path", "")).resolve() != project_root]
    entry = {
        "project_id": project_id,
        "name": name or project_root.name,
        "path": str(project_root),
        "registered_at": utc_now(),
        "source": "owledge-project",
    }
    kept.append(entry)
    write_jsonl(registry_path(library_root), kept)
    return {"passed": True, "project": entry, "registry": str(registry_path(library_root))}


def is_allowed_project_file(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    rel = path.relative_to(project_root).as_posix()
    if rel == "PROJECT_CONTEXT.md":
        return True
    parts = rel.split("/")
    if len(parts) >= 3 and parts[0] == "agent-memory" and parts[1] in ALLOWED_AGENT_MEMORY_DIRS:
        return path.suffix.lower() == ".md"
    return False


def is_reviewed_record(meta: dict[str, Any]) -> bool:
    return str(meta.get("review_status", "")).lower() == "approved" or str(meta.get("status", "")).lower() in REVIEWED_STATUSES


def is_unsafe_shared(meta: dict[str, Any]) -> bool:
    if str(meta.get("visibility", "")).lower() != "shared":
        return False
    return (
        str(meta.get("review_status", "")).lower() != "approved"
        or str(meta.get("sanitization_status", "")).lower() != "approved"
        or str(meta.get("data_class", "")).lower() not in SHARED_ALLOWED_DATA_CLASSES
    )


def iter_importable_records(project_root: pathlib.Path, reviewed_only: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for path in sorted(project_root.rglob("*.md"), key=lambda item: item.as_posix()):
        if not is_allowed_project_file(project_root, path):
            continue
        rel = path.relative_to(project_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        if is_unsafe_shared(meta):
            rejected.append({"source_path": rel, "reason": "unsafe-shared-record"})
            continue
        if reviewed_only and rel != "PROJECT_CONTEXT.md" and not is_reviewed_record(meta):
            rejected.append({"source_path": rel, "reason": "not-reviewed"})
            continue
        body = markdown_body(text)
        records.append(
            {
                "memory_id": meta.get("memory_id") or f"owlib:{slugify(rel)}",
                "project_id": meta.get("project_id") or project_id_from_context(project_root),
                "doc_type": meta.get("doc_type") or ("project_context" if rel == "PROJECT_CONTEXT.md" else "note"),
                "status": meta.get("status", ""),
                "visibility": meta.get("visibility", "private"),
                "semantic_title": meta.get("semantic_title") or path.stem,
                "summary": meta.get("summary") or body[:240].replace("\n", " "),
                "metadata": meta,
                "source_path": rel,
                "source_hash": sha256_file(path),
                "text_excerpt": body[:4000],
                "imported_at": utc_now(),
            }
        )
    return records, rejected


def sync_library(library_root: pathlib.Path, reviewed_only: bool = False) -> dict[str, Any]:
    ensure_library(library_root)
    imported = 0
    rejected_total = 0
    project_results = []
    for project in read_registry(library_root):
        project_root = pathlib.Path(project["path"]).resolve()
        validate_owledge_project(project_root)
        records, rejected = iter_importable_records(project_root, reviewed_only=reviewed_only)
        import_dir = library_root / "imports" / project["project_id"]
        if import_dir.exists():
            shutil.rmtree(import_dir)
        import_dir.mkdir(parents=True)
        write_jsonl(import_dir / "records.jsonl", records)
        write_jsonl(import_dir / "rejected.jsonl", rejected)
        imported += len(records)
        rejected_total += len(rejected)
        project_results.append({"project_id": project["project_id"], "records": len(records), "rejected": len(rejected)})
    return {"passed": True, "projects": project_results, "records": imported, "rejected": rejected_total}


def load_imported_records(library_root: pathlib.Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((library_root / "imports").glob("*/records.jsonl")):
        records.extend(read_jsonl(path))
    return records


def build_index(library_root: pathlib.Path) -> dict[str, Any]:
    ensure_library(library_root)
    records = load_imported_records(library_root)
    write_jsonl(library_root / "indexes" / "records.jsonl", records)
    projects = sorted({str(row.get("project_id", "")) for row in records if row.get("project_id")})
    summary = {
        "generated_at": utc_now(),
        "projects": projects,
        "records": len(records),
        "doc_types": {},
    }
    for record in records:
        doc_type = str(record.get("doc_type") or "unknown")
        summary["doc_types"][doc_type] = summary["doc_types"].get(doc_type, 0) + 1
    (library_root / "indexes" / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"passed": True, **summary}


def load_index_records(library_root: pathlib.Path) -> list[dict[str, Any]]:
    path = library_root / "indexes" / "records.jsonl"
    if not path.exists():
        build_index(library_root)
    return read_jsonl(path)


def normalize_list(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(item).strip().lower() for item in value if str(item).strip()}


def tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]{2,}", value.lower())}


def find_parallel_candidates(library_root: pathlib.Path) -> dict[str, Any]:
    records = load_index_records(library_root)
    candidates = []
    for idx, left in enumerate(records):
        left_meta = left.get("metadata", {})
        for right in records[idx + 1 :]:
            if left.get("project_id") == right.get("project_id"):
                continue
            right_meta = right.get("metadata", {})
            matches: dict[str, list[str]] = {}
            for field in PARALLEL_FIELDS:
                common = sorted(normalize_list(left_meta.get(field)) & normalize_list(right_meta.get(field)))
                if common:
                    matches[field] = common
            semantic_left = tokenize(" ".join([str(left.get("semantic_title", "")), str(left.get("summary", ""))]))
            semantic_right = tokenize(" ".join([str(right.get("semantic_title", "")), str(right.get("summary", ""))]))
            semantic_common = sorted(semantic_left & semantic_right)
            if len(semantic_common) >= 3:
                matches["semantic_tokens"] = semantic_common[:12]
            if matches:
                candidates.append(
                    {
                        "left": left.get("memory_id"),
                        "left_project": left.get("project_id"),
                        "right": right.get("memory_id"),
                        "right_project": right.get("project_id"),
                        "matches": matches,
                        "score": sum(len(values) for values in matches.values()),
                        "status": "parallel-candidate",
                    }
                )
    candidates.sort(key=lambda row: (-int(row["score"]), str(row["left"]), str(row["right"])))
    write_jsonl(library_root / "parallels" / "parallel-candidates.jsonl", candidates)
    return {"passed": True, "candidates": len(candidates), "path": str(library_root / "parallels" / "parallel-candidates.jsonl")}


def write_library_report(library_root: pathlib.Path) -> dict[str, Any]:
    records = load_index_records(library_root)
    parallels_path = library_root / "parallels" / "parallel-candidates.jsonl"
    parallels = read_jsonl(parallels_path) if parallels_path.exists() else []
    report_path = library_root / "reports" / f"library-report-{slugify(utc_now())}.md"
    projects = sorted({str(row.get("project_id")) for row in records})
    lines = [
        "---",
        f'generated_at: "{utc_now()}"',
        'status: "candidate"',
        'review_status: "unreviewed"',
        "---",
        "",
        "# Owlib Library Report",
        "",
        f"- Projects: {len(projects)}",
        f"- Imported records: {len(records)}",
        f"- Parallel candidates: {len(parallels)}",
        "",
        "## Projects",
        "",
    ]
    lines.extend(f"- `{project}`" for project in projects)
    lines.extend(["", "## Top Parallel Candidates", ""])
    for item in parallels[:10]:
        lines.append(f"- `{item['left']}` <-> `{item['right']}` score={item['score']}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"passed": True, "path": str(report_path), "records": len(records), "parallels": len(parallels)}


def growth_scan(library_root: pathlib.Path) -> dict[str, Any]:
    records = load_index_records(library_root)
    tags: dict[str, int] = {}
    stale = []
    for record in records:
        meta = record.get("metadata", {})
        for field in ["concept_tags", "problem_patterns", "architecture_patterns", "failure_modes"]:
            for item in normalize_list(meta.get(field)):
                tags[item] = tags.get(item, 0) + 1
        valid_until = str(meta.get("valid_until") or "")
        if valid_until and valid_until < utc_now()[:10]:
            stale.append(record.get("memory_id"))
    top_tags = sorted(tags.items(), key=lambda item: (-item[1], item[0]))[:20]
    missing_modules = []
    if any("obsidian" in tag or "vault" in tag for tag, _ in top_tags):
        missing_modules.append("obsidian-adapter")
    if any("graphrag" in tag for tag, _ in top_tags):
        missing_modules.append("graphrag-adapter")
    result = {"passed": True, "records": len(records), "top_signals": top_tags, "stale_records": stale, "missing_modules": missing_modules}
    (library_root / "indexes" / "growth-scan.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def growth_suggest(library_root: pathlib.Path) -> dict[str, Any]:
    scan = growth_scan(library_root)
    path = library_root / "reports" / f"growth-suggestions-{slugify(utc_now())}.md"
    lines = [
        "---",
        f'generated_at: "{utc_now()}"',
        'status: "candidate"',
        'review_status: "unreviewed"',
        "---",
        "",
        "# Owlib Growth Suggestions",
        "",
        "## Top Signals",
        "",
    ]
    lines.extend(f"- `{tag}`: {count}" for tag, count in scan["top_signals"])
    lines.extend(["", "## Missing Module Candidates", ""])
    if scan["missing_modules"]:
        lines.extend(f"- `{name}`" for name in scan["missing_modules"])
    else:
        lines.append("- None")
    lines.extend(["", "## Stale Records", ""])
    if scan["stale_records"]:
        lines.extend(f"- `{memory_id}`" for memory_id in scan["stale_records"][:25])
    else:
        lines.append("- None")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"passed": True, "path": str(path), "suggestions": len(scan["top_signals"]) + len(scan["missing_modules"])}


def growth_promote_candidate(library_root: pathlib.Path, title: str, source: str = "") -> dict[str, Any]:
    path = library_root / "ideas" / f"growth-candidate-{slugify(title)}.md"
    text = f"""---
memory_id: "owlib:idea:growth-candidate-{slugify(title)}"
doc_type: "idea"
status: "candidate"
visibility: "private"
data_class: "internal"
semantic_title: "{title}"
summary: "Growth candidate generated by Owlib; review before any project promotion."
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "{utc_now()}"
source: "{source}"
---

# {title}

## Candidate

Describe why this should become a reusable module, skill, pattern, lesson, or central project.

## Source Signals

{source or "Add reviewed source records before promotion."}

## Promotion Rule

This is candidate knowledge. Do not write it into any project canonical memory until a curator approves it.
"""
    path.write_text(text, encoding="utf-8")
    return {"passed": True, "path": str(path), "status": "candidate"}
