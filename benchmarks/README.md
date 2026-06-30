# Benchmarks

Owledge keeps benchmark claims local and reproducible.

## Public v0.7.0 Benchmark

The public v0.7.0 Benchmark Kit proof lives in [`v0.7.0/`](v0.7.0/).

Start here:

- [v0.7.0 benchmark summary](v0.7.0/README.md)
- [HTML comparison report](v0.7.0/results/comparison/index.html)
- [Methodology](v0.7.0/methodology.md)
- [Injected benchmark traps](v0.7.0/benchmark-explained.md)

On the v0.7.0 synthetic Markdown fixture, Owledge reduced context pollution by
88.36% on average and reduced tokens per correct answer by 83.54% on average
against the naive baseline. This is a fixture-bounded result; real-world
savings vary by vault shape, model, runtime, and retrieval configuration.

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
