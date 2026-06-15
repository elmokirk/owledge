#!/usr/bin/env python3
"""Build a drop-in Agent Memory module inside an existing Markdown KB.

This generator is intentionally additive. It does not require global
environment variables, does not rewrite existing Markdown files, and does not
convert wiki links. It creates a small local module that agents can use for
project planning, handoffs, evidence, reviews, and source-aware indexing.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import shutil
import sys
from typing import Any, Iterable


MODULE_DIRS = [
    "agent-memory/plans",
    "agent-memory/handoffs",
    "agent-memory/evidence",
    "agent-memory/reviews",
    "agent-memory/indexes",
    "agent-memory/tmp",
]

REQUIRED_MAP_KEYS = {"plans", "evidence", "handoffs", "reviews", "indexes"}
OPTIONAL_MAP_KEYS = {"ideas", "tasks", "scratch"}

EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".obsidian",
    ".trash",
    ".agent-control",
    ".cache",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
    "__pycache__",
}

MARKDOWN_SUFFIXES = {".md", ".markdown"}
WIKI_LINK_RE = re.compile(r"\[\[([^\]\n]+)\]\]")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_relative(path: pathlib.Path) -> str:
    return path.as_posix()


def resolve_kb_root(value: str) -> pathlib.Path:
    root = pathlib.Path(value).expanduser()
    if not root.is_absolute():
        root = (pathlib.Path.cwd() / root).resolve()
    else:
        root = root.resolve()
    if not root.exists():
        raise SystemExit(f"Knowledgebase root does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Knowledgebase root is not a directory: {root}")
    return root


def resolve_module_root(kb_root: pathlib.Path, layout: str, module_dir: str) -> pathlib.Path:
    if layout == "flat":
        return kb_root
    clean = module_dir.strip().strip("/\\")
    if not clean:
        raise SystemExit("--module-dir must not be empty")
    candidate = (kb_root / clean).resolve()
    try:
        candidate.relative_to(kb_root)
    except ValueError as exc:
        raise SystemExit(f"Module directory must stay inside the knowledgebase root: {candidate}") from exc
    return candidate


def is_under(path: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def has_link_component(path: pathlib.Path, root: pathlib.Path) -> bool:
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            return True
        is_junction = getattr(current, "is_junction", None)
        if callable(is_junction) and is_junction():
            return True
    return False


def reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    seen: set[str] = set()
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"Duplicate key in agent-memory-map.json: {key}")
        seen.add(key)
        payload[key] = value
    return payload


def resolve_map_path(kb_root: pathlib.Path, raw: str) -> pathlib.Path:
    candidate = pathlib.Path(raw)
    if candidate.is_absolute():
        raise SystemExit(f"Map paths must be relative to the knowledgebase root: {raw}")
    if any(part == ".." for part in candidate.parts):
        raise SystemExit(f"Map paths must not contain '..': {raw}")
    unresolved = kb_root / candidate
    if unresolved.exists() and has_link_component(unresolved, kb_root):
        raise SystemExit(f"Mapped path must not contain symlinks or junctions: {raw}")
    resolved = (kb_root / candidate).resolve()
    try:
        resolved.relative_to(kb_root)
    except ValueError as exc:
        raise SystemExit(f"Mapped path escapes the knowledgebase root: {raw}") from exc
    if not resolved.exists() or not resolved.is_dir():
        raise SystemExit(f"Mapped path must already exist as a directory: {raw}")
    if has_link_component(resolved, kb_root):
        raise SystemExit(f"Mapped path must not contain symlinks or junctions: {raw}")
    return resolved


def load_mapping(kb_root: pathlib.Path, map_file: str) -> dict[str, pathlib.Path] | None:
    explicit_map = bool(map_file)
    candidate = pathlib.Path(map_file) if map_file else kb_root / "agent-memory-map.json"
    if not candidate.is_absolute():
        candidate = kb_root / candidate
    candidate = candidate.resolve()
    if not candidate.exists():
        if explicit_map:
            raise SystemExit(f"Map file does not exist: {candidate}")
        return None
    try:
        candidate.relative_to(kb_root)
    except ValueError as exc:
        raise SystemExit(f"Map file must stay inside the knowledgebase root: {candidate}") from exc
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8-sig"), object_pairs_hook=reject_duplicate_json_keys)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if not isinstance(payload, dict):
        raise SystemExit("agent-memory-map.json must contain a JSON object.")
    missing = sorted(REQUIRED_MAP_KEYS - set(payload))
    if missing:
        raise SystemExit(f"agent-memory-map.json is missing required keys: {', '.join(missing)}")
    allowed = REQUIRED_MAP_KEYS | OPTIONAL_MAP_KEYS
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise SystemExit(f"agent-memory-map.json contains unknown keys: {', '.join(unknown)}")
    mapping: dict[str, pathlib.Path] = {}
    for key, value in payload.items():
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"Map value for '{key}' must be a non-empty relative path string.")
        mapping[key] = resolve_map_path(kb_root, value)
    return mapping


def markdown_files(kb_root: pathlib.Path, excluded_roots: Iterable[pathlib.Path], max_files: int) -> tuple[list[pathlib.Path], bool]:
    if max_files < 1:
        raise SystemExit("--max-files must be at least 1")
    excluded = [path.resolve() for path in excluded_roots]
    files: list[pathlib.Path] = []
    truncated = False
    for path in sorted(kb_root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_dir():
            continue
        if path.suffix.lower() not in MARKDOWN_SUFFIXES:
            continue
        if path.is_symlink() or has_link_component(path, kb_root):
            continue
        if any(is_under(path, excluded_root) for excluded_root in excluded):
            continue
        relative = path.relative_to(kb_root)
        if any(part in EXCLUDED_DIR_NAMES for part in relative.parts[:-1]):
            continue
        if len(files) >= max_files:
            truncated = True
            break
        files.append(path)
    return sorted(files), truncated


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            if title:
                return title
    return fallback


def frontmatter_keys(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        if not lines or lines[0].lstrip("\ufeff").strip() != "---":
            return []
    else:
        lines[0] = lines[0].lstrip("\ufeff")
    keys: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^([A-Za-z0-9_-]+)\s*:", line)
        if match:
            keys.append(match.group(1))
    return sorted(set(keys))


def scan_markdown_file(kb_root: pathlib.Path, path: pathlib.Path) -> dict[str, Any]:
    data = path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    relative = path.relative_to(kb_root)
    links = sorted(set(match.strip() for match in WIKI_LINK_RE.findall(text) if match.strip()))
    return {
        "source_path": normalize_relative(relative),
        "title": extract_title(text, path.stem),
        "size": len(data),
        "source_hash": sha256_bytes(data),
        "frontmatter_keys": frontmatter_keys(text),
        "wiki_links": links[:50],
        "wiki_link_count": len(links),
    }


def ensure_dirs(module_root: pathlib.Path) -> None:
    for relative in MODULE_DIRS:
        directory = module_root / pathlib.Path(relative)
        directory.mkdir(parents=True, exist_ok=True)
        gitkeep = directory / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")


def write_text_if_missing(path: pathlib.Path, text: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: pathlib.Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            count += 1
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return count


def module_readme(module_root: pathlib.Path, kb_root: pathlib.Path, layout: str, module_dir: str, mapping: dict[str, pathlib.Path] | None) -> str:
    relative_module = "." if module_root == kb_root else normalize_relative(module_root.relative_to(kb_root))
    write_rule = (
        "Write new planning and memory artifacts only inside the mapped vault paths listed below."
        if mapping
        else f"Write new planning and memory artifacts only inside `{relative_module}/agent-memory/`."
    )
    index_rule = (
        f"Use `{normalize_relative(mapping['indexes'].relative_to(kb_root))}/kb-scan.jsonl` as a generated source index, not canonical truth."
        if mapping
        else "Use `agent-memory/indexes/kb-scan.jsonl` as a generated source index, not canonical truth."
    )
    mapped_lines = ""
    local_paths = """| Path | Purpose |
