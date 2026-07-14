# OKF Integration Plan

Date: 2026-07-07
Status: roadmap proposal
Scope: map Google's Open Knowledge Format v0.1 into Owledge without weakening Owledge's lifecycle, privacy, and promotion model.

## Executive Summary

Google's Open Knowledge Format (OKF) is strongly aligned with Owledge's core thesis: durable knowledge should be plain Markdown with YAML frontmatter, stored as files, readable by humans, parseable by agents, and portable across tools.

The practical difference is scope:

- OKF defines a minimal interchange format.
- Owledge defines an operational memory system around Markdown: IDs, lifecycle, review, privacy, promotion, exports, agent handoffs, QA gates, and runtime adapters.

Owledge should adopt OKF as a native interchange profile, not replace its stricter memory contract. The right move is to make every exportable Owledge record optionally renderable as OKF, make OKF bundles importable into a quarantined/draft Owledge layer, and add validation/reporting that distinguishes "OKF conformant" from "Owledge governed".

## What OKF Standardizes

OKF v0.1 represents knowledge as a directory tree of Markdown files with YAML frontmatter. Each non-reserved Markdown file is a concept document. The file path is the concept ID. A concept has one required frontmatter field:

- `type`

Recommended frontmatter fields:

- `title`
- `description`
- `resource`
- `tags`
- `timestamp`

Reserved filenames:

- `index.md` for progressive disclosure
- `log.md` for chronological update history

Relationships are expressed through normal Markdown links. Consumers are expected to tolerate unknown types, unknown frontmatter keys, missing optional fields, missing indexes, and broken links.

## Owledge vs OKF

| Dimension | OKF | Owledge | Product read |
| --- | --- | --- | --- |
| Primary goal | Interoperable knowledge bundle | Durable agent memory with governance | Complementary, not competitive |
| Canonical storage | Markdown files + YAML frontmatter | Markdown files + YAML frontmatter | Direct alignment |
| Required metadata | Minimal: `type` only | Strict: stable IDs, scope, lifecycle, visibility, review, sanitization, confidence, edges | Owledge is stricter by design |
| Identity | File path without `.md` | `memory_id` as stable ID; path is source location | OKF export can use path identity while preserving `memory_id` as extension |
| Relationships | Markdown links; edge type inferred from prose | Typed `edges` in frontmatter plus evidence links | Export both: Markdown links for OKF, typed edges as Owledge extension |
| Lifecycle | Not specified | draft, active, reviewed, promoted, superseded, archived | Owledge lifecycle should remain native |
| Privacy/export safety | Not specified | visibility, data class, review and sanitization gates | Critical Owledge advantage |
| Indexing | Optional `index.md`; consumers can synthesize | JSONL indexes, manifests, tombstones, context packs | Add OKF index generation as another view |
| Logs/history | Optional `log.md`; Git recommended | Evidence, sessions, promotion manifests, finalization gates | Map selected audit summaries to OKF logs, not raw sessions |
| Runtime model | No required SDK/runtime | Local CLI, skills, runtime adapters | Owledge can be an OKF producer and consumer |
| Enterprise readiness | Format only | Partial governance; compliance still roadmap | Owledge should not overclaim compliance just because OKF is adopted |

## Realistic Feedback

OKF validates Owledge's direction. The market signal is strong: a major cloud vendor is now framing "Markdown plus YAML frontmatter plus Git" as the lowest-friction substrate for agent knowledge. That supports Owledge's positioning and reduces the need to argue for the storage primitive.

OKF also raises the bar for Owledge's interoperability story. If Owledge remains only "its own Markdown contract", it risks looking like a stricter variant of a now-standard pattern. The product should instead say: Owledge is OKF-compatible where portability matters, and Owledge-governed where agents need trust, privacy, promotion, and lifecycle discipline.

The biggest mismatch is identity. OKF treats file path as concept identity; Owledge correctly uses stable `memory_id` because paths move. Native support should not downgrade Owledge IDs. The OKF profile should preserve `memory_id` as an extension field and make path-based OKF IDs a transport alias.

The second mismatch is relationship semantics. OKF deliberately keeps links untyped. Owledge's typed edges are valuable for GraphRAG, decision traces, conflict review, and promotion. Native OKF support should emit Markdown links for OKF consumers, while preserving typed edges in frontmatter under extension keys.

The third mismatch is safety. OKF is permissive and format-level. Owledge's shared export gates are stricter and should remain mandatory for any `shared` OKF export. Importing OKF must default to private draft records until reviewed and sanitized.

## Native Integration Model

### 1. Add an OKF Profile

Add a formal `okf-v0.1` profile to Owledge docs and CLI output.

Recommended fields for Owledge-generated OKF concept frontmatter:

```yaml
type: "Owledge Lesson"
title: "Short readable title"
description: "One sentence summary."
resource: "mem:tenant:customer:project:..."
tags: ["owledge", "lesson"]
timestamp: "2026-07-07T00:00:00Z"
okf_version: "0.1"
owledge_memory_id: "mem:..."
owledge_doc_type: "lesson"
owledge_visibility: "shared"
owledge_review_status: "approved"
owledge_sanitization_status: "approved"
```

This keeps OKF consumers happy while preserving Owledge provenance.

### 2. Export OKF Bundles

