# Poweruser Positioning Kit

Optional snapshot-first scorecard for explaining where Owledge fits beside
AI-agent power-user tools.

## Purpose

This add-on does not claim that Owledge replaces execution frameworks, graph
visualizers, wikis, agent runtimes, or custom harnesses. It documents Owledge as
a memory and proof layer around those systems.

## Comparator Categories

- Owledge.
- Superpowers-style execution frameworks.
- Graphify-style graph visualizers.
- LLM Wiki / Obsidian-style knowledgebases.
- Claude Code / Codex-style agent runtimes.
- Custom harnesses and hooks.

## Run

```bash
python tools/poweruser-positioning/render-poweruser-positioning.py --project-root .
```

Outputs:

```text
.owledge/reports/poweruser-positioning/positioning.json
.owledge/reports/poweruser-positioning/positioning.md
.owledge/reports/poweruser-positioning/index.html
```

## Guardrails

- Snapshot-first and reproducible by default.
- External repo URLs can be added later without making tests network-dependent.
- Scores describe fit for Owledge's positioning, not absolute product quality.
- The result should support pitches and red-team review, not vendor bashing.