| --- | --- |
| `agent-memory/plans/` | Project plans and planning deltas |
| `agent-memory/handoffs/` | Agent handoff notes |
| `agent-memory/evidence/` | Source-backed evidence notes |
| `agent-memory/reviews/` | QA, red-team, and decision reviews |
| `agent-memory/indexes/` | Generated read-only indexes over the host KB |"""
    if mapping:
        local_paths = """| Map key | Path | Purpose |
| --- | --- | --- |
| `plans` | `{plans}` | Project plans and planning deltas |
| `handoffs` | `{handoffs}` | Agent handoff notes |
| `evidence` | `{evidence}` | Source-backed evidence notes |
| `reviews` | `{reviews}` | QA, red-team, and decision reviews |
| `indexes` | `{indexes}` | Generated read-only indexes over the host KB |""".format(
            plans=normalize_relative(mapping["plans"].relative_to(kb_root)),
            handoffs=normalize_relative(mapping["handoffs"].relative_to(kb_root)),
            evidence=normalize_relative(mapping["evidence"].relative_to(kb_root)),
            reviews=normalize_relative(mapping["reviews"].relative_to(kb_root)),
            indexes=normalize_relative(mapping["indexes"].relative_to(kb_root)),
        )
        mapped_lines = "\n## Mapped Vault Paths\n\n" + "\n".join(
            f"- `{key}` -> `{normalize_relative(path.relative_to(kb_root))}`" for key, path in sorted(mapping.items())
        ) + "\n"
    return f"""# Agent Memory Module

