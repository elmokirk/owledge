"""Contributor-only MCP boundary for the private Core command seam."""

from __future__ import annotations

from typing import Mapping


__all__: tuple[str, ...] = ()


class ContributorMcpAdapter:
    """Bind asserted Contributor provenance without accepting Owner assurance."""

    _OWNER_OPERATIONS = {
        "candidate_open",
        "candidate_review",
        "candidate_promote",
        "gap_verify",
        "recover",
    }

    def __init__(
        self,
        core: object,
        *,
        principal_id: str,
        active_authority_id: str,
        reported: Mapping[str, object],
        adapter_observed: Mapping[str, object],
        source_link_id: str | None = None,
    ) -> None:
        self._core = core
        self._principal_id = principal_id
        self._active_authority_id = active_authority_id
        self._reported = dict(reported)
        self._adapter_observed = dict(adapter_observed)
        self._source_link_id = source_link_id

    @staticmethod
    def _denied() -> dict[str, object]:
        return {
            "schema": "owledge.core-result/1",
            "status": "denied",
            "reason_code": "capability_denied",
            "summary": "This identity may not perform the requested knowledge operation.",
            "next_action": "Ask the project Owner for the required capability.",
            "data": {},
            "receipt_id": None,
        }

    def execute(
        self,
        operation: str,
        operation_id: str,
        payload: Mapping[str, object],
        *,
        target_authority_id: str | None = None,
    ) -> dict[str, object]:
        if operation in self._OWNER_OPERATIONS:
            return self._denied()
        command = {
            "schema": "owledge.core-command/1",
            "operation": operation,
            "operation_id": operation_id,
            "principal": {
                "principal_id": self._principal_id,
                "assurance": "asserted",
                "reported": dict(self._reported),
                "adapter_observed": dict(self._adapter_observed),
            },
            "active_authority_id": self._active_authority_id,
            "target_authority_id": target_authority_id or self._active_authority_id,
            "source_link_id": self._source_link_id,
            "expected_revisions": {},
            "payload": dict(payload),
        }
        return self._core.execute(command)  # type: ignore[attr-defined,no-any-return]

    def preview_gap_answer(
        self,
        operation_id: str,
        *,
        bundle_markdown: str,
        gap_id: str,
        evidence_value: str,
        statement: str,
        reported_content_origin: str,
    ) -> dict[str, object]:
        """Create a Candidate preview from plain Owner input.

        Frontmatter and editable-bundle syntax remain transport details. The
        caller supplies only the answer fields shown by a dialog or Agent.
        """

        fields = {
            "gap_id": gap_id,
            "evidence_value": evidence_value,
            "statement": statement,
            "reported_content_origin": reported_content_origin,
        }
        if any(
            not isinstance(value, str)
            or not value.strip()
            or "\n" in value
            or "\r" in value
            for value in fields.values()
        ):
            raise ValueError("Gap answers require non-empty single-line text")

        start = f'<!-- owledge-gap:start gap_id="{gap_id}" mode="editable" -->'
        end = f'<!-- owledge-gap:end gap_id="{gap_id}" -->'
        if bundle_markdown.count(start) != 1 or bundle_markdown.count(end) != 1:
            raise ValueError("Maintenance Bundle must contain one matching editable Gap")
        start_offset = bundle_markdown.index(start)
        end_offset = bundle_markdown.index(end, start_offset) + len(end)
        editable = bundle_markdown[start_offset:end_offset]
        placeholder = "evidence_value:\nstatement:\nintent_to_close: false"
        if editable.count(placeholder) != 1:
            raise ValueError("Editable Gap is not an unanswered supported form")
        answered = editable.replace(
            placeholder,
            "evidence_value: "
            + evidence_value.strip()
            + "\nstatement: "
            + statement.strip()
            + "\nintent_to_close: true",
        )
        edited_bundle = (
            bundle_markdown[:start_offset]
            + answered
            + bundle_markdown[end_offset:]
        )
        return self.execute(
            "bundle_preview",
            operation_id,
            {
                "bundle_markdown": edited_bundle,
                "content_origin": reported_content_origin,
            },
        )
