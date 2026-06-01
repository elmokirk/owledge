# Publishing Checklist

## Repository Status

The current kit is ready to publish as a concept-validated standalone local/project kit after repository metadata is set. It should not be positioned as a regulated Enterprise Server.

Release scope is frozen for v0.5.0. Do not add new product features before the
release commit; limit changes to documentation corrections, packaging hygiene,
and fixes required by release gates.

| Item | Status |
| --- | --- |
| README | Ready |
| License | Ready |
| Security policy | Ready |
| Privacy notice | Ready |
| Quickstart | Ready |
| Project-folder-only quickstart | Ready |
| Agentic memory architecture | Ready |
| Plugin install docs | Ready |
| Command reference | Ready |
| Kit/host doctor modes | Ready |
| Atomic export snapshots | Ready |
| HTML report skill/tool | Ready |
| Claude/Cowork adapter | Ready |
| Codex plugin manifest | Ready |
| Runtime capture smoke tests | Ready |
| Lifecycle and privacy gates | Ready |
| Retrieval fixture calibration | Ready |
| Red-team QA wrapper | Ready |
| macOS/Linux lean setup | Ready |
| Changelog | Ready |
| Version file | Ready |
| Tests ignored | Ready |
| Git remote | Not set in this workspace |
| GitHub release | Manual next step |

## Suggested GitHub Description

Markdown-first Agent Memory Kit for multi-agent coding workflows, RAG, GraphRAG, LightRAG, Claude/Cowork, Codex, and enterprise knowledge hubs.

## Suggested Topics

| Topic |
| --- |
| agent-memory |
| multi-agent |
| markdown |
| rag |
| graphrag |
| lightrag |
| codex |
| claude-code |
| knowledgebase |
| ai-agents |

## Pre-Publish Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\run-finalization-gates.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\run-redteam-qa.ps1 -ProjectRoot .
```

For shared export/report validation, add `-IncludeExports` to the finalization
gate:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\run-finalization-gates.ps1 -ProjectRoot . -IncludeExports
```

For optional Compliance Light add-on validation, add `-IncludeCompliance`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\run-finalization-gates.ps1 -ProjectRoot . -IncludeCompliance
```

The finalization gate includes compile, contracts, doctor, validation, full and
incremental indexes, retention audit, conflict review, sensitive-data scan,
runtime adapter smoke tests, memory evals, retrieval fixture eval, and minimal
project-folder verification. `-IncludeCompliance` validates the add-on through
a separate generated project folder; the default gate stays compliance-add-on
free.

For manual release debugging, the equivalent individual commands are listed in
`docs/command-reference.md`.

## Publish Steps

```powershell
git init
git status --short
git add .agent-control .gitignore AGENTS.md AGENTS.template.md CHANGELOG.md CLAUDE.md CLAUDE.template.md DESIGN.md LICENSE PRIVACY.md PROJECT_CONTEXT.template.md README.md REPORT_DESIGN_SELECTOR.html ROADMAP.md SECURITY.md VERSION agent-memory docs plugins shared skills tools
git status --short
git commit -m "Release Agent Memory Kit v0.5.0"
git branch -M main
git remote add origin <repo-url>
git push -u origin main
```

Do not use `git add .` after running exports or reports. Generated export snapshots, indexes, PI reports, private sessions, local secrets, and test output are ignored or should remain untracked.
