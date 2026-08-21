from __future__ import annotations

import hashlib
import pathlib
import sys
import tarfile
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import normalize_sdist


class V1M10SdistNormalizationTests(unittest.TestCase):
    def _source_archive(self, path: pathlib.Path, *, mtime: int) -> None:
        content = path.with_suffix(".txt")
        content.write_text("same local Core source\n", encoding="utf-8")
        with tarfile.open(path, "w:gz") as archive:
            info = archive.gettarinfo(content, arcname="owledge-0.8.0/source.txt")
            info.mtime = mtime
            with content.open("rb") as handle:
                archive.addfile(info, handle)

    def test_normalized_sdist_has_stable_bytes_and_rejects_unsafe_member_names(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m10-sdist-") as temporary:
            base = pathlib.Path(temporary)
            first, second = base / "first.tar.gz", base / "second.tar.gz"
            self._source_archive(first, mtime=1_700_000_000)
            self._source_archive(second, mtime=1_800_000_000)
            output_a, output_b = base / "a.tar.gz", base / "b.tar.gz"
            self.assertTrue(normalize_sdist.normalize_sdist(first, output_a)["passed"])
            self.assertTrue(normalize_sdist.normalize_sdist(second, output_b)["passed"])
            self.assertEqual(hashlib.sha256(output_a.read_bytes()).hexdigest(), hashlib.sha256(output_b.read_bytes()).hexdigest())

            unsafe = base / "unsafe.tar.gz"
            with tarfile.open(unsafe, "w:gz") as archive:
                info = tarfile.TarInfo("../escape.txt")
                info.size = 0
                archive.addfile(info)
            with self.assertRaisesRegex(ValueError, "archive_member_path_invalid"):
                normalize_sdist.normalize_sdist(unsafe, base / "unsafe-output.tar.gz")

    def test_normalized_wheel_has_stable_bytes_and_rejects_duplicate_members(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v1m10-wheel-") as temporary:
            base = pathlib.Path(temporary)
            first, second = base / "first.whl", base / "second.whl"
            for path, timestamp in ((first, (2024, 1, 2, 3, 4, 6)), (second, (2025, 2, 3, 4, 5, 6))):
                with zipfile.ZipFile(path, "w") as archive:
                    info = zipfile.ZipInfo("tools/owledge.py", date_time=timestamp)
                    archive.writestr(info, b"print('local core')\n")
            output_a, output_b = base / "a.whl", base / "b.whl"
            self.assertTrue(normalize_sdist.normalize_wheel(first, output_a)["passed"])
            self.assertTrue(normalize_sdist.normalize_wheel(second, output_b)["passed"])
            self.assertEqual(hashlib.sha256(output_a.read_bytes()).hexdigest(), hashlib.sha256(output_b.read_bytes()).hexdigest())

            duplicate = base / "duplicate.whl"
            with zipfile.ZipFile(duplicate, "w") as archive:
                archive.writestr("tools/owledge.py", b"first")
                archive.writestr("tools/owledge.py", b"second")
            with self.assertRaisesRegex(ValueError, "archive_member_duplicate"):
                normalize_sdist.normalize_wheel(duplicate, base / "duplicate-output.whl")


if __name__ == "__main__":
    unittest.main()
