#!/usr/bin/env python
"""Agent Memory Kit markdown-core tools plus optional control-plane adapter.

This module intentionally uses only the Python standard library so the kit can
bootstrap on macOS, Linux, and Windows without installing dependencies. It provides:

- Markdown frontmatter validation, memory indexing, context packs, neutral RAG
  export, LightRAG export, GraphRAG export, parallel finding, and compaction.
- SQLite WAL control-plane schema and lifecycle helpers.
- A small HTTP API for LAN/remote agents.
- Legacy contract checks, promotion, metrics, and a 50-agent concurrency
  simulation for optional runtime adapters.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import datetime as dt
import hashlib
import http.server
import html
import json
import math
import os
import pathlib
import re
import secrets
import shutil
import sqlite3
import sys
import tempfile
import threading
import time
import urllib.parse
import uuid
from typing import Any


UTC = getattr(dt, "UTC", dt.timezone.utc)


DEFAULTS = {
    "heartbeat_interval_seconds": 60,
    "lease_ttl_seconds": 900,
    "max_parallel_agents": 50,
    "max_parallel_per_project": 8,
    "sqlite_busy_timeout_ms": 30000,
    "worker_context_budget_chars": 24000,
    "planner_context_budget_chars": 40000,
}

TASK_STATUSES = {
    "backlog",
    "ready",
    "claimed",
    "in_progress",
    "blocked",
    "review",
    "qa",
    "done",
    "rejected",
    "archived",
}

MEMORY_STATUS_VALUES = {
    "draft",
    "active",
    "reviewed",
    "promoted",
    "superseded",
    "archived",
}

AGENT_ROLES = {
    "orchestrator",
    "planner",
    "strategic-reviewer",
    "worker",
    "qa-agent",
    "memory-curator",
    "observer",
}

REQUIRED_DIRS = [
    "agent-memory/templates",
    "agent-memory/schemas",
    "agent-memory/canonical",
    "agent-memory/compiled",
    "agent-memory/patterns",
    "agent-memory/lessons",
    "agent-memory/ideas",
    "agent-memory/pi-agent",
    "agent-memory/pi-agent/reports",
    "agent-memory/pi-agent/parallels",
    "agent-memory/pi-agent/trends",
    "agent-memory/pi-agent/recurring-errors",
    "agent-memory/pi-agent/concepts",
    "agent-memory/pi-agent/red-team",
    "agent-memory/pi-agent/evaluations",
    "agent-memory/pi-agent/scorecards",
    "agent-memory/pi-agent/indexes",
    "agent-memory/sessions",
    "agent-memory/decisions",
    "agent-memory/evidence",
    "agent-memory/evidence/promotions",
    "agent-memory/handoffs",
    "agent-memory/indexes",
    "agent-memory/exports/rag",
    "agent-memory/exports/lightrag",
    "agent-memory/exports/graphrag",
    "global-memory/preferences",
    "global-memory/goals",
    "global-memory/daily",
    "global-memory/tasks",
    "global-memory/ideas",
    "global-memory/research",
    "global-memory/patterns",
    "global-memory/coach",
    "global-memory/indexes",
    "global-memory/exports/rag",
    "global-memory/exports/lightrag",
    "global-memory/exports/graphrag",
    "tools",
    "docs",
    "docs/archive",
    "benchmarks",
    "benchmarks/results",
    "assets",
    ".github",
    ".github/ISSUE_TEMPLATE",
    ".github/workflows",
    "skills/agent-memory-principles",
    "skills/agent-memory-runtime-bridge",
    "skills/render-memory-report",
    "skills/review-evaluation-workflow",
    "skills/personal-pi-agent",
    "plugins/agent-memory-cowork",
    "plugins/agent-memory-cowork/.claude-plugin",
    "plugins/agent-memory-cowork/.codex-plugin",
    "plugins/agent-memory-cowork/hooks",
    "plugins/agent-memory-cowork/skills/agent-memory-principles",
    "plugins/agent-memory-cowork/skills/agent-memory-runtime-bridge",
    "plugins/agent-memory-cowork/skills/render-memory-report",
    "plugins/agent-memory-cowork/skills/review-evaluation-workflow",
    "plugins/agent-memory-cowork/agents",
    "plugins/agent-memory-cowork/commands",
    "plugins/agent-memory-cowork/scripts",
    "plugins/agent-memory-cowork/tests/fixtures",
    "plugins/pi-agent-workspace",
    "plugins/pi-agent-workspace/.claude-plugin",
    "plugins/pi-agent-workspace/.codex-plugin",
    "plugins/pi-agent-workspace/agents",
    "plugins/pi-agent-workspace/commands",
    "plugins/pi-agent-workspace/skills/pi-agent-workspace-quality",
    "plugins/pi-agent-workspace/skills/pi-agent-global-intelligence",
    "plugins/pi-agent-workspace/skills/pi-agent-red-team-evaluator",
    "plugins/pi-agent-workspace/skills/personal-pi-agent",
]

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "VERSION",
    "CHANGELOG.md",
    "SECURITY.md",
    "PRIVACY.md",
    "ROADMAP.md",
    "DESIGN.md",
    "REPORT_DESIGN_SELECTOR.html",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    "USER_CONTEXT.template.md",
    "docs/README.md",
    "docs/quickstart.md",
    "docs/agent-first-run-setup.md",
    "docs/owledge-vs-agent-methods.md",
    "docs/global-user-knowledge-layer.md",
    "docs/agentic-memory-architecture.md",
    "docs/project-folder-only-quickstart.md",
    "docs/cross-platform-lean-setup.md",
    "docs/agent-integration-guide.md",
    "docs/superpowers-integration.md",
    "docs/harness-plugin-matrix.md",
    "docs/mvp-plan-example.md",
    "docs/team-long-running-project-guide.md",
    "docs/performance-scale-notes.md",
    "docs/html-reports.md",
    "docs/project-snapshot-kit.md",
    "docs/incremental-index-workflow.md",
    "docs/reusable-review-evaluation-templates.md",
    "docs/archive/README.md",
    "docs/archive/publishing.md",
    "docs/archive/finalization-report.md",
    "docs/archive/compliance-implementation-plan.md",
    "docs/archive/compliance-roadmap.md",
    "docs/archive/dashboard-extension-plan.md",
    "docs/archive/incremental-index-finalization-sprint.md",
    "docs/archive/review-workflow-finalization-sprint.md",
    "docs/archive/ai-workos-vault-merge-evaluation.md",
    "docs/archive/ai-workos-vault-adapter-plan.md",
    "docs/archive/pi-agent-adapter-plan.md",
    "docs/archive/pi-agent-global-intelligence-plan.md",
    "docs/archive/pi-agent-red-team-evaluation-plan.md",
    "PROJECT_CONTEXT.template.md",
    "AGENTS.template.md",
    "CLAUDE.template.md",
    "CLAUDE.md",
    ".gitignore",
    "agent-memory/README.md",
    "agent-memory/templates/agent-session-template.md",
    "agent-memory/templates/orchestration-delta-template.md",
    "agent-memory/templates/root-review-template.md",
    "agent-memory/templates/adr-template.md",
    "agent-memory/templates/canonical-memory-template.md",
    "agent-memory/templates/compiled-memory-template.md",
    "agent-memory/templates/pattern-card-template.md",
    "agent-memory/templates/shared-lesson-template.md",
    "agent-memory/templates/idea-card-template.md",
    "agent-memory/templates/user-context-template.md",
    "agent-memory/templates/preference-card-template.md",
    "agent-memory/templates/goal-card-template.md",
    "agent-memory/templates/daily-note-template.md",
    "agent-memory/templates/personal-task-template.md",
    "agent-memory/templates/research-card-template.md",
    "agent-memory/templates/personal-pattern-template.md",
    "agent-memory/templates/coach-report-template.md",
    "agent-memory/templates/onboarding-profile-template.md",
    "agent-memory/ideas/pi-agent-global-intelligence.md",
    "agent-memory/templates/pi-intelligence-report-template.md",
    "agent-memory/templates/pi-parallel-report-template.md",
    "agent-memory/templates/pi-recurring-error-template.md",
    "agent-memory/templates/pi-central-project-template.md",
    "agent-memory/templates/evaluation-framework-template.md",
    "agent-memory/templates/pi-red-team-evaluation-template.md",
    "agent-memory/templates/agent-quality-scorecard-template.md",
    "agent-memory/templates/multi-perspective-red-team-review-template.md",
    "agent-memory/templates/expert-lens-evaluation-template.md",
    "agent-memory/templates/scenario-simulation-evaluation-template.md",
    "agent-memory/templates/evaluation-persona-pack-template.md",
    "agent-memory/templates/review-to-task-plan-template.md",
    "agent-memory/templates/project-index-template.md",
    "agent-memory/templates/evidence-template.md",
    "agent-memory/templates/handoff-template.md",
    "agent-memory/templates/qa-gate-template.md",
    "agent-memory/templates/rag-export-manifest-template.json",
    "agent-memory/templates/epic-overview-template.md",
    "agent-memory/templates/workpackage-template.md",
    "agent-memory/templates/techspec-template.md",
    "agent-memory/templates/task-card-template.md",
    "agent-memory/templates/qa-spec-template.md",
    "agent-memory/templates/gate-report-template.md",
    "agent-memory/templates/handoff-packet-template.md",
    "agent-memory/templates/context-pack-template.md",
    "agent-memory/schemas/tenant.schema.json",
    "agent-memory/schemas/agent.schema.json",
    "agent-memory/schemas/epic.schema.json",
    "agent-memory/schemas/workpackage.schema.json",
    "agent-memory/schemas/task-card.schema.json",
    "agent-memory/schemas/qa-spec.schema.json",
    "agent-memory/schemas/gate-report.schema.json",
    "agent-memory/schemas/context-pack.schema.json",
    "agent-memory/schemas/lightrag-export.schema.json",
    "agent-memory/schemas/frontmatter.schema.json",
    "agent-memory/schemas/edge.schema.json",
    "agent-memory/schemas/canonical-memory.schema.json",
    "agent-memory/schemas/compiled-memory.schema.json",
    "agent-memory/schemas/pattern-card.schema.json",
    "agent-memory/schemas/shared-lesson.schema.json",
    "agent-memory/schemas/rag-document.schema.json",
    "agent-memory/schemas/graphrag-node.schema.json",
    "agent-memory/schemas/graphrag-edge.schema.json",
    "agent-memory/schemas/global-user-memory.schema.json",
    "tools/owledge.py",
    "tools/agent_memory_cli.py",
    "tools/build_project_folder_kit.py",
    "tools/build_kb_module.py",
    "benchmarks/README.md",
    "benchmarks/results/README.md",
    "benchmarks/run_benchmarks.py",
    "assets/README.md",
    "assets/social-preview.svg",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/ci.yml",
    ".github/workflows/docs.yml",
    "plugins/agent-memory-cowork/tests/fixtures/session-start.json",
    "plugins/agent-memory-cowork/tests/fixtures/user-prompt.json",
    "plugins/agent-memory-cowork/tests/fixtures/post-tool-use.json",
    "plugins/agent-memory-cowork/tests/fixtures/stop.json",
    "tests/fixtures/retrieval-queries.json",
    "tests/fixtures/retrieval-corpus/agent-memory/canonical/memory-lifecycle-policy.md",
    "tests/fixtures/retrieval-corpus/agent-memory/canonical/context-pack-objective.md",
    "tests/fixtures/retrieval-corpus/agent-memory/canonical/stale-research-signal.md",
    "tests/fixtures/retrieval-corpus/agent-memory/compiled/context-pack-scoring.md",
    "tests/fixtures/retrieval-corpus/agent-memory/compiled/promotion-audit.md",
    "tests/fixtures/retrieval-corpus/agent-memory/patterns/progressive-disclosure-runtime.md",
    "tests/fixtures/retrieval-corpus/agent-memory/patterns/cross-project-parallel.md",
    "tests/fixtures/retrieval-corpus/agent-memory/lessons/privacy-export-gate.md",
    "tests/fixtures/retrieval-corpus/agent-memory/lessons/runtime-rag-safety.md",
    "tests/fixtures/retrieval-corpus/agent-memory/decisions/markdown-source-of-truth.md",
    "tests/fixtures/retrieval-corpus/agent-memory/compiled/stale-conflict-review.md",
    "skills/agent-memory-principles/SKILL.md",
    "skills/agent-memory-principles/references/principles.md",
    "skills/agent-memory-principles/references/agent-rules.md",
    "skills/agent-memory-principles/references/mapping-contract.md",
    "skills/agent-memory-principles/references/security-rules.md",
    "skills/agent-memory-runtime-bridge/SKILL.md",
    "skills/bootstrap-agent-memory/SKILL.md",
    "skills/pi-agent-workspace-quality/SKILL.md",
    "skills/pi-agent-global-intelligence/SKILL.md",
    "skills/pi-agent-red-team-evaluator/SKILL.md",
    "skills/personal-pi-agent/SKILL.md",
    "skills/render-memory-report/SKILL.md",
    "skills/review-evaluation-workflow/SKILL.md",
    "skills/render-memory-report/references/decision-report.md",
    "skills/render-memory-report/references/handoff-report.md",
    "skills/render-memory-report/references/rag-readiness-report.md",
    "skills/render-memory-report/references/agent-activity-report.md",
    "skills/render-memory-report/references/project-dashboard.md",
    "skills/render-memory-report/references/website-ui-report.md",
    "skills/render-memory-report/references/report-design-systems.md",
    "plugins/agent-memory-cowork/.claude-plugin/plugin.json",
    "plugins/agent-memory-cowork/.codex-plugin/plugin.json",
    "plugins/agent-memory-cowork/hooks/hooks.json",
    "plugins/agent-memory-cowork/hooks/hooks.python.json",
    "plugins/agent-memory-cowork/skills/agent-memory-principles/SKILL.md",
    "plugins/agent-memory-cowork/skills/agent-memory-principles/references/principles.md",
    "plugins/agent-memory-cowork/skills/agent-memory-principles/references/agent-rules.md",
    "plugins/agent-memory-cowork/skills/agent-memory-principles/references/mapping-contract.md",
    "plugins/agent-memory-cowork/skills/agent-memory-principles/references/security-rules.md",
    "plugins/agent-memory-cowork/skills/agent-memory-runtime-bridge/SKILL.md",
    "plugins/agent-memory-cowork/skills/bootstrap-agent-memory/SKILL.md",
    "plugins/agent-memory-cowork/skills/render-memory-report/SKILL.md",
    "plugins/agent-memory-cowork/skills/review-evaluation-workflow/SKILL.md",
    "plugins/agent-memory-cowork/skills/render-memory-report/references/decision-report.md",
    "plugins/agent-memory-cowork/skills/render-memory-report/references/handoff-report.md",
    "plugins/agent-memory-cowork/skills/render-memory-report/references/rag-readiness-report.md",
    "plugins/agent-memory-cowork/skills/render-memory-report/references/agent-activity-report.md",
    "plugins/agent-memory-cowork/skills/render-memory-report/references/project-dashboard.md",
    "plugins/agent-memory-cowork/skills/render-memory-report/references/website-ui-report.md",
    "plugins/agent-memory-cowork/skills/render-memory-report/references/report-design-systems.md",
    "plugins/agent-memory-cowork/agents/memory-curator.md",
    "plugins/agent-memory-cowork/commands/memory-init.md",
    "plugins/agent-memory-cowork/commands/memory-status.md",
    "plugins/agent-memory-cowork/commands/memory-doctor.md",
    "plugins/agent-memory-cowork/commands/memory-report.md",
    "plugins/agent-memory-cowork/scripts/capture-claude-event.py",
    "plugins/agent-memory-cowork/scripts/close-runtime-session.py",
    "plugins/agent-memory-cowork/README.md",
    "plugins/agent-memory-cowork/LICENSE",
    "plugins/agent-memory-cowork/VERSION",
    "plugins/agent-memory-cowork/CHANGELOG.md",
    "plugins/pi-agent-workspace/.claude-plugin/plugin.json",
    "plugins/pi-agent-workspace/.codex-plugin/plugin.json",
    "plugins/pi-agent-workspace/README.md",
    "plugins/pi-agent-workspace/agents/pi-workspace-guardian.md",
    "plugins/pi-agent-workspace/agents/pi-global-intelligence.md",
    "plugins/pi-agent-workspace/agents/pi-red-team-evaluator.md",
    "plugins/pi-agent-workspace/commands/pi-workspace-check.md",
    "plugins/pi-agent-workspace/commands/pi-intelligence-report.md",
    "plugins/pi-agent-workspace/commands/pi-redteam-evaluate.md",
    "plugins/pi-agent-workspace/skills/pi-agent-workspace-quality/SKILL.md",
    "plugins/pi-agent-workspace/skills/pi-agent-global-intelligence/SKILL.md",
    "plugins/pi-agent-workspace/skills/pi-agent-red-team-evaluator/SKILL.md",
    "plugins/pi-agent-workspace/skills/personal-pi-agent/SKILL.md",
    "docs/ideation-workflow.md",
    "docs/install-plugin.md",
    "docs/command-reference.md",
]

ADDON_REQUIRED_FILES = [
    "addons/compliance-light/addon.json",
    "addons/compliance-light/README.md",
    "addons/compliance-light/docs/compliance-light.md",
    "addons/compliance-light/templates/processing-activity-template.md",
    "addons/compliance-light/templates/ai-system-template.md",
    "addons/compliance-light/templates/provider-registry-template.md",
    "addons/compliance-light/templates/dpia-trigger-template.md",
    "addons/compliance-light/templates/data-subject-request-template.md",
    "addons/compliance-light/templates/security-incident-template.md",
    "addons/compliance-light/schemas/compliance-record.schema.json",
    "addons/compliance-light/starter/agent-memory/compliance/profile.md",
    "addons/compliance-light/tests/fixtures/minimal-pass/agent-memory/compliance/profile.md",
    "addons/compliance-light/tests/fixtures/minimal-pass/agent-memory/compliance/registers/processing-activity.md",
    "addons/compliance-light/tests/fixtures/minimal-pass/agent-memory/compliance/registers/provider.md",
    "addons/compliance-light/tests/fixtures/minimal-pass/agent-memory/compliance/ai-systems/ai-system.md",
    "addons/compliance-light/tests/fixtures/minimal-pass/agent-memory/compliance/dpia/dpia-trigger.md",
    "addons/compliance-light/tests/fixtures/missing-provider/agent-memory/compliance/profile.md",
    "addons/compliance-light/tests/fixtures/invalid-processing-fields/agent-memory/compliance/profile.md",
    "addons/compliance-light/tests/fixtures/invalid-processing-fields/agent-memory/compliance/registers/processing-activity.md",
    "addons/project-snapshot-kit/addon.json",
    "addons/project-snapshot-kit/README.md",
    "addons/project-snapshot-kit/docs/project-snapshot-kit.md",
    "addons/project-snapshot-kit/starter/agent-memory/project-snapshot/profile.md",
    "addons/project-snapshot-kit/templates/project-story-snapshot-template.md",
    "addons/project-snapshot-kit/templates/project-execution-snapshot-template.md",
    "addons/project-snapshot-kit/templates/project-site-html-template.md",
    "addons/project-snapshot-kit/skills/render-memory-report/references/project-site.md",
    "addons/project-snapshot-kit/skills/render-memory-report/references/execution-dashboard.md",
    "tests/fixtures/compliance-light/expected-installed-delta.txt",
]

CORE_FRONTMATTER_REQUIRED = [
    "memory_id",
    "tenant_id",
    "customer_id",
    "project_id",
    "doc_type",
    "status",
    "visibility",
    "data_class",
    "semantic_title",
    "summary",
    "concept_tags",
    "stack_tags",
    "problem_patterns",
    "architecture_patterns",
    "failure_modes",
    "reusable_lessons",
    "confidence",
    "review_status",
    "sanitization_status",
    "created_at",
    "updated_at",
    "source_hash",
    "edges",
]

GLOBAL_USER_DOC_TYPES = {
    "user_context",
    "preference",
    "goal",
    "daily",
    "personal_task",
    "research",
    "personal_pattern",
    "coach_report",
    "onboarding_profile",
}
EXPORTABLE_DOC_TYPES = {"project_context", "canonical", "compiled", "pattern", "lesson", "adr", "qa", "task", "handoff", "idea"} | GLOBAL_USER_DOC_TYPES
DEFAULT_RAG_DOC_TYPES = {"canonical", "compiled", "pattern", "lesson", "adr", "user_context", "preference", "goal", "research", "personal_pattern"}
RAW_PRIVATE_DOC_TYPES = {"daily", "personal_task", "onboarding_profile"}
CORPUS_TYPES = {"private", "shared"}
VISIBILITY_VALUES = {"private", "tenant", "customer", "shared"}
DATA_CLASS_VALUES = {"public", "internal", "confidential", "personal", "special-category"}
REVIEW_STATUS_VALUES = {"unreviewed", "reviewed", "approved", "rejected"}
SANITIZATION_STATUS_VALUES = {"not_required", "pending", "approved", "rejected"}
SHARED_ALLOWED_DATA_CLASSES = {"public", "internal"}
RAG_REVIEWED_STATUSES = {"reviewed", "promoted"}
RAG_REVIEWED_REVIEW_STATUSES = {"reviewed", "approved"}
RUNTIME_DRAFT_TAG = "runtime-summary"
RETENTION_CLASS_VALUES = {"transient", "short", "standard", "long", "archive", "legal-hold"}
REVIEW_CYCLE_DAYS = {
    "none": 0,
    "weekly": 7,
    "monthly": 30,
    "quarterly": 90,
    "semiannual": 182,
    "annual": 365,
}
RETENTION_DEFAULTS = {
    "session": "short",
    "evidence": "standard",
    "handoff": "standard",
    "qa": "standard",
    "task": "standard",
    "daily": "short",
    "personal_task": "short",
    "onboarding_profile": "long",
    "canonical": "long",
    "compiled": "standard",
    "pattern": "long",
    "lesson": "long",
    "adr": "archive",
    "project_context": "long",
    "user_context": "long",
    "preference": "standard",
    "goal": "standard",
    "research": "standard",
    "personal_pattern": "standard",
    "coach_report": "standard",
    "idea": "standard",
}
COMPLIANCE_PROFILE_REL = "agent-memory/compliance/profile.md"
COMPLIANCE_RECORD_TYPES = {
    "processing_activity",
    "ai_system",
    "provider",
    "dpia_trigger",
    "data_subject_request",
    "security_incident",
}
SECRET_KEY_RE = re.compile(
    r"(secret|token|password|passwd|api[_-]?key|authorization|bearer|credential|private[_-]?key|access[_-]?key|refresh[_-]?token)",
    re.IGNORECASE,
)
SECRET_VALUE_PATTERNS = [
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{8,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{8,}\b"),
    re.compile(r"(?i)\b(api[_-]?key|secret|token|authorization|password)\s*[:=]\s*['\"]?[^'\"\s,;]+"),
]
LARGE_CAPTURE_KEYS = {
    "content",
    "diff",
    "file_content",
    "message",
    "output",
    "prompt",
    "response",
    "stderr",
    "stdout",
    "text",
    "tool_input",
    "tool_output",
    "tool_response",
    "user_prompt",
}
ALLOWLIST_CAPTURE_KEYS = {
    "cwd",
    "event",
    "event_type",
    "hook_event_name",
    "matcher",
    "name",
    "session_id",
    "source",
    "status",
    "timestamp",
    "tool_name",
    "transcript_path",
    "type",
}
EDGE_TYPES = {
    "relates_to",
    "depends_on",
    "supersedes",
    "superseded_by",
    "derived_from",
    "evidence_for",
    "implements",
    "blocks",
    "unblocks",
    "validates",
    "contradicts",
    "similar_to",
    "shared_lesson_for",
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "auf",
    "before",
    "by",
    "can",
    "das",
    "der",
    "die",
    "ein",
    "eine",
    "for",
    "from",
    "in",
    "into",
    "is",
    "mit",
    "of",
    "on",
    "or",
    "should",
    "the",
    "to",
    "und",
    "use",
    "with",
}


def utc_now() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_ts(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def date_state(value: Any, now_ts: float | None = None) -> dict[str, Any]:
    text = str(value or "").strip()
    if not text:
        return {"present": False, "expired": False, "timestamp": 0.0}
    timestamp = parse_ts(text)
    current = now_ts if now_ts is not None else time.time()
    return {"present": True, "expired": bool(timestamp and timestamp <= current), "timestamp": timestamp}


def review_due(meta: dict[str, Any], now_ts: float | None = None) -> dict[str, Any]:
    cycle = str(meta.get("review_cycle") or "none").strip().lower()
    days = REVIEW_CYCLE_DAYS.get(cycle, 0)
    if days <= 0:
        return {"required": False, "due": False, "cycle": cycle, "days": days}
    last_reviewed = parse_ts(str(meta.get("last_reviewed_at") or meta.get("updated_at") or ""))
    if not last_reviewed:
        return {"required": True, "due": True, "cycle": cycle, "days": days, "reason": "missing_last_reviewed_at"}
    current = now_ts if now_ts is not None else time.time()
    due = (current - last_reviewed) >= days * 86400
    return {"required": True, "due": bool(due), "cycle": cycle, "days": days, "last_reviewed_at": meta.get("last_reviewed_at") or meta.get("updated_at")}


def memory_freshness_warnings(meta: dict[str, Any], now_ts: float | None = None) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    for key in ["expires_at", "stale_after", "valid_until"]:
        state = date_state(meta.get(key), now_ts=now_ts)
        if state["present"] and state["expired"]:
            warnings.append({"field": key, "value": meta.get(key), "reason": f"{key}_expired"})
    due = review_due(meta, now_ts=now_ts)
    if due.get("due"):
        warnings.append({"field": "last_reviewed_at", "value": due.get("last_reviewed_at", ""), "reason": due.get("reason", "review_due"), "review_cycle": due.get("cycle")})
    return warnings


def retention_class_for(meta: dict[str, Any]) -> str:
    value = str(meta.get("retention_class") or "").strip()
    if value in RETENTION_CLASS_VALUES:
        return value
    return RETENTION_DEFAULTS.get(str(meta.get("doc_type") or ""), "standard")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_text(path: pathlib.Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    tmp.write_text(text, encoding=encoding)
    os.replace(tmp, path)


def locked_atomic_write_text(path: pathlib.Path, text: str, encoding: str = "utf-8", timeout_seconds: float = 30.0) -> None:
    lock = path.with_name(f".{path.name}.lock")
    with file_lock(lock, timeout_seconds=timeout_seconds):
        atomic_write_text(path, text, encoding=encoding)


def unique_run_id(prefix: str) -> str:
    stamp = dt.datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{stamp}-{os.getpid()}-{secrets.token_hex(4)}"


@contextlib.contextmanager
def file_lock(lock_path: pathlib.Path, timeout_seconds: float = 15.0):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    handle = None
    while True:
        try:
            handle = lock_path.open("x", encoding="utf-8")
            try:
                handle.write(json.dumps({"pid": os.getpid(), "created_at": utc_now()}))
                handle.flush()
            except Exception:
                handle.close()
                with contextlib.suppress(FileNotFoundError):
                    lock_path.unlink()
                raise
            break
        except FileExistsError:
            if time.monotonic() - start > timeout_seconds:
                raise TimeoutError(f"Timed out waiting for lock: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        if handle:
            handle.close()
        with contextlib.suppress(FileNotFoundError):
            lock_path.unlink()


def slugify(value: str, fallback: str = "item") -> str:
    chars = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif char in {"-", "_", ".", ":"}:
            chars.append("-")
        elif char.isspace():
            chars.append("-")
    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:96] or fallback


def yaml_string(value: Any) -> str:
    text = str(value or "")
    text = text.replace("\\", "\\\\").replace('"', '\\"').replace("\r", " ").replace("\n", " ")
    return f'"{text}"'


def project_defaults(root: pathlib.Path) -> dict[str, str]:
    meta = {}
    context = root / "PROJECT_CONTEXT.md"
    if context.exists():
        meta = parse_frontmatter(context.read_text(encoding="utf-8", errors="replace"))
    project_slug = slugify(meta.get("project_id") or meta.get("project") or root.name, "project-local")
    return {
        "tenant_id": str(meta.get("tenant_id") or "tenant-local"),
        "customer_id": str(meta.get("customer_id") or "customer-local"),
        "project_id": str(meta.get("project_id") or project_slug),
    }


def resolve_root(value: str | None) -> pathlib.Path:
    return pathlib.Path(value or os.getcwd()).resolve()


REVIEW_WORKFLOW_TYPES = {
    "multi-perspective-red-team": {
        "template": "multi-perspective-red-team-review-template.md",
        "output_dir": pathlib.Path("agent-memory/pi-agent/red-team"),
        "file_prefix": "multi-perspective-red-team",
        "subject_placeholders": ["PATH_OR_MEMORY_ID"],
        "question_placeholders": ["What should this review prove or disprove?"],
    },
    "expert-lens": {
        "template": "expert-lens-evaluation-template.md",
        "output_dir": pathlib.Path("agent-memory/pi-agent/evaluations"),
        "file_prefix": "expert-lens-evaluation",
        "subject_placeholders": ["PATH_OR_MEMORY_ID"],
        "question_placeholders": [],
    },
    "scenario-simulation": {
        "template": "scenario-simulation-evaluation-template.md",
        "output_dir": pathlib.Path("agent-memory/pi-agent/evaluations"),
        "file_prefix": "scenario-simulation",
        "subject_placeholders": ["PATH_OR_MEMORY_ID"],
        "question_placeholders": [],
    },
    "persona-pack": {
        "template": "evaluation-persona-pack-template.md",
        "output_dir": pathlib.Path("agent-memory/pi-agent/evaluations"),
        "file_prefix": "evaluation-persona-pack",
        "subject_placeholders": [],
        "question_placeholders": [],
    },
    "review-to-task-plan": {
        "template": "review-to-task-plan-template.md",
        "output_dir": pathlib.Path("agent-memory/pi-agent/scorecards"),
        "file_prefix": "review-to-task-plan",
        "subject_placeholders": ["PATH_OR_MEMORY_ID"],
        "question_placeholders": [],
    },
}


def unique_markdown_path(output_dir: pathlib.Path, stem: str) -> pathlib.Path:
    path = output_dir / f"{stem}.md"
    if not path.exists():
        return path
    for index in range(2, 1000):
        candidate = output_dir / f"{stem}-{index}.md"
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Unable to find an unused output path for {stem}.md")


def locked_atomic_create_text(path: pathlib.Path, text: str, encoding: str = "utf-8", timeout_seconds: float = 30.0) -> None:
    lock = path.with_name(f".{path.name}.lock")
    with file_lock(lock, timeout_seconds=timeout_seconds):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {path}")
        atomic_write_text(path, text, encoding=encoding)


def run_review_workflow(
    root: pathlib.Path,
    review_type: str,
    subject: str,
    question: str | None = None,
    slug: str | None = None,
    tenant_id: str | None = None,
    customer_id: str | None = None,
    project_id: str | None = None,
    output_dir: pathlib.Path | None = None,
) -> dict[str, Any]:
    if review_type not in REVIEW_WORKFLOW_TYPES:
        raise ValueError(f"Unsupported review_type: {review_type}")

    config = REVIEW_WORKFLOW_TYPES[review_type]
    defaults = project_defaults(root)
    defaults["tenant_id"] = tenant_id or defaults["tenant_id"]
    defaults["customer_id"] = customer_id or defaults["customer_id"]
    defaults["project_id"] = project_id or defaults["project_id"]

    subject_text = subject.strip().replace("\\", "/")
    if not subject_text:
        raise ValueError("--subject is required")
    question_text = (question or "").strip()
    slug_base = slug or f"{review_type}-{subject_text}"
    artifact_slug = slugify(slug_base, config["file_prefix"])
    unique_slug = unique_run_id(artifact_slug)
    now = utc_now()

    template_path = root / "agent-memory" / "templates" / str(config["template"])
    if not template_path.exists():
        raise FileNotFoundError(f"Missing review workflow template: {template_path}")

    target_dir = output_dir if output_dir else root / config["output_dir"]
    if not target_dir.is_absolute():
        target_dir = root / target_dir
    target_dir = target_dir.resolve()
    if root not in [target_dir, *target_dir.parents]:
        raise ValueError(f"Output directory must be inside project root: {target_dir}")

    text = template_path.read_text(encoding="utf-8")
    replacements = {
        "TENANT_ID": defaults["tenant_id"],
        "CUSTOMER_ID": defaults["customer_id"],
        "PROJECT_ID": defaults["project_id"],
        "SLUG": unique_slug,
        "YYYY-MM-DDT00:00:00Z": now,
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    for placeholder in config["subject_placeholders"]:
        text = text.replace(placeholder, subject_text)
    for placeholder in config["question_placeholders"]:
        text = text.replace(placeholder, question_text or "Define the review question before scoring.")

    subject_path = (root / subject_text).resolve()
    if subject_path.exists() and root in [subject_path, *subject_path.parents] and subject_path.is_file():
        text = text.replace('source_hash: ""', f'source_hash: "{sha256_file(subject_path)}"', 1)

    if review_type == "multi-perspective-red-team" and question_text:
        text = text.replace("| Review question | |", f"| Review question | {question_text} |")
    elif review_type in {"expert-lens", "scenario-simulation"} and question_text:
        text = text.replace("| Evaluation question | |", f"| Evaluation question | {question_text} |")
        text = text.replace("Describe what must be proven under realistic use.", question_text)
    elif review_type == "review-to-task-plan" and question_text:
        text = text.replace("| Recommendation | `block | revise | accept | promote-candidate` |", f"| Recommendation | {question_text} |")
    elif review_type == "persona-pack" and question_text:
        text = text.replace("Pick 3-5 personas that match the artifact under review.", f"{question_text}\n\nPick 3-5 personas that match the artifact under review.")

    subject_title = subject_text if len(subject_text) <= 120 else f"{subject_text[:117]}..."
    title_map = {
        "multi-perspective-red-team": f"Multi-Perspective Red Team Review: {subject_title}",
        "expert-lens": f"Expert Lens Evaluation: {subject_title}",
        "scenario-simulation": f"Scenario Simulation Evaluation: {subject_title}",
        "persona-pack": f"Evaluation Persona Pack: {subject_title}",
        "review-to-task-plan": f"Review To Task Plan: {subject_title}",
    }
    text = re.sub(r'semantic_title: "[^"]+"', f"semantic_title: {yaml_string(title_map[review_type])}", text, count=1)

    output_path = unique_markdown_path(target_dir, f"{config['file_prefix']}-{unique_slug}")
    locked_atomic_create_text(output_path, text, timeout_seconds=60)

    rel_output = str(output_path.relative_to(root)).replace("\\", "/")
    rel_template = str(template_path.relative_to(root)).replace("\\", "/")
    qa_commands = [
        "python -m py_compile tools/owledge.py tools/agent_memory_cli.py",
        "python tools/agent_memory_cli.py --project-root . validate-memory --strict",
        f"python -c \"from pathlib import Path; text=Path('{rel_output}').read_text(encoding='utf-8'); raise SystemExit(1 if any(x in text for x in ['TENANT_ID','CUSTOMER_ID','PROJECT_ID']) else 0)\"",
    ]
    return {
        "output_path": rel_output,
        "review_type": review_type,
        "template_path": rel_template,
        "qa_commands": qa_commands,
    }


def db_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".agent-control" / "agent-memory.sqlite"


def admin_token_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".agent-control" / "secrets" / "admin.token"


def connect(root: pathlib.Path, path: pathlib.Path | None = None) -> sqlite3.Connection:
    db = path or db_path(root)
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db), timeout=DEFAULTS["sqlite_busy_timeout_ms"] / 1000, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute(f"PRAGMA busy_timeout={DEFAULTS['sqlite_busy_timeout_ms']}")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS agents (
          agent_id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          customer_id TEXT,
          project_id TEXT,
          role TEXT NOT NULL,
          runtime TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'active',
          token_hash TEXT NOT NULL,
          created_at TEXT NOT NULL,
          last_seen_at TEXT
        );

        CREATE TABLE IF NOT EXISTS tasks (
          task_id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          customer_id TEXT NOT NULL,
          project_id TEXT NOT NULL,
          epic_id TEXT,
          workpackage_id TEXT,
          owner_agent_id TEXT,
          status TEXT NOT NULL,
          priority TEXT NOT NULL DEFAULT 'normal',
          blocked_reason TEXT,
          acceptance_criteria TEXT,
          qa_gate_ids TEXT NOT NULL DEFAULT '[]',
          context_budget_chars INTEGER NOT NULL DEFAULT 24000,
          lease_expires_at TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          FOREIGN KEY(owner_agent_id) REFERENCES agents(agent_id)
        );

        CREATE TABLE IF NOT EXISTS runs (
          run_id TEXT PRIMARY KEY,
          task_id TEXT NOT NULL,
          agent_id TEXT NOT NULL,
          tenant_id TEXT NOT NULL,
          status TEXT NOT NULL,
          started_at TEXT NOT NULL,
          ended_at TEXT,
          summary TEXT,
          FOREIGN KEY(task_id) REFERENCES tasks(task_id),
          FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
        );

        CREATE TABLE IF NOT EXISTS evidence (
          evidence_id TEXT PRIMARY KEY,
          task_id TEXT NOT NULL,
          tenant_id TEXT NOT NULL,
          agent_id TEXT NOT NULL,
          kind TEXT NOT NULL,
          path TEXT,
          summary TEXT,
          content_hash TEXT,
          created_at TEXT NOT NULL,
          FOREIGN KEY(task_id) REFERENCES tasks(task_id)
        );

        CREATE TABLE IF NOT EXISTS gate_reports (
          gate_id TEXT PRIMARY KEY,
          task_id TEXT NOT NULL,
          tenant_id TEXT NOT NULL,
          qa_agent_id TEXT,
          final_verdict TEXT NOT NULL,
          dimensions_json TEXT NOT NULL,
          evidence_json TEXT NOT NULL,
          created_at TEXT NOT NULL,
          FOREIGN KEY(task_id) REFERENCES tasks(task_id)
        );

        CREATE TABLE IF NOT EXISTS promotions (
          promotion_id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          customer_id TEXT NOT NULL,
          project_id TEXT NOT NULL,
          source_path TEXT NOT NULL,
          target_path TEXT NOT NULL,
          review_path TEXT NOT NULL,
          status TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS events (
          event_id INTEGER PRIMARY KEY AUTOINCREMENT,
          event_type TEXT NOT NULL,
          tenant_id TEXT,
          actor_agent_id TEXT,
          task_id TEXT,
          payload_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_tenant_status ON tasks(tenant_id, status);
        CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner_agent_id);
        CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at);
        """
    )


