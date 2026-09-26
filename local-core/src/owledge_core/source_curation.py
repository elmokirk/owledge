"""Private, bounded source Evidence to reviewed reference contract."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import PurePosixPath
import re
from typing import Any

from .artifacts import ManagedMarkdown, parse_managed_markdown, parse_markdown_frontmatter
from .contracts import ContractValidationError


def validate_project_origin(origin: object, authority_id: str) -> None:
    fields = {"contribution_id", "contribution_revision", "contribution_sha256", "artifact_id",
              "authority_id", "revision", "content_sha256", "record_trust", "processing_layer",
              "relative_path", "lesson_origin"}
    if (not isinstance(origin, dict) or set(origin) != fields
            or not authority_id.startswith("user-global:")
            or not isinstance(origin.get("authority_id"), str)
            or not origin["authority_id"].startswith("project:")
            or origin.get("record_trust") != "reviewed"
            or origin.get("processing_layer") != "delta"):
        raise ContractValidationError("Project Lesson origin is invalid")
    for key in fields - {"lesson_origin"}:
        value = origin[key]
        if not isinstance(value, str) or not value or len(value) > 1024 or "\x00" in value:
            raise ContractValidationError("Project Lesson origin is invalid")
    for key in ("contribution_sha256", "content_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", origin[key]):
            raise ContractValidationError("Project Lesson origin hash is invalid")
    suffix = sha256(f"{origin['authority_id']}\0{origin['artifact_id']}\0{origin['revision']}".encode()).hexdigest()[:16]
    if (origin["contribution_id"] != f"contribution:{authority_id.replace(':', '-')}-{suffix}"
            or origin["contribution_revision"] != f"contribution-rev-1-{suffix}"):
        raise ContractValidationError("Project Lesson Contribution identity is invalid")
    from .lesson_capture import validate_origin
    validate_origin(origin["lesson_origin"], origin["authority_id"])


def validate_global_reuse_lesson(document: ManagedMarkdown) -> dict[str, Any]:
    """Validate one accepted Global Lesson whose authority remains Project-owned."""

    metadata = document.metadata
    origin = metadata.get("project_origin")
    validate_project_origin(origin, document.authority_id)
    envelope = metadata.get("curation_effect")
    prefix = f"memory:{document.authority_id.replace(':', '-')}-"
    slug = document.artifact_id.removeprefix(prefix)
    expected_path = f".owledge/curated/{slug}.md"
    version = metadata.get("document_version")
    correction_base = metadata.get("correction_base")
    base_semantics = (isinstance(envelope, dict) and version == 1
                      and envelope.get("base_revision") == "absent" and correction_base is None)
    if isinstance(envelope, dict) and type(version) is int and version > 1:
        base_semantics = (isinstance(correction_base, dict)
            and set(correction_base) == {"artifact_id", "revision", "content_sha256"}
            and correction_base.get("artifact_id") == document.artifact_id
            and correction_base.get("revision") == envelope.get("base_revision")
            and correction_base.get("content_sha256") == envelope.get("base_sha256")
            and isinstance(envelope.get("base_text_sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", envelope["base_text_sha256"]))
    if (metadata.get("schema") != "owledge.managed-markdown/1"
            or not document.authority_id.startswith("user-global:")
            or not document.artifact_id.startswith(prefix) or not slug.startswith("lesson-")
            or type(version) is not int or version < 1 or not base_semantics
            or metadata.get("lifecycle") != "accepted" or metadata.get("processing_layer") != "condensed"
            or metadata.get("source_trust") != "reviewed" or metadata.get("canonical") is not True
            or metadata.get("stage") != "curated" or metadata.get("knowledge_kind") != "lesson"
            or metadata.get("memory_kind") != "semantic"
            or metadata.get("source_contribution_id") != origin["contribution_id"]
            or metadata.get("source_artifact_id") != origin["artifact_id"]
            or metadata.get("source_authority_id") != origin["authority_id"]
            or metadata.get("source_revision") != origin["revision"]
            or metadata.get("source_content_sha256") != origin["content_sha256"]
            or metadata.get("source_record_trust") != origin["record_trust"]
            or not isinstance(envelope, dict) or envelope.get("authority_id") != document.authority_id
            or not isinstance(envelope.get("effects"), list) or len(envelope["effects"]) != 1
            or envelope["effects"][0] != {"kind": "replace" if version > 1 else "create",
                                           "relative_path": expected_path, "result_revision": document.revision}
            or not document.body.strip() or len(document.body.strip()) > 8192):
        raise ContractValidationError("Global reused Lesson is invalid")
    return origin


def validate_global_reuse_transition(base: ManagedMarkdown, result: ManagedMarkdown) -> None:
    """Allow only a new exact snapshot of the same Project-owned Lesson."""

    old = validate_global_reuse_lesson(base)
    new = validate_global_reuse_lesson(result)
    stable_origin = {"artifact_id", "authority_id", "record_trust", "processing_layer", "relative_path", "lesson_origin"}
    if (base.authority_id != result.authority_id or base.artifact_id != result.artifact_id
            or base.metadata.get("knowledge_area") != result.metadata.get("knowledge_area")
            or base.metadata.get("memory_kind") != result.metadata.get("memory_kind")
            or any(old.get(key) != new.get(key) for key in stable_origin)
            or base.metadata["document_version"] + 1 != result.metadata["document_version"]):
        raise ContractValidationError("Global reused Lesson origin transition is invalid")


def validate_global_reuse_replacement(base: ManagedMarkdown, candidate: dict[str, Any],
                                      changeset: dict[str, Any], result: ManagedMarkdown) -> None:
    """Bind the reviewed old/new preview to the exact reusable replacement."""

    validate_global_reuse_transition(base, result)
    binding = {"artifact_id": base.artifact_id, "revision": base.revision,
               "content_sha256": base.content_sha256}
    preview = candidate.get("review_preview")
    if (candidate.get("replacement_binding") != binding or not isinstance(preview, dict)
            or preview.get("base") != {**binding, "text": base.body.strip()}
            or preview.get("old_source") != base.metadata.get("project_origin")
            or changeset.get("base_revision") != base.revision
            or changeset.get("base_sha256") != base.content_sha256
            or changeset.get("base_text_sha256") != sha256(base.body.strip().encode("utf-8")).hexdigest()):
        raise ContractValidationError("Global replacement review base differs")


def project_lesson_contribution(document: ManagedMarkdown) -> dict[str, Any]:
    """Return the exact reviewed Project provenance for one fresh Feed Lesson."""

    metadata = document.metadata
    if (not valid_reuse_contribution(document, "reuse_feed")
            or metadata.get("lifecycle") != "candidate"
            or metadata.get("processing_layer") != "delta"
            or metadata.get("source_trust") != "internal"
            or metadata.get("canonical") is not False
            or metadata.get("knowledge_kind") != "lesson"
            or metadata.get("memory_kind") != "semantic"
            or metadata.get("source_record_trust") != "reviewed"
            or metadata.get("source_processing_layer") != "delta"):
        raise ContractValidationError("Feed record is not an eligible Project Lesson")
    origin = {
        "contribution_id": document.artifact_id,
        "contribution_revision": document.revision,
        "contribution_sha256": document.content_sha256,
        "artifact_id": metadata.get("source_artifact_id"),
        "authority_id": metadata.get("source_authority_id"),
        "revision": metadata.get("source_revision"),
        "content_sha256": metadata.get("source_content_sha256"),
        "record_trust": metadata.get("source_record_trust"),
        "processing_layer": metadata.get("source_processing_layer"),
        "relative_path": metadata.get("source_relative_path"),
        "lesson_origin": metadata.get("source_lesson_origin"),
    }
    validate_project_origin(origin, document.authority_id)
    if not document.body.strip() or len(document.body.strip()) > 8192:
        raise ContractValidationError("Project Lesson body is empty")
    return origin


def valid_reuse_contribution(document: ManagedMarkdown, stage: str) -> bool:
    """Validate the shared legacy or reviewed/delta Contribution envelope."""

    metadata = document.metadata
    kind = metadata.get("knowledge_kind")
    source_artifact_id = metadata.get("source_artifact_id")
    source_authority_id = metadata.get("source_authority_id")
    source_revision = metadata.get("source_revision")
    source_sha256 = metadata.get("source_content_sha256")
    source_path = metadata.get("source_relative_path")
    expected_stage = "inbox" if kind == "finding" else "reuse_feed"
    trust_layer = (metadata.get("source_record_trust"), metadata.get("source_processing_layer"))
    if not (
        metadata.get("schema") == "owledge.reuse-contribution/1"
        and metadata.get("contribution_id") == document.artifact_id
        and metadata.get("stage") == stage == expected_stage
        and isinstance(kind, str) and kind in {"lesson", "idea", "project_essence", "finding"}
        and isinstance(metadata.get("memory_kind"), str)
        and metadata["memory_kind"] in {"semantic", "episodic"}
        and isinstance(source_artifact_id, str) and bool(source_artifact_id) and len(source_artifact_id) <= 256
        and isinstance(source_authority_id, str) and source_authority_id.startswith("project:")
        and isinstance(source_revision, str) and bool(source_revision) and len(source_revision) <= 256
        and isinstance(source_sha256, str) and re.fullmatch(r"[0-9a-f]{64}", source_sha256)
        and (trust_layer == ("internal", "condensed") or trust_layer == ("reviewed", "delta"))
        and (trust_layer != ("reviewed", "delta") or kind in {"lesson", "idea", "finding", "project_essence"})
        and isinstance(source_path, str) and bool(source_path) and len(source_path) <= 1024
        and not PurePosixPath(source_path).is_absolute() and "\\" not in source_path and ":" not in source_path
        and not any(ord(char) < 32 or 127 <= ord(char) < 160 or char in "\u2028\u2029" for char in source_path)
        and all(part not in {"", ".", ".."} for part in source_path.split("/"))
    ):
        return False
    suffix = sha256(f"{source_authority_id}\0{source_artifact_id}\0{source_revision}".encode()).hexdigest()[:16]
    if (not document.authority_id.startswith("user-global:")
            or document.artifact_id != f"contribution:{document.authority_id.replace(':', '-')}-{suffix}"
            or document.revision != f"contribution-rev-1-{suffix}"):
        return False
    if trust_layer == ("reviewed", "delta") and (
        metadata.get("lifecycle") != "candidate"
        or metadata.get("processing_layer") != "delta"
        or metadata.get("source_trust") != "internal"
        or metadata.get("canonical") is not False
        or metadata.get("memory_kind") != ("episodic" if kind == "finding" else "semantic")
        or not document.body.strip() or len(document.body.strip()) > 8192
    ):
        return False
    if trust_layer == ("reviewed", "delta") and kind == "lesson":
        try:
            from .lesson_capture import validate_origin
            validate_origin(metadata.get("source_lesson_origin"), source_authority_id)
        except ContractValidationError:
            return False
    if trust_layer == ("reviewed", "delta") and kind in {"idea", "finding"}:
        from .lesson_capture import _EXCEPTIONS, _validate_submitter
        origin = metadata.get("source_record_origin")
        if (not isinstance(origin, dict) or set(origin) != {"attribution", "exception_kind"}
                or metadata.get("source_record_status") != ("possibility" if kind == "idea" else "signal")
                or (kind == "idea" and (origin.get("exception_kind") is not None or "source_exception_kind" in metadata))
                or (kind == "finding" and (not isinstance(metadata.get("source_exception_kind"), str)
                                           or metadata["source_exception_kind"] not in _EXCEPTIONS
                                           or origin.get("exception_kind") != metadata["source_exception_kind"]))):
            return False
        try:
            _validate_submitter(origin["attribution"], source_authority_id)
        except ContractValidationError:
            return False
    if trust_layer == ("reviewed", "delta") and kind == "project_essence":
        origin = metadata.get("source_concept_origin")
        if (not isinstance(origin, dict) or origin.get("project_authority_id") != source_authority_id
                or set(origin) != {"project_authority_id", "concept_id", "revision", "source_id",
                                   "source_link_id", "snapshot_sha256", "relative_path", "content_sha256"}):
            return False
    return True


def feed_reference(document: ManagedMarkdown, query: str, area: str | None,
                   stage: str = "reuse_feed") -> dict[str, Any] | None:
    if not isinstance(stage, str) or stage not in {"reuse_feed", "inbox"} or not valid_reuse_contribution(document, stage):
        raise ContractValidationError("Reuse Feed contribution contract is invalid")
    metadata = document.metadata
    kind = metadata.get("knowledge_kind")
    if kind in {"idea", "finding"}:
        declared_area = metadata.get("knowledge_area")
        if area is not None and declared_area != area:
            return None
        searchable = " ".join((document.artifact_id, str(metadata["source_artifact_id"]),
                                str(declared_area or ""), str(metadata["source_record_status"]),
                                str(metadata.get("source_exception_kind", "")), document.body))
        if query.casefold() not in searchable.casefold():
            return None
        source = {"artifact_id": metadata["source_artifact_id"],
                  "authority_id": metadata["source_authority_id"],
                  "revision": metadata["source_revision"],
                  "content_sha256": metadata["source_content_sha256"],
                  "relative_path": metadata["source_relative_path"],
                  "record_origin": metadata["source_record_origin"]}
        return {"contribution_id": document.artifact_id, "revision": document.revision,
                "content_sha256": document.content_sha256, "text": document.body.strip(),
                "canonical": False, "stage": stage, "lifecycle": "candidate",
                "source_trust": "internal", "knowledge_kind": kind,
                "memory_kind": metadata["memory_kind"], "knowledge_area": declared_area,
                "record_status": metadata["source_record_status"],
                **({"exception_kind": metadata["source_exception_kind"]} if kind == "finding" else {}),
                "source": source, "source_current": "not_checked"}
    if document.metadata.get("knowledge_kind") == "project_essence":
        declared_area = document.metadata.get("knowledge_area")
        if area is not None and declared_area != area:
            return None
        searchable = " ".join((document.artifact_id, str(declared_area or ""), document.body))
        if query.casefold() not in searchable.casefold():
            return None
        return {"contribution_id": document.artifact_id, "revision": document.revision,
                "content_sha256": document.content_sha256, "text": document.body.strip(),
                "canonical": False, "stage": "reuse_feed", "lifecycle": "candidate",
                "source_trust": "internal", "knowledge_kind": "project_essence",
                "knowledge_area": declared_area, "source": document.metadata["source_concept_origin"]}
    if document.metadata.get("knowledge_kind") != "lesson":
        return None
    origin = project_lesson_contribution(document)
    declared_area = document.metadata.get("knowledge_area")
    if area is not None and declared_area != area:
        return None
    searchable = " ".join((document.artifact_id, origin["artifact_id"], str(declared_area or ""), document.body))
    if query.casefold() not in searchable.casefold():
        return None
    return {"contribution_id": document.artifact_id, "revision": document.revision,
            "content_sha256": document.content_sha256, "text": document.body.strip(),
            "canonical": False, "stage": "reuse_feed", "lifecycle": "candidate", "source_trust": "internal",
            **({"knowledge_area": declared_area} if isinstance(declared_area, str) else {}),
            "source": origin, "source_current": "not_checked"}


def validate_global_curation_source(candidate: dict[str, Any], changeset: dict[str, Any], contribution: ManagedMarkdown) -> None:
    binding = candidate.get("contribution_binding")
    if binding is None:
        return
    origin = project_lesson_contribution(contribution)
    expected = {"contribution_id": contribution.artifact_id, "revision": contribution.revision,
                "content_sha256": contribution.content_sha256}
    document = changeset.get("result_document")
    if binding != expected or not isinstance(document, str):
        raise ContractValidationError("global curation Contribution binding is stale")
    metadata, body = parse_markdown_frontmatter(document)
    preview = candidate.get("review_preview")
    if (metadata.get("project_origin") != origin or metadata.get("curation_effect") != {
            key: value for key, value in changeset.items() if key not in {"result_document", "result_sha256"}}
            or not isinstance(preview, dict) or preview.get("source") != origin
            or body != contribution.body):
        raise ContractValidationError("global curation no longer preserves the selected Project Lesson")


def validate_discovery_request(payload: object) -> None:
    if not isinstance(payload, dict) or set(payload) not in (
        {"query", "knowledge_area", "cursor"},
        {"query", "knowledge_area", "cursor", "filters"},
    ):
        raise ContractValidationError("discovery requires its exact request")
    query, area = payload["query"], payload["knowledge_area"]
    if not isinstance(query, str) or len(query) > 256 or "\x00" in query:
        raise ContractValidationError("discovery query is invalid")
    if area is not None and (not isinstance(area, str) or len(area) > 80 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", area)):
        raise ContractValidationError("discovery Area is invalid")
    cursor = payload["cursor"]
    if cursor is not None and (not isinstance(cursor, dict) or set(cursor) != {"binding", "offset"}
                               or type(cursor["offset"]) is not int or cursor["offset"] < 1
                               or not isinstance(cursor["binding"], str) or not re.fullmatch(r"[0-9a-f]{64}", cursor["binding"])):
        raise ContractValidationError("discovery cursor is invalid")


def validate_feed_discovery_request(payload: object) -> None:
    if (not isinstance(payload, dict) or not {"query", "knowledge_area", "cursor"}.issubset(payload)
            or set(payload) - {"query", "knowledge_area", "cursor", "stage", "filters"}
            or not isinstance(payload.get("stage", "reuse_feed"), str)
            or payload.get("stage", "reuse_feed") not in {"reuse_feed", "inbox"}
            or not isinstance(payload.get("filters", {}), dict)):
        raise ContractValidationError("Feed discovery requires its exact request")
    query, area, cursor = payload["query"], payload["knowledge_area"], payload["cursor"]
    if not isinstance(query, str) or len(query) > 256 or "\x00" in query:
        raise ContractValidationError("Feed query is invalid")
    if area is not None and (not isinstance(area, str) or len(area) > 80
                             or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", area)):
        raise ContractValidationError("Feed Area is invalid")
    fields = {"relative_path", "artifact_id", "revision", "content_sha256"}
    if cursor is not None:
        if (not isinstance(cursor, dict) or set(cursor) != {"binding", "position"}
                or not isinstance(cursor.get("binding"), str) or not re.fullmatch(r"[0-9a-f]{64}", cursor["binding"])):
            raise ContractValidationError("Feed cursor is invalid")
        position = cursor.get("position")
        if (not isinstance(position, dict) or set(position) != fields
                or any(not isinstance(value, str) or not value or len(value) > 1024 for value in position.values())
                or not re.fullmatch(r"[0-9a-f]{64}", position["content_sha256"])):
            raise ContractValidationError("Feed cursor is invalid")


def _prior_reuse_lesson(document: ManagedMarkdown) -> bool:
    """Old feed-curation records stay outside the fresh-capture lookup surface."""
    metadata = document.metadata
    return (document.relative_path.rsplit("/", 1)[-1].startswith("lesson-")
            and metadata.get("knowledge_kind") == "lesson"
            and "lesson_origin" not in metadata and "curation_effect" not in metadata
            and all(isinstance(metadata.get(key), str) and metadata[key].strip() for key in
                    ("source_contribution_id", "source_artifact_id", "source_authority_id", "source_revision", "source_content_sha256")))


def discovery_reference(document: ManagedMarkdown, query: str, area: str | None) -> dict[str, Any] | None:
    if _prior_reuse_lesson(document):
        return None
    metadata = document.metadata
    declared_area = metadata.get("knowledge_area")
    if (metadata.get("schema") != "owledge.managed-markdown/1"
            or type(metadata.get("document_version")) is not int or metadata["document_version"] < 1
            or not isinstance(metadata.get("revision"), str) or not metadata["revision"].strip()
            or not isinstance(declared_area, str) or len(declared_area) > 80
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", declared_area)):
        raise ContractValidationError("source reference metadata is malformed")
    if metadata.get("knowledge_kind") in {"idea", "finding"}:
        from .lesson_capture import validate_project_record
        validate_project_record(document)
        kind = metadata["knowledge_kind"]
        name = f"{kind}:" + document.relative_path.rsplit("/", 1)[-1].removeprefix(f"{kind}-").removesuffix(".md")
        if (area is not None and declared_area != area or
                query.casefold() not in (name + " " + declared_area + " " + document.body).casefold()):
            return None
        return {"artifact_id": document.artifact_id, "name": name,
                "knowledge_area": declared_area, "knowledge_kind": kind,
                "memory_kind": metadata["memory_kind"], "record_status": metadata["record_status"],
                "revision": document.revision, "excerpt": document.body.strip()[:240], "canonical": False}
    if metadata.get("knowledge_kind") == "project_essence":
        from .lesson_capture import validate_project_essence, validate_global_essence
        if document.authority_id.startswith("project:"):
            validate_project_essence(document)
            name = "essence:project"
        else:
            validate_global_essence(document)
            name = "essence:" + metadata["project_origin"]["authority_id"].removeprefix("project:")
        if (area is not None and declared_area != area or
                query.casefold() not in (name + " " + declared_area + " " + document.body).casefold()):
            return None
        return {"artifact_id": document.artifact_id, "name": name,
                "knowledge_area": declared_area, "revision": document.revision,
                "excerpt": document.body.strip()[:240], "canonical": metadata["canonical"],
                "concept_current": True}
    if metadata.get("lifecycle") == "accepted" and metadata.get("knowledge_kind") != "lesson":
        source = metadata.get("source_evidence")
        if (not isinstance(source, dict) or set(source) != {"relative_path", "content_sha256", "excerpt", "binding", "trust"}
                or not isinstance(source.get("binding"), dict) or source.get("trust") != "external"
                or not isinstance(source.get("content_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", source["content_sha256"])
                or any(not isinstance(source.get(key), str) or not source[key].strip() for key in ("relative_path", "excerpt"))):
            raise ContractValidationError("source reference evidence is malformed")
    data = reference_data((document,), document.artifact_id)
    if data is None:
        return None
    name = document.relative_path.rsplit("/", 1)[-1].removeprefix("source-").removesuffix(".md")
    if metadata.get("knowledge_kind") == "lesson":
        name = "lesson:" + name.removeprefix("lesson-")
    if area is not None and data["knowledge_area"] != area:
        return None
    if query.casefold() not in (name + " " + str(data["knowledge_area"]) + " " + data["text"]).casefold():
        return None
    return {"artifact_id": data["artifact_id"], "name": name, "knowledge_area": data["knowledge_area"],
            "revision": data["revision"], "excerpt": data["text"][:240]}


def validate_request(payload: dict[str, object]) -> None:
    fields = {"source_search", "source_relative_path", "source_content_sha256", "source_excerpt",
              "source_binding", "proposed_text", "curation_slug", "knowledge_area"}
    if set(payload) not in (fields, fields | {"correction"}) or not isinstance(payload["source_search"], dict) or not isinstance(payload["source_binding"], dict):
        raise ContractValidationError("source Candidate requires its exact bounded request")
    if "correction" in payload:
        base = payload["correction"]
        if (not isinstance(base, dict) or set(base) != {"artifact_id", "revision", "content_sha256"}
                or any(not isinstance(base[key], str) or not base[key] or len(base[key]) > 256 for key in base)
                or not re.fullmatch(r"[0-9a-f]{64}", base["content_sha256"])):
            raise ContractValidationError("correction requires an exact base identity, revision and hash")
    for key in ("curation_slug", "knowledge_area"):
        if not isinstance(payload[key], str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", payload[key]) or len(payload[key]) > 80:
            raise ContractValidationError("source Candidate name or Area is invalid")
    for key, limit in (("proposed_text", 8192), ("source_excerpt", 512), ("source_relative_path", 1024)):
        if not isinstance(payload[key], str) or not payload[key].strip() or len(payload[key]) > limit or "\x00" in payload[key]:
            raise ContractValidationError("source Candidate text is invalid")
    if not isinstance(payload["source_content_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", payload["source_content_sha256"]):
        raise ContractValidationError("source Candidate hash is invalid")


def build_global_curation_candidate(
    active_id: str,
    authority: ManagedMarkdown,
    source: ManagedMarkdown,
    curation_slug: str,
    contribution_ids: list[str],
    project_origin: dict[str, Any] | None,
    global_base: ManagedMarkdown | None,
    replacement_base: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Render one Global reuse Candidate and its exact ChangeSet."""

    candidate_id = f"candidate:{active_id.replace(':', '-')}:curation-{curation_slug}"
    candidate_revision = "candidate-rev-1"
    changeset_id = f"changeset:{active_id.replace(':', '-')}:curation-{curation_slug}"
    idempotency_key = f"curation:{active_id}:{curation_slug}:{source.revision}"
    version = 1
    identity_hash = source.content_sha256
    if global_base is not None:
        version = global_base.metadata["document_version"] + 1
        identity_hash = sha256((global_base.content_sha256 + "\0" + source.content_sha256).encode()).hexdigest()
        suffix = "-refresh-" + identity_hash[:16]
        candidate_id += suffix
        changeset_id += suffix
        idempotency_key = f"curation-refresh:{active_id}:{curation_slug}:{global_base.content_sha256}:{source.content_sha256}"
    result_revision = f"memory-rev-{version}-{identity_hash[:16]}"
    result_relative_path = f".owledge/curated/{curation_slug}.md"
    effect_envelope = {
        "changeset_id": changeset_id, "authority_id": active_id, "base_revision": "absent",
        "policy_revision": authority.metadata.get("policy_revision"),
        "settings_revision": authority.metadata.get("settings_revision"), "idempotency_key": idempotency_key,
        "receipt_id": f"receipt:{active_id.replace(':', '-')}:promote-{curation_slug}",
        "effects": [{"kind": "create", "relative_path": result_relative_path, "result_revision": result_revision}],
    }
    if global_base is not None:
        effect_envelope.update(base_revision=global_base.revision, base_sha256=global_base.content_sha256,
                               base_text_sha256=sha256(global_base.body.strip().encode("utf-8")).hexdigest(),
                               receipt_id=effect_envelope["receipt_id"] + "-" + identity_hash[:16])
        effect_envelope["effects"][0]["kind"] = "replace"
    area_header = ""
    if "knowledge_area" in source.metadata:
        area_header = f"knowledge_area: {json.dumps(source.metadata['knowledge_area'])}\n"
    fresh_headers = ""
    if project_origin is not None:
        fresh_headers = (f"project_origin: {json.dumps(project_origin, ensure_ascii=False)}\n"
                         f"curation_effect: {json.dumps(effect_envelope, ensure_ascii=False)}\n")
    result_document = (
        "---\n"
        "schema: owledge.managed-markdown/1\n"
        f"document_version: {version}\n"
        f"artifact_id: memory:{active_id.replace(':', '-')}-{curation_slug}\n"
        f"authority_id: {active_id}\n"
        f"revision: {result_revision}\n"
        "lifecycle: accepted\n"
        "processing_layer: condensed\n"
        "source_trust: reviewed\n"
        "canonical: true\n"
        "stage: curated\n"
        "knowledge_kind: lesson\n"
        f"{area_header}"
        f"memory_kind: {source.metadata.get('memory_kind', 'semantic')}\n"
        f"source_contribution_id: {source.artifact_id}\n"
        f"source_artifact_id: {source.metadata.get('source_artifact_id')}\n"
        f"source_authority_id: {source.metadata.get('source_authority_id')}\n"
        f"source_revision: {source.metadata.get('source_revision')}\n"
        f"source_content_sha256: {source.metadata.get('source_content_sha256')}\n"
        f"source_record_trust: {source.metadata.get('source_record_trust')}\n"
        f"{fresh_headers}"
        f"{'correction_base: ' + json.dumps(replacement_base, ensure_ascii=False) + chr(10) if global_base is not None else ''}"
        "---\n"
        f"{source.body}"
    )
    result_sha256 = sha256(result_document.encode("utf-8")).hexdigest()
    review_preview = {
        "candidate_id": candidate_id,
        "candidate_revision": candidate_revision,
        "proposed_text": source.body.strip(),
        "source": project_origin or {
            "artifact_id": source.metadata.get("source_artifact_id"),
            "authority_id": source.metadata.get("source_authority_id"),
            "revision": source.metadata.get("source_revision"),
        },
        "target": result_relative_path.removeprefix(".owledge/"),
        "content_sha256": result_sha256,
    }
    if global_base is not None:
        review_preview["base"] = {**replacement_base, "text": global_base.body.strip()}
        review_preview["old_source"] = global_base.metadata["project_origin"]
    if "knowledge_area" in source.metadata:
        review_preview["knowledge_area"] = source.metadata["knowledge_area"]
    if project_origin is not None:
        review_preview.update(idempotency_key=idempotency_key,
                              expected_policy_revision=authority.metadata.get("policy_revision"),
                              expected_settings_revision=authority.metadata.get("settings_revision"))
    candidate = {
        "candidate_id": candidate_id,
        "authority_id": active_id,
        "candidate_revision": candidate_revision,
        "lifecycle": "candidate",
        "candidate_kind": "global_curation",
        "contribution_ids": list(contribution_ids),
        "review_preview": review_preview,
    }
    if project_origin is not None:
        candidate["contribution_binding"] = {"contribution_id": source.artifact_id, "revision": source.revision,
                                             "content_sha256": source.content_sha256}
    if global_base is not None:
        candidate["replacement_binding"] = dict(replacement_base)
    changeset = {**effect_envelope, "result_document": result_document, "result_sha256": result_sha256}
    return candidate, changeset


