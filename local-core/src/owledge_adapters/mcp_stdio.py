"""Bound, local stdio MCP transport for named Contributor profiles."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import BinaryIO

from .connections import resolve_connection
from .knowledge_workspace import KnowledgeWorkspaceJourney, search_knowledge
from .owner_journey import stable_operation_id


_MAX_LINE = 1_048_576
_VERSIONS = {"2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"}


def _schema(properties: dict[str, dict], required: list[str]) -> dict:
    return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}


_STRING = {"type": "string"}
_TOOLS = [
    {"name": "owledge_settings", "description": "Read effective scoped Recall and Skill-owned Research policy without changing Settings.",
     "inputSchema": _schema({"research_limit": {"type": "string", "enum": ["none", "targeted", "deep"]}}, [])},
    {"name": "owledge_search", "description": "Search reviewed knowledge and permitted original evidence; results are not an absence proof.",
     "inputSchema": _schema({"query": _STRING, "cursor": {"type": "object"}, "project_id": _STRING,
                             "recall_limit": {"type": "string", "enum": ["focused", "expanded", "audit"]},
                             "scope": {"type": "string", "enum": ["project", "global"]},
                             "filters": {"type": "object", "properties": {
                                 key: {"type": "array", "items": _STRING, "minItems": 1, "maxItems": 16}
                                 for key in ("authority_scope", "knowledge_area", "knowledge_kind", "memory_kind",
                                             "processing_layer", "lifecycle", "source_trust", "access")},
                                 "additionalProperties": False}}, ["query"])},
    {"name": "owledge_observe", "description": "Explicitly observe a bounded Global maintenance page without canonical writes.",
     "inputSchema": _schema({"cursor": {"type": "object"}}, [])},
    {"name": "owledge_read", "description": "Read an exact reviewed Lesson, nonfactual Project Idea/Finding, or source reference by handle.",
     "inputSchema": _schema({"name": _STRING, "revision": _STRING, "project_id": _STRING,
                              "scope": {"type": "string", "enum": ["project", "global"]}}, ["name"])},
    {"name": "owledge_propose_lesson", "description": "Stage a Lesson for separate human review; never approves it.",
     "inputSchema": _schema({key: _STRING for key in
                             ("name", "area", "text", "origin", "conditions", "verification", "limitations")},
                            ["name", "area", "text", "origin", "conditions", "verification", "limitations"])},
    {"name": "owledge_propose_reference", "description": "Stage one current authorized original as a reference for separate Owner review.",
     "inputSchema": _schema({key: _STRING for key in
                             ("name", "area", "text", "source_link_id", "source_file", "query")}
                            | {"cursor": {"type": "object"}},
                            ["name", "area", "text", "source_link_id", "source_file", "query"])},
    {"name": "owledge_correct_lesson", "description": "Stage an exact-base Project Lesson correction for separate human review.",
     "inputSchema": _schema({key: _STRING for key in ("name", "text", "expected_revision", "expected_sha256")},
                            ["name", "text", "expected_revision", "expected_sha256"])},
    {"name": "owledge_correct_record", "description": "Stage an exact-base Project Idea or Finding text correction for separate human review.",
     "inputSchema": _schema({key: _STRING for key in ("name", "text", "expected_revision", "expected_sha256")},
                            ["name", "text", "expected_revision", "expected_sha256"])},
    {"name": "owledge_propose_idea", "description": "Stage a Project possibility for separate human recording review; never factual evidence.",
     "inputSchema": _schema({key: _STRING for key in ("name", "area", "text")}, ["name", "area", "text"])},
    {"name": "owledge_report_finding", "description": "Stage an exceptional Project signal for separate human review and sparse Inbox contribution.",
     "inputSchema": _schema({key: _STRING for key in ("name", "area", "text", "exception_kind")},
                            ["name", "area", "text", "exception_kind"])},
    {"name": "owledge_case_query", "description": "Query one configured Project case without admitting a Gap.",
     "inputSchema": _schema({"name": _STRING}, ["name"])},
    {"name": "owledge_case_propose", "description": "Stage a bounded Project case answer for separate human review.",
     "inputSchema": _schema({key: _STRING for key in ("name", "text", "expected_revision", "expected_sha256")},
                            ["name", "text"])},
    {"name": "owledge_contribute", "description": "Submit one exact reviewed Project record to the noncanonical Global Feed through the saved grant.",
     "inputSchema": _schema({key: _STRING for key in ("name", "expected_revision", "expected_sha256")},
                            ["name", "expected_revision", "expected_sha256"])},
    {"name": "owledge_feed", "description": "Discover noncanonical Global Feed handles; discovery never approves content.",
     "inputSchema": _schema({"query": _STRING, "area": _STRING, "cursor": {"type": "object"},
                             "stage": {"type": "string", "enum": ["reuse_feed", "inbox"]},
                             "filters": {"type": "object", "properties": {
                                 key: {"type": "array", "items": _STRING, "minItems": 1, "maxItems": 16}
                                 for key in ("authority_scope", "knowledge_area", "knowledge_kind", "memory_kind",
                                             "processing_layer", "lifecycle", "source_trust", "access")},
                                 "additionalProperties": False}}, ["query"])},
    {"name": "owledge_curate", "description": "Stage one exact Global curation Candidate for separate human review.",
     "inputSchema": _schema({key: _STRING for key in ("name", "contribution_id", "revision", "content_sha256",
                                                 "base_revision", "base_sha256")},
                            ["name", "contribution_id", "revision", "content_sha256"])},
]
_TOOL_SCHEMAS = {tool["name"]: tool["inputSchema"] for tool in _TOOLS}


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    value: dict = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON member")
        value[key] = item
    return value


def _checked_arguments(name: str, arguments: object) -> dict:
    schema = _TOOL_SCHEMAS.get(name)
    if schema is None or not isinstance(arguments, dict):
        raise ValueError("unknown tool or invalid arguments")
    if set(arguments) - set(schema["properties"]) or any(key not in arguments for key in schema["required"]):
        raise ValueError("unknown, identity, or missing tool argument")
    for key, value in arguments.items():
        if key == "cursor":
            if not isinstance(value, dict):
                raise ValueError("cursor must be an object")
        elif key == "filters":
            if (not isinstance(value, dict) or len(value) > 8
                    or len(json.dumps(value, ensure_ascii=False).encode("utf-8")) > 8192):
                raise ValueError("filters must be a bounded object")
        elif key == "scope":
            if not isinstance(value, str) or value not in {"project", "global"}:
                raise ValueError("scope must be project or global")
        elif key == "stage":
            if not isinstance(value, str) or value not in {"reuse_feed", "inbox"}:
                raise ValueError("stage must be reuse_feed or inbox")
        elif not isinstance(value, str) or (key != "text" and not value.strip()) or len(value) > 16_384:
            raise ValueError("tool string argument is invalid or too large")
    return arguments


def _checked_meta(value: object) -> None:
    if not isinstance(value, dict) or len(json.dumps(value, ensure_ascii=False).encode("utf-8")) > 4096:
        raise ValueError("request metadata is invalid or too large")
    token = value.get("progressToken")
    if token is not None and (not isinstance(token, (str, int, float)) or isinstance(token, bool)
                              or isinstance(token, str) and len(token) > 128):
        raise ValueError("progress token is invalid")


def _invoke(workspace: Path, connection: str, name: str, arguments: dict) -> dict:
    core, state, profile = resolve_connection(workspace, connection)
    principal = profile["principal_id"]
    authority = profile["authority_id"]
    link = profile["source_link_id"]
    journey = KnowledgeWorkspaceJourney(core, authority_id=authority, principal_id=principal,
                                        connection_name=connection, source_link_id=link)
    if name == "owledge_settings":
        payload = {"research_limit": arguments["research_limit"]} if "research_limit" in arguments else {}
        result = journey.agent.execute("settings_inspect", stable_operation_id("named-settings", payload), payload)
        return {"status": "ready", **result["data"]} if result.get("status") == "ok" else {
            "status": "needs_attention", "reason_code": result.get("reason_code"),
            "message": result.get("summary"), "next_action": result.get("next_action")}
    if name == "owledge_search":
        if authority != "user-global:source-access":
            return journey.discover(arguments["query"], cursor=arguments.get("cursor"),
                                    filters=arguments.get("filters"), scope=arguments.get("scope"),
                                    project_id=arguments.get("project_id"), recall_limit=arguments.get("recall_limit"))
        if arguments.get("scope") == "project" and arguments.get("project_id"):
            return journey.discover(arguments["query"], cursor=arguments.get("cursor"),
                                    filters=arguments.get("filters"), scope="project",
                                    project_id=arguments["project_id"], recall_limit=arguments.get("recall_limit"))
        if arguments.get("scope") is not None or arguments.get("project_id") is not None:
            raise ValueError("Global Project search requires scope project and exact project_id")
        return search_knowledge(core, state, workspace, arguments["query"], adapter=journey.agent,
                                cursor=arguments.get("cursor"), bound_source_link=link,
                                filters=arguments.get("filters"), recall_limit=arguments.get("recall_limit"))
    if name == "owledge_observe":
        return journey.observe(arguments.get("cursor"))
    if name == "owledge_read":
        if authority == "user-global:source-access" and arguments.get("scope") == "project" and arguments.get("project_id"):
            return journey.read(arguments["name"], arguments.get("revision"), scope="project",
                                project_id=arguments["project_id"])
        if authority == "user-global:source-access" and (arguments.get("scope") is not None or arguments.get("project_id") is not None):
            raise ValueError("Global Project read requires scope project and exact project_id")
        return journey.read(arguments["name"], arguments.get("revision"),
                            scope=arguments.get("scope"), project_id=arguments.get("project_id"))
    if name == "owledge_contribute":
        if not authority.startswith("project:") or link is not None:
            raise ValueError("Contribution requires an unbound named Project Contributor")
        from .project_reuse import ProjectContribution
        operation = ProjectContribution(workspace, connection=connection, transport="mcp")
        preview = operation.preview(arguments["name"], arguments["expected_revision"], arguments["expected_sha256"])
        return operation.apply() if preview.get("status") == "preview" else preview
    if name in {"owledge_feed", "owledge_curate"}:
        if authority != "user-global:source-access" or link is not None:
            raise ValueError("Global Feed requires an unbound named Global Contributor")
        from .global_reuse import GlobalReuseJourney
        reuse = GlobalReuseJourney(workspace, connection=connection, transport="mcp")
        if name == "owledge_feed":
            return reuse.discover(arguments["query"], arguments.get("area"), arguments.get("cursor"),
                                  stage=arguments.get("stage", "reuse_feed"), filters=arguments.get("filters"))
        return reuse.curate(name=arguments["name"], contribution_id=arguments["contribution_id"],
            revision=arguments["revision"], content_sha256=arguments["content_sha256"],
            base_revision=arguments.get("base_revision"), base_sha256=arguments.get("base_sha256"))
    if name == "owledge_propose_lesson":
        return journey.lesson(**arguments)
    if name == "owledge_propose_reference":
        if authority != "user-global:source-access" or link not in (None, arguments["source_link_id"]):
            raise ValueError("Reference proposals require this bound Global source")
        from .knowledge_workspace import CASE
        search = {"coverage_case_id": CASE, "query": arguments["query"], "source_areas": ["."],
                  "source_cursor": arguments.get("cursor"), "source_link_id": arguments["source_link_id"]}
        return journey.propose(name=arguments["name"], area=arguments["area"], text=arguments["text"],
                               source_file=arguments["source_file"], search=search)
    if name in {"owledge_case_query", "owledge_case_propose"}:
        if not authority.startswith("project:"):
            raise ValueError("Named cases require a Project connection")
        from .project_workspace import ProjectCaseJourney
        cases = ProjectCaseJourney(core, authority, principal_id=principal)
        if name == "owledge_case_query":
            return cases.ask(arguments["name"])
        return cases.answer(arguments["name"], arguments["text"],
                            expected_revision=arguments.get("expected_revision"),
                            expected_sha256=arguments.get("expected_sha256"))
    if name in {"owledge_propose_idea", "owledge_report_finding"}:
        if not authority.startswith("project:"):
            raise ValueError("Typed Ideas and Findings require a Project connection")
        return journey.project_record(kind="idea" if name == "owledge_propose_idea" else "finding", **arguments)
    if name == "owledge_correct_record":
        if not authority.startswith("project:") or not arguments["name"].startswith(("idea:", "finding:")):
            raise ValueError("Typed corrections require a Project Idea or Finding handle")
        return journey.correct(**arguments)
    if not authority.startswith("project:") or not arguments["name"].startswith("lesson:"):
        raise ValueError("Only reviewed Project Lesson handles support this correction tool")
    return journey.correct(name=arguments["name"], text=arguments["text"],
                           expected_revision=arguments["expected_revision"],
                           expected_sha256=arguments["expected_sha256"])


def serve(workspace: Path, connection: str, incoming: BinaryIO, outgoing: BinaryIO) -> int:
    """Handle one installed client until EOF; stdout is JSON-RPC only."""
    resolve_connection(workspace, connection)  # fail before announcing tools or reading knowledge
    negotiated = False
    ready = False

    def write(value: dict) -> None:
        outgoing.write((json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
        outgoing.flush()

    def error(identifier: object, code: int, message: str) -> None:
        write({"jsonrpc": "2.0", "id": identifier, "error": {"code": code, "message": message}})

    while True:
        line = incoming.readline(_MAX_LINE + 1)
        if not line:
            return 0
        if len(line) > _MAX_LINE or not line.endswith(b"\n"):
            error(None, -32600, "request exceeds the bounded stdio line")
            if not line.endswith(b"\n"):
                while line and not line.endswith(b"\n"):
                    line = incoming.readline(_MAX_LINE + 1)
            continue
        try:
            request = json.loads(line.decode("utf-8"), object_pairs_hook=_unique_object,
                                 parse_constant=lambda value: (_ for _ in ()).throw(ValueError("non-finite JSON value")))
        except (UnicodeDecodeError, ValueError):
            error(None, -32700, "invalid UTF-8 JSON")
            continue
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
            error(request.get("id") if isinstance(request, dict) else None, -32600, "invalid JSON-RPC request")
            continue
        identifier = request.get("id")
        method = request["method"]
        if "id" not in request:
            if method == "notifications/initialized" and negotiated:
                ready = True
            # JSON-RPC notifications have no response, including unknown ones.
            continue
        if not isinstance(identifier, (str, int)) or isinstance(identifier, bool):
            error(None, -32600, "request id is invalid")
            continue
        params = request.get("params", {})
        if not isinstance(params, dict):
            error(identifier, -32602, "params must be an object")
            continue
        if method == "initialize":
            if negotiated or not isinstance(params.get("protocolVersion"), str):
                error(identifier, -32602, "initialize parameters are invalid")
                continue
            requested = params["protocolVersion"]
            version = requested if requested in _VERSIONS else "2025-06-18"
            negotiated = True
            write({"jsonrpc": "2.0", "id": identifier, "result": {
                "protocolVersion": version, "capabilities": {"tools": {}},
                "serverInfo": {"name": "owledge-local", "version": "0.0.0.dev0"}}})
            continue
        if not ready:
            error(identifier, -32002, "initialize and send notifications/initialized first")
            continue
        if method == "ping":
            write({"jsonrpc": "2.0", "id": identifier, "result": {}})
        elif method == "tools/list":
            try:
                if set(params) - {"cursor", "_meta"} or params.get("cursor") is not None:
                    raise ValueError("unknown tools/list arguments")
                if "_meta" in params:
                    _checked_meta(params["_meta"])
                write({"jsonrpc": "2.0", "id": identifier, "result": {"tools": _TOOLS}})
            except ValueError as problem:
                error(identifier, -32602, str(problem))
        elif method == "tools/call":
            try:
                if set(params) not in ({"name", "arguments"}, {"name", "arguments", "_meta"}) or not isinstance(params["name"], str):
                    raise ValueError("tool call arguments are invalid")
                if "_meta" in params:
                    _checked_meta(params["_meta"])
                arguments = _checked_arguments(params["name"], params["arguments"])
                result = _invoke(workspace, connection, params["name"], arguments)
                failure = result.get("status") in {"needs_attention", "denied", "invalid", "recovery_required"}
                write({"jsonrpc": "2.0", "id": identifier, "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                    "structuredContent": result, "isError": failure}})
            except ValueError as problem:
                error(identifier, -32602, str(problem))
        else:
            error(identifier, -32601, "method not found")


def entry(workspace: Path, connection: str) -> int:
    try:
        return serve(workspace, connection, sys.stdin.buffer, sys.stdout.buffer)
    except (ValueError, OSError) as error:
        print(f"Owledge MCP: {error}", file=sys.stderr)
        return 1
