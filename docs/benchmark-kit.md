# Benchmark Kit

Benchmark Kit is an optional Owledge add-on for real-file local benchmarking.
It is not part of the lean core install surface.

The add-on creates deterministic English Markdown fixture vaults, injects
known retrieval problems, runs deterministic or local Ollama benchmark modes,
and writes JSON, Markdown, HTML, and SVG reports.

Benchmark Kit has two report layers:

| Layer | Command | Purpose |
| --- | --- | --- |
| Single-run report | `run-benchmark-kit.py` plus `render-benchmark-report.py` | Shows baseline, Owledge, and oracle behavior for one model run. |
| Comparison report | `compare-benchmark-runs.py` | Compares completed model runs and turns the results into a publishing proof story. |

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

Local and cloud model runs should be executed sequentially. Do not run multiple
Ollama benchmarks in parallel if you want comparable GPU/VRAM, duration, and
tokens/sec measurements.

Multi-model comparison after completed runs:

```bash
python tools/benchmark-kit/compare-benchmark-runs.py --inputs \
  .owledge/exports/benchmark-kit-gemma4-latest/latest.json \
  .owledge/exports/benchmark-kit-qwen3-5-4b/latest.json \
  .owledge/exports/benchmark-kit-glm-5-1-cloud/latest.json \
  --output .owledge/reports/generated/benchmark-kit-comparison
```

The comparison command never calls Ollama and never runs models. It only reads
completed `latest.json` reports.

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
.owledge/exports/benchmark-kit-comparison/latest.json
.owledge/exports/benchmark-kit-comparison/latest.md
.owledge/reports/generated/benchmark-kit-comparison/index.html
.owledge/reports/generated/benchmark-kit-comparison/charts.svg
```

The HTML report leads with token usage, context pollution, local model
throughput, duration, privacy failures, and stale-context failures before
showing research-style precision and recall metrics.

The comparison HTML report leads with an Executive Verdict, Creator Pull Quote,
Model Matrix, Before vs Owledge charts, Scenario Heatmap, audience
interpretation, and caveats. It compares `metadata_scan` against
`owledge_context_pack` for privacy failures, stale failures, context pollution,
tokens per correct answer, total tokens, scenario pass rate, handoff resume
score, and tokens/sec.

`oracle` is the ground-truth reference ceiling from the fixture generator. It is
not a model and it is not an Owledge product claim.
