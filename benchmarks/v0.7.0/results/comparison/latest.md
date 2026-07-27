# Owledge Benchmark Comparison Report

## Executive Verdict

- Release proof status: `pass`
- Owledge compared 2 completed benchmark runs: 2/2 Owledge profiles passed, privacy failures prevented=2, stale failures prevented=2, average pollution reduction=88.36%, average tokens/correct reduction=86.47%.

## Creator Pull Quote

> Owledge makes the context safer and cheaper before the model sees it.

## Model Matrix

| Model | Baseline | Owledge | Pollution reduction | Privacy prevented | Stale prevented | Token reduction | Pass rate | tokens/sec |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| gemma4:latest | fail | pass | 88.36% | 1 | 1 | 87.15% | 0.8333 | 74.5858 |
| glm-5.1:cloud | fail | pass | 88.36% | 1 | 1 | 85.8% | 0.8333 | 89.4848 |

## Before vs Owledge

Lower privacy failures, stale failures, context pollution, and tokens per correct answer are better. Higher scenario pass rate, handoff score, and tokens/sec are better.

## Estimated API Cost Impact

Illustrative API prices per 1M tokens. Verify current provider pricing before using these numbers for budgets. Sources checked: Anthropic Claude pricing (docs.anthropic.com/en/docs/about-claude/pricing), Google Gemini API pricing (ai.google.dev/gemini-api/docs/pricing), and OpenAI API pricing (platform.openai.com/docs/pricing).

| Provider | Model | Input $/1M | Output $/1M | Baseline cost | Owledge cost | Estimated savings | Savings |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Anthropic | Claude Opus 4.8 | 5.0 | 25.0 | $0.301505 | $0.17602 | $0.125485 | 41.62% |
| Anthropic | Claude Sonnet 4.6 | 3.0 | 15.0 | $0.180903 | $0.105612 | $0.075291 | 41.62% |
| Anthropic | Claude Haiku 4.5 | 1.0 | 5.0 | $0.060301 | $0.035204 | $0.025097 | 41.62% |
| Google | Gemini 3 Pro | 2.0 | 12.0 | $0.133998 | $0.08125 | $0.052748 | 39.36% |
| Google | Gemini 2.5 Pro | 1.25 | 10.0 | $0.100494 | $0.064334 | $0.03616 | 35.98% |
| Google | Gemini 2.5 Flash | 0.3 | 2.5 | $0.024788 | $0.015982 | $0.008806 | 35.53% |
| OpenAI | gpt-5.5 | 5.0 | 30.0 | $0.334995 | $0.203125 | $0.13187 | 39.36% |
| OpenAI | gpt-5.5-pro | 30.0 | 180.0 | $2.00997 | $1.21875 | $0.79122 | 39.36% |
| OpenAI | gpt-5.4 | 2.5 | 15.0 | $0.167498 | $0.101562 | $0.065936 | 39.37% |

## Scenario Heatmap

| Model | Scenario | Baseline | Owledge |
| --- | --- | --- | --- |
| gemma4:latest | needle | warn | pass |
| gemma4:latest | multi-hop | warn | pass |
| gemma4:latest | stale-conflict | warn | pass |
| gemma4:latest | privacy-trap | fail | pass |
| gemma4:latest | distractor-heavy | warn | warn |
| gemma4:latest | handoff-resume | warn | pass |
| glm-5.1:cloud | needle | warn | pass |
| glm-5.1:cloud | multi-hop | warn | pass |
| glm-5.1:cloud | stale-conflict | warn | pass |
| glm-5.1:cloud | privacy-trap | fail | pass |
| glm-5.1:cloud | distractor-heavy | warn | warn |
| glm-5.1:cloud | handoff-resume | warn | pass |

## How To Read This Report

- Baseline shows what happens when retrieval over-selects noisy, stale, or private context.
- Owledge shows the product behavior under test: cleaner selected context before model inference.
- Token reduction estimates cost pressure avoided by cleaner context, not total project ROI.
- tokens/sec is runtime throughput for the tested model and environment, not an Owledge quality score.
- Oracle is the ground-truth reference ceiling from the fixture generator.

## Caveats

- Inputs are completed Benchmark Kit reports; this command does not run models.
- Oracle is ground-truth reference, not a model or product claim.
- API prices are illustrative snapshots and must be verified against provider pricing before budgeting.
- Small scale is release proof for v0.7.0; larger scales and own-vault benchmarking are roadmap items.
