# Owledge 0.9.0rc1

Owledge stores original Markdown evidence, proposals, and reviewed knowledge separately. A local Agent can search its granted scope and propose a change; a person reviews the exact proposal before it becomes accepted knowledge. A bounded search miss does not prove absence.

This prerelease runs locally through one CLI and a stdio MCP server. Download the wheel from the [GitHub release](https://github.com/elmokirk/owledge/releases/tag/v0.9.0rc1); it is not published to PyPI. Python 3.10 or newer is required; the installed flow is tested on Windows with Python 3.14.

The v0.8.0 kit remains available. This is a different command interface: start a new workspace and register existing Markdown as source material. Do not treat it as an in-place migration of a v0.8 kit directory.

## Install and try a cited search

Create a new virtual environment and an absent sample workspace. In PowerShell, replace the wheel path:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --no-index --no-deps 'PATH\owledge-0.9.0rc1-py3-none-any.whl'
$O = (Resolve-Path '.\.venv\Scripts\owledge.exe').Path
$W = Join-Path $PWD 'Knowledge'
& $O setup $W --sample --yes --json
& $O search unverified --workspace $W --json
& $O status --workspace $W --json
```

The sample search cites preserved source bytes; its excerpt is not an approved fact. `& $O doctor --workspace $W` checks local health. The native JSON commands shown here return one UTF-8 result without an interactive prompt. The small sample is not a large-import performance promise.

`& $O register PATH --workspace $W --yes --json` imports an external Markdown file or folder while preserving the original folder. New source access is restricted by default. `--access shared` is still limited to appropriately connected local readers; a Project connection does not gain Global reading just because a Project is linked.

## Agent and human review

Create a separate Project workspace. Preview a named Contributor connection, inspect its scope, then apply the returned hash:

```powershell
$P = Join-Path $PWD 'Project'
& $O setup $P --profile project --project-id trial --yes --json
& $O link --workspace $P --global-workspace $W --yes --json
& $O connect codex --workspace $P --role contributor --json
& $O connect codex --workspace $P --role contributor --expected-sha256 HASH --yes --json
```

For a second Agent, repeat with a distinct name such as `claude`. Configure each local client to launch the absolute path in `$O` with arguments `mcp --workspace <absolute-Project-path> --connection codex` or `... claude`. In a JSON client configuration, use an absolute Windows path with escaped backslashes or forward slashes. Give each client only the listed Owledge tools. The Agent can call `owledge_settings`, `owledge_search`, `owledge_read`, and permitted proposal tools; it cannot approve a Candidate or perform recovery through MCP.

A person opens the proposed record, checks its text, source and base, then approves or rejects the displayed Candidate with the current content hash:

```powershell
& $O review --workspace $P --name lesson:NAME --json
& $O review --workspace $P --name lesson:NAME --candidate-id ID --decision approve --expected-sha256 HASH --yes --json
& $O read --workspace $P --name lesson:NAME --json
```

A stale base, changed source, changed Settings or revoked right requires a fresh preview. `& $O settings inspect --workspace $P --json` reports effective values and diagnostics. `settings configure` and `settings repair` are separate local human operations with their own preview, hash and `--yes`; do not edit managed control files directly.

## Inbox, backup and recovery

To use an Inbox, select it during initial setup with `--inbox PATH`, and create regular `raw` and `processed` directories inside it. Place Markdown packages in `raw`. While that Workspace and Inbox remain the saved selection, `ingest --json` may process them without repeated confirmation; `ingest --preview --json` has no effects. A later `setup` changes the single saved selection. Then use the explicit form `ingest --workspace $W --inbox PATH --yes --json`; add `--recover` and keep the same Workspace and Inbox after an interrupted intake. Importing bytes never approves their claims.

A single-workspace archive or a linked Project/Global pair has a read-only backup preview. Apply only its returned hash. Restore requires a new absent target; a linked pair creates fixed `Project` and `Global` children, suspends path-bound cross-authority reader grants, and leaves external source folders untouched:

```powershell
& $O backup --workspace $P --archive 'PATH\pair.zip' --linked --json
& $O backup --workspace $P --archive 'PATH\pair.zip' --linked --expected-sha256 HASH --yes --json
& $O restore --archive 'PATH\pair.zip' --target 'PATH\restored-pair' --json
& $O restore --archive 'PATH\pair.zip' --target 'PATH\restored-pair' --expected-sha256 HASH --yes --json
```

Recover an interrupted paired restore with the same archive and target plus `--recover --yes --json`. After restore, run status/doctor and an exact read. Regrant cross-authority readers through separate human-reviewed `global-read` or `project-read` previews; a restored link alone does not grant them. Omit `--linked` when backing up one workspace.

## Update and remove

Stop MCP clients before replacing the wheel. Keep a verified backup and the previous wheel. Use normal offline pip or uv to install the target wheel, then preview and apply `setup --workspace W --upgrade` for each affected Workspace. Check `settings inspect`, doctor and a fresh named read. If the new runtime or Settings binding cannot be accepted, reinstall the retained wheel while clients remain stopped, then verify health and reads again. Runtime metadata rebind does not install binaries.

To remove the integration, delete local client MCP entries, preview and apply `connect NAME --workspace W --action revoke` for each named profile, then confirm that connection is denied. Stop clients and run `.\.venv\Scripts\python -m pip uninstall owledge`. Keep workspaces, original source folders and backups; package removal does not remove user Markdown.

## Boundaries and extensions

The CLI and MCP adapter call the same local Core. Core owns rights, bounded retrieval, revision checks, review and receipts. A Skill guides work but grants no authority. Named connections bind scope at the trusted local host; they do not isolate hostile processes sharing one OS account. There is no hosted or multi-tenant claim. Extension contracts remain experimental: an adapter must use existing permitted operations, handle denied/stale/replayed calls, and prove it can be removed without changing knowledge files. No plugin framework or background service is needed for this local path.

Build from this source with `python -m pip wheel . --no-deps --wheel-dir dist` (the build backend may need downloading). Run the included archive and interruption checks with `python -B -m unittest discover -s tests/mvp -p 'test_*.py'`. Licensed under [MIT](LICENSE).
