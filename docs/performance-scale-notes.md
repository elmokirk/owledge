# Performance And Scale Notes

Owledge optimizes for local, reviewable Markdown workflows rather than large
opaque databases.

## Current Scale Controls

- Metadata-only scans by default.
- No raw note body copy into KB scan indexes.
- `--max-files` limits scan size.
- `markdown_scan_truncated` reports when the limit is reached.
- Large generated or dependency directories are skipped, including `.git`,
  `.obsidian`, `.agent-control`, `node_modules`, `.venv`, `.next`, `dist`,
  `build`, `coverage`, `target`, and `vendor`.
- Mapped mode excludes generated Owledge output folders from source scans.

## Token Efficiency

Agents should use source paths, hashes, titles, frontmatter keys, and wiki-link
metadata first. They should load full note bodies only when needed for the
current task.

This avoids:

- dumping an entire vault into the prompt
- copying raw session logs
- treating generated indexes as canonical memory
- over-fetching unrelated project history

Treat this as a design rule until a benchmark report includes tokenizer-based
baseline comparisons. Public token-saving claims should compare at least:

- full vault prompt
- metadata-only scan
- generated context pack
- oracle scoped source files

## Release Benchmark Recommendation

Install the optional Benchmark Kit before making public performance or
token-efficiency claims:

```bash
python tools/owledge.py install-addon --project-root . --addon benchmark-kit
python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode small --yes
python tools/benchmark-kit/render-benchmark-report.py --format html
```

Local model testing is opt-in and runs selected models sequentially:

```bash
python tools/benchmark-kit/run-benchmark-kit.py --mode local --scale-mode small --models gemma4:latest --yes
```

Supported scale modes:

| Scale mode | Files | Use |
| --- | ---: | --- |
| `small` | 100 | CI smoke, laptop-safe sanity, release gate proof |
| `mid` | 500 | Solo or power-user project vault simulation |
| `large` | 1000 | Team-sized local benchmark |

Scenario families:

| Scenario | Challenge |
| --- | --- |
| `needle` | One relevant fact is hidden in a large corpus. |
| `multi-hop` | The answer requires two or three linked notes. |
| `stale-conflict` | A newer record must override an older contradictory record. |
| `privacy-trap` | Private or unsafe records must be excluded or refused. |
| `distractor-heavy` | Similar but wrong notes compete with the target. |
| `handoff-resume` | The model must continue from a compact handoff plus selected context. |

Stable metrics are:

- retrieval precision/recall
- context pack tokens
- irrelevant-token ratio
- answer correctness
- citation accuracy
- privacy and staleness failures
- contradiction handling
- handoff resume score
- prompt/eval token counts
- duration and tokens per second
- failure frontier scale

Harness benchmarks for Claude Code, Codex, OpenCode, Cursor, and Zed are
roadmap items. Frontier/cloud benchmark matrices are also roadmap items. The
v0.7.0 pre-release kit focuses on deterministic CI proof and optional local
Ollama validation.

The older reproducible local harness under `benchmarks/` remains useful for
assembly-strategy baselines, but public v0.7 benchmark claims should prefer
the optional Benchmark Kit add-on because it uses real generated Markdown
fixture files.

Example local matrix:

```bash
python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode small --yes
python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode mid --yes
python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode large --yes
```

## Benchmark Gate

Release QA also runs a small benchmark gate against
`benchmarks/results/baseline.json`:

```bash
python tools/owledge.py test quality-ratchet --project-root .
```

The gate is intentionally broad enough for local laptops and CI runners, but it
fails on major regressions in scan count, wall-clock runtime, Python allocation,
output size, context-pack behavior, or runtime handoff generation.
