# What is Owledge?

Owledge is an **Agentic Engineering Context & Planning Layer**. It helps a person and their agents turn transient work into durable, reviewable Markdown: project decisions, scoped plans, evidence, and handoffs.

## When it helps

Use Owledge when an agent must continue work across sessions, a plan needs evidence and a clear stop point, or an existing repository or vault needs an additive memory layer. Start with principles-only when durable files are not yet needed; add the project-local kit only when the work benefits from local validation and handoffs.

## How it works

```text
intent -> project truth -> scoped context -> agent work -> evidence and handoff -> reviewed promotion
```

1. A person sets the intent and the permitted scope.
2. Canonical Markdown records the project truth and a bounded plan.
3. An agent receives scoped context, performs the work, and records evidence.
4. The next agent can resume from the handoff; promotion into canonical truth remains reviewed.

Markdown is canonical. Indexes, reports, graphs, benchmarks, and runtime adapters are generated or optional views. Raw runtime capture is private by default; do not treat generated views as authority over reviewed project records.

For the operational lifecycle, actor authority, privacy boundary, and daily
workflow, see [How Owledge works](how-owledge-works.md).

## Benefits and boundaries

| Owledge provides | Owledge does not provide |
| --- | --- |
| Additive, inspectable project memory | A hosted Team Hub or remote synchronization service |
| Evidence-linked plans and explicit handoffs | An autonomous background scheduler |
| Optional local tools, skills, adapters, and add-ons | Automatic promotion of agent output into project truth |
| A local experimental HTTP adapter for bounded experiments | A production remote authorization or multi-tenant boundary |

The local HTTP control-plane adapter is **local experimental**, source-checkout only, and loopback-only. Its public boundary and evidence are documented in [Local HTTP control plane](security/local-http-control-plane.md). A future multi-tenant Team Hub is **post-v1**; it is not a current product capability.

## Capability maturity

Every public capability is labelled as one of: **available**, **local experimental**, **preview**, **planned**, or **post-v1**. The versioned [public capability registry](../contracts/public-capabilities.json) names the evidence, documentation, release owner, and source/retrieval date for each feature-level public capability claim. Roadmap statements are explicitly labelled.

## Choose the smallest next step

- Keep an existing system and use the rules: [Integration Decision Guide](integration-decision-guide.md).
- Create a local project memory layer: [Project quickstart](quickstart.md).
- Try a bounded proof: [Try Owledge in 5 minutes](try-owledge-in-5-minutes.md).
- Compare routes and limits: [Documentation home](README.md).
