# AGENTS.md / CLAUDE.md Integration Block

Use this when you want Owledge memory discipline inside an existing project
without installing the skills path or running `init-project`. Copy the block
below into your project's `AGENTS.md`, `CLAUDE.md`, or equivalent runtime
instruction file.

## When To Use This Block

- Your project already has an `AGENTS.md` or `CLAUDE.md` and you do not want to
  overwrite it.
- You want Owledge rules but do not need local Python tools or the full
  `.owledge/` folder structure.
- You want the smallest possible integration (principles-only path).

## Copy-Paste Block

Copy everything between the `--- BEGIN OWLEDGE ---` and `--- END OWLEDGE ---`
markers into your runtime instruction file.

```markdown
--- BEGIN OWLEDGE ---

## Owledge Memory Discipline

Treat Markdown as the canonical memory surface. Generated indexes, RAG
exports, and dashboards are disposable views.

### Read Order

1. `USER_CONTEXT.md` when present (private user profile).
2. `OWLEDGE.md` (project router, goals, decisions, next actions).
3. `.owledge/indexes/memory-index.jsonl` when present (metadata-first scan).
4. Relevant `.owledge/compiled/`, `.owledge/canonical/`,
   `.owledge/decisions/`, `.owledge/lessons/`, `.owledge/patterns/`.
5. `.owledge/ideas/` before drafting any new plan or proposing new work.

### MVP-First Planning

Before implementation, draft a plan with:

- **Goal:** smallest useful version for one real user.
- **Non-Goals:** explicit exclusions.
- **MVP Cutline:** in-scope tasks and out-of-scope items.
- **Evidence:** source paths cited for every claim.
- **Success Metrics:** at least one measurable metric with a target and a
  decision rule (met → integrate; not met → defer to roadmap).
- **Acceptance Criteria:** byte-identical source, cited tasks, review status.
- **Completion Signal:** `status: done` + all `qa_gate_ids` passing.

### Idea Capture

When work produces an idea that does not belong in the current scope:

- Capture it in `.owledge/ideas/` with `concept_tags`,
  `problem_patterns`, `architecture_patterns`, `failure_modes`, and
  `similar_to` edges.
- Store source links and hashes, not long transcripts.
- Check `.owledge/ideas/` before drafting new plans to avoid duplicates.

### Permission Mode

The `OWLEDGE.md` may set `planning_mode`:

- `supervised` (default): ask before linking existing ideas or expanding scope.
- `approve-automatically`: link and log without asking.
- `full-access`: promote ideas into tasks without asking.

### Hard Rules

- Do not reorganize existing files, wiki links, or frontmatter unless asked.
- Do not export raw sessions, private notes, or unsanitized records to shared
  RAG.
- Do not promote candidate ideas or PI reports to canonical memory without
  review.
- Do not mark work `done` unless acceptance criteria are met and QA gates pass.
- Build a task-specific context pack instead of pasting long transcripts.
- Preserve contradictions through `contradicts` edges instead of overwriting.

--- END OWLEDGE ---
```

## After Pasting

- Create a `OWLEDGE.md` with at minimum: project name, goal, and
  `project_mode` (PoC, MVP, side, SaaS).
- Create `.owledge/ideas/` and `.owledge/plans/` directories.
- When you want local validation, run
  `python tools/owledge.py init-project --target .` to add the Python tools
  additively (existing files are preserved).

## Verification

After pasting, ask your agent:

```text
Read AGENTS.md and confirm you understand the Owledge memory discipline.
What is the read order? What is the MVP plan structure? What is the completion
signal?
```

The agent should answer: read order (USER_CONTEXT → OWLEDGE → index →
compiled/canonical/decisions → ideas), MVP plan structure (goal, non-goals,
cutline, evidence, success metrics, acceptance criteria, completion signal),
and completion signal (`status: done` + QA gates passing).