def log_event(
    conn: sqlite3.Connection,
    event_type: str,
    tenant_id: str | None,
    actor_agent_id: str | None,
    task_id: str | None,
    payload: dict[str, Any],
) -> None:
    conn.execute(
        "INSERT INTO events(event_type, tenant_id, actor_agent_id, task_id, payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (event_type, tenant_id, actor_agent_id, task_id, json.dumps(payload, sort_keys=True), utc_now()),
    )


def ensure_runtime_dirs(root: pathlib.Path) -> None:
    for rel in [
        ".agent-control/logs",
        ".agent-control/secrets",
        ".agent-control/tmp",
        "agent-memory/tmp",
        "agent-memory/scratch",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)


def ensure_admin_token(root: pathlib.Path) -> str:
    token_file = admin_token_path(root)
    token_file.parent.mkdir(parents=True, exist_ok=True)
    if token_file.exists():
        return token_file.read_text(encoding="utf-8").strip()
    token = "amk_admin_" + secrets.token_urlsafe(32)
    locked_atomic_write_text(token_file, token + "\n")
    return token


def init_project(root: pathlib.Path) -> dict[str, Any]:
    for rel in REQUIRED_DIRS:
        (root / rel).mkdir(parents=True, exist_ok=True)
    ensure_runtime_dirs(root)
    token = ensure_admin_token(root)
    with connect(root) as conn:
        init_db(conn)
    return {
        "project": str(root),
        "db": str(db_path(root)),
        "admin_token_path": str(admin_token_path(root)),
        "admin_token_preview": token[:16] + "...",
    }


