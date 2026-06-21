# Trust Readiness Kit

Trust Readiness Kit is an optional documentation add-on for teams evaluating
Owledge. It turns the security and enterprise boundaries into an explicit
evaluation path.

## Install

```bash
python tools/owledge.py install-addon --project-root . --addon trust-readiness-kit
```

## What It Adds

- Data-flow map for private, project, generated, and shared artifacts.
- Threat model for a local Markdown memory kit.
- Security FAQ with clear non-goals.
- Team evaluation checklist for adoption reviews.

This add-on does not add RBAC, encryption at rest, or regulated compliance. It
documents what exists and what must be handled by the adopting team.

