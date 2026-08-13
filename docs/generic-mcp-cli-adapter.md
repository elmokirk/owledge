# Generic MCP/CLI adapter (V1)

The generic V1 profile is a project-bound stdio JSON-RPC reference adapter. It
has no runtime-specific files and does not make any Tier-1 claim for Hermes,
OpenCode, or Pi.

Install the standard project kit and the optional runtime conformance add-on,
then start it from the host project:

```bash
python tools/owledge_generic_adapter.py --project-root .
```

The server exposes capability discovery, explicit capability negotiation, an
owner-invoked read-only pre-plan capsule, and a Candidate boundary report. It
never writes a Candidate or promotes content. A later reviewed Core flow owns
those operations. The bound project cannot be changed through JSON-RPC, and
malformed requests return structured errors without stopping the server.
