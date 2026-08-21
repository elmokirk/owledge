# Distribution And Release Path

Owledge should be easy to try without making the core larger. Distribution is a
wrapper around the local Python CLI and Markdown-first contract.

## Supported Install Shapes

| Shape | Status | Purpose |
| --- | --- | --- |
| `uvx owledge` | Preferred | One-command agent/harness execution without a persistent install. |
| `uv tool install owledge` | Preferred | Repeated local CLI use after publishing to PyPI. |
| Source checkout | Supported | Development and local kit publishing. |
| `pipx install owledge` | Supported | Alternative persistent CLI path. |
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

- Create release/vX.Y.Z from main; direct version bumps on main are not permitted.
- Keep the release branch version equal to the intended PyPI version and run the docs-contract against origin/main.
- Run the release-contract with require-dist and write dist/release-evidence.json after building artifacts.
- Verify PyPI confirms the uploaded version before fast-forwarding the tested release commit to main and creating vX.Y.Z.
- Treat a PyPI-to-main promotion longer than five minutes as a failed release; reconcile it before another release begins.
- Publish from a clean tag matching `VERSION`.
- Run `python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports`.
- Run `python tools/owledge.py test launch-readiness --project-root .`.
- Run `python tools/owledge.py wikilink-audit --project-root . --check`.
- Install the optional `benchmark-kit` add-on and run `python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode small --yes`.
- Build source and wheel distributions.
- Smoke the wheel with the default minimal `owledge init --target <tmp>` and
  an explicit `owledge init --target <tmp> --profile full` compatibility path.
- Attach release ZIP and checksum files when publishing GitHub artifacts.
- Link CI workflow runs from the release notes.
- Keep raw sessions, generated local reports, temp outputs, and private memory out of release artifacts.

## README Positioning

The first screen should lead with:

1. What problem Owledge solves.
2. `uvx` or `uv tool install` path.
3. The 5-minute demo.
4. Trust boundaries.
5. Extension model and roadmap boundaries.

The source-checkout path remains valid, but public onboarding should be
uv-first.

## Release Artifact Policy

The V1 Minimal Core wheel and sdist include:

- The bounded Core Python CLI modules, templates, schemas, and shipped skills.
- The data needed for local minimal and explicit Full-profile initialization.

They deliberately exclude optional add-ons, plugins, benchmark corpora,
standalone skill bundles, example fixtures, and the `internal/` dogfood
workspace. Those remain source-checkout or post-V1 material.

Release artifacts must never include:

- Raw runtime event logs.
- Local secrets.
- Customer data.
- Private user memory.
- Generated temp output under `.agent-control/tmp`.
- The `internal/` dogfood workspace.

## Dogfooding vs. Product

This repository contains two distinct memory trees:

| Directory | Purpose | Shipped to users? |
| --- | --- | --- |
| `templates/owledge/` | Pristine product source: schemas, templates, structural `.gitkeep` files | Yes, via `quickstart`, `init-project`, `build-project-kit`, wheel, and sdist |
| `internal/owledge/` | Maintainers' live dogfood workspace: plans, sessions, generated indexes, reports, and release evidence | No, excluded from sdist and release ZIPs |

A CI `kit-integrity` gate verifies that built kits contain zero files from the
dogfood tree. A `sdist-clean` gate verifies that the PyPI source distribution
contains no `internal/` paths, no dogfood decision traces, and all required
root release docs plus the V1 Core product trees. A
`source-vs-target-audit` gate verifies `templates/owledge/` has all core
directories and no leaked dogfood.
