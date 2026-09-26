"""Transport-neutral private Core command/result seam."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
import os
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Mapping

from .artifacts import ManagedMarkdown, parse_managed_markdown, parse_markdown_frontmatter
from .contracts import (
    AuthorityRepository,
    Clock,
    ContractValidationError,
    CoverageCaseInvalidError,
    EvidenceRetriever,
    SourceConnector,
    SourceSnapshot,
    SourceSnapshotError,
)
from .health import invalid_document_count
from .lifecycle import LifecycleValidationError, preview_maintenance_bundle, render_maintenance_bundle
from .policy import has_grant, source_access_allowed, source_rights_allowed, named_connection_capabilities
from .project_io import (
    MarkdownAuthorityRepository,
    SettingsQuarantineError,
    authority_write_locks,
    case_configuration_pending,
    canonical_recovery_pending,
    recover_pending_effects,
    materialize_source_snapshot,
    source_snapshot_target_name,
)
from .retrieval import (
    raw_evidence_hit,
    CoverageOutcome,
    MarkdownReferenceRetriever,
    absence_proof_staleness_reason,
    progressive_assess,
    normalize_typed_filters,
    matches_typed_filters,
)


__all__: tuple[str, ...] = ()


_IDENTITY_PROFILES = frozenset({"poc-v1", "mvp-v1"})
_INITIAL_CANDIDATE_REVISION = re.compile(r"candidate-rev-1(?:-[0-9a-f]{16})?\Z")
_REVIEWED_CANDIDATE_REVISION = re.compile(
    r"candidate-rev-2-reviewed(?:-[0-9a-f]{16})?\Z"
)


@dataclass(frozen=True)
class _OperationPolicy:
    capability: str
    payload_required: bool = False
    write_lock: str | None = None


_OPERATION_POLICIES = MappingProxyType({
    "bundle_open": _OperationPolicy("propose", payload_required=True, write_lock="always"),
    "bundle_preview": _OperationPolicy("propose", payload_required=True, write_lock="always"),
    "case_correct": _OperationPolicy("propose", payload_required=True, write_lock="always"),
    "candidate_open": _OperationPolicy("review", payload_required=True),
    "candidate_queue": _OperationPolicy("review", payload_required=True),
    "candidate_review": _OperationPolicy("review", payload_required=True, write_lock="local_owner"),
    "candidate_promote": _OperationPolicy("promote", payload_required=True, write_lock="local_owner"),
    "contribute_for_reuse": _OperationPolicy("propose", payload_required=True),
    "curate_candidate": _OperationPolicy("propose", payload_required=True, write_lock="always"),
    "source_candidate": _OperationPolicy("propose", payload_required=True, write_lock="always"),
    "source_reference_refresh": _OperationPolicy("promote", payload_required=True, write_lock="local_owner"),
    "lesson_candidate": _OperationPolicy("propose", write_lock="always"),
    "project_record_candidate": _OperationPolicy("propose", payload_required=True, write_lock="always"),
    "curated_read": _OperationPolicy("retrieve", payload_required=True),
    "curated_discover": _OperationPolicy("retrieve"),
    "gap_admit": _OperationPolicy("propose", payload_required=True, write_lock="always"),
    "gap_verify": _OperationPolicy("promote", payload_required=True, write_lock="local_owner"),
    "inspect": _OperationPolicy("discover"),
    "settings_inspect": _OperationPolicy("retrieve"),
    "maintenance_observe": _OperationPolicy("propose", payload_required=True, write_lock="always"),
    "progressive_retrieve": _OperationPolicy("retrieve", payload_required=True),
    "reuse_feed_discover": _OperationPolicy("retrieve"),
    "retrieve": _OperationPolicy("retrieve", payload_required=True),
    "recover": _OperationPolicy("promote", payload_required=True, write_lock="local_owner"),
    "trace_read": _OperationPolicy("retrieve", payload_required=True),
})


class _FixedClock:
    def __init__(self, value: str | None) -> None:
        self._value = value

    def now(self) -> str | None:
        return self._value


class Core:
    def __init__(
        self,
        roots: Mapping[str, Path],
        clock: str | Clock | None = None,
        repository: AuthorityRepository[ManagedMarkdown] | None = None,
        reference_retriever: EvidenceRetriever[ManagedMarkdown, CoverageOutcome] | None = None,
        derived_retriever: EvidenceRetriever[ManagedMarkdown, CoverageOutcome] | None = None,
        identity_profile: str = "poc-v1",
        setup_workspace: Path | None = None,
        source_connector_factory: Callable[[Path], SourceConnector] | None = None,
    ) -> None:
        if identity_profile not in _IDENTITY_PROFILES:
            raise ValueError("Unknown Core identity profile")
        self._roots = {str(alias): Path(root) for alias, root in roots.items()}
        self._clock = _FixedClock(clock) if isinstance(clock, str) or clock is None else clock
        self._repository = repository or MarkdownAuthorityRepository(self._roots)
        self._reference_retriever = reference_retriever or MarkdownReferenceRetriever()
        self._derived_retriever = derived_retriever
        self._identity_profile = identity_profile
        self._setup_workspace = Path(setup_workspace) if setup_workspace is not None else None
        self._source_connector_factory = source_connector_factory
        self._setup_pending: SourceSnapshot | None = None

    @classmethod
    def open(
        cls,
        roots: Mapping[str, Path],
        *,
        clock: str | Clock | None = None,
        repository: AuthorityRepository[ManagedMarkdown] | None = None,
        reference_retriever: EvidenceRetriever[ManagedMarkdown, CoverageOutcome] | None = None,
        derived_retriever: EvidenceRetriever[ManagedMarkdown, CoverageOutcome] | None = None,
        identity_profile: str = "poc-v1",
        setup_workspace: Path | None = None,
        source_connector_factory: Callable[[Path], SourceConnector] | None = None,
    ) -> "Core":
        return cls(
            roots,
            clock=clock,
            repository=repository,
            reference_retriever=reference_retriever,
            derived_retriever=derived_retriever,
            identity_profile=identity_profile,
            setup_workspace=setup_workspace,
            source_connector_factory=source_connector_factory,
        )

    def _root_for_authority(self, authority_id: str) -> Path | None:
        alias = authority_id.split(":", 1)[0]
        return self._roots.get(authority_id, self._roots.get(alias))

    def _owner_settings_preflight(self, *workspaces: Path) -> None:
        """Check the owning authority before private Owner previews or effects."""
        from .project_io import require_settings_healthy, _read_exact_effect
        from .artifacts import parse_managed_markdown
        selected = {Path(value).resolve() for value in workspaces}
        for root in self._roots.values():
            if Path(root).parent.resolve() in selected:
                encoded = _read_exact_effect(Path(root), Path(root) / ".owledge/authority.md",
                                             max_bytes=1_048_576)
                authority = parse_managed_markdown(".owledge/authority.md", encoded.decode("utf-8"),
                                                   encoded_document=encoded)
                require_settings_healthy(Path(root), authority.authority_id)

    def _project_reuse_from_local_owner(self, project_workspace, global_workspace, *, apply=False, recover=False):
        """Fixed private local Owner setup port; never Contributor command dispatch."""
        from .project_io import (prepare_project_reuse_registration, apply_project_reuse_registration,
                                 recover_project_reuse_registration, _reuse_roots)
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner setup is required")
        self._owner_settings_preflight(Path(project_workspace), Path(global_workspace))
        project, target = _reuse_roots(project_workspace, global_workspace)
        def check_owner(project_id):
            from .project_io import bootstrap_authority, require_settings_healthy
            if not project_id.startswith("project:"):
                raise ContractValidationError("Project authority is required")
            for root, identity in ((project / "project", project_id), (target / "global", "user-global:source-access")):
                authority = bootstrap_authority(root, identity)
                require_settings_healthy(root, identity)
                if authority.metadata.get("mode") != "read_write" or not has_grant(authority, "principal:local-owner", "promote"):
                    raise ContractValidationError("local Owner write authority is required on both sides")
        if recover:
            with authority_write_locks((project, project / "project", target, target / "global")):
                receipt_id = recover_project_reuse_registration(project, target, check_owner=check_owner)
            return {"status": "ready", "receipt_id": receipt_id}
        if not apply:
            self._reuse_registration_pending = None
            pending = prepare_project_reuse_registration(project, target, check_owner=check_owner)
            self._reuse_registration_pending = (project, target, pending)
            return {"status": "preview", "authority_id": pending["authority_id"], "destination": str(target),
                "source_link_id": pending["source_link_id"], "grants": ["contribute"],
                "receipt_id": pending["receipt_id"], "message": "Nur Beitragsrecht; keine Global-Leserechte, keine Wissensfreigabe."}
        saved = getattr(self, "_reuse_registration_pending", None)
        self._reuse_registration_pending = None
        if saved is None or saved[:2] != (project, target):
            raise ContractValidationError("reuse registration preview is required")
        receipt_id = apply_project_reuse_registration(project, target, saved[2], check_owner=check_owner)
        return {"status": "ready", "receipt_id": receipt_id}

    def _named_contribution_grant_from_local_owner(self, project_workspace, *, name, action,
                                                    expected_sha256=None, apply=False):
        from .project_io import change_named_contribution_grant
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner contribution configuration is required")
        self._owner_settings_preflight(Path(project_workspace))
        project = Path(project_workspace)
        from .project_io import _reuse_read
        state_raw = _reuse_read(project, "workspace.json")
        state = json.loads(state_raw) if state_raw else {}
        project_id = state.get("authority_id") if isinstance(state, dict) else None
        root = self._root_for_authority(project_id) if isinstance(project_id, str) else None
        if root is None or root.resolve() != (project / "project").resolve():
            raise ContractValidationError("Project workspace does not own contribution authority")

        def check_owner(project_authority, global_authority):
            if any(item.metadata.get("mode") != "read_write" or
                   not has_grant(item, "principal:local-owner", "promote")
                   for item in (project_authority, global_authority)):
                raise ContractValidationError("local Owner write authority is required on both sides")

        def check_profile(project_authority, profile, principal):
            grants = project_authority.metadata.get("actor_grants")
            return (isinstance(grants, dict) and profile.get("status") == "active"
                    and grants.get(principal) == list(named_connection_capabilities("contributor")))

        return change_named_contribution_grant(project, name=name, action=action,
            expected_sha256=expected_sha256, apply=apply,
            check_owner=check_owner, check_profile=check_profile)

    def _named_global_reader_from_local_owner(self, project_workspace, *, name, action,
                                              expected_sha256=None, apply=False):
        from .project_io import change_named_global_reader, _reuse_read
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner reader configuration is required")
        self._owner_settings_preflight(Path(project_workspace))
        project = Path(project_workspace)
        state_raw = _reuse_read(project, "workspace.json")
        state = json.loads(state_raw) if state_raw else {}
        project_id = state.get("authority_id") if isinstance(state, dict) else None
        root = self._root_for_authority(project_id) if isinstance(project_id, str) else None
        if root is None or root.resolve() != (project / "project").resolve():
            raise ContractValidationError("Project workspace does not own reader authority")

        def check_owner(project_authority, global_authority):
            if any(item.metadata.get("mode") != "read_write" or
                   not has_grant(item, "principal:local-owner", "promote")
                   for item in (project_authority, global_authority)):
                raise ContractValidationError("local Owner write authority is required on both sides")

        def check_profile(project_authority, profile, principal):
            grants = project_authority.metadata.get("actor_grants")
            return (isinstance(grants, dict) and profile.get("status") == "active"
                    and grants.get(principal) == list(named_connection_capabilities("contributor"))
                    and has_grant(project_authority, principal, "retrieve"))

        return change_named_global_reader(project, name=name, action=action,
            expected_sha256=expected_sha256, apply=apply,
            check_owner=check_owner, check_profile=check_profile)

    def _named_project_reader_from_local_owner(self, global_workspace, *, project_id, name,
                                               action=None, project_workspace=None,
                                               expected_sha256=None, apply=False, recover=False):
        from .project_io import (change_named_project_reader, recover_named_project_reader,
                                 _project_reader_workspace)
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner Project reader configuration is required")
        self._owner_settings_preflight(Path(global_workspace), *(Path(project_workspace),) if project_workspace else ())
        target = Path(global_workspace)
        global_root = self._root_for_authority("user-global:source-access")
        if global_root is None or global_root.resolve() != (target / "global").resolve():
            raise ContractValidationError("Global workspace does not own reader authority")
        from .project_io import require_settings_healthy
        project_for_settings = _project_reader_workspace(target, project_id,
            Path(project_workspace) if project_workspace is not None else None)
        require_settings_healthy(project_for_settings / "project", project_id)

        def check_owner(global_authority, project_authority):
            if any(item.metadata.get("mode") != "read_write" or
                   not has_grant(item, "principal:local-owner", "promote")
                   for item in (global_authority, project_authority)):
                raise ContractValidationError("local Owner write authority is required on both sides")

        def check_profile(global_authority, profile, principal):
            grants = global_authority.metadata.get("actor_grants")
            return (isinstance(grants, dict) and profile.get("status") == "active"
                    and grants.get(principal) == list(named_connection_capabilities("contributor"))
                    and has_grant(global_authority, principal, "retrieve"))

        if recover:
            if project_workspace is None or action not in {"grant", "revoke"} or not apply:
                raise ContractValidationError("Project reader recovery needs exact roots and action with --yes")
            project = _project_reader_workspace(target, project_id, Path(project_workspace))
            with authority_write_locks((project, project / "project", target, target / "global"),
                                       allow_project_reader_recovery=True):
                return recover_named_project_reader(target, project_workspace=project,
                    project_id=project_id, name=name, action=action,
                    check_owner=check_owner, check_profile=check_profile)
        return change_named_project_reader(target, project_id=project_id, name=name, action=action,
            project_workspace=Path(project_workspace) if project_workspace is not None else None,
            expected_sha256=expected_sha256, apply=apply,
            check_owner=check_owner, check_profile=check_profile)

    def _read_named_global_bridge(self, command, project_authority, principal_id):
        """Recheck the saved read bridge under both authority locks before one reviewed read."""
        from .project_io import (_reuse_read, _reuse_project_state,
            validate_project_reuse_binding, local_connection_principal)
        project_id = project_authority.authority_id
        project_root = self._root_for_authority(project_id)
        global_root = self._root_for_authority("user-global:source-access")
        if project_root is None or global_root is None or project_root.name != "project":
            return self._result("denied", "global_reader_bridge_denied", "Project bridge is unavailable.",
                                "Use a registered Project connection.", {})
        project = project_root.parent
        try:
            with authority_write_locks((project_root, global_root)):
                state = _reuse_project_state(_reuse_read(project, "workspace.json"), linked=True)
                if (state["authority_id"] != project_id or
                        (validate_project_reuse_binding(project, state) / "global").resolve() != global_root.resolve()):
                    raise ContractValidationError("saved Global target changed")
                current_project = self._repository.bootstrap(project_id)
                current_global = self._repository.bootstrap("user-global:source-access")
                bridges = current_global.metadata.get("named_project_readers", {})
                binding = bridges.get(principal_id) if isinstance(bridges, dict) else None
                if not isinstance(binding, dict):
                    raise ContractValidationError("named Global reader binding is absent")
                name = binding.get("connection")
                profiles = current_project.metadata.get("connections")
                profile = profiles.get(name) if isinstance(profiles, dict) and isinstance(name, str) else None
                generations = current_project.metadata.get("connection_generations", {})
                generation = generations.get(name, current_project.content_sha256) if isinstance(generations, dict) else None
                link = state["global_contribution"]
                expected = {"project_workspace": str(project), "project_authority_id": project_id,
                    "connection": name, "principal_id": principal_id,
                    "contribution_link_id": link["source_link_id"],
                    "registration_receipt_id": link["receipt_id"], "profile_generation": generation}
                if (not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", name)
                        or principal_id != local_connection_principal(project_id, name)
                        or binding != expected or not isinstance(profile, dict)
                        or profile.get("principal_id") != principal_id
                        or profile.get("authority_id") != project_id
                        or profile.get("role") != "contributor" or profile.get("status") != "active"
                        or profile.get("source_link_id") is not None
                        or current_project.metadata.get("actor_grants", {}).get(principal_id)
                            != list(named_connection_capabilities("contributor"))
                        or not has_grant(current_project, principal_id, "retrieve")
                        or not has_grant(current_global, principal_id, "retrieve")):
                    raise ContractValidationError("named Global reader is no longer current")
                bridge_hash = sha256(json.dumps([current_project.content_sha256,
                    current_global.content_sha256, expected], sort_keys=True).encode()).hexdigest()
                inner = dict(command)
                inner["active_authority_id"] = "user-global:source-access"
                payload = command.get("payload")
                if command.get("operation") == "curated_discover" and isinstance(payload, dict):
                    payload = dict(payload)
                    cursor = payload.get("cursor")
                    if cursor is not None:
                        if (not isinstance(cursor, dict) or set(cursor) != {"bridge_binding", "global_cursor"}
                                or cursor["bridge_binding"] != bridge_hash):
                            raise ContractValidationError("Global reader continuation is stale")
                        payload["cursor"] = cursor["global_cursor"]
                    inner["payload"] = payload
                result = self._execute(inner, trusted_assurance="asserted", _validated_global_reader=True)
                if (command.get("operation") == "curated_discover" and isinstance(result.get("data"), dict)
                        and result["data"].get("continuation") is not None):
                    result = dict(result)
                    data = dict(result["data"])
                    data["continuation"] = {"bridge_binding": bridge_hash,
                                            "global_cursor": data["continuation"]}
                    result["data"] = data
                return result
        except (ContractValidationError, OSError, ValueError, TypeError):
            return self._result("denied", "global_reader_bridge_denied",
                "The named Project Global reader is not current.",
                "Ask the local Owner to check the saved bridge and reader grant.", {})

    def _read_named_project_bridge(self, command, global_authority, principal_id):
        """Resolve one Owner-registered Project on demand; Global-local reads stay independent."""
        from .project_io import (_reuse_read, _reuse_project_state, _reuse_roots,
            validate_project_reuse_binding, project_reader_pending,
            local_connection_principal, bootstrap_authority)
        project_id = command.get("target_authority_id")
        if not isinstance(project_id, str) or not re.fullmatch(r"project:[a-z0-9]+(?:-[a-z0-9]+)*", project_id):
            return self._result("denied", "project_reader_bridge_denied", "Project reader target is invalid.",
                                "Choose an Owner-registered Project ID.", {})
        global_root = self._root_for_authority("user-global:source-access")
        if global_root is None or global_root.name != "global":
            return self._result("denied", "project_reader_bridge_denied", "Global reader root is unavailable.",
                                "Open the approved Global workspace.", {})
        target_workspace = global_root.parent
        try:
            registry = global_authority.metadata.get("project_read_targets", {})
            target = registry.get(project_id) if isinstance(registry, dict) and len(registry) <= 32 else None
            if not isinstance(target, dict) or not isinstance(target.get("project_workspace"), str):
                raise ContractValidationError("Project reader target is not registered")
            project, checked_global = _reuse_roots(target["project_workspace"], target_workspace)
            if checked_global != target_workspace:
                raise ContractValidationError("Project reader target changed")
            project_root = project / "project"
            with authority_write_locks((target_workspace, global_root, project, project_root)):
                if any(project_reader_pending(root) for root in (project, target_workspace)):
                    raise ContractValidationError("Project reader recovery is required")
                current_global = self._repository.bootstrap("user-global:source-access")
                current_project = bootstrap_authority(project_root, project_id)
                registry = current_global.metadata.get("project_read_targets", {})
                target = registry.get(project_id) if isinstance(registry, dict) and len(registry) <= 32 else None
                state = _reuse_project_state(_reuse_read(project, "workspace.json"), linked=True)
                if state["authority_id"] != project_id or validate_project_reuse_binding(project, state) != target_workspace:
                    raise ContractValidationError("Project reciprocal link changed")
                link = state["global_contribution"]
                target_base = {"project_workspace": str(project), "project_authority_id": project_id,
                    "global_workspace": str(target_workspace), "contribution_link_id": link["source_link_id"],
                    "registration_receipt_id": link["receipt_id"]}
                if not isinstance(target, dict) or set(target) != set(target_base) | {"readers"} or any(
                        target.get(key) != value for key, value in target_base.items()):
                    raise ContractValidationError("Project reader registration changed")
                readers = target.get("readers")
                reader = readers.get(principal_id) if isinstance(readers, dict) and len(readers) <= 32 else None
                name = reader.get("connection") if isinstance(reader, dict) else None
                profiles = current_global.metadata.get("connections")
                profile = profiles.get(name) if isinstance(profiles, dict) and isinstance(name, str) else None
                generations = current_global.metadata.get("connection_generations", {})
                generation = generations.get(name, current_global.content_sha256) if isinstance(generations, dict) else None
                expected_reader = {"connection": name, "principal_id": principal_id,
                                   "profile_generation": generation}
                expected_project = {**target_base, **expected_reader}
                project_bindings = current_project.metadata.get("named_global_readers", {})
                if (not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", name)
                        or principal_id != local_connection_principal("user-global:source-access", name)
                        or reader != expected_reader or not isinstance(profile, dict)
                        or profile.get("principal_id") != principal_id
                        or profile.get("authority_id") != "user-global:source-access"
                        or profile.get("role") != "contributor" or profile.get("status") != "active"
                        or profile.get("source_link_id") is not None
                        or current_global.metadata.get("actor_grants", {}).get(principal_id)
                            != list(named_connection_capabilities("contributor"))
                        or not has_grant(current_global, principal_id, "retrieve")
                        or not isinstance(project_bindings, dict)
                        or project_bindings.get(principal_id) != expected_project
                        or current_project.metadata.get("actor_grants", {}).get(principal_id) != ["retrieve"]):
                    raise ContractValidationError("named Project reader is no longer current")
                binding = sha256(json.dumps([current_global.content_sha256, current_project.content_sha256,
                    expected_project, project_id], sort_keys=True).encode()).hexdigest()
                inner = dict(command)
                inner["active_authority_id"] = project_id
                payload = command.get("payload")
                if command.get("operation") == "curated_discover" and isinstance(payload, dict):
                    payload = dict(payload)
                    cursor = payload.get("cursor")
                    if cursor is not None:
                        if (not isinstance(cursor, dict) or set(cursor) != {"project_reader_binding", "project_cursor"}
                                or cursor["project_reader_binding"] != binding):
                            raise ContractValidationError("Project reader continuation is stale")
                        payload["cursor"] = cursor["project_cursor"]
                    inner["payload"] = payload
                scoped = Core.open({**self._roots, project_id: project_root}, clock=self._clock,
                    identity_profile=self._identity_profile,
                    reference_retriever=self._reference_retriever,
                    derived_retriever=self._derived_retriever,
                    source_connector_factory=self._source_connector_factory)
                result = scoped._execute(inner, trusted_assurance="asserted", _validated_project_reader=True)
                if (command.get("operation") == "curated_discover" and isinstance(result.get("data"), dict)
                        and result["data"].get("continuation") is not None):
                    result = dict(result)
                    data = dict(result["data"])
                    data["continuation"] = {"project_reader_binding": binding,
                                            "project_cursor": data["continuation"]}
                    result["data"] = data
                return result
        except (ContractValidationError, OSError, ValueError, TypeError):
            return self._result("denied", "project_reader_bridge_denied",
                "The named Global Project reader is not current.",
                "Ask the local Owner to check the saved Project registration and reader grant.", {})

    def _source_registration_from_local_owner(self, workspace, source, principal_id, *, apply=False, recover=False,
                                              access: str | None = None):
        """Private local setup port; never exposed by Contributor command dispatch."""
        from .project_io import prepare_source_registration, apply_source_registration, recover_source_registration
        if self._identity_profile != "mvp-v1" or self._source_connector_factory is None:
            raise ContractValidationError("local Owner setup is required")
        self._owner_settings_preflight(Path(workspace))
        authority_id = "user-global:source-access"
        authority = self._repository.bootstrap(authority_id)
        if not has_grant(authority, principal_id, "promote") or authority.metadata.get("mode") != "read_write":
            raise ContractValidationError("local Owner write authority is required")
        if self._root_for_authority(authority_id).resolve() != (Path(workspace) / "global").resolve():
            raise ContractValidationError("registration workspace does not own this authority")
        if recover:
            with authority_write_locks((Path(workspace), Path(workspace) / "global")):
                authority = self._repository.bootstrap(authority_id)
                if not has_grant(authority, principal_id, "promote") or authority.metadata.get("mode") != "read_write":
                    raise ContractValidationError("local Owner write authority changed")
                recover_source_registration(Path(workspace))
            return {"status": "ready", "message": "Unterbrochene Quellenregistrierung wiederhergestellt."}
        if not apply:
            self._registration_pending = None
            snapshot = self._source_connector_factory(Path(source)).scan()
            self._registration_pending = prepare_source_registration(Path(workspace), snapshot, principal_id, access)
            return self._registration_pending["preview"]
        pending = getattr(self, "_registration_pending", None)
        self._registration_pending = None
        if pending is None:
            raise ContractValidationError("source registration preview is required")
        snapshot = self._source_connector_factory(pending["snapshot"].source_root).scan()
        if snapshot != pending["snapshot"]:
            raise ContractValidationError("source changed after preview")
        def check_authority():
            authority = self._repository.bootstrap(authority_id)
            if not has_grant(authority, principal_id, "promote") or authority.metadata.get("mode") != "read_write":
                raise ContractValidationError("local Owner write authority changed")
        result = apply_source_registration(Path(workspace), pending, principal_id, check_authority=check_authority)
        self._registration_pending = None
        return result

    def _project_concept_from_local_owner(self, project_workspace: Path, snapshot: SourceSnapshot,
                                          *, apply: bool = False, expected_sha256: str | None = None):
        """Bind one already registered canonical file; the path is local configuration."""
        from .project_io import project_concept_binding, validate_project_reuse_binding
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner concept binding is required")
        self._owner_settings_preflight(Path(project_workspace))
        project = Path(project_workspace).absolute()
        state = json.loads((project / "workspace.json").read_text(encoding="utf-8"))
        target = validate_project_reuse_binding(project, state)

        def check_owner(project_authority, global_authority, source_link):
            for authority in (project_authority, global_authority):
                if (authority.metadata.get("mode") != "read_write"
                        or not has_grant(authority, "principal:local-owner", "promote")):
                    raise ContractValidationError("local Owner authority changed")
            if not source_access_allowed(source_link, "principal:local-owner"):
                raise ContractValidationError("concept Source Link is outside Owner rights")

        if self._source_connector_factory is None:
            raise ContractValidationError("safe concept source connector is unavailable")
        return project_concept_binding(project, target, snapshot, check_owner=check_owner,
                                       scan_current=lambda path: self._source_connector_factory(path).scan(),
                                       expected_sha256=expected_sha256, apply=apply)

    def _configure_project_case_from_local_owner(self, workspace: Path, *, name: str,
            question: str, title: str, area: str, value_contract: dict[str, object],
            expected_sha256: str | None = None, apply: bool = False):
        """Local Owner port for one closed Project Coverage configuration."""
        from .project_io import configure_project_case
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner Project configuration is required")
        self._owner_settings_preflight(Path(workspace))
        project = Path(workspace).absolute() / "project"
        active_id = next((key for key, value in self._roots.items()
                          if key.startswith("project:") and Path(value).resolve() == project.resolve()), None)
        if active_id is None:
            raise ContractValidationError("workspace does not own a Project authority")
        with authority_write_locks((Path(workspace), project)):
            authority = self._repository.bootstrap(active_id)
            if authority.metadata.get("mode") != "read_write" or not has_grant(authority, "principal:local-owner", "promote"):
                raise ContractValidationError("local Owner write authority changed")
            return configure_project_case(project, active_id, name=name, question=question,
                title=title, area=area, value_contract=value_contract,
                expected_sha256=expected_sha256, apply=apply)

    def _recover_project_case_from_local_owner(self, workspace: Path):
        project = Path(workspace).absolute() / "project"
        active_id = next((key for key, value in self._roots.items()
                          if key.startswith("project:") and Path(value).resolve() == project.resolve()), None)
        if active_id is None or self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner Project recovery is required")
        with authority_write_locks((Path(workspace), project)):
            authority = self._repository.bootstrap(active_id)
            if not has_grant(authority, "principal:local-owner", "promote"):
                raise ContractValidationError("local Owner recovery authority changed")
            if not case_configuration_pending(project):
                raise ContractValidationError("no Project case configuration is pending")
            recover_pending_effects(project)
        return {"status": "ready", "message": "Project case configuration recovered."}

    def _named_case_review_preview(self, authority_id, candidate, changeset, documents):
        """Revalidate a named Bundle's result against current closed Project controls."""
        from .contracts import evidence_value_matches
        name = candidate.get("named_case")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ContractValidationError("named case binding is invalid")
        registries = [item for item in documents if item.metadata.get("schema") == "owledge.coverage-case-registry/1"]
        routings = [item for item in documents if item.metadata.get("schema") == "owledge.artifact-routing/1"]
        if len(registries) != 1 or len(routings) != 1:
            raise ContractValidationError("named case controls are invalid")
        registry = registries[0].metadata
        cases = registry.get("coverage_cases", {})
        providers = registry.get("provider_contracts", {})
        route = routings[0].metadata.get("routes", {}).get(f"route:{name}")
        case = cases.get(f"coverage:{name}") if isinstance(cases, dict) else None
        provider = providers.get(f"provider:{name}") if isinstance(providers, dict) else None
        effects = changeset.get("effects")
        document = changeset.get("result_document")
        if (not all(isinstance(item, dict) for item in (route, case, provider))
                or not isinstance(effects, list) or len(effects) != 1 or not isinstance(effects[0], dict)
                or not isinstance(document, str) or changeset.get("result_sha256") != sha256(document.encode("utf-8")).hexdigest()
                or candidate.get("coverage_case_id") != f"coverage:{name}"
                or candidate.get("coverage_case_revision") != case.get("case_revision")
                or candidate.get("resolution_route_id") != f"route:{name}"
                or candidate.get("resolution_route_revision") != route.get("route_revision")
                or effects[0].get("artifact_id") != route.get("target_artifact_id")
                or effects[0].get("relative_path") != route.get("target_relative_path")
                or case.get("provider_contract_ids") != [f"provider:{name}"]
                or route.get("value_contract") != provider.get("value_contract")
                or route.get("write_mode") != "create_or_exact_replace"
                or route.get("case_name") != name):
            raise ContractValidationError("named case result changed")
        metadata, body = parse_markdown_frontmatter(document)
        values = metadata.get("evidence_values")
        key = provider.get("evidence_key")
        if (metadata.get("authority_id") != authority_id or metadata.get("artifact_id") != route["target_artifact_id"]
                or metadata.get("knowledge_kind") != "project_fact" or not isinstance(values, dict)
                or set(values) != {key} or not evidence_value_matches(values[key], provider.get("value_contract"))
                or body.strip() != f"# {route['default_title']}\n\n{route['default_title']}: {values[key]}"):
            raise ContractValidationError("named case answer changed")
        current = [item for item in documents if item.artifact_id == route["target_artifact_id"]]
        effect_kind = effects[0].get("kind")
        coverage = self._assess_coverage(documents, f"coverage:{name}")
        if effect_kind == "create":
            if (current or changeset.get("base_revision") != "absent"
                    or coverage is None or coverage.assessment.get("assessment") != "knowledge_absent"
                    or candidate.get("absence_proof_id") != coverage.assessment.get("absence_proof_id")):
                raise ContractValidationError("named case creation base changed")
        elif effect_kind == "replace":
            context = [item for item in documents if item.artifact_id == case.get("context_artifact_id")]
            selection = candidate.get("selection_binding")
            if (len(current) != 1 or candidate.get("absence_proof_id") is not None
                    or coverage is None or coverage.assessment.get("assessment") != "coverage_satisfied"
                    or not isinstance(selection, dict)
                    or selection != changeset.get("selection_binding")
                    or len(context) != 1
                    or selection != {"source_snapshot_id": coverage.assessment.get("source_snapshot_id"),
                                     "context_artifact_id": context[0].artifact_id,
                                     "context_revision": context[0].revision,
                                     "context_sha256": context[0].content_sha256}
                    or current[0].revision != changeset.get("base_revision")
                    or current[0].content_sha256 != changeset.get("base_sha256")
                    or metadata.get("document_version") != current[0].metadata.get("document_version", 0) + 1):
                raise ContractValidationError("named case correction base changed")
        else:
            raise ContractValidationError("named case effect is invalid")
        return {"candidate_id": candidate["candidate_id"], "candidate_revision": candidate["candidate_revision"],
                "content_sha256": changeset["result_sha256"], "proposed_text": body.strip(),
                "target": route["target_relative_path"], "source": {"coverage_case_id": f"coverage:{name}",
                    "absence_proof_id": candidate.get("absence_proof_id")},
                "base": {"revision": changeset["base_revision"]},
                "expected_policy_revision": changeset["policy_revision"],
                "expected_settings_revision": changeset["settings_revision"],
                "idempotency_key": changeset["idempotency_key"],
                "submitted_by": candidate.get("attribution", {}).get("submitted_by")}

    def _project_essence_from_local_owner(self, project_workspace: Path, summary: str, area: str):
        """Stage an exact charter summary through the ordinary Candidate lifecycle."""
        from .lesson_capture import build_project_essence_candidate
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner Essence staging is required")
        self._owner_settings_preflight(Path(project_workspace))
        project = Path(project_workspace).absolute()
        state = json.loads((project / "workspace.json").read_text(encoding="utf-8"))
        project_id = state.get("authority_id")
        project_root = self._root_for_authority(project_id)
        global_root = self._root_for_authority("user-global:source-access")
        if (project_root is None or global_root is None
                or project_root.resolve() != (project / "project").resolve()):
            raise ContractValidationError("linked Project Essence authority is unavailable")
        with authority_write_locks((project_root, global_root)):
            recover_pending_effects(project_root)
            authority = self._repository.bootstrap(project_id)
            global_authority = self._repository.bootstrap("user-global:source-access")
            if (not has_grant(authority, "principal:local-owner", "promote")
                    or not has_grant(global_authority, "principal:local-owner", "promote")
                    or authority.metadata.get("mode") != "read_write"):
                raise ContractValidationError("local Owner Essence authority changed")
            binding, current = self._current_project_concept(project_id, "principal:local-owner")
            if not current:
                raise ContractValidationError("canonical Project concept changed; register and bind its revision")
            artifact_id = f"memory:{project_id.replace(':', '-')}-essence-project"
            base = self._repository.read("curated_reference", project_id,
                                         {"authority_id": project_id, "artifact_id": artifact_id})
            operation_id = "op:project-essence:" + sha256(json.dumps(
                {"project": project_id, "summary": summary, "area": area,
                 "concept": binding["revision"], "base": base.content_sha256 if base else None},
                ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:24]
            candidate, changeset = build_project_essence_candidate(
                authority, summary, area, binding, operation_id, base)
            receipt_id = self._repository.apply("candidate_preview", project_id,
                {"authority_id": project_id, "operation_id": operation_id,
                 "candidate": candidate, "changeset": changeset})
            return {"status": "preview", "candidate_id": candidate["candidate_id"],
                    "review_preview": candidate["review_preview"], "receipt_id": receipt_id,
                    "message": "Exact Project concept summary staged; separate human review is required."}

    def _global_essence_from_local_owner(self, contribution_id: str,
                                         revision: str, content_sha256: str):
        """Stage one exact Feed summary for separate Global Owner review."""
        from .project_io import resolve_project_concept, read_curated_reference
        from .lesson_capture import build_global_essence_candidate, validate_project_essence
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner Global Essence curation is required")
        global_id = "user-global:source-access"
        global_root = self._root_for_authority(global_id)
        if global_root is None:
            raise ContractValidationError("Global Essence authority is unavailable")
        self._owner_settings_preflight(global_root.parent)
        contribution = self._repository.read("reuse_contribution", global_id,
            {"authority_id": global_id, "contribution_id": contribution_id})
        if (contribution is None or contribution.revision != revision
                or contribution.content_sha256 != content_sha256
                or contribution.metadata.get("knowledge_kind") != "project_essence"):
            raise ContractValidationError("exact Project Essence contribution is unavailable")
        project_id = contribution.metadata.get("source_authority_id")
        binding, project_authority, _, _, _ = resolve_project_concept(global_root.parent, project_id)
        project_root = Path(binding["project_workspace"]) / "project"
        with authority_write_locks((global_root, project_root)):
            authority = self._repository.bootstrap(global_id)
            if (authority.metadata.get("mode") != "read_write"
                    or not has_grant(authority, "principal:local-owner", "promote")
                    or not has_grant(project_authority, "principal:local-owner", "retrieve")):
                raise ContractValidationError("local Owner Global Essence authority changed")
            binding, current = self._current_project_concept(project_id, "principal:local-owner")
            if not current or contribution.metadata.get("source_concept_origin") != {
                    key: binding[key] for key in ("project_authority_id", "concept_id", "revision", "source_id",
                                             "source_link_id", "snapshot_sha256", "relative_path", "content_sha256")}:
                raise ContractValidationError("Project concept changed since contribution")
            source = read_curated_reference(project_root, authority_id=project_id,
                artifact_id=contribution.metadata["source_artifact_id"])
            if (source is None or source.revision != contribution.metadata["source_revision"]
                    or source.content_sha256 != contribution.metadata["source_content_sha256"]
                    or source.body != contribution.body):
                raise ContractValidationError("Project Essence changed since contribution")
            validate_project_essence(source)
            artifact_id = "memory:user-global-source-access-essence-" + project_id.removeprefix("project:")
            base = self._repository.read("curated_reference", global_id,
                {"authority_id": global_id, "artifact_id": artifact_id})
            candidate, changeset = build_global_essence_candidate(authority, contribution, binding, base)
            receipt_id = self._repository.apply("candidate_preview", global_id,
                {"authority_id": global_id, "operation_id": changeset["idempotency_key"],
                 "candidate": candidate, "changeset": changeset})
            return {"status": "preview", "candidate_id": candidate["candidate_id"],
                    "review_preview": candidate["review_preview"], "receipt_id": receipt_id,
                    "message": "Global Essence summary staged; separate human review is required."}

    def _named_connection_from_local_owner(self, workspace, authority_id, *, name, action="add", role=None,
                                           source_link_id=None, expected_sha256=None, apply=False):
        """Private Owner configuration seam; Contributor commands cannot invoke it."""
        from .project_io import change_named_connection
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner connection setup is required")
        self._owner_settings_preflight(Path(workspace))
        root = self._root_for_authority(authority_id)
        expected = Path(workspace) / ("project" if authority_id.startswith("project:") else "global")
        if root is None or root.resolve() != expected.resolve():
            raise ContractValidationError("connection workspace does not own this authority")

        def check_authority(authority, principal, link_id):
            if authority.metadata.get("mode") != "read_write" or not has_grant(authority, "principal:local-owner", "promote"):
                raise ContractValidationError("local Owner write authority is required for connections")
            if link_id is not None:
                controls = self._repository.progressive_controls(authority_id)
                links = [item for item in controls if item.metadata.get("source_link_id") == link_id
                         and item.metadata.get("lifecycle") == "accepted"]
                if len(links) != 1 or not source_access_allowed(links[0], principal):
                    raise ContractValidationError("selected Source Link is not explicitly shared with this connection")

        selected_role = (role or "contributor") if action == "add" else role
        try:
            capabilities = named_connection_capabilities(selected_role) if action == "add" else ()
        except ValueError as error:
            raise ContractValidationError(str(error)) from error
        return change_named_connection(root, authority_id, name=name, action=action, role=selected_role,
                                       capabilities=capabilities,
                                       source_link_id=source_link_id, expected_sha256=expected_sha256,
                                       apply=apply, check_authority=check_authority)

    def _settings_from_local_owner(self, workspace, authority_id: str, *, action: str,
                                   expected_sha256: str | None = None, apply: bool = False,
                                   recover: bool = False, updates: dict[str, str] | None = None,
                                   unset: tuple[str, ...] = ()):
        """Private fixed-path Settings inspection and governed empty-layer repair."""
        from .project_io import inspect_settings, change_settings_layer
        if self._identity_profile != "mvp-v1" or action not in {"inspect", "repair", "configure"}:
            raise ContractValidationError("local Owner Settings operation is required")
        root = self._root_for_authority(authority_id)
        expected = Path(workspace) / ("project" if authority_id.startswith("project:") else "global")
        if root is None or root.resolve() != expected.resolve():
            raise ContractValidationError("Settings workspace does not own this authority")
        if action == "inspect":
            if apply or recover or expected_sha256 is not None or updates or unset:
                raise ContractValidationError("Settings inspection is read-only")
            return inspect_settings(root, authority_id)
        authority = self._repository.bootstrap(authority_id)
        if not has_grant(authority, "principal:local-owner", "promote"):
            raise ContractValidationError("local Owner promote right is required for Settings repair")
        return change_settings_layer(root, authority_id, expected_sha256=expected_sha256,
                                     apply=apply, recover=recover, reset_empty=action == "repair",
                                     updates=updates, unset=unset)

    def _named_source_rights_from_local_owner(self, workspace, *, source_link_id, connection,
                                               action, expected_sha256=None, apply=False):
        from .project_io import change_named_source_reader
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner source-rights configuration is required")
        self._owner_settings_preflight(Path(workspace))
        expected = Path(workspace) / "global"
        root = self._root_for_authority("user-global:source-access")
        if root is None or root.resolve() != expected.resolve():
            raise ContractValidationError("source-rights workspace does not own Global authority")
        def check_owner(authority):
            if not has_grant(authority, "principal:local-owner", "promote"):
                raise ContractValidationError("local Owner promote right is required")
        def check_agent(authority, principal, role):
            try:
                grants = authority.metadata.get("actor_grants")
                return (isinstance(grants, dict)
                        and grants.get(principal) == list(named_connection_capabilities(role)))
            except ValueError:
                return False
        return change_named_source_reader(Path(workspace), source_link_id=source_link_id,
                                          connection=connection, action=action,
                                          expected_sha256=expected_sha256, apply=apply,
                                          check_owner=check_owner, check_agent=check_agent,
                                          rights_allowed=source_rights_allowed)

    def _list_named_source_rights_from_local_owner(self, workspace):
        from .project_io import list_named_source_rights
        if self._identity_profile != "mvp-v1":
            raise ContractValidationError("local Owner source-rights configuration is required")
        self._owner_settings_preflight(Path(workspace))
        root = self._root_for_authority("user-global:source-access")
        if root is None or root.resolve() != (Path(workspace) / "global").resolve():
            raise ContractValidationError("source-rights workspace does not own Global authority")
        def check_owner(authority):
            if not has_grant(authority, "principal:local-owner", "promote"):
                raise ContractValidationError("local Owner promote right is required")
        return list_named_source_rights(Path(workspace),
                                        controls=self._repository.progressive_controls("user-global:source-access"),
                                        check_owner=check_owner)

    def _source_reference_refresh_from_local_owner(self, workspace, *, name, area, text,
                                                    source_link_id, source_file, query, cursor,
                                                    expected_revision, expected_sha256):
        """Stage one exact Owner re-preview; all raw evidence is replayed by Core."""
        if (self._identity_profile != "mvp-v1"
                or self._root_for_authority("user-global:source-access") is None
                or self._root_for_authority("user-global:source-access").resolve()
                   != (Path(workspace) / "global").resolve()):
            raise ContractValidationError("local Owner Global workspace is required")
        self._owner_settings_preflight(Path(workspace))
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 80:
            raise ContractValidationError("reference name is invalid")
        active_id = "user-global:source-access"
        search = {"coverage_case_id": "coverage:source-access-originals", "query": query,
                  "source_areas": ["."], "source_cursor": cursor, "source_link_id": source_link_id}
        principal = {"principal_id": "principal:local-owner", "assurance": "local_owner",
                     "reported": {}, "adapter_observed": {}}
        command = {"schema": "owledge.core-command/1", "operation": "progressive_retrieve",
                   "operation_id": "op:reference-refresh-search:" + sha256(json.dumps(search, sort_keys=True).encode()).hexdigest()[:24],
                   "principal": principal, "active_authority_id": active_id, "target_authority_id": active_id,
                   "expected_revisions": {}, "payload": search}
        found = self._execute_from_local_owner(command)
        if found.get("status") not in {"ok", "incomplete"}:
            return {"status": "needs_attention", "details": found}
        hits = [hit for hit in found.get("data", {}).get("raw_hits", []) if hit.get("relative_path") == source_file]
        if len(hits) != 1:
            return {"status": "needs_attention", "message": "Choose the exact file on this bounded source page.",
                    "continuation": found.get("data", {}).get("continuation")}
        hit = hits[0]
        payload = {"source_search": search, "source_relative_path": source_file,
                   "source_content_sha256": hit["content_sha256"], "source_excerpt": hit["snippet"],
                   "source_binding": hit["source_binding"], "proposed_text": text,
                   "curation_slug": name, "knowledge_area": area,
                   "correction": {"artifact_id": f"memory:user-global-source-access-source-{name}",
                                  "revision": expected_revision, "content_sha256": expected_sha256}}
        command.update(operation="source_reference_refresh", payload=payload,
                       operation_id="op:reference-refresh:" + sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:24])
        result = self._execute_from_local_owner(command)
        if result.get("status") != "ok":
            return {"status": "needs_attention", "details": result}
        data = result["data"]
        return {"status": "preview", "name": name, "candidate_id": data["candidate_id"],
                "candidate_revision": data["candidate_revision"], "review_preview": data["review_preview"],
                "source_link_id": source_link_id, "relative_path": source_file,
                "message": "Exact source refresh staged for separate Owner review."}

    def _legacy_source_rights_from_local_owner(self, workspace, *, expected_sha256=None,
                                               apply=False, recover=False):
        from .project_io import migrate_legacy_source_rights
        root = self._root_for_authority("user-global:source-access")
        if (self._identity_profile != "mvp-v1" or root is None
                or root.resolve() != (Path(workspace) / "global").resolve()):
            raise ContractValidationError("local Owner Knowledge workspace is required")
        self._owner_settings_preflight(Path(workspace))
        return migrate_legacy_source_rights(Path(workspace), expected_sha256=expected_sha256,
                                            apply=apply, recover=recover)

    def _inspect_legacy_source_from_local_owner(self, workspace, *, name, revision=None):
        from .project_io import bootstrap_authority, read_curated_reference, migration_legacy_reference_allowed
        root = self._root_for_authority("user-global:source-access")
        if (self._identity_profile != "mvp-v1" or root is None
                or root.resolve() != (Path(workspace) / "global").resolve()
                or not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)):
            raise ContractValidationError("exact local Owner legacy reference handle is required")
        authority = bootstrap_authority(root, "user-global:source-access")
        if (not has_grant(authority, "principal:local-owner", "promote")
                or authority.metadata.get("rights_migration_epoch") is None):
            raise ContractValidationError("Owner-approved rights migration is required")
        artifact_id = f"memory:user-global-source-access-source-{name}"
        record = read_curated_reference(root, authority_id="user-global:source-access",
                                        artifact_id=artifact_id, revision=revision)
        if record is None or record.metadata.get("knowledge_kind") != "reference":
            raise ContractValidationError("legacy reference was not found")
        if not migration_legacy_reference_allowed(Path(root), record):
            raise ContractValidationError("reference is not bound to the historical migration inventory")
        if self._epoch_derived_allowed(record):
            raise ContractValidationError("reference is current; use normal read")
        return {"status": "ready", "name": name, "artifact_id": artifact_id,
                "revision": record.revision, "content_sha256": record.content_sha256,
                "text": record.body.strip(), "source": record.metadata.get("source_evidence"),
                "legacy": True, "message": "Historical Owner-only inspection; refresh and separate review are required."}

    def _lifecycle_identity_seed(self, operation_id: str) -> str | None:
        """Select compatibility explicitly; command syntax has no authority here."""

        return None if self._identity_profile == "poc-v1" else operation_id

    def _assess_coverage(
        self,
        documents: tuple[ManagedMarkdown, ...],
        coverage_case_id: str,
    ) -> CoverageOutcome | None:
        try:
            reference = self._reference_retriever.assess(documents, coverage_case_id)
        except TimeoutError:
            return CoverageOutcome(
                {
                    "schema": "owledge.coverage-assessment/1",
                    "assessment_id": f"assessment:resource-exhausted:{coverage_case_id}",
                    "assessment": "resource_exhausted",
                    "coverage_case_id": coverage_case_id,
                    "evidence": {},
                    "selected_artifact_ids": [],
                    "source_health": [],
                    "scan_complete": False,
                    "budget": {
                        "outcome": "exceeded",
                        "exhausted_by": "time",
                    },
                    "diagnostics": [],
                    "gap_effect_allowed": False,
                    "reference_retriever_revision": self._reference_retriever.revision,
                },
                None,
                None,
            )
        def bind_settings(outcome: CoverageOutcome | None) -> CoverageOutcome | None:
            # Preserve the frozen PoC proof wire format; ordinary MVP journeys
            # bind the complete applicable Settings snapshot.
            if self._identity_profile != "mvp-v1" or outcome is None or outcome.absence_proof is None:
                return outcome
            authority_id = outcome.absence_proof.get("active_authority_id")
            root = self._root_for_authority(authority_id) if isinstance(authority_id, str) else None
            if root is None:
                return outcome
            from .project_io import settings_snapshot_token
            proof = {**outcome.absence_proof,
                     "settings_snapshot_sha256": settings_snapshot_token(root, authority_id)}
            proof_id = "proof:sha256:" + sha256(json.dumps(
                proof, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            return CoverageOutcome({**outcome.assessment, "absence_proof_id": proof_id},
                                   proof, outcome.safe_topic)

        if self._derived_retriever is None or reference is None:
            return bind_settings(reference)
        try:
            derived = self._derived_retriever.assess(documents, coverage_case_id)
        except Exception:
            derived = None
        comparable_fields = (
            "assessment",
            "coverage_case_id",
            "coverage_case_revision",
            "source_snapshot_id",
            "evidence",
            "selected_artifact_ids",
        )
        if (
            isinstance(derived, CoverageOutcome)
            and all(
                derived.assessment.get(field) == reference.assessment.get(field)
                for field in comparable_fields
            )
        ):
            return bind_settings(reference)
        failed = dict(reference.assessment)
        failed.update(
            {
                "assessment": "retrieval_miss",
                "evidence": {},
                "selected_artifact_ids": [],
                "diagnostics": [
                    {
                        "reason_code": "retrieval_miss",
                        "reference_artifact_ids": list(
                            reference.assessment.get("selected_artifact_ids", [])
                        ),
                        "reference_retriever_revision": self._reference_retriever.revision,
                        "derived_retriever_revision": getattr(
                            self._derived_retriever,
                            "revision",
                            "unknown",
                        ),
                    }
                ],
                "gap_effect_allowed": False,
            }
        )
        failed.pop("absence_proof_id", None)
        return CoverageOutcome(failed, None, reference.safe_topic)

    @staticmethod
    def _result(
        status: str,
        reason_code: str,
        summary: str,
        next_action: str,
        data: object,
        receipt_id: str | None = None,
    ) -> dict[str, object]:
        return {
            "schema": "owledge.core-result/1",
            "status": status,
            "reason_code": reason_code,
            "summary": summary,
            "next_action": next_action,
            "data": data,
            "receipt_id": receipt_id,
        }

    @staticmethod
    def _authority_document(
        documents: tuple[ManagedMarkdown, ...],
    ) -> ManagedMarkdown | None:
        matches = [
            item
            for item in documents
            if item.metadata.get("schema") == "owledge.authority-unit/1"
        ]
        return matches[0] if len(matches) == 1 else None

    @staticmethod
    def _paths_overlap(left: Path, right: Path) -> bool:
        left_value = os.path.normcase(str(left))
        right_value = os.path.normcase(str(right))
        try:
            common = os.path.commonpath((left_value, right_value))
        except ValueError:
            return False
        return common in {left_value, right_value}

    def _setup_roots(
        self,
        source: str,
    ) -> tuple[Path, Path] | None:
        if self._setup_workspace is None or self._source_connector_factory is None:
            return None
        try:
            source_candidate = Path(source).absolute()
            source_root = source_candidate.resolve(strict=True)
            workspace = self._setup_workspace.resolve(strict=True)
            managed_roots = tuple(path.resolve(strict=True) for path in self._roots.values())
        except (FileNotFoundError, OSError):
            return None
        protected = (source_root, workspace, *managed_roots)
        if not source_root.is_dir() or not workspace.is_dir():
            return None
        if self._paths_overlap(source_root, workspace):
            return None
        if any(
            self._paths_overlap(candidate, managed)
            for candidate in (source_root, workspace)
            for managed in managed_roots
        ):
            return None
        if len({os.path.normcase(str(path)) for path in protected}) != len(protected):
            return None
        return source_candidate, workspace

    def _preview_source_setup_from_local_owner(
        self,
        source: str,
        principal_id: str,
    ) -> dict[str, object]:
        """Private setup preview; only the source-local Owner adapter can call it."""

        self._setup_pending = None
        if self._identity_profile != "mvp-v1":
            return self._result(
                "denied",
                "owner_assurance_required",
                "Lokale Owner-Bestätigung ist erforderlich.",
                "use_local_owner",
                {},
            )
        roots = self._setup_roots(source)
        if roots is None or self._source_connector_factory is None:
            return self._result(
                "invalid",
                "source_boundary_invalid",
                "Quelle und Ziel müssen getrennte lokale Verzeichnisse sein.",
                "choose_separate_directories",
                {},
            )
        source_root, _workspace = roots
        try:
            snapshot = self._source_connector_factory(source_root).scan()
        except SourceSnapshotError as error:
            status = (
                "invalid"
                if error.reason_code in {"source_ambiguous", "path_escape"}
                else "recovery_required"
            )
            return self._result(
                status,
                error.reason_code,
                "Die Markdown-Quelle konnte nicht sicher gelesen werden.",
                "repair_or_choose_source",
                {},
            )
        self._setup_pending = snapshot
        return self._result(
            "preview",
            "setup_preview_ready",
            "Die unveränderliche Quellkopie ist bereit zur Bestätigung.",
            "apply_or_reject",
            {
                "document_count": len(snapshot.files),
                "size_bytes": snapshot.size_bytes,
                "target_name": source_snapshot_target_name(snapshot),
            },
        )

    def _apply_source_setup_from_local_owner(
        self,
        principal_id: str,
    ) -> dict[str, object]:
        """Private setup effect with mandatory rescan and byte-bound apply."""

        if self._identity_profile != "mvp-v1":
            return self._result(
                "denied",
                "owner_assurance_required",
                "Lokale Owner-Bestätigung ist erforderlich.",
                "use_local_owner",
                {},
            )
        pending = self._setup_pending
        if pending is None:
            return self._result(
                "invalid",
                "setup_preview_required",
                "Vor dem Schreiben ist eine aktuelle Vorschau erforderlich.",
                "preview_source",
                {},
            )
        if self._source_connector_factory is None or self._setup_workspace is None:
            return self._result(
                "invalid",
                "setup_port_unavailable",
                "Die lokale Setup-Schnittstelle ist nicht konfiguriert.",
                "configure_setup",
                {},
            )
        try:
            current = self._source_connector_factory(pending.source_root).scan()
        except SourceSnapshotError as error:
            self._setup_pending = None
            if error.reason_code == "source_ambiguous":
                return self._result(
                    "stale",
                    "source_snapshot_mismatch",
                    "Die Quelle hat sich seit der Vorschau geändert.",
                    "preview_again",
                    {},
                )
            return self._result(
                "recovery_required",
                error.reason_code,
                "Die Quelle ist seit der Vorschau nicht mehr sicher lesbar.",
                "preview_again",
                {},
            )
        if current != pending:
            self._setup_pending = None
            return self._result(
                "stale",
                "source_snapshot_mismatch",
                "Die Quelle hat sich seit der Vorschau geändert.",
                "preview_again",
                {},
            )
        operation_id = f"op:setup:{pending.snapshot_sha256}"
        try:
            data, receipt_id = materialize_source_snapshot(
                self._setup_workspace,
                pending,
                operation_id,
                principal_id,
            )
        except (ContractValidationError, OSError):
            return self._result(
                "recovery_required",
                "target_state_invalid",
                "Das Setup-Ziel ist unvollständig oder wurde verändert.",
                "inspect_disposable_target",
                {},
            )
        self._setup_pending = None
        return self._result(
            "ok",
            "source_snapshot_ready",
            "Die unveränderliche Quellkopie wurde erstellt.",
            "continue_setup",
            data,
            receipt_id,
        )

    def _cancel_source_setup_from_local_owner(
        self,
        principal_id: str,
    ) -> dict[str, object]:
        if self._identity_profile != "mvp-v1":
            return self._result(
                "denied",
                "owner_assurance_required",
                "Lokale Owner-Bestätigung ist erforderlich.",
                "use_local_owner",
                {},
            )
        self._setup_pending = None
        return self._result(
            "ok",
            "setup_cancelled",
            "Die Setup-Vorschau wurde verworfen.",
            "none",
            {},
        )

    def _source_lineage_allowed(self, document: ManagedMarkdown,
                                controls: tuple[ManagedMarkdown, ...], principal_id: str) -> bool:
        lineage = document.metadata.get("source_lineage")
        if not isinstance(lineage, list) or not lineage:
            return False
        for entry in lineage:
            if not isinstance(entry, dict) or set(entry) != {"artifact_id", "authority_id", "binding"}:
                return False
            derived_authority_id = entry.get("authority_id")
            binding = entry.get("binding")
            raw_source_id = binding.get("linked_authority_id") if isinstance(binding, dict) else None
            if not (isinstance(entry.get("artifact_id"), str) and isinstance(derived_authority_id, str)
                    and isinstance(raw_source_id, str)
                    and source_rights_allowed(binding.get("source_access"), principal_id)):
                return False
            if derived_authority_id == document.authority_id:
                linked_controls = controls
            else:
                project_links = [item for item in controls
                                 if item.metadata.get("schema") == "owledge.knowledge-source-link/1"
                                 and item.metadata.get("lifecycle") == "accepted"
                                 and item.metadata.get("linked_authority_id") == derived_authority_id
                                 and isinstance(item.metadata.get("grants"), list)
                                 and "retrieve" in item.metadata["grants"]]
                if not project_links or self._root_for_authority(derived_authority_id) is None:
                    return False
                try:
                    if not has_grant(self._repository.bootstrap(derived_authority_id), principal_id, "retrieve"):
                        return False
                    linked_controls = self._repository.snapshot(derived_authority_id)
                except (ContractValidationError, OSError):
                    return False
            links = [item for item in linked_controls
                     if item.metadata.get("schema") == "owledge.knowledge-source-link/1"
                     and item.artifact_id == binding.get("link_artifact_id")
                     and item.authority_id == derived_authority_id
                     and item.metadata.get("linked_authority_id") == raw_source_id
                     and item.metadata.get("lifecycle") == "accepted"
                     and isinstance(item.metadata.get("grants"), list)
                     and "discover" in item.metadata["grants"]
                     and "keyword_retrieve" in item.metadata["grants"]]
            if len(links) != 1 or not source_access_allowed(links[0], principal_id):
                return False
        return True

    def _current_project_concept(self, project_id: str, principal_id: str):
        """Check reciprocal Project ownership and current raw Source Link rights."""
        from .project_io import resolve_project_concept
        global_root = self._root_for_authority("user-global:source-access")
        if global_root is None:
            raise ContractValidationError("linked Global authority is unavailable")
        binding, project_authority, global_authority, link, source_path = resolve_project_concept(
            global_root.parent, project_id)
        if (not has_grant(project_authority, principal_id, "retrieve")
                or not has_grant(global_authority, principal_id, "retrieve")
                or not source_access_allowed(link, principal_id)):
            raise ContractValidationError("Project concept is outside current rights")
        if self._source_connector_factory is None:
            raise ContractValidationError("safe concept source connector is unavailable")
        try:
            snapshot = self._source_connector_factory(source_path).scan()
            current = (snapshot.source_id == binding["source_id"]
                       and snapshot.snapshot_sha256 == binding["snapshot_sha256"]
                       and len(snapshot.files) == 1
                       and snapshot.files[0].relative_path == binding["relative_path"]
                       and snapshot.files[0].content_sha256 == binding["content_sha256"])
        except (SourceSnapshotError, OSError):
            current = False
        return binding, current

    def _essence_current(self, document: ManagedMarkdown, principal_id: str) -> bool:
        """A summary is current only with its Project head and live source rights."""
        from .lesson_capture import essence_origin, validate_project_essence, validate_global_essence
        from .project_io import read_curated_reference, resolve_project_concept
        try:
            global_record = document.authority_id == "user-global:source-access"
            if global_record:
                validate_global_essence(document)
                origin = document.metadata["project_origin"]
                project_id = origin["authority_id"]
            else:
                validate_project_essence(document)
                project_id = document.authority_id
            binding, current = self._current_project_concept(project_id, principal_id)
            if not current or document.metadata.get("concept_origin") != essence_origin(binding):
                return False
            global_root = self._root_for_authority("user-global:source-access")
            binding, _, _, _, _ = resolve_project_concept(global_root.parent, project_id)
            head_root = (global_root if global_record else Path(binding["project_workspace"]) / "project")
            head = read_curated_reference(head_root, authority_id=document.authority_id,
                                          artifact_id=document.artifact_id)
            if head is None or head.revision != document.revision or head.content_sha256 != document.content_sha256:
                return False
            if not global_record:
                return True
            contribution = self._repository.read("reuse_contribution", "user-global:source-access",
                {"authority_id": "user-global:source-access", "contribution_id": origin["contribution_id"]})
            if (contribution is None or contribution.revision != origin["contribution_revision"]
                    or contribution.content_sha256 != origin["contribution_sha256"]
                    or not self._essence_contribution_current(contribution, principal_id)):
                return False
            source = read_curated_reference(Path(binding["project_workspace"]) / "project",
                authority_id=project_id, artifact_id=origin["artifact_id"])
            return (source is not None and source.revision == origin["revision"]
                    and source.content_sha256 == origin["content_sha256"]
                    and source.body == document.body and self._essence_current(source, principal_id))
        except (ContractValidationError, OSError, TypeError, ValueError, KeyError):
            return False

    def _essence_contribution_current(self, contribution: ManagedMarkdown, principal_id: str) -> bool:
        from .source_curation import valid_reuse_contribution
        from .lesson_capture import essence_origin
        from .project_io import read_curated_reference, resolve_project_concept
        if (contribution.metadata.get("knowledge_kind") != "project_essence"
                or not valid_reuse_contribution(contribution, "reuse_feed")):
            return False
        try:
            project_id = contribution.metadata["source_authority_id"]
            binding, current = self._current_project_concept(project_id, principal_id)
            if not current or contribution.metadata.get("source_concept_origin") != essence_origin(binding):
                return False
            global_root = self._root_for_authority("user-global:source-access")
            binding, _, _, _, _ = resolve_project_concept(global_root.parent, project_id)
            source = read_curated_reference(Path(binding["project_workspace"]) / "project",
                authority_id=project_id, artifact_id=contribution.metadata["source_artifact_id"])
            return (source is not None and source.revision == contribution.metadata["source_revision"]
                    and source.content_sha256 == contribution.metadata["source_content_sha256"]
                    and source.body == contribution.body and self._essence_current(source, principal_id))
        except (ContractValidationError, OSError, TypeError, ValueError, KeyError):
            return False

    def _source_reference_allowed(self, document: ManagedMarkdown, controls: tuple[ManagedMarkdown, ...], principal_id: str,
                                  *, require_epoch: bool = True) -> bool:
        if require_epoch and not self._epoch_derived_allowed(document):
            return False
        if (document.metadata.get("knowledge_kind") == "project_essence"
                and document.metadata.get("source_trust") == "reviewed"):
            return self._essence_current(document, principal_id)
        if "source_lineage" in document.metadata and not self._source_lineage_allowed(document, controls, principal_id):
            return False
        source_identity = document.artifact_id.startswith(f"memory:{document.authority_id.replace(':', '-')}-source-")
        if document.metadata.get("knowledge_kind") != "reference":
            return not source_identity
        if not source_identity and "source_evidence" not in document.metadata:
            return True
        evidence = document.metadata.get("source_evidence")
        binding = evidence.get("binding") if isinstance(evidence, dict) else None
        if not isinstance(binding, dict):
            return False
        if not source_rights_allowed(binding.get("source_access"), principal_id):
            return False
        links = [item for item in controls
                 if item.metadata.get("schema") == "owledge.knowledge-source-link/1"
                 and item.artifact_id == binding.get("link_artifact_id")
                 and item.authority_id == document.authority_id
                 and item.metadata.get("linked_authority_id") == binding.get("linked_authority_id")
                 and item.metadata.get("lifecycle") == "accepted"
                 and isinstance(item.metadata.get("grants"), list)
                 and "keyword_retrieve" in item.metadata.get("grants", [])
                 and "discover" in item.metadata.get("grants", [])]
        return len(links) == 1 and source_access_allowed(links[0], principal_id)

    def _epoch_derived_allowed(self, document: ManagedMarkdown) -> bool:
        root = self._root_for_authority(document.authority_id)
        if root is None:
            return False
        try:
            from .project_io import migration_derived_allowed
            return migration_derived_allowed(Path(root), document)
        except (ContractValidationError, OSError, TypeError, ValueError):
            return False

    def _authorized_bundle_selection(self, active_id: str, principal_id: str,
                                     active_documents: tuple[ManagedMarkdown, ...],
                                     selected_ids: list[str], source_link_id: str | None = None) -> list[ManagedMarkdown] | None:
        """Resolve issued selections through current authority and source grants."""
        available = {item.artifact_id: item for item in active_documents
                     if self._source_reference_allowed(item, active_documents, principal_id)}
        if any(item not in available for item in selected_ids):
            source_links = [item for item in active_documents
                            if item.metadata.get("schema") == "owledge.knowledge-source-link/1"
                            and item.metadata.get("lifecycle") == "accepted"
                            and (source_link_id is None or item.metadata.get("source_link_id") == source_link_id)
                            and isinstance(item.metadata.get("grants"), list)
                            and "retrieve" in item.metadata["grants"]]
            for link in source_links:
                linked_id = link.metadata.get("linked_authority_id")
                if not isinstance(linked_id, str) or self._root_for_authority(linked_id) is None:
                    continue
                try:
                    foreign_authority = self._repository.bootstrap(linked_id)
                    if not has_grant(foreign_authority, principal_id, "retrieve"):
                        continue
                    foreign_documents = self._repository.snapshot(linked_id)
                except (ContractValidationError, OSError):
                    continue
                available.update({item.artifact_id: item for item in foreign_documents
                                  if item.metadata.get("lifecycle") == "accepted"
                                  and self._source_reference_allowed(item, foreign_documents, principal_id)})
        if any(item not in available for item in selected_ids):
            return None
        return self._reference_retriever.select(tuple(available.values()), tuple(selected_ids))

    @staticmethod
    def _issued_bundle_revisions_match(selected: list[ManagedMarkdown], revisions: dict[str, str]) -> bool:
        return (len(selected) == len(revisions)
                and {item.artifact_id: item.revision for item in selected} == revisions)

    @staticmethod
    def _selected_source_lineage(selected: list[ManagedMarkdown]) -> list[dict[str, object]]:
        return [{"artifact_id": item.artifact_id, "authority_id": item.authority_id,
                 "binding": item.metadata["source_evidence"]["binding"]}
                for item in selected
                if item.metadata.get("knowledge_kind") == "reference"
                and isinstance(item.metadata.get("source_evidence"), dict)
                and isinstance(item.metadata["source_evidence"].get("binding"), dict)]

    def _bundle_candidate_source_allowed(self, active_id: str, candidate: dict, changeset: dict,
                                         active_documents: tuple[ManagedMarkdown, ...]) -> bool:
        if candidate.get("candidate_kind") is not None:
            return True
        if "bundle_selection" not in candidate:
            return "bundle_selection" not in changeset and "source_lineage" not in changeset
        selection = candidate.get("bundle_selection")
        if not isinstance(selection, dict) or selection != changeset.get("bundle_selection"):
            return False
        lineage = candidate.get("source_lineage")
        if not isinstance(lineage, list) or not lineage or lineage != changeset.get("source_lineage"):
            return False
        try:
            result_metadata, _ = parse_markdown_frontmatter(str(changeset.get("result_document")))
        except (ContractValidationError, TypeError, ValueError):
            return False
        if result_metadata.get("source_lineage") != lineage:
            return False
        bundle_id = selection.get("bundle_id")
        revisions = selection.get("selected_revisions")
        attribution = candidate.get("attribution")
        submitter = attribution.get("submitted_by") if isinstance(attribution, dict) else None
        if not (isinstance(bundle_id, str) and isinstance(submitter, str)
                and isinstance(revisions, dict) and revisions
                and all(isinstance(key, str) and isinstance(value, str)
                        for key, value in revisions.items())):
            return False
        try:
            original_bundle = self._repository.read("bundle", active_id, {"bundle_id": bundle_id})
            original_metadata, _ = parse_markdown_frontmatter(original_bundle)
            if (original_metadata.get("authority_id") != active_id
                    or original_metadata.get("selected_revisions") != revisions
                    or original_metadata.get("selected_source_lineage") != lineage):
                return False
            selected = self._authorized_bundle_selection(active_id, submitter, active_documents, list(revisions))
            return (selected is not None
                    and self._issued_bundle_revisions_match(selected, revisions)
                    and self._selected_source_lineage(selected) == lineage)
        except (ContractValidationError, OSError, TypeError, ValueError):
            return False

    def _candidate_source_allowed(self, candidate: dict, changeset: dict,
                                  active_id: str, principal_id: str) -> bool:
        if candidate.get("candidate_kind") in {"project_essence", "global_essence"}:
            try:
                from .lesson_capture import essence_origin
                metadata, _ = parse_markdown_frontmatter(str(changeset.get("result_document")))
                project_id = (active_id if candidate.get("candidate_kind") == "project_essence"
                              else metadata["project_origin"]["authority_id"])
                binding, current = self._current_project_concept(project_id, principal_id)
                return current and metadata.get("concept_origin") == essence_origin(binding)
            except (ContractValidationError, OSError, TypeError, ValueError):
                return False
        if candidate.get("candidate_kind") != "source_curation":
            return True
        effects = changeset.get("effects")
        result = changeset.get("result_document")
        if not isinstance(effects, list) or len(effects) != 1 or not isinstance(effects[0], dict) or not isinstance(result, str):
            return False
        try:
            from .project_io import verify_source_refresh_issuance
            verify_source_refresh_issuance(self._root_for_authority(active_id), candidate, changeset)
            document = parse_managed_markdown(str(effects[0].get("relative_path")), result)
            controls = self._repository.progressive_controls(active_id)
            if not self._source_reference_allowed(document, controls, principal_id, require_epoch=False):
                return False
            evidence = document.metadata.get("source_evidence")
            binding = evidence.get("binding") if isinstance(evidence, dict) else None
            if (not isinstance(binding, dict) or not isinstance(binding.get("snapshot"), dict)
                    or set(binding["snapshot"]) != {"artifact_id", "revision", "sha256", "snapshot_sha256"}):
                return False
            links = [item for item in controls if item.artifact_id == binding.get("link_artifact_id")
                     and item.metadata.get("linked_authority_id") == binding.get("linked_authority_id")]
            if (len(links) != 1 or links[0].revision != binding.get("link_revision")
                    or links[0].content_sha256 != binding.get("link_sha256")
                    or links[0].metadata.get("source_access") != binding.get("source_access")):
                return False
            snapshot = self._repository.raw_keyword_snapshot(binding["linked_authority_id"], query="",
                max_documents=1, max_bytes=8_388_608, max_matches=1)
            manifest = snapshot.get("manifest")
            return isinstance(manifest, dict) and all(
                manifest.get(key) == value for key, value in binding.get("snapshot", {}).items())
        except (ContractValidationError, OSError, KeyError, TypeError, ValueError):
            return False

    def _run_progressive_retrieval(
        self,
        *,
        active_id: str,
        principal_id: str,
        active_documents: tuple[ManagedMarkdown, ...],
        payload: dict[str, object],
    ) -> dict[str, object]:
        if not active_id.startswith("user-global:"):
            return self._result(
                "denied",
                "access_denied",
                "Progressive global retrieval requires the active User-Global authority.",
                "Use the global retrieval profile or the ordinary Project hot path.",
                {},
            )
        registries = [
            item
            for item in active_documents
            if item.metadata.get("schema")
            == "owledge.progressive-retrieval-registry/1"
            and item.metadata.get("lifecycle") == "accepted"
            and item.metadata.get("processing_layer") == "condensed"
            and item.metadata.get("source_trust") == "internal"
        ]
        coverage_case_id = payload.get("coverage_case_id")
        query = payload.get("query")
        if (
            len(registries) != 1
            or not isinstance(coverage_case_id, str)
            or not isinstance(query, str)
            or not query.strip()
        ):
            return self._result(
                "invalid",
                "coverage_case_invalid",
                "The progressive Coverage Case is absent or ambiguous.",
                "Choose one accepted case from the global registry.",
                {},
            )
        cases = registries[0].metadata.get("coverage_cases")
        case = cases.get(coverage_case_id) if isinstance(cases, dict) else None
        progressive_order = (
            "curated",
            "inbox",
            "reuse_feed",
            "linked_project",
            "raw_keyword",
        )
        if not (
            isinstance(case, dict)
            and case.get("lifecycle") == "accepted"
            and isinstance(case.get("revision"), str)
            and isinstance(case.get("required_evidence"), list)
            and bool(case["required_evidence"])
            and all(isinstance(item, str) and item for item in case["required_evidence"])
            and len(case["required_evidence"]) == len(set(case["required_evidence"]))
            and isinstance(case.get("search_envelope"), list)
            and bool(case["search_envelope"])
            and all(item in progressive_order for item in case["search_envelope"])
            and len(case["search_envelope"]) == len(set(case["search_envelope"]))
            and tuple(case["search_envelope"])
            == tuple(sorted(case["search_envelope"], key=progressive_order.index))
            and case.get("evaluation_mode", "first_sufficient")
            in {"first_sufficient", "compare_stages"}
            and case.get("gap_admission") in {"disabled", "proof_required"}
            and (
                case.get("gap_admission") != "proof_required"
                or isinstance(case.get("safe_topic"), str)
                and bool(case.get("safe_topic"))
            )
        ):
            return self._result(
                "invalid",
                "coverage_case_invalid",
                "The progressive Coverage Case is not accepted or complete.",
                "Choose one accepted case from the global registry.",
                {},
            )
        source_links = case.get("source_links", {}) if isinstance(case, dict) else {}
        foreign_stages = {
            stage
            for stage in case.get("search_envelope", [])
            if stage in {"linked_project", "raw_keyword"}
        } if isinstance(case, dict) else set()
        if not (
            isinstance(source_links, dict)
            and set(source_links) == foreign_stages
            and all(
                isinstance(values, list)
                and values
                and all(isinstance(value, str) and value for value in values)
                and len(values) == len(set(values))
                for values in source_links.values()
            )
        ):
            return self._result(
                "invalid",
                "coverage_case_invalid",
                "The progressive Coverage Case does not bind its foreign Source Links.",
                "Bind every foreign stage to exact authority-owned Source Link identities.",
                {},
            )
        try:
            filters = normalize_typed_filters(payload.get("filters", {}))
        except ContractValidationError:
            return self._result(
                "invalid",
                "filter_invalid",
                "The retrieval filters are not valid typed selections.",
                "Use non-empty lists for supported filter fields.",
                {},
            )
        max_records = 8
        max_bytes = 65_536
        source_page_documents = payload.get("source_page_documents", 256)
        source_areas = payload.get("source_areas", ["."])
        source_cursor = payload.get("source_cursor")
        discover_source_areas = payload.get("discover_source_areas", False)
        source_area_parent = payload.get("source_area_parent", ".")
        requested_source_link_id = payload.get("source_link_id")
        if (
            not isinstance(source_page_documents, int) or not 1 <= source_page_documents <= 256
            or not isinstance(source_areas, list) or not source_areas
            or any(not isinstance(area, str) or not area for area in source_areas)
            or source_cursor is not None and not isinstance(source_cursor, dict)
            or not isinstance(discover_source_areas, bool)
            or not isinstance(source_area_parent, str) or not source_area_parent
            or requested_source_link_id is not None and not isinstance(requested_source_link_id, str)
        ):
            return self._result("invalid", "source_search_invalid", "The targeted source search request is invalid.", "Use bounded Areas and a returned continuation cursor.", {})
        override = payload.get("budget_override", {})
        if not isinstance(override, dict):
            return self._result(
                "invalid",
                "budget_invalid",
                "The retrieval budget override is invalid.",
                "Use non-negative bounded record and byte limits.",
                {},
            )
        for key, ceiling in (("max_result_records", 8), ("max_result_bytes", 65_536)):
            value = override.get(key, ceiling)
            if not isinstance(value, int) or value < 0:
                return self._result(
                    "invalid",
                    "budget_invalid",
                    "The retrieval budget override is invalid.",
                    "Use non-negative bounded record and byte limits.",
                    {},
                )
            if key == "max_result_records":
                max_records = min(value, ceiling)
            else:
                max_bytes = min(value, ceiling)

        envelope = tuple(str(item) for item in case["search_envelope"])
        compare_stages = case.get("evaluation_mode") == "compare_stages"
        stage_documents: dict[str, tuple[ManagedMarkdown, ...]] = {}
        link_records = [
            item
            for item in active_documents
            if item.metadata.get("schema") == "owledge.knowledge-source-link/1"
        ]
        empty_data = {
            "stage": None,
            "selected_artifact_ids": [],
            "excluded_artifact_ids": [],
            "citation_artifact_ids": [],
            "gap_effect_allowed": False,
        }
        proof_context: dict[str, object] = {
            "authority": {
                "artifact_id": next(
                    (
                        item.artifact_id
                        for item in active_documents
                        if item.metadata.get("schema") == "owledge.authority-unit/1"
                    ),
                    None,
                ),
                "revision": next(
                    (
                        item.revision
                        for item in active_documents
                        if item.metadata.get("schema") == "owledge.authority-unit/1"
                    ),
                    None,
                ),
                "policy_revision": next(
                    (
                        item.metadata.get("policy_revision")
                        for item in active_documents
                        if item.metadata.get("schema") == "owledge.authority-unit/1"
                    ),
                    None,
                ),
                "settings_revision": next(
                    (
                        item.metadata.get("settings_revision")
                        for item in active_documents
                        if item.metadata.get("schema") == "owledge.authority-unit/1"
                    ),
                    None,
                ),
            },
            "registry": {
                "artifact_id": registries[0].artifact_id,
                "revision": registries[0].revision,
                "sha256": registries[0].content_sha256,
            },
            "coverage_case_id": coverage_case_id,
            "coverage_case_revision": case["revision"],
            "evaluation_mode": case.get("evaluation_mode", "first_sufficient"),
            "budget": {
                "max_result_records": max_records,
                "max_result_bytes": max_bytes,
            },
            "sources": [],
        }
        assessed: dict[str, object] = {}
        observed_stage_ids: set[str] = set()
        scan_documents = 0
        scan_bytes = 0
        scan_metadata_entries = 0
        scan_metadata_dirs = 0
        raw_continuation: object = None
        raw_area_page: list[str] = []
        raw_progress: dict[str, object] = {}
        raw_unreadable_files: list[dict[str, str]] = []
        restricted_evidence_present = False
        for index, stage in enumerate(envelope):
            stage_document_limit = min(256, 500 - scan_documents)
            stage_byte_limit = min(8_388_608, 16_777_216 - scan_bytes)
            stage_scan_documents = 0
            stage_scan_bytes = 0
            if stage in {"curated", "inbox", "reuse_feed"}:
                try:
                    local_snapshot = self._repository.progressive_stage_snapshot(
                        active_id,
                        stage,
                        max_documents=stage_document_limit,
                        max_bytes=stage_byte_limit,
                    )
                except (ContractValidationError, OSError):
                    return self._result(
                        "recovery_required",
                        "source_unavailable",
                        "The requested global retrieval stage could not be read safely.",
                        "Repair only that stage before retrying it.",
                        empty_data,
                    )
                local_stage = local_snapshot.get("documents")
                if not isinstance(local_stage, tuple):
                    return self._result("invalid", "retrieval_contract_invalid", "The staged repository result is invalid.", "Repair the repository port.", empty_data)
                if local_snapshot.get("exhausted") is True:
                    return self._result(
                        "incomplete",
                        "resource_exhausted",
                        "The bounded progressive stage scan budget was exhausted.",
                        "Narrow the stage or resume with a smaller authority-owned scope.",
                        {
                            **empty_data,
                            "budget_used": {
                                "records": scan_documents + int(local_snapshot.get("documents_scanned", 0)),
                                "bytes": scan_bytes + int(local_snapshot.get("bytes_scanned", 0)),
                                "metadata_entries_examined": scan_metadata_entries + int(local_snapshot.get("metadata_entries_examined", 0)),
                                "metadata_directories_examined": scan_metadata_dirs + int(local_snapshot.get("metadata_directories_examined", 0)),
                                "metadata_entry_limit": local_snapshot.get("metadata_entry_limit", 4096),
                            },
                        },
                    )
                scan_documents += int(local_snapshot.get("documents_scanned", 0))
                scan_bytes += int(local_snapshot.get("bytes_scanned", 0))
                scan_metadata_entries += int(local_snapshot.get("metadata_entries_examined", 0))
                scan_metadata_dirs += int(local_snapshot.get("metadata_directories_examined", 0))
                stage_scan_documents += int(local_snapshot.get("documents_scanned", 0))
                stage_scan_bytes += int(local_snapshot.get("bytes_scanned", 0))
                if stage == "curated":
                    restricted_evidence_present = restricted_evidence_present or any(
                        not self._source_reference_allowed(item, active_documents, principal_id) for item in local_stage)
                    local_stage = tuple(item for item in local_stage
                                        if self._source_reference_allowed(item, active_documents, principal_id))
                if stage == "reuse_feed":
                    local_stage = tuple(item for item in local_stage if
                        item.metadata.get("knowledge_kind") != "project_essence"
                        or self._essence_contribution_current(item, principal_id))
                stage_documents[stage] = local_stage
            else:
                prefix, grant = (
                    ("project:", "retrieve")
                    if stage == "linked_project"
                    else ("source:", "keyword_retrieve")
                )
                expected_link_ids = source_links[stage]
                typed_links = [
                    item
                    for item in link_records
                    if item.metadata.get("source_link_id") in expected_link_ids
                ]
                if stage == "raw_keyword" and requested_source_link_id is not None:
                    typed_links = [item for item in typed_links
                                   if item.metadata.get("source_link_id") == requested_source_link_id]
                    if requested_source_link_id not in expected_link_ids:
                        typed_links = []
                    expected_link_ids = [requested_source_link_id]
                elif stage == "raw_keyword" and len(typed_links) > 1:
                    return self._result("invalid", "source_selection_required",
                        "Targeted raw search requires one explicit Source Link.",
                        "Choose one authorized source_link_id for this bounded search.", empty_data)
                if not typed_links:
                    return self._result(
                        "denied",
                        "source_not_linked",
                        "A required progressive source is not linked.",
                        "Add one explicit accepted read-only Source Link.",
                        empty_data,
                    )
                actual_link_ids = [
                    item.metadata.get("source_link_id") for item in typed_links
                ]
                if (
                    len(typed_links) != len(expected_link_ids)
                    or any(not isinstance(item, str) for item in actual_link_ids)
                    or sorted(str(item) for item in actual_link_ids)
                    != sorted(expected_link_ids)
                ):
                    return self._result(
                        "recovery_required",
                        "source_contract_invalid",
                        "The authority-owned Source Link identity is duplicated or ambiguous.",
                        "Repair the Source Link controls before cross-authority retrieval.",
                        empty_data,
                    )
                if any(
                    item.metadata.get("authority_id") != active_id
                    or item.metadata.get("lifecycle") != "accepted"
                    or item.metadata.get("processing_layer") != "condensed"
                    or item.metadata.get("source_trust") != "internal"
                    or not isinstance(item.metadata.get("linked_authority_id"), str)
                    or not str(item.metadata["linked_authority_id"]).startswith(prefix)
                    for item in typed_links
                ):
                    return self._result(
                        "recovery_required",
                        "source_contract_invalid",
                        "An authority-owned Source Link violates its closed trust contract.",
                        "Repair the exact Link metadata before cross-authority retrieval.",
                        empty_data,
                    )
                if stage == "raw_keyword" and any(not source_access_allowed(item, principal_id)
                                                  for item in typed_links):
                    return self._result("denied", "source_access_denied",
                        "The selected source is not shared with this identity.",
                        "Ask the Owner for an explicit source grant.", empty_data)
                linked_targets = [
                    str(item.metadata["linked_authority_id"]) for item in typed_links
                ]
                if len(set(linked_targets)) != len(linked_targets):
                    return self._result(
                        "recovery_required",
                        "source_contract_invalid",
                        "More than one Source Link targets the same foreign authority.",
                        "Keep one exact Link identity per foreign authority and stage.",
                        empty_data,
                    )
                if any(
                    not isinstance(item.metadata.get("grants"), list)
                    or grant not in item.metadata["grants"]
                    for item in typed_links
                ):
                    return self._result(
                        "denied",
                        "access_denied",
                        "At least one required progressive Source Link lacks its grant.",
                        "Repair or remove the denied link before claiming absence.",
                        empty_data,
                    )
                foreign: list[ManagedMarkdown] = []
                for link in sorted(typed_links, key=lambda item: item.artifact_id):
                    link_document_limit = min(
                        256 - stage_scan_documents,
                        500 - scan_documents,
                    )
                    link_byte_limit = min(
                        8_388_608 - stage_scan_bytes,
                        16_777_216 - scan_bytes,
                    )
                    linked_id = str(link.metadata["linked_authority_id"])
                    source_binding: dict[str, object] = {
                        "link_artifact_id": link.artifact_id,
                        "link_revision": link.revision,
                        "link_sha256": link.content_sha256,
                        "linked_authority_id": linked_id,
                        "grants": list(link.metadata["grants"]),
                        **({"source_access": link.metadata.get("source_access")} if stage == "raw_keyword" else {}),
                    }
                    try:
                        if stage == "linked_project":
                            from .project_io import require_settings_healthy, settings_snapshot_token
                            linked_root = self._root_for_authority(linked_id)
                            if linked_root is None:
                                raise ContractValidationError("linked Project root is unavailable")
                            require_settings_healthy(linked_root, linked_id)
                            target_authority = self._repository.bootstrap(linked_id)
                            if not has_grant(target_authority, principal_id, "retrieve"):
                                return self._result(
                                    "denied",
                                    "access_denied",
                                    "The caller cannot read a linked Project authority.",
                                    "Use an identity with the required source capability.",
                                    empty_data,
                                )
                            linked_snapshot = self._repository.progressive_stage_snapshot(
                                linked_id,
                                "linked_project",
                                max_documents=link_document_limit,
                                max_bytes=link_byte_limit,
                            )
                            snapshot = linked_snapshot.get("documents")
                            if not isinstance(snapshot, tuple):
                                raise ContractValidationError("linked stage result is invalid")
                            if linked_snapshot.get("exhausted") is True:
                                return self._result(
                                    "incomplete",
                                    "resource_exhausted",
                                    "The bounded linked-Project scan budget was exhausted.",
                                    "Narrow the authority-owned Project search scope.",
                                    {
                                        **empty_data,
                                        "budget_used": {
                                            "records": scan_documents + int(linked_snapshot.get("documents_scanned", 0)),
                                            "bytes": scan_bytes + int(linked_snapshot.get("bytes_scanned", 0)),
                                        },
                                    },
                                )
                            scan_documents += int(linked_snapshot.get("documents_scanned", 0))
                            scan_bytes += int(linked_snapshot.get("bytes_scanned", 0))
                            stage_scan_documents += int(linked_snapshot.get("documents_scanned", 0))
                            stage_scan_bytes += int(linked_snapshot.get("bytes_scanned", 0))
                            source_binding.update(
                                {
                                    "authority_artifact_id": target_authority.artifact_id,
                                    "authority_revision": target_authority.revision,
                                    "authority_sha256": target_authority.content_sha256,
                                    "settings_snapshot_sha256": settings_snapshot_token(linked_root, linked_id),
                                }
                            )
                            for item in snapshot:
                                item_metadata = dict(item.metadata)
                                if item_metadata.get("schema") == "owledge.managed-markdown/1":
                                    item_metadata.setdefault("stage", "linked_project")
                                    item_metadata.setdefault(
                                        "canonical",
                                        item_metadata.get("lifecycle") == "accepted"
                                        and item_metadata.get("processing_layer")
                                        == "condensed",
                                    )
                                if item_metadata.get("stage") != "linked_project":
                                    continue
                                foreign.append(
                                    ManagedMarkdown(
                                        relative_path=item.relative_path,
                                        metadata=item_metadata,
                                        body=item.body,
                                        content_sha256=item.content_sha256,
                                        size_bytes=item.size_bytes,
                                    )
                                )
                        else:
                            raw_snapshot = self._repository.raw_keyword_snapshot(
                                linked_id,
                                query=query.strip(),
                                max_documents=min(link_document_limit, source_page_documents),
                                max_bytes=link_byte_limit,
                                max_matches=max_records,
                                source_areas=tuple(source_areas),
                                cursor=source_cursor,
                                discover_areas=discover_source_areas,
                                area_parent=source_area_parent,
                                selection_binding=sha256(json.dumps({
                                    "principal": principal_id,
                                    "filters": filters,
                                    "source_link_id": requested_source_link_id,
                                    "selected_source_link_id": link.metadata.get("source_link_id"),
                                    "link_artifact_id": link.artifact_id,
                                    "link_revision": link.revision,
                                    "link_sha256": link.content_sha256,
                                    "linked_authority_id": linked_id,
                                }, sort_keys=True).encode()).hexdigest(),
                            )
                            raw_documents = raw_snapshot.get("documents")
                            manifest = raw_snapshot.get("manifest")
                            if not isinstance(raw_documents, tuple) or not isinstance(manifest, dict):
                                raise ContractValidationError("raw snapshot result is invalid")
                            if discover_source_areas:
                                return self._result("incomplete", "source_areas_available",
                                    "Authorized source Areas are available for targeted search.",
                                    "Select one or more Areas and search within the bounded source page.",
                                    {**empty_data, "source_areas": list(raw_snapshot.get("areas", ())),
                                     "continuation": raw_snapshot.get("continuation"),
                                     "search_progress": {"files_examined": 0, "bytes_examined": 0,
                                                         "areas_returned": len(raw_snapshot.get("areas", ())),
                                                         "areas_total": raw_snapshot.get("areas_total", 0)}})
                            if isinstance(raw_snapshot.get("oversized_record"), dict):
                                return self._result("incomplete", "source_record_too_large",
                                    "One selected source file exceeds the bounded raw read budget.",
                                    "Narrow or split the named source file before continuing this Area.",
                                    {**empty_data, "excluded_source_files": [raw_snapshot["oversized_record"]],
                                     "search_progress": {"files_examined": 0, "bytes_examined": 0}})
                            raw_continuation = raw_snapshot.get("continuation")
                            raw_area_page = list(raw_snapshot.get("areas", ()))
                            raw_unreadable_files = list(raw_snapshot.get("unreadable_files", ()))
                            raw_progress = {"files_examined": raw_snapshot.get("documents_scanned"),
                                            "bytes_examined": raw_snapshot.get("bytes_scanned"),
                                            "oversized_files_skipped": raw_snapshot.get("oversized_files_skipped", 0)}
                            scan_documents += int(raw_snapshot.get("documents_scanned", 0))
                            scan_bytes += int(raw_snapshot.get("bytes_scanned", 0))
                            stage_scan_documents += int(raw_snapshot.get("documents_scanned", 0))
                            stage_scan_bytes += int(raw_snapshot.get("bytes_scanned", 0))
                            foreign.extend(raw_documents)
                            source_binding["snapshot"] = manifest
                    except (ContractValidationError, OSError):
                        return self._result(
                            "recovery_required",
                            "source_unavailable",
                            "A linked progressive source is unavailable or invalid.",
                            "Repair the source boundary before treating evidence as absent.",
                            empty_data,
                        )
                    cast_sources = proof_context["sources"]
                    if isinstance(cast_sources, list):
                        cast_sources.append(source_binding)
                stage_documents[stage] = tuple(item for item in foreign if
                    stage != "linked_project" or item.metadata.get("knowledge_kind") != "project_essence"
                    or self._source_reference_allowed(item, tuple(foreign), principal_id))
            current_id_list = [item.artifact_id for item in stage_documents[stage]]
            current_ids = set(current_id_list)
            if (
                len(current_ids) != len(current_id_list)
                or observed_stage_ids.intersection(current_ids)
            ):
                return self._result(
                    "recovery_required",
                    "source_contract_invalid",
                    "A progressive artifact identity occurs in more than one stage.",
                    "Repair the duplicated staged identity before retrying.",
                    empty_data,
                )
            observed_stage_ids.update(current_ids)
            proof_context["scan_budget"] = {
                "max_stage_documents": 256,
                "max_stage_bytes": 8_388_608,
                "max_total_documents": 500,
                "max_total_bytes": 16_777_216,
                "documents_scanned": scan_documents,
                "bytes_scanned": scan_bytes,
                "metadata_entries_examined": scan_metadata_entries,
                "metadata_directories_examined": scan_metadata_dirs,
                "metadata_entry_limit": 4096,
            }
            assessed = progressive_assess(
                stage_documents,
                required_evidence=tuple(str(item) for item in case["required_evidence"]),
                search_envelope=envelope,
                query=query.strip(),
                filters=filters,
                max_result_records=max_records,
                max_result_bytes=max_bytes,
                complete=index == len(envelope) - 1,
                compare_stages=compare_stages,
                proof_context=proof_context,
                gap_admission=str(case["gap_admission"]),
                safe_topic=(str(case["safe_topic"]) if case.get("safe_topic") else None),
            )
            terminal = assessed.get("terminal")
            if not (
                isinstance(terminal, tuple)
                and len(terminal) == 2
                and all(isinstance(item, str) for item in terminal)
            ):
                return self._result(
                    "invalid",
                    "retrieval_contract_invalid",
                    "The progressive retrieval contract is invalid.",
                    "Repair the accepted global retrieval registry.",
                    {},
                )
            if terminal[0] != "continue":
                break
        terminal = assessed.get("terminal")
        if not isinstance(terminal, tuple):
            return self._result("invalid", "retrieval_contract_invalid", "The retrieval result is invalid.", "Repair the accepted registry.", {})
        status, reason = terminal
        summaries = {
            "coverage_complete": "Curated or linked knowledge covers the request.",
            "review_signal": "The Inbox contains a related signal that requires review.",
            "evidence_available": "Attributable noncanonical reuse evidence is available.",
            "untrusted_evidence": "Explicit raw fallback found untrusted source evidence.",
            "knowledge_absent": "Evidence is absent from the complete bounded envelope.",
            "evidence_conflict": "Authorized evidence contains conflicting values.",
            "resource_exhausted": "The bounded retrieval budget was exhausted.",
            "filter_match": "Curated knowledge matches the typed filters.",
            "filter_expanded": "A later permitted stage matches the typed filters.",
            "filter_no_match": "The request-local filters matched no permitted evidence.",
            "raw_no_match": "The explicit raw keyword fallback found no lexical match; absence is not proven.",
            "source_contract_invalid": "A staged record violates its closed trust contract.",
        }
        result = self._result(
            status,
            reason,
            summaries.get(reason, "The progressive retrieval completed deterministically."),
            "Use the returned evidence and provenance state.",
            assessed.get("data", {}),
        )
        result_data = result.get("data", {})
        if restricted_evidence_present and result.get("reason_code") in {"knowledge_absent", "filter_no_match"}:
            result["status"] = "incomplete"
            result["reason_code"] = "source_access_limited"
            result["summary"] = "The permitted evidence did not cover the request; restricted sources were omitted."
            result["next_action"] = "Ask the Owner for an explicit source grant before claiming absence."
            if isinstance(result_data, dict):
                result_data["gap_effect_allowed"] = False
                result_data.pop("absence_proof", None)
        if self._identity_profile == "mvp-v1" and "raw_keyword" in stage_documents:
            selected = set(result_data.get("selected_artifact_ids", []))
            hits = []
            for document in stage_documents.get("raw_keyword", ()):
                if document.artifact_id not in selected:
                    continue
                hit = raw_evidence_hit(document, query)
                bindings = [binding for binding in proof_context["sources"]
                            if binding.get("linked_authority_id") == document.authority_id
                            and isinstance(binding.get("snapshot"), dict)]
                if len(bindings) == 1:
                    binding = bindings[0]
                    hit["source_binding"] = {key: value for key, value in binding.items() if key not in {"snapshot", "grants"}}
                    hit["source_binding"]["snapshot"] = {key: value for key, value in binding["snapshot"].items() if key != "records"}
                hits.append(hit)
            result_data["raw_hits"] = hits
        if raw_progress:
            result_data["search_progress"] = {**raw_progress,
                "hits_returned": len(result_data.get("raw_hits", []))}
        if raw_continuation is not None:
            result["status"] = "incomplete"
            result["reason_code"] = "resource_exhausted"
            result["summary"] = "The bounded raw keyword scan page was exhausted."
            result["next_action"] = "Continue with the returned cursor or narrow the selected source Areas."
            result_data["continuation"] = raw_continuation
            result_data["source_areas"] = raw_area_page
        if raw_unreadable_files:
            result["status"] = "incomplete"
            result["reason_code"] = "source_encoding_unreadable"
            result["summary"] = "One or more permitted source files could not be decoded as UTF-8."
            result["next_action"] = "Repair or re-register the named UTF-8 source files; continue any returned cursor."
            result_data["unreadable_source_files"] = raw_unreadable_files
            result_data["gap_effect_allowed"] = False
            result_data.pop("absence_proof", None)
        selected_count = len(result_data.get("selected_artifact_ids", []))
        if selected_count > max_records:
            return self._result(
                "incomplete", "resource_exhausted",
                "The bounded retrieval result record budget was exhausted.",
                "Narrow the authority-owned search envelope.",
                {**empty_data, "budget_used": {
                    "records": selected_count, "record_limit": max_records,
                }},
            )
        result_bytes = len(
            json.dumps(
                result,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        if result_bytes > max_bytes:
            # Optional hints yield capacity to the unchanged primary result.
            result_data = result.get("data")
            if isinstance(result_data, dict) and "candidate_hints" in result_data:
                result_data.pop("candidate_hints")
                result_bytes = len(json.dumps(
                    result, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                ).encode("utf-8"))
        if result_bytes > max_bytes:
            return self._result(
                "incomplete",
                "resource_exhausted",
                "The bounded retrieval result context budget was exhausted.",
                "Narrow the filters or the authority-owned search envelope.",
                {
                    **empty_data,
                    **({"continuation": raw_continuation, "source_areas": raw_area_page,
                        "search_progress": raw_progress} if raw_continuation is not None else {}),
                    "budget_used": {
                        "result_bytes": result_bytes,
                        "result_byte_limit": max_bytes,
                    },
                },
            )
        return result

    def _run_maintenance_observation(
        self,
        *,
        active_id: str,
        operation_id: object,
        payload: dict[str, object],
    ) -> dict[str, object]:
        if not active_id.startswith("user-global:") or not isinstance(operation_id, str):
            return self._result(
                "denied",
                "access_denied",
                "Maintenance requires the active User-Global authority.",
                "Use the explicit global maintenance path.",
                {},
            )
        override = payload.get("budget_override", {})
        if not isinstance(override, dict):
            return self._result("invalid", "budget_invalid", "The maintenance budget is invalid.", "Use bounded non-negative limits.", {})
        max_documents = override.get("max_documents", 500)
        max_bytes = override.get("max_bytes", 16_777_216)
        cursor = payload.get("cursor")
        if not (
            isinstance(max_documents, int)
            and 0 <= max_documents <= 500
            and isinstance(max_bytes, int)
            and 0 <= max_bytes <= 16_777_216
        ):
            return self._result("invalid", "budget_invalid", "The maintenance budget is invalid.", "Use bounded non-negative limits.", {})
        if cursor is not None and not isinstance(cursor, dict):
            return self._result("invalid", "maintenance_cursor_invalid", "The maintenance cursor is invalid.", "Use only a cursor returned by the previous bounded batch.", {})
        try:
            bounded = self._repository.maintenance_snapshot(
                active_id,
                max_documents=max_documents,
                max_bytes=max_bytes,
                max_candidates=10,
                cursor=cursor,
            )
        except (ContractValidationError, OSError):
            return self._result(
                "recovery_required",
                "source_unavailable",
                "The bounded maintenance lanes could not be read safely.",
                "Repair the global maintenance source before retrying.",
                {},
            )
        records = bounded.get("documents")
        documents_scanned = bounded.get("documents_scanned")
        bytes_scanned = bounded.get("bytes_scanned")
        exhausted = bounded.get("exhausted")
        continuation_cursor = bounded.get("continuation_cursor")
        if not (
            isinstance(records, tuple)
            and isinstance(documents_scanned, int)
            and isinstance(bytes_scanned, int)
            and isinstance(exhausted, bool)
        ):
            return self._result("invalid", "maintenance_contract_invalid", "The maintenance snapshot is invalid.", "Repair the repository port.", {})
        if exhausted:
            candidates = [
                item.artifact_id
                for item in records
                if item.metadata.get("stage") in {"inbox", "reuse_feed"}
            ]
            return self._result(
                "incomplete",
                "resource_exhausted",
                "The separate maintenance budget was exhausted without effects.",
                "Resume with a bounded maintenance batch.",
                {
                    "documents_scanned": documents_scanned,
                    "bytes_scanned": bytes_scanned,
                    "metadata_entries_examined": bounded.get("metadata_entries_examined", 0),
                    "metadata_directories_examined": bounded.get("metadata_directories_examined", 0),
                    "metadata_entry_limit": bounded.get("metadata_entry_limit", 4096),
                    "candidate_ids": candidates,
                    "canonical_writes": 0,
                    "continuation_cursor": continuation_cursor,
                },
            )
        all_candidates = [
            item.artifact_id
            for item in records
            if item.metadata.get("stage") in {"inbox", "reuse_feed"}
        ]
        candidates = all_candidates
        observation = {
            "documents_scanned": documents_scanned,
            "bytes_scanned": bytes_scanned,
            "metadata_entries_examined": bounded.get("metadata_entries_examined", 0),
            "metadata_directories_examined": bounded.get("metadata_directories_examined", 0),
            "metadata_entry_limit": bounded.get("metadata_entry_limit", 4096),
            "candidate_ids": candidates,
            "canonical_writes": 0,
            "sqlite_required": False,
            "resumed_from": cursor,
        }
        try:
            receipt_id = self._repository.apply(
                "maintenance_observe",
                active_id,
                {
                    "authority_id": active_id,
                    "operation_id": operation_id,
                    "observation": observation,
                },
            )
        except (ContractValidationError, OSError):
            return self._result(
                "conflict",
                "maintenance_conflict",
                "The maintenance observation could not be recorded consistently.",
                "Inspect the existing observation receipt.",
                {},
            )
        return self._result(
            "ok",
            "maintenance_observed",
            "The bounded maintenance observation completed without canonical writes.",
            "Review only the returned bounded candidates when useful.",
            observation,
            receipt_id=receipt_id,
        )

    def _run_reuse_feed_discovery(self, *, active_id: str, principal_id: str,
                                  payload: dict[str, object]) -> dict[str, object]:
        from .source_curation import feed_reference, valid_reuse_contribution, validate_feed_discovery_request
        try:
            validate_feed_discovery_request(payload)
            stage = payload.get("stage", "reuse_feed")
            filters = normalize_typed_filters(payload.get("filters", {}))
            authority = self._repository.bootstrap(active_id)
            cursor_binding = sha256(json.dumps({"authority_id": active_id, "query": payload["query"],
                                                "knowledge_area": payload["knowledge_area"], "stage": stage,
                                                "filters": filters, "principal_id": principal_id,
                                                "authority_sha256": authority.content_sha256}, sort_keys=True).encode()).hexdigest()
            if payload["cursor"] is not None and payload["cursor"]["binding"] != cursor_binding:
                return self._result("invalid", "reuse_feed_cursor_mismatch", "The Reuse Feed query changed during continuation.",
                                    "Restart Feed discovery for the new query or Area.", {"complete_absence_proven": False})
            bounded = self._repository.maintenance_snapshot(
                active_id, max_documents=32, max_bytes=262_144,
                max_candidates=10, cursor=(payload["cursor"]["position"] if payload["cursor"] is not None else None),
                stage=stage,
            )
            records = bounded.get("documents")
            if not isinstance(records, tuple):
                raise ContractValidationError("Feed snapshot is invalid")
            contributions = []
            for document in records:
                if not valid_reuse_contribution(document, stage):
                    raise ContractValidationError("selected contribution provenance is invalid")
                if document.metadata.get("knowledge_kind") == "project_essence" and not self._essence_contribution_current(document, principal_id):
                    continue
                fresh = (document.metadata.get("source_record_trust"), document.metadata.get("source_processing_layer")) == ("reviewed", "delta")
                if not fresh:
                    continue
                if not matches_typed_filters(document, filters):
                    continue
                reference = feed_reference(document, str(payload["query"]), payload["knowledge_area"], stage)
                if reference is not None:
                    contributions.append(reference)
        except (ContractValidationError, OSError):
            return self._result("invalid", "reuse_feed_invalid", "The bounded Reuse Feed could not be read safely.",
                                "Repair malformed Feed provenance or restart from a current cursor.",
                                {"complete_absence_proven": False, "gap_effect_allowed": False})
        raw_continuation = bounded.get("continuation_cursor")
        continuation = {"binding": cursor_binding, "position": raw_continuation} if raw_continuation is not None else None
        partial = bool(bounded.get("exhausted"))
        data = {"contributions": contributions, "stage": stage, "continuation": continuation,
                "progress": {"documents_scanned": bounded.get("documents_scanned"),
                             "page_bytes_scanned": bounded.get("bytes_scanned"),
                             "metadata_entries_examined": bounded.get("metadata_entries_examined", 0),
                             "metadata_directories_examined": bounded.get("metadata_directories_examined", 0),
                             "metadata_entry_limit": bounded.get("metadata_entry_limit", 4096),
                             "cursor_validation_read_excluded": payload["cursor"] is not None},
                "complete_absence_proven": False, "gap_effect_allowed": False}
        lane_label = "Inbox" if stage == "inbox" else "Reuse Feed"
        return self._result("incomplete" if partial else "ok", "reuse_feed_partial" if partial else "reuse_feed_discovered",
                            f"The bounded {lane_label} page is incomplete." if partial else f"The bounded {lane_label} page is ready.",
                            "Continue from the returned cursor." if partial else
                            "Select an exact contribution; Idea and Finding remain noncanonical records.", data)

    def _validate_current_global_curation(self, active_id: str, candidate: dict, changeset: dict) -> None:
        binding = candidate.get("contribution_binding")
        if binding is None:
            return
        if not isinstance(binding, dict) or not isinstance(binding.get("contribution_id"), str):
            raise ContractValidationError("global curation binding is invalid")
        contribution = self._repository.read("reuse_contribution", active_id, {
            "authority_id": active_id, "contribution_id": binding["contribution_id"]})
        if contribution is None:
            raise ContractValidationError("global curation source disappeared")
        if candidate.get("candidate_kind") == "global_essence":
            from .source_curation import valid_reuse_contribution
            from .lesson_capture import essence_origin
            from .project_io import read_curated_reference, resolve_project_concept
            if (not valid_reuse_contribution(contribution, "reuse_feed")
                    or contribution.metadata.get("knowledge_kind") != "project_essence"
                    or binding != {"contribution_id": contribution.artifact_id,
                                   "revision": contribution.revision,
                                   "content_sha256": contribution.content_sha256}):
                raise ContractValidationError("Global Essence contribution changed")
            project_id = contribution.metadata["source_authority_id"]
            concept, current = self._current_project_concept(project_id, "principal:local-owner")
            if not current or contribution.metadata.get("source_concept_origin") != essence_origin(concept):
                raise ContractValidationError("Global Essence concept changed")
            global_root = self._root_for_authority(active_id)
            concept, _, _, _, _ = resolve_project_concept(global_root.parent, project_id)
            source = read_curated_reference(Path(concept["project_workspace"]) / "project",
                authority_id=project_id, artifact_id=contribution.metadata["source_artifact_id"])
            if (source is None or source.revision != contribution.metadata["source_revision"]
                    or source.content_sha256 != contribution.metadata["source_content_sha256"]
                    or source.body != contribution.body or not self._essence_current(source, "principal:local-owner")):
                raise ContractValidationError("Global Essence Project source changed")
            result_document = changeset.get("result_document")
            if not isinstance(result_document, str):
                raise ContractValidationError("Global Essence result is missing")
            result_metadata, result_body = parse_markdown_frontmatter(result_document)
            expected_origin = {"contribution_id": contribution.artifact_id,
                               "contribution_revision": contribution.revision,
                               "contribution_sha256": contribution.content_sha256,
                               "artifact_id": source.artifact_id, "authority_id": project_id,
                               "revision": source.revision, "content_sha256": source.content_sha256}
            if (result_body.strip() != contribution.body.strip()
                    or result_metadata.get("project_origin") != expected_origin
                    or result_metadata.get("concept_origin") != essence_origin(concept)):
                raise ContractValidationError("Global Essence result differs from selected contribution")
            return
        from .source_curation import validate_global_curation_source
        validate_global_curation_source(candidate, changeset, contribution)
        replacement = candidate.get("replacement_binding")
        if replacement is None:
            return
        if (not isinstance(replacement, dict)
                or set(replacement) != {"artifact_id", "revision", "content_sha256"}):
            raise ContractValidationError("Global replacement binding is invalid")
        current = self._repository.read("curated_reference", active_id, {
            "authority_id": active_id, "artifact_id": replacement.get("artifact_id")})
        base = self._repository.read("curated_reference", active_id, {
            "authority_id": active_id, "artifact_id": replacement.get("artifact_id"),
            "revision": replacement.get("revision")})
        if (current is None or base is None or replacement != {"artifact_id": base.artifact_id,
                "revision": base.revision, "content_sha256": base.content_sha256}):
            raise ContractValidationError("Global replacement base disappeared")
        from .source_curation import validate_global_reuse_replacement
        result_document = changeset.get("result_document")
        effects = changeset.get("effects")
        if not isinstance(result_document, str) or not isinstance(effects, list) or len(effects) != 1:
            raise ContractValidationError("Global replacement result is invalid")
        result = parse_managed_markdown(str(effects[0].get("relative_path")), result_document,
                                        encoded_document=result_document.encode("utf-8"))
        validate_global_reuse_replacement(base, candidate, changeset, result)
        current_is_base = current.revision == base.revision and current.content_sha256 == base.content_sha256
        result_is_visible = current.revision == result.revision and current.content_sha256 == result.content_sha256
        result_history = None if result_is_visible else self._repository.read("curated_reference", active_id, {
            "authority_id": active_id, "artifact_id": result.artifact_id, "revision": result.revision})
        if not current_is_base and not result_is_visible and (result_history is None or result_history.content_sha256 != result.content_sha256):
            raise ContractValidationError("Global replacement current state is stale")

    def _proof_read_rights_current(self, active_id: str, principal_id: str,
                                   controls: tuple[ManagedMarkdown, ...], proof: dict) -> bool:
        binding = proof.get("binding")
        sources = binding.get("sources") if isinstance(binding, dict) else None
        if not isinstance(sources, list):
            return False
        for source in sources:
            if not isinstance(source, dict):
                return False
            linked_id = source.get("linked_authority_id")
            matches = [item for item in controls
                       if item.metadata.get("schema") == "owledge.knowledge-source-link/1"
                       and item.authority_id == active_id
                       and item.artifact_id == source.get("link_artifact_id")
                       and item.metadata.get("linked_authority_id") == linked_id
                       and item.metadata.get("lifecycle") == "accepted"
                       and isinstance(item.metadata.get("grants"), list)]
            if len(matches) != 1:
                return False
            grants = matches[0].metadata["grants"]
            if isinstance(linked_id, str) and linked_id.startswith("source:"):
                if "discover" not in grants or "keyword_retrieve" not in grants or not source_access_allowed(matches[0], principal_id):
                    return False
            elif isinstance(linked_id, str) and linked_id.startswith("project:"):
                try:
                    if "retrieve" not in grants or not has_grant(self._repository.bootstrap(linked_id), principal_id, "retrieve"):
                        return False
                except (ContractValidationError, OSError):
                    return False
            else:
                return False
        registries = [item for item in controls if item.metadata.get("schema") == "owledge.progressive-retrieval-registry/1"]
        if len(registries) != 1:
            return False
        cases = registries[0].metadata.get("coverage_cases")
        case = cases.get(proof.get("coverage_case_id")) if isinstance(cases, dict) else None
        if not isinstance(case, dict):
            return False
        envelope = case.get("search_envelope")
        if not isinstance(envelope, list):
            return False
        if "curated" in envelope:
            try:
                page = self._repository.progressive_stage_snapshot(active_id, "curated",
                    max_documents=256, max_bytes=8_388_608)
                documents = page.get("documents")
                if page.get("exhausted") is True or not isinstance(documents, tuple):
                    return False
                if any(not self._source_reference_allowed(item, controls, principal_id) for item in documents):
                    return False
            except (ContractValidationError, OSError):
                return False
        return True

    def _run_progressive_gap_admission(
        self,
        *,
        active_id: str,
        principal_id: str,
        active_documents: tuple[ManagedMarkdown, ...],
        operation_id: object,
        payload: dict[str, object],
    ) -> dict[str, object]:
        proof = payload.get("absence_proof")
        proof_id = payload.get("absence_proof_id")
        expected_gap_revision = payload.get("expected_gap_revision")
        if not (
            isinstance(operation_id, str)
            and isinstance(proof, dict)
            and proof.get("schema") == "owledge.progressive-absence-proof/1"
            and isinstance(proof_id, str)
            and proof.get("proof_id") == proof_id
            and isinstance(expected_gap_revision, str)
            and isinstance(proof.get("coverage_case_id"), str)
            and isinstance(proof.get("coverage_case_revision"), str)
            and isinstance(proof.get("query"), str)
            and isinstance(proof.get("filters"), dict)
            and isinstance(proof.get("safe_topic"), str)
            and isinstance(proof.get("required_evidence"), list)
            and all(isinstance(item, str) and item for item in proof["required_evidence"])
            and isinstance(proof.get("snapshot_sha256"), str)
        ):
            return self._result(
                "invalid",
                "absence_proof_invalid",
                "The progressive Absence Proof is incomplete.",
                "Retrieve the authority-owned Coverage Case again.",
                {},
            )
        source_snapshot_id = f"snapshot:sha256:{proof['snapshot_sha256']}"
        coverage_case_id = str(proof["coverage_case_id"])
        request_sha256 = sha256(
            json.dumps(
                {
                    "absence_proof": proof,
                    "absence_proof_id": proof_id,
                    "expected_gap_revision": expected_gap_revision,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        try:
            replay = self._repository.read(
                "gap_admission_replay",
                active_id,
                {
                    "authority_id": active_id,
                    "operation_id": operation_id,
                    "coverage_case_id": coverage_case_id,
                    "proof_id": proof_id,
                    "source_snapshot_id": source_snapshot_id,
                    "expected_gap_revision": expected_gap_revision,
                    "request_sha256": request_sha256,
                },
            )
        except (ContractValidationError, OSError, ValueError):
            return self._result(
                "conflict",
                "operation_replay_mismatch",
                "The operation identity is already bound to another exact request.",
                "Use the original request or a new operation identity.",
                {},
            )
        if replay is not None:
            if not self._proof_read_rights_current(active_id, principal_id, active_documents, proof):
                return self._result("denied", "source_access_denied",
                    "The proof's sources are no longer available to this identity.",
                    "Ask the Owner for a current source grant.", {})
            gap, receipt_id, reason_code = replay
            if receipt_id is not None:
                self._repository.apply("trace_record", active_id, {
                    "authority_id": active_id,
                    "event": {"event": reason_code, "authority_id": active_id,
                              "principal_id": principal_id, "assurance": "asserted",
                              "base_revision": expected_gap_revision, "result_revision": gap["gap_revision"],
                              "outcome": f"ok/{reason_code}", "receipt_id": receipt_id,
                              "coverage_case_revision": proof["coverage_case_revision"],
                              "source_snapshot_id": source_snapshot_id, "absence_proof_id": proof_id},
                })
            return self._result(
                "ok",
                reason_code,
                "The proven global knowledge absence is recorded once.",
                "Open a bounded Maintenance Bundle when one is configured.",
                gap,
                receipt_id=receipt_id,
            )
        binding = proof.get("binding")
        budget = binding.get("budget") if isinstance(binding, dict) else None
        retry_payload: dict[str, object] = {
            "coverage_case_id": proof["coverage_case_id"],
            "query": proof["query"],
            "filters": proof["filters"],
        }
        if isinstance(budget, dict):
            retry_payload["budget_override"] = dict(budget)
        current = self._run_progressive_retrieval(
            active_id=active_id,
            principal_id=principal_id,
            active_documents=active_documents,
            payload=retry_payload,
        )
        if current.get("status") in {"denied", "recovery_required"} or current.get("reason_code") == "source_access_limited":
            return current
        current_data = current.get("data")
        current_proof = current_data.get("absence_proof") if isinstance(current_data, dict) else None
        if not (
            current.get("status") == "incomplete"
            and current.get("reason_code") == "knowledge_absent"
            and current_proof == proof
        ):
            return self._result(
                "stale", "absence_proof_mismatch",
                "The progressive Absence Proof no longer matches the bounded sources.",
                "Retrieve the Coverage Case again before admitting a Gap.", {})
        try:
            gap, receipt_id, reason_code = self._repository.apply(
                "admit_gap",
                active_id,
                {
                    "authority_id": active_id,
                    "operation_id": operation_id,
                    "coverage_case_id": coverage_case_id,
                    "coverage_case_revision": str(proof["coverage_case_revision"]),
                    "proof_id": proof_id,
                    "source_snapshot_id": source_snapshot_id,
                    "safe_topic": str(proof["safe_topic"]),
                    "required_evidence": list(proof["required_evidence"]),
                    "expected_gap_revision": expected_gap_revision,
                    "request_sha256": request_sha256,
                },
            )
            if receipt_id is not None:
                self._repository.apply(
                    "trace_record",
                    active_id,
                    {
                        "authority_id": active_id,
                        "event": {
                            "event": reason_code,
                            "authority_id": active_id,
                            "principal_id": principal_id,
                            "assurance": "asserted",
                            "base_revision": expected_gap_revision,
                            "result_revision": gap["gap_revision"],
                            "outcome": f"ok/{reason_code}",
                            "receipt_id": receipt_id,
                            "coverage_case_revision": proof["coverage_case_revision"],
                            "source_snapshot_id": source_snapshot_id,
                            "absence_proof_id": proof_id,
                        },
                    },
                )
        except (ContractValidationError, OSError, ValueError):
            return self._result(
                "recovery_required",
                "gap_effect_inconsistent",
                "The progressive Gap effect could not be applied consistently.",
                "Inspect the proof-bound effect before retrying.",
                {},
            )
        return self._result(
            "ok",
            reason_code,
            "The proven global knowledge absence is recorded once.",
            "Open a bounded Maintenance Bundle when one is configured.",
            gap,
            receipt_id=receipt_id,
        )

    def execute(self, command: Mapping[str, object]) -> dict[str, object]:
        """Execute an untrusted command; caller-declared Owner assurance is ignored."""

        return self._execute(command, trusted_assurance="asserted")

    def _execute_from_local_owner(
        self,
        command: Mapping[str, object],
    ) -> dict[str, object]:
        """Private adapter entry point that binds locally observed Owner assurance."""

        return self._execute(command, trusted_assurance="local_owner")

    def _execute_from_local_operator(self, command: Mapping[str, object], *, name: str,
                                     workspace: Path) -> dict[str, object]:
        """Bind a native human Operator to its live target, never request claims."""
        return self._execute(command, trusted_assurance="local_operator",
                             operator_name=name, operator_workspace=Path(workspace))

    def _live_operator(self, active_id: str, principal_id: str, name: str | None,
                       workspace: Path | None) -> bool:
        from .project_io import bootstrap_authority, local_connection_principal
        if (self._identity_profile != "mvp-v1" or not isinstance(name, str)
                or workspace is None or not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", name)):
            return False
        root = self._root_for_authority(active_id)
        expected = Path(workspace) / ("project" if active_id.startswith("project:") else "global")
        if root is None or root.resolve() != expected.resolve():
            return False
        try:
            authority = bootstrap_authority(Path(root), active_id)
            profiles = authority.metadata.get("connections")
            profile = profiles.get(name) if isinstance(profiles, dict) else None
            grants = authority.metadata.get("actor_grants")
            valid = (isinstance(profile, dict)
                    and set(profile) == {"principal_id", "role", "authority_id", "source_link_id", "status"}
                    and profile.get("principal_id") == principal_id
                    and principal_id == local_connection_principal(active_id, name)
                    and profile.get("role") == "operator" and profile.get("status") == "active"
                    and profile.get("authority_id") == active_id
                    and isinstance(grants, dict)
                    and grants.get(principal_id) == list(named_connection_capabilities("operator"))
                    and authority.metadata.get("mode") == "read_write")
            if not valid:
                return False
            link_id = profile.get("source_link_id")
            if link_id is None:
                return True
            if not isinstance(link_id, str):
                return False
            links = [item for item in self._repository.progressive_controls(active_id)
                     if item.metadata.get("source_link_id") == link_id]
            return len(links) == 1 and source_access_allowed(links[0], principal_id)
        except (ContractValidationError, OSError, ValueError):
            return False

    def _execute_with_write_locks(self, command, trusted_assurance, roots, read_roots=(),
                                  operator_name=None, operator_workspace=None):
        # Preflight grants have passed; re-read all authority/state bindings under
        # ordered locks before performing any effect, including receipt and Trace.
        try:
            with authority_write_locks((*roots, *read_roots)):
                for root in roots:
                    batch_review = (command.get("operation") in {"candidate_review", "candidate_promote"}
                                    and isinstance(command.get("payload"), dict)
                                    and command["payload"].get("batch_review") is True)
                    if (command.get("operation") == "maintenance_observe" or batch_review) and canonical_recovery_pending(root):
                        return self._result("recovery_required", "owner_recovery_required",
                            "Canonical recovery is pending; this operation made no changes.",
                            "Use explicit local Owner recovery before reviewing.", {})
                    if case_configuration_pending(root):
                        return self._result("recovery_required", "case_configuration_pending",
                            "Project case configuration is incomplete.", "Use local Owner case recover.", {})
                    if trusted_assurance == "local_operator":
                        if (not self._live_operator(str(command.get("active_authority_id")),
                                str(command.get("principal", {}).get("principal_id")),
                                operator_name, operator_workspace)):
                            return self._result("denied", "operator_binding_denied",
                                "The named human Operator was revoked before review.",
                                "Select an active Operator for this exact workspace.", {})
                        if (Path(root) / ".owledge/pending-effect.json").exists() or any(
                                (Path(root) / ".owledge/transactions").glob("*.md")):
                            return self._result("recovery_required", "owner_recovery_required",
                                "A pending effect needs local Owner recovery.",
                                "Ask the local Owner to recover before review.", {})
                    else:
                        recover_pending_effects(root)
                return self._execute(
                    command, trusted_assurance=trusted_assurance, _write_locks_held=True,
                    operator_name=operator_name, operator_workspace=operator_workspace,
                )
        except SettingsQuarantineError:
            return self._result("recovery_required", "settings_quarantine",
                "Settings are changed or invalid; no write or recovery ran.",
                "Inspect Settings and use explicit local Owner repair.", {})
        except (ContractValidationError, OSError):
            return self._result(
                "conflict", "authority_busy", "The authority cannot accept this write safely.",
                "Retry after the other writer finishes; do not bypass the lock.", {},
            )

    def _execute(
        self,
        command: Mapping[str, object],
        *,
        trusted_assurance: str,
        _write_locks_held: bool = False,
        operator_name: str | None = None,
        operator_workspace: Path | None = None,
        _validated_global_reader: bool = False,
        _validated_project_reader: bool = False,
    ) -> dict[str, object]:
        from .project_io import legacy_migration_pending
        if any(legacy_migration_pending(Path(root)) for root in self._roots.values()
               if Path(root).name == "global"):
            return self._result("recovery_required", "source_rights_migration_pending",
                "Source-rights migration is incomplete.", "Use local Owner source-rights recover.", {})
        try:
            if any(case_configuration_pending(root) for root in self._roots.values()
                   if Path(root).name == "project"):
                return self._result("recovery_required", "case_configuration_pending",
                    "Project case configuration is incomplete.", "Use local Owner case recover.", {})
        except (ContractValidationError, OSError):
            return self._result("recovery_required", "case_configuration_invalid",
                "Project case configuration cannot be read safely.", "Inspect local Owner recovery state.", {})
        if any((path.parent / ".owledge/project-reuse-registration.json").exists() for path in self._roots.values()):
            return self._result("recovery_required", "project_reuse_registration_pending", "Project reuse registration is incomplete.", "Use local Owner reuse registration recovery.", {})
        if any((path.parent / ".owledge/source-registration.json").exists() for path in self._roots.values()):
            return self._result("recovery_required", "source_registration_pending", "Source registration is incomplete.", "Use local Owner source registration recovery.", {})
        if command.get("schema") != "owledge.core-command/1":
            return self._result(
                "invalid",
                "command_invalid",
                "The Core request is not valid.",
                "Use the versioned Core command contract.",
                {},
            )
        operation = command.get("operation")
        operation_policy = _OPERATION_POLICIES.get(operation)
        if operation_policy is None:
            return self._result(
                "invalid",
                "operation_unknown",
                "The requested Core operation is not known.",
                "Choose a supported Core operation.",
                {},
            )
        raw_principal = command.get("principal")
        if not isinstance(raw_principal, dict) or not isinstance(
            raw_principal.get("principal_id"), str
        ):
            return self._result(
                "invalid",
                "principal_invalid",
                "The caller identity is incomplete.",
                "Provide valid principal evidence.",
                {},
            )
        principal = dict(raw_principal)
        principal["assurance"] = trusted_assurance
        active_id = command.get("active_authority_id")
        if not isinstance(active_id, str) or not active_id:
            return self._result(
                "invalid",
                "authority_document_invalid",
                "The project authority document is missing or invalid.",
                "Repair the local authority document and inspect again.",
                {},
            )
        active_root = self._root_for_authority(active_id)
        if active_root is None:
            return self._result(
                "invalid",
                "authority_document_invalid",
                "The project authority document is missing or invalid.",
                "Repair the local authority document and inspect again.",
                {},
            )
        if trusted_assurance == "local_operator" and (
                operation not in {"candidate_open", "candidate_queue", "candidate_review", "candidate_promote"}
                or not self._live_operator(active_id, str(principal["principal_id"]),
                                           operator_name, operator_workspace)):
            return self._result("denied", "operator_binding_denied",
                "The named human Operator is no longer active for this authority.",
                "Select an active Operator for this exact workspace.", {})
        try:
            authority = self._repository.bootstrap(active_id)
        except (ContractValidationError, OSError):
            return self._result(
                "invalid",
                "authority_document_invalid",
                "The project authority document is missing or invalid.",
                "Repair the local authority document and inspect again.",
                {},
            )
        if operation != "inspect":
            from .project_io import inspect_settings
            try:
                settings_state = inspect_settings(active_root, active_id)
            except (ContractValidationError, OSError, ValueError):
                return self._result("invalid", "settings_contract_invalid",
                    "The installed Settings contract cannot be validated.",
                    "Inspect the local installation and reinstall the verified contract resources.", {})
            if settings_state["status"] != "ready":
                return self._result("recovery_required", "settings_quarantine",
                    "Settings are changed or invalid; this operation made no effects.",
                    "Inspect Settings and use explicit local Owner repair.",
                    {"diagnostics": settings_state["diagnostics"], "gap_effect_allowed": False})
        principal_id = str(principal["principal_id"])
        named_project_readers = authority.metadata.get("named_project_readers", {})
        if (active_id == "user-global:source-access" and not _validated_global_reader
                and isinstance(named_project_readers, dict) and principal_id in named_project_readers):
            return self._result("denied", "global_reader_bridge_required",
                "A Project reader must use its live Project bridge.",
                "Use the named Project connection and explicit Global reviewed scope.", {})
        named_global_readers = authority.metadata.get("named_global_readers", {})
        if (active_id.startswith("project:") and not _validated_project_reader
                and isinstance(named_global_readers, dict) and principal_id in named_global_readers):
            return self._result("denied", "project_reader_bridge_required",
                "A Global reader must use its live registered Project bridge.",
                "Use the named Global connection and explicit Project reviewed scope.", {})
        owner_essence_contribution = (
            operation == "contribute_for_reuse" and trusted_assurance == "local_owner"
            and principal_id == "principal:local-owner"
            and isinstance(command.get("payload"), dict)
            and command["payload"].get("source_artifact_id") ==
                f"memory:{active_id.replace(':', '-')}-essence-project"
            and has_grant(authority, principal_id, "promote"))
        if not (has_grant(authority, principal_id, operation_policy.capability)
                or owner_essence_contribution):
            return self._result(
                "denied",
                "capability_denied",
                "This identity may not perform the requested knowledge operation.",
                "Ask the project Owner for the required capability.",
                {},
            )
        preflight_payload = command.get("payload")
        base_read_required = (
            operation == "curate_candidate" and isinstance(preflight_payload, dict)
            and "replacement_base" in preflight_payload
        ) or (
            operation == "lesson_candidate" and isinstance(preflight_payload, dict)
            and "correction" in preflight_payload
        ) or (
            operation == "project_record_candidate" and isinstance(preflight_payload, dict)
            and "correction" in preflight_payload
        )
        if base_read_required and not has_grant(authority, principal_id, "retrieve"):
            return self._result(
                "denied", "capability_denied", "This identity may not read the exact canonical correction base.",
                "Ask the project Owner for retrieve capability before proposing a replacement.", {},
            )
        if (operation in {"curate_candidate", "candidate_review", "candidate_promote"}
                and authority.metadata.get("mode") != "read_write"):
            return self._result(
                "invalid",
                "authority_read_only",
                "The current authority is not writable for this lifecycle action.",
                "Restore an Owner-approved writable authority before retrying; do not bypass review.",
                {},
            )
        target_authority_id = command.get("target_authority_id")
        cross_authority_contribution = (
            operation == "contribute_for_reuse"
            and isinstance(target_authority_id, str)
            and target_authority_id != active_id
        )
        cross_global_reader = (operation in {"curated_discover", "curated_read"}
            and active_id.startswith("project:") and target_authority_id == "user-global:source-access"
            and trusted_assurance == "asserted" and self._identity_profile == "mvp-v1")
        if cross_global_reader:
            return self._read_named_global_bridge(command, authority, principal_id)
        cross_project_reader = (operation in {"curated_discover", "curated_read"}
            and active_id == "user-global:source-access" and isinstance(target_authority_id, str)
            and target_authority_id.startswith("project:")
            and trusted_assurance == "asserted" and self._identity_profile == "mvp-v1")
        if cross_project_reader:
            return self._read_named_project_bridge(command, authority, principal_id)
        if target_authority_id != active_id and not cross_authority_contribution:
            return self._result(
                "denied",
                "capability_denied",
                "This identity may not apply the requested operation to that authority.",
                "Use the active Project authority or an explicitly authorized bridge.",
                {},
            )
        if (
            not _write_locks_held
            and self._identity_profile == "mvp-v1"
            and not cross_authority_contribution
            and (
                operation_policy.write_lock == "always"
                or (
                    operation_policy.write_lock == "local_owner"
                    and trusted_assurance in {"local_owner", "local_operator"}
                )
            )
        ):
            read_roots = []
            request = command.get("payload")
            proof = request.get("absence_proof") if isinstance(request, dict) else None
            binding = proof.get("binding") if isinstance(proof, dict) else None
            sources = binding.get("sources") if isinstance(binding, dict) else None
            if operation == "gap_admit" and isinstance(sources, list):
                # Coordinate only explicitly linked, authorized Project evidence.
                # Immutable Source originals are never locked or written here.
                try:
                    controls = self._repository.progressive_controls(active_id)
                    for source in sources:
                        if not isinstance(source, dict):
                            continue
                        linked_id = source.get("linked_authority_id")
                        if not isinstance(linked_id, str) or not linked_id.startswith("project:"):
                            continue
                        links = [item for item in controls if item.artifact_id == source.get("link_artifact_id")
                                 and item.metadata.get("linked_authority_id") == linked_id
                                 and item.metadata.get("lifecycle") == "accepted"
                                 and "retrieve" in item.metadata.get("grants", [])]
                        if len(links) == 1 and has_grant(self._repository.bootstrap(linked_id), principal_id, "retrieve"):
                            root = self._root_for_authority(linked_id)
                            if root is not None:
                                read_roots.append(root)
                except (ContractValidationError, OSError, TypeError):
                    return self._result("recovery_required", "source_unavailable", "Linked evidence cannot be stabilized.", "Repair the linked authority before admitting absence.", {})
            return self._execute_with_write_locks(command, trusted_assurance, (active_root,), read_roots,
                operator_name=operator_name, operator_workspace=operator_workspace)
        raw_payload = command.get("payload")
        if operation == "settings_inspect":
            from .project_io import inspect_settings
            if target_authority_id != active_id:
                return self._result("denied", "settings_scope_denied", "Settings belong to the active scope.",
                                    "Use the assigned connection for that scope.", {})
            policy = inspect_settings(active_root, active_id)
            if policy["status"] != "ready":
                return self._result("recovery_required", "settings_quarantine", "Settings need Owner repair.",
                                    "Ask the local Owner to inspect and repair Settings.", {})
            request = raw_payload if isinstance(raw_payload, dict) else {}
            if set(request) - {"research_limit"}:
                return self._result("invalid", "settings_limit_invalid", "Unknown Settings limit.",
                                    "Use an admitted runtime research limit.", {})
            limit = request.get("research_limit")
            if limit is not None:
                domain = ("none", "targeted", "deep")
                maximum = policy["effective"]["research_max_auto"]
                if not isinstance(limit, str) or limit not in domain or domain.index(limit) > domain.index(maximum):
                    return self._result("denied", "settings_limit_widening", "Research limit exceeds Owner maximum.",
                                        "Choose a depth at or below the Owner maximum.", {})
            policy["research_runtime_limit"] = limit or policy["effective"]["research_max_auto"]
            domain = ("none", "targeted", "deep")
            policy["research_selected_depth"] = domain[min(
                domain.index(policy["effective"]["research_default"]),
                domain.index(policy["research_runtime_limit"]))]
            return self._result("ok", "settings_ready", "Effective scoped Settings are available.",
                                "Use these values within the assigned Skill method.", policy)
        if operation == "curated_discover":
            from .source_curation import validate_discovery_request
            try:
                validate_discovery_request(raw_payload)
                filters = normalize_typed_filters(raw_payload.get("filters", {}))
                controls = self._repository.progressive_controls(active_id)
                rights_binding = sha256(json.dumps({"principal": principal_id, "links": [
                    (item.artifact_id, item.content_sha256) for item in controls
                    if item.metadata.get("schema") == "owledge.knowledge-source-link/1"]}, sort_keys=True).encode()).hexdigest()
                data = self._repository.read("curated_discover", active_id, {
                    "authority": authority, "payload": raw_payload,
                    "allowed_document": lambda item: (self._source_reference_allowed(item, controls, principal_id)
                                                      and matches_typed_filters(item, filters)),
                    "rights_binding": rights_binding})
            except (ContractValidationError, OSError):
                return self._result("invalid", "reference_discovery_invalid",
                                    "Reviewed discovery could not complete safely.",
                                    "Check the request and reference integrity; restart stale continuation.",
                                    {"gap_effect_allowed": False})
            limited = bool(data.get("resource_exhausted"))
            partial = limited or data["continuation"] is not None
            return self._result("incomplete" if partial else "ok", "resource_exhausted" if limited else "references_partial" if partial else "references_discovered",
                                "Reviewed reference discovery is partial." if partial else "Reviewed reference discovery is complete.",
                                "Narrow the search or read an exact identity; metadata enumeration reached its fixed limit."
                                if limited else "Continue the page or read a selected identity; discovery does not establish knowledge absence.", data)
        if operation == "curated_read":
            from .source_curation import reference_data
            if (not isinstance(raw_payload, dict) or set(raw_payload) not in ({"artifact_id"}, {"artifact_id", "revision"})
                    or not isinstance(raw_payload["artifact_id"], str) or len(raw_payload["artifact_id"]) > 256
                    or ("revision" in raw_payload and (not isinstance(raw_payload["revision"], str) or not raw_payload["revision"] or len(raw_payload["revision"]) > 256))):
                return self._result("invalid", "reference_input_invalid", "Choose one exact reference identity.", "Use the promoted reference identity.", {})
            try:
                self._repository.progressive_controls(active_id)
                document = self._repository.read("curated_reference", active_id, {
                    "authority_id": active_id, "artifact_id": raw_payload["artifact_id"], "revision": raw_payload.get("revision")})
                if document is not None and isinstance(document.metadata.get("knowledge_kind"), str) and document.metadata["knowledge_kind"] in {"idea", "finding"}:
                    from .lesson_capture import validate_project_record
                    from dataclasses import replace
                    kind = document.metadata["knowledge_kind"]
                    slug = document.artifact_id.removeprefix(f"memory:{active_id.replace(':', '-')}-{kind}-")
                    validate_project_record(replace(document, relative_path=f".owledge/curated/{kind}-{slug}.md"))
                    if not self._source_reference_allowed(document, self._repository.progressive_controls(active_id), principal_id):
                        return self._result("denied", "source_access_denied", "The typed record is outside this identity's rights.",
                                            "Ask the Owner for the required grant.", {})
                    data = {"artifact_id": document.artifact_id, "revision": document.revision,
                            "content_sha256": document.content_sha256, "knowledge_kind": document.metadata["knowledge_kind"],
                            "knowledge_area": document.metadata["knowledge_area"], "text": document.body.strip(),
                            "lifecycle": "accepted", "source_trust": "reviewed", "processing_layer": "delta",
                            "canonical": False, "record_status": document.metadata["record_status"],
                            "source": document.metadata["record_origin"]}
                    if document.metadata["knowledge_kind"] == "finding":
                        data["exception_kind"] = document.metadata["exception_kind"]
                    return self._result("ok", "project_record_found", "Reviewed nonfactual Project record is available.",
                                        "A recorded possibility or signal is not factual coverage or an absence proof.", data)
                if document is not None and document.metadata.get("knowledge_kind") == "project_essence":
                    if not self._essence_current(document, principal_id):
                        raise ContractValidationError("Project Essence concept source is stale")
                    return self._result("ok", "project_essence_found", "Current reviewed Project summary is available.",
                        "The external Project concept remains canonical.",
                        {"artifact_id": document.artifact_id, "revision": document.revision,
                         "content_sha256": document.content_sha256, "knowledge_kind": "project_essence",
                         "knowledge_area": document.metadata["knowledge_area"], "text": document.body.strip(),
                         "lifecycle": "accepted", "source_trust": "reviewed",
                         "processing_layer": document.metadata["processing_layer"],
                         "canonical": document.metadata["canonical"], "record_status": "summary",
                         "source": document.metadata["concept_origin"],
                         "concept_current": True})
                data = reference_data((document,) if document and
                    self._source_reference_allowed(document, self._repository.progressive_controls(active_id), principal_id)
                    else (), raw_payload["artifact_id"])
            except (ContractValidationError, OSError):
                return self._result("invalid", "reference_unavailable", "The exact reference cannot be read within its contract.", "Check its identity, integrity and bounded size.", {})
            return self._result("ok", "reference_found" if data else "reference_not_found",
                                "The reviewed reference is available." if data else "No reviewed reference has that identity.",
                                "Use the returned reference; this lookup does not establish knowledge absence.", data or {})
        if (
            operation == "gap_admit"
            and isinstance(raw_payload, dict)
            and isinstance(raw_payload.get("absence_proof"), dict)
            and raw_payload["absence_proof"].get("schema")
            == "owledge.progressive-absence-proof/1"
        ):
            try:
                progressive_controls = self._repository.progressive_controls(active_id)
            except (ContractValidationError, OSError):
                return self._result(
                    "recovery_required",
                    "source_unavailable",
                    "The progressive Gap controls could not be read safely.",
                    "Repair the authority controls before retrying.",
                    {},
                )
            return self._run_progressive_gap_admission(
                active_id=active_id,
                principal_id=principal_id,
                active_documents=progressive_controls,
                operation_id=command.get("operation_id"),
                payload=raw_payload,
            )
        if operation == "progressive_retrieve":
            if not isinstance(raw_payload, dict):
                return self._result(
                    "invalid",
                    "command_invalid",
                    "The Core request payload is incomplete.",
                    "Provide the payload declared by the operation contract.",
                    {},
                )
            try:
                progressive_controls = self._repository.progressive_controls(active_id)
            except (ContractValidationError, OSError):
                return self._result(
                    "recovery_required",
                    "source_unavailable",
                    "The progressive retrieval controls could not be read safely.",
                    "Repair the authority controls before retrying.",
                    {},
                )
            return self._run_progressive_retrieval(
                active_id=active_id,
                principal_id=principal_id,
                active_documents=progressive_controls,
                payload=raw_payload,
            )
        if operation == "reuse_feed_discover":
            if not isinstance(raw_payload, dict) or not active_id.startswith("user-global:"):
                return self._result("denied", "access_denied", "Reuse Feed discovery requires the active User-Global authority.",
                                    "Use a permitted Global maintainer identity.", {"complete_absence_proven": False})
            return self._run_reuse_feed_discovery(active_id=active_id, principal_id=principal_id, payload=raw_payload)
        if operation == "maintenance_observe":
            if not isinstance(raw_payload, dict):
                return self._result(
                    "invalid",
                    "command_invalid",
                    "The Core request payload is incomplete.",
                    "Provide the payload declared by the operation contract.",
                    {},
                )
            return self._run_maintenance_observation(
                active_id=active_id,
                operation_id=command.get("operation_id"),
                payload=raw_payload,
            )
        coverage_case_for_snapshot = None
        if operation == "retrieve" and isinstance(raw_payload, dict):
            requested_case = raw_payload.get("coverage_case_id")
            if isinstance(requested_case, str):
                coverage_case_for_snapshot = requested_case
        exact_global_curation = (operation == "curate_candidate" and isinstance(raw_payload, dict)
                                 and {"expected_contribution_revision", "expected_contribution_sha256"} <= set(raw_payload))
        try:
            active_documents = self._repository.progressive_controls(active_id) if operation in {"source_candidate", "source_reference_refresh", "lesson_candidate", "project_record_candidate"} or exact_global_curation else self._repository.snapshot(
                active_id,
                coverage_case_for_snapshot,
            )
        except CoverageCaseInvalidError:
            return self._result(
                "invalid",
                "coverage_case_invalid",
                "The requested Coverage Case is absent or not authoritatively valid.",
                "Choose one valid Case from the accepted Project registry.",
                {},
            )
        except (ContractValidationError, OSError):
            return self._result(
                "recovery_required",
                "source_unavailable",
                "The authorized Project snapshot could not be read completely.",
                "Repair or quarantine the unavailable source before retrying.",
                {},
            )
        coverage_controls: tuple[ManagedMarkdown, ...] | None = None
        if coverage_case_for_snapshot is not None:
            if (
                self._assess_coverage(
                    active_documents,
                    coverage_case_for_snapshot,
                )
                is None
            ):
                return self._result(
                    "invalid",
                    "coverage_case_invalid",
                    "The requested Coverage Case is absent or not authoritatively valid.",
                    "Choose one valid Case from the accepted Project registry.",
                    {},
                )
            coverage_controls = active_documents
            try:
                active_documents = self._repository.coverage_snapshot(
                    active_id,
                    active_documents,
                )
            except (ContractValidationError, OSError):
                return self._result(
                    "recovery_required",
                    "source_unavailable",
                    "The authorized Project snapshot could not be read completely.",
                    "Repair or quarantine the unavailable source before retrying.",
                    {},
                )
        if operation in {"retrieve", "gap_verify"} and any(
                not self._source_reference_allowed(item, active_documents, principal_id) for item in active_documents):
            return self._result("incomplete", "source_access_limited",
                "Restricted source-derived evidence is outside this identity's rights.",
                "Ask the Owner for an explicit source grant before claiming coverage or absence.", {})
        if operation_policy.payload_required:
            payload = command.get("payload")
            if not isinstance(payload, dict):
                return self._result(
                    "invalid",
                    "command_invalid",
                    "The Core request payload is incomplete.",
                    "Provide the payload declared by the operation contract.",
                    {},
                )
        if operation == "project_record_candidate":
            from .lesson_capture import build_project_record_candidate, validate_project_record_request
            if not active_id.startswith("project:") or authority.metadata.get("mode") != "read_write":
                return self._result("denied", "capability_denied", "Typed record capture requires a writable Project.",
                                    "Select a permitted Project workspace.", {})
            try:
                validate_project_record_request(raw_payload)
                correcting = "correction" in raw_payload
                base = None
                if correcting:
                    base = self._repository.read("curated_reference", active_id, {
                        "authority_id": active_id, "artifact_id": raw_payload["correction"]["artifact_id"]})
                    if base is None:
                        raise ContractValidationError("Project record correction base is missing")
                    if not self._source_reference_allowed(base, active_documents, principal_id):
                        return self._result("denied", "source_access_denied",
                            "The current Project record source is not shared with this identity.",
                            "Use a currently authorized source before correcting this record.", {})
                candidate, changeset = build_project_record_candidate(authority, raw_payload, principal_id,
                                                                        command["operation_id"], base)
            except (ContractValidationError, KeyError, OSError):
                if isinstance(raw_payload, dict) and "correction" in raw_payload:
                    return self._result("stale", "project_record_base_mismatch",
                        "The exact current Project record base is missing or changed.",
                        "Read its current revision and hash before proposing the correction.", {})
                return self._result("invalid", "project_record_input_invalid", "The bounded Project record is invalid.",
                                    "Provide a typed Idea or exceptional Finding with text and Area.", {})
            try:
                receipt_id = self._repository.apply("candidate_preview", active_id, {
                    "authority_id": active_id, "operation_id": command["operation_id"],
                    "candidate": candidate, "changeset": changeset})
            except (ContractValidationError, OSError):
                return self._result("conflict", "project_record_conflict", "That typed record name already has different content.",
                                    "Open the existing proposal or choose another name.", {})
            return self._result("ok", "project_record_candidate_ready", "The typed record is staged for Owner review.",
                                "Review its nonfactual status before recording.", {
                                    "candidate_id": candidate["candidate_id"],
                                    "candidate_revision": candidate["candidate_revision"],
                                    "artifact_id": candidate["review_preview"]["artifact_id"],
                                    "idempotency_key": changeset["idempotency_key"],
                                    "review_preview": candidate["review_preview"]}, receipt_id=receipt_id)
        if operation == "lesson_candidate":
            from .lesson_capture import build_candidate, validate_request
            if (not active_id.startswith(("project:", "user-global:")) or authority.metadata.get("mode") != "read_write"):
                return self._result("denied", "capability_denied", "Lesson capture requires writable active authority.", "Use a permitted Project or User-Global authority.", {})
            try:
                validate_request(raw_payload)
            except ContractValidationError:
                return self._result("invalid", "lesson_input_invalid", "The bounded Lesson and reported context are incomplete.", "Provide text, origin, conditions, verification and limitations.", {})
            correcting = "correction" in raw_payload
            if correcting and not active_id.startswith("project:"):
                return self._result("denied", "capability_denied", "Lesson correction is Project-only.",
                                    "Correct the owning Project Lesson; Global reuse requires a separate reviewed contribution.", {})
            try:
                base = None
                if correcting:
                    base = self._repository.read("curated_reference", active_id, {
                        "authority_id": active_id, "artifact_id": raw_payload["correction"]["artifact_id"]})
                    if base is None:
                        raise ContractValidationError("Lesson correction base is missing")
                candidate, changeset = build_candidate(authority, raw_payload, principal_id, command.get("operation_id"), base)
            except (ContractValidationError, OSError):
                if correcting:
                    return self._result("stale", "lesson_base_mismatch", "The exact current Project Lesson base is missing or changed.",
                                        "Read its current revision and hash before proposing the correction.", {})
                return self._result("invalid", "lesson_input_invalid", "The bounded Lesson and reported context are incomplete.",
                                    "Provide text, origin, conditions, verification and limitations.", {})
            try:
                receipt_id = self._repository.apply("candidate_preview", active_id, {
                    "authority_id": active_id, "operation_id": command["operation_id"], "candidate": candidate, "changeset": changeset})
            except (ContractValidationError, OSError):
                return self._result("conflict", "lesson_capture_conflict", "That Lesson proposal already has different content.", "Open the existing proposal or use the current exact correction base.", {})
            return self._result("ok", "lesson_candidate_ready", "The reported Lesson is staged for review.",
                                "Review its complete context before promotion.", {"candidate_id": candidate["candidate_id"],
                                "candidate_revision": candidate["candidate_revision"], "artifact_id": candidate["review_preview"]["artifact_id"],
                                "idempotency_key": changeset["idempotency_key"], "review_preview": candidate["review_preview"]}, receipt_id=receipt_id)
        if operation in {"source_candidate", "source_reference_refresh"}:
            from .source_curation import build_candidate, validate_request
            refreshing = operation == "source_reference_refresh"
            if (not active_id.startswith("user-global:") or authority.metadata.get("mode") != "read_write"
                    or not has_grant(authority, principal_id, "retrieve")):
                return self._result("denied", "capability_denied", "Source curation requires writable global propose and retrieve authority.", "Use an explicitly configured knowledge workspace.", {})
            if refreshing and (trusted_assurance != "local_owner" or principal_id != "principal:local-owner"):
                return self._result("denied", "owner_promotion_required", "Source refresh requires local Owner assurance.",
                                    "Use the explicit local Owner reference refresh path.", {})
            try:
                validate_request(payload)
                if refreshing and "correction" not in payload:
                    raise ContractValidationError("refresh needs exact correction base")
                if not isinstance(command.get("operation_id"), str) or not command["operation_id"]:
                    raise ContractValidationError("operation identity is missing")
            except ContractValidationError:
                return self._result("invalid", "source_candidate_input_invalid", "The bounded source proposal is invalid.", "Provide the exact selected evidence and bounded proposed text.", {})
            search = self._execute({**command, "operation": "progressive_retrieve", "payload": payload["source_search"]},
                                   trusted_assurance=trusted_assurance, _write_locks_held=True)
            if search.get("status") not in {"ok", "incomplete"}:
                return search
            hits = [hit for hit in search.get("data", {}).get("raw_hits", [])
                    if hit.get("relative_path") == payload["source_relative_path"]
                    and hit.get("content_sha256") == payload["source_content_sha256"]
                    and hit.get("snippet") == payload["source_excerpt"]
                    and hit.get("source_binding") == payload["source_binding"] and bool(hit.get("source_binding"))]
            if len(hits) != 1:
                return self._result("stale", "source_evidence_mismatch", "The selected source evidence no longer matches its authorized search.", "Search again and preview the exact current excerpt.", {})
            try:
                base = None
                if "correction" in payload:
                    base = self._repository.read("curated_reference", active_id, {
                        "authority_id": active_id, "artifact_id": payload["correction"]["artifact_id"]})
                    legacy_refresh_base = False
                    if (refreshing and principal_id == "principal:local-owner"
                            and authority.metadata.get("rights_migration_epoch") is not None
                            and base is not None and not self._epoch_derived_allowed(base)):
                        from .project_io import migration_legacy_reference_allowed
                        legacy_refresh_base = migration_legacy_reference_allowed(Path(active_root), base)
                    if base is None or not (self._source_reference_allowed(base, active_documents, principal_id)
                                            or legacy_refresh_base):
                        raise ContractValidationError("correction base is missing")
                candidate, changeset = build_candidate(authority, payload, hits[0], base, refresh=refreshing)
            except (ContractValidationError, OSError):
                return self._result("stale", "reference_base_mismatch", "The exact reference base has changed or cannot be corrected.", "Read the current reference and propose against its revision and hash.", {})
            try:
                receipt_id = self._repository.apply("candidate_preview", active_id, {
                    "authority_id": active_id, "operation_id": command["operation_id"], "candidate": candidate, "changeset": changeset})
            except (ContractValidationError, OSError):
                return self._result("conflict", "source_curation_conflict", "The source Candidate cannot be staged consistently.", "Reopen the existing proposal or choose a new name.", {})
            return self._result("ok", "source_candidate_ready", "The source proposal is ready for informed Owner review.",
                                "Open this exact Candidate before approval.", {"candidate_id": candidate["candidate_id"],
                                "candidate_revision": candidate["candidate_revision"], "idempotency_key": changeset["idempotency_key"],
                                "artifact_id": candidate["review_preview"]["artifact_id"], "review_preview": candidate["review_preview"]}, receipt_id=receipt_id)
        if operation == "candidate_queue":
            if (trusted_assurance not in {"local_owner", "local_operator"}
                    or set(payload) not in (set(), {"cursor"})):
                return self._result("denied", "owner_review_required",
                    "Candidate queue requires the local human review boundary.",
                    "Use native Owner or named Operator review.", {})
            try:
                queue = self._repository.read("candidate_queue", active_id,
                    {"authority_id": active_id, "principal_id": principal_id,
                     "cursor": payload.get("cursor")})
                if queue["resource_exhausted"]:
                    return self._result("incomplete", "resource_exhausted",
                        "Candidate metadata or byte ceiling was reached without a review effect.",
                        "Reduce the Candidate inventory or review one exact Candidate.",
                        {**queue, "items": [], "expected_sha256": None})
                items = []
                for candidate_id, revision in queue["items"]:
                    opened = self._execute({**command, "operation": "candidate_open",
                        "payload": {"candidate_id": candidate_id, "candidate_revision": revision}},
                        trusted_assurance=trusted_assurance, _write_locks_held=_write_locks_held,
                        operator_name=operator_name, operator_workspace=operator_workspace)
                    if opened.get("status") != "ok":
                        return self._result("stale", "candidate_queue_stale",
                            "A staged Candidate cannot be opened under current review rights.",
                            "Review that exact Candidate or repair its source before retrying.",
                            {"candidate_id": candidate_id, "details": opened})
                    preview = opened["data"]
                    target = preview.get("target")
                    source = preview.get("source")
                    case_id = source.get("coverage_case_id") if isinstance(source, dict) else None
                    basename = target.rsplit("/", 1)[-1].removesuffix(".md") if isinstance(target, str) else candidate_id
                    record_kind = preview.get("record_kind")
                    name = ("case:" + case_id.removeprefix("coverage:") if isinstance(case_id, str) else
                            f"{record_kind}:" + basename.removeprefix(f"{record_kind}-")
                            if record_kind in {"idea", "finding"} else
                            "lesson:" + basename.removeprefix("lesson-") if basename.startswith("lesson-") else
                            "essence:" + basename.removeprefix("essence-") if basename.startswith("essence-") else
                            basename.removeprefix("source-") if basename.startswith("source-") else basename)
                    items.append({"name": name, **preview})
                data = {**queue, "items": items}
                data["expected_sha256"] = sha256(json.dumps({
                    "authority_id": active_id, "principal_id": principal_id,
                    "cursor": payload.get("cursor"), "inventory_binding": queue["inventory_binding"],
                    "items": items}, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
                if len(json.dumps(data, ensure_ascii=False).encode("utf-8")) > 131_072:
                    return self._result("incomplete", "resource_exhausted",
                        "The ten-item preview exceeded its 128 KiB output ceiling.",
                        "Review an exact Candidate or reduce proposed text.",
                        {"items": [], "continuation": None, "expected_sha256": None,
                         "metadata_entries_examined": queue["metadata_entries_examined"],
                         "metadata_entry_limit": queue["metadata_entry_limit"]})
            except (ContractValidationError, OSError, KeyError, TypeError, ValueError):
                return self._result("stale", "candidate_queue_invalid",
                    "Candidate inventory changed or violates its bounded contract.",
                    "Repair malformed Candidates or restart the page.", {})
            return self._result("incomplete" if queue["continuation"] else "ok",
                "candidate_queue_partial" if queue["continuation"] else "candidate_queue_ready",
                "A bounded human review page is ready; no decision was applied.",
                "Review each proposed change and apply only the exact displayed page.", data)
        if operation == "candidate_open":
            candidate_id = payload.get("candidate_id")
            candidate_revision = payload.get("candidate_revision")
            if not (
                isinstance(candidate_id, str)
                and isinstance(candidate_revision, str)
                and _INITIAL_CANDIDATE_REVISION.fullmatch(candidate_revision)
                and principal.get("assurance") in {"local_owner", "local_operator"}
            ):
                return self._result(
                    "denied",
                    "owner_review_required",
                    "Candidate preview requires the current local Owner binding.",
                    "Open the Candidate through the local Owner path.",
                    {},
                )
            try:
                candidate, changeset_id = self._repository.read(
                    "candidate", active_id, {"candidate_id": candidate_id}
                )
                changeset = self._repository.read(
                    "changeset", active_id, {"changeset_id": changeset_id}
                )
                if not self._bundle_candidate_source_allowed(active_id, candidate, changeset, active_documents):
                    return self._result("denied", "source_access_denied",
                        "The issued Bundle selection is no longer authorized.",
                        "Reopen a Bundle using currently authorized sources.", {})
                result_document = changeset.get("result_document")
                result_sha256 = changeset.get("result_sha256")
                effects = changeset.get("effects")
                review_preview = candidate.get("review_preview")
                from .source_curation import validate_curation_effect
                validate_curation_effect(candidate, changeset)
                self._validate_current_global_curation(active_id, candidate, changeset)
                if candidate.get("named_case") is not None:
                    preview = self._named_case_review_preview(active_id, candidate, changeset, active_documents)
                    if candidate.get("candidate_revision") != candidate_revision or candidate.get("lifecycle") != "candidate":
                        raise ContractValidationError("named case Candidate is no longer initial")
                    return self._result("ok", "candidate_review_ready", "The exact Project answer is ready for Owner review.",
                                        "Approve or reject this bounded answer.", preview)
                expected_reviewed = "candidate-rev-2-reviewed" + candidate_revision.removeprefix("candidate-rev-1")
                reviewable = (
                    candidate.get("candidate_revision") == candidate_revision and candidate.get("lifecycle") == "candidate"
                ) or (
                    self._identity_profile == "mvp-v1"
                    and candidate.get("candidate_revision") == expected_reviewed
                    and candidate.get("lifecycle") == "reviewed"
                    and candidate.get("reviewed_result_sha256") == result_sha256
                )
                if not (
                    candidate.get("candidate_kind") in {"global_curation", "global_essence", "source_curation", "lesson_capture", "project_record", "project_essence"}
                    and reviewable
                    and isinstance(result_document, str)
                    and isinstance(result_sha256, str)
                    and sha256(result_document.encode("utf-8")).hexdigest()
                    == result_sha256
                    and isinstance(effects, list)
                    and len(effects) == 1
                    and isinstance(effects[0], dict)
                    and isinstance(review_preview, dict)
                    and review_preview.get("content_sha256") == result_sha256
                    and review_preview.get("target")
                    == str(effects[0].get("relative_path", "")).removeprefix(
                        ".owledge/"
                    )
                ):
                    raise ContractValidationError("Candidate review binding is invalid")
                result_metadata, result_body = parse_markdown_frontmatter(result_document)
                if candidate.get("candidate_kind") == "lesson_capture":
                    from .lesson_capture import validate_candidate_submitter
                    validate_candidate_submitter(candidate, active_id, result_document,
                        allow_legacy=authority.metadata.get("rights_era") != "owledge.bound-source-rights/1")
                if not self._candidate_source_allowed(candidate, changeset, active_id, principal_id):
                    return self._result("denied", "source_access_denied",
                        "The candidate source is not shared with this identity.",
                        "Ask the Owner for an explicit source grant.", {})
                expected_source = {
                    "artifact_id": result_metadata.get("source_artifact_id"),
                    "authority_id": result_metadata.get("source_authority_id"),
                    "revision": result_metadata.get("source_revision"),
                }
                if candidate.get("candidate_kind") == "global_curation" and candidate.get("contribution_binding") is not None:
                    expected_source = result_metadata.get("project_origin")
                if candidate.get("candidate_kind") in {"source_curation", "lesson_capture", "project_record", "project_essence", "global_essence"}:
                    expected_source = result_metadata.get("lesson_origin" if candidate.get("candidate_kind") == "lesson_capture" else
                                                          "record_origin" if candidate.get("candidate_kind") == "project_record" else
                                                          "concept_origin" if candidate.get("candidate_kind") in {"project_essence", "global_essence"} else "source_evidence")
                    if candidate.get("candidate_kind") == "global_essence":
                        expected_source = {"concept": result_metadata.get("concept_origin"),
                                           "project": result_metadata.get("project_origin")}
                    if (review_preview.get("idempotency_key") != changeset.get("idempotency_key")
                            or review_preview.get("expected_policy_revision") != changeset.get("policy_revision")
                            or review_preview.get("expected_settings_revision") != changeset.get("settings_revision")):
                        raise ContractValidationError("Candidate expected state preview is stale")
                if not (
                    review_preview.get("proposed_text") == result_body.strip()
                    and review_preview.get("source") == expected_source
                ):
                    raise ContractValidationError("Candidate review preview is stale")
            except (ContractValidationError, OSError):
                return self._result(
                    "stale",
                    "candidate_revision_mismatch",
                    "The Candidate preview is missing, changed, or no longer reviewable.",
                    "Recreate and reopen the bounded Candidate.",
                    {},
                )
            return self._result(
                "ok",
                "candidate_review_ready",
                "The exact nonfactual Project record is ready for recording review."
                if candidate.get("candidate_kind") == "project_record" else
                "The exact proposed global knowledge is ready for Owner review.",
                "Approve or reject this content-bound Candidate; recording approval is not factual approval."
                if candidate.get("candidate_kind") == "project_record" else
                "Approve or reject this content-bound Candidate.",
                dict(review_preview),
            )
        if cross_authority_contribution:
            # Real workspace binding narrows this private path; accepted Source
            # Links remain the underlying authority for legacy Core callers.
            from .project_io import _reuse_read, validate_project_reuse_binding
            try:
                state_raw = _reuse_read(active_root.parent, "workspace.json")
                reuse_state = json.loads(state_raw) if state_raw else {}
                real_project_reuse = reuse_state.get("schema") == "owledge.private-project-workspace/2"
                if real_project_reuse:
                    bound_target = validate_project_reuse_binding(active_root.parent, reuse_state)
                    if (reuse_state["authority_id"] != active_id
                            or self._root_for_authority(str(target_authority_id)).resolve() != bound_target / "global"
                            or command.get("source_link_id") != reuse_state["global_contribution"]["source_link_id"]
                            or set(payload) != {"source_artifact_id", "expected_source_revision", "expected_source_sha256", "preview"}
                            or type(payload["preview"]) is not bool):
                        raise ContractValidationError("exact contribution binding is required")
            except (ContractValidationError, OSError, ValueError, AttributeError):
                return self._result("denied", "contribution_binding_invalid", "The Project contribution binding changed.", "Inspect or restore the Owner-approved binding.", {})
            source_links = [
                item
                for item in active_documents
                if item.metadata.get("schema") == "owledge.knowledge-source-link/1"
                and item.metadata.get("lifecycle") == "accepted"
                and item.metadata.get("source_link_id") == command.get("source_link_id")
                and item.metadata.get("linked_authority_id") == target_authority_id
                and isinstance(item.metadata.get("grants"), list)
                and "contribute" in item.metadata["grants"]
            ]
            if len(source_links) != 1:
                return self._result(
                    "denied",
                    "capability_denied",
                    "This identity may not contribute through that authority bridge.",
                    "Use one accepted Source Link with matching contribution grants.",
                    {},
                )
            try:
                target_authority = self._repository.bootstrap(
                    str(target_authority_id)
                )
            except (ContractValidationError, OSError):
                target_authority = None
            if not (
                target_authority is not None
                and target_authority.authority_id.startswith("user-global:")
                and (has_grant(target_authority, principal_id, "contribute")
                     or owner_essence_contribution and has_grant(target_authority, principal_id, "promote"))
            ):
                return self._result(
                    "denied",
                    "capability_denied",
                    "This identity may not contribute through that authority bridge.",
                    "Use one accepted Source Link with matching contribution grants.",
                    {},
                )
            if not _write_locks_held and self._identity_profile == "mvp-v1":
                if payload.get("preview") is True:
                    # Preview never completes pending effects or writes receipts.
                    with authority_write_locks((active_root, self._root_for_authority(str(target_authority_id)))):
                        return self._execute(command, trusted_assurance=trusted_assurance, _write_locks_held=True)
                return self._execute_with_write_locks(
                    command, trusted_assurance,
                    (active_root, self._root_for_authority(str(target_authority_id))),
                )
        if operation == "contribute_for_reuse":
            source_artifact_id = payload.get("source_artifact_id")
            expected_source_revision = payload.get("expected_source_revision")
            operation_id = command.get("operation_id")
            matches = [
                item
                for item in active_documents
                if item.artifact_id == source_artifact_id
            ]
            if not (
                cross_authority_contribution
                and isinstance(operation_id, str)
                and isinstance(source_artifact_id, str)
                and isinstance(expected_source_revision, str)
                and len(matches) == 1
                and matches[0].revision == expected_source_revision
                and matches[0].metadata.get("lifecycle") == "accepted"
            ):
                return self._result(
                    "invalid",
                    "contribution_source_invalid",
                    "The reusable Project record is missing or no longer at the expected revision.",
                    "Select one accepted typed Project record at its current revision.",
                    {},
                )
            if real_project_reuse or "expected_source_sha256" in payload or payload.get("preview") is True:
                from .source_curation import reference_data
                try:
                    if isinstance(matches[0].metadata.get("knowledge_kind"), str) and matches[0].metadata["knowledge_kind"] in {"idea", "finding"}:
                        from .lesson_capture import validate_project_record
                        validate_project_record(matches[0])
                        lesson = {"artifact_id": matches[0].artifact_id, "revision": matches[0].revision,
                                  "content_sha256": matches[0].content_sha256, "text": matches[0].body.strip(),
                                  "knowledge_kind": matches[0].metadata["knowledge_kind"], "canonical": False,
                                  "record_status": matches[0].metadata["record_status"],
                                  "knowledge_area": matches[0].metadata["knowledge_area"]}
                    elif matches[0].metadata.get("knowledge_kind") == "project_essence":
                        from .lesson_capture import validate_project_essence, essence_origin
                        validate_project_essence(matches[0])
                        binding, current = self._current_project_concept(active_id, principal_id)
                        if not current or matches[0].metadata["concept_origin"] != essence_origin(binding):
                            raise ContractValidationError("Project Essence concept source changed")
                        lesson = {"artifact_id": matches[0].artifact_id, "revision": matches[0].revision,
                                  "content_sha256": matches[0].content_sha256, "text": matches[0].body.strip(),
                                  "knowledge_kind": "project_essence", "canonical": False,
                                  "record_status": "summary", "knowledge_area": matches[0].metadata["knowledge_area"]}
                    else:
                        lesson = reference_data((matches[0],), source_artifact_id)
                        if not lesson or lesson.get("knowledge_kind") != "lesson":
                            raise ContractValidationError("accepted Lesson changed after preview")
                    if matches[0].content_sha256 != payload.get("expected_source_sha256"):
                        raise ContractValidationError("accepted Project record changed after preview")
                except ContractValidationError:
                    return self._result("stale", "contribution_source_changed", "The accepted Project record changed after preview.", "Read and preview its exact revision again.", {})
                if payload.get("preview") is True:
                    return self._result("ok", "contribution_preview_ready", "Exact reviewed Project record ready for noncanonical contribution.",
                        "Apply or cancel this contribution; registration is not content approval.",
                        {"source": lesson, "source_authority_id": active_id, "target_authority_id": target_authority_id,
                         "operation_id": operation_id, "canonical": False})
            try:
                contributed, receipt_id = self._repository.apply(
                    "contribute_for_reuse",
                    str(target_authority_id),
                    {
                        "authority_id": str(target_authority_id),
                        "operation_id": operation_id,
                        "source": matches[0],
                    },
                )
                self._repository.apply("trace_record", str(target_authority_id), {
                    "authority_id": str(target_authority_id),
                    "event": {"event": "contribution_recorded", "authority_id": str(target_authority_id),
                              "principal_id": principal_id, "assurance": principal.get("assurance"),
                              "base_revision": "absent", "result_revision": contributed["revision"],
                              "outcome": "ok/contribution_recorded", "receipt_id": receipt_id},
                })
            except (ContractValidationError, OSError):
                return self._result(
                    "conflict",
                    "contribution_conflict",
                    "The reuse contribution could not be recorded consistently.",
                    "Inspect the existing contribution and retry with its original binding.",
                    {},
                )
            return self._result(
                "ok",
                "contribution_recorded",
                "Attributable Project evidence was added to the noncanonical global feed.",
                "A global maintainer may propose eligible evidence for Owner curation.",
                contributed,
                receipt_id=receipt_id,
            )
        if operation == "curate_candidate":
            contribution_ids = payload.get("contribution_ids")
            curation_slug = payload.get("curation_slug")
            operation_id = command.get("operation_id")
            exact_fields = {"contribution_ids", "curation_slug", "expected_contribution_revision", "expected_contribution_sha256"}
            refresh = set(payload) == exact_fields | {"replacement_base"}
            exact = set(payload) == exact_fields or refresh
            legacy = set(payload) == {"contribution_ids", "curation_slug"}
            replacement_base = payload.get("replacement_base")
            valid_replacement = (not refresh or (isinstance(replacement_base, dict)
                and set(replacement_base) == {"artifact_id", "revision", "content_sha256"}
                and all(isinstance(replacement_base.get(key), str) and replacement_base[key] for key in replacement_base)
                and re.fullmatch(r"[0-9a-f]{64}", replacement_base["content_sha256"])))
            if not (
                active_id.startswith("user-global:")
                and target_authority_id == active_id
                and isinstance(operation_id, str)
                and isinstance(contribution_ids, list)
                and len(contribution_ids) == 1
                and isinstance(contribution_ids[0], str)
                and isinstance(curation_slug, str)
                and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", curation_slug)
                and (legacy or exact)
                and valid_replacement
                and (not exact or (curation_slug.startswith("lesson-") and len(curation_slug.removeprefix("lesson-")) <= 80))
            ):
                return self._result(
                    "invalid",
                    "curation_input_invalid",
                    "The bounded global curation request is incomplete.",
                    "Choose one eligible Reuse Feed contribution and a stable slug.",
                    {},
                )
            matches = [
                item
                for item in active_documents
                if item.artifact_id == contribution_ids[0]
                and item.metadata.get("schema") == "owledge.reuse-contribution/1"
                and item.metadata.get("stage") == "reuse_feed"
                and item.metadata.get("canonical") is False
                and item.metadata.get("lifecycle") == "candidate"
                and item.metadata.get("knowledge_kind") == "lesson"
                and item.metadata.get("source_record_trust") == "internal"
                and item.metadata.get("source_processing_layer") == "condensed"
                and all(
                    isinstance(item.metadata.get(field), str)
                    and bool(str(item.metadata.get(field)))
                    for field in (
                        "source_artifact_id",
                        "source_authority_id",
                        "source_revision",
                        "source_content_sha256",
                        "source_record_trust",
                        "source_processing_layer",
                        "source_relative_path",
                    )
                )
                and str(item.metadata.get("source_authority_id", "")).startswith(
                    "project:"
                )
            ]
            project_origin = None
            global_base = None
            refresh_replay_only = False
            if exact:
                from .source_curation import project_lesson_contribution, validate_global_reuse_lesson
                try:
                    current = self._repository.read("reuse_contribution", active_id, {
                        "authority_id": active_id, "contribution_id": contribution_ids[0]})
                    if (current is None or current.revision != payload.get("expected_contribution_revision")
                            or current.content_sha256 != payload.get("expected_contribution_sha256")):
                        raise ContractValidationError("selected Contribution changed")
                    project_origin = project_lesson_contribution(current)
                    matches = [current]
                    if refresh:
                        expected_artifact = f"memory:{active_id.replace(':', '-')}-{curation_slug}"
                        global_base = self._repository.read("curated_reference", active_id, {
                            "authority_id": active_id, "artifact_id": expected_artifact})
                        current_binding = (None if global_base is None else {"artifact_id": global_base.artifact_id,
                                           "revision": global_base.revision, "content_sha256": global_base.content_sha256})
                        if replacement_base != current_binding:
                            global_base = self._repository.read("curated_reference", active_id, {
                                "authority_id": active_id, "artifact_id": expected_artifact,
                                "revision": replacement_base["revision"]})
                            if (global_base is None or replacement_base != {"artifact_id": global_base.artifact_id,
                                    "revision": global_base.revision, "content_sha256": global_base.content_sha256}):
                                raise ContractValidationError("Global replacement base changed")
                            refresh_replay_only = True
                        validate_global_reuse_lesson(global_base)
                except (ContractValidationError, OSError):
                    reason = "global_base_changed" if refresh else "curation_source_changed"
                    return self._result("stale", reason,
                                        "The current Global Lesson base or selected Project Lesson Contribution changed or is invalid.",
                                        "Read both current exact bindings before proposing the refresh.", {})
            if len(matches) != 1:
                return self._result(
                    "invalid",
                    "curation_source_invalid",
                    "The selected evidence is not eligible for this bounded curation flow.",
                    "Select one current noncanonical Lesson from the Reuse Feed.",
                    {},
                )
            source = matches[0]
            if "knowledge_area" in source.metadata:
                area = source.metadata["knowledge_area"]
                if (not isinstance(area, str) or not area.strip() or len(area) > 80
                        or any(ord(char) < 32 or char in "\x85\u2028\u2029" for char in area)):
                    return self._result("invalid", "curation_source_invalid", "The Lesson Area is invalid.",
                                        "Repair the source classification before curation.", {})
            from .source_curation import build_global_curation_candidate
            candidate, changeset = build_global_curation_candidate(
                active_id,
                authority,
                source,
                curation_slug,
                contribution_ids,
                project_origin,
                global_base,
                replacement_base if isinstance(replacement_base, dict) else {},
            )
            candidate_id = candidate["candidate_id"]
            candidate_revision = candidate["candidate_revision"]
            review_preview = candidate["review_preview"]
            idempotency_key = changeset["idempotency_key"]
            result_document = changeset["result_document"]
            result_sha256 = changeset["result_sha256"]
            if exact and len(result_document.encode("utf-8")) > 65_536:
                return self._result("invalid", "curation_result_too_large", "The curated Lesson exceeds its bounded read contract.",
                                    "Choose one bounded Lesson without changing its body.", {})
            if global_base is not None:
                try:
                    from .source_curation import validate_global_reuse_transition
                    result = parse_managed_markdown(changeset["effects"][0]["relative_path"], result_document,
                                                    encoded_document=result_document.encode("utf-8"))
                    validate_global_reuse_transition(global_base, result)
                except ContractValidationError:
                    return self._result("invalid", "curation_origin_changed", "The Global Lesson refresh retargets Project provenance.",
                                        "Refresh only from another reviewed snapshot of the same Project Lesson.", {})
            if refresh_replay_only:
                try:
                    existing_candidate, existing_changeset_id = self._repository.read(
                        "candidate", active_id, {"candidate_id": candidate_id})
                    existing_changeset = self._repository.read(
                        "changeset", active_id, {"changeset_id": existing_changeset_id})
                    if (existing_candidate.get("candidate_id") != candidate_id
                            or existing_changeset.get("result_sha256") != result_sha256):
                        raise ContractValidationError("Historical refresh is not an exact replay")
                except (ContractValidationError, OSError):
                    return self._result("stale", "global_base_changed", "The selected Global base is no longer current.",
                                        "Use the current exact base; historical bases are accepted only for exact operation replay.", {})
            try:
                receipt_id = self._repository.apply(
                    "candidate_preview",
                    active_id,
                    {
                        "authority_id": active_id,
                        "operation_id": operation_id,
                        "candidate": candidate,
                        "changeset": changeset,
                    },
                )
            except (ContractValidationError, OSError):
                return self._result(
                    "conflict",
                    "curation_conflict",
                    "The global Curation Candidate could not be staged consistently.",
                    "Reuse the original candidate binding or choose a new curation slug.",
                    {},
                )
            return self._result(
                "ok",
                "curation_candidate_ready",
                "One global Curation Candidate is ready for Owner review.",
                "Approve or reject this exact Candidate revision through the local Owner path.",
                {
                    "candidate_id": candidate_id,
                    "candidate_revision": candidate_revision,
                    "idempotency_key": idempotency_key,
                    "contribution_ids": list(contribution_ids),
                    "review_preview": review_preview,
                },
                receipt_id=receipt_id,
            )
        if operation == "recover":
            changeset_id = payload.get("changeset_id")
            operation_id = command.get("operation_id")
            if not (
                isinstance(changeset_id, str)
                and isinstance(operation_id, str)
                and principal.get("assurance") == "local_owner"
            ):
                return self._result(
                    "denied",
                    "owner_recovery_required",
                    "Recovery requires the current local Owner binding.",
                    "Use the separate local Owner recovery path.",
                    {},
                )
            try:
                changeset = self._repository.read(
                    "changeset", active_id, {"changeset_id": changeset_id}
                )
                recovered, receipt_id = self._repository.apply(
                    "recover",
                    active_id,
                    {
                        "authority_id": active_id,
                        "operation_id": operation_id,
                        "changeset_id": changeset_id,
                        "changeset": changeset,
                        "identity_profile": self._identity_profile,
                    },
                )
            except (ContractValidationError, OSError):
                return self._result(
                    "recovery_required",
                    "recovery_state_invalid",
                    "The interrupted ChangeSet cannot be recovered automatically.",
                    "Inspect the transaction intent and canonical target state.",
                    {},
                )
            committed = recovered.get("recovered_phase") == "canonical_effect_visible"
            return self._result(
                "ok",
                "recovered_commit" if committed else "recovered_rollback",
                "The exact visible canonical write and Trace were completed." if committed else "The incomplete canonical write was rolled back.",
                "Inspect the recovered receipt." if committed else "Retry promotion from the reviewed Candidate if still required.",
                recovered,
                receipt_id=receipt_id,
            )
        if operation == "trace_read":
            receipt_id = payload.get("receipt_id")
            if not isinstance(receipt_id, str):
                return self._result(
                    "invalid",
                    "command_invalid",
                    "The Trace request is incomplete.",
                    "Provide one lifecycle receipt identity.",
                    {},
                )
            try:
                trace = self._repository.read(
                    "trace",
                    active_id,
                    {"authority_id": active_id, "receipt_id": receipt_id},
                )
            except (ContractValidationError, OSError):
                return self._result(
                    "invalid",
                    "trace_invalid",
                    "No valid lifecycle Trace contains this receipt.",
                    "Use a receipt from the active Project authority.",
                    {},
                )
            return self._result(
                "ok",
                "trace_ready",
                "The content-minimized lifecycle Trace is ready.",
                "Inspect the ordered events and linked receipts.",
                trace,
            )
        if operation == "gap_verify":
            gap_id = payload.get("gap_id")
            coverage_case_id = payload.get("coverage_case_id")
            expected_gap_revision = payload.get("expected_gap_revision")
            operation_id = command.get("operation_id")
            clock = self._clock.now()
            if not (
                isinstance(gap_id, str)
                and isinstance(coverage_case_id, str)
                and isinstance(expected_gap_revision, str)
                and isinstance(operation_id, str)
                and isinstance(clock, str)
                and principal.get("assurance") == "local_owner"
            ):
                return self._result(
                    "denied",
                    "owner_verification_required",
                    "Gap closure requires the current local Owner binding.",
                    "Use the local Owner path with the expected Gap revision.",
                    {},
                )
            try:
                replay = self._repository.read(
                    "gap_closure_replay",
                    active_id,
                    {
                        "authority_id": active_id,
                        "operation_id": operation_id,
                        "gap_id": gap_id,
                        "expected_gap_revision": expected_gap_revision,
                        "approved_by_user": principal_id,
                    },
                )
            except (ContractValidationError, OSError):
                return self._result(
                    "invalid",
                    "operation_replay_mismatch",
                    "The operation identity is already bound to another effect.",
                    "Use the original effect binding or a new operation identity.",
                    {},
                )
            if replay is not None:
                closed, receipt_id = replay
                self._repository.apply("trace_record", active_id, {
                    "authority_id": active_id,
                    "event": {"event": "gap_closed", "authority_id": active_id,
                              "principal_id": principal_id, "assurance": principal.get("assurance"),
                              "base_revision": expected_gap_revision, "result_revision": closed["gap_revision"],
                              "outcome": "ok/gap_closed", "receipt_id": receipt_id},
                })
                return self._result(
                    "ok",
                    "gap_closed",
                    "Fresh Project evidence covers the Gap.",
                    "Use the verified canonical knowledge.",
                    closed,
                    receipt_id=receipt_id,
                )
            try:
                gap = self._repository.read("gap", active_id, {"gap_id": gap_id})
            except (ContractValidationError, OSError):
                return self._result(
                    "invalid",
                    "gap_invalid",
                    "The requested Gap is missing or invalid.",
                    "Retrieve current Gap state before verification.",
                    {},
                )
            if not (
                gap.get("revision") == expected_gap_revision
                and gap.get("lifecycle") == "open"
                and gap.get("coverage_case_id") == coverage_case_id
            ):
                return self._result(
                    "stale",
                    "gap_revision_mismatch",
                    "The Gap no longer matches the expected open revision.",
                    "Retrieve current Gap state before verification.",
                    {},
                )
            coverage = self._assess_coverage(active_documents, coverage_case_id)
            if coverage is None or coverage.assessment.get("assessment") != "coverage_satisfied":
                return self._result(
                    "incomplete",
                    "coverage_not_satisfied",
                    "Fresh Project evidence does not yet cover the Gap.",
                    "Keep the Gap open and supply the required evidence.",
                    {},
                )
            try:
                closed, receipt_id = self._repository.apply(
                    "gap_close",
                    active_id,
                    {
                        "authority_id": active_id,
                        "operation_id": operation_id,
                        "gap": gap,
                        "expected_gap_revision": expected_gap_revision,
                        "resolved_at": clock,
                        "approved_by_user": principal_id,
                    },
                )
                self._repository.apply(
                    "trace_record",
                    active_id,
                    {
                        "authority_id": active_id,
                        "event": {
                        "event": "gap_closed",
                        "authority_id": active_id,
                        "principal_id": principal_id,
                        "assurance": principal.get("assurance"),
                        "base_revision": expected_gap_revision,
                        "result_revision": closed["gap_revision"],
                        "outcome": "ok/gap_closed",
                        "receipt_id": receipt_id,
                        },
                    },
                )
            except (ContractValidationError, OSError):
                return self._result(
                    "recovery_required",
                    "gap_effect_inconsistent",
                    "The Gap closure could not be applied consistently.",
                    "Inspect and recover the bounded Core effect.",
                    {},
                )
            return self._result(
                "ok",
                "gap_closed",
                "Fresh Project evidence covers the Gap.",
                "Use the verified canonical knowledge.",
                closed,
                receipt_id=receipt_id,
            )
        if operation == "candidate_promote":
            candidate_id = payload.get("candidate_id")
            candidate_revision = payload.get("candidate_revision")
            expected_base = payload.get("expected_base_revision")
            expected_policy = payload.get("expected_policy_revision")
            expected_settings = payload.get("expected_settings_revision")
            idempotency_key = payload.get("idempotency_key")
            operation_id = command.get("operation_id")
            if not (
                isinstance(candidate_id, str)
                and isinstance(candidate_revision, str)
                and _REVIEWED_CANDIDATE_REVISION.fullmatch(candidate_revision)
                and isinstance(expected_base, str) and bool(expected_base)
                and expected_policy == authority.metadata.get("policy_revision")
                and expected_settings == authority.metadata.get("settings_revision")
                and isinstance(idempotency_key, str)
                and isinstance(operation_id, str)
                and principal.get("assurance") in {"local_owner", "local_operator"}
            ):
                return self._result(
                    "denied",
                    "owner_promotion_required",
                    "Canonical promotion requires the current local Owner binding.",
                    "Use the local Owner path with current expected revisions.",
                    {},
                )
            try:
                candidate, changeset_id = self._repository.read(
                    "candidate", active_id, {"candidate_id": candidate_id}
                )
                changeset = self._repository.read(
                    "changeset", active_id, {"changeset_id": changeset_id}
                )
                if (
                    candidate.get("candidate_revision") != candidate_revision
                    or changeset.get("base_revision") != expected_base
                    or changeset.get("policy_revision") != expected_policy
                    or changeset.get("settings_revision") != expected_settings
                    or changeset.get("idempotency_key") != idempotency_key
                    or (
                        (candidate.get("candidate_kind") in {"global_curation", "global_essence", "source_curation", "lesson_capture", "project_record", "project_essence"}
                         or candidate.get("named_case") is not None)
                        and candidate.get("reviewed_result_sha256")
                        != changeset.get("result_sha256")
                    )
                ):
                    raise ContractValidationError("promotion expected state does not match")
                self._validate_current_global_curation(active_id, candidate, changeset)
                if candidate.get("named_case") is not None:
                    self._named_case_review_preview(active_id, candidate, changeset, active_documents)
                if not self._bundle_candidate_source_allowed(active_id, candidate, changeset, active_documents):
                    return self._result("denied", "source_access_denied",
                        "The issued Bundle selection is no longer authorized.",
                        "Reopen a Bundle using currently authorized sources.", {})
                if candidate.get("candidate_kind") == "lesson_capture":
                    from .lesson_capture import validate_candidate_submitter
                    validate_candidate_submitter(candidate, active_id, changeset["result_document"],
                        allow_legacy=authority.metadata.get("rights_era") != "owledge.bound-source-rights/1")
                if not self._candidate_source_allowed(candidate, changeset, active_id, principal_id):
                    return self._result("denied", "source_access_denied",
                        "The candidate source is not shared with this identity.",
                        "Ask the Owner for an explicit source grant.", {})
                promoted, receipt_id = self._repository.apply(
                    "candidate_promote",
                    active_id,
                    {
                        "authority_id": active_id,
                        "operation_id": operation_id,
                        "candidate": candidate,
                        "changeset": changeset,
                        "promoted_by": principal_id if self._identity_profile == "mvp-v1" else None,
                    },
                )
                effects = changeset["effects"]
                self._repository.apply(
                    "trace_record",
                    active_id,
                    {
                        "authority_id": active_id,
                        "event": {
                        "event": "candidate_promoted",
                        "authority_id": active_id,
                        "principal_id": principal_id,
                        "assurance": principal.get("assurance"),
                        "base_revision": changeset["base_revision"],
                        "result_revision": effects[0]["result_revision"],
                        "outcome": "ok/candidate_promoted",
                        "receipt_id": receipt_id,
                        "promoted_by": principal_id,
                        "candidate_revision": candidate["candidate_revision"],
                        },
                    },
                )
            except (ContractValidationError, OSError):
                return self._result(
                    "conflict",
                    "revision_conflict",
                    "The reviewed Candidate no longer matches canonical expected state.",
                    "Reopen the Candidate and current authority revisions.",
                    {},
                )
            return self._result(
                "ok",
                "candidate_promoted",
                "The reviewed possibility or signal was recorded as noncanonical Project knowledge."
                if candidate.get("candidate_kind") == "project_record" else
                "The reviewed Candidate was promoted to canonical knowledge in the active authority.",
                "Use the exact typed record; it is not factual coverage."
                if candidate.get("candidate_kind") == "project_record" else
                "Use the canonical record at its returned revision.",
                promoted,
                receipt_id=receipt_id,
            )
        if operation == "candidate_review":
            candidate_id = payload.get("candidate_id")
            candidate_revision = payload.get("candidate_revision")
            decision = payload.get("decision")
            expected_result_sha256 = payload.get("expected_result_sha256")
            operation_id = command.get("operation_id")
            if not (
                isinstance(candidate_id, str)
                and isinstance(candidate_revision, str)
                and _INITIAL_CANDIDATE_REVISION.fullmatch(candidate_revision)
                and decision in {"approve", "reject"}
                and isinstance(operation_id, str)
                and principal.get("assurance") in {"local_owner", "local_operator"}
            ):
                return self._result(
                    "denied",
                    "owner_review_required",
                    "Candidate approval requires the declared local Owner path.",
                    "Ask the local Owner to approve this Candidate revision.",
                    {},
                )
            try:
                candidate, changeset_id = self._repository.read(
                    "candidate", active_id, {"candidate_id": candidate_id}
                )
                current_revision = candidate.get("candidate_revision")
                expected_reviewed_revision = (
                    "candidate-rev-2-reviewed"
                    + candidate_revision.removeprefix("candidate-rev-1")
                )
                if not (
                    isinstance(current_revision, str)
                    and current_revision in {candidate_revision, expected_reviewed_revision}
                ):
                    raise ContractValidationError("Candidate revision does not match")
                if candidate.get("contribution_binding") is not None:
                    bound_changeset = self._repository.read(
                        "changeset", active_id, {"changeset_id": changeset_id}
                    )
                    self._validate_current_global_curation(active_id, candidate, bound_changeset)
                if candidate.get("named_case") is not None:
                    bound_changeset = self._repository.read("changeset", active_id, {"changeset_id": changeset_id})
                    self._named_case_review_preview(active_id, candidate, bound_changeset, active_documents)
                if decision == "reject":
                    if current_revision != candidate_revision:
                        raise ContractValidationError("reviewed Candidate cannot be rejected")
                    return self._result(
                        "ok",
                        "candidate_rejected",
                        "The local Owner rejected the staged Candidate without canonical effect.",
                        "Leave the source evidence noncanonical or create a new bounded Candidate.",
                        {
                            "candidate_id": candidate_id,
                            "candidate_revision": candidate_revision,
                            "lifecycle": "candidate",
                            "decision": "reject",
                        },
                    )
                changeset = self._repository.read(
                    "changeset", active_id, {"changeset_id": changeset_id}
                )
                if not self._bundle_candidate_source_allowed(active_id, candidate, changeset, active_documents):
                    return self._result("denied", "source_access_denied",
                        "The issued Bundle selection is no longer authorized.",
                        "Reopen a Bundle using currently authorized sources.", {})
                review_preview = candidate.get("review_preview")
                result_document = changeset.get("result_document")
                actual_result_sha256 = changeset.get("result_sha256")
                if (candidate.get("candidate_kind") in {"global_curation", "global_essence", "source_curation", "lesson_capture", "project_record", "project_essence"}
                    or candidate.get("named_case") is not None) and not (
                    isinstance(expected_result_sha256, str)
                    and isinstance(actual_result_sha256, str)
                    and expected_result_sha256 == actual_result_sha256
                    and isinstance(result_document, str)
                    and sha256(result_document.encode("utf-8")).hexdigest()
                    == actual_result_sha256
                    and (candidate.get("named_case") is not None or
                         isinstance(review_preview, dict) and review_preview.get("content_sha256") == actual_result_sha256)
                ):
                    raise ContractValidationError("reviewed content binding does not match")
                from .source_curation import validate_curation_effect
                validate_curation_effect(candidate, changeset)
                if candidate.get("candidate_kind") in {"source_curation", "lesson_capture", "project_record", "project_essence", "global_essence"} or candidate.get("named_case") is not None:
                    opened = self._execute({**command, "operation": "candidate_open", "payload": {
                        "candidate_id": candidate_id, "candidate_revision": candidate_revision}},
                        trusted_assurance=trusted_assurance, _write_locks_held=True,
                        operator_name=operator_name, operator_workspace=operator_workspace)
                    if opened.get("reason_code") != "candidate_review_ready":
                        raise ContractValidationError("source review preview no longer matches")
                reviewed, receipt_id = self._repository.apply(
                    "candidate_review",
                    active_id,
                    {
                        "authority_id": active_id,
                        "operation_id": operation_id,
                        "candidate": candidate,
                        "changeset_id": changeset_id,
                        "reviewed_by": principal_id,
                        "reviewed_result_sha256": (
                            actual_result_sha256
                            if candidate.get("candidate_kind") in {"global_curation", "global_essence", "source_curation", "lesson_capture", "project_record", "project_essence"}
                            or candidate.get("named_case") is not None
                            else None
                        ),
                    },
                )
                self._repository.apply(
                    "trace_record",
                    active_id,
                    {
                        "authority_id": active_id,
                        "event": {
                        "event": "candidate_reviewed",
                        "authority_id": active_id,
                        "principal_id": principal_id,
                        "assurance": principal.get("assurance"),
                        "base_revision": candidate_revision,
                        "result_revision": reviewed["candidate_revision"],
                        "outcome": "ok/candidate_approved",
                        "receipt_id": receipt_id,
                        "reviewed_by": principal_id,
                        },
                    },
                )
            except (ContractValidationError, OSError):
                return self._result(
                    "stale",
                    "candidate_revision_mismatch",
                    "The Candidate is missing or no longer at the expected revision.",
                    "Reopen the current Candidate before review.",
                    {},
                )
            return self._result(
                "ok",
                "candidate_approved",
                "The local Owner approved the staged Candidate.",
                "Promote the reviewed Candidate through the local Owner path.",
                {
                    "candidate_id": reviewed["candidate_id"],
                    "candidate_revision": reviewed["candidate_revision"],
                    "lifecycle": reviewed["lifecycle"],
                    "reviewed_by": reviewed["reviewed_by"],
                },
                receipt_id=receipt_id,
            )
        if operation == "case_correct":
            from .lifecycle import preview_named_case_correction
            from .contracts import evidence_value_matches
            operation_id = command.get("operation_id")
            name, value = payload.get("case_name"), payload.get("text")
            expected_revision, expected_sha256 = payload.get("expected_revision"), payload.get("expected_sha256")
            if (not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
                    or not isinstance(operation_id, str) or not isinstance(value, str) or not isinstance(expected_revision, str)
                    or not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256)):
                return self._result("invalid", "command_invalid", "Exact case correction is incomplete.",
                                    "Use a current answer revision and hash.", {})
            registries = [item for item in active_documents if item.metadata.get("schema") == "owledge.coverage-case-registry/1"]
            routings = [item for item in active_documents if item.metadata.get("schema") == "owledge.artifact-routing/1"]
            if len(registries) != 1 or len(routings) != 1:
                return self._result("invalid", "case_invalid", "Project case controls are invalid.", "Repair the Project case.", {})
            case = registries[0].metadata.get("coverage_cases", {}).get(f"coverage:{name}")
            provider = registries[0].metadata.get("provider_contracts", {}).get(f"provider:{name}")
            route = routings[0].metadata.get("routes", {}).get(f"route:{name}")
            if (not all(isinstance(item, dict) for item in (case, provider, route))
                    or case.get("case_name") != name or route.get("case_name") != name
                    or route.get("value_contract") != provider.get("value_contract")
                    or route.get("write_mode") != "create_or_exact_replace"
                    or not evidence_value_matches(value, provider.get("value_contract"))):
                return self._result("invalid", "case_invalid", "Project case contract is invalid.", "Repair the Project case.", {})
            current = [item for item in active_documents if item.artifact_id == route.get("target_artifact_id")]
            coverage = self._assess_coverage(active_documents, f"coverage:{name}")
            context = [item for item in active_documents if item.artifact_id == case.get("context_artifact_id")]
            if (coverage is None or coverage.assessment.get("assessment") != "coverage_satisfied"
                    or len(context) != 1):
                return self._result("stale", "case_selection_changed", "Current case selection is not valid.",
                                    "Ask the configured case again.", {})
            if len(current) != 1 or current[0].revision != expected_revision or current[0].content_sha256 != expected_sha256:
                return self._result("stale", "correction_base_changed", "Accepted answer changed.",
                                    "Ask again and use its exact revision and hash.", {})
            try:
                candidate, changeset = preview_named_case_correction(authority_id=active_id, name=name,
                    old=current[0], route=route, value=value, operation_id=str(operation_id),
                    submitted_by=principal_id, policy_revision=str(authority.metadata["policy_revision"]),
                    settings_revision=str(authority.metadata["settings_revision"]))
                selection = {"source_snapshot_id": coverage.assessment.get("source_snapshot_id"),
                             "context_artifact_id": context[0].artifact_id,
                             "context_revision": context[0].revision,
                             "context_sha256": context[0].content_sha256}
                candidate["selection_binding"] = selection
                changeset["selection_binding"] = selection
                receipt_id = self._repository.apply("candidate_preview", active_id, {
                    "authority_id": active_id, "operation_id": operation_id,
                    "candidate": candidate, "changeset": changeset})
            except (ContractValidationError, LifecycleValidationError, OSError, ValueError):
                return self._result("conflict", "case_correction_conflict", "Case correction could not be staged.",
                                    "Reopen the current answer.", {})
            return self._result("ok", "candidate_ready", "Exact-base correction staged for Owner review.",
                                "Open this Candidate through local Owner review.",
                                {"candidate": candidate, "changeset": changeset}, receipt_id=receipt_id)
        if operation == "bundle_preview":
            edited_bundle = payload.get("bundle_markdown")
            content_origin = payload.get("content_origin")
            operation_id = command.get("operation_id")
            reported = principal.get("reported")
            adapter_observed = principal.get("adapter_observed")
            clock = self._clock.now()
            if not (
                isinstance(edited_bundle, str)
                and isinstance(content_origin, str)
                and isinstance(operation_id, str)
                and isinstance(reported, dict)
                and isinstance(adapter_observed, dict)
                and isinstance(clock, str)
            ):
                return self._result(
                    "invalid",
                    "command_invalid",
                    "The Bundle preview request is incomplete.",
                    "Provide the edited Bundle and attributable content origin.",
                    {},
                )
            frontmatter = edited_bundle[4:].split("\n---\n", 1)[0] if edited_bundle.startswith("---\n") else ""
            bundle_identity_count = sum(
                line.split(":", 1)[0].strip() == "bundle_id"
                for line in frontmatter.splitlines()
                if ":" in line
            )
            if bundle_identity_count != 1:
                reason = (
                    "bundle_identity_duplicate"
                    if bundle_identity_count > 1
                    else "bundle_identity_missing"
                )
                return self._result(
                    "invalid",
                    reason,
                    "The edited Bundle identity is missing or duplicated.",
                    "Restore the single Core-issued Bundle identity and retry.",
                    {},
                )
            try:
                bundle_metadata, _ = parse_markdown_frontmatter(edited_bundle)
                bundle_id = bundle_metadata.get("bundle_id")
                route_id = bundle_metadata.get("resolution_route_id")
                coverage_case_id = bundle_metadata.get("coverage_case_id")
                if not (
                    isinstance(bundle_id, str)
                    and isinstance(route_id, str)
                    and isinstance(coverage_case_id, str)
                ):
                    raise ContractValidationError("Bundle identity or route is missing")
                original_bundle = self._repository.read(
                    "bundle", active_id, {"bundle_id": bundle_id}
                )
                original_metadata, _ = parse_markdown_frontmatter(original_bundle)
                original_selection = original_metadata.get("selected_revisions")
                if not (isinstance(original_selection, dict) and original_selection
                        and all(isinstance(key, str) and isinstance(value, str)
                                for key, value in original_selection.items())):
                    raise ContractValidationError("issued Bundle selection is invalid")
                selected_documents = self._authorized_bundle_selection(
                    active_id, principal_id, active_documents, list(original_selection))
                if selected_documents is None:
                    return self._result("denied", "access_denied",
                        "The issued Bundle selection is no longer authorized.",
                        "Reopen a Bundle using currently authorized sources.", {})
                if not self._issued_bundle_revisions_match(selected_documents, original_selection):
                    return self._result("stale", "bundle_selection_changed",
                        "The issued Bundle selection changed after it was opened.",
                        "Reopen a Bundle using the current exact source revisions.", {})
                source_lineage = self._selected_source_lineage(selected_documents)
                if original_metadata.get("selected_source_lineage", []) != source_lineage:
                    return self._result("stale", "bundle_selection_changed",
                        "The issued Bundle source binding changed after it was opened.",
                        "Reopen a Bundle using the current exact source evidence.", {})
                current_coverage = self._assess_coverage(active_documents, coverage_case_id)
                if current_coverage is None:
                    raise LifecycleValidationError(
                        "invalid",
                        "bundle_identity_missing",
                        "Bundle Coverage Case is no longer valid",
                    )
                if (
                    bundle_metadata.get("coverage_case_revision")
                    != current_coverage.assessment.get("coverage_case_revision")
                ):
                    raise LifecycleValidationError(
                        "stale",
                        "coverage_case_revision_mismatch",
                        "Bundle Coverage Case revision is stale",
                    )
                if (
                    bundle_metadata.get("source_snapshot_id")
                    != current_coverage.assessment.get("source_snapshot_id")
                ):
                    raise LifecycleValidationError(
                        "stale",
                        "source_snapshot_mismatch",
                        "Bundle Source Snapshot is stale",
                    )
                routing_documents = [
                    item
                    for item in active_documents
                    if item.metadata.get("schema") == "owledge.artifact-routing/1"
                    and item.metadata.get("lifecycle") == "accepted"
                ]
                if len(routing_documents) != 1:
                    raise ContractValidationError("Artifact Routing is missing or duplicated")
                routes = routing_documents[0].metadata.get("routes")
                if not isinstance(routes, dict) or not isinstance(routes.get(route_id), dict):
                    raise ContractValidationError("Artifact Routing route is missing")
                if (
                    bundle_metadata.get("resolution_route_revision")
                    != routes[route_id].get("route_revision")
                ):
                    raise LifecycleValidationError(
                        "stale",
                        "resolution_route_revision_mismatch",
                        "Bundle Artifact Routing revision is stale",
                    )
                candidate, changeset = preview_maintenance_bundle(
                    original_bundle=original_bundle,
                    edited_bundle=edited_bundle,
                    authority_id=active_id,
                    policy_revision=str(authority.metadata["policy_revision"]),
                    settings_revision=str(authority.metadata["settings_revision"]),
                    operation_id=operation_id,
                    submitted_by=principal_id,
                    content_origin=content_origin,
                    reported=reported,
                    adapter_observed=adapter_observed,
                    route=routes[route_id],
                    clock=clock,
                    identity_seed=self._lifecycle_identity_seed(operation_id),
                    source_derived_selection=bool(source_lineage),
                    source_lineage=source_lineage,
                )
                target_artifact_id = changeset["effects"][0]["artifact_id"]
                selected_revisions = bundle_metadata.get("selected_revisions")
                occupied_artifact_ids = {item.artifact_id for item in active_documents}
                if isinstance(selected_revisions, dict):
                    occupied_artifact_ids.update(str(item) for item in selected_revisions)
                if target_artifact_id in occupied_artifact_ids:
                    raise LifecycleValidationError(
                        "invalid",
                        "path_outside_authority",
                        "Candidate target reuses an existing or foreign artifact identity",
                    )
                target_relative_path = changeset["effects"][0]["relative_path"]
                target = active_root.resolve(strict=True) / str(target_relative_path)
                try:
                    target.resolve(strict=False).relative_to(active_root.resolve(strict=True))
                except ValueError as error:
                    raise LifecycleValidationError(
                        "invalid",
                        "path_outside_authority",
                        "Candidate target escapes authority",
                    ) from error
                if target.exists():
                    raise ContractValidationError("create-only Candidate target already exists")
                receipt_id = self._repository.apply(
                    "candidate_preview",
                    active_id,
                    {
                        "authority_id": active_id,
                        "operation_id": operation_id,
                        "candidate": candidate,
                        "changeset": changeset,
                    },
                )
                attribution = candidate["attribution"]
                self._repository.apply(
                    "trace_record",
                    active_id,
                    {
                        "authority_id": active_id,
                        "event": {
                        "event": "candidate_created",
                        "authority_id": active_id,
                        "principal_id": principal_id,
                        "assurance": principal.get("assurance"),
                        "base_revision": changeset["base_revision"],
                        "result_revision": candidate["candidate_revision"],
                        "outcome": "ok/candidate_ready",
                        "receipt_id": receipt_id,
                        "reported_content_origin": attribution[
                            "reported_content_origin"
                        ],
                        "submitted_by": attribution["submitted_by"],
                        },
                    },
                )
            except LifecycleValidationError as error:
                return self._result(
                    error.status,
                    error.reason_code,
                    "The edited Bundle violates its bounded lifecycle contract.",
                    "Reopen the current Bundle and preserve its authority and read-only fences.",
                    {},
                )
            except (ContractValidationError, OSError, TypeError, ValueError):
                return self._result(
                    "invalid",
                    "bundle_invalid",
                    "The edited Bundle failed structural or lifecycle validation.",
                    "Restore the returned Bundle and edit only its Gap response.",
                    {},
                )
            return self._result(
                "ok",
                "candidate_ready",
                "The edited Gap response is staged as a Candidate.",
                "Ask the local Owner to review the Candidate.",
                {"candidate": candidate, "changeset": changeset},
                receipt_id=receipt_id,
            )
        if operation == "bundle_open":
            gap_ids = payload.get("gap_ids")
            selected_ids = payload.get("selected_artifact_ids")
            operation_id = command.get("operation_id")
            clock = self._clock.now()
            if not (
                isinstance(gap_ids, list)
                and len(gap_ids) == 1
                and isinstance(gap_ids[0], str)
                and isinstance(selected_ids, list)
                and selected_ids
                and all(isinstance(item, str) for item in selected_ids)
                and len(set(selected_ids)) == len(selected_ids)
                and isinstance(operation_id, str)
                and isinstance(clock, str)
            ):
                return self._result(
                    "invalid",
                    "command_invalid",
                    "The Bundle request is incomplete.",
                    "Provide one open Gap, an exact Atom selection, and a valid Core clock.",
                    {},
                )
            if len(selected_ids) > 16:
                return self._result(
                    "incomplete",
                    "resource_exhausted",
                    "The bounded Bundle selection exceeds the 16-record limit.",
                    "Narrow the selection before opening the Bundle.",
                    {},
                )
            gap_id = gap_ids[0]
            try:
                gap = self._repository.read("gap", active_id, {"gap_id": gap_id})
            except (ContractValidationError, OSError):
                return self._result(
                    "invalid",
                    "gap_invalid",
                    "The requested Gap is missing or invalid.",
                    "Admit a valid Gap before opening a Maintenance Bundle.",
                    {},
                )
            if gap.get("lifecycle") != "open":
                return self._result(
                    "stale",
                    "gap_not_open",
                    "The requested Gap is not open.",
                    "Retrieve current Gap state before opening a Bundle.",
                    {},
                )

            registries = [
                item
                for item in active_documents
                if item.metadata.get("schema") == "owledge.coverage-case-registry/1"
                and item.metadata.get("lifecycle") == "accepted"
            ]
            routing_documents = [
                item
                for item in active_documents
                if item.metadata.get("schema") == "owledge.artifact-routing/1"
                and item.metadata.get("lifecycle") == "accepted"
            ]
            if len(registries) != 1 or len(routing_documents) != 1:
                return self._result(
                    "invalid",
                    "bundle_contract_invalid",
                    "The Bundle control records are missing or ambiguous.",
                    "Repair the Project-owned Coverage and Artifact Routing contracts.",
                    {},
                )
            registry = registries[0]
            cases = registry.metadata.get("coverage_cases")
            envelopes = registry.metadata.get("search_envelopes")
            coverage_case_id = gap.get("coverage_case_id")
            if not (
                isinstance(cases, dict)
                and isinstance(envelopes, dict)
                and isinstance(coverage_case_id, str)
                and isinstance(cases.get(coverage_case_id), dict)
            ):
                return self._result(
                    "invalid",
                    "bundle_contract_invalid",
                    "The Gap is not bound to an accepted Coverage Case.",
                    "Repair the Project-owned Coverage contract.",
                    {},
                )
            coverage_case = cases[coverage_case_id]
            envelope_id = coverage_case.get("search_envelope_id")
            route_id = coverage_case.get("resolution_route_id")
            routes = routing_documents[0].metadata.get("routes")
            if not (
                isinstance(envelope_id, str)
                and isinstance(envelopes.get(envelope_id), dict)
                and isinstance(route_id, str)
                and isinstance(routes, dict)
                and isinstance(routes.get(route_id), dict)
            ):
                return self._result(
                    "invalid",
                    "bundle_contract_invalid",
                    "The Bundle routing contract is incomplete.",
                    "Repair the Project-owned Artifact Routing contract.",
                    {},
                )
            envelope = envelopes[envelope_id]
            route = routes[route_id]
            if route.get("record_projection") != "full_body_without_frontmatter":
                return self._result(
                    "invalid",
                    "bundle_projection_invalid",
                    "The Bundle record projection is not deterministic.",
                    "Use the declared lossless Atom-body projection.",
                    {},
                )

            selected_documents = self._authorized_bundle_selection(
                active_id, principal_id, active_documents, selected_ids,
                command.get("source_link_id") if isinstance(command.get("source_link_id"), str) else "")
            if selected_documents is None:
                return self._result(
                    "denied",
                    "access_denied",
                    "The requested bounded selection is not authorized.",
                    "Choose only Atoms available through the active authority and its grants.",
                    {},
                )
            if len(selected_documents) != len(selected_ids):
                return self._result(
                    "recovery_required",
                    "retrieval_miss",
                    "The deterministic reference selection could not be reproduced.",
                    "Repair the reference retriever before opening the Bundle.",
                    {},
                )
            proof_ids = gap.get("proof_ids")
            required_evidence = gap.get("required_evidence")
            if not (
                isinstance(proof_ids, list)
                and proof_ids
                and isinstance(proof_ids[-1], str)
                and isinstance(required_evidence, list)
                and len(required_evidence) == 1
                and isinstance(required_evidence[0], str)
                and isinstance(gap.get("revision"), str)
                and isinstance(gap.get("coverage_case_revision"), str)
                and isinstance(envelope.get("revision"), str)
                and isinstance(route.get("route_revision"), str)
                and isinstance(route.get("target_artifact_id"), str)
                and isinstance(route.get("target_relative_path"), str)
            ):
                return self._result(
                    "invalid",
                    "bundle_contract_invalid",
                    "The Gap or routing binding is incomplete.",
                    "Repair the bounded lifecycle records.",
                    {},
                )
            absence_proof_id = proof_ids[-1]
            try:
                source_snapshot_id = self._repository.read(
                    "source_snapshot_for_proof",
                    active_id,
                    {"proof_id": absence_proof_id},
                )
                bundle_id, bundle_revision, expires_at, bundle_markdown = (
                    render_maintenance_bundle(
                        authority_id=active_id,
                        policy_revision=str(authority.metadata["policy_revision"]),
                        settings_revision=str(authority.metadata["settings_revision"]),
                        coverage_case_id=coverage_case_id,
                        coverage_case_revision=str(gap["coverage_case_revision"]),
                        search_envelope_id=envelope_id,
                        search_envelope_revision=str(envelope["revision"]),
                        source_snapshot_id=source_snapshot_id,
                        absence_proof_id=absence_proof_id,
                        resolution_route_id=route_id,
                        resolution_route_revision=str(route["route_revision"]),
                        gap_id=gap_id,
                        evidence_key=required_evidence[0],
                        target_artifact_id=str(route["target_artifact_id"]),
                        target_relative_path=str(route["target_relative_path"]),
                        selected_documents=selected_documents,
                        clock=clock,
                        identity_seed=self._lifecycle_identity_seed(operation_id),
                    )
                )
                if len(bundle_markdown.encode("utf-8")) > 256 * 1024:
                    return self._result(
                        "incomplete",
                        "resource_exhausted",
                        "The rendered Bundle exceeds the 256 KiB limit.",
                        "Narrow the selection before opening the Bundle.",
                        {},
                    )
                if self._identity_profile == "mvp-v1":
                    existing = self._repository.read("bundle_existing", active_id, {"bundle_id": bundle_id})
                    if existing is not None:
                        metadata, _ = parse_markdown_frontmatter(existing)
                        original_expiry = metadata.get("expires_at")
                        if not isinstance(original_expiry, str) or bundle_markdown.replace(
                            f"expires_at: {expires_at}\n", f"expires_at: {original_expiry}\n", 1
                        ) != existing:
                            raise ContractValidationError("existing Bundle request binding changed")
                        # Reopening a durable request does not extend its expiry.
                        expires_at, bundle_markdown = original_expiry, existing
                receipt_id = self._repository.apply(
                    "bundle_open",
                    active_id,
                    {
                        "authority_id": active_id,
                        "operation_id": operation_id,
                        "gap_revision": str(gap["revision"]),
                        "bundle_id": bundle_id,
                        "bundle_revision": bundle_revision,
                        "bundle_markdown": bundle_markdown,
                    },
                )
                self._repository.apply(
                    "trace_record",
                    active_id,
                    {
                        "authority_id": active_id,
                        "event": {
                        "event": "bundle_opened",
                        "authority_id": active_id,
                        "principal_id": principal_id,
                        "assurance": principal.get("assurance"),
                        "base_revision": gap["revision"],
                        "result_revision": bundle_revision,
                        "outcome": "ok/bundle_ready",
                        "receipt_id": receipt_id,
                        },
                    },
                )
            except (ContractValidationError, OSError, ValueError):
                return self._result(
                    "recovery_required",
                    "bundle_effect_inconsistent",
                    "The Maintenance Bundle could not be rendered or stored consistently.",
                    "Inspect and recover the bounded Bundle effect.",
                    {},
                )
            return self._result(
                "ok",
                "bundle_ready",
                "The bounded Maintenance Bundle is ready.",
                "Edit only the Gap response block, then preview the Bundle.",
                {
                    "bundle_id": bundle_id,
                    "bundle_revision": bundle_revision,
                    "expires_at": expires_at,
                    "bundle_markdown": bundle_markdown,
                },
                receipt_id=receipt_id,
            )
        if operation == "gap_admit":
            proof = payload.get("absence_proof")
            proof_id = payload.get("absence_proof_id")
            expected_gap_revision = payload.get("expected_gap_revision")
            operation_id = command.get("operation_id")
            if not (
                isinstance(proof, dict)
                and isinstance(proof_id, str)
                and isinstance(expected_gap_revision, str)
                and isinstance(operation_id, str)
                and isinstance(proof.get("coverage_case_id"), str)
            ):
                return self._result(
                    "invalid",
                    "command_invalid",
                    "The Gap admission request is incomplete.",
                    "Provide one exact Absence Proof and expected Gap state.",
                    {},
                )
            source_snapshot_sha256 = proof.get("source_snapshot_sha256")
            if not isinstance(source_snapshot_sha256, str):
                return self._result(
                    "invalid",
                    "absence_proof_invalid",
                    "The Absence Proof is incomplete.",
                    "Retrieve the Coverage Case again.",
                    {},
                )
            source_snapshot_id = f"snapshot:sha256:{source_snapshot_sha256}"
            canonical_proof = json.dumps(
                proof,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            if proof_id != f"proof:sha256:{sha256(canonical_proof).hexdigest()}":
                return self._result(
                    "invalid",
                    "absence_proof_invalid",
                    "The Absence Proof does not match its content-bound identity.",
                    "Retrieve the Coverage Case again.",
                    {},
                )
            if any(not self._source_reference_allowed(item, active_documents, principal_id)
                   for item in active_documents
                   if item.metadata.get("knowledge_kind") == "reference"
                   and ("source_evidence" in item.metadata
                        or item.artifact_id.startswith(f"memory:{active_id.replace(':', '-')}-source-"))):
                return self._result("denied", "source_access_denied",
                    "A source-derived reference in the proof is no longer authorized.",
                    "Retrieve again with currently authorized sources.", {})
            try:
                replay = self._repository.read(
                    "gap_admission_replay",
                    active_id,
                    {
                        "authority_id": active_id,
                        "operation_id": operation_id,
                        "coverage_case_id": str(proof["coverage_case_id"]),
                        "proof_id": proof_id,
                        "source_snapshot_id": source_snapshot_id,
                        "expected_gap_revision": expected_gap_revision,
                    },
                )
            except (ContractValidationError, OSError, ValueError):
                return self._result(
                    "invalid",
                    "operation_replay_mismatch",
                    "The operation identity is already bound to another effect.",
                    "Use the original effect binding or a new operation identity.",
                    {},
                )
            if replay is not None:
                gap, receipt_id, reason_code = replay
                if receipt_id is not None:
                    self._repository.apply("trace_record", active_id, {
                        "authority_id": active_id,
                        "event": {"event": reason_code, "authority_id": active_id,
                                  "principal_id": principal_id, "assurance": principal.get("assurance"),
                                  "base_revision": expected_gap_revision, "result_revision": gap["gap_revision"],
                                  "outcome": f"ok/{reason_code}", "receipt_id": receipt_id,
                                  "coverage_case_revision": proof["coverage_case_revision"],
                                  "source_snapshot_id": source_snapshot_id, "absence_proof_id": proof_id},
                    })
                return self._result(
                    "ok",
                    reason_code,
                    "The proven knowledge absence is recorded once.",
                    "Open a bounded Maintenance Bundle for this Gap.",
                    gap,
                    receipt_id=receipt_id,
                )
            coverage = self._assess_coverage(
                active_documents,
                str(proof["coverage_case_id"]),
            )
            if not (
                coverage is not None
                and coverage.assessment.get("assessment") == "knowledge_absent"
                and coverage.assessment.get("absence_proof_id") == proof_id
                and coverage.absence_proof == proof
                and proof.get("active_authority_id") == active_id
            ):
                reason_code = absence_proof_staleness_reason(coverage, proof)
                return self._result(
                    "stale",
                    reason_code,
                    "The Absence Proof no longer matches the active authority snapshot.",
                    "Retrieve the Coverage Case again before admitting a Gap.",
                    {},
                )
            required_evidence = proof.get("unresolved_evidence_keys")
            if not (
                isinstance(required_evidence, list)
                and all(isinstance(key, str) for key in required_evidence)
                and isinstance(coverage.safe_topic, str)
                and isinstance(proof.get("coverage_case_revision"), str)
                and isinstance(proof.get("source_snapshot_sha256"), str)
            ):
                return self._result(
                    "invalid",
                    "absence_proof_invalid",
                    "The Absence Proof is incomplete.",
                    "Retrieve the Coverage Case again.",
                    {},
                )
            try:
                gap, receipt_id, reason_code = self._repository.apply(
                    "admit_gap",
                    active_id,
                    {
                        "authority_id": active_id,
                        "operation_id": operation_id,
                        "coverage_case_id": str(proof["coverage_case_id"]),
                        "coverage_case_revision": str(proof["coverage_case_revision"]),
                        "proof_id": proof_id,
                        "source_snapshot_id": source_snapshot_id,
                        "safe_topic": coverage.safe_topic,
                        "required_evidence": required_evidence,
                        "expected_gap_revision": expected_gap_revision,
                    },
                )
                if receipt_id is not None:
                    self._repository.apply(
                        "trace_record",
                        active_id,
                        {
                            "authority_id": active_id,
                            "event": {
                            "event": reason_code,
                            "authority_id": active_id,
                            "principal_id": principal_id,
                            "assurance": principal.get("assurance"),
                            "base_revision": expected_gap_revision,
                            "result_revision": gap["gap_revision"],
                            "outcome": f"ok/{reason_code}",
                            "receipt_id": receipt_id,
                            "coverage_case_revision": proof["coverage_case_revision"],
                            "source_snapshot_id": source_snapshot_id,
                            "absence_proof_id": proof_id,
                            },
                        },
                    )
            except (ContractValidationError, OSError):
                return self._result(
                    "recovery_required",
                    "gap_effect_inconsistent",
                    "The Gap effect could not be applied consistently.",
                    "Inspect and recover the bounded Core effect.",
                    {},
                )
            return self._result(
                "ok",
                reason_code,
                "The proven knowledge absence is recorded once.",
                "Open a bounded Maintenance Bundle for this Gap.",
                gap,
                receipt_id=receipt_id,
            )
        if operation == "retrieve":
            if not isinstance(payload.get("coverage_case_id"), str):
                return self._result(
                    "invalid",
                    "command_invalid",
                    "The retrieval request is incomplete.",
                    "Provide a declared coverage case.",
                    {},
                )
            coverage_case_id = str(payload["coverage_case_id"])
            if coverage_controls is None:
                return self._result(
                    "recovery_required",
                    "source_unavailable",
                    "The authorized Project snapshot could not be stabilized.",
                    "Repair or quarantine the changing source before retrying.",
                    {},
                )
            try:
                first_reference = self._reference_retriever.assess(
                    active_documents,
                    coverage_case_id,
                )
            except TimeoutError:
                first_reference = None
            if first_reference is not None:
                try:
                    stable_documents = self._repository.coverage_snapshot(
                        active_id,
                        coverage_controls,
                    )
                    if any(not self._source_reference_allowed(item, stable_documents, principal_id)
                           for item in stable_documents):
                        return self._result("incomplete", "source_access_limited",
                            "Restricted source-derived evidence is outside this identity's rights.",
                            "Ask the Owner for an explicit source grant before claiming coverage or absence.", {})
                    stable_reference = self._reference_retriever.assess(
                        stable_documents,
                        coverage_case_id,
                    )
                except (ContractValidationError, OSError, TimeoutError):
                    return self._result(
                        "recovery_required",
                        "source_unavailable",
                        "The authorized Project snapshot could not be stabilized.",
                        "Repair or quarantine the changing source before retrying.",
                        {},
                    )
                if stable_reference != first_reference:
                    return self._result(
                        "recovery_required",
                        "source_unavailable",
                        "The authorized Project source changed during its bounded scan.",
                        "Retry after the source is stable.",
                        {},
                    )
                active_documents = stable_documents
            coverage = self._assess_coverage(active_documents, coverage_case_id)
            if coverage is not None and coverage.assessment["assessment"] == "coverage_satisfied":
                return self._result(
                    "ok",
                    "coverage_complete",
                    "The required project evidence is complete.",
                    "Use the returned evidence for the current task.",
                    {
                        "assessment": coverage.assessment,
                        "absence_proof": coverage.absence_proof,
                    },
                )
            if coverage is None:
                return self._result(
                    "invalid",
                    "coverage_case_invalid",
                    "The requested Coverage Case is absent or not authoritatively valid.",
                    "Choose one valid Case from the accepted Project registry.",
                    {},
                )
            if coverage.assessment["assessment"] == "retrieval_miss":
                return self._result(
                    "recovery_required",
                    "retrieval_miss",
                    "The optional derived retriever disagrees with the deterministic reference scan.",
                    "Remove or rebuild the derived retriever and retry with the reference scan.",
                    {
                        "assessment": coverage.assessment,
                        "absence_proof": None,
                    },
                )
            if coverage.assessment["assessment"] == "resource_exhausted":
                return self._result(
                    "incomplete",
                    "resource_exhausted",
                    "The bounded source scan ended before coverage was established.",
                    "Narrow the declared envelope or increase its reviewed budget.",
                    {
                        "assessment": coverage.assessment,
                        "absence_proof": None,
                    },
                )
            if coverage.assessment["assessment"] == "evidence_conflict":
                return self._result(
                    "conflict",
                    "evidence_conflict",
                    "Valid providers disagree on required evidence.",
                    "Resolve the conflicting sources before admitting a Gap.",
                    {
                        "assessment": coverage.assessment,
                        "absence_proof": None,
                    },
                )
            if coverage.assessment["assessment"] == "technical_failure":
                return self._result(
                    "recovery_required",
                    "technical_failure",
                    "A candidate evidence record violates its provider contract.",
                    "Repair or quarantine the invalid evidence candidate.",
                    {
                        "assessment": coverage.assessment,
                        "absence_proof": None,
                    },
                )
            if coverage.assessment["assessment"] == "source_not_registered":
                return self._result(
                    "incomplete",
                    "source_not_registered",
                    "The declared search envelope contains no registered source records.",
                    "Register a source before treating missing evidence as knowledge absence.",
                    {
                        "assessment": coverage.assessment,
                        "absence_proof": None,
                    },
                )
            if coverage.assessment["assessment"] == "knowledge_absent":
                return self._result(
                    "incomplete",
                    "knowledge_absent",
                    "Required evidence is absent from the complete bounded source snapshot.",
                    "Submit the returned proof to a separate Gap admission operation if needed.",
                    {
                        "assessment": coverage.assessment,
                        "absence_proof": coverage.absence_proof,
                    },
                )
            return self._result(
                "incomplete",
                "coverage_unresolved",
                "The declared evidence could not be established safely.",
                "Inspect the assessment before requesting a separate Gap effect.",
                {
                    "assessment": coverage.assessment,
                    "absence_proof": coverage.absence_proof,
                },
            )
        linked: list[dict[str, object]] = []
        requested_link = command.get("source_link_id")
        for item in active_documents:
            if item.metadata.get("schema") != "owledge.knowledge-source-link/1":
                continue
            if requested_link is not None and item.metadata.get("source_link_id") != requested_link:
                continue
            linked_id = str(item.metadata.get("linked_authority_id", ""))
            link_grants = item.metadata.get("grants", [])
            foreign_root = self._root_for_authority(linked_id)
            if not (
                foreign_root is not None
                and isinstance(link_grants, list)
                and "discover" in link_grants
            ):
                continue
            try:
                foreign_authority = self._repository.bootstrap(linked_id)
            except (ContractValidationError, OSError):
                continue
            if has_grant(foreign_authority, principal_id, "discover"):
                try:
                    foreign_documents = self._repository.snapshot(linked_id)
                except (ContractValidationError, OSError):
                    continue
                linked.append(
                    {
                        "authority_id": linked_id,
                        "source_link_id": item.metadata["source_link_id"],
                        "grants": list(link_grants),
                        "record_count": len(foreign_documents),
                    }
                )
        linked.sort(key=lambda item: str(item["authority_id"]))
        return self._result(
            "ok",
            "project_inspected",
            "The project is ready for bounded knowledge operations.",
            "Retrieve a declared coverage case.",
            {
                "active_authority": {
                    "authority_id": authority.authority_id,
                    "artifact_id": authority.artifact_id,
                    "revision": authority.metadata["revision"],
                    "policy_revision": authority.metadata["policy_revision"],
                    "settings_revision": authority.metadata["settings_revision"],
                    "mode": authority.metadata["mode"],
                    "record_count": len(active_documents),
                },
                "linked_authorities": linked,
                "health": {"invalid_documents": invalid_document_count(active_documents)},
            },
        )
