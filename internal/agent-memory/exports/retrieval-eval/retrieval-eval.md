# Memory Retrieval Eval

## Summary

- Projects: retrieval-fixture, retrieval-reference
- Corpus documents: 11
- Overall score: 93.53
- Precision score: 78.45
- Scalability score: 100
- Reusability score: 100
- Parallel score: 100
- Safety score: 100.0
- Passed thresholds: True
- Cross-project parallel candidates: 16

## Freshness Warnings

- `mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:stale-research-signal` (agent-memory/canonical/stale-research-signal.md): 3 warning(s)
- `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` (agent-memory/compiled/context-pack-scoring.md): 1 warning(s)
- `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` (agent-memory/compiled/stale-conflict-review.md): 2 warning(s)

## Query Results

### lifecycle-safety

- Query: `agent memory retention stale conflict sensitive data raw session shared export production ready`
- Precision@5: 1.0
- Recall@5: 0.4545
- MRR: 1.0
- nDCG@5: 1.0
- Project coverage: 1.0
- Latency: 0.457 ms
- Top hits:
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=88.522754)
  - `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` (retrieval-reference, score=70.659981)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety` (retrieval-fixture, score=37.263981)
  - `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` (retrieval-reference, score=32.251154)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:stale-research-signal` (retrieval-fixture, score=24.734642)

### context-objective-scoring

- Query: `context pack task objective score_breakdown freshness_warnings budget exclusions retrieval calibration`
- Precision@5: 1.0
- Recall@5: 0.4545
- MRR: 1.0
- nDCG@5: 1.0
- Project coverage: 1.0
- Latency: 0.41 ms
- Top hits:
  - `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` (retrieval-fixture, score=226.186217)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:context-pack-objective` (retrieval-fixture, score=154.471258)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:stale-research-signal` (retrieval-fixture, score=37.4946)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=13.868617)
  - `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` (retrieval-reference, score=8.318333)

### runtime-procedural-memory

- Query: `progressive disclosure procedural memory runtime bridge Codex Claude Cowork skill index project kit`
- Precision@5: 1.0
- Recall@5: 0.4545
- MRR: 1.0
- nDCG@5: 1.0
- Project coverage: 1.0
- Latency: 0.393 ms
- Top hits:
  - `mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime` (retrieval-fixture, score=207.845825)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=33.015527)
  - `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` (retrieval-reference, score=29.788804)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:pattern:cross-project-parallel` (retrieval-fixture, score=28.731069)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety` (retrieval-fixture, score=14.840396)

### markdown-source-of-truth

- Query: `Markdown source of truth adapters vector database dashboard MCP canonical memory retrieval`
- Precision@5: 1.0
- Recall@5: 0.4545
- MRR: 1.0
- nDCG@5: 1.0
- Project coverage: 1.0
- Latency: 0.408 ms
- Top hits:
  - `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` (retrieval-reference, score=173.709225)
  - `mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime` (retrieval-fixture, score=41.62425)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=37.741275)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:compiled:promotion-audit` (retrieval-fixture, score=24.373675)
  - `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` (retrieval-reference, score=19.81105)

### privacy-export-gate

- Query: `shared retrieval export privacy gate confidential data sanitization approved raw sessions rejected`
- Precision@5: 0.8
- Recall@5: 0.8
- MRR: 1.0
- nDCG@5: 0.9829
- Project coverage: 1.0
- Latency: 0.394 ms
- Top hits:
  - `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` (retrieval-reference, score=228.844825)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety` (retrieval-fixture, score=76.665325)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=61.0995)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:pattern:cross-project-parallel` (retrieval-fixture, score=11.395542)
  - `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` (retrieval-reference, score=4.558217)

### promotion-audit

- Query: `promotion audit source hash review approval target policy manifest evidence durable memory`
- Precision@5: 0.8
- Recall@5: 0.8
- MRR: 1.0
- nDCG@5: 0.9829
- Project coverage: 1.0
- Latency: 0.388 ms
- Top hits:
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:compiled:promotion-audit` (retrieval-fixture, score=322.897575)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=44.496375)
  - `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` (retrieval-reference, score=24.876225)
  - `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` (retrieval-reference, score=19.665)
  - `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` (retrieval-reference, score=17.966162)

### stale-conflict-review

- Query: `stale memory conflict contradiction review supersession stale_after valid_until warnings`
- Precision@5: 0.8
- Recall@5: 0.8
- MRR: 1.0
- nDCG@5: 1.0
- Project coverage: 1.0
- Latency: 0.374 ms
- Top hits:
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:stale-research-signal` (retrieval-fixture, score=91.7378)
  - `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` (retrieval-reference, score=54.0)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=40.6318)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:compiled:promotion-audit` (retrieval-fixture, score=24.876225)
  - `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` (retrieval-reference, score=14.5475)