def build_candidate(authority: ManagedMarkdown, payload: dict[str, Any], hit: dict[str, Any],
                    base: ManagedMarkdown | None = None, *, refresh: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    """Render one reviewed creation or exact-base source correction."""
    active = authority.authority_id
    prefix = active.replace(":", "-")
    slug = payload["curation_slug"]
    candidate_id = f"candidate:{prefix}:source-{slug}"
    changeset_id = f"changeset:{prefix}:source-{slug}"
    artifact_id = f"memory:{prefix}-source-{slug}"
    source = {"relative_path": hit["relative_path"], "content_sha256": hit["content_sha256"],
              "excerpt": hit["snippet"], "binding": hit["source_binding"], "trust": "external"}
    proposed = payload["proposed_text"].strip()
    source_hash = sha256(json.dumps(source, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    identity_hash = sha256((source_hash + "\0" + proposed + "\0" + payload["knowledge_area"]).encode()).hexdigest()
    version = 1
    if base is not None:
        expected = {"artifact_id": base.artifact_id, "revision": base.revision, "content_sha256": base.content_sha256}
        old_source = base.metadata.get("source_evidence")
        same_logical_source = (isinstance(old_source, dict)
                               and old_source.get("relative_path") == source["relative_path"]
                               and isinstance(old_source.get("binding"), dict)
                               and old_source["binding"].get("link_artifact_id") == source["binding"].get("link_artifact_id")
                               and old_source["binding"].get("linked_authority_id") == source["binding"].get("linked_authority_id"))
        if (payload.get("correction") != expected or base.artifact_id != artifact_id
                or reference_data((base,), artifact_id) is None or base.authority_id != active
                or base.metadata.get("knowledge_area") != payload["knowledge_area"]
                or (not refresh and old_source != source)
                or (refresh and not same_logical_source)
                or type(base.metadata.get("document_version")) is not int):
            raise ContractValidationError("correction base or preserved provenance differs")
        version = base.metadata["document_version"] + 1
        identity_hash = sha256((identity_hash + base.content_sha256).encode()).hexdigest()
        suffix = ("-refresh-" if refresh else "-correction-") + identity_hash[:16]
        candidate_id += suffix
        changeset_id += suffix
    revision = f"memory-rev-{version}-{identity_hash[:16]}"
    path = f".owledge/curated/source-{slug}.md"
    idempotency_key = f"source-curation:{active}:{slug}:{identity_hash}"
    effect_envelope = {"changeset_id": changeset_id, "authority_id": active, "base_revision": "absent",
                       "policy_revision": authority.metadata["policy_revision"], "settings_revision": authority.metadata["settings_revision"],
                       "idempotency_key": idempotency_key, "receipt_id": f"receipt:{prefix}:promote-source-{slug}",
                       "effects": [{"kind": "create", "relative_path": path, "result_revision": revision}]}
    if base is not None:
        effect_envelope.update(base_revision=base.revision, base_sha256=base.content_sha256,
                               base_text_sha256=sha256(base.body.strip().encode("utf-8")).hexdigest(),
                               receipt_id=effect_envelope["receipt_id"] + "-" + identity_hash[:16])
        effect_envelope["effects"][0]["kind"] = "replace"
    metadata = {"schema": "owledge.managed-markdown/1", "document_version": version,
                "artifact_id": artifact_id, "authority_id": active, "revision": revision,
                "lifecycle": "accepted", "processing_layer": "condensed", "source_trust": "reviewed",
                "canonical": True, "stage": "curated", "knowledge_kind": "reference", "memory_kind": "semantic",
                "knowledge_area": payload["knowledge_area"], "source_evidence": source, "curation_effect": effect_envelope}
    if base is not None:
        metadata["correction_base"] = payload["correction"]
        if refresh:
            metadata["source_refresh"] = {"old_source": old_source, "new_source": source}
    document = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items()) + "\n---\n\n" + proposed + "\n"
    digest = sha256(document.encode("utf-8")).hexdigest()
    preview = {"candidate_id": candidate_id, "candidate_revision": "candidate-rev-1", "artifact_id": artifact_id,
               "proposed_text": proposed, "source": source, "target": path.removeprefix(".owledge/"),
               "content_sha256": digest, "knowledge_area": payload["knowledge_area"], "idempotency_key": idempotency_key,
               "expected_policy_revision": authority.metadata["policy_revision"],
               "expected_settings_revision": authority.metadata["settings_revision"]}
    if base is not None:
        preview["base"] = {**payload["correction"], "text": base.body.strip()}
        if refresh:
            preview["old_source"] = old_source
            preview["refresh_kind"] = "exact_source_repreview"
    candidate = {"candidate_id": candidate_id, "authority_id": active, "candidate_revision": "candidate-rev-1",
                 "lifecycle": "candidate", "candidate_kind": "source_curation", "review_preview": preview}
    if refresh:
        candidate["source_refresh_binding"] = {"base": payload["correction"],
                                                "old_source": old_source, "new_source": source}
    changeset = {**effect_envelope, "result_document": document, "result_sha256": digest}
    return candidate, changeset


def validate_curation_effect(candidate: dict[str, Any], changeset: dict[str, Any]) -> None:
    """Recheck approved content and its effect at preview, promotion and recovery."""
    if candidate.get("candidate_kind") == "global_essence":
        from .lesson_capture import validate_global_essence
        preview, document = candidate.get("review_preview"), changeset.get("result_document")
        effects = changeset.get("effects")
        if (not isinstance(preview, dict) or not isinstance(document, str)
                or not isinstance(effects, list) or len(effects) != 1
                or not isinstance(effects[0], dict)):
            raise ContractValidationError("Global Essence preview is incomplete")
        record = parse_managed_markdown(str(effects[0].get("relative_path")), document,
                                        encoded_document=document.encode("utf-8"))
        validate_global_essence(record)
        origin = record.metadata["project_origin"]
        slug = "essence-" + origin["authority_id"].removeprefix("project:")
        prefix = record.authority_id.replace(":", "-")
        suffix = "" if record.metadata["document_version"] == 1 else "-refresh-" + record.revision.rsplit("-", 1)[-1]
        digest = sha256(document.encode("utf-8")).hexdigest()
        exact = {"contribution_id": origin["contribution_id"],
                 "revision": origin["contribution_revision"],
                 "content_sha256": origin["contribution_sha256"]}
        envelope = {key: value for key, value in changeset.items() if key not in {"result_document", "result_sha256"}}
        if (candidate.get("authority_id") != record.authority_id
                or candidate.get("candidate_id") != f"candidate:{prefix}:{slug}{suffix}"
                or preview.get("candidate_id") != candidate.get("candidate_id")
                or changeset.get("changeset_id") != f"changeset:{prefix}:{slug}{suffix}"
                or changeset.get("receipt_id") != f"receipt:{prefix}:promote-{slug}{suffix}"
                or candidate.get("contribution_binding") != exact
                or candidate.get("candidate_revision") not in {"candidate-rev-1", "candidate-rev-2-reviewed"}
                or preview.get("candidate_revision") != "candidate-rev-1"
                or changeset.get("result_sha256") != digest
                or preview.get("content_sha256") != digest
                or preview.get("artifact_id") != record.artifact_id
                or preview.get("target") != record.relative_path.removeprefix(".owledge/")
                or preview.get("proposed_text") != record.body.strip()
                or preview.get("source") != {"concept": record.metadata["concept_origin"], "project": origin}
                or preview.get("record_kind") != "project_essence"
                or preview.get("record_status") != "summary"
                or preview.get("canonical") is not True
                or preview.get("knowledge_area") != record.metadata["knowledge_area"]
                or preview.get("idempotency_key") != changeset.get("idempotency_key")
                or preview.get("expected_policy_revision") != changeset.get("policy_revision")
                or preview.get("expected_settings_revision") != changeset.get("settings_revision")
                or record.metadata.get("curation_effect") != envelope
                or candidate.get("lifecycle") == "reviewed" and candidate.get("reviewed_result_sha256") != digest):
            raise ContractValidationError("Global Essence reviewed effect differs")
        if record.metadata["document_version"] > 1:
            base = preview.get("base")
            if (not isinstance(base, dict) or set(base) != {"artifact_id", "revision", "content_sha256", "text"}
                    or record.metadata.get("correction_base") != {key: base[key] for key in ("artifact_id", "revision", "content_sha256")}
                    or sha256(str(base["text"]).encode("utf-8")).hexdigest() != changeset.get("base_text_sha256")):
                raise ContractValidationError("Global Essence refresh preview differs")
        return
    if candidate.get("candidate_kind") == "project_essence":
        from .lesson_capture import validate_project_essence
        preview, document = candidate.get("review_preview"), changeset.get("result_document")
        if not isinstance(preview, dict) or not isinstance(document, str):
            raise ContractValidationError("Project Essence preview is incomplete")
        path = ".owledge/curated/essence-project.md"
        record = parse_managed_markdown(path, document, encoded_document=document.encode("utf-8"))
        validate_project_essence(record)
        metadata = record.metadata
        prefix = record.authority_id.replace(":", "-")
        suffix = "" if metadata["document_version"] == 1 else "-refresh-" + record.revision.rsplit("-", 1)[-1]
        expected_candidate = f"candidate:{prefix}:essence-project{suffix}"
        expected_changeset = f"changeset:{prefix}:essence-project{suffix}"
        envelope = {key: value for key, value in changeset.items() if key not in {"result_document", "result_sha256"}}
        digest = sha256(document.encode("utf-8")).hexdigest()
        if (candidate.get("authority_id") != record.authority_id
                or candidate.get("candidate_id") != expected_candidate
                or preview.get("candidate_id") != expected_candidate
                or changeset.get("changeset_id") != expected_changeset
                or changeset.get("receipt_id") != f"receipt:{prefix}:promote-essence-project{suffix}"
                or candidate.get("candidate_revision") not in {"candidate-rev-1", "candidate-rev-2-reviewed"}
                or preview.get("candidate_revision") != "candidate-rev-1"
                or changeset.get("result_sha256") != digest
                or preview.get("content_sha256") != digest
                or preview.get("artifact_id") != record.artifact_id
                or preview.get("target") != "curated/essence-project.md"
                or preview.get("proposed_text") != record.body.strip()
                or preview.get("source") != metadata["concept_origin"]
                or preview.get("submitted_by") != metadata["essence_submission"]
                or candidate.get("submitted_by") != preview.get("submitted_by")
                or preview.get("record_kind") != "project_essence"
                or preview.get("record_status") != "summary"
                or preview.get("canonical") is not False
                or preview.get("knowledge_area") != metadata["knowledge_area"]
                or preview.get("idempotency_key") != changeset.get("idempotency_key")
                or preview.get("expected_policy_revision") != changeset.get("policy_revision")
                or preview.get("expected_settings_revision") != changeset.get("settings_revision")
                or metadata.get("curation_effect") != envelope
                or candidate.get("lifecycle") == "reviewed" and candidate.get("reviewed_result_sha256") != digest):
            raise ContractValidationError("Project Essence reviewed effect differs")
        if metadata["document_version"] > 1:
            base = preview.get("base")
            if (not isinstance(base, dict) or set(base) != {"artifact_id", "revision", "content_sha256", "text"}
                    or metadata.get("correction_base") != {key: base[key] for key in ("artifact_id", "revision", "content_sha256")}
                    or sha256(str(base["text"]).encode("utf-8")).hexdigest() != changeset.get("base_text_sha256")):
                raise ContractValidationError("Project Essence refresh preview differs")
        return
    if candidate.get("candidate_kind") == "project_record":
        from .lesson_capture import validate_project_record
        preview, document = candidate.get("review_preview"), changeset.get("result_document")
        if not isinstance(preview, dict) or not isinstance(document, str):
            raise ContractValidationError("Project record preview is incomplete")
        metadata, body = parse_markdown_frontmatter(document)
        authority = candidate.get("authority_id")
        if not isinstance(authority, str) or not authority.startswith("project:"):
            raise ContractValidationError("Project record authority is invalid")
        path = str(metadata.get("artifact_id", "")).removeprefix(f"memory:{authority.replace(':', '-')}-")
        expected_path = f".owledge/curated/{path}.md"
        record = parse_managed_markdown(expected_path, document, encoded_document=document.encode("utf-8"))
        validate_project_record(record)
        prefix = authority.replace(":", "-")
        correcting = metadata["document_version"] > 1
        suffix = "-correction-" + record.revision.rsplit("-", 1)[-1] if correcting else ""
        expected_candidate = f"candidate:{prefix}:{path}{suffix}"
        expected_changeset = f"changeset:{prefix}:{path}{suffix}"
        if (candidate.get("candidate_id") != expected_candidate
                or changeset.get("changeset_id") != expected_changeset
                or preview.get("candidate_id") != expected_candidate
                or preview.get("candidate_revision") != "candidate-rev-1"
                or candidate.get("candidate_revision") not in {"candidate-rev-1", "candidate-rev-2-reviewed"}
                or changeset.get("receipt_id") != f"receipt:{prefix}:promote-{path}{suffix}"):
            raise ContractValidationError("Project record identity differs from staged Candidate")
        envelope = {key: value for key, value in changeset.items() if key not in {"result_document", "result_sha256"}}
        digest = sha256(document.encode("utf-8")).hexdigest()
        if (record.authority_id != authority or metadata.get("curation_effect") != envelope
                or changeset.get("result_sha256") != digest
                or preview.get("content_sha256") != digest or preview.get("target") != expected_path.removeprefix(".owledge/")
                or preview.get("artifact_id") != record.artifact_id or preview.get("proposed_text") != body.strip()
                or preview.get("source") != metadata.get("record_origin")
                or preview.get("record_kind") != metadata.get("knowledge_kind")
                or preview.get("record_status") != metadata.get("record_status")
                or preview.get("knowledge_area") != metadata.get("knowledge_area")
                or preview.get("submitted_by") != (metadata.get("correction_submission") if correcting
                                                   else metadata["record_origin"]["attribution"])
                or (metadata.get("knowledge_kind") == "finding"
                    and (correcting or "exception_kind" in preview)
                    and preview.get("exception_kind") != metadata.get("exception_kind"))
                or candidate.get("submitted_by") != preview.get("submitted_by")
                or preview.get("idempotency_key") != changeset.get("idempotency_key")
                or preview.get("expected_policy_revision") != changeset.get("policy_revision")
                or preview.get("expected_settings_revision") != changeset.get("settings_revision")
                or candidate.get("lifecycle") == "reviewed" and candidate.get("reviewed_result_sha256") != digest):
            raise ContractValidationError("Project record reviewed effect differs")
        if correcting:
            base = preview.get("base")
            if (not isinstance(base, dict) or set(base) != {"artifact_id", "revision", "content_sha256", "text"}
                    or metadata.get("correction_base") != {key: base[key] for key in ("artifact_id", "revision", "content_sha256")}
                    or sha256(str(base["text"]).encode("utf-8")).hexdigest() != changeset.get("base_text_sha256")):
                raise ContractValidationError("Project record correction preview differs")
        return
    if candidate.get("candidate_kind") not in {"global_curation", "source_curation", "lesson_capture"}:
        return
    preview, document = candidate.get("review_preview"), changeset.get("result_document")
    effects = changeset.get("effects")
    if (not isinstance(preview, dict) or not isinstance(document, str) or not isinstance(effects, list)
            or len(effects) != 1 or not isinstance(effects[0], dict)):
        raise ContractValidationError("curation effect is incomplete")
    metadata, body = parse_markdown_frontmatter(document)
    authority = candidate.get("authority_id")
    if not isinstance(authority, str):
        raise ContractValidationError("curation authority is missing")
    prefix = f"memory:{authority.replace(':', '-')}-"
    artifact_id = metadata.get("artifact_id")
    if not isinstance(artifact_id, str) or not artifact_id.startswith(prefix):
        raise ContractValidationError("curation result identity is invalid")
    slug = artifact_id.removeprefix(prefix)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ContractValidationError("curation destination identity is invalid")
    expected_path = f".owledge/curated/{slug}.md"
    digest = sha256(document.encode("utf-8")).hexdigest()
    replacing = (effects[0].get("kind") == "replace"
                 and candidate.get("candidate_kind") in {"global_curation", "source_curation", "lesson_capture"})
    if replacing:
        base = preview.get("base")
        if (not isinstance(base, dict) or set(base) != {"artifact_id", "revision", "content_sha256", "text"}
                or metadata.get("correction_base") != {key: value for key, value in base.items() if key != "text"}
                or not isinstance(base.get("text"), str)
                or sha256(base["text"].encode("utf-8")).hexdigest() != changeset.get("base_text_sha256")
                or base.get("artifact_id") != artifact_id or base.get("revision") != changeset.get("base_revision")
                or not isinstance(base.get("revision"), str) or base["revision"] == "absent"
                or base.get("content_sha256") != changeset.get("base_sha256")
                or not isinstance(base.get("content_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", base["content_sha256"])
                or type(metadata.get("document_version")) is not int or metadata["document_version"] < 2):
            raise ContractValidationError("correction review base is invalid")
        if candidate.get("candidate_kind") == "lesson_capture":
            from .lesson_capture import validate_project_lesson
            validate_project_lesson(parse_managed_markdown(expected_path, document, encoded_document=document.encode("utf-8")))
        if candidate.get("candidate_kind") == "global_curation":
            replacement = candidate.get("replacement_binding")
            if (replacement != {key: value for key, value in base.items() if key != "text"}
                    or preview.get("old_source") is None):
                raise ContractValidationError("Global replacement binding is invalid")
            validate_project_origin(preview["old_source"], authority)
            validate_global_reuse_lesson(parse_managed_markdown(expected_path, document, encoded_document=document.encode("utf-8")))
    if (effects[0] != {"kind": "replace" if replacing else "create", "relative_path": expected_path, "result_revision": metadata.get("revision")}
            or (not replacing and changeset.get("base_revision") != "absent") or changeset.get("authority_id") != authority
            or metadata.get("authority_id") != authority or metadata.get("lifecycle") != "accepted"
            or metadata.get("canonical") is not True or metadata.get("stage") != "curated"
            or metadata.get("source_trust") != "reviewed" or changeset.get("result_sha256") != digest
            or preview.get("content_sha256") != digest or preview.get("target") != expected_path.removeprefix(".owledge/")
            or preview.get("proposed_text") != body.strip()):
        raise ContractValidationError("curation result and effect binding differ")
    expected_source = {"artifact_id": metadata.get("source_artifact_id"), "authority_id": metadata.get("source_authority_id"),
                       "revision": metadata.get("source_revision")}
    if candidate.get("candidate_kind") == "global_curation" and candidate.get("contribution_binding") is not None:
        expected_source = metadata.get("project_origin")
        validate_project_origin(expected_source, authority)
        envelope = {key: value for key, value in changeset.items() if key not in {"result_document", "result_sha256"}}
        if (metadata.get("curation_effect") != envelope or metadata.get("knowledge_kind") != "lesson"
                or not slug.startswith("lesson-") or preview.get("idempotency_key") != changeset.get("idempotency_key")
                or preview.get("expected_policy_revision") != changeset.get("policy_revision")
                or preview.get("expected_settings_revision") != changeset.get("settings_revision")):
            raise ContractValidationError("global curation envelope is not the reviewed effect")
    if candidate.get("candidate_kind") in {"source_curation", "lesson_capture"}:
        lesson = candidate.get("candidate_kind") == "lesson_capture"
        expected_source = metadata.get("lesson_origin" if lesson else "source_evidence")
        if not lesson:
            refresh = metadata.get("source_refresh")
            binding = candidate.get("source_refresh_binding")
            if (refresh is None) != (binding is None):
                raise ContractValidationError("source refresh marker differs")
            if refresh is not None:
                old_source = refresh.get("old_source") if isinstance(refresh, dict) else None
                new_source = refresh.get("new_source") if isinstance(refresh, dict) else None
                if (not replacing or not isinstance(refresh, dict) or not isinstance(old_source, dict)
                        or not isinstance(new_source, dict) or new_source != expected_source
                        or binding != {"base": metadata.get("correction_base"),
                                       "old_source": old_source, "new_source": new_source}
                        or preview.get("old_source") != old_source
                        or preview.get("refresh_kind") != "exact_source_repreview"
                        or not isinstance(old_source.get("binding"), dict)
                        or not isinstance(new_source.get("binding"), dict)
                        or old_source.get("relative_path") != new_source.get("relative_path")
                        or any(old_source["binding"].get(key) != new_source["binding"].get(key)
                               for key in ("link_artifact_id", "linked_authority_id"))
                        or not str(candidate.get("candidate_id", "")).startswith(
                            f"candidate:{authority.replace(':', '-')}:source-{slug.removeprefix('source-')}-refresh-")):
                    raise ContractValidationError("source refresh binding is invalid")
            elif preview.get("old_source") is not None or preview.get("refresh_kind") is not None:
                raise ContractValidationError("ordinary source correction has a refresh marker")
        if lesson:
            from .lesson_capture import validate_origin
            validate_origin(expected_source, authority)
        envelope = {key: value for key, value in changeset.items() if key not in {"result_document", "result_sha256"}}
        if (metadata.get("curation_effect") != envelope or metadata.get("knowledge_kind") != ("lesson" if lesson else "reference")
                or not slug.startswith("lesson-" if lesson else "source-") or preview.get("artifact_id") != artifact_id
                or preview.get("knowledge_area") != metadata.get("knowledge_area")
                or preview.get("idempotency_key") != changeset.get("idempotency_key")
                or preview.get("expected_policy_revision") != changeset.get("policy_revision")
                or preview.get("expected_settings_revision") != changeset.get("settings_revision")):
            raise ContractValidationError("source curation envelope is not the reviewed effect")
    if preview.get("source") != expected_source:
        raise ContractValidationError("curation source preview differs from result")
    if preview.get("knowledge_area") != metadata.get("knowledge_area"):
        raise ContractValidationError("curation Area preview differs from result")
    if candidate.get("lifecycle") == "reviewed" and candidate.get("reviewed_result_sha256") != digest:
        raise ContractValidationError("curation approval no longer binds the effect")


def reference_data(documents: tuple[ManagedMarkdown, ...], artifact_id: str) -> dict[str, Any] | None:
    lessons = [item for item in documents if item.artifact_id == artifact_id and not _prior_reuse_lesson(item)
               and item.metadata.get("canonical") is True and item.metadata.get("lifecycle") == "accepted"
               and item.metadata.get("stage") == "curated" and item.metadata.get("knowledge_kind") == "lesson"
               and item.metadata.get("source_trust") == "reviewed"]
    if lessons:
        if len(lessons) != 1:
            raise ContractValidationError("Lesson identity is ambiguous")
        item = lessons[0]
        source = item.metadata.get("project_origin")
        if source is not None:
            validate_project_origin(source, item.authority_id)
        else:
            from .lesson_capture import validate_origin
            source = item.metadata.get("lesson_origin")
            validate_origin(source, item.authority_id)
        return {"artifact_id": item.artifact_id, "revision": item.revision, "content_sha256": item.content_sha256,
                "text": item.body.strip(), "knowledge_kind": "lesson", "knowledge_area": item.metadata.get("knowledge_area"),
                "source": source}
    matches = [item for item in documents if item.artifact_id == artifact_id and
               item.metadata.get("canonical") is True and item.metadata.get("lifecycle") == "accepted" and
               item.metadata.get("stage") == "curated" and item.metadata.get("knowledge_kind") == "reference" and
               item.metadata.get("source_trust") == "reviewed" and
               isinstance(item.metadata.get("source_evidence"), dict)]
    if len(matches) != 1:
        return None
    item = matches[0]
    return {"artifact_id": item.artifact_id, "revision": item.revision, "content_sha256": item.content_sha256, "text": item.body.strip(),
            "knowledge_area": item.metadata.get("knowledge_area"), "source": item.metadata["source_evidence"]}
