# Installation Hub

Choose one delivery path. Do not combine a package command with a source-only
add-on command unless the recipe explicitly says to use a source checkout.

| Goal | Canonical recipe | Writes to the host project | Boundary |
| --- | --- | --- | --- |
| Apply the operating rules only | [Principles-only](principles-only.md) | None | No local validation, indexes, or adapter. |
| Add durable project memory from the package | [Project package recipe](project.md#package-recipe) | Project-local files only | Core kit; no source-only add-ons. |
| Develop or use a source-only add-on | [Project source recipe](project.md#source-recipe) | Project-local files only | Checkout and target root are distinct. |
| Create an additive Markdown KB module | [KB integration guide](../agent-integration-guide.md) | `owledge-module/` by default | Existing notes stay unchanged. |
| Add an optional runtime adapter | [Plugin installation](../install-plugin.md) | Only when explicitly selected | Local adapter support, not marketplace certification. |

## Footprint and ownership

The package wheel for v0.7.0 is 289,991 bytes compressed. The source-project
recipe was measured on 2026-07-29 from a clean checkout: 184 files / 894,212
bytes in the host project; `.owledge/` accounts for 115 files / 83,798 bytes.
Exact totals change with release content and optional selections.

| Location | Owner | Meaning | Removal / rebuild |
| --- | --- | --- | --- |
| `OWLEDGE.md`, `AGENTS.md`, `CLAUDE.md`, `DESIGN.md` | Project | Canonical entrypoint and instructions | Review before removal; preserve local edits. |
| `.owledge/decisions`, `plans`, `evidence`, `handoffs` | Project | Canonical durable work | Never delete as routine uninstall or upgrade cleanup. |
| `.owledge/indexes`, `reports/generated`, `exports` | Generated | Rebuildable views | Rebuild from canonical Markdown; safe to remove when no longer needed. |
| `tools/`, `skills/`, `.agents/skills/` | Owledge kit copy | Local CLI and discoverable skills | Replace via reviewed upgrade or remove when retiring the kit. |
| `plugins/owledge-cowork/` | Optional adapter | Private local hook adapter | Exists only when selected; remove separately. |

The package recipe is idempotent for an existing target: it adds missing kit
files and does not overwrite existing project files. For version changes, use
the reviewed [upgrade guide](../upgrading.md), not a blind reinstall.

## Verify, recover, and remove

Every recipe ends with `doctor`; a successful result has `"passed": true`.
If it does not, keep the output, confirm the documented working directory, and
run the same command with the stated project root. Do not use `--force` on a
non-disposable project folder.

To retire Owledge, first retain or export any canonical plans, evidence, and
handoffs you still need. Then remove only the Owledge-owned kit copies and
generated views after review; do not delete existing host files merely because
they sit beside the kit. The detailed project recipe lists the created paths.

## One command owner

This hub owns installation-path selection and command boundaries. Individual
pages own complete recipes. README and the docs home route here; they do not
duplicate an alternate installation chain.
