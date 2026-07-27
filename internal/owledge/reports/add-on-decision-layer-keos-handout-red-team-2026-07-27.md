---
memory_id: "mem:owledge:global:owledge:report:add-on-decision-layer-keos-handout-red-team-2026-07-27"
doc_type: "report"
status: "candidate"
visibility: "private"
data_class: "internal"
semantic_title: "KEOS handout red-team review for Owledge hardening"
summary: "Provenance-preserving candidate review of private KEOS-derived Owledge improvement proposals and Hermes integration feedback, mapped to v0.7.1, post-v1 roadmap, or rejection."
created_at: "2026-07-27T00:00:00Z"
updated_at: "2026-07-27T00:00:00Z"
source_hash: "88e081d0e573fd6166ccf60f9d6d6b9fb858c77e06cdb3657b4064f810f18133"
review_status: "candidate"
edges:
  - type: "supports"
    target: "mem:owledge:global:owledge:plan:add-on-decision-layer-discovery"
    confidence: 0.95
    reason: "Records the first private handout as candidate evidence without promoting raw private content."
  - type: "informs"
    target: "mem:owledge:global:owledge:plan:v0.7.1-public-docs-adoption"
    confidence: 0.7
    reason: "Some findings harden v0.7.1 documentation truth, but most implementation work belongs after v0.7.1."
---

# KEOS Handout Red-Team Review

## Intake Card

Primary source handled: private KEOS operations handoff supplied by the owner on
2026-07-27. The body describes 13 Owledge improvement specs derived from KEOS
operation between February and July 2026. It says the target baseline is
Owledge v0.7.0 and that the target changelog was checked on 2026-07-25.

Secondary source handled: a ChatGPT chat artifact about Owledge's potential for
Hermes Agents, supplied by the owner on 2026-07-27. Its source hash is
`e82670089b6cf50ca6893d9f7f7bb8b381db7fbc87d63e221de9e605e5c627e5`. It
contains a reflection, not a validated Hermes fixture transcript.

Privacy boundary: the raw handout is not copied into this repository. This
report stores only a hash, scope summary, red-team conclusions, and roadmap
mapping. Frontmatter and Obsidian wikilinks were ignored per owner instruction.

Unknowns: original author identities, whether the artifacts were model-generated
or human-written, their exact source dates beyond supplied filenames/context,
and whether additional external-agent feedback exists outside the supplied
files.

## Provisional Rubric

Rubric status: approved by the owner on 2026-07-27. Scores and classifications
remain advisory until an explicit owner decision promotes a finding into a
ticket, plan amendment, roadmap item, or rejection.

Criteria:

- User value: does this reduce repeated agent/user pain?
- MVP fit: does this preserve v0.7.1 local first-value scope?
- Technical truth: does it match current architecture and roadmap?
- Evidence quality: is there concrete operational evidence, not only taste?
- Risk: does it expand authority, attack surface, or schema churn?
- Harness portability: does it help Codex, Claude Code, OpenCode, Hermes, and generic agents?
- Token/context efficiency: does it lower recurring context cost or tool confusion?
- Documentation clarity: does it make adoption or maintenance clearer?

## Red-Team Verdict

The handout has real value, but it is not a single implementation package. It
mixes three classes of work:

- v0.7.1 hardening signals: source freshness for public claims, context budget
  discipline, and explicit read-only/write-boundary wording.
- Existing roadmap reinforcements: task contracts, context budgets, write
  policy, promotion lifecycle, locks, evidence append, and approval states.
- Overcut specs: a generic one-tool write MCP, a new concept document type, and
  broad language gates as immediate product work.

The highest-value kernels are not the most dramatic features. The durable
value is in preventing stale evidence, naked IDs, prose-only tasks, silent
context bloat, and unsafe write authority. The write-path ideas are valuable
only after privacy, promotion, locking, idempotency, and project binding exist.

