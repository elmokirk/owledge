"""Explicit fresh local knowledge profile over Core-owned Candidate operations."""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
import re
from datetime import datetime, timezone
from uuid import uuid4

from .local_setup import OwnerWorkspaceSetup, runtime_fingerprint, _state_bytes
from .source_workspace import AUTHORITY, CASE, LINK, SCHEMA as SOURCE_SCHEMA, _document, open_source_workspace
from .mcp import ContributorMcpAdapter
from .owner import LocalOwnerAdapter
from .owner_journey import stable_operation_id

SCHEMA = "owledge.private-knowledge-workspace/1"
MULTISOURCE_SCHEMA = "owledge.private-knowledge-workspace/2"
SOURCE_FREE_SCHEMA = "owledge.private-knowledge-workspace/3"
AGENT = "principal:knowledge-agent"
OWNER = "principal:local-owner"


class KnowledgeWorkspaceSetup(OwnerWorkspaceSetup):
    def preview(self) -> dict[str, object]:
        if self.source is None:
            return {"status": "preview", "profile": "knowledge", "destination": str(self.target),
                    "documents": 0, "size_bytes": 0,
                    "message": "Neuer lokaler Wissensbereich ohne Quelle; Originalsuche wird erst nach expliziter Registrierung verfügbar."}
        return {**super().preview(), "profile": "knowledge", "message":
                "Neuer lokaler Wissensbereich: Agent darf lesen und vorschlagen; nur lokale Freigabe darf Wissen übernehmen. Originale bleiben unverändert."}

    def apply(self) -> dict[str, object]:
        from owledge_core.project_io import materialize_owner_workspace, source_snapshot_target_name
        if self.source is None:
            state = {"schema": SOURCE_FREE_SCHEMA, "roots": {"user-global": "global"},
                     "runtime_sha256": runtime_fingerprint(), "imports": []}
            documents = {
                "global/.owledge/authority.md": _document("authority:source-access", "owledge.authority-unit/1",
                    mode="read_write", policy_revision="policy-knowledge-1", settings_revision="settings-knowledge-1",
                    rights_era="owledge.bound-source-rights/1", connections={},
                    actor_grants={AGENT: ["discover", "retrieve", "propose"],
                                  OWNER: ["discover", "retrieve", "review", "promote"]}),
                "global/.owledge/progressive-retrieval.md": _document("registry:source-access", "owledge.progressive-retrieval-registry/1",
                    coverage_cases={}),
                "workspace.json": json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            }
            materialize_owner_workspace(self.target, documents)
            return {"status": "ready", "profile": "knowledge", "destination": str(self.target),
                    "message": "Leerer Wissensbereich bereit. Registriere eine Quelle für die Originalsuche."}
        from owledge_connectors.markdown_source import MarkdownSourceConnector
        current = MarkdownSourceConnector(self.source).scan()
        if current != self.snapshot:
            raise ValueError("Die Quelle wurde seit der Vorschau verändert. Bitte neu starten.")
        state = {"schema": SCHEMA, "roots": {"user-global": "global",
                 "source": "sources/" + source_snapshot_target_name(current)},
                 "source_root": str(self.source), "source_id": current.source_id,
                 "source_snapshot_sha256": current.snapshot_sha256, "runtime_sha256": runtime_fingerprint()}
        documents = {
            "global/.owledge/authority.md": _document("authority:source-access", "owledge.authority-unit/1",
                mode="read_write", policy_revision="policy-knowledge-1", settings_revision="settings-knowledge-1",
                rights_era="owledge.bound-source-rights/1", connections={},
                actor_grants={AGENT: ["discover", "retrieve", "propose"],
                              OWNER: ["discover", "retrieve", "review", "promote"]}),
            "global/.owledge/raw-link.md": _document(LINK, "owledge.knowledge-source-link/1",
                source_link_id=LINK, linked_authority_id=current.source_id, grants=["discover", "keyword_retrieve"],
                source_access={"access": "restricted", "principals": [AGENT, OWNER]}),
            "global/.owledge/progressive-retrieval.md": _document("registry:source-access", "owledge.progressive-retrieval-registry/1",
                coverage_cases={CASE: {"revision": "source-access-1", "lifecycle": "accepted",
                    "required_evidence": ["raw_content"], "search_envelope": ["raw_keyword"],
                    "source_links": {"raw_keyword": [LINK]}, "gap_admission": "disabled"}}),
            "workspace.json": json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        }
        materialize_owner_workspace(self.target, documents, source_snapshot=current)
        return {"status": "ready", "profile": "knowledge", "destination": str(self.target),
                "message": "Leerer Wissensbereich und Originalkopie bereit. Noch kein Wissen freigegeben."}


