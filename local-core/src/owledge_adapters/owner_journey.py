"""Private human-facing host for the source-local MVP."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from uuid import uuid4
from dataclasses import dataclass
from typing import Mapping, Sequence

from .mcp import ContributorMcpAdapter
from .owner import LocalOwnerAdapter


__all__: tuple[str, ...] = ()


_ROUTE_NEGATIONS = frozenset({"kein", "keine", "keinen", "nicht", "ohne", "irrelevant"})


def stable_operation_id(operation: str, bound_input: Mapping[str, object]) -> str:
    """Return a deterministic private operation identity for exact input."""

    normalized = json.dumps(
        {"operation": operation, "input": dict(bound_input)},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256(normalized).hexdigest()[:16]
    verb = re.sub(r"[^a-z0-9]+", "-", operation.lower()).strip("-") or "operation"
    return f"op:{verb}:{digest}"


def _search_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))


def _search_tokens(value: str) -> frozenset[str]:
    tokens = re.findall(r"[a-z0-9]+", _search_text(value))
    return frozenset(
        token[:-1] if len(token) > 4 and token.endswith("s") else token
        for token in tokens
    )


@dataclass(frozen=True, slots=True)
class _CoverageRoute:
    coverage_case_id: str
    label: str
    aliases: tuple[str, ...]
    context_artifact_ids: tuple[str, ...]


class LocalOwnerHost:
    """Translate four human verbs into the private Core command contract."""

    verbs = ("setup", "doctor", "ask", "maintain")

    def __init__(
        self,
        core: object,
        *,
        principal_id: str,
        contributor_id: str,
        active_authority_id: str,
        coverage_catalog: Sequence[Mapping[str, object]],
        source_link_id: str | None = None,
        setup_adapter: object | None = None,
    ) -> None:
        self._coverage_catalog = tuple(self._route(item) for item in coverage_catalog)
        if getattr(core, "_identity_profile", None) != "mvp-v1":
            raise ValueError("The Owner host requires the MVP identity profile")
        self._contributor = ContributorMcpAdapter(
            core,
            principal_id=contributor_id,
            active_authority_id=active_authority_id,
            source_link_id=source_link_id,
            reported={"agent_name": "owledge-mvp-owner-host", "model": "none"},
            adapter_observed={
                "runtime": "source-local-owner-host",
                "runtime_version": "1",
                "run_id": stable_operation_id("host", {"authority": active_authority_id}),
            },
        )
        self._owner = LocalOwnerAdapter(
            core,
            principal_id=principal_id,
            active_authority_id=active_authority_id,
            reported={"agent_name": "local-owner", "model": "human"},
            adapter_observed={
                "runtime": "source-local-owner-host",
                "runtime_version": "1",
                "run_id": stable_operation_id("owner", {"authority": active_authority_id}),
            },
        )
        self._setup_adapter = setup_adapter
        self._pending: dict[str, object] | None = None
        self.last_receipt_id: str | None = None

    @staticmethod
    def _route(value: Mapping[str, object]) -> _CoverageRoute:
        case_id = value.get("coverage_case_id")
        label = value.get("label")
        aliases = value.get("aliases")
        context = value.get("context_artifact_ids")
        if not (
            isinstance(case_id, str)
            and case_id
            and isinstance(label, str)
            and label
            and isinstance(aliases, (tuple, list))
            and aliases
            and all(isinstance(item, str) and item for item in aliases)
            and isinstance(context, (tuple, list))
            and context
            and all(isinstance(item, str) and item for item in context)
        ):
            raise ValueError("Coverage catalog entries must be complete")
        return _CoverageRoute(case_id, label, tuple(aliases), tuple(context))

    @staticmethod
    def _invalid(message: str) -> dict[str, object]:
        return {"status": "invalid", "message": message, "user_action_required": False}

    @staticmethod
    def _friendly_failure(result: Mapping[str, object]) -> dict[str, object]:
        status = str(result.get("status", "invalid"))
        summary = str(result.get("summary", "Die Anfrage konnte nicht abgeschlossen werden."))
        labels = {
            "denied": "not_allowed",
            "stale": "needs_refresh",
            "conflict": "needs_review",
            "recovery_required": "needs_recovery",
            "incomplete": "incomplete",
            "invalid": "invalid",
        }
        return {
            "status": labels.get(status, "failed"),
            "message": summary,
            "user_action_required": status in {"stale", "conflict", "recovery_required"},
        }

    def _match_route(self, question: str) -> _CoverageRoute | None:
        query_tokens = _search_tokens(question)
        if query_tokens & _ROUTE_NEGATIONS:
            return None
        route_lexicons = {
            route.coverage_case_id: _search_tokens(" ".join((route.label, *route.aliases)))
            for route in self._coverage_catalog
        }
        matches = []
        for route in self._coverage_catalog:
            route_tokens = route_lexicons[route.coverage_case_id]
            other_tokens = frozenset().union(
                *(
                    tokens
                    for case_id, tokens in route_lexicons.items()
                    if case_id != route.coverage_case_id
                )
            )
            distinctive_tokens = route_tokens - other_tokens
            if (
                len(query_tokens & route_tokens) >= 2
                and query_tokens & distinctive_tokens
            ):
                matches.append(route)
        return matches[0] if len(matches) == 1 else None

    @staticmethod
    def _visible_answer(route: _CoverageRoute, evidence: object) -> str:
        if not isinstance(evidence, dict) or len(evidence) != 1:
            return f"{route.label}: im freigegebenen Projektwissen dokumentiert."
        value = next(iter(evidence.values()))
        if isinstance(value, dict):
            value = value.get("value")
        if isinstance(value, str) and ":" not in value and "\n" not in value:
            return f"{route.label}: {value}"
        return f"{route.label}: aktives Projektwissen."

    def run(self, verb: str, **arguments: object) -> dict[str, object]:
        """Run one user-visible verb and return a metadata-free result."""

        if verb not in self.verbs:
            return self._invalid("Unbekannter Befehl. Erlaubt sind setup, doctor, ask und maintain.")
        if verb == "setup" and arguments:
            return self._setup(arguments)
        if verb in {"setup", "doctor"}:
            return self._inspect(verb)
        if verb == "ask":
            question = arguments.get("question")
            if not isinstance(question, str) or not question.strip():
                return self._invalid("Bitte gib eine konkrete Frage an.")
            return self._ask(question.strip())
        return self._maintain(arguments)

    def _setup(self, arguments: Mapping[str, object]) -> dict[str, object]:
        if self._setup_adapter is None:
            return self._invalid("Die lokale Quellen-Einrichtung ist nicht verfügbar.")
        source = arguments.get("source")
        decision = arguments.get("decision")
        if isinstance(source, str) and source.strip() and decision is None:
            preview = getattr(self._setup_adapter, "preview", None)
            return (
                preview(source.strip())
                if preview is not None
                else self._invalid("Die lokale Quellen-Einrichtung ist unvollständig.")
            )
        if source is None and decision in {"apply", "reject"}:
            action = getattr(self._setup_adapter, str(decision), None)
            return (
                action()
                if action is not None
                else self._invalid("Die Setup-Entscheidung ist nicht verfügbar.")
            )
        return self._invalid(
            "Gib entweder einen Markdown-Ordner oder danach apply beziehungsweise reject an."
        )

    def _inspect(self, verb: str) -> dict[str, object]:
        result = self._contributor.execute(
            "inspect",
            stable_operation_id(verb, {"mode": "read_only"}),
            {},
        )
        if (result.get("status"), result.get("reason_code")) != ("ok", "project_inspected"):
            return self._friendly_failure(result)
        data = result.get("data")
        health = data.get("health") if isinstance(data, dict) else None
        invalid = health.get("invalid_documents", 0) if isinstance(health, dict) else 0
        if invalid:
            return {
                "status": "needs_repair",
                "message": f"{invalid} verwaltete Dateien sind ungültig.",
                "user_action_required": True,
            }
        return {
            "status": "ready" if verb == "setup" else "healthy",
            "message": "Owledge kann diesen Wissensbereich verwenden.",
            "user_action_required": False,
        }

    def _ask(self, question: str) -> dict[str, object]:
        route = self._match_route(question)
        if route is None:
            self._pending = None
            return {
                "status": "not_found",
                "message": "Die Frage passt zu keinem freigegebenen Wissensfall.",
                "user_action_required": False,
            }
        retrieve_input = {"question": question, "coverage_case_id": route.coverage_case_id}
        result = self._contributor.execute(
            "retrieve",
            stable_operation_id("retrieve", retrieve_input),
            retrieve_input,
        )
        terminal = (result.get("status"), result.get("reason_code"))
        if terminal == ("ok", "coverage_complete"):
            data = result.get("data")
            assessment = data.get("assessment") if isinstance(data, dict) else None
            evidence = assessment.get("evidence") if isinstance(assessment, dict) else None
            self._pending = None
            return {
                "status": "answered",
                "answer": self._visible_answer(route, evidence),
                "source": "Freigegebenes Projektwissen",
                "message": "Die Antwort stammt aus freigegebenem Wissen.",
                "user_action_required": False,
            }
        if terminal != ("incomplete", "knowledge_absent"):
            self._pending = None
            return self._friendly_failure(result)
        data = result.get("data")
        assessment = data.get("assessment") if isinstance(data, dict) else None
        proof = data.get("absence_proof") if isinstance(data, dict) else None
        proof_id = assessment.get("absence_proof_id") if isinstance(assessment, dict) else None
        if not isinstance(proof, dict) or not isinstance(proof_id, str):
            return self._invalid("Die Wissenslücke konnte nicht sicher belegt werden.")
        admitted = self._contributor.execute(
            "gap_admit",
            stable_operation_id("gap-admit", {"proof": proof_id}),
            {
                "absence_proof_id": proof_id,
                "absence_proof": proof,
                "expected_gap_revision": "absent",
            },
        )
        if (admitted.get("status"), admitted.get("reason_code")) not in {
            ("ok", "gap_opened"),
            ("ok", "gap_recurred"),
            ("ok", "gap_reopened"),
            ("ok", "gap_unchanged"),
        }:
            return self._friendly_failure(admitted)
        admitted_data = admitted.get("data")
        gap_id = admitted_data.get("gap_id") if isinstance(admitted_data, dict) else None
        gap_revision = (
            admitted_data.get("gap_revision") if isinstance(admitted_data, dict) else None
        )
        if not isinstance(gap_id, str) or not isinstance(gap_revision, str):
            return self._invalid("Der Wissensvorgang besitzt keine gültige Referenz.")
        bundle = self._contributor.execute(
            "bundle_open",
            stable_operation_id(
                "bundle-open",
                {"gap": gap_id, "context": route.context_artifact_ids},
            ),
            {"gap_ids": [gap_id], "selected_artifact_ids": list(route.context_artifact_ids)},
        )
        if (bundle.get("status"), bundle.get("reason_code")) != ("ok", "bundle_ready"):
            return self._friendly_failure(bundle)
        bundle_data = bundle.get("data")
        bundle_markdown = bundle_data.get("bundle_markdown") if isinstance(bundle_data, dict) else None
        if not isinstance(bundle_markdown, str):
            return self._invalid("Der Arbeitskontext konnte nicht vorbereitet werden.")
        self._pending = {
            "stage": "answer",
            "label": route.label,
            "gap_id": gap_id,
            "gap_revision": gap_revision,
            "coverage_case_id": route.coverage_case_id,
            "bundle_markdown": bundle_markdown,
        }
        return {
            "status": "needs_input",
            "message": f"Für '{route.label}' fehlt freigegebenes Wissen.",
            "question": question,
            "user_action_required": True,
        }

    def _maintain(self, arguments: Mapping[str, object]) -> dict[str, object]:
        decision = arguments.get("decision")
        if decision is not None:
            return self._decide(decision)
        answer = arguments.get("answer")
        if "statement" in arguments:
            return self._invalid(
                "Gib nur deine Antwort ein; Owledge erstellt den Wissenssatz selbst."
            )
        if not isinstance(answer, str) or not answer.strip():
            return self._invalid("Bitte beantworte die offene Frage, bevor du sie freigibst.")
        answer = answer.strip()
        if "\n" in answer or "\r" in answer:
            return self._invalid("Bitte gib eine kurze Antwort in einer Zeile ein.")
        if self._pending is None or self._pending.get("stage") != "answer":
            return self._invalid("Es gibt keine offene Frage für eine Vorschau.")
        label = self._pending.get("label")
        gap_id = self._pending.get("gap_id")
        bundle_markdown = self._pending.get("bundle_markdown")
        if not (
            isinstance(label, str)
            and isinstance(gap_id, str)
            and isinstance(bundle_markdown, str)
        ):
            return self._invalid("Der offene Wissensvorgang ist unvollständig.")
        statement = f"{label}: {answer}"
        try:
            result = self._contributor.preview_gap_answer(
                stable_operation_id(
                    "bundle-preview",
                    {"gap": gap_id, "answer": answer, "statement": statement},
                ),
                bundle_markdown=bundle_markdown,
                gap_id=gap_id,
                evidence_value=answer,
                statement=statement,
                reported_content_origin="local-owner",
            )
        except ValueError:
            return self._invalid("Die Antwort konnte nicht sicher als Vorschau aufbereitet werden.")
        if (result.get("status"), result.get("reason_code")) != ("ok", "candidate_ready"):
            return self._friendly_failure(result)
        data = result.get("data")
        candidate = data.get("candidate") if isinstance(data, dict) else None
        changeset = data.get("changeset") if isinstance(data, dict) else None
        if not isinstance(candidate, dict) or not isinstance(changeset, dict):
            return self._invalid("Die Vorschau ist unvollständig.")
        document = changeset.get("result_document")
        if not isinstance(document, str):
            return self._invalid("Die Vorschau enthält kein lesbares Ergebnis.")
        body = document.split("\n---\n", 1)[-1].strip()
        self._pending = {
            "stage": "preview",
            "candidate": candidate,
            "changeset": changeset,
            "preview": body,
            "gap_id": self._pending.get("gap_id"),
            "gap_revision": self._pending.get("gap_revision"),
            "coverage_case_id": self._pending.get("coverage_case_id"),
        }
        return {
            "status": "preview",
            "message": "Prüfe die Änderung. Erst approve schreibt freigegebenes Wissen.",
            "preview": body,
            "decision_options": ["approve", "reject"],
            "user_action_required": True,
        }

    def _decide(self, decision: object) -> dict[str, object]:
        if decision not in {"approve", "reject"}:
            return self._invalid("Die Entscheidung muss approve oder reject sein.")
        if self._pending is None or self._pending.get("stage") != "preview":
            return self._invalid("Vor der Entscheidung ist eine aktuelle Preview erforderlich.")
        if decision == "reject":
            self._pending = None
            return {
                "status": "cancelled",
                "message": "Die Vorschau wurde verworfen. Freigegebenes Wissen blieb unverändert.",
                "user_action_required": False,
            }
        candidate = self._pending.get("candidate")
        changeset = self._pending.get("changeset")
        if not isinstance(candidate, dict) or not isinstance(changeset, dict):
            return self._invalid("Die Vorschau ist nicht mehr vollständig.")
        candidate_id = candidate.get("candidate_id")
        candidate_revision = candidate.get("candidate_revision")
        if not isinstance(candidate_id, str) or not isinstance(candidate_revision, str):
            return self._invalid("Die Vorschau besitzt keine gültige Version.")
        reviewed = self._owner.execute(
            "candidate_review",
            stable_operation_id(
                "candidate-review",
                {"candidate": candidate_id, "revision": candidate_revision},
            ),
            {
                "candidate_id": candidate_id,
                "candidate_revision": candidate_revision,
                "decision": "approve",
            },
        )
        if (reviewed.get("status"), reviewed.get("reason_code")) != ("ok", "candidate_approved"):
            return self._friendly_failure(reviewed)
        reviewed_data = reviewed.get("data")
        reviewed_revision = (
            reviewed_data.get("candidate_revision") if isinstance(reviewed_data, dict) else None
        )
        if not isinstance(reviewed_revision, str):
            return self._invalid("Die Freigabe besitzt keine gültige Version.")
        promoted = self._owner.execute(
            "candidate_promote",
            stable_operation_id(
                "candidate-promote",
                {"candidate": candidate_id, "revision": reviewed_revision},
            ),
            {
                "candidate_id": candidate_id,
                "candidate_revision": reviewed_revision,
                "expected_base_revision": changeset.get("base_revision"),
                "expected_policy_revision": changeset.get("policy_revision"),
                "expected_settings_revision": changeset.get("settings_revision"),
                "idempotency_key": changeset.get("idempotency_key"),
            },
        )
        if (promoted.get("status"), promoted.get("reason_code")) != (
            "ok",
            "candidate_promoted",
        ):
            return self._friendly_failure(promoted)
        gap_id = self._pending.get("gap_id")
        gap_revision = self._pending.get("gap_revision")
        coverage_case_id = self._pending.get("coverage_case_id")
        if not (
            isinstance(gap_id, str)
            and isinstance(gap_revision, str)
            and isinstance(coverage_case_id, str)
        ):
            return self._invalid("Die Wissenslücke kann noch nicht sicher geschlossen werden.")
        verified = self._owner.execute(
            "gap_verify",
            stable_operation_id(
                "gap-verify",
                {"gap": gap_id, "revision": gap_revision},
            ),
            {
                "gap_id": gap_id,
                "coverage_case_id": coverage_case_id,
                "expected_gap_revision": gap_revision,
            },
        )
        if (verified.get("status"), verified.get("reason_code")) != (
            "ok",
            "gap_closed",
        ):
            return self._friendly_failure(verified)
        preview = self._pending.get("preview")
        self.last_receipt_id = verified.get("receipt_id")
        self._pending = None
        return {
            "status": "accepted",
            "message": "Die geprüfte Änderung ist jetzt freigegebenes Wissen.",
            "preview": preview if isinstance(preview, str) else "",
            "user_action_required": False,
        }


class WorkspaceOwnerJourney:
    """Small private DEMO presentation layer over the admitted Core operations."""

    def __init__(self, core: object, *, workspace=None) -> None:
        from .local_setup import PROJECT, GLOBAL, OWNER, CONTRIBUTOR, MAINTAINER
        self.core = core
        self.workspace = workspace
        common = {"reported": {"agent_name": "owner-workspace", "model": "none"},
                  "adapter_observed": {"runtime": "source-local-cli", "runtime_version": "1", "run_id": "owner-workspace"}}
        self.project = ContributorMcpAdapter(core, principal_id=CONTRIBUTOR, active_authority_id=PROJECT,
            source_link_id="link:demo-to-global", **common)
        self.global_agent = ContributorMcpAdapter(core, principal_id=MAINTAINER, active_authority_id=GLOBAL, **common)
        self.owner = LocalOwnerAdapter(core, principal_id=OWNER, active_authority_id=GLOBAL, **common)
        self._curation: dict[str, object] | None = None

    def gap_host(self) -> LocalOwnerHost:
        from .local_setup import PROJECT, OWNER, CONTRIBUTOR
        return LocalOwnerHost(self.core, principal_id=OWNER, contributor_id=CONTRIBUTOR,
            active_authority_id=PROJECT, source_link_id="link:demo-to-global", coverage_catalog=({
                "coverage_case_id": "coverage:demo-review-window", "label": "Agent-Lesson-Reviewfenster",
                "aliases": ("reviewfenster", "prüfzeit", "review window"),
                "context_artifact_ids": ("artifact:demo-project-brief",),
            },))

    def summary(self) -> dict[str, object]:
        # Each explicit observation is a new request, not replay of old evidence.
        result = self.global_agent.execute("maintenance_observe", stable_operation_id("summary", {"request": uuid4().hex}), {})
        if result.get("status") not in {"ok", "incomplete"}:
            return LocalOwnerHost._friendly_failure(result)
        data = result.get("data", {})
        return {"status": "observed" if result.get("status") == "ok" else "incomplete", "documents_scanned": data.get("documents_scanned", 0),
            "bytes_scanned": data.get("bytes_scanned", 0), "candidates": len(data.get("candidate_ids", [])),
            "metadata_entries_examined": data.get("metadata_entries_examined", 0),
            "metadata_directories_examined": data.get("metadata_directories_examined", 0),
            "metadata_entry_limit": data.get("metadata_entry_limit", 4096),
            "continuation_cursor": data.get("continuation_cursor"),
            "canonical_writes": data.get("canonical_writes", 0),
            "message": "Begrenzte Bestandsübersicht; keine automatische Gap-Erkennung und keine Modellaufrufe."}

    def preview_curation(self, topic: str) -> dict[str, object]:
        from .local_setup import curation_reference
        if topic not in {"lesson", "alternative"}:
            return LocalOwnerHost._invalid("Wähle lesson oder alternative.")
        data = curation_reference(self.workspace, topic) if self.workspace else None
        if data is None:
            contribution = self.contribute(topic)
            if contribution.get("status") != "ok":
                return LocalOwnerHost._friendly_failure(contribution)
            candidate = self.global_agent.execute("curate_candidate", stable_operation_id("curate", {"topic": topic}),
                {"contribution_ids": [contribution["data"]["contribution_id"]], "curation_slug": "demo-" + topic})
            if candidate.get("status") != "ok":
                return LocalOwnerHost._friendly_failure(candidate)
            data = candidate["data"]
            if self.workspace:
                data = curation_reference(self.workspace, topic, data)
        if not isinstance(data, dict) or any(not isinstance(data.get(key), str) for key in ("candidate_id", "candidate_revision", "idempotency_key")):
            return LocalOwnerHost._invalid("Die gespeicherte Vorschau ist unvollständig. Keine Freigabe möglich.")
        opened = self.owner.open_candidate(data["candidate_id"], data["candidate_revision"])
        if opened.get("status") != "ok":
            return LocalOwnerHost._friendly_failure(opened)
        self._curation = {"candidate": data, "preview": opened["data"]}
        source = opened["data"]["source"]
        return {"status": "preview", "proposed_text": opened["data"]["proposed_text"],
            "source": {"project": source["authority_id"].split(":", 1)[-1],
                "document": source["artifact_id"].split(":", 1)[-1], "revision": source["revision"]},
            "target": opened["data"]["target"],
            "message": "Nur dieser angezeigte Inhalt wird bei approve freigegeben.", "decision_options": ["approve", "reject", "cancel"]}

    def decide_curation(self, decision: str) -> dict[str, object]:
        if not self._curation:
            return LocalOwnerHost._invalid("Öffne zuerst die aktuelle Vorschau.")
        if decision not in {"approve", "reject", "cancel"}:
            return LocalOwnerHost._invalid("Wähle approve, reject oder cancel.")
        if decision == "cancel":
            self._curation = None
            return {"status": "cancelled", "message": "Keine Freigabe; Vorschau kann erneut geöffnet werden."}
        candidate, preview = self._curation["candidate"], self._curation["preview"]
        reviewed = self.owner.execute("candidate_review", stable_operation_id("review", {"candidate": candidate["candidate_id"], "decision": decision}),
            {"candidate_id": candidate["candidate_id"], "candidate_revision": candidate["candidate_revision"],
             "decision": decision, "expected_result_sha256": preview["content_sha256"]})
        if reviewed.get("status") != "ok":
            return LocalOwnerHost._friendly_failure(reviewed)
        if decision == "reject":
            self._curation = None
            return {"status": "rejected", "message": "Vorschlag abgelehnt; bestätigtes Wissen blieb unverändert."}
        promoted = self.owner.execute("candidate_promote", stable_operation_id("promote", {"candidate": candidate["candidate_id"]}),
            {"candidate_id": candidate["candidate_id"], "candidate_revision": reviewed["data"]["candidate_revision"],
             "expected_base_revision": "absent", "expected_policy_revision": "policy-global-1",
             "expected_settings_revision": "settings-global-1", "idempotency_key": candidate["idempotency_key"]})
        if promoted.get("status") != "ok":
            return LocalOwnerHost._friendly_failure(promoted)
        self._curation = None
        return {"status": "accepted", "message": "Geprüftes DEMO-Wissen ist jetzt global freigegeben."}

    def ask(self, question: str, depth: str, *, source_areas: tuple[str, ...] = (".",),
            source_cursor: dict[str, object] | None = None,
            discover_source_areas: bool = False, source_area_parent: str = ".",
            source_link_id: str | None = None) -> dict[str, object]:
        if depth == "originals" and discover_source_areas and not question.strip():
            question = "area-discovery"
        if not question.strip():
            return LocalOwnerHost._invalid("Bitte gib eine Frage oder ein Suchwort an.")
        tokens = _search_tokens(question)
        if depth != "originals":
            expected = {"beitrage", "beitrag", "reuse", "lesson", "wiederverwendung"} if depth == "feed" else {"speicher", "speichern", "gespeichert", "storage", "markdown"}
            if not tokens.intersection(expected) or tokens.intersection(_ROUTE_NEGATIONS):
                return {"status": "not_found", "message": "Kein passender DEMO-Wissensfall; keine Wissenslücke angelegt."}
        request = {"coverage_case_id": "coverage:demo-" + depth, "query": question}
        if depth == "originals":
            request.update({"source_areas": list(source_areas), "source_cursor": source_cursor,
                            "discover_source_areas": discover_source_areas,
                            "source_area_parent": source_area_parent, "source_link_id": source_link_id})
        result = self.global_agent.execute("progressive_retrieve", stable_operation_id("ask", {"question": question, "depth": depth,
            "source_areas": source_areas, "source_cursor": source_cursor, "discover_source_areas": discover_source_areas,
            "source_area_parent": source_area_parent, "source_link_id": source_link_id}), request)
        if result.get("status") == "incomplete" and depth == "originals":
            data = result.get("data", {})
            return {"status": "incomplete", "message": "Suchseite abgeschlossen; Suche noch unvollständig. Mit continuation fortsetzen." if data.get("continuation") else result.get("summary"),
                    "reason_code": result.get("reason_code"), "next_action": result.get("next_action"),
                    "gap_effect_allowed": False,
                    "source_areas": data.get("source_areas", []), "source_hits": [
                        {"file": hit["relative_path"], "excerpt": hit["snippet"], "verified_knowledge": False}
                        for hit in data.get("raw_hits", [])], "continuation": data.get("continuation"),
                    "search_progress": data.get("search_progress", {})}
        if result.get("status") != "ok":
            return LocalOwnerHost._friendly_failure(result)
        data = result.get("data", {})
        evidence = data.get("evidence", {})
        labels = {"curated": "Bestätigtes DEMO-Wissen", "project": "Bestätigtes DEMO-Projektwissen",
                  "feed": "Wiederverwendung, nichtkanonisch", "originals": "Originalquellen, unbestätigt"}
        return {"status": "answered", "source": labels[depth], "matches": len(data.get("selected_artifact_ids", [])),
            **({"source_areas": data.get("source_areas", []), "continuation": data.get("continuation"),
                "gap_effect_allowed": False} if depth == "originals" else {}),
            **({"search_progress": data["search_progress"]} if "search_progress" in data else {}),
            "answer": evidence.get("store", "Attributierte Beiträge verfügbar." if depth == "feed" else "Keyword-Treffer; keine bestätigte Wahrheitsaussage."),
            "source_hits": [{"file": hit["relative_path"], "excerpt": hit["snippet"], "verified_knowledge": False}
                for hit in data.get("raw_hits", [])],
            "message": "DEMO-Kandidat; keine automatische Wissenskuratierung."}

    def contribute(self, topic: str) -> dict[str, object]:
        from .local_setup import GLOBAL
        if topic not in {"lesson", "alternative"}:
            return LocalOwnerHost._invalid("Wähle lesson oder alternative.")
        return self.project.execute("contribute_for_reuse", stable_operation_id("contribute", {"topic": topic}),
            {"source_artifact_id": "lesson:demo-" + topic, "expected_source_revision": "demo-rev-1"}, target_authority_id=GLOBAL)
