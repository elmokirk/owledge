# Owledge Benchmark Kit

Optional real-file benchmark add-on for Owledge.

The kit creates deterministic synthetic Markdown fixture vaults, runs
retrieval/context-pack scenarios against those files, and writes JSON,
Markdown, HTML, and SVG reports focused on token usage, local performance, and
context pollution.

The kit has two report layers:

| Layer | Command | Purpose |
| --- | --- | --- |
| Single-run report | `run-benchmark-kit.py` plus `render-benchmark-report.py` | Shows baseline, Owledge, and oracle behavior for one model run. |
| Comparison report | `compare-benchmark-runs.py` | Compares completed model runs and turns the results into a publishing proof story. |

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

Run local and cloud model benchmarks sequentially. Parallel local runs can
distort GPU/VRAM, duration, and tokens/sec measurements.

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
.owledge/exports/benchmark-kit-comparison/latest.json
.owledge/exports/benchmark-kit-comparison/latest.md
.owledge/reports/generated/benchmark-kit-comparison/index.html
.owledge/reports/generated/benchmark-kit-comparison/charts.svg
```

Read `.owledge/benchmark-kit/BENCHMARK_EXPLAINED.md` before interpreting
results. It explains the injected distractor, stale, private, multi-hop,
handoff, and needle problems.

The comparison report includes an Executive Verdict, Creator Pull Quote, Model
Matrix, Before vs Owledge charts, Scenario Heatmap, audience interpretation,
and caveats. `oracle` is the ground-truth reference ceiling from the fixture
generator, not a model or product claim.
