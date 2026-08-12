---
memory_id: "mem:owledge:global:owledge:research:v1-architecture-primary-sources-2026-08-11"
tenant_id: "owledge"
customer_id: "global"
project_id: "owledge"
doc_type: "research"
status: "active"
visibility: "private"
data_class: "internal"
semantic_title: "Owledge V1 Architecture Research Against Current Primary Sources"
summary: "Primary-source research on MCP security, packaging language choices, LangGraph integration, EU privacy and AI governance, tracing boundaries, provider policy, and multi-model evaluation for the Owledge V1 sparring session."
concept_tags:
  - "mcp-security"
  - "enterprise-architecture"
  - "agent-observability"
  - "evaluation"
stack_tags:
  - "python"
  - "mcp"
  - "langgraph"
problem_patterns:
  - "runtime telemetry confused with durable knowledge"
  - "remote agent access without resource-bound authorization"
  - "framework state becoming canonical memory"
architecture_patterns:
  - "transport-neutral capability kernel"
  - "markdown canonical derived views disposable"
  - "policy-gated provider adapters"
failure_modes:
  - "token passthrough"
  - "cross-tenant retrieval"
  - "unbounded content logging"
  - "uncalibrated single-model judge"
reusable_lessons:
  - "Keep the Python core and expose framework-neutral seams before considering a rewrite."
  - "Separate traces, audit receipts, episodic candidates, and canonical knowledge."
confidence: 0.92
review_status: "unreviewed"
sanitization_status: "not_required"
created_at: "2026-08-11T18:58:32Z"
updated_at: "2026-08-11T18:58:32Z"
retention_class: "standard"
stale_after: "2026-11-11T00:00:00Z"
expires_at: ""
last_reviewed_at: ""
review_cycle: "quarterly"
source_url: "https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization"
source_date: "2025-11-25"
retrieved_at: "2026-08-11T18:58:32Z"
valid_until: "2026-11-11T00:00:00Z"
version_context: "Current official sources retrieved 2026-08-11; MCP specification 2025-11-25; EU law consolidated through Regulation (EU) 2026/1744."
source_hash: ""
edges: []
---

# Owledge V1 Architecture: Current Primary-Source Research

Stand: 11. August 2026. This note supports architecture sparring; the EU section is not legal advice. Role, risk, transfer, and retention assessments remain deployment-specific.

## Executive verdict

The primary sources support a small Python standalone core, a separate hosted Hub/governance layer, and MCP as a transport adapter. They do **not** support a V1 rewrite in TypeScript or Rust, LangGraph as canonical memory, full prompt/response logging, automatic knowledge promotion, or a multi-LLM council in the request path.

The most valuable V1 work is therefore structural: stable capability contracts, resource-bound authorization, tenant isolation before retrieval, provenance/effect receipts, append/propose/promote separation, provider policy manifests, minimal audit events, and deterministic retrieval/evaluation gates.

## 1. MCP authorization and server security

### Primary-source facts

