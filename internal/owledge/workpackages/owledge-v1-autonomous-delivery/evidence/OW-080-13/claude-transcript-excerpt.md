# OW-080-13 — Claude Code Harness Transcript Excerpt

This sanitised, transcript-visible excerpt is retained in place of the temporary raw transcript, which the product owner explicitly authorised us to remove. It contains no credentials, paths outside the project, or free-form model reasoning.

## Execution envelope

- Harness: Claude Code 2.1.228, Print Safe Mode
- Model: `sonnet`, low effort, maximum budget 1.00 USD
- Permissions: no bypass; the only Bash prefixes allowed were `python tools/owledge.py resume-context-v1 *`, `python tools/owledge.py gate-sidecar-v1 *`, and `python -m unittest tests.unit.test_ow08013_resume_context`.
- Input baseline: commit `d94bbf1`; hashes are recorded in `claude-harness-receipt.yaml`.

## Observed terminal output

```text
All three exit code 0.

1. `resume-context-v1` → EXIT:0, `"passed": true`
2. `gate-sidecar-v1` → EXIT:0, top-level `"passed": true`, but inner `summary.passed: false` (6/6 fixtures failed)
3. `test_ow08013_resume_context` → EXIT:0, `OK` (6 tests passed)
CLAUDE_EXIT=0
```

The inner fixture failures are intentional: this command proves that a capped summary is emitted while the complete sidecar roundtrip remains exact.
