"""Contained local Markdown reads for the private Core."""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import tempfile
import time
from contextlib import contextmanager, ExitStack
from contextvars import ContextVar
from hashlib import sha256
from pathlib import Path
from typing import Callable, Mapping

from .artifacts import (
    ManagedMarkdown,
    parse_managed_markdown,
    parse_markdown_frontmatter,
    render_source_manifest,
    render_source_setup_receipt,
    render_source_sidecar,
    unicode_keyword_spans,
)
from .contracts import (
    ContractValidationError,
    CoverageCaseInvalidError,
    SourceSnapshot,
)


__all__: tuple[str, ...] = ()


_INITIAL_CANDIDATE_REVISION = re.compile(r"candidate-rev-1(?:-[0-9a-f]{16})?\Z")
_REVIEWED_CANDIDATE_REVISION = re.compile(
    r"candidate-rev-2-reviewed(?:-[0-9a-f]{16})?\Z"
)
_ORDINARY_EFFECT_DIRS = frozenset({"gaps", "receipts", "candidates", "changesets",
                                   "bundles", "inbox", "reuse-feed"})
_METADATA_ENTRY_LIMIT = 4096
_PAIR_VALIDATION_PARENT: ContextVar[Path | None] = ContextVar("paired_restore_validation_parent", default=None)


@contextmanager
def paired_restore_readback(parent: Path):
    """Let exact restored children be checked while their publication guard remains."""
    resolved = _validated_root(parent)
    if not (resolved / ".owledge/paired-restore.json").is_file():
        raise ContractValidationError("paired restore readback guard is missing")
    token = _PAIR_VALIDATION_PARENT.set(resolved)
    try:
        yield
    finally:
        _PAIR_VALIDATION_PARENT.reset(token)


def paired_restore_readback_active(parent: Path) -> bool:
    return _PAIR_VALIDATION_PARENT.get() == Path(parent).resolve(strict=True)


def _bounded_markdown_inventory(
    lanes: tuple[Path, ...], *, recursive: bool, limit: int = _METADATA_ENTRY_LIMIT,
) -> tuple[list[Path], int, int, bool]:
    """Enumerate metadata with a fixed ceiling before sorting or reading bodies.

    An overflow probe is counted as work. The partial path list must never be
    treated as a complete inventory or used to issue a continuation cursor.
    """
    paths: list[Path] = []
    entries_examined = 0
    directories_examined = 0
    pending = list(reversed(lanes))
    while pending:
        directory = pending.pop()
        if not directory.exists():
            continue
        if not directory.is_dir() or directory.is_symlink() or _is_reparse_path(directory):
            raise ContractValidationError("metadata directory is invalid")
        directories_examined += 1
        if directories_examined > limit:
            return paths, entries_examined, directories_examined, True
        with os.scandir(directory) as iterator:
            for entry in iterator:
                entries_examined += 1
                if entries_examined > limit:
                    return paths, entries_examined, directories_examined, True
                path = Path(entry.path)
                if recursive and (entry.is_symlink() or _is_reparse_path(path)):
                    raise ContractValidationError("metadata lane contains a linked entry")
                if recursive and entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                elif entry.name.endswith(".md"):
                    # Keep links in the inventory so the bounded reader rejects
                    # them instead of silently hiding malformed evidence.
                    paths.append(path)
    paths.sort(key=lambda item: item.as_posix().casefold())
    return paths, entries_examined, directories_examined, False


def canonical_recovery_pending(root: Path) -> bool:
    """Fail closed on pending effects or an unbounded transaction directory."""
    resolved = _validated_root(root)
    if (resolved / ".owledge" / "pending-effect.json").exists():
        return True
    try:
        paths, _, _, overflow = _bounded_markdown_inventory(
            (resolved / ".owledge" / "transactions",), recursive=False)
    except (ContractValidationError, OSError):
        return True
    return overflow or bool(paths)


@contextmanager
def authority_write_locks(roots, *, allow_project_reader_recovery: bool = False,
                          allow_settings_repair: bool = False):
    """Serialize cooperating local writers; OS releases locks after process death.

    Handles live in the OS temp cache, so locking linked read-only evidence does
    not alter that authority. Hot retrieval remains lock-free. External text
    editors and lock-directory tampering are outside the cooperating-writer model.
    """
    with ExitStack() as stack:
        lock_root = Path(tempfile.gettempdir()) / "owledge-core-writers"
        if any(_is_reparse_path(path) for path in (lock_root, *lock_root.parents)):
            raise ContractValidationError("writer cache crosses a link")
        lock_root.mkdir(exist_ok=True)
        lock_root = _validated_root(lock_root)
        requested_roots = {_validated_root(Path(item)) for item in roots}
        settings_links = {}
        for root in tuple(requested_roots):
            authority_path = root / ".owledge/authority.md"
            if root.name == "project" and _effect_exists(root, authority_path):
                authority_bytes = _read_exact_effect(root, authority_path, max_bytes=1_048_576)
                header = parse_managed_markdown(".owledge/authority.md",
                    authority_bytes.decode("utf-8"), encoded_document=authority_bytes)
                linked = _settings_linked_global(root, header.authority_id)
                if linked is not None:
                    settings_links[root] = (header.authority_id, linked)
                    requested_roots.update((root.parent, linked))
        locked_roots = sorted(requested_roots, key=lambda p: str(p).casefold())
        for root in locked_roots:
            key = sha256(os.path.normcase(str(root)).encode("utf-8")).hexdigest()
            target = lock_root / f"{key}.lock"
            _validated_effect_path(lock_root, target, must_exist=False)
            flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(target, flags, 0o600)
            handle = stack.enter_context(os.fdopen(descriptor, "r+b", buffering=0))
            if os.fstat(handle.fileno()).st_nlink != 1:
                raise ContractValidationError("writer lock must not be linked")
            _validated_effect_path(lock_root, target, must_exist=True)
            deadline = time.monotonic() + 5
            while True:
                try:
                    if os.name == "nt":
                        import msvcrt
                        handle.seek(0)
                        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise ContractValidationError("authority writer is busy")
                    time.sleep(0.01)
        for root, (authority_id, linked) in settings_links.items():
            if _settings_linked_global(root, authority_id) != linked:
                raise ContractValidationError("linked Settings target changed before the writer lock")
        if not allow_settings_repair:
            for root in locked_roots:
                authority_path = root / ".owledge" / "authority.md"
                if _effect_exists(root, authority_path):
                    authority_raw = _read_exact_effect(root, authority_path, max_bytes=1_048_576)
                    header = parse_managed_markdown(".owledge/authority.md", authority_raw.decode("utf-8"),
                                                    encoded_document=authority_raw)
                    require_settings_healthy(root, header.authority_id)
        if not allow_project_reader_recovery:
            workspaces = set(locked_roots)
            for root in locked_roots:
                if (root.name in {"project", "global"}
                        and _effect_exists(root, root / ".owledge/authority.md")):
                    workspaces.add(root.parent)
            for workspace in workspaces:
                if project_reader_pending(workspace):
                    raise ContractValidationError("Project reader recovery is required before another write")
                state_path = workspace / "workspace.json"
                if not _effect_exists(workspace, state_path):
                    continue
                raw = _read_exact_effect(workspace, state_path, max_bytes=65_536)
                state = json.loads(raw)
                if not isinstance(state, dict) or state.get("schema") != _LINKED_PROJECT_SCHEMA:
                    continue
                linked = state.get("global_contribution")
                if not isinstance(linked, dict) or not isinstance(linked.get("workspace"), str):
                    raise ContractValidationError("linked Project reader state is invalid")
                _, global_workspace = _reuse_roots(workspace, linked["workspace"])
                if project_reader_pending(global_workspace):
                    raise ContractValidationError("linked Global Project reader recovery is required")
        yield


class MarkdownAuthorityRepository:
    """Only admitted PoC repository: contained authority-scoped Markdown."""

    def __init__(self, roots: Mapping[str, Path]) -> None:
        self._roots = {str(alias): Path(root) for alias, root in roots.items()}

    def root_for(self, authority_id: str) -> Path | None:
        return self._roots.get(authority_id, self._roots.get(authority_id.split(":", 1)[0]))

    def bootstrap(self, authority_id: str) -> ManagedMarkdown:
        root = self.root_for(authority_id)
        if root is None:
            raise ContractValidationError("authority handle is unknown")
        return bootstrap_authority(root, authority_id)

    def snapshot(
        self,
        authority_id: str,
        coverage_case_id: str | None = None,
    ) -> tuple[ManagedMarkdown, ...]:
        root = self.root_for(authority_id)
        if root is None:
            raise ContractValidationError("authority handle is unknown")
        if coverage_case_id is not None:
            # The inward I/O role only exposes control documents here.  The
            # outer API/retrieval roles own semantic Coverage Case validation
            # and may request the full snapshot only after that check passes.
            return load_authority_control_documents(root, authority_id)
        return load_authority_documents(root, authority_id)

    def maintenance_snapshot(
        self,
        authority_id: str,
        *,
        max_documents: int,
        max_bytes: int,
        max_candidates: int,
        cursor: Mapping[str, object] | None,
        stage: str | None = None,
    ) -> Mapping[str, object]:
        root = self.root_for(authority_id)
        if root is None:
            raise ContractValidationError("authority handle is unknown")
        return load_maintenance_snapshot(
            root,
            authority_id,
            max_documents=max_documents,
            max_bytes=max_bytes,
            max_candidates=max_candidates,
            cursor=cursor,
            stage=stage,
        )

    def progressive_controls(self, authority_id: str) -> tuple[ManagedMarkdown, ...]:
        root = self.root_for(authority_id)
        if root is None:
            raise ContractValidationError("authority handle is unknown")
        return load_authority_control_documents(root, authority_id)

    def progressive_stage_snapshot(
        self,
        authority_id: str,
        stage: str,
        *,
        max_documents: int,
        max_bytes: int,
    ) -> Mapping[str, object]:
        root = self.root_for(authority_id)
        if root is None:
            raise ContractValidationError("authority handle is unknown")
        return load_progressive_stage(
            root,
            authority_id,
            stage,
            max_documents=max_documents,
            max_bytes=max_bytes,
        )

    def raw_keyword_snapshot(
        self,
        authority_id: str,
        *,
        query: str,
        max_documents: int,
        max_bytes: int,
        max_matches: int = 8,
        source_areas: tuple[str, ...] = (".",),
        cursor: Mapping[str, object] | None = None,
        discover_areas: bool = False,
        area_parent: str = ".",
        selection_binding: str = "",
    ) -> Mapping[str, object]:
        root = self.root_for(authority_id)
        if root is None:
            raise ContractValidationError("authority handle is unknown")
        return load_raw_keyword_snapshot(
            root,
            authority_id,
            query=query,
            max_documents=max_documents,
            max_bytes=max_bytes,
            max_matches=max_matches,
            source_areas=source_areas,
            cursor=cursor,
            discover_areas=discover_areas,
            area_parent=area_parent,
            selection_binding=selection_binding,
        )

    def apply(
        self,
        operation: str,
        authority_id: str,
        arguments: Mapping[str, object],
    ) -> object:
        root = self.root_for(authority_id)
        if root is None:
            raise ContractValidationError("authority handle is unknown")
        effects = {
            "admit_gap": admit_gap,
            "bundle_open": apply_bundle_open,
            "candidate_preview": apply_candidate_preview,
            "candidate_review": apply_candidate_review,
            "candidate_promote": promote_candidate,
            "contribute_for_reuse": contribute_for_reuse,
            "gap_close": close_gap,
            "maintenance_observe": record_maintenance_observation,
            "recover": recover_transaction,
            "trace_record": record_trace_event,
        }
        effect = effects.get(operation)
        if effect is None:
            raise ContractValidationError("repository operation is not admitted")
        return effect(root, **dict(arguments))

    def coverage_snapshot(
        self,
        authority_id: str,
        controls: tuple[ManagedMarkdown, ...],
    ) -> tuple[ManagedMarkdown, ...]:
        root = self.root_for(authority_id)
        if root is None:
            raise ContractValidationError("authority handle is unknown")
        return load_coverage_documents(root, controls)

    def read(
        self,
        operation: str,
        authority_id: str,
        arguments: Mapping[str, object],
    ) -> object:
        root = self.root_for(authority_id)
        if root is None:
            raise ContractValidationError("authority handle is unknown")
        readers = {
            "bundle": read_bundle,
            "bundle_existing": read_existing_bundle,
            "candidate": read_candidate,
            "candidate_queue": read_candidate_queue,
            "changeset": read_changeset,
            "gap": read_gap,
            "gap_admission_replay": replay_gap_admission,
            "gap_closure_replay": replay_gap_closure,
            "source_snapshot_for_proof": source_snapshot_for_proof,
            "trace": read_trace,
            "curated_reference": read_curated_reference,
            "curated_discover": discover_curated_references,
            "reuse_contribution": read_reuse_contribution,
        }
        reader = readers.get(operation)
        if reader is None:
            raise ContractValidationError("repository read is not admitted")
        return reader(root, **dict(arguments))


def discover_curated_references(root: Path, *, authority: ManagedMarkdown, payload: dict,
                                allowed_document: Callable[[ManagedMarkdown], bool] | None = None,
                                rights_binding: str = "") -> dict:
    """Bound directory inventory and body reads before returning a page.

    The cursor detects ordinary local edits via file metadata, not a cryptographic
    snapshot of unread bodies. It conveys position, never permission or absence.
    """
    from .source_curation import discovery_reference
    resolved = _validated_root(root)
    directory = resolved / ".owledge" / "curated"

    def inventory():
        if not _effect_exists(resolved, directory):
            return [], 0, 0, False
        if not directory.is_dir():
            raise ContractValidationError("curated reference directory is invalid")
        entries = []
        paths, examined, dirs, overflow = _bounded_markdown_inventory((directory,), recursive=False)
        if overflow:
            return [], examined, dirs, True
        for path in paths:
            if not path.name.startswith(("source-", "lesson-", "essence-", "idea-", "finding-")):
                continue
            # Legacy feed curation allowed longer names; they cannot be fresh
            # Lesson handles and remain outside this bounded lookup surface.
            if path.name.startswith("lesson-") and len(path.stem.removeprefix("lesson-")) > 80:
                continue
            facts = _materialized_path_facts(resolved, path)
            if facts[3] != 1 or not stat.S_ISREG(facts[6]):
                raise ContractValidationError("reference is not a regular unlinked document")
            entries.append((path.name, *facts[1:], path.stat().st_ctime_ns))
        return entries, examined, dirs, False

    entries, metadata_entries, metadata_dirs, overflow = inventory()
    if overflow:
        return {"references": [], "continuation": None,
                "progress": {"files_examined": 0, "bytes_examined": 0,
                             "metadata_entries_examined": metadata_entries,
                             "metadata_directories_examined": metadata_dirs,
                             "metadata_entry_limit": _METADATA_ENTRY_LIMIT},
                "resource_exhausted": True, "gap_effect_allowed": False}
    binding = sha256(json.dumps({"root": str(resolved), "authority": authority.content_sha256,
                                 "rights": rights_binding,
                                 "query": payload["query"], "area": payload["knowledge_area"],
                                 "filters": payload.get("filters", {}),
                                 "inventory": entries}, sort_keys=True).encode()).hexdigest()
    cursor = payload["cursor"]
    offset = cursor["offset"] if cursor is not None else 0
    if cursor is not None and (cursor["binding"] != binding or offset >= len(entries)):
        raise ContractValidationError("discovery cursor is stale or mismatched")
    references, files, size = [], 0, 0
    while offset < len(entries) and files < 32 and len(references) < 8:
        entry = entries[offset]
        document_size = entry[4]
        if document_size > 65_536:
            raise ContractValidationError("reference exceeds its bounded read budget")
        # Reserve the bounded reader's one-byte overflow probe, including races.
        if size + document_size >= 262_144:
            break
        path = directory / entry[0]
        artifact_id = f"memory:{authority.authority_id.replace(':', '-')}-{path.stem}"
        document = read_curated_reference(root, authority_id=authority.authority_id, artifact_id=artifact_id,
                                          max_bytes=min(65_536, 262_144 - size - 1))
        if document is None:
            raise ContractValidationError("reference disappeared")
        files += 1
        size += document.size_bytes
        offset += 1
        if allowed_document is not None and not allowed_document(document):
            continue
        match = discovery_reference(document, payload["query"], payload["knowledge_area"])
        if match is not None:
            references.append(match)
    rechecked, rechecked_entries, rechecked_dirs, rechecked_overflow = inventory()
    if rechecked_overflow or rechecked != entries:
        raise ContractValidationError("discovery inventory changed while read")
    continuation = {"binding": binding, "offset": offset} if offset < len(entries) else None
    return {"references": references, "continuation": continuation,
            "progress": {"files_examined": files, "bytes_examined": size,
                         "metadata_entries_examined": metadata_entries + rechecked_entries,
                         "metadata_directories_examined": metadata_dirs + rechecked_dirs,
                         "metadata_entry_limit": _METADATA_ENTRY_LIMIT},
            "resource_exhausted": False, "gap_effect_allowed": False}


def _reference_history_target(root: Path, artifact_id: str, revision: str) -> Path:
    key = sha256((artifact_id + "\0" + revision).encode("utf-8")).hexdigest()
    return root / ".owledge" / "reference-history" / f"{key}.snapshot"


def read_curated_reference(root: Path, *, authority_id: str, artifact_id: str, max_bytes: int = 65_536, revision: str | None = None) -> ManagedMarkdown | None:
    """Read one generated reference, with fixed path and byte bounds."""
    prefix = f"memory:{authority_id.replace(':', '-')}-"
    relative_id = artifact_id.removeprefix(prefix)
    if not artifact_id.startswith(prefix) or not relative_id.startswith(("source-", "lesson-", "idea-", "finding-", "essence-")):
        raise ContractValidationError("reference identity is outside the active authority")
    kind, slug = relative_id.split("-", 1)
    if len(slug) > 80 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ContractValidationError("reference identity is invalid")
    resolved = _validated_root(root)
    target = resolved / ".owledge" / "curated" / f"{kind}-{slug}.md"
    if not _effect_exists(resolved, target):
        return None
    document = _read_managed_document_bounded(resolved, target, max_bytes=min(65_536, max_bytes))
    if document is None:
        raise ContractValidationError("reference exceeds its bounded read budget")
    if document.authority_id != authority_id or document.artifact_id != artifact_id:
        raise ContractValidationError("reference identity changed")
    if revision is not None and document.revision != revision:
        target = _reference_history_target(resolved, artifact_id, revision)
        if not _effect_exists(resolved, target):
            return None
        document = _read_managed_document_bounded(resolved, target, max_bytes=min(65_536, max_bytes))
        if document is None or document.authority_id != authority_id or document.artifact_id != artifact_id or document.revision != revision:
            raise ContractValidationError("historical reference binding differs")
        envelope = document.metadata.get("curation_effect")
        receipt_id = envelope.get("receipt_id") if isinstance(envelope, dict) else None
        if not isinstance(receipt_id, str) or not re.fullmatch(r"receipt:[a-zA-Z0-9:_-]+", receipt_id):
            raise ContractValidationError("historical reference receipt is missing")
        receipt, _ = _read_effect_metadata(resolved, resolved / ".owledge" / "receipts" / f"{receipt_id.replace(':', '-')}.md")
        if (receipt.get("authority_id") != authority_id or receipt.get("result_revision") != revision
                or receipt.get("result_sha256") != document.content_sha256 or receipt.get("outcome") != "ok/candidate_promoted"):
            raise ContractValidationError("historical reference differs from its promotion receipt")
    return document


def read_reuse_contribution(root: Path, *, authority_id: str, contribution_id: str) -> ManagedMarkdown | None:
    """Read one deterministic Feed identity with the normal contained-file bounds."""

    prefix = f"contribution:{authority_id.replace(':', '-')}-"
    suffix = contribution_id.removeprefix(prefix)
    if not contribution_id.startswith(prefix) or not re.fullmatch(r"[0-9a-f]{16}", suffix):
        raise ContractValidationError("reuse contribution identity is invalid")
    resolved = _validated_root(root)
    target = resolved / ".owledge" / "reuse-feed" / f"{contribution_id.replace(':', '-')}.md"
    if not _effect_exists(resolved, target):
        return None
    document = _read_managed_document_bounded(resolved, target, max_bytes=65_536)
    if document is None:
        raise ContractValidationError("reuse contribution exceeds its bounded read budget")
    if document.authority_id != authority_id or document.artifact_id != contribution_id:
        raise ContractValidationError("reuse contribution identity changed")
    return document


def _validated_root(root: Path) -> Path:
    candidate = Path(root)
    if not candidate.exists() or not candidate.is_dir() or candidate.is_symlink():
        raise ContractValidationError("authority root is invalid")
    return candidate.resolve(strict=True)


def _read_managed_document(root: Path, path: Path) -> ManagedMarkdown:
    if path.is_symlink():
        raise ContractValidationError("managed Markdown path escapes through a link")
    resolved = path.resolve(strict=True)
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as error:
        raise ContractValidationError("managed Markdown path is outside authority") from error
    encoded = resolved.read_bytes()
    try:
        document = encoded.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContractValidationError("managed Markdown is not UTF-8") from error
    return parse_managed_markdown(relative, document, encoded_document=encoded)


def _read_managed_document_bounded(
    root: Path,
    path: Path,
    *,
    max_bytes: int,
) -> ManagedMarkdown | None:
    """Read one stable managed record without crossing the caller's byte budget."""

    if max_bytes < 0:
        raise ContractValidationError("managed Markdown byte budget is invalid")
    before = _materialized_path_facts(root, path)
    if before[3] != 1:
        raise ContractValidationError("managed Markdown is linked")
    if int(before[4]) > max_bytes:
        return None
    resolved = before[0]
    if not isinstance(resolved, Path):
        raise ContractValidationError("managed Markdown path identity is invalid")
    try:
        relative = resolved.relative_to(root).as_posix()
        with path.open("rb") as handle:
            encoded = handle.read(max_bytes + 1)
    except ValueError as error:
        raise ContractValidationError("managed Markdown is outside authority") from error
    except (FileNotFoundError, OSError) as error:
        raise ContractValidationError("managed Markdown changed while read") from error
    after = _materialized_path_facts(root, path)
    if before != after or len(encoded) != int(before[4]):
        raise ContractValidationError("managed Markdown changed while read")
    if len(encoded) > max_bytes:
        return None
    try:
        document = encoded.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContractValidationError("managed Markdown is not UTF-8") from error
    return parse_managed_markdown(relative, document, encoded_document=encoded)


def bootstrap_authority(root: Path, expected_authority_id: str) -> ManagedMarkdown:
    """Read only the named authority header before capability evaluation."""

    authority = _settings_authority_header(root, expected_authority_id)
    if legacy_migration_pending(_validated_root(root)):
        raise ContractValidationError("recover interrupted source-rights migration")
    _legacy_migration_receipt(_validated_root(root), authority)
    return authority


def _settings_authority_header(root: Path, expected_authority_id: str) -> ManagedMarkdown:
    """Read the same bounded header without ordinary migration recovery gates."""

    resolved_root = _validated_root(root)
    if (_effect_exists(resolved_root.parent.parent,
                       resolved_root.parent.parent / ".owledge/paired-restore.json")
            and not paired_restore_readback_active(resolved_root.parent.parent)):
        raise ContractValidationError("paired restore requires explicit Owner recovery")
    authority_path = resolved_root / ".owledge" / "authority.md"
    if not authority_path.is_file():
        raise ContractValidationError("authority document is missing")
    authority = _read_managed_document_bounded(resolved_root, authority_path, max_bytes=1_048_576)
    if authority is None:
        raise ContractValidationError("authority header exceeds its 1 MiB control limit")
    if (
        authority.metadata.get("schema") != "owledge.authority-unit/1"
        or authority.authority_id != expected_authority_id
    ):
        raise ContractValidationError("authority document identity does not match")
    return authority


_SETTINGS_LAYER_KEYS = {"schema", "document_version", "artifact_id", "authority_id", "revision",
                        "lifecycle", "processing_layer", "source_trust", "registry_sha256", "values"}


class SettingsQuarantineError(ContractValidationError):
    """A workspace layer is invalid or no longer matches its governed snapshot."""


def _settings_local(root: Path, authority: ManagedMarkdown, catalog: dict[str, object]) -> dict[str, object]:
    registry_sha256 = str(catalog["registry_sha256"])
    target = root / ".owledge" / "settings.md"
    relative = ".owledge/settings.md"
    result: dict[str, object] = {"authority_id": authority.authority_id, "relative_path": relative,
                                 "state": "absent", "settings_revision": authority.metadata.get("settings_revision"),
                                 "diagnostics": []}
    if not _effect_exists(root, target):
        if (authority.metadata.get("settings_source_sha256") not in (None, "absent")
                or authority.metadata.get("settings_registry_sha256") not in (None, registry_sha256)):
            result["state"] = "unbound"
            result["diagnostics"] = [{"code": "settings_snapshot_stale", "source": relative,
                                      "key": "settings_source_sha256", "rule": "bound layer disappeared",
                                      "repair": "Preview and apply local Owner settings repair."}]
        return result
    try:
        raw = _read_exact_effect(root, target, max_bytes=65_536)
        digest = sha256(raw).hexdigest()
        result["content_sha256"] = digest
        document = parse_managed_markdown(relative, raw.decode("utf-8"), encoded_document=raw)
        metadata = document.metadata
        required = {"schema": "owledge.settings-layer/1", "document_version": 1,
                    "artifact_id": f"settings:{authority.authority_id.replace(':', '-')}",
                    "authority_id": authority.authority_id, "lifecycle": "accepted",
                    "processing_layer": "configuration", "source_trust": "owner",
                    "registry_sha256": registry_sha256}
        problems = []
        for key in sorted(_SETTINGS_LAYER_KEYS - set(metadata)):
            problems.append((key, "required key is missing"))
        for key in sorted(set(metadata) - _SETTINGS_LAYER_KEYS):
            problems.append((key, "unknown key is not admitted"))
        for key, expected in required.items():
            if key in metadata and (type(metadata[key]) is not type(expected) or metadata[key] != expected):
                problems.append((key, "value must match the closed Settings contract"))
        if "revision" in metadata and (not isinstance(metadata["revision"], str) or not metadata["revision"]):
            problems.append(("revision", "nonempty revision is required"))
        if "values" in metadata:
            values = metadata["values"]
            if not isinstance(values, dict):
                problems.append(("values", "closed typed object is required"))
            else:
                for key in sorted(values):
                    spec = catalog["specs"].get(key)
                    if spec is None:
                        problems.append((str(key), "setting key is not in the verified registry"))
                    elif not isinstance(values[key], str) or values[key] not in spec["domain"]:
                        problems.append((str(key), "setting value is outside the declared enum domain"))
                if not problems:
                    result["values"] = dict(values)
        if document.body.strip():
            problems.append(("body", "Settings body must be empty"))
        if problems:
            result["state"] = "invalid"
            result["diagnostics"] = [{"code": "settings_invalid", "source": relative, "key": key,
                                      "rule": rule, "repair": "Preview and apply local Owner reset-empty repair."}
                                     for key, rule in problems]
            return result
        result["revision"] = document.revision
    except (ContractValidationError, OSError, UnicodeError, ValueError):
        result["state"] = "invalid"
        result["diagnostics"] = [{"code": "settings_invalid", "source": relative, "key": None,
                                  "rule": "closed Settings layer schema, version, registry and values required",
                                  "repair": "Preview and apply local Owner reset-empty repair."}]
        return result
    if (authority.metadata.get("settings_source_sha256") != digest
            or authority.metadata.get("settings_registry_sha256") != registry_sha256):
        result["state"] = "unbound"
        result["diagnostics"] = [{"code": "settings_snapshot_stale", "source": relative, "key": None,
                                  "rule": "valid layer differs from the governed authority snapshot",
                                  "repair": "Preview and apply local Owner settings repair."}]
    else:
        result["state"] = "valid"
    return result


def _settings_linked_global(root: Path, authority_id: str) -> Path | None:
    if not authority_id.startswith("project:"):
        return None
    workspace = root.parent
    state_path = workspace / "workspace.json"
    if not _effect_exists(workspace, state_path):
        return None
    state = json.loads(_read_exact_effect(workspace, state_path, max_bytes=65_536))
    if not isinstance(state, dict) or state.get("schema") != _LINKED_PROJECT_SCHEMA:
        return None
    linked = state.get("global_contribution")
    if not isinstance(linked, dict) or not isinstance(linked.get("workspace"), str):
        raise ContractValidationError("linked Settings authority is invalid")
    _, global_workspace = _reuse_roots(workspace, linked["workspace"])
    return global_workspace / "global"


def inspect_settings(root: Path, authority_id: str) -> dict[str, object]:
    """Inspect the complete bounded empty-catalog layer without applying an effect."""
    from .contracts import verified_settings_catalog
    catalog = verified_settings_catalog()
    resolved = _validated_root(root)
    authority = _settings_authority_header(resolved, authority_id)
    layer = _settings_local(resolved, authority, catalog)
    layers = [layer]
    if _effect_exists(resolved, resolved / ".owledge/settings-repair.json"):
        layer["diagnostics"].append({"code": "settings_repair_pending", "source": ".owledge/settings-repair.json",
                                     "key": None, "rule": "governed repair is interrupted",
                                     "repair": "Use explicit local Owner settings repair --recover."})
    if _effect_exists(resolved, resolved / ".owledge/settings-repair-link.json"):
        layer["diagnostics"].append({"code": "settings_linked_repair_pending", "source": ".owledge/settings-repair-link.json",
                                     "key": None, "rule": "linked Project Settings repair is interrupted",
                                     "repair": "Recover the linked Project Settings repair."})
    global_root = _settings_linked_global(resolved, authority_id)
    if global_root is not None:
        global_authority = _settings_authority_header(global_root, _REUSE_GLOBAL)
        global_layer = _settings_local(global_root, global_authority, catalog)
        if _effect_exists(global_root, global_root / ".owledge/settings-repair.json"):
            global_layer["diagnostics"].append({"code": "settings_repair_pending",
                "source": ".owledge/settings-repair.json", "key": None,
                "rule": "linked Global Settings repair is interrupted",
                "repair": "Recover the Global Settings repair at its own workspace."})
        if _effect_exists(global_root, global_root / ".owledge/settings-repair-link.json"):
            global_layer["diagnostics"].append({"code": "settings_linked_repair_pending",
                "source": ".owledge/settings-repair-link.json", "key": None,
                "rule": "linked Project Settings repair is interrupted",
                "repair": "Recover the linked Project Settings repair."})
        layers.insert(0, global_layer)
    effective = dict(catalog["defaults"])
    sources = {key: "catalog" for key in effective}
    for current in layers:
        if current["state"] == "valid":
            for key, value in current.get("values", {}).items():
                effective[key] = value
                sources[key] = current["authority_id"]
    for family in ("recall", "research"):
        domain = catalog["specs"][family + "_default"]["domain"]
        if domain.index(effective[family + "_default"]) > domain.index(effective[family + "_max_auto"]):
            layers[-1]["diagnostics"].append({"code": "settings_precedence_invalid",
                "source": layers[-1]["relative_path"], "key": family + "_default",
                "rule": "effective default exceeds the applicable Owner maximum",
                "repair": "Adjust the local override or maximum through Owner settings configure."})
    diagnostics = [item for current in layers for item in current["diagnostics"]]
    snapshot = sha256(json.dumps({"registry_sha256": catalog["registry_sha256"], "layers": [
        {"authority_id": item["authority_id"], "state": item["state"],
         "content_sha256": item.get("content_sha256"), "settings_revision": item.get("settings_revision")}
        for item in layers]}, sort_keys=True).encode()).hexdigest()
    return {"status": "ready" if not diagnostics else "quarantined", "registry_id": catalog["registry_id"],
            "registry_sha256": catalog["registry_sha256"], "bundle_sha256": catalog["bundle_sha256"],
            "layers": layers, "effective": effective, "sources": sources, "diagnostics": diagnostics,
            "snapshot_sha256": snapshot}


def require_settings_healthy(root: Path, authority_id: str) -> None:
    inspected = inspect_settings(root, authority_id)
    if inspected["status"] != "ready":
        raise SettingsQuarantineError("Settings quarantine requires explicit local Owner repair")


def settings_snapshot_token(root: Path, authority_id: str) -> str:
    inspected = inspect_settings(root, authority_id)
    if inspected["status"] != "ready":
        raise SettingsQuarantineError("Settings snapshot is quarantined")
    return str(inspected["snapshot_sha256"])


def _settings_repair_plan(root: Path, authority_id: str, authority_raw: bytes,
                          layer_raw: bytes | None, registry_sha256: str,
                          linked_binding: object = None, values: dict[str, str] | None = None) -> dict[str, object]:
    from .contracts import verified_settings_catalog
    catalog = verified_settings_catalog()
    values = {} if values is None else dict(sorted(values.items()))
    if (registry_sha256 != catalog["registry_sha256"] or any(
            key not in catalog["specs"] or not isinstance(value, str)
            or value not in catalog["specs"][key]["domain"] for key, value in values.items())):
        raise ContractValidationError("proposed Settings values are invalid")
    effective = dict(catalog["defaults"])
    sources = {key: "catalog" for key in effective}
    for item in linked_binding or []:
        for key, value in item.get("values", {}).items():
            effective[key], sources[key] = value, item["authority_id"]
    for key, value in values.items():
        effective[key], sources[key] = value, authority_id
    for family in ("recall", "research"):
        domain = catalog["specs"][family + "_default"]["domain"]
        if domain.index(effective[family + "_default"]) > domain.index(effective[family + "_max_auto"]):
            raise ContractValidationError("effective Settings default exceeds the Owner maximum")
    authority = parse_managed_markdown(".owledge/authority.md", authority_raw.decode("utf-8"),
                                       encoded_document=authority_raw)
    if authority.authority_id != authority_id or authority.metadata.get("schema") != "owledge.authority-unit/1":
        raise ContractValidationError("Settings repair authority is invalid")
    old_hash = sha256(layer_raw).hexdigest() if layer_raw is not None else "absent"
    identity = sha256((authority.content_sha256 + old_hash + registry_sha256
                       + json.dumps(values, sort_keys=True)).encode()).hexdigest()[:16]
    revision = f"settings-rev-{identity}"
    layer_meta = {"schema": "owledge.settings-layer/1", "document_version": 1,
                  "artifact_id": f"settings:{authority_id.replace(':', '-')}", "authority_id": authority_id,
                  "revision": revision, "lifecycle": "accepted", "processing_layer": "configuration",
                  "source_trust": "owner", "registry_sha256": registry_sha256, "values": values}
    layer_document = _render_metadata_document(layer_meta, "\n")
    layer_hash = sha256(layer_document.encode("utf-8")).hexdigest()
    settings_revision = f"settings-{identity}"
    auth_meta = dict(authority.metadata)
    auth_meta.update(revision=f"authority-{identity}", settings_revision=settings_revision,
                     settings_source_sha256=layer_hash, settings_registry_sha256=registry_sha256)
    authority_document = _render_metadata_document(auth_meta, authority.body)
    receipt_id = f"receipt:{authority_id.replace(':', '-')}:settings-{identity}"
    receipt_meta = {"schema": "owledge.receipt/1", "document_version": 1, "receipt_id": receipt_id,
                    "authority_id": authority_id, "operation": "settings_repair", "outcome": "ok/settings_repaired",
                    "base_revision": authority.revision, "result_revision": settings_revision,
                    "source_sha256": old_hash, "result_sha256": layer_hash, "registry_sha256": registry_sha256}
    receipt_document = _render_metadata_document(receipt_meta, "\nSettings repair applied.\n")
    binding = {"authority_id": authority_id, "authority_sha256": authority.content_sha256,
               "old_sha256": old_hash, "new_sha256": layer_hash, "registry_sha256": registry_sha256,
               "settings_revision": settings_revision, "linked_binding": linked_binding, "values": values}
    expected = sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    return {"status": "preview", "expected_sha256": expected, "authority_id": authority_id,
            "relative_path": ".owledge/settings.md", "old_sha256": old_hash, "new_sha256": layer_hash,
            "registry_sha256": registry_sha256, "values": values, "effective": effective, "sources": sources,
            "settings_revision": settings_revision,
            "receipt_id": receipt_id, "authority_document": authority_document,
            "layer_document": layer_document, "receipt_document": receipt_document}


