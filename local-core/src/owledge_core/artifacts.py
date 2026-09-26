"""Parsing and validation for private Core Markdown artifacts."""

from __future__ import annotations

import json
from hashlib import sha256
from dataclasses import dataclass
from typing import Iterator, Mapping
import unicodedata

from .contracts import (
    ContractValidationError,
    SourceFileSnapshot,
    SourceSnapshot,
)


__all__: tuple[str, ...] = ()


def unicode_keyword_spans(text: str) -> Iterator[tuple[str, int]]:
    """Yield normalized words with offsets into the unchanged decoded text."""
    start: int | None = None
    for index, character in enumerate(text + " "):
        if character.isalnum() or (start is not None and unicodedata.category(character).startswith("M")):
            if start is None:
                start = index
            continue
        if start is not None:
            token = unicodedata.normalize("NFC", text[start:index].casefold())
            if len(token) >= 3:
                yield token, start
            start = None


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ContractValidationError("frontmatter JSON object key is duplicated")
        result[key] = value
    return result


@dataclass(frozen=True, slots=True)
class ManagedMarkdown:
    relative_path: str
    metadata: Mapping[str, object]
    body: str
    content_sha256: str
    size_bytes: int

    @property
    def artifact_id(self) -> str:
        return str(self.metadata["artifact_id"])

    @property
    def authority_id(self) -> str:
        return str(self.metadata["authority_id"])

    @property
    def revision(self) -> str:
        return str(self.metadata["revision"])


def _scalar(value: str) -> object:
    stripped = value.strip()
    if stripped.startswith(("{", "[", '"')) or stripped in {"true", "false", "null"}:
        try:
            return json.loads(stripped, object_pairs_hook=_unique_json_object)
        except json.JSONDecodeError as error:
            raise ContractValidationError("frontmatter value is invalid JSON") from error
    if stripped.isdecimal():
        return int(stripped)
    if not stripped:
        raise ContractValidationError("frontmatter value must not be empty")
    return stripped


def parse_markdown_frontmatter(document: str) -> tuple[dict[str, object], str]:
    """Parse the shared frontmatter syntax without assuming one artifact schema."""

    normalized = document.replace("\r\n", "\n")
    if not normalized.startswith("---\n") or "\n---\n" not in normalized[4:]:
        raise ContractValidationError("Markdown frontmatter is missing")
    header, body = normalized[4:].split("\n---\n", 1)
    metadata: dict[str, object] = {}
    for line in header.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ContractValidationError("frontmatter field is malformed")
        key, value = line.split(":", 1)
        key = key.strip()
        if not key or key in metadata:
            raise ContractValidationError("frontmatter field is duplicated or empty")
        metadata[key] = _scalar(value)
    return metadata, body


def parse_managed_markdown(
    relative_path: str,
    document: str,
    *,
    encoded_document: bytes | None = None,
) -> ManagedMarkdown:
    encoded = document.encode("utf-8") if encoded_document is None else encoded_document
    if encoded.decode("utf-8") != document:
        raise ContractValidationError("managed Markdown byte representation does not match")
    metadata, body = parse_markdown_frontmatter(document)
    required = {
        "schema",
        "document_version",
        "artifact_id",
        "authority_id",
        "revision",
        "lifecycle",
        "processing_layer",
        "source_trust",
    }
    if not required <= set(metadata):
        raise ContractValidationError("managed Markdown required field is missing")
    return ManagedMarkdown(
        relative_path=relative_path,
        metadata=metadata,
        body=body,
        content_sha256=sha256(encoded).hexdigest(),
        size_bytes=len(encoded),
    )


def _source_slug(snapshot: SourceSnapshot) -> str:
    return snapshot.source_id.removeprefix("source:")


def _source_record_id(snapshot: SourceSnapshot, source_file: SourceFileSnapshot) -> str:
    identity = f"{snapshot.source_id}\0{source_file.relative_path}".encode("utf-8")
    return f"source-record:{sha256(identity).hexdigest()}"


def render_source_sidecar(
    snapshot: SourceSnapshot,
    source_file: SourceFileSnapshot,
) -> tuple[str, str]:
    """Render metadata for opaque source bytes without interpreting those bytes."""

    artifact_id = _source_record_id(snapshot, source_file)
    document = (
        "---\n"
        "schema: owledge.source-sidecar/1\n"
        "document_version: 1\n"
        f"artifact_id: {artifact_id}\n"
        f"authority_id: {snapshot.source_id}\n"
        f"revision: source-rev-1-{snapshot.snapshot_sha256[:16]}\n"
        "lifecycle: observed\n"
        "processing_layer: raw\n"
        "source_trust: external\n"
        "canonical: false\n"
        f"source_relative_path: {json.dumps(source_file.relative_path, ensure_ascii=False)}\n"
        f"source_size_bytes: {source_file.size_bytes}\n"
        f"source_content_sha256: {source_file.content_sha256}\n"
        "---\n\n"
        "# External source record\n\n"
        "Metadata for an opaque, read-only source document. The source body is not interpreted.\n"
    )
    return artifact_id, document


def render_source_manifest(
    snapshot: SourceSnapshot,
    records: list[dict[str, object]],
) -> str:
    """Render the deterministic manifest for one byte-exact source snapshot."""

    rendered_records = json.dumps(
        records,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (
        "---\n"
        "schema: owledge.source-snapshot/1\n"
        "document_version: 1\n"
        f"artifact_id: source-manifest:{snapshot.snapshot_sha256}\n"
        f"authority_id: {snapshot.source_id}\n"
        f"revision: source-rev-1-{snapshot.snapshot_sha256[:16]}\n"
        "lifecycle: observed\n"
        "processing_layer: raw\n"
        "source_trust: external\n"
        "canonical: false\n"
        "snapshot_mode: byte_copy\n"
        f"snapshot_sha256: {snapshot.snapshot_sha256}\n"
        f"document_count: {len(snapshot.files)}\n"
        f"size_bytes: {snapshot.size_bytes}\n"
        f"records: {rendered_records}\n"
        "---\n\n"
        "# External source snapshot\n\n"
        "This manifest describes copied source bytes. It grants no knowledge authority.\n"
    )


def render_source_setup_receipt(
    snapshot: SourceSnapshot,
    operation_id: str,
    approved_by: str,
) -> tuple[str, str]:
    """Render minimal local evidence for a completed source snapshot setup."""

    slug = _source_slug(snapshot)
    receipt_id = f"receipt:{slug}:setup-{snapshot.snapshot_sha256}"
    document = (
        "---\n"
        "schema: owledge.receipt/1\n"
        "document_version: 1\n"
        f"receipt_id: {receipt_id}\n"
        f"authority_id: {snapshot.source_id}\n"
        "operation: setup_apply\n"
        "outcome: ok/source_snapshot_ready\n"
        f"operation_id: {operation_id}\n"
        f"snapshot_sha256: {snapshot.snapshot_sha256}\n"
        f"approved_by: {approved_by}\n"
        "---\n\n"
        "# Source setup receipt\n\n"
        "Byte-exact snapshot materialized in the disposable setup workspace.\n"
    )
    return receipt_id, document
