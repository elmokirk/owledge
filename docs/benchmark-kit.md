# Benchmark Kit

Benchmark Kit is an optional Owledge add-on for real-file local benchmarking.
It is not part of the lean core install surface.

The add-on creates deterministic English Markdown fixture vaults, injects
known retrieval problems, runs deterministic or local Ollama benchmark modes,
and writes JSON, Markdown, HTML, and SVG reports.

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon benchmark-kit
```

## Run

Deterministic CI-safe run:

```bash
python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode small --yes
python tools/benchmark-kit/render-benchmark-report.py --format html
```

Local Ollama run:

```bash
python tools/benchmark-kit/run-benchmark-kit.py --mode local --scale-mode small --models gemma4:latest --yes
python tools/benchmark-kit/render-benchmark-report.py --format html
```

## Scale Modes

| Mode | Files | Use |
| --- | ---: | --- |
| `small` | 100 | CI, smoke tests, quick local demo |
| `mid` | 500 | Solo or power-user project vault |
| `large` | 1000 | Team-sized local benchmark |

`xl`, 10k-file stress tests, external datasets, own-vault benchmarking, and
cloud/frontier matrices are roadmap items.

## Injected Problems

Read `.owledge/benchmark-kit/BENCHMARK_EXPLAINED.md` after installing the
add-on. It explains the intentionally injected benchmark problems:

- `needle`
- `multi-hop`
- `stale-conflict`
- `privacy-trap`
- `distractor-heavy`
- `handoff-resume`

## Outputs

Generated outputs are ignored by default:

```text
.owledge/tmp/benchmark-kit/fixtures/<run-id>/<scale-mode>/
.owledge/exports/benchmark-kit/latest.json
.owledge/exports/benchmark-kit/latest.md
.owledge/exports/benchmark-kit/results.jsonl
.owledge/reports/generated/benchmark-kit/index.html
.owledge/reports/generated/benchmark-kit/charts.svg
```

The HTML report leads with token usage, context pollution, local model
throughput, duration, privacy failures, and stale-context failures before
showing research-style precision and recall metrics.
