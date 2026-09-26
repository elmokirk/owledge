"""Read unmanaged Markdown as inert, byte-exact source observations."""

from __future__ import annotations

import hashlib
import os
import re
import stat
from pathlib import Path
from typing import NamedTuple

from owledge_core.contracts import SourceFileSnapshot, SourceSnapshot, SourceSnapshotError


__all__: tuple[str, ...] = ()


class _PathFacts(NamedTuple):
    resolved: Path
    file_id: tuple[int, int]
    nlink: int
    size_bytes: int
    mtime_ns: int
    mode: int
    is_symlink: bool
    is_reparse: bool


_STABLE_FACT_FIELDS = (
    "resolved",
    "file_id",
    "nlink",
    "size_bytes",
    "mtime_ns",
    "mode",
    "is_symlink",
    "is_reparse",
)

_STABLE_DIRECTORY_FACT_FIELDS = tuple(
    field for field in _STABLE_FACT_FIELDS if field != "size_bytes"
)


def _path_facts(path: Path) -> _PathFacts:
    observed = path.lstat()
    attributes = getattr(observed, "st_file_attributes", 0)
    is_symlink = path.is_symlink()
    return _PathFacts(
        resolved=path.resolve(strict=True),
        file_id=(int(observed.st_dev), int(observed.st_ino)),
        nlink=int(observed.st_nlink),
        size_bytes=int(observed.st_size),
        mtime_ns=int(observed.st_mtime_ns),
        mode=int(observed.st_mode),
        is_symlink=is_symlink,
        is_reparse=is_symlink
        or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)),
    )


def _is_reparse_path(path: Path) -> bool:
    try:
        facts = _path_facts(path)
    except (FileNotFoundError, OSError) as error:
        raise SourceSnapshotError("source_unavailable", "source path is unavailable") from error
    return facts.is_reparse


def _read_stable_file(path: Path, root: Path) -> bytes:
    try:
        before = _path_facts(path)
        if before.is_reparse or before.nlink != 1 or not stat.S_ISREG(before.mode):
            raise SourceSnapshotError("source_unsafe", "source file is linked or not a regular file")
        before.resolved.relative_to(root)
        content = path.read_bytes()
        after = _path_facts(path)
    except SourceSnapshotError:
        raise
    except ValueError as error:
        raise SourceSnapshotError("path_escape", "source file escaped its root") from error
    except (FileNotFoundError, OSError) as error:
        raise SourceSnapshotError("source_unavailable", "source file is unavailable") from error
    if any(
        getattr(before, field) != getattr(after, field)
        for field in _STABLE_FACT_FIELDS
    ):
        raise SourceSnapshotError("source_unstable", "source changed while it was read")
    if len(content) != before.size_bytes:
        raise SourceSnapshotError("source_unstable", "source size changed while it was read")
    return content


def _stable_directory_entries(
    directory: Path,
    root: Path,
) -> tuple[tuple[str, ...], _PathFacts]:
    try:
        before = _path_facts(directory)
        if before.is_reparse:
            raise SourceSnapshotError("source_unsafe", "source directory is linked")
        before.resolved.relative_to(root)
        with os.scandir(directory) as iterator:
            names = tuple(sorted((entry.name for entry in iterator), key=str.casefold))
        after = _path_facts(directory)
    except SourceSnapshotError:
        raise
    except ValueError as error:
        raise SourceSnapshotError("path_escape", "source directory escaped its root") from error
    except (FileNotFoundError, OSError) as error:
        raise SourceSnapshotError("source_unavailable", "source directory is unavailable") from error
    if any(
        getattr(before, field) != getattr(after, field)
        for field in _STABLE_DIRECTORY_FACT_FIELDS
    ):
        raise SourceSnapshotError("source_unstable", "source directory changed during scan")
    return names, after


def _assert_directory_unchanged(
    directory: Path,
    expected: _PathFacts,
    expected_names: tuple[str, ...] | None = None,
) -> None:
    try:
        current = _path_facts(directory)
        current_names = None
        if expected_names is not None:
            with os.scandir(directory) as iterator:
                current_names = tuple(
                    sorted((entry.name for entry in iterator), key=str.casefold)
                )
    except (FileNotFoundError, OSError) as error:
        raise SourceSnapshotError("source_unstable", "source directory changed during scan") from error
    if any(
        getattr(expected, field) != getattr(current, field)
        for field in _STABLE_DIRECTORY_FACT_FIELDS
    ) or (expected_names is not None and current_names != expected_names):
        raise SourceSnapshotError("source_unstable", "source directory changed during scan")