Add:

```bash
python tools/owledge.py --project-root . export-okf --corpus-type shared
```

Output:

```text
.owledge/exports/okf/
  index.md
  log.md
  canonical/
  decisions/
  lessons/
  patterns/
  handoffs/
  references/
  manifest.json
  latest.json
```

Policy:

- `private` export may include draft/internal records for local use.
- `shared` export must require the existing reviewed, approved, sanitized, safe-data-class gates.
- Generated OKF bundles remain disposable views. Markdown source remains canonical.

### 3. Import OKF Bundles

Add:

```bash
python tools/owledge.py --project-root . import-okf --bundle /path/to/okf --mode draft
```

Default import target:

```text
.owledge/imports/okf/<bundle-name>/
```

Import policy:

- Imported concepts become `status: draft`.
- `visibility: private` by default.
- `review_status: unreviewed`.
- `sanitization_status: pending`.
- `memory_id` is generated unless `owledge_memory_id` is present and valid.
- OKF Markdown links are preserved; typed edges are inferred only into a review report unless explicitly accepted.

### 4. Validate OKF Conformance

Add:

```bash
python tools/owledge.py --project-root . validate-okf --bundle .owledge/exports/okf
```

Checks:

- every concept `.md` has parseable YAML frontmatter
- every concept has non-empty `type`
- reserved `index.md` and `log.md` follow OKF structure
- bundle-root `index.md` may declare `okf_version: "0.1"`
- unknown fields are accepted
- broken links are warnings, not failures

### 5. Add OKF Readiness Report

Extend HTML/report tooling with an `okf-readiness` report:

- OKF conformance status
- export eligibility counts
- rejected records by reason
- private/shared boundary status
- Markdown-link graph preview
- typed Owledge edge preservation summary

### 6. Add OKF to Cross-Project Hub

The cross-project hub should accept OKF as a neutral ingest/export envelope:

```text
project Owledge memory
-> reviewed shared export
-> OKF bundle
-> external hub / Google Knowledge Catalog / other agents
```

Reverse flow:

```text
external OKF bundle
-> private draft import
-> review/sanitize/promote
-> Owledge canonical/pattern/lesson records
```

## Field Mapping

| OKF field | Owledge source | Direction | Notes |
| --- | --- | --- | --- |
| `type` | `doc_type` mapped to readable type | export/import | Required for OKF |
| `title` | `semantic_title` or Markdown H1 | export/import | Prefer `semantic_title` |
| `description` | `summary` | export/import | One-sentence target |
| `resource` | `memory_id` or external source URI | export/import | Use `memory_id` when no external asset exists |
| `tags` | `concept_tags` + selected `stack_tags` | export/import | Avoid leaking sensitive tags in shared export |
| `timestamp` | `updated_at` | export/import | ISO 8601 |
| concept ID | source path in OKF bundle | export/import | Treat as alias, not stable Owledge ID |
| Markdown links | body links + edge renderings | export/import | OKF graph surface |
| `index.md` | generated from memory index | export | Progressive disclosure |
| `log.md` | generated from promotion/export manifest | export | Do not include raw sessions |
| unknown fields | preserved | import/export | OKF requires tolerance |

Owledge extension fields should use an `owledge_` prefix to avoid pretending they are part of OKF v0.1.

## Recommended Roadmap Items

| Priority | Item | Outcome |
| --- | --- | --- |
| P0 | OKF positioning update | README/docs state "OKF-compatible interchange; Owledge-governed memory lifecycle" |
| P1 | `validate-okf` | Validate external and generated OKF bundles without weakening Owledge validation |
| P1 | `export-okf` | Generate OKF v0.1 bundles from private/shared Owledge memory with existing export gates |
| P1 | OKF field map schemas | Add documented mapping and fixtures for `doc_type` to OKF `type` |
| P2 | `import-okf` draft ingest | Bring external OKF bundles into private draft import area with review reports |
| P2 | OKF readiness report | HTML report for conformance, rejected records, graph links, and safety gates |
| P2 | Cross-project hub OKF bridge | Use OKF as neutral exchange format for reviewed hub sync |
| P3 | Knowledge Catalog adapter notes | Document Google Knowledge Catalog / BigQuery-oriented producer-consumer path |

## Definition Of Done

Native OKF support is done when:

- Owledge can validate an OKF bundle.
- Owledge can export a conformant OKF v0.1 bundle from reviewed memory.
- Shared OKF export cannot leak private, unreviewed, unsanitized, confidential, personal, or raw session records.
- Owledge can import an external OKF bundle into private drafts without automatic promotion.
- Round-trip tests preserve source paths, `memory_id`, summary/title metadata, Markdown links, and extension fields.
- Docs clearly distinguish OKF conformance from Owledge governance.

## Product Positioning

Recommended language:

> Owledge is an OKF-compatible agent memory layer. OKF gives Owledge a portable interchange format; Owledge adds the operational layer agents need in real projects: durable IDs, scoped context, review, sanitization, promotion, evidence, handoffs, and safe exports.

Avoid:

- "Owledge replaces OKF"
- "OKF solves compliance"
- "Path identity is enough"
- "All Owledge memory is OKF by default"

The stronger claim is narrower: Owledge should speak OKF at its boundaries while keeping its stricter memory contract inside the system.
