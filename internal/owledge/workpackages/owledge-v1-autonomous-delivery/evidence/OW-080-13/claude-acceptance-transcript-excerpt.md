# OW-080-13 — Claude Code Complete Acceptance Transcript Excerpt

This sanitised, transcript-visible excerpt is retained in place of the raw
Claude response. It contains only the execution envelope, command result, and
the acceptance values emitted by the worker.

- Harness: Claude Code 2.1.228, Print Safe Mode
- Model: `sonnet`, low effort, maximum budget 1.00 USD
- Permissions: no bypass; only `Bash(python tools/owledge.py resume-acceptance-v1 *)`
- Input baseline: commit `46a247a`, bound by `claude-complete-harness-receipt.yaml`

```text
Exit code: 0
passed: true
persisted: warm 84 < cold 14101 < baseline 18795
reset_baseline: warm 110 < cold 14127 < baseline 18821
golden_digest == reconstructed_digest: true; diff_exit_code: 0
stale_handoff: resume_context.stale_handoff (rejected)
sidecar: capped to 5 failures; complete six-row payload reconstructed; roundtrip_equal: true
owner_alignment_stop: awaiting_user_alignment; selection_allowed: false
```

The command output contains the complete JSON witness at
`claude-acceptance-witness.json`; the raw response is intentionally not retained.
