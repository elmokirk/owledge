# Finalization Gates

- Generated at: 2026-06-25T11:27:36Z
- Passed: False
- Failed gates: 1
- Quality ratchet summary: internal/agent-memory/exports/finalization-gates/quality-ratchet-summary.json

## Gates

- PASS `python-compile` in 0.325s
- PASS `public-docs` in 0.017s
- PASS `release-trust` in 0.001s
- PASS `principles-skill` in 0.002s
- PASS `principles-only` in 0.002s
- PASS `principles-scenarios` in 1.618s
- PASS `poweruser-simulations` in 13.521s
- FAIL `contracts` in 0.007s - {
  "project": "C:\\Users\\Kirk\\Documents\\Playground\\agent-memory-standalone",
  "passed": false,
  "totalChecks": 328,
  "failedChecks": 89,
  "results": [
    {
      "name": "dir:agent-memory/templates",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/schemas",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/canonical",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/compiled",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/patterns",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/lessons",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/ideas",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/pi-agent",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/pi-agent/reports",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/pi-agent/parallels",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/pi-agent/trends",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/pi-agent/recurring-errors",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/pi-agent/concepts",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/pi-agent/red-team",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/pi-agent/evaluations",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/pi-agent/scorecards",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/pi-agent/indexes",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/sessions",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/decisions",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/evidence",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/evidence/promotions",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/handoffs",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/indexes",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/exports/rag",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/exports/lightrag",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:agent-memory/exports/graphrag",
      "passed": false,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/preferences",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/goals",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/daily",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/tasks",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/ideas",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/research",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/patterns",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/coach",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/indexes",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/exports/rag",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/exports/lightrag",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:global-memory/exports/graphrag",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:tools",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:docs",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:docs/archive",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:benchmarks",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:benchmarks/results",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:assets",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:.github",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:.github/ISSUE_TEMPLATE",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:.github/workflows",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:skills/agent-memory-principles",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:skills/agent-memory-runtime-bridge",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:skills/render-memory-report",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:skills/review-evaluation-workflow",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:skills/personal-pi-agent",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:skills/concept-blindspot-audit",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/.claude-plugin",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/.codex-plugin",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/hooks",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/skills/agent-memory-principles",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/skills/agent-memory-runtime-bridge",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/skills/render-memory-report",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/skills/review-evaluation-workflow",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/agents",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/commands",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/scripts",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/agent-memory-cowork/tests/fixtures",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/pi-agent-workspace",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/pi-agent-workspace/.claude-plugin",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/pi-agent-workspace/.codex-plugin",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/pi-agent-workspace/agents",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/pi-agent-workspace/commands",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/pi-agent-workspace/skills/pi-agent-workspace-quality",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/pi-agent-workspace/skills/pi-agent-global-intelligence",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/pi-agent-workspace/skills/pi-agent-red-team-evaluator",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "dir:plugins/pi-agent-workspace/skills/personal-pi-agent",
      "passed": true,
      "details": "Required directory exists."
    },
    {
      "name": "file:README.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:LICENSE",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:VERSION",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:CHANGELOG.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:SECURITY.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:PRIVACY.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:ROADMAP.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:DESIGN.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:REPORT_DESIGN_SELECTOR.html",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:CONTRIBUTING.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:CODE_OF_CONDUCT.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:SUPPORT.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:USER_CONTEXT.template.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/README.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/quickstart.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/agent-first-run-setup.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/owledge-vs-agent-methods.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/global-user-knowledge-layer.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/agentic-memory-architecture.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/project-folder-only-quickstart.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/cross-platform-lean-setup.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/agent-integration-guide.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/superpowers-integration.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/harness-plugin-matrix.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/mvp-plan-example.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/team-long-running-project-guide.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/performance-scale-notes.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/html-reports.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/project-snapshot-kit.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/incremental-index-workflow.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/reusable-review-evaluation-templates.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/README.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/publishing.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/finalization-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/compliance-implementation-plan.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/compliance-roadmap.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/dashboard-extension-plan.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/incremental-index-finalization-sprint.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/review-workflow-finalization-sprint.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/ai-workos-vault-merge-evaluation.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/ai-workos-vault-adapter-plan.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/pi-agent-adapter-plan.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/pi-agent-global-intelligence-plan.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/archive/pi-agent-red-team-evaluation-plan.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:PROJECT_CONTEXT.template.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:AGENTS.template.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:CLAUDE.template.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:CLAUDE.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:.gitignore",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/README.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/agent-session-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/orchestration-delta-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/root-review-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/adr-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/concept-audit-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/canonical-memory-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/compiled-memory-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/pattern-card-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/shared-lesson-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/idea-card-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/user-context-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/preference-card-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/goal-card-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/daily-note-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/personal-task-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/research-card-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/personal-pattern-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/coach-report-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/onboarding-profile-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/pi-intelligence-report-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/pi-parallel-report-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/pi-recurring-error-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/pi-central-project-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/evaluation-framework-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/pi-red-team-evaluation-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/agent-quality-scorecard-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/multi-perspective-red-team-review-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/expert-lens-evaluation-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/scenario-simulation-evaluation-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/evaluation-persona-pack-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/review-to-task-plan-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/project-index-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/evidence-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/handoff-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/qa-gate-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/rag-export-manifest-template.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/epic-overview-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/workpackage-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/techspec-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/task-card-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/qa-spec-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/gate-report-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/handoff-packet-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/templates/context-pack-template.md",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/tenant.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/agent.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/epic.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/workpackage.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/task-card.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/qa-spec.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/gate-report.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/context-pack.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/lightrag-export.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/frontmatter.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/edge.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/canonical-memory.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/compiled-memory.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/pattern-card.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/shared-lesson.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/rag-document.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/graphrag-node.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/graphrag-edge.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:agent-memory/schemas/global-user-memory.schema.json",
      "passed": false,
      "details": "Required file exists."
    },
    {
      "name": "file:tools/owledge.py",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tools/agent_memory_cli.py",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tools/build_project_folder_kit.py",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tools/build_kb_module.py",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:benchmarks/README.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:benchmarks/results/README.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:benchmarks/run_benchmarks.py",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:assets/README.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:assets/social-preview.svg",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:.github/ISSUE_TEMPLATE/bug_report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:.github/ISSUE_TEMPLATE/feature_request.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:.github/PULL_REQUEST_TEMPLATE.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:.github/workflows/ci.yml",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:.github/workflows/docs.yml",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/tests/fixtures/session-start.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/tests/fixtures/user-prompt.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/tests/fixtures/post-tool-use.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/tests/fixtures/stop.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-queries.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/canonical/memory-lifecycle-policy.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/canonical/context-pack-objective.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/canonical/stale-research-signal.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/compiled/context-pack-scoring.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/compiled/promotion-audit.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/patterns/progressive-disclosure-runtime.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/patterns/cross-project-parallel.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/lessons/privacy-export-gate.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/lessons/runtime-rag-safety.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/decisions/markdown-source-of-truth.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:tests/fixtures/retrieval-corpus/agent-memory/compiled/stale-conflict-review.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/agent-memory-principles/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/agent-memory-principles/references/principles.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/agent-memory-principles/references/agent-rules.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/agent-memory-principles/references/mapping-contract.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/agent-memory-principles/references/security-rules.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/agent-memory-runtime-bridge/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/bootstrap-agent-memory/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/pi-agent-workspace-quality/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/pi-agent-global-intelligence/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/pi-agent-red-team-evaluator/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/personal-pi-agent/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/render-memory-report/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/review-evaluation-workflow/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/concept-blindspot-audit/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/concept-blindspot-audit/references/audit-dimensions.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/concept-blindspot-audit/references/profile-template.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/render-memory-report/references/decision-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/render-memory-report/references/handoff-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/render-memory-report/references/rag-readiness-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/render-memory-report/references/agent-activity-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/render-memory-report/references/project-dashboard.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/render-memory-report/references/website-ui-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:skills/render-memory-report/references/report-design-systems.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/.claude-plugin/plugin.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/.codex-plugin/plugin.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/hooks/hooks.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/hooks/hooks.python.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/agent-memory-principles/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/agent-memory-principles/references/principles.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/agent-memory-principles/references/agent-rules.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/agent-memory-principles/references/mapping-contract.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/agent-memory-principles/references/security-rules.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/agent-memory-runtime-bridge/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/bootstrap-agent-memory/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/render-memory-report/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/review-evaluation-workflow/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/render-memory-report/references/decision-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/render-memory-report/references/handoff-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/render-memory-report/references/rag-readiness-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/render-memory-report/references/agent-activity-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/render-memory-report/references/project-dashboard.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/render-memory-report/references/website-ui-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/skills/render-memory-report/references/report-design-systems.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/agents/memory-curator.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/commands/memory-init.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/commands/memory-status.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/commands/memory-doctor.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/commands/memory-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/scripts/capture-claude-event.py",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/scripts/close-runtime-session.py",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/README.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/LICENSE",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/VERSION",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/agent-memory-cowork/CHANGELOG.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/.claude-plugin/plugin.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/.codex-plugin/plugin.json",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/README.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/agents/pi-workspace-guardian.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/agents/pi-global-intelligence.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/agents/pi-red-team-evaluator.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/commands/pi-workspace-check.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/commands/pi-intelligence-report.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/commands/pi-redteam-evaluate.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/skills/pi-agent-workspace-quality/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/skills/pi-agent-global-intelligence/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/skills/pi-agent-red-team-evaluator/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:plugins/pi-agent-workspace/skills/personal-pi-agent/SKILL.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/ideation-workflow.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/install-plugin.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:docs/command-reference.md",
      "passed": true,
      "details": "Required file exists."
    },
    {
      "name": "file:addons/compliance-light/addon.json",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/README.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/docs/compliance-light.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/templates/processing-activity-template.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/templates/ai-system-template.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/templates/provider-registry-template.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/templates/dpia-trigger-template.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/templates/data-subject-request-template.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/templates/security-incident-template.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/schemas/compliance-record.schema.json",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/starter/agent-memory/compliance/profile.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/tests/fixtures/minimal-pass/agent-memory/compliance/profile.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/tests/fixtures/minimal-pass/agent-memory/compliance/registers/processing-activity.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/tests/fixtures/minimal-pass/agent-memory/compliance/registers/provider.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/tests/fixtures/minimal-pass/agent-memory/compliance/ai-systems/ai-system.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/tests/fixtures/minimal-pass/agent-memory/compliance/dpia/dpia-trigger.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/tests/fixtures/missing-provider/agent-memory/compliance/profile.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/tests/fixtures/invalid-processing-fields/agent-memory/compliance/profile.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/compliance-light/tests/fixtures/invalid-processing-fields/agent-memory/compliance/registers/processing-activity.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/project-snapshot-kit/addon.json",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/project-snapshot-kit/README.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/project-snapshot-kit/docs/project-snapshot-kit.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/project-snapshot-kit/starter/agent-memory/project-snapshot/profile.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/project-snapshot-kit/templates/project-story-snapshot-template.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/project-snapshot-kit/templates/project-execution-snapshot-template.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/project-snapshot-kit/templates/project-site-html-template.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/project-snapshot-kit/skills/render-memory-report/references/project-site.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:addons/project-snapshot-kit/skills/render-memory-report/references/execution-dashboard.md",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "file:tests/fixtures/compliance-light/expected-installed-delta.txt",
      "passed": true,
      "details": "Optional add-on file exists."
    },
    {
      "name": "addon-schema-json:compliance-record.schema.json",
      "passed": true,
      "details": "Valid JSON."
    },
    {
      "name": "gitignore:.agent-control/agent-memory.sqlite*",
      "passed": true,
      "details": "Runtime or scratch path is ignored."
    },
    {
      "name": "gitignore:.agent-control/secrets/",
      "passed": true,
      "details": "Runtime or scratch path is ignored."
    },
    {
      "name": "gitignore:agent-memory/tmp/",
      "passed": true,
      "details": "Runtime or scratch path is ignored."
    },
    {
      "name": "gitignore:agent-memory/exports/retrieval-eval/",
      "passed": true,
      "details": "Runtime or scratch path is ignored."
    },
    {
      "name": "gitignore:agent-memory/exports/finalization-gates/",
      "passed": true,
      "details": "Runtime or scratch path is ignored."
    },
    {
      "name": "gitignore:agent-memory/exports/compliance/",
      "passed": true,
      "details": "Runtime or scratch path is ignored."
    },
    {
      "name": "gitignore:agent-memory/reports/project-site/",
      "passed": true,
      "details": "Runtime or scratch path is ignored."
    },
    {
      "name": "gitignore:agent-memory/project-snapshot/project-snapshot-manifest.json",
      "passed": true,
      "details": "Runtime or scratch path is ignored."
    },
    {
      "name": "gitignore:agent-plans/",
      "passed": true,
      "details": "Runtime or scratch path is ignored."
    },
    {
      "name": "runtime-instructions-sync",
      "passed": true,
      "details": "AGENTS and CLAUDE templates should remain byte-identical."
    },
    {
      "name": "tenant-fields-present",
      "passed": true,
      "details": "Files missing tenant fields: "
    }
  ]
}
- PASS `core-platform-neutral` in 0.235s
- PASS `generated-kit-surface` in 3.665s
- PASS `doctor` in 0.008s
- PASS `validate` in 0.088s
- PASS `index-full` in 0.051s
- PASS `index-incremental` in 0.067s
- PASS `retention` in 0.017s
- PASS `conflicts` in 0.077s
- PASS `sensitive-scan` in 0.102s
- PASS `runtime-adapters` in 1.444s
- PASS `memory-evals` in 3.246s
- PASS `retrieval-fixture` in 0.03s
- PASS `kb-ingestion-safety` in 0.139s
- PASS `benchmark` in 2.07s
- PASS `quality-ratchet` in 8.022s
- PASS `kb-module` in 0.256s
- PASS `project-folder-kit` in 0.89s
- PASS `dogfood-sync` in 0.009s
- PASS `upgrade-drift` in 0.218s
- PASS `concept-audit-fresh` in 0.001s
- PASS `compliance-addon-source` in 0.0s
- PASS `project-folder-kit-compliance` in 0.908s
- PASS `compliance-gates` in 0.014s
- PASS `export-rag-shared` in 0.06s
- PASS `export-lightrag-shared` in 0.086s
- PASS `export-graphrag-shared` in 0.059s
- PASS `report-shared` in 0.046s
