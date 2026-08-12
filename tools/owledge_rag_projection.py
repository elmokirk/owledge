#!/usr/bin/env python3
"""Clean, deterministic RAG projection v1; never embeds governance frontmatter."""
from __future__ import annotations
import hashlib
import re
from typing import Any

PRIVATE = {"personal", "special-category", "secret"}

def _body_sections(body: str) -> list[tuple[str, str]]:
    sections=[]; heading=""
    for part in re.split(r"(?m)^(#{1,6}\s+.+)$", body):
        if part.startswith("#"): heading=re.sub(r"^#+\s*", "", part).strip()
        elif part.strip(): sections.append((heading, part.strip()))
    return sections or [("", body.strip())]

def project(record: dict[str, Any]) -> list[dict[str, Any]]:
    meta=record["metadata"]
    if str(meta.get("data_class", "internal")).lower() in PRIVATE: return []
    if str(meta.get("source_freshness", meta.get("freshness", "current"))).lower() in {"stale","expired"}: return []
    doc_type=str(meta.get("doc_type", ""))
    if doc_type in {"research", "research_finding", "research_synthesis"}:
        if not str(meta.get("research_reason", "")).strip() or not str(meta.get("context", meta.get("research_context", ""))).strip(): return []
        if str(meta.get("research_freshness", "current")).lower() in {"stale", "expired"}: return []
    body=str(record["body"]).replace("\r\n", "\n").replace("\r", "\n")
    if body.startswith("---\n"):
        parts=body.split("\n---\n", 1)
        body=parts[1] if len(parts)==2 else ""
    rows=[]; seen=set()
    for ordinal,(heading,section) in enumerate(_body_sections(body)):
        text="\n".join(item for item in [str(meta.get("semantic_title", "")), str(meta.get("summary", "")), heading, section] if item).strip()
        claim_hash=hashlib.sha256(text.encode()).hexdigest()
        if not text or claim_hash in seen: continue
        seen.add(claim_hash)
        rows.append({"chunk_id": f"{meta['memory_id']}:{ordinal}:{claim_hash[:12]}", "embedding_text": text,
          "metadata": {"memory_id":meta["memory_id"],"source_hash":record["source_hash"],"document_version":meta.get("document_version"),"freshness":meta.get("source_freshness",meta.get("freshness","current")),"tombstone":bool(meta.get("tombstone",False)),"edges":meta.get("edges",[]),"claim_hash":claim_hash}})
    return rows
