# Quickstart

## Goal

Use the Agent Memory Kit inside a project while keeping Markdown as the source of truth.

This is the safe path from a GitHub link to a working host project.

## 1. Clone The Kit

Windows:

```powershell
git clone <repo-url> C:\AgentMemoryKit
```

macOS/Linux:

```bash
git clone <repo-url> ~/AgentMemoryKit
cd ~/AgentMemoryKit
```

Use another directory if preferred.

You can use the kit without a global environment variable by passing the kit path explicitly:

```powershell
$kitRoot = "C:\AgentMemoryKit"
```

Optional convenience for repeated local use:

```powershell
[Environment]::SetEnvironmentVariable("AGENT_MEMORY_KIT_ROOT", "C:\AgentMemoryKit", "User")
$env:AGENT_MEMORY_KIT_ROOT = "C:\AgentMemoryKit"
```

## 2. Bootstrap A Host Project

```powershell
cd C:\path\to\your-project
powershell -NoProfile -ExecutionPolicy Bypass -File "$kitRoot\tools\bootstrap-agent-memory.ps1" -ProjectRoot . -KitRoot $kitRoot
```

This creates missing files without overwriting existing project memory.

If you chose the optional environment variable, this equivalent command also works:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:AGENT_MEMORY_KIT_ROOT\tools\bootstrap-agent-memory.ps1" -ProjectRoot .
```

## 3. Verify The Host Project

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-host-install.ps1 -ProjectRoot .
```

macOS/Linux:

```bash
bash tools/verify-host-install.sh --project-root .
```

Expected result: `doctor` and strict validation pass.

## Minimal Project Folder Only

For a disposable test or a project-local kit without plugins and release assets:

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$kitRoot\tools\build-project-folder-kit.ps1" -OutputPath C:\tmp\agent-memory-project-kit -Verify
```

macOS/Linux:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --verify
```

With Claude/Cowork plugin adapter and Unix hooks:

```bash
python3 tools/build_project_folder_kit.py --output-path /tmp/agent-memory-project-kit --include-plugin-adapter --plugin-hook-profile unix --verify
```

Then use the generated folder directly or copy its contents into a project. See
`docs/project-folder-only-quickstart.md` for the exact contents and exclusions.
Use another disposable output path if `C:\tmp` is not writable.

## Copy Into A Project

| Source | Target |
| --- | --- |
| `PROJECT_CONTEXT.template.md` | `PROJECT_CONTEXT.md` |
| `USER_CONTEXT.template.md` | `USER_CONTEXT.md` |
| `AGENTS.template.md` | `AGENTS.md` |
| `CLAUDE.template.md` | `CLAUDE.md` |
| `agent-memory/` | `agent-memory/` |
| `global-memory/` | optional private user-level memory |
| `tools/` | `tools/` |
| `plugins/agent-memory-cowork/` | optional plugin adapter |
| `skills/` | optional runtime skills |

Do not copy the ignored `tests/` folder into production projects unless you want local demos.

`USER_CONTEXT.md` and `global-memory/**/*.md` are ignored by default in host projects. Keep them local/private unless you intentionally create a private global vault.

## Optional First Generated Views

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build-memory-index.ps1 -ProjectRoot .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\render-memory-report.ps1 -ProjectRoot . -ReportType project-dashboard -Audience private
```

Only run RAG exports when the memory is reviewed enough for retrieval:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-rag-documents.ps1 -ProjectRoot . -CorpusType private
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-lightrag.ps1 -ProjectRoot . -CorpusType private
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-graphrag.ps1 -ProjectRoot . -CorpusType private
```

Open `REPORT_DESIGN_SELECTOR.html` to choose a report style, then keep the selected id in `DESIGN.md`.

## Agent Rules

| Agent Type | Reads | Writes |
| --- | --- | --- |
| Worker | `USER_CONTEXT.md` if present, `PROJECT_CONTEXT.md`, index, compiled/canonical | sessions, evidence, handoffs |
| Planner | user preferences/goals, project context, specs, canonical | tasks, specs, handoffs |
| QA Agent | specs, evidence, outputs | QA reports |
| Memory Curator | sessions, evidence, drafts | canonical, compiled, patterns, lessons |
| Orchestrator | reviewed user and project context | plans, promotions, routing |
| Personal PI Agent | global preferences, goals, ideas, research, patterns | candidate coach reports and stale-knowledge findings |

## Visual Reports

| User Need | Command |
| --- | --- |
| Decision visualisation | `tools\render-memory-report.ps1 -ReportType decision -Audience private` |
| PM/dev handoff | `tools\render-memory-report.ps1 -ReportType handoff -Audience customer` |
| RAG readiness | `tools\render-memory-report.ps1 -ReportType rag-readiness -Audience private` |
| Agent activity | `tools\render-memory-report.ps1 -ReportType agent-activity -Audience private` |
| Stakeholder dashboard | `tools\render-memory-report.ps1 -ReportType project-dashboard -Audience customer` |
| Website/UI decisions | `tools\render-memory-report.ps1 -ReportType website-ui -Audience private` |

HTML reports are generated views. Persist user decisions back to Markdown or code through a separate reviewed agent task.

## Claude/Cowork Adapter

Install the plugin globally, but point it at the active project. See `docs/install-plugin.md` for the exact Claude/Codex copy paths.

When Claude/Cowork starts from the initialized project root, the hooks can find
`PROJECT_CONTEXT.md`, `agent-memory/`, and the local CLI without environment
variables. Use an explicit project root only when the runtime starts elsewhere.

```powershell
$env:AGENT_MEMORY_PROJECT_ROOT = "C:\path\to\project"
$env:AGENT_MEMORY_CAPTURE_MODE = "standard"
```

`AGENT_MEMORY_KIT_ROOT` is optional for a bootstrapped project because the host project already contains `tools/agent_memory_cli.py`. Set it only when the plugin must fall back to the global kit tools.

On macOS/Linux, use the Unix hook profile or generate the folder with
`--include-plugin-adapter --plugin-hook-profile unix`.

Use `memory-init` for setup, `memory-status` for read-only status, `memory-doctor` for QA, and `memory-report` for generated HTML reports.

For a central hub or shared machine, always scope customer-facing reports and private exports:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\export-lightrag.ps1 -CorpusType private -TenantId tenant-a -CustomerId customer-a -ProjectId project-a
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\render-memory-report.ps1 -ReportType project-dashboard -Audience customer -TenantId tenant-a -CustomerId customer-a -ProjectId project-a
```

## RAG Rules

- Use RAG as a consumer, not source of truth.
- Export reviewed/promoted knowledge only by default.
- Shared exports require `visibility=shared`, `review_status=approved`, and `sanitization_status=approved`.
- Raw sessions are for deep dives, not default RAG ingestion.
- Daily notes, personal tasks and onboarding profiles are not default RAG input.
- Private RAG exports still require reviewed/promoted knowledge by default; pass `-IncludeDrafts` only for explicit local debugging.
