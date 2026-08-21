#!/usr/bin/env python3
"""Normalize a built sdist to deterministic tar/gzip metadata for local release QA."""
from __future__ import annotations

import argparse
import gzip
import io
import pathlib
import tarfile
import zipfile


DEFAULT_EPOCH = 315532800  # 1980-01-01: valid for ZIP-adjacent release tooling.


def _safe_name(name: str) -> str:
    path = pathlib.PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or not name:
        raise ValueError("archive_member_path_invalid")
    return path.as_posix()


def normalize_sdist(source: pathlib.Path, output: pathlib.Path, *, epoch: int = DEFAULT_EPOCH) -> dict[str, object]:
    if epoch < DEFAULT_EPOCH:
        raise ValueError("epoch_before_zip_safe_minimum")
    if not source.is_file() or source.suffixes[-2:] != [".tar", ".gz"]:
        raise ValueError("sdist_source_invalid")
    output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with tarfile.open(source, "r:gz") as archive:
        members = sorted(archive.getmembers(), key=lambda member: member.name)
        payloads: list[tuple[tarfile.TarInfo, bytes | None]] = []
        for member in members:
            safe_name = _safe_name(member.name)
            normalized = tarfile.TarInfo(safe_name)
            normalized.mode = member.mode
            normalized.type = member.type
            normalized.linkname = member.linkname
            normalized.size = member.size if member.isfile() else 0
            normalized.mtime = epoch
            normalized.uid = 0
            normalized.gid = 0
            normalized.uname = ""
            normalized.gname = ""
            content = archive.extractfile(member).read() if member.isfile() else None
            payloads.append((normalized, content))
    with output.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=epoch, filename="") as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as target:
                for member, content in payloads:
                    target.addfile(member, io.BytesIO(content) if content is not None else None)
                    written += 1
    return {"passed": True, "members": written, "epoch": epoch, "output": output.name}


def normalize_wheel(source: pathlib.Path, output: pathlib.Path, *, epoch: int = DEFAULT_EPOCH) -> dict[str, object]:
    """Normalize ZIP metadata without changing the signed-off wheel payload."""
    if epoch < DEFAULT_EPOCH:
        raise ValueError("epoch_before_zip_safe_minimum")
    if not source.is_file() or source.suffix != ".whl":
        raise ValueError("wheel_source_invalid")
    output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with zipfile.ZipFile(source, "r") as archive:
        members = sorted(archive.infolist(), key=lambda member: member.filename)
        names = [_safe_name(member.filename) for member in members]
        if len(names) != len(set(names)):
            raise ValueError("archive_member_duplicate")
        payloads = [(name, archive.read(member), member.external_attr) for name, member in zip(names, members)]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for name, content, external_attr in payloads:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = external_attr
            target.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            written += 1
    return {"passed": True, "members": written, "epoch": epoch, "output": output.name}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize an Owledge wheel or source distribution for deterministic local release QA.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--epoch", type=int, default=DEFAULT_EPOCH)
    args = parser.parse_args(argv)
    try:
        source = pathlib.Path(args.source)
        result = normalize_wheel(source, pathlib.Path(args.output), epoch=args.epoch) if source.suffix == ".whl" else normalize_sdist(source, pathlib.Path(args.output), epoch=args.epoch)
    except ValueError as exc:
        print('{"passed": false, "error": "' + str(exc) + '"}')
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
