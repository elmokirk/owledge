# Compliance Roadmap

Date: 2026-05-16  
Status: optional compliance roadmap/reference baseline  
Scope: Germany/EU projects using the Agent Memory Kit, agent runtimes, project knowledgebases, RAG exports, MCP adapters, and external agent access.

This roadmap is not legal advice and does not replace counsel review. It describes optional engineering and governance controls that deployments should consider before making compliance, regulated-production, agency, or enterprise claims in Germany/EU. The default Agent Memory Kit remains a lean project-memory kit; Compliance Light is opt-in support, not certification.

## Research Baseline

This roadmap was strengthened against the following current primary or official sources:

| Area | Source | Compliance Signal |
| --- | --- | --- |
| GDPR/DSGVO | [Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng) | Controller/processor duties, DPIA, records of processing, data subject rights, breach notification, transfers |
| Germany BDSG | [Bundesdatenschutzgesetz](https://www.gesetze-im-internet.de/bdsg_2018/) | German national GDPR supplements, employee data and supervisory context |
| German AI + privacy guidance | [BfDI AI information and checklist](https://www.bfdi.bund.de/EN/Fachthemen/Inhalte/Technologie/KuenstlicheIntelligenz.html) and [DSK AI guidance](https://www.datenschutzkonferenz-online.de/orientierungshilfen.html) | AI use still requires lawful basis, purpose limitation, transparency, DPIA assessment, provider and processing-role clarity |
| EU AI Act | [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng) and [European Commission AI Act page](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) | AI literacy, prohibited practices, GPAI/provider obligations, high-risk system duties, transparency and governance timeline |
| NIS2/BSI | [BSI NIS2 information](https://mip2.bsi.bund.de/en/info-nis2-registrierung/) | Registration and incident reporting obligations for covered entities after German implementation; security governance baseline for enterprise customers |
| TDDDG/ePrivacy | [TDDDG](https://www.gesetze-im-internet.de/ttdsg/) | Device access, telemetry, cookies, local browser/plugin storage and communication privacy triggers |
| Data Act | [Regulation (EU) 2023/2854](https://eur-lex.europa.eu/eli/reg/2023/2854/oj/eng) | Data access, portability, cloud switching and contractual fairness triggers for data services |
| Cyber Resilience Act | [Regulation (EU) 2024/2847](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng) | Vulnerability handling, secure-by-design and supply-chain evidence for products with digital elements |
| Security baseline | [BSI IT-Grundschutz](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/IT-Grundschutz/it-grundschutz_node.html) and [BSI C5](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/Cloud-Computing/Anforderungskatalog-C5/anforderungskatalog-c5_node.html) | German security control references for professional and cloud deployments |

## Current Timing Notes

| Regulation | Current Timing For Planning |
| --- | --- |
| GDPR/DSGVO | Fully applicable; treat every personal-data workflow as live compliance scope |
| EU AI Act | Entered into force on 2024-08-01; prohibited practices and AI literacy apply since 2025-02-02; GPAI governance/provider obligations apply from 2025-08-02; most rules apply from 2026-08-02; some high-risk product obligations run to 2027 and must be watched for Omnibus/standards changes |
| NIS2 Germany | BSI states that registration and reporting duties under the German NIS2 implementation apply from 2025-12-06 for covered entities |
| Data Act | Core data access and switching duties are planning-relevant for data services since 2025-09-12 |
| Cyber Resilience Act | Product/security-by-design obligations phase in through 2026-2027; treat supply-chain evidence and vulnerability handling as immediate preparation tasks |
| TDDDG/ePrivacy | Device access, cookies, telemetry and plugin/browser storage checks are already current German compliance triggers |

## Critical Findings

The previous roadmap correctly identified the major directions, but it was too weak for production claims:

| Finding | Impact | Required Correction |
| --- | --- | --- |
| Data classification existed, but no processing inventory | GDPR accountability cannot be shown | Add records of processing, purpose, legal basis, role, recipient, transfer and retention metadata |
| Sanitization existed, but no rights workflow | DSAR/delete/export requests cannot be fulfilled reliably | Add subject access, deletion, rectification, portability, objection and restriction workflows |
| Raw event exclusion existed, but no retention policy | Private logs can accumulate beyond purpose | Add retention defaults, purge, anonymization and legal-hold handling |
| No DPIA/DSFA workflow | AI/RAG and agent telemetry can be high risk under GDPR | Add DPIA triggers, templates, approvals and residual-risk sign-off |
| AI Act treated as future-only | AI literacy and prohibited practices already matter | Add AI inventory, risk classification, AI literacy evidence and prohibited-use gates |
| No provider/model registry | LLM processing roles, locations and sub-processors remain unclear | Add model/provider registry, DPA/SCC/TIA fields, data-use controls and fallback policy |
| No incident workflow | GDPR/NIS2/security reporting cannot be evidenced | Add incident severity, timelines, notification evidence and postmortem artifacts |
| No RBAC or tenant isolation implementation | Multi-customer agency use is unsafe | Add access model, tenant/customer/project scoping, audit logs and export scopes |
| No secure MCP baseline | External agents/VPS access could leak memory | Add scoped MCP resources, OAuth/token auth, read-only defaults and append-only writes |
| No compliance acceptance tests | Claims cannot be regression-tested | Add compliance doctor, schema validation, export safety and fixture tests |

## Applicability Model

The system must not assume every deployment has the same legal duties. It must classify each deployment using trigger questions.

| Trigger | If Yes |
| --- | --- |
| Personal data is stored, summarized, embedded or exported | GDPR/BDSG controls apply |
| Employee, applicant, customer or user behavior is logged | DPIA/DSFA trigger assessment required |
| Special-category data, credentials, secrets or customer confidential data may appear | Stricter classification, redaction, access control and review required |
| Agent outputs affect people, eligibility, employment, credit, education, health, safety or legal positions | AI Act high-risk/prohibited-practice analysis required |
| The system is offered to customers as a service | Processor/controller role matrix, DPA, sub-processor registry, audit evidence and security baseline required |
| The customer is critical infrastructure, essential/important entity, finance, health, public sector or regulated industry | NIS2/DORA/sector-specific controls may apply |
| The product includes packaged software, agent plugins, downloadable clients or networked product features | CRA/supply-chain vulnerability handling may apply |
| Browser/device storage, telemetry or plugin hooks are used | TDDDG/ePrivacy consent and transparency checks may apply |
| Data moves outside the EEA or to non-EU providers | Transfer mechanism, SCC/DPF/TIA and provider controls required |

## Target State

The future target state for optional compliance support is:

```text
Markdown remains canonical.
Compliance metadata is first-class frontmatter.
Raw runtime capture is private, minimized and retention-bound.
Shared exports contain only reviewed, approved and sanitized knowledge.
AI/provider usage is inventoried, scoped and risk-classified.
External agents access only scoped resources through auditable adapters.
Every compliance-relevant action leaves evidence.
```

## Control Domains

### 1. Governance And Accountability

| Control | Target |
| --- | --- |
| Processing inventory | Every project has a records-of-processing artifact with purposes, legal basis, categories, recipients, transfers and retention |
| Role matrix | Controller, processor, joint-controller and sub-processor roles are explicit per deployment |
| Ownership | Tenant, customer, project, data owner and technical owner are required |
| Policy pack | Privacy, security, AI usage, retention, incident and vendor policies are versioned |
| Audit evidence | Promotions, exports, access, deletes, incidents and AI/provider changes produce append-only evidence |

### 2. Data Protection By Design

| Control | Target |
| --- | --- |
| Data minimization | Default context packs exclude raw logs, long transcripts and unrelated personal data |
| Classification | `data_class`, `visibility`, `review_status`, `sanitization_status`, and sensitivity flags gate every export |
| Redaction | Secrets, tokens, emails, phone numbers and likely personal data are detected before shared export |
| DPIA/DSFA | Trigger-based assessment for agent telemetry, RAG, profiling, sensitive projects and external agent access |
| Data subject rights | Export, delete, rectify, restrict and objection workflows work against canonical memory and generated indexes |
| Retention | Raw sessions, evidence, exports and reports have retention classes and purge/anonymize tooling |

### 3. AI Act Readiness

| Control | Target |
| --- | --- |
| AI system inventory | Every agent workflow records purpose, model/provider, human owner, input/output data, autonomy level and affected users |
| Risk classification | Prohibited, high-risk, limited-risk, GPAI-dependent and minimal-risk classifications are documented |
| AI literacy | Operators and reviewers have documented training/checklists for safe system use |
| Human oversight | High-impact outputs require review gates and cannot auto-promote into canonical/shared memory |
| Transparency | AI-generated artifacts are labeled internally; customer-facing reports disclose AI-assisted generation where required |
| GPAI/provider evidence | Provider terms, data-use policy, model version, logging behavior and EU availability are captured |
| Monitoring | Failure modes, incidents, drift, recurring errors and hallucination risks are tracked as memory artifacts |

### 4. Security, NIS2 And Supply Chain

| Control | Target |
| --- | --- |
| Security baseline | BSI IT-Grundschutz/C5-inspired controls mapped for local, cloud and enterprise hub deployments |
| Access control | Role-based and tenant-scoped access for enterprise hub, exports, reports and MCP adapters |
| Incident response | GDPR breach clock and NIS2-style early warning/notification/final report fields are available for covered customers |
| Secrets management | No provider keys in memory files; local secrets are referenced by name and stored outside Git |
| Supply chain | Dependency inventory, vulnerability handling, plugin provenance and release evidence are maintained |
| Secure MCP | stdio for local-only use; HTTP requires auth, scoped resources, URI validation, rate limits and audit logs |

### 5. Cross-Project Knowledge And Shared Vault

| Control | Target |
| --- | --- |
| Canonical boundary | Project-local Markdown remains source of truth; global vault is reviewed aggregation only |
| Shared promotion | Shared lessons require `visibility=shared`, `review_status=approved`, `sanitization_status=approved` and promotion evidence |
| Tenant isolation | Tenant/customer/project IDs are mandatory for exports, reports and enterprise hub scanning |
| Conflict handling | Contradictions are linked with typed edges instead of overwritten |
| Research reuse | Research enters compiled/pattern/lesson artifacts only after source, date, license and review checks |

## Maturity Levels

| Level | Name | Meaning |
| --- | --- | --- |
| 0 | Prototype | Local memory works, no compliance claims |
| 1 | Controlled Local | Classification, validation, private raw logs and reviewed exports work |
| 2 | Agency Controls Track | DPIA triggers, retention, DSAR, incident, provider registry and sanitized customer reports work |
| 3 | Enterprise Controls Track | RBAC, tenant isolation, audit logs, vendor controls, secure MCP and security baseline evidence work |
| 4 | Regulated Controls Track | Sector-specific overlays, legal sign-off, penetration testing, DPA/SCC/TIA packs and external audit evidence exist |

Current system maturity: Level 1 with parts of Level 2.  
Future compliance-support target: Level 3 control coverage for general agency/SaaS use; Level 4 control coverage for regulated enterprise customers.

## Legal And Regulatory Watch

The roadmap remains future-safe by tracking obligations as controls, not one-off laws.

| Cadence | Watch Item | Owner Artifact |
| --- | --- | --- |
| Monthly | EU AI Act Commission guidance, harmonized standards, GPAI code updates, national authority assignments | `agent-memory/compliance/regulatory-watch.md` |
| Monthly | BfDI/DSK AI and GDPR guidance | `agent-memory/compliance/regulatory-watch.md` |
| Quarterly | BSI/NIS2 implementation, IT-Grundschutz/C5 changes and incident guidance | `agent-memory/compliance/security-baseline.md` |
| Quarterly | SCC/DPF transfer changes and provider terms | `agent-memory/compliance/provider-registry.md` |
| Release-based | New agent plugin, MCP adapter, model provider, export mode or external agent access | DPIA/AI risk trigger review |

## Definition Of Done

The roadmap is final for implementation when these statements are true:

| Statement | Status |
| --- | --- |
| The legal baseline covers Germany/EU data protection, AI, security, device/privacy and supply-chain triggers | Done |
| Known roadmap gaps are explicit and mapped to controls | Done |
| The roadmap distinguishes prototype, agency, enterprise and regulated maturity | Done |
| Future legal changes are handled through watch artifacts and trigger-based controls | Done |
| A separate implementation plan exists with phases, files, tooling and acceptance tests | Done once `docs/archive/compliance-implementation-plan.md` is present |

## Non-Negotiable Production Gates

No deployment may be described as compliance-ready unless all applicable gates pass:

1. `compliance-doctor` passes for the selected tenant/customer/project.
2. No shared export contains private, confidential, personal, unsanitized or unreviewed records.
3. Provider/model registry exists and includes processing role, region, data-use and retention fields.
4. DPIA/DSFA trigger assessment is completed for agent telemetry, RAG and external agent access.
5. Retention, delete/export, incident and access-control workflows are tested with fixtures.
6. MCP/external access is scoped, authenticated and audited.
7. Legal/owner sign-off is recorded for regulated or customer-facing deployments.
