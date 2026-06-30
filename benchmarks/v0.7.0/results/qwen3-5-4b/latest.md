# Owledge Benchmark Kit Report

## Run Summary

- Passed: `false`
- Mode: `local`
- Scale mode: `small`
- File count: `100`
- Model(s): `qwen3.5:4b`
- Profiles tested: `metadata_scan, owledge_context_pack, oracle`
- Total tokens: `40768`
- Context pollution: `0.2737`
- Duration ms: `565653`
- Tokens/sec: `37.3757`
- Privacy failures: `1`
- Stale failures: `1`
- Fixture directory: `.owledge/tmp/benchmark-kit/fixtures/20260629094411-seed42-small/small`
- Explanation: `.owledge/benchmark-kit/BENCHMARK_EXPLAINED.md`

## Before vs Owledge

| Metric | Baseline metadata_scan | Owledge context pack | Oracle reference |
| --- | ---: | ---: | ---: |
| Context pollution | 0.7356 | 0.0856 | 0.0 |
| Privacy failures | 1 | 0 | 0 |
| Stale failures | 1 | 0 | 0 |
| Tokens per correct answer | 8964.0 | 2002.17 | 1804.5 |
| Verdict | fail | pass | pass |

Baseline failures are expected contrast when the naive profile over-selects noisy, stale, or private context. The Owledge verdict is the product proof.

## Privacy Trap Explained

The benchmark injects private Markdown notes that look relevant to the question. A reliable context pack must exclude those notes, even when their wording appears useful.

## What This Means

- Total tokens show how much context and completion budget the run consumed.
- Tokens per correct answer is the practical cost of useful retrieval.
- Context pollution measures irrelevant, stale, private, or background context inside selected packs; lower is better.
- Privacy failures must stay at zero for shareable or team-safe usage.
- Stale failures show whether outdated records entered the answer context.
- tokens/sec and duration reflect local runtime performance and vary by hardware.

## Scenario Results

| Status | Scenario | Profile | Model | Precision | Recall | Pollution | Tokens | Duration ms |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| warn | needle | metadata_scan | qwen3.5:4b | 0.2 | 1.0 | 0.805 | 3211 | 44990 |
| pass | needle | owledge_context_pack | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 1166 | 19660 |
| pass | needle | oracle | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 1166 | 19474 |
| warn | multi-hop | metadata_scan | qwen3.5:4b | 0.5 | 1.0 | 0.5056 | 1835 | 1 |
| pass | multi-hop | owledge_context_pack | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 4911 | 103366 |
| pass | multi-hop | oracle | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 4911 | 103032 |
| warn | stale-conflict | metadata_scan | qwen3.5:4b | 0.2 | 1.0 | 0.8036 | 3424 | 39488 |
| pass | stale-conflict | owledge_context_pack | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 1349 | 24420 |
| pass | stale-conflict | oracle | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 1349 | 24168 |
| fail | privacy-trap | metadata_scan | qwen3.5:4b | 0.2 | 1.0 | 0.8065 | 2907 | 26225 |
| pass | privacy-trap | owledge_context_pack | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 1297 | 23281 |
| pass | privacy-trap | oracle | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 1297 | 23078 |
| warn | distractor-heavy | metadata_scan | qwen3.5:4b | 0.1111 | 1.0 | 0.8937 | 4972 | 39491 |
| warn | distractor-heavy | owledge_context_pack | qwen3.5:4b | 0.5 | 1.0 | 0.5137 | 2617 | 48263 |
| pass | distractor-heavy | oracle | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 1431 | 26713 |
| warn | handoff-resume | metadata_scan | qwen3.5:4b | 0.4 | 1.0 | 0.5989 | 1579 | 1 |
| pass | handoff-resume | owledge_context_pack | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 673 | 1 |
| pass | handoff-resume | oracle | qwen3.5:4b | 1.0 | 1.0 | 0.0 | 673 | 1 |

## Caveats

Fixture content is deterministic and synthetic. Local model timings vary by hardware, model quantization, Ollama version, and background load.

## Final Verdict

- Baseline verdict: `fail` - Baseline failed as expected: naive metadata scanning over-selected unsafe, stale, or noisy context.
- Owledge verdict: `pass` - Owledge passed: the context-pack profile kept private and stale records out while staying inside the target pollution band.
- Oracle verdict: `pass` - Oracle is the reference ceiling and should be treated as an ideal comparison point, not a product claim.
- Product verdict: `pass`
- Conclusion: Owledge passed: the baseline profile over-selected unsafe or stale context, while the Owledge context-pack profile kept private and stale records out.