This is a drop-in planning and memory module for this Markdown knowledgebase.

## Agent Rules

- Treat existing knowledgebase files as read-only unless the user explicitly asks for edits.
- Do not rewrite, normalize, or convert existing `[[Wiki Links]]`.
- Do not require or set OS environment variables.
- {write_rule}
- {index_rule}
- Cite original source paths when creating plans, handoffs, evidence, or reviews.

## Local Paths

{local_paths}
{mapped_lines}

## Refresh

From the kit repo or copied tool location, run:

```bash
python tools/build_kb_module.py --knowledgebase-root "{kb_root}" --layout {layout} --module-dir "{module_dir}"
```

This refreshes generated module indexes without changing existing KB notes.
"""


def sample_plan(records: list[dict[str, Any]]) -> str:
    generated_at = utc_now()
    sources = records[:5]
    source_lines = "\n".join(
        f"- `{record['source_path']}` - {record['title']} ({record['source_hash'][:12]})"
        for record in sources
    )
    if not source_lines:
        source_lines = "- No Markdown source files were found during the initial scan."
    return f"""---
doc_type: "plan"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "Example KB-backed project plan"
summary: "Starter project plan generated from read-only knowledgebase scan metadata."
created_at: "{generated_at}"
updated_at: "{generated_at}"
---

# Example KB-Backed Project Plan

## Goal

Create a source-backed project plan from the existing Markdown knowledgebase without changing the original notes.

## Initial Sources

{source_lines}

## Working Rules

- Keep the existing knowledgebase structure intact.
- Reference source paths instead of copying long note contents.
- Write new planning artifacts inside this module only.
- Review and sanitize any content before shared export.

## Next Actions