Hermes-specific feedback reinforces the current v0.7.1 strategy: Owledge should
act as a project-local read-only MCP sidecar for scoped context, not as a
replacement for Hermes memory or compression. The claimed token/performance
benefits remain candidate claims until Hermes-specific A/B evidence exists.

## Spec Classification

| Spec | Provisional Decision | Real Value | Main Risk | Mapping |
| --- | --- | --- | --- | --- |
| S1 language/voice gate | Defer/rework | Configurable release lint can catch cheap mechanical defects. | False positives and language-specific scope can distract from v0.7.1 English adoption. | Post-v1 QA hardening, possibly `OW-100-05`/release gates. |
| S2 plaintext IDs | Accept as UX hardening | Reduces lookup friction in CLI/MCP text output. | Touches many outputs; JSON compatibility must stay frozen. | `OW-100-05`; optional docs/report contract in `OW-071-12`. |
| S3 source vs review freshness | Accept for v0.7.1 evidence policy; implement later as schema/scoring | Directly prevents stale external claims from shaping plans. | Overstrict doctor checks can burden local notes that are not external claims. | v0.7.1 amendment to `OW-071-04`/`OW-071-13` claim evidence; implementation in `OW-080-05`, `OW-090-06`, `OW-090-09`. |
| S4 archived terminal state | Accept principle, defer implementation | Avoids irreversible loss of user-authored knowledge. | "Never delete" must distinguish source Markdown from generated indexes/caches. | `OW-090-01`, `OW-090-02`, `OW-100-05`; related to `OW-071-01` archive stale claims. |
| S5 write MCP | Reject exact shape; accept direction later | Server-set frontmatter and typed semantic writes are important. | A single generic `log(...)` is still an arbitrary write primitive and conflicts with current semantic-write roadmap. | Rework under `OW-090-04`; v0.7.1 must remain read-only. |
| S6 audience field | Accept problem; owner chose separated fields | Transferability/audience matters for export and adoption presets. | Exact `audience: universal/partial/local` would collide with existing `audience_ids`, visibility, and data-class semantics. | Docs boundary in `OW-071-14`; schema review in `OW-080-02` with `transferability` separate from `audience_ids`. |
| S7 single-writer matrix | Accept later | Addresses real multi-agent write conflicts. | Premature path writers can create fake safety before claims/leases exist. | `OW-081-06` claims/worktree planner and `OW-090-04` locks/idempotency. |
| S8 task contract | Accept; already aligned | Converts vague tasks into verifiable work. | Heuristic "verb starts DoD" check can be noisy; outcome validation should be structural first. | `OW-080-03` WorkContract/Backlog/RunState. |
| S9 context budget metric | Accept; already aligned | Directly protects agent reasoning space and small-model viability. | Token estimates vary by model; use deterministic estimates plus explicit limitations. | `OW-071-03`, `OW-071-04` information budget, `OW-080-05`, `OW-080-07`, `OW-100-04`. |
| S10 concept document type | Defer/rework | Captures reusable, implementation-independent product principles. | May duplicate existing `concept_tags`, `concept-audit`, typed edges, and research templates. | Schema exploration in `OW-080-02`; do not add to v0.7.1. |
| S11 approval gates | Accept later | Separates strategic human decisions from mechanical permissions. | Blocks can become ceremony unless tied to risk categories and DAG dependencies. | `OW-080-12`, `OW-081-12`, `OW-090-02`. |
| S12 experience append | Accept later, not as generic write | Prevents duplicate living-doc sprawl. | Requires safe append semantics, similarity suggestions, and promotion policy. | `OW-090-04` semantic writes plus `OW-090-02` promotion lifecycle. |
| S13 integration write block | Defer until write MCP exists | A compact integration contract is valuable once writes are supported. | Adding it now would falsely imply v0.7.1 write support. | Keep v0.7.1 `OW-071-12` read-only; add write path after `OW-090-04`. |

## Hermes Feedback Classification