def open_knowledge_workspace(target: Path, state: dict[str, object]):
    source_free = state.get("schema") == SOURCE_FREE_SCHEMA
    if state.get("schema") in {MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}:
        from .local_setup import _unlinked_path
        from owledge_core.api import Core
        imports = state.get("imports")
        if not isinstance(imports, list) or not (0 if source_free else 1) <= len(imports) <= 64:
            raise ValueError("Ungültige zusätzliche Quellenbindungen.")
        if source_free:
            if (set(state) != {"schema", "roots", "runtime_sha256", "imports"}
                    or state.get("roots") != {"user-global": "global"}
                    or not isinstance(state.get("runtime_sha256"), str)
                    or not re.fullmatch(r"[0-9a-f]{64}", state["runtime_sha256"])):
                raise ValueError("Ungültiger quellenfreier Knowledge-Workspace-Vertrag.")
            roots = {"user-global": _unlinked_path(target / "global")}
            seen = set()
        else:
            core, _ = open_source_workspace(target, {key: SOURCE_SCHEMA if key == "schema" else value for key, value in state.items() if key != "imports"})
            roots = dict(core._roots)
            seen = {state["source_id"]}
        for item in imports:
            fields = {"source_id", "source_root", "snapshot_sha256", "root", "source_link_id", "operation_id", "approved_by"}
            if not isinstance(item, dict) or set(item) not in (fields, fields | {"source_access"}):
                raise ValueError("Ungültige Quellenbindung.")
            if not all(isinstance(item[key], str) and item[key] for key in fields) or not re.fullmatch(r"source:[a-z0-9-]+", item["source_id"]) or item["source_id"] in seen:
                raise ValueError("Mehrdeutige Quellenidentität.")
            rights = item.get("source_access")
            if rights is not None and rights not in ({"access": "restricted", "principals": [item["approved_by"]]},
                                                      {"access": "shared", "principals": []}):
                raise ValueError("Ungültige Quellenrechte.")
            if not re.fullmatch(r"[0-9a-f]{64}", item["snapshot_sha256"]) or item["root"] != "sources/source-" + item["source_id"].removeprefix("source:") + "-" + item["snapshot_sha256"][:16]:
                raise ValueError("Ungültiger Snapshot-Pfad.")
            if item["source_link_id"] != "link:import-" + item["source_id"].removeprefix("source:") or item["operation_id"] != "op:import:" + item["snapshot_sha256"]:
                raise ValueError("Ungültiger Quellenbeleg.")
            roots[item["source_id"]] = _unlinked_path(target / item["root"])
            seen.add(item["source_id"])
        from owledge_connectors.markdown_source import MarkdownSourceConnector
        return Core.open(roots, identity_profile="mvp-v1", clock=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                         source_connector_factory=MarkdownSourceConnector), state
    if state.get("schema") != SCHEMA:
        raise ValueError("Ungültiger Knowledge-Workspace-Vertrag.")
    # Same contained-root layout; grants come from actual Core authority, never this substitution.
    core, _ = open_source_workspace(target, {**state, "schema": SOURCE_SCHEMA})
    from owledge_connectors.markdown_source import MarkdownSourceConnector
    from owledge_core.api import Core
    return Core.open(core._roots, identity_profile="mvp-v1",
                     clock=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                     source_connector_factory=MarkdownSourceConnector), state


