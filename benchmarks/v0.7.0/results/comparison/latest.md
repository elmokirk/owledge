# Owledge Benchmark Comparison Report

## Executive Verdict

- Release proof status: `pass`
- Owledge compared 3 completed benchmark runs: 3/3 Owledge profiles passed, privacy failures prevented=3, stale failures prevented=3, average pollution reduction=88.36%, average tokens/correct reduction=83.54%.

## Creator Pull Quote

> Owledge makes the context safer and cheaper before the model sees it.

## Model Matrix

| Model | Baseline | Owledge | Pollution reduction | Privacy prevented | Stale prevented | Token reduction | Pass rate | tokens/sec |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| gemma4:latest | fail | pass | 88.36% | 1 | 1 | 87.15% | 0.8333 | 74.5858 |
| qwen3.5:4b | fail | pass | 88.36% | 1 | 1 | 77.66% | 0.8333 | 37.6034 |
| glm-5.1:cloud | fail | pass | 88.36% | 1 | 1 | 85.8% | 0.8333 | 89.4848 |

## Before vs Owledge

Lower privacy failures, stale failures, context pollution, and tokens per correct answer are better. Higher scenario pass rate, handoff score, and tokens/sec are better.

## Estimated API Cost Impact

Illustrative API prices per 1M tokens. Verify current provider pricing before using these numbers for budgets. Sources checked: Anthropic Claude pricing (docs.anthropic.com/en/docs/about-claude/pricing), Google Gemini API pricing (ai.google.dev/gemini-api/docs/pricing), and OpenAI API pricing (platform.openai.com/docs/pricing).

| Provider | Model | Input $/1M | Output $/1M | Baseline cost | Owledge cost | Estimated savings | Savings |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Anthropic | Claude Opus 4.8 | 5.0 | 25.0 | $0.489345 | $0.396005 | $0.09334 | 19.07% |
| Anthropic | Claude Sonnet 4.6 | 3.0 | 15.0 | $0.293607 | $0.237603 | $0.056004 | 19.07% |
| Anthropic | Claude Haiku 4.5 | 1.0 | 5.0 | $0.097869 | $0.079201 | $0.018668 | 19.07% |
| Google | Gemini 3 Pro | 2.0 | 12.0 | $0.218954 | $0.185236 | $0.033718 | 15.4% |
| Google | Gemini 2.5 Pro | 1.25 | 10.0 | $0.165866 | $0.149315 | $0.016551 | 9.98% |
| Google | Gemini 2.5 Flash | 0.3 | 2.5 | $0.040969 | $0.037177 | $0.003792 | 9.26% |
| OpenAI | gpt-5.5 | 5.0 | 30.0 | $0.547385 | $0.46309 | $0.084295 | 15.4% |
| OpenAI | gpt-5.5-pro | 30.0 | 180.0 | $3.28431 | $2.77854 | $0.50577 | 15.4% |
| OpenAI | gpt-5.4 | 2.5 | 15.0 | $0.273693 | $0.231545 | $0.042148 | 15.4% |

## Scenario Heatmap

| Model | Scenario | Baseline | Owledge |
| --- | --- | --- | --- |
| gemma4:latest | needle | warn | pass |
| gemma4:latest | multi-hop | warn | pass |
| gemma4:latest | stale-conflict | warn | pass |
| gemma4:latest | privacy-trap | fail | pass |
| gemma4:latest | distractor-heavy | warn | warn |
| gemma4:latest | handoff-resume | warn | pass |
| qwen3.5:4b | needle | warn | pass |
| qwen3.5:4b | multi-hop | warn | pass |
| qwen3.5:4b | stale-conflict | warn | pass |
| qwen3.5:4b | privacy-trap | fail | pass |
| qwen3.5:4b | distractor-heavy | warn | warn |
| qwen3.5:4b | handoff-resume | warn | pass |
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

## Skipped Inputs

- `.owledge\exports\benchmark-kit-nemotron-nano-cloud\latest.json`
