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

## Pull Request Rules

- Keep Markdown as the source of truth.
- Do not add global-setup requirements unless they are optional compatibility paths.
- Do not rewrite existing KB notes or wiki links by default.
- Keep public docs concise and GitHub-readable.
- Add or update tests when behavior, contracts, docs integrity, or packaging changes.

## Scope Discipline

This repository is a local/project utility layer. Avoid turning it into a hosted platform, enterprise control plane, or mandatory migration framework without an explicit design decision.

## Dogfooding vs. Product

- `templates/agent-memory/` is the shipped source. Only commit schemas, templates, and `.gitkeep` here.
- `internal/agent-memory/` is the maintainers' live workspace. Generated artifacts (indexes, exports, decision traces, compiled snapshots) go here.
- Never commit generated files to `templates/`.
- Run dogfood gates against `internal/`: `python tools/owledge.py finalization-gates --project-root internal --include-compliance --include-exports`
