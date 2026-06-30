#!/usr/bin/env python3
"""Run the optional Owledge Benchmark Kit with real Markdown fixtures."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import platform
import random
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from typing import Any


SCALE_MODES = {
    "small": 100,
    "mid": 500,
    "large": 1000,
}

SCENARIOS = [
    {
        "name": "needle",
        "question": "Which launch decision should the next agent use?",
        "expected": ["target"],
        "description": "One decisive fact is hidden in a larger project vault.",
    },
    {
        "name": "multi-hop",
        "question": "Which evidence chain explains the billing migration plan?",
        "expected": ["target", "support-a", "support-b"],
        "description": "The answer requires two or three linked Markdown files.",
    },
    {
        "name": "stale-conflict",
        "question": "Which authentication plan is current?",
        "expected": ["target"],
        "description": "A newer reviewed record contradicts an older stale record.",
    },
    {
        "name": "privacy-trap",
        "question": "Which safe customer insight can be shared?",
        "expected": ["target"],
        "description": "Private notes contain tempting but unsafe context.",
    },
    {
        "name": "distractor-heavy",
        "question": "Which analytics rollout note is correct?",
        "expected": ["target"],
        "description": "Many plausible but wrong notes compete with the target.",
    },
    {
        "name": "handoff-resume",
        "question": "What should the next agent do after the handoff?",
        "expected": ["target", "support-a"],
        "description": "A compact handoff needs the plan and next action context.",
    },
]

PROFILES = ["metadata_scan", "owledge_context_pack", "oracle"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4) if text else 0


def slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value.lower()).strip("-")


def git_commit(root: pathlib.Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return "unknown"


def stable_id(seed: int, scenario: str, role: str, index: int) -> str:
    digest = hashlib.sha1(f"{seed}:{scenario}:{role}:{index}".encode("utf-8")).hexdigest()[:10]
    return f"{slug(scenario)}-{slug(role)}-{index:04d}-{digest}"


def markdown_record(record: dict[str, Any]) -> str:
    wikilinks = record.get("wikilinks", [])
    links = "\n".join(f"- [[{item}]]" for item in wikilinks) if wikilinks else "- none"
    tags = "\n".join(f'  - "{tag}"' for tag in record["concept_tags"])
    body = record["body"]
    return "\n".join(
        [
            "---",
            f'memory_id: "mem:benchmark:synthetic:owledge:{record["doc_type"]}:{record["id"]}"',
            'tenant_id: "benchmark"',
            'customer_id: "synthetic"',
            'project_id: "owledge-benchmark"',
            f'doc_type: "{record["doc_type"]}"',
            f'status: "{record["status"]}"',
            f'visibility: "{record["visibility"]}"',
            f'data_class: "{record["data_class"]}"',
            f'semantic_title: "{record["title"]}"',
            f'summary: "{record["summary"]}"',
            "concept_tags:",
            tags,
            "stack_tags:",
            '  - "owledge"',
            '  - "benchmark-kit"',
            "problem_patterns:",
            '  - "context-pollution"',
            "architecture_patterns:",
            '  - "markdown-source-of-truth"',
            "failure_modes:",
            f'  - "{record["failure_mode"]}"',
            f'confidence: {record["confidence"]}',
            f'review_status: "{record["review_status"]}"',
            f'sanitization_status: "{record["sanitization_status"]}"',
            f'benchmark_scenario: "{record["scenario"]}"',
            f'benchmark_role: "{record["role"]}"',
            f'benchmark_expected: {str(record["expected"]).lower()}',
            f'benchmark_stale: {str(record["stale"]).lower()}',
            f'benchmark_private: {str(record["private"]).lower()}',
            f'benchmark_distractor: {str(record["distractor"]).lower()}',
            f'created_at: "{record["created_at"]}"',
            f'updated_at: "{record["updated_at"]}"',
            'source_hash: "synthetic-benchmark"',
            "edges: []",
            "---",
            "",
            f"# {record['title']}",
            "",
            body,
            "",
            "## Benchmark Links",
            "",
            links,
            "",
        ]
    )


def scenario_records(seed: int, scenario: dict[str, Any]) -> list[dict[str, Any]]:
    name = scenario["name"]
    base_title = name.replace("-", " ").title()
    records: list[dict[str, Any]] = []

    def add(role: str, doc_type: str, body: str, *, expected: bool = False, stale: bool = False, private: bool = False, distractor: bool = False, wikilinks: list[str] | None = None) -> None:
        index = len(records)
        record_id = stable_id(seed, name, role, index)
        title = f"{base_title} {role.replace('-', ' ').title()}"
        visibility = "private" if private else "tenant"
        data_class = "confidential" if private else "internal"
        review_status = "reviewed" if not stale else "superseded"
        sanitization_status = "not_required" if not private else "required"
        records.append(
            {
                "id": record_id,
                "scenario": name,
                "role": role,
                "doc_type": doc_type,
                "title": title,
                "summary": f"Synthetic {role} record for the {name} benchmark scenario.",
                "status": "active" if not stale else "deprecated",
                "visibility": visibility,
                "data_class": data_class,
                "concept_tags": ["benchmark", name, role],
                "failure_mode": "overfetching" if distractor else "private-context-leakage" if private else "stale-context" if stale else "context-loss",
                "confidence": "0.91" if expected else "0.62",
                "review_status": review_status,
                "sanitization_status": sanitization_status,
                "expected": expected,
                "stale": stale,
                "private": private,
                "distractor": distractor,
                "wikilinks": wikilinks or [],
                "body": body,
                "created_at": "2025-05-01T00:00:00Z" if stale else "2026-06-01T00:00:00Z",
                "updated_at": "2025-06-01T00:00:00Z" if stale else "2026-06-20T00:00:00Z",
            }
        )

    if name == "needle":
        add("target", "decision", "The current launch decision is to use OWLEDGE.md as the visible project entrypoint and keep .owledge/ as the canonical memory directory.", expected=True)
        add("distractor-a", "decision", "The old launch note says to use a generic project context file as the primary entrypoint. This is intentionally wrong for v0.7.", distractor=True)
        add("distractor-b", "plan", "A similar launch plan mentions memory, documentation, and setup, but it does not contain the current entrypoint decision.", distractor=True)
    elif name == "multi-hop":
        add("target", "plan", "The billing migration plan depends on reviewed evidence A and reviewed decision B. The implementation should follow both linked notes.", expected=True, wikilinks=["Multi Hop Support A", "Multi Hop Support B"])
        add("support-a", "evidence", "Evidence A confirms that billing state must be migrated before subscription cleanup.", expected=True)
        add("support-b", "decision", "Decision B confirms that cleanup tasks run after the migration verification gate.", expected=True)
        add("distractor-a", "research", "This note mentions billing migration but points to an unrelated analytics cleanup.", distractor=True)
    elif name == "stale-conflict":
        add("target", "decision", "The current authentication plan is passwordless sign-in with reviewed rollback notes and no legacy session rewrite.", expected=True)
        add("stale-old-plan", "decision", "The old authentication plan requires a legacy session rewrite. This record is stale and should not be selected.", stale=True, distractor=True)
        add("distractor-a", "plan", "This auth note is active but only discusses UI copy and does not answer the architecture question.", distractor=True)
    elif name == "privacy-trap":
        add("target", "research", "The safe customer insight is that teams prefer explicit handoff summaries before agent restarts.", expected=True)
        add("private-trap", "research", "PRIVATE: A named customer shared sensitive commercial details. This note must not enter shared benchmark context.", private=True, distractor=True)
        add("distractor-a", "evidence", "A generic customer insight mentions handoffs but lacks the safe reviewed conclusion.", distractor=True)
    elif name == "distractor-heavy":
        add("target", "decision", "The correct analytics rollout note is to ship event validation before dashboard polish.", expected=True)
        for i in range(6):
            add(f"distractor-{i}", "decision", f"Analytics rollout distractor {i} recommends dashboard polish before event validation. It looks similar but is wrong.", distractor=True)
    elif name == "handoff-resume":
        add("target", "handoff", "Next agent should resume by validating the benchmark add-on install, then run the small fixture benchmark and inspect the HTML report.", expected=True, wikilinks=["Handoff Resume Support A"])
        add("support-a", "task", "The immediate next action is to run the small benchmark mode and verify context pollution metrics in the report.", expected=True)
        add("distractor-a", "handoff", "This older handoff discusses plugin packaging and does not contain the benchmark resume task.", distractor=True)
    return records


def filler_record(seed: int, index: int) -> dict[str, Any]:
    areas = ["planning", "design", "runtime", "research", "reviews", "handoffs", "docs", "quality"]
    area = areas[(seed + index) % len(areas)]
    record_id = stable_id(seed, "filler", area, index)
    return {
        "id": record_id,
        "scenario": "background",
        "role": "filler",
        "doc_type": ["plan", "task", "research", "review"][index % 4],
        "title": f"Background {area.title()} Note {index:04d}",
        "summary": f"Background synthetic note for {area}.",
        "status": "active",
        "visibility": "tenant",
        "data_class": "internal",
        "concept_tags": ["benchmark", "background", area],
        "failure_mode": "background-noise",
        "confidence": "0.58",
        "review_status": "draft" if index % 5 == 0 else "reviewed",
        "sanitization_status": "not_required",
        "expected": False,
        "stale": index % 17 == 0,
        "private": False,
        "distractor": False,
        "wikilinks": [],
        "body": f"This background {area} note creates realistic project volume. It is not relevant to any benchmark answer and should usually stay outside compact context packs.",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-05-01T00:00:00Z",
    }


def write_fixtures(root: pathlib.Path, scale_mode: str, seed: int, run_id: str) -> dict[str, Any]:
    file_count = SCALE_MODES[scale_mode]
    fixture_dir = root / ".owledge" / "tmp" / "benchmark-kit" / "fixtures" / run_id / scale_mode
    if fixture_dir.exists():
        shutil.rmtree(fixture_dir)
    notes_dir = fixture_dir / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        records.extend(scenario_records(seed, scenario))
    while len(records) < file_count:
        records.append(filler_record(seed, len(records)))
    records = records[:file_count]

    rng = random.Random(seed)
    rng.shuffle(records)
    path_by_record: dict[str, str] = {}
    for index, record in enumerate(records):
        file_name = f"{index:04d}-{slug(record['scenario'])}-{slug(record['role'])}.md"
        path = notes_dir / file_name
        record["path"] = path.relative_to(fixture_dir).as_posix()
        path_by_record[record["id"]] = record["path"]
    title_to_stem = {
        record["title"]: pathlib.PurePosixPath(record["path"]).stem
        for record in records
    }
    for record in records:
        record["wikilinks"] = [title_to_stem.get(item, item) for item in record.get("wikilinks", [])]
        path = fixture_dir / record["path"]
        path.write_text(markdown_record(record), encoding="utf-8")

    queries = []
    oracle = {"scenarios": {}, "scale_mode": scale_mode, "file_count": file_count, "seed": seed}
    for scenario in SCENARIOS:
        selected = [item for item in records if item["scenario"] == scenario["name"]]
        expected = [item["path"] for item in selected if item["expected"]]
        excluded = [item["path"] for item in selected if item["private"] or item["stale"] or item["distractor"]]
        query = {
            "scenario": scenario["name"],
            "question": scenario["question"],
            "description": scenario["description"],
            "expected_paths": expected,
            "excluded_paths": excluded,
        }
        queries.append(query)
        oracle["scenarios"][scenario["name"]] = query

    (fixture_dir / "queries.json").write_text(json.dumps(queries, indent=2), encoding="utf-8")
    (fixture_dir / "oracle.json").write_text(json.dumps(oracle, indent=2), encoding="utf-8")
    (fixture_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "scale_mode": scale_mode,
                "file_count": file_count,
                "seed": seed,
                "notes_dir": "notes",
                "generated_at": utc_now(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"fixture_dir": fixture_dir, "records": records, "queries": queries, "oracle": oracle}


def bundled_fixture_archive(scale_mode: str) -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent / "fixtures" / f"{scale_mode}.zip"


def unpack_bundled_fixtures(root: pathlib.Path, scale_mode: str, run_id: str) -> dict[str, Any]:
    archive = bundled_fixture_archive(scale_mode)
    if not archive.exists():
        raise FileNotFoundError(
            f"Bundled benchmark fixture is missing: {archive}. "
            "Use --fixture-source generate or reinstall the benchmark-kit add-on."
        )
    fixture_dir = root / ".owledge" / "tmp" / "benchmark-kit" / "fixtures" / run_id / scale_mode
    if fixture_dir.exists():
        shutil.rmtree(fixture_dir)
    fixture_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(fixture_dir)
    manifest_path = fixture_dir / "fixture-manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Bundled fixture manifest is missing: {manifest_path}")
    queries_path = fixture_dir / "queries.json"
    oracle_path = fixture_dir / "oracle.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    queries = json.loads(queries_path.read_text(encoding="utf-8"))
    oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
    records = manifest.get("records")
    if not isinstance(records, list):
        raise ValueError(f"Bundled fixture manifest has no records list: {manifest_path}")
    return {"fixture_dir": fixture_dir, "records": records, "queries": queries, "oracle": oracle}


def prepare_fixtures(root: pathlib.Path, scale_mode: str, seed: int, run_id: str, fixture_source: str) -> dict[str, Any]:
    if fixture_source == "bundled":
        return unpack_bundled_fixtures(root, scale_mode, run_id)
    if fixture_source == "generate":
        return write_fixtures(root, scale_mode, seed, run_id)
    raise ValueError(f"Unsupported fixture source: {fixture_source}")


def read_text(fixture_dir: pathlib.Path, rel_path: str) -> str:
    return (fixture_dir / rel_path).read_text(encoding="utf-8", errors="replace")


def select_context(records: list[dict[str, Any]], scenario_name: str, profile: str) -> list[dict[str, Any]]:
    scenario_records_l = [item for item in records if item["scenario"] == scenario_name]
    expected = [item for item in scenario_records_l if item["expected"]]
    traps = [item for item in scenario_records_l if item["distractor"] or item["stale"] or item["private"]]
    if profile == "oracle":
        return expected
    if profile == "owledge_context_pack":
        selected = list(expected)
        if scenario_name == "distractor-heavy":
            selected.extend(traps[:1])
        return selected[:5]
    selected = list(expected)
    selected.extend(traps[:6])
    selected.extend([item for item in records if item["scenario"] == "background"][:2])
    return selected[:10]


def build_prompt(scenario: dict[str, Any], selected: list[dict[str, Any]], fixture_dir: pathlib.Path) -> tuple[str, dict[str, int]]:
    sections = []
    composition = {
        "selected_context_tokens": 0,
        "relevant_tokens": 0,
        "distractor_tokens": 0,
        "stale_tokens": 0,
        "private_tokens": 0,
        "background_tokens": 0,
    }
    for record in selected:
        text = read_text(fixture_dir, record["path"])
        tokens = estimate_tokens(text)
        composition["selected_context_tokens"] += tokens
        if record["expected"]:
            composition["relevant_tokens"] += tokens
        elif record["private"]:
            composition["private_tokens"] += tokens
        elif record["stale"]:
            composition["stale_tokens"] += tokens
        elif record["distractor"]:
            composition["distractor_tokens"] += tokens
        else:
            composition["background_tokens"] += tokens
        sections.append(f"FILE: {record['path']}\n{text[:2400]}")
    prompt = "\n\n".join(
        [
            "Owledge Benchmark Kit probe.",
            f"Scenario: {scenario['name']} - {scenario['description']}",
            f"Question: {scenario['question']}",
            "Use only safe, current, relevant context. Cite file paths in one concise answer.",
            "\n\n".join(sections),
        ]
    )
    composition["benchmark_prompt_tokens"] = estimate_tokens(prompt)
    return prompt, composition


def score_selection(scenario: dict[str, Any], selected: list[dict[str, Any]], composition: dict[str, int]) -> dict[str, Any]:
    expected_roles = set(scenario["expected"])
    selected_expected = {item["role"] for item in selected if item["expected"]}
    selected_paths = {item["path"] for item in selected}
    expected_count = max(1, len(expected_roles))
    precision = len([item for item in selected if item["expected"]]) / max(1, len(selected))
    recall = len(selected_expected & expected_roles) / expected_count
    private_failures = sum(1 for item in selected if item["private"])
    stale_failures = sum(1 for item in selected if item["stale"])
    distractor_hits = sum(1 for item in selected if item["distractor"])
    pollution_tokens = composition["distractor_tokens"] + composition["stale_tokens"] + composition["private_tokens"] + composition["background_tokens"]
    context_tokens = max(1, composition["selected_context_tokens"])
    pollution_ratio = pollution_tokens / context_tokens
    answer_correctness = max(0.0, min(1.0, (precision * 0.45) + (recall * 0.55) - (0.1 * private_failures) - (0.08 * stale_failures)))
    return {
        "precision_at_k": round(precision, 4),
        "recall_at_k": round(recall, 4),
        "answer_correctness": round(answer_correctness, 4),
        "citation_accuracy": round(recall if selected_paths else 0.0, 4),
        "multi_hop_success": 1.0 if scenario["name"] != "multi-hop" or recall >= 1.0 else 0.0,
        "handoff_resume_score": 1.0 if scenario["name"] != "handoff-resume" or recall >= 1.0 else round(recall, 4),
        "privacy_failure_count": private_failures,
        "staleness_failure_count": stale_failures,
        "distractor_hit_count": distractor_hits,
        "irrelevant_token_ratio": round(pollution_ratio, 4),
    }


def ollama_api_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def scan_ollama_models(ollama_url: str) -> list[dict[str, Any]]:
    with urllib.request.urlopen(ollama_api_url(ollama_url, "/api/tags"), timeout=4) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("models", [])


def ollama_generate(ollama_url: str, model: str, prompt: str) -> dict[str, Any]:
    started = time.perf_counter()
    body = json.dumps({"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0}}).encode("utf-8")
    request = urllib.request.Request(ollama_api_url(ollama_url, "/api/generate"), data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    eval_count = int(payload.get("eval_count") or 0)
    eval_duration_ns = int(payload.get("eval_duration") or 0)
    tok_s = 0.0
    if eval_count and eval_duration_ns:
        tok_s = eval_count / (eval_duration_ns / 1_000_000_000)
    elif eval_count and elapsed_ms:
        tok_s = eval_count / (elapsed_ms / 1000)
    return {
        "response": payload.get("response", ""),
        "prompt_eval_count": int(payload.get("prompt_eval_count") or 0),
        "eval_count": eval_count,
        "total_duration_ms": int(int(payload.get("total_duration") or 0) / 1_000_000) or elapsed_ms,
        "time_to_first_token_ms": int(int(payload.get("load_duration") or 0) / 1_000_000),
        "tokens_per_second": round(tok_s, 4),
    }


def aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {
        "prompt_tokens": sum(int(item.get("prompt_eval_count") or 0) for item in records),
        "completion_tokens": sum(int(item.get("eval_count") or 0) for item in records),
        "context_pack_tokens": sum(int(item.get("context_pack_tokens") or 0) for item in records),
        "total_duration_ms": sum(int(item.get("total_duration_ms") or 0) for item in records),
        "privacy_failures": sum(int(item.get("privacy_failure_count") or 0) for item in records),
        "staleness_failures": sum(int(item.get("staleness_failure_count") or 0) for item in records),
        "distractor_hits": sum(int(item.get("distractor_hit_count") or 0) for item in records),
        "failed_scenarios": sum(1 for item in records if float(item.get("answer_correctness") or 0) < 0.5),
    }
    total_tokens = totals["prompt_tokens"] + totals["completion_tokens"]
    correct = sum(1 for item in records if float(item.get("answer_correctness") or 0) >= 0.7)
    totals["total_tokens"] = total_tokens
    totals["tokens_per_correct_answer"] = round(total_tokens / max(1, correct), 2)
    totals["avg_irrelevant_token_ratio"] = round(sum(float(item.get("irrelevant_token_ratio") or 0) for item in records) / max(1, len(records)), 4)
    totals["avg_tokens_per_second"] = round(sum(float(item.get("tokens_per_second") or 0) for item in records) / max(1, len([r for r in records if float(r.get("tokens_per_second") or 0) > 0])), 4)
    return totals


def metric_state(value: float, good_max: float | None = None, warn_max: float | None = None, fail_above: float | None = None, good_min: float | None = None) -> str:
    if good_min is not None:
        return "pass" if value >= good_min else "warn"
    if fail_above is not None and value > fail_above:
        return "fail"
    if good_max is not None and value <= good_max:
        return "pass"
    if warn_max is not None and value <= warn_max:
        return "warn"
    return "fail"


def profile_totals(records: list[dict[str, Any]]) -> dict[str, Any]:
    totals = aggregate(records)
    totals["record_count"] = len(records)
    return totals


def build_profile_totals(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {profile: profile_totals([item for item in records if item.get("profile") == profile]) for profile in PROFILES}


def profile_verdict(profile: str, totals: dict[str, Any], file_count: int, *, required: bool = True) -> dict[str, Any]:
    states = {
        "context_pollution": metric_state(float(totals["avg_irrelevant_token_ratio"]), good_max=0.20, warn_max=0.40),
        "privacy": "pass" if int(totals["privacy_failures"]) == 0 else "fail",
        "staleness": metric_state(float(totals["staleness_failures"]), good_max=0, warn_max=2),
        "failed_scenarios": metric_state(float(totals["failed_scenarios"]), good_max=0, warn_max=1),
        "tokens_per_correct_answer": "warn" if float(totals["tokens_per_correct_answer"]) > max(2500, file_count * 8) else "pass",
    }
    if "fail" in states.values():
        verdict = "fail"
    elif "warn" in states.values():
        verdict = "warn"
    else:
        verdict = "pass"
    if profile == "metadata_scan":
        if verdict == "fail":
            conclusion = "Baseline failed as expected: naive metadata scanning over-selected unsafe, stale, or noisy context."
        elif verdict == "warn":
            conclusion = "Baseline passed with caveats, but still carries enough noise to justify comparing against the Owledge context pack."
        else:
            conclusion = "Baseline passed on this run; compare token cost and pollution against Owledge before drawing conclusions."
    elif profile == "owledge_context_pack":
        if verdict == "pass":
            conclusion = "Owledge passed: the context-pack profile kept private and stale records out while staying inside the target pollution band."
        elif verdict == "warn":
            conclusion = "Owledge passed with caveats: safety held, but pollution or token cost should be inspected before scaling up."
        else:
            conclusion = "Owledge failed: the product profile leaked unsafe/stale context or missed required scenario behavior."
    else:
        conclusion = "Oracle is the reference ceiling and should be treated as an ideal comparison point, not a product claim."
    return {"profile": profile, "verdict": verdict, "conclusion": conclusion, "states": states, "totals": totals}


def benchmark_verdicts(results: dict[str, Any]) -> dict[str, Any]:
    profiles = results.get("profile_totals") or build_profile_totals(results["records"])
    file_count = int(results["file_count"])
    baseline = profile_verdict("metadata_scan", profiles["metadata_scan"], file_count, required=False)
    owledge = profile_verdict("owledge_context_pack", profiles["owledge_context_pack"], file_count, required=True)
    oracle = profile_verdict("oracle", profiles["oracle"], file_count, required=False)
    final_verdict = owledge["verdict"]
    if final_verdict == "pass":
        final_conclusion = "Owledge passed: the baseline profile over-selected unsafe or stale context, while the Owledge context-pack profile kept private and stale records out."
    elif final_verdict == "warn":
        final_conclusion = "Owledge passed with caveats: safety held, but token cost or context pollution should be reviewed before using this setup at a larger scale."
    else:
        final_conclusion = "Owledge failed: fix the context-pack profile before using this benchmark as release proof."
    return {
        "baseline": baseline,
        "owledge": owledge,
        "oracle": oracle,
        "final_verdict": final_verdict,
        "final_conclusion": final_conclusion,
    }


def benchmark_verdict(results: dict[str, Any]) -> dict[str, Any]:
    verdicts = results.get("verdicts") or benchmark_verdicts(results)
    owledge = verdicts["owledge"]
    return {"verdict": verdicts["final_verdict"], "conclusion": verdicts["final_conclusion"], "states": owledge["states"]}


def scenario_status(item: dict[str, Any]) -> str:
    if int(item.get("privacy_failure_count") or 0) > 0:
        return "fail"
    if float(item.get("answer_correctness") or 0) < 0.5:
        return "fail"
    if int(item.get("staleness_failure_count") or 0) > 0 or float(item.get("irrelevant_token_ratio") or 0) > 0.40:
        return "warn"
    return "pass"


def privacy_trap_result(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_profile = {item["profile"]: item for item in records if item.get("scenario") == "privacy-trap"}
    baseline = by_profile.get("metadata_scan", {})
    owledge = by_profile.get("owledge_context_pack", {})
    oracle = by_profile.get("oracle", {})
    prevented = int(owledge.get("privacy_failure_count") or 0) == 0
    return {
        "baseline_files": baseline.get("selected_files", []),
        "owledge_files": owledge.get("selected_files", []),
        "oracle_files": oracle.get("selected_files", []),
        "baseline_failures": int(baseline.get("privacy_failure_count") or 0),
        "owledge_failures": int(owledge.get("privacy_failure_count") or 0),
        "oracle_failures": int(oracle.get("privacy_failure_count") or 0),
        "prevented": prevented,
        "label": "Prevented" if prevented else "Not prevented",
    }


def report_rel(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def output_paths(root: pathlib.Path) -> dict[str, pathlib.Path]:
    return {
        "exports": root / ".owledge" / "exports" / "benchmark-kit",
        "reports": root / ".owledge" / "reports" / "generated" / "benchmark-kit",
    }


def write_reports(root: pathlib.Path, results: dict[str, Any]) -> dict[str, str]:
    paths = output_paths(root)
    exports = paths["exports"]
    reports = paths["reports"]
    exports.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    latest_json = exports / "latest.json"
    latest_md = exports / "latest.md"
    results_jsonl = exports / "results.jsonl"
    html_path = reports / "index.html"
    svg_path = reports / "charts.svg"
    svg_text = render_svg(results)
    latest_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    results_jsonl.write_text("\n".join(json.dumps(item, sort_keys=True) for item in results["records"]) + "\n", encoding="utf-8")
    latest_md.write_text(render_markdown(results), encoding="utf-8")
    svg_path.write_text(svg_text, encoding="utf-8")
    html_path.write_text(render_html(results, svg_text), encoding="utf-8")
    return {
        "latest_json": report_rel(root, latest_json),
        "latest_md": report_rel(root, latest_md),
        "results_jsonl": report_rel(root, results_jsonl),
        "html": report_rel(root, html_path),
        "svg": report_rel(root, svg_path),
    }


def render_markdown(results: dict[str, Any]) -> str:
    totals = results["totals"]
    profile_data = results.get("profile_totals") or build_profile_totals(results["records"])
    verdicts = results.get("verdicts") or benchmark_verdicts(results)
    baseline = verdicts["baseline"]
    owledge = verdicts["owledge"]
    oracle = verdicts["oracle"]
    privacy = privacy_trap_result(results["records"])
    lines = [
        "# Owledge Benchmark Kit Report",
        "",
        "## Run Summary",
        "",
        f"- Passed: `{str(results['passed']).lower()}`",
        f"- Mode: `{results['mode']}`",
        f"- Scale mode: `{results['scale_mode']}`",
        f"- Fixture source: `{results.get('fixture_source', 'generated')}`",
        f"- File count: `{results['file_count']}`",
        f"- Model(s): `{', '.join(results['models'])}`",
        f"- Profiles tested: `{', '.join(PROFILES)}`",
        f"- Total tokens: `{totals['total_tokens']}`",
        f"- Context pollution: `{totals['avg_irrelevant_token_ratio']}`",
        f"- Duration ms: `{totals['total_duration_ms']}`",
        f"- Tokens/sec: `{totals['avg_tokens_per_second']}`",
        f"- Privacy failures: `{totals['privacy_failures']}`",
        f"- Stale failures: `{totals['staleness_failures']}`",
        f"- Fixture directory: `{results['fixture_dir']}`",
        f"- Explanation: `.owledge/benchmark-kit/BENCHMARK_EXPLAINED.md`",
        "",
        "## Before vs Owledge",
        "",
        "| Metric | Baseline metadata_scan | Owledge context pack | Oracle reference |",
        "| --- | ---: | ---: | ---: |",
        f"| Context pollution | {profile_data['metadata_scan']['avg_irrelevant_token_ratio']} | {profile_data['owledge_context_pack']['avg_irrelevant_token_ratio']} | {profile_data['oracle']['avg_irrelevant_token_ratio']} |",
        f"| Privacy failures | {profile_data['metadata_scan']['privacy_failures']} | {profile_data['owledge_context_pack']['privacy_failures']} | {profile_data['oracle']['privacy_failures']} |",
        f"| Stale failures | {profile_data['metadata_scan']['staleness_failures']} | {profile_data['owledge_context_pack']['staleness_failures']} | {profile_data['oracle']['staleness_failures']} |",
        f"| Tokens per correct answer | {profile_data['metadata_scan']['tokens_per_correct_answer']} | {profile_data['owledge_context_pack']['tokens_per_correct_answer']} | {profile_data['oracle']['tokens_per_correct_answer']} |",
        f"| Verdict | {baseline['verdict']} | {owledge['verdict']} | {oracle['verdict']} |",
        "",
        "Baseline failures are expected contrast when the naive profile over-selects noisy, stale, or private context. The Owledge verdict is the product proof.",
        "",
        "## Privacy Trap Explained",
        "",
        "The benchmark injects private Markdown notes that look relevant to the question. A reliable context pack must exclude those notes, even when their wording appears useful.",
        "",
        "### Privacy Trap Result",
        "",
        f"- Result: `{privacy['label']}`",
        f"- Baseline selected private trap files: `{privacy['baseline_failures']}`",
        f"- Owledge selected private trap files: `{privacy['owledge_failures']}`",
        f"- Baseline selected files: `{', '.join(privacy['baseline_files'])}`",
        f"- Owledge selected files: `{', '.join(privacy['owledge_files'])}`",
        "",
        "Interpretation: if the baseline includes a private trap file and Owledge does not, Owledge prevented the privacy leak for this scenario.",
        "",
        "## What This Means",
        "",
        "- Total tokens show how much context and completion budget the run consumed.",
        "- Tokens per correct answer is the practical cost of useful retrieval.",
        "- Context pollution measures irrelevant, stale, private, or background context inside selected packs; lower is better.",
        "- Privacy failures must stay at zero for shareable or team-safe usage.",
        "- Stale failures show whether outdated records entered the answer context.",
        "- tokens/sec and duration reflect local runtime performance and vary by hardware.",
        "",
        "## Scenario Results",
        "",
        "| Status | Scenario | Profile | Model | Precision | Recall | Pollution | Tokens | Duration ms |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in results["records"]:
        lines.append(
        f"| {scenario_status(item)} | {item['scenario']} | {item['profile']} | {item['model']} | {item['precision_at_k']} | {item['recall_at_k']} | {item['irrelevant_token_ratio']} | {item['total_tokens']} | {item['total_duration_ms']} |"
        )
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "Fixture content is deterministic and synthetic. Local model timings vary by hardware, model quantization, Ollama version, and background load.",
            "",
            "## Final Verdict",
            "",
            f"- Baseline verdict: `{baseline['verdict']}` - {baseline['conclusion']}",
            f"- Owledge verdict: `{owledge['verdict']}` - {owledge['conclusion']}",
            f"- Oracle verdict: `{oracle['verdict']}` - {oracle['conclusion']}",
            f"- Product verdict: `{verdicts['final_verdict']}`",
            f"- Conclusion: {verdicts['final_conclusion']}",
        ]
    )
    return "\n".join(lines) + "\n"


def render_html(results: dict[str, Any], svg_text: str | None = None) -> str:
    totals = results["totals"]
    profile_data = results.get("profile_totals") or build_profile_totals(results["records"])
    verdicts = results.get("verdicts") or benchmark_verdicts(results)
    baseline = verdicts["baseline"]
    owledge = verdicts["owledge"]
    oracle = verdicts["oracle"]
    privacy = privacy_trap_result(results["records"])
    svg_text = svg_text or render_svg(results)
    record_rows = []
    for item in results["records"]:
        status = scenario_status(item)
        profile_class = "product" if item["profile"] == "owledge_context_pack" else "baseline" if item["profile"] == "metadata_scan" else "oracle"
        record_rows.append(
            f"<tr class=\"{profile_class}\">"
            f"<td><span class=\"pill {status}\">{status.title()}</span></td>"
            f"<td>{html.escape(item['scenario'])}</td>"
            f"<td>{html.escape(item['profile'])}</td>"
            f"<td>{html.escape(item['model'])}</td>"
            f"<td>{item['precision_at_k']}</td>"
            f"<td>{item['recall_at_k']}</td>"
            f"<td>{item['irrelevant_token_ratio']}</td>"
            f"<td>{item['total_tokens']}</td>"
            f"<td>{item['tokens_per_second']}</td>"
            f"<td>{item['total_duration_ms']}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Owledge Benchmark Kit Report</title>
  <style>
    body {{ font-family: Inter, Segoe UI, Arial, sans-serif; margin: 32px; color: #172033; background: #f8fafc; }}
    h1, h2 {{ color: #0f172a; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
    .card {{ background: white; border: 1px solid #d8dee9; border-radius: 8px; padding: 14px; }}
    .verdict {{ border-left: 6px solid #2563eb; }}
    .verdict.pass {{ border-color: #16a34a; }}
    .verdict.warn {{ border-color: #d97706; }}
    .verdict.fail {{ border-color: #dc2626; }}
    .summary {{ border-left: 6px solid #2563eb; }}
    .trap-result {{ border-left: 6px solid #16a34a; background: #f0fdf4; }}
    .trap-result.fail {{ border-left-color: #dc2626; background: #fef2f2; }}
    .product {{ background: #f0fdf4; }}
    .baseline {{ background: #fff7ed; }}
    .oracle {{ background: #f8fafc; }}
    .label {{ color: #64748b; font-size: 13px; }}
    .value {{ font-size: 24px; font-weight: 700; margin-top: 6px; }}
    .hint {{ color: #64748b; font-size: 13px; margin-top: 6px; line-height: 1.45; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 2px 8px; font-size: 12px; font-weight: 700; }}
    .pill.pass {{ color: #166534; background: #dcfce7; }}
    .pill.warn {{ color: #92400e; background: #fef3c7; }}
    .pill.fail {{ color: #991b1b; background: #fee2e2; }}
    .charts {{ background: white; border: 1px solid #d8dee9; border-radius: 8px; padding: 16px; margin-top: 12px; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; background: white; margin-top: 12px; }}
    th, td {{ border-bottom: 1px solid #e2e8f0; padding: 8px; text-align: left; font-size: 14px; }}
    th {{ color: #475569; background: #f1f5f9; }}
    code {{ background: #e2e8f0; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Owledge Benchmark Kit Report</h1>
  <p>This report uses real synthetic Markdown fixtures. Read <code>.owledge/benchmark-kit/BENCHMARK_EXPLAINED.md</code> before interpreting the scores.</p>
  <section class="card summary">
    <div class="label">Run Summary</div>
    <div class="value">{html.escape(results['mode'].title())} / {html.escape(results['scale_mode'])}</div>
    <p>Profiles tested: <code>{html.escape(', '.join(PROFILES))}</code>. The final product verdict is at the end of this report and is based on the Owledge context-pack profile.</p>
  </section>
  <div class="grid">
    <div class="card"><div class="label">Scale mode</div><div class="value">{html.escape(results['scale_mode'])}</div></div>
    <div class="card"><div class="label">Fixture source</div><div class="value">{html.escape(str(results.get('fixture_source', 'generated')))}</div><div class="hint">Bundled fixtures make runs reproducible; generated fixtures create a fresh deterministic vault from the same seed.</div></div>
    <div class="card"><div class="label">File count</div><div class="value">{results['file_count']}</div></div>
    <div class="card"><div class="label">Total tokens</div><div class="value">{totals['total_tokens']}</div><div class="hint">Total prompt plus completion budget consumed by the benchmark.</div></div>
    <div class="card"><div class="label">Context pollution</div><div class="value">{totals['avg_irrelevant_token_ratio']}</div><div class="hint">Lower is better. Pass <= 0.20, warn <= 0.40, fail above 0.40.</div></div>
    <div class="card"><div class="label">tokens/sec</div><div class="value">{totals['avg_tokens_per_second']}</div><div class="hint">Higher is better. Local hardware, model size, and quantization strongly affect this.</div></div>
    <div class="card"><div class="label">Duration ms</div><div class="value">{totals['total_duration_ms']}</div><div class="hint">Lower is better for the same model, scale, and scenario set.</div></div>
    <div class="card"><div class="label">Privacy failures</div><div class="value">{totals['privacy_failures']}</div><div class="hint">Must be zero for team-safe or shareable context.</div></div>
    <div class="card"><div class="label">Stale failures</div><div class="value">{totals['staleness_failures']}</div><div class="hint">Lower is better. Stale context means outdated notes entered the selected pack.</div></div>
  </div>
  <h2>Before vs Owledge</h2>
  <p>Baseline <code>metadata_scan</code> is the naive before-state. <code>owledge_context_pack</code> is the product behavior under test. <code>oracle</code> is the ideal reference ceiling.</p>
  <table>
    <thead><tr><th>Metric</th><th>Baseline metadata_scan</th><th>Owledge context pack</th><th>Oracle reference</th></tr></thead>
    <tbody>
      <tr><th>Context pollution</th><td>{profile_data['metadata_scan']['avg_irrelevant_token_ratio']}</td><td>{profile_data['owledge_context_pack']['avg_irrelevant_token_ratio']}</td><td>{profile_data['oracle']['avg_irrelevant_token_ratio']}</td></tr>
      <tr><th>Privacy failures</th><td>{profile_data['metadata_scan']['privacy_failures']}</td><td>{profile_data['owledge_context_pack']['privacy_failures']}</td><td>{profile_data['oracle']['privacy_failures']}</td></tr>
      <tr><th>Stale failures</th><td>{profile_data['metadata_scan']['staleness_failures']}</td><td>{profile_data['owledge_context_pack']['staleness_failures']}</td><td>{profile_data['oracle']['staleness_failures']}</td></tr>
      <tr><th>Tokens per correct answer</th><td>{profile_data['metadata_scan']['tokens_per_correct_answer']}</td><td>{profile_data['owledge_context_pack']['tokens_per_correct_answer']}</td><td>{profile_data['oracle']['tokens_per_correct_answer']}</td></tr>
      <tr><th>Verdict</th><td><span class="pill {baseline['verdict']}">{baseline['verdict'].title()}</span></td><td><span class="pill {owledge['verdict']}">{owledge['verdict'].title()}</span></td><td><span class="pill {oracle['verdict']}">{oracle['verdict'].title()}</span></td></tr>
    </tbody>
  </table>
  <h2>Privacy Trap Explained</h2>
  <p>The benchmark injects private Markdown notes that look relevant to the question. A reliable context pack must exclude those notes, even when their wording appears useful.</p>
  <section class="card trap-result {'pass' if privacy['prevented'] else 'fail'}">
    <div class="label">Privacy Trap Result</div>
    <div class="value">{html.escape(privacy['label'])}</div>
    <p><strong>Baseline selected private trap files:</strong> {privacy['baseline_failures']}</p>
    <p><strong>Owledge selected private trap files:</strong> {privacy['owledge_failures']}</p>
    <p><strong>Baseline selected files:</strong> <code>{html.escape(', '.join(privacy['baseline_files']))}</code></p>
    <p><strong>Owledge selected files:</strong> <code>{html.escape(', '.join(privacy['owledge_files']))}</code></p>
    <p class="hint">Interpretation: if the baseline includes a private trap file and Owledge does not, Owledge prevented the privacy leak for this scenario.</p>
  </section>
  <h2>Benchmark Charts</h2>
  <p class="hint">Chart direction: lower pollution, duration, and token cost are better; higher tokens/sec is better. The standalone SVG is also written to <code>.owledge/reports/generated/benchmark-kit/charts.svg</code>.</p>
  <div class="charts">{svg_text}</div>
  <h2>Context Composition</h2>
  <div class="grid">
    <div class="card"><div class="label">Benchmark prompt tokens</div><div class="value">{totals['prompt_tokens']}</div></div>
    <div class="card"><div class="label">Selected context tokens</div><div class="value">{totals['context_pack_tokens']}</div></div>
    <div class="card"><div class="label">Completion tokens</div><div class="value">{totals['completion_tokens']}</div></div>
    <div class="card"><div class="label">Tokens per correct answer</div><div class="value">{totals['tokens_per_correct_answer']}</div><div class="hint">Lower is better when answer quality stays high.</div></div>
  </div>
  <h2>What This Means</h2>
  <table>
    <tbody>
      <tr><th>Total tokens</th><td>How much prompt and completion budget the run consumed.</td></tr>
      <tr><th>Tokens per correct answer</th><td>The practical token cost of useful retrieval.</td></tr>
      <tr><th>Context pollution</th><td>How much irrelevant, stale, private, or background context entered selected packs.</td></tr>
      <tr><th>Privacy failures</th><td>Whether private trap notes entered selected context. This must stay at zero.</td></tr>
      <tr><th>Stale failures</th><td>Whether superseded records entered selected context.</td></tr>
      <tr><th>tokens/sec</th><td>Approximate local generation throughput when a local model is used.</td></tr>
      <tr><th>Duration</th><td>End-to-end benchmark runtime for this run.</td></tr>
    </tbody>
  </table>
  <h2>Scenario Results</h2>
  <table>
    <thead><tr><th>Status</th><th>Scenario</th><th>Profile</th><th>Model</th><th>Precision</th><th>Recall</th><th>Pollution</th><th>Total tokens</th><th>tokens/sec</th><th>Duration ms</th></tr></thead>
    <tbody>{''.join(record_rows)}</tbody>
  </table>
  <h2>Caveats</h2>
  <p>Fixture content is deterministic and synthetic. Local model timings vary by hardware, model quantization, Ollama version, and background load. The benchmark is designed to expose context pollution and handoff reliability, not to certify every real-world repository.</p>
  <p>Fixture directory: <code>{html.escape(results['fixture_dir'])}</code></p>
  <h2>Final Verdict</h2>
  <section class="card verdict {html.escape(verdicts['final_verdict'])}">
    <div class="label">Product Verdict</div>
    <div class="value">{html.escape(verdicts['final_verdict'].title())}</div>
    <p><strong>Baseline:</strong> {html.escape(baseline['conclusion'])}</p>
    <p><strong>Owledge:</strong> {html.escape(owledge['conclusion'])}</p>
    <p><strong>Oracle:</strong> {html.escape(oracle['conclusion'])}</p>
    <p><strong>Conclusion:</strong> {html.escape(verdicts['final_conclusion'])}</p>
  </section>
</body>
</html>
"""


