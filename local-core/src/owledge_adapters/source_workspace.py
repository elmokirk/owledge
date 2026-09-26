"""Private read-only Source workspace; no generated knowledge or promotion lane."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re

from .local_setup import OwnerWorkspaceSetup, _state_bytes, _unlinked_path, runtime_fingerprint
from .mcp import ContributorMcpAdapter
from .owner_journey import stable_operation_id

SCHEMA = "owledge.private-source-workspace/1"
AUTHORITY = "user-global:source-access"
READER = "principal:source-reader"
LINK = "link:source-access-originals"
CASE = "coverage:source-access-originals"


def _document(identity: str, schema: str, **fields: object) -> str:
    metadata = {"schema": schema, "document_version": 1, "artifact_id": identity,
                "authority_id": AUTHORITY, "revision": "source-access-1",
                "lifecycle": "accepted", "processing_layer": "condensed",
                "source_trust": "internal", **fields}
    return "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}"
                              for key, value in metadata.items()) + "\n---\n\n# Source access configuration\n"


class SourceWorkspaceSetup(OwnerWorkspaceSetup):
    """Reuse source/path validation and atomic materialization, not DEMO facts."""

    def preview(self) -> dict[str, object]:
        return {**super().preview(), "profile": "source", "message":
                "Schreibgeschützter Quellenzugang ohne Beispielwissen. Originale bleiben unverändert; keine Kuratierung."}

    def apply(self) -> dict[str, object]:
        from owledge_connectors.markdown_source import MarkdownSourceConnector
        from owledge_core.project_io import materialize_owner_workspace, source_snapshot_target_name
        current = MarkdownSourceConnector(self.source).scan()
        if current != self.snapshot:
            raise ValueError("Die Quelle wurde seit der Vorschau verändert. Bitte neu starten.")
        state = {"schema": SCHEMA, "roots": {"user-global": "global",
                 "source": "sources/" + source_snapshot_target_name(current)},
                 "source_root": str(self.source), "source_id": current.source_id,
                 "source_snapshot_sha256": current.snapshot_sha256,
                 "runtime_sha256": runtime_fingerprint()}
        documents = {
            "global/.owledge/authority.md": _document("authority:source-access", "owledge.authority-unit/1",
                mode="read_only", policy_revision="policy-source-access-1", settings_revision="settings-source-access-1",
                actor_grants={READER: ["discover", "retrieve"]}),
            "global/.owledge/raw-link.md": _document(LINK, "owledge.knowledge-source-link/1",
                source_link_id=LINK, linked_authority_id=current.source_id, grants=["discover", "keyword_retrieve"],
                source_access={"access": "restricted", "principals": [READER]}),
            "global/.owledge/progressive-retrieval.md": _document("registry:source-access", "owledge.progressive-retrieval-registry/1",
                coverage_cases={CASE: {"revision": "source-access-1", "lifecycle": "accepted",
                    "required_evidence": ["raw_content"], "search_envelope": ["raw_keyword"],
                    "source_links": {"raw_keyword": [LINK]}, "gap_admission": "disabled"}}),
            "workspace.json": json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        }
        materialize_owner_workspace(self.target, documents, source_snapshot=current)
        return {"status": "ready", "profile": "source", "destination": str(self.target),
                "message": "Quellenzugang bereit. Kein kuratiertes Wissen erzeugt."}


def open_source_workspace(target: Path, state: dict[str, object]):
    from owledge_core.api import Core
    root = _unlinked_path(target)
    expected_keys = {"schema", "roots", "source_root", "source_id", "source_snapshot_sha256", "runtime_sha256"}
    if set(state) != expected_keys or state.get("schema") != SCHEMA:
        raise ValueError("Ungültiger Source-Workspace-Vertrag.")
    for key in ("source_root", "source_id", "source_snapshot_sha256", "runtime_sha256"):
        if not isinstance(state[key], str) or not state[key]:
            raise ValueError("Unvollständiger Source-Workspace-Vertrag.")
    mapping = state["roots"]
    if (not isinstance(mapping, dict) or set(mapping) != {"user-global", "source"}
            or mapping["user-global"] != "global" or not isinstance(mapping["source"], str)
            or not re.fullmatch(r"sources/[a-zA-Z0-9_-]+", mapping["source"])):
        raise ValueError("Ungültige lokale Source-Pfade.")
    roots = {key: _unlinked_path(root / relative) for key, relative in mapping.items()}
    if any(not path.is_relative_to(root) for path in roots.values()):
        raise ValueError("Source-Pfad liegt außerhalb des Workspace.")
    return Core.open(roots, identity_profile="mvp-v1",
                     clock=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")), state


class SourceWorkspaceJourney:
    def __init__(self, core: object):
        self.agent = ContributorMcpAdapter(core, principal_id=READER, active_authority_id=AUTHORITY,
            reported={"agent_name": "source-access", "model": "none"},
            adapter_observed={"runtime": "source-local-cli", "runtime_version": "1", "run_id": "source-access"})

    def ask(self, question: str, depth: str, **selection: object) -> dict[str, object]:
        if depth != "originals":
            return {"status": "not_available", "message":
                    "Dieser Quellenzugang enthält noch kein kuratiertes Wissen. Nutze --depth originals für belegte Quellensuche."}
        if not question.strip() and selection.get("discover_source_areas") is True:
            # The Core envelope requires a query; area enumeration never uses it
            # to match bodies. Keep a stable value for continuation binding.
            question = "area-discovery"
        if not question.strip():
            return {"status": "invalid", "message": "Bitte Suchwort angeben."}
        request = {"coverage_case_id": CASE, "query": question, **selection}
        if "source_areas" in request:
            request["source_areas"] = list(request["source_areas"])
        result = self.agent.execute("progressive_retrieve", stable_operation_id("source-search", request), request)
        if result.get("status") not in {"ok", "incomplete"}:
            return {"status": "needs_attention", "reason_code": result.get("reason_code"),
                    "message": result.get("summary"), "next_action": result.get("next_action")}
        data = result.get("data", {})
        hits = [{"file": hit["relative_path"], "excerpt": hit["snippet"],
                 "content_sha256": hit["content_sha256"], "verified_knowledge": False}
                for hit in data.get("raw_hits", [])]
        return {"status": "incomplete" if result["status"] == "incomplete" else "answered" if hits else "not_found",
                "reason_code": result.get("reason_code"), "next_action": result.get("next_action"),
                "excluded_source_files": data.get("excluded_source_files", []),
                "unreadable_source_files": data.get("unreadable_source_files", []),
                "source": "Originalquellen, unbestätigt", "source_hits": hits,
                "source_areas": data.get("source_areas", []), "continuation": data.get("continuation"),
                "search_progress": data.get("search_progress", {}), "gap_effect_allowed": False,
                "message": "Quellenbelege, keine bestätigte aktuelle Wahrheit. Kein Gap angelegt."}


def source_workspace_health(target: Path) -> dict[str, object]:
    from owledge_connectors.markdown_source import MarkdownSourceConnector
    from owledge_core.project_io import _source_snapshot_files, _validate_materialized_source
    state = json.loads(_state_bytes(target))
    core, state = open_source_workspace(target, state)
    inspected = SourceWorkspaceJourney(core).agent.execute("inspect", "op:source-access-doctor", {})
    healthy = (inspected.get("reason_code") == "project_inspected"
               and inspected.get("data", {}).get("health", {}).get("invalid_documents", 0) == 0)
    snapshot = MarkdownSourceConnector(Path(state["source_root"])).scan()
    unchanged = snapshot.snapshot_sha256 == state["source_snapshot_sha256"]
    if unchanged:
        expected, originals, _ = _source_snapshot_files(snapshot, "op:owner-workspace-setup", "principal:local-owner")
        _validate_materialized_source(target / state["roots"]["source"], expected, originals)
    return {"status": "healthy" if healthy and unchanged else "needs_attention",
            "source_unchanged": unchanged, "originals_unchanged": unchanged,
            "runtime_current": state["runtime_sha256"] == runtime_fingerprint(),
            "message": "Quellen-Snapshot geprüft; keine Synchronisierung oder Kuratierung."}
