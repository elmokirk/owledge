# Distribution And Release Path

Owledge should be easy to try without making the core larger. Distribution is a
wrapper around the existing local Python CLI and Markdown-first contract.

## Supported Install Shapes

| Shape | Status | Purpose |
| --- | --- | --- |
| Source checkout | Supported | Development and local kit publishing. |
| `pipx install owledge` | Packaging-ready | Preferred public CLI path after publishing to PyPI. |
| GitHub release ZIP | Recommended | Offline-friendly release artifact with checksums. |
| Runtime plugin folders | Supported locally | Claude/Cowork/Codex-compatible adapter files. |

## Console Script

The package metadata exposes:

```bash
owledge --help
```

This delegates to `tools/owledge.py`. It does not introduce another memory
engine, database, daemon, or hosted service.

## Release Checklist

- Publish from a clean tag matching `VERSION`.
- Run `python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports`.
- Run `python tools/owledge.py test launch-readiness --project-root .`.
- Build source and wheel distributions.
- Attach release ZIP and checksum files.
- Link CI workflow runs from the release notes.
- Keep raw sessions, generated local reports, temp outputs, and private memory out of release artifacts.

## README Positioning

The first screen should lead with:

1. What problem Owledge solves.
2. Install or try path.
3. The 5-minute demo.
4. Trust boundaries.
5. Extension model.

The source-checkout path remains valid, but it should not be the only public
onboarding route once packages are published.

## Release Artifact Policy

Release artifacts may include:

- Core Python CLI files.
- Templates, schemas, docs, skills, and plugin adapter files.
- Optional add-ons under `addons/`.
- Example vaults and demo fixtures.

Release artifacts must not include:

- Raw runtime event logs.
- Local secrets.
- Customer data.
- Private user memory.
- Generated temp output under `.agent-control/tmp`.
- The `internal/` dogfood workspace.

## Dogfooding vs. Product

This repository contains two distinct memory trees:

| Directory | Purpose | Shipped to users? |
|-----------|---------|-------------------|
| `templates/agent-memory/` | Pristine product source: schemas, templates, structural `.gitkeep` | Yes — via `init-project`, `build-project-kit`, and sdist |
| `internal/agent-memory/` | Maintainers' live dogfood: decision traces, compiled snapshots, generated indexes, red-team reports, benchmarks | No — excluded from sdist and release ZIPs |

A CI `kit-integrity` gate verifies that built kits contain zero files from the dogfood tree. A `sdist-clean` gate verifies the PyPI source distribution contains no `internal/` paths. A `source-vs-target-audit` gate verifies `templates/agent-memory/` has all core directories and no leaked dogfood.

