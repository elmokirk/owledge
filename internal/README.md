# Internal Dogfood Workspace

This directory is the maintainers' live dogfood workspace. It is **not** shipped
to users.

## Purpose

- Generated artifacts (indexes, exports, compiled snapshots, decision traces,
  red-team reports, benchmarks) live here.
- Maintainers run the full gate suite against this directory.
- Everything here is tracked in git for reproducibility.

## Usage

```bash
# Dogfood health check
python tools/agent_memory_cli.py --project-root internal doctor --mode host

# Full finalization gates
python tools/owledge.py finalization-gates --project-root internal --include-compliance --include-exports

# Red-team QA
python tools/owledge.py redteam-qa --project-root internal

# Benchmarks
python tools/owledge.py benchmark --project-root internal --scale-files 100 --seed 1
```

## Boundary Rule

Never write dogfood artifacts (decision traces, compiled snapshots, indexes,
exports) into `templates/`. That directory is the shipped product source. This
directory is the only place generated dogfood content should accumulate.