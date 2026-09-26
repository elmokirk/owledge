"""Bounded reported Lesson proposals using the existing reviewed ChangeSet loop."""
from __future__ import annotations

from hashlib import sha256
import json
import re

from .artifacts import ManagedMarkdown, parse_markdown_frontmatter
from .contracts import ContractValidationError


def validate_project_lesson(document: ManagedMarkdown) -> None:
    metadata = document.metadata
    authority = document.authority_id
    prefix = f"memory:{authority.replace(':', '-')}-lesson-"
    slug = document.artifact_id.removeprefix(prefix)
    envelope = metadata.get("curation_effect")
    effects = envelope.get("effects") if isinstance(envelope, dict) else None
    effect = effects[0] if isinstance(effects, list) and len(effects) == 1 and isinstance(effects[0], dict) else None
    replacing = isinstance(effect, dict) and effect.get("kind") == "replace"
    correction = metadata.get("correction_base")
    if (not authority.startswith("project:") or not document.artifact_id.startswith(prefix)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or len(slug) > 80
            or document.relative_path != f".owledge/curated/lesson-{slug}.md"
            or metadata.get("schema") != "owledge.managed-markdown/1"
            or type(metadata.get("document_version")) is not int or metadata["document_version"] < 1
            or metadata.get("lifecycle") != "accepted" or metadata.get("processing_layer") != "delta"
            or metadata.get("source_trust") != "reviewed" or metadata.get("canonical") is not True
            or metadata.get("stage") != "curated" or metadata.get("knowledge_kind") != "lesson"
            or metadata.get("memory_kind") != "semantic" or "project_origin" in metadata
            or not isinstance(metadata.get("knowledge_area"), str)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["knowledge_area"])
            or not isinstance(envelope, dict) or envelope.get("authority_id") != authority
            or not isinstance(effect, dict) or effect.get("kind") not in {"create", "replace"}
            or effect.get("relative_path") != document.relative_path or effect.get("result_revision") != document.revision
            or any(not isinstance(envelope.get(key), str) or not envelope[key] for key in
                   ("changeset_id", "base_revision", "policy_revision", "settings_revision", "idempotency_key", "receipt_id"))):
        raise ContractValidationError("Project Lesson contract is invalid")
    if replacing:
        if (metadata["document_version"] < 2 or not isinstance(correction, dict)
                or set(correction) != {"artifact_id", "revision", "content_sha256"}
                or correction.get("artifact_id") != document.artifact_id
                or correction.get("revision") != envelope.get("base_revision")
                or correction.get("content_sha256") != envelope.get("base_sha256")
                or not isinstance(envelope.get("base_text_sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", envelope["base_text_sha256"])):
            raise ContractValidationError("Project Lesson correction contract is invalid")
        submission = metadata.get("correction_submission")
        if submission is not None:
            _validate_submitter(submission, authority)
    elif envelope.get("base_revision") != "absent" or correction is not None:
        raise ContractValidationError("Project Lesson creation contract is invalid")
    elif "correction_submission" in metadata:
        raise ContractValidationError("Project Lesson creation cannot claim a correction submitter")
    validate_origin(metadata.get("lesson_origin"), authority)


def validate_request(payload: object) -> None:
    fields = {"name", "knowledge_area", "text", "origin", "conditions", "verification", "limitations"}
    correction_fields = {"name", "text", "correction"}
    if not isinstance(payload, dict):
        raise ContractValidationError("Lesson requires its exact bounded request")
    keys = frozenset(payload)
    if keys not in {frozenset(fields), frozenset(correction_fields)}:
        raise ContractValidationError("Lesson requires its exact bounded request")
    for key in (("name", "knowledge_area") if keys == fields else ("name",)):
        value = payload[key]
        if not isinstance(value, str) or len(value) > 80 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
            raise ContractValidationError("Lesson name or Area is invalid")
    if keys == correction_fields:
        correction = payload["correction"]
        if (not isinstance(correction, dict) or set(correction) != {"artifact_id", "revision", "content_sha256"}
                or any(not isinstance(correction.get(key), str) or not correction[key] or len(correction[key]) > 256
                       for key in correction)
                or not re.fullmatch(r"[0-9a-f]{64}", correction["content_sha256"])):
            raise ContractValidationError("Lesson correction base is invalid")
        text = payload["text"]
        if not isinstance(text, str) or not text.strip() or len(text) > 8192 or any(char in text for char in "\x00\x85\u2028\u2029"):
            raise ContractValidationError("Lesson correction text is invalid")
        return
    for key in fields - {"name", "knowledge_area"}:
        value = payload[key]
        if (not isinstance(value, str) or not value.strip() or len(value) > (8192 if key == "text" else 2048)
                or any(char in value for char in "\x00\x85\u2028\u2029")):
            raise ContractValidationError("Lesson text or reported context is invalid")


def validate_origin(source: object, authority_id: str) -> None:
    if (not isinstance(source, dict)
            or set(source) != {"trust", "origin", "conditions", "verification", "limitations", "attribution"}
            or source.get("trust") != "reported"):
        raise ContractValidationError("Lesson origin must remain reported")
    for key in ("origin", "conditions", "verification", "limitations"):
        value = source[key]
        if (not isinstance(value, str) or not value.strip() or len(value) > 2048
                or any(char in value for char in "\x00\x85\u2028\u2029")):
            raise ContractValidationError("Lesson context is invalid")
    attribution = source["attribution"]
    if (not isinstance(attribution, dict) or set(attribution) != {"principal_id", "authority_id", "operation_id"}
            or attribution.get("authority_id") != authority_id
            or any(not isinstance(attribution.get(key), str) or not attribution[key].strip()
                   or len(attribution[key]) > 256
                   or any(ord(char) < 32 or 127 <= ord(char) < 160 or char in "\u2028\u2029"
                          for char in attribution[key]) for key in attribution)):
        raise ContractValidationError("Lesson attribution is invalid")


def build_candidate(authority: ManagedMarkdown, payload: dict, principal_id: str, operation_id: str,
                    base: ManagedMarkdown | None = None):
    validate_request(payload)
    submitted_by = {"principal_id": principal_id, "authority_id": authority.authority_id,
                    "operation_id": operation_id}
    _validate_submitter(submitted_by, authority.authority_id)
    active = authority.authority_id
    prefix = active.replace(":", "-")
    slug = "lesson-" + payload["name"]
    correcting = base is not None
    if correcting:
        expected_id = f"memory:{prefix}-{slug}"
        correction = payload.get("correction")
        metadata = base.metadata
        validate_project_lesson(base)
        expected_base = {"artifact_id": base.artifact_id, "revision": base.revision, "content_sha256": base.content_sha256}
        if (not active.startswith("project:") or correction != expected_base or base.artifact_id != expected_id
                or base.authority_id != active):
            raise ContractValidationError("Lesson correction base is not an accepted Project Lesson")
        source = metadata.get("lesson_origin")
        area = metadata["knowledge_area"]
        version = metadata["document_version"] + 1
    else:
        source = {"trust": "reported", **{key: payload[key].strip() for key in ("origin", "conditions", "verification", "limitations")},
                  "attribution": {"principal_id": principal_id, "authority_id": active, "operation_id": operation_id}}
        area = payload["knowledge_area"]
        version = 1
    validate_origin(source, active)
    text = payload["text"].strip()
    identity = sha256(json.dumps({"source": source, "text": text, "area": area,
                                  **({"base": base.content_sha256} if correcting else {})},
                                 sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    artifact_id = f"memory:{prefix}-{slug}"
    suffix = "-correction-" + identity[:16] if correcting else ""
    candidate_id = f"candidate:{prefix}:{slug}{suffix}"
    revision = f"memory-rev-{version}-" + identity[:16]
    path = f".owledge/curated/{slug}.md"
    envelope = {"changeset_id": f"changeset:{prefix}:{slug}{suffix}", "authority_id": active,
                "base_revision": base.revision if correcting else "absent",
                "policy_revision": authority.metadata["policy_revision"], "settings_revision": authority.metadata["settings_revision"],
                "idempotency_key": f"lesson-{'correction' if correcting else 'capture'}:{active}:{payload['name']}:{identity}",
                "receipt_id": f"receipt:{prefix}:promote-{slug}{suffix}",
                "effects": [{"kind": "replace" if correcting else "create", "relative_path": path, "result_revision": revision}]}
    if correcting:
        envelope.update(base_sha256=base.content_sha256,
                        base_text_sha256=sha256(base.body.strip().encode("utf-8")).hexdigest())
    metadata = {"schema": "owledge.managed-markdown/1", "document_version": version, "artifact_id": artifact_id,
                "authority_id": active, "revision": revision, "lifecycle": "accepted", "processing_layer": "delta",
                "source_trust": "reviewed", "canonical": True, "stage": "curated", "knowledge_kind": "lesson",
                "memory_kind": "semantic", "knowledge_area": area,
                "lesson_origin": source, "curation_effect": envelope}
    if correcting:
        metadata["correction_base"] = payload["correction"]
        metadata["correction_submission"] = submitted_by
    document = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items()) + "\n---\n\n" + text + "\n"
    if len(document.encode("utf-8")) > 65_536:
        raise ContractValidationError("Lesson exceeds the bounded curated read budget")
    digest = sha256(document.encode()).hexdigest()
    preview = {"candidate_id": candidate_id, "candidate_revision": "candidate-rev-1", "artifact_id": artifact_id,
               "proposed_text": text, "source": source, "target": path.removeprefix(".owledge/"),
               "submitted_by": submitted_by,
               "content_sha256": digest, "knowledge_area": area, "idempotency_key": envelope["idempotency_key"],
               "expected_policy_revision": envelope["policy_revision"], "expected_settings_revision": envelope["settings_revision"]}
    if correcting:
        preview["base"] = {**payload["correction"], "text": base.body.strip()}
    return ({"candidate_id": candidate_id, "authority_id": active, "candidate_revision": "candidate-rev-1",
             "lifecycle": "candidate", "candidate_kind": "lesson_capture", "submitted_by": submitted_by,
             "review_preview": preview},
            {**envelope, "result_document": document, "result_sha256": digest})


def _validate_submitter(value: object, authority_id: str) -> None:
    if (not isinstance(value, dict) or set(value) != {"principal_id", "authority_id", "operation_id"}
            or value.get("authority_id") != authority_id
            or any(not isinstance(value.get(key), str) or not value[key].strip()
                   or len(value[key]) > 256
                   or any(ord(char) < 32 or 127 <= ord(char) < 160 or char in "\u2028\u2029"
                          for char in value[key]) for key in value)):
        raise ContractValidationError("Lesson submitter is invalid")


def validate_candidate_submitter(candidate: dict, authority_id: str, result_document: str,
                                 *, allow_legacy: bool = False) -> None:
    submitter = candidate.get("submitted_by")
    preview = candidate.get("review_preview")
    result_metadata, _ = parse_markdown_frontmatter(result_document)
    if (allow_legacy and "submitted_by" not in candidate and isinstance(preview, dict)
            and "submitted_by" not in preview and "correction_submission" not in result_metadata):
        return
    _validate_submitter(submitter, authority_id)
    if not isinstance(preview, dict) or preview.get("submitted_by") != submitter:
        raise ContractValidationError("Lesson review submitter does not match Candidate")
    expected = (result_metadata.get("correction_submission") if "correction_base" in result_metadata
                else (result_metadata.get("lesson_origin") or {}).get("attribution"))
    if expected != submitter:
        raise ContractValidationError("Lesson submitter does not match hashed result provenance")


def essence_origin(binding: dict) -> dict:
    """Flatten a designation without its private Project workspace path."""
    return {key: binding[key] for key in ("project_authority_id", "concept_id", "revision",
            "source_id", "source_link_id", "snapshot_sha256", "relative_path", "content_sha256")}


def validate_project_essence(document: ManagedMarkdown) -> None:
    metadata = document.metadata
    authority = document.authority_id
    prefix = f"memory:{authority.replace(':', '-')}-essence-project"
    envelope = metadata.get("curation_effect")
    effects = envelope.get("effects") if isinstance(envelope, dict) else None
    effect = effects[0] if isinstance(effects, list) and len(effects) == 1 else None
    origin = metadata.get("concept_origin")
    if (not authority.startswith("project:") or document.artifact_id != prefix
            or document.relative_path != ".owledge/curated/essence-project.md"
            or metadata.get("schema") != "owledge.managed-markdown/1"
            or type(metadata.get("document_version")) is not int or metadata["document_version"] < 1
            or metadata.get("lifecycle") != "accepted" or metadata.get("processing_layer") != "delta"
            or metadata.get("source_trust") != "reviewed" or metadata.get("canonical") is not False
            or metadata.get("stage") != "curated" or metadata.get("knowledge_kind") != "project_essence"
            or metadata.get("memory_kind") != "semantic" or metadata.get("record_status") != "summary"
            or not isinstance(metadata.get("knowledge_area"), str)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["knowledge_area"])
            or not isinstance(origin, dict)
            or set(origin) != {"project_authority_id", "concept_id", "revision", "source_id",
                               "source_link_id", "snapshot_sha256", "relative_path", "content_sha256"}
            or origin.get("project_authority_id") != authority
            or origin.get("concept_id") != "concept:" + authority.removeprefix("project:")
            or not all(isinstance(origin.get(key), str) and origin[key] for key in origin)
            or not all(re.fullmatch(r"[0-9a-f]{64}", origin[key]) for key in ("snapshot_sha256", "content_sha256"))
            or not isinstance(envelope, dict) or envelope.get("authority_id") != authority
            or not isinstance(effect, dict) or effect.get("relative_path") != document.relative_path
            or effect.get("result_revision") != document.revision
            or effect.get("kind") != ("create" if metadata["document_version"] == 1 else "replace")
            or not document.body.strip() or len(document.body.strip()) > 2048):
        raise ContractValidationError("Project Essence contract is invalid")
    _validate_submitter(metadata.get("essence_submission"), authority)
    base = metadata.get("correction_base")
    if metadata["document_version"] == 1:
        if envelope.get("base_revision") != "absent" or base is not None:
            raise ContractValidationError("Project Essence creation base is invalid")
    elif (not isinstance(base, dict) or set(base) != {"artifact_id", "revision", "content_sha256"}
          or base.get("artifact_id") != document.artifact_id
          or base.get("revision") != envelope.get("base_revision")
          or base.get("content_sha256") != envelope.get("base_sha256")):
        raise ContractValidationError("Project Essence refresh base is invalid")


def build_project_essence_candidate(authority: ManagedMarkdown, summary: str, area: str,
                                    binding: dict, operation_id: str,
                                    base: ManagedMarkdown | None = None):
    active = authority.authority_id
    if (not active.startswith("project:") or not isinstance(summary, str) or not summary.strip()
            or len(summary.strip()) > 2048 or any(char in summary for char in "\x00\x85\u2028\u2029")
            or not isinstance(area, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", area)
            or not isinstance(binding, dict) or binding.get("project_authority_id") != active):
        raise ContractValidationError("Project Essence proposal is invalid")
    origin = essence_origin(binding)
    prefix = active.replace(":", "-")
    slug = "essence-project"
    artifact_id = f"memory:{prefix}-{slug}"
    path = f".owledge/curated/{slug}.md"
    if base is not None:
        validate_project_essence(base)
        if (base.artifact_id != artifact_id or base.metadata["concept_origin"]["source_id"] != origin["source_id"]
                or base.metadata["knowledge_area"] != area):
            raise ContractValidationError("Project Essence refresh source changed")
    version = base.metadata["document_version"] + 1 if base is not None else 1
    submission = {"principal_id": "principal:local-owner", "authority_id": active,
                  "operation_id": operation_id}
    identity = sha256(json.dumps({"summary": summary.strip(), "area": area, "origin": origin,
                                  "base": base.content_sha256 if base else None},
                                 sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
    revision = f"memory-rev-{version}-{identity}"
    suffix = "-refresh-" + identity if base else ""
    candidate_id = f"candidate:{prefix}:{slug}{suffix}"
    changeset_id = f"changeset:{prefix}:{slug}{suffix}"
    envelope = {"changeset_id": changeset_id, "authority_id": active,
                "base_revision": base.revision if base else "absent",
                "policy_revision": authority.metadata["policy_revision"],
                "settings_revision": authority.metadata["settings_revision"],
                "idempotency_key": f"project-essence:{active}:{identity}",
                "receipt_id": f"receipt:{prefix}:promote-{slug}{suffix}",
                "effects": [{"kind": "replace" if base else "create", "relative_path": path,
                             "result_revision": revision}]}
    if base is not None:
        envelope.update(base_sha256=base.content_sha256,
                        base_text_sha256=sha256(base.body.strip().encode("utf-8")).hexdigest())
    metadata = {"schema": "owledge.managed-markdown/1", "document_version": version,
                "artifact_id": artifact_id, "authority_id": active, "revision": revision,
                "lifecycle": "accepted", "processing_layer": "delta", "source_trust": "reviewed",
                "canonical": False, "stage": "curated", "knowledge_kind": "project_essence",
                "memory_kind": "semantic", "knowledge_area": area, "record_status": "summary",
                "concept_origin": origin, "essence_submission": submission, "curation_effect": envelope}
    if base is not None:
        metadata["correction_base"] = {"artifact_id": base.artifact_id,
                                       "revision": base.revision, "content_sha256": base.content_sha256}
    document = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}"
                                       for key, value in metadata.items()) + "\n---\n\n" + summary.strip() + "\n"
    digest = sha256(document.encode("utf-8")).hexdigest()
    preview = {"candidate_id": candidate_id, "candidate_revision": "candidate-rev-1",
               "artifact_id": artifact_id, "proposed_text": summary.strip(), "source": origin,
               "target": path.removeprefix(".owledge/"), "submitted_by": submission,
               "content_sha256": digest, "knowledge_area": area,
               "record_kind": "project_essence", "record_status": "summary", "canonical": False,
               "idempotency_key": envelope["idempotency_key"],
               "expected_policy_revision": envelope["policy_revision"],
               "expected_settings_revision": envelope["settings_revision"]}
    if base is not None:
        preview["base"] = {"artifact_id": base.artifact_id, "revision": base.revision,
                           "content_sha256": base.content_sha256, "text": base.body.strip()}
    return ({"candidate_id": candidate_id, "authority_id": active,
             "candidate_revision": "candidate-rev-1", "lifecycle": "candidate",
             "candidate_kind": "project_essence", "submitted_by": submission,
             "review_preview": preview},
            {**envelope, "result_document": document, "result_sha256": digest})


def build_global_essence_candidate(authority: ManagedMarkdown, contribution: ManagedMarkdown,
                                   binding: dict, base: ManagedMarkdown | None = None):
    """Curate one exact Project summary without taking ownership of its charter."""
    if (authority.authority_id != "user-global:source-access"
            or contribution.metadata.get("schema") != "owledge.reuse-contribution/1"
            or contribution.metadata.get("stage") != "reuse_feed"
            or contribution.metadata.get("knowledge_kind") != "project_essence"
            or contribution.metadata.get("source_concept_origin") != essence_origin(binding)
            or contribution.metadata.get("source_record_trust") != "reviewed"
            or contribution.metadata.get("source_processing_layer") != "delta"):
        raise ContractValidationError("Global Essence contribution is invalid")
    project_id = binding["project_authority_id"]
    slug = "essence-" + project_id.removeprefix("project:")
    if not re.fullmatch(r"essence-[a-z0-9]+(?:-[a-z0-9]+)*", slug) or len(slug) > 80:
        raise ContractValidationError("Project Essence identity is invalid")
    active = authority.authority_id
    prefix = active.replace(":", "-")
    artifact_id = f"memory:{prefix}-{slug}"
    path = f".owledge/curated/{slug}.md"
    if base is not None:
        validate_global_essence(base)
        if base.artifact_id != artifact_id or base.metadata["project_origin"]["authority_id"] != project_id:
            raise ContractValidationError("Global Essence refresh retargets Project")
    version = base.metadata["document_version"] + 1 if base else 1
    identity = sha256(json.dumps({"source": contribution.content_sha256,
        "base": base.content_sha256 if base else None}, sort_keys=True).encode()).hexdigest()[:16]
    revision = f"memory-rev-{version}-{identity}"
    suffix = "-refresh-" + identity if base else ""
    candidate_id = f"candidate:{prefix}:{slug}{suffix}"
    changeset_id = f"changeset:{prefix}:{slug}{suffix}"
    origin = {"contribution_id": contribution.artifact_id,
              "contribution_revision": contribution.revision,
              "contribution_sha256": contribution.content_sha256,
              "artifact_id": contribution.metadata["source_artifact_id"],
              "authority_id": project_id,
              "revision": contribution.metadata["source_revision"],
              "content_sha256": contribution.metadata["source_content_sha256"]}
    envelope = {"changeset_id": changeset_id, "authority_id": active,
                "base_revision": base.revision if base else "absent",
                "policy_revision": authority.metadata["policy_revision"],
                "settings_revision": authority.metadata["settings_revision"],
                "idempotency_key": f"global-essence:{project_id}:{identity}",
                "receipt_id": f"receipt:{prefix}:promote-{slug}{suffix}",
                "effects": [{"kind": "replace" if base else "create",
                             "relative_path": path, "result_revision": revision}]}
    if base is not None:
        envelope.update(base_sha256=base.content_sha256,
                        base_text_sha256=sha256(base.body.strip().encode()).hexdigest())
    metadata = {"schema": "owledge.managed-markdown/1", "document_version": version,
                "artifact_id": artifact_id, "authority_id": active, "revision": revision,
                "lifecycle": "accepted", "processing_layer": "condensed", "source_trust": "reviewed",
                "canonical": True, "stage": "curated", "knowledge_kind": "project_essence",
                "memory_kind": "semantic", "knowledge_area": contribution.metadata["knowledge_area"],
                "record_status": "summary", "concept_origin": essence_origin(binding),
                "project_origin": origin, "curation_effect": envelope}
    if base is not None:
        metadata["correction_base"] = {"artifact_id": base.artifact_id,
                                       "revision": base.revision, "content_sha256": base.content_sha256}
    document = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}"
                                       for key, value in metadata.items()) + "\n---\n\n" + contribution.body.strip() + "\n"
    digest = sha256(document.encode()).hexdigest()
    preview = {"candidate_id": candidate_id, "candidate_revision": "candidate-rev-1",
               "artifact_id": artifact_id, "proposed_text": contribution.body.strip(),
               "source": {"concept": essence_origin(binding), "project": origin},
               "target": path.removeprefix(".owledge/"), "content_sha256": digest,
               "knowledge_area": metadata["knowledge_area"], "record_kind": "project_essence",
               "record_status": "summary", "canonical": True,
               "idempotency_key": envelope["idempotency_key"],
               "expected_policy_revision": envelope["policy_revision"],
               "expected_settings_revision": envelope["settings_revision"]}
    if base is not None:
        preview["base"] = {"artifact_id": base.artifact_id, "revision": base.revision,
                           "content_sha256": base.content_sha256, "text": base.body.strip()}
    candidate = {"candidate_id": candidate_id, "authority_id": active,
                 "candidate_revision": "candidate-rev-1", "lifecycle": "candidate",
                 "candidate_kind": "global_essence", "review_preview": preview,
                 "contribution_binding": {"contribution_id": contribution.artifact_id,
                    "revision": contribution.revision, "content_sha256": contribution.content_sha256}}
    return candidate, {**envelope, "result_document": document, "result_sha256": digest}


