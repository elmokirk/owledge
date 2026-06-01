# Website And UI Report

## Use When

Use for website decisions, UI build reports, visual design explanation, branding, design systems, component decisions, layout reviews, or design-token choices.

## Sources

Prefer:

- website or UI decision docs
- `agent-memory/canonical/`
- `agent-memory/decisions/`
- screenshots or evidence files
- design-token files when present

## Sections

| Section | Purpose |
| --- | --- |
| Visual objective | What the UI should communicate |
| Audience | Who uses it |
| Layout decisions | Structure and hierarchy |
| Component decisions | Reusable UI pieces |
| Design tokens | Color, spacing, radius, typography |
| Rejected alternatives | What not to do |
| Transfer block | JSON settings for an implementation agent |
| Sources | Links and hashes |

## Interactive Controls

Include controls when useful:

- color swatches
- radius slider
- spacing density slider
- type scale slider
- contrast switch
- mode toggle
- exported JSON settings block

## Persistence Rule

Control changes in HTML are not canonical. To persist them, the user must ask an agent to apply the exported JSON settings into Markdown or code.
