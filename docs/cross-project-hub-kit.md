# Cross-Project Hub Kit

Optional add-on for linking project-local Owledge memory to a central knowledge
base without making the hub overwrite project truth.

## Purpose

- Record reviewed lessons, patterns, and decisions from external projects.
- Keep external project paths as provenance.
- Build a source project -> shared learning -> reused project map.

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon cross-project-hub-kit
```

## Build Map

```bash
python tools/cross-project-hub/build-cross-project-map.py --project-root .
```

## Guardrails

- No raw session import.
- No automatic promotion.
- No central overwrite of project-local truth.
- Shared records must be reviewed and sanitized before reuse.

