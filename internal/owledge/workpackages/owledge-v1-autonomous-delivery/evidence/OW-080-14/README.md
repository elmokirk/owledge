---
ticket: OW-080-14
status: implementation_in_progress
visibility: private
data_class: internal
---

# OW-080-14 Evidence

The migration fixture proves pointer-manifest size, active-register-only cold
load, stable finding SHA preservation, traversal/missing-register fail-closed
behavior, and copy-only migration. The live dogfood `RUN-STATE.yaml` is never a
migration target; its before/after SHA is asserted by the focused suite.
