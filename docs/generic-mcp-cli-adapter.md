# Generic MCP/CLI adapter (V1)

The generic V1 profile is a project-bound stdio JSON-RPC reference adapter. It
implements MCP `2026-07-28` discovery and per-request protocol metadata. It
has no runtime-specific files and does not make any Tier-1 claim for Hermes,
OpenCode, or Pi.

Install the standard project kit and the optional runtime conformance add-on,
then start it from the host project:

```bash
python tools/owledge_generic_adapter.py --project-root .
```

Start with `server/discover` and supply
`_meta.io.modelcontextprotocol/protocolVersion: "2026-07-28"` on every modern
request. The server exposes exactly five Core-owned tools: capabilities,
recall, context, propose and review. Candidate writes and reviews remain
revision-bound; the adapter cannot access storage directly, change its bound
project, use the network, or promote content without an explicit `review`
request. Legacy `2024-11-05` stdio clients remain supported as a compatibility
path, but new clients should use discovery.
