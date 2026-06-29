---
memory_id: "mem:tenant-local:customer-local:owledge-standalone:compiled:project-execution-snapshot"
tenant_id: "tenant-local"
customer_id: "customer-local"
project_id: "owledge-standalone"
doc_type: "compiled"
snapshot_kind: "execution_state"
status: "draft"
visibility: "private"
data_class: "internal"
semantic_title: "Project execution snapshot"
summary: "Reusable MVP, roadmap, workstream, task, blocker, QA, and agent activity snapshot."
concept_tags:
  - "project-snapshot"
stack_tags: []
problem_patterns: []
architecture_patterns: []
failure_modes: []
reusable_lessons: []
confidence: 0.7
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "2026-06-19T14:04:07Z"
updated_at: "2026-06-19T14:04:07Z"
retention_class: "standard"
stale_after: ""
expires_at: ""
last_reviewed_at: ""
review_cycle: "monthly"
source_hash: "d848dec2c3e8ec4b6add79cf32eede623c1ea74c26994368af4eb42d12bfa0a6"
edges: []
---
# Project Execution Snapshot

## Goal

Keep owledge-standalone execution state visible through local Owledge plans, task cards, evidence, handoffs, and generated snapshots.

## MVP

- Install Project Snapshot Kit only when requested.
- Generate source-backed Markdown snapshots.
- Generate static local HTML from existing snapshots.
- Track Owledge-local task status deterministically.

## Explicitly Out Of MVP

- External GitHub, Linear, or Jira synchronization.
- Hosted dashboard, authentication, or RBAC.
- Automatic promotion to canonical memory.
- Model calls from the CLI.

## Active Workstreams

| Task type | Count |
| --- | --- |

## Task Status

| Status | Count |
| --- | --- |

## Local Tasks And Plans

- No Owledge-local task artifacts found.

## Roadmap

- Refresh snapshots when source hashes change.
- Keep HTML regeneration deterministic and zero-token.
- Add external ticket adapters later as optional importers.

## Blockers

- No blockers detected in local task artifacts.

## QA Gates

- Run `python tools/owledge_core.py --project-root . validate-memory --strict`.
- Run `python tools/owledge.py doctor --project-root .`.
- Run add-on generation with `--changed-only` before sharing reports.

## Latest Agent Activity

Source-backed activity is summarized from handoffs and evidence records only. Raw runtime event logs are excluded.

## Sources

| Source | Type | Hash |
| --- | --- | --- |
| OWLEDGE.template.md | project_context | bd2e88a545213622 |
| .owledge/ideas/pi-agent-global-intelligence.md | idea | 0bc48096b1cb2930 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260526152155-8884-c0d48fe7.md | qa | 69ba6f055bfb27d1 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260526152246-23008-b6295fd5.md | qa | a385048efd5ca51b |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260526184806-16688-d0de5d35.md | qa | a004375d0e9883a0 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260526184929-31580-875b8946.md | qa | 61eedfe8b4583042 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260527134409-43176-c0ea8c34.md | qa | 8ca60f3d8217e0ae |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260527134527-18064-1776618b.md | qa | d2d56a6c0ad55864 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260527134652-44888-989b2391.md | qa | 8947a4c0b6d85931 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260527191826-26932-48444041.md | qa | 29a3380a86ef3278 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260601114428-46544-1892e18b.md | qa | 68c60511c7ab5b2a |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260615182353-21644-9208b830.md | qa | 2b952ae362d830b3 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260615202645-4976-af217c1a.md | qa | 70c38ca1ef8ae52f |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260618124159-45020-5ec83a9c.md | qa | 60c0a104bd7a3a28 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260618124238-45764-175c918f.md | qa | 93b68f5d8508969c |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260618124312-48992-b62a825e.md | qa | 05391ea2b2e7aac4 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260618124555-7228-9757e6f0.md | qa | 92940aa225962276 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260618131340-57980-fb4fecec.md | qa | 9e8ccf579b25e530 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260618131428-31236-c3812307.md | qa | 30e33cabb1ff1265 |
| .owledge/pi-agent/red-team/multi-perspective-red-team-v0-5-final-redteam-20260618131551-44460-1ce99787.md | qa | c6a7766468129ac9 |
| .owledge/pi-agent/red-team/pi-redteam-evaluation-20260516105511-40152-35dbdf99.md | qa | fa0e15c1ee44e451 |
| .owledge/pi-agent/red-team/pi-redteam-evaluation-20260516132641-39528-a85541aa.md | qa | c3c631f2cf915849 |
| .owledge/pi-agent/red-team/pi-redteam-evaluation-20260516133409-54600-b276791e.md | qa | d4b4b5bafd625cb7 |
| .owledge/pi-agent/reports/pi-intelligence-20260516105510-21912-e98369c6.md | qa | 1464c196a21bfcaa |