def validate_global_essence(document: ManagedMarkdown) -> None:
    metadata = document.metadata
    origin = metadata.get("project_origin")
    effect = metadata.get("curation_effect")
    effects = effect.get("effects") if isinstance(effect, dict) else None
    slug = "essence-" + str(origin.get("authority_id", "")).removeprefix("project:") if isinstance(origin, dict) else ""
    if (document.authority_id != "user-global:source-access"
            or not isinstance(origin, dict)
            or set(origin) != {"contribution_id", "contribution_revision", "contribution_sha256",
                               "artifact_id", "authority_id", "revision", "content_sha256"}
            or not origin["authority_id"].startswith("project:")
            or document.artifact_id != f"memory:user-global-source-access-{slug}"
            or document.relative_path != f".owledge/curated/{slug}.md"
            or metadata.get("knowledge_kind") != "project_essence"
            or metadata.get("canonical") is not True
            or metadata.get("source_trust") != "reviewed"
            or metadata.get("processing_layer") != "condensed"
            or metadata.get("lifecycle") != "accepted"
            or metadata.get("record_status") != "summary"
            or not isinstance(metadata.get("concept_origin"), dict)
            or metadata["concept_origin"].get("project_authority_id") != origin["authority_id"]
            or not isinstance(effect, dict) or effect.get("authority_id") != document.authority_id
            or not isinstance(effects, list) or len(effects) != 1
            or effects[0].get("relative_path") != document.relative_path
            or effects[0].get("result_revision") != document.revision
            or not document.body.strip() or len(document.body.strip()) > 2048):
        raise ContractValidationError("Global Essence contract is invalid")