### cross-project-parallels

- Query: `cross project parallel discovery recurring patterns typed edges stable memory ids shared lessons`
- Precision@5: 0.8
- Recall@5: 0.8
- MRR: 1.0
- nDCG@5: 0.9558
- Project coverage: 1.0
- Latency: 0.381 ms
- Top hits:
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:pattern:cross-project-parallel` (retrieval-fixture, score=253.877229)
  - `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` (retrieval-reference, score=52.773854)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=40.345229)
  - `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` (retrieval-reference, score=27.05689)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety` (retrieval-fixture, score=14.692975)

### progressive-disclosure-skillset

- Query: `progressive disclosure skill index detailed Markdown procedures task description matches runtime bridge`
- Precision@5: 0.6
- Recall@5: 0.6
- MRR: 1.0
- nDCG@5: 1.0
- Project coverage: 1.0
- Latency: 0.455 ms
- Top hits:
  - `mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime` (retrieval-fixture, score=191.113037)
  - `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` (retrieval-reference, score=29.820267)
  - `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` (retrieval-fixture, score=27.13425)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety` (retrieval-fixture, score=14.962842)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=12.607833)

### freshness-warnings

- Query: `freshness warnings stale research valid until dates stale_after review cycle without deleting memory`
- Precision@5: 0.8
- Recall@5: 0.8
- MRR: 1.0
- nDCG@5: 1.0
- Project coverage: 1.0
- Latency: 0.421 ms
- Top hits:
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:stale-research-signal` (retrieval-fixture, score=225.029877)
  - `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` (retrieval-reference, score=40.076538)
  - `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` (retrieval-fixture, score=27.080731)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:compiled:promotion-audit` (retrieval-fixture, score=23.600521)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:context-pack-objective` (retrieval-fixture, score=23.018621)

### generated-views-boundary

- Query: `generated indexes exports dashboards reports rebuildable views not canonical memory source truth`
- Precision@5: 0.6
- Recall@5: 0.6
- MRR: 1.0
- nDCG@5: 0.8529
- Project coverage: 1.0
- Latency: 0.389 ms
- Top hits:
  - `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` (retrieval-reference, score=78.5565)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:compiled:promotion-audit` (retrieval-fixture, score=23.954883)
  - `mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime` (retrieval-fixture, score=19.047737)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety` (retrieval-fixture, score=18.91175)
  - `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` (retrieval-reference, score=17.966162)

### runtime-rag-safety

- Query: `runtime events raw sessions private summarized before shared RAG reviewed sanitized promotion`
- Precision@5: 0.8
- Recall@5: 0.8
- MRR: 1.0
- nDCG@5: 1.0
- Project coverage: 1.0
- Latency: 0.381 ms
- Top hits:
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety` (retrieval-fixture, score=210.390775)
  - `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` (retrieval-reference, score=99.7395)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=56.378175)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:compiled:promotion-audit` (retrieval-fixture, score=21.2106)
  - `mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime` (retrieval-fixture, score=19.70985)

### context-budget-exclusions

- Query: `context budget excluded sources included sources dropped records task objective scoring`
- Precision@5: 0.8
- Recall@5: 0.8
- MRR: 1.0
- nDCG@5: 0.9829
- Project coverage: 1.0
- Latency: 0.381 ms
- Top hits:
  - `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` (retrieval-fixture, score=147.910125)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:context-pack-objective` (retrieval-fixture, score=85.925125)
  - `mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime` (retrieval-fixture, score=5.819)
  - `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` (retrieval-reference, score=5.175)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=1.1638)

### red-team-quality-loop

- Query: `red team scorecard QA review evidence metrics promote candidate safety privacy quality ratchet`
- Precision@5: 0.6
- Recall@5: 0.6
- MRR: 1.0
- nDCG@5: 0.9675
- Project coverage: 1.0
- Latency: 0.382 ms
- Top hits:
  - `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` (retrieval-reference, score=32.250688)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:compiled:promotion-audit` (retrieval-fixture, score=23.600521)
  - `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` (retrieval-reference, score=14.985385)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=13.825477)
  - `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` (retrieval-fixture, score=7.452796)

### add-on-boundary

