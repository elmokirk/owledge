# Pilot Benchmark Kit

This optional add-on turns existing Owledge gate outputs into a compact pilot
proof: JSON metrics, a Markdown summary, and a static HTML/SVG chart view.

Charts are generated views. They do not become canonical memory.

## Inputs

The report builder reads whichever files exist:

- `benchmarks/results/latest.json`
- `.owledge/exports/retrieval-eval/retrieval-eval.json`
- `.owledge/exports/finalization-gates/quality-ratchet-summary.json`
- `.owledge/exports/finalization-gates/latest.json`
- optional installed fixture inputs under `.owledge/pilot-benchmark/fixtures/`

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon pilot-benchmark-kit
```

## Build A Report

```bash
python tools/pilot-benchmark/render-pilot-benchmark.py --project-root .
```

The script writes generated views under
`.owledge/reports/pilot-benchmark/`.

## Guardrails

- no raw session logs
- no private user memory
- no canonical writes
- no hosted service
- no dashboard app