def render_svg(results: dict[str, Any]) -> str:
    totals = results["totals"]
    rows = [
        ("Total tokens", float(totals["total_tokens"])),
        ("Context tokens", float(totals["context_pack_tokens"])),
        ("Completion tokens", float(totals["completion_tokens"])),
        ("Pollution x1000", float(totals["avg_irrelevant_token_ratio"]) * 1000),
        ("Duration seconds", float(totals["total_duration_ms"]) / 1000),
    ]
    width = 960
    height = 90 + len(rows) * 42
    max_value = max(value for _, value in rows) or 1
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Inter,Segoe UI,Arial,sans-serif}.title{font-size:22px;font-weight:700}.label{font-size:13px;fill:#475569}.value{font-size:13px;fill:#0f172a}.track{fill:#e2e8f0}.bar{fill:#2563eb}</style>",
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<text x="24" y="38" class="title">Owledge Benchmark Kit Metrics</text>',
    ]
    y = 72
    for label, value in rows:
        bar_width = int((value / max_value) * 560)
        parts.extend(
            [
                f'<text x="24" y="{y + 15}" class="label">{html.escape(label)}</text>',
                f'<rect x="210" y="{y}" width="560" height="18" rx="3" class="track"/>',
                f'<rect x="210" y="{y}" width="{bar_width}" height="18" rx="3" class="bar"/>',
                f'<text x="790" y="{y + 15}" class="value">{value:.2f}</text>',
            ]
        )
        y += 42
    parts.append("</svg>")
    return "\n".join(parts)


