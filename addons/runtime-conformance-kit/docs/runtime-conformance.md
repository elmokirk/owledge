# Runtime Conformance

Runtime Conformance Kit makes local adapter support auditable. It does not claim
marketplace certification. It checks that each runtime profile has fixture
events, expected artifacts, and declared failure modes.

## Runtimes

| Runtime | Status |
| --- | --- |
| Codex | Local adapter support |
| Claude Code | Local adapter support |
| Cowork-compatible | Local adapter support |

## Run

```bash
python tools/runtime-conformance/run-runtime-conformance.py --project-root .
```

The runner is read-only and does not write memory records.

