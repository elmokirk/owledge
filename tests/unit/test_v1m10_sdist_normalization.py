from __future__ import annotations

import hashlib
import pathlib
import sys
import tarfile
import tempfile
import unittest


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


if __name__ == "__main__":
    unittest.main()
