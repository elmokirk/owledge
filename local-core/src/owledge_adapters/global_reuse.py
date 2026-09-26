"""Private CLI journey for reviewed Project Lesson reuse."""
from pathlib import Path

from .knowledge_workspace import AGENT, OWNER, SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA, _record_name
from .local_setup import open_workspace
from .mcp import ContributorMcpAdapter
from .owner import LocalOwnerAdapter
from .owner_journey import stable_operation_id
from .source_workspace import AUTHORITY


class GlobalReuseJourney:
    def __init__(self, workspace: Path, *, connection: str | None = None, transport: str = "cli"):
        self.workspace = Path(workspace)
        self.connection = connection
        if transport not in {"cli", "mcp"}:
            raise ValueError("unknown Global reuse transport")
        if connection is None:
            self.core, self.state = open_workspace(self.workspace)
            principal = AGENT
        else:
            from .connections import resolve_connection
            self.core, self.state, profile = resolve_connection(self.workspace, connection)
            if profile["source_link_id"] is not None:
                raise ValueError("Global reuse uses a general Contributor profile.")
            principal = profile["principal_id"]
        if self.state.get("schema") not in {SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}:
            raise ValueError("Global reuse requires a Knowledge workspace.")
        authority_id = AUTHORITY
        common = {"reported": {"agent_name": connection or "global-reuse-cli", "model": "none"},
                  "adapter_observed": {"runtime": "owledge-local-mcp" if transport == "mcp" else "owledge-local-cli" if connection else "source-local-cli",
                                       "runtime_version": "1", "run_id": "global-reuse"}}
        self.agent = ContributorMcpAdapter(self.core, principal_id=principal, active_authority_id=authority_id, **common)
        self.owner = LocalOwnerAdapter(self.core, principal_id=OWNER, active_authority_id=authority_id, **common)
        self.pending = None

    def _check_live(self):
        if self.connection is None:
            return
        from .connections import resolve_connection
        _, state, profile = resolve_connection(self.workspace, self.connection)
        if (profile["principal_id"] != self.agent._principal_id or profile["source_link_id"] is not None
                or state != self.state):
            raise ValueError("Named Global Contributor binding changed.")

    def discover(self, query: str, area: str | None = None, cursor: dict | None = None,
                 *, stage: str = "reuse_feed", filters: dict | None = None):
        self._check_live()
        payload = {"query": query, "knowledge_area": area, "cursor": cursor,
                   "stage": stage, "filters": filters or {}}
        result = self.agent.execute("reuse_feed_discover", stable_operation_id("reuse-feed", payload), payload)
        if result.get("status") in {"ok", "incomplete"}:
            return {"status": "incomplete" if result["status"] == "incomplete" else "discovered", **result["data"],
                    "message": "Bounded noncanonical Project contribution page; an empty page is not a Gap."}
        return {"status": "needs_attention", "details": result}

    def curate(self, *, name: str, contribution_id: str, revision: str, content_sha256: str,
               base_revision: str | None = None, base_sha256: str | None = None):
        self._check_live()
        self.pending = None
        slug = _record_name(name)
        payload = {"contribution_ids": [contribution_id], "curation_slug": slug,
                   "expected_contribution_revision": revision, "expected_contribution_sha256": content_sha256}
        if (base_revision is None) != (base_sha256 is None):
            return {"status": "needs_attention", "message": "Global refresh requires one complete exact base."}
        if base_revision is not None:
            payload["replacement_base"] = {"artifact_id": f"memory:{AUTHORITY.replace(':', '-')}-{slug}",
                                           "revision": base_revision, "content_sha256": base_sha256}
        result = self.agent.execute("curate_candidate", stable_operation_id("reuse-curation", payload), payload)
        if result.get("status") != "ok":
            return {"status": "needs_attention", "details": result}
        candidate = result["data"]
        if self.connection is not None:
            return {"status": "preview", "name": name, "candidate_id": candidate["candidate_id"],
                    "candidate_revision": candidate["candidate_revision"],
                    "review_preview": candidate["review_preview"], "contribution_ids": candidate["contribution_ids"],
                    "canonical": False,
                    "message": "Unreviewed Global Candidate staged; separate human review is required."}
        opened = self.owner.open_candidate(candidate["candidate_id"], candidate["candidate_revision"])
        if opened.get("status") != "ok":
            return {"status": "needs_attention", "details": opened}
        self.pending = {"candidate": candidate, "preview": opened["data"]}
        response = {"status": "preview", "name": name, "proposed_text": opened["data"]["proposed_text"],
                "source": opened["data"]["source"], "target": opened["data"]["target"],
                "message": "Only this unchanged Project Lesson is proposed for Global review."}
        if "base" in opened["data"]:
            response.update(old_text=opened["data"]["base"]["text"],
                            old_source_revision=opened["data"]["old_source"]["revision"],
                            new_source_revision=opened["data"]["source"]["revision"],
                            message="This exact selected Project snapshot will replace the shown Global Lesson after Owner review; revision ids do not prove latestness.")
        return response

    def decide(self, decision: str):
        pending, self.pending = self.pending, None
        if decision not in {"approve", "reject"} or pending is None:
            return {"status": "cancelled", "message": "No Global curation was approved."}
        candidate, preview = pending["candidate"], pending["preview"]
        request = {"candidate_id": candidate["candidate_id"], "candidate_revision": candidate["candidate_revision"],
                   "decision": decision, "expected_result_sha256": preview["content_sha256"]}
        reviewed = self.owner.execute("candidate_review", stable_operation_id("reuse-review", request), request)
        if reviewed.get("status") != "ok":
            return {"status": "needs_attention", "details": reviewed}
        if decision == "reject":
            return {"status": "rejected", "message": "Rejected; curated Global knowledge is unchanged."}
        request = {"candidate_id": candidate["candidate_id"], "candidate_revision": reviewed["data"]["candidate_revision"],
                   "expected_base_revision": preview.get("base", {}).get("revision", "absent"), "expected_policy_revision": preview["expected_policy_revision"],
                   "expected_settings_revision": preview["expected_settings_revision"], "idempotency_key": candidate["idempotency_key"]}
        promoted = self.owner.execute("candidate_promote", stable_operation_id("reuse-promote", request), request)
        return ({"status": "accepted", "receipt_id": promoted.get("receipt_id"),
                 "message": "Reviewed Project Lesson is now curated Global knowledge."}
                if promoted.get("status") == "ok" else {"status": "needs_attention", "details": promoted})
