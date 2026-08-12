---
title: "Vibecoding Golden Demo"
date: "2026-08-12"
status: "active"
---

# Vibecoding Golden Demo

This is a small, no-key demonstration of the Owledge loop:

```text
feature request -> scoped context -> evidence -> handoff -> fresh resume
```

It proves a bounded local workflow. It does not claim an agent runtime, remote
Hub, automatic promotion, macOS/Linux package verification, or a complete
product backlog.

## Proof 1: 30 seconds, no installation and zero writes

Read [the 30-second proof](../examples/vibecoding-golden-demo/30-second-proof.md).
The visible result is the mapping from a feature request to its evidence and
handoff. The success signal is explicit: the next agent has all three durable
links. Reading this page or the proof performs zero disk writes.

## Proof 2: five minutes, package-only scratch project

Create a disposable folder. No source checkout, add-on, account, or API key is
needed:

```bash
uvx owledge quickstart --target ./owledge-filter-demo
```

`passed: true` is the installation success signal. Then give a coding agent
this bounded request from the new project root:

```text
Create exactly three durable Markdown artifacts for the completed-item filter
example: .owledge/canonical/filter-request.md,
.owledge/evidence/filter-request-check.md, and
.owledge/handoffs/filter-request-resume.md. Use the public templates already
in .owledge/templates/, retain private visibility, use `doc_type: qa` for the
acceptance-check artifact, link evidence and handoff to
the request, and do not modify application source files. The smallest outcome
is: hide completed items in the current view without changing stored data.
Record the three acceptance checks from this prompt: unfinished stays visible,
completed is hidden, and toggling does not mutate stored items.
```

The expected result is the same compact shape as the
[checked seed artifacts](../examples/vibecoding-golden-demo/seed/). They are
reference content, not files installed automatically by the package.

Verify the scratch project:

```bash
owledge doctor --project-root ./owledge-filter-demo --mode host
owledge build-context-pack --project-root ./owledge-filter-demo \
  --task-id filter-request --agent-role worker \
  --objective "Verify the completed-item filter without widening scope"
```

Both commands return JSON. The second output must include the scoped request
and identify selected or excluded sources; it is a read-only context result.
Rerunning `quickstart` against the same target is additive and reports existing
files as skipped, so it does not overwrite the three agent-authored artifacts.

To reset, delete only the disposable `owledge-filter-demo` folder. Nothing was
written outside that target.

## Proof 3: fresh agent resume, without chat

Start a new agent session in the scratch project and give it this prompt:

```text
Do not use chat history. Read OWLEDGE.md, then
.owledge/handoffs/filter-request-resume.md. Use `owledge build-context-pack`
for task `filter-request` before proposing work. Report the scope, the three
recorded checks, and the next safe action. Do not add sync, accounts, deletion,
or remote-runtime work.
```

Success means the agent can name the request, evidence, three checks, scope
boundary, and the safe next action (confirm the checks before creating a
separate request) from project files alone. If an optional runtime is
unavailable, this manual prompt and the installed CLI path still work; no
runtime plugin is required.

## Source-only optional demo

The [Launch Demo Kit](../addons/launch-demo-kit/README.md) remains a separate
source-checkout add-on with synthetic showcase assets. Do not substitute it for
the package-only path above and do not call its prepared files live feature
evidence.
