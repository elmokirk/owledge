# Security Rules

These rules implement the release security posture for Agent Memory principles.

## Zero-Env Default

- Do not require OS environment variables for normal setup.
- Prefer repo-local scripts, explicit CLI arguments, relative paths, and local config files.
- Treat environment variables only as optional compatibility fallbacks.

## Path Safety

- Resolve and normalize every write target before writing.
- Verify every write target stays inside the knowledgebase or module root.
- Reject absolute paths in `agent-memory-map.json`.
- Reject `..` traversal segments.
- Reject symlinks and junctions in mapped write paths.
- Fail closed when a target is ambiguous, missing, or outside scope.

## Secret And Privacy Safety

- Do metadata-only scans by default: path, title, hash, frontmatter keys, and wiki-link names.
- Do not copy raw note bodies into generated indexes by default.
- Do not export private, confidential, personal, or unsanitized records to shared corpora.
- Raw session logs stay private and ignored by default.
- Run sensitive-data scans before release or shared export.

## Tool Safety

- Read repository scripts before running unfamiliar commands.
- Avoid shell string composition with untrusted paths.
- Prefer argument arrays and native path APIs.
- Use write probes only inside approved temp or module directories.

## Review Gates

Shared or central reuse requires:

- explicit source paths or memory IDs
- review status approved or reviewed
- sanitization approved where needed
- safe data class
- no raw logs or private notes