def _settings_repair_bytes(root: Path) -> tuple[bytes, bytes | None]:
    authority = _read_exact_effect(root, root / ".owledge/authority.md", max_bytes=1_048_576)
    layer_path = root / ".owledge/settings.md"
    layer = _read_exact_effect(root, layer_path, max_bytes=1_048_576) if _effect_exists(root, layer_path) else None
    return authority, layer


def _settings_other_binding(inspected: dict[str, object], authority_id: str) -> list[dict[str, object]]:
    return [{"authority_id": item["authority_id"], "state": item["state"],
             "content_sha256": item.get("content_sha256"), "settings_revision": item.get("settings_revision"),
             "values": item.get("values", {})}
            for item in inspected["layers"] if item["authority_id"] != authority_id]


def recover_settings_repair(root: Path, authority_id: str) -> dict[str, object]:
    """Redo only a reconstructed, exact local Settings repair journal."""
    from .contracts import verified_settings_catalog
    resolved = _validated_root(root)
    journal_path = resolved / ".owledge/settings-repair.json"
    linked_root = _settings_linked_global(resolved, authority_id)
    marker_path = linked_root / ".owledge/settings-repair-link.json" if linked_root is not None else None
    if not _effect_exists(resolved, journal_path) and marker_path is not None and _effect_exists(linked_root, marker_path):
        marker = json.loads(_read_exact_effect(linked_root, marker_path, max_bytes=4096))
        current_authority, current_layer = _settings_repair_bytes(resolved)
        observed_pair = (sha256(current_authority).hexdigest(),
                         sha256(current_layer).hexdigest() if current_layer is not None else "absent")
        prior_pair = (marker.get("authority_sha256"), marker.get("layer_sha256")) if isinstance(marker, dict) else None
        after_pair = (marker.get("after_authority_sha256"), marker.get("after_layer_sha256")) if isinstance(marker, dict) else None
        if (not isinstance(marker, dict) or marker.get("schema") != "owledge.settings-repair-link/1"
                or marker.get("project_root") != str(resolved) or marker.get("authority_id") != authority_id
                or observed_pair not in (prior_pair, after_pair)):
            raise ContractValidationError("orphan linked Settings marker differs")
        if observed_pair == after_pair:
            receipt_id = marker.get("receipt_id")
            if not isinstance(receipt_id, str) or not re.fullmatch(r"receipt:[a-z0-9:-]+", receipt_id):
                raise ContractValidationError("orphan linked Settings receipt identity is invalid")
            receipt_path = resolved / ".owledge/receipts" / f"{receipt_id.replace(':', '-')}.md"
            if not _effect_exists(resolved, receipt_path):
                raise ContractValidationError("orphan linked Settings marker lacks a receipt")
        _unlink_effect(linked_root, marker_path)
        return {"status": "ready", "recovered": "orphan_marker", "authority_id": authority_id}
    raw = _read_exact_effect(resolved, journal_path, max_bytes=4_300_000)
    try:
        journal = json.loads(raw)
        if (not isinstance(journal, dict) or set(journal) != {"schema", "authority_id", "registry_sha256",
                "before_authority", "before_layer_hex", "expected_sha256", "linked_binding", "values"}
                or journal["schema"] != "owledge.settings-repair/1" or journal["authority_id"] != authority_id
                or not isinstance(journal["before_authority"], str)
                or journal["before_layer_hex"] is not None and not isinstance(journal["before_layer_hex"], str)):
            raise ContractValidationError("Settings repair journal is malformed")
        registry_sha = str(verified_settings_catalog()["registry_sha256"])
        if journal["registry_sha256"] != registry_sha:
            raise ContractValidationError("Settings repair catalog changed")
        inspected = inspect_settings(resolved, authority_id)
        if _settings_other_binding(inspected, authority_id) != journal["linked_binding"]:
            raise ContractValidationError("linked Settings changed during repair")
        before_authority = journal["before_authority"].encode("utf-8")
        before_layer = bytes.fromhex(journal["before_layer_hex"]) if journal["before_layer_hex"] is not None else None
        plan = _settings_repair_plan(resolved, authority_id, before_authority, before_layer, registry_sha,
                                     journal["linked_binding"], journal["values"])
        if plan["expected_sha256"] != journal["expected_sha256"]:
            raise ContractValidationError("Settings repair journal binding changed")
        if marker_path is not None:
            marker = json.loads(_read_exact_effect(linked_root, marker_path, max_bytes=4096))
            if marker != {"schema": "owledge.settings-repair-link/1", "project_root": str(resolved),
                           "authority_id": authority_id, "expected_sha256": journal["expected_sha256"],
                           "authority_sha256": sha256(before_authority).hexdigest(),
                           "layer_sha256": sha256(before_layer).hexdigest() if before_layer is not None else "absent",
                           "after_authority_sha256": sha256(str(plan["authority_document"]).encode()).hexdigest(),
                           "after_layer_sha256": plan["new_sha256"], "receipt_id": plan["receipt_id"]}:
                raise ContractValidationError("linked Settings repair marker differs")
    except (UnicodeError, ValueError, KeyError, TypeError) as error:
        raise ContractValidationError("Settings repair journal is invalid") from error
    targets = ((resolved / ".owledge/settings.md", before_layer, str(plan["layer_document"]).encode("utf-8")),
               (resolved / ".owledge/authority.md", before_authority, str(plan["authority_document"]).encode("utf-8")),
               (resolved / ".owledge/receipts" / f"{str(plan['receipt_id']).replace(':', '-')}.md", None,
                str(plan["receipt_document"]).encode("utf-8")))
    for target, before, after in targets:
        observed = _read_exact_effect(resolved, target, max_bytes=1_048_576) if _effect_exists(resolved, target) else None
        if observed not in (before, after):
            raise ContractValidationError("Settings repair target changed during recovery")
    for target, _, after in targets:
        if not _effect_exists(resolved, target) or _read_exact_effect(resolved, target, max_bytes=1_048_576) != after:
            _write_exact_atomic(resolved, target, after.decode("utf-8"))
    require_layer = _settings_local(resolved, bootstrap_authority(resolved, authority_id),
                                    verified_settings_catalog())
    if require_layer["state"] != "valid":
        raise ContractValidationError("Settings repair read-back differs")
    _unlink_effect(resolved, journal_path)
    if marker_path is not None:
        _unlink_effect(linked_root, marker_path)
    return {"status": "ready", "authority_id": authority_id, "settings_revision": plan["settings_revision"],
            "receipt_id": plan["receipt_id"], "registry_sha256": registry_sha,
            "values": plan["values"], "effective": plan["effective"], "sources": plan["sources"]}


def change_settings_layer(root: Path, authority_id: str, *, expected_sha256: str | None = None,
                          apply: bool = False, recover: bool = False,
                          reset_empty: bool = True, updates: dict[str, str] | None = None,
                          unset: tuple[str, ...] = ()) -> dict[str, object]:
    """Owner-only exact reset of one fixed local layer; no arbitrary settings paths."""
    from .contracts import verified_settings_catalog
    resolved = _validated_root(root)
    if recover:
        linked_root = _settings_linked_global(resolved, authority_id)
        with authority_write_locks((resolved,) if linked_root is None else (resolved, linked_root), allow_settings_repair=True):
            return recover_settings_repair(resolved, authority_id)
    inspected = inspect_settings(resolved, authority_id)
    if _effect_exists(resolved, resolved / ".owledge/settings-repair-link.json"):
        raise SettingsQuarantineError("recover the linked Project Settings repair first")
    if any(item["authority_id"] != authority_id and item["diagnostics"] for item in inspected["layers"]):
        raise SettingsQuarantineError("repair linked Global Settings at its own authority first")
    if _effect_exists(resolved, resolved / ".owledge/settings-repair.json"):
        raise SettingsQuarantineError("recover the pending Settings repair first")
    registry_sha = str(verified_settings_catalog()["registry_sha256"])
    catalog = verified_settings_catalog()
    if reset_empty:
        if updates or unset:
            raise ContractValidationError("reset-empty cannot contain Settings overrides")
        values = {}
    else:
        local = next(item for item in inspected["layers"] if item["authority_id"] == authority_id)
        if local["state"] in {"invalid", "unbound"}:
            raise SettingsQuarantineError("repair the local Settings layer before configuring overrides")
        values = dict(local.get("values", {}))
        for key in unset:
            if key not in catalog["specs"]:
                raise ContractValidationError("unknown Settings override cannot be removed")
            values.pop(key, None)
        for key, value in (updates or {}).items():
            values[key] = value
    before_authority, before_layer = _settings_repair_bytes(resolved)
    linked_binding = _settings_other_binding(inspected, authority_id)
    plan = _settings_repair_plan(resolved, authority_id, before_authority, before_layer, registry_sha,
                                 linked_binding, values)
    if not apply:
        return {key: value for key, value in plan.items() if not key.endswith("_document")}
    if expected_sha256 != plan["expected_sha256"]:
        raise ContractValidationError("Settings repair preview is stale")
    linked_root = _settings_linked_global(resolved, authority_id)
    with authority_write_locks((resolved,) if linked_root is None else (resolved, linked_root), allow_settings_repair=True):
        fresh_inspected = inspect_settings(resolved, authority_id)
        if any(item["authority_id"] != authority_id and item["diagnostics"] for item in fresh_inspected["layers"]):
            raise SettingsQuarantineError("linked Global Settings changed")
        if _settings_other_binding(fresh_inspected, authority_id) != linked_binding:
            raise ContractValidationError("linked Settings changed after preview")
        fresh_authority, fresh_layer = _settings_repair_bytes(resolved)
        fresh = _settings_repair_plan(resolved, authority_id, fresh_authority, fresh_layer, registry_sha,
                                      linked_binding, values)
        if fresh["expected_sha256"] != expected_sha256:
            raise ContractValidationError("Settings repair preview changed under lock")
        journal = {"schema": "owledge.settings-repair/1", "authority_id": authority_id,
                   "registry_sha256": registry_sha, "before_authority": fresh_authority.decode("utf-8"),
                   "before_layer_hex": fresh_layer.hex() if fresh_layer is not None else None,
                   "expected_sha256": expected_sha256, "linked_binding": linked_binding, "values": values}
        encoded = json.dumps(journal, ensure_ascii=False, sort_keys=True)
        if len(encoded.encode("utf-8")) > 4_300_000:
            raise ContractValidationError("Settings repair journal exceeds its bound")
        if linked_root is not None:
            marker = {"schema": "owledge.settings-repair-link/1", "project_root": str(resolved),
                      "authority_id": authority_id, "expected_sha256": expected_sha256,
                      "authority_sha256": sha256(fresh_authority).hexdigest(),
                      "layer_sha256": sha256(fresh_layer).hexdigest() if fresh_layer is not None else "absent",
                      "after_authority_sha256": sha256(str(fresh["authority_document"]).encode()).hexdigest(),
                      "after_layer_sha256": fresh["new_sha256"], "receipt_id": fresh["receipt_id"]}
            _write_exact_atomic(linked_root, linked_root / ".owledge/settings-repair-link.json",
                                json.dumps(marker, ensure_ascii=False, sort_keys=True))
        _write_exact_atomic(resolved, resolved / ".owledge/settings-repair.json", encoded)
        return recover_settings_repair(resolved, authority_id)


def local_connection_principal(authority_id: str, name: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", name):
        raise ContractValidationError("connection name is invalid")
    return "principal:local-connection-" + sha256((authority_id + "\0" + name).encode("utf-8")).hexdigest()[:24]


_LEGACY_MIGRATION_SCHEMA = "owledge.source-rights-migration/1"
_LEGACY_MIGRATION_JOURNAL = ".owledge/source-rights-migration.json"
_LEGACY_MIGRATION_RECEIPT = ".owledge/receipts/receipt-user-global-source-access-rights-migration.md"


def legacy_migration_pending(global_root: Path) -> bool:
    root = _validated_root(global_root)
    return _effect_exists(root, root / _LEGACY_MIGRATION_JOURNAL)


def _legacy_migration_receipt(root: Path, authority: ManagedMarkdown) -> dict[str, object] | None:
    epoch = authority.metadata.get("rights_migration_epoch")
    if epoch is None:
        return None
    if not isinstance(epoch, str) or not re.fullmatch(r"[0-9a-f]{64}", epoch):
        raise ContractValidationError("rights migration epoch is invalid")
    receipt, _ = _read_effect_metadata(root, root / _LEGACY_MIGRATION_RECEIPT)
    if (receipt.get("schema") != "owledge.receipt/1"
            or receipt.get("receipt_id") != "receipt:user-global-source-access:rights-migration"
            or receipt.get("authority_id") != authority.authority_id
            or receipt.get("operation") != "source_rights_migrate"
            or receipt.get("outcome") != "ok/rights_migrated"
            or receipt.get("result_revision") != "rights-migration-" + epoch[:16]
            or receipt.get("migration_epoch") != epoch
            or not isinstance(receipt.get("legacy_inventory"), dict)):
        raise ContractValidationError("rights migration receipt is missing or changed")
    return receipt


def migration_epoch(root: Path, authority_id: str) -> str | None:
    authority = bootstrap_authority(root, authority_id)
    return authority.metadata.get("rights_migration_epoch")


def migration_derived_allowed(root: Path, document: ManagedMarkdown) -> bool:
    """Only an exact post-migration promotion is current derived knowledge."""
    if ("curation_effect" not in document.metadata
            and document.metadata.get("knowledge_kind") is None
            and document.metadata.get("schema") not in {"owledge.bundle/1", "owledge.candidate/1"}):
        return True
    epoch = migration_epoch(root, document.authority_id)
    if epoch is None:
        return True
    envelope = document.metadata.get("curation_effect")
    receipt_id = envelope.get("receipt_id") if isinstance(envelope, dict) else None
    if not isinstance(receipt_id, str) or not re.fullmatch(r"receipt:[a-zA-Z0-9:_-]+", receipt_id):
        return False
    try:
        receipt, _ = _read_effect_metadata(_validated_root(root), _validated_root(root) / ".owledge" /
                                           "receipts" / f"{receipt_id.replace(':', '-')}.md")
    except (ContractValidationError, OSError):
        return False
    return (receipt.get("schema") == "owledge.receipt/1"
            and receipt.get("authority_id") == document.authority_id
            and receipt.get("operation") == "candidate_promote"
            and receipt.get("outcome") == "ok/candidate_promoted"
            and receipt.get("migration_epoch") == epoch
            and receipt.get("result_revision") == document.revision
            and receipt.get("result_sha256") == document.content_sha256)


def migration_legacy_reference_allowed(root: Path, document: ManagedMarkdown) -> bool:
    """Permit Owner inspection/re-preview only for exact bytes inventoried at cutover."""
    if (document.metadata.get("knowledge_kind") != "reference"
            or not document.artifact_id.startswith("memory:user-global-source-access-source-")):
        return False
    resolved = _validated_root(root)
    authority = bootstrap_authority(resolved, document.authority_id)
    receipt = _legacy_migration_receipt(resolved, authority)
    inventory = receipt.get("legacy_inventory") if isinstance(receipt, dict) else None
    if not isinstance(inventory, dict):
        return False
    slug = document.artifact_id.removeprefix("memory:user-global-source-access-source-")
    current_path = resolved / ".owledge" / "curated" / f"source-{slug}.md"
    current = _read_managed_document_bounded(resolved, current_path, max_bytes=65_536)
    if current is None or current.artifact_id != document.artifact_id:
        return False
    relative = (current_path if current.revision == document.revision
                else _reference_history_target(resolved, document.artifact_id, document.revision)).relative_to(resolved).as_posix()
    if inventory.get(relative) == document.content_sha256:
        return True
    # An exact old current reference moves to the history path during the first
    # post-migration refresh. Its original cutover bytes remain the authority.
    original_current = current_path.relative_to(resolved).as_posix()
    return (relative != original_current
            and inventory.get(original_current) == document.content_sha256)


def _migration_preview_receipt(root: Path, authority_id: str, candidate_id: str,
                               candidate_kind: str) -> dict[str, object]:
    suffix = (sha256(candidate_id.encode("utf-8")).hexdigest()[:16]
              if candidate_kind in {"global_curation", "global_essence", "source_curation", "lesson_capture",
                                    "project_record", "project_essence"}
              else candidate_id.rsplit("-", 1)[-1])
    receipt_id = f"receipt:{authority_id.replace(':', '-')}:candidate-preview-{suffix}"
    receipt, _ = _read_effect_metadata(root, root / ".owledge" / "receipts" /
                                       f"{receipt_id.replace(':', '-')}.md")
    return receipt


def verify_migration_candidate_issuance(root: Path, authority_id: str,
                                        candidate: dict[str, object], changeset: dict[str, object]) -> str | None:
    epoch = migration_epoch(root, authority_id)
    if epoch is None:
        return None
    candidate_id = candidate.get("candidate_id")
    if not isinstance(candidate_id, str):
        raise ContractValidationError("Candidate identity is missing")
    receipt = _migration_preview_receipt(_validated_root(root), authority_id, candidate_id,
                                         str(candidate.get("candidate_kind")))
    initial = dict(candidate)
    if initial.get("lifecycle") == "reviewed":
        initial.pop("reviewed_by", None)
        initial.pop("reviewed_result_sha256", None)
        initial["lifecycle"] = "candidate"
        reviewed_revision = initial.get("candidate_revision")
        if not isinstance(reviewed_revision, str) or not reviewed_revision.startswith("candidate-rev-2-reviewed"):
            raise ContractValidationError("reviewed Candidate revision is invalid")
        initial["candidate_revision"] = "candidate-rev-1" + reviewed_revision.removeprefix("candidate-rev-2-reviewed")
    if (receipt.get("migration_epoch") != epoch
            or receipt.get("authority_id") != authority_id
            or receipt.get("result_revision") != initial.get("candidate_revision")
            or receipt.get("candidate_binding_sha256") != _effect_binding_hash(initial)
            or receipt.get("changeset_binding_sha256") != _effect_binding_hash(changeset)):
        raise ContractValidationError("Candidate predates rights migration or differs from issued preview")
    return epoch


def _render_metadata_document(metadata: dict, body: str) -> str:
    return "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False, separators=(',', ':'))}"
                                for key, value in metadata.items()) + "\n---\n" + body


def _legacy_read(root: Path, target: Path, maximum: int) -> bytes:
    contained = _validated_effect_path(root, target, must_exist=True)
    with contained.open("rb") as handle:
        facts = os.fstat(handle.fileno())
        if not stat.S_ISREG(facts.st_mode) or facts.st_nlink != 1 or facts.st_size > maximum:
            raise ContractValidationError("legacy migration input exceeds bounded review")
        encoded = handle.read(maximum + 1)
    if len(encoded) > maximum:
        raise ContractValidationError("legacy migration input exceeds bounded review")
    return encoded


def _legacy_inventory(global_root: Path, excluded: set[str]) -> dict[str, str]:
    root = _validated_root(global_root)
    controls = root / ".owledge"
    if not controls.is_dir() or controls.is_symlink():
        raise ContractValidationError("legacy authority metadata is unavailable")
    inventory: dict[str, str] = {}
    total = 0
    pending = [controls]
    entries_seen = 0
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as scan:
            for entry in scan:
                entries_seen += 1
                if entries_seen > 4096 or entry.is_symlink():
                    raise ContractValidationError("legacy inventory exceeds bounded review or crosses a link")
                path = Path(entry.path)
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                    continue
                if not entry.is_file(follow_symlinks=False):
                    raise ContractValidationError("legacy inventory contains an unsupported entry")
                relative = path.relative_to(root).as_posix()
                if relative in excluded:
                    continue
                size = entry.stat(follow_symlinks=False).st_size
                if len(inventory) >= 1024 or size > 16_777_216 - total:
                    raise ContractValidationError("legacy inventory exceeds bounded review")
                contained = _validated_effect_path(root, path, must_exist=True)
                with contained.open("rb") as handle:
                    facts = os.fstat(handle.fileno())
                    if not stat.S_ISREG(facts.st_mode) or facts.st_nlink != 1:
                        raise ContractValidationError("legacy inventory file is invalid")
                    encoded = handle.read(16_777_216 - total + 1)
                total += len(encoded)
                if total > 16_777_216:
                    raise ContractValidationError("legacy inventory exceeds bounded review")
                inventory[relative] = sha256(encoded).hexdigest()
    return inventory


def _legacy_migration_plan(workspace: Path, *, preimages: dict[str, str] | None = None) -> dict[str, object]:
    root = _validated_root(workspace)
    global_root = _validated_root(root / "global")
    transactions = global_root / ".owledge" / "transactions"
    if transactions.exists():
        if transactions.is_symlink() or not transactions.is_dir():
            raise ContractValidationError("recover pending canonical transaction before rights migration")
        with os.scandir(transactions) as scan:
            if next(scan, None) is not None:
                raise ContractValidationError("recover pending canonical transaction before rights migration")
    state_bytes = _legacy_read(root, root / "workspace.json", 262_144)
    state = json.loads(state_bytes)
    if (not isinstance(state, dict) or state.get("schema") not in {
            "owledge.private-knowledge-workspace/1", "owledge.private-knowledge-workspace/2",
            "owledge.private-knowledge-workspace/3"}
            or not isinstance(state.get("imports", []), list) or len(state.get("imports", [])) > 64):
        raise ContractValidationError("unsupported legacy Knowledge workspace")
    links: dict[str, str] = {}
    if state.get("source_id") is not None:
        links[".owledge/raw-link.md"] = state["source_id"]
    for entry in state.get("imports", []):
        if (not isinstance(entry, dict) or not isinstance(entry.get("source_id"), str)
                or not re.fullmatch(r"source:[a-z0-9-]+", entry["source_id"])
                or entry.get("source_link_id") != "link:import-" + entry["source_id"].removeprefix("source:")):
            raise ContractValidationError("legacy source registration is invalid")
        links[f".owledge/import-{entry['source_id'].removeprefix('source:')}.md"] = entry["source_id"]
    expected = {".owledge/authority.md", *links}
    before = preimages if preimages is not None else {
        relative: _legacy_read(global_root, global_root / relative, 65_536).decode("utf-8")
        for relative in expected}
    if set(before) != expected:
        raise ContractValidationError("legacy migration preimages are incomplete")
    if any(not isinstance(value, str) or len(value.encode("utf-8")) > 65_536 for value in before.values()):
        raise ContractValidationError("legacy migration preimage exceeds bounded review")
    authority = parse_managed_markdown(".owledge/authority.md", before[".owledge/authority.md"])
    metadata = dict(authority.metadata)
    if (authority.authority_id != "user-global:source-access"
            or metadata.get("schema") != "owledge.authority-unit/1"
            or metadata.get("mode") != "read_write"
            or "rights_era" in metadata or "connections" in metadata
            or "rights_migration_epoch" in metadata
            or not isinstance(metadata.get("actor_grants"), dict)
            or "promote" not in metadata["actor_grants"].get("principal:local-owner", [])):
        raise ContractValidationError("legacy local Owner authority is unsupported")
    inventory = _legacy_inventory(global_root, expected | {_LEGACY_MIGRATION_JOURNAL, _LEGACY_MIGRATION_RECEIPT})
    before_hashes = {key: sha256(value.encode("utf-8")).hexdigest() for key, value in before.items()}
    epoch = sha256(json.dumps({"state": sha256(state_bytes).hexdigest(), "before": before_hashes,
                               "inventory": inventory}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    version = metadata.get("document_version")
    if type(version) is not int or version < 1:
        raise ContractValidationError("legacy authority version is invalid")
    metadata.update(rights_era="owledge.bound-source-rights/1", connections={},
                    rights_migration_epoch=epoch, document_version=version + 1,
                    revision="rights-migration-" + epoch[:16], policy_revision="policy-rights-migration-" + epoch[:16])
    after: dict[str, str] = {}
    for relative, source_id in links.items():
        link = parse_managed_markdown(relative, before[relative])
        fields = dict(link.metadata)
        if (fields.get("schema") != "owledge.knowledge-source-link/1"
                or fields.get("authority_id") != authority.authority_id
                or fields.get("linked_authority_id") != source_id
                or fields.get("source_link_id") != link.artifact_id
                or fields.get("grants") != ["discover", "keyword_retrieve"]
                or "source_access" in fields):
            raise ContractValidationError("legacy raw Source Link is unsupported")
        number = fields.get("document_version")
        if type(number) is not int or number < 1:
            raise ContractValidationError("legacy raw Source Link version is invalid")
        fields.update(source_access={"access": "restricted", "principals": ["principal:local-owner"]},
                      document_version=number + 1, revision="rights-migration-" + epoch[:16])
        after[relative] = _render_metadata_document(fields, link.body)
    receipt = ("---\nschema: owledge.receipt/1\ndocument_version: 1\n"
               "receipt_id: receipt:user-global-source-access:rights-migration\n"
               "authority_id: user-global:source-access\noperation: source_rights_migrate\n"
               "outcome: ok/rights_migrated\nbase_revision: legacy\n"
               f"result_revision: {metadata['revision']}\nmigration_epoch: {epoch}\n"
               f"prior_authority_sha256: {before_hashes['.owledge/authority.md']}\n"
               f"legacy_inventory: {json.dumps(inventory, ensure_ascii=False, sort_keys=True, separators=(',', ':'))}\n"
               "---\n\n# Source rights migration\n\nOld derived knowledge remains quarantined.\n")
    after[_LEGACY_MIGRATION_RECEIPT] = receipt
    after[".owledge/authority.md"] = _render_metadata_document(metadata, authority.body)
    journal = {"schema": _LEGACY_MIGRATION_SCHEMA, "before": before, "after": after,
               "epoch": epoch, "state_sha256": sha256(state_bytes).hexdigest(), "inventory": inventory}
    if len(json.dumps(journal, ensure_ascii=False, sort_keys=True).encode("utf-8")) > 262_144:
        raise ContractValidationError("rights migration journal exceeds bounded review")
    return {"before": before, "after": after, "epoch": epoch, "inventory": inventory,
            "state_sha256": sha256(state_bytes).hexdigest(), "before_hashes": before_hashes,
            "preview": {"status": "preview", "authority_id": authority.authority_id,
                        "expected_sha256": epoch, "raw_links": sorted(links), "raw_access_after": "owner_only",
                        "quarantined_documents": len(inventory), "quarantined_bytes": sum(
                            (global_root / relative).stat().st_size for relative in inventory),
                        "actor_grants_preserved": True, "connections_after": {},
                        "message": "Old derived knowledge and pending Candidates remain quarantined; review each fresh revision."}}


def migrate_legacy_source_rights(workspace: Path, *, expected_sha256: str | None = None,
                                 apply: bool = False, recover: bool = False) -> dict[str, object]:
    """Owner-approved bounded raw-rights cutover with exact redo recovery."""
    root = _validated_root(workspace)
    global_root = _validated_root(root / "global")
    journal_path = global_root / _LEGACY_MIGRATION_JOURNAL

    def finish_journal() -> dict[str, object]:
        encoded = _legacy_read(global_root, journal_path, 262_144)
        journal = json.loads(encoded)
        if (not isinstance(journal, dict) or journal.get("schema") != _LEGACY_MIGRATION_SCHEMA
                or not isinstance(journal.get("before"), dict)
                or not isinstance(journal.get("after"), dict)
                or not isinstance(journal.get("epoch"), str)):
            raise ContractValidationError("rights migration journal is invalid")
        plan = _legacy_migration_plan(root, preimages=journal["before"])
        if (journal.get("after") != plan["after"] or journal.get("epoch") != plan["epoch"]
                or journal.get("state_sha256") != plan["state_sha256"]
                or journal.get("inventory") != plan["inventory"]):
            raise ContractValidationError("rights migration journal differs from exact Owner plan")
        for relative, content in plan["after"].items():
            target = global_root / relative
            before = plan["before"].get(relative)
            current = _legacy_read(global_root, target, max(len(str(before).encode("utf-8")),
                len(content.encode("utf-8")))).decode("utf-8") if _effect_exists(global_root, target) else None
            if current not in (before, content):
                raise ContractValidationError("rights migration target changed during recovery")
        for relative in [*sorted(set(plan["after"]) - {".owledge/authority.md"}), ".owledge/authority.md"]:
            target = global_root / relative
            if not _effect_exists(global_root, target) or _legacy_read(global_root, target,
                    max(len(plan["after"][relative].encode("utf-8")),
                        len(str(plan["before"].get(relative, "")).encode("utf-8")))).decode("utf-8") != plan["after"][relative]:
                _write_exact_atomic(global_root, target, plan["after"][relative])
        _unlink_effect(global_root, journal_path)
        return {**plan["preview"], "status": "ready", "message": "Raw sources are Owner-only; old derived knowledge is quarantined."}

    if not apply and not recover:
        if _effect_exists(global_root, journal_path):
            raise ContractValidationError("recover interrupted rights migration first")
        if (_effect_exists(global_root, global_root / ".owledge/pending-effect.json")
                or _effect_exists(root, root / ".owledge/source-registration.json")):
            raise ContractValidationError("recover other pending work before rights migration")
        return _legacy_migration_plan(root)["preview"]
    with authority_write_locks((root, global_root)):
        if recover:
            if not _effect_exists(global_root, journal_path):
                raise ContractValidationError("no interrupted rights migration exists")
            return finish_journal()
        if _effect_exists(global_root, journal_path):
            raise ContractValidationError("recover interrupted rights migration first")
        if (_effect_exists(global_root, global_root / ".owledge/pending-effect.json")
                or _effect_exists(root, root / ".owledge/source-registration.json")):
            raise ContractValidationError("recover other pending work before rights migration")
        plan = _legacy_migration_plan(root)
        if expected_sha256 != plan["epoch"]:
            raise ContractValidationError("rights migration changed after preview")
        journal = {"schema": _LEGACY_MIGRATION_SCHEMA, "before": plan["before"],
                   "after": plan["after"], "epoch": plan["epoch"],
                   "state_sha256": plan["state_sha256"], "inventory": plan["inventory"]}
        _write_exact_atomic(global_root, journal_path, json.dumps(journal, ensure_ascii=False, sort_keys=True))
        return finish_journal()


def change_named_connection(root: Path, authority_id: str, *, name: str, action: str, role: str | None,
                            capabilities: tuple[str, ...],
                            source_link_id: str | None, expected_sha256: str | None,
                            apply: bool, check_authority: Callable[[ManagedMarkdown, str, str | None], None]) -> dict[str, object]:
    """Preview or CAS one Owner-approved local connection configuration."""

    if (not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", name) or action not in {"add", "revoke"}
            or role not in {None, "contributor", "operator"}):
        raise ContractValidationError("connection name or action is invalid")
    if source_link_id is not None and (not isinstance(source_link_id, str)
                                       or not re.fullmatch(r"link:[a-z0-9-]{1,120}", source_link_id)):
        raise ContractValidationError("connection source link is invalid")
    resolved = _validated_root(root)

    def current_change() -> tuple[dict[str, object], str]:
        authority = bootstrap_authority(resolved, authority_id)
        if authority.metadata.get("rights_era") != "owledge.bound-source-rights/1":
            raise ContractValidationError("legacy workspace needs explicit source-rights migration/re-preview before Agent connection")
        connections = authority.metadata.get("connections")
        grants = authority.metadata.get("actor_grants")
        if not isinstance(connections, dict) or not isinstance(grants, dict):
            raise ContractValidationError("connection authority configuration is invalid")
        if len(connections) >= 32 and name not in connections:
            raise ContractValidationError("named connection limit reached")
        existing = connections.get(name)
        principal = local_connection_principal(authority_id, name)
        check_authority(authority, principal, source_link_id if action == "add" else None)
        if action == "revoke" and (not isinstance(existing, dict) or existing.get("status") != "active"):
            raise ContractValidationError("active named connection was not found")
        if action == "revoke" and existing.get("principal_id") != principal:
            raise ContractValidationError("named connection principal does not match its authority")
        effective_role = role if action == "add" else existing.get("role")
        if action == "revoke" and role is not None and effective_role != role:
            raise ContractValidationError("named connection role changed")
        if effective_role not in {"contributor", "operator"}:
            raise ContractValidationError("named connection role is invalid")
        if action == "add" and isinstance(existing, dict) and existing.get("status") == "active":
            raise ContractValidationError("named connection is already active")
        updated_connections = dict(connections)
        updated_grants = dict(grants)
        generations = authority.metadata.get("connection_generations", {})
        if (not isinstance(generations, dict) or any(
            not isinstance(key, str) or not isinstance(value, str)
            or not re.fullmatch(r"[0-9a-f]{64}", value)
            for key, value in generations.items())):
            raise ContractValidationError("connection generation registry is invalid")
        updated_generations = dict(generations)
        for prior_name in connections:
            updated_generations.setdefault(prior_name, authority.content_sha256)
        updated_generations[name] = sha256((authority.content_sha256 + "\0" + action + "\0" + name).encode()).hexdigest()
        if action == "add":
            updated_connections[name] = {"principal_id": principal, "role": effective_role,
                                         "authority_id": authority_id, "source_link_id": source_link_id,
                                         "status": "active"}
            updated_grants[principal] = list(capabilities)
        else:
            updated_connections[name] = {**existing, "status": "revoked"}
            updated_grants.pop(principal, None)
        metadata = dict(authority.metadata)
        version = metadata.get("document_version")
        if type(version) is not int or version < 1:
            raise ContractValidationError("authority version is invalid")
        suffix = sha256((authority.content_sha256 + action + name + effective_role + str(source_link_id)).encode("utf-8")).hexdigest()[:24]
        metadata.update({"connections": updated_connections, "actor_grants": updated_grants,
                         "connection_generations": updated_generations,
                         "document_version": version + 1,
                         "revision": "connection-rev-" + suffix,
                         "policy_revision": "policy-connection-" + suffix,
                         "last_connection_change": {"approved_by": "principal:local-owner", "action": action,
                                                    "name": name, "principal_id": principal,
                                                    "prior_sha256": authority.content_sha256}})
        document = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False, separators=(',', ':'))}"
                                         for key, value in metadata.items()) + "\n---\n" + authority.body
        if len(document.encode("utf-8")) > 1_048_576:
            raise ContractValidationError("named connection exceeds authority document budget")
        result = {"status": "ready" if apply else "preview", "name": name, "action": action, "role": effective_role,
                  "principal_id": principal, "authority_id": authority_id,
                  "source_link_id": source_link_id if action == "add" else existing.get("source_link_id"),
                  "expected_sha256": authority.content_sha256, "revision": metadata["revision"]}
        return result, document

    if not apply:
        return current_change()[0]
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ContractValidationError("connection apply needs the exact preview hash")
    with authority_write_locks((resolved,)):
        result, document = current_change()
        if result["expected_sha256"] != expected_sha256:
            raise ContractValidationError("connection authority changed after preview")
        _write_exact_atomic(resolved, resolved / ".owledge" / "authority.md", document)
        return result


