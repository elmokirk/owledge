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

The script writes:

- `benchmarks/results/latest.json`
- `benchmarks/results/latest.md`

These files are generated locally and ignored by git by default.