def _validate_source_root(root: Path) -> Path:
    candidate = Path(root).absolute()
    try:
        if not candidate.exists() or not candidate.is_dir():
            raise SourceSnapshotError("source_unavailable", "source directory is unavailable")
        components = (candidate, *candidate.parents)
        if any(_is_reparse_path(component) for component in components):
            raise SourceSnapshotError("source_unsafe", "source path crosses a link")
        return candidate.resolve(strict=True)
    except SourceSnapshotError:
        raise
    except (FileNotFoundError, OSError) as error:
        raise SourceSnapshotError("source_unavailable", "source directory is unavailable") from error


class MarkdownSourceConnector:
    """One-shot scanner with no write, parse, execution, or trust capability."""

    def __init__(self, source_root: Path) -> None:
        self._source_root = Path(source_root)

    def scan(self) -> SourceSnapshot:
        candidate = self._source_root.absolute()
        try:
            candidate_facts = _path_facts(candidate)
        except (FileNotFoundError, OSError) as error:
            raise SourceSnapshotError("source_unavailable", "source path is unavailable") from error
        if candidate_facts.is_reparse:
            raise SourceSnapshotError("source_unsafe", "source path crosses a link")
        if stat.S_ISREG(candidate_facts.mode):
            if any(_is_reparse_path(parent) for parent in candidate.parents):
                raise SourceSnapshotError("source_unsafe", "source path crosses a link")
            selected = candidate_facts.resolved
            if selected.suffix.casefold() != ".md":
                raise SourceSnapshotError("source_ambiguous", "source has no Markdown documents")
            source_file = SourceFileSnapshot.from_bytes(
                selected.name,
                _read_stable_file(selected, selected),
            )
            path_digest = hashlib.sha256(
                os.path.normcase(str(selected)).encode("utf-8")
            ).hexdigest()[:12]
            slug = re.sub(r"[^a-z0-9]+", "-", selected.stem.casefold()).strip("-") or "document"
            return SourceSnapshot.create(
                f"source:{slug}-{path_digest}", selected, [source_file]
            )
        root = _validate_source_root(self._source_root)
        root_facts = _path_facts(root)
        files: list[SourceFileSnapshot] = []
        pending = [root]
        visited_directories: list[tuple[Path, _PathFacts, tuple[str, ...]]] = []
        try:
            while pending:
                directory = pending.pop()
                names, directory_facts = _stable_directory_entries(directory, root)
                visited_directories.append((directory, directory_facts, names))
                for name in names:
                    _assert_directory_unchanged(directory, directory_facts)
                    path = directory / name
                    if _is_reparse_path(path):
                        raise SourceSnapshotError("source_unsafe", "source contains a link")
                    if path.is_dir():
                        pending.append(path)
                        continue
                    if not path.is_file() or path.suffix.casefold() != ".md":
                        continue
                    relative = path.relative_to(root).as_posix()
                    files.append(
                        SourceFileSnapshot.from_bytes(
                            relative,
                            _read_stable_file(path, root),
                        )
                    )
                _assert_directory_unchanged(directory, directory_facts, names)
            for directory, directory_facts, names in reversed(visited_directories):
                _assert_directory_unchanged(directory, directory_facts, names)
        except SourceSnapshotError:
            raise
        except (FileNotFoundError, OSError) as error:
            raise SourceSnapshotError("source_unavailable", "source scan did not complete") from error
        if not files:
            raise SourceSnapshotError("source_ambiguous", "source has no Markdown documents")
        _assert_directory_unchanged(root, root_facts)
        path_digest = hashlib.sha256(
            os.path.normcase(str(root)).encode("utf-8")
        ).hexdigest()[:12]
        slug = re.sub(r"[^a-z0-9]+", "-", root.name.casefold()).strip("-") or "vault"
        return SourceSnapshot.create(f"source:{slug}-{path_digest}", root, files)
