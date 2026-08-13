# Project-local kit recipes

Use these recipes for a coding project that needs a small durable-knowledge
entrypoint. The default `minimal` profile is additive: it does not change the
host framework, package manager, or existing source files.

## Package recipe

**Prerequisite:** `uv` can run the published `owledge` package. Work from any
directory and replace the target placeholder with an empty or existing project
directory.

```bash
uvx owledge quickstart --target /path/to/your-project
uvx owledge doctor --project-root /path/to/your-project
```

Expected output from the second command: JSON with `"passed": true`. The first
command adds missing project-local kit files; a rerun skips existing files
rather than overwriting them. This package path does **not** provide source-only
add-ons, plugin bundles, or a persistent `owledge` executable.

## Source recipe

**Prerequisite:** a local Owledge checkout and Python 3.10+. From the
**Owledge checkout** (not from the target project), run:

```bash
python tools/owledge.py init-project --target /path/to/your-project
python tools/owledge.py doctor --project-root /path/to/your-project
```

The default creates only `OWLEDGE.md`, `.owledge/config.yaml`, and an install
manifest. Schemas remain package resources; skills, local tool copies and
adapter bundles remain out of the default footprint. The expected doctor output
is `"passed": true`. Rerunning `init-project` is additive and skips existing
files.

### Explicit full compatibility profile

Use the existing larger local-tools and discoverable-skills kit only when a
project needs those compatibility surfaces or a source-only add-on:

```bash
python tools/owledge.py init-project --target /path/to/your-project --profile full
```

### Private local user-global Null-Space

Link a project only when you explicitly choose a local directory that you own:

```bash
python tools/owledge.py init --target /path/to/your-project --link-global /path/to/your-null-space --owner-id local-owner
```

`--link-global` always requires that explicit absolute path; Owledge never
discovers a Null-Space from an environment variable, home-directory default, or
network location.

Owledge records that project in an owner-controlled local allowlist. The link
permits only `project_user` and `user_global`; networking, remote sync,
enterprise scope and automatic discovery are denied. Reviewed private Markdown
under the Null-Space can be scanned directly; any generated index remains a
rebuildable local projection.

### Source-only optional add-ons

Add-ons require that same source checkout. They are not part of the package
recipe:

```bash
python tools/owledge.py install-addon --project-root /path/to/your-project --addon launch-demo-kit
python tools/owledge.py doctor --project-root /path/to/your-project
```

Use only the add-on needed for the current proof or workflow. Add-ons are
optional and do not replace canonical Markdown memory.

## What both recipes create

The default minimal profile creates a project router and config only. The
explicit `full` profile may also create the larger compatibility kit, local
tools, source skills and discoverable `.agents/skills/` mirrors. Requesting a
plugin or compliance add-on also selects that explicit compatibility surface.

## Upgrade, recovery, and uninstall

Use [Upgrading Owledge](../upgrading.md) for an installed kit: `safe` preserves
user-edited files, `manual` emits a reviewable patch, and `force-templates`
requires explicit confirmation. If a recipe fails, keep the JSON output, verify
the checkout and target roots, and rerun `doctor` before retrying.

To retire the kit, first preserve any project-owned canonical records. Then
review and remove only Owledge-owned `tools/`, `skills/`, `.agents/skills/`, and
generated `.owledge/` views as appropriate. Do not remove canonical
`.owledge/decisions`, `plans`, `evidence`, or `handoffs` as an uninstall step.
