# Local HTTP Control Plane

Status: **local experimental**. This adapter is a bounded loopback-only
interface for agents running on the same machine. It is not a hosted service,
production Team Hub, remote team-sync service, or enterprise authorization
boundary.

Start it explicitly:

```bash
python tools/owledge_core.py --project-root . serve --host 127.0.0.1 --port 8765
```

Only `127.0.0.1`, `localhost`, and `::1` are accepted. A non-loopback bind
fails before project initialization. Possession of the administrator token
does not change that rule.

## Supported security boundary

The versioned source of truth is
[`contracts/local-http-control-plane-v1.json`](../../contracts/local-http-control-plane-v1.json).
It defines the Endpoint x Role matrix, exact scope rule, stable error codes,
and resource bounds.

- Agent authorization uses the authenticated identity and its exact
  `tenant_id`, `customer_id`, and `project_id`. Request fields cannot override
  that identity or scope.
- The administrator token can register agent identities and read aggregate
  metrics. It cannot perform tenant-scoped task, evidence, gate, context,
  promotion, or export operations.
- `/health` is unauthenticated but returns only `status`, `profile`, and
  `api_version`; it does not disclose filesystem or database details.
- Bodies are limited to 1 MiB, request I/O to 10 seconds, concurrent requests
  to 8, and each client to 120 requests per 60 seconds.
- Task, gate, and promotion identifiers fail closed on cross-scope or
  cross-resource collisions.

These are process-local controls for the experimental adapter. They do not
replace operating-system access control or protect against an already
compromised local account.

The concept-audit lifecycle check runs an upgrade dry-run as a local subprocess
and passes the canonical Owledge source root explicitly. That check does not
start this HTTP adapter, make a network request, or relax the existing
project/source path validation.

## Explicitly unsupported

TLS termination, non-loopback deployment, administrator-token rotation or
revocation, backup/restore, high availability, and multi-process rate limiting
are unsupported. Put no reverse proxy, tunnel, container port publication, or
other remote exposure in front of this profile. A future remote or Team Hub
profile requires a separate reviewed threat model and versioned contract.

For scripts, treat the JSON `error` field as the stable machine-readable code.
Human-readable exception details are intentionally not returned.
