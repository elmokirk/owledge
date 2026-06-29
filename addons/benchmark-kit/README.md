# Owledge Benchmark Kit

Optional real-file benchmark add-on for Owledge.

The kit creates deterministic synthetic Markdown fixture vaults, runs
retrieval/context-pack scenarios against those files, and writes JSON,
Markdown, HTML, and SVG reports focused on token usage, local performance, and
context pollution.

## Install

From an Owledge checkout:

```bash
python tools/owledge.py install-addon --project-root /path/to/project --addon benchmark-kit
```

## Run

Deterministic CI-safe benchmark:

```bash
python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode small --yes
python tools/benchmark-kit/render-benchmark-report.py --format html
```

Local Ollama benchmark:

```bash
python tools/benchmark-kit/run-benchmark-kit.py --mode local --scale-mode small --models gemma4:latest --yes
python tools/benchmark-kit/render-benchmark-report.py --format html
```

## Scale Modes

| Mode | Files | Purpose |
| --- | ---: | --- |
| `small` | 100 | CI, smoke tests, quick local demo |
| `mid` | 500 | Solo or power-user project vault |
| `large` | 1000 | Team-sized local benchmark |

## Outputs

Generated files are written under:

```text
.owledge/tmp/benchmark-kit/fixtures/<run-id>/<scale-mode>/
.owledge/exports/benchmark-kit/latest.json
.owledge/exports/benchmark-kit/latest.md
.owledge/exports/benchmark-kit/results.jsonl
.owledge/reports/generated/benchmark-kit/index.html
.owledge/reports/generated/benchmark-kit/charts.svg
```

Read `.owledge/benchmark-kit/BENCHMARK_EXPLAINED.md` before interpreting
results. It explains the injected distractor, stale, private, multi-hop,
handoff, and needle problems.
