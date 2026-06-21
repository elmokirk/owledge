# TS Adapter Kit

This optional add-on lets Node/TypeScript projects validate the Owledge
Markdown contract in CI without replacing the Python CLI or creating a second
memory engine.

## What It Does

- scans Markdown files under `agent-memory/`
- validates required frontmatter fields
- checks shared records for approved review and sanitization states
- can run against the retrieval fixture corpus

## What It Does Not Do

- no hosted service
- no vector database
- no runtime capture
- no promotion decisions
- no rewrite of Markdown memory

## Run From Source Checkout

```bash
node addons/ts-adapter-kit/bin/owledge-lint.mjs --root tests/fixtures/retrieval-corpus
```

## Run After Installing The Add-On

```bash
python tools/owledge.py install-addon --project-root . --addon ts-adapter-kit
node tools/ts-adapter/bin/owledge-lint.mjs --root .
```

Use this in Node/TypeScript CI when the project wants fast validation of the
same Markdown contract used by the Owledge Python tools.
