# Owledge v0.7.0 Benchmark Methodology

## Goal

The v0.7.0 benchmark tests whether Owledge creates safer and cheaper context
packs before model inference. It is not a general intelligence benchmark and it
is not a leaderboard for every model.

## Profiles

Each run compares three profiles:

| Profile | Meaning |
| --- | --- |
| `metadata_scan` | Naive baseline that can over-select relevant-looking but unsafe or stale notes. |
| `owledge_context_pack` | Product behavior under test. |
| `oracle` | Ground-truth reference ceiling from the fixture, not a model claim. |

The public verdict is based on the Owledge profile. Baseline failures are shown
as the before-state contrast.

## Scale Modes

The Benchmark Kit ships three deterministic fixture scales:

| Scale | Files | Purpose |
| --- | ---: | --- |
| `small` | 100 | Release proof, CI smoke, quick local demo. |
| `mid` | 500 | Larger local reproduction run. |
| `large` | 1000 | Team-sized synthetic vault reproduction run. |

The v0.7.0 published model results use `small`. Larger public result matrices
are intentionally left for later releases because local model runs should stay
reproducible and resource-conscious.

## Models Published

The v0.7.0 release-proof comparison includes complete runs for:

- `gemma4:latest`
- `glm-5.1:cloud`

The historical `qwen3.5:4b` report is excluded because it records four timeouts
and `passed: false`; its raw files remain available for audit. Incomplete
reports now fail comparison input validation. `nemotron-nano:cloud` is not
included because no completed release-proof report was available in the
verified artifact set. The comparison tool does not fabricate missing or
incomplete model results.

## Metrics

| Metric | Direction | Why it matters |
| --- | --- | --- |
| Context pollution | Lower is better | Shows how much irrelevant, stale, private, or distracting context entered the pack. |
| Tokens per correct answer | Lower is better | Shows token efficiency when quality holds. |
| Total tokens | Lower is better if quality holds | Shows cost and context-window pressure. |
| Privacy failures | Must be zero | Private notes should not enter selected context. |
| Stale failures | Must be zero | Outdated notes should not override current records. |
| Scenario pass rate | Higher is better | Shows reliability across the fixture scenarios. |
| Handoff resume score | Higher is better | Shows whether compact handoff context is enough to resume. |
| tokens/sec | Higher is better | Shows runtime/model throughput; it is hardware and provider dependent. |

Quality and retrieval metrics are gated independently from token efficiency.
The frozen baseline requires at least 0.95 average answer correctness, 0.90
precision@k, 1.0 recall@k, 1.0 citation accuracy, no privacy or staleness
failures, at most 0.10 average context pollution, and at least 80% average
tokens-per-correct-answer reduction across complete reference reports.

`baseline-contract-v1.json` binds the fixture and source reports by SHA-256.
`held-out-journeys-v1.json` seals the exact threshold and adversarial boundary
cases. Any fixture, threshold, reference-report, or held-out change requires a
new baseline version and an explicit Owledge decision.

## Reproduction

Install the optional Benchmark Kit into a project and run:

```bash
python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode small --fixture-source bundled --yes
python tools/benchmark-kit/render-benchmark-report.py --format html
```

For local Ollama models, run one model at a time:

```bash
python tools/benchmark-kit/run-benchmark-kit.py --mode local --scale-mode small --fixture-source bundled --models gemma4:latest --yes
python tools/benchmark-kit/render-benchmark-report.py --format html
```

Sequential local runs are intentional. Running models in parallel can distort
GPU, VRAM, token/sec, and duration measurements.

## Limitations

These results come from a synthetic Markdown vault. They prove the benchmarked
behavior on a controlled fixture, not a guaranteed savings percentage for every
project. Real-world savings vary by vault shape, writing quality, model
behavior, context window, and selected retrieval strategy.
