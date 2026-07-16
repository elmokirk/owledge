"""Run the CI core gate surface locally with the active Python interpreter."""

from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parent.parent
PREFLIGHT_ENV = {**os.environ, "PYTHONPYCACHEPREFIX": str(pathlib.Path(tempfile.gettempdir()) / "owledge-pycache")}
COMPILE_TARGETS = [
    "tools/owledge.py",
    "tools/owledge_mcp.py",
    "tools/owledge_core.py",
    "tools/build_kb_module.py",
    "tools/build_project_folder_kit.py",
    "benchmarks/run_benchmarks.py",
    "plugins/owledge-cowork/scripts/capture-claude-event.py",
    "plugins/owledge-cowork/scripts/close-runtime-session.py",
]
CORE_GATES = [
    "public-docs", "release-trust", "version-contract", "docs-contract",
    "release-contract", "legacy-naming-clean", "standalone-skills",
    "core-platform-neutral", "kb-module", "runtime-adapters",
    "benchmark-kit-ci", "mcp-readonly", "publish-readiness",
]
RELEASE_QA_GATES = ["version-contract", "docs-contract", "release-contract"]


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True, env=PREFLIGHT_ENV)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("release-qa", "core"), default="core")
    args = parser.parse_args()
    run([sys.executable, "-m", "py_compile", *COMPILE_TARGETS])
    for gate in CORE_GATES if args.scope == "core" else RELEASE_QA_GATES:
        run([sys.executable, "tools/owledge.py", "test", gate, "--project-root", "."])
    if args.scope == "core":
        run([sys.executable, "tools/owledge_core.py", "--project-root", ".", "test-contracts"])
        run([sys.executable, "tools/owledge.py", "wikilink-audit", "--project-root", ".", "--check"])
    print(f"CI preflight passed ({args.scope}, Python {sys.version.split()[0]}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
