# Project-local kit recipes

Use these recipes for a coding project that needs durable plans, evidence,
handoffs, and local validation. Both are additive: they do not change the host
framework, package manager, or existing source files.

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

The checkout root supplies templates and tools; `/path/to/your-project` is the
only host-project write target. The expected doctor output is `"passed": true`.
Rerunning `init-project` is additive and skips existing kit files.

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

The core kit may create the files and folders listed in the
[Installation Hub ownership table](README.md#footprint-and-ownership), including
canonical Markdown under `.owledge/`, local tools, source skills, and
discoverable `.agents/skills/` mirrors. The plugin adapter is absent unless you
explicitly use `--include-plugin-adapter` from a source checkout.

## Upgrade, recovery, and uninstall

Use [Upgrading Owledge](../upgrading.md) for an installed kit: `safe` preserves
user-edited files, `manual` emits a reviewable patch, and `force-templates`
requires explicit confirmation. If a recipe fails, keep the JSON output, verify
the checkout and target roots, and rerun `doctor` before retrying.

To retire the kit, first preserve any project-owned canonical records. Then
review and remove only Owledge-owned `tools/`, `skills/`, `.agents/skills/`, and
generated `.owledge/` views as appropriate. Do not remove canonical
`.owledge/decisions`, `plans`, `evidence`, or `handoffs` as an uninstall step.
