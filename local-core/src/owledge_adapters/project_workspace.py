"""Private source-free Project binding; all knowledge effects belong to Core."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from .local_setup import _unlinked_path, _state_bytes, runtime_fingerprint
from .knowledge_workspace import KnowledgeWorkspaceJourney

SCHEMA = "owledge.private-project-workspace/1"
LINKED_SCHEMA = "owledge.private-project-workspace/2"
AGENT = "principal:project-agent"
OWNER = "principal:local-owner"


def _identity(value):
    if not isinstance(value, str) or len(value) > 80 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ValueError("Wähle eine kurze Projekt-ID, etwa sample-project.")
    return "project:" + value


class ProjectWorkspaceSetup:
    def __init__(self, target: Path, project_id: str):
        self.target = Path(target).absolute()
        self.authority_id = _identity(project_id)
        _unlinked_path(self.target.parent)
        if self.target.exists() or self.target.is_symlink():
            raise ValueError("Wähle einen neuen, noch nicht vorhandenen Arbeitsordner.")

    def preview(self):
        return {"status": "preview", "profile": "project", "destination": str(self.target),
                "authority_id": self.authority_id, "message": "Leerer Projektbereich; lokale Freigabe übernimmt vorgeschlagene Lessons."}

    def apply(self):
        from owledge_core.project_io import materialize_owner_workspace
        metadata = {"schema": "owledge.authority-unit/1", "document_version": 1,
                    "artifact_id": "authority:project", "authority_id": self.authority_id,
                    "revision": "project-1", "lifecycle": "accepted", "processing_layer": "condensed",
                    "source_trust": "internal", "mode": "read_write", "policy_revision": "policy-project-1",
                    "settings_revision": "settings-project-1", "rights_era": "owledge.bound-source-rights/1",
                    "connections": {}, "actor_grants": {
                        AGENT: ["discover", "retrieve", "propose"], OWNER: ["discover", "retrieve", "review", "promote"]}}
        state = {"schema": SCHEMA, "authority_id": self.authority_id, "roots": {"project": "project"},
                 "runtime_sha256": runtime_fingerprint()}
        document = "---\n" + "\n".join(f"{key}: {json.dumps(value)}" for key, value in metadata.items()) + "\n---\n\n# Project authority\n"
        materialize_owner_workspace(self.target, {"project/.owledge/authority.md": document,
            "workspace.json": json.dumps(state, sort_keys=True, indent=2) + "\n"})
        return {**self.preview(), "status": "ready"}


def open_project_workspace(target, state):
    from owledge_core.api import Core
    from owledge_connectors.markdown_source import MarkdownSourceConnector
    if isinstance(state, dict) and state.get("schema") == LINKED_SCHEMA:
        from owledge_core.project_io import validate_project_reuse_binding
        global_workspace = validate_project_reuse_binding(target, state)
        base = {key: SCHEMA if key == "schema" else value for key, value in state.items() if key != "global_contribution"}
        core, _ = open_project_workspace(target, base)
        roots = {**core._roots, state["global_contribution"]["authority_id"]: global_workspace / "global"}
        return Core.open(roots, identity_profile="mvp-v1", clock=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                         source_connector_factory=MarkdownSourceConnector), state
    if (not isinstance(state, dict) or set(state) != {"schema", "authority_id", "roots", "runtime_sha256"}
            or state.get("schema") != SCHEMA or state.get("roots") != {"project": "project"}
            or not isinstance(state.get("authority_id"), str) or not state["authority_id"].startswith("project:")
            or _identity(state["authority_id"].removeprefix("project:")) != state["authority_id"]
            or not isinstance(state.get("runtime_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", state["runtime_sha256"])):
        raise ValueError("Ungültige Projektbindung.")
    root = _unlinked_path(Path(target))
    project = _unlinked_path(root / "project")
    core = Core.open({state["authority_id"]: project}, identity_profile="mvp-v1",
                     clock=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                     source_connector_factory=MarkdownSourceConnector)
    return core, state


def project_workspace_health(target):
    core, state = open_project_workspace(target, json.loads(_state_bytes(target)))
    result = KnowledgeWorkspaceJourney(core, authority_id=state["authority_id"], principal_id=AGENT).agent.execute("inspect", "op:project-doctor", {})
    healthy = result.get("reason_code") == "project_inspected" and result.get("data", {}).get("health", {}).get("invalid_documents", 0) == 0
    return {"status": "healthy" if healthy else "needs_attention", "runtime_current": state["runtime_sha256"] == runtime_fingerprint()}


class ProjectCaseJourney:
    """Human-named facade over persisted Project Coverage and Gap records."""

    def __init__(self, core, authority_id: str, principal_id: str = AGENT):
        from .knowledge_workspace import KnowledgeWorkspaceJourney
        self.core = core
        self.authority_id = authority_id
        self.journey = KnowledgeWorkspaceJourney(core, authority_id=authority_id, principal_id=principal_id)

    def _check_recovery(self):
        from owledge_core.project_io import case_configuration_pending
        if case_configuration_pending(self.core._roots[self.authority_id]):
            raise ValueError("Projektfall-Konfiguration unterbrochen; case recover als Owner ausführen.")

    def _case(self, name: str):
        self._check_recovery()
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ValueError("Wähle einen konfigurierten Fallnamen.")
        documents = self.core._repository.snapshot(self.authority_id)
        registries = [item for item in documents if item.metadata.get("schema") == "owledge.coverage-case-registry/1"]
        routes = [item for item in documents if item.metadata.get("schema") == "owledge.artifact-routing/1"]
        if len(registries) != 1 or len(routes) != 1:
            raise ValueError("Projektfälle sind nicht vollständig konfiguriert.")
        registry = registries[0].metadata
        routing = routes[0].metadata
        case = registry.get("coverage_cases", {}).get(f"coverage:{name}")
        route = routing.get("routes", {}).get(f"route:{name}")
        provider = registry.get("provider_contracts", {}).get(f"provider:{name}")
        if not all(isinstance(item, dict) for item in (case, route, provider)):
            raise ValueError("Der Projektfall ist nicht konfiguriert.")
        if (case.get("case_name") != name or case.get("resolution_route_id") != f"route:{name}"
                or route.get("coverage_case_id") != f"coverage:{name}"
                or case.get("required_evidence") != [provider.get("evidence_key")]
                or route.get("value_contract") != provider.get("value_contract")):
            raise ValueError("Der Projektfall ist inkonsistent.")
        return case, route, provider

    def list(self):
        self._check_recovery()
        documents = self.core._repository.snapshot(self.authority_id)
        registries = [item for item in documents if item.metadata.get("schema") == "owledge.coverage-case-registry/1"]
        if len(registries) > 1:
            raise ValueError("Projektfälle sind mehrdeutig.")
        cases = registries[0].metadata.get("coverage_cases", {}) if registries else {}
        return {"status": "ready", "cases": [item.get("case_name") for item in cases.values()
            if isinstance(item, dict) and isinstance(item.get("case_name"), str)]}

    def show(self, name: str):
        case, route, provider = self._case(name)
        return {"status": "ready", "case": name, "question": case["question"],
                "title": route["default_title"], "answer_type": provider["value_contract"]["type"],
                "value_contract": provider["value_contract"]}

    def ask(self, name: str):
        case, route, _ = self._case(name)
        result = self.journey.agent.execute("retrieve", f"op:case-ask:{name}:{case['case_revision']}",
            {"question": case["question"], "coverage_case_id": f"coverage:{name}"})
        if (result.get("status"), result.get("reason_code")) == ("incomplete", "knowledge_absent"):
            return {"status": "knowledge_absent", "case": name, "question": case["question"],
                    "absence_proof_id": result["data"]["assessment"]["absence_proof_id"],
                    "proof_complete": isinstance(result["data"].get("absence_proof"), dict)}
        if (result.get("status"), result.get("reason_code")) == ("ok", "coverage_complete"):
            evidence = result["data"]["assessment"].get("evidence", {})
            evidence_item = evidence.get(next(iter(evidence), "")) if isinstance(evidence, dict) else None
            answer_text = evidence_item.get("value") if isinstance(evidence_item, dict) else evidence_item
            target = next((item for item in self.core._repository.snapshot(self.authority_id)
                           if item.artifact_id == route["target_artifact_id"]), None)
            return {"status": "answered", "case": name, "answer": evidence,
                    "answer_text": answer_text if isinstance(answer_text, str) else None,
                    "revision": target.revision if target else None,
                    "content_sha256": target.content_sha256 if target else None}
        return {"status": "needs_attention", "details": result}

    def answer(self, name: str, text: str, *, expected_revision: str | None = None,
               expected_sha256: str | None = None):
        from .owner_journey import stable_operation_id
        from owledge_core.contracts import evidence_value_matches
        from owledge_core.project_io import _gap_identity
        case, route, provider = self._case(name)
        if not evidence_value_matches(text, provider["value_contract"]):
            raise ValueError("Die Antwort verletzt den begrenzten Fallvertrag.")
        retrieval = self.journey.agent.execute("retrieve", stable_operation_id("case-retrieve", {"case": name}),
            {"question": case["question"], "coverage_case_id": f"coverage:{name}"})
        if (retrieval.get("status"), retrieval.get("reason_code")) == ("ok", "coverage_complete"):
            if not expected_revision or not expected_sha256:
                return {"status": "needs_attention", "message": "Vorhandene Antwort benötigt exakte Revision und SHA-256 aus case ask."}
            staged = self.journey.agent.execute("case_correct", stable_operation_id("case-correct", {
                "case": name, "revision": expected_revision, "sha256": expected_sha256, "text": text}),
                {"case_name": name, "text": text, "expected_revision": expected_revision,
                 "expected_sha256": expected_sha256})
            if (staged.get("status"), staged.get("reason_code")) != ("ok", "candidate_ready"):
                return {"status": "needs_attention", "details": staged}
            candidate = staged["data"]["candidate"]
            return {"status": "preview", "case": name, "candidate_id": candidate["candidate_id"],
                    "candidate_revision": candidate["candidate_revision"], "review_name": f"case:{name}",
                    "proposed_text": staged["data"]["changeset"]["result_document"].split("\n---\n", 1)[-1].strip(),
                    "base_revision": expected_revision, "base_sha256": expected_sha256}
        if (retrieval.get("status"), retrieval.get("reason_code")) != ("incomplete", "knowledge_absent"):
            return {"status": "needs_attention", "message": "Ein neuer Gap ist nicht belegt; vorhandenes Wissen benötigt exakte Korrektur.",
                    "details": retrieval}
        if expected_revision is not None or expected_sha256 is not None:
            return {"status": "needs_attention", "message": "Die exakte Korrekturbasis ist nicht mehr vorhanden; Fall erneut abfragen."}
        proof = retrieval["data"]["absence_proof"]
        proof_id = retrieval["data"]["assessment"]["absence_proof_id"]
        gap_id = _gap_identity(self.authority_id, f"coverage:{name}")
        try:
            current_gap = self.core._repository.read("gap", self.authority_id, {"gap_id": gap_id})
            expected_gap = current_gap["revision"]
        except ValueError:
            expected_gap = "absent"
        admitted = self.journey.agent.execute("gap_admit", stable_operation_id("case-gap-admit", {"proof": proof_id,
            "base": expected_gap}),
            {"absence_proof_id": proof_id, "absence_proof": proof,
             "expected_gap_revision": expected_gap})
        if admitted.get("status") != "ok":
            return {"status": "needs_attention", "details": admitted}
        opened = self.journey.agent.execute("bundle_open", stable_operation_id("case-bundle", {"gap": gap_id,
            "revision": admitted["data"]["gap_revision"]}),
            {"gap_ids": [gap_id], "selected_artifact_ids": [case["context_artifact_id"]]})
        if (opened.get("status"), opened.get("reason_code")) != ("ok", "bundle_ready"):
            return {"status": "needs_attention", "details": opened}
        staged = self.journey.agent.preview_gap_answer(stable_operation_id("case-answer", {"case": name,
            "proof": proof_id, "answer": text}), bundle_markdown=opened["data"]["bundle_markdown"],
            gap_id=gap_id, evidence_value=text, statement=f"{route['default_title']}: {text}",
            reported_content_origin="named-project-case")
        if (staged.get("status"), staged.get("reason_code")) != ("ok", "candidate_ready"):
            return {"status": "needs_attention", "details": staged}
        candidate = staged["data"]["candidate"]
        return {"status": "preview", "case": name, "candidate_id": candidate["candidate_id"],
                "candidate_revision": candidate["candidate_revision"], "review_name": f"case:{name}",
                "proposed_text": staged["data"]["changeset"]["result_document"].split("\n---\n", 1)[-1].strip(),
                "gap_id": gap_id, "gap_revision": admitted["data"]["gap_revision"]}

    def verify(self, name: str):
        from .owner_journey import stable_operation_id
        from owledge_core.project_io import _gap_identity
        self._case(name)
        gap_id = _gap_identity(self.authority_id, f"coverage:{name}")
        gap = self.core._repository.read("gap", self.authority_id, {"gap_id": gap_id})
        result = self.journey.owner.execute("gap_verify", stable_operation_id("case-verify", {"case": name,
            "revision": gap["revision"]}), {"gap_id": gap_id, "coverage_case_id": f"coverage:{name}",
            "expected_gap_revision": gap["revision"]})
        return {"status": "verified" if (result.get("status"), result.get("reason_code")) == ("ok", "gap_closed")
                else "needs_attention", "details": result}