_EXCEPTIONS = {"critical-finding", "protected-decision", "unresolved-conflict", "curated-review"}


def validate_project_record_request(payload: object) -> None:
    if not isinstance(payload, dict) or not isinstance(payload.get("record_kind"), str) or payload["record_kind"] not in {"idea", "finding"}:
        raise ContractValidationError("Project record kind is invalid")
    kind = payload["record_kind"]
    expected = {"record_kind", "name", "knowledge_area", "text"}
    if kind == "finding":
        expected.add("exception_kind")
    correcting = set(payload) == {"record_kind", "name", "text", "correction"}
    if set(payload) != expected and not correcting:
        raise ContractValidationError("Project record request has unexpected fields")
    for key in (("name",) if correcting else ("name", "knowledge_area")):
        value = payload[key]
        if not isinstance(value, str) or len(value) > 80 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
            raise ContractValidationError("Project record name or Area is invalid")
    value = payload["text"]
    if (not isinstance(value, str) or not value.strip() or len(value) > 8192
            or any(char in value for char in "\x00\x85\u2028\u2029")):
        raise ContractValidationError("Project record text is invalid")
    if kind == "finding" and not correcting and (not isinstance(payload["exception_kind"], str) or payload["exception_kind"] not in _EXCEPTIONS):
        raise ContractValidationError("Finding needs a sparse Inbox exception category")
    if correcting:
        correction = payload["correction"]
        if (not isinstance(correction, dict) or set(correction) != {"artifact_id", "revision", "content_sha256"}
                or any(not isinstance(correction.get(key), str) or not correction[key] or len(correction[key]) > 256
                       for key in correction)
                or not re.fullmatch(r"[0-9a-f]{64}", correction["content_sha256"])):
            raise ContractValidationError("Project record correction base is invalid")


