"""Private source-local Owner CLI. Not a public package entry point."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import sys
from pathlib import Path
from typing import TextIO
from .workspace_selection import default_config_path, read_selection, save_selection

from .local_setup import OwnerWorkspaceSetup, OwnerWorkspaceUpgrade, workspace_health, open_workspace, record_workspace_trace
from .owner_journey import WorkspaceOwnerJourney, LocalOwnerHost

__all__: tuple[str, ...] = ()


def _run_native(args, outgoing: TextIO, selection: dict[str, str]) -> int:
    def emit(result: dict[str, object]) -> None:
        if args.json:
            outgoing.write(json.dumps(result, ensure_ascii=False) + "\n")
        elif args.verb == "search":
            outgoing.write(f"Suche: {result.get('status')} — {result.get('message', '')}\n")
            for item in result.get("reviewed", []):
                label = ("Aufgezeichnete Möglichkeit" if item.get("record_status") == "possibility" else
                         "Aufgezeichnetes Signal" if item.get("record_status") == "signal" else "Freigegeben")
                outgoing.write(f"{label}: {item.get('name')} — {item.get('excerpt', '')}\n")
            for hit in result.get("citations", []):
                outgoing.write(f"Quelle: {hit['file']} (Originalauszug, unbestätigt)\n"
                               f"Quellen-Link: {hit.get('source_link_id')}\n"
                               f"Relative Datei: {hit.get('relative_path')}\n{hit['excerpt']}\n")
            for item in result.get("unreadable_source_files", []):
                outgoing.write(f"Nicht als UTF-8 lesbar: {item['source']}/{item['relative_path']}; "
                               "Original als UTF-8 bereitstellen und erneut registrieren.\n")
            if result.get("continuation"):
                outgoing.write("Weitere Treffer verfügbar; mit --cursor aus der JSON-Ausgabe fortsetzen.\n")
        else:
            outgoing.write(f"{result.get('status')}: {result.get('message', '')}\n")
            for key in ("workspace", "source", "package", "files", "bytes", "source_access"):
                if key in result:
                    outgoing.write(f"{key}: {result[key]}\n")
            for item in result.get("packages", []):
                outgoing.write(f"Paket {item.get('package')}: {item.get('status')} ({item.get('files', 0)} Dateien)\n")
        outgoing.flush()

    workspace = Path(args.workspace)
    if args.verb == "ingest":
        from .ingest import InboxImport, inbox_journal_pending, recover_inbox_import
        inbox_value = args.inbox or selection.get("inbox")
        if not inbox_value:
            raise ValueError("Keine Inbox konfiguriert. Verwende setup --inbox oder ingest --inbox.")
        inbox = Path(inbox_value).absolute()
        configured_inbox = (args.inbox is None and selection.get("workspace") == str(workspace)
                            and selection.get("inbox") == str(inbox))
        apply_authorized = args.yes or configured_inbox
        if args.recover:
            if args.preview:
                emit({"status": "preview", "message": "Ausstehende Inbox-Aufnahme wiederherstellen."})
                return 0
            if not apply_authorized:
                emit({"status": "needs_confirmation", "message": "Mit --yes die Inbox-Wiederherstellung starten."})
                return 2
            emit(recover_inbox_import(workspace, inbox))
            return 0
        if inbox_journal_pending(workspace, inbox):
            raise ValueError("Inbox-Aufnahme unterbrochen. Führe ingest --recover --yes aus.")
        raw = inbox / "raw"
        if not raw.is_dir() or raw.is_symlink():
            raise ValueError("Die Inbox benötigt ein reguläres raw-Verzeichnis.")
        packages = []
        for package in sorted(raw.iterdir(), key=lambda path: path.name.casefold()):
            try:
                operation = InboxImport(workspace, inbox, package)
                result = operation.preview() if args.preview or not apply_authorized else operation.apply()
                packages.append({"package": package.name, **result})
            except (ValueError, OSError) as error:
                packages.append({"package": package.name, "status": "needs_attention", "message": str(error)})
                emit({"status": "needs_attention", "message": "Inbox-Aufnahme angehalten; vorherige Pakete bleiben gebucht.",
                      "packages": packages, "completed": len(packages) - 1})
                return 1
        if not args.preview and not apply_authorized:
            emit({"status": "needs_confirmation", "message": "Inbox geprüft; mit --yes aufnehmen. Keine Daten geschrieben.",
                  "packages": packages, "completed": 0})
            return 2
        emit({"status": "preview" if args.preview else "ready",
              "message": "Inbox-Vorschau ohne Änderungen." if args.preview else "Inbox-Aufnahme abgeschlossen.",
              "packages": packages, "completed": 0 if args.preview else len(packages)})
        return 0

    if args.verb == "register":
        from .ingest import InboxImport, SourceImport, recover_import, recover_inbox_import, inbox_journal_pending
        source_arg = args.source or args.path
        if args.source and args.path or source_arg and args.package or args.recover and (source_arg or args.package or args.access):
            raise ValueError("Wähle genau eine Quelle, ein Inbox-Paket oder --recover.")
        inbox_value = args.inbox or selection.get("inbox")
        inbox = Path(inbox_value).absolute() if inbox_value else None
        if args.recover:
            if args.preview:
                emit({"status": "preview", "message": "Ausstehende Registrierung/Inbox-Aufnahme wiederherstellen."})
                return 0
            if not args.yes:
                emit({"status": "needs_confirmation", "message": "Mit --yes die Wiederherstellung starten."})
                return 2
            result = recover_inbox_import(workspace, inbox) if inbox is not None and inbox_journal_pending(workspace, inbox) else recover_import(workspace)
            emit(result)
            return 0
        if bool(source_arg) == bool(args.package):
            raise ValueError("Wähle register DATEI/ORDNER oder --package NAME aus der konfigurierten Inbox.")
        if args.package:
            if inbox is None:
                raise ValueError("Keine Inbox konfiguriert. Verwende setup --inbox oder register --inbox.")
            from .ingest import _package_name
            operation = InboxImport(workspace, inbox, inbox / "raw" / _package_name(args.package), access=args.access)
        else:
            if args.inbox:
                raise ValueError("--inbox gehört zur Paketaufnahme; direkte Registrierung nutzt --source.")
            operation = SourceImport(workspace, Path(source_arg), access=args.access)
        preview = operation.preview()
        if args.preview:
            emit(preview)
            return 0
        if not args.yes:
            emit({**preview, "status": "needs_confirmation", "message": "Geprüft; mit --yes anwenden. Keine Daten geschrieben."})
            return 2
        result = operation.apply()
        emit(result)
        return 0

    from .knowledge_workspace import OWNER, search_knowledge, KnowledgeWorkspaceJourney
    from .local_setup import open_workspace
    from .owner import LocalOwnerAdapter
    filters: dict[str, list[str]] = {}
    for term in args.filter:
        key, separator, value = term.partition("=")
        if not separator or not key or not value:
            raise ValueError("--filter erwartet KEY=VALUE.")
        filters.setdefault(key, []).append(value)
    core, state = open_workspace(workspace)
    adapter = None
    bound_link = None
    if args.connection:
        from .connections import resolve_connection
        core, state, profile = resolve_connection(workspace, args.connection)
        journey = KnowledgeWorkspaceJourney(core, authority_id=profile["authority_id"],
            principal_id=profile["principal_id"], connection_name=args.connection,
            source_link_id=profile["source_link_id"], transport="cli")
        if profile["authority_id"] != "user-global:source-access":
            if args.source or args.project:
                raise ValueError("Project-Suche kennt keine Global-Quellenauswahl.")
            found = journey.discover(args.question, cursor=json.loads(args.cursor) if args.cursor else None,
                                     filters=filters, scope="global" if args.global_scope else "project",
                                     recall_limit=args.recall_limit)
            details = found.get("details", {})
            result = {"status": found.get("status"), "reason_code": found.get("reason_code") or details.get("reason_code"),
                      "message": found.get("message") or details.get("summary", ""),
                      "next_action": found.get("next_action") or details.get("next_action"),
                      "reviewed": found.get("references", []), "citations": [],
                      "continuation": found.get("continuation"),
                      "search_progress": found.get("progress", {}), "recall": found.get("recall")}
            emit(result)
            return 0 if found.get("status") in {"discovered", "incomplete"} else 1
        if args.project:
            if args.source or args.global_scope:
                raise ValueError("Project-Lesen nutzt nur den registrierten Project-ID-Bereich.")
            found = journey.discover(args.question, cursor=json.loads(args.cursor) if args.cursor else None,
                                     filters=filters, scope="project", project_id=args.project,
                                     recall_limit=args.recall_limit)
            details = found.get("details", {})
            result = {"status": found.get("status"), "reason_code": found.get("reason_code") or details.get("reason_code"),
                      "message": found.get("message") or details.get("summary", ""),
                      "next_action": found.get("next_action") or details.get("next_action"),
                      "reviewed": found.get("references", []), "citations": [],
                      "continuation": found.get("continuation"),
                      "search_progress": found.get("progress", {}), "recall": found.get("recall")}
            emit(result)
            return 0 if found.get("status") in {"discovered", "incomplete"} else 1
        adapter = journey.agent
        bound_link = profile["source_link_id"]
    if args.global_scope:
        raise ValueError("--global benötigt eine benannte Project-Verbindung.")
    if args.project:
        raise ValueError("--project benötigt eine benannte Global-Verbindung.")
    if not isinstance(state, dict) or state.get("schema") not in {
            "owledge.private-knowledge-workspace/1", "owledge.private-knowledge-workspace/2",
            "owledge.private-knowledge-workspace/3"}:
        raise ValueError("Native Suche benötigt einen Knowledge-Workspace.")
    owner = LocalOwnerAdapter(core, principal_id=OWNER, active_authority_id="user-global:source-access",
                              reported={"agent_name": "human-cli", "model": "none"},
                              adapter_observed={"runtime": "owledge-local-cli", "runtime_version": "1", "run_id": "native-search"})
    result = search_knowledge(core, state, workspace, args.question, adapter=adapter or owner,
                              source=args.source, cursor=json.loads(args.cursor) if args.cursor else None,
                              bound_source_link=bound_link, filters=filters, recall_limit=args.recall_limit)
    emit(result)
    return 0 if result.get("status") != "needs_attention" else 1


def _run_setup(args, incoming: TextIO, outgoing: TextIO, target: Path,
               config_path: Path | None = None) -> int:
    def write_result(result: dict[str, object]) -> None:
        result = {"destination": str(target), **result}
        if args.json:
            outgoing.write(json.dumps(result, ensure_ascii=True) + "\n")
        else:
            label = {"preview": "Vorschau", "ready": "Bereit", "cancelled": "Abgebrochen",
                     "needs_confirmation": "Bestätigung erforderlich", "needs_attention": "Fehler"}.get(
                         str(result.get("status")), str(result.get("status", "Status")))
            outgoing.write(f"{label}: {result.get('message', '')}\n")
            if result.get("destination"):
                outgoing.write(f"Ziel: {result['destination']}\n")
            if result.get("status") in {"preview", "needs_confirmation"}:
                outgoing.write("Nächster Schritt: Mit --yes anwenden; --preview bleibt schreibgeschützt.\n")
            elif result.get("status") == "ready":
                outgoing.write(f"Nächster Schritt: status --workspace \"{target}\" ausführen.\n")
        outgoing.flush()

    try:
        if args.sample:
            if args.source or args.upgrade or args.profile != "knowledge":
                raise ValueError("--sample gehört nur zum neuen Knowledge-Setup ohne --source.")
            sample = Path(__file__).with_name("samples") / "quickstart.md"
            if not sample.is_file():
                raise ValueError("Das gebündelte Beispiel fehlt in dieser Installation.")
            sample_copy = target.with_name(target.name + "-quickstart.md")
            if target.exists() or sample_copy.exists():
                raise ValueError("Ziel oder Beispielquelle existiert bereits; wähle einen neuen Workspace-Namen.")
            if not target.parent.is_dir():
                raise ValueError("Erstelle zuerst den übergeordneten Zielordner.")
            sample_bytes = sample.read_bytes()
            sample_preview = {"status": "preview", "profile": "knowledge", "documents": 1,
                              "bytes": len(sample_bytes), "message":
                              f"Gebündelte Beispielquelle wird als {sample_copy.name} angelegt; keine Wissensfreigabe."}
            if args.preview:
                write_result(sample_preview)
                return 0
            if config_path is not None and config_path.exists():
                read_selection(config_path)
            if not args.yes:
                write_result({**sample_preview, "status": "needs_confirmation",
                              "message": "Beispiel geprüft; mit --yes anlegen. Keine Dateien geschrieben."})
                return 2
            with sample_copy.open("xb") as stream:
                stream.write(sample_bytes)
                stream.flush()
                import os
                os.fsync(stream.fileno())
            try:
                from .knowledge_workspace import KnowledgeWorkspaceSetup
                applied = KnowledgeWorkspaceSetup(target, sample_copy).apply()
            except (ValueError, OSError):
                if not target.exists():
                    sample_copy.unlink()
                raise
            if config_path is not None:
                try:
                    save_selection(config_path, target, Path(args.inbox).absolute() if args.inbox else None)
                except (ValueError, OSError) as error:
                    write_result({"status": "needs_attention", "message":
                        f"Workspace wurde erstellt, aber Auswahl nicht gespeichert: {error}. Verwende --workspace \"{target}\"."})
                    return 1
            write_result(applied)
            return 0
        if not args.source and not args.upgrade and args.profile not in {"project", "knowledge"}:
            raise ValueError("Wähle mit --source eine bestehende Markdown-Datei oder einen Markdown-Ordner.")
        if args.upgrade and (args.source or args.project_id or args.profile != "knowledge"):
            raise ValueError("Upgrade verwendet nur den vorhandenen Workspace, keine Profil-, Projekt- oder Quellenauswahl.")
        if args.profile == "project" and args.source:
            raise ValueError("Projektprofil unterstützt keine Quelle beim Setup.")
        if args.profile != "project" and args.project_id:
            raise ValueError("--project-id gehört ausschließlich zum Projektprofil.")
        from .source_workspace import SourceWorkspaceSetup
        from .knowledge_workspace import KnowledgeWorkspaceSetup
        from .project_workspace import ProjectWorkspaceSetup
        setup_type = {"source": SourceWorkspaceSetup, "knowledge": KnowledgeWorkspaceSetup,
                      "demo": OwnerWorkspaceSetup}.get(args.profile)
        operation = (OwnerWorkspaceUpgrade(target) if args.upgrade else
                     ProjectWorkspaceSetup(target, args.project_id) if args.profile == "project" else
                     setup_type(target, Path(args.source) if args.source else None))
        preview = operation.preview()
        if args.preview:
            write_result(preview)
            return 0
        if config_path is not None and config_path.exists():
            read_selection(config_path)
        def persist_selection() -> bool:
            if config_path is None:
                return True
            try:
                save_selection(config_path, target, Path(args.inbox).absolute() if args.inbox else None)
                return True
            except (ValueError, OSError) as error:
                write_result({"status": "needs_attention", "message":
                    f"Workspace wurde erstellt, aber die Auswahl konnte nicht gespeichert werden: {error}. "
                    f"Verwende --workspace \"{target}\" und repariere die lokale Auswahl."})
                return False
        if args.yes:
            applied = operation.apply()
            if not persist_selection():
                return 1
            write_result(applied)
            return 0
        if args.json or not bool(getattr(incoming, "isatty", lambda: False)()):
            write_result({"status": "needs_confirmation", "destination": str(target),
                          "message": "Setup wurde geprüft, aber noch nicht angewendet."})
            return 2
        write_result(preview)
        outgoing.write("apply oder reject: ")
        outgoing.flush()
        if incoming.readline().strip().lower() != "apply":
            write_result({"status": "cancelled", "destination": str(target),
                          "message": "Keine Dateien geschrieben."})
            return 0
        applied = operation.apply()
        if not persist_selection():
            return 1
        write_result(applied)
        return 0
    except (ValueError, OSError) as error:
        write_result({"status": "needs_attention", "destination": str(target), "message": str(error)})
        return 1


def main(argv: list[str] | None = None, *, input_stream: TextIO | None = None,
         output_stream: TextIO | None = None, config_path: Path | None = None) -> int:
    incoming = input_stream or sys.stdin
    outgoing = output_stream or sys.stdout
    parser = argparse.ArgumentParser(description="Privater Owledge MVP-Kandidat: setup, doctor, ask, maintain, status.")
    commands = parser.add_subparsers(dest="verb", required=True)
    setup_parser = commands.add_parser("setup")
    setup_parser.add_argument("directory", nargs="?")
    setup_parser.add_argument("--workspace")
    setup_parser.add_argument("--profile", choices=("knowledge", "project", "source", "demo"), default="knowledge")
    setup_parser.add_argument("--source")
    setup_parser.add_argument("--sample", action="store_true")
    setup_parser.add_argument("--inbox")
    setup_parser.add_argument("--project-id", default="")
    setup_parser.add_argument("--upgrade", action="store_true")
    decision = setup_parser.add_mutually_exclusive_group()
    decision.add_argument("--yes", action="store_true")
    decision.add_argument("--preview", action="store_true")
    setup_parser.add_argument("--json", action="store_true")
    legacy = argparse.ArgumentParser(add_help=False)
    legacy.add_argument("--workspace", required=True)
    legacy.add_argument("--source")
    legacy.add_argument("--access", choices=("restricted", "shared"))
    legacy.add_argument("--inbox")
    legacy.add_argument("--name", default="")
    legacy.add_argument("--knowledge-area")
    legacy.add_argument("--source-file", default="")
    legacy.add_argument("--text", default="")
    legacy.add_argument("--origin", default="")
    legacy.add_argument("--conditions", default="")
    legacy.add_argument("--verification", default="")
    legacy.add_argument("--limitations", default="")
    legacy.add_argument("--expected-revision", default="")
    legacy.add_argument("--expected-sha256", default="")
    legacy.add_argument("--base-revision", default="")
    legacy.add_argument("--base-sha256", default="")
    legacy.add_argument("--candidate-id")
    legacy.add_argument("--contribution-id")
    legacy.add_argument("--revision")
    legacy.add_argument("--recover-import", action="store_true")
    legacy.add_argument("--global-workspace")
    legacy.add_argument("--recover-link", action="store_true")
    legacy.add_argument("--archive")
    legacy.add_argument("--question", default="")
    legacy.add_argument("--depth", choices=("curated", "feed", "project", "originals"), default="curated")
    legacy.add_argument("--area", action="append", default=[])
    legacy.add_argument("--cursor")
    legacy.add_argument("--discover-areas", action="store_true")
    legacy.add_argument("--area-parent", default=".")
    legacy.add_argument("--source-link")
    legacy.add_argument("--action", choices=("summary", "contribute", "curate", "gap", "propose", "correct", "lesson", "review", "backup", "restore", "ingest", "link-global"), default="summary")
    legacy.add_argument("--topic", choices=("lesson", "alternative"), default="lesson")
    for verb in ("doctor", "ask", "maintain"):
        commands.add_parser(verb, parents=[legacy])
    status_parser = commands.add_parser("status")
    status_parser.add_argument("--workspace")
    status_parser.add_argument("--json", action="store_true")
    register_parser = commands.add_parser("register")
    register_parser.add_argument("path", nargs="?")
    register_parser.add_argument("--workspace")
    register_parser.add_argument("--source")
    register_parser.add_argument("--package")
    register_parser.add_argument("--inbox")
    register_parser.add_argument("--access", choices=("restricted", "shared"))
    register_parser.add_argument("--recover", action="store_true")
    register_parser.add_argument("--yes", action="store_true")
    register_parser.add_argument("--preview", action="store_true")
    register_parser.add_argument("--json", action="store_true")
    ingest_parser = commands.add_parser("ingest")
    ingest_parser.add_argument("--workspace")
    ingest_parser.add_argument("--inbox")
    ingest_parser.add_argument("--recover", action="store_true")
    ingest_parser.add_argument("--yes", action="store_true")
    ingest_parser.add_argument("--preview", action="store_true")
    ingest_parser.add_argument("--json", action="store_true")
    backup_parser = commands.add_parser("backup")
    backup_parser.add_argument("--workspace", required=True)
    backup_parser.add_argument("--archive", required=True)
    backup_parser.add_argument("--linked", action="store_true")
    backup_parser.add_argument("--expected-sha256")
    backup_parser.add_argument("--yes", action="store_true")
    backup_parser.add_argument("--json", action="store_true")
    restore_parser = commands.add_parser("restore")
    restore_parser.add_argument("--archive", required=True)
    restore_parser.add_argument("--target", required=True)
    restore_parser.add_argument("--linked", action="store_true")
    restore_parser.add_argument("--recover", action="store_true")
    restore_parser.add_argument("--expected-sha256")
    restore_parser.add_argument("--yes", action="store_true")
    restore_parser.add_argument("--json", action="store_true")
    search_parser = commands.add_parser("search")
    search_parser.add_argument("question")
    search_parser.add_argument("--workspace")
    search_parser.add_argument("--source")
    search_parser.add_argument("--connection")
    search_parser.add_argument("--global", dest="global_scope", action="store_true")
    search_parser.add_argument("--project")
    search_parser.add_argument("--filter", action="append", default=[])
    search_parser.add_argument("--recall-limit", choices=("focused", "expanded", "audit"))
    search_parser.add_argument("--cursor")
    search_parser.add_argument("--json", action="store_true")
    observe_parser = commands.add_parser("observe")
    observe_parser.add_argument("--workspace")
    observe_parser.add_argument("--connection", required=True)
    observe_parser.add_argument("--cursor")
    observe_parser.add_argument("--json", action="store_true")
    mcp_parser = commands.add_parser("mcp")
    mcp_parser.add_argument("--workspace")
    mcp_parser.add_argument("--connection", required=True)
    connect_parser = commands.add_parser("connect")
    connect_parser.add_argument("name", nargs="?")
    connect_parser.add_argument("--list", action="store_true")
    connect_parser.add_argument("--workspace")
    connect_parser.add_argument("--action", choices=("add", "revoke"), default="add")
    connect_parser.add_argument("--role", choices=("contributor", "operator"))
    connect_parser.add_argument("--source-link")
    connect_parser.add_argument("--expected-sha256")
    connect_parser.add_argument("--yes", action="store_true")
    connect_parser.add_argument("--json", action="store_true")
    rights_parser = commands.add_parser("source-rights")
    rights_parser.add_argument("action", choices=("list", "grant", "revoke", "migrate", "recover", "inspect-legacy"))
    rights_parser.add_argument("--workspace")
    rights_parser.add_argument("--source-link")
    rights_parser.add_argument("--connection")
    rights_parser.add_argument("--name")
    rights_parser.add_argument("--revision")
    rights_parser.add_argument("--expected-sha256")
    rights_parser.add_argument("--yes", action="store_true")
    rights_parser.add_argument("--json", action="store_true")
    reference_parser = commands.add_parser("reference")
    reference_parser.add_argument("action", choices=("propose", "refresh"))
    reference_parser.add_argument("name")
    reference_parser.add_argument("--workspace")
    reference_parser.add_argument("--connection")
    reference_parser.add_argument("--source-link", required=True)
    reference_parser.add_argument("--file", required=True)
    reference_parser.add_argument("--query", required=True)
    reference_parser.add_argument("--area", required=True)
    reference_parser.add_argument("--text", required=True)
    reference_parser.add_argument("--cursor")
    reference_parser.add_argument("--expected-revision")
    reference_parser.add_argument("--expected-sha256")
    reference_parser.add_argument("--json", action="store_true")
    review_parser = commands.add_parser("review")
    review_parser.add_argument("--workspace")
    review_parser.add_argument("--name", required=True)
    review_parser.add_argument("--candidate-id")
    review_parser.add_argument("--operator")
    review_parser.add_argument("--decision", choices=("approve", "reject"))
    review_parser.add_argument("--expected-sha256")
    review_parser.add_argument("--yes", action="store_true")
    review_parser.add_argument("--json", action="store_true")
    batch_parser = commands.add_parser("review-batch")
    batch_parser.add_argument("--workspace")
    batch_parser.add_argument("--operator")
    batch_parser.add_argument("--cursor")
    batch_parser.add_argument("--decision", choices=("approve", "reject"))
    batch_parser.add_argument("--expected-sha256")
    batch_parser.add_argument("--yes", action="store_true")
    batch_parser.add_argument("--json", action="store_true")
    for verb in ("idea", "finding"):
        record_parser = commands.add_parser(verb)
        record_parser.add_argument("name")
        record_parser.add_argument("--workspace")
        record_parser.add_argument("--area", required=True)
        record_parser.add_argument("--text", required=True)
        if verb == "finding":
            record_parser.add_argument("--exception-kind", required=True,
                                       choices=("critical-finding", "protected-decision", "unresolved-conflict", "curated-review"))
        record_parser.add_argument("--json", action="store_true")
    correct_parser = commands.add_parser("correct")
    correct_parser.add_argument("name")
    correct_parser.add_argument("--workspace")
    correct_parser.add_argument("--connection")
    correct_parser.add_argument("--text", required=True)
    correct_parser.add_argument("--expected-revision", required=True)
    correct_parser.add_argument("--expected-sha256", required=True)
    correct_parser.add_argument("--json", action="store_true")
    read_parser = commands.add_parser("read")
    read_parser.add_argument("--workspace")
    read_parser.add_argument("--name", required=True)
    read_parser.add_argument("--revision")
    read_parser.add_argument("--connection")
    read_parser.add_argument("--global", dest="global_scope", action="store_true")
    read_parser.add_argument("--project")
    read_parser.add_argument("--json", action="store_true")
    project_read_parser = commands.add_parser("project-read")
    project_read_parser.add_argument("--workspace", required=True)
    project_read_parser.add_argument("--project-id", required=True)
    project_read_parser.add_argument("--project-workspace")
    project_read_parser.add_argument("--connection", required=True)
    project_read_parser.add_argument("--action", choices=("grant", "revoke"), required=True)
    project_read_parser.add_argument("--expected-sha256")
    project_read_parser.add_argument("--recover", action="store_true")
    project_read_parser.add_argument("--yes", action="store_true")
    project_read_parser.add_argument("--json", action="store_true")
    global_read_parser = commands.add_parser("global-read")
    global_read_parser.add_argument("--workspace", required=True)
    global_read_parser.add_argument("--connection", required=True)
    global_read_parser.add_argument("--action", choices=("grant", "revoke"), required=True)
    global_read_parser.add_argument("--expected-sha256")
    global_read_parser.add_argument("--yes", action="store_true")
    global_read_parser.add_argument("--json", action="store_true")
    contribute_parser = commands.add_parser("contribute")
    contribute_parser.add_argument("--workspace")
    contribute_parser.add_argument("--name", required=True)
    contribute_parser.add_argument("--expected-revision")
    contribute_parser.add_argument("--expected-sha256")
    contribute_parser.add_argument("--connection")
    contribute_parser.add_argument("--yes", action="store_true")
    contribute_parser.add_argument("--json", action="store_true")
    link_parser = commands.add_parser("link")
    link_parser.add_argument("--workspace")
    link_parser.add_argument("--global-workspace")
    link_parser.add_argument("--connection")
    link_parser.add_argument("--action", choices=("grant", "revoke"))
    link_parser.add_argument("--expected-sha256")
    link_parser.add_argument("--yes", action="store_true")
    link_parser.add_argument("--json", action="store_true")
    feed_parser = commands.add_parser("feed")
    feed_parser.add_argument("query")
    feed_parser.add_argument("--workspace", required=True)
    feed_parser.add_argument("--connection", required=True)
    feed_parser.add_argument("--area")
    feed_parser.add_argument("--cursor")
    feed_parser.add_argument("--stage", choices=("reuse_feed", "inbox"), default="reuse_feed")
    feed_parser.add_argument("--filter", action="append", default=[])
    feed_parser.add_argument("--json", action="store_true")
    curate_parser = commands.add_parser("curate")
    curate_parser.add_argument("name")
    curate_parser.add_argument("--workspace", required=True)
    curate_parser.add_argument("--connection", required=True)
    curate_parser.add_argument("--contribution-id", required=True)
    curate_parser.add_argument("--expected-revision", required=True)
    curate_parser.add_argument("--expected-sha256", required=True)
    curate_parser.add_argument("--base-revision")
    curate_parser.add_argument("--base-sha256")
    curate_parser.add_argument("--json", action="store_true")
    essence_parser = commands.add_parser("essence")
    essence_parser.add_argument("action", choices=("bind", "propose", "curate"))
    essence_parser.add_argument("--workspace")
    essence_parser.add_argument("--concept")
    essence_parser.add_argument("--summary")
    essence_parser.add_argument("--area")
    essence_parser.add_argument("--expected-sha256")
    essence_parser.add_argument("--contribution-id")
    essence_parser.add_argument("--revision")
    essence_parser.add_argument("--yes", action="store_true")
    essence_parser.add_argument("--json", action="store_true")
    settings_parser = commands.add_parser("settings")
    settings_parser.add_argument("action", choices=("inspect", "repair", "configure"))
    settings_parser.add_argument("--workspace", required=True)
    settings_parser.add_argument("--scope", choices=("local",))
    settings_parser.add_argument("--reset-empty", action="store_true")
    settings_parser.add_argument("--recall-default", choices=("focused", "expanded", "audit"))
    settings_parser.add_argument("--recall-max-auto", choices=("focused", "expanded", "audit"))
    settings_parser.add_argument("--research-default", choices=("none", "targeted", "deep"))
    settings_parser.add_argument("--research-max-auto", choices=("none", "targeted", "deep"))
    settings_parser.add_argument("--unset", action="append", choices=("recall_default", "recall_max_auto", "research_default", "research_max_auto"), default=[])
    settings_parser.add_argument("--expected-sha256")
    settings_parser.add_argument("--recover", action="store_true")
    settings_parser.add_argument("--yes", action="store_true")
    settings_parser.add_argument("--json", action="store_true")
    case_parser = commands.add_parser("case")
    case_parser.add_argument("action", choices=("add", "list", "show", "ask", "answer", "verify", "recover"))
    case_parser.add_argument("name", nargs="?")
    case_parser.add_argument("--workspace")
    case_parser.add_argument("--question")
    case_parser.add_argument("--title")
    case_parser.add_argument("--area")
    case_parser.add_argument("--answer-type", choices=("text", "integer"), default="text")
    case_parser.add_argument("--max-chars", type=int, default=200)
    case_parser.add_argument("--minimum", type=int)
    case_parser.add_argument("--maximum", type=int)
    case_parser.add_argument("--text")
    case_parser.add_argument("--expected-revision")
    case_parser.add_argument("--expected-sha256")
    case_parser.add_argument("--yes", action="store_true")
    case_parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    def emit(value):
        outgoing.write(json.dumps(value, ensure_ascii=False) + "\n")
        outgoing.flush()

    if args.verb in {"backup", "restore"}:
        try:
            from .workspace_archive import WorkspaceArchive
            if args.verb == "backup" and args.expected_sha256 and not args.yes:
                raise ValueError("Backup hash belongs to explicit --yes apply.")
            if args.verb == "restore" and args.recover and (not args.yes or args.expected_sha256):
                raise ValueError("Restore recovery requires --recover --yes without a preview hash.")
            operation = WorkspaceArchive(Path(args.workspace if args.verb == "backup" else args.target),
                Path(args.archive), args.verb, linked=args.linked,
                recover=args.verb == "restore" and args.recover)
            if args.verb == "restore" and args.recover:
                result = operation.recover()
            elif not args.yes:
                result = operation.preview()
            else:
                if not args.expected_sha256:
                    raise ValueError("Apply requires --expected-sha256 from the exact preview.")
                result = operation.apply(args.expected_sha256)
            if args.json:
                emit(result)
            else:
                outgoing.write(f"{args.verb}: {result['status']}\n")
                outgoing.write(f"Files: {result.get('files', 0)}; Bytes: {result.get('bytes', 0)}\n")
                if result.get("pair"):
                    pair = result["pair"]
                    outgoing.write(f"Project: {pair['old_project']} -> {pair['new_project']}\n")
                    outgoing.write(f"Global: {pair['old_global']} -> {pair['new_global']}\n")
                    outgoing.write(f"Reissued current link: {pair['source_link_id']}; receipt: {pair['receipt_id']}\n")
                    outgoing.write(f"Suspended cross-readers: {', '.join(pair['suspended_readers']) or '(none)'}\n")
                    if pair.get("external_projects_unavailable"):
                        outgoing.write(f"External Project registrations need Owner re-link: {', '.join(pair['external_projects_unavailable'])}\n")
                if result.get("expected_sha256"):
                    outgoing.write(f"Exact hash: {result['expected_sha256']}\n")
            return 0
        except (ValueError, OSError) as error:
            emit({"status": "needs_attention", "message": str(error)}) if args.json else outgoing.write(f"Fehler: {error}\n")
            return 1

    if args.verb == "settings":
        from owledge_core.contracts import verified_settings_catalog
        try:
            verified_settings_catalog()
        except (ValueError, OSError) as error:
            result = {"status": "quarantined", "message": str(error),
                      "diagnostics": [{"code": "settings_contract_invalid", "source": "installed contract",
                                       "key": None, "rule": "verified Settings resources could not be read",
                                       "repair": "Inspect the installation and reinstall verified resources."}]}
            if args.json:
                emit(result)
            else:
                outgoing.write(f"Settings contract invalid: {error}. Reinstall verified resources.\n")
            return 1
        try:
            workspace = Path(args.workspace).absolute()
            from .local_setup import open_settings_workspace
            core, state, authority_id = open_settings_workspace(workspace)
            updates = {key: value for key, value in (("recall_default", args.recall_default),
                ("recall_max_auto", args.recall_max_auto), ("research_default", args.research_default),
                ("research_max_auto", args.research_max_auto)) if value is not None}
            if args.action == "inspect":
                if args.scope or args.reset_empty or args.expected_sha256 or args.recover or args.yes or updates or args.unset:
                    raise ValueError("Settings inspection ist schreibgeschützt.")
                result = core._settings_from_local_owner(workspace, authority_id, action="inspect")
            else:
                if (args.scope != "local" or args.reset_empty != (args.action == "repair")
                        or args.action == "repair" and (updates or args.unset)
                        or args.action == "configure" and not (updates or args.unset or args.recover)
                        or args.recover and (args.expected_sha256 or not args.yes or updates or args.unset)):
                    raise ValueError("Settings repair/configure benötigen --scope local; reset-empty gehört nur zu repair; Recovery zusätzlich --recover --yes.")
                result = core._settings_from_local_owner(workspace, authority_id, action=args.action,
                    expected_sha256=args.expected_sha256, apply=args.yes, recover=args.recover,
                    updates=updates, unset=tuple(args.unset))
            if args.json:
                emit(result)
            else:
                outgoing.write(f"Settings: {result['status']}\n")
                if result.get("registry_sha256"):
                    outgoing.write(f"Catalog SHA-256: {result['registry_sha256']}\n")
                if result.get("snapshot_sha256"):
                    outgoing.write(f"Snapshot SHA-256: {result['snapshot_sha256']}\n")
                if isinstance(result.get("values"), dict):
                    values_text = ", ".join(f"{key}={value}" for key, value in sorted(result["values"].items())) or "(keine lokalen Überschreibungen)"
                    outgoing.write(f"Lokale Werte: {values_text}\n")
                for key, value in result.get("effective", {}).items():
                    outgoing.write(f"{key}={value} ({result.get('sources', {}).get(key, 'unknown')})\n")
                for layer in result.get("layers", []):
                    for item in layer.get("diagnostics", []):
                        source = item.get("source") or "installed contract"
                        key = item.get("key") or "document"
                        outgoing.write(f"{layer.get('authority_id')} {source} [{key}]: "
                                       f"{item['code']} — {item['rule']} {item['repair']}\n")
                if result.get("expected_sha256"):
                    quote = lambda value: "'" + str(value).replace("'", "''") + "'"
                    options = ("--reset-empty" if args.action == "repair" else " ".join(
                        [f"--{key.replace('_', '-')} {value}" for key, value in updates.items()]
                        + [f"--unset {key}" for key in args.unset]))
                    outgoing.write(f"Anwenden: settings {args.action} --workspace {quote(workspace)} "
                                   f"--scope local {options} --expected-sha256 {result['expected_sha256']} --yes\n")
                outgoing.flush()
            return 0 if result["status"] in {"ready", "preview", "quarantined"} else 1
        except (ValueError, OSError) as error:
            result = {"status": "needs_attention", "message": str(error),
                      "diagnostics": [{"code": "settings_operation_invalid", "source": str(args.workspace),
                                       "key": None, "rule": "Settings request or workspace binding is stale or invalid",
                                       "repair": "Inspect Settings, correct the request, or re-preview before applying."}]}
            if args.json:
                emit(result)
            else:
                outgoing.write(f"Fehler: {error}\n")
            return 1

    if args.verb == "case":
        try:
            from .project_workspace import ProjectCaseJourney, SCHEMA as PROJECT_SCHEMA, LINKED_SCHEMA
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                raise ValueError("Project-Workspace fehlt.")
            workspace = Path(chosen).absolute()
            core, state = open_workspace(workspace)
            if state.get("schema") not in {PROJECT_SCHEMA, LINKED_SCHEMA}:
                raise ValueError("Project-Fälle benötigen einen Project-Workspace.")
            journey = ProjectCaseJourney(core, state["authority_id"])
            if args.action == "add":
                if not args.name or not args.question or not args.area:
                    raise ValueError("case add benötigt Name, --question und --area.")
                if args.answer_type == "text":
                    if args.minimum is not None or args.maximum is not None:
                        raise ValueError("Zahlengrenzen gehören nur zu --answer-type integer.")
                    value_contract = {"type": "bounded_text", "max_chars": args.max_chars}
                else:
                    if args.minimum is None or args.maximum is None:
                        raise ValueError("Ganzzahlige Antwort benötigt --minimum und --maximum.")
                    value_contract = {"type": "integer_string", "minimum": args.minimum, "maximum": args.maximum}
                result = core._configure_project_case_from_local_owner(workspace, name=args.name,
                    question=args.question, title=args.title or args.question, area=args.area,
                    value_contract=value_contract, expected_sha256=args.expected_sha256, apply=args.yes)
            elif args.action == "recover":
                if not args.yes:
                    result = {"status": "preview", "message": "Unterbrochene Fallkonfiguration als Owner wiederherstellen; --yes anwenden."}
                else:
                    result = core._recover_project_case_from_local_owner(workspace)
            else:
                if args.yes or args.question or args.title or args.area:
                    raise ValueError("Diese Fallaktion verwendet keine Konfigurationsfelder.")
                if args.action == "list":
                    result = journey.list()
                elif not args.name:
                    raise ValueError("Der Fallname fehlt.")
                elif args.action == "show":
                    result = journey.show(args.name)
                elif args.action == "ask":
                    result = journey.ask(args.name)
                elif args.action == "answer":
                    if args.text is None:
                        raise ValueError("case answer benötigt --text.")
                    result = journey.answer(args.name, args.text, expected_revision=args.expected_revision,
                                            expected_sha256=args.expected_sha256)
                else:
                    result = journey.verify(args.name)
            if args.json:
                emit(result)
            else:
                outgoing.write(f"Fall {args.action}: {result.get('status')}\n")
                if result.get("status") == "preview" and args.action == "add":
                    quote = lambda value: "'" + str(value).replace("'", "''") + "'"
                    answer_options = (f"--answer-type integer --minimum {args.minimum} --maximum {args.maximum}"
                                      if args.answer_type == "integer" else f"--answer-type text --max-chars {args.max_chars}")
                    outgoing.write(f"Anwenden: case add {args.name} --workspace {quote(workspace)} "
                                   f"--question {quote(args.question)} --title {quote(args.title or args.question)} "
                                   f"--area {quote(args.area)} {answer_options} "
                                   f"--expected-sha256 {result['expected_sha256']} --yes\n")
                if result.get("status") == "preview" and args.action == "answer":
                    outgoing.write(f"Review: review --workspace \"{workspace}\" --name case:{args.name} --candidate-id {result['candidate_id']}\n")
                if result.get("status") == "answered" and args.action == "ask":
                    outgoing.write(f"Antwort: {result.get('answer_text', '')}\n"
                                   f"Revision: {result.get('revision', '')}\n"
                                   f"SHA-256: {result.get('content_sha256', '')}\n")
                outgoing.flush()
            return 0 if result.get("status") in {"preview", "ready", "answered", "knowledge_absent", "verified"} else 1
        except (ValueError, OSError) as error:
            emit({"status": "needs_attention", "message": str(error)})
            return 1

    if args.verb == "essence":
        try:
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                raise ValueError("Project-Workspace fehlt.")
            workspace = Path(chosen).absolute()
            core, state = open_workspace(workspace)
            from .project_workspace import LINKED_SCHEMA
            if args.action in {"bind", "propose"} and state.get("schema") != LINKED_SCHEMA:
                raise ValueError("Project Essence benötigt einen verknüpften Project-Workspace.")
            if args.action == "curate":
                from .knowledge_workspace import SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA
                if state.get("schema") not in {SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}:
                    raise ValueError("Global Essence curation benötigt einen Knowledge-Workspace.")
                if not args.contribution_id or not args.revision or not args.expected_sha256 or args.yes:
                    raise ValueError("Curate benötigt exakte Contribution-ID, --revision und --expected-sha256; Review ist separat.")
                result = core._global_essence_from_local_owner(args.contribution_id, args.revision, args.expected_sha256)
            elif args.action == "bind":
                if not args.concept or args.summary or args.area or args.contribution_id or args.revision:
                    raise ValueError("Bind benötigt genau --concept CONCEPT.md.")
                from owledge_connectors.markdown_source import MarkdownSourceConnector
                concept = Path(args.concept).absolute()
                if concept.name != "CONCEPT.md" or not concept.is_file() or concept.is_symlink():
                    raise ValueError("Wähle eine reguläre CONCEPT.md.")
                snapshot = MarkdownSourceConnector(concept).scan()
                result = core._project_concept_from_local_owner(workspace, snapshot,
                    apply=args.yes, expected_sha256=args.expected_sha256)
            else:
                if not args.summary or not args.area or args.concept or args.yes or args.expected_sha256 or args.contribution_id or args.revision:
                    raise ValueError("Propose benötigt --summary und --area; Review ist separat.")
                result = core._project_essence_from_local_owner(workspace, args.summary, args.area)
            if args.json:
                emit(result)
            else:
                outgoing.write(f"Essence {args.action}: {result['status']}\n")
                if result.get("review_preview"):
                    shown = result["review_preview"]
                    outgoing.write(f"Kandidat: {result['candidate_id']}\nVorschlag: {shown['proposed_text']}\nQuelle: {shown['source']}\n")
                if result.get("status") == "preview" and args.action == "bind":
                    outgoing.write(f"Anwenden: essence bind --workspace \"{workspace}\" --concept \"{concept}\" --expected-sha256 {result['expected_sha256']} --yes\n")
                outgoing.flush()
            return 0 if result.get("status") in {"preview", "ready"} else 1
        except (ValueError, OSError) as error:
            emit({"status": "needs_attention", "message": str(error)})
            return 1

    if args.verb == "setup":
        if args.directory is not None and args.workspace is not None:
            setup_parser.error("DIRECTORY und --workspace dürfen nicht gemeinsam verwendet werden.")
        selected = args.directory if args.directory is not None else args.workspace
        if selected == "":
            setup_parser.error("Der Setup-Pfad darf nicht leer sein.")
        target = Path(selected or "owledge").absolute()
        return _run_setup(args, incoming, outgoing, target, config_path)

    if args.verb == "mcp":
        try:
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                raise ValueError("Kein Workspace gewählt. Führe setup aus oder verwende --workspace.")
            from .mcp_stdio import entry as mcp_entry
            return mcp_entry(Path(chosen).absolute(), args.connection)
        except (ValueError, OSError) as error:
            print(f"Owledge MCP: {error}", file=sys.stderr)
            return 1

    if args.verb == "reference":
        try:
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                raise ValueError("Kein Workspace gewählt. Führe setup aus oder verwende --workspace.")
            workspace = Path(chosen).absolute()
            from .knowledge_workspace import SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA, CASE, KnowledgeWorkspaceJourney
            core, state = open_workspace(workspace)
            if state.get("schema") not in {SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}:
                raise ValueError("Quellenreferenzen benötigen einen Knowledge-Workspace.")
            if args.action == "propose":
                if not args.connection or args.expected_revision or args.expected_sha256:
                    raise ValueError("Vorschlag benötigt --connection und keine Refresh-Basis.")
                from .connections import resolve_connection
                core, _, profile = resolve_connection(workspace, args.connection)
                if profile["authority_id"] != "user-global:source-access" or profile["source_link_id"] not in (None, args.source_link):
                    raise ValueError("Verbindung ist nicht für diesen Global Source Link gebunden.")
                journey = KnowledgeWorkspaceJourney(core, principal_id=profile["principal_id"],
                                                    connection_name=args.connection,
                                                    source_link_id=profile["source_link_id"])
                search = {"coverage_case_id": CASE, "query": args.query, "source_areas": ["."],
                          "source_cursor": json.loads(args.cursor) if args.cursor else None,
                          "source_link_id": args.source_link}
                result = journey.propose(name=args.name, area=args.area, text=args.text,
                                         source_file=args.file, search=search)
            else:
                if args.connection or not args.expected_revision or not args.expected_sha256:
                    raise ValueError("Refresh benötigt exakte Revision und Hash, ohne Contributor-Verbindung.")
                result = core._source_reference_refresh_from_local_owner(
                    workspace, name=args.name, area=args.area, text=args.text,
                    source_link_id=args.source_link, source_file=args.file, query=args.query,
                    cursor=json.loads(args.cursor) if args.cursor else None,
                    expected_revision=args.expected_revision, expected_sha256=args.expected_sha256)
            if args.json:
                outgoing.write(json.dumps(result, ensure_ascii=False) + "\n")
            else:
                outgoing.write(f"Referenz: {result.get('status')} — {result.get('name', args.name)}\n")
                if result.get("status") == "preview":
                    outgoing.write(f"Candidate: {result['candidate_id']}\nQuelle: {args.source_link} {args.file}\n"
                                   f"Vorschlag: {args.text}\n")
                    if result.get("review_preview", {}).get("old_source") is not None:
                        outgoing.write(f"Alte Quellenbindung: {result['review_preview']['old_source']}\n"
                                       f"Neue Quellenbindung: {result['review_preview']['source']}\n")
                    outgoing.write(f"Nächster Schritt: review --workspace \"{workspace}\" --name {args.name} "
                                   f"--candidate-id {result['candidate_id']}\n")
                else:
                    outgoing.write(f"{result.get('message', result.get('details', ''))}\n")
            outgoing.flush()
            return 0 if result.get("status") == "preview" else 1
        except (ValueError, OSError) as error:
            outgoing.write(json.dumps({"status": "needs_attention", "message": str(error)}, ensure_ascii=False) + "\n"
                           if args.json else f"Fehler: {error}\n")
            return 1

    if args.verb == "source-rights":
        try:
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                raise ValueError("Kein Workspace gewählt. Führe setup aus oder verwende --workspace.")
            workspace = Path(chosen).absolute()
            core, state = open_workspace(workspace)
            from .knowledge_workspace import SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA, AUTHORITY
            if state.get("schema") not in {SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}:
                raise ValueError("Quellenrechte benötigen einen Knowledge-Workspace.")
            if args.action == "migrate":
                if args.source_link or args.connection or args.name or args.revision:
                    raise ValueError("migrate wird ohne Quellen- oder Verbindungsnamen verwendet.")
                result = core._legacy_source_rights_from_local_owner(workspace,
                    expected_sha256=args.expected_sha256, apply=args.yes)
            elif args.action == "recover":
                if args.source_link or args.connection or args.name or args.revision or args.yes or args.expected_sha256:
                    raise ValueError("recover wird ohne Änderungsargumente verwendet.")
                result = core._legacy_source_rights_from_local_owner(workspace, recover=True)
            elif args.action == "inspect-legacy":
                if not args.name or args.source_link or args.connection or args.yes or args.expected_sha256:
                    raise ValueError("inspect-legacy benötigt nur --name und optional --revision.")
                result = core._inspect_legacy_source_from_local_owner(workspace, name=args.name, revision=args.revision)
            elif args.action == "list":
                if args.source_link or args.connection or args.expected_sha256 or args.yes:
                    raise ValueError("list wird ohne Änderungsargumente verwendet.")
                result = core._list_named_source_rights_from_local_owner(workspace)
            else:
                if not args.source_link or not args.connection:
                    raise ValueError("--source-link und --connection sind erforderlich.")
                result = core._named_source_rights_from_local_owner(workspace,
                    source_link_id=args.source_link, connection=args.connection, action=args.action,
                    expected_sha256=args.expected_sha256, apply=args.yes)
            if args.json:
                outgoing.write(json.dumps(result, ensure_ascii=False) + "\n")
            elif args.action == "list":
                outgoing.write(f"Quellen: {len(result['links'])}\n")
                for row in result["links"]:
                    reader_labels = [f"{name} ({row['reader_status'][name]})" for name in row["readers"]]
                    outgoing.write(f"{row['source_link_id']}: {row['source_name']} ({row['source_path']}) — "
                                   f"{row['access']} — Leser: {', '.join(reader_labels) or 'keine'}\n")
            elif args.action in {"migrate", "recover"}:
                outgoing.write(f"Quellenrechte-Migration: {result['status']} — Rohquellen danach nur Owner; alte Ableitungen gesperrt.\n")
                if result["status"] == "preview":
                    outgoing.write(f"Anwenden: source-rights migrate --workspace '{workspace}' "
                                   f"--expected-sha256 {result['expected_sha256']} --yes\n")
            elif args.action == "inspect-legacy":
                outgoing.write(f"Historische Referenz {result['name']} ({result['revision']}, {result['content_sha256']}):\n"
                               f"{result['text']}\n")
            else:
                outgoing.write(f"Quellenrecht: {result['status']} — {args.action} {args.connection} auf {args.source_link}\n")
                outgoing.write("Zugriff danach: " + ("erlaubt\n" if result["allowed_after"] else "entzogen\n"))
                if result["status"] == "preview":
                    outgoing.write(f"Anwenden: source-rights {args.action} --workspace \"{workspace}\" "
                                   f"--source-link {args.source_link} --connection {args.connection} "
                                   f"--expected-sha256 {result['expected_sha256']} --yes\n")
            outgoing.flush()
            return 0
        except (ValueError, OSError) as error:
            outgoing.write(json.dumps({"status": "needs_attention", "message": str(error)}, ensure_ascii=False) + "\n"
                           if args.json else f"Fehler: {error}\n")
            return 1

    if args.verb == "connect":
        try:
            if args.list and (args.name or args.yes or args.source_link or args.expected_sha256 or args.action != "add" or args.role):
                raise ValueError("--list wird ohne Änderungsargumente verwendet.")
            if not args.list and not args.name:
                raise ValueError("Wähle einen Verbindungsnamen oder --list.")
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                raise ValueError("Kein Workspace gewählt. Führe setup aus oder verwende --workspace.")
            if args.action == "revoke" and args.source_link is not None:
                raise ValueError("--source-link gehört nur zur neuen Verbindung.")
            workspace = Path(chosen).absolute()
            core, state = open_workspace(workspace)
            from .knowledge_workspace import SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA, AUTHORITY
            from .project_workspace import SCHEMA as PROJECT_SCHEMA, LINKED_SCHEMA
            if state.get("schema") in {SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}:
                authority, authority_root = AUTHORITY, workspace / "global"
            elif state.get("schema") in {PROJECT_SCHEMA, LINKED_SCHEMA}:
                authority, authority_root = state["authority_id"], workspace / "project"
            else:
                raise ValueError("Benannte Verbindung benötigt einen Knowledge- oder Project-Workspace.")
            from owledge_core.project_io import bootstrap_authority
            if args.list:
                header = bootstrap_authority(authority_root, authority)
                if header.metadata.get("rights_era") != "owledge.bound-source-rights/1" or not isinstance(header.metadata.get("connections"), dict):
                    raise ValueError("Älterer Workspace benötigt eine ausdrückliche Quellenrechte-Migration vor Agent-Verbindungen.")
                result = {"status": "ready", "authority_id": authority,
                          "connections": header.metadata["connections"], "revision": header.revision}
            else:
                result = core._named_connection_from_local_owner(workspace, authority,
                    name=args.name, action=args.action, role=args.role, source_link_id=args.source_link,
                    expected_sha256=args.expected_sha256, apply=args.yes)
            if args.json:
                outgoing.write(json.dumps(result, ensure_ascii=False) + "\n")
            else:
                if args.list:
                    outgoing.write(f"Verbindungen: {len(result['connections'])}\n")
                    for name, profile in sorted(result["connections"].items()):
                        outgoing.write(f"{name}: {profile['status']} {profile['role']} ({profile['principal_id']})\n")
                else:
                    outgoing.write(f"Verbindung: {result['status']} — {result['name']} ({result['action']})\n"
                                   f"Rolle: {result['role']}\nPrincipal: {result['principal_id']}\nAuthority: {result['authority_id']}\n")
                if result["status"] == "preview":
                    outgoing.write(f"Anwenden: connect {args.name} --workspace \"{workspace}\" --action {args.action} --role {result['role']} "
                                   + (f"--source-link {args.source_link} " if args.source_link else "")
                                   + f"--expected-sha256 {result['expected_sha256']} --yes\n")
            outgoing.flush()
            return 0
        except (ValueError, OSError) as error:
            outgoing.write(json.dumps({"status": "needs_attention", "message": str(error)}, ensure_ascii=False) + "\n"
                           if args.json else f"Fehler: {error}\n")
            return 1

    if args.verb == "review-batch":
        try:
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                raise ValueError("Kein Workspace gewählt. Führe setup aus oder verwende --workspace.")
            workspace = Path(chosen).absolute()
            if args.operator:
                from .connections import resolve_connection
                core, state, profile = resolve_connection(workspace, args.operator, role="operator")
            else:
                core, state = open_workspace(workspace)
                profile = None
            from .knowledge_workspace import KnowledgeWorkspaceJourney
            from .project_workspace import SCHEMA as PROJECT_SCHEMA, LINKED_SCHEMA
            actor = ({"principal_id": profile["principal_id"], "connection_name": args.operator,
                      "operator_workspace": workspace, "transport": "cli"} if profile is not None else
                     {"transport": "cli"})
            journey = (KnowledgeWorkspaceJourney(core, authority_id=state["authority_id"], **actor)
                       if state.get("schema") in {PROJECT_SCHEMA, LINKED_SCHEMA}
                       else KnowledgeWorkspaceJourney(core, **actor))
            cursor = json.loads(args.cursor) if args.cursor else None
            if args.decision is None and args.expected_sha256 is None and not args.yes:
                result = journey.batch_preview(cursor)
            elif not args.decision or not args.expected_sha256 or not args.yes:
                raise ValueError("Batch-Anwendung benötigt --decision, --expected-sha256 und --yes.")
            else:
                result = journey.batch_apply(cursor=cursor, decision=args.decision,
                                             expected_sha256=args.expected_sha256)
            if args.operator:
                result["operator"] = args.operator
                result["actor_principal_id"] = profile["principal_id"]
            if args.json:
                outgoing.write(json.dumps(result, ensure_ascii=False) + "\n")
            else:
                outgoing.write(f"Review-Seite: {result.get('status')} — {result.get('message', '')}\n")
                for item in result.get("items", []):
                    label = ("Möglichkeit/Signal, kein Faktenbeleg" if item.get("record_kind") in {"idea", "finding"}
                             else "Freigabevorschlag")
                    outgoing.write(f"{label}: {item.get('name')} ({item['candidate_id']})\n"
                                   f"Quelle: {item.get('source')}\nZiel: {item.get('target')}\n"
                                   f"Vorschlag: {item.get('proposed_text')}\n"
                                   f"Inhaltshash: {item.get('content_sha256')}\n")
                for item in result.get("results", []):
                    outgoing.write(f"Entscheidung: {item.get('name')} {item.get('status')} ({item.get('receipt_id')})\n")
                if result.get("failed_item"):
                    outgoing.write(f"Gestoppt bei: {result['failed_item']}\nRest: {result.get('unprocessed_ids', [])}\n")
                if result.get("status") == "preview":
                    outgoing.write(f"Anwenden: review-batch --workspace \"{workspace}\" "
                                   + (f"--operator {args.operator} " if args.operator else "")
                                   + (f"--cursor '{json.dumps(cursor, ensure_ascii=False)}' " if cursor else "")
                                   + f"--decision approve --expected-sha256 {result['expected_sha256']} --yes\n")
                    if result.get("continuation"):
                        outgoing.write("Weitere Seite: --cursor aus der JSON-Ausgabe unverändert übernehmen.\n")
            outgoing.flush()
            return 0 if result.get("status") in {"preview", "incomplete", "accepted", "rejected", "partial"} else 1
        except (ValueError, OSError) as error:
            outgoing.write(json.dumps({"status": "needs_attention", "message": str(error)}, ensure_ascii=False) + "\n"
                           if args.json else f"Fehler: {error}\n")
            return 1

    if args.verb == "review":
        try:
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                raise ValueError("Kein Workspace gewählt. Führe setup aus oder verwende --workspace.")
            workspace = Path(chosen).absolute()
            if args.operator:
                from .connections import resolve_connection
                core, state, operator_profile = resolve_connection(workspace, args.operator, role="operator")
            else:
                core, state = open_workspace(workspace)
                operator_profile = None
            from .knowledge_workspace import KnowledgeWorkspaceJourney
            from .project_workspace import SCHEMA as PROJECT_SCHEMA, LINKED_SCHEMA
            operator_args = ({"principal_id": operator_profile["principal_id"], "connection_name": args.operator,
                              "operator_workspace": workspace} if operator_profile is not None else {})
            journey = (KnowledgeWorkspaceJourney(core, authority_id=state["authority_id"], **operator_args)
                       if state.get("schema") in {PROJECT_SCHEMA, LINKED_SCHEMA}
                       else KnowledgeWorkspaceJourney(core, **operator_args))
            preview = journey.preview(args.name, args.candidate_id)
            if preview.get("status") != "preview":
                result = preview
            elif args.decision is None and not args.yes and args.expected_sha256 is None:
                result = preview
            elif not args.decision or not args.yes or args.expected_sha256 != preview["content_sha256"]:
                raise ValueError("Review-Anwendung benötigt --decision, --yes und --expected-sha256 der aktuellen Vorschau.")
            else:
                decision = journey.decide(args.decision)
                result = {"status": decision.get("status"), "preview": preview, "decision": args.decision,
                          "receipt_id": decision.get("receipt_id"), "details": decision.get("details")}
            if args.operator:
                result["operator"] = args.operator
                result["actor_principal_id"] = operator_profile["principal_id"]
            if args.json:
                outgoing.write(json.dumps(result, ensure_ascii=False) + "\n")
            else:
                shown = result.get("preview", result)
                outgoing.write(f"Review: {result.get('status')}\nPrüfende Person: {args.operator or 'lokaler Owner'}\nEingereicht von: {shown.get('submitted_by')}\nQuelle: {shown.get('source')}\n"
                               f"Basis: {shown.get('base')}\nVorschlag: {shown.get('proposed_text')}\n")
                if shown.get("old_source") is not None:
                    outgoing.write(f"Alte Quellenbindung: {shown['old_source']}\n"
                                   f"Neue Quellenbindung: {shown['source']}\n")
                if shown.get("record_kind") in {"idea", "finding"}:
                    outgoing.write(f"Typ: {shown['record_kind']}; Status: {shown['record_status']}; kanonisch: nein. "
                                   "Freigabe bestätigt nur die Aufzeichnung, keinen Faktenbeleg.\n")
                if result.get("status") == "preview":
                    outgoing.write(f"Anwenden: review --workspace \"{workspace}\" --name {args.name} --candidate-id {shown['candidate_id']} "
                                   + (f"--operator {args.operator} " if args.operator else "") +
                                   f"--decision approve --expected-sha256 {shown['content_sha256']} --yes\n")
            outgoing.flush()
            return 0 if result.get("status") in {"preview", "accepted", "rejected"} else 1
        except (ValueError, OSError) as error:
            outgoing.write(json.dumps({"status": "needs_attention", "message": str(error)}, ensure_ascii=False) + "\n"
                           if args.json else f"Fehler: {error}\n")
            return 1

    if args.verb == "observe":
        try:
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                raise ValueError("Kein Workspace gewählt. Führe setup aus oder verwende --workspace.")
            workspace = Path(chosen).absolute()
            from .connections import resolve_connection
            from .knowledge_workspace import KnowledgeWorkspaceJourney
            core, _, profile = resolve_connection(workspace, args.connection)
            result = KnowledgeWorkspaceJourney(core, authority_id=profile["authority_id"],
                principal_id=profile["principal_id"], connection_name=args.connection,
                source_link_id=profile["source_link_id"], transport="cli").observe(
                    json.loads(args.cursor) if args.cursor else None)
            if args.json:
                outgoing.write(json.dumps(result, ensure_ascii=False) + "\n")
            else:
                outgoing.write(f"Beobachtung: {result['status']} — {result.get('message', '')}\n")
                outgoing.write(f"Dokumente: {result.get('documents_scanned', 0)}; Bytes: {result.get('bytes_scanned', 0)}; "
                               f"Metadaten-Einträge: {result.get('metadata_entries_examined', 0)} "
                               f"(Limit {result.get('metadata_entry_limit', 4096)}); "
                               f"Verzeichnisse: {result.get('metadata_directories_examined', 0)}; "
                               f"kanonische Änderungen: {result.get('canonical_writes', 0)}\n")
                if result.get("continuation_cursor") is not None:
                    outgoing.write("Weitere Seite: --cursor aus der JSON-Ausgabe unverändert übernehmen.\n")
            outgoing.flush()
            return 0 if result.get("status") in {"observed", "incomplete"} else 1
        except (ValueError, OSError) as error:
            outgoing.write(json.dumps({"status": "needs_attention", "message": str(error)}, ensure_ascii=False) + "\n"
                           if args.json else f"Fehler: {error}\n")
            return 1

    if args.verb in {"idea", "finding", "correct", "read", "contribute", "link", "global-read", "project-read", "feed", "curate"}:
        try:
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                raise ValueError("Kein Workspace gewählt. Führe setup aus oder verwende --workspace.")
            workspace = Path(chosen).absolute()
            from .project_workspace import SCHEMA as PROJECT_SCHEMA, LINKED_SCHEMA
            if args.verb == "project-read":
                core, state = open_workspace(workspace)
                result = core._named_project_reader_from_local_owner(workspace,
                    project_id=args.project_id, name=args.connection, action=args.action,
                    project_workspace=args.project_workspace, expected_sha256=args.expected_sha256,
                    apply=args.yes, recover=args.recover)
            elif args.verb == "global-read":
                core, state = open_workspace(workspace)
                result = core._named_global_reader_from_local_owner(workspace, name=args.connection,
                    action=args.action, expected_sha256=args.expected_sha256, apply=args.yes)
            elif args.verb == "link":
                if args.action is None and args.connection is None:
                    if not args.global_workspace or args.expected_sha256:
                        raise ValueError("Originale Verknüpfung benötigt --global-workspace ohne Beitragsgrant.")
                    from .project_reuse import ProjectReuseRegistration
                    operation = ProjectReuseRegistration(workspace, Path(args.global_workspace).absolute())
                    result = operation.preview()
                    if args.yes:
                        result = operation.apply()
                else:
                    if args.global_workspace or not args.connection or not args.action:
                        raise ValueError("Benanntes Beitragsrecht benötigt --connection und --action ohne Zielersetzung.")
                    core, state = open_workspace(workspace)
                    result = core._named_contribution_grant_from_local_owner(workspace, name=args.connection,
                        action=args.action, expected_sha256=args.expected_sha256, apply=args.yes)
            elif args.verb == "contribute":
                from .project_reuse import ProjectContribution
                operation = ProjectContribution(workspace, connection=args.connection)
                result = operation.preview(args.name, args.expected_revision, args.expected_sha256)
                if args.yes:
                    if not args.expected_revision or not args.expected_sha256:
                        raise ValueError("Beitrag benötigt --expected-revision und --expected-sha256 der aktuellen Vorschau.")
                    if result.get("status") == "preview":
                        result = operation.apply()
            elif args.verb == "feed":
                from .global_reuse import GlobalReuseJourney
                filters: dict[str, list[str]] = {}
                for term in args.filter:
                    key, separator, value = term.partition("=")
                    if not separator or not key or not value:
                        raise ValueError("--filter erwartet KEY=VALUE.")
                    filters.setdefault(key, []).append(value)
                result = GlobalReuseJourney(workspace, connection=args.connection).discover(
                    args.query, args.area, json.loads(args.cursor) if args.cursor else None,
                    stage=args.stage, filters=filters)
            elif args.verb == "curate":
                from .global_reuse import GlobalReuseJourney
                result = GlobalReuseJourney(workspace, connection=args.connection).curate(
                    name=args.name, contribution_id=args.contribution_id,
                    revision=args.expected_revision, content_sha256=args.expected_sha256,
                    base_revision=args.base_revision, base_sha256=args.base_sha256)
            else:
                core, state = open_workspace(workspace)
                from .knowledge_workspace import SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA
                project_profile = state.get("schema") in {PROJECT_SCHEMA, LINKED_SCHEMA}
                if not project_profile and not (args.verb == "read"
                        and state.get("schema") in {SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}):
                    raise ValueError("Idea, Finding und Project-Lesen benötigen einen Project-Workspace.")
                from .knowledge_workspace import KnowledgeWorkspaceJourney, _record_name
                from .project_workspace import AGENT as PROJECT_AGENT
                from .owner_journey import stable_operation_id
                journey = KnowledgeWorkspaceJourney(core, authority_id=state["authority_id"], principal_id=PROJECT_AGENT) if project_profile else None
                if args.verb in {"idea", "finding"}:
                    result = journey.project_record(kind=args.verb, name=args.name, area=args.area,
                                                    text=args.text, exception_kind=getattr(args, "exception_kind", None))
                elif args.verb == "correct":
                    if not args.name.startswith(("idea:", "finding:")):
                        raise ValueError("correct benötigt idea:NAME oder finding:NAME.")
                    if args.connection:
                        from .connections import resolve_connection
                        core, state, profile = resolve_connection(workspace, args.connection)
                        journey = KnowledgeWorkspaceJourney(core, authority_id=profile["authority_id"],
                            principal_id=profile["principal_id"], connection_name=args.connection,
                            source_link_id=profile["source_link_id"], transport="cli")
                    result = journey.correct(name=args.name, text=args.text,
                        expected_revision=args.expected_revision, expected_sha256=args.expected_sha256)
                elif args.connection:
                    from .connections import resolve_connection
                    core, state, profile = resolve_connection(workspace, args.connection)
                    if args.global_scope and not profile["authority_id"].startswith("project:"):
                        raise ValueError("Benanntes Global-Lesen benötigt einen Project-Workspace.")
                    if args.project and profile["authority_id"] != "user-global:source-access":
                        raise ValueError("Benanntes Project-Lesen benötigt einen Global-Workspace.")
                    if args.project and args.global_scope:
                        raise ValueError("Wähle genau einen fremden Lesebereich.")
                    named = KnowledgeWorkspaceJourney(core, authority_id=profile["authority_id"],
                        principal_id=profile["principal_id"], connection_name=args.connection,
                        source_link_id=profile["source_link_id"], transport="cli")
                    result = named.read(args.name, args.revision,
                                        scope="global" if args.global_scope else "project" if args.project else None,
                                        project_id=args.project)
                else:
                    if args.global_scope or args.project:
                        raise ValueError("Fremdes Lesen benötigt eine benannte Verbindung.")
                    selected_authority = state["authority_id"] if project_profile else "user-global:source-access"
                    payload = {"artifact_id": f"memory:{selected_authority.replace(':', '-')}-{_record_name(args.name)}"}
                    if args.revision:
                        payload["revision"] = args.revision
                    if project_profile:
                        owner = journey.owner
                    else:
                        from .owner import LocalOwnerAdapter
                        owner = LocalOwnerAdapter(core, principal_id="principal:local-owner",
                            active_authority_id="user-global:source-access",
                            reported={"agent_name": "human-cli", "model": "none"},
                            adapter_observed={"runtime": "owledge-local-cli", "runtime_version": "1", "run_id": "essence-read"})
                    found = owner.execute("curated_read", stable_operation_id("native-owner-read", payload), payload)
                    if found.get("reason_code") == "reference_not_found":
                        result = {"status": "not_found", "message": "Keine freigegebene Referenz; kein Gap angelegt."}
                    elif found.get("status") == "ok":
                        result = {"status": "answered", **found["data"]}
                    else:
                        result = {"status": "needs_attention", "details": found}
            if args.json:
                outgoing.write(json.dumps(result, ensure_ascii=False) + "\n")
            else:
                outgoing.write(f"{result.get('status')}: {result.get('message', '')}\n")
                if result.get("record_kind") or result.get("knowledge_kind") in {"idea", "finding"}:
                    outgoing.write(f"Typ: {result.get('record_kind') or result.get('knowledge_kind')}"
                                   f"; Status: {result.get('record_status')}; kanonisch: nein\n")
                if "text" in result:
                    outgoing.write(str(result["text"]) + "\n")
                if "proposed_text" in result:
                    outgoing.write(f"Vorschlag: {result['proposed_text']}\n")
                if result.get("status") == "preview" and args.verb == "contribute":
                    source = result.get("source", {})
                    outgoing.write(f"Anwenden: contribute --workspace \"{workspace}\" --name {args.name} "
                                   + (f"--connection {args.connection} " if args.connection else "") +
                                   f"--expected-revision {source.get('revision')} --expected-sha256 {source.get('content_sha256')} --yes\n")
                if result.get("status") == "preview" and args.verb == "link" and args.connection:
                    outgoing.write(f"Anwenden: link --workspace \"{workspace}\" --connection {args.connection} "
                                   f"--action {args.action} --expected-sha256 {result['expected_sha256']} --yes\n")
                if result.get("status") == "preview" and args.verb == "global-read":
                    outgoing.write(f"Anwenden: global-read --workspace \"{workspace}\" --connection {args.connection} "
                                   f"--action {args.action} --expected-sha256 {result['expected_sha256']} --yes\n")
                if result.get("status") == "preview" and args.verb == "project-read":
                    outgoing.write(f"Anwenden: project-read --workspace \"{workspace}\" --project-id {args.project_id} "
                                   f"--connection {args.connection} --action {args.action} "
                                   + (f"--project-workspace \"{args.project_workspace}\" " if args.project_workspace else "")
                                   + f"--expected-sha256 {result['expected_sha256']} --yes\n")
                if args.verb == "feed":
                    for item in result.get("entries", result.get("contributions", [])):
                        kind = item.get("knowledge_kind")
                        label = "Möglichkeit" if kind == "idea" else "Signal" if kind == "finding" else "Feed, ungeprüft"
                        outgoing.write(f"{label}: {item}\n")
                if result.get("status") == "preview" and args.verb == "curate":
                    outgoing.write(f"Kandidat: {result['candidate_id']} (noch nicht freigegeben)\n"
                                   f"Nächster Schritt: review --workspace \"{workspace}\" --name {args.name} "
                                   f"--candidate-id {result['candidate_id']}\n")
            outgoing.flush()
            return 0 if result.get("status") in {"preview", "accepted", "answered", "recorded", "ready", "discovered", "incomplete"} else 1
        except (ValueError, OSError) as error:
            outgoing.write(json.dumps({"status": "needs_attention", "message": str(error)}, ensure_ascii=False) + "\n"
                           if args.json else f"Fehler: {error}\n")
            return 1

    if args.verb in {"status", "register", "search", "ingest"}:
        try:
            selection = read_selection(config_path) if config_path is not None and not args.workspace else {}
            chosen = args.workspace or selection.get("workspace")
            if not chosen:
                if args.verb == "status" and config_path is None:
                    chosen = "."
                else:
                    raise ValueError("Kein Workspace gewählt. Führe setup aus oder verwende --workspace.")
            args.workspace = str(Path(chosen).absolute())
            if args.verb in {"register", "search", "ingest"}:
                return _run_native(args, outgoing, selection)
        except (ValueError, OSError) as error:
            result = {"status": "needs_attention", "message": str(error)}
            outgoing.write(json.dumps(result, ensure_ascii=False) + "\n" if args.json else f"Fehler: {error}\n")
            return 1

    if args.verb == "status":
        workspace = Path(args.workspace).absolute()
        try:
            result = {"workspace": str(workspace), **workspace_health(workspace)}
        except (ValueError, OSError) as error:
            result = {
                "workspace": str(workspace),
                "status": "needs_attention",
                "message": (
                    f"Workspace kann nicht geprüft werden: {error} "
                    "Wähle den richtigen Workspace; führe bei fehlendem Setup setup aus oder nutze "
                    "bei einem unterbrochenen Zustand den bestehenden Recovery-/Doctor-Pfad."
                ),
            }
        if result.get("runtime_current") is False:
            result["runtime_warning"] = "Laufzeitbindung ist veraltet; vor weiterer Arbeit setup --upgrade ausführen."
        if args.json:
            outgoing.write(json.dumps(result, ensure_ascii=True) + "\n")
        else:
            outgoing.write(f"Status: {result['status']}\n")
            if "runtime_current" in result:
                outgoing.write(f"Laufzeit: {'aktuell' if result['runtime_current'] else 'veraltet'}\n")
            labels = {
                "source_unchanged": "Quelle unverändert",
                "originals_unchanged": "Originalkopie unverändert",
                "trace_verified": "Trace geprüft",
                "receipts_verified": "Receipts geprüft",
            }
            for key, label in labels.items():
                if key in result:
                    outgoing.write(f"{label}: {result[key]}\n")
            imports = result.get("imports")
            if isinstance(imports, list):
                failed_imports = sum(item.get("source_unchanged") is not True for item in imports if isinstance(item, dict))
                outgoing.write(f"Importe mit Handlungsbedarf: {failed_imports}\n")
                if failed_imports:
                    outgoing.write("Nächster Schritt: Betroffene Quellen und Importe mit doctor prüfen.\n")
            elif result.get("source_unchanged") is False:
                outgoing.write("Nächster Schritt: Die konfigurierte Quelle mit doctor prüfen.\n")
            if result.get("runtime_warning"):
                outgoing.write(f"Warnung: {result['runtime_warning']}\n")
            if result.get("message"):
                outgoing.write(f"Hinweis: {result['message']}\n")
        outgoing.flush()
        return 0 if result["status"] == "healthy" else 1

    try:
        from .project_workspace import SCHEMA as PROJECT_SCHEMA, LINKED_SCHEMA
        if args.inbox and not (args.verb == "maintain" and args.action == "ingest"):
            raise ValueError("--inbox gehört ausschließlich zur Aktion ingest.")
        if args.access and not (args.verb == "maintain" and args.action == "ingest" and not args.recover_import):
            raise ValueError("--access gehört ausschließlich zur neuen Quellenregistrierung oder einem expliziten ingest.")
        if args.verb == "maintain" and args.action == "link-global":
            from .project_reuse import ProjectReuseRegistration
            if not args.global_workspace:
                raise ValueError("Wähle mit --global-workspace einen bestehenden Knowledge-Workspace.")
            operation = ProjectReuseRegistration(Path(args.workspace), Path(args.global_workspace))
            emit({"status": "preview", "message": "Unterbrochene Beitragsverknüpfung wiederherstellen."} if args.recover_link else operation.preview())
            outgoing.write("apply oder reject: ")
            outgoing.flush()
            if incoming.readline().strip().lower() != "apply":
                emit({"status": "cancelled"})
                return 0
            emit(operation.recover() if args.recover_link else operation.apply())
            return 0
        if args.global_workspace or args.recover_link:
            raise ValueError("Global-Auswahl und Wiederherstellung gehören zur Aktion link-global.")
        from .local_setup import _state_bytes
        workspace_state = None
        from .ingest import inbox_journal_pending
        recovering_import = (args.verb == "maintain" and args.action == "ingest" and args.recover_import
                             and ((Path(args.workspace) / ".owledge/source-registration.json").exists()
                                  or inbox_journal_pending(Path(args.workspace), Path(args.inbox) if args.inbox else None)))
        # A pending registration deliberately blocks ordinary workspace reads.
        # Its existing Owner recovery path validates the journal and authority.
        if not recovering_import and (Path(args.workspace) / "workspace.json").exists():
            workspace_state = json.loads(_state_bytes(Path(args.workspace)))
        project_profile = (isinstance(workspace_state, dict)
                           and workspace_state.get("schema") in {PROJECT_SCHEMA, LINKED_SCHEMA})
        if project_profile and (args.source or args.inbox or args.source_file or args.source_link or args.area or args.discover_areas
                or args.depth != "curated" or args.archive or args.recover_import
                or (args.verb == "maintain" and args.action not in {"lesson", "review", "contribute"}
                    and not (args.action == "correct" and args.name.startswith("lesson:")))):
            raise ValueError("Projektprofil unterstützt Lesson-Vorschlag, exakte Lesson-Korrektur, lokale Review, Beitrag, Lesen und Doctor; keine Quellen- oder Global-Kuratierung.")
        if project_profile and args.verb == "maintain" and args.action == "contribute":
            from .project_reuse import ProjectContribution
            operation = ProjectContribution(Path(args.workspace))
            preview = operation.preview(args.name, args.revision)
            emit(preview)
            if preview.get("status") != "preview":
                return 1
            outgoing.write("apply oder reject: ")
            outgoing.flush()
            if incoming.readline().strip().lower() != "apply":
                emit({"status": "cancelled"})
                return 0
            result = operation.apply()
            emit(result)
            return 0 if result.get("status") == "recorded" else 1
        if args.verb == "maintain" and args.action == "ingest":
            from .ingest import SourceImport
            if args.recover_import:
                from .ingest import recover_import, recover_inbox_import
                emit({"status": "preview", "message": "Unterbrochene Quellenregistrierung abschließen; keine Wissensfreigabe."})
                outgoing.write("apply oder reject: ")
                outgoing.flush()
                if incoming.readline().strip().lower() != "apply":
                    emit({"status": "cancelled"})
                    return 0
                if args.inbox and inbox_journal_pending(Path(args.workspace), Path(args.inbox)):
                    emit(recover_inbox_import(Path(args.workspace), Path(args.inbox)))
                else:
                    emit(recover_import(Path(args.workspace)))
                return 0
            if not args.source:
                raise ValueError("Wähle mit --source eine bestehende Markdown-Datei oder einen Markdown-Ordner.")
            if args.inbox:
                from .ingest import InboxImport
                operation = InboxImport(Path(args.workspace), Path(args.inbox), Path(args.source), access=args.access)
            else:
                operation = SourceImport(Path(args.workspace), Path(args.source), access=args.access)
            emit(operation.preview())
            outgoing.write("apply oder reject: ")
            outgoing.flush()
            if incoming.readline().strip().lower() != "apply":
                emit({"status": "cancelled", "message": "Keine Quelle registriert."})
                return 0
            emit(operation.apply())
            return 0
        if args.verb == "maintain" and args.action in {"backup", "restore"}:
            from .workspace_archive import WorkspaceArchive
            if not args.archive:
                raise ValueError("Wähle mit --archive eine Sicherungsdatei.")
            operation = WorkspaceArchive(Path(args.workspace), Path(args.archive), args.action)
            emit(operation.preview())
            outgoing.write("apply oder reject: ")
            outgoing.flush()
            if incoming.readline().strip().lower() != "apply":
                emit({"status": "cancelled", "message": "Abgebrochen; keine Sicherung oder Wiederherstellung geschrieben."})
                return 0
            emit(operation.apply())
            return 0
        if args.verb == "doctor":
            result = workspace_health(Path(args.workspace))
            emit(result)
            return 0 if result["status"] == "healthy" else 1
        core, state = open_workspace(Path(args.workspace))
        from .source_workspace import SCHEMA, SourceWorkspaceJourney
        source_only = state.get("schema") == SCHEMA
        from .knowledge_workspace import SCHEMA as KNOWLEDGE_SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA, CASE, KnowledgeWorkspaceJourney
        from .project_workspace import SCHEMA as PROJECT_SCHEMA, AGENT as PROJECT_AGENT
        knowledge_schemas = {KNOWLEDGE_SCHEMA, MULTISOURCE_SCHEMA, SOURCE_FREE_SCHEMA}
        if state.get("schema") in {*knowledge_schemas, PROJECT_SCHEMA, LINKED_SCHEMA}:
            knowledge = (KnowledgeWorkspaceJourney(core, authority_id=state["authority_id"], principal_id=PROJECT_AGENT)
                         if state.get("schema") in {PROJECT_SCHEMA, LINKED_SCHEMA} else KnowledgeWorkspaceJourney(core))
            if args.verb == "ask" and args.depth == "feed" and state.get("schema") in knowledge_schemas:
                from .global_reuse import GlobalReuseJourney
                result = GlobalReuseJourney(Path(args.workspace)).discover(
                    args.question, args.knowledge_area, json.loads(args.cursor) if args.cursor else None)
            elif args.verb == "ask" and args.depth != "originals":
                result = (knowledge.read(args.name, args.revision) if args.name else knowledge.discover(
                    args.question, args.knowledge_area, json.loads(args.cursor) if args.cursor else None))
            elif args.verb == "maintain" and args.action == "lesson":
                result = knowledge.lesson(name=args.name, area=args.knowledge_area or "agent-work", text=args.text,
                    origin=args.origin, conditions=args.conditions, verification=args.verification, limitations=args.limitations)
            elif args.verb == "maintain" and args.action in {"propose", "correct"}:
                search = {"coverage_case_id": CASE, "query": args.question,
                          "source_areas": args.area or ["."], "source_cursor": json.loads(args.cursor) if args.cursor else None,
                          "source_link_id": args.source_link}
                proposal = dict(name=args.name, area=args.knowledge_area or "reference", text=args.text,
                                source_file=args.source_file, search=search)
                result = (knowledge.correct(**proposal, expected_revision=args.expected_revision, expected_sha256=args.expected_sha256)
                          if args.action == "correct" else knowledge.propose(**proposal))
            elif args.verb == "maintain" and args.action == "review":
                preview = knowledge.preview(args.name, args.candidate_id)
                emit(preview)
                if preview.get("status") != "preview":
                    return 1
                outgoing.write("approve, reject oder cancel: ")
                outgoing.flush()
                result = knowledge.decide(incoming.readline().strip().lower())
            elif args.verb == "maintain" and args.action == "curate" and state.get("schema") in knowledge_schemas:
                if not all((args.name, args.contribution_id, args.revision, args.expected_sha256)):
                    raise ValueError("Curation requires --name, --contribution-id, --revision and --expected-sha256 from Feed discovery.")
                if bool(args.base_revision) != bool(args.base_sha256):
                    raise ValueError("Global refresh requires both --base-revision and --base-sha256.")
                from .global_reuse import GlobalReuseJourney
                reuse = GlobalReuseJourney(Path(args.workspace))
                preview = reuse.curate(name=args.name, contribution_id=args.contribution_id,
                                       revision=args.revision, content_sha256=args.expected_sha256,
                                       base_revision=args.base_revision or None, base_sha256=args.base_sha256 or None)
                emit(preview)
                if preview.get("status") != "preview":
                    return 1
                outgoing.write("approve, reject oder cancel: ")
                outgoing.flush()
                result = reuse.decide(incoming.readline().strip().lower())
            elif args.verb == "ask":
                if state.get("schema") == SOURCE_FREE_SCHEMA and not state["imports"]:
                    result = {"status": "not_available", "message": "Registriere zuerst eine Quelle für die Originalsuche."}
                else:
                    source_journey = SourceWorkspaceJourney(core)
                    source_journey.agent = knowledge.agent
                    result = source_journey.ask(args.question, args.depth, source_areas=tuple(args.area or ["."]),
                        source_cursor=json.loads(args.cursor) if args.cursor else None, discover_source_areas=args.discover_areas,
                        source_area_parent=args.area_parent, source_link_id=args.source_link)
            else:
                result = {"status": "not_available", "message": "Dieses Profil unterstützt Vorschlag und lokale Freigabe, keine automatische Wartung."}
            emit(result)
            return 0 if result.get("status") in {"answered", "discovered", "not_found", "incomplete", "preview", "accepted", "rejected", "cancelled"} else 1
        if source_only and args.verb == "maintain":
            emit({"status": "not_available", "message": "Quellenzugang ist schreibgeschützt; keine Wissenspflege oder Freigabe verfügbar."})
            return 1
        journey = SourceWorkspaceJourney(core) if source_only else WorkspaceOwnerJourney(core, workspace=Path(args.workspace))
        if args.verb == "ask":
            question = args.question
            if not question and not args.discover_areas:
                outgoing.write("Frage oder Suchwort: ")
                outgoing.flush()
                question = incoming.readline().strip()
            cursor = json.loads(args.cursor) if args.cursor else None
            if cursor is not None and not isinstance(cursor, dict):
                raise ValueError("--cursor erwartet das unveränderte JSON-Objekt der vorherigen Antwort.")
            result = journey.ask(question, args.depth, source_areas=tuple(args.area or ["."]),
                                 source_cursor=cursor, discover_source_areas=args.discover_areas,
                                 source_area_parent=args.area_parent, source_link_id=args.source_link)
            emit(result)
            return 0 if result.get("status") in {"answered", "not_found", "incomplete"} else 1
        if args.action == "contribute":
            result = journey.contribute(args.topic)
            if result.get("status") == "ok":
                emit({"status": "recorded", "source": "DEMO-Projekt / " + args.topic + ".md",
                    "message": "DEMO-Beitrag in Wiederverwendung aufgenommen, nichtkanonisch."})
                return 0
            emit(LocalOwnerHost._friendly_failure(result))
            return 1
        if args.action == "curate":
            preview = journey.preview_curation(args.topic)
            emit(preview)
            if preview.get("status") != "preview":
                return 1
            outgoing.write("approve, reject oder cancel: ")
            outgoing.flush()
            result = journey.decide_curation(incoming.readline().strip().lower() or "cancel")
            emit(result)
            return 0 if result.get("status") in {"accepted", "rejected", "cancelled"} else 1
        if args.action == "summary":
            result = journey.summary()
            emit(result)
            return 0 if result.get("status") in {"observed", "incomplete"} else 1
        if args.action == "gap":
            host = journey.gap_host()
            result = host.run("ask", question="Welches Reviewfenster gilt für Agent Lessons?")
            emit(result)
            if result.get("status") == "answered":
                return 0
            if result.get("status") != "needs_input":
                return 1
            outgoing.write("DEMO: Innerhalb wie vieler Stunden prüfen (1–168)? ")
            outgoing.flush()
            answer = incoming.readline().strip()
            if not answer or answer.lower() in {"cancel", "reject"}:
                emit({"status": "cancelled", "message": "Keine Antwort und keine Freigabe gespeichert."})
                return 0
            preview = host.run("maintain", answer=answer)
            emit(preview)
            if preview.get("status") != "preview":
                return 1
            outgoing.write("approve oder reject: ")
            outgoing.flush()
            decision = incoming.readline().strip().lower()
            result = host.run("maintain", decision="approve" if decision == "approve" else "reject")
            if result.get("status") == "accepted" and host.last_receipt_id:
                record_workspace_trace(Path(args.workspace), host.last_receipt_id)
            emit(result)
            return 0 if result.get("status") in {"accepted", "cancelled"} else 1
        raise ValueError("Diese Wartungsaktion ist noch nicht verfügbar.")
    except (ValueError, OSError) as error:
        emit({"status": "needs_attention", "message": str(error)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


def entry() -> int:
    # The installed executable owns its pipe encoding; injected main() streams do not.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="strict")
    return main(config_path=default_config_path())
