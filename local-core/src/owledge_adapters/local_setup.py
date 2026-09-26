"""Human-facing adapter for the private source-local setup port."""

from __future__ import annotations

from typing import Mapping
from pathlib import Path
import os
import stat
import json
import hashlib
import re
from datetime import datetime, timezone


__all__: tuple[str, ...] = ()

PROJECT = "project:demo"
GLOBAL = "user-global:owner"
OWNER = "principal:local-owner"
CONTRIBUTOR = "principal:project-agent"
MAINTAINER = "principal:maintenance-agent"
WORKSPACE_SCHEMA = "owledge.private-owner-workspace/1"


def runtime_fingerprint() -> str:
    """Private source identity, not a product version or compatibility promise."""
    source = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for package in ("owledge_core", "owledge_adapters", "owledge_connectors"):
        for path in sorted((source / package).rglob("*.py")):
            digest.update(path.relative_to(source).as_posix().encode("utf-8") + b"\0")
            digest.update(path.read_bytes() + b"\0")
    from owledge_core.contracts import settings_resource_paths, verified_settings_catalog
    verified_settings_catalog()
    for path in settings_resource_paths():
        digest.update(path.name.encode("utf-8") + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def _state_bytes(target: Path, *, settings_repair: bool = False) -> bytes:
    root = _unlinked_path(target)
    if (root.parent / ".owledge/paired-restore.json").exists():
        from owledge_core.project_io import paired_restore_readback_active
        if not paired_restore_readback_active(root.parent):
            raise ValueError("Paired restore requires explicit local Owner recovery before workspace access.")
    if not settings_repair and (root / ".owledge/project-reuse-registration.json").exists():
        raise ValueError("Projektverknüpfung unterbrochen; lokale Owner-Wiederherstellung erforderlich.")
    if not settings_repair and (root / ".owledge/source-registration.json").exists():
        raise ValueError("Quellenaufnahme unterbrochen; lokale Owner-Wiederherstellung erforderlich.")
    if not settings_repair and (root / ".owledge/inbox-import.json").exists():
        raise ValueError("Inbox-Transport unterbrochen; explizite lokale Owner-Wiederherstellung mit --inbox erforderlich.")
    path = _unlinked_path(root / "workspace.json")
    before = path.stat()
    if before.st_nlink != 1 or before.st_size > 65536 or not stat.S_ISREG(before.st_mode):
        raise ValueError("Die lokale Workspace-Konfiguration ist ungültig.")
    with path.open("rb") as handle:
        opened = os.fstat(handle.fileno())
        raw = handle.read(65537)
        after = os.fstat(handle.fileno())
    final = path.stat()
    # Windows path-stat and handle-stat expose different ctime semantics.
    facts = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_nlink)
    if (len(raw) > 65536 or not (facts(before) == facts(opened) == facts(after) == facts(final))
            or before.st_ctime_ns != final.st_ctime_ns or opened.st_ctime_ns != after.st_ctime_ns):
        raise ValueError("Die Workspace-Konfiguration wurde während des Lesens verändert.")
    return raw


def record_workspace_trace(target: Path, receipt_id: str) -> None:
    from owledge_core.project_io import update_owner_workspace_state
    before = _state_bytes(target)
    state = json.loads(before)
    state["last_gap_receipt"] = receipt_id
    update_owner_workspace_state(target, before, (json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))


