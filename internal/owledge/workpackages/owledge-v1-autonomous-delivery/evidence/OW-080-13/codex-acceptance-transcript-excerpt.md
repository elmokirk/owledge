# OW-080-13 — Codex Complete Acceptance Transcript Excerpt

This sanitised, transcript-visible excerpt is retained in place of the raw
Codex response. It contains only the execution envelope, command result, and
the acceptance values emitted by the worker.

- Harness: OpenAI Codex CLI 0.147.0, goal-resume-equivalent `exec` session
- Model: `gpt-5.5`
- Invocation: `-c model_auto_compact_token_limit=100000 --approve-for-me --ephemeral`
- Observed sandbox: workspace-write; no bypass
- Input baseline: commit `46a247a`, bound by `codex-complete-harness-receipt.yaml`

```text
Exit code: 0
passed: true
model_auto_compact_token_limit: 100000 (enabled)
persisted: warm 84 < cold 14101 < baseline 18795
reset_baseline: warm 110 < cold 14127 < baseline 18821
golden_digest == reconstructed_digest: true; diff_exit_code: 0
stale_handoff: resume_context.stale_handoff (rejected)
sidecar: capped to 5 failures; complete six-row payload reconstructed; roundtrip_equal: true
owner_alignment_stop: awaiting_user_alignment; selection_allowed: false
```

The command output contains the complete JSON witness at
`codex-acceptance-witness.json`; the raw response is intentionally not retained.
