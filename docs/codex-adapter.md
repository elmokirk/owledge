# Codex adapter (V1)

Owledge supports Codex through the project-local `AGENTS.md` entrypoint and
the discoverable `.agents/skills/` mirror. The source `skills/` directory is
kept as the vendored bundle; `.owledge/skills/` is not a Codex discovery root.

## Capability boundary

The Codex profile uses the shared `AdapterManifest v1` contract. It can request
local project/user-global context, read control state, create a Core-owned
checkpoint/handoff, and write a project-scoped Candidate when the matching
permission is explicitly supplied. It cannot inspect a plan automatically,
perform durable routing, access Core storage directly, use enterprise scope, or
dispatch an orchestrator.

Codex-native lifecycle hooks are not declared in V1. This is an explicit
`unsupported` result, not a silent skipped capture path. The user or agent must
invoke the local command surface from the initialized project; Owledge does not
invoke a recursive Codex CLI from an active Codex Goal session.

## Verify an initialized project

```bash
python tools/owledge_adapter_contracts.py validate --manifest .owledge/runtime-conformance/codex.json
python tools/owledge_adapter_contracts.py negotiate --manifest .owledge/runtime-conformance/codex.json --capability context.read --scope project_user --permission read_project
python tools/runtime-conformance/run-runtime-conformance.py --project-root .
```

The second command must return a structured `supported` result. An unsupported
hook or capability must return a structured `unsupported` result instead.
