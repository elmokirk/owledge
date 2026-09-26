"""Pure authority-bound capability decisions."""

from __future__ import annotations

from .artifacts import ManagedMarkdown


__all__: tuple[str, ...] = ()


def named_connection_capabilities(role: str) -> tuple[str, ...]:
    """The single authority rule for Owner-issued named local profiles."""
    if role == "contributor":
        return ("discover", "retrieve", "propose")
    if role == "operator":
        return ("discover", "retrieve", "review", "promote")
    raise ValueError("named connection role is invalid")


def has_grant(authority: ManagedMarkdown, principal_id: str, capability: str) -> bool:
    raw = authority.metadata.get("actor_grants", {})
    if not isinstance(raw, dict):
        return False
    grants = raw.get(principal_id, ())
    return isinstance(grants, list) and capability in grants


def source_rights_allowed(rights: object, principal_id: str) -> bool:
    """Check a persisted source right without using request-selected filters."""
    if not isinstance(rights, dict) or set(rights) != {"access", "principals"}:
        return False
    access, principals = rights["access"], rights["principals"]
    if (not isinstance(access, str) or access not in {"shared", "restricted"} or not isinstance(principals, list)
            or any(not isinstance(item, str) or not item.startswith("principal:") for item in principals)
            or len(principals) != len(set(principals)) or access == "shared" and principals):
        return False
    return access == "shared" or principal_id in principals


def source_access_allowed(link: ManagedMarkdown, principal_id: str) -> bool:
    return source_rights_allowed(link.metadata.get("source_access"), principal_id)
