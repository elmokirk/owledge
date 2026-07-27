# Session Continuity

This reference defines the per-phase checklist convention that lets a new
agent resume a plan from the exact last-completed step instead of restarting
the whole plan.

## Checklist format

Every multi-phase plan (`docs/*-plan.md` with two or more `## Phase` or
`### Phase` headings) must include, under each phase, a `### Checklist`
section with exactly three checkboxes:

```markdown
### Checklist

- [ ] implementation done
- [ ] QA checks done
- [ ] quick review done
```

Use GitHub-flavored `- [ ]` syntax so renderers display a checkbox and
plain-text agents can still parse `[ ]`.

Each phase must also list its concrete QA gate commands before the checklist.
The checkbox says whether those gates passed; it is not a substitute for
showing the commands.

## Owledge workpackage tasklists

For multi-agent release work, create a separate tasklist workpackage from
`.owledge/templates/phase-tasklist-template.md` under `.owledge/workpackages/`.
The workpackage is orchestrator-owned and should include:

- resume state
- agent rules
- one section per phase
- QA gate commands for the phase
- the three standard checkboxes

In this repository's dogfood workspace, use
`internal/owledge/workpackages/` until dogfood memory is migrated to the
public `.owledge/` shape.

## Resume rule

When a session breaks and a new agent picks up the plan:

1. Read the plan top-to-bottom.
2. Find the **first unchecked box**.
3. Continue from there. Never restart a completed phase.

If a box is checked but the work is incomplete (stale checkbox):

1. Re-run that phase's QA gate.
2. If the gate fails, uncheck the box and redo the phase from the beginning.
3. If the gate passes, the checkbox is valid; continue.

The QA gate is the source of truth, not the checkbox. The checkbox is a
navigation aid.

## Subagent progress reporting

Subagents check their own boxes before returning to the orchestrator. Each
subagent works a disjoint phase (the planning layer already mandates disjoint
task lanes). The orchestrator checks cross-phase boxes after synthesizing
subagent results.

## Audit trail

The checkbox is **not** an audit record. The phase's QA gate output (committed
to `internal/owledge/exports/` or the project's equivalent) is the durable
evidence. The checkbox points at the evidence; it does not replace it.

## When to use this convention

- **Mandatory** for plans with two or more `## Phase` headings.
- **Optional** for single-phase plans (a single phase rarely breaks mid-step).
- The `test_planning_conventions.py` gate enforces the convention on
  multi-phase plans only.

## Worked example

```markdown
## Phase 2 - P1 doc/config fixes

### Files
- `CHANGELOG.md` - add bullets for Phase 5 and E6.
- `docs/command-reference.md` - add concept-audit rows.

### Acceptance
`public-docs` gate green; CHANGELOG mentions Phase 5.

### Gates
python tools/owledge.py test public-docs --project-root .

### Checklist
- [x] implementation done
- [x] QA checks done
- [ ] quick review done
```

A resuming agent reads this, sees `quick review done` is unchecked, and
performs the quick review of Phase 2 — without re-running Phase 1.
