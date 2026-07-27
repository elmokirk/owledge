---
memory_id: "mem:owledge:global:owledge:plan:add-on-decision-layer-discovery"
doc_type: "plan"
status: "ready"
visibility: "private"
data_class: "internal"
semantic_title: "Add-on Decision Layer and Project Hardening discovery"
summary: "Define a safe, evidence-linked feedback-ingestion and multi-model plan-comparison layer without expanding the v0.7.1 local adoption release."
created_at: "2026-07-27T00:00:00Z"
updated_at: "2026-07-27T00:00:00Z"
branch: "codex/owledge-v1-autonomous-roadmap"
review_status: "candidate"
edges:
  - type: "supports"
    target: "mem:owledge:global:owledge:plan:v0.7.1-public-docs-adoption"
    confidence: 0.9
    reason: "External feedback can harden release decisions without becoming a v0.7.1 dependency."
---

# Add-on Decision Layer and Project Hardening Discovery

## Goal

Define the smallest trustworthy Owledge layer for importing external feedback,
independent agent evaluations, and competing plans so a user can compare them,
spar with models, and promote only the owner-approved conclusions into project
plans, tickets, or roadmap.

## MVP cutline

Must prove:

- a private handout or external review can be recorded with source, date,
  author/model, scope, and confidence;
- plans can be compared against an explicit user-approved rubric;
- a facilitator can turn findings into accepted changes, deferred roadmap
  items, or rejected candidates with rationale;
- no transcript, score, or model verdict automatically changes project truth.

Non-goals:

- no hosted evaluation service, background polling, automatic agent dispatch,
  model ranking claim, or cross-team synchronization;
- no requirement that v0.7.1 waits for this discovery track;
- no ingestion of secrets or private raw notes into shared retrieval.

## Phase 1 - Feedback intake and metric contract

### Deliverable

Specify a private feedback card with provenance, scope, claim, evidence,
confidence, recommendation, and data-class fields. Define a compact default
rubric: user value, MVP fit, technical truth, evidence quality, risk, harness
portability, token/context efficiency, and documentation clarity.

### QA gate

One supplied private handout can be classified without exposing its raw private
content in public docs or canonical project truth.

### Checklist

- [ ] intake contract drafted
- [ ] rubric and privacy boundary reviewed
- [ ] quick review complete

## Phase 2 - Independent plan sparring

### Deliverable

Define a repeatable ceremony: independently produce or collect plans; normalize
their scope; score claims against the shared rubric; let models challenge each
other's omissions; present disagreements and evidence to the user.

### QA gate

Two plan candidates can be compared without collapsing their provenance or
mistaking a model score for an owner decision.

### Checklist

- [ ] comparison protocol drafted
- [ ] disagreement and evidence rules tested
- [ ] quick review complete

## Phase 3 - Project Hardening decision bridge

### Deliverable

Define how approved findings map to an existing ticket, a plan amendment, a
roadmap item, or an explicit rejection. Preserve the original plan and show
the decision delta; never overwrite it silently.

### QA gate

Every accepted finding has an owner decision, destination, and rationale; every
deferred finding has a roadmap trigger.

### Checklist

- [ ] decision mapping contract drafted
- [ ] example delta and handoff reviewed
- [ ] quick review complete

## Integration rule

Use the current release plan as the control plane. A finding may change a
v0.7.1 ticket only when it is necessary for the local first-value journey or a
truth/safety gate. Otherwise keep it as a post-v1 roadmap candidate. The user
approves any change to locked product decisions or release scope.

## Recovery

On a resumed session, read the paired checklist, the latest supplied feedback,
and the active phase only. Re-run that phase's QA gate and continue from its
first unchecked item. Record unresolved disagreement rather than forcing a
consensus.

## Resume state

Awaiting a private-system improvement handout and user-approved sparring rubric.