def change_named_source_reader(workspace: Path, *, source_link_id: str, connection: str,
                               action: str, expected_sha256: str | None, apply: bool,
                               check_owner: Callable[[ManagedMarkdown], None],
                               check_agent: Callable[[ManagedMarkdown, str, str], bool],
                               rights_allowed: Callable[[object, str], bool]) -> dict[str, object]:
    """Change only one registered restricted raw link after an exact Owner preview."""
    if action not in {"grant", "revoke"}:
        raise ContractValidationError("source-rights action is invalid")
    principal = local_connection_principal("user-global:source-access", connection)
    root = _validated_root(workspace)
    global_root = _validated_root(root / "global")

    def current():
        if (_effect_exists(root, root / ".owledge/source-registration.json")
                or _effect_exists(root, root / "global/.owledge/source-registration.json")):
            raise ContractValidationError("source registration requires recovery before rights changes")
        authority = bootstrap_authority(global_root, "user-global:source-access")
        check_owner(authority)
        profiles = authority.metadata.get("connections")
        if (authority.metadata.get("rights_era") != "owledge.bound-source-rights/1"
                or authority.metadata.get("mode") != "read_write"
                or not isinstance(profiles, dict)):
            raise ContractValidationError("local Owner source-rights authority is unavailable")
        profile = profiles.get(connection)
        if (not isinstance(profile, dict) or profile.get("status") not in ({"active"} if action == "grant" else {"active", "revoked"})
                or profile.get("role") not in {"contributor", "operator"}
                or profile.get("authority_id") != "user-global:source-access"
                or profile.get("principal_id") != principal
                or action == "grant" and profile.get("source_link_id") not in (None, source_link_id)
                or action == "grant" and not check_agent(authority, principal, profile["role"])):
            raise ContractValidationError("known same-Global named connection is required")
        state_bytes = _read_exact_effect(root, root / "workspace.json")
        state = json.loads(state_bytes)
        if not isinstance(state, dict) or state.get("schema") not in {
                "owledge.private-knowledge-workspace/1", "owledge.private-knowledge-workspace/2",
                "owledge.private-knowledge-workspace/3"}:
            raise ContractValidationError("knowledge source registry is invalid")
        registered = {"link:source-access-originals": ("global/.owledge/raw-link.md", state.get("source_id"))}
        for item in state.get("imports", []):
            if (not isinstance(item, dict) or not isinstance(item.get("source_id"), str)
                    or not re.fullmatch(r"source:[a-z0-9-]+", item["source_id"])
                    or item.get("source_link_id") != "link:import-" + item["source_id"].removeprefix("source:")):
                raise ContractValidationError("knowledge source registry is invalid")
            registered[item.get("source_link_id")] = (
                "global/.owledge/import-" + item["source_id"].removeprefix("source:") + ".md",
                item["source_id"])
        if source_link_id not in registered or registered[source_link_id][1] is None:
            raise ContractValidationError("registered raw Source Link was not found")
        relative, source_id = registered[source_link_id]
        if not re.fullmatch(r"source:[a-z0-9-]+", source_id):
            raise ContractValidationError("registered source identity is invalid")
        target = root / relative
        original = _read_exact_effect(root, target)
        metadata, body = parse_markdown_frontmatter(original.decode("utf-8"))
        if (metadata.get("schema") != "owledge.knowledge-source-link/1"
                or metadata.get("authority_id") != "user-global:source-access"
                or metadata.get("source_link_id") != source_link_id
                or metadata.get("artifact_id") != source_link_id
                or metadata.get("linked_authority_id") != source_id
                or metadata.get("lifecycle") != "accepted"
                or metadata.get("grants") != ["discover", "keyword_retrieve"]
                or metadata.get("processing_layer") != "condensed"
                or metadata.get("source_trust") != "internal"):
            raise ContractValidationError("registered raw Source Link changed")
        rights = metadata.get("source_access")
        if (not isinstance(rights, dict) or rights.get("access") != "restricted"
                or not rights_allowed(rights, "principal:local-owner")):
            raise ContractValidationError("restricted Source Link with retained Owner access is required")
        readers = rights["principals"]
        if action == "grant" and principal in readers or action == "revoke" and principal not in readers:
            raise ContractValidationError("requested reader right is already in that state")
        version = metadata.get("document_version")
        if type(version) is not int or version < 1:
            raise ContractValidationError("Source Link version is invalid")
        before_hash = sha256(original).hexdigest()
        authority_hash = authority.content_sha256
        state_hash = sha256(state_bytes).hexdigest()
        approval = sha256(json.dumps([authority_hash, state_hash, before_hash, source_link_id,
                                      connection, action], separators=(",", ":")).encode("utf-8")).hexdigest()
        changed = [*readers, principal] if action == "grant" else [reader for reader in readers if reader != principal]
        suffix = approval[:24]
        updated = {**metadata, "source_access": {"access": "restricted", "principals": changed},
                   "document_version": version + 1, "revision": "source-reader-" + suffix,
                   "last_source_rights_change": {"approved_by": "principal:local-owner", "action": action,
                                                 "connection": connection, "principal_id": principal,
                                                 "prior_sha256": before_hash}}
        document = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False, separators=(',', ':'))}"
                                          for key, value in updated.items()) + "\n---\n" + body
        result = {"status": "ready" if apply else "preview", "action": action,
                  "source_link_id": source_link_id, "connection": connection, "principal_id": principal,
                  "access": "restricted", "allowed_after": action == "grant",
                  "expected_sha256": approval, "prior_link_sha256": before_hash,
                  "revision": updated["revision"]}
        return result, target, document

    if not apply:
        return current()[0]
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ContractValidationError("source-rights apply needs the exact preview hash")
    with authority_write_locks((root, global_root)):
        result, target, document = current()
        if result["expected_sha256"] != expected_sha256:
            raise ContractValidationError("source-rights authority or link changed after preview")
        _write_exact_atomic(root, target, document)
        return result


def list_named_source_rights(workspace: Path, *, controls: tuple[ManagedMarkdown, ...],
                             check_owner: Callable[[ManagedMarkdown], None]) -> dict[str, object]:
    """Owner view of registered raw links and current named readers, without source bodies."""
    root = _validated_root(workspace)
    authority = bootstrap_authority(root / "global", "user-global:source-access")
    check_owner(authority)
    profiles = authority.metadata.get("connections")
    if (authority.metadata.get("rights_era") != "owledge.bound-source-rights/1"
            or not isinstance(profiles, dict)):
        raise ContractValidationError("local Owner source-rights authority is unavailable")
    state = json.loads(_read_exact_effect(root, root / "workspace.json"))
    if not isinstance(state, dict) or state.get("schema") not in {
            "owledge.private-knowledge-workspace/1", "owledge.private-knowledge-workspace/2",
            "owledge.private-knowledge-workspace/3"}:
        raise ContractValidationError("knowledge source registry is invalid")
    registered = ({"link:source-access-originals": state["source_root"]}
                  if state.get("source_id") else {})
    for item in state.get("imports", []):
        if (not isinstance(item, dict) or not isinstance(item.get("source_id"), str)
                or not re.fullmatch(r"source:[a-z0-9-]+", item["source_id"])
                or item.get("source_link_id") != "link:import-" + item["source_id"].removeprefix("source:")
                or not isinstance(item.get("source_root"), str)):
            raise ContractValidationError("knowledge source registry is invalid")
        registered[item["source_link_id"]] = item["source_root"]
    rows = []
    for link in controls:
        link_id = link.metadata.get("source_link_id")
        if link_id not in registered or link.metadata.get("schema") != "owledge.knowledge-source-link/1":
            continue
        rights = link.metadata.get("source_access")
        if not isinstance(rights, dict):
            raise ContractValidationError("Source Link rights are invalid")
        readers = sorted(name for name, profile in profiles.items()
                         if isinstance(profile, dict) and profile.get("status") in {"active", "revoked"}
                         and profile.get("principal_id") == local_connection_principal("user-global:source-access", name)
                         and profile["principal_id"] in rights.get("principals", []))
        reader_status = {name: profiles[name]["status"] for name in readers}
        source_path = registered[link_id]
        rows.append({"source_link_id": link_id, "source_name": Path(source_path).name,
                     "source_path": source_path, "access": rights.get("access"),
                     "revision": link.revision, "readers": readers, "reader_status": reader_status})
    return {"status": "ready", "authority_id": "user-global:source-access",
            "links": sorted(rows, key=lambda row: row["source_link_id"])}


def project_concept_binding(project_workspace: Path, global_workspace: Path,
                            snapshot: SourceSnapshot | None = None, *,
                            check_owner: Callable[[ManagedMarkdown, ManagedMarkdown, ManagedMarkdown], None],
                            scan_current: Callable[[Path], SourceSnapshot],
                            expected_sha256: str | None = None, apply: bool = False) -> dict[str, object]:
    """Designate one registered single-file concept with one Global authority CAS."""
    project, target = _reuse_roots(project_workspace, global_workspace)

    def current() -> tuple[dict[str, object], str]:
        project_state = json.loads(_reuse_read(project, "workspace.json") or "null")
        if not isinstance(project_state, dict) or project_state.get("schema") != _LINKED_PROJECT_SCHEMA:
            raise ContractValidationError("Project needs an explicit Global contribution link")
        if validate_project_reuse_binding(project, project_state) != target:
            raise ContractValidationError("Project contribution link changed")
        project_id = project_state["authority_id"]
        project_authority = bootstrap_authority(project / "project", project_id)
        global_authority = bootstrap_authority(target / "global", _REUSE_GLOBAL)
        if snapshot is None or len(snapshot.files) != 1:
            raise ContractValidationError("concept must be one exact Markdown file")
        if scan_current(snapshot.source_root) != snapshot:
            raise ContractValidationError("concept changed since exact source scan")
        state = json.loads(_reuse_read(target, "workspace.json") or "null")
        entries = state.get("imports", []) if isinstance(state, dict) else []
        if isinstance(state, dict) and "source_id" in state:
            entries = [{"source_id": state["source_id"], "source_root": state["source_root"],
                        "snapshot_sha256": state["source_snapshot_sha256"],
                        "source_link_id": "link:source-access-originals", "primary": True}, *entries]
        if not isinstance(entries, list):
            raise ContractValidationError("Global source registry is invalid")
        matches = [entry for entry in entries if isinstance(entry, dict)
                   and entry.get("source_id") == snapshot.source_id
                   and entry.get("snapshot_sha256") == snapshot.snapshot_sha256
                   and isinstance(entry.get("source_root"), str)
                   and os.path.normcase(str(Path(entry["source_root"]).absolute()))
                   == os.path.normcase(str(snapshot.source_root.absolute()))]
        if len(matches) != 1:
            raise ContractValidationError("register the current exact concept source first")
        entry = matches[0]
        if entry.get("primary"):
            validate_primary_snapshot(target, state)
            link_path = "global/.owledge/raw-link.md"
        else:
            validate_imported_snapshot(target, entry)
            link_path = "global/.owledge/import-" + snapshot.source_id.removeprefix("source:") + ".md"
        link_raw = _reuse_read(target, link_path)
        if link_raw is None:
            raise ContractValidationError("registered concept Source Link is missing")
        link = parse_managed_markdown(link_path.removeprefix("global/"), link_raw)
        if (link.authority_id != _REUSE_GLOBAL or link.artifact_id != entry["source_link_id"]
                or link.metadata.get("linked_authority_id") != snapshot.source_id
                or link.metadata.get("lifecycle") != "accepted"):
            raise ContractValidationError("registered concept Source Link changed")
        check_owner(project_authority, global_authority, link)
        prior = global_authority.metadata.get("project_concepts", {})
        if not isinstance(prior, dict) or len(prior) > 64:
            raise ContractValidationError("Project concept registry is invalid")
        old = prior.get(project_id)
        if old is not None and (not isinstance(old, dict) or old.get("source_id") != snapshot.source_id):
            raise ContractValidationError("Project concept source identity cannot change silently")
        version = old.get("document_version", 0) + 1 if old else 1
        if type(version) is not int or version > 1024:
            raise ContractValidationError("Project concept revision limit reached")
        binding = {"project_authority_id": project_id, "project_workspace": str(project),
                   "project_link_id": project_state["global_contribution"]["source_link_id"],
                   "concept_id": "concept:" + project_id.removeprefix("project:"),
                   "document_version": version,
                   "revision": f"concept-rev-{version}-{snapshot.snapshot_sha256[:16]}",
                   "source_id": snapshot.source_id, "source_link_id": entry["source_link_id"],
                   "snapshot_sha256": snapshot.snapshot_sha256,
                   "relative_path": snapshot.files[0].relative_path,
                   "content_sha256": snapshot.files[0].content_sha256}
        before = _reuse_read(target, "global/.owledge/authority.md")
        if before is None:
            raise ContractValidationError("Global authority is missing")
        before_sha = sha256(before.encode("utf-8")).hexdigest()
        if old is not None and all(old.get(key) == binding[key] for key in
                                   ("source_id", "source_link_id", "snapshot_sha256", "relative_path", "content_sha256")):
            return {"status": "ready", "already_current": True, "expected_sha256": before_sha,
                    "binding": old}, before
        metadata = dict(global_authority.metadata)
        if type(metadata.get("document_version")) is not int:
            raise ContractValidationError("Global authority version is invalid")
        metadata["project_concepts"] = {**prior, project_id: binding}
        metadata["document_version"] += 1
        suffix = sha256((before_sha + binding["revision"]).encode()).hexdigest()[:24]
        metadata["revision"] = "project-concept-" + suffix
        metadata["policy_revision"] = "policy-project-concept-" + suffix
        metadata["last_concept_change"] = {"approved_by": "principal:local-owner",
                                           "project_authority_id": project_id,
                                           "prior_sha256": before_sha,
                                           "old_revision": old.get("revision") if old else None,
                                           "new_revision": binding["revision"]}
        after = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False, separators=(',', ':'))}"
                                        for key, value in metadata.items()) + "\n---\n" + global_authority.body
        return {"status": "preview", "already_current": False, "expected_sha256": before_sha,
                "old": old, "binding": binding}, after

    if not apply:
        return current()[0]
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ContractValidationError("concept bind needs exact authority preview hash")
    with authority_write_locks((project, project / "project", target, target / "global")):
        result, document = current()
        if result["expected_sha256"] != expected_sha256:
            raise ContractValidationError("concept binding changed after preview")
        if not result["already_current"]:
            _write_exact_atomic(target / "global", target / "global/.owledge/authority.md", document)
        return {**result, "status": "ready"}


