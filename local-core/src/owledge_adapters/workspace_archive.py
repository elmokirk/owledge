"""Private Owner-only, same-host workspace backup; no knowledge transformation."""
from __future__ import annotations

from hashlib import sha256
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tempfile
import zipfile
from contextlib import nullcontext

from .local_setup import _unlinked_path, open_workspace
from owledge_core.project_io import authority_write_locks

MAX_FILES = 50_000
MAX_BYTES = 256 * 1024 * 1024
MAX_MANIFEST_BYTES = 16 * 1024 * 1024
SCHEMA = 'owledge.private-workspace-backup/1'
PAIR_SCHEMA = 'owledge.private-paired-workspace-backup/1'


def _safe_name(name):
    if not isinstance(name, str) or not name or len(name.encode('utf8')) > 4096:
        raise ValueError('Invalid backup path')
    parts = name.split('/')
    if (str(PurePosixPath(name)) != name or any(
            part in {'', '.', '..'} or len(part.encode('utf-16-le')) // 2 > 255 or part.endswith(('.', ' '))
            or re.search(r'[\\:<>"|?*\x00-\x1f]', part)
            or part.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(10)), *(f'LPT{i}' for i in range(10))}
            for part in parts)):
        raise ValueError('Unsafe backup path')
    return name


def _read(path, limit):
    path = _unlinked_path(path)
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > limit:
        raise ValueError('Linked, nonregular or oversized backup input')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        data = stream.read(before.st_size + 1)
        after = os.fstat(stream.fileno())
    final = path.stat()
    facts = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_nlink)
    if len(data) > limit or not (facts(before) == facts(opened) == facts(after) == facts(final)):
        raise ValueError('Backup input changed while reading')
    return data, not bool(before.st_mode & stat.S_IWUSR)


def _inventory(root):
    records, folded, total = {}, set(), 0
    pending = [root]
    while pending:
        directory = _unlinked_path(pending.pop())
        for path in sorted(directory.iterdir()):
            path = _unlinked_path(path)
            name = _safe_name(path.relative_to(root).as_posix())
            if name.casefold() in folded:
                raise ValueError('Case-aliased backup paths')
            folded.add(name.casefold())
            if len(folded) > MAX_FILES:
                raise ValueError('Backup entry budget exceeded')
            if path.is_dir():
                pending.append(path)
                continue
            data, readonly = _read(path, MAX_BYTES - total)
            total += len(data)
            records[name] = {'sha256': sha256(data).hexdigest(), 'size': len(data), 'readonly': readonly}
            if len(records) > MAX_FILES:
                raise ValueError('Backup file budget exceeded')
    if 'workspace.json' not in records:
        raise ValueError('Not an Owledge workspace')
    return records


def _destination(path):
    path = _unlinked_path(path.absolute().parent) / path.name
    if os.path.lexists(path) or not path.parent.is_dir():
        raise ValueError('Choose an absent target with an existing parent')
    return path


def _inside(path, root):
    return path == root or root in path.parents


def _pair_records(project: Path, global_workspace: Path):
    project_records, global_records = _inventory(project), _inventory(global_workspace)
    records = {'Project/' + key: value for key, value in project_records.items()}
    records.update({'Global/' + key: value for key, value in global_records.items()})
    if len(records) > MAX_FILES or sum(item['size'] for item in records.values()) > MAX_BYTES:
        raise ValueError('Paired backup exceeds the shared archive budget')
    return records


