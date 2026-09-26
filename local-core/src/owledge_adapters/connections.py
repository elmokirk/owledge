"""Read-only resolution of named local Contributor profiles at the host boundary."""
from __future__ import annotations

from pathlib import Path
import re

from .local_setup import open_workspace


RIGHTS_ERA = "owledge.bound-source-rights/1"


def resolve_connection(workspace: Path, name: str, *, role: str = "contributor"):
    """Resolve a trusted launch name; repeat before every Agent operation."""
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", name):
        raise ValueError("Ungültiger Verbindungsname.")
    workspace = Path(workspace).absolute()
    core, state = open_workspace(workspace)
    from .knowledge_workspace import SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA, AUTHORITY
    from .project_workspace import SCHEMA as PROJECT_SCHEMA, LINKED_SCHEMA
    if state.get("schema") in {SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}:
        authority_id, root = AUTHORITY, workspace / "global"
    elif state.get("schema") in {PROJECT_SCHEMA, LINKED_SCHEMA}:
        authority_id, root = state["authority_id"], workspace / "project"
    else:
        raise ValueError("Benannte Agent-Verbindungen benötigen einen Knowledge- oder Project-Workspace.")
    from owledge_core.project_io import bootstrap_authority, local_connection_principal
    from owledge_core.policy import named_connection_capabilities, source_access_allowed
    try:
        capabilities = named_connection_capabilities(role)
    except ValueError as error:
        raise ValueError("Ungültige Verbindungsrolle.") from error
    authority = bootstrap_authority(root, authority_id)
    if authority.metadata.get("rights_era") != RIGHTS_ERA:
        raise ValueError("Älterer Workspace: vor Agent-Zugang Quellenrechte und abgeleitete Kandidaten ausdrücklich migrieren/neu prüfen. setup --upgrade genügt nicht.")
    connections = authority.metadata.get("connections")
    if not isinstance(connections, dict):
        raise ValueError("Verbindungsregister fehlt oder ist ungültig.")
    profile = connections.get(name)
    if (not isinstance(profile, dict) or set(profile) !=
            {"principal_id", "role", "authority_id", "source_link_id", "status"}
            or profile.get("status") != "active" or profile.get("role") != role
            or profile.get("authority_id") != authority_id
            or profile.get("principal_id") != local_connection_principal(authority_id, name)):
        raise ValueError("Benannte Verbindung fehlt, wurde widerrufen oder ist ungültig.")
    principal = profile["principal_id"]
    grants = authority.metadata.get("actor_grants")
    if not isinstance(grants, dict) or grants.get(principal) != list(capabilities):
        raise ValueError("Verbindungsrechte wurden widerrufen oder sind unvollständig.")
    link_id = profile["source_link_id"]
    if link_id is not None:
        if not isinstance(link_id, str):
            raise ValueError("Verbindungs-Source-Link ist ungültig.")
        controls = core._repository.progressive_controls(authority_id)
        links = [item for item in controls if item.metadata.get("source_link_id") == link_id]
        if len(links) != 1 or not source_access_allowed(links[0], principal):
            raise ValueError("Verbindungs-Source-Link ist nicht mehr freigegeben.")
    return core, state, dict(profile)
