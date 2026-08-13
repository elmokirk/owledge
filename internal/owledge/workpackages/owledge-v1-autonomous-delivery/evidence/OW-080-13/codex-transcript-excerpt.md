# OW-080-13 — Codex Runtime Transcript Excerpt (Partial)

This sanitised, transcript-visible excerpt preserves the successful initial
Codex harness run without claiming full ticket acceptance. The temporary raw
last-message transcript is removed after this excerpt is bound to its SHA.

## Execution envelope

- Harness: OpenAI Codex CLI 0.147.0; `codex exec --ephemeral --approve-for-me`
- Model: `gpt-5.5`
- Observed sandbox: workspace-write; no sandbox bypass
- Input baseline: commit `d3019c5`; input hashes are in
  `codex-initial-harness-receipt.yaml`.

## Observed terminal output

```text
COMMAND 1 exit code: 0
resume-context-v1: passed true; warm_resume_drain 86; cold_resume_drain 13831; durable_state_loaded false

COMMAND 2 exit code: 0
gate-sidecar-v1: passed true; roundtrip_equal true; sidecar_bytes 413;
summary total 6, failed 6, passed false

COMMAND 3 exit code: 0
Ran 6 tests in 0.088s
OK
```

This run proves the three listed commands only. It does not prove every
OW-080-13 Verify clause; see `implementation-checkpoint.yaml` and F-080-03.
