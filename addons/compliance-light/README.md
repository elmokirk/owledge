# Compliance Light Add-on

Optional compliance-support layer for Owledge.

This add-on is intentionally not part of the default minimal project kit. Use it
only when a project needs lightweight governance evidence for customer data,
personal data, external AI providers, shared exports, or AI-risk review.

It provides Markdown templates and read-only compliance checks. It does not
provide legal advice, certification, RBAC, encryption, automatic deletion, or a
secure MCP/API access layer.

## Build A Project Folder With Compliance Support

```bash
python tools/owledge.py build-project-kit --output-path /tmp/owledge-project-kit-compliance --include-compliance --verify
```

## Check Compliance State

```bash
python tools/owledge_core.py --project-root . compliance-doctor
```

The file copy contract for this add-on lives in `addon.json`.
