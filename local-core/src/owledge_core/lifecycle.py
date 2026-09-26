"""Pure rendering for bounded private Core lifecycle artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone

from .artifacts import ManagedMarkdown, parse_markdown_frontmatter
from .contracts import evidence_value_matches

__all__: tuple[str, ...] = ()


class LifecycleValidationError(ValueError):
    def __init__(self, status: str, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.reason_code = reason_code


def _expires_at(clock: str) -> str:
    parsed = datetime.fromisoformat(clock.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Core clock must include a timezone")
    expires = parsed.astimezone(timezone.utc) + timedelta(hours=1)
    return expires.isoformat(timespec="seconds").replace("+00:00", "Z")


def _identity_token(kind: str, bindings: dict[str, object]) -> str:
    encoded = json.dumps(
        {"kind": kind, "bindings": bindings},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def render_maintenance_bundle(
    *,
    authority_id: str,
    policy_revision: str,
    settings_revision: str,
    coverage_case_id: str,
    coverage_case_revision: str,
    search_envelope_id: str,
    search_envelope_revision: str,
    source_snapshot_id: str,
    absence_proof_id: str,
    resolution_route_id: str,
    resolution_route_revision: str,
    gap_id: str,
    evidence_key: str,
    target_artifact_id: str,
    target_relative_path: str,
    selected_documents: list[ManagedMarkdown],
    clock: str,
    identity_seed: str | None = None,
) -> tuple[str, str, str, str]:
    """Render one exact lossless read-only Atom selection and editable Gap."""

    authority_slug = authority_id.replace(":", "-")
    authority_title = authority_id.split(":", 1)[-1].replace("-", " ").title()
    selected_revisions = {
        item.artifact_id: item.revision
        for item in sorted(selected_documents, key=lambda document: document.artifact_id)
    }
    if identity_seed is None:
        bundle_suffix = "001"
        bundle_revision = "bundle-rev-1"
    else:
        bundle_suffix = _identity_token(
            "maintenance-bundle",
            {
                "authority_id": authority_id,
                "gap_id": gap_id,
                "absence_proof_id": absence_proof_id,
                "selected_revisions": selected_revisions,
                "identity_seed": identity_seed,
            },
        )
        bundle_revision = f"bundle-rev-1-{bundle_suffix}"
    bundle_id = f"bundle:{authority_slug}:gap-closure-{bundle_suffix}"
    expires_at = _expires_at(clock)
    lines = [
        "---",
        "schema: owledge.maintenance-bundle/1",
        f"bundle_id: {bundle_id}",
        f"bundle_revision: {bundle_revision}",
        f"authority_id: {authority_id}",
        f"policy_revision: {policy_revision}",
        f"settings_revision: {settings_revision}",
        f"coverage_case_id: {coverage_case_id}",
        f"coverage_case_revision: {coverage_case_revision}",
        f"search_envelope_id: {search_envelope_id}",
        f"search_envelope_revision: {search_envelope_revision}",
        f"source_snapshot_id: {source_snapshot_id}",
        f"absence_proof_id: {absence_proof_id}",
        f"resolution_route_id: {resolution_route_id}",
        f"resolution_route_revision: {resolution_route_revision}",
        f"expires_at: {expires_at}",
        "selected_revisions: "
        + json.dumps(selected_revisions, ensure_ascii=False, separators=(",", ":")),
        "open_gap_ids: "
        + json.dumps([gap_id], ensure_ascii=False, separators=(",", ":")),
        f"target_artifact_id: {target_artifact_id}",
        f"target_relative_path: {target_relative_path}",
        "---",
        "",
        f"# {authority_title} Knowledge Maintenance",
        "",
    ]
    selected_source_lineage = [
        {"artifact_id": item.artifact_id, "authority_id": item.authority_id,
         "binding": item.metadata["source_evidence"]["binding"]}
        for item in selected_documents
        if item.metadata.get("knowledge_kind") == "reference"
        and isinstance(item.metadata.get("source_evidence"), dict)
        and isinstance(item.metadata["source_evidence"].get("binding"), dict)
    ]
    if selected_source_lineage:
        lines.insert(lines.index("open_gap_ids: " + json.dumps([gap_id], ensure_ascii=False, separators=(",", ":"))),
                     "selected_source_lineage: " + json.dumps(selected_source_lineage, ensure_ascii=False, separators=(",", ":")))
    for document in selected_documents:
        lines.extend(
            [
                f'<!-- owledge-record:start artifact_id="{document.artifact_id}" revision="{document.revision}" mode="read_only" -->',
                document.body.strip("\n"),
                f'<!-- owledge-record:end artifact_id="{document.artifact_id}" -->',
                "",
            ]
        )
    lines.extend(
        [
            f'<!-- owledge-gap:start gap_id="{gap_id}" mode="editable" -->',
            "## Gap Response",
            "",
            f"evidence_key: {evidence_key}",
            "evidence_value:",
            "statement:",
            "intent_to_close: false",
            f'<!-- owledge-gap:end gap_id="{gap_id}" -->',
            "",
        ]
    )
    return bundle_id, bundle_revision, expires_at, "\n".join(lines)


def preview_maintenance_bundle(
    *,
    original_bundle: str,
    edited_bundle: str,
    authority_id: str,
    policy_revision: str,
    settings_revision: str,
    operation_id: str,
    submitted_by: str,
    content_origin: str,
    reported: dict[str, object],
    adapter_observed: dict[str, object],
    route: dict[str, object],
    clock: str,
    identity_seed: str | None = None,
    source_derived_selection: bool = False,
    source_lineage: list[dict[str, object]] | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    """Validate one edited Gap block and derive a Candidate/ChangeSet preview."""

    original_metadata, _ = parse_markdown_frontmatter(original_bundle)
    edited_metadata, _ = parse_markdown_frontmatter(edited_bundle)
    if edited_metadata.get("authority_id") != original_metadata.get("authority_id"):
        raise LifecycleValidationError(
            "denied", "scope_widening_denied", "Bundle authority changed"
        )
    for field in ("selected_revisions", "open_gap_ids", "target_artifact_id", "target_relative_path"):
        if edited_metadata.get(field) != original_metadata.get(field):
            raise LifecycleValidationError(
                "denied", "scope_widening_denied", f"Bundle scope changed: {field}"
            )
    if original_metadata != edited_metadata:
        raise LifecycleValidationError(
            "invalid", "bundle_identity_missing", "Bundle frontmatter binding changed"
        )
    if original_metadata.get("authority_id") != authority_id:
        raise LifecycleValidationError(
            "denied", "scope_widening_denied", "Bundle authority is outside active scope"
        )
    if (
        original_metadata.get("policy_revision") != policy_revision
        or original_metadata.get("settings_revision") != settings_revision
    ):
        reason = (
            "policy_revision_mismatch"
            if original_metadata.get("policy_revision") != policy_revision
            else "settings_revision_mismatch"
        )
        raise LifecycleValidationError("stale", reason, "Bundle authority revisions are stale")
    expiry = original_metadata.get("expires_at")
    if not isinstance(expiry, str):
        raise ValueError("Bundle expiry is missing")
    now = datetime.fromisoformat(clock.replace("Z", "+00:00"))
    expires = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
    if now > expires:
        raise LifecycleValidationError("stale", "bundle_expired", "Bundle expired")

    record_pattern = re.compile(
        r'<!-- owledge-record:start artifact_id="([^"]+)" revision="([^"]+)" mode="read_only" -->\n'
        r'.*?\n<!-- owledge-record:end artifact_id="\1" -->\n?',
        re.DOTALL,
    )
    original_records = list(record_pattern.finditer(original_bundle))
    edited_records = list(record_pattern.finditer(edited_bundle))

    def record_map(matches: list[re.Match[str]]) -> dict[str, str]:
        mapped: dict[str, str] = {}
        for match in matches:
            artifact_id = match.group(1)
            if artifact_id in mapped:
                raise LifecycleValidationError(
                    "invalid", "bundle_identity_duplicate", "Bundle record identity duplicated"
                )
            mapped[artifact_id] = match.group(0)
        return mapped

    original_record_map = record_map(original_records)
    edited_record_map = record_map(edited_records)
    if not set(edited_record_map) <= set(original_record_map):
        raise LifecycleValidationError(
            "denied", "scope_widening_denied", "Bundle record selection widened"
        )
    if any(
        edited_record_map[artifact_id] != original_record_map[artifact_id]
        for artifact_id in edited_record_map
    ):
        raise LifecycleValidationError(
            "invalid", "bundle_fence_mismatch", "Bundle read-only record changed"
        )
    original_without_records = re.sub(
        r"\n{3,}", "\n\n", record_pattern.sub("", original_bundle)
    )
    edited_without_records = re.sub(
        r"\n{3,}", "\n\n", record_pattern.sub("", edited_bundle)
    )

    gap_pattern = re.compile(
        r'<!-- owledge-gap:start gap_id="([^"]+)" mode="editable" -->\n'
        r'(.*?)\n<!-- owledge-gap:end gap_id="\1" -->',
        re.DOTALL,
    )
    original_matches = list(gap_pattern.finditer(original_without_records))
    edited_matches = list(gap_pattern.finditer(edited_without_records))
    if len(original_matches) != 1 or len(edited_matches) != 1:
        reason = "bundle_identity_duplicate" if len(edited_matches) > 1 else "bundle_identity_missing"
        raise LifecycleValidationError("invalid", reason, "Bundle Gap identity is invalid")
    original_gap = original_matches[0]
    edited_gap = edited_matches[0]
    if original_gap.group(1) != edited_gap.group(1):
        raise LifecycleValidationError(
            "denied", "scope_widening_denied", "Bundle Gap identity changed"
        )
    if (
        original_without_records[: original_gap.start()]
        != edited_without_records[: edited_gap.start()]
        or original_without_records[original_gap.end() :]
        != edited_without_records[edited_gap.end() :]
    ):
        raise LifecycleValidationError(
            "invalid", "bundle_fence_mismatch", "Bundle read-only structure changed"
        )

    response: dict[str, str] = {}
    for line in edited_gap.group(2).splitlines():
        if ":" not in line or line.startswith("#"):
            continue
        key, value = line.split(":", 1)
        response[key.strip()] = value.strip()
    evidence_key = response.get("evidence_key")
    evidence_value = response.get("evidence_value")
    statement = response.get("statement")
    if (
        not evidence_key
        or not evidence_value
        or not evidence_value_matches(evidence_value, route.get("value_contract", {"type": "integer_string", "minimum": 1, "maximum": 168}))
        or not statement
        or response.get("intent_to_close") != "true"
    ):
        raise ValueError("Bundle Gap response is incomplete or invalid")
    target_artifact_id = route.get("target_artifact_id")
    target_relative_path = route.get("target_relative_path")
    default_title = route.get("default_title")
    if not all(
        isinstance(item, str) and item
        for item in (target_artifact_id, target_relative_path, default_title)
    ):
        raise ValueError("Artifact Routing target is incomplete")

    authority_slug = authority_id.replace(":", "-")
    coverage_case_id = original_metadata.get("coverage_case_id")
    coverage_case_revision = original_metadata.get("coverage_case_revision")
    absence_proof_id = original_metadata.get("absence_proof_id")
    resolution_route_id = original_metadata.get("resolution_route_id")
    resolution_route_revision = original_metadata.get("resolution_route_revision")
    if not all(
        isinstance(item, str) and item
        for item in (
            coverage_case_id,
            coverage_case_revision,
            absence_proof_id,
            resolution_route_id,
            resolution_route_revision,
        )
    ):
        raise ValueError("Bundle proof or route binding is incomplete")
    if identity_seed is None:
        lifecycle_suffix = "001"
    else:
        lifecycle_suffix = _identity_token(
            "candidate-preview",
            {
                "authority_id": authority_id,
                "coverage_case_id": coverage_case_id,
                "absence_proof_id": absence_proof_id,
                "target_artifact_id": target_artifact_id,
                "evidence_key": evidence_key,
                "evidence_value": evidence_value,
                "statement": statement,
                "identity_seed": identity_seed,
            },
        )
    candidate_id = f"candidate:{authority_slug}:gap-closure-{lifecycle_suffix}"
    candidate_revision = (
        "candidate-rev-1"
        if identity_seed is None
        else f"candidate-rev-1-{lifecycle_suffix}"
    )
    candidate = {
        "candidate_id": candidate_id,
        "candidate_revision": candidate_revision,
        "authority_id": authority_id,
        "lifecycle": "candidate",
        "processing_layer": "delta",
        "attribution": {
            "reported_content_origin": content_origin,
            "submitted_by": submitted_by,
        },
        "provenance": {
            "reported": reported,
            "adapter_observed": adapter_observed,
            "core_assigned": {
                "operation_id": operation_id,
                "target_authority_id": authority_id,
            },
        },
        "coverage_case_id": coverage_case_id,
        "coverage_case_revision": coverage_case_revision,
        "absence_proof_id": absence_proof_id,
        "resolution_route_id": resolution_route_id,
        "resolution_route_revision": resolution_route_revision,
    }
    if isinstance(route.get("case_name"), str):
        candidate["named_case"] = route["case_name"]
    bundle_selection = {
        "bundle_id": original_metadata.get("bundle_id"),
        "selected_revisions": original_metadata.get("selected_revisions"),
    }
    if source_derived_selection:
        candidate["bundle_selection"] = bundle_selection
        candidate["source_lineage"] = source_lineage
    normalized_reported = {
        key: reported[key]
        for key in ("agent_name", "model")
        if key in reported
    }
    normalized_reported["reported_content_origin"] = content_origin
    normalized_adapter = {
        key: adapter_observed[key]
        for key in ("run_id", "runtime", "runtime_version")
        if key in adapter_observed
    }
    core_assigned = {
        "candidate_id": candidate_id,
        "operation_id": operation_id,
        "submitted_by": submitted_by,
    }
    result_revision = (
        "rev-agent-lesson-review-window-1"
        if identity_seed is None
        else f"rev-{target_artifact_id.replace(':', '-')}-{lifecycle_suffix}"
    )
    result_document = (
        "---\n"
        "schema: owledge.managed-markdown/1\n"
        "document_version: 1\n"
        f"artifact_id: {target_artifact_id}\n"
        f"authority_id: {authority_id}\n"
        f"revision: {result_revision}\n"
        "lifecycle: accepted\n"
        f"processing_layer: {route['candidate_processing_layer']}\n"
        f"source_trust: {route['target_source_trust']}\n"
        f"knowledge_kind: {route['knowledge_kind']}\n"
        f"memory_kind: {route['memory_kind']}\n"
        + ("source_lineage: " + json.dumps(source_lineage, ensure_ascii=False, separators=(",", ":")) + "\n" if source_derived_selection else "")
        + "evidence_values: "
        + json.dumps({evidence_key: evidence_value}, ensure_ascii=False, separators=(",", ":"))
        + "\n"
        "provenance_reported: "
        + json.dumps(normalized_reported, ensure_ascii=False, separators=(",", ":"))
        + "\n"
        "provenance_adapter_observed: "
        + json.dumps(normalized_adapter, ensure_ascii=False, separators=(",", ":"))
        + "\n"
        "provenance_core_assigned: "
        + json.dumps(core_assigned, ensure_ascii=False, separators=(",", ":"))
        + "\n"
        "---\n\n"
        f"# {default_title}\n\n"
        f"{statement}\n"
    )
    changeset = {
        "schema": "owledge.changeset/1",
        "changeset_id": f"changeset:{authority_slug}:gap-closure-{lifecycle_suffix}",
        "authority_id": authority_id,
        "base_revision": "absent",
        "policy_revision": policy_revision,
        "settings_revision": settings_revision,
        "idempotency_key": f"idempotency:gap-closure-{lifecycle_suffix}",
        "effects": [
            {
                "kind": "create",
                "artifact_id": target_artifact_id,
                "relative_path": target_relative_path,
                "result_revision": result_revision,
            }
        ],
        "result_document": result_document,
        "result_sha256": hashlib.sha256(result_document.encode("utf-8")).hexdigest(),
        "receipt_id": f"receipt:{authority_slug}:gap-closure-{lifecycle_suffix}",
        "coverage_case_revision": coverage_case_revision,
        "absence_proof_id": absence_proof_id,
        "resolution_route_id": resolution_route_id,
        "resolution_route_revision": resolution_route_revision,
    }
    if source_derived_selection:
        changeset["bundle_selection"] = bundle_selection
        changeset["source_lineage"] = source_lineage
    return candidate, changeset


def preview_named_case_correction(*, authority_id: str, name: str, old: ManagedMarkdown,
                                  route: dict[str, object], value: str, operation_id: str,
                                  submitted_by: str, policy_revision: str,
                                  settings_revision: str) -> tuple[dict[str, object], dict[str, object]]:
    """Stage one exact-base correction using the existing Candidate/ChangeSet lifecycle."""
    from .contracts import evidence_value_matches
    contract = route.get("value_contract")
    if (not evidence_value_matches(value, contract)
            or old.artifact_id != route.get("target_artifact_id")
            or old.relative_path != route.get("target_relative_path")
            or old.authority_id != authority_id
            or old.metadata.get("lifecycle") != "accepted"
            or old.metadata.get("knowledge_kind") != "project_fact"):
        raise LifecycleValidationError("stale", "correction_base_changed", "Accepted case answer changed")
    evidence = old.metadata.get("evidence_values")
    if not isinstance(evidence, dict) or len(evidence) != 1:
        raise LifecycleValidationError("invalid", "correction_base_invalid", "Accepted answer is malformed")
    evidence_key = next(iter(evidence))
    suffix = _identity_token("named-case-correction", {"authority": authority_id, "name": name,
        "base_revision": old.revision, "base_sha256": old.content_sha256,
        "value": value, "operation_id": operation_id})
    result_revision = f"rev-{str(old.artifact_id).replace(':', '-')}-{suffix}"
    metadata = {**old.metadata, "document_version": old.metadata["document_version"] + 1,
                "revision": result_revision, "processing_layer": "delta",
                "evidence_values": {evidence_key: value}}
    body = f"\n# {route['default_title']}\n\n{route['default_title']}: {value}\n"
    document = "---\n" + "\n".join(f"{key}: {json.dumps(item, ensure_ascii=False, separators=(',', ':'))}"
                                       for key, item in metadata.items()) + "\n---\n" + body
    candidate_id = f"candidate:{authority_id.replace(':', '-')}:case-correction-{suffix}"
    candidate = {"candidate_id": candidate_id, "candidate_revision": f"candidate-rev-1-{suffix}",
                 "authority_id": authority_id, "lifecycle": "candidate", "processing_layer": "delta",
                 "named_case": name, "coverage_case_id": f"coverage:{name}",
                 "coverage_case_revision": route["route_revision"],
                 "resolution_route_id": f"route:{name}",
                 "resolution_route_revision": route["route_revision"],
                 "attribution": {"reported_content_origin": "named-project-case-correction",
                                 "submitted_by": submitted_by},
                 "provenance": {"core_assigned": {"operation_id": operation_id,
                                                 "target_authority_id": authority_id}}}
    changeset = {"schema": "owledge.changeset/1",
                 "changeset_id": f"changeset:{authority_id.replace(':', '-')}:case-correction-{suffix}",
                 "authority_id": authority_id, "base_revision": old.revision,
                 "base_sha256": old.content_sha256,
                 "policy_revision": policy_revision, "settings_revision": settings_revision,
                 "idempotency_key": f"idempotency:case-correction-{suffix}",
                 "effects": [{"kind": "replace", "artifact_id": old.artifact_id,
                              "relative_path": old.relative_path, "result_revision": result_revision}],
                 "result_document": document,
                 "result_sha256": hashlib.sha256(document.encode("utf-8")).hexdigest(),
                 "receipt_id": f"receipt:{authority_id.replace(':', '-')}:case-correction-{suffix}",
                 "coverage_case_revision": route["route_revision"],
                 "resolution_route_id": f"route:{name}", "resolution_route_revision": route["route_revision"]}
    return candidate, changeset
