# Owledge Examples

Small examples for launch demos and manual smoke tests.

## Demo Vault

`demo-vault/` is a tiny Markdown knowledgebase with wiki links. Use it to show
that Owledge adds a module without rewriting existing notes:

```bash
python tools/owledge.py add-kb-module --knowledgebase-root examples/demo-vault --include-cli
```

After the command, existing files in `examples/demo-vault/` should remain
unchanged and generated Owledge files should live under
`examples/demo-vault/owledge-module/`.

Generated module files are local demo output and should not be committed.
