# Choose an Owledge adoption preset

Choose the smallest local preset that proves the current need. Owledge does not
require a hosted account, remote synchronization, a vector database, or a
background worker. Every preset keeps reviewed project Markdown authoritative.

## Preset selector

| Preset | Choose it when | Maturity | Value | Authority and automation | Privacy | Prerequisites | Limits | Upgrade path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Principles-only | You need the operating rules in an existing agent workflow | Available | MVP cutline, plans, evidence, and handoffs without installation | Host instructions and owner workflow govern writes; no automatic promotion | Uses the host's existing privacy rules | An instruction-following agent | No local Owledge validation or generated indexes | Add a manual mini-kit or project-local kit |
| Manual mini-kit | You want a small, visible plan/checklist pair but not the full initializer | Available | Durable planning artifacts in the host's approved locations | Manual, owner-controlled; no hooks or scheduler | Keep host-private material out of shared artifacts | A chosen host planning directory | No generated CLI tooling or automatic discovery | Initialize the project-local kit when validation is needed |
| Existing repository kit | A coding repository needs durable project truth and local checks | Available | `OWLEDGE.md`, `.owledge/`, local tools, discoverable skills | CLI and skills are on-demand; promotion is reviewed workflow, not automation | Raw sessions are private by default | Local source checkout or package path | Local project boundary only | Add a KB module, runtime adapter, or optional add-on as needed |
| Standalone project folder | A new or portable project needs the kit without a full source repository | Available | Generated project folder with local tools and skills | Local and explicit; no hosted control plane | Private global layer remains opt-in | Build-project-kit output | No automatic central registry | Move/copy into a project, then add only required adapters |
| Markdown knowledge-base module | An existing Markdown/Obsidian vault must remain unchanged | Available | Additive module or mapped indexes | Module writes are bounded to Owledge-owned/mapped folders | Source notes remain local; metadata-first scanning | Existing vault and optional `owledge-map.json` | No vault migration or wiki-link rewrite | Use project kit only for a separate coding project |
| Local runtime adapter | A compatible runtime needs optional private event capture | Available local adapter | Local hooks, session drafts, and runtime smoke checks | Hooks are optional and fail-soft; they do not promote truth | Raw captures stay private candidates | Explicit plugin installation and compatible local runtime | Not marketplace certification or remote service | Keep the same local Markdown source; remove the adapter when unneeded |
| Private global layer | One person wants optional private context across local projects | Preview, opt-in | Private preferences, goals, and ideas can inform planning | Explicit local linkage; no automatic project override or promotion | `USER_CONTEXT.md` and `global-memory/` are private by default | Explicit private global vault/link | Not team synchronization or shared RAG by default | Keep private/local or later adopt reviewed cross-project tooling |
| Cross-project power-user hub | You need a local map of reviewed lessons across projects | Available optional add-on | Central local map of reviewed, sanitized project learnings | Explicit add-on commands; no central overwrite or automatic import | Reviewed/sanitized records only; no raw sessions | Source checkout and `cross-project-hub-kit` | Not Owlib, not remote sync, not a Team Hub | Evaluate Owlib compatibility only after `G-071-C-COMPAT` |

## Capability boundaries that must not be conflated

| Name | Current maturity | What it is today | What it is not |
| --- | --- | --- | --- |
| `global-memory` / private global layer | Preview, opt-in | Private user-level local context | A shared organization memory, automatic project sync, or project authority |
| Cross-Project Hub Kit | Available optional add-on | Local map built from reviewed and sanitized project records | Owlib, hosted remote synchronization, or a multi-tenant Team Hub |
| Owlib | Preview / legacy compatibility | A separate, evolving local library direction for reviewed cross-project learning and PI work | A currently supported host layout or an automatic global install; `G-071-C-COMPAT` has not accepted compatibility |
| Local HTTP control-plane adapter | Local experimental | Bounded loopback-only source-checkout experiments | A production remote server, Team Hub, or enterprise authorization boundary |
| Read-only MCP | Available local adapter | Explicit local project reads | Write-enabled MCP, remote MCP service, promotion API, or sync layer |
| Team Hub | Post-v1 | Future multi-tenant collaboration direction | A current capability or v1 dependency |
| Git/CI Sync Layer | Post-v1 | Future synchronization direction | A current remote-sync path |

## Decision examples

| Need | Select | Do not select merely because it sounds larger |
| --- | --- | --- |
| "Keep a feature request focused and preserve future ideas" | Principles-only with `owledge-contract` | Runtime adapter, Hub, or MCP |
| "Our application repository needs resumable evidence and validation" | Existing repository kit | A global layer or Team Hub |
| "Our Obsidian notes must not be reorganized" | Markdown knowledge-base module | Project-kit migration or a vector database |
| "I want private preferences to guide my own projects" | Private global layer after explicit opt-in | Cross-project hub or team synchronization |
| "We need reviewed lessons from several local projects" | Cross-Project Hub Kit | Owlib compatibility, remote HTTP, or Team Hub |
| "A client wants a remote shared service" | Record it as post-v1 Team Hub/Sync roadmap work | Local HTTP, MCP, Hub Kit, or global memory |

## Safe next actions

1. Start with [the integration decision guide](integration-decision-guide.md) if
   you only need an existing path selection.
2. Use [skills and agent integrations](skills-and-agent-integrations.md) when
   the decision includes a harness, skill, hook, or MCP adapter.
3. Use [the installation hub](install/README.md) only after selecting a preset.
4. Read [local HTTP control-plane boundaries](security/local-http-control-plane.md)
   before any HTTP experiment.

If no current preset meets the requirement, keep the request as a roadmap
candidate. Do not relabel a local adapter as hosted functionality to unblock a
decision.
