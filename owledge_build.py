"""Build hooks that keep the V1 release artifact within its Core boundary."""

from __future__ import annotations

from pathlib import Path

from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist


V1_CORE_TOOL_MODULES = frozenset({
    "__init__.py",
    "owledge.py",
    "owledge_core.py",
    "owledge_adapter_contracts.py",
    "owledge_generic_adapter.py",
    "owledge_null_space.py",
    "owledge_v1_retrieval.py",
    "owledge_v1_lifecycle.py",
    "build_project_folder_kit.py",
})


def is_v1_release_source(path: str) -> bool:
    """Return whether a source-tree path belongs in the bounded V1 archive."""
    parts = Path(path).parts
    return not parts or parts[0] != "tools" or len(parts) == 1 or parts[1] in V1_CORE_TOOL_MODULES


class V1CoreBuildPy(_build_py):
    """Ship only modules required by the V1 public Core surface."""

    def find_package_modules(self, package: str, package_dir: str):
        modules = super().find_package_modules(package, package_dir)
        if package != "tools":
            return modules
        return [module for module in modules if Path(module[2]).name in V1_CORE_TOOL_MODULES]


class V1CoreSdist(_sdist):
    """Keep source archives congruent with the V1 wheel's module boundary."""

    def make_release_tree(self, base_dir: str, files: list[str]) -> None:
        super().make_release_tree(base_dir, [item for item in files if is_v1_release_source(item)])
        sources = Path(base_dir) / "owledge.egg-info" / "SOURCES.txt"
        if sources.is_file():
            kept = [line for line in sources.read_text(encoding="utf-8").splitlines() if is_v1_release_source(line)]
            sources.write_text("\n".join(kept) + "\n", encoding="utf-8")