def curation_reference(target: Path, topic: str, reference: dict[str, object] | None = None):
    """Persist only object references, never a decision or permission."""
    from owledge_core.project_io import update_owner_workspace_state
    before = _state_bytes(target)
    state = json.loads(before)
    references = state.get("curation_refs", {})
    if not isinstance(references, dict) or set(references) - {"lesson", "alternative"}:
        raise ValueError("Die gespeicherten Vorschau-Verweise sind ungültig.")
    if reference is None:
        return references.get(topic)
    fields = ("candidate_id", "candidate_revision", "idempotency_key")
    saved = {key: reference[key] for key in fields}
    state["curation_refs"] = {**references, topic: saved}
    update_owner_workspace_state(target, before, (json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    return saved


class OwnerWorkspaceUpgrade:
    """Preview-only until confirmed; updates host metadata, never knowledge."""

    def __init__(self, target: Path):
        self.target = target
        self.before = _state_bytes(target)
        _, self.state = open_workspace(target)
        self.fingerprint = runtime_fingerprint()

    def preview(self) -> dict[str, object]:
        return {"status": "preview", "already_current": self.state.get("runtime_sha256") == self.fingerprint,
            "message": "Privates source-local Upgrade: nur Laufzeitbindung aktualisieren. Keine Wissensmigration, keine Veröffentlichung."}

    def apply(self) -> dict[str, object]:
        from owledge_core.project_io import update_owner_workspace_state
        if runtime_fingerprint() != self.fingerprint:
            raise ValueError("Der Programmstand hat sich geändert. Bitte neue Vorschau öffnen.")
        state = {**self.state, "runtime_sha256": self.fingerprint}
        update_owner_workspace_state(self.target, self.before, (json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
        return {"status": "ready", "message": "Private Laufzeitbindung aktualisiert; Wissensdateien unverändert."}


def _document(authority: str, identity: str, body: str, **fields: object) -> str:
    metadata = {
        "schema": "owledge.managed-markdown/1", "document_version": 1,
        "artifact_id": identity, "authority_id": authority, "revision": "demo-rev-1",
        "lifecycle": "accepted", "processing_layer": "condensed", "source_trust": "internal",
        **fields,
    }
    return "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False, separators=(',', ':'))}" for key, value in metadata.items()) + "\n---\n\n# DEMO\n\n" + body + "\n"


def _bootstrap_documents(snapshot) -> dict[str, str]:
    from owledge_core.project_io import source_snapshot_target_name
    documents = {}
    for alias, authority in (("project", PROJECT), ("global", GLOBAL)):
        grants = {
            OWNER: ["discover", "retrieve", "review", "promote"],
            CONTRIBUTOR: ["discover", "retrieve", "propose"] if alias == "project" else ["discover", "retrieve", "contribute"],
            MAINTAINER: ["discover", "retrieve"] if alias == "project" else ["discover", "retrieve", "propose"],
        }
        documents[f"{alias}/.owledge/authority.md"] = _document(
            authority, f"authority:{alias}", "Isolierter DEMO-Bereich, kein importiertes Nutzerwissen.",
            schema="owledge.authority-unit/1", mode="read_write",
            policy_revision=f"policy-{alias}-1", settings_revision=f"settings-{alias}-1", actor_grants=grants,
        )
    for relative, authority, linked, identity, grants in (
        ("project/.owledge/source-link.md", PROJECT, GLOBAL, "link:demo-to-global", ["discover", "retrieve", "contribute"]),
        ("global/.owledge/project-link.md", GLOBAL, PROJECT, "link:global-to-demo", ["discover", "retrieve"]),
        ("global/.owledge/raw-link.md", GLOBAL, snapshot.source_id, "link:global-to-source", ["discover", "keyword_retrieve"]),
    ):
        documents[relative] = _document(authority, identity, "Explizite DEMO-Verknüpfung.",
            schema="owledge.knowledge-source-link/1", source_link_id=identity, linked_authority_id=linked,
            grants=grants, **({"source_access": {"access": "restricted", "principals": [OWNER, MAINTAINER]}}
                             if linked.startswith("source:") else {}))
    stages = ["curated", "inbox", "reuse_feed", "linked_project", "raw_keyword"]
    cases = {}
    for name, key, envelope in (
        ("curated", "store", ["curated"]), ("project", "store", ["linked_project"]),
        ("feed", "knowledge_kind", ["reuse_feed"]), ("originals", "raw_content", stages),
    ):
        links = {}
        if "linked_project" in envelope:
            links["linked_project"] = ["link:global-to-demo"]
        if "raw_keyword" in envelope:
            links["raw_keyword"] = ["link:global-to-source"]
        cases["coverage:demo-" + name] = {"revision": "demo-case-1", "lifecycle": "accepted", "required_evidence": [key],
            "search_envelope": envelope, "source_links": links, "gap_admission": "disabled"}
    documents["global/.owledge/progressive-retrieval.md"] = _document(GLOBAL, "registry:demo-global", "Begrenzte DEMO-Suchprofile.",
        schema="owledge.progressive-retrieval-registry/1", coverage_cases=cases)
    documents["global/.owledge/curated/store.md"] = _document(GLOBAL, "memory:demo-store", "DEMO: Der bestätigte Wissensspeicher ist Markdown.",
        canonical=True, stage="curated", knowledge_kind="reference", memory_kind="semantic", knowledge_area="architecture", access="private", evidence={"store": "Markdown"})
    documents["project/knowledge/project-brief.md"] = _document(PROJECT, "artifact:demo-project-brief", "DEMO-Projekt mit Markdown als Speicher. Kein importiertes Projektwissen.",
        canonical=True, stage="linked_project", knowledge_kind="project_fact", memory_kind="semantic", knowledge_area="architecture", access="project",
        evidence={"store": "Markdown"}, evidence_values={"project.agent_lesson.canonical_authority": PROJECT})
    for topic, body in (("lesson", "DEMO: Keep canonical Markdown independent from adapters."),
                        ("alternative", "DEMO: Review source provenance before adopting a lesson.")):
        documents[f"project/knowledge/{topic}.md"] = _document(PROJECT, "lesson:demo-" + topic, body,
            canonical=True, stage="linked_project", knowledge_kind="lesson", memory_kind="semantic", knowledge_area="engineering", access="project")
    provider_id = "provider:demo-review-window"
    envelope_id = "search-envelope:demo-lessons"
    case_id = "coverage:demo-review-window"
    route_id = "route:demo-review-window"
    documents["project/.owledge/coverage-cases.md"] = _document(PROJECT, "registry:demo-coverage", "DEMO-Reviewfenster: fehlendes Wissen nur nach vollständiger begrenzter Suche.",
        schema="owledge.coverage-case-registry/1", document_version=3,
        search_envelopes={envelope_id: {"schema": "owledge.search-envelope/1", "revision": "demo-envelope-1",
            "authority_id": PROJECT, "relative_prefixes": ["knowledge/"], "provider_contract_ids": [provider_id],
            "retriever_contract_revision": "owledge.markdown-reference-retriever/1", "max_records": 256,
            "max_bytes": 4194304, "completion": "all_matched_records_healthy_and_scanned"}},
        provider_contracts={provider_id: {"schema": "owledge.evidence-provider-contract/1", "revision": "demo-provider-1",
            "evidence_key": "project.agent_lesson.review_window_hours", "provider_authority_id": PROJECT,
            "provider_schema": "owledge.managed-markdown/1", "lifecycle": "accepted", "processing_layer": ["condensed", "delta"],
            "source_trust": "internal", "knowledge_kind": "project_fact", "memory_kind": "semantic",
            "value_contract": {"type": "integer_string", "minimum": 1, "maximum": 168}}},
        coverage_cases={case_id: {"case_revision": "demo-case-1", "required_evidence": ["project.agent_lesson.review_window_hours"],
            "safe_topic": "Agent-Lesson-Reviewfenster", "search_envelope_id": envelope_id,
            "provider_contract_ids": [provider_id], "gap_admission": "proof_required", "resolution_route_id": route_id}})
    documents["project/.owledge/artifact-routing.md"] = _document(PROJECT, "routing:demo", "DEMO-Ziel für die geprüfte Antwort.",
        schema="owledge.artifact-routing/1", routes={route_id: {"route_revision": "demo-route-1", "coverage_case_id": case_id,
            "target_artifact_id": "artifact:demo-agent-lesson-review-window", "target_relative_path": "knowledge/agent-lesson-review-window.md",
            "target_schema": "owledge.managed-markdown/1", "write_mode": "create", "knowledge_kind": "project_fact", "memory_kind": "semantic",
            "candidate_processing_layer": "delta", "accepted_lifecycle": "accepted", "target_source_trust": "internal",
            "default_title": "DEMO Agent Lesson Review Window", "record_projection": "full_body_without_frontmatter"}})
    state = {
        "schema": WORKSPACE_SCHEMA,
        "roots": {"project": "project", "user-global": "global", "source": "sources/" + source_snapshot_target_name(snapshot)},
        "source_root": str(snapshot.source_root), "source_snapshot_sha256": snapshot.snapshot_sha256,
        "source_id": snapshot.source_id, "demo": True,
        "runtime_sha256": runtime_fingerprint(),
    }
    documents["workspace.json"] = json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return documents


def _unlinked_path(path: Path) -> Path:
    absolute = path.absolute()
    for part in (absolute, *absolute.parents):
        if part.exists() and (part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("Der Arbeitsordner darf keine Verknüpfungen enthalten.")
    return absolute.resolve(strict=True)


def open_workspace(target: Path):
    """Resolve only the fixed local roots; persisted state cannot inject authority paths."""
    from owledge_core.api import Core
    root = _unlinked_path(Path(target))
    state = json.loads(_state_bytes(root))
    from .project_workspace import SCHEMA as PROJECT_SCHEMA, LINKED_SCHEMA, open_project_workspace
    if isinstance(state, dict) and state.get("schema") in {PROJECT_SCHEMA, LINKED_SCHEMA}:
        return open_project_workspace(root, state)
    from .knowledge_workspace import SCHEMA as KNOWLEDGE_SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA, open_knowledge_workspace
    if isinstance(state, dict) and state.get("schema") in {KNOWLEDGE_SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}:
        return open_knowledge_workspace(root, state)
    from .source_workspace import SCHEMA, open_source_workspace
    if isinstance(state, dict) and state.get("schema") == SCHEMA:
        return open_source_workspace(root, state)
    if not isinstance(state, dict) or state.get("schema") != WORKSPACE_SCHEMA or state.get("demo") is not True:
        raise ValueError("Dieser Workspace-Vertrag wird nicht unterstützt.")
    if any(not isinstance(state.get(key), str) or not state[key] for key in ("source_root", "source_snapshot_sha256", "source_id", "runtime_sha256")):
        raise ValueError("Die Workspace-Konfiguration ist unvollständig.")
    mapping = state.get("roots")
    if not isinstance(mapping, dict) or set(mapping) != {"project", "user-global", "source"}:
        raise ValueError("Die lokalen Wissensbereiche sind unvollständig.")
    if mapping["project"] != "project" or mapping["user-global"] != "global":
        raise ValueError("Die lokalen Wissensbereiche wurden verändert.")
    source_relative = mapping["source"]
    if not isinstance(source_relative, str) or len(source_relative.split("/")) != 2 or not source_relative.startswith("sources/") or "\\" in source_relative or ".." in source_relative:
        raise ValueError("Die Originalkopie besitzt keinen gültigen lokalen Pfad.")
    roots = {name: _unlinked_path(root / relative) for name, relative in mapping.items()}
    if any(not path.is_relative_to(root) for path in roots.values()):
        raise ValueError("Ein Wissensbereich liegt außerhalb des Arbeitsordners.")
    core = Core.open(roots, identity_profile="mvp-v1", clock=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    return core, state


def open_settings_workspace(target: Path):
    """Open only the fixed Owner Settings authority during interrupted transport."""
    from owledge_core.api import Core
    from .project_workspace import SCHEMA as PROJECT_SCHEMA, LINKED_SCHEMA
    from .knowledge_workspace import SCHEMA as KNOWLEDGE_SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA
    from .source_workspace import SCHEMA as SOURCE_SCHEMA
    root = _unlinked_path(Path(target))
    state = json.loads(_state_bytes(root, settings_repair=True))
    if not isinstance(state, dict) or not isinstance(state.get("roots"), dict):
        raise ValueError("Settings workspace state is invalid")
    if state.get("schema") in {PROJECT_SCHEMA, LINKED_SCHEMA}:
        authority_id = state.get("authority_id")
        if (not isinstance(authority_id, str) or not re.fullmatch(r"project:[a-z0-9]+(?:-[a-z0-9]+)*", authority_id)
                or state["roots"].get("project") != "project"):
            raise ValueError("Project Settings authority is invalid")
        authority_root = _unlinked_path(root / "project")
    elif state.get("schema") in {KNOWLEDGE_SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA, SOURCE_SCHEMA}:
        if state["roots"].get("user-global") != "global":
            raise ValueError("Global Settings authority is invalid")
        authority_id = "user-global:source-access"
        authority_root = _unlinked_path(root / "global")
    else:
        raise ValueError("Settings require a single Project or Global workspace")
    return Core.open({authority_id: authority_root}, identity_profile="mvp-v1"), state, authority_id


class OwnerWorkspaceSetup:
    """Preview an explicit disposable workspace; never interpret source Markdown."""

    def __init__(self, target: Path, source: Path | None) -> None:
        from owledge_connectors.markdown_source import MarkdownSourceConnector

        self.target = Path(target).absolute()
        self.source = Path(source).absolute() if source is not None else None
        paths = (self.target,) if self.source is None else (self.target, self.source)
        for path in paths:
            for part in (path, *path.parents):
                if part.exists() and (
                    part.is_symlink()
                    or getattr(part.lstat(), "st_file_attributes", 0)
                    & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
                ):
                    raise ValueError("Quelle und Ziel dürfen keine Verknüpfungen enthalten.")
        if not self.target.parent.is_dir():
            raise ValueError("Erstelle zuerst den übergeordneten Zielordner; wähle darin einen neuen Arbeitsordner.")
        if self.target.exists():
            raise ValueError("Wähle einen neuen, noch nicht vorhandenen Arbeitsordner.")
        if self.source is None:
            self.snapshot = None
            return
        source_resolved = self.source.resolve(strict=True)
        target_resolved = self.target.resolve()
        try:
            common = Path(os.path.commonpath((source_resolved, target_resolved)))
        except ValueError:
            common = None
        if common in {source_resolved, target_resolved}:
            raise ValueError("Quelle und Arbeitsordner müssen voneinander getrennt sein.")
        self.snapshot = MarkdownSourceConnector(self.source).scan()

    def preview(self) -> dict[str, object]:
        return {
            "status": "preview",
            "message": "DEMO: Getrennte Projekt- und Global-Bereiche; Originalquelle bleibt unverändert. Keine automatische Wissenskuratierung.",
            "documents": len(self.snapshot.files),
            "bytes": self.snapshot.size_bytes,
            "destination": str(self.target),
        }

    def apply(self) -> dict[str, object]:
        from owledge_connectors.markdown_source import MarkdownSourceConnector
        from owledge_core.project_io import materialize_owner_workspace
        current = MarkdownSourceConnector(self.source).scan()
        if current != self.snapshot:
            raise ValueError("Die Quelle wurde seit der Vorschau verändert. Bitte neu starten.")
        materialize_owner_workspace(self.target, _bootstrap_documents(current), source_snapshot=current)
        return {"status": "ready", "message": "DEMO-Arbeitsordner mit unveränderten Originalen ist bereit.", "destination": str(self.target)}


def workspace_health(target: Path) -> dict[str, object]:
    from .source_workspace import SCHEMA, source_workspace_health
    state = json.loads(_state_bytes(target))
    def with_settings(health: dict[str, object]) -> dict[str, object]:
        from owledge_core.project_io import inspect_settings
        roots = state.get("roots", {}) if isinstance(state, dict) else {}
        layers = []
        for name, authority_id in (("project", str(state.get("authority_id", ""))),
                                   ("user-global", "user-global:source-access")):
            relative = roots.get(name) if isinstance(roots, dict) else None
            if isinstance(relative, str) and relative:
                try:
                    layers.append(inspect_settings(target / relative, authority_id))
                except (ValueError, OSError) as error:
                    layers.append({"status": "quarantined", "diagnostics": [{"code": "settings_contract_invalid",
                        "source": name, "key": None, "rule": str(error)}]})
        health["settings"] = layers
        if any(item["status"] != "ready" for item in layers):
            health["status"] = "needs_attention"
        return health
    from .project_workspace import SCHEMA as PROJECT_SCHEMA, LINKED_SCHEMA, project_workspace_health
    if isinstance(state, dict) and state.get("schema") in {PROJECT_SCHEMA, LINKED_SCHEMA}:
        return with_settings(project_workspace_health(target))
    from .knowledge_workspace import SCHEMA as KNOWLEDGE_SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA, knowledge_workspace_health
    if isinstance(state, dict) and state.get("schema") in {KNOWLEDGE_SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}:
        return with_settings(knowledge_workspace_health(target))
    if isinstance(state, dict) and state.get("schema") == SCHEMA:
        return with_settings(source_workspace_health(target))
    from .mcp import ContributorMcpAdapter
    from owledge_connectors.markdown_source import MarkdownSourceConnector
    core, state = open_workspace(target)
    results = {}
    for name, authority in (("project", PROJECT), ("global", GLOBAL)):
        adapter = ContributorMcpAdapter(core, principal_id=CONTRIBUTOR, active_authority_id=authority,
            reported={"agent_name": "owner-host", "model": "none"}, adapter_observed={"runtime": "local", "runtime_version": "1", "run_id": "doctor"})
        result = adapter.execute("inspect", "op:doctor:" + name, {})
        results[name] = "healthy" if result.get("reason_code") == "project_inspected" and result.get("data", {}).get("health", {}).get("invalid_documents", 0) == 0 else "needs_repair"
    snapshot = MarkdownSourceConnector(Path(state["source_root"])).scan()
    unchanged = snapshot.snapshot_sha256 == state["source_snapshot_sha256"]
    from owledge_core.project_io import _source_snapshot_files, _validate_materialized_source
    originals_unchanged = False
    if unchanged:
        expected, originals, _ = _source_snapshot_files(snapshot, "op:owner-workspace-setup", OWNER)
        _validate_materialized_source(Path(target) / state["roots"]["source"], expected, originals)
        originals_unchanged = True
    trace = None
    receipt = state.get("last_gap_receipt")
    if receipt is not None:
        adapter = ContributorMcpAdapter(core, principal_id=CONTRIBUTOR, active_authority_id=PROJECT,
            reported={"agent_name": "owner-host", "model": "none"}, adapter_observed={"runtime": "local", "runtime_version": "1", "run_id": "doctor-trace"})
        result = adapter.execute("trace_read", "op:doctor:trace", {"receipt_id": receipt})
        trace = result.get("reason_code") == "trace_ready"
    return {"status": "healthy" if unchanged and trace is not False and all(value == "healthy" for value in results.values()) else "needs_attention",
            **results, "source_unchanged": unchanged, "originals_unchanged": originals_unchanged,
            "trace_verified": trace, "receipts_verified": trace,
            "runtime_current": state.get("runtime_sha256") == runtime_fingerprint(),
            "message": "DEMO-Kandidat; Trace- und Receipt-Verknüpfungen nur für den zuletzt abgeschlossenen Gap-Lauf, keine signierte Echtheit. Originalquellen werden nicht automatisch kuratiert."}


class LocalSetupAdapter:
    """Bind local Owner assurance and hide Core setup metadata."""

    def __init__(self, core: object, *, principal_id: str) -> None:
        self._core = core
        self._principal_id = principal_id

    @staticmethod
    def _data(result: Mapping[str, object]) -> Mapping[str, object]:
        data = result.get("data")
        return data if isinstance(data, dict) else {}

    def preview(self, source: str) -> dict[str, object]:
        method = getattr(self._core, "_preview_source_setup_from_local_owner", None)
        if method is None:
            return {
                "status": "invalid",
                "message": "Die lokale Setup-Schnittstelle ist nicht verfügbar.",
                "user_action_required": False,
            }
        result = method(source, self._principal_id)
        if (result.get("status"), result.get("reason_code")) == (
            "preview",
            "setup_preview_ready",
        ):
            data = self._data(result)
            return {
                "status": "preview",
                "message": "Quelle geprüft. Bestätige die unveränderliche Arbeitskopie.",
                "documents": data.get("document_count", 0),
                "bytes": data.get("size_bytes", 0),
                "destination": data.get("target_name", ""),
                "decision_options": ["apply", "reject"],
                "user_action_required": True,
            }
        return self._failure(result)

    def apply(self) -> dict[str, object]:
        method = getattr(self._core, "_apply_source_setup_from_local_owner", None)
        if method is None:
            return {
                "status": "invalid",
                "message": "Die lokale Setup-Schnittstelle ist nicht verfügbar.",
                "user_action_required": False,
            }
        result = method(self._principal_id)
        if (result.get("status"), result.get("reason_code")) == (
            "ok",
            "source_snapshot_ready",
        ):
            data = self._data(result)
            return {
                "status": "ready",
                "message": "Die schreibgeschützte Arbeitskopie ist bereit.",
                "documents": data.get("document_count", 0),
                "bytes": data.get("size_bytes", 0),
                "destination": data.get("target_name", ""),
                "already_current": data.get("already_current", False),
                "user_action_required": False,
            }
        return self._failure(result)

    def reject(self) -> dict[str, object]:
        method = getattr(self._core, "_cancel_source_setup_from_local_owner", None)
        if method is None:
            return {
                "status": "invalid",
                "message": "Die lokale Setup-Schnittstelle ist nicht verfügbar.",
                "user_action_required": False,
            }
        result = method(self._principal_id)
        if (result.get("status"), result.get("reason_code")) == (
            "ok",
            "setup_cancelled",
        ):
            return {
                "status": "cancelled",
                "message": "Die Vorschau wurde verworfen; es wurde nichts geschrieben.",
                "user_action_required": False,
            }
        return self._failure(result)

    @staticmethod
    def _failure(result: Mapping[str, object]) -> dict[str, object]:
        status = str(result.get("status", "invalid"))
        visible_status = {
            "stale": "needs_refresh",
            "recovery_required": "needs_repair",
            "denied": "not_allowed",
            "invalid": "invalid",
        }.get(status, "failed")
        return {
            "status": visible_status,
            "message": str(result.get("summary", "Das Setup konnte nicht abgeschlossen werden.")),
            "user_action_required": status in {"stale", "recovery_required"},
        }
