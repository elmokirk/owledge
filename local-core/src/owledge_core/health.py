"""Read-only health observations."""

from __future__ import annotations

from .artifacts import ManagedMarkdown


__all__: tuple[str, ...] = ()


def invalid_document_count(documents: tuple[ManagedMarkdown, ...]) -> int:
    return 0
