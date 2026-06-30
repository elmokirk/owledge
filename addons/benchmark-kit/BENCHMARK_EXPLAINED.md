# Owledge Benchmark Kit Explained

The Owledge Benchmark Kit uses synthetic Markdown projects instead of external
datasets because Owledge is not a generic question answering system. It is a
git-native memory and handoff layer for agentic project work. The benchmark
therefore creates realistic project notes with Owledge-style frontmatter,
links, decisions, reviews, handoffs, and research records.

## Injected Problems

The benchmark deliberately inserts failure modes that real agent projects run
into:

| Problem | How it is injected | What should happen |
| --- | --- | --- |
| `distractor` | Plausible files use similar wording but point to the wrong decision, plan, or handoff. | Retrieval should keep them out of the final context pack. |
| `stale` | Older records contradict newer reviewed records. | The benchmark should prefer the newer reviewed record and count stale leakage. |
| `private` | Private or unsafe notes include tempting but non-shareable details. | Private context should be excluded from shared context and counted as a failure if selected. |
| `multi-hop` | The answer requires two or three linked Markdown files. | Retrieval should include the linked evidence chain, not only the first match. |
| `handoff` | A compact handoff refers to a plan, decision, and next action. | The selected context should let a new agent resume correctly. |
| `needle` | One decisive fact is hidden in a larger fixture vault. | Retrieval should find the relevant file without pulling broad unrelated context. |

## Metrics

Power users usually care about practical cost and reliability first:

- `total_tokens`: total prompt plus completion tokens used by the run.
- `context_pack_tokens`: tokens selected for the model context.
- `irrelevant_token_ratio`: share of selected context that came from
  distractor, stale, private, generated, or unrelated records.
- `tokens_per_correct_answer`: total tokens divided by successful scenario
  answers.
- `tokens_per_second`: local model throughput when an Ollama model is used.
- `privacy_failure_count`: private records selected into context.
- `staleness_failure_count`: stale records selected into context.
- `handoff_resume_score`: whether the handoff scenario includes the files a
  follow-up agent needs.

Research-style metrics are still included for users who need them:

- `precision_at_k`
- `recall_at_k`
- `citation_accuracy`
- `multi_hop_success`
- `answer_correctness`

## What This Benchmark Can Prove

It can show whether Owledge-style retrieval and context packing reduce token
waste, avoid context pollution, and produce usable handoff context on a
controlled Markdown project.

## What This Benchmark Cannot Prove

It does not prove performance on every real repository, every local model, or
every enterprise knowledge base. External datasets, own-vault benchmarking,
cloud/frontier matrices, and 10k-file stress tests are roadmap items.
