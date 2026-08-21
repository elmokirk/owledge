# Contributing

## Focus

Owledge accepts contributions that improve:

- Markdown-first memory workflows
- project planning and handoff quality
- safe integration with existing knowledgebases
- runtime adapters and documentation
- release gates, benchmarks, and public repo quality

## Before Opening A Pull Request

Run:

```bash
python tools/owledge.py test public-docs --project-root .
python tools/owledge.py finalization-gates --project-root internal --include-compliance
```

Before committing a product, documentation, contract, or workflow change, run
the CI-equivalent preflight locally:

```bash
python tools/ci_preflight.py --scope core
```

For release and documentation contracts alone, use
`python tools/ci_preflight.py --scope release-qa`. Before merging contract or
workflow changes, run that scope in each supported Linux interpreter:

```bash
docker run --rm -v "$PWD:/workspace:ro" -w /workspace python:3.10 python tools/ci_preflight.py --scope release-qa
docker run --rm -v "$PWD:/workspace:ro" -w /workspace python:3.11 python tools/ci_preflight.py --scope release-qa
docker run --rm -v "$PWD:/workspace:ro" -w /workspace python:3.12 python tools/ci_preflight.py --scope release-qa
```

## Pull Request Rules

- Product-surface changes must update every documentation file mapped by
  contracts/release-surface.json; CI blocks a PR when the docs-contract finds
  missing updates.
- Run the version-contract and docs-contract against origin/main before
  requesting review for public changes.
- Do not bump VERSION directly on main. Prepare a release/vX.Y.Z branch; the
  release workflow promotes it only after PyPI confirms the package.

- Keep Markdown as the source of truth.
- Do not add global-setup requirements unless they are optional compatibility paths.
- Do not rewrite existing KB notes or wiki links by default.
- Keep public docs concise and GitHub-readable.
- Add or update tests when behavior, contracts, docs integrity, or packaging changes.

## Schema & Template Changes

Any PR touching `templates/` or `schemas/` MUST:

1. Bump `VERSION` (the kit version stamp).
2. Add a `## Upgrade notes` section to `CHANGELOG.md` declaring `breaking: yes|no|additive`.
3. Paste `owledge upgrade --dry-run` output (run against a prior install) into the PR description.
4. Run `python tools/owledge.py finalization-gates --project-root . --include-compliance --include-exports` and confirm green.

The release workflow enforces the `## Upgrade notes` requirement when templates or schemas changed in the tag diff.

## Scope Discipline

This repository is a local/project utility layer. Avoid turning it into a hosted platform, enterprise control plane, or mandatory migration framework without an explicit design decision.

## Dogfooding vs. Product

- `templates/agent-memory/` is the shipped source. Only commit schemas, templates, and `.gitkeep` here.
- `internal/agent-memory/` is the maintainers' live workspace. Generated artifacts (indexes, exports, decision traces, compiled snapshots) go here.
- Never commit generated files to `templates/`.
- Run dogfood gates against `internal/`: `python tools/owledge.py finalization-gates --project-root internal --include-compliance --include-exports`
