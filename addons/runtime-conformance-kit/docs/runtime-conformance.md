# AdapterManifest v1

Runtime Conformance Kit makes local adapter support auditable; it does not make
marketplace-certification or untested runtime claims. The V1 profile set is
fixed: `codex`, `claude-code`, and `generic-mcp-cli`.
Each manifest declares only local `project_user` and `user_global` context,
read/control, checkpoint/handoff, and project-scoped Candidate writes. The
manifest explicitly reports unsupported automatic pre-plan inspection, durable
routing, direct Core storage access, enterprise scope, and orchestration.

`tools/owledge_adapter_contracts.py` validates and negotiates this boundary.
The add-on runner stays read-only and checks that all three shipped manifests
make equivalent declarations.
