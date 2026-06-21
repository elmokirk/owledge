# Decision Trace Kit

Optional add-on that renders a read-only decision trace from Owledge Markdown
memory into JSON and HTML.

## Trace Shape

```text
project context -> goal -> idea -> plan -> task -> evidence -> review -> decision/ADR -> lesson/pattern
```

The trace is generated from `memory_id`, document type, review status,
visibility, source hashes, and typed frontmatter edges. If explicit edges are
missing, the renderer adds read-only inferred phase edges for visualization
only; it does not write those inferred edges back to source Markdown.

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon decision-trace-kit
```

## Render

```bash
python tools/decision-trace/render-decision-trace.py --project-root .
```

Outputs:

```text
agent-memory/decision-trace/trace.json
agent-memory/reports/decision-trace/index.html
```

## Guardrails

- HTML is a generated view.
- JSON is a trace artifact, not canonical project truth.
- Shared mode excludes private, unsanitized, and unreviewed records.
- The add-on does not promote decisions or edit source memory.
- The HTML tree is generated from `trace.json` data and contains no write
  controls.
