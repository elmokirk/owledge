# Minimal Owledge Artifact Contract

Use these compact structures when the host project has no stronger convention.
They are source artifacts, not generated reports. Keep frontmatter searchable,
stable, and small; put detail in Markdown sections.

## Location and IDs

1. Reuse the host project's plan, checklist, ticket, and roadmap locations.
2. Otherwise use `docs/owledge/plans/`, `docs/owledge/checklists/`,
   `docs/owledge/tickets/`, and `docs/owledge/roadmap.md`.
3. Use one lowercase-hyphenated slug across artifacts, for example
   `docs-adoption-v071`.
4. Link the plan and checklist in both directions.

## Plan

```markdown
---
id: "plan:docs-adoption-v071"
type: "plan"
status: "active" # draft | active | blocked | complete
title: "Short outcome-oriented title"
summary: "One sentence: user value and boundary."
scope: "MVP scope only"
mvp: "Observable proof of value"
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
checklist: "../checklists/docs-adoption-v071.md"
sources: []
---

# Title

## Goal

## MVP cutline

- Must prove:
- Non-goals:
- Roadmap deferrals:

## Phase 1 - Name

### Scope and deliverable

### QA gate

`exact command or manual verification`

### Definition of done

### Checklist

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done

## Recovery

Read the paired checklist; rerun the active phase QA gate; continue at the
first unchecked item. Record a failed gate before repair.
```

Use two or more phases for any task that can break across sessions. A single
phase still needs the QA gate and three checklist items.

## Checklist

```markdown
---
id: "checklist:docs-adoption-v071"
type: "checklist"
status: "active"
plan: "../plans/docs-adoption-v071.md"
updated_at: "YYYY-MM-DD"
---

# Title checklist

## Resume state

Current phase: `Phase 1`; next action: `state exact action`.

## Phase 1

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done
```

## Ticket

Create tickets for independent work, delegated work, or a phase requiring its
own owner/acceptance gate. A plan plus checklist remains mandatory even when
tickets exist.

```markdown
---
id: "ticket:docs-adoption-v071-install"
type: "ticket"
status: "ready" # backlog | ready | active | blocked | done
plan: "../plans/docs-adoption-v071.md"
owner_role: "docs-engineer"
allowed_paths: ["docs/install/"]
---

# Outcome

## Acceptance

## Evidence

## Handoff
```

## Roadmap item

```markdown
### Future: short title

- Why deferred: outside the current MVP cutline.
- Value: expected user or system gain.
- Trigger: condition that makes this ready to plan.
```

## Handoff

```markdown
## Handoff

- Objective:
- Status and active phase:
- Artifacts changed:
- Evidence and QA result:
- Risks or blockers:
- Next action: first unchecked checklist item.
```