| Claim | Provisional Decision | Real Value | Main Risk | Mapping |
| --- | --- | --- | --- | --- |
| Owledge as Hermes MCP sidecar | Accept for v0.7.1 read-only framing | Matches the current local-first, read-only Hermes profile. | Public docs could overstate integration maturity before fixture proof. | `OW-071-07`, `OW-071-12`. |
| Keep Hermes memory/compression; use Owledge for project artifacts | Accept | Clean division of responsibility; avoids permanent prompt bloat. | Needs careful wording so Owledge is not framed as a Hermes replacement. | `OW-071-11`, `OW-071-12`. |
| Initial Hermes tool allowlist of entrypoint/search/context-pack | Defer as start-mode candidate | Small tool surface lowers tool-choice and token risk. | Current `OW-071-07` acceptance also requires list tasks/reviews; changing that is a scope decision. | Candidate amendment to `OW-071-07`, not applied automatically. |
| Hermes A/B benchmark | Accept later | Gives evidence for prompt tokens, tool calls, quality, and resume time. | Running it before adapter fixture stability can create noisy numbers. | `OW-071-07` smoke evidence, broader benchmark under `OW-100-04`. |
| Current scaling risk for simple text search | Accept as risk | Prevents overclaiming large-vault latency. | Needs measured fixture, not intuition. | `OW-100-01`; limitation wording in v0.7.1 docs. |

Hermes decision: keep the current `OW-071-07` read-only acceptance surface. The
entrypoint/search/context-pack subset may be used as an initial smoke or
starter mode, but it does not replace the full ticket proof that includes
tasks/reviews and verifies no write tools exist.

## v0.7.1 Scope Impact

No supplied spec justifies implementing runtime, hosted, or write-enabled
features before v0.7.1. The local first-value scope should remain intact.

Candidate v0.7.1 amendments only:

- `OW-071-04` / `OW-071-13`: every external current-capability claim should
  carry source date or retrieval date in the evidence record. This is a docs
  truth requirement, not a new runtime feature.
- `OW-071-04`: keep the pre-install information budget explicit; this supports
  S9 without adding new context-pack implementation.
- `OW-071-12`: integration docs should explicitly say current MCP is read-only
  and no agent may assume a write path. This rejects premature S13 while
  preserving the future direction.

Owner approved these narrow amendments on 2026-07-27.

## Owner Decision: Audience And Transferability

Decision date: 2026-07-27.

The owner approved the separated-field model:

```yaml
audience_ids: ["beginner", "maintainer", "agent"]
transferability: universal | partial | local
applies_to: []
visibility: private | shared | public
data_class: internal | confidential | public
```

Meaning:

- `audience_ids` identifies target users, roles, or reviewer lenses.
- `transferability` identifies whether an artifact is reusable outside its
  origin context.
- `applies_to` narrows partial transferability to specific projects, runtimes,
  domains, or scenarios.
- `visibility` and `data_class` remain the privacy and sharing controls.

Reason: this preserves existing `audience_ids` semantics, avoids overloading one
field with privacy/export meaning, and gives future export tooling a mechanical
filter without weakening data-class policy.

Destination: document the distinction in v0.7.1 adoption/preset wording where
needed; implement schema, defaults, migration, and validation in `OW-080-02`.

## Final Bridge

The owner requested the optimal implementation steps be finalized on
2026-07-27. The accepted decision bridge is recorded in
`internal/owledge/decisions/add-on-decision-layer-final-bridge-2026-07-27.md`.
That bridge is the implementation control for feedback-derived hardening.

## Rejected Or Unsafe As Written

- S5 as "exactly one write tool" is too coarse. Owledge's roadmap correctly
  says semantic writes must map to contract transitions and evidence events.
- S10 as an immediate new document type is premature. The current system already
  has concept tags, concept audit history, and typed-edge direction; adding a
  new top-level type needs migration analysis.
- S13 before `OW-090-04` would be a false capability claim.

## Open Questions For Owner

None for this planning bridge. Future tickets may still raise implementation
questions within their scoped gates.
