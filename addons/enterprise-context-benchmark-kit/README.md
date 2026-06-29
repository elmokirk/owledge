# Enterprise Context Benchmark Kit

Optional research-grade add-on for proving Owledge context hygiene before making
token or cost claims.

## Experiment Question

How do context assembly strategies behave as a Markdown-first agent memory vault
grows from a fresh project to a synthetic two-year enterprise project?

## Hypotheses

- H1: Scoped Owledge context packs grow sublinearly compared with full-vault
  prompting.
- H2: Owledge context packs reduce irrelevant-context ratio compared with naive
  paste and keyword search.
- H3: Metadata-first selection plus scoped context remains closer to the oracle
  set than full-vault prompting under a tighter token budget.

## What It Measures

- Full vault prompt size.
- Naive paste from recent project history.
- Keyword search from query terms.
- Metadata-first scan.
- Owledge scoped context pack.
- Oracle ground-truth source set.

Metrics include prompt tokens, estimated input cost, useful-source precision and
recall, irrelevant-token ratio, oracle distance, dropped-source reasons, runtime,
peak memory, and privacy leakage count.

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon enterprise-context-benchmark-kit
```

## Run

```bash
python tools/enterprise-context-benchmark/run-enterprise-context-benchmark.py --project-root . --profile enterprise_default --seed 42
```

`enterprise_default` runs the full growth curve from fresh through 4,800
Markdown files. `enterprise_full` extends the same curve to 10,000 files.

Outputs:

```text
benchmarks/results/context-growth.json
benchmarks/results/context-growth-charts.json
benchmarks/results/token-efficiency.md
.owledge/reports/enterprise-context-benchmark/index.html
.owledge/reports/enterprise-context-benchmark/*.svg
```

## Guardrails

- Generated benchmark corpora stay under `.agent-control/tmp/`.
- Reports are generated views, not canonical memory.
- Cost numbers are scenario estimates, not universal savings claims.
- Raw private session logs are not benchmark inputs.
- Charts are generated from `context-growth.json` and
  `context-growth-charts.json`; do not hardcode result values in HTML.
- Publication-style claims must cite commit, seed, profile, tokenizer, and
  command.
