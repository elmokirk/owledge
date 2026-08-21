---
memory_id: "mem:owledge:global:owledge:handoff:skill-authoring-guidance"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "handoff"
artifact_type: "workpackage"
document_version: 1
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge compact skill authoring guidance handoff"
summary: "Canonical handoff for writing and modernizing Owledge skills as compact routers with progressive references, deterministic scripts, decision matrices and behavioral tests."
concept_tags: ["skill-authoring", "agent-guidance", "context-budget", "progressive-disclosure"]
stack_tags: ["markdown", "yaml", "python"]
confidence: 0.97
review_status: "owner_requested"
sanitization_status: "not_required"
created_at: "2026-08-21T18:00:00+02:00"
updated_at: "2026-08-21T18:00:00+02:00"
source_hash: ""
edges:
  - type: "governs"
    target: "mem:owledge:global:owledge:plan:versioned-migration-hybrid"
    confidence: 1.0
    reason: "The migration skill is the first full implementation of this authoring contract."
  - type: "extends"
    target: "mem:owledge:global:owledge:decision:skill-discovery-and-bounded-planning-2026-07-27"
    confidence: 1.0
    reason: "Adds authoring and evaluation rules to the accepted discovery contract."
---

# Compact skill authoring guidance handoff

## Use this handoff when

Create or substantially revise an Owledge skill. Apply it to existing skills
only through a scoped ticket with before-and-after behavior evidence. This file
defines the authoring contract. A skill's domain contract remains in that
skill's own references and scripts.

Future maintainer instructions should point here with one trigger: read this
handoff before creating or substantially revising an Owledge skill. MIG-04 owns
that pointer and its validator coverage. Until MIG-04 lands, this artifact is
the reviewed design contract, not an enforced repository rule.

## Governing idea

Use `router` as the leading word. `SKILL.md` selects a branch. It does not
carry every branch's procedure.

The standard combines these reviewed ideas:

| Source | Adopted mechanism | Owledge use |
| --- | --- | --- |
| Matt Pocock, `writing-for-agents` | context pointers, two loads, leading words, completion criteria, pruning | precise discovery and branch-local reads |
| OpenAI `skill-creator` | progressive disclosure, discriminating description, scripts for deterministic work, forward testing | package structure and validation |
| Ponytail | YAGNI, reuse, standard library, minimum code that works | no speculative references, scripts or dependencies |
| Caveman | terse technical phrasing with clarity exceptions | compact outputs, full wording for safety and irreversible actions |
| Unslop | plain active language, no filler, concrete claims | router and reference prose |
| Impeccable | purposeful hierarchy, progressive disclosure, no repeated UI copy | skill UX, labels, errors and route clarity |

Caveman is a style input, not an upstream dependency. Matt Pocock later
removed it as a duplicate. Owledge keeps the useful compression rule while
retaining normal grammar for safety, approvals and multi-step procedures.

## Required package shape

```text
skills/<skill-name>/
  SKILL.md
  agents/openai.yaml
  references/<branch>.md
  scripts/<deterministic-helper>.*
```

Create only resources used by a real branch. Omit empty directories, README,
changelog, duplicated quick reference and copied external manuals.

## Main router contract

`SKILL.md` must stay at or below 90 lines unless a measured behavioral test
shows the split hides required shared guidance. It contains:

1. frontmatter with exact name and a discriminating one-sentence description;
2. one outcome and one leading word;
3. shared trust, permission and stop boundaries;
4. one decision matrix;
5. the fixed output or completion schema;
6. conditional pointers to references and scripts.

| Agent question | Keep in `SKILL.md` | Move out |
| --- | --- | --- |
| Should this skill run? | trigger and nearest confusing boundary | examples and marketing copy |
| Which branch applies? | decision matrix | branch procedure |
| What can never be skipped? | trust, permission, destructive stop | ordinary domain detail |
| What proves this branch done? | checkable completion criterion | long test instructions |
| What should load now? | one conditional pointer | unrelated references |
| What work must be exact? | script invocation and input contract | script implementation |

### Decision matrix schema

Every router table uses these columns unless a smaller table proves clearer:

