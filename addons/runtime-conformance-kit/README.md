# Runtime Conformance Kit

Runtime Conformance Kit is an optional add-on for checking that runtime adapter
claims are backed by fixture contracts. It starts with Codex, Claude Code, and
Cowork-compatible runtimes.

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon runtime-conformance-kit
```

## Run

```bash
python tools/runtime-conformance/run-runtime-conformance.py --project-root .
```

The runner is read-only. It verifies that contracts and fixture references are
present and that expected artifact paths are declared.

