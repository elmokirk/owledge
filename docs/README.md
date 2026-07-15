# Owledge Docs

## Current release

**Owledge v0.7.0** is the current released package. The canonical release
version is [../VERSION](../VERSION); use [quickstart.md](quickstart.md) for new
installs and [upgrading.md](upgrading.md) for existing projects.

Start with the path that matches your setup.

Maintainers: distribution.md defines the release-branch, PyPI confirmation,
main-promotion, and release-evidence contract.

## I only want the principles in an existing agent system

- This is the default minimal path
- Read [agent-integration-guide.md](agent-integration-guide.md)
- Read [integration-decision-guide.md](integration-decision-guide.md) when you are unsure which path to choose
- Use `skills/owledge-principles` as the portable rule set
- Add project files only when the team wants local validation and indexes

## I want to see value in five minutes

- Read [try-owledge-in-5-minutes.md](try-owledge-in-5-minutes.md)
- Install `launch-demo-kit` for evidence, handoff, and a static proof report
- Run `python tools/owledge.py test launch-readiness --project-root .` before broad sharing

## I already have a Markdown knowledgebase

- Read [agent-integration-guide.md](agent-integration-guide.md)
- Then read [mvp-plan-example.md](mvp-plan-example.md)
- For a tiny demo vault, see [../examples/README.md](../examples/README.md)

## I want Owledge inside a coding project

- Read [quickstart.md](quickstart.md)
- Then read [command-reference.md](command-reference.md)
- Use `uvx owledge quickstart --target <path>` for the package-first path
- Expect `OWLEDGE.md` and `.owledge/` in new v0.7.0 projects

## I want plugin or harness setup

- Read [install-plugin.md](install-plugin.md)
- Then read [harness-plugin-matrix.md](harness-plugin-matrix.md)
- Read-only MCP is available through `tools/owledge_mcp.py`; write-enabled MCP and harness benchmarks are roadmap items

## I want an optional project cockpit

- Install the optional `project-snapshot-kit` add-on
- Read [project-snapshot-kit.md](project-snapshot-kit.md)
- Generate snapshots or static HTML only when explicitly requested

## I want to understand scale and quality

- Read [performance-scale-notes.md](performance-scale-notes.md)
- Read [benchmark-kit.md](benchmark-kit.md)
- Run `owledge wikilink-audit --project-root . --check` for Markdown/Obsidian link health
- Install `benchmark-kit` for optional real Markdown fixture benchmark reports
- Run `python tools/benchmark-kit/run-benchmark-kit.py --mode ci --scale-mode small --yes` for deterministic benchmark reports
- Use `python tools/benchmark-kit/run-benchmark-kit.py --mode local --scale-mode small --models <model> --yes` for opt-in sequential Ollama testing
- Use `python tools/benchmark-kit/compare-benchmark-runs.py --inputs <reports...> --output .owledge/reports/generated/benchmark-kit-comparison` for multi-model baseline-vs-Owledge proof reports
- Use [../standalone-skills/README.md](../standalone-skills/README.md) when you only want one Owledge skill without the full kit
- Read [critique-derived-addons-roadmap.md](critique-derived-addons-roadmap.md) for the power-user critique that shaped the optional add-on layer
- Read [power-user-objections.md](power-user-objections.md) for durable pitch objections and product guardrails
- Install `decision-trace-kit` when you need a visual, read-only decision tree from Markdown memory records
- Install `cross-project-hub-kit` when reviewed lessons from separate projects should feed a central reusable hub
- Install `swarm-coordination-kit` when multiple agents need role lanes, handoffs, and promotion proposals
- Install `poweruser-positioning-kit` when you need a snapshot-first positioning scorecard for adjacent AI-agent tool categories
- Read [launch-readiness.md](launch-readiness.md)
- Read [distribution.md](distribution.md)
- Read [operational-hardening.md](operational-hardening.md)
- Read [team-long-running-project-guide.md](team-long-running-project-guide.md)
- Run `python tools/owledge.py test quality-ratchet --project-root .`

## I want category context

- Read [owledge-vs-agent-methods.md](owledge-vs-agent-methods.md)
- Read [superpowers-integration.md](superpowers-integration.md) when comparing Owledge with execution frameworks
- Read [okf-integration-plan.md](okf-integration-plan.md) for the planned OKF-compatible interchange profile

## Advanced

- [project-folder-only-quickstart.md](project-folder-only-quickstart.md)
- [cross-platform-lean-setup.md](cross-platform-lean-setup.md)
- [agent-first-run-setup.md](agent-first-run-setup.md)

## Integration And Setup Guides

- [agents-md-integration-block.md](agents-md-integration-block.md) - copy-paste Owledge rules into an existing AGENTS.md or CLAUDE.md
- [pi-agent-setup.md](pi-agent-setup.md) - how to set up and run the PI Agent (deterministic mode, no auth needed)

## Feedback And Roadmap

- [feedback-round-2026-06.md](feedback-round-2026-06.md) - structured feedback triage with tickets FB-001 through FB-017 (including Round 2 feature ideas FB-013 through FB-017)
- [roadmap-ideas-2026-06.md](roadmap-ideas-2026-06.md) - idea log from the 2026-06 feedback round with 16 idea cards (including Round 2 feature ideas)
- [strategic-roadmap-2026-2027.md](strategic-roadmap-2026-2027.md) - decision-ready product and execution roadmap after the v0.7.0 release

## Maintainer And Historical Docs

- [archive/README.md](archive/README.md)
