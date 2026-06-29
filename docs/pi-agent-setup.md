# PI Agent Setup Guide

## What The PI Agent Does

The PI Agent is an optional intelligence layer that scans project and
cross-project memory to find:

- **Parallels** across projects (shared `concept_tags`,
  `problem_patterns`, `architecture_patterns`, `failure_modes`)
- **Recurring errors** (repeated `failure_modes` across records)
- **Central project candidates** (tags appearing 2+ times across projects)
- **Growth signals** (top tags that may indicate missing modules or patterns)
- **Stale records** (research cards past their `valid_until` date)

## What The PI Agent Does NOT Do

- It does **not** auto-promote findings to canonical memory.
- It does **not** rewrite project files.
- It does **not** require an LLM provider API key for v1.
- It does **not** run as a background daemon.
- It does **not** make decisions — it produces candidate artifacts for curator
  review.

## Does PI Agent Need Provider Auth?

**No, not for the current deterministic mode.**

The PI Agent v1 runs **deterministic signals locally** using frontmatter tag
intersections and count-based heuristics (`owlib/src/owlib/pi.py`). It reads
`concept_tags`, `problem_patterns`, `architecture_patterns`, `failure_modes`,
and `reusable_lessons` from frontmatter and computes overlaps. No external LLM
call is made.

A future **semantic mode** (planned, not implemented) would use an LLM to detect
semantic similarity beyond exact tag matches. That mode would require provider
auth (OpenAI, Anthropic, or local Ollama). Until then, no API key is needed.

| Mode | Status | Auth needed |
| --- | --- | --- |
| Deterministic (tag intersection + counts) | Implemented, usable | No |
| Semantic (LLM-assisted similarity) | Planned, not implemented | Yes (future) |

## Setup

### 1. Initialize The Owlib Library

```bash
python -m owlib init --library-root /path/to/owl-library
```

This creates the library structure and `owlib.yaml` config.

### 2. Register Projects

```bash
python -m owlib register-project --library-root /path/to/owl-library --path /path/to/project
```

A project must have `OWLEDGE.md` and `.owledge/` to be registered.

### 3. Sync Reviewed Records

```bash
python -m owlib sync --library-root /path/to/owl-library --reviewed-only
```

Only records with `review_status: approved` (or `status: active/promoted/
reviewed`) are imported. Unsafe shared records are rejected.

### 4. Build The Index

```bash
python -m owlib index --library-root /path/to/owl-library
```

### 5. Run PI Agent

```bash
# Full PI report
python -m owlib pi report --library-root /path/to/owl-library

# Find parallels across projects
python -m owlib pi find-parallels --library-root /path/to/owl-library

# Detect recurring errors
python -m owlib pi recurring-errors --library-root /path/to/owl-library

# Suggest central project candidates
python -m owlib pi suggest-central-projects --library-root /path/to/owl-library

# Red-team the PI report (quality gate)
python -m owlib pi redteam --library-root /path/to/owl-library
```

### 6. Optional PI Agent Module

```bash
python -m owlib module install --library-root /path/to/owl-library pi-agent
python -m owlib module status --library-root /path/to/owl-library
```

The `pi-agent` module adds candidate-only roles: Parallel Scout, Freshness
Auditor, Conflict Reviewer, Idea Synthesizer, Quality Ratchet Monitor, and
Owl Librarian.

## Notification

Currently, PI Agent findings are written to:

- `library/reports/pi-agent/pi-report-*.md`
- `library/parallels/parallel-candidates.jsonl`
- `library/reports/pi-agent/recurring-errors.jsonl`
- `library/reports/pi-agent/central-project-candidates.jsonl`

The agent reads these at session start when the user asks about cross-project
intelligence. A notification artifact (`parallels-notice.md`) that the agent
surfaces proactively is planned (see `docs/feedback-round-2026-06.md` FB-006).

## Guardrails

- PI findings are **candidate knowledge**. Review status defaults to
  `unreviewed`.
- Promotion into project `canonical/`, `patterns/`, or `lessons/` requires
  explicit curator approval.
- The PI red-team scores reports from 1-100; scores below 95 require revision
  before promotion.
- Private tenant data must not enter shared reports.
- Raw chat logs are not a primary source.

## Skills

The following skills provide PI Agent behavior guidance for agents:

- `skills/pi-agent-global-intelligence/` — cross-project parallels, trends,
  recurring errors, central project candidates.
- `skills/personal-pi-agent/` — private global user knowledge (preferences,
  goals, ideas, research freshness, coach reports).
- `skills/pi-agent-red-team-evaluator/` — 1-100 scorecards for PI findings.
- `skills/pi-agent-workspace-quality/` — workspace health and quality checks.

## Troubleshooting

| Problem | Cause | Fix |
| --- | --- | --- |
| `Missing OWLEDGE.md` | Project not initialized with Owledge | Run `python tools/owledge.py init-project --target /path/to/project` |
| `No projects registered` | No projects synced to library | Run `register-project` for each project |
| `No parallels found` | Projects share no tags | Add `concept_tags` / `problem_patterns` to frontmatter |
| `PI report score < 95` | Report missing sections | Ensure report has Parallel Candidates, Growth Signals, Recommended Actions |