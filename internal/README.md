# Internal Dogfood Workspace

This directory is the maintainers' live dogfood workspace. It is **not** shipped
to users.

## Purpose

- Generated artifacts (indexes, exports, compiled snapshots, decision traces,
  red-team reports, benchmarks) live here.
- Maintainers run the full gate suite against this directory.
- Generated artifacts (exports, red-team reports, tmp, indexes) are ignored by
  git. Structural directories, the latest export snapshot, and finalization-gate
  summaries are tracked for reproducibility.

## Usage

```bash
# Dogfood health check
python tools/owledge_core.py --project-root internal doctor --mode host

# Full finalization gates (auto-detects internal/owledge/ for memory ops)
python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports

# Red-team QA (auto-detects internal/owledge/)
python tools/owledge.py redteam-qa --project-root .

# Benchmarks (auto-detects internal/owledge/)
python tools/owledge.py benchmark --project-root . --scale-files 100 --seed 1
```

## Boundary Rule

Never write dogfood artifacts (decision traces, compiled snapshots, indexes,
exports) into `templates/`. That directory is the shipped product source. This
directory is the only place generated dogfood content should accumulate.

## Keeping dogfood in sync

The `internal/owledge/templates/` tree must mirror `templates/owledge/templates/`
(one-way: product source -> dogfood). Dogfood-only artifacts (decisions, sessions, evidence,
handoffs, decision-trace) are NOT synced and live only in `internal/`.

Check for drift:

```bash
python tools/owledge_core.py --project-root . dogfood-sync-check
```

Reconcile drift:

```bash
python tools/owledge.py sync-dogfood --dry-run   # default, shows what would change
python tools/owledge.py sync-dogfood --apply     # copies templates -> internal
```

The `dogfood-sync` finalization gate fails if template files drift.