- Query: `optional add ons proof QA distribution generated artifacts no default dependency no hosted service`
- Precision@5: 0.0
- Recall@5: 0.0
- MRR: 0.0
- nDCG@5: 0.0
- Project coverage: 1.0
- Latency: 0.371 ms
- Top hits:
  - `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` (retrieval-fixture, score=5.651144)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety` (retrieval-fixture, score=4.520915)
  - `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` (retrieval-reference, score=4.467308)

### knowledgebase-ingestion

- Query: `existing Markdown Obsidian knowledgebase metadata first scan no wiki link rewrite no body copy`
- Precision@5: 0.8
- Recall@5: 0.8
- MRR: 1.0
- nDCG@5: 0.9047
- Project coverage: 1.0
- Latency: 0.37 ms
- Top hits:
  - `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` (retrieval-reference, score=19.950996)
  - `mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime` (retrieval-fixture, score=12.421327)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=7.452796)
  - `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` (retrieval-fixture, score=4.520915)
  - `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` (retrieval-reference, score=4.520915)

### typescript-eval-adapter

- Query: `TypeScript Node adapter validation frontmatter schema lint CI optional no second memory engine`
- Precision@5: 0.8
- Recall@5: 0.8
- MRR: 1.0
- nDCG@5: 0.9829
- Project coverage: 1.0
- Latency: 0.372 ms
- Top hits:
  - `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` (retrieval-reference, score=22.358388)
  - `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` (retrieval-fixture, score=9.336673)
  - `mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime` (retrieval-fixture, score=8.4249)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:canonical:stale-research-signal` (retrieval-fixture, score=6.781373)
  - `mem:tenant-fixture:customer-fixture:retrieval-fixture:compiled:promotion-audit` (retrieval-fixture, score=6.781373)

## Top Cross-Project Parallels

- `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` <-> `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` via {'concept_tags': ['agent-memory', 'production-ready', 'retrieval-calibration'], 'stack_tags': ['markdown'], 'architecture_patterns': ['markdown-source-of-truth', 'project-folder-only'], 'semantic_tokens': ['are', 'export', 'memory', 'privacy', 'private', 'raw', 'retrieval', 'review', 'sessions', 'shared']}
- `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` <-> `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` via {'concept_tags': ['agent-memory', 'production-ready', 'retrieval-calibration'], 'stack_tags': ['markdown'], 'problem_patterns': ['contradictory-memory', 'stale-memory'], 'architecture_patterns': ['markdown-source-of-truth', 'project-folder-only'], 'failure_modes': ['unreviewed-shared-memory'], 'semantic_tokens': ['conflict', 'edges', 'lifecycle', 'memory', 'policy', 'review']}
- `mem:fixture:demo:retrieval-fixture:canonical:memory-lifecycle-policy` <-> `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` via {'concept_tags': ['agent-memory', 'production-ready', 'retrieval-calibration'], 'stack_tags': ['markdown'], 'problem_patterns': ['contradictory-memory'], 'architecture_patterns': ['markdown-source-of-truth'], 'semantic_tokens': ['are', 'edges', 'memory', 'project', 'retrieval', 'runtime', 'treat']}
- `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` <-> `mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime` via {'concept_tags': ['agent-memory', 'production-ready', 'retrieval-calibration'], 'architecture_patterns': ['markdown-source-of-truth'], 'semantic_tokens': ['adapters', 'are', 'canonical', 'markdown', 'memory', 'not', 'runtime']}
- `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` <-> `mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety` via {'semantic_tokens': ['are', 'evidence', 'exports', 'must', 'not', 'private', 'rag', 'raw', 'retrieval', 'sessions', 'shared']}
- `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` <-> `mem:fixture:demo:retrieval-reference:compiled:stale-conflict-review` via {'concept_tags': ['agent-memory', 'production-ready', 'retrieval-calibration'], 'stack_tags': ['markdown'], 'problem_patterns': ['stale-memory'], 'architecture_patterns': ['project-folder-only'], 'semantic_tokens': ['context', 'edge', 'instead', 'memory']}
- `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` <-> `mem:fixture:demo:retrieval-fixture:pattern:progressive-disclosure-runtime` via {'concept_tags': ['agent-memory', 'production-ready', 'retrieval-calibration'], 'architecture_patterns': ['markdown-source-of-truth'], 'semantic_tokens': ['are', 'memory', 'not']}
- `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` <-> `mem:shared:shared:retrieval-reference:lesson:privacy-export-gate` via {'concept_tags': ['agent-memory', 'production-ready', 'retrieval-calibration'], 'stack_tags': ['markdown'], 'architecture_patterns': ['project-folder-only']}
- `mem:fixture:demo:retrieval-fixture:compiled:context-pack-scoring` <-> `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` via {'concept_tags': ['agent-memory', 'production-ready', 'retrieval-calibration'], 'stack_tags': ['markdown']}
- `mem:fixture:demo:retrieval-reference:adr:markdown-source-of-truth` <-> `mem:tenant-fixture:customer-fixture:retrieval-fixture:lesson:runtime-rag-safety` via {'semantic_tokens': ['are', 'not', 'retrieval', 'runtime']}
