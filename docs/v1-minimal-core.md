# Owledge V1 Minimal Core candidate

This page describes the bounded V1 product candidate on the current local
release branch. It is not an announcement that a package has been published.

## Shipped Core boundary

Owledge V1 is a local, Markdown-first Core with these deliberately small
surfaces:

- a zero-install Principles path and a minimal project install;
- exactly eight public CLI operations: `init`, `doctor`, `recall`, `context`,
  `propose`, `review`, `sync`, and `upgrade`;
- two local scopes only: `project_user` and explicitly linked `user_global`;
- local Candidate, park/resurface, reviewed-promotion, tombstone, and health
  contracts; and
- thin Codex, Claude Code, and generic MCP/CLI bridges over the same local
  Core. The generic bridge exposes exactly five MCP tools and allows only the
  explicit private Candidate write.

The normal path is local and offline. Project Markdown remains canonical;
indexes are rebuildable. Retrieved Markdown is display-only untrusted content,
never an instruction to execute automatically.

## First local journey

Start with Principles when you only need operating rules. For a local Core
project, initialize a minimal project first, then explicitly opt into a local
user-global directory when cross-project reviewed reuse is useful:

```bash
owledge init --target /path/to/project --profile minimal
owledge init --target /path/to/project --profile full --link-global /absolute/local/owledge-null-space
owledge doctor --project-root /path/to/project
```

`--link-global` requires an absolute local directory. Network paths, implicit
environment/home discovery, unlinked projects, enterprise scope, and remote
sync are denied. Ordinary recall excludes raw, Candidate, and parked records;
planning-purpose recall can show a relevant parked essence together with its
reason and reconsideration trigger.

## Evidence and support boundary

The candidate has controlled Windows evidence for the local install, upgrade,
recovery, privacy/security, lifecycle, and three-adapter journey. It does not
claim marketplace certification, hosted service, remote synchronization, or
macOS/Linux support. Executed macOS/Linux wheel-only proof is required before
any publication decision.

The following products are explicitly post-V1 or outside the V1 default path:
Single-Organization Hub, Pi adapter, LightRAG, Documentation Compiler,
supply-chain extensions, enterprise policy/authentication, remote sync, and
generic JSONL export. They remain in the maintained parking register rather
than silently becoming candidate requirements.

For the exact capability inventory, see the
[public capability registry](../contracts/public-capabilities.json) and the
[harness boundary](harness-plugin-matrix.md). For existing project upgrades,
read [Upgrading](upgrading.md).