def validate_project_record(document: ManagedMarkdown) -> None:
    metadata = document.metadata
    authority = document.authority_id
    kind = metadata.get("knowledge_kind")
    if not isinstance(kind, str) or kind not in {"idea", "finding"}:
        raise ContractValidationError("Project record kind is invalid")
    prefix = f"memory:{authority.replace(':', '-')}-{kind}-"
    slug = document.artifact_id.removeprefix(prefix)
    envelope = metadata.get("curation_effect")
    effects = envelope.get("effects") if isinstance(envelope, dict) else None
    effect = effects[0] if isinstance(effects, list) and len(effects) == 1 and isinstance(effects[0], dict) else None
    replacing = isinstance(effect, dict) and effect.get("kind") == "replace"
    source = metadata.get("record_origin")
    if (not authority.startswith("project:") or not document.artifact_id.startswith(prefix)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or len(slug) > 80
            or document.relative_path != f".owledge/curated/{kind}-{slug}.md"
            or metadata.get("schema") != "owledge.managed-markdown/1"
            or type(metadata.get("document_version")) is not int or metadata["document_version"] < 1
            or metadata.get("lifecycle") != "accepted"
            or metadata.get("processing_layer") != "delta" or metadata.get("source_trust") != "reviewed"
            or metadata.get("canonical") is not False or metadata.get("stage") != "curated"
            or metadata.get("memory_kind") != ("semantic" if kind == "idea" else "episodic")
            or metadata.get("record_status") != ("possibility" if kind == "idea" else "signal")
            or not isinstance(metadata.get("knowledge_area"), str)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["knowledge_area"])
            or not isinstance(source, dict) or set(source) != {"attribution", "exception_kind"}
            or source.get("exception_kind") != (None if kind == "idea" else metadata.get("exception_kind"))
            or (kind == "finding" and (not isinstance(metadata.get("exception_kind"), str)
                                        or metadata["exception_kind"] not in _EXCEPTIONS))
            or (kind == "idea" and "exception_kind" in metadata)
            or not isinstance(envelope, dict) or envelope.get("authority_id") != authority
            or not isinstance(effect, dict) or not isinstance(effect.get("kind"), str)
            or effect["kind"] not in {"create", "replace"}
            or effect.get("relative_path") != document.relative_path or effect.get("result_revision") != document.revision
            or any(not isinstance(envelope.get(key), str) or not envelope[key] for key in
                   ("changeset_id", "policy_revision", "settings_revision", "idempotency_key", "receipt_id"))
            or not document.body.strip() or len(document.body.strip()) > 8192):
        raise ContractValidationError("Project record contract is invalid")
    _validate_submitter(source["attribution"], authority)
    if replacing:
        correction = metadata.get("correction_base")
        submission = metadata.get("correction_submission")
        if (metadata["document_version"] < 2 or not isinstance(correction, dict)
                or set(correction) != {"artifact_id", "revision", "content_sha256"}
                or any(not isinstance(correction.get(key), str) or not correction[key] or len(correction[key]) > 256
                       for key in correction)
                or not re.fullmatch(r"[0-9a-f]{64}", correction["content_sha256"])
                or correction.get("artifact_id") != document.artifact_id
                or correction.get("revision") != envelope.get("base_revision")
                or correction.get("content_sha256") != envelope.get("base_sha256")
                or not isinstance(envelope.get("base_text_sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", envelope["base_text_sha256"])
                or submission is None):
            raise ContractValidationError("Project record correction binding is invalid")
        _validate_submitter(submission, authority)
    elif (metadata["document_version"] != 1 or envelope.get("base_revision") != "absent"
          or "correction_base" in metadata or "correction_submission" in metadata):
        raise ContractValidationError("Project record creation binding is invalid")


def build_project_record_candidate(authority: ManagedMarkdown, payload: dict, principal_id: str, operation_id: str,
                                   base: ManagedMarkdown | None = None):
    validate_project_record_request(payload)
    active = authority.authority_id
    if not active.startswith("project:"):
        raise ContractValidationError("typed records are Project-only")
    kind, name = payload["record_kind"], payload["name"]
    prefix = active.replace(":", "-")
    slug = f"{kind}-{name}"
    attribution = {"principal_id": principal_id, "authority_id": active, "operation_id": operation_id}
    _validate_submitter(attribution, active)
    correcting = base is not None
    if correcting:
        validate_project_record(base)
        expected_base = {"artifact_id": base.artifact_id, "revision": base.revision,
                         "content_sha256": base.content_sha256}
        if (payload.get("correction") != expected_base or base.authority_id != active
                or base.artifact_id != f"memory:{prefix}-{slug}"):
            raise ContractValidationError("Project record correction base is stale")
        origin = base.metadata["record_origin"]
        area = base.metadata["knowledge_area"]
        exception_kind = base.metadata.get("exception_kind")
        version = base.metadata["document_version"] + 1
    else:
        origin = {"attribution": attribution, "exception_kind": payload.get("exception_kind")}
        area = payload["knowledge_area"]
        exception_kind = payload.get("exception_kind")
        version = 1
    text = payload["text"].strip()
    identity = sha256(json.dumps({"origin": origin, "text": text, "area": area, "kind": kind,
                                  **({"base": base.content_sha256, "submission": attribution} if correcting else {})},
                                  sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    artifact_id = f"memory:{prefix}-{slug}"
    path = f".owledge/curated/{slug}.md"
    revision = f"memory-rev-{version}-{identity[:16]}"
    suffix = "-correction-" + identity[:16] if correcting else ""
    envelope = {"changeset_id": f"changeset:{prefix}:{slug}{suffix}", "authority_id": active,
                "base_revision": base.revision if correcting else "absent", "policy_revision": authority.metadata["policy_revision"],
                "settings_revision": authority.metadata["settings_revision"],
                "idempotency_key": f"project-record:{active}:{slug}:{identity}",
                "receipt_id": f"receipt:{prefix}:promote-{slug}{suffix}",
                "effects": [{"kind": "replace" if correcting else "create", "relative_path": path, "result_revision": revision}]}
    if correcting:
        envelope.update(base_sha256=base.content_sha256,
                        base_text_sha256=sha256(base.body.strip().encode("utf-8")).hexdigest())
    metadata = {"schema": "owledge.managed-markdown/1", "document_version": version, "artifact_id": artifact_id,
                "authority_id": active, "revision": revision, "lifecycle": "accepted", "processing_layer": "delta",
                "source_trust": "reviewed", "canonical": False, "stage": "curated", "knowledge_kind": kind,
                "memory_kind": "semantic" if kind == "idea" else "episodic", "knowledge_area": area,
                "record_status": "possibility" if kind == "idea" else "signal", "record_origin": origin,
                "curation_effect": envelope}
    if kind == "finding":
        metadata["exception_kind"] = exception_kind
    if correcting:
        metadata["correction_base"] = payload["correction"]
        metadata["correction_submission"] = attribution
    document = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items()) + "\n---\n\n" + text + "\n"
    if len(document.encode("utf-8")) > 65_536:
        raise ContractValidationError("Project record exceeds bounded read budget")
    digest = sha256(document.encode("utf-8")).hexdigest()
    candidate_id = f"candidate:{prefix}:{slug}{suffix}"
    preview = {"candidate_id": candidate_id, "candidate_revision": "candidate-rev-1", "artifact_id": artifact_id,
               "proposed_text": text, "source": origin, "target": path.removeprefix(".owledge/"),
               "submitted_by": attribution, "content_sha256": digest, "knowledge_area": area,
               "record_kind": kind, "record_status": metadata["record_status"],
               **({"exception_kind": exception_kind} if kind == "finding" else {}),
               "idempotency_key": envelope["idempotency_key"],
               "expected_policy_revision": envelope["policy_revision"],
               "expected_settings_revision": envelope["settings_revision"]}
    if correcting:
        preview["base"] = {**payload["correction"], "text": base.body.strip()}
    return ({"candidate_id": candidate_id, "authority_id": active, "candidate_revision": "candidate-rev-1",
             "lifecycle": "candidate", "candidate_kind": "project_record", "submitted_by": attribution,
             "review_preview": preview}, {**envelope, "result_document": document, "result_sha256": digest})