def _name(name: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 80:
        raise ValueError("Wähle einen kurzen Namen, etwa brand-accent.")
    return name


def _record_name(name: str) -> str:
    """Colon-qualified Lesson handles cannot collide with reference names."""
    for kind in ("lesson", "idea", "finding"):
        if name.startswith(kind + ":"):
            return kind + "-" + _name(name.removeprefix(kind + ":"))
    if name == "essence:project":
        return "essence-project"
    if name.startswith("essence:"):
        return "essence-" + _name(name.removeprefix("essence:"))
    return "source-" + _name(name)


def knowledge_workspace_health(target: Path) -> dict[str, object]:
    from owledge_connectors.markdown_source import MarkdownSourceConnector
    from owledge_core.project_io import _source_snapshot_files, _validate_materialized_source, validate_primary_snapshot
    core, state = open_knowledge_workspace(target, json.loads(_state_bytes(target)))
    result = KnowledgeWorkspaceJourney(core).agent.execute("inspect", "op:knowledge-doctor", {})
    healthy = (result.get("reason_code") == "project_inspected"
               and result.get("data", {}).get("health", {}).get("invalid_documents", 0) == 0)
    source_free = state["schema"] == SOURCE_FREE_SCHEMA
    if source_free:
        unchanged = True
    else:
        validate_primary_snapshot(target, state)
        try:
            snapshot = MarkdownSourceConnector(Path(state["source_root"])).scan()
            unchanged = snapshot.snapshot_sha256 == state["source_snapshot_sha256"]
        except (ValueError, OSError):
            unchanged = False
    imported_health = []
    from owledge_core.contracts import SourceSnapshot
    for item in state.get("imports", []):
        preserved_root = target / item["root"]
        preserved = MarkdownSourceConnector(preserved_root / "originals" / item["snapshot_sha256"]).scan()
        preserved = SourceSnapshot.create(item["source_id"], Path(item["source_root"]), preserved.files)
        if preserved.snapshot_sha256 != item["snapshot_sha256"]:
            raise ValueError("Importierte Originale wurden verändert.")
        expected, originals, _ = _source_snapshot_files(preserved, item["operation_id"], item["approved_by"])
        _validate_materialized_source(preserved_root, expected, originals)
        try:
            live = MarkdownSourceConnector(Path(item["source_root"])).scan()
            source_unchanged = live.snapshot_sha256 == item["snapshot_sha256"]
        except (ValueError, OSError):
            source_unchanged = False
        imported_health.append({"source_link_id": item["source_link_id"], "source_unchanged": source_unchanged, "originals_unchanged": True})
    empty_source_free = source_free and not imported_health
    return {"status": "healthy" if healthy and unchanged and all(item["source_unchanged"] for item in imported_health) else "needs_attention",
            **({} if source_free else {"source_unchanged": unchanged}),
            **({} if empty_source_free else {"originals_unchanged": True}),
            **({"imports": imported_health} if imported_health else {}),
            "runtime_current": state["runtime_sha256"] == runtime_fingerprint(),
            "message": "Lokaler Wissensbereich und aktive Snapshots geprüft; erhaltene historische Snapshots werden nicht vollständig neu gescannt. Keine automatische Synchronisierung oder Freigabe."}


def _bounded_recall_pages(agent, query: str, filters: dict, cursor: dict | None,
                          recall_limit: str | None, fetch_page, *, selected_keys: tuple[str, ...],
                          scope_binding: dict[str, object]) -> dict[str, object]:
    """One shared, settings-bound continuation loop for native and MCP search."""
    domain = ("focused", "expanded", "audit")
    policy_result = agent.execute("settings_inspect", stable_operation_id("recall-settings", {}), {})
    if policy_result.get("status") != "ok":
        return {"status": "needs_attention", "reason_code": policy_result.get("reason_code"),
                "message": policy_result.get("summary"), "next_action": policy_result.get("next_action")}
    policy = policy_result["data"]
    effective = policy["effective"]
    maximum = effective["recall_max_auto"]
    if recall_limit is not None and (recall_limit not in domain or domain.index(recall_limit) > domain.index(maximum)):
        return {"status": "needs_attention", "reason_code": "settings_limit_widening",
                "message": "Recall limit exceeds the Owner maximum.",
                "next_action": "Choose a limit at or below the applicable Owner maximum."}
    ceiling = recall_limit or maximum
    start = effective["recall_default"]
    if domain.index(start) > domain.index(ceiling):
        start = ceiling
    binding = sha256(json.dumps({"query": query, "filters": filters, "snapshot": policy["snapshot_sha256"],
        "principal": getattr(agent, "_principal_id", None), "ceiling": ceiling,
        "scope": scope_binding},
        sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    if cursor is not None:
        if (not isinstance(cursor, dict) or set(cursor) != {"recall_binding", "page_cursor"}
                or cursor["recall_binding"] != binding or not isinstance(cursor["page_cursor"], dict)):
            raise ValueError("Recall continuation is stale; restart from the first page.")
        page_cursor = cursor["page_cursor"]
    else:
        page_cursor = None
    selected = {key: [] for key in selected_keys}
    seen = {key: set() for key in selected_keys}
    pages = 0
    pages_fetched = 0
    output_bytes = 0
    documents_examined = 0
    bytes_examined = 0
    page_progress = []
    unreadable = []
    excluded = []
    limiting_reasons = []
    result = {}
    last_committed = {}
    output_limited = False
    while pages < domain.index(ceiling) + 1:
        current_policy = agent.execute("settings_inspect", stable_operation_id("recall-settings", {}), {})
        if (current_policy.get("status") != "ok"
                or current_policy["data"].get("snapshot_sha256") != policy["snapshot_sha256"]):
            return {"status": "needs_attention", "reason_code": "settings_snapshot_stale",
                    "message": "Settings changed during recall.", "next_action": "Restart the search."}
        result = fetch_page(page_cursor)
        if result.get("status") == "needs_attention":
            return result
        pages_fetched += 1
        progress = result.get("search_progress", result.get("progress", {}))
        page_progress.append(progress)
        components = (item.get("search_progress", item) for item in progress) if isinstance(progress, list) else (progress,)
        for component in components:
            if isinstance(component, dict):
                documents_examined += int(component.get("files_examined", component.get("documents_scanned", 0)))
                bytes_examined += int(component.get("bytes_examined", component.get("bytes_scanned", 0)))
        pending = {key: [] for key in selected_keys}
        pending_ids = {key: set() for key in selected_keys}
        pending_bytes = 0
        for key in selected_keys:
            for item in result.get(key, []):
                identity = json.dumps(item, sort_keys=True, ensure_ascii=False)
                if identity not in seen[key] and identity not in pending_ids[key]:
                    item_bytes = len(json.dumps(item, sort_keys=True, ensure_ascii=False).encode("utf-8"))
                    pending[key].append((identity, item))
                    pending_ids[key].add(identity)
                    pending_bytes += item_bytes
        if output_bytes + pending_bytes > 196608:
            output_limited = True
            break
        pages += 1
        for key in selected_keys:
            for identity, item in pending[key]:
                selected[key].append(item)
                seen[key].add(identity)
        output_bytes += pending_bytes
        last_committed = result
        unreadable.extend(result.get("unreadable_source_files", []))
        excluded.extend(result.get("excluded_source_files", []))
        irreversible_resource = result.get("reason_code") == "resource_exhausted" and any(
            isinstance(component, dict) and component.get("oversized_files_skipped", 0) for component in
            ((item.get("search_progress", item) for item in progress) if isinstance(progress, list) else (progress,)))
        if result.get("excluded_source_files"):
            limiting_reasons.append("source_record_too_large")
        elif result.get("reason_code") in {"source_access_limited", "source_unavailable",
                                         "source_encoding_unreadable", "source_record_too_large"} or irreversible_resource:
            limiting_reasons.append(result["reason_code"])
        continuation = result.get("continuation")
        if continuation is None or (pages >= domain.index(start) + 1
                                    and any(selected.values())):
            break
        page_cursor = continuation
    out = dict(last_committed)
    out.update(selected)
    if output_limited:
        out["status"] = "incomplete" if pages and page_cursor is not None else "needs_attention"
        out["reason_code"] = "recall_output_limited"
        out["message"] = "Recall output reached its bounded limit; narrow the query or continue the current page."
        out["continuation"] = page_cursor
    if out.get("continuation") is not None:
        out["continuation"] = {"recall_binding": binding, "page_cursor": out["continuation"]}
    out["unreadable_source_files"] = unreadable
    out["excluded_source_files"] = excluded
    if limiting_reasons and not output_limited:
        out["status"] = "incomplete"
        out["reason_code"] = limiting_reasons[0]
    if any(selected.values()) and out.get("status") == "not_found":
        out["status"] = "found"
    out["recall"] = {"start": start, "actual": domain[max(0, min(pages_fetched - 1, 2))], "max_auto": maximum,
        "runtime_limit": ceiling, "pages": pages_fetched, "pages_returned": pages,
        "escalation_reason": "no_useful_match_with_continuation" if pages_fetched > domain.index(start) + 1 else None,
        "records": sum(len(items) for items in selected.values()), "output_bytes": output_bytes,
        "documents_examined": documents_examined, "bytes_examined": bytes_examined,
        "page_progress": page_progress,
        "settings_snapshot_sha256": policy["snapshot_sha256"]}
    return out


def search_knowledge(core: object, state: dict, workspace: Path, question: str, *,
                     adapter: object, source: str | None = None, cursor: dict | None = None,
                     bound_source_link: str | None = None,
                     filters: dict[str, list[str]] | None = None,
                     recall_limit: str | None = None) -> dict[str, object]:
    return _bounded_recall_pages(adapter, question, filters or {}, cursor, recall_limit,
        lambda page_cursor: _search_knowledge_page(core, state, workspace, question,
            adapter=adapter, source=source, cursor=page_cursor, bound_source_link=bound_source_link,
            filters=filters), selected_keys=("reviewed", "citations"),
        scope_binding={"authority": "user-global:source-access", "source": source,
                       "source_link_id": bound_source_link})


def _search_knowledge_page(core: object, state: dict, workspace: Path, question: str, *,
                     adapter: object, source: str | None = None, cursor: dict | None = None,
                     bound_source_link: str | None = None,
                     filters: dict[str, list[str]] | None = None) -> dict[str, object]:
    """Shared Owner/Contributor search journey with Core-owned staged rights."""
    from owledge_core.policy import source_access_allowed
    sources: list[tuple[str, str, Path, str]] = []
    if isinstance(state.get("source_root"), str):
        sources.append((state["source_root"], LINK, workspace / state["roots"]["source"], state["source_snapshot_sha256"]))
    for item in state.get("imports", []):
        if isinstance(item, dict) and isinstance(item.get("source_root"), str) and isinstance(item.get("source_link_id"), str):
            sources.append((item["source_root"], item["source_link_id"], workspace / item["root"], item["snapshot_sha256"]))
    principal = adapter._principal_id
    controls = core._repository.progressive_controls(AUTHORITY)
    permitted_links = {item.metadata.get("source_link_id") for item in controls
                       if item.metadata.get("schema") == "owledge.knowledge-source-link/1"
                       and source_access_allowed(item, principal)}
    chosen = [item for item in sources if item[1] in permitted_links
              and (bound_source_link is None or item[1] == bound_source_link)
              and (source is None or Path(item[0]).resolve() == Path(source).resolve())]
    filters = filters or {}
    cursor_binding = sha256(json.dumps({
        "query": question, "filters": filters, "principal": principal,
        "source": source, "bound_source_link": bound_source_link,
        "chosen": [(item[0], item[1], item[3]) for item in chosen],
    }, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    if source is not None and not chosen:
        raise ValueError("Quelle ist nicht registriert oder für diese Verbindung nicht freigegeben.")
    if cursor is not None and (not isinstance(cursor, dict) or cursor.get("stage") not in {"reviewed", "originals"}
                               or cursor.get("binding") != cursor_binding):
        raise ValueError("--cursor erwartet das unveränderte JSON-Objekt aus der vorherigen Antwort.")
    if cursor is not None and cursor["stage"] == "reviewed" and (set(cursor) != {"stage", "cursor", "binding"} or not isinstance(cursor["cursor"], dict)):
        raise ValueError("Ungültige freigegebene Suchseite.")
    if cursor is not None and cursor["stage"] == "originals" and (
            set(cursor) != {"stage", "source_index", "source_root", "source_cursor", "binding"}
            or type(cursor["source_index"]) is not int or not 0 <= cursor["source_index"] < len(chosen)
            or cursor["source_root"] != chosen[cursor["source_index"]][0]
            or cursor["source_cursor"] is not None and not isinstance(cursor["source_cursor"], dict)):
        raise ValueError("Ungültige Original-Suchseite.")
    reviewed, reviewed_reason, reviewed_progress = [], None, {}
    if cursor is None or cursor["stage"] == "reviewed":
        request = {"query": question, "knowledge_area": None, "filters": filters,
                   "cursor": cursor["cursor"] if cursor is not None else None}
        result = adapter.execute("curated_discover", stable_operation_id("native-reviewed", request), request)
        if result.get("status") not in {"ok", "incomplete"}:
            return {"status": "needs_attention", "reason_code": result.get("reason_code"),
                    "message": result.get("summary"), "next_action": result.get("next_action")}
        data = result.get("data", {})
        reviewed = data.get("references", [])
        reviewed_reason = result.get("reason_code")
        reviewed_progress = data.get("progress", {})
        if result.get("reason_code") == "resource_exhausted":
            return {"status": "incomplete", "message": "Metadatenlimit erreicht; Bestand bereinigen oder exakten Namen lesen.",
                    "reviewed": [], "citations": [], "continuation": None,
                    "search_progress": data.get("progress", {}), "reason_code": "resource_exhausted"}
        if data.get("continuation") is not None:
            return {"status": "incomplete", "message": "Freigegebene Suchseite; weitere Seiten verfügbar.",
                    "reviewed": reviewed, "citations": [],
                    "continuation": {"stage": "reviewed", "cursor": data["continuation"], "binding": cursor_binding},
                    "search_progress": data.get("progress", {}), "reason_code": reviewed_reason}
    citations, progress, unreadable = [], ([reviewed_progress] if reviewed_progress.get("files_examined", 0) else []), []
    excluded = []
    continuation, limited_reason = None, None
    start = cursor["source_index"] if cursor is not None and cursor["stage"] == "originals" else 0
    max_sources_per_page = 4
    for index in range(start, min(len(chosen), start + max_sources_per_page)):
        source_root, source_link, snapshot_root, snapshot_sha = chosen[index]
        source_cursor = cursor["source_cursor"] if cursor is not None and cursor["stage"] == "originals" and index == start else None
        request = {"coverage_case_id": CASE, "query": question, "source_link_id": source_link,
                   "source_areas": ["."], "filters": filters,
                   "budget_override": {"max_result_records": 8 - len(citations)},
                   **({"source_cursor": source_cursor} if source_cursor is not None else {})}
        result = adapter.execute("progressive_retrieve", stable_operation_id("native-search", request), request)
        if result.get("status") not in {"ok", "incomplete"}:
            return {"status": "needs_attention", "reason_code": result.get("reason_code"),
                    "message": result.get("summary"), "next_action": result.get("next_action")}
        data = result.get("data", {})
        for hit in data.get("raw_hits", []):
            preserved = snapshot_root / "originals" / snapshot_sha / hit["relative_path"]
            if (not preserved.is_file() or not preserved.resolve().is_relative_to(snapshot_root.resolve())
                    or sha256(preserved.read_bytes()).hexdigest() != hit["content_sha256"]):
                raise ValueError("Der erhaltene Quellenbeleg hat sich verändert; Status/Doctor prüfen.")
            citations.append({"file": str(preserved), "origin": source_root,
                              "source_link_id": source_link, "relative_path": hit["relative_path"],
                              "excerpt": hit["snippet"],
                              "content_sha256": hit["content_sha256"], "verified_knowledge": False})
        progress.append({"source": source_root, "search_progress": data.get("search_progress", {})})
        unreadable.extend({"source": source_root, **item} for item in data.get("unreadable_source_files", []))
        excluded.extend({"source": source_root, **item} for item in data.get("excluded_source_files", []))
        if result.get("reason_code") in {"source_access_limited", "resource_exhausted", "source_unavailable",
                                         "source_encoding_unreadable", "source_record_too_large"}:
            limited_reason = result["reason_code"]
        next_cursor = data.get("continuation")
        if next_cursor is not None or len(citations) >= 8:
            next_index = index if next_cursor is not None else index + 1
            if next_index < len(chosen):
                continuation = {"stage": "originals", "source_index": next_index,
                                "source_root": chosen[next_index][0], "source_cursor": next_cursor,
                                "binding": cursor_binding}
            break
    else:
        next_index = start + max_sources_per_page
        if next_index < len(chosen):
            continuation = {"stage": "originals", "source_index": next_index,
                            "source_root": chosen[next_index][0], "source_cursor": None,
                            "binding": cursor_binding}
    if excluded:
        limited_reason = "source_record_too_large"
    status = "incomplete" if limited_reason or continuation is not None else "found" if citations or reviewed else "not_found"
    return {"status": status, "message": "Originalauszüge sind Quellenbelege, kein freigegebenes Wissen.",
            "reviewed": reviewed, "citations": citations, "continuation": continuation,
            "search_progress": progress, "unreadable_source_files": unreadable,
            "excluded_source_files": excluded,
            "scope": "permitted_sources_only",
            "reason_code": limited_reason or reviewed_reason or "search_complete"}


class KnowledgeWorkspaceJourney:
    def __init__(self, core: object, *, authority_id: str = AUTHORITY, principal_id: str = AGENT,
                 connection_name: str | None = None, source_link_id: str | None = None,
                 operator_workspace: Path | None = None, transport: str | None = None):
        if operator_workspace is not None and connection_name is None:
            raise ValueError("Named Operator needs an exact local connection name.")
        if transport not in {None, "cli", "mcp"}:
            raise ValueError("Unknown local transport label.")
        self.authority_id = authority_id
        self.connection_name = connection_name
        common = {"reported": {"agent_name": ("human-operator:" + connection_name) if operator_workspace is not None else connection_name or "knowledge-cli", "model": "none"},
                  "adapter_observed": {"runtime": "owledge-local-cli" if operator_workspace is not None or transport == "cli" else "owledge-local-mcp" if connection_name or transport == "mcp" else "source-local-cli",
                                       "runtime_version": "1", "run_id": connection_name or "knowledge"}}
        self.agent = ContributorMcpAdapter(core, principal_id=principal_id, active_authority_id=authority_id,
                                           source_link_id=source_link_id, **common)
        self.owner = LocalOwnerAdapter(core, principal_id=principal_id if operator_workspace is not None else OWNER,
                                       active_authority_id=authority_id,
                                       operator_name=connection_name if operator_workspace is not None else None,
                                       operator_workspace=operator_workspace, **common)
        self.pending = None

    def _operation_id(self, label: str, payload: dict) -> str:
        return stable_operation_id(label, {"connection": self.connection_name, "payload": payload}) if self.connection_name else stable_operation_id(label, payload)

    def lesson(self, *, name: str, area: str, text: str, origin: str, conditions: str, verification: str, limitations: str):
        payload = {"name": _name(name), "knowledge_area": area, "text": text, "origin": origin,
                   "conditions": conditions, "verification": verification, "limitations": limitations}
        result = self.agent.execute("lesson_candidate", self._operation_id("lesson-proposal", payload), payload)
        if result.get("status") != "ok":
            return {"status": "needs_attention", "details": result}
        return {"status": "preview", "name": "lesson:" + name, "candidate_id": result["data"]["candidate_id"],
                "proposed_text": text, "source": result["data"]["review_preview"]["source"],
                "message": "Lesson als berichteter Vorschlag gespeichert. Kontext und Verifikation vor Freigabe prüfen; Project Lessons können nach Freigabe auf exakter Basis korrigiert werden."}

    def project_record(self, *, kind: str, name: str, area: str, text: str, exception_kind: str | None = None):
        payload = {"record_kind": kind, "name": _name(name), "knowledge_area": area, "text": text}
        if exception_kind is not None:
            payload["exception_kind"] = exception_kind
        result = self.agent.execute("project_record_candidate", self._operation_id("project-record", payload), payload)
        if result.get("status") != "ok":
            return {"status": "needs_attention", "details": result}
        preview = result["data"]["review_preview"]
        return {"status": "preview", "name": kind + ":" + name, "candidate_id": preview["candidate_id"],
                "proposed_text": preview["proposed_text"], "record_kind": kind,
                "record_status": preview["record_status"], "canonical": False,
                "submitted_by": preview["submitted_by"],
                "message": "Nonfactual Project record staged for separate human recording review."}

    def propose(self, *, name: str, area: str, text: str, source_file: str, search: dict[str, object], correction: dict | None = None):
        name = _name(name)
        found = self.agent.execute("progressive_retrieve", self._operation_id("knowledge-source", search), search)
        if found.get("status") not in {"ok", "incomplete"}:
            return {"status": "needs_attention", "details": found}
        matches = [hit for hit in found.get("data", {}).get("raw_hits", []) if hit["relative_path"] == source_file]
        if len(matches) != 1:
            return {"status": "needs_attention", "message": "Wähle eine Datei aus dieser Suchseite; bei Bedarf mit Cursor fortsetzen.",
                    "continuation": found.get("data", {}).get("continuation")}
        hit = matches[0]
        payload = {"source_search": search, "source_relative_path": source_file,
                   "source_content_sha256": hit["content_sha256"], "source_excerpt": hit["snippet"],
                   "source_binding": hit["source_binding"], "proposed_text": text,
                   "curation_slug": name, "knowledge_area": area}
        if correction is not None:
            payload["correction"] = correction
        result = self.agent.execute("source_candidate", self._operation_id("source-proposal", payload), payload)
        if result.get("status") != "ok":
            return {"status": "needs_attention", "details": result}
        return {"status": "preview", "name": name, "candidate_id": result["data"]["candidate_id"],
                "candidate_revision": result["data"]["candidate_revision"],
                "source_link_id": search.get("source_link_id"), "relative_path": source_file,
                "source_excerpt": hit["snippet"], "proposed_text": text,
                "review_preview": result["data"]["review_preview"],
                "message": "Vorschlag gespeichert, nicht freigegeben. Lokale Review-Aktion öffnet die geprüfte Vorschau."}

    def correct(self, *, name: str, expected_revision: str, expected_sha256: str, **proposal):
        if not expected_revision or not expected_sha256:
            raise ValueError("Korrektur benötigt --expected-revision und --expected-sha256 aus der gelesenen Referenz.")
        if name.startswith(("idea:", "finding:")):
            kind, raw_name = name.split(":", 1)
            slug = _name(raw_name)
            payload = {"record_kind": kind, "name": slug, "text": proposal["text"],
                       "correction": {"artifact_id": f"memory:{self.authority_id.replace(':', '-')}-{kind}-{slug}",
                                      "revision": expected_revision, "content_sha256": expected_sha256}}
            result = self.agent.execute("project_record_candidate", self._operation_id("project-record-correction", payload), payload)
            if result.get("status") != "ok":
                return {"status": "needs_attention", "details": result}
            preview = result["data"]["review_preview"]
            return {"status": "preview", "name": name, "candidate_id": preview["candidate_id"],
                    "old_text": preview["base"]["text"], "proposed_text": preview["proposed_text"],
                    "base": preview["base"], "record_kind": kind, "knowledge_area": preview["knowledge_area"],
                    "exception_kind": preview.get("exception_kind"), "submitted_by": preview["submitted_by"],
                    "canonical": False, "message": "Exact-base nonfactual Project record correction staged for separate review."}
        if name.startswith("lesson:"):
            lesson_name = _name(name.removeprefix("lesson:"))
            payload = {"name": lesson_name, "text": proposal["text"], "correction": {
                "artifact_id": f"memory:{self.authority_id.replace(':', '-')}-lesson-{lesson_name}",
                "revision": expected_revision, "content_sha256": expected_sha256}}
            result = self.agent.execute("lesson_candidate", self._operation_id("lesson-correction", payload), payload)
            if result.get("status") != "ok":
                return {"status": "needs_attention", "details": result}
            preview = result["data"]["review_preview"]
            return {"status": "preview", "name": name, "candidate_id": result["data"]["candidate_id"],
                    "old_text": preview["base"]["text"], "proposed_text": preview["proposed_text"],
                    "source": preview["source"],
                    "message": "Exact-base Project Lesson correction staged; origin and Area remain unchanged."}
        return self.propose(name=name, correction={"artifact_id": f"memory:{self.authority_id.replace(':', '-')}-source-{_name(name)}",
            "revision": expected_revision, "content_sha256": expected_sha256}, **proposal)

    def preview(self, name: str, candidate_id: str | None = None):
        if name.startswith("case:"):
            case_name = _name(name.removeprefix("case:"))
            if candidate_id is None or not re.fullmatch(
                    rf"candidate:{re.escape(self.authority_id.replace(':', '-'))}:(?:gap-closure|case-correction)-[0-9a-f]{{16}}", candidate_id):
                raise ValueError("Der Fall benötigt die exakte Candidate-ID aus case answer.")
            opened = self.owner.open_candidate(candidate_id, "candidate-rev-1-" + candidate_id.rsplit("-", 1)[-1])
            if opened.get("status") != "ok":
                return {"status": "needs_attention", "details": opened}
            self.pending = opened["data"]
            if self.pending.get("source", {}).get("coverage_case_id") != f"coverage:{case_name}":
                self.pending = None
                raise ValueError("Candidate gehört nicht zum gewählten Fall.")
            return {"status": "preview", "name": name, **self.pending}
        initial_id = f"candidate:{self.authority_id.replace(':', '-')}:{_record_name(name)}"
        curation_id = f"candidate:{self.authority_id.replace(':', '-')}:curation-{_record_name(name)}"
        is_curation = (self.authority_id.startswith("user-global:") and candidate_id is not None
            and (candidate_id == curation_id or re.fullmatch(re.escape(curation_id) + r"-refresh-[0-9a-f]{16}", candidate_id)))
        if candidate_id is not None and candidate_id != initial_id and not re.fullmatch(re.escape(initial_id) + r"-(?:correction|refresh)-[0-9a-f]{16}", candidate_id) and not is_curation:
            raise ValueError("Korrektur-Kandidat gehört nicht zum gewählten Referenznamen.")
        candidate_id = candidate_id or initial_id
        opened = self.owner.open_candidate(candidate_id, "candidate-rev-1")
        if opened.get("status") != "ok":
            return {"status": "needs_attention", "details": opened}
        self.pending = opened["data"]
        if is_curation and self.pending.get("target") != f"curated/{_record_name(name)}.md":
            self.pending = None
            raise ValueError("Global Candidate gehört nicht zum gewählten Referenznamen.")
        return {"status": "preview", "name": name, "source": self.pending["source"],
                "knowledge_area": self.pending["knowledge_area"],
                "proposed_text": self.pending["proposed_text"], "target": self.pending["target"],
                "candidate_id": self.pending["candidate_id"],
                "candidate_revision": self.pending["candidate_revision"],
                "content_sha256": self.pending["content_sha256"],
                **({"submitted_by": self.pending["submitted_by"]} if "submitted_by" in self.pending else {}),
                **({"record_kind": self.pending["record_kind"], "record_status": self.pending["record_status"], "canonical": False}
                   if "record_kind" in self.pending else {}),
                **({"base": self.pending["base"]} if "base" in self.pending else {}),
                **({"old_source": self.pending["old_source"], "refresh_kind": self.pending.get("refresh_kind")}
                   if "old_source" in self.pending else {}),
                "message": "Freigabe bestätigt nur die Aufzeichnung; Idee oder Finding ist kein Faktenbeleg."
                           if "record_kind" in self.pending else
                           "Nur den angezeigten Vorschlag freigeben; die Quelle allein beweist keine aktuelle Wahrheit."}

    def decide(self, decision: str, *, batch: bool = False):
        if decision not in {"approve", "reject"} or self.pending is None:
            return {"status": "cancelled", "message": "Keine Freigabe gespeichert."}
        preview = self.pending
        request = {"candidate_id": preview["candidate_id"], "candidate_revision": preview["candidate_revision"],
                   "decision": decision, "expected_result_sha256": preview["content_sha256"]}
        if batch:
            request["batch_review"] = True
        reviewed = self.owner.execute("candidate_review", stable_operation_id("knowledge-review", request), request)
        if reviewed.get("status") != "ok":
            return {"status": "needs_attention", "details": reviewed}
        if decision == "reject":
            return {"status": "rejected", "message": "Vorschlag abgelehnt; bestätigtes Wissen unverändert."}
        request = {"candidate_id": preview["candidate_id"], "candidate_revision": reviewed["data"]["candidate_revision"],
                   "expected_base_revision": preview.get("base", {}).get("revision", "absent"), "expected_policy_revision": preview["expected_policy_revision"],
                   "expected_settings_revision": preview["expected_settings_revision"], "idempotency_key": preview["idempotency_key"]}
        if batch:
            request["batch_review"] = True
        promoted = self.owner.execute("candidate_promote", stable_operation_id("knowledge-promote", request), request)
        return ({"status": "accepted", "message": "Nichtkanonische Möglichkeit oder Signal aufgezeichnet; kein Faktenbeleg."
                 if preview.get("record_kind") in {"idea", "finding"} else "Freigegebene Referenz gespeichert.",
                 "receipt_id": promoted.get("receipt_id")}
                if promoted.get("status") == "ok" else {"status": "needs_attention", "details": promoted})

    def batch_preview(self, cursor: dict | None = None):
        payload = {"cursor": cursor} if cursor is not None else {}
        result = self.owner.execute("candidate_queue", self._operation_id("review-batch-page", payload), payload)
        if result.get("status") in {"ok", "incomplete"}:
            data = result.get("data", {})
            return {"status": "incomplete" if result.get("reason_code") == "resource_exhausted" else "preview",
                    "reason_code": result.get("reason_code"), "message": result.get("summary"), **data}
        return {"status": "needs_attention", "reason_code": result.get("reason_code"),
                "message": result.get("summary"), "details": result}

    def batch_apply(self, *, cursor: dict | None, decision: str, expected_sha256: str):
        if decision not in {"approve", "reject"} or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
            raise ValueError("Batch review requires approve/reject and the exact page hash.")
        page = self.batch_preview(cursor)
        if page.get("status") != "preview" or page.get("expected_sha256") != expected_sha256:
            return {"status": "needs_attention", "reason_code": "batch_page_stale",
                    "message": "Die angezeigte Seite ist nicht mehr exakt aktuell; neue Vorschau öffnen.",
                    "results": [], "unprocessed_ids": [item["candidate_id"] for item in page.get("items", [])]}
        items = page["items"]
        if not items:
            return {"status": "needs_attention", "reason_code": "batch_empty",
                    "message": "Keine Vorschläge auf dieser Seite; keine Entscheidung gebucht.",
                    "results": [], "unprocessed_ids": []}
        results = []
        for index, item in enumerate(items):
            self.pending = item
            outcome = self.decide(decision, batch=True)
            if outcome.get("status") not in {"accepted", "rejected"}:
                return {"status": "partial" if results else "needs_attention", "decision": decision,
                        "results": results, "failed_item": {"candidate_id": item["candidate_id"],
                                                       "name": item.get("name"), "details": outcome},
                        "unprocessed_ids": [later["candidate_id"] for later in items[index + 1:]],
                        "continuation": None,
                        "message": "Bisherige Entscheidungen bleiben einzeln gebucht; Rest neu prüfen."}
            results.append({"candidate_id": item["candidate_id"], "name": item.get("name"),
                            "status": outcome["status"], "receipt_id": outcome.get("receipt_id")})
        return {"status": "accepted" if decision == "approve" else "rejected", "decision": decision,
                "results": results, "unprocessed_ids": [], "continuation": None,
                "message": "Jeder Vorschlag wurde einzeln entschieden."
                           if decision == "approve" else
                           "Ablehnung hat keine kanonische Wirkung und entfernt Vorschläge nicht dauerhaft aus der Liste."}

    def _reviewed_target(self, scope: str | None, project_id: str | None) -> str:
        if scope is not None and (not isinstance(scope, str) or scope not in {"project", "global"}):
            raise ValueError("Reviewed scope is invalid.")
        if scope == "global":
            if not self.authority_id.startswith("project:") or project_id is not None:
                raise ValueError("Global reviewed scope requires a named Project connection.")
            return "user-global:source-access"
        if self.authority_id == "user-global:source-access" and scope == "project":
            if not isinstance(project_id, str) or not re.fullmatch(r"project:[a-z0-9]+(?:-[a-z0-9]+)*", project_id):
                raise ValueError("Project reviewed scope needs an exact registered Project ID.")
            return project_id
        if project_id is not None:
            raise ValueError("Project ID needs Global Project scope.")
        return self.authority_id

    def read(self, name: str, revision: str | None = None, *, scope: str | None = None,
             project_id: str | None = None):
        target = self._reviewed_target(scope, project_id)
        payload = {"artifact_id": f"memory:{target.replace(':', '-')}-{_record_name(name)}"}
        if revision is not None:
            payload["revision"] = revision
        result = self.agent.execute("curated_read", stable_operation_id("knowledge-read", payload), payload,
                                    target_authority_id=target)
        if result.get("reason_code") == "reference_not_found":
            return {"status": "not_found", "message": "Keine freigegebene Referenz unter diesem Namen. Kein Gap angelegt."}
        if result.get("status") == "ok":
            return {"status": "answered", **result["data"]}
        return {"status": "needs_attention", "details": result}

    def discover(self, query: str, area: str | None = None, cursor: dict | None = None,
                 filters: dict[str, list[str]] | None = None, *, scope: str | None = None,
                 project_id: str | None = None, recall_limit: str | None = None):
        target = self._reviewed_target(scope, project_id)
        def page(page_cursor):
            payload = {"query": query, "knowledge_area": area, "cursor": page_cursor, "filters": filters or {}}
            result = self.agent.execute("curated_discover", stable_operation_id("knowledge-discover", payload), payload,
                                        target_authority_id=target)
            if result.get("status") in {"ok", "incomplete"}:
                return {"status": "incomplete" if result["status"] == "incomplete" else "discovered",
                        **result["data"],
                        "message": "Suchseite bestätigter Referenzen, keine fertige Antwort. Mit --name gezielt öffnen; Suchseiten mit --cursor fortsetzen. Eine leere Suche ist kein Gap."}
            return {"status": "needs_attention", "reason_code": result.get("reason_code"),
                    "message": result.get("summary"), "next_action": result.get("next_action"), "details": result}
        return _bounded_recall_pages(self.agent, query, {"knowledge_area": area, **(filters or {})}, cursor,
                                     recall_limit, page, selected_keys=("references",),
                                     scope_binding={"active_authority": self.authority_id, "target": target,
                                                    "project_id": project_id})

    def observe(self, cursor: dict | None = None):
        if self.authority_id != AUTHORITY:
            raise ValueError("Observation requires a named Global Contributor.")
        payload = {"cursor": cursor} if cursor is not None else {}
        result = self.agent.execute("maintenance_observe",
            self._operation_id("named-observation", {"request": uuid4().hex, **payload}), payload)
        if result.get("status") in {"ok", "incomplete"}:
            return {"status": "observed" if result["status"] == "ok" else "incomplete",
                    "reason_code": result.get("reason_code"), "receipt_id": result.get("receipt_id"),
                    **result.get("data", {}),
                    "message": result.get("summary", "")}
        return {"status": "needs_attention", "reason_code": result.get("reason_code"),
                "message": result.get("summary"), "next_action": result.get("next_action")}
