"""Private explicit contribution setup and submission; effects are Core-owned."""
from pathlib import Path


class ProjectReuseRegistration:
    def __init__(self, project_workspace, global_workspace):
        from owledge_core.api import Core
        self.project = Path(project_workspace)
        self.target = Path(global_workspace)
        self.core = Core.open({}, identity_profile="mvp-v1")

    def preview(self):
        return self.core._project_reuse_from_local_owner(self.project, self.target)

    def apply(self):
        return self.core._project_reuse_from_local_owner(self.project, self.target, apply=True)

    def recover(self):
        return self.core._project_reuse_from_local_owner(self.project, self.target, recover=True)


class ProjectContribution:
    def __init__(self, project_workspace, *, connection: str | None = None, transport: str = "cli"):
        from .local_setup import open_workspace
        from .project_workspace import LINKED_SCHEMA, AGENT
        from .knowledge_workspace import KnowledgeWorkspaceJourney
        from .mcp import ContributorMcpAdapter
        self.workspace = Path(project_workspace)
        self.connection = connection
        if transport not in {"cli", "mcp"}:
            raise ValueError("unknown contribution transport")
        if connection is None:
            self.core, self.state = open_workspace(self.workspace)
            principal = AGENT
        else:
            from .connections import resolve_connection
            self.core, self.state, profile = resolve_connection(self.workspace, connection)
            if profile["source_link_id"] is not None:
                raise ValueError("Project contribution uses the saved link, not a raw Source Link profile.")
            principal = profile["principal_id"]
        if self.state.get("schema") != LINKED_SCHEMA:
            raise ValueError("Projektprofil benötigt zuerst eine freigegebene Global-Beitragsverknüpfung.")
        self.knowledge = KnowledgeWorkspaceJourney(self.core, authority_id=self.state["authority_id"], principal_id=principal,
            connection_name=connection, transport=transport if connection else None)
        self.agent = ContributorMcpAdapter(self.core, principal_id=principal, active_authority_id=self.state["authority_id"],
            source_link_id=self.state["global_contribution"]["source_link_id"], reported={"agent_name": connection or "project-cli"},
            adapter_observed={"runtime": "owledge-local-mcp" if transport == "mcp" else "owledge-local-cli" if connection else "source-local-cli"})
        from .owner import LocalOwnerAdapter
        self.owner = LocalOwnerAdapter(self.core, principal_id="principal:local-owner",
            active_authority_id=self.state["authority_id"], reported={"agent_name": "human-cli", "model": "none"},
            adapter_observed={"runtime": "owledge-local-cli", "runtime_version": "1", "run_id": "essence-contribution"})
        self.pending = None

    def _check_live(self):
        if self.connection is None:
            return
        from .connections import resolve_connection
        _, state, profile = resolve_connection(self.workspace, self.connection)
        if (profile["principal_id"] != self.agent._principal_id
                or profile["source_link_id"] is not None
                or state.get("global_contribution") != self.state["global_contribution"]):
            raise ValueError("Named Project contribution binding changed.")

    def _owner_contribute(self, operation_id, payload):
        """Trusted native CLI Owner transition; target is the validated link."""
        return self.core._execute_from_local_owner({
            "schema": "owledge.core-command/1", "operation": "contribute_for_reuse",
            "operation_id": operation_id,
            "principal": {"principal_id": "principal:local-owner", "assurance": "local_owner",
                          "reported": {"agent_name": "human-cli", "model": "none"},
                          "adapter_observed": {"runtime": "owledge-local-cli", "runtime_version": "1", "run_id": "essence-contribution"}},
            "active_authority_id": self.state["authority_id"],
            "target_authority_id": self.state["global_contribution"]["authority_id"],
            "source_link_id": self.state["global_contribution"]["source_link_id"],
            "expected_revisions": {}, "payload": payload})

    def preview(self, name, revision=None, expected_sha256=None):
        from .owner_journey import stable_operation_id
        self._check_live()
        self.pending = None
        essence = name == "essence:project"
        if essence and self.connection is not None:
            return {"status": "needs_attention", "message": "Project Essence contribution remains a separate local Owner action."}
        if essence:
            payload = {"artifact_id": f"memory:{self.state['authority_id'].replace(':', '-')}-essence-project"}
            if revision:
                payload["revision"] = revision
            opened = self.owner.execute("curated_read", stable_operation_id("owner-essence-read", payload), payload)
            source = {"status": "answered", **opened["data"]} if opened.get("status") == "ok" and opened.get("reason_code") != "reference_not_found" else {"status": "needs_attention", "details": opened}
        else:
            source = self.knowledge.read(name, revision)
        if source.get("status") != "answered" or source.get("knowledge_kind") not in {"lesson", "idea", "finding", "project_essence"}:
            return {"status": "needs_attention", "message": "Wähle ein freigegebenes Project Lesson/Idea/Finding.", "details": source}
        if expected_sha256 is not None and source.get("content_sha256") != expected_sha256:
            return {"status": "stale", "message": "Project record hash changed; preview again."}
        payload = {"source_artifact_id": source["artifact_id"], "expected_source_revision": source["revision"],
            "expected_source_sha256": source["content_sha256"], "preview": True}
        operation_id = stable_operation_id("project-contribution", {"source": source["artifact_id"],
            "revision": source["revision"], "sha256": source["content_sha256"], "target": self.state["global_contribution"]})
        actor = self._owner_contribute if essence else None
        result = (actor(operation_id, payload) if essence else
                  self.agent.execute("contribute_for_reuse", operation_id, payload,
                      target_authority_id=self.state["global_contribution"]["authority_id"]))
        if result.get("status") != "ok":
            return {"status": "needs_attention", "details": result}
        self.pending = (operation_id, {**payload, "preview": False}, actor)
        return {"status": "preview", **result["data"], "message": "Expliziter noncanonical Beitrag; Projekt bleibt Quelle der Wahrheit."}

    def apply(self):
        self._check_live()
        pending, self.pending = self.pending, None
        if pending is None:
            raise ValueError("Beitragsvorschau ist erforderlich.")
        result = (pending[2](pending[0], pending[1]) if pending[2] else
                  self.agent.execute("contribute_for_reuse", pending[0], pending[1],
                      target_authority_id=self.state["global_contribution"]["authority_id"]))
        if result.get("status") != "ok":
            return {"status": result.get("status", "needs_attention"), "details": result}
        return {"status": "recorded", "canonical": False, "receipt_id": result["receipt_id"],
            **result["data"], "message": "noncanonical Beitrag gespeichert; keine Global-Leserechte oder automatische Kuratierung."}
