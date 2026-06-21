# Pilot Benchmark Kit

Pilot Benchmark Kit turns existing Owledge JSON outputs into static review
views for a pilot stakeholder conversation. It does not create canonical memory.

## Inputs

The renderer accepts any subset of these JSON files:

| Input | Typical source |
| --- | --- |
| Benchmark result | `benchmarks/results/latest.json` |
| Retrieval eval | `agent-memory/exports/retrieval-eval/retrieval-eval.json` |
| Quality ratchet or finalization gates | `agent-memory/exports/finalization-gates/quality-ratchet-summary.json` or `agent-memory/exports/finalization-gates/latest.json` |

## Output

The renderer writes:

| File | Purpose |
| --- | --- |
| `pilot-benchmark.md` | Human-readable summary for review threads. |
| `pilot-benchmark.html` | Standalone visual report for demos. |
| `pilot-benchmark.svg` | Static chart asset that can be embedded elsewhere. |

These files are generated views. Treat the original JSON exports and reviewed
project Markdown as the source of truth.

## Commands

Render from default project outputs:

```bash
python tools/pilot-benchmark/render-pilot-benchmark.py --project-root .
```

Render from the installed starter fixtures:

```bash
python tools/pilot-benchmark/render-pilot-benchmark.py ^
  --project-root . ^
  --benchmark agent-memory/pilot-benchmark/fixtures/benchmark-latest.json ^
  --retrieval agent-memory/pilot-benchmark/fixtures/retrieval-eval.json ^
  --finalization agent-memory/pilot-benchmark/fixtures/finalization-summary.json
```

Write to a custom report directory:

```bash
python tools/pilot-benchmark/render-pilot-benchmark.py --project-root . --out-dir tmp/pilot-benchmark
```

## Reading The Charts

- Score bars show retrieval quality and finalization gate scores on a 0-100
  scale.
- Runtime bars show benchmark and finalization step durations in seconds.
- Missing inputs are reported in the Markdown and HTML instead of failing the
  command. Use `--strict` when missing inputs should fail CI.
