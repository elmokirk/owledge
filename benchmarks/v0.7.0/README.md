# Owledge v0.7.0 Benchmark

This folder contains the public v0.7.0 benchmark artifacts for the optional
Owledge Benchmark Kit.

## Executive Result

On the deterministic v0.7.0 small Markdown fixture, Owledge reduced context
pollution by **88.36% on average** and reduced tokens per correct answer by
**83.54% on average** compared with the naive metadata-scan baseline.

All three completed release-proof runs passed the Owledge profile:

| Model | Runtime tier | Baseline verdict | Owledge verdict | Pollution reduction | Tokens/correct reduction |
| --- | --- | --- | --- | ---: | ---: |
| `gemma4:latest` | local | fail | pass | 88.36% | 87.15% |
| `qwen3.5:4b` | local | fail | pass | 88.36% | 77.66% |
| `glm-5.1:cloud` | Ollama cloud | fail | pass | 88.36% | 85.80% |

Read the comparison report first:

- [HTML comparison report](results/comparison/index.html)
- [Markdown comparison report](results/comparison/latest.md)
- [Machine-readable comparison JSON](results/comparison/latest.json)

## What This Proves

The benchmark compares a naive `metadata_scan` baseline against the
`owledge_context_pack` profile and an `oracle` reference. The baseline is
expected to over-select stale, private, or distracting notes. The Owledge
profile is the product behavior under test.

In this release fixture, Owledge:

- kept private trap notes out of selected context across all completed model
  runs;
- kept stale records out of selected context across all completed model runs;
- reduced irrelevant context before the model saw the prompt;
- kept small local models usable on structured project-memory tasks;
- preserved handoff-resume behavior with a compact selected context.

The useful claim is evidence-bounded: Owledge can reduce token waste and
context pollution on structured project-memory tasks. The exact percentage in a
real project depends on vault size, note quality, model, runtime, and retrieval
configuration.

## Why Small Local Models Matter

`gemma4:latest` and `qwen3.5:4b` are intentionally included because they
represent realistic local setups. The result is not that small models become
frontier models. The result is that cleaner context lets small models spend
less of their limited budget on stale, private, or irrelevant text.

## Privacy Trap Result

The privacy trap injects a private note that looks relevant to the question but
must not enter selected context. A baseline failure is intentional and useful:
it shows what happens when retrieval over-selects. The product proof is whether
the Owledge profile prevents that private note from entering the context pack.

In the published v0.7.0 runs, the baseline fails the privacy trap and Owledge
passes it.

## Fixture Boundary

These benchmarks use synthetic English Markdown vaults, not a personal or
enterprise vault. That is deliberate: the fixtures are deterministic, portable,
and safe to publish. They test retrieval traps, token waste, stale conflicts,
private context exclusion, multi-hop planning, distractor pressure, and handoff
resume behavior.

Real projects can do better or worse depending on how consistently teams write
plans, decisions, handoffs, and reviews. Users should run the Benchmark Kit on
their own environment before making cost or performance claims for their own
vaults.

## Files

| Path | Purpose |
| --- | --- |
| `results/comparison/` | Multi-model Baseline vs Owledge proof report. |
| `results/gemma4-latest/` | Single-model local run for `gemma4:latest`. |
| `results/qwen3-5-4b/` | Single-model local run for `qwen3.5:4b`. |
| `results/glm-5-1-cloud/` | Single-model Ollama cloud run for `glm-5.1:cloud`. |
| `fixtures/small/` | 100-file deterministic Markdown fixture used for release proof. |
| `fixtures/mid/` | 500-file deterministic Markdown fixture for user reproduction. |
| `fixtures/large/` | 1000-file deterministic Markdown fixture for user reproduction. |
| `methodology.md` | How the benchmark was run and how to interpret it. |
| `benchmark-explained.md` | Explanation of the injected benchmark traps. |