def resolve_project_concept(global_workspace: Path, project_id: str):
    """Resolve only an Owner-designated Project and its registered source."""
    target = _validated_root(global_workspace)
    global_authority = bootstrap_authority(target / "global", _REUSE_GLOBAL)
    mapping = global_authority.metadata.get("project_concepts")
    if not isinstance(mapping, dict) or not isinstance(project_id, str):
        raise ContractValidationError("Project concept designation is missing")
    binding = mapping.get(project_id)
    fields = {"project_authority_id", "project_workspace", "project_link_id", "concept_id",
              "document_version", "revision", "source_id", "source_link_id",
              "snapshot_sha256", "relative_path", "content_sha256"}
    if (not isinstance(binding, dict) or set(binding) != fields
            or binding.get("project_authority_id") != project_id
            or type(binding.get("document_version")) is not int or binding["document_version"] < 1
            or binding.get("concept_id") != "concept:" + project_id.removeprefix("project:")
            or binding.get("revision") != f"concept-rev-{binding['document_version']}-{str(binding.get('snapshot_sha256'))[:16]}"
            or not isinstance(binding.get("snapshot_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", binding["snapshot_sha256"])
            or not isinstance(binding.get("content_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", binding["content_sha256"])
            or not isinstance(binding.get("relative_path"), str)
            or not re.fullmatch(r"[^/\\:.]+\.md", binding["relative_path"])):
        raise ContractValidationError("Project concept designation is invalid")
    project, checked_target = _reuse_roots(binding["project_workspace"], target)
    if checked_target != target:
        raise ContractValidationError("Project concept target changed")
    state = json.loads(_reuse_read(project, "workspace.json") or "null")
    if (not isinstance(state, dict) or state.get("schema") != _LINKED_PROJECT_SCHEMA
            or state.get("authority_id") != project_id
            or validate_project_reuse_binding(project, state) != target
            or state["global_contribution"]["source_link_id"] != binding["project_link_id"]):
        raise ContractValidationError("Project concept reciprocal link changed")
    project_authority = bootstrap_authority(project / "project", project_id)
    source_state = json.loads(_reuse_read(target, "workspace.json") or "null")
    entries = source_state.get("imports", []) if isinstance(source_state, dict) else []
    if isinstance(source_state, dict) and "source_id" in source_state:
        entries = [{"source_id": source_state["source_id"], "source_root": source_state["source_root"],
                    "snapshot_sha256": source_state["source_snapshot_sha256"],
                    "source_link_id": "link:source-access-originals", "primary": True}, *entries]
    if not isinstance(entries, list):
        raise ContractValidationError("Global source registry is invalid")
    matches = [item for item in entries if isinstance(item, dict)
               and item.get("source_id") == binding["source_id"]
               and item.get("source_link_id") == binding["source_link_id"]
               and item.get("snapshot_sha256") == binding["snapshot_sha256"]]
    if len(matches) != 1:
        raise ContractValidationError("Project concept source was revised; bind its new snapshot")
    entry = matches[0]
    if entry.get("primary"):
        validate_primary_snapshot(target, source_state)
        relative_link = "global/.owledge/raw-link.md"
    else:
        validate_imported_snapshot(target, entry)
        relative_link = "global/.owledge/import-" + binding["source_id"].removeprefix("source:") + ".md"
    link_raw = _reuse_read(target, relative_link)
    if link_raw is None:
        raise ContractValidationError("Project concept Source Link is missing")
    link = parse_managed_markdown(relative_link.removeprefix("global/"), link_raw)
    if (link.artifact_id != binding["source_link_id"] or link.authority_id != _REUSE_GLOBAL
            or link.metadata.get("linked_authority_id") != binding["source_id"]
            or link.metadata.get("lifecycle") != "accepted"
            or not isinstance(link.metadata.get("grants"), list)
            or not {"discover", "keyword_retrieve"}.issubset(link.metadata["grants"])):
        raise ContractValidationError("Project concept Source Link is invalid")
    return binding, project_authority, global_authority, link, Path(entry["source_root"])


def load_authority_documents(
    root: Path,
    expected_authority_id: str,
) -> tuple[ManagedMarkdown, ...]:
    """Load one already-authorized authority with exact source bytes."""

    resolved_root = _validated_root(root)
    documents: list[ManagedMarkdown] = []
    identities: set[str] = set()
    for path in sorted(resolved_root.rglob("*.md"), key=lambda item: item.as_posix()):
        relative_parts = path.relative_to(resolved_root).parts
        if len(relative_parts) >= 2 and relative_parts[:2] in {
            (".owledge", "bundles"),
            (".owledge", "candidates"),
            (".owledge", "changesets"),
            (".owledge", "gaps"),
            (".owledge", "receipts"),
            (".owledge", "traces"),
            (".owledge", "transactions"),
        }:
            continue
        parsed = _read_managed_document(resolved_root, path)
        if parsed.authority_id != expected_authority_id:
            raise ContractValidationError("document authority does not match its root")
        if parsed.artifact_id in identities:
            raise ContractValidationError("artifact identity is duplicated")
        identities.add(parsed.artifact_id)
        documents.append(parsed)
    authority_documents = [
        item
        for item in documents
        if item.metadata.get("schema") == "owledge.authority-unit/1"
    ]
    if len(authority_documents) != 1:
        raise ContractValidationError("authority document is missing or duplicated")
    return tuple(documents)


def load_maintenance_snapshot(
    root: Path,
    expected_authority_id: str,
    *,
    max_documents: int,
    max_bytes: int,
    max_candidates: int,
    cursor: Mapping[str, object] | None,
    stage: str | None = None,
) -> dict[str, object]:
    """Read only the bounded global maintenance lanes and report actual work."""

    resolved_root = _validated_root(root)
    if stage not in (None, "reuse_feed", "inbox"):
        raise ContractValidationError("maintenance selected lane is invalid")
    candidates: list[tuple[Path, bool]] = []
    metadata_entries = 0
    metadata_dirs = 0
    lanes = ((Path(".owledge") / "curated", Path(".owledge") / "inbox",
              Path(".owledge") / "reuse-feed") if stage is None else
             (Path(".owledge") / ("reuse-feed" if stage == "reuse_feed" else "inbox"),))
    for relative in lanes:
        lane = resolved_root / relative
        paths, examined, dirs, overflow = _bounded_markdown_inventory(
            (lane,), recursive=True,
            limit=_METADATA_ENTRY_LIMIT - max(metadata_entries, metadata_dirs))
        metadata_entries += examined
        metadata_dirs += dirs
        if overflow or metadata_entries > _METADATA_ENTRY_LIMIT or metadata_dirs > _METADATA_ENTRY_LIMIT:
            return {"documents": (), "documents_scanned": 0, "bytes_scanned": 0,
                    "metadata_entries_examined": metadata_entries,
                    "metadata_directories_examined": metadata_dirs,
                    "metadata_entry_limit": _METADATA_ENTRY_LIMIT,
                    "exhausted": True, "continuation_cursor": None}
        candidates.extend((path, relative.name in {"inbox", "reuse-feed"}) for path in paths)
    ordered = sorted(candidates, key=lambda item: item[0].as_posix().casefold())
    start_index = 0
    if cursor is not None:
        if set(cursor) != {
            "relative_path",
            "artifact_id",
            "revision",
            "content_sha256",
        } or any(not isinstance(value, str) or not value for value in cursor.values()):
            raise ContractValidationError("maintenance cursor is invalid")
        cursor_path = str(cursor["relative_path"])
        positions = [
            index
            for index, (path, _) in enumerate(ordered)
            if path.relative_to(resolved_root).as_posix() == cursor_path
        ]
        if len(positions) != 1:
            raise ContractValidationError("maintenance cursor is stale")
        cursor_document = _read_managed_document_bounded(resolved_root, ordered[positions[0]][0], max_bytes=65_536)
        if not (cursor_document is not None
            and
            cursor_document.artifact_id == cursor["artifact_id"]
            and cursor_document.revision == cursor["revision"]
            and cursor_document.content_sha256 == cursor["content_sha256"]
        ):
            raise ContractValidationError("maintenance cursor is stale")
        start_index = positions[0] + 1
    documents: list[ManagedMarkdown] = []
    used_bytes = 0
    exhausted = False
    candidate_count = 0
    for path, is_candidate in ordered[start_index:]:
        if is_candidate and candidate_count >= max_candidates:
            exhausted = True
            break
        if path.is_symlink():
            raise ContractValidationError("maintenance document is linked")
        if len(documents) >= max_documents:
            exhausted = True
            break
        document = _read_managed_document_bounded(
            resolved_root,
            path,
            max_bytes=max_bytes - used_bytes,
        )
        if document is None:
            exhausted = True
            break
        if document.authority_id != expected_authority_id:
            raise ContractValidationError("maintenance document authority does not match")
        documents.append(document)
        used_bytes += document.size_bytes
        candidate_count += int(is_candidate)
    continuation_cursor = None
    if exhausted and documents:
        last = documents[-1]
        continuation_cursor = {
            "relative_path": last.relative_path,
            "artifact_id": last.artifact_id,
            "revision": last.revision,
            "content_sha256": last.content_sha256,
        }
    return {
        "documents": tuple(documents),
        "documents_scanned": len(documents),
        "bytes_scanned": used_bytes,
        "metadata_entries_examined": metadata_entries,
        "metadata_directories_examined": metadata_dirs,
        "metadata_entry_limit": _METADATA_ENTRY_LIMIT,
        "exhausted": exhausted,
        "continuation_cursor": continuation_cursor,
    }


def load_progressive_stage(
    root: Path,
    expected_authority_id: str,
    stage: str,
    *,
    max_documents: int,
    max_bytes: int,
) -> dict[str, object]:
    """Read exactly one global retrieval lane after its predecessor misses."""

    lane_names = {
        "curated": "curated",
        "inbox": "inbox",
        "reuse_feed": "reuse-feed",
    }
    if stage not in {*lane_names, "linked_project"}:
        raise ContractValidationError("progressive stage is not local")
    resolved_root = _validated_root(root)
    if (_effect_exists(resolved_root.parent.parent,
                       resolved_root.parent.parent / ".owledge/paired-restore.json")
            and not paired_restore_readback_active(resolved_root.parent.parent)):
        raise ContractValidationError("paired restore requires explicit Owner recovery")
    lane_name = lane_names.get(stage)
    lane = (
        resolved_root / ".owledge" / str(lane_name)
        if lane_name is not None
        else resolved_root / "knowledge"
    )
    if not lane.exists():
        return {"documents": (), "documents_scanned": 0, "bytes_scanned": 0,
                "metadata_entries_examined": 0, "metadata_directories_examined": 0,
                "metadata_entry_limit": _METADATA_ENTRY_LIMIT, "exhausted": False}
    if not lane.is_dir() or lane.is_symlink():
        raise ContractValidationError("progressive stage lane is invalid")
    documents: list[ManagedMarkdown] = []
    identities: set[str] = set()
    paths, metadata_entries, metadata_dirs, overflow = _bounded_markdown_inventory(
        (lane,), recursive=True)
    if overflow:
        return {"documents": (), "documents_scanned": 0, "bytes_scanned": 0,
                "metadata_entries_examined": metadata_entries,
                "metadata_directories_examined": metadata_dirs,
                "metadata_entry_limit": _METADATA_ENTRY_LIMIT,
                "exhausted": True}
    used_bytes = 0
    exhausted = False
    for path in paths:
        if len(documents) >= max_documents:
            exhausted = True
            break
        document = _read_managed_document_bounded(
            resolved_root,
            path,
            max_bytes=max_bytes - used_bytes,
        )
        if document is None:
            exhausted = True
            break
        if document.authority_id != expected_authority_id:
            raise ContractValidationError("progressive stage authority does not match")
        if document.artifact_id in identities:
            raise ContractValidationError("progressive stage identity is duplicated")
        identities.add(document.artifact_id)
        documents.append(document)
        used_bytes += document.size_bytes
    return {
        "documents": tuple(documents),
        "documents_scanned": len(documents),
        "bytes_scanned": used_bytes,
        "metadata_entries_examined": metadata_entries,
        "metadata_directories_examined": metadata_dirs,
        "metadata_entry_limit": _METADATA_ENTRY_LIMIT,
        "exhausted": exhausted,
    }


def load_raw_keyword_snapshot(
    root: Path,
    expected_authority_id: str,
    *,
    query: str,
    max_documents: int,
    max_bytes: int,
    max_matches: int = 8,
    source_areas: tuple[str, ...] = (".",),
    cursor: Mapping[str, object] | None = None,
    discover_areas: bool = False,
    area_parent: str = ".",
    selection_binding: str = "",
) -> dict[str, object]:
    """Search one immutable RW-MVP-03 source snapshot without trusting its bytes."""

    resolved_root = _validated_root(root)
    source_directory = resolved_root / ".owledge" / "sources"
    if not source_directory.is_dir() or source_directory.is_symlink():
        raise ContractValidationError("source manifest directory is invalid")
    manifests: list[Path] = []
    source_entries = 0
    with os.scandir(source_directory) as iterator:
        for entry in iterator:
            source_entries += 1
            if source_entries > 256:
                raise ContractValidationError("source manifest directory exceeds its 256-entry limit")
            if entry.is_symlink() or _is_reparse_path(Path(entry.path)):
                raise ContractValidationError("source manifest directory is linked")
            if entry.is_dir(follow_symlinks=False):
                manifests.append(Path(entry.path) / "manifest.md")
    manifests.sort(key=lambda item: item.as_posix().casefold())
    if len(manifests) != 1:
        raise ContractValidationError("source snapshot manifest is missing or ambiguous")
    manifest = _read_managed_document_bounded(resolved_root, manifests[0], max_bytes=16_777_216)
    if manifest is None:
        raise ContractValidationError("source manifest exceeds its 16 MiB limit")
    metadata = manifest.metadata
    records = metadata.get("records")
    snapshot_sha256 = metadata.get("snapshot_sha256")
    if not (
        metadata.get("schema") == "owledge.source-snapshot/1"
        and manifest.authority_id == expected_authority_id
        and metadata.get("lifecycle") == "observed"
        and metadata.get("processing_layer") == "raw"
        and metadata.get("source_trust") == "external"
        and metadata.get("canonical") is False
        and isinstance(snapshot_sha256, str)
        and re.fullmatch(r"[0-9a-f]{64}", snapshot_sha256)
        and isinstance(records, list)
        and len(records) <= 16_384
    ):
        raise ContractValidationError("source snapshot manifest contract is invalid")
    query_tokens = {token for token, _ in unicode_keyword_spans(query)}
    if Path(area_parent).is_absolute() or ".." in Path(area_parent).parts:
        raise ContractValidationError("source area parent is invalid")
    parent_parts = () if area_parent == "." else Path(area_parent).parts
    available_area_set: set[str] = set()
    selectable_areas: set[str] = {"."}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("relative_path"), str):
            raise ContractValidationError("source snapshot record is invalid")
        parts = Path(str(record["relative_path"])).parts
        if len(parts) > 32 or len(str(record["relative_path"])) > 1024:
            raise ContractValidationError("source snapshot record path exceeds its bound")
        if len(parts) == 1:
            selectable_areas.add("@root")
        else:
            selectable_areas.add(Path(*parts[:-1]).as_posix() + "/@root")
        for depth in range(1, len(parts)):
            selectable_areas.add(Path(*parts[:depth]).as_posix())
        if parts[:len(parent_parts)] != parent_parts:
            continue
        remainder = parts[len(parent_parts):]
        if len(remainder) == 1:
            available_area_set.add("@root" if not parent_parts else Path(*parent_parts).as_posix() + "/@root")
        elif remainder:
            available_area_set.add(Path(*(parent_parts + (remainder[0],))).as_posix())
    all_available_areas = sorted(available_area_set, key=str.casefold)
    normalized_areas = tuple(sorted(set(source_areas), key=str.casefold))
    if not normalized_areas or any(
        area not in {".", "@root"} and (Path(area).is_absolute() or ".." in Path(area).parts)
        for area in normalized_areas
    ) or any(area not in selectable_areas for area in normalized_areas):
        raise ContractValidationError("source area selection is invalid")
    query_sha256 = sha256(query.strip().casefold().encode("utf-8")).hexdigest()
    scope_sha256 = sha256("\n".join(normalized_areas).encode("utf-8")).hexdigest()
    cursor_binding = {
        "schema": "owledge.raw-search-cursor/1",
        "authority_id": expected_authority_id,
        "query_sha256": query_sha256,
        "scope_sha256": scope_sha256,
        "snapshot_sha256": snapshot_sha256,
        "manifest_sha256": manifest.content_sha256,
        "source_artifact_id": manifest.artifact_id,
        "mode": "discover" if discover_areas else "search",
        "area_parent": area_parent,
        "selection_binding": selection_binding,
    }
    offset = 0
    if cursor is not None:
        if not isinstance(cursor, Mapping) or any(cursor.get(key) != value for key, value in cursor_binding.items()):
            raise ContractValidationError("raw search cursor binding is invalid or stale")
        offset = cursor.get("offset", -1)
        if not isinstance(offset, int) or offset < 0 or offset > len(records):
            raise ContractValidationError("raw search cursor offset is invalid")
    if discover_areas:
        available_areas = all_available_areas[offset:offset + 128]
        next_area_offset = offset + len(available_areas)
        return {
            "documents": (), "manifest": {"artifact_id": manifest.artifact_id, "revision": manifest.revision,
            "sha256": manifest.content_sha256, "snapshot_sha256": snapshot_sha256, "records": []},
            "areas": tuple(available_areas), "documents_scanned": 0, "bytes_scanned": 0,
            "exhausted": next_area_offset < len(all_available_areas),
            "continuation": ({**cursor_binding, "offset": next_area_offset}
                             if next_area_offset < len(all_available_areas) else None),
            "areas_total": len(all_available_areas),
        }
    matches: list[ManagedMarkdown] = []
    inventory: list[dict[str, object]] = []
    bytes_scanned = 0
    exhausted = False
    oversized_files_skipped = 0
    unreadable_files: list[dict[str, str]] = []
    oversized_record: dict[str, object] | None = None
    next_offset = offset
    for record_index, record in enumerate(records[offset:], start=offset):
        if not isinstance(record, dict):
            raise ContractValidationError("source snapshot record is invalid")
        artifact_id = record.get("artifact_id")
        relative_path = record.get("relative_path")
        sidecar_path = record.get("sidecar_path")
        content_sha256 = record.get("content_sha256")
        size_bytes = record.get("size_bytes")
        if not (
            isinstance(artifact_id, str)
            and isinstance(relative_path, str)
            and isinstance(sidecar_path, str)
            and isinstance(content_sha256, str)
            and isinstance(size_bytes, int)
        ):
            raise ContractValidationError("source snapshot record fields are invalid")
        record_path = Path(relative_path)
        next_offset = record_index + 1
        if "." not in normalized_areas and not any(
            (area == "@root" and len(record_path.parts) == 1)
            or (area.endswith("/@root") and record_path.parent.as_posix() == area[:-6])
            or (area != "@root" and not area.endswith("/@root")
                and (record_path.as_posix() == area or record_path.as_posix().startswith(area + "/")))
            for area in normalized_areas
        ):
            continue
        if len(inventory) >= max_documents or bytes_scanned + size_bytes > max_bytes:
            exhausted = True
            if not inventory and size_bytes > max_bytes:
                next_offset = record_index
                oversized_files_skipped += 1
                oversized_record = {"relative_path": relative_path, "size_bytes": size_bytes}
            else:
                next_offset = record_index
            break
        sidecar = _read_managed_document_bounded(
            resolved_root, resolved_root / Path(sidecar_path), max_bytes=1_048_576)
        if sidecar is None:
            raise ContractValidationError("source sidecar exceeds its 1 MiB limit")
        if not (
            sidecar.artifact_id == artifact_id
            and sidecar.authority_id == expected_authority_id
            and sidecar.metadata.get("schema") == "owledge.source-sidecar/1"
            and sidecar.metadata.get("lifecycle") == "observed"
            and sidecar.metadata.get("processing_layer") == "raw"
            and sidecar.metadata.get("source_trust") == "external"
            and sidecar.metadata.get("canonical") is False
            and sidecar.metadata.get("source_relative_path") == relative_path
            and sidecar.metadata.get("source_content_sha256") == content_sha256
            and sidecar.metadata.get("source_size_bytes") == size_bytes
        ):
            raise ContractValidationError("source sidecar does not match its manifest")
        original = resolved_root / "originals" / snapshot_sha256 / Path(relative_path)
        content = _read_stable_materialized_file(
            resolved_root, original, max_bytes=min(size_bytes, max_bytes - bytes_scanned))
        if len(content) != size_bytes or sha256(content).hexdigest() != content_sha256:
            raise ContractValidationError("source original does not match its sidecar")
        inventory.append(
            {
                "artifact_id": artifact_id,
                "relative_path": relative_path,
                "sha256": content_sha256,
                "size_bytes": size_bytes,
            }
        )
        bytes_scanned += size_bytes
        try:
            body = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            unreadable_files.append({"relative_path": relative_path, "reason": "invalid_utf8"})
            continue
        body_tokens = {token for token, _ in unicode_keyword_spans(body)}
        if not query_tokens.intersection(body_tokens):
            continue
        raw_metadata = dict(sidecar.metadata)
        raw_metadata.update(
            {
                "stage": "raw_keyword",
                "raw_match": True,
                "knowledge_area": "external",
                "knowledge_kind": "source_evidence",
                "memory_kind": "episodic",
                "access": "private",
            }
        )
        matches.append(
            ManagedMarkdown(
                relative_path=relative_path,
                metadata=raw_metadata,
                body=body,
                content_sha256=content_sha256,
                size_bytes=size_bytes,
            )
        )
        if max_matches > 0 and len(matches) >= max_matches and record_index + 1 < len(records):
            exhausted = True
            next_offset = record_index + 1
            break
    return {
        "documents": tuple(matches),
        "manifest": {
            "artifact_id": manifest.artifact_id,
            "revision": manifest.revision,
            "sha256": manifest.content_sha256,
            "snapshot_sha256": snapshot_sha256,
            "records": inventory,
        },
        "documents_scanned": len(inventory),
        "bytes_scanned": bytes_scanned,
        "exhausted": exhausted,
        "areas": tuple(all_available_areas[:128]),
        "continuation": ({**cursor_binding, "offset": next_offset}
                         if exhausted and oversized_record is None else None),
        "oversized_files_skipped": oversized_files_skipped,
        "oversized_record": oversized_record,
        "unreadable_files": unreadable_files,
    }


def load_authority_control_documents(
    root: Path,
    expected_authority_id: str,
) -> tuple[ManagedMarkdown, ...]:
    """Load only top-level Project controls before any knowledge-body scan."""

    resolved_root = _validated_root(root)
    if (_effect_exists(resolved_root.parent.parent,
                       resolved_root.parent.parent / ".owledge/paired-restore.json")
            and not paired_restore_readback_active(resolved_root.parent.parent)):
        raise ContractValidationError("paired restore requires explicit Owner recovery")
    control_root = resolved_root / ".owledge"
    documents: list[ManagedMarkdown] = []
    identities: set[str] = set()
    paths, examined, _, overflow = _bounded_markdown_inventory((control_root,), recursive=False)
    if overflow:
        raise ContractValidationError(
            f"authority control metadata limit {_METADATA_ENTRY_LIMIT} exceeded after {examined} entries")
    total_bytes = 0
    for path in paths:
        try:
            parsed = _read_managed_document_bounded(
                resolved_root, path, max_bytes=min(1_048_576, 16_777_216 - total_bytes))
            if parsed is None:
                raise ContractValidationError("authority control byte limit exceeded")
        except ContractValidationError as error:
            if path.name == "coverage-cases.md":
                raise CoverageCaseInvalidError(
                    "Coverage Case registry is malformed"
                ) from error
            raise
        if parsed.authority_id != expected_authority_id:
            raise ContractValidationError("control authority does not match its root")
        if parsed.artifact_id in identities:
            raise ContractValidationError("control artifact identity is duplicated")
        identities.add(parsed.artifact_id)
        documents.append(parsed)
        total_bytes += parsed.size_bytes
    authority_documents = [
        item
        for item in documents
        if item.metadata.get("schema") == "owledge.authority-unit/1"
    ]
    if len(authority_documents) != 1:
        raise ContractValidationError("authority document is missing or duplicated")
    return tuple(documents)


def load_coverage_documents(
    root: Path,
    controls: tuple[ManagedMarkdown, ...],
) -> tuple[ManagedMarkdown, ...]:
    """Load evidence candidates after control validation, preserving invalid provenance."""

    resolved_root = _validated_root(root)
    documents = list(controls)
    identities = {item.artifact_id for item in controls}
    for path in sorted(resolved_root.rglob("*.md"), key=lambda item: item.as_posix()):
        relative = path.relative_to(resolved_root)
        if relative.parts and relative.parts[0] == ".owledge":
            continue
        parsed = _read_managed_document(resolved_root, path)
        if parsed.artifact_id in identities:
            raise ContractValidationError("artifact identity is duplicated")
        identities.add(parsed.artifact_id)
        documents.append(parsed)
    return tuple(documents)


def load_authority_state(
    roots: Mapping[str, Path],
) -> tuple[tuple[ManagedMarkdown, ...], dict[str, Path]]:
    documents: list[ManagedMarkdown] = []
    identities: set[str] = set()
    authority_roots: dict[str, Path] = {}
    for alias in sorted(roots):
        resolved_root = _validated_root(Path(roots[alias]))
        header = _read_managed_document(
            resolved_root,
            resolved_root / ".owledge" / "authority.md",
        )
        root_documents = list(load_authority_documents(resolved_root, header.authority_id))
        for parsed in root_documents:
            if parsed.artifact_id in identities:
                raise ContractValidationError("artifact identity is duplicated")
            identities.add(parsed.artifact_id)
            documents.append(parsed)
        authority_documents = [
            item
            for item in root_documents
            if item.metadata.get("schema") == "owledge.authority-unit/1"
        ]
        if len(authority_documents) == 1:
            authority_id = authority_documents[0].authority_id
            if authority_id in authority_roots:
                raise ContractValidationError("authority root is duplicated")
            authority_roots[authority_id] = resolved_root
    return tuple(documents), authority_roots


def load_authority_roots(roots: Mapping[str, Path]) -> tuple[ManagedMarkdown, ...]:
    return load_authority_state(roots)[0]


def _gap_identity(authority_id: str, coverage_case_id: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9:-]*", authority_id):
        raise ContractValidationError("gap authority identity is invalid")
    if not re.fullmatch(r"coverage:[a-z0-9][a-z0-9-]*", coverage_case_id):
        raise ContractValidationError("gap coverage identity is invalid")
    authority_suffix = authority_id.split(":", 1)[-1]
    coverage_suffix = coverage_case_id.removeprefix("coverage:")
    scoped_prefix = f"{authority_suffix}-"
    if coverage_suffix.startswith(scoped_prefix):
        coverage_suffix = coverage_suffix[len(scoped_prefix) :]
    return f"gap:{authority_id.replace(':', '-')}:{coverage_suffix}"


def _render_open_gap(
    *,
    gap_id: str,
    authority_id: str,
    coverage_case_id: str,
    coverage_case_revision: str,
    revision: str,
    proof_ids: list[str],
    safe_topic: str,
    required_evidence: list[str],
    observation_count: int,
) -> str:
    rendered_proof_ids = json.dumps(
        proof_ids,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    evidence = json.dumps(required_evidence, ensure_ascii=False, separators=(",", ":"))
    return (
        "---\n"
        "schema: owledge.gap/1\n"
        "document_version: 1\n"
        f"gap_id: {gap_id}\n"
        f"authority_id: {authority_id}\n"
        f"revision: {revision}\n"
        "lifecycle: open\n"
        f"coverage_case_id: {coverage_case_id}\n"
        f"coverage_case_revision: {coverage_case_revision}\n"
        f"proof_ids: {rendered_proof_ids}\n"
        f"safe_topic: {safe_topic}\n"
        f"required_evidence: {evidence}\n"
        f"observation_count: {observation_count}\n"
        "resolved_at: null\n"
        "approved_by_user: null\n"
        "---\n\n"
        f"# {safe_topic}\n\n"
        "Required Evidence is not yet covered.\n"
    )


def _render_gap_receipt(
    *,
    receipt_id: str,
    authority_id: str,
    operation_id: str,
    proof_id: str,
    source_snapshot_id: str,
    outcome: str,
    base_revision: str,
    result_revision: str,
    request_sha256: str | None = None,
) -> str:
    request_binding = (
        "" if request_sha256 is None else f"request_sha256: {request_sha256}\n"
    )
    return (
        "---\n"
        "schema: owledge.receipt/1\n"
        "document_version: 1\n"
        f"receipt_id: {receipt_id}\n"
        f"authority_id: {authority_id}\n"
        "operation: gap_admit\n"
        f"outcome: ok/{outcome}\n"
        f"base_revision: {base_revision}\n"
        f"result_revision: {result_revision}\n"
        f"operation_id: {operation_id}\n"
        f"proof_id: {proof_id}\n"
        f"source_snapshot_id: {source_snapshot_id}\n"
        f"{request_binding}"
        "---\n\n"
        "# Core Effect Receipt\n\n"
        "Deterministic content-minimized effect evidence.\n"
    )


def _is_reparse_path(path: Path) -> bool:
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return path.is_symlink() or bool(
        attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _validated_effect_path(
    root: Path,
    target: Path,
    *,
    must_exist: bool,
) -> Path:
    """Resolve one effect path inside its authority before any content I/O."""

    resolved_root = _validated_root(root)
    candidate = Path(target)
    try:
        relative = candidate.relative_to(resolved_root)
    except ValueError as error:
        raise ContractValidationError("Core effect artifact is outside authority") from error

    current = resolved_root
    for part in relative.parts:
        current = current / part
        if _is_reparse_path(current):
            raise ContractValidationError("Core effect path escapes through a link")

    try:
        resolved_target = candidate.resolve(strict=must_exist)
    except FileNotFoundError as error:
        raise ContractValidationError("Core effect artifact is missing") from error
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError as error:
        raise ContractValidationError("Core effect artifact is outside authority") from error
    return candidate


def _effect_exists(root: Path, target: Path) -> bool:
    return _validated_effect_path(root, target, must_exist=False).exists()


def _read_exact_effect(root: Path, target: Path, *, max_bytes: int | None = None) -> bytes:
    contained = _validated_effect_path(root, target, must_exist=True)
    if not contained.is_file():
        raise ContractValidationError("Core effect artifact is invalid")
    if max_bytes is None:
        return contained.read_bytes()
    if max_bytes < 0 or contained.stat().st_size > max_bytes:
        raise ContractValidationError("Core effect artifact exceeds its bounded read")
    with contained.open("rb") as handle:
        encoded = handle.read(max_bytes + 1)
    if len(encoded) > max_bytes:
        raise ContractValidationError("Core effect artifact exceeds its bounded read")
    return encoded


def _write_exact_atomic(root: Path, target: Path, document: str) -> None:
    target = _validated_effect_path(root, target, must_exist=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    _validated_effect_path(root, target.parent, must_exist=True)
    _validated_effect_path(root, target, must_exist=False)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(document.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        temporary = _validated_effect_path(root, Path(temporary_name), must_exist=True)
        _validated_effect_path(root, target, must_exist=False)
        temporary.replace(target)
    except BaseException:
        temporary = Path(temporary_name)
        try:
            if _effect_exists(root, temporary):
                _unlink_effect(root, temporary)
        except ContractValidationError:
            pass
        raise


def _write_exact_exclusive(root: Path, target: Path, document: str) -> None:
    target = _validated_effect_path(root, target, must_exist=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    _validated_effect_path(root, target.parent, must_exist=True)
    _validated_effect_path(root, target, must_exist=False)
    try:
        with target.open("xb") as handle:
            handle.write(document.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise ContractValidationError("promotion transaction already exists") from error


def _unlink_effect(root: Path, target: Path) -> None:
    _validated_effect_path(root, target, must_exist=True).unlink()


def _read_effect_metadata(
    root: Path,
    target: Path,
    *, max_bytes: int | None = None,
) -> tuple[dict[str, object], bytes]:
    resolved_root = _validated_root(root)
    encoded = _read_exact_effect(resolved_root, target, max_bytes=max_bytes)
    try:
        document = encoded.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContractValidationError("Core effect artifact is not UTF-8") from error
    metadata, _ = parse_markdown_frontmatter(document)
    return metadata, encoded


def replay_gap_admission(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    coverage_case_id: str,
    proof_id: str,
    source_snapshot_id: str,
    expected_gap_revision: str | None = None,
    request_sha256: str | None = None,
) -> tuple[dict[str, object], str, str] | None:
    """Return a prior exactly bound Gap effect before freshness re-evaluation."""

    resolved_root = _validated_root(root)
    receipts = resolved_root / ".owledge" / "receipts"
    if not receipts.is_dir():
        return None
    for target in sorted(receipts.glob("*.md"), key=lambda item: item.name):
        metadata, _ = _read_effect_metadata(resolved_root, target)
        if metadata.get("operation_id") != operation_id:
            continue
        expected = {
            "schema": "owledge.receipt/1",
            "authority_id": authority_id,
            "operation": "gap_admit",
            "proof_id": proof_id,
            "source_snapshot_id": source_snapshot_id,
        }
        if expected_gap_revision is not None:
            expected["base_revision"] = expected_gap_revision
        if request_sha256 is not None:
            expected["request_sha256"] = request_sha256
        if any(metadata.get(key) != value for key, value in expected.items()):
            raise ContractValidationError("operation replay binding does not match")
        outcome = metadata.get("outcome")
        result_revision = metadata.get("result_revision")
        receipt_id = metadata.get("receipt_id")
        if not (
            outcome in {"ok/gap_opened", "ok/gap_recurred", "ok/gap_reopened"}
            and isinstance(result_revision, str)
            and isinstance(receipt_id, str)
        ):
            raise ContractValidationError("operation replay receipt is invalid")
        gap_id = _gap_identity(authority_id, coverage_case_id)
        gap_target = (
            resolved_root / ".owledge" / "gaps" / f"{gap_id.replace(':', '-')}.md"
        )
        gap_metadata, _ = _read_effect_metadata(resolved_root, gap_target)
        proof_ids = gap_metadata.get("proof_ids")
        if not isinstance(proof_ids, list) or proof_id not in proof_ids:
            raise ContractValidationError("operation replay Gap binding is invalid")
        observation_count = 1 if outcome == "ok/gap_opened" else int(
            result_revision.removeprefix("gap-rev-").removesuffix("-open")
        )
        return (
            {
                "gap_id": gap_id,
                "gap_revision": result_revision,
                "lifecycle": "open",
                "observation_count": observation_count,
                "proof_id": proof_id,
                "source_snapshot_id": source_snapshot_id,
            },
            receipt_id,
            outcome.removeprefix("ok/"),
        )
    return None


def read_gap(root: Path, gap_id: str) -> dict[str, object]:
    resolved_root = _validated_root(root)
    target = resolved_root / ".owledge" / "gaps" / f"{gap_id.replace(':', '-')}.md"
    metadata, _ = _read_effect_metadata(resolved_root, target)
    if metadata.get("schema") != "owledge.gap/1" or metadata.get("gap_id") != gap_id:
        raise ContractValidationError("Gap identity does not match")
    return metadata


def replay_gap_closure(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    gap_id: str,
    expected_gap_revision: str,
    approved_by_user: str,
) -> tuple[dict[str, object], str] | None:
    """Return an exactly bound prior Gap-close effect before revalidation."""

    resolved_root = _validated_root(root)
    revision_match = re.fullmatch(r"gap-rev-(\d+)(?:-open)?", expected_gap_revision)
    if revision_match is None:
        return None
    sequence = int(revision_match.group(1))
    result_revision = f"gap-rev-{sequence + 1}-closed"
    receipt_id = f"receipt:{authority_id.replace(':', '-')}:gap-close-{sequence:03d}"
    receipt_target = (
        resolved_root
        / ".owledge"
        / "receipts"
        / f"{receipt_id.replace(':', '-')}.md"
    )
    if not _effect_exists(resolved_root, receipt_target):
        return None
    receipt, _ = _read_effect_metadata(resolved_root, receipt_target)
    expected_receipt = {
        "schema": "owledge.receipt/1",
        "receipt_id": receipt_id,
        "authority_id": authority_id,
        "operation": "gap_verify",
        "outcome": "ok/gap_closed",
        "base_revision": expected_gap_revision,
        "result_revision": result_revision,
        "operation_id": operation_id,
        "approved_by_user": approved_by_user,
    }
    if any(receipt.get(key) != value for key, value in expected_receipt.items()):
        raise ContractValidationError("Gap closure replay binding does not match")
    gap = read_gap(resolved_root, gap_id)
    if not (
        gap.get("authority_id") == authority_id
        and gap.get("revision") == result_revision
        and gap.get("lifecycle") == "closed"
        and gap.get("approved_by_user") == approved_by_user
        and isinstance(gap.get("resolved_at"), str)
    ):
        raise ContractValidationError("Gap closure replay state does not match")
    return (
        {
            "gap_id": gap_id,
            "gap_revision": result_revision,
            "lifecycle": "closed",
            "resolved_at": gap["resolved_at"],
            "approved_by_user": approved_by_user,
        },
        receipt_id,
    )


def recover_pending_effects(root: Path) -> None:
    """Complete one bounded metadata/receipt batch under its authority writer lock."""
    resolved = _validated_root(root)
    pending = resolved / ".owledge" / "pending-effect.json"
    if not _effect_exists(resolved, pending):
        return
    try:
        encoded = _read_exact_effect(resolved, pending)
        if len(encoded) > 2 * 1024 * 1024:
            raise ContractValidationError("pending effect exceeds bounded metadata size")
        journal = json.loads(encoded)
    except (ValueError, UnicodeError) as error:
        raise ContractValidationError("pending effect is not valid JSON") from error
    if not isinstance(journal, dict):
        raise ContractValidationError("pending effect is not an object")
    entries = journal.get("entries")
    config_slug = journal.get("case_slug") if journal.get("schema") == "owledge.case-config-batch/1" else None
    config_paths = ({".owledge/authority.md", ".owledge/coverage-cases.md",
                     ".owledge/artifact-routing.md", f"knowledge/context-{config_slug}.md"}
                    if isinstance(config_slug, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", config_slug) else set())
    ordinary_batch = journal.get("schema") == "owledge.effect-batch/1" and isinstance(entries, list) and 1 <= len(entries) <= 3
    case_batch = (bool(config_paths) and isinstance(entries, list) and len(entries) == 4
                  and {item.get("path") for item in entries if isinstance(item, dict)} == config_paths)
    if not (ordinary_batch or case_batch):
        raise ContractValidationError("pending effect batch is invalid")
    validated = []
    targets = set()
    # Validate the entire batch before touching any target. An external edit
    # produces an explicit conflict, never an automatic overwrite.
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("content"), str):
            raise ContractValidationError("pending effect entry is invalid")
        relative = Path(entry["path"])
        ordinary_path = (relative.suffix == ".md" and len(relative.parts) == 3
                         and relative.parts[0] == ".owledge" and relative.parts[1] in
                         _ORDINARY_EFFECT_DIRS)
        if relative.is_absolute() or ".." in relative.parts or ":" in entry["path"] or not (entry["path"] in config_paths if case_batch else ordinary_path):
            raise ContractValidationError("pending effect target is outside metadata")
        normalized = relative.as_posix().casefold()
        prior_hash = entry.get("before_sha256")
        if normalized in targets or "before_sha256" not in entry or (prior_hash is not None and (not isinstance(prior_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", prior_hash))):
            raise ContractValidationError("pending effect target or prior hash is ambiguous")
        targets.add(normalized)
        target = resolved / relative
        current = _read_exact_effect(resolved, target) if _effect_exists(resolved, target) else None
        try:
            entry["path"].encode("utf-8")
            content = entry["content"].encode("utf-8")
        except UnicodeError as error:
            raise ContractValidationError("pending effect entry is not valid UTF-8") from error
        current_hash = sha256(current).hexdigest() if current is not None else None
        if current != content and current_hash != entry.get("before_sha256"):
            raise ContractValidationError("pending effect target changed")
        validated.append((target, entry["content"], current != content))
    if case_batch:
        inputs = journal.get("inputs")
        if (not isinstance(inputs, dict)
                or set(inputs) != {"name", "question", "title", "area", "value_contract"}
                or inputs.get("name") != config_slug
                or not isinstance(inputs.get("value_contract"), dict)
                or any(not isinstance(inputs.get(key), str) for key in ("name", "question", "title", "area"))
                or not isinstance(journal.get("authority_id"), str)):
            raise ContractValidationError("pending case input is invalid")
        preimages = {}
        for entry in entries:
            before = entry.get("before_content")
            if before is not None and not isinstance(before, str):
                raise ContractValidationError("pending case preimage is invalid")
            if (sha256(before.encode("utf-8")).hexdigest() if before is not None else None) != entry.get("before_sha256"):
                raise ContractValidationError("pending case preimage hash is invalid")
            preimages[entry["path"]] = before
        planned = configure_project_case(resolved, journal["authority_id"],
            **inputs, _preimages=preimages, _return_documents=True)
        if (planned["documents"] != {entry["path"]: entry["content"] for entry in entries}
                or planned["expected_sha256"] != journal.get("expected_sha256")):
            raise ContractValidationError("pending case effect differs from exact Owner plan")
    for target, content, needs_write in validated:
        if needs_write:
            _write_exact_atomic(resolved, target, content)
    _unlink_effect(resolved, pending)


def case_configuration_pending(root: Path) -> bool:
    resolved = _validated_root(root)
    pending = resolved / ".owledge" / "pending-effect.json"
    if not _effect_exists(resolved, pending):
        return False
    encoded = _read_exact_effect(resolved, pending)
    if len(encoded) > 2 * 1024 * 1024:
        raise ContractValidationError("pending effect exceeds bounded size")
    try:
        journal = json.loads(encoded)
    except (UnicodeError, ValueError, AttributeError) as error:
        raise ContractValidationError("pending effect is invalid") from error
    if not isinstance(journal, dict):
        raise ContractValidationError("pending effect is invalid")
    entries = journal.get("entries")
    if journal.get("schema") != "owledge.effect-batch/1":
        return True
    if not isinstance(entries, list) or not 1 <= len(entries) <= 3:
        return True
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            return True
        relative = Path(entry["path"])
        if (relative.is_absolute() or ".." in relative.parts or ":" in entry["path"]
                or relative.suffix != ".md" or len(relative.parts) != 3
                or relative.parts[0] != ".owledge" or relative.parts[1] not in _ORDINARY_EFFECT_DIRS):
            return True
    return False


def _write_effect_batch(root: Path, documents: Mapping[Path, str]) -> None:
    """Durable redo record for a finite metadata effect (at most three files)."""
    pending = root / ".owledge" / "pending-effect.json"
    if _effect_exists(root, pending):
        raise ContractValidationError("recover the pending effect before another write")
    entries = []
    for target, content in documents.items():
        _validated_effect_path(root, target, must_exist=False)
        before = _read_exact_effect(root, target) if _effect_exists(root, target) else None
        entries.append({"path": target.relative_to(root).as_posix(), "content": content,
                        "before_sha256": sha256(before).hexdigest() if before is not None else None})
    encoded = json.dumps({"schema": "owledge.effect-batch/1", "entries": entries}, ensure_ascii=False, sort_keys=True)
    if len(encoded.encode("utf-8")) > 2 * 1024 * 1024:
        raise ContractValidationError("effect batch exceeds bounded metadata size")
    _write_exact_atomic(root, pending, encoded)
    recover_pending_effects(root)


def configure_project_case(root: Path, authority_id: str, *, name: str, question: str,
                           title: str, area: str, value_contract: dict[str, object],
                           expected_sha256: str | None = None, apply: bool = False,
                           _preimages: dict[str, str | None] | None = None,
                           _return_documents: bool = False) -> dict[str, object]:
    """Owner-only closed case configuration, with an exact four-effect redo record."""
    from .contracts import valid_evidence_value_contract
    if not (re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) and len(name) <= 48
            and all(isinstance(item, str) and 1 <= len(item) <= 160 and len(item.encode("utf-8")) <= 512
                    and item.splitlines() == [item]
                    and not any(ord(char) < 32 or ord(char) == 127 for char in item)
                    and "<!--" not in item and "-->" not in item
                    for item in (question, title, area))
            and len(area) <= 80 and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", area)
            and valid_evidence_value_contract(value_contract)
            and value_contract["type"] in {"bounded_text", "integer_string"}):
        raise ContractValidationError("bounded case input is invalid")
    resolved = _validated_root(root)
    if _preimages is None and _effect_exists(resolved, resolved / ".owledge" / "pending-effect.json"):
        raise ContractValidationError("recover pending configuration before another operation")
    def previous(path: Path) -> str | None:
        relative = path.relative_to(resolved).as_posix()
        if _preimages is not None:
            if relative not in _preimages:
                raise ContractValidationError("case recovery preimage is missing")
            return _preimages[relative]
        return _read_exact_effect(resolved, path).decode("utf-8") if _effect_exists(resolved, path) else None
    authority_path = resolved / ".owledge" / "authority.md"
    authority_raw = previous(authority_path)
    if authority_raw is None:
        raise ContractValidationError("Project authority is missing")
    authority, authority_body = parse_markdown_frontmatter(authority_raw)
    if authority.get("authority_id") != authority_id or authority.get("mode") != "read_write":
        raise ContractValidationError("Project authority changed")
    old_settings = authority.get("settings_revision")
    if not isinstance(old_settings, str):
        raise ContractValidationError("Project settings revision missing")
    registry_path = resolved / ".owledge" / "coverage-cases.md"
    routing_path = resolved / ".owledge" / "artifact-routing.md"
    context_path = resolved / "knowledge" / f"context-{name}.md"
    if previous(context_path) is not None:
        raise ContractValidationError("case already exists")

    def existing(path: Path, schema: str, identity: str):
        prior = previous(path)
        if prior is not None:
            metadata, body = parse_markdown_frontmatter(prior)
            if metadata.get("schema") != schema or metadata.get("authority_id") != authority_id:
                raise ContractValidationError("Project configuration is invalid")
            return metadata, body
        return ({"schema": schema, "document_version": 0, "artifact_id": identity,
                 "authority_id": authority_id, "revision": "absent", "lifecycle": "accepted",
                 "processing_layer": "condensed", "source_trust": "internal"}, "")

    registry, _ = existing(registry_path, "owledge.coverage-case-registry/1", "registry:project-coverage")
    routing, _ = existing(routing_path, "owledge.artifact-routing/1", "routing:project")
    cases = registry.get("coverage_cases", {})
    providers = registry.get("provider_contracts", {})
    envelopes = registry.get("search_envelopes", {})
    routes = routing.get("routes", {})
    if not all(isinstance(item, dict) for item in (cases, providers, envelopes, routes)):
        raise ContractValidationError("Project configuration maps are invalid")
    if len(cases) >= 64 or any(len(item) != len(cases) for item in (providers, envelopes, routes)):
        raise ContractValidationError("Project case catalog is inconsistent or full")
    case_id, provider_id, envelope_id, route_id = (f"{prefix}:{name}" for prefix in
                                                   ("coverage", "provider", "search-envelope", "route"))
    if any(key in mapping for key, mapping in ((case_id, cases), (provider_id, providers),
                                               (envelope_id, envelopes), (route_id, routes))):
        raise ContractValidationError("case already exists")
    next_settings = f"settings-project-{sha256((old_settings + name + question + title + area).encode('utf-8')).hexdigest()[:16]}"
    evidence_key = f"project.{name.replace('-', '_')}.answer"
    next_authority = {**authority, "document_version": int(authority["document_version"]) + 1,
                      "revision": f"authority-{next_settings}", "settings_revision": next_settings}
    next_registry = {**registry, "document_version": int(registry["document_version"]) + 1,
                     "revision": f"registry-{next_settings}",
                     "provider_contracts": {**providers, provider_id: {
                         "schema": "owledge.evidence-provider-contract/1", "revision": next_settings,
                         "evidence_key": evidence_key, "provider_authority_id": authority_id,
                         "provider_schema": "owledge.managed-markdown/1", "lifecycle": "accepted",
                         "processing_layer": ["condensed", "delta"], "source_trust": "internal",
                         "knowledge_kind": "project_fact", "memory_kind": "semantic",
                         "value_contract": value_contract}},
                     "search_envelopes": {**envelopes, envelope_id: {
                         "schema": "owledge.search-envelope/1", "revision": next_settings,
                         "authority_id": authority_id, "relative_prefixes": ["knowledge/"],
                         "provider_contract_ids": [provider_id],
                         "retriever_contract_revision": "owledge.markdown-reference-retriever/1",
                         "max_records": 256, "max_bytes": 4194304,
                         "completion": "all_matched_records_healthy_and_scanned"}},
                     "coverage_cases": {**cases, case_id: {
                         "case_revision": next_settings, "required_evidence": [evidence_key],
                         "safe_topic": title, "search_envelope_id": envelope_id,
                         "provider_contract_ids": [provider_id], "gap_admission": "proof_required",
                         "resolution_route_id": route_id, "question": question, "case_name": name,
                         "context_artifact_id": f"context:{name}"}}}
    next_routing = {**routing, "document_version": int(routing["document_version"]) + 1,
                    "revision": f"routing-{next_settings}",
                    "routes": {**routes, route_id: {
                        "route_revision": next_settings, "coverage_case_id": case_id,
                        "target_artifact_id": f"answer:{name}",
                        "target_relative_path": f"knowledge/answer-{name}.md",
                        "target_schema": "owledge.managed-markdown/1", "write_mode": "create_or_exact_replace",
                        "knowledge_kind": "project_fact", "memory_kind": "semantic",
                        "candidate_processing_layer": "delta", "accepted_lifecycle": "accepted",
                        "target_source_trust": "internal", "default_title": title,
                        "record_projection": "full_body_without_frontmatter",
                        "case_name": name,
                        "value_contract": value_contract}}}

    def render(metadata: dict[str, object], body: str) -> str:
        return "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))}"
                                        for key, value in metadata.items()) + "\n---\n" + body

    context = {"schema": "owledge.managed-markdown/1", "document_version": 1,
               "artifact_id": f"context:{name}", "authority_id": authority_id,
               "revision": f"context-{next_settings}", "lifecycle": "accepted",
               "processing_layer": "condensed", "source_trust": "internal",
               "canonical": False, "knowledge_kind": "project_context", "memory_kind": "semantic",
               "knowledge_area": area}
    documents = {authority_path: render(next_authority, authority_body),
                 registry_path: render(next_registry, "\n# Project coverage cases\n"),
                 routing_path: render(next_routing, "\n# Project artifact routing\n"),
                 context_path: render(context, f"\n# {title}\n\nQuestion: {question}\n")}
    digest = sha256(json.dumps({"before": [sha256(prior.encode("utf-8")).hexdigest()
                                                  if (prior := previous(path)) is not None else None for path in documents],
                                "after": [sha256(value.encode("utf-8")).hexdigest() for value in documents.values()]},
                               sort_keys=True).encode("utf-8")).hexdigest()
    preview = {"status": "preview", "case": name, "question": question,
               "coverage_case_id": case_id, "expected_sha256": digest,
               "settings_revision": old_settings}
    if _return_documents:
        if _preimages is None:
            raise ContractValidationError("case plan is internal to recovery")
        return {"documents": {path.relative_to(resolved).as_posix(): content for path, content in documents.items()},
                "expected_sha256": digest}
    if not apply:
        return preview
    if expected_sha256 != digest:
        raise ContractValidationError("case configuration preview is stale")
    entries = []
    for path, content in documents.items():
        prior = previous(path)
        before = prior.encode("utf-8") if prior is not None else None
        entries.append({"path": path.relative_to(resolved).as_posix(), "content": content,
                        "before_sha256": sha256(before).hexdigest() if before is not None else None,
                        "before_content": prior})
    encoded = json.dumps({"schema": "owledge.case-config-batch/1", "authority_id": authority_id,
                          "case_slug": name,
                          "inputs": {"name": name, "question": question, "title": title, "area": area,
                                     "value_contract": value_contract},
                          "expected_sha256": digest, "entries": entries}, ensure_ascii=False, sort_keys=True)
    if len(encoded.encode("utf-8")) > 2 * 1024 * 1024:
        raise ContractValidationError("case configuration is too large")
    _write_exact_atomic(resolved, resolved / ".owledge" / "pending-effect.json", encoded)
    recover_pending_effects(resolved)
    return {**preview, "status": "ready", "settings_revision": next_settings}


def close_gap(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    gap: dict[str, object],
    expected_gap_revision: str,
    resolved_at: str,
    approved_by_user: str,
) -> tuple[dict[str, object], str]:
    """Close one open Gap only after its caller has freshly verified coverage."""

    resolved_root = _validated_root(root)
    gap_id = gap.get("gap_id")
    coverage_case_id = gap.get("coverage_case_id")
    coverage_case_revision = gap.get("coverage_case_revision")
    proof_ids = gap.get("proof_ids")
    safe_topic = gap.get("safe_topic")
    required_evidence = gap.get("required_evidence")
    observation_count = gap.get("observation_count")
    if not (
        isinstance(gap_id, str)
        and gap.get("authority_id") == authority_id
        and gap.get("revision") == expected_gap_revision
        and gap.get("lifecycle") == "open"
        and isinstance(coverage_case_id, str)
        and isinstance(coverage_case_revision, str)
        and isinstance(proof_ids, list)
        and all(isinstance(item, str) for item in proof_ids)
        and isinstance(safe_topic, str)
        and isinstance(required_evidence, list)
        and all(isinstance(item, str) for item in required_evidence)
        and isinstance(observation_count, int)
    ):
        raise ContractValidationError("open Gap does not match expected closure state")

    result_revision = f"gap-rev-{observation_count + 1}-closed"
    rendered_proof_ids = json.dumps(proof_ids, ensure_ascii=False, separators=(",", ":"))
    rendered_evidence = json.dumps(
        required_evidence,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    gap_document = (
        "---\n"
        "schema: owledge.gap/1\n"
        "document_version: 1\n"
        f"gap_id: {gap_id}\n"
        f"authority_id: {authority_id}\n"
        f"revision: {result_revision}\n"
        "lifecycle: closed\n"
        f"coverage_case_id: {coverage_case_id}\n"
        f"coverage_case_revision: {coverage_case_revision}\n"
        f"proof_ids: {rendered_proof_ids}\n"
        f"safe_topic: {safe_topic}\n"
        f"required_evidence: {rendered_evidence}\n"
        f"observation_count: {observation_count}\n"
        f"resolved_at: {resolved_at}\n"
        f"approved_by_user: {approved_by_user}\n"
        "---\n\n"
        f"# {safe_topic}\n\n"
        "Required Evidence is covered.\n"
    )
    receipt_id = f"receipt:{authority_id.replace(':', '-')}:gap-close-{observation_count:03d}"
    receipt_document = (
        "---\n"
        "schema: owledge.receipt/1\n"
        "document_version: 1\n"
        f"receipt_id: {receipt_id}\n"
        f"authority_id: {authority_id}\n"
        "operation: gap_verify\n"
        "outcome: ok/gap_closed\n"
        f"base_revision: {expected_gap_revision}\n"
        f"result_revision: {result_revision}\n"
        f"operation_id: {operation_id}\n"
        f"approved_by_user: {approved_by_user}\n"
        "---\n\n"
        "# Core Effect Receipt\n\n"
        "Deterministic content-minimized effect evidence.\n"
    )
    gap_target = resolved_root / ".owledge" / "gaps" / f"{gap_id.replace(':', '-')}.md"
    receipt_target = (
        resolved_root
        / ".owledge"
        / "receipts"
        / f"{receipt_id.replace(':', '-')}.md"
    )
    if _effect_exists(resolved_root, receipt_target):
        raise ContractValidationError("Gap closure receipt exists without replay match")
    _write_effect_batch(resolved_root, {gap_target: gap_document, receipt_target: receipt_document})
    return (
        {
            "gap_id": gap_id,
            "gap_revision": result_revision,
            "lifecycle": "closed",
            "resolved_at": resolved_at,
            "approved_by_user": approved_by_user,
        },
        receipt_id,
    )


def record_trace_event(
    root: Path,
    *,
    authority_id: str,
    event: dict[str, object],
) -> dict[str, object]:
    """Append one content-minimized lifecycle event with receipt idempotency."""

    resolved_root = _validated_root(root)
    receipt_id = event.get("receipt_id")
    if not isinstance(receipt_id, str) or event.get("authority_id") != authority_id:
        raise ContractValidationError("Trace event binding is invalid")
    trace_id = f"trace:{authority_id.replace(':', '-')}:gap-closure-001"
    target = (
        resolved_root / ".owledge" / "traces" / f"{trace_id.replace(':', '-')}.md"
    )
    events: list[dict[str, object]] = []
    if _effect_exists(resolved_root, target):
        metadata, _ = _read_effect_metadata(resolved_root, target)
        existing = metadata.get("events")
        if not (
            metadata.get("schema") == "owledge.trace/1"
            and metadata.get("trace_id") == trace_id
            and metadata.get("authority_id") == authority_id
            and isinstance(existing, list)
            and all(isinstance(item, dict) for item in existing)
        ):
            raise ContractValidationError("existing Trace is invalid")
        events = [dict(item) for item in existing]
        matches = [item for item in events if item.get("receipt_id") == receipt_id]
        if matches:
            if len(matches) != 1 or matches[0] != event:
                raise ContractValidationError("Trace replay binding does not match")
            return {"trace_id": trace_id, "events": events}
    events.append(dict(event))
    rendered_events = json.dumps(events, ensure_ascii=False, separators=(",", ":"))
    document = (
        "---\n"
        "schema: owledge.trace/1\n"
        "document_version: 1\n"
        f"trace_id: {trace_id}\n"
        f"authority_id: {authority_id}\n"
        f"events: {rendered_events}\n"
        "---\n\n"
        "# Gap Closure Trace\n\n"
        f"{len(events)} content-minimized durable lifecycle events.\n"
    )
    if len(events) == 6:
        document = document.replace(
            "6 content-minimized durable lifecycle events.",
            "Six content-minimized durable lifecycle events.",
        )
    _write_exact_atomic(resolved_root, target, document)
    return {"trace_id": trace_id, "events": events}


def read_trace(
    root: Path,
    *,
    authority_id: str,
    receipt_id: str,
) -> dict[str, object]:
    """Read the single lifecycle Trace containing a requested receipt."""

    resolved_root = _validated_root(root)
    trace_root = resolved_root / ".owledge" / "traces"
    if not trace_root.is_dir():
        raise ContractValidationError("Trace is missing")
    matches: list[dict[str, object]] = []
    for target in sorted(trace_root.glob("*.md"), key=lambda item: item.name):
        metadata, _ = _read_effect_metadata(resolved_root, target)
        events = metadata.get("events")
        if not (
            metadata.get("schema") == "owledge.trace/1"
            and metadata.get("authority_id") == authority_id
            and isinstance(metadata.get("trace_id"), str)
            and isinstance(events, list)
            and all(isinstance(item, dict) for item in events)
        ):
            raise ContractValidationError("Trace is invalid")
        if any(item.get("receipt_id") == receipt_id for item in events):
            matches.append({"trace_id": metadata["trace_id"], "events": events})
    if len(matches) != 1:
        raise ContractValidationError("Trace receipt binding is missing or ambiguous")
    for event in matches[0]["events"]:
        identity = event.get("receipt_id")
        if not isinstance(identity, str):
            raise ContractValidationError("Trace receipt identity is invalid")
        receipt_target = resolved_root / ".owledge" / "receipts" / f"{identity.replace(':', '-')}.md"
        receipt, _ = _read_effect_metadata(resolved_root, receipt_target)
        if (receipt.get("schema") != "owledge.receipt/1"
                or receipt.get("receipt_id") != identity
                or receipt.get("authority_id") != authority_id
                or receipt.get("outcome") != event.get("outcome")
                or receipt.get("result_revision") != event.get("result_revision")):
            raise ContractValidationError("Trace receipt binding does not match durable evidence")
    return matches[0]


def source_snapshot_for_proof(root: Path, proof_id: str) -> str:
    resolved_root = _validated_root(root)
    receipts = resolved_root / ".owledge" / "receipts"
    if not receipts.is_dir():
        raise ContractValidationError("Absence Proof receipt is missing")
    matches: list[str] = []
    for target in sorted(receipts.glob("*.md"), key=lambda item: item.name):
        metadata, _ = _read_effect_metadata(resolved_root, target)
        if (
            metadata.get("schema") == "owledge.receipt/1"
            and metadata.get("operation") == "gap_admit"
            and metadata.get("proof_id") == proof_id
            and isinstance(metadata.get("source_snapshot_id"), str)
        ):
            matches.append(str(metadata["source_snapshot_id"]))
    if len(matches) != 1:
        raise ContractValidationError("Absence Proof receipt is missing or duplicated")
    return matches[0]


def apply_bundle_open(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    gap_revision: str,
    bundle_id: str,
    bundle_revision: str,
    bundle_markdown: str,
) -> str:
    """Persist the derived Bundle and exact receipt with idempotent replay."""

    resolved_root = _validated_root(root)
    epoch = migration_epoch(resolved_root, authority_id)
    bundle_suffix = bundle_id.rsplit("-", 1)[-1]
    receipt_id = f"receipt:{authority_id.replace(':', '-')}:bundle-open-{bundle_suffix}"
    bundle_target = (
        resolved_root / ".owledge" / "bundles" / f"{bundle_id.replace(':', '-')}.md"
    )
    receipt_target = (
        resolved_root
        / ".owledge"
        / "receipts"
        / f"{receipt_id.replace(':', '-')}.md"
    )
    receipt = (
        "---\n"
        "schema: owledge.receipt/1\n"
        "document_version: 1\n"
        f"receipt_id: {receipt_id}\n"
        f"authority_id: {authority_id}\n"
        "operation: bundle_open\n"
        "outcome: ok/bundle_ready\n"
        f"base_revision: {gap_revision}\n"
        f"result_revision: {bundle_revision}\n"
        f"operation_id: {operation_id}\n"
        + (f"migration_epoch: {epoch}\nresult_sha256: {sha256(bundle_markdown.encode('utf-8')).hexdigest()}\n"
           if epoch is not None else "")
        + "---\n\n"
        "# Core Effect Receipt\n\n"
        "Deterministic content-minimized effect evidence.\n"
    )
    expected_bundle = bundle_markdown.encode("utf-8")
    expected_receipt = receipt.encode("utf-8")
    bundle_exists = _effect_exists(resolved_root, bundle_target)
    receipt_exists = _effect_exists(resolved_root, receipt_target)
    if bundle_exists or receipt_exists:
        if not bundle_exists or not receipt_exists:
            raise ContractValidationError("Bundle effect is only partially durable")
        if (
            _read_exact_effect(resolved_root, bundle_target) != expected_bundle
            or _read_exact_effect(resolved_root, receipt_target) != expected_receipt
        ):
            raise ContractValidationError("existing Bundle effect does not match replay")
        return receipt_id
    _write_effect_batch(resolved_root, {bundle_target: bundle_markdown, receipt_target: receipt})
    return receipt_id


def read_bundle(root: Path, bundle_id: str) -> str:
    resolved_root = _validated_root(root)
    target = (
        resolved_root / ".owledge" / "bundles" / f"{bundle_id.replace(':', '-')}.md"
    )
    metadata, encoded = _read_effect_metadata(resolved_root, target)
    if (
        metadata.get("schema") != "owledge.maintenance-bundle/1"
        or metadata.get("bundle_id") != bundle_id
    ):
        raise ContractValidationError("Maintenance Bundle identity does not match")
    authority_id = metadata.get("authority_id")
    if not isinstance(authority_id, str):
        raise ContractValidationError("Maintenance Bundle authority is missing")
    epoch = migration_epoch(resolved_root, authority_id)
    if epoch is not None:
        bundle_suffix = bundle_id.rsplit("-", 1)[-1]
        receipt_id = f"receipt:{authority_id.replace(':', '-')}:bundle-open-{bundle_suffix}"
        receipt, _ = _read_effect_metadata(resolved_root, resolved_root / ".owledge" / "receipts" /
                                           f"{receipt_id.replace(':', '-')}.md")
        if (receipt.get("migration_epoch") != epoch or receipt.get("authority_id") != authority_id
                or receipt.get("operation") != "bundle_open" or receipt.get("outcome") != "ok/bundle_ready"
                or receipt.get("result_revision") != metadata.get("revision")
                or receipt.get("result_sha256") != sha256(encoded).hexdigest()):
            raise ContractValidationError("Maintenance Bundle predates rights migration")
    return encoded.decode("utf-8")


def read_existing_bundle(root: Path, bundle_id: str) -> str | None:
    resolved = _validated_root(root)
    target = resolved / ".owledge" / "bundles" / f"{bundle_id.replace(':', '-')}.md"
    return read_bundle(resolved, bundle_id) if _effect_exists(resolved, target) else None


def _render_candidate_document(
    candidate: dict[str, object],
    changeset_id: str,
) -> str:
    candidate_id = candidate["candidate_id"]
    authority_id = candidate["authority_id"]
    candidate_revision = candidate["candidate_revision"]
    lifecycle = candidate["lifecycle"]
    origin = (
        "Reported Project possibility or exceptional signal; Owner review records it without factual promotion."
        if candidate.get("candidate_kind") == "project_record"
        else
        "Reported from bounded Agent work; verification and applicability are claims for review."
        if candidate.get("candidate_kind") == "lesson_capture"
        else
        "Derived from validated external Source evidence."
        if candidate.get("candidate_kind") == "source_curation"
        else
        "Derived from validated Reuse Feed evidence."
        if candidate.get("candidate_kind") == "global_curation"
        else "Derived from one validated editable Gap response."
    )
    return (
        "---\n"
        "schema: owledge.candidate/1\n"
        "document_version: 1\n"
        f"candidate_id: {candidate_id}\n"
        f"authority_id: {authority_id}\n"
        f"revision: {candidate_revision}\n"
        f"lifecycle: {lifecycle}\n"
        "processing_layer: delta\n"
        "source_trust: internal\n"
        "candidate: "
        + json.dumps(candidate, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        f"changeset_id: {changeset_id}\n"
        "---\n\n"
        "# Candidate Preview\n\n"
        f"{origin}\n"
    )


def contribute_for_reuse(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    source: ManagedMarkdown,
) -> tuple[dict[str, object], str]:
    """Copy one typed Project record into noncanonical global evidence."""

    resolved_root = _validated_root(root)
    kind = source.metadata.get("knowledge_kind")
    if not isinstance(kind, str) or kind not in {"lesson", "idea", "project_essence", "finding"}:
        raise ContractValidationError("source record is not reusable evidence")
    if kind in {"idea", "finding"} and source.metadata.get("source_trust") == "reviewed":
        from .lesson_capture import validate_project_record
        validate_project_record(source)
    if kind == "project_essence" and source.metadata.get("source_trust") == "reviewed":
        from .lesson_capture import validate_project_essence
        validate_project_essence(source)
    area_header = ""
    if "knowledge_area" in source.metadata:
        area = source.metadata["knowledge_area"]
        if (not isinstance(area, str) or not area.strip() or len(area) > 80
                or any(ord(char) < 32 or char in "\x85\u2028\u2029" for char in area)):
            raise ContractValidationError("source Knowledge Area is invalid")
        area_header = f"knowledge_area: {json.dumps(area)}\n"
    source_authority = source.authority_id
    if not source_authority.startswith("project:") or not authority_id.startswith(
        "user-global:"
    ):
        raise ContractValidationError("reuse contribution authority transition is invalid")
    slug_seed = f"{source_authority}\0{source.artifact_id}\0{source.revision}"
    suffix = sha256(slug_seed.encode("utf-8")).hexdigest()[:16]
    contribution_id = f"contribution:{authority_id.replace(':', '-')}-{suffix}"
    revision = f"contribution-rev-1-{suffix}"
    stage = "inbox" if kind == "finding" else "reuse_feed"
    relative_directory = "inbox" if kind == "finding" else "reuse-feed"
    target = (
        resolved_root
        / ".owledge"
        / relative_directory
        / f"{contribution_id.replace(':', '-')}.md"
    )
    receipt_id = f"receipt:{authority_id.replace(':', '-')}:contribute-{suffix}"
    receipt_target = (
        resolved_root
        / ".owledge"
        / "receipts"
        / f"{receipt_id.replace(':', '-')}.md"
    )
    memory_kind = source.metadata.get("memory_kind", "semantic")
    origin_header = ""
    if kind == "lesson" and "lesson_origin" in source.metadata:
        from .lesson_capture import validate_origin
        validate_origin(source.metadata["lesson_origin"], source.authority_id)
        origin_header = f"source_lesson_origin: {json.dumps(source.metadata['lesson_origin'], ensure_ascii=False)}\n"
    if kind in {"idea", "finding"} and source.metadata.get("source_trust") == "reviewed":
        origin_header = (f"source_record_origin: {json.dumps(source.metadata['record_origin'], ensure_ascii=False)}\n"
                         f"source_record_status: {source.metadata['record_status']}\n"
                         + (f"source_exception_kind: {source.metadata['exception_kind']}\n" if kind == "finding" else ""))
    if kind == "project_essence" and source.metadata.get("source_trust") == "reviewed":
        origin_header = f"source_concept_origin: {json.dumps(source.metadata['concept_origin'], ensure_ascii=False)}\n"
    contribution = (
        "---\n"
        "schema: owledge.reuse-contribution/1\n"
        "document_version: 1\n"
        f"artifact_id: {contribution_id}\n"
        f"contribution_id: {contribution_id}\n"
        f"authority_id: {authority_id}\n"
        f"revision: {revision}\n"
        "lifecycle: candidate\n"
        "processing_layer: delta\n"
        "source_trust: internal\n"
        "canonical: false\n"
        f"stage: {stage}\n"
        f"knowledge_kind: {kind}\n"
        f"{area_header}"
        f"memory_kind: {memory_kind}\n"
        f"source_artifact_id: {source.artifact_id}\n"
        f"source_authority_id: {source_authority}\n"
        f"source_revision: {source.revision}\n"
        f"source_content_sha256: {source.content_sha256}\n"
        f"source_record_trust: {source.metadata.get('source_trust')}\n"
        f"source_processing_layer: {source.metadata.get('processing_layer')}\n"
        f"source_relative_path: {json.dumps(source.relative_path, ensure_ascii=False)}\n"
        f"{origin_header}"
        "---\n"
        f"{source.body}"
    )
    receipt = (
        "---\n"
        "schema: owledge.receipt/1\n"
        "document_version: 1\n"
        f"receipt_id: {receipt_id}\n"
        f"authority_id: {authority_id}\n"
        "operation: contribute_for_reuse\n"
        "outcome: ok/contribution_recorded\n"
        f"operation_id: {operation_id}\n"
        f"source_artifact_id: {source.artifact_id}\n"
        f"source_authority_id: {source_authority}\n"
        f"source_revision: {source.revision}\n"
        f"result_revision: {revision}\n"
        "---\n\n"
        "# Core Effect Receipt\n\n"
        "Deterministic content-minimized effect evidence.\n"
    )
    expected = {
        target: contribution.encode("utf-8"),
        receipt_target: receipt.encode("utf-8"),
    }
    existence = {path: _effect_exists(resolved_root, path) for path in expected}
    if any(existence.values()):
        if not all(existence.values()) or any(
            _read_exact_effect(resolved_root, path) != content
            for path, content in expected.items()
        ):
            raise ContractValidationError("reuse contribution replay does not match")
    else:
        _write_effect_batch(resolved_root, {target: contribution, receipt_target: receipt})
    return (
        {
            "contribution_id": contribution_id,
            "revision": revision,
            "content_sha256": sha256(contribution.encode("utf-8")).hexdigest(),
            "stage": stage,
            "knowledge_kind": kind,
            "source_artifact_id": source.artifact_id,
            "source_authority_id": source_authority,
            "source_revision": source.revision,
        },
        receipt_id,
    )


def record_maintenance_observation(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    observation: dict[str, object],
) -> str:
    """Persist one content-minimized noncanonical maintenance receipt."""

    resolved_root = _validated_root(root)
    encoded = json.dumps(
        observation,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = sha256(encoded.encode("utf-8")).hexdigest()
    operation_digest = sha256(operation_id.encode("utf-8")).hexdigest()[:16]
    receipt_id = (
        f"receipt:{authority_id.replace(':', '-')}:maintenance-{operation_digest}"
    )
    target = (
        resolved_root
        / ".owledge"
        / "receipts"
        / f"{receipt_id.replace(':', '-')}.md"
    )
    document = (
        "---\n"
        "schema: owledge.receipt/1\n"
        "document_version: 1\n"
        f"receipt_id: {receipt_id}\n"
        f"authority_id: {authority_id}\n"
        "operation: maintenance_observe\n"
        "outcome: ok/maintenance_observed\n"
        f"operation_id: {operation_id}\n"
        f"observation_sha256: {digest}\n"
        f"documents_scanned: {observation.get('documents_scanned')}\n"
        f"bytes_scanned: {observation.get('bytes_scanned')}\n"
        f"candidate_count: {len(observation.get('candidate_ids', []))}\n"
        "canonical_writes: 0\n"
        "---\n\n"
        "# Maintenance Observation Receipt\n\n"
        "No canonical knowledge effect was applied.\n"
    )
    if _effect_exists(resolved_root, target):
        if _read_exact_effect(resolved_root, target) != document.encode("utf-8"):
            raise ContractValidationError("maintenance observation replay does not match")
        return receipt_id
    _write_exact_atomic(resolved_root, target, document)
    return receipt_id


def _effect_binding_hash(value: dict[str, object]) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")).hexdigest()


def verify_source_refresh_issuance(root: Path, candidate: dict[str, object],
                                   changeset: dict[str, object]) -> None:
    """Tie a refresh to its original trusted staging receipt, not editable paired effects."""
    if candidate.get("candidate_kind") != "source_curation":
        return
    candidate_id = candidate.get("candidate_id")
    if not isinstance(candidate_id, str):
        raise ContractValidationError("source Candidate identity is invalid")
    if candidate.get("source_refresh_binding") is None:
        preview = candidate.get("review_preview")
        authority_id = candidate.get("authority_id")
        artifact_id = preview.get("artifact_id") if isinstance(preview, dict) else None
        artifact_prefix = f"memory:{authority_id.replace(':', '-')}-source-" if isinstance(authority_id, str) else ""
        if not isinstance(artifact_id, str) or not artifact_id.startswith(artifact_prefix):
            raise ContractValidationError("source Candidate artifact identity is invalid")
        stem = f"candidate:{authority_id.replace(':', '-')}:source-{artifact_id.removeprefix(artifact_prefix)}"
        if not candidate_id.startswith(stem) or candidate_id.removeprefix(stem).startswith("-refresh-"):
            raise ContractValidationError("source refresh issuance marker is missing")
        return
    authority_id = candidate.get("authority_id")
    if not isinstance(authority_id, str) or not candidate_id.startswith(
            f"candidate:{authority_id.replace(':', '-')}:source-"):
        raise ContractValidationError("source refresh authority is invalid")
    suffix = sha256(candidate_id.encode("utf-8")).hexdigest()[:16]
    receipt_id = f"receipt:{authority_id.replace(':', '-')}:candidate-preview-{suffix}"
    resolved = _validated_root(root)
    receipt, _ = _read_effect_metadata(resolved, resolved / ".owledge" / "receipts" /
                                       f"{receipt_id.replace(':', '-')}.md")
    initial = dict(candidate)
    if initial.get("lifecycle") == "reviewed":
        initial.pop("reviewed_by", None)
        initial.pop("reviewed_result_sha256", None)
        initial["lifecycle"] = "candidate"
        initial["candidate_revision"] = "candidate-rev-1"
    if (receipt.get("schema") != "owledge.receipt/1" or receipt.get("receipt_id") != receipt_id
            or receipt.get("authority_id") != authority_id
            or receipt.get("operation") != "source_reference_refresh"
            or receipt.get("outcome") != "ok/source_candidate_ready"
            or not isinstance(receipt.get("operation_id"), str)
            or not receipt["operation_id"].startswith("op:reference-refresh:")
            or receipt.get("result_revision") != "candidate-rev-1"
            or receipt.get("candidate_binding_sha256") != _effect_binding_hash(initial)
            or receipt.get("changeset_binding_sha256") != _effect_binding_hash(changeset)):
        raise ContractValidationError("source refresh was not issued by Owner staging")


def apply_candidate_preview(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    candidate: dict[str, object],
    changeset: dict[str, object],
) -> str:
    """Persist a deterministic Candidate and staged ChangeSet, never knowledge."""

    resolved_root = _validated_root(root)
    epoch = migration_epoch(resolved_root, authority_id)
    candidate_id = candidate.get("candidate_id")
    candidate_revision = candidate.get("candidate_revision")
    changeset_id = changeset.get("changeset_id")
    if not all(
        isinstance(item, str) and item
        for item in (candidate_id, candidate_revision, changeset_id)
    ):
        raise ContractValidationError("Candidate preview identity is incomplete")
    candidate = {**candidate, "settings_snapshot_sha256": settings_snapshot_token(resolved_root, authority_id)}
    candidate_suffix = (
        sha256(str(candidate_id).encode("utf-8")).hexdigest()[:16]
        if candidate.get("candidate_kind") in {"global_curation", "global_essence", "source_curation", "lesson_capture", "project_record", "project_essence"}
        else str(candidate_id).rsplit("-", 1)[-1]
    )
    receipt_id = (
        f"receipt:{authority_id.replace(':', '-')}:candidate-preview-{candidate_suffix}"
    )
    candidate_target = (
        resolved_root
        / ".owledge"
        / "candidates"
        / f"{candidate_id.replace(':', '-')}.md"
    )
    changeset_target = (
        resolved_root
        / ".owledge"
        / "changesets"
        / f"{changeset_id.replace(':', '-')}.md"
    )
    receipt_target = (
        resolved_root
        / ".owledge"
        / "receipts"
        / f"{receipt_id.replace(':', '-')}.md"
    )
    candidate_document = _render_candidate_document(candidate, changeset_id)
    changeset_document = (
        "---\n"
        "schema: owledge.changeset/1\n"
        "document_version: 1\n"
        f"changeset_id: {changeset_id}\n"
        f"authority_id: {authority_id}\n"
        "revision: changeset-rev-1\n"
        "lifecycle: staged\n"
        "processing_layer: delta\n"
        "source_trust: internal\n"
        "changeset: "
        + json.dumps(changeset, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        "---\n\n"
        "# Staged ChangeSet\n\n"
        "No canonical effect has been applied.\n"
    )
    preview_operation = (
        "project_essence_candidate"
        if candidate.get("candidate_kind") == "project_essence"
        else
        "project_record_candidate"
        if candidate.get("candidate_kind") == "project_record"
        else
        "lesson_candidate"
        if candidate.get("candidate_kind") == "lesson_capture"
        else
        "source_reference_refresh"
        if candidate.get("candidate_kind") == "source_curation" and candidate.get("source_refresh_binding") is not None
        else
        "source_candidate"
        if candidate.get("candidate_kind") == "source_curation"
        else
        "curate_candidate"
        if candidate.get("candidate_kind") in {"global_curation", "global_essence"}
        else "bundle_preview"
    )
    preview_outcome = (
        "project_essence_candidate_ready"
        if candidate.get("candidate_kind") == "project_essence"
        else
        "project_record_candidate_ready"
        if candidate.get("candidate_kind") == "project_record"
        else
        "lesson_candidate_ready"
        if candidate.get("candidate_kind") == "lesson_capture"
        else
        "source_candidate_ready"
        if candidate.get("candidate_kind") == "source_curation"
        else
        "curation_candidate_ready"
        if candidate.get("candidate_kind") in {"global_curation", "global_essence"}
        else "candidate_ready"
    )
    receipt = (
        "---\n"
        "schema: owledge.receipt/1\n"
        "document_version: 1\n"
        f"receipt_id: {receipt_id}\n"
        f"authority_id: {authority_id}\n"
        f"operation: {preview_operation}\n"
        f"outcome: ok/{preview_outcome}\n"
        "base_revision: absent\n"
        f"result_revision: {candidate_revision}\n"
        f"operation_id: {operation_id}\n"
        + (f"candidate_binding_sha256: {_effect_binding_hash(candidate)}\n"
           f"changeset_binding_sha256: {_effect_binding_hash(changeset)}\n"
           if preview_operation == "source_reference_refresh" or epoch is not None else "")
        + (f"migration_epoch: {epoch}\n" if epoch is not None else "")
        + "---\n\n"
        "# Core Effect Receipt\n\n"
        "Deterministic content-minimized effect evidence.\n"
    )
    expected = {
        candidate_target: candidate_document.encode("utf-8"),
        changeset_target: changeset_document.encode("utf-8"),
        receipt_target: receipt.encode("utf-8"),
    }
    existence = {
        target: _effect_exists(resolved_root, target) for target in expected
    }
    if any(existence.values()):
        if not all(existence.values()):
            raise ContractValidationError("Candidate preview is only partially durable")
        # Reopen an unchanged staged request after review without revoking or
        # silently reusing approval. The caller still receives an initial preview
        # and must explicitly re-confirm through the Owner path.
        existing_candidate, existing_changeset = read_candidate(resolved_root, str(candidate_id))
        if existing_candidate.get("lifecycle") == "reviewed":
            original_candidate = dict(existing_candidate)
            original_candidate.pop("reviewed_by", None)
            original_candidate.pop("reviewed_result_sha256", None)
            original_candidate["candidate_revision"] = candidate_revision
            original_candidate["lifecycle"] = "candidate"
            if existing_changeset != changeset_id or original_candidate != candidate:
                raise ContractValidationError("reviewed Candidate differs from staged request")
            expected[candidate_target] = _read_exact_effect(resolved_root, candidate_target)
        if any(
            _read_exact_effect(resolved_root, target) != content
            for target, content in expected.items()
        ):
            raise ContractValidationError("existing Candidate preview does not match replay")
        return receipt_id
    _write_effect_batch(resolved_root, {candidate_target: candidate_document,
                                      changeset_target: changeset_document, receipt_target: receipt})
    return receipt_id


def read_candidate(
    root: Path,
    candidate_id: str,
) -> tuple[dict[str, object], str]:
    resolved_root = _validated_root(root)
    target = (
        resolved_root
        / ".owledge"
        / "candidates"
        / f"{candidate_id.replace(':', '-')}.md"
    )
    metadata, _ = _read_effect_metadata(resolved_root, target, max_bytes=1_048_576)
    candidate = metadata.get("candidate")
    changeset_id = metadata.get("changeset_id")
    if not (
        metadata.get("schema") == "owledge.candidate/1"
        and metadata.get("candidate_id") == candidate_id
        and isinstance(candidate, dict)
        and candidate.get("candidate_id") == candidate_id
        and candidate.get("authority_id") == metadata.get("authority_id")
        and candidate.get("candidate_revision") == metadata.get("revision")
        and candidate.get("lifecycle") == metadata.get("lifecycle")
        and isinstance(changeset_id, str)
    ):
        raise ContractValidationError("Candidate identity does not match")
    expected_settings = settings_snapshot_token(resolved_root, str(metadata["authority_id"]))
    saved_settings = candidate.get("settings_snapshot_sha256")
    if saved_settings != expected_settings:
        if saved_settings is not None or any(item["state"] != "absent"
                for item in inspect_settings(resolved_root, str(metadata["authority_id"]))["layers"]):
            raise ContractValidationError("Candidate Settings snapshot changed")
    if migration_epoch(resolved_root, str(metadata["authority_id"])) is not None:
        verify_migration_candidate_issuance(resolved_root, str(metadata["authority_id"]),
            candidate, read_changeset(resolved_root, changeset_id))
    return dict(candidate), changeset_id


def read_candidate_queue(
    root: Path, *, authority_id: str, principal_id: str,
    cursor: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Inventory the flat Candidate lane before opening any human review page."""
    resolved = _validated_root(root)
    lane = resolved / ".owledge" / "candidates"
    paths, metadata_entries, metadata_dirs, overflow = _bounded_markdown_inventory(
        (lane,), recursive=False)
    progress = {"metadata_entries_examined": metadata_entries,
                "metadata_directories_examined": metadata_dirs,
                "metadata_entry_limit": _METADATA_ENTRY_LIMIT,
                "candidate_bytes_examined": 0, "candidate_byte_limit": 8_388_608}
    if overflow:
        return {"items": (), "continuation": None, "resource_exhausted": True, **progress}
    inventory: list[tuple[str, str, str]] = []
    staged: list[tuple[str, str]] = []
    used_bytes = 0
    for path in paths:
        before = _materialized_path_facts(resolved, path)
        if before[3] != 1 or not stat.S_ISREG(before[6]):
            raise ContractValidationError("Candidate inventory contains a linked or nonregular file")
        remaining = min(131_072, 8_388_608 - used_bytes)
        if remaining <= 0:
            return {"items": (), "continuation": None, "resource_exhausted": True,
                    **{**progress, "candidate_bytes_examined": used_bytes}}
        try:
            encoded = _read_exact_effect(resolved, path, max_bytes=remaining)
        except ContractValidationError as error:
            if "bounded read" in str(error):
                return {"items": (), "continuation": None, "resource_exhausted": True,
                        **{**progress, "candidate_bytes_examined": used_bytes}}
            raise
        used_bytes += len(encoded)
        if _materialized_path_facts(resolved, path) != before:
            raise ContractValidationError("Candidate inventory changed during bounded read")
        try:
            metadata, _ = parse_markdown_frontmatter(encoded.decode("utf-8"))
        except (UnicodeError, ContractValidationError) as error:
            raise ContractValidationError("Candidate inventory contains malformed Markdown") from error
        candidate = metadata.get("candidate")
        candidate_id = metadata.get("candidate_id")
        revision = metadata.get("revision")
        lifecycle = metadata.get("lifecycle")
        if not (metadata.get("schema") == "owledge.candidate/1"
                and metadata.get("authority_id") == authority_id
                and isinstance(candidate_id, str) and candidate_id
                and path.name == f"{candidate_id.replace(':', '-')}.md"
                and isinstance(revision, str) and revision
                and lifecycle in {"candidate", "reviewed"}
                and isinstance(candidate, dict)
                and candidate.get("candidate_id") == candidate_id
                and candidate.get("authority_id") == authority_id
                and candidate.get("candidate_revision") == revision
                and candidate.get("lifecycle") == lifecycle
                and isinstance(metadata.get("changeset_id"), str)):
            raise ContractValidationError("Candidate inventory identity is invalid")
        inventory.append((path.name, sha256(encoded).hexdigest(), revision))
        if lifecycle == "candidate":
            if not _INITIAL_CANDIDATE_REVISION.fullmatch(revision):
                raise ContractValidationError("Candidate inventory revision is invalid")
            staged.append((candidate_id, revision))
    binding = sha256(json.dumps({"authority_id": authority_id, "principal_id": principal_id,
                                 "inventory": inventory}, sort_keys=True).encode()).hexdigest()
    offset = 0
    if cursor is not None:
        if (not isinstance(cursor, Mapping) or set(cursor) != {"binding", "offset"}
                or cursor.get("binding") != binding or type(cursor.get("offset")) is not int
                or not 0 < cursor["offset"] < len(staged)):
            raise ContractValidationError("Candidate queue cursor is stale or invalid")
        offset = cursor["offset"]
    page = tuple(staged[offset:offset + 10])
    next_offset = offset + len(page)
    return {"items": page, "continuation": {"binding": binding, "offset": next_offset}
            if next_offset < len(staged) else None, "inventory_binding": binding,
            "resource_exhausted": False, **{**progress, "candidate_bytes_examined": used_bytes}}


def apply_candidate_review(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    candidate: dict[str, object],
    changeset_id: str,
    reviewed_by: str,
    reviewed_result_sha256: str | None = None,
) -> tuple[dict[str, object], str]:
    """Apply one local-Owner Candidate approval without canonical effect."""

    resolved_root = _validated_root(root)
    epoch = verify_migration_candidate_issuance(resolved_root, authority_id, candidate,
                                                read_changeset(resolved_root, changeset_id))
    candidate_id = candidate.get("candidate_id")
    if not isinstance(candidate_id, str):
        raise ContractValidationError("Candidate identity is invalid")
    verify_source_refresh_issuance(resolved_root, candidate, read_changeset(resolved_root, changeset_id))
    current_revision = candidate.get("candidate_revision")
    if not isinstance(current_revision, str):
        raise ContractValidationError("Candidate is not reviewable")
    if _INITIAL_CANDIDATE_REVISION.fullmatch(current_revision):
        revision_suffix = current_revision.removeprefix("candidate-rev-1")
        base_revision = current_revision
        reviewed_revision = f"candidate-rev-2-reviewed{revision_suffix}"
    elif _REVIEWED_CANDIDATE_REVISION.fullmatch(current_revision):
        revision_suffix = current_revision.removeprefix("candidate-rev-2-reviewed")
        base_revision = f"candidate-rev-1{revision_suffix}"
        reviewed_revision = current_revision
    else:
        raise ContractValidationError("Candidate is not reviewable")
    reviewed = dict(candidate)
    reviewed["candidate_revision"] = reviewed_revision
    reviewed["lifecycle"] = "reviewed"
    reviewed["reviewed_by"] = reviewed_by
    if reviewed_result_sha256 is not None:
        reviewed["reviewed_result_sha256"] = reviewed_result_sha256
    candidate_target = (
        resolved_root
        / ".owledge"
        / "candidates"
        / f"{candidate_id.replace(':', '-')}.md"
    )
    candidate_suffix = (
        sha256(candidate_id.encode("utf-8")).hexdigest()[:16]
        if candidate.get("candidate_kind") in {"global_curation", "source_curation", "lesson_capture", "project_record"}
        else candidate_id.rsplit("-", 1)[-1]
    )
    receipt_id = f"receipt:{authority_id.replace(':', '-')}:candidate-review-{candidate_suffix}"
    receipt_target = (
        resolved_root
        / ".owledge"
        / "receipts"
        / f"{receipt_id.replace(':', '-')}.md"
    )
    reviewed_document = _render_candidate_document(reviewed, changeset_id)
    receipt = (
        "---\n"
        "schema: owledge.receipt/1\n"
        "document_version: 1\n"
        f"receipt_id: {receipt_id}\n"
        f"authority_id: {authority_id}\n"
        "operation: candidate_review\n"
        "outcome: ok/candidate_approved\n"
        f"base_revision: {base_revision}\n"
        f"result_revision: {reviewed_revision}\n"
        f"operation_id: {operation_id}\n"
        f"reviewed_by: {reviewed_by}\n"
        + (f"migration_epoch: {epoch}\n" if epoch is not None else "")
        + (f"reviewed_candidate_binding_sha256: {_effect_binding_hash(reviewed)}\n" if epoch is not None else "")
        + "---\n\n"
        "# Core Effect Receipt\n\n"
        "Deterministic content-minimized effect evidence.\n"
    )
    expected_candidate = reviewed_document.encode("utf-8")
    expected_receipt = receipt.encode("utf-8")
    if _effect_exists(resolved_root, receipt_target):
        if (
            _read_exact_effect(resolved_root, candidate_target) != expected_candidate
            or _read_exact_effect(resolved_root, receipt_target) != expected_receipt
        ):
            raise ContractValidationError("existing Candidate review does not match replay")
        return reviewed, receipt_id
    if (
        candidate.get("candidate_revision") != base_revision
        or candidate.get("lifecycle") != "candidate"
    ):
        raise ContractValidationError("Candidate is not reviewable")
    _write_effect_batch(resolved_root, {candidate_target: reviewed_document, receipt_target: receipt})
    return reviewed, receipt_id


def read_changeset(root: Path, changeset_id: str) -> dict[str, object]:
    resolved_root = _validated_root(root)
    target = (
        resolved_root
        / ".owledge"
        / "changesets"
        / f"{changeset_id.replace(':', '-')}.md"
    )
    metadata, _ = _read_effect_metadata(resolved_root, target, max_bytes=1_048_576)
    changeset = metadata.get("changeset")
    if not (
        metadata.get("schema") == "owledge.changeset/1"
        and metadata.get("changeset_id") == changeset_id
        and isinstance(changeset, dict)
    ):
        raise ContractValidationError("ChangeSet identity does not match")
    return dict(changeset)


def promote_candidate(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    candidate: dict[str, object],
    changeset: dict[str, object],
    _resume_visible: bool = False,
    promoted_by: str | None = None,
) -> tuple[dict[str, object], str]:
    """Apply one reviewed creation or exact-base correction through a durable intent."""

    from .source_curation import validate_curation_effect
    validate_curation_effect(candidate, changeset)
    resolved_root = _validated_root(root)
    epoch = verify_migration_candidate_issuance(resolved_root, authority_id, candidate, changeset)
    verify_source_refresh_issuance(resolved_root, candidate, changeset)
    effects = changeset.get("effects")
    result_document = changeset.get("result_document")
    result_sha256 = changeset.get("result_sha256")
    changeset_id = changeset.get("changeset_id")
    if not (
        isinstance(candidate.get("candidate_revision"), str)
        and _REVIEWED_CANDIDATE_REVISION.fullmatch(
            str(candidate.get("candidate_revision"))
        )
        and candidate.get("lifecycle") == "reviewed"
        and isinstance(effects, list)
        and len(effects) == 1
        and isinstance(effects[0], dict)
        and (effects[0].get("kind") == "create" or
             (effects[0].get("kind") == "replace"
              and (candidate.get("candidate_kind") in {"source_curation", "lesson_capture", "project_record", "project_essence", "global_essence"}
                   or candidate.get("named_case") is not None
                   or (candidate.get("candidate_kind") == "global_curation"
                       and isinstance(candidate.get("replacement_binding"), dict)
                       and set(candidate["replacement_binding"]) == {"artifact_id", "revision", "content_sha256"}
                       and candidate["replacement_binding"].get("revision") == changeset.get("base_revision")
                       and candidate["replacement_binding"].get("content_sha256") == changeset.get("base_sha256")))))
        and isinstance(effects[0].get("relative_path"), str)
        and isinstance(effects[0].get("result_revision"), str)
        and isinstance(result_document, str)
        and isinstance(result_sha256, str)
        and isinstance(changeset_id, str)
        and sha256(result_document.encode("utf-8")).hexdigest() == result_sha256
    ):
        raise ContractValidationError("reviewed Candidate or ChangeSet is invalid")
    target = resolved_root / str(effects[0]["relative_path"])
    try:
        target.resolve(strict=False).relative_to(resolved_root)
    except ValueError as error:
        raise ContractValidationError("ChangeSet target escapes authority") from error
    if target.is_symlink():
        raise ContractValidationError("ChangeSet target escapes through a link")

    receipt_id = str(changeset.get("receipt_id"))
    if epoch is not None:
        candidate_id = str(candidate.get("candidate_id"))
        suffix = (sha256(candidate_id.encode("utf-8")).hexdigest()[:16]
                  if candidate.get("candidate_kind") in {"global_curation", "source_curation", "lesson_capture", "project_record"}
                  else candidate_id.rsplit("-", 1)[-1])
        review_id = f"receipt:{authority_id.replace(':', '-')}:candidate-review-{suffix}"
        reviewed_receipt, _ = _read_effect_metadata(resolved_root, resolved_root / ".owledge" /
            "receipts" / f"{review_id.replace(':', '-')}.md")
        if (reviewed_receipt.get("migration_epoch") != epoch
                or reviewed_receipt.get("reviewed_candidate_binding_sha256") != _effect_binding_hash(candidate)
                or reviewed_receipt.get("result_revision") != candidate.get("candidate_revision")):
            raise ContractValidationError("Candidate review predates rights migration or changed")
    receipt_target = (
        resolved_root
        / ".owledge"
        / "receipts"
        / f"{receipt_id.replace(':', '-')}.md"
    )
    receipt = (
        "---\n"
        "schema: owledge.receipt/1\n"
        "document_version: 1\n"
        f"receipt_id: {receipt_id}\n"
        f"authority_id: {authority_id}\n"
        "operation: candidate_promote\n"
        "outcome: ok/candidate_promoted\n"
        f"base_revision: {changeset['base_revision']}\n"
        f"result_revision: {effects[0]['result_revision']}\n"
        f"operation_id: {operation_id}\n"
        f"idempotency_key: {changeset['idempotency_key']}\n"
        f"candidate_revision: {candidate['candidate_revision']}\n"
        f"result_sha256: {result_sha256}\n"
        + (f"migration_epoch: {epoch}\n" if epoch is not None else "")
        + "---\n\n"
        "# Core Effect Receipt\n\n"
        "Deterministic content-minimized effect evidence.\n"
    )
    if promoted_by is not None:
        if not re.fullmatch(r"principal:[a-zA-Z0-9:_-]+", promoted_by):
            raise ContractValidationError("promotion actor is invalid")
        receipt = receipt.replace("\n---\n\n# Core Effect Receipt", f"\npromoted_by: {promoted_by}\n---\n\n# Core Effect Receipt")
    expected_target = result_document.encode("utf-8")
    expected_receipt = receipt.encode("utf-8")
    transaction_target = resolved_root / ".owledge" / "transactions" / f"{changeset_id.replace(':', '-')}.md"
    resuming = _resume_visible and _effect_exists(resolved_root, target)
    if resuming:
        if _read_exact_effect(resolved_root, target) != expected_target:
            raise ContractValidationError("recovery canonical bytes do not match")
        if _effect_exists(resolved_root, transaction_target):
            transaction, _ = _read_effect_metadata(resolved_root, transaction_target)
            expected = {
                "schema": "owledge.transaction-intent/1", "changeset_id": changeset_id,
                "authority_id": authority_id, "operation_id": operation_id,
                "target_relative_path": effects[0]["relative_path"],
                "result_sha256": result_sha256, "receipt_id": receipt_id,
            }
            if promoted_by is not None:
                expected["promoted_by"] = promoted_by
            if effects[0]["kind"] == "replace":
                expected.update(base_revision=changeset["base_revision"], base_sha256=changeset["base_sha256"])
            if any(transaction.get(key) != value for key, value in expected.items()) or transaction.get("phase") not in {"intent_durable", "canonical_effect_visible"}:
                raise ContractValidationError("recovery intent binding does not match")
        elif not _effect_exists(resolved_root, receipt_target):
            raise ContractValidationError("visible canonical effect has no durable provenance")
    if _effect_exists(resolved_root, receipt_target):
        replay_target = target
        if (candidate.get("candidate_kind") in {"global_curation", "global_essence", "source_curation", "lesson_capture", "project_record", "project_essence"}
                and _effect_exists(resolved_root, target) and _read_exact_effect(resolved_root, target) != expected_target):
            metadata, _ = parse_markdown_frontmatter(result_document)
            replay_target = _reference_history_target(resolved_root, metadata["artifact_id"], metadata["revision"])
        if (
            not _effect_exists(resolved_root, replay_target)
            or _read_exact_effect(resolved_root, replay_target) != expected_target
            or _read_exact_effect(resolved_root, receipt_target) != expected_receipt
        ):
            raise ContractValidationError("promotion replay binding does not match")
        if resuming and _effect_exists(resolved_root, transaction_target):
            _unlink_effect(resolved_root, transaction_target)
        return (
            {
                "candidate_id": candidate["candidate_id"],
                "candidate_revision": candidate["candidate_revision"],
                "result_revision": effects[0]["result_revision"],
                "result_sha256": result_sha256,
            },
            receipt_id,
        )
    if not resuming and changeset.get("base_revision") == "absent" and _effect_exists(
        resolved_root, target
    ):
        raise ContractValidationError("create-only ChangeSet target already exists")

    if effects[0]["kind"] == "replace":
        result_metadata, _ = parse_markdown_frontmatter(result_document)
        history_target = _reference_history_target(resolved_root, result_metadata["artifact_id"], str(changeset["base_revision"]))
        old_bytes = _read_exact_effect(resolved_root, history_target if resuming else target)
        old = parse_managed_markdown(str(effects[0]["relative_path"]), old_bytes.decode("utf-8"), encoded_document=old_bytes)
        if candidate.get("candidate_kind") == "lesson_capture":
            from .lesson_capture import validate_project_lesson
            validate_project_lesson(old)
        if candidate.get("candidate_kind") == "project_record":
            from .lesson_capture import validate_project_record
            validate_project_record(old)
        if candidate.get("candidate_kind") == "project_essence":
            from .lesson_capture import validate_project_essence
            validate_project_essence(old)
        if candidate.get("candidate_kind") == "global_essence":
            from .lesson_capture import validate_global_essence
            validate_global_essence(old)
        if candidate.get("candidate_kind") == "global_curation":
            from .source_curation import validate_global_reuse_replacement
            result = parse_managed_markdown(str(effects[0]["relative_path"]), result_document,
                                            encoded_document=result_document.encode("utf-8"))
            validate_global_reuse_replacement(old, candidate, changeset, result)
        if candidate.get("candidate_kind") == "source_curation":
            preserved_provenance = old.metadata.get("source_evidence") == result_metadata.get("source_evidence")
            if not preserved_provenance:
                source_refresh = result_metadata.get("source_refresh")
                preserved_provenance = (isinstance(source_refresh, dict)
                    and source_refresh.get("old_source") == old.metadata.get("source_evidence")
                    and source_refresh.get("new_source") == result_metadata.get("source_evidence")
                    and candidate.get("source_refresh_binding") == {
                        "base": result_metadata.get("correction_base"),
                        "old_source": source_refresh["old_source"], "new_source": source_refresh["new_source"]})
        elif candidate.get("candidate_kind") == "lesson_capture":
            preserved_provenance = (old.metadata.get("lesson_origin") == result_metadata.get("lesson_origin")
                                    and "project_origin" not in old.metadata and "project_origin" not in result_metadata)
        elif candidate.get("candidate_kind") == "project_record":
            preserved_provenance = (old.metadata.get("record_origin") == result_metadata.get("record_origin")
                                    and old.metadata.get("knowledge_kind") == result_metadata.get("knowledge_kind")
                                    and old.metadata.get("memory_kind") == result_metadata.get("memory_kind")
                                    and old.metadata.get("record_status") == result_metadata.get("record_status")
                                    and old.metadata.get("exception_kind") == result_metadata.get("exception_kind"))
        elif candidate.get("candidate_kind") == "project_essence":
            preserved_provenance = (old.metadata["concept_origin"]["source_id"]
                                    == result_metadata["concept_origin"]["source_id"])
        elif candidate.get("candidate_kind") == "global_essence":
            preserved_provenance = (old.metadata["project_origin"]["authority_id"]
                                    == result_metadata["project_origin"]["authority_id"])
        else:
            preserved_provenance = (candidate.get("candidate_kind") == "global_curation"
                                    or candidate.get("named_case") is not None
                                    and old.metadata.get("provenance_core_assigned") == result_metadata.get("provenance_core_assigned"))
        if (old.content_sha256 != changeset.get("base_sha256") or old.revision != changeset["base_revision"]
                or old.artifact_id != result_metadata["artifact_id"] or old.authority_id != authority_id
                or not preserved_provenance
                or old.metadata.get("knowledge_area") != result_metadata.get("knowledge_area")
                or old.metadata.get("document_version", 0) + 1 != result_metadata["document_version"]
                or (candidate.get("named_case") is None
                    and old.body.strip() != candidate["review_preview"]["base"]["text"])):
            raise ContractValidationError("correction canonical base differs from reviewed state")
        if not resuming:
            if _effect_exists(resolved_root, history_target):
                if _read_exact_effect(resolved_root, history_target) != old_bytes:
                    raise ContractValidationError("immutable reference history differs")
            else:
                # Cooperating writers hold the authority lock. Atomic publication
                # prevents a killed writer leaving a truncated immutable snapshot.
                _write_exact_atomic(resolved_root, history_target, old_bytes.decode("utf-8"))

    transaction_id = str(changeset_id).replace(":", "-")
    transaction_target = (
        resolved_root / ".owledge" / "transactions" / f"{transaction_id}.md"
    )
    intent_base = (
        "---\n"
        "schema: owledge.transaction-intent/1\n"
        "document_version: 1\n"
        f"changeset_id: {changeset_id}\n"
        f"authority_id: {authority_id}\n"
        f"operation_id: {operation_id}\n"
        f"target_relative_path: {effects[0]['relative_path']}\n"
        f"result_sha256: {result_sha256}\n"
        f"receipt_id: {receipt_id}\n"
    )
    intent_durable = intent_base + "phase: intent_durable\n---\n\n# Transaction Intent\n"
    if effects[0]["kind"] == "replace":
        intent_base += f"base_revision: {changeset['base_revision']}\nbase_sha256: {changeset['base_sha256']}\n"
        intent_durable = intent_base + "phase: intent_durable\n---\n\n# Transaction Intent\n"
    if promoted_by is not None:
        intent_base += f"promoted_by: {promoted_by}\n"
        intent_durable = intent_base + "phase: intent_durable\n---\n\n# Transaction Intent\n"
    canonical_visible = (
        intent_base + "phase: canonical_effect_visible\n---\n\n# Transaction Intent\n"
    )
    if not resuming:
        _write_exact_exclusive(resolved_root, transaction_target, intent_durable)
    try:
        if not resuming:
            _write_exact_atomic(resolved_root, target, result_document)
        _write_exact_atomic(resolved_root, transaction_target, canonical_visible)
        _write_exact_atomic(resolved_root, receipt_target, receipt)
        _unlink_effect(resolved_root, transaction_target)
    except BaseException:
        raise
    return (
        {
            "candidate_id": candidate["candidate_id"],
            "candidate_revision": candidate["candidate_revision"],
            "result_revision": effects[0]["result_revision"],
            "result_sha256": result_sha256,
        },
        receipt_id,
    )


def recover_transaction(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    changeset_id: str,
    changeset: dict[str, object],
    identity_profile: str = "poc-v1",
) -> tuple[dict[str, object], str]:
    """Roll back one durable intent that has no visible canonical effect."""

    resolved_root = _validated_root(root)
    effects = changeset.get("effects")
    if isinstance(changeset.get("result_document"), str):
        metadata, _ = parse_markdown_frontmatter(changeset["result_document"])
        if metadata.get("source_refresh") is not None:
            candidate_id = changeset_id.replace("changeset:", "candidate:", 1)
            candidate, bound_changeset_id = read_candidate(resolved_root, candidate_id)
            if bound_changeset_id != changeset_id:
                raise ContractValidationError("source refresh recovery Candidate differs")
            verify_source_refresh_issuance(resolved_root, candidate, changeset)
    if not (
        changeset.get("changeset_id") == changeset_id
        and isinstance(effects, list)
        and len(effects) == 1
        and isinstance(effects[0], dict)
        and isinstance(effects[0].get("relative_path"), str)
    ):
        raise ContractValidationError("recovery ChangeSet is invalid")
    target = resolved_root / str(effects[0]["relative_path"])
    try:
        target.resolve(strict=False).relative_to(resolved_root)
    except ValueError as error:
        raise ContractValidationError("recovery target escapes authority") from error
    transaction_target = (
        resolved_root
        / ".owledge"
        / "transactions"
        / f"{changeset_id.replace(':', '-')}.md"
    )
    old_visible = False
    if effects[0].get("kind") == "replace":
        if not _effect_exists(resolved_root, target):
            raise ContractValidationError("correction target is missing")
        current_hash = sha256(_read_exact_effect(resolved_root, target)).hexdigest()
        if current_hash not in {changeset.get("base_sha256"), changeset.get("result_sha256")}:
            raise ContractValidationError("correction target is neither old nor new")
        old_visible = current_hash == changeset.get("base_sha256")
    if identity_profile == "mvp-v1" and _effect_exists(resolved_root, target) and not old_visible:
        return _recover_visible_promotion(
            resolved_root, authority_id, operation_id, changeset_id, changeset, transaction_target,
        )
    receipt_id = f"receipt:{authority_id.replace(':', '-')}:recovery-001"
    if identity_profile == "mvp-v1":
        receipt_id = f"receipt:{authority_id.replace(':', '-')}:recovery-{sha256(changeset_id.encode()).hexdigest()[:16]}"
    receipt_target = (
        resolved_root
        / ".owledge"
        / "receipts"
        / f"{receipt_id.replace(':', '-')}.md"
    )
    receipt = (
        "---\n"
        "schema: owledge.receipt/1\n"
        "document_version: 1\n"
        f"receipt_id: {receipt_id}\n"
        f"authority_id: {authority_id}\n"
        "operation: recover\n"
        "outcome: ok/recovered_rollback\n"
        "base_revision: intent_durable\n"
        "result_revision: absent\n"
        f"operation_id: {operation_id}\n"
        f"changeset_id: {changeset_id}\n"
        "---\n\n"
        "# Core Effect Receipt\n\n"
        "Deterministic content-minimized effect evidence.\n"
    )
    result = {
        "changeset_id": changeset_id,
        "recovered_phase": "intent_durable",
        "result_revision": "absent",
    }
    if old_visible:
        receipt = receipt.replace("result_revision: absent\n", f"result_revision: {changeset['base_revision']}\n")
        result["result_revision"] = changeset["base_revision"]
    if _effect_exists(resolved_root, receipt_target):
        if (
            _read_exact_effect(resolved_root, receipt_target) != receipt.encode("utf-8")
            or (_effect_exists(resolved_root, target) and not old_visible)
        ):
            raise ContractValidationError("recovery replay binding does not match")
        if not _effect_exists(resolved_root, transaction_target):
            return result, receipt_id
    transaction, _ = _read_effect_metadata(resolved_root, transaction_target)
    expected_intent = {
        "schema": "owledge.transaction-intent/1",
        "changeset_id": changeset_id,
        "authority_id": authority_id,
        "target_relative_path": effects[0]["relative_path"],
        "result_sha256": changeset.get("result_sha256"),
        "receipt_id": changeset.get("receipt_id"),
        "phase": "intent_durable",
    }
    if old_visible:
        expected_intent.update(base_revision=changeset["base_revision"], base_sha256=changeset["base_sha256"])
    if any(transaction.get(key) != value for key, value in expected_intent.items()):
        raise ContractValidationError("recovery intent binding does not match")
    if _effect_exists(resolved_root, target) and not old_visible:
        raise ContractValidationError("intent-durable recovery target is unexpectedly visible")
    _write_exact_atomic(resolved_root, receipt_target, receipt)
    _unlink_effect(resolved_root, transaction_target)
    return result, receipt_id


def _recover_visible_promotion(root, authority_id, operation_id, changeset_id, changeset, intent_target):
    """Finish only the exact already-visible reviewed effect, never new knowledge."""
    promotion_receipt_id = str(changeset.get("receipt_id"))
    promotion_receipt = root / ".owledge" / "receipts" / f"{promotion_receipt_id.replace(':', '-')}.md"
    binding_target = intent_target if _effect_exists(root, intent_target) else promotion_receipt
    binding, _ = _read_effect_metadata(root, binding_target)
    original_operation = binding.get("operation_id")
    if not isinstance(original_operation, str):
        raise ContractValidationError("promotion operation provenance is missing")
    candidates = []
    for path in sorted((root / ".owledge" / "candidates").glob("*.md")):
        metadata, _ = _read_effect_metadata(root, path)
        if metadata.get("changeset_id") == changeset_id:
            candidates.append(metadata.get("candidate"))
    if len(candidates) != 1 or not isinstance(candidates[0], dict):
        raise ContractValidationError("recovery Candidate binding is ambiguous")
    candidate = candidates[0]
    if candidate.get("authority_id") != authority_id or not isinstance(candidate.get("reviewed_by"), str):
        raise ContractValidationError("recovery Owner binding is missing")
    if candidate.get("candidate_kind") in {"global_curation", "source_curation", "lesson_capture", "project_record"} and candidate.get("reviewed_result_sha256") != changeset.get("result_sha256"):
        raise ContractValidationError("recovery reviewed content is stale")
    actor = binding.get("promoted_by")
    if not isinstance(actor, str):
        raise ContractValidationError("actual promotion actor is missing")
    promoted, _ = promote_candidate(root, authority_id=authority_id, operation_id=original_operation,
                                   candidate=candidate, changeset=changeset, _resume_visible=True, promoted_by=actor)
    # The original Owner-approved effect owns this Trace; the recovering caller
    # does not retroactively become its author.
    record_trace_event(root, authority_id=authority_id, event={
        "event": "candidate_promoted", "authority_id": authority_id, "principal_id": actor,
        "assurance": "local_owner", "base_revision": changeset["base_revision"],
        "result_revision": promoted["result_revision"], "outcome": "ok/candidate_promoted",
        "receipt_id": promotion_receipt_id, "promoted_by": actor,
        "candidate_revision": candidate["candidate_revision"],
    })
    receipt_id = f"receipt:{authority_id.replace(':', '-')}:recovery-commit-{sha256(changeset_id.encode()).hexdigest()[:16]}"
    receipt_target = root / ".owledge" / "receipts" / f"{receipt_id.replace(':', '-')}.md"
    receipt = ("---\nschema: owledge.receipt/1\ndocument_version: 1\n"
               f"receipt_id: {receipt_id}\nauthority_id: {authority_id}\noperation: recover\n"
               f"outcome: ok/recovered_commit\noperation_id: {operation_id}\nchangeset_id: {changeset_id}\n"
               f"promotion_receipt_id: {promotion_receipt_id}\nresult_sha256: {changeset['result_sha256']}\n"
               "---\n\n# Recovery Receipt\n\nExact reviewed effect and Trace completed.\n")
    if _effect_exists(root, receipt_target):
        if _read_exact_effect(root, receipt_target) != receipt.encode("utf-8"):
            raise ContractValidationError("recovery replay does not match")
    else:
        _write_exact_atomic(root, receipt_target, receipt)
    return {"changeset_id": changeset_id, "recovered_phase": "canonical_effect_visible",
            "result_revision": promoted["result_revision"]}, receipt_id


def admit_gap(
    root: Path,
    *,
    authority_id: str,
    operation_id: str,
    coverage_case_id: str,
    coverage_case_revision: str,
    proof_id: str,
    source_snapshot_id: str,
    safe_topic: str,
    required_evidence: list[str],
    expected_gap_revision: str,
    request_sha256: str | None = None,
) -> tuple[dict[str, object], str | None, str]:
    """Apply one exact, idempotent proof-admitted Gap-open effect."""

    resolved_root = _validated_root(root)
    gap_id = _gap_identity(authority_id, coverage_case_id)
    gap_target = (
        resolved_root / ".owledge" / "gaps" / f"{gap_id.replace(':', '-')}.md"
    )
    if _effect_exists(resolved_root, gap_target):
        metadata, _ = _read_effect_metadata(resolved_root, gap_target)
        current_revision = metadata.get("revision")
        proof_ids = metadata.get("proof_ids")
        observation_count = metadata.get("observation_count")
        expected = {
            "schema": "owledge.gap/1",
            "gap_id": gap_id,
            "authority_id": authority_id,
            "coverage_case_id": coverage_case_id,
            "coverage_case_revision": coverage_case_revision,
            "safe_topic": safe_topic,
            "required_evidence": required_evidence,
        }
        if (
            any(metadata.get(key) != value for key, value in expected.items())
            or not isinstance(current_revision, str)
            or not isinstance(proof_ids, list)
            or not all(isinstance(item, str) for item in proof_ids)
            or not isinstance(observation_count, int)
        ):
            raise ContractValidationError("existing Gap contract does not match")
        if metadata.get("lifecycle") not in {"open", "closed"}:
            raise ContractValidationError("existing Gap lifecycle is invalid")
        if proof_id in proof_ids and metadata.get("lifecycle") == "closed":
            raise ContractValidationError("closed Gap cannot reopen from an already resolved proof")
        if proof_id in proof_ids and metadata.get("lifecycle") == "open":
            return (
                {
                    "gap_id": gap_id,
                    "gap_revision": current_revision,
                    "lifecycle": "open",
                    "observation_count": observation_count,
                    "proof_id": proof_id,
                    "source_snapshot_id": source_snapshot_id,
                },
                None,
                "gap_unchanged",
            )
        if expected_gap_revision != current_revision:
            raise ContractValidationError("Gap expected revision does not match")
        next_count = observation_count + 1
        next_revision = f"gap-rev-{next_count + (1 if metadata.get('lifecycle') == 'closed' else 0)}-open"
        next_proof_ids = [*proof_ids, proof_id]
        reason_code = "gap_reopened" if metadata.get("lifecycle") == "closed" else "gap_recurred"
        receipt_id = f"receipt:{authority_id.replace(':', '-')}:gap-recur-{next_count - 1:03d}"
        base_revision = current_revision
    else:
        if expected_gap_revision != "absent":
            raise ContractValidationError("Gap expected revision does not match")
        next_count = 1
        next_revision = "gap-rev-1"
        next_proof_ids = [proof_id]
        reason_code = "gap_opened"
        receipt_id = f"receipt:{authority_id.replace(':', '-')}:gap-open-001"
        base_revision = "absent"

    receipt_target = (
        resolved_root
        / ".owledge"
        / "receipts"
        / f"{receipt_id.replace(':', '-')}.md"
    )
    gap_document = _render_open_gap(
        gap_id=gap_id,
        authority_id=authority_id,
        coverage_case_id=coverage_case_id,
        coverage_case_revision=coverage_case_revision,
        revision=next_revision,
        proof_ids=next_proof_ids,
        safe_topic=safe_topic,
        required_evidence=required_evidence,
        observation_count=next_count,
    )
    receipt_document = _render_gap_receipt(
        receipt_id=receipt_id,
        authority_id=authority_id,
        operation_id=operation_id,
        proof_id=proof_id,
        source_snapshot_id=source_snapshot_id,
        outcome=reason_code,
        base_revision=base_revision,
        result_revision=next_revision,
        request_sha256=request_sha256,
    )
    if _effect_exists(resolved_root, receipt_target):
        raise ContractValidationError("Gap receipt already exists without replay match")
    _write_effect_batch(resolved_root, {gap_target: gap_document, receipt_target: receipt_document})

    result = {
        "gap_id": gap_id,
        "gap_revision": next_revision,
        "lifecycle": "open",
        "observation_count": next_count,
        "proof_id": proof_id,
        "source_snapshot_id": source_snapshot_id,
    }
    return result, receipt_id, reason_code


def source_snapshot_target_name(snapshot: SourceSnapshot) -> str:
    """Return a portable, content-bound directory name for a source snapshot."""

    slug = snapshot.source_id.removeprefix("source:")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise ContractValidationError("source identity is unsafe")
    return f"source-{slug}-{snapshot.snapshot_sha256[:16]}"


def _source_snapshot_files(
    snapshot: SourceSnapshot,
    operation_id: str,
    approved_by: str,
) -> tuple[dict[str, bytes], frozenset[str], str]:
    expected: dict[str, bytes] = {}
    originals: set[str] = set()
    records: list[dict[str, object]] = []
    source_slug = snapshot.source_id.removeprefix("source:")
    for source_file in snapshot.files:
        original_path = (
            Path("originals") / snapshot.snapshot_sha256 / Path(source_file.relative_path)
        ).as_posix()
        expected[original_path] = source_file.content
        originals.add(original_path)
        artifact_id, sidecar = render_source_sidecar(snapshot, source_file)
        record_hash = artifact_id.removeprefix("source-record:")
        sidecar_path = (
            Path(".owledge")
            / "sources"
            / source_slug
            / "records"
            / f"{record_hash}.md"
        ).as_posix()
        expected[sidecar_path] = sidecar.encode("utf-8")
        records.append(
            {
                "artifact_id": artifact_id,
                "content_sha256": source_file.content_sha256,
                "relative_path": source_file.relative_path,
                "sidecar_path": sidecar_path,
                "size_bytes": source_file.size_bytes,
            }
        )
    manifest_path = (
        Path(".owledge") / "sources" / source_slug / "manifest.md"
    ).as_posix()
    expected[manifest_path] = render_source_manifest(snapshot, records).encode("utf-8")
    receipt_id, receipt = render_source_setup_receipt(snapshot, operation_id, approved_by)
    receipt_path = (
        Path(".owledge") / "receipts" / f"setup-{snapshot.snapshot_sha256}.md"
    ).as_posix()
    expected[receipt_path] = receipt.encode("utf-8")
    return expected, frozenset(originals), receipt_id


def _validate_materialized_source(
    target: Path,
    expected: Mapping[str, bytes],
    originals: frozenset[str],
) -> None:
    def directory_facts(path: Path) -> tuple[object, ...]:
        facts = _materialized_path_facts(target, path)
        # Directory allocation size is not content identity. File sizes remain
        # checked by stable file reads; exact tree and bytes are checked below.
        return facts[:4] + facts[5:]

    if not target.is_dir() or _is_reparse_path(target):
        raise ContractValidationError("source snapshot target is invalid")
    actual_files: set[str] = set()
    actual_directories: set[str] = set()
    observed_content: dict[str, bytes] = {}
    pending = [target]
    while pending:
        directory = pending.pop()
        before = directory_facts(directory)
        try:
            entries = sorted(directory.iterdir(), key=lambda item: item.name.casefold())
        except (FileNotFoundError, OSError) as error:
            raise ContractValidationError("source snapshot changed during replay") from error
        after = directory_facts(directory)
        if before != after:
            raise ContractValidationError("source snapshot changed during replay")
        for path in entries:
            current = directory_facts(directory)
            if current != after:
                raise ContractValidationError("source snapshot changed during replay")
            relative = path.relative_to(target).as_posix()
            if path.is_dir():
                actual_directories.add(relative)
                pending.append(path)
            elif path.is_file():
                actual_files.add(relative)
                observed_content[relative] = _read_stable_materialized_file(target, path)
            else:
                raise ContractValidationError("source snapshot entry is invalid")
        if directory_facts(directory) != after:
            raise ContractValidationError("source snapshot changed during replay")
    if actual_files != set(expected):
        raise ContractValidationError("source snapshot file set does not match")
    expected_directories = {
        Path(*Path(relative).parts[:index]).as_posix()
        for relative in expected
        for index in range(1, len(Path(relative).parts))
    }
    if actual_directories != expected_directories:
        raise ContractValidationError("source snapshot directory set does not match")
    for relative, content in expected.items():
        path = target / Path(relative)
        if observed_content.get(relative) != content:
            raise ContractValidationError("source snapshot bytes do not match")
        if relative in originals and path.stat().st_mode & stat.S_IWUSR:
            raise ContractValidationError("source snapshot original is writable")


def _materialized_path_facts(root: Path, path: Path) -> tuple[object, ...]:
    try:
        observed = path.lstat()
        attributes = getattr(observed, "st_file_attributes", 0)
        linked = path.is_symlink() or bool(
            attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        )
        resolved = path.resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, OSError, ValueError) as error:
        raise ContractValidationError("source snapshot path escaped or changed") from error
    if linked:
        raise ContractValidationError("source snapshot contains a link")
    return (
        resolved,
        int(observed.st_dev),
        int(observed.st_ino),
        int(observed.st_nlink),
        int(observed.st_size),
        int(observed.st_mtime_ns),
        int(observed.st_mode),
        linked,
    )


def _read_stable_materialized_file(root: Path, path: Path, *, max_bytes: int | None = None) -> bytes:
    before = _materialized_path_facts(root, path)
    if before[3] != 1:
        raise ContractValidationError("source snapshot contains a hardlink")
    if max_bytes is not None and (max_bytes < 0 or before[4] > max_bytes):
        raise ContractValidationError("source snapshot exceeds its bounded read")
    try:
        if max_bytes is None:
            content = path.read_bytes()
        else:
            with path.open("rb") as handle:
                content = handle.read(max_bytes + 1)
            if len(content) > max_bytes:
                raise ContractValidationError("source snapshot exceeds its bounded read")
    except (FileNotFoundError, OSError) as error:
        raise ContractValidationError("source snapshot changed during replay") from error
    after = _materialized_path_facts(root, path)
    if before != after or len(content) != before[4]:
        raise ContractValidationError("source snapshot changed during replay")
    return content


def _path_identity(facts: tuple[object, ...]) -> tuple[object, ...]:
    return facts[0], facts[1], facts[2], facts[6], facts[7]


def _assert_workspace_anchor(
    workspace_candidate: Path,
    resolved_workspace: Path,
    expected_identity: tuple[object, ...],
) -> None:
    if any(_is_reparse_path(path) for path in (workspace_candidate, *workspace_candidate.parents)):
        raise ContractValidationError("setup workspace crosses a link")
    current = _materialized_path_facts(resolved_workspace, resolved_workspace)
    if _path_identity(current) != expected_identity:
        raise ContractValidationError("setup workspace changed during materialization")


def _assert_target_anchor(
    resolved_workspace: Path,
    target: Path,
    expected_identity: tuple[object, ...],
) -> None:
    current = _materialized_path_facts(resolved_workspace, target)
    if _path_identity(current) != expected_identity:
        raise ContractValidationError("source snapshot target changed during materialization")


def _clear_readonly_and_remove(path: Path) -> None:
    def repair_permissions(function: object, candidate: str, _info: object) -> None:
        os.chmod(candidate, stat.S_IWRITE | stat.S_IREAD)
        if callable(function):
            function(candidate)

    if path.exists():
        shutil.rmtree(path, onerror=repair_permissions)


def update_owner_workspace_state(workspace: Path, expected_bytes: bytes, new_bytes: bytes) -> None:
    """Compare-and-swap private host metadata; never changes knowledge files."""
    resolved = _validated_root(Path(workspace))
    target = resolved / "workspace.json"
    try:
        document = json.loads(new_bytes)
    except (ValueError, UnicodeError) as error:
        raise ContractValidationError("workspace metadata is invalid") from error
    if not isinstance(document, dict) or len(new_bytes) > 1024 * 1024:
        raise ContractValidationError("workspace metadata is not a bounded object")
    try:
        previous = json.loads(expected_bytes)
    except (ValueError, UnicodeError) as error:
        raise ContractValidationError("expected workspace metadata is invalid") from error
    mapping = previous.get("roots") if isinstance(previous, dict) else None
    if not isinstance(mapping, dict):
        raise ContractValidationError("workspace authority roots are missing")
    authority_roots = []
    for key, directory in (("project", "project"), ("user-global", "global")):
        if key in mapping:
            if mapping[key] != directory:
                raise ContractValidationError("workspace authority root is invalid")
            authority_roots.append(resolved / directory)
    if not authority_roots:
        raise ContractValidationError("workspace has no declared authority")
    with authority_write_locks((resolved, *authority_roots)):
        for root in authority_roots:
            if not _effect_exists(root, root / ".owledge/authority.md"):
                raise ContractValidationError("declared workspace authority header is missing")
        if _read_exact_effect(resolved, target) != expected_bytes:
            raise ContractValidationError("workspace state changed after preview")
        _write_exact_atomic(resolved, target, new_bytes.decode("utf-8"))


_REUSE_PENDING = ".owledge/project-reuse-registration.json"
_REUSE_RECEIPT = ".owledge/project-reuse-receipt.json"
_REUSE_LINK = "project/.owledge/global-contribution-link.md"
_PROJECT_SCHEMA = "owledge.private-project-workspace/1"
_LINKED_PROJECT_SCHEMA = "owledge.private-project-workspace/2"
_REUSE_GLOBAL = "user-global:source-access"
_REUSE_ACTOR = "principal:project-agent"


def _reuse_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _reuse_read(root, relative):
    path = root / relative
    if not _effect_exists(root, path):
        return None
    content = _read_exact_effect(root, path)
    if len(content) > 65536:
        raise ContractValidationError("reuse registration document exceeds limit")
    return content.decode("utf-8")


def _reuse_roots(project_workspace, global_workspace):
    # Inspect the supplied spelling before resolve can erase a junction or a
    # linked ancestor. This boundary is shared by preview, apply and recovery.
    supplied = [Path(item).absolute() for item in (project_workspace, global_workspace)]
    for root in (*supplied, supplied[0] / "project", supplied[1] / "global"):
        if any(_is_reparse_path(part) for part in (root, *root.parents)):
            raise ContractValidationError("reuse workspace path crosses a link")
    project, target = (_validated_root(item) for item in supplied)
    if project.is_relative_to(target) or target.is_relative_to(project):
        raise ContractValidationError("reuse workspaces must be separate")
    _validated_root(project / "project")
    _validated_root(target / "global")
    return project, target


def _reuse_project_state(raw, *, linked=False):
    state = json.loads(raw)
    fields = {"schema", "authority_id", "roots", "runtime_sha256"}
    if linked:
        fields.add("global_contribution")
    if (not isinstance(state, dict) or set(state) != fields
            or state["schema"] != (_LINKED_PROJECT_SCHEMA if linked else _PROJECT_SCHEMA)
            or state["roots"] != {"project": "project"}
            or not isinstance(state["authority_id"], str)
            or not re.fullmatch(r"project:[a-z0-9]+(?:-[a-z0-9]+)*", state["authority_id"])
            or len(state["authority_id"]) > 88
            or not isinstance(state["runtime_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", state["runtime_sha256"])):
        raise ContractValidationError("invalid Project reuse binding")
    return state


def _reuse_plan(project, target, before):
    """Reconstruct the only admitted delta; journals never provide write paths."""
    if not isinstance(before, dict) or set(before) != {"project_state", "global_state", "project_authority", "global_authority"} or not all(isinstance(v, str) and len(v.encode("utf-8")) <= 65536 for v in before.values()):
        raise ContractValidationError("invalid reuse registration prior state")
    state = _reuse_project_state(before["project_state"])
    global_state = json.loads(before["global_state"])
    global_fields = {"schema", "roots", "source_root", "source_id", "source_snapshot_sha256", "runtime_sha256"}
    source_free = isinstance(global_state, dict) and global_state.get("schema") == "owledge.private-knowledge-workspace/3"
    source_free_valid = (source_free and set(global_state) == {"schema", "roots", "runtime_sha256", "imports"}
        and global_state.get("roots") == {"user-global": "global"}
        and isinstance(global_state.get("runtime_sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", global_state["runtime_sha256"])
        and isinstance(global_state.get("imports"), list) and len(global_state["imports"]) <= 64)
    legacy_valid = (isinstance(global_state, dict) and global_state.get("schema") in {
            "owledge.private-knowledge-workspace/1", "owledge.private-knowledge-workspace/2"}
            and set(global_state) == global_fields | ({"imports"} if global_state["schema"].endswith("/2") else set())
            and isinstance(global_state.get("roots"), dict)
            and set(global_state["roots"]) == {"user-global", "source"}
            and global_state["roots"].get("user-global") == "global"
            and isinstance(global_state["roots"].get("source"), str)
            and re.fullmatch(r"sources/[a-zA-Z0-9_-]+", global_state["roots"]["source"])
            and all(isinstance(global_state[key], str) and global_state[key] for key in global_fields - {"schema", "roots"})
            and ("imports" not in global_state or isinstance(global_state["imports"], list) and 1 <= len(global_state["imports"]) <= 64))
    if not (source_free_valid or legacy_valid):
        raise ContractValidationError("reuse target must be a Knowledge workspace")
    for key, identity in (("project_authority", state["authority_id"]), ("global_authority", _REUSE_GLOBAL)):
        authority = parse_managed_markdown(".owledge/authority.md", before[key])
        if (authority.metadata.get("schema") != "owledge.authority-unit/1" or authority.authority_id != identity
                or authority.metadata.get("mode") != "read_write"):
            raise ContractValidationError("writable authority binding is required on both sides")
    fields, body = parse_markdown_frontmatter(before["global_authority"])
    grants = fields["actor_grants"].get(_REUSE_ACTOR, [])
    if grants not in ([], ["contribute"]):
        raise ContractValidationError("Project actor already has broader Global grants")
    seed = _reuse_json({"project": str(project), "global": str(target), "authority_id": state["authority_id"]})
    suffix = sha256(seed.encode("utf-8")).hexdigest()[:24]
    link_id = "link:project-global-contribute-" + suffix
    receipt_id = "receipt:project-global-link-" + suffix
    binding = {"workspace": str(target), "authority_id": _REUSE_GLOBAL, "source_link_id": link_id, "receipt_id": receipt_id}
    state.update(schema=_LINKED_PROJECT_SCHEMA, global_contribution=binding)
    fields["actor_grants"][_REUSE_ACTOR] = ["contribute"]
    fields["document_version"] += 1
    fields["revision"] = "contribution-registration-" + suffix
    fields["policy_revision"] = "policy-contribution-registration-" + suffix
    render = lambda metadata, body: "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items()) + "\n---\n" + body
    link = {"schema": "owledge.knowledge-source-link/1", "document_version": 1,
        "artifact_id": link_id, "source_link_id": link_id, "authority_id": state["authority_id"],
        "revision": "contribution-registration-1", "lifecycle": "accepted", "processing_layer": "condensed",
        "source_trust": "internal", "linked_authority_id": _REUSE_GLOBAL, "grants": ["contribute"]}
    receipt = {"schema": "owledge.private-project-reuse-receipt/1", "receipt_id": receipt_id,
        "authority_id": state["authority_id"], "binding": binding, "approved_by": "principal:local-owner",
        "outcome": "contribution_link_registered"}
    return {"project_state": _reuse_json(state), "global_authority": render(fields, body),
            "link": render(link, "\n# Contribution-only Global link\n"), "receipt": _reuse_json(receipt)}


def relocate_fixed_project_global_pair(contents: Mapping[str, bytes], *, old_project: Path,
                                       old_global: Path, new_project: Path,
                                       new_global: Path) -> dict[str, object]:
    """Reissue only the current path-bound controls of one archived linked pair.

    This is a pure bounded plan over already verified archive bytes. Historical
    receipts, references, Feed records and preserved originals are not rewritten.
    """
    keys = {"state": "Project/workspace.json",
            "project_authority": "Project/project/.owledge/authority.md",
            "global_authority": "Global/global/.owledge/authority.md",
            "link": "Project/project/.owledge/global-contribution-link.md",
            "receipt": "Project/.owledge/project-reuse-receipt.json"}
    if any(key not in contents or len(contents[key]) > 1_048_576 for key in keys.values()):
        raise ContractValidationError("paired archive is missing bounded current controls")
    old_project, old_global = Path(old_project).absolute(), Path(old_global).absolute()
    new_project, new_global = Path(new_project).absolute(), Path(new_global).absolute()
    if (new_project == old_project or new_global == old_global
            or new_project.parent != new_global.parent
            or new_project.name != "Project" or new_global.name != "Global"):
        raise ContractValidationError("paired restore requires fixed new Project/Global children")
    state = _reuse_project_state(contents[keys["state"]].decode("utf-8"), linked=True)
    if state["global_contribution"]["workspace"] != str(old_global):
        raise ContractValidationError("archived Project Global target differs")
    project_id = state["authority_id"]
    old_suffix = sha256(_reuse_json({"project": str(old_project), "global": str(old_global),
                                     "authority_id": project_id}).encode()).hexdigest()[:24]
    old_link_id = "link:project-global-contribute-" + old_suffix
    old_receipt_id = "receipt:project-global-link-" + old_suffix
    old_binding = {"workspace": str(old_global), "authority_id": _REUSE_GLOBAL,
                   "source_link_id": old_link_id, "receipt_id": old_receipt_id}
    if state["global_contribution"] != old_binding:
        raise ContractValidationError("archived Project registration is not exact")
    receipt = json.loads(contents[keys["receipt"]])
    if receipt != {"schema": "owledge.private-project-reuse-receipt/1", "receipt_id": old_receipt_id,
                   "authority_id": project_id, "binding": old_binding,
                   "approved_by": "principal:local-owner", "outcome": "contribution_link_registered"}:
        raise ContractValidationError("archived pair registration receipt differs")
    link = parse_managed_markdown(keys["link"], contents[keys["link"]].decode("utf-8"),
                                  encoded_document=contents[keys["link"]])
    if (link.artifact_id != old_link_id or link.authority_id != project_id
            or link.metadata.get("source_link_id") != old_link_id
            or link.metadata.get("linked_authority_id") != _REUSE_GLOBAL
            or link.metadata.get("grants") != ["contribute"]):
        raise ContractValidationError("archived Project contribution link differs")
    project_authority = parse_managed_markdown(keys["project_authority"],
        contents[keys["project_authority"]].decode("utf-8"),
        encoded_document=contents[keys["project_authority"]])
    global_authority = parse_managed_markdown(keys["global_authority"],
        contents[keys["global_authority"]].decode("utf-8"),
        encoded_document=contents[keys["global_authority"]])
    if (project_authority.authority_id != project_id or global_authority.authority_id != _REUSE_GLOBAL
            or global_authority.metadata.get("actor_grants", {}).get(_REUSE_ACTOR) != ["contribute"]):
        raise ContractValidationError("archived pair authority controls differ")
    new_suffix = sha256(_reuse_json({"project": str(new_project), "global": str(new_global),
                                     "authority_id": project_id}).encode()).hexdigest()[:24]
    new_link_id = "link:project-global-contribute-" + new_suffix
    new_receipt_id = "receipt:project-global-link-" + new_suffix
    new_binding = {"workspace": str(new_global), "authority_id": _REUSE_GLOBAL,
                   "source_link_id": new_link_id, "receipt_id": new_receipt_id}
    changes: dict[str, bytes] = {}
    state["global_contribution"] = new_binding
    changes[keys["state"]] = _reuse_json(state).encode("utf-8")
    link_fields = dict(link.metadata)
    link_fields.update(artifact_id=new_link_id, source_link_id=new_link_id,
                       revision="contribution-registration-" + new_suffix)
    changes[keys["link"]] = _render_metadata_document(link_fields, link.body).encode("utf-8")
    receipt["receipt_id"], receipt["binding"] = new_receipt_id, new_binding
    changes[keys["receipt"]] = _reuse_json(receipt).encode("utf-8")

    project_fields = dict(project_authority.metadata)
    global_fields = dict(global_authority.metadata)
    project_grants = project_fields.get("actor_grants")
    global_grants = global_fields.get("actor_grants")
    project_readers = project_fields.get("named_global_readers", {})
    global_readers = global_fields.get("named_project_readers", {})
    targets = global_fields.get("project_read_targets", {})
    concepts = global_fields.get("project_concepts", {})
    if not all(isinstance(item, dict) for item in (project_grants, global_grants,
                                                   project_readers, global_readers, targets, concepts)):
        raise ContractValidationError("archived pair reader or Concept registry is invalid")
    if any(not isinstance(entry, dict) or not isinstance(entry.get("readers"), dict)
           for entry in targets.values()):
        raise ContractValidationError("archived Project reader target is invalid")
    for principal, binding in project_readers.items():
        if (not isinstance(principal, str) or not isinstance(binding, dict)
                or binding.get("project_workspace") != str(old_project)
                or binding.get("global_workspace") != str(old_global)
                or binding.get("contribution_link_id") != old_link_id
                or binding.get("registration_receipt_id") != old_receipt_id):
            raise ContractValidationError("archived reverse reader binding differs")
    for principal, binding in global_readers.items():
        if not isinstance(principal, str) or not isinstance(binding, dict) or set(binding) != {
                "project_workspace", "project_authority_id", "connection", "principal_id",
                "contribution_link_id", "registration_receipt_id", "profile_generation"}:
            raise ContractValidationError("archived Global reader binding differs")
        bound_project = binding["project_workspace"]
        bound_id = binding["project_authority_id"]
        connection = binding["connection"]
        if (not isinstance(bound_project, str) or not Path(bound_project).is_absolute()
                or not isinstance(bound_id, str) or not re.fullmatch(r"project:[a-z0-9]+(?:-[a-z0-9]+)*", bound_id)
                or not isinstance(connection, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", connection)
                or binding["principal_id"] != principal
                or local_connection_principal(bound_id, connection) != principal
                or not isinstance(binding["profile_generation"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", binding["profile_generation"])):
            raise ContractValidationError("archived Global reader binding differs")
        bound_suffix = sha256(_reuse_json({"project": bound_project, "global": str(old_global),
                                          "authority_id": bound_id}).encode()).hexdigest()[:24]
        if (binding["contribution_link_id"] != "link:project-global-contribute-" + bound_suffix
                or binding["registration_receipt_id"] != "receipt:project-global-link-" + bound_suffix):
            raise ContractValidationError("archived Global reader binding differs")
        if bound_id == project_id and bound_project != str(old_project):
            raise ContractValidationError("archived selected Project reader path differs")
    suspended = sorted(set(project_readers) | set(global_readers) |
        {principal for entry in targets.values() if isinstance(entry, dict)
         for principal in entry.get("readers", {})})
    for principal in project_readers:
        if project_grants.get(principal) != ["retrieve"]:
            raise ContractValidationError("archived reverse reader grant differs")
        project_grants.pop(principal)
    for principal in global_readers:
        rights = global_grants.get(principal, [])
        if not isinstance(rights, list) or "retrieve" not in rights:
            raise ContractValidationError("archived Global reader grant differs")
        kept = sorted(set(rights) - {"retrieve"})
        if kept:
            global_grants[principal] = kept
        else:
            global_grants.pop(principal)
    project_fields["named_global_readers"] = {}
    global_fields["named_project_readers"] = {}
    global_fields["project_read_targets"] = {}
    old_concept = concepts.get(project_id)
    if old_concept is not None:
        if (not isinstance(old_concept, dict) or old_concept.get("project_workspace") != str(old_project)
                or old_concept.get("project_link_id") != old_link_id):
            raise ContractValidationError("archived Project Concept path differs")
        concept = dict(old_concept)
        version = concept.get("document_version")
        if type(version) is not int or not 1 <= version <= 1024:
            raise ContractValidationError("Project Concept revision is invalid")
        # The source designation did not change. Reissuing only its private path
        # keeps existing Essence provenance current when its live source is current.
        concept.update(project_workspace=str(new_project), project_link_id=new_link_id)
        global_fields["project_concepts"] = {project_id: concept}
    else:
        global_fields["project_concepts"] = {}
    for fields, authority, key in ((project_fields, project_authority, keys["project_authority"]),
                                   (global_fields, global_authority, keys["global_authority"])):
        version = fields.get("document_version")
        if type(version) is not int or version < 1:
            raise ContractValidationError("archived pair authority version is invalid")
        fields.update(document_version=version + 1,
                      revision="paired-restore-" + new_suffix,
                      policy_revision="policy-paired-restore-" + new_suffix)
        rendered = _render_metadata_document(fields, authority.body).encode("utf-8")
        if len(rendered) > 1_048_576:
            raise ContractValidationError("paired restore authority exceeds control budget")
        changes[key] = rendered
    return {"changes": changes, "old_project": str(old_project), "old_global": str(old_global),
            "new_project": str(new_project), "new_global": str(new_global),
            "project_authority_id": project_id,
            "source_link_id": new_link_id, "receipt_id": new_receipt_id,
            "concept_reissued": old_concept is not None,
            "suspended_readers": suspended,
            "external_projects_unavailable": sorted((set(concepts) | set(targets) |
                {entry["project_authority_id"] for entry in global_readers.values()}) - {project_id})}


def validate_project_reuse_binding(project_workspace, state):
    """Validate a saved one-way binding without reading Global knowledge bodies."""
    project = Path(project_workspace).absolute()
    _reuse_project_state(_reuse_json(state), linked=True)
    binding = state["global_contribution"]
    if (not isinstance(binding, dict) or set(binding) != {"workspace", "authority_id", "source_link_id", "receipt_id"}
            or not all(isinstance(v, str) for v in binding.values()) or binding["authority_id"] != _REUSE_GLOBAL
            or not Path(binding["workspace"]).is_absolute()):
        raise ContractValidationError("invalid contribution-only target")
    project, target = _reuse_roots(project, binding["workspace"])
    for root in (project, target):
        if _effect_exists(root, root / _REUSE_PENDING):
            raise ContractValidationError("Project reuse registration requires local Owner recovery")
    receipt_raw = _reuse_read(project, _REUSE_RECEIPT)
    if receipt_raw is None:
        raise ContractValidationError("Project reuse registration receipt is missing")
    receipt = json.loads(receipt_raw)
    if receipt != {"schema": "owledge.private-project-reuse-receipt/1", "receipt_id": binding["receipt_id"],
            "authority_id": state["authority_id"], "binding": binding, "approved_by": "principal:local-owner",
            "outcome": "contribution_link_registered"}:
        raise ContractValidationError("Project reuse registration receipt does not match")
    suffix = sha256(_reuse_json({"project": str(project), "global": str(target), "authority_id": state["authority_id"]}).encode("utf-8")).hexdigest()[:24]
    if binding["source_link_id"] != "link:project-global-contribute-" + suffix or binding["receipt_id"] != "receipt:project-global-link-" + suffix:
        raise ContractValidationError("Project reuse identity does not match")
    link_raw = _reuse_read(project, _REUSE_LINK)
    if link_raw is None:
        raise ContractValidationError("Project contribution link is missing")
    link = parse_managed_markdown(".owledge/global-contribution-link.md", link_raw)
    if (link.authority_id != state["authority_id"] or link.artifact_id != binding["source_link_id"]
            or link.metadata.get("source_link_id") != binding["source_link_id"]
            or link.metadata.get("schema") != "owledge.knowledge-source-link/1"
            or link.metadata.get("lifecycle") != "accepted" or link.metadata.get("linked_authority_id") != _REUSE_GLOBAL
            or link.metadata.get("grants") != ["contribute"]):
        raise ContractValidationError("Project contribution link is invalid")
    global_authority = bootstrap_authority(target / "global", _REUSE_GLOBAL)
    if (global_authority.metadata.get("mode") != "read_write"
            or global_authority.metadata.get("actor_grants", {}).get(_REUSE_ACTOR) != ["contribute"]):
        raise ContractValidationError("Global contribution grant changed")
    return target


def change_named_contribution_grant(project_workspace: Path, *, name: str, action: str,
                                    expected_sha256: str | None, apply: bool,
                                    check_owner: Callable[[ManagedMarkdown, ManagedMarkdown], None],
                                    check_profile: Callable[[ManagedMarkdown, dict, str], bool]) -> dict[str, object]:
    """CAS one named principal's contribution grant through the saved bridge."""
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", name) or action not in {"grant", "revoke"}:
        raise ContractValidationError("named contribution action is invalid")
    project = _validated_root(Path(project_workspace))

    def current() -> tuple[dict[str, object], Path, str]:
        state_raw = _reuse_read(project, "workspace.json")
        state = _reuse_project_state(state_raw, linked=True)
        target = validate_project_reuse_binding(project, state)
        project_root, global_root = project / "project", target / "global"
        project_authority = bootstrap_authority(project_root, state["authority_id"])
        global_authority = bootstrap_authority(global_root, _REUSE_GLOBAL)
        check_owner(project_authority, global_authority)
        profiles = project_authority.metadata.get("connections")
        profile = profiles.get(name) if isinstance(profiles, dict) else None
        principal = local_connection_principal(state["authority_id"], name)
        if (not isinstance(profile, dict) or profile.get("principal_id") != principal
                or profile.get("authority_id") != state["authority_id"]
                or action == "grant" and (profile.get("role") != "contributor"
                    or profile.get("source_link_id") is not None)
                or profile.get("status") not in ({"active"} if action == "grant" else {"active", "revoked"})
                or action == "grant" and not check_profile(project_authority, profile, principal)):
            raise ContractValidationError("known unbound Project Contributor is required")
        grants = global_authority.metadata.get("actor_grants")
        if not isinstance(grants, dict) or grants.get(principal, []) not in (
                [], ["contribute"], ["retrieve"], ["contribute", "retrieve"]):
            raise ContractValidationError("named Global principal has other rights")
        present = "contribute" in grants.get(principal, [])
        if (action == "grant") == present:
            raise ContractValidationError("named contribution grant is already in that state")
        binding = state["global_contribution"]
        link_raw = _reuse_read(project, _REUSE_LINK)
        digest = sha256(json.dumps([sha256(state_raw.encode()).hexdigest(), project_authority.content_sha256,
            global_authority.content_sha256, sha256(link_raw.encode()).hexdigest(), binding, name, action],
            ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        fields = dict(global_authority.metadata)
        updated = dict(grants)
        capabilities = set(grants.get(principal, []))
        capabilities.add("contribute") if action == "grant" else capabilities.discard("contribute")
        if capabilities:
            updated[principal] = sorted(capabilities)
        else:
            updated.pop(principal, None)
        version = fields.get("document_version")
        if type(version) is not int or version < 1:
            raise ContractValidationError("Global authority version is invalid")
        fields.update(actor_grants=updated, document_version=version + 1,
            revision="named-contribution-" + digest[:24],
            policy_revision="policy-named-contribution-" + digest[:24],
            last_named_contribution_change={"approved_by": "principal:local-owner", "action": action,
                "name": name, "principal_id": principal, "project_authority_id": state["authority_id"],
                "source_link_id": binding["source_link_id"], "prior_sha256": global_authority.content_sha256})
        document = _render_metadata_document(fields, global_authority.body)
        if len(document.encode("utf-8")) > 1_048_576:
            raise ContractValidationError("named contribution exceeds authority document budget")
        return ({"status": "ready" if apply else "preview", "action": action, "connection": name,
                 "principal_id": principal, "project_authority_id": state["authority_id"],
                 "target_authority_id": _REUSE_GLOBAL, "source_link_id": binding["source_link_id"],
                 "expected_sha256": digest, "granted_after": action == "grant"}, global_root, document)

    if not apply:
        return current()[0]
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ContractValidationError("named contribution grant needs exact preview hash")
    state = _reuse_project_state(_reuse_read(project, "workspace.json"), linked=True)
    target = _reuse_roots(project, state["global_contribution"]["workspace"])[1]
    with authority_write_locks((project / "project", target / "global")):
        result, global_root, document = current()
        if global_root.resolve() != (target / "global").resolve():
            raise ContractValidationError("Global contribution target changed before locked apply")
        if result["expected_sha256"] != expected_sha256:
            raise ContractValidationError("Project or Global contribution binding changed after preview")
        _write_exact_atomic(global_root, global_root / ".owledge/authority.md", document)
        return result


def change_named_global_reader(project_workspace: Path, *, name: str, action: str,
                               expected_sha256: str | None, apply: bool,
                               check_owner: Callable[[ManagedMarkdown, ManagedMarkdown], None],
                               check_profile: Callable[[ManagedMarkdown, dict, str], bool]) -> dict[str, object]:
    """CAS one separate Project-to-Global reviewed reader assignment."""
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", name) or action not in {"grant", "revoke"}:
        raise ContractValidationError("named Global reader action is invalid")
    project = _validated_root(Path(project_workspace))

    def current() -> tuple[dict[str, object], Path, str]:
        state_raw = _reuse_read(project, "workspace.json")
        state = _reuse_project_state(state_raw, linked=True)
        target = validate_project_reuse_binding(project, state)
        project_root, global_root = project / "project", target / "global"
        project_authority = bootstrap_authority(project_root, state["authority_id"])
        global_authority = bootstrap_authority(global_root, _REUSE_GLOBAL)
        check_owner(project_authority, global_authority)
        profiles = project_authority.metadata.get("connections")
        profile = profiles.get(name) if isinstance(profiles, dict) else None
        principal = local_connection_principal(state["authority_id"], name)
        if (not isinstance(profile, dict) or profile.get("principal_id") != principal
                or profile.get("authority_id") != state["authority_id"]
                or profile.get("status") not in ({"active"} if action == "grant" else {"active", "revoked"})
                or action == "grant" and (profile.get("role") != "contributor"
                    or profile.get("source_link_id") is not None
                    or not check_profile(project_authority, profile, principal))):
            raise ContractValidationError("known unbound Project Contributor is required")
        generations = project_authority.metadata.get("connection_generations", {})
        if not isinstance(generations, dict):
            raise ContractValidationError("Project connection generation registry is invalid")
        generation = generations.get(name, project_authority.content_sha256)
        if not isinstance(generation, str) or not re.fullmatch(r"[0-9a-f]{64}", generation):
            raise ContractValidationError("Project connection generation is invalid")
        bridges = global_authority.metadata.get("named_project_readers", {})
        grants = global_authority.metadata.get("actor_grants")
        if (not isinstance(bridges, dict) or not isinstance(grants, dict)
                or grants.get(principal, []) not in
                    ([], ["contribute"], ["retrieve"], ["contribute", "retrieve"])):
            raise ContractValidationError("named Global reader controls are invalid")
        prior = bridges.get(principal)
        has_retrieve = "retrieve" in grants.get(principal, [])
        if (prior is None) != (not has_retrieve):
            raise ContractValidationError("named Global reader binding and grant disagree")
        binding = state["global_contribution"]
        expected_prior = {"project_workspace": str(project), "project_authority_id": state["authority_id"],
                          "connection": name, "principal_id": principal,
                          "contribution_link_id": binding["source_link_id"],
                          "registration_receipt_id": binding["receipt_id"]}
        if has_retrieve and (not isinstance(prior, dict)
                             or set(prior) != set(expected_prior) | {"profile_generation"}
                             or any(prior.get(key) != value for key, value in expected_prior.items())
                             or not isinstance(prior.get("profile_generation"), str)
                             or not re.fullmatch(r"[0-9a-f]{64}", prior["profile_generation"])):
            raise ContractValidationError("retained Global reader binding is invalid")
        if action == "revoke" and not has_retrieve or action == "grant" and has_retrieve and prior["profile_generation"] == generation:
            raise ContractValidationError("named Global reader is already in that state")
        link_raw = _reuse_read(project, _REUSE_LINK)
        digest = sha256(json.dumps([sha256(state_raw.encode()).hexdigest(), project_authority.content_sha256,
            global_authority.content_sha256, sha256(link_raw.encode()).hexdigest(), binding, generation,
            name, action], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        fields = dict(global_authority.metadata)
        updated_grants, updated_bridges = dict(grants), dict(bridges)
        capabilities = set(grants.get(principal, []))
        if action == "grant":
            capabilities.add("retrieve")
            updated_bridges[principal] = {**expected_prior, "profile_generation": generation}
        else:
            capabilities.discard("retrieve")
            updated_bridges.pop(principal)
        if capabilities:
            updated_grants[principal] = sorted(capabilities)
        else:
            updated_grants.pop(principal, None)
        version = fields.get("document_version")
        if type(version) is not int or version < 1:
            raise ContractValidationError("Global authority version is invalid")
        fields.update(actor_grants=updated_grants, named_project_readers=updated_bridges,
            document_version=version + 1, revision="named-global-reader-" + digest[:24],
            policy_revision="policy-named-global-reader-" + digest[:24],
            last_named_global_reader_change={"approved_by": "principal:local-owner", "action": action,
                "connection": name, "principal_id": principal, "project_authority_id": state["authority_id"],
                "prior_sha256": global_authority.content_sha256})
        document = _render_metadata_document(fields, global_authority.body)
        if len(document.encode("utf-8")) > 1_048_576:
            raise ContractValidationError("named Global reader exceeds authority document budget")
        return ({"status": "ready" if apply else "preview", "action": action, "connection": name,
                 "principal_id": principal, "project_authority_id": state["authority_id"],
                 "target_authority_id": _REUSE_GLOBAL, "expected_sha256": digest,
                 "granted_after": action == "grant"}, global_root, document)

    if not apply:
        return current()[0]
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ContractValidationError("named Global reader requires exact preview hash")
    state = _reuse_project_state(_reuse_read(project, "workspace.json"), linked=True)
    target = _reuse_roots(project, state["global_contribution"]["workspace"])[1]
    with authority_write_locks((project / "project", target / "global")):
        result, global_root, document = current()
        if global_root.resolve() != (target / "global").resolve():
            raise ContractValidationError("Global reader target changed before locked apply")
        if result["expected_sha256"] != expected_sha256:
            raise ContractValidationError("Project or Global reader binding changed after preview")
        _write_exact_atomic(global_root, global_root / ".owledge/authority.md", document)
        return result


_PROJECT_READER_PENDING = ".owledge/project-reader-grant.json"


def project_reader_pending(root: Path) -> bool:
    return _effect_exists(Path(root), Path(root) / _PROJECT_READER_PENDING)


def _project_reader_journal(root: Path) -> str | None:
    path = root / _PROJECT_READER_PENDING
    return _read_exact_effect(root, path, max_bytes=4_300_000).decode("utf-8") if _effect_exists(root, path) else None


def _project_reader_plan(global_workspace: Path, project_workspace: Path, project_id: str,
                         name: str, action: str, before: dict[str, str],
                         *, check_owner, check_profile) -> tuple[dict, dict[str, str]]:
    """Reconstruct the only two authority deltas from exact preimages."""
    global_workspace = _validated_root(global_workspace)
    project, target = _reuse_roots(project_workspace, global_workspace)
    if target != global_workspace or not re.fullmatch(r"project:[a-z0-9]+(?:-[a-z0-9]+)*", project_id):
        raise ContractValidationError("Project reader target is invalid")
    state = _reuse_project_state(_reuse_read(project, "workspace.json"), linked=True)
    if state["authority_id"] != project_id or validate_project_reuse_binding(project, state) != target:
        raise ContractValidationError("Project reader reciprocal registration changed")
    if (not isinstance(before, dict) or set(before) != {"global_authority", "project_authority"}
            or any(not isinstance(value, str) or len(value.encode("utf-8")) > 1_048_576 for value in before.values())):
        raise ContractValidationError("Project reader preimage is invalid")
    global_authority = parse_managed_markdown(".owledge/authority.md", before["global_authority"])
    project_authority = parse_managed_markdown(".owledge/authority.md", before["project_authority"])
    if (global_authority.authority_id != _REUSE_GLOBAL or project_authority.authority_id != project_id
            or global_authority.metadata.get("schema") != "owledge.authority-unit/1"
            or project_authority.metadata.get("schema") != "owledge.authority-unit/1"):
        raise ContractValidationError("Project reader authority preimage is invalid")
    check_owner(global_authority, project_authority)
    profiles = global_authority.metadata.get("connections")
    profile = profiles.get(name) if isinstance(profiles, dict) else None
    principal = local_connection_principal(_REUSE_GLOBAL, name)
    if (not isinstance(profile, dict) or profile.get("principal_id") != principal
            or profile.get("authority_id") != _REUSE_GLOBAL
            or profile.get("status") not in ({"active"} if action == "grant" else {"active", "revoked"})
            or action == "grant" and (profile.get("role") != "contributor"
                or profile.get("source_link_id") is not None
                or not check_profile(global_authority, profile, principal))):
        raise ContractValidationError("known unbound Global Contributor is required")
    generations = global_authority.metadata.get("connection_generations", {})
    if not isinstance(generations, dict):
        raise ContractValidationError("Global profile generations are invalid")
    generation = generations.get(name, global_authority.content_sha256)
    if not isinstance(generation, str) or not re.fullmatch(r"[0-9a-f]{64}", generation):
        raise ContractValidationError("Global profile generation is invalid")
    targets = global_authority.metadata.get("project_read_targets", {})
    if not isinstance(targets, dict) or len(targets) > 32:
        raise ContractValidationError("Project reader registry is invalid")
    link = state["global_contribution"]
    target_base = {"project_workspace": str(project), "project_authority_id": project_id,
                   "global_workspace": str(target), "contribution_link_id": link["source_link_id"],
                   "registration_receipt_id": link["receipt_id"]}
    prior_target = targets.get(project_id)
    if prior_target is not None and (not isinstance(prior_target, dict)
            or set(prior_target) != set(target_base) | {"readers"}
            or any(prior_target.get(key) != value for key, value in target_base.items())
            or not isinstance(prior_target.get("readers"), dict)):
        raise ContractValidationError("retained Project target changed")
    if prior_target is None and (action != "grant" or len(targets) >= 32):
        raise ContractValidationError("Project reader target is not registered")
    readers = dict(prior_target["readers"]) if prior_target else {}
    if len(readers) > 32 or action == "grant" and principal not in readers and len(readers) >= 32:
        raise ContractValidationError("Project reader limit exceeded")
    project_bindings = project_authority.metadata.get("named_global_readers", {})
    project_grants = project_authority.metadata.get("actor_grants")
    if not isinstance(project_bindings, dict) or not isinstance(project_grants, dict):
        raise ContractValidationError("Project reader controls are invalid")
    old_reader = readers.get(principal)
    old_project = project_bindings.get(principal)
    expected_reader = {"connection": name, "principal_id": principal, "profile_generation": generation}
    expected_project = {**target_base, "connection": name, "principal_id": principal,
                        "profile_generation": old_reader.get("profile_generation") if isinstance(old_reader, dict) else generation}
    if ((old_reader is None) != (old_project is None)
            or (old_reader is None) != (project_grants.get(principal, []) == [])
            or old_reader is not None and (not isinstance(old_reader, dict)
                or set(old_reader) != set(expected_reader)
                or old_reader.get("connection") != name or old_reader.get("principal_id") != principal
                or old_project != expected_project or project_grants.get(principal) != ["retrieve"])):
        raise ContractValidationError("Project reader assignments disagree")
    if action == "revoke" and old_reader is None or action == "grant" and old_reader == expected_reader:
        raise ContractValidationError("Project reader is already in that state")
    if action == "grant":
        readers[principal] = expected_reader
        project_bindings = {**project_bindings, principal: {**expected_project, "profile_generation": generation}}
        project_grants = {**project_grants, principal: ["retrieve"]}
    else:
        readers.pop(principal)
        project_bindings = {key: value for key, value in project_bindings.items() if key != principal}
        project_grants = {key: value for key, value in project_grants.items() if key != principal}
    updated_targets = {**targets, project_id: {**target_base, "readers": readers}}
    digest = sha256(json.dumps([sha256(before["global_authority"].encode()).hexdigest(),
        sha256(before["project_authority"].encode()).hexdigest(), target_base, name, action, generation],
        sort_keys=True).encode()).hexdigest()
    after = {}
    for side, authority, changes in (("global_authority", global_authority,
                                      {"project_read_targets": updated_targets}),
                                     ("project_authority", project_authority,
                                      {"named_global_readers": project_bindings, "actor_grants": project_grants})):
        fields = dict(authority.metadata)
        version = fields.get("document_version")
        if type(version) is not int or version < 1:
            raise ContractValidationError("Project reader authority version is invalid")
        fields.update(changes, document_version=version + 1,
            revision="project-reader-" + digest[:24], policy_revision="policy-project-reader-" + digest[:24],
            last_project_reader_change={"approved_by": "principal:local-owner", "action": action,
                                        "project_authority_id": project_id, "connection": name,
                                        "prior_sha256": authority.content_sha256})
        rendered = _render_metadata_document(fields, authority.body)
        if len(rendered.encode("utf-8")) > 1_048_576:
            raise ContractValidationError("Project reader authority document exceeds budget")
        after[side] = rendered
    return ({"status": "preview", "action": action, "project_authority_id": project_id,
             "project_workspace": str(project), "connection": name, "principal_id": principal,
             "expected_sha256": digest, "granted_after": action == "grant"}, after)


def _project_reader_authority_bytes(global_workspace: Path, project_workspace: Path) -> dict[str, str]:
    paths = ((global_workspace, global_workspace / "global/.owledge/authority.md", "global_authority"),
             (project_workspace, project_workspace / "project/.owledge/authority.md", "project_authority"))
    return {key: _read_exact_effect(root, path, max_bytes=1_048_576).decode("utf-8")
            for root, path, key in paths}


def _project_reader_workspace(global_workspace: Path, project_id: str,
                              project_workspace: Path | None) -> Path:
    if project_workspace is not None:
        project, target = _reuse_roots(project_workspace, global_workspace)
        if target != global_workspace:
            raise ContractValidationError("Project reader target changed")
        return project
    global_authority = bootstrap_authority(global_workspace / "global", _REUSE_GLOBAL)
    targets = global_authority.metadata.get("project_read_targets", {})
    target = targets.get(project_id) if isinstance(targets, dict) else None
    if not isinstance(target, dict) or not isinstance(target.get("project_workspace"), str):
        raise ContractValidationError("first Project reader grant needs exact Project workspace")
    project, checked_global = _reuse_roots(target["project_workspace"], global_workspace)
    if checked_global != global_workspace:
        raise ContractValidationError("registered Project target changed")
    return project


def recover_named_project_reader(global_workspace: Path, *, project_workspace: Path,
                                 project_id: str, name: str, action: str,
                                 check_owner, check_profile) -> dict[str, object]:
    """Explicit two-authority recovery; caller holds both workspace and authority locks."""
    target = _validated_root(global_workspace)
    project, checked_target = _reuse_roots(project_workspace, target)
    if checked_target != target:
        raise ContractValidationError("Project reader recovery target changed")
    copies = [_project_reader_journal(root) for root in (project, target)]
    present = [copy for copy in copies if copy is not None]
    if not present or any(copy != present[0] for copy in present):
        raise ContractValidationError("Project reader recovery journals are missing or mismatched")
    journal = json.loads(present[0])
    if (not isinstance(journal, dict) or set(journal) !=
            {"schema", "project_workspace", "global_workspace", "project_id", "connection", "action", "before"}
            or journal["schema"] != "owledge.private-project-reader-grant/1"
            or journal["project_workspace"] != str(project) or journal["global_workspace"] != str(target)
            or journal["project_id"] != project_id or journal["connection"] != name
            or journal["action"] != action):
        raise ContractValidationError("Project reader recovery request differs from journal")
    preview, after = _project_reader_plan(target, project, project_id, name, action,
        journal["before"], check_owner=check_owner, check_profile=check_profile)
    current = _project_reader_authority_bytes(target, project)
    if any(current[key] not in (journal["before"][key], after[key]) for key in after):
        raise ContractValidationError("Project reader recovery authority changed")
    for root, copy in zip((project, target), copies):
        if copy is None:
            _write_exact_atomic(root, root / _PROJECT_READER_PENDING, present[0])
    if current["project_authority"] != after["project_authority"]:
        _write_exact_atomic(project / "project", project / "project/.owledge/authority.md", after["project_authority"])
    if current["global_authority"] != after["global_authority"]:
        _write_exact_atomic(target / "global", target / "global/.owledge/authority.md", after["global_authority"])
    for root in (project, target):
        _unlink_effect(root, root / _PROJECT_READER_PENDING)
    return {**preview, "status": "ready", "recovered": True}


def change_named_project_reader(global_workspace: Path, *, project_id: str, name: str,
                                action: str, project_workspace: Path | None,
                                expected_sha256: str | None, apply: bool,
                                check_owner, check_profile) -> dict[str, object]:
    """Owner CAS for one named Global principal and one exact registered Project."""
    target = _validated_root(global_workspace)
    if (not re.fullmatch(r"project:[a-z0-9]+(?:-[a-z0-9]+)*", project_id)
            or not re.fullmatch(r"[a-z][a-z0-9-]{0,39}", name)
            or action not in {"grant", "revoke"}):
        raise ContractValidationError("Project reader request is invalid")
    project = _project_reader_workspace(target, project_id, project_workspace)
    def current():
        if any(project_reader_pending(root) for root in (project, target)):
            raise ContractValidationError("Project reader recovery is required")
        before = _project_reader_authority_bytes(target, project)
        preview, after = _project_reader_plan(target, project, project_id, name, action,
            before, check_owner=check_owner, check_profile=check_profile)
        return preview, before, after
    if not apply:
        return current()[0]
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ContractValidationError("Project reader apply requires exact preview hash")
    with authority_write_locks((project, project / "project", target, target / "global")):
        preview, before, after = current()
        if preview["expected_sha256"] != expected_sha256 or preview["project_workspace"] != str(project):
            raise ContractValidationError("Project reader preview is stale")
        journal = _reuse_json({"schema": "owledge.private-project-reader-grant/1",
            "project_workspace": str(project), "global_workspace": str(target),
            "project_id": project_id, "connection": name, "action": action, "before": before})
        if len(journal.encode("utf-8")) > 4_300_000:
            raise ContractValidationError("Project reader journal exceeds bounded budget")
        # Global marker first: linked Project writers can inspect it even before
        # their local copy appears after an interrupted first journal write.
        for root in (target, project):
            _write_exact_atomic(root, root / _PROJECT_READER_PENDING, journal)
        return recover_named_project_reader(target, project_workspace=project, project_id=project_id,
            name=name, action=action, check_owner=check_owner, check_profile=check_profile)


def prepare_project_reuse_registration(project_workspace, global_workspace, *, check_owner):
    project, target = _reuse_roots(project_workspace, global_workspace)
    for root in (project, target):
        for marker in (_REUSE_PENDING, ".owledge/source-registration.json"):
            if _effect_exists(root, root / marker):
                raise ContractValidationError("registration requires local Owner recovery")
    before = {"project_state": _reuse_read(project, "workspace.json"), "global_state": _reuse_read(target, "workspace.json"),
        "project_authority": _reuse_read(project, "project/.owledge/authority.md"),
        "global_authority": _reuse_read(target, "global/.owledge/authority.md")}
    state = json.loads(before["project_state"] or "null")
    if not isinstance(state, dict) or not isinstance(state.get("authority_id"), str):
        raise ContractValidationError("Project authority identity is missing")
    check_owner(state["authority_id"])
    if isinstance(state, dict) and state.get("schema") == _LINKED_PROJECT_SCHEMA:
        if validate_project_reuse_binding(project, state) != target:
            raise ContractValidationError("Project is already linked to another Global workspace")
        return {"before": before, "already_current": True, "receipt_id": state["global_contribution"]["receipt_id"],
            "source_link_id": state["global_contribution"]["source_link_id"], "authority_id": state["authority_id"]}
    after = _reuse_plan(project, target, before)
    if _reuse_read(project, _REUSE_LINK) is not None or _reuse_read(project, _REUSE_RECEIPT) is not None:
        raise ContractValidationError("Project reuse registration destination already exists")
    binding = json.loads(after["project_state"])["global_contribution"]
    return {"before": before, "after": after, "already_current": False, "receipt_id": binding["receipt_id"],
        "source_link_id": binding["source_link_id"], "authority_id": state["authority_id"]}


def apply_project_reuse_registration(project_workspace, global_workspace, pending, *, check_owner):
    project, target = _reuse_roots(project_workspace, global_workspace)
    with authority_write_locks((project, project / "project", target, target / "global")):
        current = prepare_project_reuse_registration(project, target, check_owner=check_owner)
        if current != pending:
            raise ContractValidationError("reuse registration changed after preview")
        if current["already_current"]:
            return current["receipt_id"]
        journal = _reuse_json({"schema": "owledge.private-project-reuse-registration/1", "project": str(project),
            "global": str(target), "before": current["before"]})
        if len(journal.encode("utf-8")) > 65536:
            raise ContractValidationError("reuse registration journal exceeds limit")
        # No configuration changes until both sides carry the same blocking journal.
        for root in (project, target):
            _write_exact_atomic(root, root / _REUSE_PENDING, journal)
        return recover_project_reuse_registration(project, target, check_owner=check_owner)


def recover_project_reuse_registration(project_workspace, global_workspace, *, check_owner):
    """Caller holds both workspace+authority locks; explicit roots never come from a journal."""
    project, target = _reuse_roots(project_workspace, global_workspace)
    copies = [_reuse_read(root, _REUSE_PENDING) for root in (project, target)]
    present = [copy for copy in copies if copy is not None]
    if not present or any(copy != present[0] for copy in present):
        raise ContractValidationError("reuse recovery journal is missing or mismatched")
    journal = json.loads(present[0])
    if (not isinstance(journal, dict) or set(journal) != {"schema", "project", "global", "before"}
            or journal["schema"] != "owledge.private-project-reuse-registration/1"
            or journal["project"] != str(project) or journal["global"] != str(target)):
        raise ContractValidationError("invalid reuse registration journal")
    before = journal["before"]
    after = _reuse_plan(project, target, before)
    # Both current Owner grants must still authorize recovery, including partially applied policy.
    identity = json.loads(before["project_state"])["authority_id"]
    check_owner(identity)
    effects = [(project, "workspace.json", before["project_state"], after["project_state"]),
        (target, "global/.owledge/authority.md", before["global_authority"], after["global_authority"]),
        (project, _REUSE_LINK, None, after["link"]), (project, _REUSE_RECEIPT, None, after["receipt"])]
    if (_reuse_read(project, "project/.owledge/authority.md") != before["project_authority"]
            or _reuse_read(target, "workspace.json") != before["global_state"]):
        raise ContractValidationError("reuse registration authority or workspace changed")
    for root, relative, old, new in effects:
        if _reuse_read(root, relative) not in (old, new):
            raise ContractValidationError("reuse registration target changed")
    for root, copy in zip((project, target), copies):
        if copy is None:
            _write_exact_atomic(root, root / _REUSE_PENDING, present[0])
    for root, relative, old, new in effects:
        if _reuse_read(root, relative) != new:
            _write_exact_atomic(root, root / relative, new)
    for root in (project, target):
        _unlink_effect(root, root / _REUSE_PENDING)
    return json.loads(after["receipt"])["receipt_id"]


def prepare_source_registration(workspace: Path, snapshot: SourceSnapshot, principal_id: str, access: str | None = None):
    """Prepare a fixed additional-source binding, never an arbitrary config edit."""
    if access not in {None, "restricted", "shared"}:
        raise ContractValidationError("source access must be restricted or shared")
    selected_access = access or "restricted"
    source_access = {"access": selected_access, "principals": [principal_id] if selected_access == "restricted" else []}
    root = _validated_root(workspace)
    if _effect_exists(root, root / ".owledge/source-registration.json"):
        raise ContractValidationError("source registration requires local Owner recovery")
    source = snapshot.source_root.resolve(strict=True)
    if source.is_relative_to(root) or root.is_relative_to(source):
        raise ContractValidationError("source and workspace must be separate")
    before = _read_exact_effect(root, root / "workspace.json")
    state = json.loads(before)
    schemas = {"owledge.private-knowledge-workspace/1", "owledge.private-knowledge-workspace/2", "owledge.private-knowledge-workspace/3"}
    fields = {"schema", "roots", "source_root", "source_id", "source_snapshot_sha256", "runtime_sha256"}
    source_free = isinstance(state, dict) and state.get("schema") == "owledge.private-knowledge-workspace/3"
    expected_fields = ({"schema", "roots", "runtime_sha256", "imports"} if source_free
                       else fields | ({"imports"} if isinstance(state, dict) and state.get("schema") == "owledge.private-knowledge-workspace/2" else set()))
    if (not isinstance(state, dict) or state.get("schema") not in schemas or set(state) != expected_fields
            or source_free and state.get("roots") != {"user-global": "global"}):
        raise ContractValidationError("unsupported knowledge workspace binding")
    imports = state.get("imports", [])
    if not isinstance(imports, list) or len(imports) > 64:
        raise ContractValidationError("source binding limit reached or invalid")
    primary = None if source_free else {"source_id": state["source_id"], "source_root": state["source_root"],
               "snapshot_sha256": state["source_snapshot_sha256"], "root": state["roots"]["source"],
               "source_link_id": "link:source-access-originals"}
    for item in ([primary] if primary is not None else []) + imports:
        same_path = os.path.normcase(str(Path(item["source_root"]).absolute())) == os.path.normcase(str(source))
        if item["source_id"] == snapshot.source_id or same_path:
            if item["source_id"] != snapshot.source_id or not same_path:
                raise ContractValidationError("source path and identity disagree")
            link_path = ("global/.owledge/raw-link.md" if item is primary else
                         "global/.owledge/import-" + snapshot.source_id.removeprefix("source:") + ".md")
            existing_link, _ = parse_markdown_frontmatter(_read_exact_effect(root, root / link_path).decode("utf-8"))
            existing_access = existing_link.get("source_access")
            if access is not None and existing_access != source_access:
                raise ContractValidationError("source access change requires a separate reviewed operation")
            if item["snapshot_sha256"] == snapshot.snapshot_sha256:
                return {"snapshot": snapshot, "before": before, "preview": {"status": "preview", "already_current": True,
                    "source_link_id": item["source_link_id"], "source_access": existing_access}}
            if primary is not None and item is primary:
                validate_primary_snapshot(root, state)
                registry_target = root / "global/.owledge/progressive-retrieval.md"
                registry_before = _read_exact_effect(root, registry_target)
                link_path = "global/.owledge/raw-link.md"
                link_before = _read_exact_effect(root, root / link_path)
                target_name = source_snapshot_target_name(snapshot)
                revised_state = {**state, "roots": {**state["roots"], "source": "sources/" + target_name},
                                 "source_snapshot_sha256": snapshot.snapshot_sha256}
                workspace_document = json.dumps(revised_state, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
                changes = _source_revision_changes(root, primary, snapshot)
                return {"snapshot": snapshot, "before": before, "registry_before": registry_before,
                        "documents": {link_path: link_before.decode("utf-8"),
                                      "global/.owledge/progressive-retrieval.md": registry_before.decode("utf-8"),
                                      "workspace.json": workspace_document},
                        "preview": {"status": "preview", "already_current": False, "revision_of_source": True,
                                    "primary_source": True, "source_link_id": primary["source_link_id"],
                                    "source_access": existing_access,
                                    "old_snapshot_sha256": primary["snapshot_sha256"],
                                    "new_snapshot_sha256": snapshot.snapshot_sha256, "changes": changes,
                                    "message": "Exact changed primary folder snapshot; accepted knowledge remains unchanged until separate review."}}
            old_entry = item
            import_index = imports.index(item)
            validate_imported_snapshot(root, old_entry)
            registry_target = root / "global/.owledge/progressive-retrieval.md"
            registry_before = _read_exact_effect(root, registry_target)
            link_path = "global/.owledge/import-" + snapshot.source_id.removeprefix("source:") + ".md"
            link_before = _read_exact_effect(root, root / link_path)
            target_name = source_snapshot_target_name(snapshot)
            entry = {"source_id": snapshot.source_id, "source_root": old_entry["source_root"],
                     "snapshot_sha256": snapshot.snapshot_sha256, "root": "sources/" + target_name,
                     "source_link_id": old_entry["source_link_id"],
                     "operation_id": "op:import:" + snapshot.snapshot_sha256, "approved_by": principal_id,
                     **({"source_access": old_entry["source_access"]} if "source_access" in old_entry else {})}
            revised_imports = list(imports)
            revised_imports[import_index] = entry
            revised_state = {**state, "imports": revised_imports}
            workspace_document = json.dumps(revised_state, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
            if len(workspace_document.encode("utf-8")) > 65536:
                raise ContractValidationError("workspace binding exceeds read limit")
            changes = _source_revision_changes(root, old_entry, snapshot)
            return {"snapshot": snapshot, "before": before, "registry_before": registry_before,
                    "documents": {link_path: link_before.decode("utf-8"),
                                  "global/.owledge/progressive-retrieval.md": registry_before.decode("utf-8"),
                                  "workspace.json": workspace_document},
                    "preview": {"status": "preview", "already_current": False, "revision_of_source": True,
                                "source_link_id": old_entry["source_link_id"], "source_access": existing_access,
                                "old_snapshot_sha256": old_entry["snapshot_sha256"],
                                "new_snapshot_sha256": snapshot.snapshot_sha256, "changes": changes,
                                "message": "Exact changed folder snapshot; accepted knowledge remains unchanged until separate review."}}
    if len(imports) == 64:
        raise ContractValidationError("source binding limit reached")
    registry_target = root / "global/.owledge/progressive-retrieval.md"
    registry_before = _read_exact_effect(root, registry_target)
    metadata, body = parse_markdown_frontmatter(registry_before.decode("utf-8"))
    if metadata.get("schema") != "owledge.progressive-retrieval-registry/1" or metadata.get("authority_id") != "user-global:source-access":
        raise ContractValidationError("source registration registry is invalid")
    cases = metadata.get("coverage_cases")
    if source_free and not imports:
        if cases != {}:
            raise ContractValidationError("first source registration requires an empty registry")
        case = {"revision": "source-access-1", "lifecycle": "accepted",
                "required_evidence": ["raw_content"], "search_envelope": ["raw_keyword"],
                "source_links": {"raw_keyword": []}, "gap_admission": "disabled"}
        cases["coverage:source-access-originals"] = case
    else:
        case = cases.get("coverage:source-access-originals") if isinstance(cases, dict) else None
        if not isinstance(case, dict) or case.get("gap_admission") != "disabled" or case.get("search_envelope") != ["raw_keyword"]:
            raise ContractValidationError("source registration requires the raw-only disabled-Gap case")
    link = "link:import-" + snapshot.source_id.removeprefix("source:")
    target_name = source_snapshot_target_name(snapshot)
    link_path = "global/.owledge/import-" + snapshot.source_id.removeprefix("source:") + ".md"
    if _effect_exists(root, root / link_path):
        raise ContractValidationError("source link destination already exists")
    entry = {"source_id": snapshot.source_id, "source_root": str(source), "snapshot_sha256": snapshot.snapshot_sha256,
             "root": "sources/" + target_name, "source_link_id": link,
             "operation_id": "op:import:" + snapshot.snapshot_sha256, "approved_by": principal_id,
             "source_access": source_access}
    case["source_links"]["raw_keyword"].append(link)
    metadata["document_version"] += 1
    metadata["revision"] = "source-registration-" + snapshot.snapshot_sha256[:16]
    render = lambda fields, body: "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in fields.items()) + "\n---\n" + body
    link_metadata = {"schema": "owledge.knowledge-source-link/1", "document_version": 1,
        "artifact_id": link, "authority_id": "user-global:source-access", "revision": "source-registration-1",
        "lifecycle": "accepted", "processing_layer": "condensed", "source_trust": "internal",
        "source_link_id": link, "linked_authority_id": snapshot.source_id, "grants": ["discover", "keyword_retrieve"],
        "source_access": source_access}
    state.update(schema=("owledge.private-knowledge-workspace/3" if source_free else "owledge.private-knowledge-workspace/2"),
                 imports=[*imports, entry])
    documents = {link_path: render(link_metadata, "\n# Imported source link\n"),
                 "global/.owledge/progressive-retrieval.md": render(metadata, body),
                 "workspace.json": json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n"}
    if len(documents["workspace.json"].encode("utf-8")) > 65536:
        raise ContractValidationError("workspace binding exceeds read limit")
    return {"snapshot": snapshot, "before": before, "registry_before": registry_before, "documents": documents,
        "preview": {"status": "preview", "already_current": False, "source_link_id": link,
            "source_access": source_access,
            "documents": len(snapshot.files), "schema_before": json.loads(before)["schema"], "schema_after": state["schema"],
            "message": "Zusätzliche unveränderte Quelle; keine Freigabe, kein Verschieben, keine Quellenersetzung."}}


def apply_source_registration(workspace: Path, pending: dict, principal_id: str, *, check_authority):
    """Serialize publication; a durable journal blocks readers until completion."""
    root = _validated_root(workspace)
    with authority_write_locks((root, root / "global")):
        check_authority()
        if _read_exact_effect(root, root / "workspace.json") != pending["before"]:
            raise ContractValidationError("workspace changed after source preview")
        if pending["preview"]["already_current"]:
            return {**pending["preview"], "status": "ready"}
        if _read_exact_effect(root, root / "global/.owledge/progressive-retrieval.md") != pending["registry_before"]:
            raise ContractValidationError("source registry changed after preview")
        snapshot = pending["snapshot"]
        materialization_reused = False
        if pending["preview"].get("primary_source") is True:
            next_state = json.loads(pending["documents"]["workspace.json"])
            target = _validated_effect_path(root, root / next_state["roots"]["source"], must_exist=False)
            materialization_reused = target.exists()
            if materialization_reused:
                _, receipt_id = validate_primary_snapshot(root, next_state)
            else:
                _, receipt_id = materialize_source_snapshot(
                    root / "sources", snapshot, "op:import:" + snapshot.snapshot_sha256, principal_id)
                validate_primary_snapshot(root, next_state)
        else:
            sources_root = _validated_effect_path(root, root / "sources", must_exist=False)
            if not sources_root.exists():
                sources_root.mkdir()
            _, receipt_id = materialize_source_snapshot(sources_root, snapshot, "op:import:" + snapshot.snapshot_sha256, principal_id)
        journal_path = root / ".owledge/source-registration.json"
        if _effect_exists(root, journal_path):
            raise ContractValidationError("recover pending source registration")
        entries = []
        for relative, content in pending["documents"].items():
            target = root / relative
            current = _read_exact_effect(root, target) if _effect_exists(root, target) else None
            if relative not in {"workspace.json", "global/.owledge/progressive-retrieval.md"} and current is not None:
                if not pending["preview"].get("revision_of_source") or current.decode("utf-8") != content:
                    raise ContractValidationError("source link appeared or changed after preview")
            entries.append({"path": relative, "content": content, "before": current.decode("utf-8") if current is not None else None,
                            "before_sha256": sha256(current).hexdigest() if current is not None else None})
        _write_exact_atomic(root, journal_path, json.dumps({"schema": "owledge.source-registration/1", "entries": entries}, ensure_ascii=False))
        recover_source_registration(root)
        result = {**pending["preview"], "status": "ready", "receipt_id": receipt_id}
        if pending["preview"].get("primary_source") is True:
            result["materialization_reused"] = materialization_reused
        return result


def recover_source_registration(workspace: Path):
    """Caller holds workspace+global locks and proves local Owner authority."""
    root = _validated_root(workspace)
    journal_path = root / ".owledge/source-registration.json"
    encoded = _read_exact_effect(root, journal_path)
    if len(encoded) > 262144:
        raise ContractValidationError("source registration journal exceeds limit")
    journal = json.loads(encoded)
    entries = journal.get("entries") if isinstance(journal, dict) else None
    if not isinstance(journal, dict) or journal.get("schema") != "owledge.source-registration/1" or not isinstance(entries, list) or len(entries) != 3:
        raise ContractValidationError("invalid source registration journal")
    paths = [entry.get("path") for entry in entries if isinstance(entry, dict)]
    if (len(paths) != 3 or paths[1:] != ["global/.owledge/progressive-retrieval.md", "workspace.json"]
            or not isinstance(paths[0], str)
            or paths[0] != "global/.owledge/raw-link.md" and not re.fullmatch(r"global/\.owledge/import-[a-z0-9-]+\.md", paths[0])):
        raise ContractValidationError("invalid source registration destinations")
    validated = []
    for entry in entries:
        if set(entry) != {"path", "content", "before", "before_sha256"} or not isinstance(entry["content"], str) or entry["before"] is not None and not isinstance(entry["before"], str):
            raise ContractValidationError("invalid source registration entry")
        before_hash = sha256(entry["before"].encode("utf-8")).hexdigest() if entry["before"] is not None else None
        if before_hash != entry["before_sha256"]:
            raise ContractValidationError("invalid source registration prior state")
        target = root / entry["path"]
        current = _read_exact_effect(root, target) if _effect_exists(root, target) else None
        content = entry["content"].encode("utf-8")
        if current != content and (sha256(current).hexdigest() if current is not None else None) != entry["before_sha256"]:
            raise ContractValidationError("source registration target changed")
        validated.append((target, entry["content"], current != content))
    entry = _validate_registration_delta(entries)
    if entry.get("primary_source") is True:
        validate_primary_snapshot(root, entry["state"])
    else:
        validate_imported_snapshot(root, entry)
    for target, content, changed in validated:
        if changed:
            _write_exact_atomic(root, target, content)
    _unlink_effect(root, journal_path)


def validate_primary_snapshot(workspace, state):
    """Validate the selected primary snapshot using its own bounded receipt."""

    root = _validated_root(workspace)
    fields = {"schema", "roots", "source_root", "source_id", "source_snapshot_sha256", "runtime_sha256"}
    if (not isinstance(state, dict) or state.get("schema") not in {
            "owledge.private-knowledge-workspace/1", "owledge.private-knowledge-workspace/2"}
            or set(state) != fields | ({"imports"} if state.get("schema", "").endswith("/2") else set())):
        raise ContractValidationError("primary source state is invalid")
    source_id, snapshot_hash = state.get("source_id"), state.get("source_snapshot_sha256")
    if (not isinstance(source_id, str) or not re.fullmatch(r"source:[a-z0-9][a-z0-9-]*", source_id)
            or not isinstance(snapshot_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", snapshot_hash)
            or not isinstance(state.get("source_root"), str)):
        raise ContractValidationError("primary source identity is invalid")
    expected_root = "sources/source-" + source_id.removeprefix("source:") + "-" + snapshot_hash[:16]
    roots = state.get("roots")
    if (not isinstance(roots, dict) or roots != {"user-global": "global", "source": expected_root}):
        raise ContractValidationError("primary source root is invalid")
    target = _validated_effect_path(root, root / expected_root, must_exist=True)
    receipt_id = f"receipt:{source_id.removeprefix('source:')}:setup-{snapshot_hash}"
    receipt_path = _validated_effect_path(
        root, target / ".owledge" / "receipts" / f"setup-{snapshot_hash}.md", must_exist=True)
    before = _materialized_path_facts(root, receipt_path)
    if before[3] != 1 or not stat.S_ISREG(int(before[6])) or int(before[4]) > 65_536:
        raise ContractValidationError("primary source receipt is invalid or exceeds its read limit")
    with receipt_path.open("rb") as handle:
        encoded = handle.read(65_537)
    after = _materialized_path_facts(root, receipt_path)
    if before != after or len(encoded) != int(before[4]) or len(encoded) > 65_536:
        raise ContractValidationError("primary source receipt changed while read")
    try:
        metadata, _ = parse_markdown_frontmatter(encoded.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise ContractValidationError("primary source receipt is not UTF-8") from error
    operation_id = metadata.get("operation_id")
    allowed_operations = {"op:owner-workspace-setup", "op:import:" + snapshot_hash}
    expected = {"schema": "owledge.receipt/1", "document_version": 1, "receipt_id": receipt_id,
                "authority_id": source_id, "operation": "setup_apply", "outcome": "ok/source_snapshot_ready",
                "operation_id": operation_id, "snapshot_sha256": snapshot_hash,
                "approved_by": "principal:local-owner"}
    if not isinstance(operation_id, str) or operation_id not in allowed_operations or metadata != expected:
        raise ContractValidationError("primary source receipt provenance is invalid")
    entry = {"source_id": source_id, "source_root": state["source_root"], "snapshot_sha256": snapshot_hash,
             "root": expected_root, "source_link_id": "link:source-access-originals",
             "operation_id": operation_id, "approved_by": "principal:local-owner"}
    validate_imported_snapshot(root, entry)
    return entry, receipt_id


def validate_imported_snapshot(workspace, entry):
    """Verify preserved originals independently from the mutable input folder."""
    from .contracts import SourceFileSnapshot
    root = _validated_root(workspace)
    preserved = _validated_effect_path(root, root / entry["root"], must_exist=True)
    slug = entry["source_id"].removeprefix("source:")
    metadata, _ = _read_effect_metadata(root, preserved / f".owledge/sources/{slug}/manifest.md")
    records = metadata.get("records")
    if not isinstance(records, list) or not records:
        raise ContractValidationError("imported snapshot manifest is invalid")
    files = []
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("relative_path"), str):
            raise ContractValidationError("imported snapshot record is invalid")
        relative = record["relative_path"]
        # SourceFileSnapshot validates portable paths before reading their bytes.
        SourceFileSnapshot.from_bytes(relative, b"")
        content = _read_exact_effect(root, preserved / "originals" / entry["snapshot_sha256"] / relative)
        files.append(SourceFileSnapshot.from_bytes(relative, content))
    snapshot = SourceSnapshot.create(entry["source_id"], Path(entry["source_root"]), files)
    if snapshot.snapshot_sha256 != entry["snapshot_sha256"]:
        raise ContractValidationError("imported original bytes changed")
    expected, originals, _ = _source_snapshot_files(snapshot, entry["operation_id"], entry["approved_by"])
    _validate_materialized_source(preserved, expected, originals)


def _source_revision_changes(workspace: Path, old_entry: dict, snapshot: SourceSnapshot) -> dict[str, object]:
    """Return a bounded relative-path summary without copying source bodies."""

    root = _validated_root(workspace)
    preserved = _validated_effect_path(root, root / old_entry["root"], must_exist=True)
    slug = old_entry["source_id"].removeprefix("source:")
    metadata, _ = _read_effect_metadata(root, preserved / f".owledge/sources/{slug}/manifest.md")
    records = metadata.get("records")
    if not isinstance(records, list):
        raise ContractValidationError("imported snapshot manifest is invalid")
    old = {record.get("relative_path"): record.get("content_sha256") for record in records if isinstance(record, dict)}
    if len(old) != len(records) or any(not isinstance(path, str) or not isinstance(digest, str) for path, digest in old.items()):
        raise ContractValidationError("imported snapshot records are invalid")
    new = {item.relative_path: item.content_sha256 for item in snapshot.files}
    limit = 32
    path_order = lambda path: (path.casefold(), path)
    added = sorted(new.keys() - old.keys(), key=path_order)
    removed = sorted(old.keys() - new.keys(), key=path_order)
    changed = sorted((path for path in old.keys() & new.keys() if old[path] != new[path]), key=path_order)
    return {"added": added[:limit], "changed": changed[:limit], "removed": removed[:limit],
            "counts": {"added": len(added), "changed": len(changed), "removed": len(removed)},
            "truncated": any(len(items) > limit for items in (added, changed, removed))}


def _validate_registration_delta(entries):
    """A redo journal may add exactly one read-only source, never arbitrary grants."""
    try:
        old = json.loads(entries[2]["before"])
        new = json.loads(entries[2]["content"])
        if not isinstance(old, dict) or not isinstance(new, dict):
            raise ValueError("source registration state is invalid")
        primary = entries[0]["path"] == "global/.owledge/raw-link.md"
        if primary:
            schema = old.get("schema")
            fields = {"schema", "roots", "source_root", "source_id", "source_snapshot_sha256", "runtime_sha256"}
            expected_fields = fields | ({"imports"} if schema == "owledge.private-knowledge-workspace/2" else set())
            old_hash, new_hash, source_id = old.get("source_snapshot_sha256"), new.get("source_snapshot_sha256"), old.get("source_id")
            if (schema not in {"owledge.private-knowledge-workspace/1", "owledge.private-knowledge-workspace/2"}
                    or new.get("schema") != schema or set(old) != expected_fields or set(new) != expected_fields
                    or not isinstance(source_id, str) or not re.fullmatch(r"source:[a-z0-9][a-z0-9-]*", source_id)
                    or not isinstance(old_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", old_hash)
                    or not isinstance(new_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", new_hash)
                    or old_hash == new_hash):
                raise ValueError("invalid primary source revision identity")
            slug = source_id.removeprefix("source:")
            old_roots = {"user-global": "global", "source": f"sources/source-{slug}-{old_hash[:16]}"}
            new_roots = {"user-global": "global", "source": f"sources/source-{slug}-{new_hash[:16]}"}
            expected = {**old, "roots": new_roots, "source_snapshot_sha256": new_hash}
            if (old.get("roots") != old_roots or new != expected
                    or entries[0]["before"] != entries[0]["content"]
                    or entries[1]["before"] != entries[1]["content"]):
                raise ValueError("unexpected primary source revision delta")
            return {"primary_source": True, "state": new}
        old_imports = old.get("imports", [])
        imports = new.get("imports")
        if not isinstance(old_imports, list) or not isinstance(imports, list):
            raise ValueError("source registration imports are invalid")
        source_free = old.get("schema") == "owledge.private-knowledge-workspace/3"
        if source_free and (set(old) != {"schema", "roots", "runtime_sha256", "imports"}
                or old.get("roots") != {"user-global": "global"}
                or not isinstance(old.get("runtime_sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", old["runtime_sha256"])
                or len(old_imports) > 64):
            raise ValueError("invalid source-free workspace state")
        revision = (old.get("schema") == new.get("schema")
                    and old.get("schema") in {"owledge.private-knowledge-workspace/2", "owledge.private-knowledge-workspace/3"}
                    and len(imports) == len(old_imports))
        if revision:
            changed = [index for index, pair in enumerate(zip(old_imports, imports)) if pair[0] != pair[1]]
            if len(changed) != 1 or {key: value for key, value in new.items() if key != "imports"} != {key: value for key, value in old.items() if key != "imports"}:
                raise ValueError("unexpected source revision delta")
            index = changed[0]
            prior, entry = old_imports[index], imports[index]
            if not isinstance(prior, dict) or not isinstance(entry, dict):
                raise ValueError("source revision entries are invalid")
            if any(prior.get(key) != entry.get(key) for key in ("source_id", "source_root", "source_link_id")):
                raise ValueError("source revision changed stable identity")
            if prior.get("snapshot_sha256") == entry.get("snapshot_sha256"):
                raise ValueError("source revision did not change snapshot")
            if entries[0]["before"] != entries[0]["content"] or entries[1]["before"] != entries[1]["content"]:
                raise ValueError("source revision changed link or registry")
        else:
            if not imports or not isinstance(imports[-1], dict):
                raise ValueError("source binding entry is invalid")
            entry = imports[-1]
            expected = {**old, "schema": ("owledge.private-knowledge-workspace/3" if source_free else "owledge.private-knowledge-workspace/2"),
                        "imports": [*old_imports, entry]}
            if new != expected or len(imports) != len(old_imports) + 1 or entries[0]["before"] is not None:
                raise ValueError("unexpected source binding delta")
        fields = {"source_id", "source_root", "snapshot_sha256", "root", "source_link_id", "operation_id", "approved_by"}
        if set(entry) not in (fields, fields | {"source_access"}) or not all(isinstance(entry.get(key), str) and entry[key] for key in fields):
            raise ValueError("invalid imported source binding")
        rights = entry.get("source_access")
        if rights is not None and rights not in ({"access": "restricted", "principals": [entry["approved_by"]]},
                                                {"access": "shared", "principals": []}):
            raise ValueError("invalid imported source rights")
        slug = entry["source_id"].removeprefix("source:")
        if not re.fullmatch(r"[a-z0-9-]+", slug) or not entry["source_id"].startswith("source:") or not re.fullmatch(r"[0-9a-f]{64}", entry["snapshot_sha256"]):
            raise ValueError("invalid imported identity")
        if entry["root"] != f"sources/source-{slug}-{entry['snapshot_sha256'][:16]}" or entry["source_link_id"] != "link:import-" + slug or entries[0]["path"] != f"global/.owledge/import-{slug}.md":
            raise ValueError("invalid imported path binding")
        if entry["operation_id"] != "op:import:" + entry["snapshot_sha256"]:
            raise ValueError("invalid receipt binding")
        link, _ = parse_markdown_frontmatter(entries[0]["content"])
        expected_link = {"schema": "owledge.knowledge-source-link/1", "document_version": 1,
            "artifact_id": entry["source_link_id"], "authority_id": "user-global:source-access", "revision": "source-registration-1",
            "lifecycle": "accepted", "processing_layer": "condensed", "source_trust": "internal",
            "source_link_id": entry["source_link_id"], "linked_authority_id": entry["source_id"],
            "grants": ["discover", "keyword_retrieve"],
            **({"source_access": rights} if rights is not None else {})}
        if revision:
            current_rights = link.get("source_access")
            if (link.get("schema") != expected_link["schema"]
                    or any(link.get(key) != expected_link[key] for key in
                           ("artifact_id", "authority_id", "lifecycle", "processing_layer",
                            "source_trust", "source_link_id", "linked_authority_id", "grants"))
                    or not isinstance(current_rights, dict)
                    or set(current_rights) != {"access", "principals"}
                    or current_rights["access"] not in {"restricted", "shared"}
                    or not isinstance(current_rights["principals"], list)
                    or current_rights["access"] == "restricted"
                       and "principal:local-owner" not in current_rights["principals"]
                    or current_rights["access"] == "shared" and current_rights["principals"] != []
                    or any(not isinstance(item, str) or not item.startswith("principal:")
                           for item in current_rights["principals"])
                    or len(current_rights["principals"]) != len(set(current_rights["principals"]))
                    or type(link.get("document_version")) is not int or link["document_version"] < 1):
                raise ValueError("invalid revised source permissions")
        elif link != expected_link:
            raise ValueError("invalid imported source permissions")
        if not revision:
            registry, body = parse_markdown_frontmatter(entries[1]["before"])
            actual, actual_body = parse_markdown_frontmatter(entries[1]["content"])
            if source_free and not old_imports:
                if registry.get("coverage_cases") != {}:
                    raise ValueError("first source registry is not empty")
                registry["coverage_cases"]["coverage:source-access-originals"] = {
                    "revision": "source-access-1", "lifecycle": "accepted",
                    "required_evidence": ["raw_content"], "search_envelope": ["raw_keyword"],
                    "source_links": {"raw_keyword": []}, "gap_admission": "disabled"}
            registry["coverage_cases"]["coverage:source-access-originals"]["source_links"]["raw_keyword"].append(entry["source_link_id"])
            registry["document_version"] += 1
            registry["revision"] = "source-registration-" + entry["snapshot_sha256"][:16]
            if actual != registry or body != actual_body:
                raise ValueError("unexpected retrieval policy delta")
        return entry
    except (ValueError, TypeError, KeyError, IndexError) as error:
        raise ContractValidationError("source registration journal changes unsupported policy") from error


def materialize_owner_workspace(
    target: Path, documents: Mapping[str, str], *, source_snapshot: SourceSnapshot | None = None,
) -> Path:
    """Publish a new disposable setup only after all files and originals validate.

    The caller obtains explicit preview approval. Never merges an existing tree.
    Setup documents are configuration/demo inputs, not automatic Source curation.
    """
    from .contracts import verified_settings_catalog
    verified_settings_catalog()
    candidate = Path(target).absolute()
    if any(_is_reparse_path(path) for path in (candidate, *candidate.parents)):
        raise ContractValidationError("workspace target crosses a link")
    parent = _validated_root(candidate.parent)
    if candidate.exists() or not documents:
        raise ContractValidationError("workspace target must be new and absent")
    for relative, content in documents.items():
        path = Path(relative)
        if not isinstance(content, str) or path.is_absolute() or ".." in path.parts or not path.parts or ":" in relative or "\\" in relative:
            raise ContractValidationError("workspace document path is invalid")
    identity = _path_identity(_materialized_path_facts(parent, parent))
    temporary = Path(tempfile.mkdtemp(prefix=".owledge-setup-", dir=parent))
    temporary_identity = _path_identity(_materialized_path_facts(parent, temporary))
    try:
        for relative, content in sorted(documents.items()):
            _assert_workspace_anchor(candidate.parent, parent, identity)
            _assert_target_anchor(parent, temporary, temporary_identity)
            _write_exact_atomic(temporary, temporary / relative, content)
        if source_snapshot is not None:
            source_root = temporary / "sources"
            source_root.mkdir(exist_ok=True)
            materialize_source_snapshot(source_root, source_snapshot,
                                        "op:owner-workspace-setup", "principal:local-owner")
        _assert_workspace_anchor(candidate.parent, parent, identity)
        if candidate.exists():
            raise ContractValidationError("workspace appeared during setup")
        os.rename(temporary, candidate)
        return candidate
    except BaseException:
        # Only our explicit mkdtemp staging directory may be cleaned up.
        try:
            _assert_workspace_anchor(candidate.parent, parent, identity)
            _assert_target_anchor(parent, temporary, temporary_identity)
        except (ContractValidationError, OSError):
            pass  # Leave a displaced staging tree for explicit inspection.
        else:
            _clear_readonly_and_remove(temporary)
        raise


def materialize_source_snapshot(
    workspace_root: Path,
    snapshot: SourceSnapshot,
    operation_id: str,
    approved_by: str,
) -> tuple[dict[str, object], str]:
    """Materialize one immutable source snapshot below a disposable workspace."""

    workspace_candidate = Path(workspace_root).absolute()
    if any(_is_reparse_path(path) for path in (workspace_candidate, *workspace_candidate.parents)):
        raise ContractValidationError("setup workspace crosses a link")
    resolved_workspace = _validated_root(workspace_candidate)
    workspace_identity = _path_identity(
        _materialized_path_facts(resolved_workspace, resolved_workspace)
    )
    target_name = source_snapshot_target_name(snapshot)
    target = resolved_workspace / target_name
    expected, originals, receipt_id = _source_snapshot_files(
        snapshot,
        operation_id,
        approved_by,
    )
    if target.exists():
        _validate_materialized_source(target, expected, originals)
        return (
            {
                "target_name": target_name,
                "snapshot_sha256": snapshot.snapshot_sha256,
                "document_count": len(snapshot.files),
                "size_bytes": snapshot.size_bytes,
                "already_current": True,
            },
            receipt_id,
        )

    _assert_workspace_anchor(workspace_candidate, resolved_workspace, workspace_identity)
    temporary = Path(tempfile.mkdtemp(prefix=".owledge-source-", dir=resolved_workspace))
    temporary_identity = _path_identity(
        _materialized_path_facts(resolved_workspace, temporary)
    )
    try:
        for relative, content in sorted(expected.items()):
            _assert_workspace_anchor(workspace_candidate, resolved_workspace, workspace_identity)
            _assert_target_anchor(resolved_workspace, temporary, temporary_identity)
            destination = temporary / Path(relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            _assert_workspace_anchor(workspace_candidate, resolved_workspace, workspace_identity)
            _assert_target_anchor(resolved_workspace, temporary, temporary_identity)
            destination.write_bytes(content)
            if relative in originals:
                destination.chmod(stat.S_IREAD)
        _validate_materialized_source(temporary, expected, originals)
        _assert_workspace_anchor(workspace_candidate, resolved_workspace, workspace_identity)
        if target.exists():
            raise ContractValidationError("source snapshot target appeared during setup")
        try:
            os.rename(temporary, target)
        except FileExistsError as error:
            raise ContractValidationError("source snapshot target appeared during setup") from error
        _validate_materialized_source(target, expected, originals)
    except BaseException:
        _clear_readonly_and_remove(temporary)
        raise
    return (
        {
            "target_name": target_name,
            "snapshot_sha256": snapshot.snapshot_sha256,
            "document_count": len(snapshot.files),
            "size_bytes": snapshot.size_bytes,
            "already_current": False,
        },
        receipt_id,
    )
