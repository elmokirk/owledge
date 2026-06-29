---
memory_id: "mem:owledge:global:owledge:workpackage:v0.7.0-pre-release-agent-tasklist"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "workpackage"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge v0.7.0 pre-release agent tasklist"
summary: "Agent-facing phase checklist and QA gate tracker for the Owledge v0.7.0 pre-release realization plan."
concept_tags:
  - "release-readiness"
  - "subagent-coordination"
  - "phase-checklist"
  - "qa-gates"
stack_tags:
  - "python"
  - "markdown"
  - "github-actions"
problem_patterns:
  - "interrupted-session-resume"
  - "parallel-subagent-plan-conflict"
architecture_patterns:
  - "orchestrator-owned-tasklist"
  - "lane-handoff"
  - "qa-gate-before-checkbox"
failure_modes:
  - "checkbox-without-evidence"
  - "partial-phase-resume"
confidence: 0.9
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "2026-06-26T00:00:00Z"
updated_at: "2026-06-26T00:00:00Z"
source_hash: ""
edges:
  - type: "derived_from"
    target: "mem:owledge:global:owledge:plan:v0.7.0-pre-release-realization"
    confidence: 0.95
    reason: "This tasklist operationalizes the v0.7.0 pre-release realization plan."
---

# Owledge v0.7.0 Pre-Release Agent Tasklist

## Resume State

Current resume point: **Phase 11 - Final verification, QA checks**.

Recovered interruption point: **Phase 9 - Runtime/add-on boundary**. The prior
session began migrating add-on public paths from `.owledge/` to `.owledge/`,
then stopped during smoke testing. Phase 9 was restarted from scratch, BOMs were
removed, manifests were hardened, all add-ons installed into `.owledge/`, and
core generated outputs were verified to avoid root `.owledge/`.

Remaining local verification caveats: `twine` and `pytest` are not installed in
the local runtime, and local `uvx` is blocked by sandbox access to AppData. CI
and release workflows are wired to cover these checks.

## Agent Rules

- Orchestrator owns this tasklist and central release notes.
- Subagents write lane handoffs under `.owledge/workpackages/<wp>/lanes/<agent-id>.md`
  in generated user projects, or `internal/owledge/workpackages/<wp>/lanes/`
  in this dogfood repository until dogfood memory is migrated.
- A checkbox is only checked after its QA evidence exists.
- If a checked box becomes stale after later edits, uncheck it and rerun the
  phase gate.
- Resume rule: find the first unchecked checkbox and continue there.

## Phase 0 - Branch And Baseline

Goal: create branch, record dirty state, and establish baseline gates.

QA gate:

```bash
git status --short
python tools/owledge.py concept-audit --project-root . --format summary
python tools/owledge.py test release-trust --project-root .
python tools/owledge.py test public-docs --project-root .
python tools/owledge_core.py --project-root . test-contracts
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 1 - `.owledge/` Foundation

Goal: quickstart/init create `OWLEDGE.md` and `.owledge/`; public behavior no
longer depends on `OWLEDGE.md`.

QA gate:

```bash
python tools/owledge.py quickstart --target .agent-control/tmp/owledge-foundation-smoke
python tools/owledge.py doctor --project-root .agent-control/tmp/owledge-foundation-smoke
python tools/owledge_core.py --project-root . test-contracts
python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 2 - Generated-State Policy

Goal: private/generated state is ignored; durable plans, reviews, handoffs,
audiences, and research remain trackable.

QA gate:

```bash
git status --short
python tools/owledge.py test quality-ratchet --project-root .
python tools/owledge_core.py --project-root . sdist-clean
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 3 - Packaging And CLI Parity

Goal: package data, wheel/sdist, and smoke installs expose v0.7.0 templates and
commands.

QA gate:

```bash
python -m build
twine check dist/*
uvx --from dist/<built-wheel>.whl owledge --help
uvx --from dist/<built-wheel>.whl owledge quickstart --target .agent-control/tmp/owledge-wheel-smoke
python tools/owledge_core.py --project-root . sdist-clean
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 4 - CI Release Gates

Goal: GitHub workflows validate the v0.7.0 release surface.

QA gate:

```bash
python -m py_compile tools/owledge.py tools/owledge_core.py tools/build_project_folder_kit.py tools/owledge_mcp.py
python tools/owledge.py test benchmark-kit-ci --project-root .
python tools/owledge.py test mcp-readonly --project-root .
python tools/owledge.py test runtime-adapters --project-root .
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 5 - Read-Only MCP P0

Goal: expose scoped read-only MCP tools and no write tools.

QA gate:

```bash
python tools/owledge.py test mcp-readonly --project-root .
python tools/owledge.py test runtime-adapters --project-root .
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 6 - Native Planning Layers

Goal: reviews, audiences, research, and brainstorm candidate layer exist as
native Owledge artifacts.

QA gate:

```bash
python tools/owledge.py concept-audit --project-root . --format summary
python tools/owledge_core.py --project-root . validate-memory --strict
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 7 - Wikilink Audit

Goal: read-only wikilink audit reports valid, broken, and ambiguous links and
does not auto-write canonical edges.

QA gate:

```bash
python tools/owledge.py wikilink-audit --project-root . --check
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 8 - Benchmark Kit V2

Goal: deterministic CI mode, local Ollama scan/selection, sequential model runs,
and HTML-first reporting exist.

QA gate:

```bash
python tools/owledge.py test benchmark-kit-ci --project-root .
python tools/owledge.py benchmark-kit run --mode ci --output .owledge/reports/generated/benchmark --yes
python tools/owledge.py benchmark-kit report --format html
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 9 - Runtime/Add-on Boundary

Goal: add-ons and runtime/plugin surfaces install without recreating root
`.owledge/`; roadmap-only claims remain bounded.

QA gate:

```bash
python tools/owledge_core.py --project-root . addon-boundary-check
python tools/owledge.py quickstart --target .agent-control/tmp/owledge-addon-smoke
python tools/owledge.py install-addon --project-root .agent-control/tmp/owledge-addon-smoke --addon launch-demo-kit
python tools/owledge.py install-addon --project-root .agent-control/tmp/owledge-addon-smoke --addon project-snapshot-kit
python tools/owledge.py project-snapshot --project-root .agent-control/tmp/owledge-addon-smoke --yes
python tools/owledge.py test runtime-adapters --project-root .
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 10 - Final Docs And Launch Surface

Goal: README, docs, command reference, roadmap, troubleshooting, Mermaid
workflows, and links reflect the final implementation.

QA gate:

```bash
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py test release-trust --project-root .
python tools/owledge.py wikilink-audit --project-root . --check
```

Checklist:

- [x] implementation done
- [x] QA checks done
- [x] quick review done

## Phase 11 - Final Verification

Goal: v0.7.0 release candidate is publish-ready.

QA gate:

```bash
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py test release-trust --project-root .
python tools/owledge.py test launch-readiness --project-root .
python tools/owledge.py test runtime-adapters --project-root .
python tools/owledge.py test quality-ratchet --project-root .
python tools/owledge_core.py --project-root . test-contracts
python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports
python tools/owledge.py concept-audit --project-root . --format summary
python -m pytest tests/unit -q
python -m build
```

Checklist:

- [x] implementation done
- [ ] QA checks done
- [ ] quick review done