1. Ask the user which project or goal should be planned.
2. Select the relevant source notes from `agent-memory/indexes/kb-scan.jsonl`.
3. Create a concrete project plan in `agent-memory/plans/`.
4. Add evidence or handoff notes only when they cite source paths.
"""


def copy_cli(source_root: pathlib.Path, target_root: pathlib.Path) -> pathlib.Path | None:
    source = source_root / "tools" / "agent_memory_cli.py"
    if not source.exists():
        return None
    target = target_root / "tools" / "agent_memory_cli.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(source, target)
    return target


def build(args: argparse.Namespace) -> dict[str, Any]:
    source_root = pathlib.Path(args.kit_root).resolve() if args.kit_root else pathlib.Path(__file__).resolve().parents[1]
    kb_root = resolve_kb_root(args.knowledgebase_root)
    mapping = load_mapping(kb_root, args.map_file)
    module_root = kb_root if mapping else resolve_module_root(kb_root, args.layout, args.module_dir)
    module_root.mkdir(parents=True, exist_ok=True)
    if not mapping:
        ensure_dirs(module_root)

    plan_dir = mapping["plans"] if mapping else module_root / "agent-memory" / "plans"
    index_dir = mapping["indexes"] if mapping else module_root / "agent-memory" / "indexes"
    excluded_roots = (
        [path for key, path in mapping.items() if key != "ideas"]
        if mapping
        else [module_root]
    )
    discovered, truncated = markdown_files(kb_root, excluded_roots, args.max_files)
    records = [scan_markdown_file(kb_root, path) for path in discovered]

    created_files: list[str] = []
    skipped_files: list[str] = []

    module_doc = (index_dir / "AGENT_MEMORY_MODULE.md") if mapping else (module_root / "AGENT_MEMORY_MODULE.md")
    if write_text_if_missing(module_doc, module_readme(module_root, kb_root, args.layout, args.module_dir, mapping)):
        created_files.append(normalize_relative(module_doc.relative_to(kb_root)))
    else:
        skipped_files.append(normalize_relative(module_doc.relative_to(kb_root)))

    plan_path = plan_dir / "example-kb-backed-project-plan.md"
    if args.create_sample_plan:
        if write_text_if_missing(plan_path, sample_plan(records)):
            created_files.append(normalize_relative(plan_path.relative_to(kb_root)))
        else:
            skipped_files.append(normalize_relative(plan_path.relative_to(kb_root)))

    copied_cli_path = copy_cli(source_root, index_dir if mapping else module_root) if args.include_cli else None
    copied_cli = normalize_relative(copied_cli_path.relative_to(kb_root)) if copied_cli_path else None
    if copied_cli:
        created_files.append(copied_cli)

    index_path = index_dir / "kb-scan.jsonl"
    rows = write_jsonl(index_path, records)

    status = {
        "generated_at": utc_now(),
        "knowledgebase_root": str(kb_root),
        "module_root": str(module_root),
        "mode": "mapped" if mapping else "module",
        "layout": "mapped" if mapping else args.layout,
        "module_dir": args.module_dir if args.layout != "flat" else "",
        "markdown_files_scanned": rows,
        "markdown_scan_truncated": truncated,
        "max_files": args.max_files,
        "index_path": normalize_relative(index_path.relative_to(kb_root)),
        "module_doc": normalize_relative(module_doc.relative_to(kb_root)),
        "created_files": created_files,
        "skipped_existing_module_files": skipped_files,
        "existing_kb_files_modified": False,
        "wiki_links_converted": False,
        "requires_os_environment_variables": False,
        "copied_cli": copied_cli,
        "mapping_enabled": bool(mapping),
        "mapped_paths": {
            key: normalize_relative(path.relative_to(kb_root)) for key, path in sorted((mapping or {}).items())
        },
    }
    write_json(index_dir / "kb-module-status.json", status)
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a drop-in Agent Memory module for an existing Markdown knowledgebase.")
    parser.add_argument("--knowledgebase-root", required=True, help="Existing Markdown KB or Obsidian vault root.")
    parser.add_argument("--kit-root", default="", help="Optional Agent Memory Kit root. Defaults to this script's repo.")
    parser.add_argument("--layout", choices=["module-dir", "flat"], default="module-dir")
    parser.add_argument("--module-dir", default="agent-memory-module")
    parser.add_argument("--map-file", default="", help="Optional agent-memory-map.json path inside the KB.")
    parser.add_argument("--max-files", type=int, default=10000)
    parser.add_argument("--include-cli", action="store_true", help="Copy tools/agent_memory_cli.py into the module.")
    parser.add_argument("--create-sample-plan", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args(argv)
    result = build(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
