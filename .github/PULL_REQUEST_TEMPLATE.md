## Summary

Describe the user-facing change in plain language.

## Checks

- [ ] `python tools/owledge.py test public-docs --project-root .`
- [ ] `python tools/owledge.py finalization-gates --project-root . --include-compliance`
- [ ] Docs updated if install paths, harness support, or public behavior changed
- [ ] If this PR touches `templates/` or `schemas/`: bumped `VERSION`, added `## Upgrade notes` to `CHANGELOG.md` with `breaking: yes|no|additive`, pasted `owledge upgrade --dry-run` output

## Notes

Call out any tradeoffs, follow-up work, or manual GitHub metadata changes.