- The current MCP authorization specification applies to HTTP transports. It uses OAuth discovery, Protected Resource Metadata, resource indicators, and audience-bound tokens. Clients must send the target `resource`; servers must validate that the token was issued for that MCP server. Least-privilege scopes and step-up authorization are explicit parts of the design. [MCP Authorization 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- MCP security guidance explicitly forbids token passthrough. A server calling a downstream API must use a separate downstream token, not forward the client token. Local servers should prefer `stdio`; local HTTP needs an authorization token or restricted IPC, sandboxing, and minimal filesystem/network privileges. [MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)
- Experimental MCP Tasks must be bound to the authorization context. Without identity binding, servers should not expose task listing and must use high-entropy IDs and short TTLs. [MCP Tasks 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks)

### Architecture inference for Owledge

Use two deployment profiles:

1. **Local:** `stdio`, project-root allowlist, inherited OS identity, no network listener by default.
2. **Hosted:** Streamable HTTP behind OAuth/OIDC; the Hub acts as MCP resource server, publishes RFC 9728 metadata, validates issuer/audience/expiry/scopes, and resolves tenant/project scope server-side.

Required V1 invariants:

- Never accept a remote `project_root` or arbitrary path.
- Enforce tenant/project/data-class before search, not by filtering returned hits.
- Separate scopes such as `memory:read`, `context:build`, `evidence:append`, `promotion:request`, `promotion:execute`, and `admin`.
- Bind jobs, continuation tokens, cache entries, and audit receipts to principal plus tenant plus project.
- Keep read-only MCP as the safe default. Writes must be explicit effects with idempotency and optimistic revision checks.

## 2. Python/uvx versus TypeScript or Rust

### Primary-source facts

- `uvx` runs Python tools in temporary isolated environments; `uv tool install` creates persistent isolated tools on `PATH`; exact versions and bounded version ranges are supported, and upgrades respect installed constraints. [uv Tools Guide](https://docs.astral.sh/uv/guides/tools/)
- Python packages declare portable CLI wrappers through `[project.scripts]`/`console_scripts`. [PyPA `pyproject.toml`](https://packaging.python.org/en/latest/specifications/pyproject-toml/) and [Entry Points specification](https://packaging.python.org/en/latest/specifications/entry-points/)
- `npm exec`/`npx` similarly runs package binaries, may fetch missing packages into the npm cache, and exposes install-script controls. [npm exec](https://docs.npmjs.com/cli/v11/commands/npm-exec/)
- `cargo install` builds and installs binary crates and presumes a Rust/Cargo toolchain. The Rust book states it is a convenience for Rust developers, not a system-package replacement. [Cargo install](https://doc.rust-lang.org/book/ch14-04-installing-binaries.html)

### Decision

Keep the core in Python through V1. `uvx owledge` is already a credible zero-/low-install adoption path, and the current implementation, tests, schemas, and Markdown toolchain are Python assets. A TypeScript rewrite would exchange working product depth for ecosystem familiarity; a Rust rewrite would improve startup/distribution potential only after paying the highest development and migration cost.

V1 should instead provide:

- a correct PyPI package with `owledge` console entry point;
- `uvx owledge@<version>` examples for reproducibility and `uv tool install` plus `uv tool upgrade` for persistent global installation;
- a versioned JSON/capability contract so TypeScript, Rust, Hermes, and other harnesses integrate without sharing implementation language;
- optional thin TS/Rust SDKs generated from schemas only after the protocol stabilizes.

Rust becomes justified post-V1 only for measured hotspots or a self-contained edge binary. TypeScript becomes justified for a web/control plane or native Node SDK, not as a prerequisite for MCP adoption.

## 3. LangChain/LangGraph seam

### Primary-source facts

- LangGraph distinguishes thread-scoped checkpoint state from cross-thread stores. [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) and [Stores](https://docs.langchain.com/oss/python/langgraph/stores)
- The official LangChain MCP adapters convert MCP tools into LangChain tools and can connect to multiple MCP servers. [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)

### Architecture inference

Owledge should integrate at the **tool/store boundary**, not become a LangGraph checkpointer or inherit LangGraph's memory model:

- LangGraph thread/checkpoint: transient orchestration state.
- LangGraph Store: optional application memory owned by that harness.
- Owledge: canonical project knowledge, provenance, decisions, evidence, review, and promotion.

Expose `memory.search`, `artifact.read`, `context.build`, `evidence.append`, and `promotion.request` through MCP. A LangGraph node calls these tools; it does not directly mutate Owledge Markdown or mirror the entire corpus into a LangGraph Store. This preserves framework neutrality and prevents two competing sources of truth.

## 4. Privacy, provider policy, and the EU AI Act

### Primary-source facts

- GDPR requires purpose limitation, data minimisation, storage limitation, privacy by design/default, processor contracts, processing records, security, and high-risk impact assessment. Roles are functional: controller determines purpose/essential means; processor acts on documented instructions. [GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04) and [EDPB Controller/Processor Guidelines 07/2020](https://www.edpb.europa.eu/documents/guideline/guidelines-072020-on-the-concepts-of-controller-and-processor-in-the-gdpr_en)
- The EU AI Act assigns duties according to role and intended purpose. Integrating an external GPAI model into a Librarian makes Owledge a downstream AI-system provider, not automatically the provider of the GPAI model. General project knowledge retrieval is not automatically high-risk; Annex III purposes such as recruitment, worker evaluation, credit, or access to essential services can change the classification. [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj?locale=en), [Commission GPAI Guidelines](https://digital-strategy.ec.europa.eu/en/policies/guidelines-gpai-providers), and [Regulation (EU) 2026/1744](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32026R1744)
- Provider settings differ by endpoint and feature. OpenAI documents endpoint-specific application-state retention and ZDR eligibility; Anthropic states commercial API/customer data is not used for training by default and approved enterprise API customers can obtain ZDR with feature caveats; Vertex AI states customer data is not used for training without permission and documents specific retention exceptions. [OpenAI Data Controls](https://platform.openai.com/docs/models/default-usage-policies-by-endpoint), [Anthropic Commercial Data Roles](https://support.anthropic.com/en/articles/9267385-does-anthropic-act-as-a-data-processor-or-controller), [Anthropic ZDR](https://privacy.anthropic.com/en/articles/8956058-i-have-a-zero-data-retention-agreement-with-anthropic-what-products-does-it-apply-to), and [Vertex AI ZDR](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/vertex-ai-zero-data-retention)

### V1 implications

- Treat the hosted Owledge service as processor for customer project content unless a reviewed data flow establishes another role; separate account/security analytics where Owledge may act for its own purposes.
- Maintain a provider manifest per model adapter: provider, model/version, region, training use, retention, ZDR eligibility, subprocessors, transfer mechanism, supported data classes, and prohibited features.
- Default to no cross-tenant learning, no provider training opt-in, no autonomous natural-person ranking, and no external side effect without human approval.
- Add tenant export/deletion, retention policies, incident workflow, DPA/subprocessor transparency, encrypted transport/storage, and redaction before provider calls.
- Keep core storage/search separable from model-backed Librarian features. AI-generated material remains labelled suggestion until reviewed.

Regulated high-risk profiles, FRIA/DPIA automation, sovereign deployments, CMK/BYOK, and sector-specific conformity packs are post-V1. They should not bloat the standalone core.

## 5. Tracing, audit, episodic capture, and knowledge logging

### Primary-source facts

- OpenTelemetry's GenAI conventions model spans, metrics, and events. Full prompts, outputs, tool arguments, and results are opt-in and explicitly warned as potentially sensitive. [OpenTelemetry GenAI Events](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-events.md)
- LangSmith traces group runs and can automatically capture inputs, outputs, and metadata; its hosted retention and tracing controls are distinct from application state, and tracing can be disabled or conditionally enabled. [LangSmith Observability Concepts](https://docs.langchain.com/langsmith/observability-concepts) and [Data Storage and Privacy](https://docs.langchain.com/langsmith/data-storage-and-privacy)

### Required four-way separation

| Stream | Purpose | Default content | Retention/promotion |
| --- | --- | --- | --- |
| Runtime trace | Debug latency, calls, retries, tokens | IDs, timings, model/tool names, errors; content opt-in/redacted | Short TTL; never auto-promote |
| Security audit | Accountability for effects | actor, tenant, capability, effect, target, result, timestamp, revision | Tamper-evident, policy retention; no raw prompt by default |
| Episodic candidate | Capture what happened and possible lessons | bounded summary plus explicit evidence refs | Private draft; review before promotion |
| Canonical knowledge | Stable project truth | reviewed decision/fact/procedure with provenance | Versioned lifecycle and supersession |

Therefore, a universal "log everything into Owledge" pipeline is unsafe. The session-summary skill may read a redacted trace and emit a candidate, but raw traces are evidence inputs, not memory.

## 6. Multi-LLM judges and evaluation

### Primary-source facts

- OpenAI's current evaluation guide recommends task-specific production-representative data, continuous evaluation, automated scoring where possible, and calibration against human feedback. It notes LLMs are more reliable at discrimination/pairwise comparison than open-ended judging. [OpenAI Evaluation Best Practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- MT-Bench found useful human agreement but documented position, verbosity, self-enhancement, and reasoning biases in LLM judges. [Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
- A panel of diverse, smaller model families reduced intra-model bias and cost relative to one large judge across the paper's evaluated settings. [Verga et al., 2024, PoLL](https://arxiv.org/abs/2404.18796)

### Owledge evaluation design

V1 order of precedence:

1. Deterministic validators for schemas, IDs, relations, scopes, provenance, graph traversal, and exact tool effects.
2. Retrieval gold sets: source expected, source forbidden, context precision/recall, contamination, tenant isolation, and budget adherence.
3. Human-curated rubrics for summary faithfulness, answer usefulness, uncertainty, and correct escalation.
4. One calibrated LLM judge only where deterministic grading is insufficient; blind candidate identity, randomize pair order, require cited rubric evidence, and record judge model/version/prompt/settings.
5. A cross-family panel only for release decisions or disputed subjective cases. Track disagreement rather than averaging it away, and send threshold/disagreement cases to a human.

Never let the candidate model be the sole judge of its own output. Do not place a multi-model jury in the normal Librarian request path: it raises cost, latency, privacy exposure, and provider dependence without improving deterministic knowledge integrity.

## V1 essentials versus post-V1

| Area | V1 essential | Post-V1 / optional |
| --- | --- | --- |
| Core/distribution | Python package, `uvx`/`uv tool`, stable schema/API, upgrade/rollback docs | Rust hotspot/binary; TS/Rust SDKs after contract stability |
| MCP | local stdio; hosted OAuth resource server; audience/scope validation; read-only default | dynamic capability marketplace; broad write surface |
| Hub | tenant/project registry, server-side routing, policy enforcement, receipts, export/delete | multi-region, sovereignty, CMK/BYOK, SCIM/SIEM |
| Librarian | search/context/answer with provenance; proposal-only learning; human confirmation | autonomous curation, daily automation, cross-project recommendations after evaluation |
| Frameworks | MCP/tool integration recipe for LangGraph and other harnesses | native framework adapters only when demand is measured |
| Logs | separated minimal trace/audit/candidate/canonical schemas | full observability backend, replay UI, long-term trace analytics |
| Providers | explicit registry and data-policy gates; local/BYO path | policy-aware multi-provider routing and private endpoints |
| Evaluation | deterministic gates, retrieval corpus, human-calibrated rubric judge | diverse judge panel for high-value release adjudication |
| Compliance | privacy/security baseline, role/data-flow inventory, DPA/subprocessors, AI disclosure | regulated deployment profiles and sector-specific conformity |

## Bottom line for the 18-question sparring

The central product seam is not "one Librarian agent that knows everything." It is a transport-neutral, policy-enforced knowledge capability layer whose canonical state remains inspectable and whose Librarian is one replaceable consumer/orchestrator. That architecture supports local standalone use, a central authenticated Hub, MCP access from many harnesses, and later Enterprise controls without forcing LangGraph, a vector database, a particular model provider, or a language rewrite into the core.
