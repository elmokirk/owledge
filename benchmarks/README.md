# Benchmarks

Owledge keeps benchmark claims local and reproducible.

## Included Scenarios

- KB scan on a synthetic Markdown vault
- context-pack generation for a scoped task
- runtime handoff/resume through durable session artifacts

## Run

```bash
python tools/owledge.py benchmark --project-root .
```

Run a larger local scale matrix before making public performance claims:

```bash
python tools/owledge.py benchmark --project-root . --scale-files 100,1000,10000
```

Use `50000` only as an explicit local stress test, not as a default CI run.

The script writes:

- `benchmarks/results/latest.json`
- `benchmarks/results/latest.md`

These files are generated locally and ignored by git by default.

## Reported Fields

- commit SHA
- OS and Python version
- synthetic vault sizes
- wall-clock runtime
- peak Python allocation bytes
- output bytes
- records per second for KB scans
