#!/usr/bin/env python3
"""Fail-soft Claude/Cowork session-close hook for macOS/Linux plugin installs."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


HOOK = "close-runtime-session"


def write_error(message: str, root: pathlib.Path | None = None) -> None:
    try:
        if root and root.exists():
            log_root = root / ".agent-control" / "logs"
        else:
            log_root = pathlib.Path(tempfile.gettempdir()) / "agent-memory-plugin-logs"
        log_root.mkdir(parents=True, exist_ok=True)
        row = {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "hook": HOOK,
            "message": message,
        }
        with (log_root / "plugin-errors.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    except Exception:
        pass


def find_project_root(start: pathlib.Path) -> pathlib.Path:
    explicit = os.environ.get("AGENT_MEMORY_PROJECT_ROOT")
    if explicit:
        root = pathlib.Path(explicit).expanduser().resolve()
        if not (root / "agent-memory").exists():
            raise RuntimeError(f"AGENT_MEMORY_PROJECT_ROOT does not contain agent-memory: {root}")
        if not (root / "PROJECT_CONTEXT.md").exists() and not os.environ.get("AGENT_MEMORY_PROJECT_ROOT_ALLOW_UNINITIALIZED"):
            raise RuntimeError(f"AGENT_MEMORY_PROJECT_ROOT is not initialized. Missing PROJECT_CONTEXT.md: {root}")
        return root

    current = start.resolve()
    while True:
        if (current / "PROJECT_CONTEXT.md").exists() and (current / "agent-memory").exists():
            return current
        if current.parent == current:
            raise RuntimeError("Could not find Agent Memory project root. Run from the project root or set AGENT_MEMORY_PROJECT_ROOT.")
        current = current.parent


def resolve_cli(root: pathlib.Path) -> pathlib.Path:
    local = root / "tools" / "agent_memory_cli.py"
    if local.exists():
        return local
    kit_root = os.environ.get("AGENT_MEMORY_KIT_ROOT")
    if kit_root:
        kit_cli = pathlib.Path(kit_root).expanduser().resolve() / "tools" / "agent_memory_cli.py"
        if kit_cli.exists():
            return kit_cli
    plugin_root = pathlib.Path(__file__).resolve().parents[1]
    repo_candidate = plugin_root.parents[1] if len(plugin_root.parents) > 1 else plugin_root
    repo_cli = repo_candidate / "tools" / "agent_memory_cli.py"
    if repo_cli.exists():
        return repo_cli
    raise RuntimeError("Missing Agent Memory CLI. Copy tools/agent_memory_cli.py into the project or set AGENT_MEMORY_KIT_ROOT.")


def session_id_from_payload(payload: str) -> str:
    event = json.loads(payload or "{}")
    if event.get("session_id"):
        return str(event["session_id"])
    if event.get("transcript_path"):
        return pathlib.Path(str(event["transcript_path"])).stem
    raise RuntimeError("Close hook payload must include session_id or transcript_path.")


def main() -> int:
    root: pathlib.Path | None = None
    try:
        root = find_project_root(pathlib.Path.cwd())
        cli = resolve_cli(root)
        capture_mode = os.environ.get("AGENT_MEMORY_CAPTURE_MODE", "standard")
        payload = sys.stdin.read() or "{}"
        session_id = session_id_from_payload(payload)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            handle.write(payload)
            event_path = pathlib.Path(handle.name)
        try:
            subprocess.run(
                [
                    sys.executable,
                    str(cli),
                    "--project-root",
                    str(root),
                    "capture-runtime-event",
                    "--runtime",
                    "claude-cowork",
                    "--capture-mode",
                    capture_mode,
                    "--event-file",
                    str(event_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(cli),
                    "--project-root",
                    str(root),
                    "close-runtime-session",
                    "--runtime",
                    "claude-cowork",
                    "--session-id",
                    session_id,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        finally:
            event_path.unlink(missing_ok=True)
    except Exception as exc:
        write_error(str(exc), root)
        if os.environ.get("AGENT_MEMORY_STRICT_HOOKS") == "1":
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
