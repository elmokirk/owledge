"""Deterministic required-Evidence retrieval and coverage assessment."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from hashlib import sha256

from .artifacts import ManagedMarkdown, unicode_keyword_spans
from .contracts import ContractValidationError, evidence_value_matches, valid_evidence_value_contract


__all__: tuple[str, ...] = ()


def raw_evidence_hit(document: ManagedMarkdown, query: str) -> dict[str, object]:
    """Bounded output projection; original read size and hash remain provenance."""
    folded_body = document.body.casefold()
    phrase = re.search(r"(?<!\w)" + re.escape(query.casefold()) + r"(?!\w)", folded_body) if query else None
    if phrase is None:
        tokens = {token for token, _ in unicode_keyword_spans(query)}
        position = next((offset for token, offset in unicode_keyword_spans(document.body)
                         if token in tokens), 0)
    else:
        position = 0
        # Case folding can expand characters; retain original-source offsets.
        folded_offset = 0
        for position, character in enumerate(document.body):
            if folded_offset + len(character.casefold()) > phrase.start():
                break
            folded_offset += len(character.casefold())
    start = max(0, position - 80)
    return {
        "relative_path": document.relative_path,
        "snippet": document.body[start:start + 512],
        "content_sha256": document.content_sha256,
        "canonical": False,
        "trust": "external",
    }


@dataclass(frozen=True, slots=True)
class CoverageOutcome:
    assessment: dict[str, object]
    absence_proof: dict[str, object] | None
    safe_topic: str | None


class MarkdownReferenceRetriever:
    """Deterministic authority-local reference implementation."""

    revision = "owledge.markdown-reference-retriever/1"

    def assess(
        self,
        documents: tuple[ManagedMarkdown, ...],
        coverage_case_id: str,
    ) -> CoverageOutcome | None:
        return assess_coverage(documents, coverage_case_id)

    def select(
        self,
        documents: tuple[ManagedMarkdown, ...],
        selected_artifact_ids: tuple[str, ...],
    ) -> tuple[ManagedMarkdown, ...]:
        available = {item.artifact_id: item for item in documents}
        if any(item not in available for item in selected_artifact_ids):
            return ()
        return tuple(available[item] for item in selected_artifact_ids)


_PROGRESSIVE_STAGES = (
    "curated",
    "inbox",
    "reuse_feed",
    "linked_project",
    "raw_keyword",
)
_PROGRESSIVE_FILTERS = {
    "authority_scope": "authority_id",
    "knowledge_area": "knowledge_area",
    "knowledge_kind": "knowledge_kind",
    "memory_kind": "memory_kind",
    "processing_layer": "processing_layer",
    "lifecycle": "lifecycle",
    "source_trust": "source_trust",
    "access": "access",
}


def normalize_typed_filters(raw: object) -> dict[str, tuple[str, ...]]:
    """Validate the closed retrieval selection once for every reader surface."""
    if not isinstance(raw, dict) or any(
        not isinstance(name, str) or name not in _PROGRESSIVE_FILTERS
        or not isinstance(values, list) or not values or len(values) > 16
        or any(not isinstance(value, str) or not value or len(value) > 256 for value in values)
        or len(values) != len(set(values))
        for name, values in raw.items()
    ):
        raise ContractValidationError("retrieval filters are invalid typed selections")
    return {name: tuple(values) for name, values in raw.items()}


def matches_typed_filters(
    document: ManagedMarkdown, filters: dict[str, tuple[str, ...]],
) -> bool:
    return all(
        document.metadata.get(_PROGRESSIVE_FILTERS[name]) in allowed
        for name, allowed in filters.items()
    )


def _valid_reuse_contribution(
    document: ManagedMarkdown,
    stage: str,
) -> bool:
    from .source_curation import valid_reuse_contribution
    return valid_reuse_contribution(document, stage)


def _progressive_values(
    document: ManagedMarkdown, required_evidence: tuple[str, ...],
) -> dict[str, object]:
    evidence = document.metadata.get("evidence")
    values = dict(evidence) if isinstance(evidence, dict) else {}
    values.update({
        key: document.metadata[key] for key in required_evidence
        if isinstance(document.metadata.get(key), str)
    })
    return values


def progressive_assess(
    stage_documents: dict[str, tuple[ManagedMarkdown, ...]],
    *,
    required_evidence: tuple[str, ...],
    search_envelope: tuple[str, ...],
    query: str,
    filters: dict[str, tuple[str, ...]],
    max_result_records: int,
    max_result_bytes: int,
    complete: bool = True,
    compare_stages: bool = False,
    proof_context: dict[str, object] | None = None,
    gap_admission: str = "disabled",
    safe_topic: str | None = None,
) -> dict[str, object]:
    """Evaluate the currently loaded prefix of a versioned retrieval ladder."""

    if (
        not required_evidence
        or len(set(required_evidence)) != len(required_evidence)
        or any(not item for item in required_evidence)
        or not search_envelope
        or len(set(search_envelope)) != len(search_envelope)
        or any(item not in _PROGRESSIVE_STAGES for item in search_envelope)
        or tuple(sorted(search_envelope, key=_PROGRESSIVE_STAGES.index))
        != search_envelope
        or any(key not in _PROGRESSIVE_FILTERS for key in filters)
        or any(not values or len(values) != len(set(values)) for values in filters.values())
        or gap_admission not in {"disabled", "proof_required"}
        or (gap_admission == "proof_required" and not safe_topic)
    ):
        return {"terminal": ("invalid", "retrieval_contract_invalid"), "data": {}}

    evaluated_stages = tuple(stage for stage in search_envelope if stage in stage_documents)
    if evaluated_stages != search_envelope[: len(evaluated_stages)]:
        return {"terminal": ("invalid", "retrieval_contract_invalid"), "data": {}}
    eligible: dict[str, list[ManagedMarkdown]] = {}
    excluded: set[str] = set()
    manifests: list[dict[str, object]] = []
    invalid_contract = False
    matching_ideas: list[ManagedMarkdown] = []
    for stage in evaluated_stages:
        stage_matches: list[ManagedMarkdown] = []
        documents = sorted(stage_documents.get(stage, ()), key=lambda item: item.artifact_id)
        manifests.append(
            {
                "stage": stage,
                "records": [
                    {
                        "artifact_id": item.artifact_id,
                        "revision": item.revision,
                        "sha256": item.content_sha256,
                    }
                    for item in documents
                ],
            }
        )
        for document in documents:
            schema = document.metadata.get("schema")
            common = document.metadata.get("stage") == stage
            managed_inbox = (
                schema == "owledge.managed-markdown/1"
                and document.metadata.get("lifecycle") == "open"
                and document.metadata.get("source_trust") == "unreviewed"
            )
            contributed_inbox = (
                _valid_reuse_contribution(document, stage)
                and document.metadata.get("lifecycle") == "candidate"
                and document.metadata.get("source_trust") == "internal"
            )
            valid_contract = common and {
                "curated": (
                    schema == "owledge.managed-markdown/1"
                    and document.metadata.get("lifecycle") == "accepted"
                    and document.metadata.get("processing_layer") == "condensed"
                    and document.metadata.get("source_trust") in {"internal", "reviewed"}
                    and document.metadata.get("canonical") is True
                ),
                "inbox": (
                    (managed_inbox or contributed_inbox)
                    and document.metadata.get("processing_layer") == "delta"
                    and document.metadata.get("canonical") is False
                ),
                "reuse_feed": (
                    _valid_reuse_contribution(document, stage)
                    and document.metadata.get("lifecycle") == "candidate"
                    and document.metadata.get("processing_layer") == "delta"
                    and document.metadata.get("source_trust") == "internal"
                    and document.metadata.get("canonical") is False
                ),
                "linked_project": (
                    schema == "owledge.managed-markdown/1"
                    and document.metadata.get("lifecycle") == "accepted"
                    and document.metadata.get("processing_layer") == "condensed"
                    and document.metadata.get("source_trust") == "internal"
                    and document.metadata.get("canonical") is True
                ),
                "raw_keyword": (
                    schema == "owledge.source-sidecar/1"
                    and document.metadata.get("lifecycle") == "observed"
                    and document.metadata.get("processing_layer") == "raw"
                    and document.metadata.get("source_trust") == "external"
                    and document.metadata.get("canonical") is False
                ),
            }[stage]
            valid_project_candidate = (
                stage == "linked_project"
                and common
                and schema == "owledge.managed-markdown/1"
                and document.metadata.get("lifecycle") == "candidate"
                and document.metadata.get("processing_layer") == "delta"
                and document.metadata.get("source_trust") == "internal"
                and document.metadata.get("canonical") is False
                and document.metadata.get("knowledge_kind") in {"idea", "finding"}
                and document.metadata.get("memory_kind") in {"semantic", "episodic"}
            )
            valid_project_signal = (
                stage == "linked_project"
                and schema == "owledge.managed-markdown/1"
                and document.metadata.get("lifecycle") == "accepted"
                and document.metadata.get("processing_layer") == "delta"
                and document.metadata.get("source_trust") == "reviewed"
                and document.metadata.get("canonical") is False
                and isinstance(document.metadata.get("knowledge_kind"), str)
                and document.metadata["knowledge_kind"] in {"idea", "finding"}
            )
            if valid_project_signal:
                from .lesson_capture import validate_project_record
                try:
                    validate_project_record(document)
                except ContractValidationError:
                    valid_project_signal = False
            if valid_project_candidate or valid_project_signal:
                excluded.add(document.artifact_id)
                candidate_values = _progressive_values(document, required_evidence)
                if (
                    document.metadata.get("knowledge_kind") == "idea"
                    and matches_typed_filters(document, filters)
                    and all(isinstance(candidate_values.get(key), str) and candidate_values[key]
                            for key in required_evidence)
                ):
                    matching_ideas.append(document)
                continue
            if (stage == "reuse_feed" and valid_contract
                    and isinstance(document.metadata.get("knowledge_kind"), str)
                    and document.metadata["knowledge_kind"] == "idea"):
                excluded.add(document.artifact_id)
                if (document.metadata["knowledge_kind"] == "idea"
                        and matches_typed_filters(document, filters)):
                    matching_ideas.append(document)
                continue
            if (document.metadata.get("knowledge_kind") == "project_essence"
                    and (document.metadata.get("source_trust") == "reviewed"
                         or document.metadata.get("source_record_trust") == "reviewed")):
                excluded.add(document.artifact_id)
                continue
            if not valid_contract:
                excluded.add(document.artifact_id)
                invalid_contract = True
                continue
            matched_filters = matches_typed_filters(document, filters)
            if not matched_filters:
                excluded.add(document.artifact_id)
                continue
            if (stage == "inbox" and schema == "owledge.reuse-contribution/1"
                    and document.metadata.get("knowledge_kind") == "finding"
                    and document.metadata.get("source_record_trust") == "reviewed"
                    and document.metadata.get("source_processing_layer") == "delta"):
                if query.casefold() in document.body.casefold():
                    stage_matches.append(document)
                else:
                    excluded.add(document.artifact_id)
                continue
            evidence_values = _progressive_values(document, required_evidence)
            if stage == "raw_keyword" and document.metadata.get("raw_match") is True:
                stage_matches.append(document)
            elif all(
                isinstance(evidence_values.get(key), str) and bool(evidence_values.get(key))
                for key in required_evidence
            ):
                stage_matches.append(document)
        eligible[stage] = stage_matches

    def hint_metadata(selected_count: int = 0) -> dict[str, object]:
        if not matching_ideas or selected_count >= max_result_records:
            return {}
        idea = min(matching_ideas, key=lambda item: item.artifact_id)
        return {"candidate_hints": [{
            "artifact_id": idea.artifact_id,
            "authority_id": idea.authority_id,
            "revision": idea.revision,
            "lifecycle": idea.metadata.get("lifecycle"),
            "canonical": False,
            "label": "Geprüfte Möglichkeit" if idea.metadata.get("lifecycle") == "accepted" else "Unbestätigte Idee",
        }]}

    if invalid_contract:
        return {
            "terminal": ("recovery_required", "source_contract_invalid"),
            "data": {
                "stage": evaluated_stages[-1] if evaluated_stages else None,
                "selected_artifact_ids": [],
                "excluded_artifact_ids": sorted(excluded),
                "citation_artifact_ids": [],
                "gap_effect_allowed": False,
            },
        }

    if eligible.get("inbox") and not eligible.get("curated") and not compare_stages:
        signals = eligible["inbox"]
        if len(signals) > max_result_records or sum(item.size_bytes for item in signals) > max_result_bytes:
            return {"terminal": ("incomplete", "resource_exhausted"),
                    "data": {"stage": "inbox", "selected_artifact_ids": [],
                             "excluded_artifact_ids": sorted(excluded), "citation_artifact_ids": [],
                             "gap_effect_allowed": False}}
        return {
            "terminal": ("incomplete", "review_signal"),
            "data": {
                "stage": "inbox",
                "selected_artifact_ids": [item.artifact_id for item in signals],
                "excluded_artifact_ids": sorted(excluded),
                "citation_artifact_ids": [],
                "source_trust": signals[0].metadata.get("source_trust"),
                "gap_effect_allowed": False,
            },
        }

    answer_stages = ("curated", "reuse_feed", "linked_project", "raw_keyword")
    all_matches = [item for stage in answer_stages for item in eligible.get(stage, [])]
    # Cross-stage comparison is opt-in; contradictions within a loaded stage
    # never become an answer by iteration order.
    comparison_groups = [eligible.get(stage, []) for stage in answer_stages]
    if compare_stages and complete:
        comparison_groups.append(all_matches)
    conflicting = any(
        len({
            values[key]
            for item in group
            if isinstance((values := _progressive_values(item, required_evidence)).get(key), str)
        }) > 1
        for group in comparison_groups for key in required_evidence
    )
    if conflicting:
        return {
            "terminal": ("conflict", "evidence_conflict"),
            "data": {
                "stage": None,
                "selected_artifact_ids": sorted(item.artifact_id for item in all_matches),
                "excluded_artifact_ids": sorted(excluded),
                "citation_artifact_ids": [],
                "gap_effect_allowed": False,
                **hint_metadata(len(all_matches)),
            },
        }

    selected_stage = next(
        (stage for stage in answer_stages if eligible.get(stage)),
        None,
    )
    if selected_stage is not None and (not compare_stages or complete):
        selected = eligible[selected_stage]
        result_bytes = sum(
            len(json.dumps(raw_evidence_hit(item, query), ensure_ascii=False).encode("utf-8"))
            if selected_stage == "raw_keyword" else item.size_bytes
            for item in selected
        )
        if len(selected) > max_result_records or result_bytes > max_result_bytes:
            return {
                "terminal": ("incomplete", "resource_exhausted"),
                "data": {
                    "stage": None,
                    "selected_artifact_ids": [],
                    "excluded_artifact_ids": sorted(excluded),
                    "citation_artifact_ids": [],
                    "gap_effect_allowed": False,
                    "budget_used": {
                        "records": len(selected),
                        "bytes": result_bytes,
                    },
                },
            }
        reason = {
            "reuse_feed": "evidence_available",
            "raw_keyword": "untrusted_evidence",
        }.get(selected_stage, "coverage_complete")
        if filters:
            reason = "filter_match" if selected_stage == "curated" else "filter_expanded"
        evidence: dict[str, str] = {}
        for item in selected:
            value_map = _progressive_values(item, required_evidence)
            evidence.update(
                {
                    key: str(value_map[key])
                    for key in required_evidence
                    if isinstance(value_map.get(key), str)
                }
            )
        selected_ids = [item.artifact_id for item in selected]
        return {
            "terminal": ("ok", reason),
            "data": {
                "stage": selected_stage,
                "selected_artifact_ids": selected_ids,
                "excluded_artifact_ids": sorted(excluded),
                "citation_artifact_ids": selected_ids,
                "source_trust": selected[0].metadata.get("source_trust"),
                "evidence": evidence,
                "gap_effect_allowed": False,
                "budget_used": {"records": len(selected), "bytes": result_bytes},
                **hint_metadata(len(selected)),
            },
        }

    if not complete:
        return {
            "terminal": ("continue", "stage_no_match"),
            "data": {
                "stage": evaluated_stages[-1] if evaluated_stages else None,
                "selected_artifact_ids": [],
                "excluded_artifact_ids": sorted(excluded),
                "citation_artifact_ids": [],
                "gap_effect_allowed": False,
            },
        }

    if filters:
        return {
            "terminal": ("incomplete", "filter_no_match"),
            "data": {
                **hint_metadata(),
                "stage": None,
                "selected_artifact_ids": [],
                "excluded_artifact_ids": sorted(excluded),
                "citation_artifact_ids": [],
                "gap_effect_allowed": False,
            },
        }

    if "raw_keyword" in search_envelope:
        return {
            "terminal": ("incomplete", "raw_no_match"),
            "data": {
                **hint_metadata(),
                "stage": None,
                "selected_artifact_ids": [],
                "excluded_artifact_ids": sorted(excluded),
                "citation_artifact_ids": [],
                "gap_effect_allowed": False,
            },
        }

    if gap_admission != "proof_required":
        return {
            "terminal": ("incomplete", "knowledge_absent"),
            "data": {
                **hint_metadata(),
                "stage": None,
                "selected_artifact_ids": [],
                "excluded_artifact_ids": sorted(excluded),
                "citation_artifact_ids": [],
                "gap_effect_allowed": False,
            },
        }

    proof_binding = proof_context if isinstance(proof_context, dict) else {}
    proof_material = json.dumps(
        {
            "query": query,
            "required_evidence": required_evidence,
            "search_envelope": search_envelope,
            "filters": filters,
            "manifests": manifests,
            "context": proof_binding,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    proof_sha256 = sha256(proof_material.encode("utf-8")).hexdigest()
    return {
        "terminal": ("incomplete", "knowledge_absent"),
        "data": {
            **hint_metadata(),
            "stage": None,
            "selected_artifact_ids": [],
            "excluded_artifact_ids": sorted(excluded),
            "citation_artifact_ids": [],
            "gap_effect_allowed": True,
            "absence_proof": {
                "schema": "owledge.progressive-absence-proof/1",
                "proof_id": f"proof:sha256:{proof_sha256}",
                "required_evidence": list(required_evidence),
                "search_envelope": list(search_envelope),
                "coverage_case_id": proof_binding.get("coverage_case_id"),
                "coverage_case_revision": proof_binding.get("coverage_case_revision"),
                "query": query,
                "filters": {key: list(values) for key, values in filters.items()},
                "safe_topic": safe_topic,
                "snapshot_sha256": proof_sha256,
                "binding": proof_binding,
            },
        },
    }


def absence_proof_staleness_reason(
    coverage: CoverageOutcome | None,
    supplied: dict[str, object],
) -> str:
    """Classify one stale proof binding without authorizing an effect."""

    current = None if coverage is None else coverage.absence_proof
    if not isinstance(current, dict):
        return "absence_proof_mismatch"
    field_reasons = (
        ("coverage_registry_revision", "coverage_registry_revision_mismatch"),
        ("coverage_case_revision", "coverage_case_revision_mismatch"),
        ("provider_contracts", "provider_contract_revision_mismatch"),
        ("search_envelope_revision", "search_envelope_revision_mismatch"),
        ("policy_revision", "policy_revision_mismatch"),
        ("settings_revision", "settings_revision_mismatch"),
        ("source_snapshot_sha256", "source_snapshot_mismatch"),
    )
    for field, reason in field_reasons:
        if supplied.get(field) != current.get(field):
            return reason
    return "absence_proof_mismatch"


def _registry(
    documents: tuple[ManagedMarkdown, ...],
) -> ManagedMarkdown | None:
    matches = tuple(
        item
        for item in documents
        if item.metadata.get("schema") == "owledge.coverage-case-registry/1"
        and item.metadata.get("lifecycle") == "accepted"
        and item.metadata.get("processing_layer") == "condensed"
        and item.metadata.get("source_trust") == "internal"
    )
    return matches[0] if len(matches) == 1 else None


def _matches_prefix(relative_path: str, prefixes: list[object]) -> bool:
    return any(
        isinstance(prefix, str) and prefix and relative_path.startswith(prefix)
        for prefix in prefixes
    )


def _snapshot(
    documents: tuple[ManagedMarkdown, ...],
    prefixes: list[object],
) -> tuple[tuple[ManagedMarkdown, ...], str, int]:
    candidates = tuple(
        sorted(
            (item for item in documents if _matches_prefix(item.relative_path, prefixes)),
            key=lambda item: item.artifact_id,
        )
    )
    manifest = [
        {
            "artifact_id": item.artifact_id,
            "authority_id": item.authority_id,
            "relative_path": item.relative_path,
            "revision": item.revision,
            "sha256": item.content_sha256,
            "size": item.size_bytes,
        }
        for item in candidates
    ]
    encoded = json.dumps(
        manifest,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return candidates, sha256(encoded).hexdigest(), sum(item.size_bytes for item in candidates)


def _provider_matches(
    document: ManagedMarkdown,
    contract: dict[str, object],
) -> bool:
    field_bindings = {
        "authority_id": document.authority_id,
        "schema": document.metadata.get("schema"),
        "lifecycle": document.metadata.get("lifecycle"),
        "processing_layer": document.metadata.get("processing_layer"),
        "source_trust": document.metadata.get("source_trust"),
        "knowledge_kind": document.metadata.get("knowledge_kind"),
        "memory_kind": document.metadata.get("memory_kind"),
    }
    expected_bindings = {
        "authority_id": contract.get("provider_authority_id"),
        "schema": contract.get("provider_schema"),
        "lifecycle": contract.get("lifecycle"),
        "processing_layer": contract.get("processing_layer"),
        "source_trust": contract.get("source_trust"),
        "knowledge_kind": contract.get("knowledge_kind"),
        "memory_kind": contract.get("memory_kind"),
    }
    for key, expected in expected_bindings.items():
        actual = field_bindings[key]
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def _value_matches(value: object, contract: object) -> bool:
    return evidence_value_matches(value, contract)


def _assessment_id(authority_id: str, coverage_case_id: str) -> str:
    authority_slug = authority_id.replace(":", "-")
    coverage_slug = coverage_case_id.removeprefix("coverage:")
    authority_scope = authority_id.split(":", 1)[-1] + "-"
    if coverage_slug.startswith(authority_scope):
        coverage_slug = coverage_slug[len(authority_scope) :]
    return f"assessment:{authority_slug}:{coverage_slug}-001"


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value)


def _valid_value_contract(value: object) -> bool:
    return valid_evidence_value_contract(value)


def _valid_provider_contract(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    processing = value.get("processing_layer")
    valid_processing = (
        processing in {"condensed", "delta"}
        if isinstance(processing, str)
        else isinstance(processing, list)
        and bool(processing)
        and len(processing) == len(set(processing))
        and all(item in {"condensed", "delta"} for item in processing)
    )
    return (
        value.get("schema") == "owledge.evidence-provider-contract/1"
        and _nonempty_string(value.get("revision"))
        and _nonempty_string(value.get("evidence_key"))
        and _nonempty_string(value.get("provider_authority_id"))
        and value.get("provider_schema") == "owledge.managed-markdown/1"
        and value.get("lifecycle") == "accepted"
        and valid_processing
        and value.get("source_trust") == "internal"
        and _nonempty_string(value.get("knowledge_kind"))
        and value.get("memory_kind") in {"semantic", "episodic"}
        and _valid_value_contract(value.get("value_contract"))
    )


def _valid_search_envelope(value: object, authority_id: str) -> bool:
    if not isinstance(value, dict):
        return False
    prefixes = value.get("relative_prefixes")
    provider_ids = value.get("provider_contract_ids")
    return (
        value.get("schema") == "owledge.search-envelope/1"
        and _nonempty_string(value.get("revision"))
        and value.get("authority_id") == authority_id
        and isinstance(prefixes, list)
        and bool(prefixes)
        and all(
            isinstance(item, str)
            and bool(item)
            and not item.startswith(("/", "\\"))
            and ".." not in item.split("/")
            for item in prefixes
        )
        and isinstance(provider_ids, list)
        and bool(provider_ids)
        and all(_nonempty_string(item) for item in provider_ids)
        and len(provider_ids) == len(set(provider_ids))
        and value.get("retriever_contract_revision")
        == "owledge.markdown-reference-retriever/1"
        and isinstance(value.get("max_records"), int)
        and int(value["max_records"]) > 0
        and isinstance(value.get("max_bytes"), int)
        and int(value["max_bytes"]) > 0
        and value.get("completion") == "all_matched_records_healthy_and_scanned"
    )


def _valid_coverage_case(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    required = value.get("required_evidence")
    provider_ids = value.get("provider_contract_ids")
    gap_admission = value.get("gap_admission")
    return (
        _nonempty_string(value.get("case_revision"))
        and isinstance(required, list)
        and bool(required)
        and all(_nonempty_string(item) for item in required)
        and len(required) == len(set(required))
        and _nonempty_string(value.get("safe_topic"))
        and _nonempty_string(value.get("search_envelope_id"))
        and isinstance(provider_ids, list)
        and bool(provider_ids)
        and all(_nonempty_string(item) for item in provider_ids)
        and len(provider_ids) == len(set(provider_ids))
        and gap_admission in {"disabled", "proof_required"}
        and (
            gap_admission != "proof_required"
            or _nonempty_string(value.get("resolution_route_id"))
        )
    )


def _valid_registry_bindings(
    cases: dict[str, object],
    providers: dict[str, object],
    envelopes: dict[str, object],
) -> bool:
    for case in cases.values():
        if not isinstance(case, dict):
            return False
        provider_ids = case.get("provider_contract_ids")
        required = case.get("required_evidence")
        envelope_id = case.get("search_envelope_id")
        if not (
            isinstance(provider_ids, list)
            and isinstance(required, list)
            and isinstance(envelope_id, str)
            and envelope_id in envelopes
            and all(item in providers for item in provider_ids)
        ):
            return False
        provider_keys = {
            providers[item].get("evidence_key")
            for item in provider_ids
            if isinstance(providers.get(item), dict)
        }
        if provider_keys != set(required):
            return False
    for envelope_id, envelope in envelopes.items():
        if not isinstance(envelope, dict):
            return False
        declared = envelope.get("provider_contract_ids")
        used = {
            provider_id
            for case in cases.values()
            if isinstance(case, dict) and case.get("search_envelope_id") == envelope_id
            for provider_id in case.get("provider_contract_ids", [])
            if isinstance(provider_id, str)
        }
        if not isinstance(declared, list) or set(declared) != used:
            return False
    return True


def assess_coverage(
    documents: tuple[ManagedMarkdown, ...],
    coverage_case_id: str,
) -> CoverageOutcome | None:
    """Evaluate one Project-owned coverage case without applying effects."""

    registry = _registry(documents)
    if registry is None:
        return None
    cases = registry.metadata.get("coverage_cases")
    provider_contracts = registry.metadata.get("provider_contracts")
    search_envelopes = registry.metadata.get("search_envelopes")
    if not all(isinstance(item, dict) for item in (cases, provider_contracts, search_envelopes)):
        return None
    if (
        not all(_valid_provider_contract(item) for item in provider_contracts.values())
        or not all(
            _valid_search_envelope(item, registry.authority_id)
            for item in search_envelopes.values()
        )
        or not all(_valid_coverage_case(item) for item in cases.values())
        or not _valid_registry_bindings(cases, provider_contracts, search_envelopes)
    ):
        return None
    raw_case = cases.get(coverage_case_id)
    if not _valid_coverage_case(raw_case):
        return None
    case_revision = raw_case.get("case_revision")
    required = raw_case.get("required_evidence")
    provider_ids = raw_case.get("provider_contract_ids")
    envelope_id = raw_case.get("search_envelope_id")
    safe_topic = raw_case.get("safe_topic")
    if not (
        isinstance(case_revision, str)
        and isinstance(required, list)
        and required
        and all(isinstance(key, str) for key in required)
        and isinstance(provider_ids, list)
        and all(isinstance(item, str) for item in provider_ids)
        and isinstance(envelope_id, str)
        and isinstance(safe_topic, str)
    ):
        return None
    envelope = search_envelopes.get(envelope_id)
    if not isinstance(envelope, dict):
        return None
    resolved_contracts = [provider_contracts.get(item) for item in provider_ids]
    if (
        not provider_ids
        or any(not isinstance(item, dict) for item in resolved_contracts)
        or any(
            item.get("schema") != "owledge.evidence-provider-contract/1"
            or not isinstance(item.get("revision"), str)
            or item.get("evidence_key") not in required
            for item in resolved_contracts
            if isinstance(item, dict)
        )
        or any(
            not any(
                isinstance(provider_contracts.get(contract_id), dict)
                and provider_contracts[contract_id].get("evidence_key") == evidence_key
                for contract_id in provider_ids
            )
            for evidence_key in required
        )
    ):
        return None
    prefixes = envelope.get("relative_prefixes")
    record_limit = envelope.get("max_records")
    byte_limit = envelope.get("max_bytes")
    envelope_provider_ids = envelope.get("provider_contract_ids")
    if not (
        isinstance(prefixes, list)
        and isinstance(record_limit, int)
        and isinstance(byte_limit, int)
        and isinstance(envelope_provider_ids, list)
        and all(isinstance(item, str) for item in envelope_provider_ids)
        and set(provider_ids) <= set(envelope_provider_ids)
    ):
        return None

    candidates, snapshot_hash, bytes_scanned = _snapshot(documents, prefixes)
    budget_complete = len(candidates) <= record_limit and bytes_scanned <= byte_limit
    evidence: dict[str, object] = {}
    selected: set[str] = set()
    excluded: dict[str, str] = {}
    diagnostics: list[dict[str, object]] = []
    for evidence_key in required:
        matching_contract_ids = [
            contract_id
            for contract_id in provider_ids
            if isinstance(provider_contracts.get(contract_id), dict)
            and provider_contracts[contract_id].get("evidence_key") == evidence_key
        ]
        values: dict[str, list[ManagedMarkdown]] = {}
        for document in candidates:
            raw_values = document.metadata.get("evidence_values")
            if not isinstance(raw_values, dict) or evidence_key not in raw_values:
                excluded.setdefault(document.artifact_id, "evidence_key_absent")
                continue
            value = raw_values[evidence_key]
            valid_contracts = [
                contract_id
                for contract_id in matching_contract_ids
                if _provider_matches(document, provider_contracts[contract_id])
                and _value_matches(
                    value,
                    provider_contracts[contract_id].get("value_contract"),
                )
            ]
            if not valid_contracts:
                excluded.setdefault(document.artifact_id, "provider_contract_mismatch")
                diagnostics.append(
                    {
                        "reason_code": "invalid_evidence_candidate",
                        "artifact_id": document.artifact_id,
                        "evidence_key": evidence_key,
                    }
                )
                continue
            values.setdefault(str(value), []).append(document)
        if len(values) == 1:
            value, sources = next(iter(values.items()))
            sources = sorted(sources, key=lambda item: item.artifact_id)
            contract_id = matching_contract_ids[0]
            contract = provider_contracts[contract_id]
            evidence[evidence_key] = {
                "value": value,
                "provider_contract_id": contract_id,
                "provider_contract_revision": contract["revision"],
                "sources": [
                    {
                        "artifact_id": item.artifact_id,
                        "authority_id": item.authority_id,
                        "revision": item.revision,
                    }
                    for item in sources
                ],
            }
            selected.update(item.artifact_id for item in sources)
        elif len(values) > 1:
            diagnostics.append(
                {
                    "reason_code": "evidence_conflict",
                    "evidence_key": evidence_key,
                    "candidate_values": sorted(values),
                    "candidate_provenance": [
                        {
                            "value": value,
                            "sources": [
                                {
                                    "artifact_id": item.artifact_id,
                                    "authority_id": item.authority_id,
                                    "revision": item.revision,
                                }
                                for item in sorted(
                                    values[value],
                                    key=lambda source: source.artifact_id,
                                )
                            ],
                        }
                        for value in sorted(values)
                    ],
                }
            )

    selection_complete = len(selected) <= 8
    complete = (
        budget_complete
        and selection_complete
        and len(evidence) == len(required)
        and not diagnostics
    )
    unresolved = sorted(key for key in required if key not in evidence)
    source_registered = bool(candidates)
    provable_absence = (
        budget_complete
        and selection_complete
        and source_registered
        and bool(unresolved)
        and not diagnostics
        and raw_case.get("gap_admission") == "proof_required"
    )
    diagnostic_codes = {str(item.get("reason_code")) for item in diagnostics}
    if complete:
        assessment_kind = "coverage_satisfied"
    elif not budget_complete or not selection_complete:
        assessment_kind = "resource_exhausted"
    elif "evidence_conflict" in diagnostic_codes:
        assessment_kind = "evidence_conflict"
    elif "invalid_evidence_candidate" in diagnostic_codes:
        assessment_kind = "technical_failure"
    elif not source_registered:
        assessment_kind = "source_not_registered"
    elif provable_absence:
        assessment_kind = "knowledge_absent"
    else:
        assessment_kind = "knowledge_unresolved"
    source_health = [
        {"artifact_id": item.artifact_id, "status": "healthy"}
        for item in candidates
    ]
    budget: dict[str, object] = {
        "outcome": "complete" if budget_complete and selection_complete else "exceeded",
        "records_scanned": len(candidates),
        "bytes_scanned": bytes_scanned,
        "record_limit": record_limit,
        "byte_limit": byte_limit,
    }
    if not selection_complete:
        budget["selected_records"] = len(selected)
        budget["selected_record_limit"] = 8
    assessment = {
        "schema": "owledge.coverage-assessment/1",
        "assessment_id": _assessment_id(registry.authority_id, coverage_case_id),
        "assessment": assessment_kind,
        "coverage_case_id": coverage_case_id,
        "coverage_case_revision": case_revision,
        "source_snapshot_id": f"snapshot:sha256:{snapshot_hash}",
        "required_evidence": list(required),
        "evidence": evidence,
        "selected_artifact_ids": sorted(selected) if selection_complete else [],
        "excluded_candidates": [
            {"artifact_id": artifact_id, "reason_code": reason_code}
            for artifact_id, reason_code in sorted(excluded.items())
            if artifact_id not in selected
        ],
        "source_health": source_health,
        "scan_complete": budget_complete and selection_complete,
        "budget": budget,
        "diagnostics": diagnostics,
        "gap_effect_allowed": provable_absence,
    }
    absence_proof: dict[str, object] | None = None
    if provable_absence:
        authority = next(
            (
                item
                for item in documents
                if item.metadata.get("schema") == "owledge.authority-unit/1"
                and item.authority_id == registry.authority_id
            ),
            None,
        )
        envelope_revision = envelope.get("revision")
        retriever_revision = envelope.get("retriever_contract_revision")
        if not (
            authority is not None
            and isinstance(envelope_revision, str)
            and isinstance(retriever_revision, str)
        ):
            assessment["assessment"] = "knowledge_unresolved"
            assessment["gap_effect_allowed"] = False
            return CoverageOutcome(
                assessment=assessment,
                absence_proof=None,
                safe_topic=safe_topic,
            )
        proof_provider_contracts = [
            {
                "provider_contract_id": contract_id,
                "revision": provider_contracts[contract_id]["revision"],
            }
            for contract_id in sorted(provider_ids)
            if isinstance(provider_contracts.get(contract_id), dict)
            and isinstance(provider_contracts[contract_id].get("revision"), str)
        ]
        absence_proof = {
            "schema": "owledge.knowledge-absence-proof/1",
            "active_authority_id": registry.authority_id,
            "coverage_case_id": coverage_case_id,
            "coverage_case_revision": case_revision,
            "search_envelope_id": envelope_id,
            "search_envelope_revision": envelope_revision,
            "policy_revision": authority.metadata["policy_revision"],
            "settings_revision": authority.metadata["settings_revision"],
            "source_snapshot_sha256": snapshot_hash,
            "scan_complete": True,
            "budget_outcome": "complete",
            "unresolved_evidence_keys": unresolved,
            "reference_retriever_contract_revision": retriever_revision,
            "coverage_registry_artifact_id": registry.artifact_id,
            "coverage_registry_revision": registry.revision,
            "provider_contracts": proof_provider_contracts,
            "source_health": source_health,
        }
        canonical_proof = json.dumps(
            absence_proof,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        assessment["absence_proof_id"] = f"proof:sha256:{sha256(canonical_proof).hexdigest()}"
    return CoverageOutcome(
        assessment=assessment,
        absence_proof=absence_proof,
        safe_topic=safe_topic,
    )


def retrieve_evidence(
    documents: tuple[ManagedMarkdown, ...],
    coverage_case_id: str,
) -> tuple[tuple[str, ...], dict[str, str], tuple[str, ...], str | None]:
    required: tuple[str, ...] = ()
    safe_topic: str | None = None
    for item in documents:
        cases = item.metadata.get("coverage_cases")
        if isinstance(cases, dict) and coverage_case_id in cases:
            raw = cases[coverage_case_id]
            if isinstance(raw, list) and all(isinstance(key, str) for key in raw):
                required = tuple(raw)
            elif isinstance(raw, dict):
                raw_required = raw.get("required_evidence")
                raw_topic = raw.get("safe_topic")
                if (
                    isinstance(raw_required, list)
                    and all(isinstance(key, str) for key in raw_required)
                    and isinstance(raw_topic, str)
                    and raw_topic
                ):
                    required = tuple(raw_required)
                    safe_topic = raw_topic
            break
    evidence: dict[str, str] = {}
    selected: set[str] = set()
    for item in documents:
        if item.metadata.get("lifecycle") != "accepted":
            continue
        values = item.metadata.get("evidence_values")
        if not isinstance(values, dict):
            continue
        for key in required:
            value = values.get(key)
            if isinstance(value, str) and key not in evidence:
                evidence[key] = value
                selected.add(item.artifact_id)
    return required, evidence, tuple(sorted(selected)), safe_topic
