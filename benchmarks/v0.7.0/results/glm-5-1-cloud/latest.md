# Owledge Benchmark Kit Report

## Run Summary

- Passed: `true`
- Mode: `local`
- Scale mode: `small`
- File count: `100`
- Model(s): `glm-5.1:cloud`
- Profiles tested: `metadata_scan, owledge_context_pack, oracle`
- Total tokens: `26739`
- Context pollution: `0.2737`
- Duration ms: `103863`
- Tokens/sec: `88.7409`
- Privacy failures: `1`
- Stale failures: `1`
- Fixture directory: `.owledge/tmp/benchmark-kit/fixtures/20260629100314-seed42-small/small`
- Explanation: `.owledge/benchmark-kit/BENCHMARK_EXPLAINED.md`

## Before vs Owledge

| Metric | Baseline metadata_scan | Owledge context pack | Oracle reference |
| --- | ---: | ---: | ---: |
| Context pollution | 0.7356 | 0.0856 | 0.0 |
| Privacy failures | 1 | 0 | 0 |
| Stale failures | 1 | 0 | 0 |
| Tokens per correct answer | 7485.0 | 1062.67 | 898.83 |
| Verdict | fail | pass | pass |

Baseline failures are expected contrast when the naive profile over-selects noisy, stale, or private context. The Owledge verdict is the product proof.

## Privacy Trap Explained

The benchmark injects private Markdown notes that look relevant to the question. A reliable context pack must exclude those notes, even when their wording appears useful.

### Privacy Trap Result

- Result: `Prevented`
- Baseline selected private trap files: `1`
- Owledge selected private trap files: `0`
- Baseline selected files: `notes/0011-privacy-trap-target.md, notes/0039-privacy-trap-distractor-a.md, notes/0088-privacy-trap-private-trap.md, notes/0000-background-filler.md, notes/0001-background-filler.md`
- Owledge selected files: `notes/0011-privacy-trap-target.md`

Interpretation: if the baseline includes a private trap file and Owledge does not, Owledge prevented the privacy leak for this scenario.

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
| warn | needle | metadata_scan | glm-5.1:cloud | 0.2 | 1.0 | 0.805 | 2177 | 2821 |
| pass | needle | owledge_context_pack | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 768 | 2670 |
| pass | needle | oracle | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 758 | 2555 |
| warn | multi-hop | metadata_scan | glm-5.1:cloud | 0.5 | 1.0 | 0.5056 | 2369 | 6878 |
| pass | multi-hop | owledge_context_pack | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 1683 | 8688 |
| pass | multi-hop | oracle | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 1329 | 3404 |
| warn | stale-conflict | metadata_scan | glm-5.1:cloud | 0.2 | 1.0 | 0.8036 | 2049 | 5468 |
| pass | stale-conflict | owledge_context_pack | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 816 | 6134 |
| pass | stale-conflict | oracle | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 790 | 5111 |
| fail | privacy-trap | metadata_scan | glm-5.1:cloud | 0.2 | 1.0 | 0.8065 | 2272 | 6896 |
| pass | privacy-trap | owledge_context_pack | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 755 | 3657 |
| pass | privacy-trap | oracle | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 701 | 9383 |
| warn | distractor-heavy | metadata_scan | glm-5.1:cloud | 0.1111 | 1.0 | 0.8937 | 3817 | 5856 |
| warn | distractor-heavy | owledge_context_pack | glm-5.1:cloud | 0.5 | 1.0 | 0.5137 | 1086 | 14929 |
| pass | distractor-heavy | oracle | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 541 | 1736 |
| warn | handoff-resume | metadata_scan | glm-5.1:cloud | 0.4 | 1.0 | 0.5989 | 2286 | 9683 |
| pass | handoff-resume | owledge_context_pack | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 1268 | 3821 |
| pass | handoff-resume | oracle | glm-5.1:cloud | 1.0 | 1.0 | 0.0 | 1274 | 4173 |

## Caveats

Fixture content is deterministic and synthetic. Local model timings vary by hardware, model quantization, Ollama version, and background load.

## Final Verdict

- Baseline verdict: `fail` - Baseline failed as expected: naive metadata scanning over-selected unsafe, stale, or noisy context.
- Owledge verdict: `pass` - Owledge passed: the context-pack profile kept private and stale records out while staying inside the target pollution band.
- Oracle verdict: `pass` - Oracle is the reference ceiling and should be treated as an ideal comparison point, not a product claim.
- Product verdict: `pass`
- Conclusion: Owledge passed: the baseline profile over-selected unsafe or stale context, while the Owledge context-pack profile kept private and stale records out.
