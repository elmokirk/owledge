# Launch Readiness Rubric

This rubric measures whether Owledge is ready for broad distribution without
turning the core into a large platform. The target for broad launch is **95+**.

## Score Model

| Dimension | Weight | 95+ launch expectation |
| --- | ---: | --- |
| Value Clarity | 20 | A cold user understands the pain and payoff on the first screen. |
| Usability / Onboarding | 20 | A user can run a 5-minute demo and see durable artifacts. |
| Differentiation | 15 | Owledge is clearly distinct from chat history, vector DBs, and agent methods. |
| Trust / Evidence | 15 | Claims are backed by gates, examples, source paths, and privacy boundaries. |
| Distribution / Shareability | 15 | Install, screenshots, demo output, release artifacts, and social preview exist. |
| Execution Completeness | 15 | Core gates pass and optional launch add-ons validate their own promises. |

## Pass/Fail Criteria

Broad launch requires all of the following:

- Score average is at least 95 across the six dimensions.
- No individual reviewer score is below 90.
- `doctor`, `validate-memory --strict`, and finalization gates pass.
- `test launch-readiness` passes.
- The 5-minute demo produces visible evidence, handoff, and index artifacts.
- Runtime conformance fixtures exist for Codex, Claude Code, and Cowork-compatible runtimes.
- PI proof includes a non-empty red-team artifact with a non-zero score and evidence.
- Optional TS and pilot benchmark proof add-ons validate as add-ons, not as core dependencies.
- Public docs state that Owledge is a local kit, not a regulated enterprise server.

## Core Freeze Rule

The launch program must not change:

- Markdown as canonical memory.
- The existing folder contract.
- Promotion, review, data-class, or visibility semantics.
- Default project setup behavior.
- Raw-session privacy defaults.

Launch improvements should land as add-ons, docs, packaging metadata, or
read-only gates. Minimal core edits are allowed only for packaging entrypoints,
linking, and obvious gate correctness bugs.

## Reviewer Checklist

| Question | Pass signal |
| --- | --- |
| Can a creator record the demo without explaining internals first? | The 5-minute path shows before/after and expected outputs. |
| Can a power user adopt it safely? | Daily commands, privacy boundaries, and runtime paths are explicit. |
| Can an architect trust the model? | Source-of-truth boundaries and generated-view boundaries are explicit. |
| Can a team evaluate it? | Threat model, data flow, and limitations are documented. |
| Can PI-agent value be demonstrated? | The proof kit closes a learning loop from signal to promoted pattern. |

## Required Evidence Paths

| Evidence | Path |
| --- | --- |
| 5-minute demo | `docs/try-owledge-in-5-minutes.md` |
| Launch add-ons | `addons/launch-demo-kit/`, `addons/trust-readiness-kit/`, `addons/runtime-conformance-kit/`, `addons/pi-proof-kit/`, `addons/ts-adapter-kit/`, `addons/pilot-benchmark-kit/` |
| Power-user proof add-ons | `addons/enterprise-context-benchmark-kit/`, `addons/decision-trace-kit/`, `addons/cross-project-hub-kit/`, `addons/swarm-coordination-kit/`, `addons/poweruser-positioning-kit/` |
| Distribution path | `docs/distribution.md` |
| Core gates | `agent-memory/exports/finalization-gates/latest.md` |
| Security boundary | `SECURITY.md` |

## Red-Team Re-Review

After implementation, repeat the six-perspective review:

1. Content creator / workflow educator.
2. Senior AI harness architect.
3. Claude Code / Codex power user.
4. PI Agent creator.
5. Strict developer-tools reviewer.
6. Open-source adoption / DevRel / enterprise enablement.

The launch is ready only when the average is 95+ and the weakest perspective is
at least 90.