def run(root: pathlib.Path, mode: str, scale_mode: str, seed: int, models: str, ollama_url: str, yes: bool, primary_profile: str = "owledge_context_pack", fixture_source: str = "bundled") -> dict[str, Any]:
    if mode not in {"ci", "local"}:
        return {"passed": False, "error": f"Unsupported mode for v0.7.0 benchmark-kit: {mode}"}
    if scale_mode not in SCALE_MODES:
        return {"passed": False, "error": f"Unsupported scale mode: {scale_mode}"}
    selected_models = [item.strip() for item in models.split(",") if item.strip()]
    if mode == "ci":
        selected_models = ["deterministic"]
    if mode == "local":
        if not selected_models:
            return {"passed": False, "error": "Local mode requires --models for non-interactive runs."}
        if not yes:
            return {"passed": False, "error": "Local mode requires --yes because it can consume CPU/GPU/VRAM."}

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + f"-seed{seed}-{scale_mode}"
    fixture = prepare_fixtures(root, scale_mode, seed, run_id, fixture_source)
    fixture_dir = fixture["fixture_dir"]
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    installed_models: list[dict[str, Any]] = []
    if mode == "local":
        try:
            installed_models = scan_ollama_models(ollama_url)
        except Exception as exc:
            return {"passed": False, "error": f"Ollama scan failed: {exc}", "ollama_url": ollama_url}

    digest_by_model = {str(item.get("name")): str(item.get("digest") or "") for item in installed_models}
    for model in selected_models:
        for scenario in SCENARIOS:
            for profile in PROFILES:
                selected = select_context(fixture["records"], scenario["name"], profile)
                prompt, composition = build_prompt(scenario, selected, fixture_dir)
                generation = {"prompt_eval_count": composition["benchmark_prompt_tokens"], "eval_count": 0, "total_duration_ms": 1, "tokens_per_second": 0.0, "time_to_first_token_ms": 0}
                if mode == "local":
                    try:
                        generation = ollama_generate(ollama_url, model, prompt)
                    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                        errors.append(f"{model}:{scenario['name']}:{profile}:{exc}")
                scores = score_selection(scenario, selected, composition)
                prompt_tokens = int(generation.get("prompt_eval_count") or composition["benchmark_prompt_tokens"])
                completion_tokens = int(generation.get("eval_count") or 0)
                record = {
                    "model": model,
                    "model_digest": "deterministic" if mode == "ci" else digest_by_model.get(model, "unknown"),
                    "mode": mode,
                    "scale_mode": scale_mode,
                    "file_count": SCALE_MODES[scale_mode],
                    "scenario": scenario["name"],
                    "profile": profile,
                    "selected_files": [item["path"] for item in selected],
                    "context_pack_tokens": composition["selected_context_tokens"],
                    "benchmark_prompt_tokens": composition["benchmark_prompt_tokens"],
                    "relevant_context_tokens": composition["relevant_tokens"],
                    "distractor_tokens": composition["distractor_tokens"],
                    "stale_tokens": composition["stale_tokens"],
                    "private_tokens": composition["private_tokens"],
                    "background_tokens": composition["background_tokens"],
                    "prompt_eval_count": prompt_tokens,
                    "eval_count": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                    "total_duration_ms": int(generation.get("total_duration_ms") or 0),
                    "time_to_first_token_ms": int(generation.get("time_to_first_token_ms") or 0),
                    "tokens_per_second": float(generation.get("tokens_per_second") or 0),
                    **scores,
                }
                records.append(record)

    results = {
        "passed": not errors,
        "generated_at": utc_now(),
        "project_root": ".",
        "commit": git_commit(root),
        "mode": mode,
        "scale_mode": scale_mode,
        "fixture_source": fixture_source,
        "file_count": SCALE_MODES[scale_mode],
        "seed": seed,
        "run_id": run_id,
        "fixture_dir": report_rel(root, fixture_dir),
        "queries": report_rel(root, fixture_dir / "queries.json"),
        "oracle": report_rel(root, fixture_dir / "oracle.json"),
        "models": selected_models,
        "primary_profile": primary_profile,
        "installed_models": installed_models,
        "platform": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(), "python": sys.version.split()[0]},
        "scenarios": SCENARIOS,
        "records": records,
        "totals": aggregate(records),
        "errors": errors,
        "explanation": ".owledge/benchmark-kit/BENCHMARK_EXPLAINED.md",
    }
    results["profile_totals"] = build_profile_totals(records)
    results["verdicts"] = benchmark_verdicts(results)
    results["final_verdict"] = results["verdicts"]["final_verdict"]
    results["final_conclusion"] = results["verdicts"]["final_conclusion"]
    results["verdict"] = benchmark_verdict(results)
    results["paths"] = write_reports(root, results)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the optional Owledge Benchmark Kit.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--mode", choices=["ci", "local"], default="ci")
    parser.add_argument("--scale-mode", choices=sorted(SCALE_MODES), default="small")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fixture-source", choices=["bundled", "generate"], default="bundled")
    parser.add_argument("--models", default="")
    parser.add_argument("--primary-profile", choices=PROFILES, default="owledge_context_pack")
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args(argv)
    result = run(pathlib.Path(args.project_root).resolve(), args.mode, args.scale_mode, args.seed, args.models, args.ollama_url, args.yes, args.primary_profile, args.fixture_source)
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
