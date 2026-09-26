"""Separate local-Owner boundary for privileged Core operations."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping


__all__: tuple[str, ...] = ()


class LocalOwnerAdapter:
    """Bind local Owner assurance outside Agent-controlled request data."""

    def __init__(
        self,
        core: object,
        *,
        principal_id: str,
        active_authority_id: str,
        reported: Mapping[str, object],
        adapter_observed: Mapping[str, object],
        operator_name: str | None = None,
        operator_workspace: Path | None = None,
    ) -> None:
        if (operator_name is None) != (operator_workspace is None):
            raise ValueError("Named Operator requires name and workspace together.")
        self._core = core
        self._principal_id = principal_id
        self._active_authority_id = active_authority_id
        self._reported = dict(reported)
        self._adapter_observed = dict(adapter_observed)
        self._operator_name = operator_name
        self._operator_workspace = operator_workspace

    def execute(
        self,
        operation: str,
        operation_id: str,
        payload: Mapping[str, object],
    ) -> dict[str, object]:
        command = {
            "schema": "owledge.core-command/1",
            "operation": operation,
            "operation_id": operation_id,
            "principal": {
                "principal_id": self._principal_id,
                "assurance": "local_operator" if self._operator_name is not None else "local_owner",
                "reported": dict(self._reported),
                "adapter_observed": dict(self._adapter_observed),
            },
            "active_authority_id": self._active_authority_id,
            "target_authority_id": self._active_authority_id,
            "expected_revisions": {},
            "payload": dict(payload),
        }
        if self._operator_name is not None:
            return self._core._execute_from_local_operator(command, name=self._operator_name,
                workspace=self._operator_workspace)  # type: ignore[attr-defined,no-any-return]
        return self._core._execute_from_local_owner(command)  # type: ignore[attr-defined,no-any-return]

    def open_candidate(
        self,
        candidate_id: str,
        candidate_revision: str,
    ) -> dict[str, object]:
        """Show one bounded proposal without exposing frontmatter to the Owner."""

        return self.execute(
            "candidate_open",
            f"op:candidate-open:{candidate_id}:{candidate_revision}",
            {
                "candidate_id": candidate_id,
                "candidate_revision": candidate_revision,
            },
        )
