# OW-080-13 — Persisted Codex Resume Transcript Excerpt

This sanitised excerpt replaces three temporary raw response files. It records
the actual persisted-session transition without overstating it as an interactive
slash-command transcript.

```text
Setup: Codex CLI 0.147.0 created non-ephemeral session
019ffb21-8fe6-7762-bd6e-2a8612ff184f using gpt-5.5, workspace-write,
and model_auto_compact_token_limit=100000. Setup witness: exit 0.

Resume: `codex exec resume 019ffb21-8fe6-7762-bd6e-2a8612ff184f` completed
with exit 0. The CLI defaulted this intermediate continuation to gpt-5.6-sol.

Final Resume: `codex exec resume -m gpt-5.5
019ffb21-8fe6-7762-bd6e-2a8612ff184f` completed with exit 0.
The final result was passed true: auto-compact 100000 enabled; persisted
86 < 14240 < 18932; reset 112 < 14266 < 18958; digest diff exit 0;
stale handoff rejected; sidecar roundtrip true; alignment selection false.
```

The persisted `exec resume` evidence is stronger than the earlier ephemeral
run, but it is deliberately not called a literal interactive `/goal` transcript.
