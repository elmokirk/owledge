# Owlib

Owlib is a standalone, Python-first knowledge hub for Owledge-compatible
project memory. Owledge stays project-local; Owlib reads reviewed project
artifacts into a central library so agents can find cross-project parallels,
stale knowledge, recurring failures, central project candidates, and reusable
patterns.

Owlib never rewrites registered projects. It imports metadata and short
excerpts into the library, writes candidate reports, and leaves promotion to a
human or curator workflow.

## Quickstart

```bash
python -m owlib init --library-root /path/to/owl-library
python -m owlib register-project --library-root /path/to/owl-library --path /path/to/project
python -m owlib sync --library-root /path/to/owl-library --reviewed-only
python -m owlib index --library-root /path/to/owl-library
python -m owlib find-parallels --library-root /path/to/owl-library
python -m owlib report --library-root /path/to/owl-library
python -m owlib quality --library-root /path/to/owl-library
```

## Skill-Only Use

Export runtime-specific skill packs without installing plugins:

```bash
python -m owlib skill export --runtime codex --output-dir /path/to/out
python -m owlib skill export --runtime claude --output-dir /path/to/out
python -m owlib skill export --runtime hermes --output-dir /path/to/out
python -m owlib skill export --runtime generic --output-dir /path/to/out
```

Agents can follow these skills even when the CLI is unavailable. When the CLI is
available, the skills call `owlib` commands for deterministic reports.

## On-Demand Modules

Core stays small. Optional modules are installed into the library:

```bash
python -m owlib module install --library-root /path/to/owl-library pi-agent
python -m owlib module status --library-root /path/to/owl-library
```

The `pi-agent` module adds candidate-only roles for library maintenance:
Parallel Scout, Freshness Auditor, Conflict Reviewer, Idea Synthesizer, Quality
Ratchet Monitor, and Owl Librarian.

## Quality

Owlib includes local quality and scale checks:

```bash
python -m owlib doctor --library-root /path/to/owl-library
python -m owlib quality --library-root /path/to/owl-library
python -m owlib benchmark --library-root /path/to/owl-library --record-counts 10,100,1000
```

The quality gate checks the library structure, OS-neutral package surface,
module catalog, skill catalog, growth scan, and PI red-team output.

## Boundaries

- Owlib reads registered Owledge projects read-only.
- Raw sessions and unsafe shared records are not imported.
- Reports, growth suggestions, and PI outputs are candidate knowledge.
- Promotion into project canonical memory is always explicit and external.
