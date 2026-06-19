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

Use the reproducible local harness under `benchmarks/` before making any public
performance or token-efficiency claims.

Minimum benchmark scenarios:

- KB scan on an existing-style Markdown vault
- context-pack generation for a scoped task
- runtime handoff/resume through durable session artifacts

Track at least:

- wall-clock runtime
- commit SHA, OS, Python version, CPU count, and command
- files scanned
- truncation status
- records per second
- peak Python allocation bytes
- output bytes or record count
- included source count
- tokenizer-based prompt tokens when making public token claims

Example local matrix:

```bash
python tools/owledge.py benchmark --project-root . --scale-files 100,1000,10000
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
