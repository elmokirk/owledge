# Compliance Light

Compliance Light is an optional support layer for projects using the Agent
Memory Kit with personal data, customer data, external AI providers, or shared
exports.

It is not a compliance platform and does not claim GDPR, AI Act, ISO, SOC 2, or
enterprise readiness. It gives teams a small Markdown-first evidence surface:

- project compliance profile
- processing activity template
- AI system inventory template
- provider registry template
- DPIA trigger template
- data subject request template
- security incident template
- read-only compliance doctor
- combined compliance gates

## Default Posture

The starter profile is conservative:

- personal data disabled
- customer data disabled
- external AI providers disabled
- high-impact AI disabled
- shared exports disabled

With those defaults, the layer verifies that the project is prepared for light
governance without requiring enterprise controls. Enabling any trigger turns on
the matching checks.

## What It Does Not Do

- No legal advice.
- No automatic deletion or anonymization.
- No RBAC or tenant access enforcement.
- No encryption-at-rest implementation.
- No secure MCP or hosted API layer.
- No certification claim.