| Signal | Mode | Load | Action | Done when | Route |
| --- | --- | --- | --- | --- | --- |
| observable input | one branch name | minimum source set | one bounded action | checkable result | exact reference or script |

Unknown, ambiguous, unauthorised and destructive cases need explicit rows.
Their positive target is a safe stop with the missing decision named.

## Reference contract

- One reference owns one branch or one shared contract.
- The router states when to read it and what decision it changes.
- Keep definitions, rules and caveats together.
- Link onward only when the next file is conditional.
- Keep each meaning in one place. A repeated meaning is drift.
- Leave cheap facts in code, config or `--help`. Document reasons and traps.

## Script contract

Use a script when exact logic, repeated transformation or stable validation
matters. Scripts accept explicit paths and structured inputs, emit structured
results, and fail closed. They do not infer approval, browse for updates,
mutate their own skill, or write outside declared roots.

Prefer an existing project helper, then the standard library, then an installed
dependency. Add a dependency only after a measured blocker and owner approval.
Security checks, error handling and regression tests are outside this economy.

## Writing rules

- Use active voice and one idea per sentence.
- State actions, numbers, paths and stop conditions.
- Remove explanations the agent already knows.
- Use one stable term for one concept.
- Phrase the target behavior positively. Keep prohibitions for hard guards.
- Compress routine output. Expand security, approval and recovery wording.
- Do not repeat the heading in the first sentence.

Run the no-op test on every paragraph. If deleting it changes no decision,
action, boundary or completion check, delete it.

## Invocation decision

| Need | Policy |
| --- | --- |
| Agent must discover it from task wording | model-invoked with precise trigger description |
| Only the owner should start it | explicit-only metadata |
| Several explicit-only skills are hard to remember | add one human-invoked router |
| Two skills share substantial reference | use one canonical external reference, not duplicated bodies |

Sensitive mutation does not require hiding the skill. Keep discovery precise
and require approval immediately before the mutation.

## Test matrix

| Layer | Proof |
| --- | --- |
| Structure | valid frontmatter, name, links, line budget, no placeholders |
| Routing | every signal selects one expected mode and one primary reference |
| Boundaries | unknown, ambiguous, unauthorised and destructive prompts stop safely |
| Determinism | script outputs and receipts are stable for identical inputs |
| Context | branch loads exclude unrelated references and stay within recorded budget |
| Behavior | realistic prompts produce the required action and completion result |
| Portability | source and discovery mirrors match; supported harness fixtures pass |
| Regression | a known bad prompt fails before the fix and passes after it |

Do not accept tests that only match headings or preferred wording. Forward-test
with one constrained-context profile and one frontier profile when the skill is
complex or safety-sensitive. Record model, context limit, prompt, loaded files,
result and limitations.

## Modernizing existing skills

1. Inventory triggers, branches, references, scripts, mirrors and callers.
2. Capture current behavior with realistic fixtures.
3. Mark duplicate meaning, no-op prose, hidden branches and stale facts.
4. Create the router table and choose one leading word.
5. Move branch-only material behind conditional pointers.
6. Replace repeated agent reasoning with deterministic scripts where useful.
7. Run structure, behavior, context and mirror tests.
8. Change one skill per ticket. Preserve compatibility or document the break.

Done means behavior is preserved or intentionally changed, the router is
smaller, each branch loads less irrelevant context, and evidence can reproduce
the result.

## Required handoff from each skill ticket

Return these fields:

```yaml
skill:
leading_word:
invocation_policy:
router_lines:
branches:
max_primary_references_per_branch:
behavior_tests:
context_measurement:
changed_contracts:
known_limits:
next_exact_action:
```

## Source record

Reviewed 2026-08-21. Use upstream as research input, not a runtime dependency.

- https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents
- https://github.com/openai/skills/tree/main/skills/.system/skill-creator
- https://github.com/DietrichGebert/ponytail
- https://github.com/mattpocock/skills
- Local `unslop` and `impeccable` skills installed for this workspace

## Next exact action

Create the migration workpackage control plane and execute `MIG-01`. After the
migration skill passes G-MIG-05-READY, audit existing Owledge skills by context
cost and routing risk. Modernize one skill per ticket. Do not mass-rewrite them.
