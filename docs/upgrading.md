# Upgrading Owledge

## Version stamping

Every shipped template carries an `owledge_kit_version` frontmatter field matching the kit's `VERSION` file. The existing `version:` field is the `MEMORY_SCHEMA_VERSION` (memory-schema version, own source of truth). After `owledge init-project`, a `kit-manifest.json` appears at the project root recording `kit_version`, `memory_schema_version`, and per-file `sha256_installed` + `sha256_original` hashes.

## Checking for drift

```bash
python tools/owledge.py doctor --project-root .
```

The `version-drift` check compares the manifest's `kit_version` against the running CLI's `KIT_VERSION`. A mismatch means the installed kit is older (or newer) than the CLI. `outdated_files` lists pristine files that can be safely updated; `user_edited_files` lists files you have modified (which `safe` mode will not overwrite).

## Upgrade modes

| Mode | Behavior | Never-touch list respected |
| --- | --- | --- |
| `safe` (default) | Updates only pristine files; skips user-edited files with a warning | Yes |
| `force-templates` | Updates every updatable file except never-touch list; requires `--yes` or interactive confirmation on a TTY | Yes |
| `manual` | Emits a `git apply`-able patch to `agent-memory/exports/upgrade-pending.patch`; always dry-run (`--apply` is rejected) | Yes |

Use `safe` for routine additive upgrades where you have lightly customized a few
shipped files and want to preserve your edits. Use `force-templates` when you
intentionally want to reset every updatable shipped file to the current kit
version (for example after merging upstream fixes into a fork); it never touches
the never-touch list, so project memory and user-content files remain intact.
Use `manual` in CI or review workflows where you want to inspect the proposed
diff as a single `git apply`-able patch before deciding whether to apply it.
`manual` mode is always dry-run: `--apply --mode=manual` is rejected with exit
code 2 (manual emits a patch, never writes).

## Never-touch list (hardcoded, no flag bypasses)

- `PROJECT_CONTEXT.md`, `AGENTS.md`, `CLAUDE.md`, `USER_CONTEXT.md`
- `agent-memory/{decisions,plans,sessions,evidence,handoffs}/**`
- `global-memory/**`

## Commands

```bash
python tools/owledge.py upgrade --dry-run                    # default: show what would change
python tools/owledge.py upgrade --dry-run --mode=manual      # emit a git-apply-able patch
python tools/owledge.py upgrade --apply                      # safe mode apply
python tools/owledge.py upgrade --apply --mode=force-templates --yes  # force apply
```

## Recovery

If an upgrade goes wrong:
1. `git checkout -- kit-manifest.json` (restore the prior manifest)
2. `python tools/owledge.py upgrade --dry-run` (see the diff)
3. `git checkout -- <files>` to revert any file

## Additive vs breaking changes

When a release ships an additive-only schema change (new optional field, new template), `CHANGELOG.md` declares `breaking: no` or `breaking: additive` under `## Upgrade notes`. The `--dry-run` report marks such updates as `alert_level: additive` (informational). Breaking changes are marked `alert_level: breaking`.

## When upgrades are needed

Upgrades are needed when the kit version (the `VERSION` file) bumps. Run
`owledge doctor --project-root .` to detect `version-drift`; the report lists

`outdated_files` (pristine, safe to update) and `user_edited_files` (yours,
left alone by `safe` mode).

Additive schema changes (new optional frontmatter fields, new templates) are
safe to apply with `safe` mode — they will not overwrite your edits and will not
break existing memory records. Breaking changes (removed fields, renamed keys,
changed required-vs-optional) require manual review: use `--mode=manual` to emit
a patch, inspect it, and adapt your project before applying.

## Skills and the manifest

`init-project` installs the kit's skills (`skills/agent-memory-principles`,
`skills/agent-memory-runtime-bridge`, `skills/review-evaluation-workflow`,
`skills/render-memory-report`, `skills/concept-blindspot-audit`) into your
project and records each skill file in `kit-manifest.json`. This means `doctor`
detects skill drift and `upgrade --apply --mode=safe` updates skill files you
have not edited. The `concept-blindspot-audit` skill was added in v0.6.1; if you
installed owledge before v0.6.1, re-running `init-project` on your existing
project will install the new skill (it uses `copy_file_if_missing`, so it will
not overwrite files you already have).

## Global layer and upgrades

`global-link.json` (written by `init-project --link-global`) is a
project-specific link. The upgrade command does **not** touch it — upgrades
operate only on shipped kit files, never on project configuration or the global
layer.

If the global layer path changes (for example, you move `~/.owledge/global`), do
not run `upgrade`. Re-run `owledge init-project --link-global <new-path>` to
refresh the link. `doctor` reports a `global-link` error if the linked path is
missing.

## Dogfood sync (for maintainers)

Maintainers use `sync-dogfood --apply` to mirror
`templates/agent-memory/templates/` → `internal/agent-memory/templates/` after
editing product templates. The mirror is strictly one-way; the
`dogfood-sync` finalization gate fails if the two trees drift. See
`internal/README.md` for the maintainer workflow.

```bash
python tools/owledge.py sync-dogfood --dry-run --project-root .
python tools/owledge.py sync-dogfood --apply --project-root .
```

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| "No kit-manifest.json found" | Run `owledge init-project --target .` first to write the manifest |
| "Kit installed at vX, CLI is vY" | Run `owledge upgrade --dry-run --project-root .` to see the diff, then `--apply` |
| "Lock held by PID" | Remove `agent-memory/.upgrade.lock` if the prior run is no longer active |
| "force-templates requires --yes" | Add `--yes` (or run on a TTY for interactive confirmation) |
| "manual mode is always dry-run" | Remove `--apply` from your `--mode=manual` invocation; manual emits a patch only |