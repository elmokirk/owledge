# Owledge Benchmark Kit Report

## Run Summary

- Passed: `true`
- Mode: `local`
- Scale mode: `small`
- File count: `100`
- Model(s): `gemma4:latest`
- Profiles tested: `metadata_scan, owledge_context_pack, oracle`
- Total tokens: `32362`
- Context pollution: `0.2737`
- Duration ms: `131459`
- Tokens/sec: `74.2364`
- Privacy failures: `1`
- Stale failures: `1`
- Fixture directory: `.owledge/tmp/benchmark-kit/fixtures/20260629094140-seed42-small/small`
- Explanation: `.owledge/benchmark-kit/BENCHMARK_EXPLAINED.md`

## Before vs Owledge

| Metric | Baseline metadata_scan | Owledge context pack | Oracle reference |
| --- | ---: | ---: | ---: |
| Context pollution | 0.7356 | 0.0856 | 0.0 |
| Privacy failures | 1 | 0 | 0 |
| Stale failures | 1 | 0 | 0 |
| Tokens per correct answer | 9269.5 | 1190.67 | 1113.17 |
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
| warn | needle | metadata_scan | gemma4:latest | 0.2 | 1.0 | 0.805 | 2741 | 9689 |
| pass | needle | owledge_context_pack | gemma4:latest | 1.0 | 1.0 | 0.0 | 796 | 4935 |
| pass | needle | oracle | gemma4:latest | 1.0 | 1.0 | 0.0 | 796 | 4867 |
| warn | multi-hop | metadata_scan | gemma4:latest | 0.5 | 1.0 | 0.5056 | 3245 | 10655 |
| pass | multi-hop | owledge_context_pack | gemma4:latest | 1.0 | 1.0 | 0.0 | 2011 | 10283 |
| pass | multi-hop | oracle | gemma4:latest | 1.0 | 1.0 | 0.0 | 2011 | 10270 |
| warn | stale-conflict | metadata_scan | gemma4:latest | 0.2 | 1.0 | 0.8036 | 2824 | 9944 |
| pass | stale-conflict | owledge_context_pack | gemma4:latest | 1.0 | 1.0 | 0.0 | 763 | 4348 |
| pass | stale-conflict | oracle | gemma4:latest | 1.0 | 1.0 | 0.0 | 763 | 4359 |
| fail | privacy-trap | metadata_scan | gemma4:latest | 0.2 | 1.0 | 0.8065 | 2618 | 7816 |
| pass | privacy-trap | owledge_context_pack | gemma4:latest | 1.0 | 1.0 | 0.0 | 873 | 5989 |
| pass | privacy-trap | oracle | gemma4:latest | 1.0 | 1.0 | 0.0 | 873 | 5946 |
| warn | distractor-heavy | metadata_scan | gemma4:latest | 0.1111 | 1.0 | 0.8937 | 4202 | 5827 |
| warn | distractor-heavy | owledge_context_pack | gemma4:latest | 0.5 | 1.0 | 0.5137 | 1235 | 5228 |
| pass | distractor-heavy | oracle | gemma4:latest | 1.0 | 1.0 | 0.0 | 770 | 4553 |
| warn | handoff-resume | metadata_scan | gemma4:latest | 0.4 | 1.0 | 0.5989 | 2909 | 10894 |
| pass | handoff-resume | owledge_context_pack | gemma4:latest | 1.0 | 1.0 | 0.0 | 1466 | 7950 |
| pass | handoff-resume | oracle | gemma4:latest | 1.0 | 1.0 | 0.0 | 1466 | 7906 |

## Caveats

Fixture content is deterministic and synthetic. Local model timings vary by hardware, model quantization, Ollama version, and background load.

## Final Verdict

- Baseline verdict: `fail` - Baseline failed as expected: naive metadata scanning over-selected unsafe, stale, or noisy context.
- Owledge verdict: `pass` - Owledge passed: the context-pack profile kept private and stale records out while staying inside the target pollution band.
- Oracle verdict: `pass` - Oracle is the reference ceiling and should be treated as an ideal comparison point, not a product claim.
- Product verdict: `pass`
- Conclusion: Owledge passed: the baseline profile over-selected unsafe or stale context, while the Owledge context-pack profile kept private and stale records out.
