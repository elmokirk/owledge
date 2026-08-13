# Runtime Conformance Kit

Runtime Conformance Kit is an optional add-on for checking that runtime adapter
claims are backed by AdapterManifest v1 fixtures. It covers exactly Codex,
Claude Code, and generic MCP/CLI. Hub, Pi, and automatic orchestration are not
V1 adapter capabilities.

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon runtime-conformance-kit
```

## Run

```bash
python tools/runtime-conformance/run-runtime-conformance.py --project-root .
```

The runner is read-only. It verifies that all three manifests make the required
equivalent capability and explicit-degradation declarations.
