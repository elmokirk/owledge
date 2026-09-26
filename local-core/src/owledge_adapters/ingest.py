"""Private explicit source registration and recoverable local inbox transport."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile

from .local_setup import open_workspace


INBOX_JOURNAL = ".owledge-inbox-import.json"
WORKSPACE_JOURNAL = ".owledge/inbox-import.json"
MAX_FILES = 1_000
MAX_BYTES = 16 * 1024 * 1024
MAX_ENTRIES = 2_000
MAX_DEPTH = 64
MAX_PATH_BYTES = 4_096
MAX_JOURNAL_BYTES = 262_144


class SourceImport:
    def __init__(self, workspace: Path, source: Path, *, access: str | None = None):
        from owledge_connectors.markdown_source import MarkdownSourceConnector
        from .knowledge_workspace import SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA, OWNER
        self.workspace, self.source = workspace, source
        self.core, state = open_workspace(workspace)
        if state["schema"] not in {SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}:
            raise ValueError("Ingest benötigt einen lokalen Knowledge-Workspace.")
        self.core._source_connector_factory = MarkdownSourceConnector
        self.owner = OWNER
        self.access = access

    def preview(self):
        return self.core._source_registration_from_local_owner(self.workspace, self.source, self.owner, access=self.access)

    def apply(self):
        return self.core._source_registration_from_local_owner(self.workspace, self.source, self.owner, apply=True,
                                                                access=self.access)


def recover_import(workspace):
    from owledge_core.api import Core
    from owledge_connectors.markdown_source import MarkdownSourceConnector
    from .local_setup import _unlinked_path
    root = _unlinked_path(workspace)
    core = Core.open({"user-global": _unlinked_path(root / "global")}, identity_profile="mvp-v1",
                     source_connector_factory=MarkdownSourceConnector)
    return core._source_registration_from_local_owner(root, None, "principal:local-owner", recover=True)


def _read_regular(path: Path, limit: int) -> bytes:
    from .local_setup import _unlinked_path
    target = _unlinked_path(path)
    before = target.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > limit:
        raise ValueError("Inbox-Datei ist verknüpft, nicht regulär oder zu groß.")
    with target.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        data = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
    final = target.stat()
    facts = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_nlink, item.st_mode)
    if len(data) > limit or not (facts(before) == facts(opened) == facts(after) == facts(final)):
        raise ValueError("Inbox-Datei wurde während des Lesens verändert.")
    return data


def _package_name(name: str) -> str:
    if (not isinstance(name, str) or not name or name in {".", ".."} or name.endswith((".", " "))
            or len(name.encode("utf-16-le")) // 2 > 255 or re.search(r'[\\/:<>"|?*\x00-\x1f]', name)
            or name.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(10)), *(f"LPT{i}" for i in range(10))}
            or name.startswith(".owledge-")):
        raise ValueError("Unsicherer Inbox-Paketname.")
    return name


def _inventory(package: Path) -> tuple[dict[str, object], object]:
    from .local_setup import _unlinked_path
    from owledge_connectors.markdown_source import (
        MarkdownSourceConnector, _assert_directory_unchanged, _is_reparse_path,
        _path_facts, _read_stable_file, _stable_directory_entries,
    )
    from owledge_core.contracts import SourceFileSnapshot
    package = _unlinked_path(Path(package))
    root = package
    items = []
    observed_total = 0
    if root.is_file():
        facts = _path_facts(root)
        if facts.size_bytes > MAX_BYTES:
            raise ValueError(f"Inbox-Paket überschreitet das Limit von {MAX_BYTES} Bytes.")
        files = [(root.name, _read_stable_file(root, root))]
        kind = "file"
    else:
        kind = "directory"
        files = []
        pending = [root]
        visited = []
        observed_entries = 0
        while pending:
            directory = pending.pop()
            names, facts = _stable_directory_entries(directory, root)
            visited.append((directory, facts, names))
            for name in names:
                observed_entries += 1
                if observed_entries > MAX_ENTRIES:
                    raise ValueError(f"Inbox-Paket überschreitet das Limit von {MAX_ENTRIES} Einträgen.")
                _assert_directory_unchanged(directory, facts)
                path = directory / name
                relative = path.relative_to(root)
                if len(relative.parts) > MAX_DEPTH or len(relative.as_posix().encode("utf-8")) > MAX_PATH_BYTES:
                    raise ValueError("Inbox-Paket überschreitet das Pfadlimit.")
                if _is_reparse_path(path):
                    raise ValueError("Inbox-Paket enthält eine Verknüpfung.")
                observed = _path_facts(path)
                if stat.S_ISDIR(observed.mode):
                    pending.append(path)
                    continue
                if not stat.S_ISREG(observed.mode) or observed.nlink != 1 or path.suffix.casefold() != ".md":
                    raise ValueError("Inbox-Paket darf nur reguläre Markdown-Dateien enthalten.")
                if len(files) >= MAX_FILES:
                    raise ValueError(f"Inbox-Paket überschreitet das Limit von {MAX_FILES} Dateien.")
                observed_total += observed.size_bytes
                if observed_total > MAX_BYTES:
                    raise ValueError(f"Inbox-Paket überschreitet das Limit von {MAX_BYTES} Bytes.")
                files.append((relative.as_posix(), _read_stable_file(path, root)))
            _assert_directory_unchanged(directory, facts, names)
        for directory, facts, names in reversed(visited):
            _assert_directory_unchanged(directory, facts, names)
    if len(files) > MAX_FILES:
        raise ValueError(f"Inbox-Paket überschreitet das Limit von {MAX_FILES} Dateien.")
    total = 0
    for relative, content in files:
        item = SourceFileSnapshot.from_bytes(relative, content)
        total += item.size_bytes
        if total > MAX_BYTES:
            raise ValueError(f"Inbox-Paket überschreitet das Limit von {MAX_BYTES} Bytes.")
        items.append(item)
    items.sort(key=lambda item: item.normalized_path)
    records = [{"path": item.relative_path, "sha256": item.content_sha256, "size": item.size_bytes}
               for item in items]
    snapshot = MarkdownSourceConnector(package).scan()
    expected = [{"path": item.relative_path, "sha256": item.content_sha256, "size": item.size_bytes}
                for item in snapshot.files]
    if records != expected:
        raise ValueError("Inbox-Paket wurde während der Inventur verändert.")
    return {"kind": kind, "files": records, "count": len(records), "bytes": total,
            "snapshot_sha256": snapshot.snapshot_sha256}, snapshot


def _validate_inventory(value, *, optional=False):
    if optional and value is None:
        return None
    if (not isinstance(value, dict) or set(value) != {"kind", "files", "count", "bytes", "snapshot_sha256"}
            or value.get("kind") not in {"file", "directory"} or not isinstance(value.get("files"), list)
            or type(value.get("count")) is not int or type(value.get("bytes")) is not int
            or value["count"] != len(value["files"]) or not 1 <= value["count"] <= MAX_FILES
            or not 0 <= value["bytes"] <= MAX_BYTES
            or not isinstance(value.get("snapshot_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", value["snapshot_sha256"])):
        raise ValueError("Inbox-Inventar ist ungültig.")
    total, names = 0, set()
    for item in value["files"]:
        if (not isinstance(item, dict) or set(item) != {"path", "sha256", "size"}
                or not isinstance(item.get("path"), str) or not isinstance(item.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
                or type(item.get("size")) is not int or item["size"] < 0):
            raise ValueError("Inbox-Inventareintrag ist ungültig.")
        from owledge_core.contracts import SourceFileSnapshot
        SourceFileSnapshot.from_bytes(item["path"], b"")
        folded = item["path"].casefold()
        if folded in names:
            raise ValueError("Inbox-Inventarpfade kollidieren.")
        names.add(folded)
        total += item["size"]
    if total != value["bytes"] or (value["kind"] == "file" and value["count"] != 1):
        raise ValueError("Inbox-Inventarsumme ist ungültig.")
    return value


def _atomic_write(path: Path, data: bytes) -> None:
    if path.exists():
        raise ValueError("Inbox-Wiederherstellungsjournal existiert bereits.")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".owledge-inbox-journal-", dir=path.parent)
    stage = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(stage, path)
    finally:
        stage.unlink(missing_ok=True)


def _paths(workspace: Path, inbox: Path, name: str):
    suffix = sha256((str(workspace) + "\0" + str(inbox) + "\0" + name).encode("utf-8")).hexdigest()[:16]
    raw = inbox / "raw" / name
    destination = inbox / "processed" / name
    stage = inbox / "processed" / f".owledge-stage-{suffix}"
    backup = inbox / "processed" / f".owledge-backup-{suffix}"
    consumed = inbox / "raw" / f".owledge-consumed-{suffix}"
    return raw, destination, stage, backup, consumed


def _workspace_state(workspace: Path) -> tuple[bytes, dict[str, object]]:
    from .local_setup import _state_bytes
    encoded = _state_bytes(workspace)
    state = json.loads(encoded)
    if not isinstance(state, dict):
        raise ValueError("Ungültiger Knowledge-Workspace.")
    return encoded, state


def _overlaps(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _owner_preview(workspace: Path, source: Path, access: str | None = None):
    from .knowledge_workspace import OWNER
    from .local_setup import _unlinked_path
    from owledge_connectors.markdown_source import MarkdownSourceConnector
    from owledge_core.api import Core
    core = Core.open({"user-global": _unlinked_path(workspace / "global")}, identity_profile="mvp-v1",
                     source_connector_factory=MarkdownSourceConnector)
    return core._source_registration_from_local_owner(workspace, source, OWNER, access=access)


def _recovery_owner_preflight(workspace: Path, source: Path, access: str | None = None) -> None:
    from owledge_core.contracts import ContractValidationError
    try:
        _owner_preview(workspace, source, access)
    except ContractValidationError as error:
        if ((workspace / ".owledge/source-registration.json").exists()
                and str(error) == "source registration requires local Owner recovery"):
            return
        raise


def _registered_binding(workspace: Path, state: dict[str, object], destination: Path):
    wanted = os.path.normcase(os.path.abspath(str(destination)))
    matches = []
    source_root = state.get("source_root")
    if isinstance(source_root, str) and os.path.normcase(os.path.abspath(source_root)) == wanted:
        matches.append(("primary", state))
    for entry in state.get("imports", []):
        locator = entry.get("source_root") if isinstance(entry, dict) else None
        if isinstance(locator, str) and os.path.normcase(os.path.abspath(locator)) == wanted:
            matches.append(("import", entry))
    if len(matches) != 1:
        return None
    from owledge_core.project_io import validate_imported_snapshot, validate_primary_snapshot
    kind, binding = matches[0]
    if kind == "primary":
        validate_primary_snapshot(workspace, state)
    else:
        validate_imported_snapshot(workspace, binding)
    return matches[0]


def _copy_snapshot(snapshot, package_kind: str, destination: Path) -> None:
    if package_kind == "file":
        destination.parent.mkdir(parents=True, exist_ok=True)
        if len(snapshot.files) != 1 or snapshot.files[0].relative_path != destination.name:
            raise ValueError("Inbox-Dateipaket stimmt nicht mit seinem Zielnamen überein.")
        destination.write_bytes(snapshot.files[0].content)
        return
    destination.mkdir(parents=True)
    for item in snapshot.files:
        target = destination / item.relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(item.content)


def _container_package(container: Path, name: str) -> Path:
    return container / name


def _remove_owned(container: Path, name: str, expected: dict[str, object]) -> None:
    package = _container_package(container, name)
    actual, _ = _inventory(package)
    if actual != expected or sorted(path.name for path in container.iterdir()) != [name]:
        raise ValueError("Journal-eigene Inbox-Dateien wurden verändert; keine Bereinigung ausgeführt.")
    if package.is_file():
        package.unlink()
        container.rmdir()
    else:
        shutil.rmtree(package)
        container.rmdir()


def _direct_state(workspace: Path) -> dict[str, object]:
    return json.loads(_read_regular(workspace / "workspace.json", 65_536))


def _verify_committed(workspace: Path, destination: Path, expected: dict[str, object]):
    state = _direct_state(workspace)
    if not destination.exists():
        return None
    binding = _registered_binding(workspace, state, destination)
    if binding is None:
        return None
    observed, snapshot = _inventory(destination)
    kind, saved = binding
    saved_hash = state["source_snapshot_sha256"] if kind == "primary" else saved.get("snapshot_sha256")
    saved_source = state["source_id"] if kind == "primary" else saved.get("source_id")
    if saved_hash != expected["snapshot_sha256"]:
        return None
    if observed != expected or saved_hash != snapshot.snapshot_sha256 or saved_source != snapshot.source_id:
        raise ValueError("Verarbeitete Quelle unterscheidet sich von der bestätigten Aufnahme.")
    return binding


def _remove_partial_owned(container: Path, name: str, expected: dict[str, object]) -> None:
    from .local_setup import _unlinked_path
    from owledge_connectors.markdown_source import (
        _assert_directory_unchanged, _is_reparse_path, _path_facts,
        _read_stable_file, _stable_directory_entries,
    )
    if not container.exists():
        return
    container = _unlinked_path(Path(container))
    root = container
    names, container_facts = _stable_directory_entries(container, root)
    if not names:
        container.rmdir()
        return
    if names != (name,):
        raise ValueError("Journal-eigener Zwischenpfad enthält fremde Dateien.")
    expected_records = {item["path"]: (item["sha256"], item["size"]) for item in expected["files"]}
    package = container / name
    if _is_reparse_path(package):
        raise ValueError("Journal-eigener Zwischenpfad enthält eine Verknüpfung.")
    if package.is_file():
        if expected["kind"] != "file":
            raise ValueError("Journal-eigener Zwischenpfad hat den falschen Pakettyp.")
        content = _read_stable_file(package, root)
        observed = (sha256(content).hexdigest(), len(content))
        if expected_records.get(name) != observed:
            raise ValueError("Journal-eigener Zwischenpfad wurde verändert.")
        _assert_directory_unchanged(container, container_facts, (name,))
        package.unlink()
    else:
        if expected["kind"] != "directory" or not package.is_dir():
            raise ValueError("Journal-eigener Zwischenpfad hat den falschen Pakettyp.")
        pending, visited, entry_count = [package], [], 0
        while pending:
            directory = pending.pop()
            directory_names, directory_facts = _stable_directory_entries(directory, root)
            visited.append((directory, directory_facts, directory_names))
            for child_name in directory_names:
                entry_count += 1
                if entry_count > MAX_ENTRIES:
                    raise ValueError("Journal-eigener Zwischenpfad enthält zu viele Einträge.")
                child = directory / child_name
                relative = child.relative_to(package)
                if len(relative.parts) > MAX_DEPTH or len(relative.as_posix().encode("utf-8")) > MAX_PATH_BYTES:
                    raise ValueError("Journal-eigener Zwischenpfad überschreitet das Pfadlimit.")
                if _is_reparse_path(child):
                    raise ValueError("Journal-eigener Zwischenpfad enthält eine Verknüpfung.")
                facts = _path_facts(child)
                if stat.S_ISDIR(facts.mode):
                    pending.append(child)
                    continue
                if not stat.S_ISREG(facts.mode) or facts.nlink != 1:
                    raise ValueError("Journal-eigener Zwischenpfad enthält eine Sonderdatei.")
                content = _read_stable_file(child, root)
                if expected_records.get(relative.as_posix()) != (sha256(content).hexdigest(), len(content)):
                    raise ValueError("Journal-eigener Zwischenpfad wurde verändert.")
            _assert_directory_unchanged(directory, directory_facts, directory_names)
        for directory, directory_facts, directory_names in reversed(visited):
            _assert_directory_unchanged(directory, directory_facts, directory_names)
        _assert_directory_unchanged(container, container_facts, (name,))
        shutil.rmtree(package)
    container.rmdir()


class InboxImport:
    def __init__(self, workspace: Path, inbox: Path, source: Path, *, access: str | None = None):
        from .local_setup import _unlinked_path
        self.workspace = _unlinked_path(Path(workspace))
        self.inbox = _unlinked_path(Path(inbox))
        raw_root = _unlinked_path(self.inbox / "raw")
        self.processed_root = _unlinked_path(self.inbox / "processed")
        self.source = _unlinked_path(Path(source))
        self.access = access
        if self.source.parent != raw_root:
            raise ValueError("--source muss genau ein direktes Paket unter <inbox>/raw wählen.")
        self.name = _package_name(self.source.name)
        self.raw, self.destination, self.stage, self.backup, self.consumed = _paths(
            self.workspace, self.inbox, self.name)
        if self.workspace == self.inbox or self.workspace in self.inbox.parents or self.inbox in self.workspace.parents:
            raise ValueError("Inbox und Workspace müssen getrennt sein.")
        for path in (self.stage, self.backup, self.consumed):
            if os.path.lexists(path):
                raise ValueError("Inbox enthält einen ausstehenden oder kollidierenden Transportpfad.")
        if (self.workspace / WORKSPACE_JOURNAL).exists() or (self.inbox / INBOX_JOURNAL).exists():
            raise ValueError("Inbox-Transport erfordert explizite Wiederherstellung.")
        self.workspace_before, self.state = _workspace_state(self.workspace)
        self.raw_inventory, self.raw_snapshot = _inventory(self.source)
        self.old_inventory = None
        self.binding = None
        existing_locators = ([Path(self.state["source_root"]).absolute()] if isinstance(self.state.get("source_root"), str) else [])
        existing_locators.extend(Path(item["source_root"]).absolute()
                                 for item in self.state.get("imports", []) if isinstance(item, dict))
        if any(_overlaps(self.raw, locator) for locator in existing_locators):
            raise ValueError("Raw-Paket ist bereits eine aktive Quelle und wird nicht automatisch verschoben.")
        for locator in existing_locators:
            if self.destination.exists() and self.destination.resolve(strict=True) == locator:
                continue
            if _overlaps(self.destination, locator):
                raise ValueError("Processed-Ziel überlappt eine bestehende Quelle.")
        if self.destination.exists():
            self.binding = _registered_binding(self.workspace, self.state, self.destination)
            if self.binding is None:
                raise ValueError("Processed-Ziel existiert ohne exakte Workspace-Bindung.")
            self.old_inventory, _ = _inventory(self.destination)
            if self.old_inventory["kind"] != self.raw_inventory["kind"]:
                raise ValueError("Inbox-Pakettyp darf sich nicht ändern.")
            self.kind = "repeat" if self.old_inventory == self.raw_inventory else "changed"
            source_preview = SourceImport(self.workspace, self.destination, access=access).preview()
        else:
            self.kind = "new"
            source_preview = SourceImport(self.workspace, self.source, access=access).preview()
        self.preview_data = {"status": "preview", "transport": "inbox", "kind": self.kind,
            "package": self.name, "files": self.raw_inventory["count"], "bytes": self.raw_inventory["bytes"],
            "source_access": source_preview.get("source_access"),
            "message": "Technische Aufnahme nach processed; keine Wissensfreigabe."}

    def preview(self):
        return dict(self.preview_data)

    def _record(self):
        record = {"schema": "owledge.inbox-import/1", "workspace": str(self.workspace), "inbox": str(self.inbox),
                  "package": self.name, "kind": self.kind, "raw": self.raw_inventory, "old": self.old_inventory,
                  "workspace_sha256": sha256(self.workspace_before).hexdigest(), "access": self.access}
        encoded = (json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        if len(encoded) > MAX_JOURNAL_BYTES:
            raise ValueError("Inbox-Journal überschreitet sein Größenlimit.")
        return record, encoded

    def apply(self):
        from owledge_core.project_io import authority_write_locks
        with authority_write_locks((self.inbox,)):
            return self._apply_with_inbox_lock()

    def _apply_with_inbox_lock(self):
        from owledge_core.project_io import authority_write_locks
        global_root = self.workspace / "global"
        with authority_write_locks((global_root,)):
            from .local_setup import _unlinked_path
            _unlinked_path(self.inbox / "raw")
            _unlinked_path(self.inbox / "processed")
            if _read_regular(self.workspace / "workspace.json", 65_536) != self.workspace_before:
                raise ValueError("Workspace wurde seit der Inbox-Vorschau verändert.")
            current, snapshot = _inventory(self.raw)
            if current != self.raw_inventory:
                raise ValueError("Raw-Paket wurde seit der Inbox-Vorschau verändert.")
            if self.destination.exists():
                old, _ = _inventory(self.destination)
                if old != self.old_inventory:
                    raise ValueError("Processed-Ziel wurde seit der Inbox-Vorschau verändert.")
            elif self.old_inventory is not None:
                raise ValueError("Processed-Ziel ist seit der Inbox-Vorschau verschwunden.")
            # Current Owner/read_write authorization must succeed before the first adapter write.
            SourceImport(self.workspace, self.destination if self.destination.exists() else self.raw,
                         access=self.access).preview()
            operation = SourceImport(self.workspace, self.destination, access=self.access)
            _, encoded = self._record()
            _atomic_write(self.inbox / INBOX_JOURNAL, encoded)
            _atomic_write(self.workspace / WORKSPACE_JOURNAL, encoded)
            if self.kind != "repeat":
                self.stage.mkdir()
                staged = _container_package(self.stage, self.name)
                _copy_snapshot(snapshot, self.raw_inventory["kind"], staged)
                if _inventory(staged)[0] != self.raw_inventory:
                    raise ValueError("Inbox-Staging unterscheidet sich vom Raw-Paket.")
                if self.kind == "changed":
                    self.backup.mkdir()
                    os.rename(self.destination, _container_package(self.backup, self.name))
                os.rename(staged, self.destination)
                self.stage.rmdir()
        # Core acquires its own Global writer lock. The retained Inbox lock
        # prevents a second transport or recovery in this non-reentrant window.
        core_preview = operation.preview()
        result = operation.apply()
        with authority_write_locks((global_root,)):
            if _verify_committed(self.workspace, self.destination, self.raw_inventory) is None:
                raise ValueError("Core hat die verarbeitete Quelle nicht exakt bestätigt.")
            if _inventory(self.raw)[0] != self.raw_inventory:
                raise ValueError("Raw-Paket wurde vor der Bereinigung verändert.")
            self.consumed.mkdir()
            os.rename(self.raw, _container_package(self.consumed, self.name))
            _remove_owned(self.consumed, self.name, self.raw_inventory)
            if self.backup.exists():
                _remove_owned(self.backup, self.name, self.old_inventory)
            (self.inbox / INBOX_JOURNAL).unlink()
            (self.workspace / WORKSPACE_JOURNAL).unlink()
            return {"status": "processed", "transport": "inbox", "kind": self.kind,
                    "source_link_id": core_preview["source_link_id"], "receipt_id": result.get("receipt_id"),
                    "message": "Technisch verarbeitet und durch Core-Beleg geprüft; keine Wissensfreigabe."}


def inbox_journal_pending(workspace: Path, inbox: Path | None) -> bool:
    return (Path(workspace) / WORKSPACE_JOURNAL).exists() or bool(inbox and (Path(inbox) / INBOX_JOURNAL).exists())


def _load_recovery_record(workspace: Path, inbox: Path):
    copies = []
    for path in (inbox / INBOX_JOURNAL, workspace / WORKSPACE_JOURNAL):
        if path.exists():
            copies.append(_read_regular(path, MAX_JOURNAL_BYTES))
    if not copies or any(copy != copies[0] for copy in copies):
        raise ValueError("Inbox-Journale fehlen oder stimmen nicht überein.")
    record = json.loads(copies[0])
    fields = {"schema", "workspace", "inbox", "package", "kind", "raw", "old", "workspace_sha256"}
    if (not isinstance(record, dict) or set(record) not in (fields, fields | {"access"})
            or record["schema"] != "owledge.inbox-import/1" or record["workspace"] != str(workspace)
            or record["inbox"] != str(inbox) or record["kind"] not in {"new", "repeat", "changed"}
            or record.get("access") not in {None, "restricted", "shared"}):
        raise ValueError("Inbox-Journalbindung ist ungültig.")
    _package_name(record["package"])
    _validate_inventory(record["raw"])
    _validate_inventory(record["old"], optional=True)
    if ((record["kind"] == "new") != (record["old"] is None)
            or record["kind"] in {"repeat", "changed"} and record["old"] is None
            or not isinstance(record["workspace_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", record["workspace_sha256"])):
        raise ValueError("Inbox-Journalzustand ist ungültig.")
    return record, copies[0]


def recover_inbox_import(workspace: Path, inbox: Path):
    from .local_setup import _unlinked_path
    from owledge_core.project_io import authority_write_locks
    workspace, inbox = _unlinked_path(workspace), _unlinked_path(inbox)
    with authority_write_locks((inbox,)):
        return _recover_inbox_with_inbox_lock(workspace, inbox)


def _recover_inbox_with_inbox_lock(workspace: Path, inbox: Path):
    from .local_setup import _unlinked_path
    from owledge_core.project_io import authority_write_locks
    global_root = workspace / "global"
    with authority_write_locks((global_root,)):
        _unlinked_path(inbox / "raw")
        _unlinked_path(inbox / "processed")
        record, encoded = _load_recovery_record(workspace, inbox)
        name = record["package"]
        raw, destination, stage, backup, consumed = _paths(workspace, inbox, name)
        probe = destination if destination.exists() else raw
        _recovery_owner_preflight(workspace, probe, record.get("access"))
    # Keep the Inbox lock while Core recovery acquires Global itself; release
    # the transport's Global lock before entering that non-reentrant writer.
    if (workspace / ".owledge/source-registration.json").exists():
        recover_import(workspace)
    with authority_write_locks((global_root,)):
        current_record, current_encoded = _load_recovery_record(workspace, inbox)
        if current_record != record or current_encoded != encoded:
            raise ValueError("Inbox-Journal wurde während Core-Recovery verändert.")
        committed = _verify_committed(workspace, destination, record["raw"]) is not None
        if not committed:
            if sha256(_read_regular(workspace / "workspace.json", 65_536)).hexdigest() != record["workspace_sha256"]:
                raise ValueError("Workspace wurde seit Beginn des Inbox-Transports verändert.")
            if not raw.exists() or _inventory(raw)[0] != record["raw"]:
                raise ValueError("Raw-Paket fehlt oder wurde verändert; keine Rücknahme möglich.")
            if consumed.exists() and any(consumed.iterdir()):
                raise ValueError("Raw-Bereinigung ohne bestätigte Core-Aufnahme ist ungültig.")
            destination_inventory = _inventory(destination)[0] if destination.exists() else None
            backup_package = _container_package(backup, name)
            backup_inventory = None
            backup_empty = backup.exists() and not any(backup.iterdir())
            if backup.exists() and not backup_empty:
                if not backup_package.exists():
                    raise ValueError("Inbox-Backup enthält fremde Dateien.")
                backup_inventory = _inventory(backup_package)[0]
                if backup_inventory != record["old"] or sorted(path.name for path in backup.iterdir()) != [name]:
                    raise ValueError("Inbox-Backup unterscheidet sich vom journalgebundenen alten Paket.")
            if record["kind"] == "new":
                if backup.exists() or destination_inventory is not None and destination_inventory != record["raw"]:
                    raise ValueError("Neues Processed-Ziel ist kein journalgebundener Zustand.")
            elif record["kind"] == "repeat":
                if backup.exists() or destination_inventory != record["old"] or record["old"] != record["raw"]:
                    raise ValueError("Wiederholtes Processed-Ziel wurde verändert.")
            else:
                if backup_inventory is not None:
                    if destination_inventory is not None and destination_inventory != record["raw"]:
                        raise ValueError("Revidiertes Processed-Ziel ist kein journalgebundener Zustand.")
                elif destination_inventory != record["old"]:
                    raise ValueError("Altes Processed-Ziel wurde vor der Rücknahme verändert.")
            if stage.exists():
                _remove_partial_owned(stage, name, record["raw"])
            if consumed.exists():
                consumed.rmdir()
            if record["kind"] == "new" and destination.exists():
                stage.mkdir(exist_ok=False)
                os.rename(destination, _container_package(stage, name))
                _remove_owned(stage, name, record["raw"])
            elif record["kind"] == "changed" and backup_inventory is not None:
                if destination.exists():
                    stage.mkdir(exist_ok=False)
                    os.rename(destination, _container_package(stage, name))
                    _remove_owned(stage, name, record["raw"])
                os.rename(backup_package, destination)
                backup.rmdir()
            elif backup_empty:
                backup.rmdir()
            final_destination = _inventory(destination)[0] if destination.exists() else None
            if ((record["kind"] == "new" and final_destination is not None)
                    or (record["kind"] in {"repeat", "changed"} and final_destination != record["old"])):
                raise ValueError("Processed-Ziel wurde nicht exakt wiederhergestellt.")
        else:
            consumed_empty = consumed.exists() and not any(consumed.iterdir())
            if raw.exists():
                if _inventory(raw)[0] != record["raw"]:
                    raise ValueError("Raw-Paket wurde nach bestätigter Aufnahme verändert.")
                if consumed.exists() and not consumed_empty:
                    raise ValueError("Inbox-Bereinigungspfad kollidiert.")
                if consumed_empty:
                    consumed.rmdir()
                consumed.mkdir()
                os.rename(raw, _container_package(consumed, name))
            if consumed.exists():
                _remove_partial_owned(consumed, name, record["raw"])
            if backup.exists():
                if not record["old"]:
                    raise ValueError("Unerwartetes Inbox-Backup nach Core-Aufnahme.")
                _remove_partial_owned(backup, name, record["old"])
            if stage.exists():
                _remove_partial_owned(stage, name, record["raw"])
        for path in (inbox / INBOX_JOURNAL, workspace / WORKSPACE_JOURNAL):
            if path.exists():
                if _read_regular(path, MAX_JOURNAL_BYTES) != encoded:
                    raise ValueError("Inbox-Journal wurde verändert.")
                path.unlink()
        return {"status": "processed" if committed else "restored", "transport": "inbox",
                "message": "Inbox-Transport wiederhergestellt."}