def read_json_body(handler: http.server.BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length") or 0)
    if length <= 0:
        return {}
    raw = handler.rfile.read(length).decode("utf-8")
    if not raw.strip():
        return {}
    return json.loads(raw)


def write_json(handler: http.server.BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    data = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def bearer(handler: http.server.BaseHTTPRequestHandler) -> str:
    header = handler.headers.get("Authorization") or ""
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return ""


def get_agent_by_token(conn: sqlite3.Connection, token: str) -> sqlite3.Row | None:
    if not token:
        return None
    token_hash = sha256_text(token)
    return conn.execute("SELECT * FROM agents WHERE token_hash = ? AND status = 'active'", (token_hash,)).fetchone()


def require_auth(
    handler: http.server.BaseHTTPRequestHandler,
    conn: sqlite3.Connection,
    root: pathlib.Path,
    admin_ok: bool = True,
) -> sqlite3.Row | str | None:
    token = bearer(handler)
    if admin_ok:
        admin = admin_token_path(root)
        if admin.exists() and token == admin.read_text(encoding="utf-8").strip():
            return "admin"
    agent = get_agent_by_token(conn, token)
    if agent:
        conn.execute("UPDATE agents SET last_seen_at = ? WHERE agent_id = ?", (utc_now(), agent["agent_id"]))
        return agent
    write_json(handler, 401, {"error": "missing_or_invalid_bearer_token"})
    return None


def register_agent(conn: sqlite3.Connection, body: dict[str, Any]) -> dict[str, Any]:
    role = body.get("role", "worker")
    if role not in AGENT_ROLES:
        raise ValueError(f"Invalid role: {role}")
    agent_id = body.get("agent_id") or f"agent-{secrets.token_hex(6)}"
    token = body.get("token") or "amk_agent_" + secrets.token_urlsafe(32)
    now = utc_now()
    conn.execute(
        """
        INSERT INTO agents(agent_id, tenant_id, customer_id, project_id, role, runtime, status, token_hash, created_at, last_seen_at)
        VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)
        ON CONFLICT(agent_id) DO UPDATE SET
          tenant_id=excluded.tenant_id,
          customer_id=excluded.customer_id,
          project_id=excluded.project_id,
          role=excluded.role,
          runtime=excluded.runtime,
          status='active',
          token_hash=excluded.token_hash,
          last_seen_at=excluded.last_seen_at
        """,
        (
            agent_id,
            body["tenant_id"],
            body.get("customer_id", ""),
            body.get("project_id", ""),
            role,
            body.get("runtime", "other"),
            sha256_text(token),
            now,
            now,
        ),
    )
    log_event(conn, "agent.registered", body["tenant_id"], agent_id, None, {"role": role})
    return {"agent_id": agent_id, "token": token}


def upsert_task(conn: sqlite3.Connection, body: dict[str, Any]) -> dict[str, Any]:
    task_id = body["task_id"]
    status = body.get("status", "ready")
    if status not in TASK_STATUSES:
        raise ValueError(f"Invalid task status: {status}")
    now = utc_now()
    conn.execute(
        """
        INSERT INTO tasks(task_id, tenant_id, customer_id, project_id, epic_id, workpackage_id, status, priority,
          acceptance_criteria, qa_gate_ids, context_budget_chars, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(task_id) DO UPDATE SET
          status=excluded.status,
          priority=excluded.priority,
          acceptance_criteria=excluded.acceptance_criteria,
          qa_gate_ids=excluded.qa_gate_ids,
          context_budget_chars=excluded.context_budget_chars,
          updated_at=excluded.updated_at
        """,
        (
            task_id,
            body["tenant_id"],
            body["customer_id"],
            body["project_id"],
            body.get("epic_id", ""),
            body.get("workpackage_id", ""),
            status,
            body.get("priority", "normal"),
            body.get("acceptance_criteria", ""),
            json.dumps(body.get("qa_gate_ids", [])),
            int(body.get("context_budget_chars", DEFAULTS["worker_context_budget_chars"])),
            now,
            now,
        ),
    )
    log_event(conn, "task.upserted", body["tenant_id"], body.get("actor_agent_id"), task_id, {"status": status})
    return {"task_id": task_id, "status": status}


def claim_task(conn: sqlite3.Connection, task_id: str, body: dict[str, Any], actor: sqlite3.Row | str) -> tuple[int, dict[str, Any]]:
    agent_id = body.get("agent_id") or (actor["agent_id"] if isinstance(actor, sqlite3.Row) else None)
    if not agent_id:
        return 400, {"error": "agent_id_required"}
    agent = conn.execute("SELECT * FROM agents WHERE agent_id = ? AND status = 'active'", (agent_id,)).fetchone()
    task = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not agent or not task:
        return 404, {"error": "agent_or_task_not_found"}
    if agent["tenant_id"] != task["tenant_id"]:
        return 403, {"error": "tenant_boundary_violation"}
    now = utc_now()
    lease_expires = (
        dt.datetime.now(UTC) + dt.timedelta(seconds=int(body.get("lease_ttl_seconds", DEFAULTS["lease_ttl_seconds"])))
    ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    allowed = set(body.get("expected_statuses") or ["backlog", "ready", "blocked", "review", "claimed", "in_progress"])
    if task["status"] not in allowed:
        return 409, {"error": "status_not_claimable", "status": task["status"]}
    lease_stale = parse_ts(task["lease_expires_at"]) <= time.time()
    same_owner = task["owner_agent_id"] == agent_id
    owner_free = task["owner_agent_id"] in (None, "")
    if not (owner_free or same_owner or lease_stale):
        return 409, {"error": "task_already_claimed", "owner_agent_id": task["owner_agent_id"]}
    conn.execute("BEGIN IMMEDIATE")
    try:
        updated = conn.execute(
            """
            UPDATE tasks
            SET owner_agent_id = ?, status = 'claimed', lease_expires_at = ?, updated_at = ?
            WHERE task_id = ?
              AND tenant_id = ?
              AND (
                owner_agent_id IS NULL OR owner_agent_id = '' OR owner_agent_id = ?
                OR lease_expires_at IS NULL OR lease_expires_at <= ?
              )
            """,
            (agent_id, lease_expires, now, task_id, agent["tenant_id"], agent_id, now),
        ).rowcount
        if updated != 1:
            conn.execute("ROLLBACK")
            return 409, {"error": "task_already_claimed"}
        run_id = body.get("run_id") or f"run-{secrets.token_hex(8)}"
        conn.execute(
            "INSERT OR IGNORE INTO runs(run_id, task_id, agent_id, tenant_id, status, started_at) VALUES (?, ?, ?, ?, 'active', ?)",
            (run_id, task_id, agent_id, agent["tenant_id"], now),
        )
        log_event(conn, "task.claimed", agent["tenant_id"], agent_id, task_id, {"run_id": run_id, "lease_expires_at": lease_expires})
        conn.execute("COMMIT")
        return 200, {"task_id": task_id, "agent_id": agent_id, "run_id": run_id, "lease_expires_at": lease_expires}
    except Exception:
        conn.execute("ROLLBACK")
        raise


def heartbeat_task(conn: sqlite3.Connection, task_id: str, body: dict[str, Any], actor: sqlite3.Row | str) -> tuple[int, dict[str, Any]]:
    agent_id = body.get("agent_id") or (actor["agent_id"] if isinstance(actor, sqlite3.Row) else "")
    task = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not task:
        return 404, {"error": "task_not_found"}
    if task["owner_agent_id"] != agent_id:
        return 403, {"error": "not_task_owner"}
    lease_expires = (
        dt.datetime.now(UTC) + dt.timedelta(seconds=int(body.get("lease_ttl_seconds", DEFAULTS["lease_ttl_seconds"])))
    ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    conn.execute("UPDATE tasks SET lease_expires_at = ?, updated_at = ? WHERE task_id = ?", (lease_expires, utc_now(), task_id))
    log_event(conn, "task.heartbeat", task["tenant_id"], agent_id, task_id, {"lease_expires_at": lease_expires})
    return 200, {"task_id": task_id, "lease_expires_at": lease_expires}


def update_task(conn: sqlite3.Connection, task_id: str, body: dict[str, Any], actor: sqlite3.Row | str) -> tuple[int, dict[str, Any]]:
    task = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not task:
        return 404, {"error": "task_not_found"}
    agent_id = body.get("agent_id") or (actor["agent_id"] if isinstance(actor, sqlite3.Row) else "")
    status = body.get("status", task["status"])
    if status not in TASK_STATUSES:
        return 400, {"error": "invalid_status"}
    if status == "done":
        gate_ids = json.loads(task["qa_gate_ids"] or "[]")
        if gate_ids:
            passing = conn.execute(
                "SELECT COUNT(*) AS n FROM gate_reports WHERE task_id = ? AND final_verdict IN ('pass', 'pass_with_concerns')",
                (task_id,),
            ).fetchone()["n"]
            if passing < len(gate_ids):
                return 409, {"error": "required_qa_gates_missing", "required": len(gate_ids), "passing": passing}
    conn.execute(
        "UPDATE tasks SET status = ?, blocked_reason = ?, updated_at = ? WHERE task_id = ?",
        (status, body.get("blocked_reason", task["blocked_reason"]), utc_now(), task_id),
    )
    log_event(conn, "task.updated", task["tenant_id"], agent_id, task_id, {"status": status})
    return 200, {"task_id": task_id, "status": status}


def release_task(conn: sqlite3.Connection, task_id: str, body: dict[str, Any], actor: sqlite3.Row | str) -> tuple[int, dict[str, Any]]:
    task = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not task:
        return 404, {"error": "task_not_found"}
    agent_id = body.get("agent_id") or (actor["agent_id"] if isinstance(actor, sqlite3.Row) else "")
    if task["owner_agent_id"] != agent_id and actor != "admin":
        return 403, {"error": "not_task_owner"}
    next_status = body.get("status", "ready")
    conn.execute(
        "UPDATE tasks SET owner_agent_id = NULL, status = ?, lease_expires_at = NULL, updated_at = ? WHERE task_id = ?",
        (next_status, utc_now(), task_id),
    )
    log_event(conn, "task.released", task["tenant_id"], agent_id, task_id, {"status": next_status})
    return 200, {"task_id": task_id, "status": next_status}


def add_evidence(conn: sqlite3.Connection, task_id: str, body: dict[str, Any], actor: sqlite3.Row | str) -> tuple[int, dict[str, Any]]:
    task = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not task:
        return 404, {"error": "task_not_found"}
    agent_id = body.get("agent_id") or (actor["agent_id"] if isinstance(actor, sqlite3.Row) else "")
    evidence_id = body.get("evidence_id") or f"ev-{secrets.token_hex(8)}"
    content = body.get("summary", "") + body.get("path", "")
    conn.execute(
        """
        INSERT INTO evidence(evidence_id, task_id, tenant_id, agent_id, kind, path, summary, content_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            evidence_id,
            task_id,
            task["tenant_id"],
            agent_id,
            body.get("kind", "note"),
            body.get("path", ""),
            body.get("summary", ""),
            body.get("content_hash") or sha256_text(content),
            utc_now(),
        ),
    )
    log_event(conn, "task.evidence", task["tenant_id"], agent_id, task_id, {"evidence_id": evidence_id})
    return 200, {"evidence_id": evidence_id}


def add_gate_report(conn: sqlite3.Connection, gate_id: str, body: dict[str, Any], actor: sqlite3.Row | str) -> tuple[int, dict[str, Any]]:
    task_id = body["task_id"]
    task = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not task:
        return 404, {"error": "task_not_found"}
    agent_id = body.get("qa_agent_id") or (actor["agent_id"] if isinstance(actor, sqlite3.Row) else "")
    verdict = body.get("final_verdict", "fail")
    if verdict not in {"pass", "fail", "pass_with_concerns", "pending"}:
        return 400, {"error": "invalid_final_verdict"}
    conn.execute(
        """
        INSERT INTO gate_reports(gate_id, task_id, tenant_id, qa_agent_id, final_verdict, dimensions_json, evidence_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(gate_id) DO UPDATE SET
          final_verdict=excluded.final_verdict,
          dimensions_json=excluded.dimensions_json,
          evidence_json=excluded.evidence_json,
          created_at=excluded.created_at
        """,
        (
            gate_id,
            task_id,
            task["tenant_id"],
            agent_id,
            verdict,
            json.dumps(body.get("dimensions", {}), sort_keys=True),
            json.dumps(body.get("evidence", []), sort_keys=True),
            utc_now(),
        ),
    )
    if verdict == "fail":
        conn.execute(
            "UPDATE tasks SET status = 'blocked', blocked_reason = ?, updated_at = ? WHERE task_id = ?",
            (body.get("blocked_reason", "QA gate failed"), utc_now(), task_id),
        )
    log_event(conn, "gate.reported", task["tenant_id"], agent_id, task_id, {"gate_id": gate_id, "final_verdict": verdict})
    return 200, {"gate_id": gate_id, "final_verdict": verdict}


def build_context_pack(conn: sqlite3.Connection, root: pathlib.Path, body: dict[str, Any]) -> dict[str, Any]:
    task_id = body["task_id"]
    task = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not task:
        raise ValueError("task_not_found")
    tenant_id = body.get("tenant_id") or task["tenant_id"]
    if tenant_id != task["tenant_id"]:
        raise PermissionError("tenant_boundary_violation")
    role = body.get("agent_role", "worker")
    objective = str(body.get("objective") or "")
    budget = int(body.get("budget_chars") or (DEFAULTS["planner_context_budget_chars"] if role in {"planner", "orchestrator", "strategic-reviewer"} else task["context_budget_chars"]))
    sources: list[tuple[str, pathlib.Path]] = []
    for rel in [
        "PROJECT_CONTEXT.md",
        "PROJECT_CONTEXT.template.md",
        "agent-memory/README.md",
    ]:
        path = root / rel
        if path.exists():
            sources.append((rel, path))
    for base in ["agent-memory/decisions", "agent-memory/canonical", "agent-memory/compiled"]:
        folder = root / base
        if folder.exists():
            for path in sorted(folder.rglob("*.md"))[:40]:
                sources.append((str(path.relative_to(root)), path))
    included = []
    excluded = []
    chunks = [
        f"# Context Pack: {task_id}\n",
        f"- tenant_id: {task['tenant_id']}",
        f"- customer_id: {task['customer_id']}",
        f"- project_id: {task['project_id']}",
        f"- agent_role: {role}",
        f"- task_status: {task['status']}",
        f"- owner_agent_id: {task['owner_agent_id'] or ''}",
        f"- objective: {objective}",
        "\n## Task\n",
        objective or task["acceptance_criteria"] or "No acceptance criteria recorded.",
        "\n## Sources\n",
    ]
    remaining = budget - sum(len(x) for x in chunks)
    for rel, path in sources:
        text = path.read_text(encoding="utf-8", errors="replace")
        entry = {"path": rel, "hash": sha256_file(path), "chars": len(text)}
        if remaining <= 0 or len(text) > remaining:
            excluded.append({**entry, "reason": "context_budget"})
            continue
        chunks.append(f"\n### {rel}\n\n{text}\n")
        included.append(entry)
        remaining -= len(text)
    content = "\n".join(chunks)[:budget]
    return {
        "context_pack_id": f"ctx-{task_id}-{sha256_text(content)[:12]}",
        "tenant_id": task["tenant_id"],
        "customer_id": task["customer_id"],
        "project_id": task["project_id"],
        "task_id": task_id,
        "agent_role": role,
        "budget_chars": budget,
        "content": content,
        "included_sources": included,
        "excluded_sources": excluded,
    }


def context_pack_score(record: dict[str, Any], query: str, preferred_types: list[str], now_ts: float | None = None) -> tuple[float, dict[str, Any], list[dict[str, Any]]]:
    meta = record["metadata"]
    query_tokens = set(tokenize(query))
    haystack_parts = [
        str(meta.get("memory_id", "")),
        str(meta.get("semantic_title", "")),
        str(meta.get("summary", "")),
        list_text(meta.get("concept_tags", [])),
        list_text(meta.get("stack_tags", [])),
        list_text(meta.get("problem_patterns", [])),
        list_text(meta.get("architecture_patterns", [])),
        list_text(meta.get("failure_modes", [])),
        list_text(meta.get("reusable_lessons", [])),
        record["source_path"],
        markdown_body(record["content"])[:2500],
    ]
    haystack_text = " ".join(haystack_parts)
    haystack_tokens = set(tokenize(haystack_text))
    overlap = sorted(query_tokens & haystack_tokens)
    doc_type = str(meta.get("doc_type", ""))
    type_priority = max(0, len(preferred_types) - preferred_types.index(doc_type)) if doc_type in preferred_types else 0
    status_score = 4 if meta.get("status") in {"reviewed", "promoted"} else 2 if meta.get("status") == "active" else 0
    review_score = 3 if meta.get("review_status") == "approved" else 2 if meta.get("review_status") == "reviewed" else 0
    tag_score = len(overlap) * 3
    exact_score = 8 if query and query.lower() in haystack_text.lower() else 0
    edge_score = 0
    for edge in meta.get("edges", []):
        if isinstance(edge, dict):
            edge_text = " ".join(str(edge.get(key, "")) for key in ["type", "target", "reason"])
            edge_score += min(4, len(query_tokens & set(tokenize(edge_text))) * 2)
    warnings = memory_freshness_warnings(meta, now_ts=now_ts)
    freshness_penalty = -8 if any(w["field"] in {"expires_at", "valid_until"} for w in warnings) else -4 if warnings else 0
    score_breakdown = {
        "doc_type_priority": type_priority,
        "status": status_score,
        "review": review_score,
        "tag_summary_match": tag_score,
        "exact_match": exact_score,
        "edge_match": edge_score,
        "freshness": freshness_penalty,
        "matched_terms": overlap,
    }
    total = sum(value for value in score_breakdown.values() if isinstance(value, (int, float)))
    return float(total), score_breakdown, warnings


def build_context_pack_markdown(
    root: pathlib.Path,
    task_id: str,
    agent_role: str = "worker",
    budget_chars: int | None = None,
    tenant_id: str | None = None,
    customer_id: str | None = None,
    project_id: str | None = None,
    objective: str | None = None,
) -> dict[str, Any]:
    records = load_memory_records(root, include_sessions=False)
    explicit_scope = bool(tenant_id or customer_id or project_id)
    defaults = project_defaults(root)
    scope = {
        "tenant_id": tenant_id or (defaults["tenant_id"] if explicit_scope else None),
        "customer_id": customer_id or (defaults["customer_id"] if explicit_scope else None),
        "project_id": project_id or (defaults["project_id"] if explicit_scope else None),
    }
    tenants = {str(record["metadata"].get("tenant_id", "")) for record in records if record["metadata"].get("tenant_id")}
    real_tenants = {value for value in tenants if value not in {"TENANT_ID", "tenant-local"}}
    if len(real_tenants) > 1 and not (scope["tenant_id"] or tenant_id):
        raise PermissionError("tenant_scope_required_for_multi_tenant_context_pack")
    if not explicit_scope and len(real_tenants) <= 1:
        scope = {"tenant_id": None, "customer_id": None, "project_id": None}
    budget = int(budget_chars or (DEFAULTS["planner_context_budget_chars"] if agent_role in {"planner", "orchestrator", "strategic-reviewer"} else DEFAULTS["worker_context_budget_chars"]))
    preferred_types = ["user_context", "preference", "goal", "compiled", "canonical", "adr", "research", "personal_pattern", "pattern", "lesson", "idea", "qa", "task", "handoff"]
    scored = []
    no_relevance = []
    now_ts = time.time()
    query = " ".join(part for part in [task_id, objective or ""] if part).strip()
    for record in records:
        meta = record["metadata"]
        reason = scope_rejection_reason(meta, scope["tenant_id"], scope["customer_id"], scope["project_id"], allow_global_user=True)
        if reason:
            continue
        score, score_breakdown, freshness_warnings = context_pack_score(record, query, preferred_types, now_ts=now_ts)
        if score > 0:
            scored.append((score, record, score_breakdown, freshness_warnings))
        elif len(no_relevance) < 50:
            no_relevance.append({"memory_id": meta.get("memory_id"), "source_path": record["source_path"], "reason": "no_relevance", "score_breakdown": score_breakdown, "freshness_warnings": freshness_warnings})
    scored.sort(key=lambda item: (-item[0], item[1]["source_path"]))
    raw_chars_available = sum(len(record["content"]) for _, record, _, _ in scored)
    chunks = [
        f"# Context Pack: {task_id}",
        f"- objective: {objective or ''}",
        f"- agent_role: {agent_role}",
        f"- budget_chars: {budget}",
        f"- tenant_scope: {scope['tenant_id'] or defaults['tenant_id']}",
        f"- customer_scope: {scope['customer_id'] or defaults['customer_id']}",
        f"- project_scope: {scope['project_id'] or defaults['project_id']}",
        "",
        "## Index Summary",
    ]
    included = []
    dropped = list(no_relevance)
    remaining = budget - sum(len(chunk) + 1 for chunk in chunks)
    for score, record, score_breakdown, freshness_warnings in scored:
        meta = record["metadata"]
        snippet = "\n".join(
            [
                f"### {meta.get('semantic_title', meta.get('memory_id'))}",
                f"- memory_id: {meta.get('memory_id')}",
                f"- doc_type: {meta.get('doc_type')}",
                f"- source: {record['source_path']}",
                f"- summary: {meta.get('summary', '')}",
                f"- score: {score}",
                f"- freshness_warnings: {len(freshness_warnings)}",
                "",
                markdown_body(record["content"])[:2000],
                "",
            ]
        )
        if len(snippet) <= remaining:
            chunks.append(snippet)
            included.append({"memory_id": meta.get("memory_id"), "source_path": record["source_path"], "score": score, "score_breakdown": score_breakdown, "freshness_warnings": freshness_warnings, "chars": len(snippet)})
            remaining -= len(snippet)
        else:
            dropped.append({"memory_id": meta.get("memory_id"), "source_path": record["source_path"], "reason": "context_budget", "score": score, "score_breakdown": score_breakdown, "freshness_warnings": freshness_warnings, "chars": len(snippet)})
    content = "\n".join(chunks)
    included_chars = len(content)
    return {
        "context_pack_id": f"ctx-md-{sha256_text(task_id + content)[:12]}",
        "task_id": task_id,
        "objective": objective or "",
        "agent_role": agent_role,
        "tenant_id": scope["tenant_id"] or defaults["tenant_id"],
        "customer_id": scope["customer_id"] or defaults["customer_id"],
        "project_id": scope["project_id"] or defaults["project_id"],
        "budget_chars": budget,
        "content": content,
        "included_sources": included,
        "excluded_sources": dropped,
        "freshness_warnings": [warning for source in included + dropped for warning in source.get("freshness_warnings", [])],
        "raw_chars_available": raw_chars_available,
        "included_chars": included_chars,
        "compression_ratio": round((included_chars / raw_chars_available), 4) if raw_chars_available else 0,
        "estimated_tokens": max(1, included_chars // 4) if included_chars else 0,
        "dropped_sources": len(dropped),
    }


def promote_memory(conn: sqlite3.Connection, root: pathlib.Path, body: dict[str, Any]) -> dict[str, Any]:
    source = (root / body["source_path"]).resolve()
    target = (root / body["target_path"]).resolve()
    review = (root / body["review_path"]).resolve()
    root_resolved = root.resolve()
    try:
        source_rel = source.relative_to(root_resolved)
        target_rel = target.relative_to(root_resolved)
        review_rel = review.relative_to(root_resolved)
    except ValueError:
        raise PermissionError("path_outside_project")
    if not source.exists():
        raise FileNotFoundError(str(source))
    if not review.exists():
        raise FileNotFoundError(str(review))
    allowed_targets = {
        "canonical": "agent-memory/canonical",
        "compiled": "agent-memory/compiled",
        "pattern": "agent-memory/patterns",
        "lesson": "agent-memory/lessons",
    }
    source_text = source.read_text(encoding="utf-8", errors="replace")
    source_meta = parse_frontmatter(source_text)
    review_text_raw = review.read_text(encoding="utf-8", errors="replace")
    review_text = review_text_raw.lower()
    review_meta = parse_frontmatter(review_text_raw)
    source_errors = frontmatter_errors(source_meta, str(source_rel).replace("\\", "/"), exportable_only=False)
    if source_errors:
        raise PermissionError("source_frontmatter_invalid:" + "; ".join(source_errors[:3]))
    for key in ["tenant_id", "customer_id", "project_id"]:
        if source_meta.get(key) != body[key]:
            raise PermissionError(f"{key}_mismatch")
    doc_type = str(source_meta.get("doc_type", ""))
    target_root = allowed_targets.get(doc_type)
    if not target_root or not str(target_rel).replace("\\", "/").startswith(target_root + "/"):
        raise PermissionError("target_path_not_allowed_for_doc_type")
    if source_meta.get("status") not in {"reviewed", "promoted"}:
        raise PermissionError("source_status_must_be_reviewed_or_promoted")
    if source_meta.get("review_status") not in {"reviewed", "approved"}:
        raise PermissionError("source_review_status_must_be_reviewed_or_approved")
    if source_meta.get("visibility") == "shared":
        if source_meta.get("sanitization_status") != "approved" or source_meta.get("data_class") not in SHARED_ALLOWED_DATA_CLASSES:
            raise PermissionError("shared_promotion_requires_approved_sanitization")
    expected_hash = body.get("source_hash")
    actual_hash = sha256_file(source)
    if expected_hash and expected_hash != actual_hash:
        raise PermissionError("source_hash_mismatch")
    review_approves = (
        review_meta.get("review_status") in {"reviewed", "approved"}
        or review_meta.get("final_verdict") == "pass"
        or ("pass" in review_text and "fail" not in review_text)
    )
    if not review_approves:
        raise PermissionError("review_does_not_approve_promotion")
    promotion_id = body.get("promotion_id") or f"promo-{secrets.token_hex(8)}"
    target.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(root / ".agent-control" / "locks" / f"{promotion_id}.lock", timeout_seconds=60):
        locked_atomic_write_text(target, source_text, timeout_seconds=60)
        manifest_dir = root / "agent-memory" / "evidence" / "promotions"
        manifest = {
            "promotion_id": promotion_id,
            "tenant_id": body["tenant_id"],
            "customer_id": body["customer_id"],
            "project_id": body["project_id"],
            "agent_id": body.get("agent_id") or "cli-curator",
            "source_path": str(source_rel).replace("\\", "/"),
            "target_path": str(target_rel).replace("\\", "/"),
            "review_path": str(review_rel).replace("\\", "/"),
            "source_hash": actual_hash,
            "review_hash": sha256_file(review),
            "policy_version": "promotion-v0.3",
            "created_at": utc_now(),
        }
        locked_atomic_write_text(manifest_dir / f"{promotion_id}.json", json.dumps(manifest, indent=2, sort_keys=True), timeout_seconds=60)
    conn.execute(
        """
        INSERT INTO promotions(promotion_id, tenant_id, customer_id, project_id, source_path, target_path, review_path, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'promoted', ?)
        """,
        (
            promotion_id,
            body["tenant_id"],
            body["customer_id"],
            body["project_id"],
            str(source_rel).replace("\\", "/"),
            str(target_rel).replace("\\", "/"),
            str(review_rel).replace("\\", "/"),
            utc_now(),
        ),
    )
    log_event(conn, "memory.promoted", body["tenant_id"], body.get("agent_id"), None, {"promotion_id": promotion_id})
    return {"promotion_id": promotion_id, "target_path": str(target_rel).replace("\\", "/"), "source_hash": actual_hash, "manifest_path": f"agent-memory/evidence/promotions/{promotion_id}.json"}


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "[]"}:
        return [] if value == "[]" else ""
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    with contextlib.suppress(ValueError):
        if "." in value:
            return float(value)
        return int(value)
    return value


def parse_frontmatter(text: str) -> dict[str, Any]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    meta: dict[str, Any] = {}
    current_key = None
    current_list_item: dict[str, Any] | None = None
    for raw in parts[1].splitlines():
        if not raw.strip():
            continue
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("- ") and current_key:
            if not isinstance(meta.get(current_key), list):
                meta[current_key] = []
            item = stripped[2:].strip()
            if ":" in item:
                key, value = item.split(":", 1)
                current_list_item = {key.strip(): parse_scalar(value)}
                meta.setdefault(current_key, []).append(current_list_item)
            else:
                current_list_item = None
                meta.setdefault(current_key, []).append(parse_scalar(item))
            continue
        if line.startswith("    ") and current_list_item and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_list_item[key.strip()] = parse_scalar(value)
            continue
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            current_list_item = None
            meta[current_key] = parse_scalar(value)
    return meta


def markdown_body(text: str) -> str:
    text = text.lstrip("\ufeff")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].lstrip()
    return text


def memory_markdown_files(root: pathlib.Path, include_sessions: bool = True) -> list[pathlib.Path]:
    bases = [
        "USER_CONTEXT.md",
        "USER_CONTEXT.template.md",
        "PROJECT_CONTEXT.md",
        "PROJECT_CONTEXT.template.md",
        "global-memory/preferences",
        "global-memory/goals",
        "global-memory/daily",
        "global-memory/tasks",
        "global-memory/ideas",
        "global-memory/research",
        "global-memory/patterns",
        "global-memory/coach",
        "agent-memory/canonical",
        "agent-memory/compiled",
        "agent-memory/patterns",
        "agent-memory/lessons",
        "agent-memory/ideas",
        "agent-memory/decisions",
        "agent-memory/evidence",
        "agent-memory/handoffs",
        "agent-memory/pi-agent/reports",
        "agent-memory/pi-agent/parallels",
        "agent-memory/pi-agent/trends",
        "agent-memory/pi-agent/recurring-errors",
        "agent-memory/pi-agent/concepts",
        "agent-memory/pi-agent/red-team",
        "agent-memory/pi-agent/evaluations",
        "agent-memory/pi-agent/scorecards",
    ]
    if include_sessions:
        bases.append("agent-memory/sessions")
    files: list[pathlib.Path] = []
    for rel in bases:
        path = root / rel
        if path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
    return sorted(set(files))


def retrieval_header(meta: dict[str, Any]) -> str:
    def join_values(key: str) -> str:
        value = meta.get(key, [])
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return str(value)

    return "\n".join(
        [
            f"memory_id: {meta.get('memory_id', '')}",
            f"doc_type: {meta.get('doc_type', '')}",
            f"tenant_id: {meta.get('tenant_id', '')}",
            f"customer_id: {meta.get('customer_id', '')}",
            f"project_id: {meta.get('project_id', '')}",
            f"semantic_title: {meta.get('semantic_title', meta.get('title', ''))}",
            f"summary: {meta.get('summary', '')}",
            f"concept_tags: {join_values('concept_tags')}",
            f"stack_tags: {join_values('stack_tags')}",
            f"problem_patterns: {join_values('problem_patterns')}",
            f"architecture_patterns: {join_values('architecture_patterns')}",
            f"failure_modes: {join_values('failure_modes')}",
            f"reusable_lessons: {join_values('reusable_lessons')}",
            "",
        ]
    )


def frontmatter_errors(meta: dict[str, Any], rel: str, exportable_only: bool = False) -> list[str]:
    errors: list[str] = []
    if not meta:
        return [] if exportable_only else [f"{rel}: missing frontmatter"]
    if exportable_only and meta.get("doc_type") not in EXPORTABLE_DOC_TYPES:
        return []
    for key in CORE_FRONTMATTER_REQUIRED:
        if key not in meta:
            errors.append(f"{rel}: missing {key}")
    if "memory_id" in meta and not str(meta["memory_id"]).startswith("mem:"):
        errors.append(f"{rel}: memory_id must start with mem:")
    enum_checks = {
        "doc_type": EXPORTABLE_DOC_TYPES,
        "status": MEMORY_STATUS_VALUES,
        "visibility": VISIBILITY_VALUES,
        "data_class": DATA_CLASS_VALUES,
        "review_status": REVIEW_STATUS_VALUES,
        "sanitization_status": SANITIZATION_STATUS_VALUES,
        "retention_class": RETENTION_CLASS_VALUES,
        "review_cycle": set(REVIEW_CYCLE_DAYS),
    }
    for key, allowed in enum_checks.items():
        if key in meta and meta[key] not in allowed:
            errors.append(f"{rel}: invalid {key}={meta[key]}")
    for key in ["stale_after", "expires_at", "last_reviewed_at", "valid_until"]:
        if meta.get(key) and not parse_ts(str(meta.get(key))):
            errors.append(f"{rel}: invalid date field {key}={meta.get(key)}")
    edges = meta.get("edges", [])
    if not isinstance(edges, list):
        errors.append(f"{rel}: edges must be a list")
    else:
        for idx, edge in enumerate(edges):
            if not isinstance(edge, dict):
                errors.append(f"{rel}: edge {idx} must be an object")
                continue
            if edge.get("type") not in EDGE_TYPES:
                errors.append(f"{rel}: edge {idx} has invalid type")
            if not edge.get("target"):
                errors.append(f"{rel}: edge {idx} missing target")
    if meta.get("visibility") == "shared":
        if meta.get("review_status") != "approved":
            errors.append(f"{rel}: shared visibility requires review_status=approved")
        if meta.get("sanitization_status") != "approved":
            errors.append(f"{rel}: shared visibility requires sanitization_status=approved")
        if meta.get("data_class") not in SHARED_ALLOWED_DATA_CLASSES:
            errors.append(f"{rel}: shared visibility cannot export data_class={meta.get('data_class')}")
    if meta.get("doc_type") == "research":
        for key in ["source_url", "source_date", "retrieved_at", "valid_until", "version_context"]:
            if not meta.get(key):
                errors.append(f"{rel}: research requires {key}")
    if meta.get("doc_type") == "preference" and not meta.get("last_confirmed_at"):
        errors.append(f"{rel}: preference requires last_confirmed_at")
    if meta.get("doc_type") == "coach_report":
        for key in ["source_memory_ids", "recommendation_confidence", "next_action"]:
            if key not in meta:
                errors.append(f"{rel}: coach_report requires {key}")
    return errors


def disallowed_control_characters(text: str) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    for idx, char in enumerate(text):
        codepoint = ord(char)
        if codepoint < 32 and char not in ("\t", "\n", "\r"):
            findings.append((idx, f"U+{codepoint:04X}"))
            if len(findings) >= 5:
                break
    return findings


def load_memory_records(root: pathlib.Path, include_sessions: bool = True) -> list[dict[str, Any]]:
    records = []
    for path in memory_markdown_files(root, include_sessions=include_sessions):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        if not meta.get("memory_id"):
            continue
        if meta.get("data_class") == "confidential" or RUNTIME_DRAFT_TAG in (meta.get("concept_tags") or []):
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        source_hash = sha256_file(path)
        records.append(
            {
                "path": path,
                "source_path": rel,
                "source_hash": source_hash,
                "metadata": meta,
                "content": text,
                "body": markdown_body(text),
            }
        )
    return records


def validate_memory(root: pathlib.Path, strict: bool = False) -> dict[str, Any]:
    results = []
    records = load_memory_records(root, include_sessions=True)
    all_files = memory_markdown_files(root, include_sessions=True)
    by_id: dict[str, list[str]] = {}
    for record in records:
        mid = str(record["metadata"].get("memory_id", ""))
        by_id.setdefault(mid, []).append(record["source_path"])
    for path in all_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        rel = str(path.relative_to(root)).replace("\\", "/")
        control_chars = disallowed_control_characters(text)
        for offset, codepoint in control_chars:
            results.append(
                {
                    "name": f"content-control-character:{rel}",
                    "passed": False,
                    "details": f"{rel}: disallowed control character {codepoint} at offset {offset}",
                }
            )
        errors = frontmatter_errors(meta, rel, exportable_only=not strict)
        for error in errors:
            results.append({"name": f"frontmatter:{rel}", "passed": False, "details": error})
        if not errors and meta.get("memory_id"):
            results.append({"name": f"frontmatter:{rel}", "passed": True, "details": "Valid core frontmatter."})
    for mid, paths in by_id.items():
        results.append({"name": f"unique-memory-id:{mid}", "passed": len(paths) == 1, "details": ", ".join(paths)})
    known_ids = set(by_id)
    for record in records:
        for edge in record["metadata"].get("edges", []):
            if not isinstance(edge, dict) or edge.get("external"):
                continue
            target = edge.get("target")
            if target and str(target).startswith("mem:"):
                results.append(
                    {
                        "name": f"edge-target:{record['metadata']['memory_id']}->{target}",
                        "passed": target in known_ids,
                        "details": "Internal edge target exists." if target in known_ids else "Missing internal edge target.",
                    }
                )
    failed = [r for r in results if not r["passed"]]
    return {"project": str(root), "passed": not failed, "totalChecks": len(results), "failedChecks": len(failed), "results": results}


def audit_retention(root: pathlib.Path) -> dict[str, Any]:
    now_ts = time.time()
    findings: list[dict[str, Any]] = []
    for path in memory_markdown_files(root, include_sessions=True):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        if not meta.get("memory_id"):
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        retention_class = retention_class_for(meta)
        if not meta.get("retention_class"):
            findings.append(
                {
                    "severity": "info",
                    "action": "add_retention_class",
                    "memory_id": meta.get("memory_id"),
                    "source_path": rel,
                    "doc_type": meta.get("doc_type", ""),
                    "retention_class": retention_class,
                    "reason": "retention_class_defaulted",
                }
            )
        for warning in memory_freshness_warnings(meta, now_ts=now_ts):
            severity = "warning"
            action = "review"
            if warning["field"] == "expires_at":
                severity = "error" if retention_class != "legal-hold" else "warning"
                action = "purge_or_anonymize_preview" if retention_class != "legal-hold" else "legal_hold_review"
            findings.append(
                {
                    "severity": severity,
                    "action": action,
                    "memory_id": meta.get("memory_id"),
                    "source_path": rel,
                    "doc_type": meta.get("doc_type", ""),
                    "retention_class": retention_class,
                    **warning,
                }
            )
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding["severity"]] = counts.get(finding["severity"], 0) + 1
    preview = [
        finding
        for finding in findings
        if finding.get("action") in {"purge_or_anonymize_preview", "legal_hold_review"}
    ]
    return {
        "project": str(root),
        "generated_at": utc_now(),
        "passed": counts.get("error", 0) == 0,
        "findings": findings,
        "counts": counts,
        "purge_preview": preview,
        "policy": "retention-audit-v0.5-read-only",
    }


def review_memory_conflicts(root: pathlib.Path) -> dict[str, Any]:
    now_ts = time.time()
    records = load_memory_records(root, include_sessions=True)
    by_id = {str(record["metadata"].get("memory_id")): record for record in records}
    findings: list[dict[str, Any]] = []
    active_statuses = {"active", "reviewed", "promoted"}
    for record in records:
        meta = record["metadata"]
        rel = record["source_path"]
        for warning in memory_freshness_warnings(meta, now_ts=now_ts):
            findings.append(
                {
                    "severity": "warning",
                    "kind": warning["reason"],
                    "memory_id": meta.get("memory_id"),
                    "source_path": rel,
                    **warning,
                }
            )
        for edge in meta.get("edges", []):
            if not isinstance(edge, dict):
                continue
            edge_type = edge.get("type")
            if edge_type not in {"contradicts", "supersedes", "superseded_by"}:
                continue
            target_id = str(edge.get("target") or "")
            target = by_id.get(target_id)
            target_status = target["metadata"].get("status", "") if target else "missing"
            source_status = meta.get("status", "")
            severity = "info"
            if edge_type == "contradicts" and source_status in active_statuses and target_status in active_statuses:
                severity = "error"
            elif edge_type in {"supersedes", "superseded_by"} and source_status in active_statuses and target_status in active_statuses:
                severity = "warning"
            findings.append(
                {
                    "severity": severity,
                    "kind": f"edge_{edge_type}",
                    "memory_id": meta.get("memory_id"),
                    "source_path": rel,
                    "target": target_id,
                    "target_status": target_status,
                    "source_status": source_status,
                    "reason": edge.get("reason", ""),
                    "recommended_action": "review_conflict_or_supersession",
                }
            )
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding["severity"]] = counts.get(finding["severity"], 0) + 1
    return {
        "project": str(root),
        "generated_at": utc_now(),
        "passed": counts.get("error", 0) == 0,
        "findings": findings,
        "counts": counts,
        "policy": "memory-conflict-review-v0.5",
    }


def scan_sensitive_data(root: pathlib.Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    def scan_text(text: str, rel: str, memory_id: str = "") -> None:
        for line_no, line in enumerate(text.splitlines(), start=1):
            redacted_line = line.strip()
            if len(redacted_line) > 180:
                redacted_line = redacted_line[:177] + "..."
            for pattern in SECRET_VALUE_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        {
                            "severity": "error",
                            "kind": "secret_pattern",
                            "memory_id": memory_id,
                            "source_path": rel,
                            "line": line_no,
                            "excerpt": pattern.sub("[REDACTED]", redacted_line),
                            "recommended_action": "redact_before_export_or_promotion",
                        }
                    )
                    break
            else:
                if SECRET_KEY_RE.search(line) and re.search(r"[:=]\s*['\"]?[A-Za-z0-9._~+/=-]{12,}", line):
                    findings.append(
                        {
                            "severity": "warning",
                            "kind": "secret_key_like_field",
                            "memory_id": memory_id,
                            "source_path": rel,
                            "line": line_no,
                            "excerpt": re.sub(r"([:=]\s*)[^'\"\s,;]+", r"\1[REDACTED]", redacted_line),
                            "recommended_action": "review_sensitive_field",
                        }
                    )
    for path in memory_markdown_files(root, include_sessions=True):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        if not meta.get("memory_id"):
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        scan_text(text, rel, str(meta.get("memory_id") or ""))
    for path in sorted((root / "agent-memory" / "sessions").glob("**/events.jsonl")) if (root / "agent-memory" / "sessions").exists() else []:
        rel = str(path.relative_to(root)).replace("\\", "/")
        scan_text(path.read_text(encoding="utf-8", errors="replace"), rel, "")
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding["severity"]] = counts.get(finding["severity"], 0) + 1
    return {
        "project": str(root),
        "generated_at": utc_now(),
        "passed": counts.get("error", 0) == 0,
        "findings": findings,
        "counts": counts,
        "policy": "sensitive-data-scan-v0.5-read-only",
    }


def memory_doctor(root: pathlib.Path, mode: str = "auto") -> dict[str, Any]:
    checks = []

    def add(name: str, passed: bool, severity: str, details: str, fix: str = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "severity": severity, "details": details, "fix": fix})

    is_kit = (root / "PROJECT_CONTEXT.template.md").exists() and (root / "tools" / "agent_memory_cli.py").exists() and (root / "agent-memory" / "templates").is_dir()
    detected_mode = "kit" if is_kit and not (root / "PROJECT_CONTEXT.md").exists() else "host"
    effective_mode = detected_mode if mode == "auto" else mode
    add("doctor-mode", True, "info", f"Doctor mode: {effective_mode} (detected: {detected_mode}).")
    if effective_mode == "kit":
        add("kit-template-project-context", (root / "PROJECT_CONTEXT.template.md").exists(), "error", "PROJECT_CONTEXT.template.md is present.", "Restore the kit templates.")
        add("kit-template-agents", (root / "AGENTS.template.md").exists(), "error", "AGENTS.template.md is present.", "Restore the kit templates.")
        add("kit-template-claude", (root / "CLAUDE.template.md").exists(), "error", "CLAUDE.template.md is present.", "Restore the kit templates.")
        add("kit-tools", (root / "tools" / "agent_memory_cli.py").exists(), "error", "Kit CLI exists.", "Restore tools/agent_memory_cli.py.")
    else:
        add("project-context", (root / "PROJECT_CONTEXT.md").exists(), "error", "PROJECT_CONTEXT.md is present.", "Run init-agent-memory or copy PROJECT_CONTEXT.template.md.")
        add("agents-md", (root / "AGENTS.md").exists(), "error", "AGENTS.md is present.", "Run bootstrap-agent-memory for this repo.")
        add("claude-md", (root / "CLAUDE.md").exists(), "warning", "CLAUDE.md is present.", "Copy CLAUDE.template.md if Claude/Cowork is used.")
    add("agent-memory-dir", (root / "agent-memory").is_dir(), "error", "agent-memory directory is present.", "Run init-agent-memory for this repo.")
    add("design-md", (root / "DESIGN.md").exists(), "warning", "DESIGN.md is present.", "Copy DESIGN.md from the kit if visual reports are used.")
    add("cli-local", (root / "tools" / "agent_memory_cli.py").exists(), "warning", "Local CLI exists.", "Copy tools/agent_memory_cli.py into the project or run from an Owledge repo checkout when local tooling is missing.")
    add("raw-events-ignored", bool(_gitignore_contains(root, "agent-memory/sessions/**/events.jsonl")), "warning", "Raw runtime event logs are ignored by git.", "Add agent-memory/sessions/**/events.jsonl to .gitignore for privacy.")
    validation = validate_memory(root)
    add("memory-validation", bool(validation["passed"]), "error", f"Memory validation: {validation['failedChecks']} failed of {validation['totalChecks']}.", "Run python tools/agent_memory_cli.py --project-root . validate-memory --strict and fix reported frontmatter/edge issues.")
    version_file = root / "VERSION"
    readme = root / "README.md"
    if version_file.exists() and readme.exists():
        version = version_file.read_text(encoding="utf-8", errors="replace").strip()
        readme_text = readme.read_text(encoding="utf-8", errors="replace")
        version_ok = f"version-{version}-" in readme_text or f"version-{version}" in readme_text
        add("version-consistency", version_ok, "warning", f"README version badge {'matches' if version_ok else 'does not match'} VERSION ({version}).", "Align README version badge and VERSION.")
    hook_error_log = root / ".agent-control" / "logs" / "plugin-errors.jsonl"
    hook_error_count = 0
    if hook_error_log.exists():
        hook_error_count = sum(1 for line in hook_error_log.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
    add("runtime-hook-errors", hook_error_count == 0, "warning", f"Runtime hook error log entries: {hook_error_count}.", "Inspect .agent-control/logs/plugin-errors.jsonl and fix plugin install issues.")
    session_events = list((root / "agent-memory" / "sessions").glob("**/events.jsonl")) if (root / "agent-memory" / "sessions").exists() else []
    oversized_sessions = [path for path in session_events if path.stat().st_size > 5_000_000]
    add("runtime-session-log-size", not oversized_sessions, "warning", f"Oversized runtime event logs: {len(oversized_sessions)}.", "Close sessions, compact summaries, or rotate private runtime logs.")
    add("private-session-events", not session_events, "info", f"Private raw event logs found: {len(session_events)}.", "Keep raw events private; compact and redact before sharing.")
    shared_unsafe = []
    for record in load_memory_records(root, include_sessions=False):
        meta = record["metadata"]
        if meta.get("visibility") == "shared" and (
            meta.get("review_status") != "approved"
            or meta.get("sanitization_status") != "approved"
            or meta.get("data_class") not in SHARED_ALLOWED_DATA_CLASSES
        ):
            shared_unsafe.append(record["source_path"])
    add("shared-export-safe", not shared_unsafe, "error", f"Unsafe shared records: {len(shared_unsafe)}.", "Approve review and sanitization before shared export.")
    failed = [check for check in checks if not check["passed"] and check["severity"] in {"error", "warning"}]
    score = max(0, 100 - sum(15 if check["severity"] == "error" else 5 for check in failed))
    return {"project": str(root), "score": score, "passed": not any(check for check in checks if not check["passed"] and check["severity"] == "error"), "checks": checks, "unsafe_shared_records": shared_unsafe}


def compliance_bool(meta: dict[str, Any], key: str, default: bool = False) -> bool:
    value = meta.get(key)
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def compliance_record_type(meta: dict[str, Any], path: pathlib.Path) -> str:
    value = str(meta.get("compliance_record_type") or "").strip()
    if value in COMPLIANCE_RECORD_TYPES:
        return value
    name = path.name.lower()
    if "processing" in name:
        return "processing_activity"
    if "ai-system" in name or "ai_system" in name:
        return "ai_system"
    if "provider" in name:
        return "provider"
    if "dpia" in name or "dsfa" in name:
        return "dpia_trigger"
    if "data-subject" in name or "dsar" in name:
        return "data_subject_request"
    if "incident" in name:
        return "security_incident"
    return ""


def compliance_markdown_records(root: pathlib.Path) -> list[dict[str, Any]]:
    base = root / "agent-memory" / "compliance"
    if not base.exists():
        return []
    records = []
    for path in sorted(base.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        rel = str(path.relative_to(root)).replace("\\", "/")
        records.append(
            {
                "path": path,
                "source_path": rel,
                "metadata": meta,
                "record_type": compliance_record_type(meta, path),
                "body": markdown_body(text),
            }
        )
    return records


def _missing_required(meta: dict[str, Any], keys: list[str]) -> list[str]:
    missing = []
    for key in keys:
        value = meta.get(key)
        if value is None or value == "" or str(value).strip().upper().startswith("TODO"):
            missing.append(key)
    return missing


def compliance_doctor(root: pathlib.Path) -> dict[str, Any]:
    checks = []

    def add(name: str, passed: bool, severity: str, details: str, fix: str = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "severity": severity, "details": details, "fix": fix})

    profile_path = root / COMPLIANCE_PROFILE_REL
    installed = profile_path.exists()
    add(
        "compliance-layer-installed",
        installed,
        "error",
        "Compliance Light profile is present." if installed else "Compliance Light add-on is not installed.",
        "Build a project kit with --include-compliance or copy the Compliance Light files listed in addons/compliance-light/addon.json.",
    )
    if not installed:
        failed = [check for check in checks if not check["passed"] and check["severity"] in {"error", "warning"}]
        return {
            "project": str(root),
            "generated_at": utc_now(),
            "installed": False,
            "score": 0,
            "passed": False,
            "checks": checks,
            "blocking_findings": failed,
            "warnings": [],
            "policy": "compliance-light-v0.1-read-only",
        }

    profile = parse_frontmatter(profile_path.read_text(encoding="utf-8", errors="replace"))
    records = compliance_markdown_records(root)
    by_type: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if record["record_type"]:
            by_type.setdefault(record["record_type"], []).append(record)

    mode = str(profile.get("compliance_mode") or "").strip()
    add("compliance-mode-light", mode == "light", "error", f"compliance_mode={mode or '[missing]'}", "Set compliance_mode: light in agent-memory/compliance/profile.md.")
    add("compliance-owner", bool(str(profile.get("owner") or "").strip()), "warning", "Compliance owner is set.", "Set owner in the compliance profile.")
    add("jurisdictions", bool(profile.get("jurisdictions")), "warning", "Jurisdictions are declared.", "Add jurisdictions such as EU and DE to the compliance profile.")

    personal_data = compliance_bool(profile, "personal_data_allowed")
    customer_data = compliance_bool(profile, "customer_data_allowed")
    external_providers = compliance_bool(profile, "external_ai_providers")
    high_impact_ai = compliance_bool(profile, "high_impact_ai")
    shared_exports = compliance_bool(profile, "shared_exports_allowed")

    processing_required = personal_data or customer_data or shared_exports
    processing_records = by_type.get("processing_activity", [])
    add(
        "processing-activity",
        (not processing_required) or bool(processing_records),
        "error",
        f"Processing activity records: {len(processing_records)}; required={processing_required}.",
        "Create a processing activity from agent-memory/templates/processing-activity-template.md.",
    )
    for record in processing_records:
        missing = _missing_required(record["metadata"], ["purpose", "legal_basis", "data_categories", "retention_class", "owner"])
        add(
            f"processing-activity-fields:{record['source_path']}",
            not missing,
            "error",
            "Required fields present." if not missing else "Missing fields: " + ", ".join(missing),
            "Fill purpose, legal_basis, data_categories, retention_class, and owner.",
        )

    provider_records = by_type.get("provider", [])
    add(
        "provider-registry",
        (not external_providers) or bool(provider_records),
        "error",
        f"Provider records: {len(provider_records)}; required={external_providers}.",
        "Create a provider registry record from agent-memory/templates/provider-registry-template.md.",
    )
    for record in provider_records:
        missing = _missing_required(record["metadata"], ["provider_name", "processing_role", "region", "data_use_policy", "retention_policy"])
        add(
            f"provider-fields:{record['source_path']}",
            not missing,
            "error",
            "Required fields present." if not missing else "Missing fields: " + ", ".join(missing),
            "Fill provider_name, processing_role, region, data_use_policy, and retention_policy.",
        )

    ai_system_required = external_providers or high_impact_ai
    ai_records = by_type.get("ai_system", [])
    add(
        "ai-system-inventory",
        (not ai_system_required) or bool(ai_records),
        "error",
        f"AI system records: {len(ai_records)}; required={ai_system_required}.",
        "Create an AI system inventory record from agent-memory/templates/ai-system-template.md.",
    )
    for record in ai_records:
        missing = _missing_required(record["metadata"], ["system_name", "purpose", "model_provider", "autonomy_level", "human_oversight", "risk_class"])
        add(
            f"ai-system-fields:{record['source_path']}",
            not missing,
            "error",
            "Required fields present." if not missing else "Missing fields: " + ", ".join(missing),
            "Fill system_name, purpose, model_provider, autonomy_level, human_oversight, and risk_class.",
        )

    dpia_required = high_impact_ai or (personal_data and external_providers)
    dpia_records = by_type.get("dpia_trigger", [])
    add(
        "dpia-trigger",
        (not dpia_required) or bool(dpia_records),
        "error",
        f"DPIA trigger records: {len(dpia_records)}; required={dpia_required}.",
        "Create a DPIA trigger record from agent-memory/templates/dpia-trigger-template.md.",
    )

    shared_unsafe = []
    for record in load_memory_records(root, include_sessions=False):
        meta = record["metadata"]
        if meta.get("visibility") == "shared" and (
            meta.get("review_status") != "approved"
            or meta.get("sanitization_status") != "approved"
            or meta.get("data_class") not in SHARED_ALLOWED_DATA_CLASSES
        ):
            shared_unsafe.append(record["source_path"])
    add("shared-export-safe", not shared_unsafe, "error", f"Unsafe shared records: {len(shared_unsafe)}.", "Approve review and sanitization before shared export.")

    retention = audit_retention(root)
    add("retention-audit", bool(retention["passed"]), "error", f"Retention errors: {retention.get('counts', {}).get('error', 0)}.", "Run audit-retention and review expired records.")
    sensitive = scan_sensitive_data(root)
    add("sensitive-data-scan", bool(sensitive["passed"]), "error", f"Sensitive-data errors: {sensitive.get('counts', {}).get('error', 0)}.", "Redact secrets or sensitive content before export.")
    add("compliance-reports-ignored", bool(_gitignore_contains(root, "agent-memory/exports/compliance/")), "warning", "Compliance reports are ignored by git.", "Add agent-memory/exports/compliance/ to .gitignore.")

    blocking = [check for check in checks if not check["passed"] and check["severity"] == "error"]
    warnings = [check for check in checks if not check["passed"] and check["severity"] == "warning"]
    score = max(0, 100 - (25 * len(blocking)) - (5 * len(warnings)))
    return {
        "project": str(root),
        "generated_at": utc_now(),
        "installed": True,
        "score": score,
        "passed": not blocking,
        "checks": checks,
        "blocking_findings": blocking,
        "warnings": warnings,
        "policy": "compliance-light-v0.1-read-only",
    }


def _gitignore_contains(root: pathlib.Path, pattern: str) -> bool:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        return False
    return pattern in {line.strip() for line in gitignore.read_text(encoding="utf-8", errors="replace").splitlines()}


def memory_index_row(record: dict[str, Any]) -> dict[str, Any]:
    meta = record["metadata"]
    return {
        "memory_id": meta.get("memory_id"),
        "tenant_id": meta.get("tenant_id"),
        "customer_id": meta.get("customer_id"),
        "project_id": meta.get("project_id"),
        "doc_type": meta.get("doc_type"),
        "status": meta.get("status"),
        "visibility": meta.get("visibility"),
        "data_class": meta.get("data_class"),
        "semantic_title": meta.get("semantic_title", meta.get("title", "")),
        "summary": meta.get("summary", ""),
        "concept_tags": meta.get("concept_tags", []),
        "stack_tags": meta.get("stack_tags", []),
        "problem_patterns": meta.get("problem_patterns", []),
        "architecture_patterns": meta.get("architecture_patterns", []),
        "failure_modes": meta.get("failure_modes", []),
        "reusable_lessons": meta.get("reusable_lessons", []),
        "edges": meta.get("edges", []),
        "source_path": record["source_path"],
        "source_hash": record["source_hash"],
        "updated_at": meta.get("updated_at", ""),
    }


def read_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def memory_index_manifest_row(root: pathlib.Path, record: dict[str, Any]) -> dict[str, Any]:
    path = root / record["source_path"]
    stat = path.stat()
    return {
        "memory_id": record["metadata"].get("memory_id"),
        "source_path": record["source_path"],
        "source_hash": record["source_hash"],
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def read_memory_index_manifest(path: pathlib.Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return {}
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        return {}
    result = {}
    for record in records:
        if isinstance(record, dict) and record.get("source_path"):
            result[str(record["source_path"])] = record
    return result


def write_memory_index_outputs(
    root: pathlib.Path,
    rows: list[dict[str, Any]],
    records_by_path: dict[str, dict[str, Any]],
    mode: str,
) -> tuple[pathlib.Path, pathlib.Path]:
    out = root / "agent-memory" / "indexes" / "memory-index.jsonl"
    manifest_path = root / "agent-memory" / "indexes" / "memory-index-manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else "")
    manifest = {
        "schema_version": 1,
        "mode": mode,
        "generated_at": utc_now(),
        "index_path": str(out.relative_to(root)).replace("\\", "/"),
        "rows": len(rows),
        "records": [memory_index_manifest_row(root, records_by_path[row["source_path"]]) for row in rows],
    }
    locked_atomic_write_text(out, payload)
    locked_atomic_write_text(manifest_path, json.dumps(manifest, sort_keys=True) + "\n")
    return out, manifest_path


def build_memory_index(root: pathlib.Path, incremental: bool = False, track_tombstones: bool = False) -> dict[str, Any]:
    records = load_memory_records(root, include_sessions=True)
    records_by_path = {record["source_path"]: record for record in records}
    out = root / "agent-memory" / "indexes" / "memory-index.jsonl"
    manifest_path = root / "agent-memory" / "indexes" / "memory-index-manifest.json"
    tombstone_path = root / "agent-memory" / "indexes" / "memory-index-tombstones.jsonl"
    mode = "incremental" if incremental else "full"

    rows = []
    changed = 0
    unchanged = 0
    deleted = 0
    new_tombstones: list[dict[str, Any]] = []

    if incremental:
        previous_rows = read_jsonl(out)
        previous_by_path = {str(row["source_path"]): row for row in previous_rows if row.get("source_path")}
        previous_manifest = read_memory_index_manifest(manifest_path)
        previous_paths = set(previous_manifest) if previous_manifest else set(previous_by_path)
        current_paths = set(records_by_path)
        deleted_at = utc_now()
        for source_path in sorted(previous_paths - current_paths):
            previous = previous_manifest.get(source_path) or previous_by_path.get(source_path, {})
            source_exists = (root / source_path).exists()
            new_tombstones.append(
                {
                    "memory_id": previous.get("memory_id"),
                    "source_path": source_path,
                    "source_hash": previous.get("source_hash"),
                    "deleted_at": deleted_at,
                    "reason": "source_missing" if not source_exists else "record_not_indexable",
                }
            )
        deleted = len(new_tombstones)

        for source_path in sorted(current_paths):
            record = records_by_path[source_path]
            previous_row = previous_by_path.get(source_path)
            previous_fingerprint = previous_manifest.get(source_path) or previous_row or {}
            if (
                previous_row
                and previous_row.get("source_hash") == record["source_hash"]
                and previous_fingerprint.get("source_hash") == record["source_hash"]
                and (root / source_path).exists()
            ):
                rows.append(previous_row)
                unchanged += 1
            else:
                rows.append(memory_index_row(record))
                changed += 1
    else:
        for record in records:
            rows.append(memory_index_row(record))
        changed = len(rows)

    rows.sort(key=lambda row: str(row.get("source_path", "")))
    out, manifest_path = write_memory_index_outputs(root, rows, records_by_path, mode)

    result: dict[str, Any] = {
        "path": str(out.relative_to(root)).replace("\\", "/"),
        "rows": len(rows),
        "changed": changed,
        "unchanged": unchanged,
        "deleted": deleted,
        "tombstoned": deleted,
        "mode": mode,
        "manifest_path": str(manifest_path.relative_to(root)).replace("\\", "/"),
    }

    if track_tombstones:
        existing_tombstones = read_jsonl(tombstone_path)
        seen = {
            (
                tombstone.get("memory_id"),
                tombstone.get("source_path"),
                tombstone.get("source_hash"),
            )
            for tombstone in existing_tombstones
        }
        combined_tombstones = list(existing_tombstones)
        for tombstone in new_tombstones:
            key = (tombstone.get("memory_id"), tombstone.get("source_path"), tombstone.get("source_hash"))
            if key not in seen:
                combined_tombstones.append(tombstone)
                seen.add(key)
        locked_atomic_write_text(
            tombstone_path,
            "\n".join(json.dumps(row, sort_keys=True) for row in combined_tombstones) + ("\n" if combined_tombstones else ""),
        )
        result["tombstone_path"] = str(tombstone_path.relative_to(root)).replace("\\", "/")

    return result

def scope_rejection_reason(
    meta: dict[str, Any],
    tenant_id: str | None = None,
    customer_id: str | None = None,
    project_id: str | None = None,
    allow_global_user: bool = False,
) -> str | None:
    if allow_global_user and meta.get("doc_type") in GLOBAL_USER_DOC_TYPES:
        return None
    if tenant_id and meta.get("tenant_id") != tenant_id:
        return "tenant_scope_mismatch"
    if customer_id and meta.get("customer_id") != customer_id:
        return "customer_scope_mismatch"
    if project_id and meta.get("project_id") != project_id:
        return "project_scope_mismatch"
    return None


def rag_rejection_reason(meta: dict[str, Any], corpus_type: str, include_sessions: bool, include_drafts: bool) -> str | None:
    doc_type = meta.get("doc_type")
    if doc_type in RAW_PRIVATE_DOC_TYPES:
        return "personal_raw_doc_type_excluded"
    if doc_type not in DEFAULT_RAG_DOC_TYPES and not include_sessions:
        return "doc_type_not_in_default_rag"
    if RUNTIME_DRAFT_TAG in (meta.get("concept_tags") or []):
        return "runtime_summary_draft"
    if doc_type == "session" and not include_sessions:
        return "session_excluded"
    if include_drafts:
        if meta.get("status") not in {"draft", "active", "reviewed", "promoted"}:
            return "status_not_exportable"
    else:
        if meta.get("status") not in RAG_REVIEWED_STATUSES:
            return "status_not_reviewed_or_promoted"
        if meta.get("review_status") not in RAG_REVIEWED_REVIEW_STATUSES:
            return "not_reviewed_or_promoted"
    if corpus_type == "shared":
        if meta.get("visibility") != "shared":
            return "not_shared_visibility"
        if meta.get("review_status") != "approved":
            return "review_not_approved"
        if meta.get("sanitization_status") != "approved":
            return "sanitization_not_approved"
        if meta.get("data_class") not in SHARED_ALLOWED_DATA_CLASSES:
            return "data_class_not_allowed"
    return None


def export_rag_documents(
    root: pathlib.Path,
    corpus_type: str = "private",
    include_sessions: bool = False,
    include_drafts: bool = False,
    tenant_id: str | None = None,
    customer_id: str | None = None,
    project_id: str | None = None,
) -> dict[str, Any]:
    rows = []
    rejected: dict[str, int] = {}
    for record in load_memory_records(root, include_sessions=include_sessions):
        meta = record["metadata"]
        reason = scope_rejection_reason(meta, tenant_id, customer_id, project_id) or rag_rejection_reason(meta, corpus_type, include_sessions, include_drafts)
        if reason:
            rejected[reason] = rejected.get(reason, 0) + 1
            continue
        rows.append(
            {
                "memory_id": meta["memory_id"],
                "metadata": {k: v for k, v in meta.items() if k != "edges"},
                "content": retrieval_header(meta) + "\n" + record["body"],
                "relationships": meta.get("edges", []),
                "source_path": record["source_path"],
                "source_hash": record["source_hash"],
            }
        )
    out_dir = root / "agent-memory" / "exports" / "rag"
    out_dir.mkdir(parents=True, exist_ok=True)
    generation_id = unique_run_id(f"{corpus_type}-rag")
    generation_dir = out_dir / generation_id
    generation_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{corpus_type}-documents.jsonl"
    payload = "\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else "")
    manifest = {
        "generated_at": utc_now(),
        "generation_id": generation_id,
        "policy_version": "rag-export-v0.2",
        "corpus_type": corpus_type,
        "include_sessions": include_sessions,
        "include_drafts": include_drafts,
        "tenant_id": tenant_id or "",
        "customer_id": customer_id or "",
        "project_id": project_id or "",
        "accepted_count": len(rows),
        "rejected_counts": rejected,
        "filters": {
            "default_doc_types": sorted(DEFAULT_RAG_DOC_TYPES),
            "shared_requires": ["visibility=shared", "review_status=approved", "sanitization_status=approved", f"data_class in {sorted(SHARED_ALLOWED_DATA_CLASSES)}"],
            "private_default": "reviewed/promoted records only unless include_drafts=true",
        },
    }
    manifest_path = out_dir / f"{corpus_type}-manifest.json"
    generation_out = generation_dir / "documents.jsonl"
    generation_manifest = generation_dir / "manifest.json"
    with file_lock(out_dir / f".{corpus_type}.export.lock", timeout_seconds=60):
        atomic_write_text(generation_out, payload)
        atomic_write_text(generation_manifest, json.dumps(manifest, indent=2, sort_keys=True))
        atomic_write_text(out, payload)
        atomic_write_text(manifest_path, json.dumps(manifest, indent=2, sort_keys=True))
        atomic_write_text(out_dir / f"{corpus_type}-latest.json", json.dumps({"generation_id": generation_id, "documents": str(generation_out.relative_to(root)), "manifest": str(generation_manifest.relative_to(root))}, indent=2, sort_keys=True))
    return {
        "path": str(out.relative_to(root)),
        "rows": len(rows),
        "corpus_type": corpus_type,
        "manifest": str(manifest_path.relative_to(root)),
        "generation_id": generation_id,
        "generation_path": str(generation_dir.relative_to(root)),
        "generation_documents": str(generation_out.relative_to(root)),
        "generation_manifest": str(generation_manifest.relative_to(root)),
        "rejected_counts": rejected,
    }


def export_lightrag(
    root: pathlib.Path,
    tenant_id: str | None = None,
    customer_id: str | None = None,
    project_id: str | None = None,
    corpus_type: str = "private",
    include_drafts: bool = False,
) -> dict[str, Any]:
    rag_result = export_rag_documents(
        root,
        corpus_type=corpus_type,
        include_drafts=include_drafts,
        tenant_id=tenant_id,
        customer_id=customer_id,
        project_id=project_id,
    )
    rag_path = root / rag_result["generation_documents"]
    rows = [json.loads(line) for line in rag_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    out_dir = root / "agent-memory" / "exports" / "lightrag"
    out_dir.mkdir(parents=True, exist_ok=True)
    generation_id = unique_run_id(f"{corpus_type}-lightrag")
    generation_dir = out_dir / generation_id
    generation_dir.mkdir(parents=True, exist_ok=True)
    export_rows = []
    texts = []
    ids = []
    file_paths = []
    for row in rows:
        meta = row["metadata"]
        export_row = {
            "doc_id": row["memory_id"],
            "memory_id": row["memory_id"],
            "tenant_id": meta.get("tenant_id", ""),
            "customer_id": meta.get("customer_id", ""),
            "project_id": meta.get("project_id", ""),
            "source_path": row["source_path"],
            "source_hash": row["source_hash"],
            "data_class": meta.get("data_class", "internal"),
            "acl": meta.get("acl", [meta.get("tenant_id", "")]) if isinstance(meta.get("acl", []), list) else [meta.get("tenant_id", "")],
            "content": row["content"],
        }
        export_rows.append(export_row)
        ids.append(export_row["doc_id"])
        texts.append(export_row["content"])
        file_paths.append(export_row["source_path"])
    manifest = {
        "generated_at": utc_now(),
        "generation_id": generation_id,
        "corpus_type": corpus_type,
        "tenant_id": tenant_id or "",
        "customer_id": customer_id or "",
        "project_id": project_id or "",
        "document_count": len(export_rows),
        "rag_manifest": rag_result.get("generation_manifest", rag_result.get("manifest", "")),
        "rag_generation_id": rag_result.get("generation_id", ""),
        "policy_version": "lightrag-export-v0.2",
        "documents": [{"memory_id": row["memory_id"], "source_path": row["source_path"], "source_hash": row["source_hash"]} for row in export_rows],
    }
    writes = {
        "lightrag-export.jsonl": "\n".join(json.dumps(row, sort_keys=True) for row in export_rows) + ("\n" if export_rows else ""),
        "texts.json": json.dumps(texts, indent=2),
        "ids.json": json.dumps(ids, indent=2),
        "file_paths.json": json.dumps(file_paths, indent=2),
        "manifest.json": json.dumps(manifest, indent=2, sort_keys=True),
    }
    with file_lock(out_dir / ".lightrag-export.lock", timeout_seconds=60):
        for name, text in writes.items():
            atomic_write_text(generation_dir / name, text)
            atomic_write_text(out_dir / name, text)
        atomic_write_text(out_dir / "latest.json", json.dumps({"generation_id": generation_id, "path": str(generation_dir.relative_to(root)), "manifest": str((generation_dir / "manifest.json").relative_to(root))}, indent=2, sort_keys=True))
    return {"path": str((out_dir / "lightrag-export.jsonl").relative_to(root)), "rows": len(export_rows), "manifest": str((out_dir / "manifest.json").relative_to(root)), "generation_id": generation_id, "generation_path": str(generation_dir.relative_to(root))}


def export_graphrag(
    root: pathlib.Path,
    corpus_type: str = "private",
    include_drafts: bool = False,
    tenant_id: str | None = None,
    customer_id: str | None = None,
    project_id: str | None = None,
) -> dict[str, Any]:
    nodes = []
    edges = []
    rejected: dict[str, int] = {}
    accepted_ids: set[str] = set()
    for record in load_memory_records(root, include_sessions=False):
        meta = record["metadata"]
        reason = scope_rejection_reason(meta, tenant_id, customer_id, project_id) or rag_rejection_reason(meta, corpus_type, include_sessions=False, include_drafts=include_drafts)
        if reason:
            rejected[reason] = rejected.get(reason, 0) + 1
            continue
        accepted_ids.add(str(meta["memory_id"]))
        nodes.append(
            {
                "id": meta["memory_id"],
                "label": meta.get("semantic_title", meta["memory_id"]),
                "type": meta.get("doc_type"),
                "metadata": {k: v for k, v in meta.items() if k != "edges"},
                "source_path": record["source_path"],
            }
        )
        for edge in meta.get("edges", []):
            if isinstance(edge, dict):
                edges.append(
                    {
                        "source": meta["memory_id"],
                        "target": edge.get("target", ""),
                        "type": edge.get("type", "relates_to"),
                        "reason": edge.get("reason", ""),
                        "confidence": edge.get("confidence", 0),
                    }
                )
    edges = [edge for edge in edges if edge["source"] in accepted_ids and (not str(edge["target"]).startswith("mem:") or edge["target"] in accepted_ids)]
    out_dir = root / "agent-memory" / "exports" / "graphrag"
    out_dir.mkdir(parents=True, exist_ok=True)
    generation_id = unique_run_id(f"{corpus_type}-graphrag")
    generation_dir = out_dir / generation_id
    generation_dir.mkdir(parents=True, exist_ok=True)
    nodes_payload = "\n".join(json.dumps(row, sort_keys=True) for row in nodes) + ("\n" if nodes else "")
    edges_payload = "\n".join(json.dumps(row, sort_keys=True) for row in edges) + ("\n" if edges else "")
    manifest = {
        "generated_at": utc_now(),
        "generation_id": generation_id,
        "policy_version": "graphrag-export-v0.2",
        "corpus_type": corpus_type,
        "include_drafts": include_drafts,
        "tenant_id": tenant_id or "",
        "customer_id": customer_id or "",
        "project_id": project_id or "",
        "accepted_nodes": len(nodes),
        "accepted_edges": len(edges),
        "rejected_counts": rejected,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_payload = json.dumps(manifest, indent=2, sort_keys=True)
    with file_lock(out_dir / ".graphrag-export.lock", timeout_seconds=60):
        atomic_write_text(generation_dir / "nodes.jsonl", nodes_payload)
        atomic_write_text(generation_dir / "edges.jsonl", edges_payload)
        atomic_write_text(generation_dir / "manifest.json", manifest_payload)
        atomic_write_text(out_dir / "nodes.jsonl", nodes_payload)
        atomic_write_text(out_dir / "edges.jsonl", edges_payload)
        atomic_write_text(manifest_path, manifest_payload)
        atomic_write_text(out_dir / "latest.json", json.dumps({"generation_id": generation_id, "path": str(generation_dir.relative_to(root)), "manifest": str((generation_dir / "manifest.json").relative_to(root))}, indent=2, sort_keys=True))
    return {"nodes": len(nodes), "edges": len(edges), "nodes_path": str((out_dir / "nodes.jsonl").relative_to(root)), "edges_path": str((out_dir / "edges.jsonl").relative_to(root)), "manifest": str(manifest_path.relative_to(root)), "generation_id": generation_id, "generation_path": str(generation_dir.relative_to(root)), "rejected_counts": rejected}


def tokenize(value: Any) -> list[str]:
    text = str(value or "").lower()
    return [token for token in re.findall(r"[a-z0-9][a-z0-9-]{1,}", text) if token not in STOP_WORDS]


def list_text(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value or "")


def retrieval_document_text(record: dict[str, Any]) -> dict[str, str]:
    meta = record["metadata"]
    return {
        "title": str(meta.get("semantic_title", meta.get("title", ""))),
        "summary": str(meta.get("summary", "")),
        "tags": " ".join(
            [
                list_text(meta.get("concept_tags", [])),
                list_text(meta.get("stack_tags", [])),
                list_text(meta.get("problem_patterns", [])),
                list_text(meta.get("architecture_patterns", [])),
                list_text(meta.get("failure_modes", [])),
                list_text(meta.get("reusable_lessons", [])),
            ]
        ),
        "body": record.get("body", ""),
    }


def collect_retrieval_corpus(project_roots: list[pathlib.Path], include_sessions: bool = False) -> list[dict[str, Any]]:
    corpus = []
    now_ts = time.time()
    for root in project_roots:
        for record in load_memory_records(root, include_sessions=include_sessions):
            meta = record["metadata"]
            if not include_sessions:
                if meta.get("doc_type") not in DEFAULT_RAG_DOC_TYPES:
                    continue
                if meta.get("status") not in {"active", "reviewed", "promoted"}:
                    continue
            fields = retrieval_document_text(record)
            text = "\n".join(fields.values())
            corpus.append(
                {
                    "memory_id": meta.get("memory_id"),
                    "project_root": str(root),
                    "project_id": meta.get("project_id", ""),
                    "tenant_id": meta.get("tenant_id", ""),
                    "customer_id": meta.get("customer_id", ""),
                    "doc_type": meta.get("doc_type", ""),
                    "status": meta.get("status", ""),
                    "visibility": meta.get("visibility", ""),
                    "data_class": meta.get("data_class", ""),
                    "review_status": meta.get("review_status", ""),
                    "sanitization_status": meta.get("sanitization_status", ""),
                    "semantic_title": fields["title"],
                    "summary": fields["summary"],
                    "source_path": record["source_path"],
                    "source_hash": record["source_hash"],
                    "fields": fields,
                    "text": text,
                    "freshness_warnings": memory_freshness_warnings(meta, now_ts=now_ts),
                    "tokens": {
                        "title": tokenize(fields["title"]),
                        "summary": tokenize(fields["summary"]),
                        "tags": tokenize(fields["tags"]),
                        "body": tokenize(fields["body"]),
                    },
                    "metadata": meta,
                }
            )
    return corpus


def score_retrieval_doc(query: str, doc: dict[str, Any]) -> dict[str, Any]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return {"score": 0.0, "score_breakdown": {}}
    qset = set(query_tokens)
    weights = {"title": 7.0, "summary": 5.0, "tags": 4.0, "body": 1.0}
    score = 0.0
    field_scores: dict[str, float] = {}
    for field, weight in weights.items():
        tokens = doc["tokens"].get(field, [])
        if not tokens:
            field_scores[field] = 0.0
            continue
        counts: dict[str, int] = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
        field_score = 0.0
        for token in qset:
            if token in counts:
                field_score += weight * (1.0 + min(counts[token], 3) * 0.15)
        field_scores[field] = round(field_score, 6)
        score += field_score
    normalized_query = " ".join(query_tokens)
    normalized_text = " ".join(tokenize(doc["text"]))
    phrase_bonus = 12.0 if normalized_query and normalized_query in normalized_text else 0.0
    score += phrase_bonus
    coverage = len(qset & set(tokenize(doc["text"]))) / max(1, len(qset))
    status_boost = 1.15 if doc.get("status") in {"reviewed", "promoted"} else 1.0
    review_boost = 1.1 if doc.get("review_status") == "approved" else 1.0
    final = round(score * (0.7 + coverage) * status_boost * review_boost, 6)
    return {
        "score": final,
        "score_breakdown": {
            "fields": field_scores,
            "phrase_bonus": phrase_bonus,
            "coverage": round(coverage, 6),
            "status_boost": status_boost,
            "review_boost": review_boost,
            "pre_boost_score": round(score, 6),
            "final_score": final,
        },
    }


def retrieve_memory(query: str, corpus: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
    scored = []
    for doc in corpus:
        scored_result = score_retrieval_doc(query, doc)
        score = scored_result["score"]
        if score <= 0:
            continue
        scored.append(
            {
                "memory_id": doc["memory_id"],
                "project_id": doc["project_id"],
                "doc_type": doc["doc_type"],
                "status": doc["status"],
                "visibility": doc["visibility"],
                "semantic_title": doc["semantic_title"],
                "summary": doc["summary"],
                "source_path": doc["source_path"],
                "score": score,
                "score_breakdown": scored_result["score_breakdown"],
                "freshness_warnings": doc.get("freshness_warnings", []),
            }
        )
    return sorted(scored, key=lambda row: (-row["score"], row["memory_id"]))[:top_k]


def ndcg_at_k(relevances: list[int], k: int) -> float:
    gains = relevances[:k]
    dcg = sum((2**rel - 1) / math.log2(idx + 2) for idx, rel in enumerate(gains))
    ideal = sorted(relevances, reverse=True)[:k]
    idcg = sum((2**rel - 1) / math.log2(idx + 2) for idx, rel in enumerate(ideal))
    return 0.0 if idcg == 0 else dcg / idcg


def default_retrieval_queries(corpus: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def ids_containing(*parts: str) -> list[str]:
        selected = []
        for doc in corpus:
            haystack = " ".join([doc["memory_id"], doc["semantic_title"], doc["summary"], doc["text"]]).lower()
            if all(part.lower() in haystack for part in parts):
                selected.append(doc["memory_id"])
        return selected

    return [
        {
            "name": "rag-safety",
            "query": "private raw events reviewed promotion shared RAG pollution",
            "expected_ids": ids_containing("raw", "rag") + ids_containing("reviewed", "promotion"),
            "expect_projects": ["cowork-agency-demo", "zeus-agent-agency"],
        },
        {
            "name": "multimodal-graphrag",
            "query": "multimodal GraphRAG knowledgebase hundreds agents agency substrate",
            "expected_ids": ids_containing("graphrag") + ids_containing("knowledgebase"),
            "expect_projects": ["zeus-agent-agency"],
        },
        {
            "name": "agency-repeatability",
            "query": "agency delivery repeatability agent context fragmentation reusable client intelligence",
            "expected_ids": ids_containing("agency", "delivery") + ids_containing("context", "fragmentation"),
            "expect_projects": ["cowork-agency-demo", "zeus-agent-agency"],
        },
        {
            "name": "positioning-brand-website",
            "query": "Zeus positioning brand website AI-first agency operating system",
            "expected_ids": ids_containing("positioning") + ids_containing("website"),
            "expect_projects": ["zeus-agent-agency"],
        },
        {
            "name": "harness-runtime",
            "query": "custom agent harness Codex Claude Cowork Hermes OpenClaw PI Agents",
            "expected_ids": ids_containing("harness") + ids_containing("runtime"),
            "expect_projects": ["zeus-agent-agency"],
        },
    ]


def load_retrieval_queries(path: pathlib.Path | None) -> list[dict[str, Any]] | None:
    if not path:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    queries = data.get("queries") if isinstance(data, dict) else data
    if not isinstance(queries, list):
        raise ValueError("Retrieval queries file must contain a JSON array or an object with a queries array.")
    normalized = []
    for idx, query in enumerate(queries):
        if not isinstance(query, dict):
            raise ValueError(f"Retrieval query {idx} must be an object.")
        if not query.get("query"):
            raise ValueError(f"Retrieval query {idx} missing query.")
        normalized.append(
            {
                "name": str(query.get("name") or f"query-{idx + 1}"),
                "query": str(query["query"]),
                "expected_ids": list(query.get("expected_ids") or []),
                "expect_projects": list(query.get("expect_projects") or []),
            }
        )
    return normalized


def cross_project_parallel_candidates(corpus: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fields = ["concept_tags", "stack_tags", "problem_patterns", "architecture_patterns", "failure_modes", "reusable_lessons"]
    candidates = []
    for i, left in enumerate(corpus):
        left_meta = left["metadata"]
        for right in corpus[i + 1 :]:
            if left["project_id"] == right["project_id"]:
                continue
            right_meta = right["metadata"]
            matches: dict[str, list[str]] = {}
            for field in fields:
                lvals = set(str(v).lower() for v in left_meta.get(field, []) if str(v).strip()) if isinstance(left_meta.get(field), list) else set()
                rvals = set(str(v).lower() for v in right_meta.get(field, []) if str(v).strip()) if isinstance(right_meta.get(field), list) else set()
                common = sorted(lvals & rvals)
                if common:
                    matches[field] = common
            left_semantic = set(tokenize(" ".join([left["semantic_title"], left["summary"], list_text(left_meta.get("reusable_lessons", []))])))
            right_semantic = set(tokenize(" ".join([right["semantic_title"], right["summary"], list_text(right_meta.get("reusable_lessons", []))])))
            semantic_common = sorted((left_semantic & right_semantic) - STOP_WORDS)
            semantic_union = left_semantic | right_semantic
            semantic_similarity = len(semantic_common) / max(1, len(semantic_union))
            if len(semantic_common) >= 3 or semantic_similarity >= 0.12:
                matches["semantic_tokens"] = semantic_common[:12]
            if matches:
                candidates.append(
                    {
                        "left": left["memory_id"],
                        "left_project": left["project_id"],
                        "right": right["memory_id"],
                        "right_project": right["project_id"],
                        "matches": matches,
                        "match_weight": sum(len(values) for values in matches.values()),
                        "semantic_similarity": round(semantic_similarity, 4),
                    }
                )
    return sorted(candidates, key=lambda row: (-row["match_weight"], row["left"], row["right"]))


def evaluate_memory_retrieval(
    root: pathlib.Path,
    project_roots: list[pathlib.Path],
    output_dir: pathlib.Path | None = None,
    top_k: int = 5,
    include_sessions: bool = False,
    queries_file: pathlib.Path | None = None,
    min_overall_score: float | None = None,
    min_safety_score: float | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()
    corpus = collect_retrieval_corpus(project_roots, include_sessions=include_sessions)
    build_seconds = time.perf_counter() - start
    queries = load_retrieval_queries(queries_file) or default_retrieval_queries(corpus)
    query_results = []
    query_latencies = []
    for query in queries:
        qstart = time.perf_counter()
        hits = retrieve_memory(query["query"], corpus, top_k=top_k)
        latency = time.perf_counter() - qstart
        query_latencies.append(latency)
        expected = set(query.get("expected_ids", []))
        hit_ids = [hit["memory_id"] for hit in hits]
        relevant_flags = [1 if mid in expected else 0 for mid in hit_ids]
        first_relevant = next((idx + 1 for idx, flag in enumerate(relevant_flags) if flag), None)
        projects_found = sorted(set(hit["project_id"] for hit in hits))
        expected_projects = set(query.get("expect_projects", []))
        query_results.append(
            {
                "name": query["name"],
                "query": query["query"],
                "expected_count": len(expected),
                "hits": hits,
                "precision_at_k": sum(relevant_flags) / max(1, len(hits)),
                "recall_at_k": sum(relevant_flags) / max(1, len(expected)),
                "mrr": 0.0 if first_relevant is None else 1.0 / first_relevant,
                "ndcg_at_k": ndcg_at_k(relevant_flags, top_k),
                "projects_found": projects_found,
                "project_coverage": len(expected_projects & set(projects_found)) / max(1, len(expected_projects)),
                "latency_ms": round(latency * 1000, 3),
            }
        )
    parallels = cross_project_parallel_candidates(corpus)
    project_ids = sorted(set(doc["project_id"] for doc in corpus))
    reusable_docs = [
        doc
        for doc in corpus
        if doc.get("status") in {"reviewed", "promoted"}
        and (doc.get("visibility") == "shared" or bool(doc["metadata"].get("reusable_lessons", [])))
    ]
    shared_docs = [doc for doc in corpus if doc.get("visibility") == "shared"]
    unsafe_shared = [
        doc
        for doc in shared_docs
        if doc.get("sanitization_status") != "approved"
        or doc.get("review_status") != "approved"
        or doc.get("data_class") not in SHARED_ALLOWED_DATA_CLASSES
    ]
    raw_session_hits = [doc for doc in corpus if doc.get("doc_type") == "session"]
    freshness_warnings = [
        {
            "memory_id": doc["memory_id"],
            "project_id": doc["project_id"],
            "source_path": doc["source_path"],
            "warnings": doc.get("freshness_warnings", []),
        }
        for doc in corpus
        if doc.get("freshness_warnings")
    ]
    avg_precision = sum(row["precision_at_k"] for row in query_results) / max(1, len(query_results))
    avg_recall = sum(row["recall_at_k"] for row in query_results) / max(1, len(query_results))
    avg_mrr = sum(row["mrr"] for row in query_results) / max(1, len(query_results))
    avg_ndcg = sum(row["ndcg_at_k"] for row in query_results) / max(1, len(query_results))
    avg_project_coverage = sum(row["project_coverage"] for row in query_results) / max(1, len(query_results))
    p95_latency = sorted(query_latencies)[max(0, math.ceil(len(query_latencies) * 0.95) - 1)] if query_latencies else 0
    total_chars = sum(len(doc["text"]) for doc in corpus)
    scalability_score = max(0, min(100, 100 - (p95_latency * 1000 / 10) + min(10, len(corpus) / 10)))
    precision_score = round(((avg_precision * 0.35) + (avg_recall * 0.3) + (avg_mrr * 0.2) + (avg_ndcg * 0.15)) * 100, 2)
    reusability_score = round(min(100, (len(reusable_docs) / max(1, len(corpus)) * 70) + (len(shared_docs) * 8) + (avg_project_coverage * 20)), 2)
    parallel_score = round(min(100, len(parallels) * 8 + avg_project_coverage * 30), 2)
    safety_score = 100.0 if not unsafe_shared and not raw_session_hits else max(0.0, 100.0 - len(unsafe_shared) * 20 - len(raw_session_hits) * 10)
    overall = round((precision_score * 0.3) + (scalability_score * 0.2) + (reusability_score * 0.2) + (parallel_score * 0.2) + (safety_score * 0.1), 2)
    thresholds = {
        "min_overall_score": min_overall_score,
        "min_safety_score": min_safety_score,
    }
    failures = []
    if min_overall_score is not None and overall < min_overall_score:
        failures.append({"metric": "overall_score", "actual": overall, "required": min_overall_score})
    if min_safety_score is not None and safety_score < min_safety_score:
        failures.append({"metric": "safety_score", "actual": safety_score, "required": min_safety_score})
    if queries_file and not corpus:
        failures.append({"metric": "corpus.documents", "actual": 0, "required": ">0"})
    result = {
        "generated_at": utc_now(),
        "project_roots": [str(path) for path in project_roots],
        "project_ids": project_ids,
        "queries_file": str(queries_file) if queries_file else "",
        "thresholds": thresholds,
        "failures": failures,
        "passed": not failures,
        "corpus": {
            "documents": len(corpus),
            "total_chars": total_chars,
            "include_sessions": include_sessions,
            "build_ms": round(build_seconds * 1000, 3),
        },
        "metrics": {
            "precision_score": precision_score,
            "avg_precision_at_k": round(avg_precision, 4),
            "avg_recall_at_k": round(avg_recall, 4),
            "avg_mrr": round(avg_mrr, 4),
            "avg_ndcg_at_k": round(avg_ndcg, 4),
            "avg_project_coverage": round(avg_project_coverage, 4),
            "scalability_score": round(scalability_score, 2),
            "p95_query_latency_ms": round(p95_latency * 1000, 3),
            "reusability_score": reusability_score,
            "reusable_docs": len(reusable_docs),
            "shared_docs": len(shared_docs),
            "parallel_score": parallel_score,
            "cross_project_parallel_candidates": len(parallels),
            "safety_score": safety_score,
            "unsafe_shared_docs": len(unsafe_shared),
            "raw_session_docs_in_corpus": len(raw_session_hits),
            "overall_score": overall,
        },
        "queries": query_results,
        "freshness_warnings": freshness_warnings,
        "top_parallel_candidates": parallels[:20],
    }
    out_dir = output_dir or (root / "agent-memory" / "exports" / "retrieval-eval")
    out_dir.mkdir(parents=True, exist_ok=True)
    locked_atomic_write_text(out_dir / "retrieval-eval.json", json.dumps(result, indent=2, sort_keys=True))
    lines = [
        "# Memory Retrieval Eval",
        "",
        "## Summary",
        "",
        f"- Projects: {', '.join(project_ids)}",
        f"- Corpus documents: {len(corpus)}",
        f"- Overall score: {overall}",
        f"- Precision score: {precision_score}",
        f"- Scalability score: {round(scalability_score, 2)}",
        f"- Reusability score: {reusability_score}",
        f"- Parallel score: {parallel_score}",
        f"- Safety score: {safety_score}",
        f"- Passed thresholds: {not failures}",
        f"- Cross-project parallel candidates: {len(parallels)}",
        "",
    ]
    if failures:
        lines.extend(["## Threshold Failures", ""])
        for failure in failures:
            lines.append(f"- {failure['metric']}: {failure['actual']} < {failure['required']}")
        lines.append("")
    if freshness_warnings:
        lines.extend(["## Freshness Warnings", ""])
        for warning in freshness_warnings[:25]:
            lines.append(f"- `{warning['memory_id']}` ({warning['source_path']}): {len(warning['warnings'])} warning(s)")
        lines.append("")
    lines.extend(["## Query Results", ""])
    for row in query_results:
        lines.extend(
            [
                f"### {row['name']}",
                "",
                f"- Query: `{row['query']}`",
                f"- Precision@{top_k}: {round(row['precision_at_k'], 4)}",
                f"- Recall@{top_k}: {round(row['recall_at_k'], 4)}",
                f"- MRR: {round(row['mrr'], 4)}",
                f"- nDCG@{top_k}: {round(row['ndcg_at_k'], 4)}",
                f"- Project coverage: {round(row['project_coverage'], 4)}",
                f"- Latency: {row['latency_ms']} ms",
                "- Top hits:",
            ]
        )
        for hit in row["hits"]:
            lines.append(f"  - `{hit['memory_id']}` ({hit['project_id']}, score={hit['score']})")
        lines.append("")
    lines.extend(["## Top Cross-Project Parallels", ""])
    for candidate in parallels[:10]:
        lines.append(f"- `{candidate['left']}` <-> `{candidate['right']}` via {candidate['matches']}")
    locked_atomic_write_text(out_dir / "retrieval-eval.md", "\n".join(lines) + "\n")
    result["outputs"] = {
        "json": str((out_dir / "retrieval-eval.json").resolve()),
        "markdown": str((out_dir / "retrieval-eval.md").resolve()),
    }
    return result


REPORT_TYPE_LABELS = {
    "decision": "Decision Report",
    "handoff": "Handoff Report",
    "rag-readiness": "RAG Readiness Report",
    "agent-activity": "Agent Activity Report",
    "project-dashboard": "Project Dashboard",
    "website-ui": "Website / UI Report",
    "project-site": "Project Snapshot Site",
    "execution-dashboard": "Execution Dashboard",
}


REPORT_TYPE_DOCS = {
    "decision": {"adr", "canonical", "evidence", "compiled"},
    "handoff": {"handoff", "session", "compiled", "evidence", "qa"},
    "rag-readiness": DEFAULT_RAG_DOC_TYPES | {"qa", "handoff"},
    "agent-activity": {"session", "compiled", "evidence", "handoff"},
    "project-dashboard": {"project_context", "canonical", "compiled", "adr", "lesson"},
    "website-ui": {"canonical", "compiled", "adr", "evidence", "lesson"},
    "project-site": {"project_context", "canonical", "compiled", "adr", "lesson", "handoff", "evidence", "qa"},
    "execution-dashboard": {"compiled", "handoff", "evidence", "qa", "adr"},
}


PROJECT_SNAPSHOT_PROFILE_REL = "agent-memory/project-snapshot/profile.md"
PROJECT_SNAPSHOT_MANIFEST_REL = "agent-memory/project-snapshot/project-snapshot-manifest.json"
PROJECT_STORY_SNAPSHOT_REL = "agent-memory/compiled/project-story-snapshot.md"
PROJECT_EXECUTION_SNAPSHOT_REL = "agent-memory/compiled/project-execution-snapshot.md"
PROJECT_SNAPSHOT_REPORT_TYPES = {"project-site", "execution-dashboard"}
PROJECT_SNAPSHOT_DEFAULT_TOKEN_BUDGET = 12000
PROJECT_SNAPSHOT_LARGE_TOKEN_BUDGET = 40000


REPORT_DESIGN_PRESETS = {
    "atlas-command": {
        "name": "Atlas Command",
        "bg": "#f6f7f9",
        "panel": "#ffffff",
        "ink": "#17191d",
        "muted": "#626b78",
        "line": "#d9dee7",
        "accent": "#245c88",
        "radius": "8px",
        "density": "18px",
        "font_family": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    },
    "glass-ledger": {"name": "Glass Ledger", "bg": "#eef5f3", "panel": "#fbfffd", "ink": "#13211f", "muted": "#5f716c", "line": "#c8d9d4", "accent": "#317873", "radius": "14px", "density": "20px", "font_family": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'},
    "signal-grid": {"name": "Signal Grid", "bg": "#111418", "panel": "#181d23", "ink": "#f5f2ea", "muted": "#adb4bd", "line": "#343b45", "accent": "#b36b00", "radius": "4px", "density": "16px", "font_family": 'ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace'},
    "courtroom-brief": {"name": "Courtroom Brief", "bg": "#fbf7ef", "panel": "#fffdf7", "ink": "#241a14", "muted": "#735f53", "line": "#e3d5c6", "accent": "#7a3b1f", "radius": "3px", "density": "20px", "font_family": 'Georgia, "Times New Roman", serif'},
    "mission-control": {"name": "Mission Control", "bg": "#071117", "panel": "#0e1c24", "ink": "#edfaff", "muted": "#9db4bf", "line": "#23404d", "accent": "#35b7d8", "radius": "8px", "density": "16px", "font_family": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'},
    "blueprint-studio": {"name": "Blueprint Studio", "bg": "#edf7fb", "panel": "#fbfdff", "ink": "#112834", "muted": "#607782", "line": "#bdd9e6", "accent": "#1178a8", "radius": "2px", "density": "20px", "font_family": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'},
    "executive-ledger": {"name": "Executive Ledger", "bg": "#faf8f1", "panel": "#fffdf8", "ink": "#171b26", "muted": "#6f6b61", "line": "#e4dcc8", "accent": "#9b7a2f", "radius": "6px", "density": "24px", "font_family": 'Georgia, "Times New Roman", serif'},
    "graph-aurora": {"name": "Graph Aurora", "bg": "#10151f", "panel": "#171d2a", "ink": "#f2fff8", "muted": "#aebbc9", "line": "#30394a", "accent": "#78d6a3", "radius": "16px", "density": "20px", "font_family": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'},
    "monolith-minimal": {"name": "Monolith Minimal", "bg": "#f3f3f0", "panel": "#ffffff", "ink": "#0a0a0a", "muted": "#5d5d58", "line": "#cfcfca", "accent": "#111111", "radius": "0px", "density": "16px", "font_family": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'},
    "workshop-canvas": {"name": "Workshop Canvas", "bg": "#fffaf2", "panel": "#fffefa", "ink": "#24211b", "muted": "#756b5c", "line": "#eadcc7", "accent": "#d66a28", "radius": "10px", "density": "20px", "font_family": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'},
    "neon-console": {"name": "Neon Console", "bg": "#050806", "panel": "#0b120d", "ink": "#eaffef", "muted": "#9db7a6", "line": "#214d31", "accent": "#39ff88", "radius": "5px", "density": "16px", "font_family": 'ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace'},
    "nordic-clarity": {"name": "Nordic Clarity", "bg": "#f7faf9", "panel": "#ffffff", "ink": "#18211f", "muted": "#64706d", "line": "#d7e2df", "accent": "#3f8f95", "radius": "8px", "density": "24px", "font_family": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'},
    "evidence-vault": {"name": "Evidence Vault", "bg": "#111820", "panel": "#18222d", "ink": "#f8fbff", "muted": "#aeb8c5", "line": "#354456", "accent": "#d24b35", "radius": "7px", "density": "16px", "font_family": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'},
    "product-lab": {"name": "Product Lab", "bg": "#fff6f8", "panel": "#ffffff", "ink": "#24151b", "muted": "#76636a", "line": "#f0ccd7", "accent": "#e24d7b", "radius": "12px", "density": "20px", "font_family": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'},
    "zeus-celestial": {"name": "Zeus Celestial", "bg": "#080b13", "panel": "#111827", "ink": "#f4f8ff", "muted": "#a9b4c4", "line": "#2a3447", "accent": "#65a9ff", "radius": "14px", "density": "24px", "font_family": 'Georgia, "Times New Roman", serif'},
}


def html_escape(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def read_report_design(root: pathlib.Path) -> dict[str, str]:
    design_file = root / "DESIGN.md"
    selected = "atlas-command"
    if design_file.exists():
        with contextlib.suppress(Exception):
            meta = parse_frontmatter(design_file.read_text(encoding="utf-8"))
            selected = str(meta.get("selected_report_design") or selected).strip()
    design = dict(REPORT_DESIGN_PRESETS.get(selected, REPORT_DESIGN_PRESETS["atlas-command"]))
    design["id"] = selected if selected in REPORT_DESIGN_PRESETS else "atlas-command"
    return design


def report_rejection_reason(meta: dict[str, Any], audience: str) -> str | None:
    if audience == "private":
        return None
    if meta.get("visibility") == "private":
        return "private_visibility"
    if meta.get("data_class") in {"confidential", "personal", "special-category"}:
        return "restricted_data_class"
    if audience == "customer":
        if meta.get("visibility") not in {"customer", "shared"}:
            return "not_customer_visible"
        if meta.get("review_status") != "approved":
            return "customer_review_not_approved"
        if meta.get("sanitization_status") != "approved":
            return "not_customer_sanitized"
    if audience == "shared" and (
        meta.get("visibility") != "shared"
        or meta.get("review_status") != "approved"
        or meta.get("sanitization_status") != "approved"
    ):
        return "not_shared_report_safe"
    return None


def selected_report_records(
    root: pathlib.Path,
    report_type: str,
    include_sessions: bool = False,
    audience: str = "private",
    tenant_id: str | None = None,
    customer_id: str | None = None,
    project_id: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    wanted = REPORT_TYPE_DOCS.get(report_type, DEFAULT_RAG_DOC_TYPES)
    records = []
    rejected: dict[str, int] = {}
    for record in load_memory_records(root, include_sessions=include_sessions or report_type in {"handoff", "agent-activity"}):
        meta = record["metadata"]
        if meta.get("doc_type") in wanted:
            reason = scope_rejection_reason(meta, tenant_id, customer_id, project_id) or report_rejection_reason(meta, audience)
            if reason:
                rejected[reason] = rejected.get(reason, 0) + 1
                continue
            records.append(record)
    return records, rejected


def render_memory_report(
    root: pathlib.Path,
    report_type: str,
    output_dir: pathlib.Path | None = None,
    title: str | None = None,
    audience: str = "private",
    tenant_id: str | None = None,
    customer_id: str | None = None,
    project_id: str | None = None,
) -> dict[str, Any]:
    if report_type not in REPORT_TYPE_LABELS:
        raise ValueError(f"Unknown report type: {report_type}")
    if report_type == "project-site":
        return render_project_snapshot_site(root, output_dir=output_dir, title=title, audience=audience)
    if report_type == "execution-dashboard":
        return render_execution_dashboard(root, output_dir=output_dir, title=title, audience=audience)
    records, report_rejected = selected_report_records(
        root,
        report_type,
        audience=audience,
        tenant_id=tenant_id,
        customer_id=customer_id,
        project_id=project_id,
    )
    defaults = project_defaults(root)
    design = read_report_design(root)
    now = utc_now()
    label = REPORT_TYPE_LABELS[report_type]
    title = title or f"{label}: {defaults['project_id']}"
    out_dir = output_dir or (root / "agent-memory" / "reports" / "html")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{report_type}-{slugify(defaults['project_id'])}.html"
    source_rows = []
    cards = []
    doc_type_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    shared_count = 0
    unsafe_shared = 0
    for record in records:
        meta = record["metadata"]
        doc_type = str(meta.get("doc_type", "unknown"))
        status = str(meta.get("status", "unknown"))
        doc_type_counts[doc_type] = doc_type_counts.get(doc_type, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
        if meta.get("visibility") == "shared":
            shared_count += 1
            if meta.get("review_status") != "approved" or meta.get("sanitization_status") != "approved":
                unsafe_shared += 1
        source_rows.append(
            f"<tr><td><code>{html_escape(record['source_path'])}</code></td><td>{html_escape(meta.get('memory_id', ''))}</td><td>{html_escape(doc_type)}</td><td><code>{html_escape(record['source_hash'][:16])}</code></td></tr>"
        )
        cards.append(
            f"""
            <article class="memory-card" data-doc-type="{html_escape(doc_type)}">
              <div class="card-topline">
                <span>{html_escape(doc_type)}</span>
                <span>{html_escape(status)}</span>
                <span>{html_escape(meta.get('visibility', ''))}</span>
              </div>
              <h3>{html_escape(meta.get('semantic_title', meta.get('title', meta.get('memory_id', 'Untitled'))))}</h3>
              <p>{html_escape(meta.get('summary', markdown_body(record['content'])[:280]))}</p>
              <dl>
                <div><dt>Memory ID</dt><dd><code>{html_escape(meta.get('memory_id', ''))}</code></dd></div>
                <div><dt>Source</dt><dd><code>{html_escape(record['source_path'])}</code></dd></div>
                <div><dt>Hash</dt><dd><code>{html_escape(record['source_hash'][:24])}</code></dd></div>
              </dl>
            </article>
            """
        )

    def stat_cards(values: dict[str, int]) -> str:
        return "".join(f"<div class='stat'><strong>{count}</strong><span>{html_escape(key)}</span></div>" for key, count in sorted(values.items()))

    design_controls = ""
    if report_type == "website-ui":
        design_controls = """
        <section class="panel">
          <h2>Design Token Decision Controls</h2>
          <div class="controls-grid">
            <label>Radius <input id="radius" type="range" min="0" max="18" value="8"></label>
            <label>Spacing <input id="spacing" type="range" min="8" max="32" value="18"></label>
            <label>Type scale <input id="typeScale" type="range" min="90" max="125" value="100"></label>
            <label>Primary color <input id="primaryColor" type="color" value="{html_escape(design['accent'])}"></label>
          </div>
          <textarea id="decisionJson" readonly aria-label="Design decision JSON"></textarea>
        </section>
        """

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_escape(title)}</title>
  <style>
    :root {{
      --bg: {design['bg']};
      --panel: {design['panel']};
      --ink: {design['ink']};
      --muted: {design['muted']};
      --line: {design['line']};
      --accent: {design['accent']};
      --radius: {design['radius']};
      --density: {design['density']};
      --scale: 1;
      --font-family: {design['font_family']};
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font-family); font-size: calc(16px * var(--scale)); }}
    header {{ padding: 34px min(6vw, 72px); background: var(--panel); border-bottom: 1px solid var(--line); }}
    main {{ padding: 26px min(6vw, 72px) 60px; }}
    h1 {{ margin: 0 0 8px; font-size: clamp(32px, 5vw, 62px); letter-spacing: 0; }}
    h2 {{ margin: 0 0 18px; font-size: clamp(24px, 3vw, 36px); letter-spacing: 0; }}
    h3 {{ margin: 0 0 8px; letter-spacing: 0; }}
    p {{ color: var(--muted); line-height: 1.55; }}
    code {{ font-size: 0.9em; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }}
    .chip {{ padding: 7px 10px; border: 1px solid var(--line); border-radius: 999px; background: var(--panel); color: var(--muted); }}
    .toolbar {{ position: sticky; top: 0; z-index: 5; display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 12px; padding: 14px min(6vw, 72px); background: color-mix(in srgb, var(--panel) 94%, transparent); border-bottom: 1px solid var(--line); backdrop-filter: blur(12px); }}
    .toolbar label, .controls-grid label {{ display: grid; gap: 6px; color: var(--muted); font-size: 13px; font-weight: 700; }}
    .panel {{ margin-top: 24px; padding: var(--density); border: 1px solid var(--line); border-radius: var(--radius); background: var(--panel); }}
    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }}
    .stat {{ padding: var(--density); border: 1px solid var(--line); border-radius: var(--radius); background: var(--panel); }}
    .stat strong {{ display: block; font-size: 34px; }}
    .stat span {{ color: var(--muted); }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
    .memory-card {{ padding: var(--density); border: 1px solid var(--line); border-radius: var(--radius); background: var(--panel); }}
    .card-topline {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; color: var(--accent); font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    dl {{ display: grid; gap: 10px; }}
    dt {{ color: var(--muted); font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    dd {{ margin: 2px 0 0; overflow-wrap: anywhere; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; }}
    .controls-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; }}
    textarea {{ width: 100%; min-height: 150px; margin-top: 14px; padding: 12px; border: 1px solid var(--line); border-radius: var(--radius); font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
    body.contrast {{ --bg: #0f1115; --panel: #181c22; --ink: #f5f7fa; --muted: #b8c0cc; --line: #343b47; }}
    @media (max-width: 760px) {{ .toolbar {{ grid-template-columns: 1fr; position: static; }} }}
  </style>
</head>
<body>
  <header>
    <p class="chip">Generated view. Markdown remains source of truth.</p>
    <h1>{html_escape(title)}</h1>
    <p>{html_escape(label)} generated from Agent Memory files.</p>
    <div class="meta">
      <span class="chip">Generated: {html_escape(now)}</span>
      <span class="chip">Project: {html_escape(defaults['project_id'])}</span>
      <span class="chip">Tenant: {html_escape(defaults['tenant_id'])}</span>
      <span class="chip">Scope: {html_escape(' / '.join(value for value in [tenant_id, customer_id, project_id] if value) or 'project default')}</span>
      <span class="chip">Audience: {html_escape(audience)}</span>
      <span class="chip">Design: {html_escape(design['name'])} ({html_escape(design['id'])})</span>
      <span class="chip">Records: {len(records)}</span>
      <span class="chip">Shared: {shared_count}</span>
      <span class="chip">Unsafe shared: {unsafe_shared}</span>
    </div>
  </header>
  <section class="toolbar" aria-label="Report display controls">
    <label>Density <input id="density" type="range" min="10" max="30" value="18"></label>
    <label>Font size <input id="fontSize" type="range" min="90" max="120" value="100"></label>
    <label>Accent <input id="accent" type="color" value="#245c88"></label>
    <label>High contrast <input id="contrast" type="checkbox"></label>
  </section>
  <main>
    <section class="panel">
      <h2>Summary</h2>
      <div class="stats">
        <div class="stat"><strong>{len(records)}</strong><span>source records</span></div>
        <div class="stat"><strong>{len(doc_type_counts)}</strong><span>document types</span></div>
        <div class="stat"><strong>{shared_count}</strong><span>shared records</span></div>
        <div class="stat"><strong>{unsafe_shared}</strong><span>unsafe shared records</span></div>
        <div class="stat"><strong>{sum(report_rejected.values())}</strong><span>audience-filtered records</span></div>
      </div>
    </section>
    <section class="panel">
      <h2>Document Types</h2>
      <div class="stats">{stat_cards(doc_type_counts)}</div>
    </section>
    <section class="panel">
      <h2>Status</h2>
      <div class="stats">{stat_cards(status_counts)}</div>
    </section>
    {design_controls}
    <section class="panel">
      <h2>Memory Records</h2>
      <div class="cards">{''.join(cards) or '<p>No matching memory records found.</p>'}</div>
    </section>
    <section class="panel">
      <h2>Sources And Hashes</h2>
      <table>
        <thead><tr><th>Source</th><th>Memory ID</th><th>Type</th><th>Hash</th></tr></thead>
        <tbody>{''.join(source_rows) or '<tr><td colspan="4">No sources.</td></tr>'}</tbody>
      </table>
    </section>
  </main>
  <script>
    const root = document.documentElement;
    const density = document.getElementById('density');
    const fontSize = document.getElementById('fontSize');
    const accent = document.getElementById('accent');
    const contrast = document.getElementById('contrast');
    function updateBase() {{
      root.style.setProperty('--density', density.value + 'px');
      root.style.setProperty('--scale', String(Number(fontSize.value) / 100));
      root.style.setProperty('--accent', accent.value);
      document.body.classList.toggle('contrast', contrast.checked);
      updateDecisionJson();
    }}
    [density, fontSize, accent, contrast].forEach(el => el.addEventListener('input', updateBase));
    function updateDecisionJson() {{
      const target = document.getElementById('decisionJson');
      if (!target) return;
      const radius = document.getElementById('radius');
      const spacing = document.getElementById('spacing');
      const typeScale = document.getElementById('typeScale');
      const primaryColor = document.getElementById('primaryColor');
      const payload = {{
        source: 'html-report-presentation-state',
        project_id: {json.dumps(defaults['project_id'])},
        report_type: {json.dumps(report_type)},
        generated_at: {json.dumps(now)},
        design_tokens: {{
          radius_px: Number(radius.value),
          spacing_px: Number(spacing.value),
          type_scale_percent: Number(typeScale.value),
          primary_color: primaryColor.value
        }}
      }};
      target.value = JSON.stringify(payload, null, 2);
      root.style.setProperty('--radius', radius.value + 'px');
      root.style.setProperty('--density', spacing.value + 'px');
      root.style.setProperty('--scale', String(Number(typeScale.value) / 100));
      root.style.setProperty('--accent', primaryColor.value);
    }}
    ['radius','spacing','typeScale','primaryColor'].forEach(id => {{
      const el = document.getElementById(id);
      if (el) el.addEventListener('input', updateDecisionJson);
    }});
    updateBase();
  </script>
</body>
</html>
"""
    locked_atomic_write_text(out, html_text)
    return {
        "path": str(out.relative_to(root)),
        "records": len(records),
        "report_type": report_type,
        "title": title,
        "audience": audience,
        "unsafe_shared_records": unsafe_shared,
        "rejected_counts": report_rejected,
    }


def project_snapshot_profile_path(root: pathlib.Path) -> pathlib.Path:
    return root / pathlib.Path(PROJECT_SNAPSHOT_PROFILE_REL)


def project_snapshot_addon_installed(root: pathlib.Path) -> bool:
    return project_snapshot_profile_path(root).exists()


def require_project_snapshot_addon(root: pathlib.Path) -> None:
    if not project_snapshot_addon_installed(root):
        raise FileNotFoundError(
            "Project Snapshot Kit is not installed. Run: "
            "python tools/owledge.py install-addon --project-root . --addon project-snapshot-kit"
        )


def write_text_if_changed(path: pathlib.Path, text: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8", errors="replace") == text:
        return False
    locked_atomic_write_text(path, text)
    return True


def safe_project_file(root: pathlib.Path, relative: str) -> pathlib.Path | None:
    if not relative or ".." in pathlib.PurePosixPath(relative.replace("\\", "/")).parts:
        return None
    path = root / pathlib.Path(relative)
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return path


def read_memory_index_rows_for_snapshot(root: pathlib.Path) -> tuple[list[dict[str, Any]], bool]:
    index_path = root / "agent-memory" / "indexes" / "memory-index.jsonl"
    if index_path.exists():
        return read_jsonl(index_path), True
    records = load_memory_records(root, include_sessions=False)
    return [memory_index_row(record) for record in records], False


def first_markdown_heading(text: str, fallback: str) -> str:
    for line in markdown_body(text).splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def source_excerpt(root: pathlib.Path, relative: str, max_chars: int = 1200) -> str:
    if relative.endswith("events.jsonl"):
        return ""
    path = safe_project_file(root, relative)
    if not path or not path.exists() or not path.is_file() or path.suffix.lower() != ".md":
        return ""
    return markdown_body(path.read_text(encoding="utf-8", errors="replace")).strip()[:max_chars]


def project_snapshot_rows(root: pathlib.Path, rows: list[dict[str, Any]], limit: int = 60) -> list[dict[str, Any]]:
    wanted = {"project_context", "canonical", "compiled", "adr", "lesson", "pattern", "idea", "handoff", "evidence", "qa"}
    generated_sources = {
        PROJECT_STORY_SNAPSHOT_REL,
        PROJECT_EXECUTION_SNAPSHOT_REL,
        PROJECT_SNAPSHOT_MANIFEST_REL,
    }
    filtered = [
        row
        for row in rows
        if row.get("doc_type") in wanted
        and row.get("data_class") not in {"confidential", "personal", "special-category"}
        and not str(row.get("source_path", "")).endswith("events.jsonl")
        and str(row.get("source_path", "")) not in generated_sources
        and not str(row.get("source_path", "")).startswith("agent-memory/reports/")
        and not str(row.get("source_path", "")).startswith("agent-memory/project-snapshot/")
    ]
    priority = {
        "project_context": 0,
        "canonical": 1,
        "adr": 2,
        "compiled": 3,
        "lesson": 4,
        "pattern": 5,
        "idea": 6,
        "handoff": 7,
        "evidence": 8,
        "qa": 9,
    }
    filtered.sort(key=lambda row: (priority.get(str(row.get("doc_type")), 99), str(row.get("source_path", ""))))
    return filtered[:limit]


def scan_project_task_artifacts(root: pathlib.Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for base_rel, durable in [("agent-memory/plans", True), ("agent-plans", False)]:
        base = root / pathlib.Path(base_rel)
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            rel = str(path.relative_to(root)).replace("\\", "/")
            text = path.read_text(encoding="utf-8", errors="replace")
            meta = parse_frontmatter(text)
            item_type = str(meta.get("type") or meta.get("doc_type") or "Plan")
            if item_type not in {"TaskCard", "WorkPackage", "EpicOverview", "Plan", "task", "handoff"} and base_rel == "agent-plans":
                item_type = "Plan"
            title = str(meta.get("title") or meta.get("semantic_title") or first_markdown_heading(text, path.stem))
            status = str(meta.get("status") or "unknown")
            body = markdown_body(text)
            blocker_lines = [line.strip("- ").strip() for line in body.splitlines() if "block" in line.lower()][:3]
            artifacts.append(
                {
                    "id": str(meta.get("id") or meta.get("memory_id") or path.stem),
                    "type": item_type,
                    "status": status,
                    "priority": str(meta.get("priority") or ""),
                    "title": title,
                    "source_path": rel,
                    "source_hash": sha256_file(path),
                    "durable": durable,
                    "blockers": blocker_lines,
                    "epic_id": str(meta.get("epic_id") or ""),
                    "workpackage_id": str(meta.get("workpackage_id") or ""),
                }
            )
    return artifacts


def count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def bullet_lines(values: list[str], empty: str = "None detected.") -> str:
    cleaned = [value for value in values if value]
    if not cleaned:
        return f"- {empty}"
    return "\n".join(f"- {value}" for value in cleaned)


def project_snapshot_source_fingerprints(rows: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> dict[str, str]:
    fingerprints: dict[str, str] = {}
    for row in rows:
        if row.get("source_path") and row.get("source_hash"):
            fingerprints[str(row["source_path"])] = str(row["source_hash"])
    for task in tasks:
        if task.get("source_path") and task.get("source_hash"):
            fingerprints[str(task["source_path"])] = str(task["source_hash"])
    return dict(sorted(fingerprints.items()))


def snapshot_frontmatter(defaults: dict[str, str], kind: str, title: str, summary: str, source_hash: str, now: str) -> str:
    slug = "project-story-snapshot" if kind == "project_story" else "project-execution-snapshot"
    return f"""---
memory_id: "mem:{defaults['tenant_id']}:{defaults['customer_id']}:{defaults['project_id']}:compiled:{slug}"
tenant_id: {yaml_string(defaults['tenant_id'])}
customer_id: {yaml_string(defaults['customer_id'])}
project_id: {yaml_string(defaults['project_id'])}
doc_type: "compiled"
snapshot_kind: {yaml_string(kind)}
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: {yaml_string(title)}
summary: {yaml_string(summary)}
concept_tags:
  - "project-snapshot"
stack_tags: []
problem_patterns: []
architecture_patterns: []
failure_modes: []
reusable_lessons: []
confidence: 0.7
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: {yaml_string(now)}
updated_at: {yaml_string(now)}
retention_class: "standard"
stale_after: ""
expires_at: ""
last_reviewed_at: ""
review_cycle: "monthly"
source_hash: {yaml_string(source_hash)}
edges: []
---
"""


def collect_project_snapshot_model(root: pathlib.Path, token_budget: int, allow_large_context: bool) -> dict[str, Any]:
    defaults = project_defaults(root)
    rows, used_index = read_memory_index_rows_for_snapshot(root)
    selected_rows = project_snapshot_rows(root, rows)
    tasks = scan_project_task_artifacts(root)
    extra_sources: list[dict[str, Any]] = []
    for rel in ["README.md", "ROADMAP.md", "PROJECT_CONTEXT.md", "PROJECT_CONTEXT.template.md"]:
        path = root / rel
        if path.exists() and path.is_file():
            extra_sources.append(
                {
                    "source_path": rel,
                    "source_hash": sha256_file(path),
                    "doc_type": "project_source",
                    "status": "active",
                    "semantic_title": first_markdown_heading(path.read_text(encoding="utf-8", errors="replace"), rel),
                    "summary": source_excerpt(root, rel, max_chars=220).replace("\n", " "),
                }
            )
    all_source_rows = selected_rows + extra_sources
    source_fingerprints = project_snapshot_source_fingerprints(all_source_rows, tasks)
    source_fingerprint_text = json.dumps(source_fingerprints, sort_keys=True)
    source_hash = sha256_text(source_fingerprint_text)
    snippets = [source_excerpt(root, str(row.get("source_path", "")), max_chars=900) for row in all_source_rows[:18]]
    estimate_input_tokens = max(0, math.ceil((len(json.dumps(all_source_rows[:80], sort_keys=True)) + sum(len(item) for item in snippets)) / 4))
    estimate_output_tokens = 3500 if tasks else 2500
    if token_budget > PROJECT_SNAPSHOT_LARGE_TOKEN_BUDGET and not allow_large_context:
        raise ValueError("Token budgets above 40000 require --allow-large-context.")
    if estimate_input_tokens > token_budget and not allow_large_context:
        raise ValueError(f"Estimated narrative refresh input tokens ({estimate_input_tokens}) exceed --token-budget {token_budget}. Pass --allow-large-context to continue.")
    return {
        "defaults": defaults,
        "rows": all_source_rows,
        "tasks": tasks,
        "used_memory_index": used_index,
        "source_fingerprints": source_fingerprints,
        "source_hash": source_hash,
        "token_estimate": {
            "model_tokens_used": 0,
            "estimated_refresh_input_tokens": estimate_input_tokens,
            "estimated_refresh_output_tokens": estimate_output_tokens,
            "token_budget": token_budget,
            "allow_large_context": allow_large_context,
        },
        "counts": {
            "doc_types": count_by(all_source_rows, "doc_type"),
            "record_status": count_by(all_source_rows, "status"),
            "task_status": count_by(tasks, "status"),
            "task_types": count_by(tasks, "type"),
        },
    }


def render_project_story_snapshot_markdown(model: dict[str, Any], now: str) -> str:
    defaults = model["defaults"]
    rows = model["rows"]
    counts = model["counts"]
    source_hash = model["source_hash"]
    titles = [str(row.get("semantic_title") or row.get("summary") or row.get("source_path")) for row in rows[:10]]
    summaries = [str(row.get("summary") or "") for row in rows[:8] if row.get("summary")]
    problem_patterns = sorted({str(item) for row in rows for item in row.get("problem_patterns", []) if item})
    architecture_patterns = sorted({str(item) for row in rows for item in row.get("architecture_patterns", []) if item})
    feature_tags = sorted({str(item) for row in rows for item in row.get("concept_tags", []) if item})[:12]
    sources = [[row.get("source_path", ""), row.get("doc_type", ""), str(row.get("source_hash", ""))[:16]] for row in rows[:30]]
    body = f"""# Project Story Snapshot

## One-Line Pitch

{defaults['project_id']} is summarized from local Owledge memory as a source-backed project with {len(rows)} selected records and {sum(counts['task_status'].values())} local planning artifacts.

## Problem

{bullet_lines(problem_patterns, "No explicit problem patterns found in selected memory.")}

## Target Users

- Project owners who need a durable overview of agent-planned work.
- Agents that need compact project context without reloading full history.

## Painpoints Solved

{bullet_lines(summaries[:6], "No reusable painpoint summaries found yet.")}

## Core Features

{bullet_lines(feature_tags or titles[:8], "No feature tags found yet.")}

## Workflows

{bullet_lines(architecture_patterns, "No explicit architecture or workflow patterns found yet.")}

## Architecture And Layers

{md_table(["Document type", "Count"], [[key, value] for key, value in sorted(counts["doc_types"].items())])}

## Current Status

{md_table(["Status", "Count"], [[key, value] for key, value in sorted(counts["record_status"].items())])}

## Sources

{md_table(["Source", "Type", "Hash"], sources)}
"""
    return snapshot_frontmatter(defaults, "project_story", "Project story snapshot", "Reusable project orientation, pitch, painpoints, workflows, and feature overview.", source_hash, now) + body


def render_project_execution_snapshot_markdown(model: dict[str, Any], now: str) -> str:
    defaults = model["defaults"]
    rows = model["rows"]
    tasks = model["tasks"]
    counts = model["counts"]
    source_hash = model["source_hash"]
    blockers = [blocker for task in tasks for blocker in task.get("blockers", [])][:10]
    task_rows = [
        [task.get("id", ""), task.get("type", ""), task.get("status", ""), task.get("priority", ""), task.get("source_path", "")]
        for task in tasks[:40]
    ]
    source_rows = [[row.get("source_path", ""), row.get("doc_type", ""), str(row.get("source_hash", ""))[:16]] for row in rows[:24]]
    body = f"""# Project Execution Snapshot

## Goal

Keep {defaults['project_id']} execution state visible through local Owledge plans, task cards, evidence, handoffs, and generated snapshots.

## MVP

- Install Project Snapshot Kit only when requested.
- Generate source-backed Markdown snapshots.
- Generate static local HTML from existing snapshots.
- Track Owledge-local task status deterministically.

## Explicitly Out Of MVP

- External GitHub, Linear, or Jira synchronization.
- Hosted dashboard, authentication, or RBAC.
- Automatic promotion to canonical memory.
- Model calls from the CLI.

## Active Workstreams

{md_table(["Task type", "Count"], [[key, value] for key, value in sorted(counts["task_types"].items())])}

## Task Status

{md_table(["Status", "Count"], [[key, value] for key, value in sorted(counts["task_status"].items())])}

## Local Tasks And Plans

{md_table(["ID", "Type", "Status", "Priority", "Source"], task_rows) if task_rows else "- No Owledge-local task artifacts found."}

## Roadmap

- Refresh snapshots when source hashes change.
- Keep HTML regeneration deterministic and zero-token.
- Add external ticket adapters later as optional importers.

## Blockers

{bullet_lines(blockers, "No blockers detected in local task artifacts.")}

## QA Gates

- Run `python tools/agent_memory_cli.py --project-root . validate-memory --strict`.
- Run `python tools/owledge.py doctor --project-root .`.
- Run add-on generation with `--changed-only` before sharing reports.

## Latest Agent Activity

Source-backed activity is summarized from handoffs and evidence records only. Raw runtime event logs are excluded.

## Sources

{md_table(["Source", "Type", "Hash"], source_rows)}
"""
    return snapshot_frontmatter(defaults, "execution_state", "Project execution snapshot", "Reusable MVP, roadmap, workstream, task, blocker, QA, and agent activity snapshot.", source_hash, now) + body


def read_project_snapshot_manifest(root: pathlib.Path) -> dict[str, Any]:
    path = root / pathlib.Path(PROJECT_SNAPSHOT_MANIFEST_REL)
    if not path.exists():
        return {}
    with contextlib.suppress(Exception):
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        if isinstance(data, dict):
            return data
    return {}


def write_project_snapshot_manifest(root: pathlib.Path, payload: dict[str, Any]) -> bool:
    path = root / pathlib.Path(PROJECT_SNAPSHOT_MANIFEST_REL)
    return write_text_if_changed(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def build_project_snapshot(
    root: pathlib.Path,
    render_html: bool = False,
    changed_only: bool = False,
    token_budget: int = PROJECT_SNAPSHOT_DEFAULT_TOKEN_BUDGET,
    allow_large_context: bool = False,
) -> dict[str, Any]:
    require_project_snapshot_addon(root)
    model = collect_project_snapshot_model(root, token_budget=token_budget, allow_large_context=allow_large_context)
    previous_manifest = read_project_snapshot_manifest(root)
    story_path = root / pathlib.Path(PROJECT_STORY_SNAPSHOT_REL)
    execution_path = root / pathlib.Path(PROJECT_EXECUTION_SNAPSHOT_REL)
    now = utc_now()
    generated_files: list[str] = []
    skipped_files: list[str] = []
    unchanged_sources = previous_manifest.get("source_hash") == model["source_hash"]
    snapshots_exist = story_path.exists() and execution_path.exists()
    if changed_only and unchanged_sources and snapshots_exist:
        skipped_files.extend([PROJECT_STORY_SNAPSHOT_REL, PROJECT_EXECUTION_SNAPSHOT_REL])
    else:
        story_text = render_project_story_snapshot_markdown(model, now)
        execution_text = render_project_execution_snapshot_markdown(model, now)
        if write_text_if_changed(story_path, story_text):
            generated_files.append(PROJECT_STORY_SNAPSHOT_REL)
        else:
            skipped_files.append(PROJECT_STORY_SNAPSHOT_REL)
        if write_text_if_changed(execution_path, execution_text):
            generated_files.append(PROJECT_EXECUTION_SNAPSHOT_REL)
        else:
            skipped_files.append(PROJECT_EXECUTION_SNAPSHOT_REL)
    html_result: dict[str, Any] | None = None
    if render_html:
        site_dir = root / "agent-memory" / "reports" / "project-site"
        expected_pages = ["index.html", "product.html", "workflows.html", "implementation.html", "activity.html", "sources.html"]
        html_exists = all((site_dir / page).exists() for page in expected_pages)
        if changed_only and unchanged_sources and html_exists:
            skipped_files.extend([f"agent-memory/reports/project-site/{page}" for page in expected_pages])
            html_result = {
                "path": "agent-memory/reports/project-site/index.html",
                "paths": [],
                "report_type": "project-site",
                "audience": "private",
                "records": 2,
                "skipped": True,
            }
        else:
            html_result = render_project_snapshot_site(root)
            generated_files.extend(html_result.get("paths", []))
    manifest_payload = {
        "generated_at": now,
        "project_id": model["defaults"]["project_id"],
        "source_hash": model["source_hash"],
        "source_paths": model["source_fingerprints"],
        "generated_files": generated_files,
        "skipped_files": skipped_files,
        "used_memory_index": model["used_memory_index"],
        "counts": model["counts"],
        "token_estimate": model["token_estimate"],
        "html": html_result or {},
    }
    write_project_snapshot_manifest(root, manifest_payload)
    return {
        "passed": True,
        "addon": "project-snapshot-kit",
        "generated_files": generated_files,
        "skipped_files": skipped_files,
        "manifest_path": PROJECT_SNAPSHOT_MANIFEST_REL,
        "source_hash": model["source_hash"],
        "changed_only": changed_only,
        "render_html": render_html,
        "token_estimate": model["token_estimate"],
    }


def project_snapshot_file_href(raw: str) -> str | None:
    normalized = raw.strip().replace("\\", "/")
    if not normalized or "://" in normalized or " " in normalized:
        return None
    safe_prefix = (
        normalized.startswith("./")
        or normalized.startswith("../")
        or normalized.startswith("/")
        or normalized.startswith("agent-memory/")
        or normalized.startswith("agent-plans/")
        or normalized.startswith("docs/")
        or normalized.startswith("tools/")
        or normalized.startswith("addons/")
    )
    safe_suffix = pathlib.PurePosixPath(normalized).suffix.lower() in {
        ".md",
        ".html",
        ".py",
        ".json",
        ".jsonl",
        ".txt",
        ".yaml",
        ".yml",
    }
    if safe_prefix or safe_suffix:
        return urllib.parse.quote(normalized, safe="/#?=&:.-_")
    return None


def project_snapshot_inline_html(text: str) -> str:
    direct_href = project_snapshot_file_href(text)
    if direct_href:
        escaped_text = html_escape(text)
        return f"<a class='file-link' href='{direct_href}'>{escaped_text}</a>"

    def code_repl(match: re.Match[str]) -> str:
        raw = match.group(1)
        escaped = html_escape(raw)
        href = project_snapshot_file_href(raw)
        if href:
            return f"<a class='file-link' href='{href}'><code>{escaped}</code></a>"
        return f"<code>{escaped}</code>"

    escaped = html_escape(text)
    return re.sub(r"`([^`]+)`", code_repl, escaped)


def markdown_table_to_html(table_lines: list[str]) -> str:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in table_lines]
    if len(rows) < 2 or not all(rows):
        return "<pre class='md-table'>" + html_escape("\n".join(table_lines)) + "</pre>"
    separator = rows[1]
    if not all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in separator):
        return "<pre class='md-table'>" + html_escape("\n".join(table_lines)) + "</pre>"
    header = rows[0]
    body_rows = rows[2:]
    head_html = "".join(f"<th>{project_snapshot_inline_html(cell)}</th>" for cell in header)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{project_snapshot_inline_html(cell)}</td>" for cell in row) + "</tr>"
        for row in body_rows
    )
    return f"<div class='table-wrap'><table><thead><tr>{head_html}</tr></thead><tbody>{body_html}</tbody></table></div>"


def html_from_markdown_fragment(markdown: str) -> str:
    html_lines: list[str] = []
    in_list = False
    in_table = False
    table_lines: list[str] = []

    def flush_list() -> None:
        nonlocal in_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False

    def flush_table() -> None:
        nonlocal in_table, table_lines
        if not in_table:
            return
        html_lines.append(markdown_table_to_html(table_lines))
        table_lines = []
        in_table = False

    for raw in markdown_body(markdown).splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_list()
            flush_table()
            continue
        if stripped.startswith("|"):
            flush_list()
            in_table = True
            table_lines.append(stripped)
            continue
        flush_table()
        if stripped.startswith("### "):
            flush_list()
            html_lines.append(f"<h3>{project_snapshot_inline_html(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            flush_list()
            html_lines.append(f"<h2>{project_snapshot_inline_html(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            flush_list()
            html_lines.append(f"<h1>{project_snapshot_inline_html(stripped[2:])}</h1>")
        elif stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{project_snapshot_inline_html(stripped[2:])}</li>")
        else:
            flush_list()
            html_lines.append(f"<p>{project_snapshot_inline_html(stripped)}</p>")
    flush_list()
    flush_table()
    return "\n".join(html_lines)


def project_snapshot_metrics(
    story_text: str,
    execution_text: str,
    manifest: dict[str, Any],
) -> list[tuple[str, str, str]]:
    source_count = len(manifest.get("source_paths") or {})
    token_estimate = manifest.get("token_estimate") or {}
    estimated_input = token_estimate.get("estimated_refresh_input_tokens", 0)
    model_tokens_used = token_estimate.get("model_tokens_used", 0)
    sections = len(re.findall(r"^##\s+", story_text + "\n" + execution_text, flags=re.MULTILINE))
    return [
        ("Sources", str(source_count), "Indexed files considered"),
        ("Sections", str(sections), "Snapshot sections rendered"),
        ("Est. input", str(estimated_input), "Future narrative refresh budget"),
        ("Model tokens", str(model_tokens_used), "Used for this deterministic render"),
    ]


def project_snapshot_page(
    title: str,
    active: str,
    body: str,
    design: dict[str, str],
    generated_at: str,
    metrics: list[tuple[str, str, str]] | None = None,
) -> str:
    nav = [
        ("index.html", "Overview"),
        ("product.html", "Product"),
        ("workflows.html", "Workflows"),
        ("implementation.html", "Implementation"),
        ("activity.html", "Activity"),
        ("sources.html", "Sources"),
    ]
    nav_html = "".join(f"<a class='{ 'active' if href == active else '' }' href='{href}'>{label}</a>" for href, label in nav)
    metric_html = ""
    if metrics:
        metric_html = "<section class='metrics' aria-label='Snapshot metrics'>" + "".join(
            f"<article class='metric'><span>{html_escape(label)}</span><strong>{html_escape(value)}</strong><small>{html_escape(caption)}</small></article>"
            for label, value, caption in metrics
        ) + "</section>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_escape(title)}</title>
  <style>
    :root {{
      --bg: {design['bg']};
      --surface: {design['panel']};
      --surface-2: color-mix(in srgb, {design['panel']} 88%, {design['accent']});
      --ink: {design['ink']};
      --muted: {design['muted']};
      --line: {design['line']};
      --accent: {design['accent']};
      --radius: {design['radius']};
      --font-family: {design['font_family']};
      --density: {design.get('density', '20px')};
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font-family); font-size: 16px; }}
    header {{ padding: 30px min(5vw, 64px); background: var(--surface); border-bottom: 1px solid var(--line); }}
    .topline {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px; color: var(--muted); font-size: 13px; }}
    .badge {{ display: inline-flex; align-items: center; border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px; color: var(--accent); background: color-mix(in srgb, var(--surface) 82%, var(--accent)); font-weight: 700; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 20px; }}
    nav a {{ color: var(--muted); text-decoration: none; border: 1px solid var(--line); border-radius: 999px; padding: 8px 12px; background: var(--surface); }}
    nav a:hover {{ color: var(--ink); border-color: var(--accent); }}
    nav a.active {{ color: white; background: var(--accent); border-color: var(--accent); }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px min(5vw, 64px) 64px; }}
    h1 {{ margin: 10px 0 0; font-size: 42px; line-height: 1.08; letter-spacing: 0; }}
    h2 {{ margin-top: 30px; font-size: 25px; line-height: 1.2; letter-spacing: 0; }}
    h3 {{ margin-top: 22px; line-height: 1.3; letter-spacing: 0; }}
    p, li {{ color: var(--muted); line-height: 1.55; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .metric {{ background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 16px; min-width: 0; }}
    .metric span {{ display: block; color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .metric strong {{ display: block; color: var(--ink); font-size: 28px; line-height: 1.1; margin-top: 8px; }}
    .metric small {{ display: block; color: var(--muted); margin-top: 8px; line-height: 1.35; }}
    .panel {{ background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: var(--density); }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: var(--radius); margin: 16px 0; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 620px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ color: var(--ink); background: var(--surface-2); font-size: 12px; text-transform: uppercase; }}
    td {{ color: var(--muted); line-height: 1.5; }}
    tr:last-child td {{ border-bottom: 0; }}
    .md-table {{ overflow-x: auto; white-space: pre-wrap; background: var(--surface-2); border: 1px solid var(--line); border-radius: var(--radius); padding: 14px; }}
    code {{ overflow-wrap: anywhere; color: var(--ink); background: var(--surface-2); border: 1px solid var(--line); border-radius: 6px; padding: 1px 5px; }}
    .file-link {{ color: var(--accent); text-decoration: none; }}
    .file-link:hover {{ text-decoration: underline; }}
    details {{ border: 1px solid var(--line); border-radius: var(--radius); padding: 12px 14px; background: var(--surface-2); }}
    summary {{ cursor: pointer; color: var(--ink); font-weight: 700; }}
    @media (max-width: 840px) {{
      h1 {{ font-size: 32px; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 560px) {{
      header, main {{ padding-left: 18px; padding-right: 18px; }}
      .metrics {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="topline"><span class="badge">Project Snapshot</span><span>Generated {html_escape(generated_at)}</span><span>Markdown snapshots are the source of truth.</span></div>
    <h1>{html_escape(title)}</h1>
    <nav>{nav_html}</nav>
  </header>
  <main>{metric_html}<section class="panel">{body}</section></main>
</body>
</html>
"""


def render_project_snapshot_site(
    root: pathlib.Path,
    output_dir: pathlib.Path | None = None,
    title: str | None = None,
    audience: str = "private",
) -> dict[str, Any]:
    require_project_snapshot_addon(root)
    if audience != "private":
        raise ValueError("Project Snapshot Kit reports are private-only in the MVP.")
    story_path = root / pathlib.Path(PROJECT_STORY_SNAPSHOT_REL)
    execution_path = root / pathlib.Path(PROJECT_EXECUTION_SNAPSHOT_REL)
    if not story_path.exists() or not execution_path.exists():
        raise FileNotFoundError("Project snapshot Markdown is missing. Run build-project-snapshot before rendering HTML.")
    design = read_report_design(root)
    generated_at = utc_now()
    out_dir = output_dir or (root / "agent-memory" / "reports" / "project-site")
    out_dir.mkdir(parents=True, exist_ok=True)
    story_text = story_path.read_text(encoding="utf-8", errors="replace")
    execution_text = execution_path.read_text(encoding="utf-8", errors="replace")
    manifest = read_project_snapshot_manifest(root)
    metrics = project_snapshot_metrics(story_text, execution_text, manifest)
    source_lines = [
        f"- `{path}` `{str(hash_value)[:16]}`"
        for path, hash_value in sorted((manifest.get("source_paths") or {}).items())
    ]
    token_estimate = manifest.get("token_estimate", {})
    source_body = "# Sources\n\n" + "\n".join(source_lines or ["- No manifest sources found."])
    source_html = (
        html_from_markdown_fragment(source_body)
        + "\n<details open><summary>Token estimate</summary><pre class='md-table'>"
        + html_escape(json.dumps(token_estimate, indent=2, sort_keys=True))
        + "</pre></details>"
    )
    pages = {
        "index.html": html_from_markdown_fragment(story_text),
        "product.html": html_from_markdown_fragment(story_text),
        "workflows.html": html_from_markdown_fragment(story_text),
        "implementation.html": html_from_markdown_fragment(execution_text),
        "activity.html": html_from_markdown_fragment(execution_text),
        "sources.html": source_html,
    }
    written: list[str] = []
    for filename, body in pages.items():
        page_title = title or f"Project Snapshot: {project_defaults(root)['project_id']}"
        if filename != "index.html":
            page_title = f"{page_title} - {filename.removesuffix('.html').replace('-', ' ').title()}"
        out = out_dir / filename
        if write_text_if_changed(out, project_snapshot_page(page_title, filename, body, design, generated_at, metrics)):
            written.append(str(out.relative_to(root)).replace("\\", "/"))
    return {
        "path": str((out_dir / "index.html").relative_to(root)).replace("\\", "/"),
        "paths": written,
        "report_type": "project-site",
        "audience": audience,
        "records": 2,
    }


def render_execution_dashboard(
    root: pathlib.Path,
    output_dir: pathlib.Path | None = None,
    title: str | None = None,
    audience: str = "private",
) -> dict[str, Any]:
    require_project_snapshot_addon(root)
    if audience != "private":
        raise ValueError("Execution dashboard is private-only in the MVP.")
    execution_path = root / pathlib.Path(PROJECT_EXECUTION_SNAPSHOT_REL)
    if not execution_path.exists():
        raise FileNotFoundError("Project execution snapshot is missing. Run build-project-snapshot before rendering HTML.")
    design = read_report_design(root)
    generated_at = utc_now()
    out_dir = output_dir or (root / "agent-memory" / "reports" / "project-site")
    out_dir.mkdir(parents=True, exist_ok=True)
    execution_text = execution_path.read_text(encoding="utf-8", errors="replace")
    manifest = read_project_snapshot_manifest(root)
    metrics = project_snapshot_metrics("", execution_text, manifest)
    body = html_from_markdown_fragment(execution_text)
    title = title or f"Execution Dashboard: {project_defaults(root)['project_id']}"
    out = out_dir / "execution-dashboard.html"
    changed = write_text_if_changed(out, project_snapshot_page(title, "implementation.html", body, design, generated_at, metrics))
    return {
        "path": str(out.relative_to(root)).replace("\\", "/"),
        "paths": [str(out.relative_to(root)).replace("\\", "/")] if changed else [],
        "report_type": "execution-dashboard",
        "audience": audience,
        "records": 1,
    }


def find_parallels(root: pathlib.Path) -> dict[str, Any]:
    records = load_memory_records(root, include_sessions=False)
    candidates = []
    fields = ["problem_patterns", "failure_modes", "architecture_patterns", "stack_tags"]
    for i, left in enumerate(records):
        left_meta = left["metadata"]
        if left_meta.get("doc_type") not in DEFAULT_RAG_DOC_TYPES:
            continue
        for right in records[i + 1 :]:
            right_meta = right["metadata"]
            if right_meta.get("doc_type") not in DEFAULT_RAG_DOC_TYPES:
                continue
            if left_meta.get("memory_id") == right_meta.get("memory_id"):
                continue
            matches: dict[str, list[str]] = {}
            for field in fields:
                lvals = set(left_meta.get(field, []) if isinstance(left_meta.get(field, []), list) else [])
                rvals = set(right_meta.get(field, []) if isinstance(right_meta.get(field, []), list) else [])
                common = sorted(lvals & rvals)
                if common:
                    matches[field] = common
            if matches:
                candidates.append(
                    {
                        "left": left_meta["memory_id"],
                        "right": right_meta["memory_id"],
                        "matches": matches,
                        "status": "parallel-candidate",
                    }
                )
    out = root / "agent-memory" / "indexes" / "parallel-candidates.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    locked_atomic_write_text(out, "\n".join(json.dumps(row, sort_keys=True) for row in candidates) + ("\n" if candidates else ""))
    return {"path": str(out.relative_to(root)), "candidates": len(candidates)}


def compact_sessions(root: pathlib.Path) -> dict[str, Any]:
    session_dir = root / "agent-memory" / "sessions"
    out_dir = root / "agent-memory" / "compiled"
    out_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    for path in sorted(session_dir.rglob("*.md")) if session_dir.exists() else []:
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        if not meta.get("memory_id"):
            continue
        slug = pathlib.Path(path.stem).stem
        out = out_dir / f"compiled-{slug}.md"
        if out.exists():
            continue
        body = markdown_body(text)
        summary = meta.get("summary", body[:500].replace("\n", " "))
        source_rel = str(path.relative_to(root)).replace("\\", "/")
        compiled = f"""---
memory_id: "{meta.get('memory_id')}:compiled"
tenant_id: "{meta.get('tenant_id', '')}"
customer_id: "{meta.get('customer_id', '')}"
project_id: "{meta.get('project_id', '')}"
doc_type: "compiled"
status: "draft"
visibility: "{meta.get('visibility', 'private')}"
data_class: "{meta.get('data_class', 'internal')}"
semantic_title: "Compiled session: {meta.get('semantic_title', slug)}"
summary: "{str(summary).replace('"', "'")}"
concept_tags: []
stack_tags: []
problem_patterns: []
architecture_patterns: []
failure_modes: []
reusable_lessons: []
confidence: 0.6
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "{utc_now()}"
updated_at: "{utc_now()}"
source_hash: "{sha256_file(path)}"
edges:
  - type: "derived_from"
    target: "{meta.get('memory_id')}"
    reason: "Compiled from session"
    confidence: 1.0
---

# Compiled Session: {meta.get('semantic_title', slug)}

## Summary

{summary}

## Evidence

- Source: `{source_rel}`
"""
        locked_atomic_write_text(out, compiled)
        created += 1
    return {"created": created, "path": str(out_dir.relative_to(root))}


def read_event_payload(event_file: str | None) -> dict[str, Any]:
    if event_file:
        raw = pathlib.Path(event_file).read_text(encoding="utf-8-sig")
    else:
        raw = sys.stdin.read()
    raw = raw.lstrip("\ufeff").strip()
    if not raw:
        return {}
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Runtime event payload must be a JSON object.")
    return payload


def event_value(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = payload.get(key)
        if value not in {None, ""}:
            return str(value)
    return ""


def runtime_session_paths(root: pathlib.Path, session_id: str) -> dict[str, pathlib.Path]:
    session_slug = slugify(session_id, "runtime-session")
    session_dir = root / "agent-memory" / "sessions" / session_slug
    return {
        "session_dir": session_dir,
        "events": session_dir / "events.jsonl",
        "session_md": session_dir / "session.md",
        "summary_md": session_dir / "summary.md",
        "state": session_dir / "session-state.json",
        "lock": session_dir / ".session.lock",
    }


def read_runtime_session_state(paths: dict[str, pathlib.Path]) -> dict[str, Any]:
    if paths["state"].exists():
        try:
            state = json.loads(paths["state"].read_text(encoding="utf-8"))
            if isinstance(state, dict):
                return state
        except Exception:
            pass
    event_count = 0
    if paths["events"].exists():
        with paths["events"].open("r", encoding="utf-8", errors="replace") as handle:
            event_count = sum(1 for line in handle if line.strip())
    return {"event_count": event_count}


def write_runtime_session_state(paths: dict[str, pathlib.Path], state: dict[str, Any]) -> None:
    state = {**state, "updated_at": utc_now()}
    atomic_write_text(paths["state"], json.dumps(state, indent=2, sort_keys=True) + "\n")


def session_memory_id(defaults: dict[str, str], session_id: str) -> str:
    return "mem:{tenant_id}:{customer_id}:{project_id}:session:{slug}".format(
        tenant_id=slugify(defaults["tenant_id"], "tenant-local"),
        customer_id=slugify(defaults["customer_id"], "customer-local"),
        project_id=slugify(defaults["project_id"], "project-local"),
        slug=slugify(session_id, "runtime-session"),
    )


def write_runtime_session_markdown(
    root: pathlib.Path,
    session_id: str,
    runtime: str,
    agent_id: str,
    status: str,
    event_count: int,
    source_hash: str,
    last_event_type: str,
) -> pathlib.Path:
    defaults = project_defaults(root)
    paths = runtime_session_paths(root, session_id)
    paths["session_dir"].mkdir(parents=True, exist_ok=True)
    memory_id = session_memory_id(defaults, session_id)
    now = utc_now()
    source_rel = str(paths["events"].relative_to(root)).replace("\\", "/") if paths["events"].exists() else ""
    text = f"""---
memory_id: {yaml_string(memory_id)}
tenant_id: {yaml_string(defaults["tenant_id"])}
customer_id: {yaml_string(defaults["customer_id"])}
project_id: {yaml_string(defaults["project_id"])}
doc_type: "session"
status: {yaml_string(status)}
visibility: "private"
data_class: "confidential"
semantic_title: {yaml_string(f"{runtime} session {session_id}")}
summary: {yaml_string(f"Private runtime capture with {event_count} events; last event: {last_event_type or 'unknown'}.")}
concept_tags:
  - "agent-memory"
  - "runtime-capture"
stack_tags:
  - {yaml_string(runtime)}
problem_patterns: []
architecture_patterns:
  - "markdown-first-memory"
failure_modes: []
reusable_lessons: []
confidence: 0.7
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: {yaml_string(now)}
updated_at: {yaml_string(now)}
source_hash: {yaml_string(source_hash)}
edges: []
---

# Runtime Session Capture

This private session artifact was generated by the Agent Memory runtime plugin.

## Session

- Runtime: `{runtime}`
- Session ID: `{session_id}`
- Agent ID: `{agent_id}`
- Event count: `{event_count}`
- Raw event log: `{source_rel}`
- Last event: `{last_event_type or 'unknown'}`

Raw events are private working memory and must not be promoted to shared RAG directly.
"""
    atomic_write_text(paths["session_md"], text)
    return paths["session_md"]


def capture_runtime_event(
    root: pathlib.Path,
    payload: dict[str, Any],
    runtime: str = "generic",
    event_type: str | None = None,
    session_id: str | None = None,
    agent_id: str | None = None,
    capture_mode: str = "standard",
) -> dict[str, Any]:
    capture_mode = capture_mode if capture_mode in {"minimal", "standard", "full-private"} else "standard"
    runtime = runtime or event_value(payload, "runtime", "source") or "generic"
    event_type = event_type or event_value(payload, "hook_event_name", "event_type", "event", "type") or "RuntimeEvent"
    session_id = session_id or event_value(payload, "session_id", "conversation_id", "chat_id")
    if not session_id:
        transcript = event_value(payload, "transcript_path")
        session_id = pathlib.Path(transcript).stem if transcript else f"{runtime}-{utc_now()}-{uuid.uuid4().hex[:8]}"
    agent_id = agent_id or event_value(payload, "agent_id", "assistant_id") or runtime

    paths = runtime_session_paths(root, session_id)
    paths["session_dir"].mkdir(parents=True, exist_ok=True)
    with file_lock(paths["lock"]):
        state = read_runtime_session_state(paths)
        event_record = {
            "captured_at": utc_now(),
            "runtime": runtime,
            "event_type": event_type,
            "session_id": session_id,
            "agent_id": agent_id,
            "capture_mode": capture_mode,
            "payload_hash": sha256_text(json.dumps(payload, sort_keys=True)),
            "payload": redact_capture_value(payload, mode=capture_mode),
        }
        with paths["events"].open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event_record, sort_keys=True) + "\n")
        event_count = int(state.get("event_count") or 0) + 1
        write_runtime_session_state(
            paths,
            {
                "event_count": event_count,
                "last_event_type": event_type,
                "last_capture_mode": capture_mode,
                "events_bytes": paths["events"].stat().st_size,
            },
        )
        source_hash = sha256_file(paths["events"])
        session_md = write_runtime_session_markdown(root, session_id, runtime, agent_id, "active", event_count, source_hash, event_type)
    return {
        "captured": True,
        "runtime": runtime,
        "event_type": event_type,
        "session_id": session_id,
        "events_path": str(paths["events"].relative_to(root)).replace("\\", "/"),
        "session_path": str(session_md.relative_to(root)).replace("\\", "/"),
        "event_count": event_count,
        "source_hash": source_hash,
        "capture_mode": capture_mode,
    }


def safe_excerpt(value: Any, max_chars: int = 240) -> str:
    text = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    for pattern in SECRET_VALUE_PATTERNS:
        text = pattern.sub("[redacted-secret]", text)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def redact_capture_value(value: Any, key: str = "", mode: str = "standard") -> Any:
    if mode == "minimal":
        if isinstance(value, dict):
            return {k: redact_capture_value(v, k, mode) for k, v in value.items() if k in ALLOWLIST_CAPTURE_KEYS or k.endswith("_path")}
        if isinstance(value, list):
            return {"redacted_list_length": len(value)}
    if SECRET_KEY_RE.search(key):
        return "[redacted-sensitive-field]"
    if isinstance(value, dict):
        return {str(k): redact_capture_value(v, str(k), mode) for k, v in value.items()}
    if isinstance(value, list):
        limit = 20 if mode == "full-private" else 8
        redacted = [redact_capture_value(item, key, mode) for item in value[:limit]]
        if len(value) > limit:
            redacted.append({"truncated_items": len(value) - limit})
        return redacted
    if isinstance(value, str):
        cleaned = safe_excerpt(value, max_chars=4000 if mode == "full-private" else (1000 if key not in LARGE_CAPTURE_KEYS else 360))
        if key in LARGE_CAPTURE_KEYS and len(value) > len(cleaned):
            return {"excerpt": cleaned, "sha256": sha256_text(value), "original_chars": len(value)}
        return cleaned
    return value


def close_runtime_session(
    root: pathlib.Path,
    session_id: str,
    runtime: str = "generic",
    agent_id: str = "runtime-agent",
) -> dict[str, Any]:
    paths = runtime_session_paths(root, session_id)
    if not paths["events"].exists():
        raise FileNotFoundError(f"No runtime events found for session_id={session_id}")
    with file_lock(paths["lock"]):
        events = [json.loads(line) for line in paths["events"].read_text(encoding="utf-8").splitlines() if line.strip()]
        already_closed = any(str(event.get("event_type", "")).lower() == "runtimeclosed" for event in events)
        if not already_closed:
            close_record = {
                "captured_at": utc_now(),
                "runtime": runtime,
                "event_type": "RuntimeClosed",
                "session_id": session_id,
                "agent_id": agent_id,
                "capture_mode": "system",
                "payload_hash": sha256_text(f"{session_id}:RuntimeClosed"),
                "payload": {"closed": True},
            }
            with paths["events"].open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(close_record, sort_keys=True) + "\n")
            events.append(close_record)
            write_runtime_session_state(
                paths,
                {
                    "event_count": len(events),
                    "last_event_type": "RuntimeClosed",
                    "last_capture_mode": "system",
                    "events_bytes": paths["events"].stat().st_size,
                    "closed": True,
                },
            )

        event_types: dict[str, int] = {}
        prompt_excerpts = []
        tool_names = []
        for event in events:
            event_type = str(event.get("event_type", "RuntimeEvent"))
            event_types[event_type] = event_types.get(event_type, 0) + 1
            payload = event.get("payload", {})
            if not isinstance(payload, dict):
                continue
            prompt = payload.get("prompt") or payload.get("user_prompt") or payload.get("message")
            if prompt and len(prompt_excerpts) < 5:
                prompt_excerpts.append(safe_excerpt(prompt))
            tool_name = payload.get("tool_name") or payload.get("name")
            if tool_name and str(tool_name) not in tool_names:
                tool_names.append(str(tool_name))

        source_hash = sha256_file(paths["events"])
        last_event_type = events[-1].get("event_type", "RuntimeEvent") if events else "RuntimeEvent"
        session_md = write_runtime_session_markdown(root, session_id, runtime, agent_id, "reviewed", len(events), source_hash, str(last_event_type))
        defaults = project_defaults(root)
        memory_id = session_memory_id(defaults, session_id)
        compiled_id = f"{memory_id}:summary"
        events_rel = str(paths["events"].relative_to(root)).replace("\\", "/")
        session_rel = str(session_md.relative_to(root)).replace("\\", "/")
        summary_rel = str(paths["summary_md"].relative_to(root)).replace("\\", "/")
        now = utc_now()
        event_type_lines = "\n".join(f"- `{key}`: {value}" for key, value in sorted(event_types.items())) or "- None"
        prompt_lines = "\n".join(f"- {excerpt}" for excerpt in prompt_excerpts) or "- No prompt excerpts captured."
        tool_lines = "\n".join(f"- `{name}`" for name in tool_names[:20]) or "- No tool names captured."
        compiled = f"""---
memory_id: {yaml_string(compiled_id)}
tenant_id: {yaml_string(defaults["tenant_id"])}
customer_id: {yaml_string(defaults["customer_id"])}
project_id: {yaml_string(defaults["project_id"])}
doc_type: "session"
status: "draft"
visibility: "private"
data_class: "confidential"
semantic_title: {yaml_string(f"Draft summary for {runtime} session {session_id}")}
summary: {yaml_string(f"Draft private summary candidate for {runtime} session with {len(events)} captured events.")}
concept_tags:
  - "agent-memory"
  - "runtime-summary"
stack_tags:
  - {yaml_string(runtime)}
problem_patterns: []
architecture_patterns:
  - "markdown-first-memory"
failure_modes: []
reusable_lessons: []
confidence: 0.5
review_status: "unreviewed"
sanitization_status: "pending"
created_at: {yaml_string(now)}
updated_at: {yaml_string(now)}
source_hash: {yaml_string(source_hash)}
edges:
  - type: "derived_from"
    target: {yaml_string(memory_id)}
    reason: "Draft summary candidate generated from private runtime events"
    confidence: 1.0
---

# Draft Runtime Session Summary

This is a private draft summary candidate. A memory curator must review and sanitize it before any promotion.

## Event Mix

{event_type_lines}

## Prompt Excerpts

{prompt_lines}

## Tool Names

{tool_lines}

## Evidence

- Session markdown: `{session_rel}`
- Raw private events: `{events_rel}`
- Source hash: `{source_hash}`
"""
        atomic_write_text(paths["summary_md"], compiled)
        return {
            "closed": True,
            "session_id": session_id,
            "session_path": session_rel,
            "events_path": events_rel,
            "summary_path": summary_rel,
            "event_count": len(events),
            "event_types": event_types,
            "source_hash": source_hash,
            "already_closed": already_closed,
        }


def metrics(conn: sqlite3.Connection) -> dict[str, Any]:
    now = utc_now()
    total_agents = conn.execute("SELECT COUNT(*) AS n FROM agents").fetchone()["n"]
    active_agents = conn.execute("SELECT COUNT(*) AS n FROM agents WHERE status = 'active'").fetchone()["n"]
    total_tasks = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
    stale_leases = conn.execute(
        "SELECT COUNT(*) AS n FROM tasks WHERE lease_expires_at IS NOT NULL AND lease_expires_at <= ? AND status IN ('claimed', 'in_progress')",
        (now,),
    ).fetchone()["n"]
    by_status = {
        row["status"]: row["n"]
        for row in conn.execute("SELECT status, COUNT(*) AS n FROM tasks GROUP BY status").fetchall()
    }
    return {
        "generated_at": now,
        "total_agents": total_agents,
        "active_agents": active_agents,
        "total_tasks": total_tasks,
        "stale_leases": stale_leases,
        "tasks_by_status": by_status,
    }


class ThreadedHTTPServer(http.server.ThreadingHTTPServer):
    daemon_threads = True


def make_handler(root: pathlib.Path):
    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "AgentMemoryControlPlane/0.2"

        def log_message(self, fmt: str, *args: Any) -> None:
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            with connect(root) as conn:
                init_db(conn)
                if parsed.path == "/health":
                    journal = conn.execute("PRAGMA journal_mode").fetchone()[0]
                    payload = {"status": "ok", "db": str(db_path(root)), "journal_mode": journal, **metrics(conn)}
                    write_json(self, 200, payload)
                    return
                if parsed.path == "/metrics":
                    if require_auth(self, conn, root) is None:
                        return
                    write_json(self, 200, metrics(conn))
                    return
            write_json(self, 404, {"error": "not_found"})

        def do_POST(self) -> None:
            self.handle_write("POST")

        def do_PATCH(self) -> None:
            self.handle_write("PATCH")

        def handle_write(self, method: str) -> None:
            parsed = urllib.parse.urlparse(self.path)
            parts = [p for p in parsed.path.split("/") if p]
            body = read_json_body(self)
            with connect(root) as conn:
                init_db(conn)
                actor = require_auth(self, conn, root)
                if actor is None:
                    return
                try:
                    if method == "POST" and parsed.path == "/agents/register":
                        if actor != "admin":
                            write_json(self, 403, {"error": "admin_token_required"})
                            return
                        write_json(self, 200, register_agent(conn, body))
                        return
                    if method == "POST" and parsed.path == "/tasks":
                        write_json(self, 200, upsert_task(conn, body))
                        return
                    if len(parts) == 3 and parts[0] == "tasks" and parts[2] == "claim" and method == "POST":
                        status, payload = claim_task(conn, parts[1], body, actor)
                        write_json(self, status, payload)
                        return
                    if len(parts) == 3 and parts[0] == "tasks" and parts[2] == "heartbeat" and method == "POST":
                        status, payload = heartbeat_task(conn, parts[1], body, actor)
                        write_json(self, status, payload)
                        return
                    if len(parts) == 2 and parts[0] == "tasks" and method == "PATCH":
                        status, payload = update_task(conn, parts[1], body, actor)
                        write_json(self, status, payload)
                        return
                    if len(parts) == 3 and parts[0] == "tasks" and parts[2] == "release" and method == "POST":
                        status, payload = release_task(conn, parts[1], body, actor)
                        write_json(self, status, payload)
                        return
                    if len(parts) == 3 and parts[0] == "tasks" and parts[2] == "evidence" and method == "POST":
                        status, payload = add_evidence(conn, parts[1], body, actor)
                        write_json(self, status, payload)
                        return
                    if len(parts) == 3 and parts[0] == "gates" and parts[2] == "run" and method == "POST":
                        status, payload = add_gate_report(conn, parts[1], body, actor)
                        write_json(self, status, payload)
                        return
                    if parsed.path == "/context-pack/build" and method == "POST":
                        write_json(self, 200, build_context_pack(conn, root, body))
                        return
                    if parsed.path == "/memory/promote" and method == "POST":
                        write_json(self, 200, promote_memory(conn, root, body))
                        return
                    if parsed.path == "/exports/lightrag/build" and method == "POST":
                        corpus_type = body.get("corpus_type", "private")
                        if corpus_type not in CORPUS_TYPES:
                            write_json(self, 400, {"error": "invalid_corpus_type", "allowed": sorted(CORPUS_TYPES)})
                            return
                        write_json(
                            self,
                            200,
                            export_lightrag(
                                root,
                                body.get("tenant_id"),
                                customer_id=body.get("customer_id"),
                                project_id=body.get("project_id"),
                                corpus_type=corpus_type,
                                include_drafts=bool(body.get("include_drafts", False)),
                            ),
                        )
                        return
                except PermissionError as exc:
                    write_json(self, 403, {"error": str(exc)})
                    return
                except (KeyError, ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
                    write_json(self, 400, {"error": str(exc)})
                    return
            write_json(self, 404, {"error": "not_found"})

    return Handler


def serve(root: pathlib.Path, host: str, port: int) -> None:
    init_project(root)
    if host not in {"127.0.0.1", "localhost", "::1"} and not admin_token_path(root).exists():
        raise SystemExit("Refusing remote bind without admin token. Run init-agent-memory first.")
    server = ThreadedHTTPServer((host, port), make_handler(root))
    print(json.dumps({"status": "listening", "host": host, "port": port, "health": f"http://{host}:{port}/health"}, indent=2))
    server.serve_forever()


def test_contracts(root: pathlib.Path) -> dict[str, Any]:
    results = []

    def add(name: str, passed: bool, details: str = "") -> None:
        results.append({"name": name, "passed": passed, "details": details})

    for rel in REQUIRED_DIRS:
        add(f"dir:{rel}", (root / rel).is_dir(), "Required directory exists.")
    for rel in REQUIRED_FILES:
        add(f"file:{rel}", (root / rel).is_file(), "Required file exists.")
    if (root / "addons" / "compliance-light").exists():
        for rel in ADDON_REQUIRED_FILES:
            add(f"file:{rel}", (root / rel).is_file(), "Optional add-on file exists.")
    for schema in (root / "agent-memory" / "schemas").glob("*.json"):
        try:
            json.loads(schema.read_text(encoding="utf-8"))
            add(f"schema-json:{schema.name}", True, "Valid JSON.")
        except json.JSONDecodeError as exc:
            add(f"schema-json:{schema.name}", False, str(exc))
    addon_schema_dir = root / "addons" / "compliance-light" / "schemas"
    if addon_schema_dir.exists():
        for schema in addon_schema_dir.glob("*.json"):
            try:
                json.loads(schema.read_text(encoding="utf-8"))
                add(f"addon-schema-json:{schema.name}", True, "Valid JSON.")
            except json.JSONDecodeError as exc:
                add(f"addon-schema-json:{schema.name}", False, str(exc))
    gitignore = (root / ".gitignore").read_text(encoding="utf-8") if (root / ".gitignore").exists() else ""
    for pattern in [
        ".agent-control/agent-memory.sqlite*",
        ".agent-control/secrets/",
        "agent-memory/tmp/",
        "agent-memory/exports/retrieval-eval/",
        "agent-memory/exports/finalization-gates/",
        "agent-memory/exports/compliance/",
        "agent-memory/reports/project-site/",
        "agent-memory/project-snapshot/project-snapshot-manifest.json",
        "agent-plans/",
    ]:
        add(f"gitignore:{pattern}", pattern in gitignore, "Runtime or scratch path is ignored.")
    agents = root / "AGENTS.template.md"
    claude = root / "CLAUDE.template.md"
    if agents.exists() and claude.exists():
        add("runtime-instructions-sync", agents.read_text(encoding="utf-8") == claude.read_text(encoding="utf-8"), "AGENTS and CLAUDE templates should remain byte-identical.")
    placeholders = []
    for rel in ["PROJECT_CONTEXT.template.md", "AGENTS.template.md", "CLAUDE.template.md"]:
        text = (root / rel).read_text(encoding="utf-8")
        if "tenant_id" not in text and "TENANT_ID" not in text:
            placeholders.append(rel)
    add("tenant-fields-present", not placeholders, "Files missing tenant fields: " + ", ".join(placeholders))
    failed = [r for r in results if not r["passed"]]
    return {"project": str(root), "passed": not failed, "totalChecks": len(results), "failedChecks": len(failed), "results": results}


def run_evals(root: pathlib.Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(
        prefix="agent-memory-eval-",
        dir=str(root / ".agent-control" / "tmp") if (root / ".agent-control" / "tmp").exists() else None,
        ignore_cleanup_errors=True,
    ) as tmp:
        eval_root = pathlib.Path(tmp)
        with connect(eval_root, eval_root / "eval.sqlite") as conn:
            init_db(conn)
            agent_tokens = []
            for i in range(50):
                reg = register_agent(
                    conn,
                    {
                        "agent_id": f"agent-{i:02d}",
                        "tenant_id": "tenant_a",
                        "customer_id": "customer_a",
                        "project_id": "project_a",
                        "role": "worker",
                        "runtime": "codex",
                    },
                )
                agent_tokens.append(reg)
            register_agent(
                conn,
                {
                    "agent_id": "agent-other-tenant",
                    "tenant_id": "tenant_b",
                    "customer_id": "customer_b",
                    "project_id": "project_b",
                    "role": "worker",
                    "runtime": "claude-code",
                },
            )
            for i in range(200):
                upsert_task(
                    conn,
                    {
                        "task_id": f"task-{i:03d}",
                        "tenant_id": "tenant_a",
                        "customer_id": "customer_a",
                        "project_id": "project_a",
                        "epic_id": "epic-eval",
                        "workpackage_id": "wp-eval",
                        "status": "ready",
                        "qa_gate_ids": ["gate-required"],
                        "acceptance_criteria": "Pass required QA gate.",
                    },
                )

            lock = threading.Lock()
            claims: list[dict[str, Any]] = []

            def worker(agent_index: int) -> int:
                claimed = 0
                local_conn = connect(eval_root, eval_root / "eval.sqlite")
                try:
                    init_db(local_conn)
                    actor = local_conn.execute("SELECT * FROM agents WHERE agent_id = ?", (f"agent-{agent_index:02d}",)).fetchone()
                    for task_index in range(200):
                        status, payload = claim_task(local_conn, f"task-{task_index:03d}", {"agent_id": actor["agent_id"]}, actor)
                        if status == 200:
                            claimed += 1
                            with lock:
                                claims.append(payload)
                finally:
                    local_conn.close()
                return claimed

            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                counts = list(executor.map(worker, range(50)))

            claimed_task_ids = [c["task_id"] for c in claims]
            duplicate_claims = len(claimed_task_ids) - len(set(claimed_task_ids))
            actor_b = conn.execute("SELECT * FROM agents WHERE agent_id = 'agent-other-tenant'").fetchone()
            status_b, tenant_payload = claim_task(conn, "task-000", {"agent_id": "agent-other-tenant"}, actor_b)
            done_status, done_payload = update_task(conn, "task-000", {"agent_id": "agent-00", "status": "done"}, "admin")
            add_gate_report(conn, "gate-required", {"task_id": "task-000", "final_verdict": "pass", "dimensions": {"tests": "pass"}}, "admin")
            done_after_gate_status, _ = update_task(conn, "task-000", {"agent_id": "agent-00", "status": "done"}, "admin")
            summary = {
                "mode": "50-agent-simulation",
                "agents": 50,
                "tasks": 200,
                "total_claims": len(claims),
                "duplicate_claims": duplicate_claims,
                "max_claims_by_agent": max(counts),
                "tenant_isolation_status": status_b,
                "tenant_isolation_payload": tenant_payload,
                "done_without_gate_status": done_status,
                "done_without_gate_payload": done_payload,
                "done_after_gate_status": done_after_gate_status,
            }
            summary["passed"] = (
                len(claims) == 200
                and duplicate_claims == 0
                and status_b == 403
                and done_status == 409
                and done_after_gate_status == 200
            )
            return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent Memory Kit control plane and harness")
    parser.add_argument("--project-root", default=os.getcwd())
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init")
    validate_p = sub.add_parser("validate-memory")
    validate_p.add_argument("--strict", action="store_true")
    doctor_p = sub.add_parser("doctor")
    doctor_p.add_argument("--mode", default="auto", choices=["auto", "kit", "host"])
    index_p = sub.add_parser("build-memory-index")
    index_p.add_argument("--incremental", action="store_true")
    index_p.add_argument("--track-tombstones", action="store_true")
    rag_p = sub.add_parser("export-rag-documents")
    rag_p.add_argument("--corpus-type", default="private", choices=sorted(CORPUS_TYPES))
    rag_p.add_argument("--include-sessions", action="store_true")
    rag_p.add_argument("--include-drafts", action="store_true")
    rag_p.add_argument("--tenant-id")
    rag_p.add_argument("--customer-id")
    rag_p.add_argument("--project-id")
    graph_p = sub.add_parser("export-graphrag")
    graph_p.add_argument("--corpus-type", default="private", choices=sorted(CORPUS_TYPES))
    graph_p.add_argument("--include-drafts", action="store_true")
    graph_p.add_argument("--tenant-id")
    graph_p.add_argument("--customer-id")
    graph_p.add_argument("--project-id")
    sub.add_parser("find-parallels")
    sub.add_parser("compact-sessions")
    capture_p = sub.add_parser("capture-runtime-event")
    capture_p.add_argument("--event-file")
    capture_p.add_argument("--runtime", default="generic")
    capture_p.add_argument("--event-type")
    capture_p.add_argument("--session-id")
    capture_p.add_argument("--agent-id")
    capture_p.add_argument("--capture-mode", default="standard", choices=["minimal", "standard", "full-private"])
    close_p = sub.add_parser("close-runtime-session")
    close_p.add_argument("--session-id", required=True)
    close_p.add_argument("--runtime", default="generic")
    close_p.add_argument("--agent-id", default="runtime-agent")
    serve_p = sub.add_parser("serve")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8765)
    sub.add_parser("test-contracts")
    context_p = sub.add_parser("build-context-pack")
    context_p.add_argument("--task-id", required=True)
    context_p.add_argument("--tenant-id")
    context_p.add_argument("--customer-id")
    context_p.add_argument("--project-id")
    context_p.add_argument("--agent-role", default="worker")
    context_p.add_argument("--budget-chars", type=int)
    context_p.add_argument("--objective")
    snapshot_p = sub.add_parser("build-project-snapshot")
    snapshot_p.add_argument("--render-html", action="store_true")
    snapshot_p.add_argument("--changed-only", action="store_true")
    snapshot_p.add_argument("--token-budget", type=int, default=PROJECT_SNAPSHOT_DEFAULT_TOKEN_BUDGET)
    snapshot_p.add_argument("--allow-large-context", action="store_true")
    sub.add_parser("audit-retention")
    sub.add_parser("review-memory-conflicts")
    sub.add_parser("scan-memory-sensitive-data")
    sub.add_parser("compliance-doctor")
    sub.add_parser("run-evals")
    sub.add_parser("metrics")
    promote_p = sub.add_parser("promote")
    promote_p.add_argument("--tenant-id", required=True)
    promote_p.add_argument("--customer-id", required=True)
    promote_p.add_argument("--project-id", required=True)
    promote_p.add_argument("--source-path", required=True)
    promote_p.add_argument("--target-path", required=True)
    promote_p.add_argument("--review-path", required=True)
    promote_p.add_argument("--source-hash")
    promote_p.add_argument("--agent-id", default="cli-curator")
    export_p = sub.add_parser("export-lightrag")
    export_p.add_argument("--tenant-id")
    export_p.add_argument("--customer-id")
    export_p.add_argument("--project-id")
    export_p.add_argument("--corpus-type", default="private", choices=sorted(CORPUS_TYPES))
    export_p.add_argument("--include-drafts", action="store_true")
    eval_retrieval_p = sub.add_parser("eval-memory-retrieval")
    eval_retrieval_p.add_argument("--project-roots", nargs="+", required=True)
    eval_retrieval_p.add_argument("--output-dir")
    eval_retrieval_p.add_argument("--top-k", type=int, default=5)
    eval_retrieval_p.add_argument("--include-sessions", action="store_true")
    eval_retrieval_p.add_argument("--queries-file")
    eval_retrieval_p.add_argument("--min-overall-score", type=float)
    eval_retrieval_p.add_argument("--min-safety-score", type=float)
    render_p = sub.add_parser("render-memory-report")
    render_p.add_argument("--report-type", required=True, choices=sorted(REPORT_TYPE_LABELS))
    render_p.add_argument("--output-dir")
    render_p.add_argument("--title")
    render_p.add_argument("--audience", default="private", choices=["private", "customer", "shared"])
    render_p.add_argument("--tenant-id")
    render_p.add_argument("--customer-id")
    render_p.add_argument("--project-id")
    review_p = sub.add_parser("run-review-workflow")
    review_p.add_argument("--review-type", required=True, choices=sorted(REVIEW_WORKFLOW_TYPES))
    review_p.add_argument("--subject", required=True)
    review_p.add_argument("--question")
    review_p.add_argument("--slug")
    review_p.add_argument("--output-dir")
    review_p.add_argument("--tenant-id")
    review_p.add_argument("--customer-id")
    review_p.add_argument("--project-id")

    args = parser.parse_args(argv)
    root = resolve_root(args.project_root)

    try:
        if args.command == "init":
            print(json.dumps(init_project(root), indent=2, sort_keys=True))
        elif args.command == "validate-memory":
            result = validate_memory(root, strict=args.strict)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["passed"] else 1
        elif args.command == "doctor":
            result = memory_doctor(root, mode=args.mode)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["passed"] else 1
        elif args.command == "build-memory-index":
            print(json.dumps(build_memory_index(root, incremental=args.incremental, track_tombstones=args.track_tombstones), indent=2, sort_keys=True))
        elif args.command == "export-rag-documents":
            print(json.dumps(export_rag_documents(root, corpus_type=args.corpus_type, include_sessions=args.include_sessions, include_drafts=args.include_drafts, tenant_id=args.tenant_id, customer_id=args.customer_id, project_id=args.project_id), indent=2, sort_keys=True))
        elif args.command == "export-graphrag":
            print(json.dumps(export_graphrag(root, corpus_type=args.corpus_type, include_drafts=args.include_drafts, tenant_id=args.tenant_id, customer_id=args.customer_id, project_id=args.project_id), indent=2, sort_keys=True))
        elif args.command == "find-parallels":
            print(json.dumps(find_parallels(root), indent=2, sort_keys=True))
        elif args.command == "compact-sessions":
            print(json.dumps(compact_sessions(root), indent=2, sort_keys=True))
        elif args.command == "capture-runtime-event":
            payload = read_event_payload(args.event_file)
            print(
                json.dumps(
                    capture_runtime_event(root, payload, args.runtime, args.event_type, args.session_id, args.agent_id, args.capture_mode),
                    indent=2,
                    sort_keys=True,
                )
            )
        elif args.command == "close-runtime-session":
            print(json.dumps(close_runtime_session(root, args.session_id, args.runtime, args.agent_id), indent=2, sort_keys=True))
        elif args.command == "serve":
            serve(root, args.host, args.port)
        elif args.command == "test-contracts":
            result = test_contracts(root)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["passed"] else 1
        elif args.command == "build-context-pack":
            result = None
            db = db_path(root)
            if db.exists():
                with connect(root) as conn:
                    init_db(conn)
                    task = conn.execute("SELECT task_id FROM tasks WHERE task_id = ?", (args.task_id,)).fetchone()
                    if task:
                        result = build_context_pack(
                            conn,
                            root,
                            {
                                "task_id": args.task_id,
                                "tenant_id": args.tenant_id,
                                "agent_role": args.agent_role,
                                "budget_chars": args.budget_chars,
                                "objective": args.objective,
                            },
                        )
            if result is None:
                result = build_context_pack_markdown(
                    root,
                    args.task_id,
                    args.agent_role,
                    args.budget_chars,
                    tenant_id=args.tenant_id,
                    customer_id=args.customer_id,
                    project_id=args.project_id,
                    objective=args.objective,
                )
            print(json.dumps(result, indent=2, sort_keys=True))
        elif args.command == "build-project-snapshot":
            print(
                json.dumps(
                    build_project_snapshot(
                        root,
                        render_html=args.render_html,
                        changed_only=args.changed_only,
                        token_budget=args.token_budget,
                        allow_large_context=args.allow_large_context,
                    ),
                    indent=2,
                    sort_keys=True,
                )
            )
        elif args.command == "audit-retention":
            result = audit_retention(root)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["passed"] else 1
        elif args.command == "review-memory-conflicts":
            result = review_memory_conflicts(root)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["passed"] else 1
        elif args.command == "scan-memory-sensitive-data":
            result = scan_sensitive_data(root)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["passed"] else 1
        elif args.command == "compliance-doctor":
            result = compliance_doctor(root)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["passed"] else 1
        elif args.command == "run-evals":
            result = run_evals(root)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["passed"] else 1
        elif args.command == "metrics":
            with connect(root) as conn:
                init_db(conn)
                print(json.dumps(metrics(conn), indent=2, sort_keys=True))
        elif args.command == "promote":
            with connect(root) as conn:
                init_db(conn)
                result = promote_memory(
                    conn,
                    root,
                    {
                        "tenant_id": args.tenant_id,
                        "customer_id": args.customer_id,
                        "project_id": args.project_id,
                        "source_path": args.source_path,
                        "target_path": args.target_path,
                        "review_path": args.review_path,
                        "source_hash": args.source_hash,
                        "agent_id": args.agent_id,
                    },
                )
            print(json.dumps(result, indent=2, sort_keys=True))
        elif args.command == "export-lightrag":
            print(json.dumps(export_lightrag(root, args.tenant_id, customer_id=args.customer_id, project_id=args.project_id, corpus_type=args.corpus_type, include_drafts=args.include_drafts), indent=2, sort_keys=True))
        elif args.command == "eval-memory-retrieval":
            project_roots = [resolve_root(path) for path in args.project_roots]
            output_dir = pathlib.Path(args.output_dir).resolve() if args.output_dir else None
            queries_file = pathlib.Path(args.queries_file).resolve() if args.queries_file else None
            result = evaluate_memory_retrieval(
                root,
                project_roots,
                output_dir=output_dir,
                top_k=args.top_k,
                include_sessions=args.include_sessions,
                queries_file=queries_file,
                min_overall_score=args.min_overall_score,
                min_safety_score=args.min_safety_score,
            )
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["passed"] else 1
        elif args.command == "render-memory-report":
            output_dir = pathlib.Path(args.output_dir).resolve() if args.output_dir else None
            print(json.dumps(render_memory_report(root, args.report_type, output_dir=output_dir, title=args.title, audience=args.audience, tenant_id=args.tenant_id, customer_id=args.customer_id, project_id=args.project_id), indent=2, sort_keys=True))
        elif args.command == "run-review-workflow":
            output_dir = pathlib.Path(args.output_dir) if args.output_dir else None
            print(
                json.dumps(
                    run_review_workflow(
                        root,
                        args.review_type,
                        args.subject,
                        question=args.question,
                        slug=args.slug,
                        tenant_id=args.tenant_id,
                        customer_id=args.customer_id,
                        project_id=args.project_id,
                        output_dir=output_dir,
                    ),
                    indent=2,
                    sort_keys=True,
                )
            )
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc), "type": type(exc).__name__}, indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
