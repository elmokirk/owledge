---
title: "Project Site HTML Template Notes"
status: "active"
type: "template"
template_kind: "project-site-html"
---

# Project Site HTML Template Notes

This optional add-on renders read-only project dashboards. The generated HTML
must stay local, static, and self-contained.

## Borrowed Interface Rules

- Use CSS variables derived from the active Owledge report design.
- Keep all CSS inline; do not use external URLs, CDNs, remote fonts, or assets.
- Use a responsive report shell: header, status badge, navigation, metric cards,
  content panel, source context, and mobile-safe spacing.
- Render Markdown tables as HTML tables.
- Render long source/evidence blocks with `<details>` when a compact view helps.
- Render local file references as links when they are safe relative paths.
- Do not use `localStorage`; generated pages are deterministic read-only views.
- Do not add export buttons to read-only dashboards.

Markdown snapshots remain the source of truth. HTML is generated output.
