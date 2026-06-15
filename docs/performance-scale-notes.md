# Performance And Scale Notes

Agent Memory Kit optimizes for local, reviewable Markdown workflows rather than
large opaque databases.

## Current Scale Controls

- Metadata-only scans by default.
- No raw note body copy into KB scan indexes.
- `--max-files` limits scan size.
- `markdown_scan_truncated` reports when the limit is reached.
- Large generated or dependency directories are skipped, including `.git`,
  `.obsidian`, `.agent-control`, `node_modules`, `.venv`, `.next`, `dist`,
  `build`, `coverage`, `target`, and `vendor`.
- Mapped mode excludes generated Agent Memory output folders from source scans.

## Token Efficiency

Agents should use source paths, hashes, titles, frontmatter keys, and wiki-link
metadata first. They should load full note bodies only when needed for the
current task.

This avoids:

- dumping an entire vault into the prompt
- copying raw session logs
- treating generated indexes as canonical memory
- over-fetching unrelated project history

## Release Benchmark Recommendation

Before a major public announcement, run a simple benchmark with 1k and 10k
Markdown files:

- wall-clock runtime
- files scanned
- truncation status
- generated index size
- existing file hash stability