class WorkspaceArchive:
    def __init__(self, workspace: Path, archive: Path, action: str, *, linked: bool = False,
                 recover: bool = False):
        self.workspace = (workspace.absolute() if action == 'restore' and recover else
                          _destination(workspace) if action == 'restore' else _unlinked_path(workspace.absolute()))
        self.archive = (_destination(archive) if action == 'backup' else _unlinked_path(archive.absolute()))
        self.action = action
        self.linked = linked
        self.recovering = recover
        if action == 'backup':
            _destination(self.archive)
            if _inside(self.archive, self.workspace):
                raise ValueError('Backup must be outside its source workspace')
            _, state = open_workspace(self.workspace)
            if linked:
                from owledge_core.project_io import validate_project_reuse_binding
                if state.get('schema') != 'owledge.private-project-workspace/2':
                    raise ValueError('Paired backup requires the exact registered Project/Global pair')
                self.global_workspace = validate_project_reuse_binding(self.workspace, state)
                if _inside(self.archive, self.global_workspace):
                    raise ValueError('Backup must be outside both linked source workspaces')
                open_workspace(self.global_workspace)
                self.roots = [self.workspace, self.workspace / 'project',
                              self.global_workspace, self.global_workspace / 'global']
            else:
                self.roots = [self.workspace, *(_unlinked_path(self.workspace / item) for item in state['roots'].values())]
            with authority_write_locks(self.roots):
                self.records = _pair_records(self.workspace, self.global_workspace) if linked else _inventory(self.workspace)
            self.manifest = json.dumps({'schema': PAIR_SCHEMA if linked else SCHEMA, 'files': self.records,
                **({'origins': {'project': str(self.workspace), 'global': str(self.global_workspace)}} if linked else {})},
                sort_keys=True).encode('utf8')
            if len(self.manifest) > MAX_MANIFEST_BYTES:
                raise ValueError('Oversized archive manifest')
            self.expected_sha256 = sha256(self.manifest + str(self.archive).encode()).hexdigest()
        elif action == 'restore':
            if not recover:
                _destination(self.workspace)
            if _inside(self.archive, self.workspace):
                raise ValueError('Archive cannot be inside restore target')
            self.raw, _ = _read(self.archive, MAX_BYTES + 64 * 1024 * 1024)
            try:
                self.records, self.contents, self.manifest_data = self._validate_archive()
            except (zipfile.BadZipFile, KeyError, RuntimeError, NotImplementedError) as error:
                raise ValueError('Invalid or unsupported backup archive') from error
            self.linked = self.manifest_data['schema'] == PAIR_SCHEMA
            if linked and not self.linked:
                raise ValueError('Selected archive is not a linked pair')
            if self.linked:
                from owledge_core.project_io import relocate_fixed_project_global_pair
                origins = self.manifest_data['origins']
                self.pair_plan = relocate_fixed_project_global_pair(self.contents,
                    old_project=Path(origins['project']), old_global=Path(origins['global']),
                    new_project=self.workspace / 'Project', new_global=self.workspace / 'Global')
            self.expected_sha256 = sha256(self.raw + str(self.workspace).encode()).hexdigest()
        else:
            raise ValueError('Unknown archive action')

    def _validate_archive(self):
        with zipfile.ZipFile(io.BytesIO(self.raw)) as archive:
            entries = archive.infolist()
            names = [item.filename for item in entries]
            if len(names) > MAX_FILES + 1 or len(set(name.casefold() for name in names)) != len(names):
                raise ValueError('Duplicate or excessive archive entries')
            if any(item.is_dir() or stat.S_ISLNK(item.external_attr >> 16) or item.flag_bits & 1 for item in entries):
                raise ValueError('Unsupported archive entry')
            if sum(item.file_size for item in entries) > MAX_BYTES + 16 * 1024 * 1024:
                raise ValueError('Archive expansion budget exceeded')
            info = archive.getinfo('manifest.json')
            if info.file_size > MAX_MANIFEST_BYTES:
                raise ValueError('Oversized archive manifest')
            manifest = json.loads(archive.read(info))
            pair = isinstance(manifest, dict) and manifest.get('schema') == PAIR_SCHEMA
            if (not isinstance(manifest, dict) or set(manifest) != ({'schema', 'files', 'origins'} if pair else {'schema', 'files'})
                    or manifest['schema'] not in {SCHEMA, PAIR_SCHEMA}):
                raise ValueError('Unknown backup manifest')
            records = manifest['files']
            required = {'Project/workspace.json', 'Global/workspace.json'} if pair else {'workspace.json'}
            if not isinstance(records, dict) or not required.issubset(records) or len(records) > MAX_FILES:
                raise ValueError('Invalid backup inventory')
            if pair and (not isinstance(manifest['origins'], dict) or set(manifest['origins']) != {'project', 'global'}
                    or any(not isinstance(value, str) or not Path(value).is_absolute() for value in manifest['origins'].values())
                    or any(not name.startswith(('Project/', 'Global/')) for name in records)):
                raise ValueError('Invalid paired backup origins or paths')
            expected = {'manifest.json'} | {'files/' + _safe_name(name) for name in records}
            if set(names) != expected:
                raise ValueError('Unexpected or missing archive entry')
            folded = {name.casefold() for name in records}
            if len(folded) != len(records) or any(str(parent).casefold() in folded for name in records for parent in PurePosixPath(name).parents if str(parent) != '.'):
                raise ValueError('Aliased or conflicting archive paths')
            contents, total = {}, 0
            for name, record in records.items():
                if (not isinstance(record, dict) or set(record) != {'sha256', 'size', 'readonly'}
                        or type(record['size']) is not int or record['size'] < 0
                        or type(record['readonly']) is not bool or not isinstance(record['sha256'], str)
                        or not re.fullmatch('[0-9a-f]{64}', record['sha256'])):
                    raise ValueError('Invalid backup file record')
                total += record['size']
                if total > MAX_BYTES or archive.getinfo('files/' + name).file_size != record['size']:
                    raise ValueError('Backup byte budget or size mismatch')
                data = archive.read('files/' + name)
                if sha256(data).hexdigest() != record['sha256']:
                    raise ValueError('Backup checksum mismatch')
                contents[name] = data
            return records, contents, manifest

    def preview(self):
        return {'status': 'preview', 'action': self.action, 'files': len(self.records),
                'bytes': sum(item['size'] for item in self.records.values()),
                'expected_sha256': self.expected_sha256, 'linked': self.linked,
                **({'pair': {key: value for key, value in self.pair_plan.items() if key != 'changes'}}
                   if self.action == 'restore' and self.linked else {}),
                'message': 'Lokale Dateisicherung inklusive privater Originale. Neues Ziel, kein Überschreiben. Quellpfade unverändert; leere Ordner, ACLs und Laufzeitinstallation nicht enthalten.'}

    def apply(self, expected_sha256: str | None = None):
        if expected_sha256 is not None and expected_sha256 != self.expected_sha256:
            raise ValueError('Backup or restore preview changed')
        if self.action == 'backup':
            with authority_write_locks(self.roots):
                current = _pair_records(self.workspace, self.global_workspace) if self.linked else _inventory(self.workspace)
                if current != self.records:
                    raise ValueError('Workspace changed since preview')
                _destination(self.archive)
                descriptor, temporary = tempfile.mkstemp(prefix='.owledge-backup-', dir=self.archive.parent)
                stage = Path(temporary)
                try:
                    with os.fdopen(descriptor, 'w+b') as output:
                        with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                            archive.writestr('manifest.json', self.manifest)
                            for name in self.records:
                                path = (self.workspace / name.removeprefix('Project/') if name.startswith('Project/') else
                                        self.global_workspace / name.removeprefix('Global/')) if self.linked else self.workspace / name
                                data, _ = _read(path, MAX_BYTES)
                                if sha256(data).hexdigest() != self.records[name]['sha256']:
                                    raise ValueError('Workspace changed during backup')
                                archive.writestr('files/' + name, data)
                        output.flush()
                        os.fsync(output.fileno())
                    current = _pair_records(self.workspace, self.global_workspace) if self.linked else _inventory(self.workspace)
                    if current != self.records:
                        raise ValueError('Workspace changed during backup')
                    _destination(self.archive)
                    # Same-directory link publishes complete bytes exclusively;
                    # removing the staging name leaves an ordinary single-link file.
                    os.link(stage, self.archive)
                finally:
                    stage.unlink(missing_ok=True)
        else:
            if self.linked:
                return self._apply_pair_restore()
            _destination(self.workspace)
            current, _ = _read(self.archive, MAX_BYTES + 64 * 1024 * 1024)
            if current != self.raw:
                raise ValueError('Archive changed since preview')
            stage = Path(tempfile.mkdtemp(prefix='.owledge-restore-', dir=self.workspace.parent))
            try:
                for name, data in self.contents.items():
                    path = stage / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                    if self.records[name]['readonly']:
                        path.chmod(stat.S_IREAD)
                open_workspace(stage)
                from owledge_core.project_io import require_settings_healthy
                from owledge_core.artifacts import parse_managed_markdown
                for local_root in (stage / "project", stage / "global"):
                    if (local_root / ".owledge/authority.md").exists():
                        authority_path = local_root / ".owledge/authority.md"
                        if authority_path.stat().st_size > 1_048_576:
                            raise ValueError("Restored authority exceeds its bounded control limit")
                        with authority_path.open("rb") as handle:
                            raw_authority = handle.read(1_048_577)
                        if len(raw_authority) > 1_048_576:
                            raise ValueError("Restored authority exceeds its bounded control limit")
                        header = parse_managed_markdown(".owledge/authority.md", raw_authority.decode("utf-8"),
                                                        encoded_document=raw_authority)
                        require_settings_healthy(local_root, header.authority_id)
                if _inventory(stage) != self.records:
                    raise ValueError('Restored inventory differs')
                _destination(self.workspace)
                stage.rename(self.workspace)
            finally:
                if stage.exists():
                    for path in stage.rglob('*'):
                        if path.is_file():
                            path.chmod(stat.S_IREAD | stat.S_IWRITE)
                    shutil.rmtree(stage)
        return {'status': 'ready', 'action': self.action, 'files': len(self.records),
                'bytes': sum(item['size'] for item in self.records.values()),
                'message': 'Sicherung erstellt.' if self.action == 'backup' else 'In neues Verzeichnis wiederhergestellt; jetzt doctor und Wissen prüfen.'}

    def _pair_paths(self):
        suffix = sha256(str(self.workspace).encode('utf-8')).hexdigest()[:24]
        parent = self.workspace.parent
        return (parent / f'.owledge-pair-restore-{suffix}.json',
                parent / f'.owledge-pair-stage-{suffix}',
                Path('.owledge/paired-restore.json'))

    def _pair_payloads(self):
        payloads = {}
        marker = json.dumps({'schema': 'owledge.paired-restore/1',
            'expected_sha256': self.expected_sha256,
            'archive_sha256': sha256(self.raw).hexdigest(),
            'target': str(self.workspace)}, sort_keys=True).encode('utf-8')
        payloads['.owledge/paired-restore.json'] = marker
        payloads.update(self.contents)
        payloads.update(self.pair_plan['changes'])
        return payloads

    def _pair_journal(self):
        return {'schema': 'owledge.paired-restore-journal/1',
                'target': str(self.workspace), 'archive': str(self.archive),
                'archive_sha256': sha256(self.raw).hexdigest(),
                'expected_sha256': self.expected_sha256,
                'old_project': self.pair_plan['old_project'],
                'old_global': self.pair_plan['old_global']}

    def _complete_pair_stage(self, stage: Path):
        """Redo only missing atomically staged archive members; never replace a changed member."""
        if not stage.exists():
            stage.mkdir()
        if not stage.is_dir() or stage.is_symlink():
            raise ValueError('Paired restore stage is not an ordinary directory')
        payloads = self._pair_payloads()
        expected_directories = {'.owledge-partials'}
        for name in payloads:
            parts = Path(name).parts
            expected_directories.update(str(Path(*parts[:index])).replace('\\', '/')
                                        for index in range(1, len(parts)))
        pending, entries, seen = [stage], 0, set()
        while pending:
            directory = pending.pop()
            for path in directory.iterdir():
                entries += 1
                if entries > MAX_FILES + 16:
                    raise ValueError('Paired restore stage entry budget exceeded')
                relative = path.relative_to(stage).as_posix()
                seen.add(relative)
                if path.is_symlink() or getattr(path.lstat(), 'st_file_attributes', 0) & 0x400:
                    raise ValueError('Paired restore stage contains a linked entry')
                if relative == '.owledge-partials':
                    if not path.is_dir():
                        raise ValueError('Paired restore partial directory is invalid')
                    partial_names = {sha256(name.encode('utf-8')).hexdigest() + '.part': len(data)
                                     for name, data in payloads.items()}
                    partial_count = 0
                    for partial in path.iterdir():
                        partial_count += 1
                        seen.add(partial.relative_to(stage).as_posix())
                        if partial_count > len(payloads) or partial.name not in partial_names:
                            raise ValueError('Paired restore contains an unrelated partial member')
                        _unlinked_path(partial)
                        facts = partial.stat()
                        if not stat.S_ISREG(facts.st_mode) or facts.st_nlink != 1 or facts.st_size > partial_names[partial.name]:
                            raise ValueError('Paired restore partial member is invalid')
                    continue
                if path.is_dir():
                    if relative not in expected_directories:
                        raise ValueError('Paired restore stage contains an unrelated directory')
                    pending.append(path)
                elif relative in payloads:
                    observed, _ = _read(path, len(payloads[relative]))
                    if observed != payloads[relative]:
                        raise ValueError('Paired restore staged member changed')
                else:
                    raise ValueError('Paired restore stage contains an unrelated member')
        if seen and not (stage / '.owledge/paired-restore.json').is_file():
            marker_partial = '.owledge-partials/' + sha256(
                b'.owledge/paired-restore.json').hexdigest() + '.part'
            if not seen.issubset({'.owledge', '.owledge-partials', marker_partial}):
                raise ValueError('Paired restore stage lacks its exact recovery marker')
        partials = stage / '.owledge-partials'
        if not partials.exists():
            partials.mkdir()
        if not partials.is_dir() or partials.is_symlink():
            raise ValueError('Paired restore partial directory is invalid')
        for name, data in payloads.items():
            path = stage / name
            path.parent.mkdir(parents=True, exist_ok=True)
            _unlinked_path(path.parent)
            if os.path.lexists(path):
                observed, _ = _read(path, len(data))
                if observed != data:
                    raise ValueError('Paired restore staged member changed')
                continue
            temporary = partials / (sha256(name.encode('utf-8')).hexdigest() + '.part')
            if os.path.lexists(temporary):
                _unlinked_path(temporary)
                if not temporary.is_file():
                    raise ValueError('Paired restore partial member is invalid')
                temporary.unlink()
            with temporary.open('xb') as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            if name in self.records and self.records[name]['readonly']:
                path.chmod(stat.S_IREAD)
        if any(partials.iterdir()):
            raise ValueError('Paired restore contains an unrelated partial member')
        partials.rmdir()

    def _verify_pair(self, root: Path, *, allow_finished_marker: bool = False):
        def names(directory: Path, limit: int):
            found = set()
            for item in directory.iterdir():
                found.add(item.name)
                if len(found) > limit:
                    raise ValueError('Paired restore root contains excessive entries')
            return found
        if (names(root, 3) != {'Project', 'Global', '.owledge'}
                or names(root / '.owledge', 1) !=
                   ({'paired-restore.json'} if (root / '.owledge/paired-restore.json').exists() else set())):
            raise ValueError('Paired restore root contains unrelated entries')
        payloads = self._pair_payloads()
        expected = {name: {'sha256': sha256(data).hexdigest(), 'size': len(data)}
                    for name, data in payloads.items()}
        observed = _inventory(root / 'Project')
        observed = {'Project/' + name: value for name, value in observed.items()}
        observed.update({'Global/' + name: value for name, value in _inventory(root / 'Global').items()})
        marker = root / '.owledge/paired-restore.json'
        if marker.is_file():
            data, _ = _read(marker, 4096)
            observed['.owledge/paired-restore.json'] = {'sha256': sha256(data).hexdigest(), 'size': len(data)}
        elif allow_finished_marker:
            expected.pop('.owledge/paired-restore.json')
        else:
            raise ValueError('Paired restore marker is missing before readback')
        if set(observed) != set(expected) or any(
                observed[name]['sha256'] != record['sha256'] or observed[name]['size'] != record['size']
                for name, record in expected.items()):
            raise ValueError('Paired restore readback differs from the exact archive and relocation plan')

    def _recover_pair_restore(self):
        journal_path, stage, marker_relative = self._pair_paths()
        raw, _ = _read(journal_path, 4096)
        if json.loads(raw) != self._pair_journal():
            raise ValueError('Paired restore journal differs from preview')
        current, _ = _read(self.archive, MAX_BYTES + 64 * 1024 * 1024)
        if current != self.raw:
            raise ValueError('Paired archive changed before recovery')
        if os.path.lexists(self.workspace):
            if stage.exists():
                raise ValueError('Paired stage and target both exist; inspect before recovery')
            self._verify_pair(self.workspace, allow_finished_marker=True)
        else:
            self._complete_pair_stage(stage)
            self._verify_pair(stage)
            _destination(self.workspace)
            stage.rename(self.workspace)
            self._verify_pair(self.workspace)
        marker = self.workspace / marker_relative
        from owledge_core.project_io import paired_restore_readback, require_settings_healthy
        validation = paired_restore_readback(self.workspace) if marker.exists() else nullcontext()
        with validation:
            for workspace, authority_root, authority_id in (
                    (self.workspace / 'Project', 'project', self.pair_plan['project_authority_id']),
                    (self.workspace / 'Global', 'global', 'user-global:source-access')):
                open_workspace(workspace)
                require_settings_healthy(workspace / authority_root, authority_id)
        if marker.exists():
            marker.unlink()
        journal_path.unlink()
        return {'status': 'ready', 'action': 'restore', 'linked': True,
                'expected_sha256': self.expected_sha256,
                'pair': {key: value for key, value in self.pair_plan.items() if key != 'changes'},
                'files': len(self.records),
                'bytes': sum(item['size'] for item in self.records.values()),
                'message': 'The fixed Project/Global pair is restored; regrant suspended cross-authority readers explicitly.'}

    def _apply_pair_restore(self):
        journal_path, stage, marker_relative = self._pair_paths()
        _destination(self.workspace)
        if journal_path.exists() or os.path.lexists(stage):
            raise ValueError('Recover the interrupted paired restore before a new apply')
        current, _ = _read(self.archive, MAX_BYTES + 64 * 1024 * 1024)
        if current != self.raw:
            raise ValueError('Paired archive changed after preview')
        journal = json.dumps(self._pair_journal(), sort_keys=True).encode('utf-8')
        if len(journal) > 4096:
            raise ValueError('Paired restore journal exceeds its bound')
        with journal_path.open('xb') as handle:
            handle.write(journal)
            handle.flush()
            os.fsync(handle.fileno())
        stage.mkdir()
        self._complete_pair_stage(stage)
        return self._recover_pair_restore()

    def recover(self):
        if self.action != 'restore' or not self.linked:
            raise ValueError('Only an interrupted linked restore has this recovery path')
        return self._recover_pair_restore()
