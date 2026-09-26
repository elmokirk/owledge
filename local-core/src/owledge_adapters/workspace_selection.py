"""Private local CLI selection, separate from canonical workspace knowledge."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat


def default_config_path() -> Path:
    override = os.environ.get("OWLEDGE_LOCAL_CONFIG")
    if override:
        return Path(override).expanduser().absolute()
    base = os.environ.get("LOCALAPPDATA") if os.name == "nt" else os.environ.get("XDG_CONFIG_HOME")
    return (Path(base) if base else Path.home() / ".config") / "owledge" / "local-workspace.json"


def read_selection(path: Path) -> dict[str, str]:
    path = Path(path)
    if not path.exists():
        raise ValueError("Kein Workspace gespeichert. Führe setup aus oder wähle --workspace.")
    if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode) or path.stat().st_size > 4096:
        raise ValueError("Gespeicherte Workspace-Auswahl ist ungültig.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Gespeicherte Workspace-Auswahl ist ungültig.") from error
    if (not isinstance(value, dict) or set(value) not in ({"schema", "workspace"}, {"schema", "workspace", "inbox"})
            or value.get("schema") != "owledge.local-selection/1"
            or not isinstance(value.get("workspace"), str) or not Path(value["workspace"]).is_absolute()
            or "inbox" in value and (not isinstance(value["inbox"], str) or not Path(value["inbox"]).is_absolute())):
        raise ValueError("Gespeicherte Workspace-Auswahl ist ungültig.")
    return value


def save_selection(path: Path, workspace: Path, inbox: Path | None = None) -> None:
    path = Path(path)
    if path.exists() or path.is_symlink():
        old = read_selection(path)
    else:
        old = {}
    value = {"schema": "owledge.local-selection/1", "workspace": str(workspace.absolute())}
    if inbox is not None:
        value["inbox"] = str(inbox.absolute())
    elif old.get("workspace") == value["workspace"] and "inbox" in old:
        value["inbox"] = old["inbox"]
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise ValueError("Konfigurationsverzeichnis darf keine Verknüpfung sein.")
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise ValueError("Konfigurationsspeicherung ist bereits ausstehend.")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
