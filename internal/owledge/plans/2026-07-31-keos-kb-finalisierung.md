---
title: "KEOS Knowledge Base v2.3 — Finaler Umsetzungsplan"
description: "Production-Plan: rag-wiki (80% fertig) + Nextcloud-Syncer-Add-on + BGE-M3 + Reranking + Frontmatter-Strip-Parser + PII-Schutz + KEOS-Konzept-Integration. Ausführbar von nativem Coding-Agent auf Windows."
type: implementation-plan
status: draft-v2.3-final
version: "2.3.1"
created: 2026-07-31
updated: 2026-07-31
author: hermes-ops (kirk-ops personality)
scope: "C:\\Users\\Kirk\\Documents\\KEOS_KB\\ + rag-wiki + Nextcloud"
universality: "🟢"
hardening: "3-Subagent-Review integriert: Red Team + Blindspot + Senior Engineer. 4 blocking fixes (B1-B4), 16 non-blocking fixes (NB1-NB16). Plan-Freeze: keine v2.4."
related:
  - "external KEOS vault: kb-plan-v2.2"
  - "external KEOS vault: KEOS-Finalisierungsplan-v2"
  - "external KEOS vault: KEOS-Strategieplan-v1"
  - "external KEOS vault: KEOS-Agent-Primitive"
  - "external KEOS vault: rag-wiki-Stack-Gap-Briefing"
  - "external KEOS vault: PolyGraphVault-Syncer"
  - "external KEOS vault: Frontmatter-Pollution-Learning-K25"
external_reference_scope: "Historical references point to the separate KEOS vault and are not Owledge repository links."
concept_tags: [knowledge-base, rag, graphrag, rag-wiki, nextcloud, frontmatter-parser, keos-integration]
stack_tags: [rag-wiki, lightrag, neo4j, qdrant, tei, bge-m3, nextcloud, ollama, docker, mcp]
confidence: 0.9
edges:
  - type: "derived_from"
    target: "external KEOS vault: kb-plan-v2.2"
    weight: 1.0
  - type: "relates_to"
    target: "external KEOS vault: KEOS-Finalisierungsplan-v2"
    weight: 0.95
  - type: "relates_to"
    target: "external KEOS vault: KEOS-Agent-Primitive"
    weight: 0.9
  - type: "relates_to"
    target: "external KEOS vault: rag-wiki-Stack-Gap-Briefing"
    weight: 0.85
---

# KEOS Knowledge Base v2.3 — Finaler Umsetzungsplan

> **WICHTIG:** Dieser Plan ist für einen **nativen Coding-Agent auf Windows** (Claude Code / Codex / OpenCode). Die Hermes-Docker-Instanz bleibt im Planning-Modus. Der Coding-Agent baut auf Windows auf.

> **Basis:** rag-wiki (M1 Knowledge Hub, 80% fertig) + Nextcloud-Syncer-Add-on. KEOS-Konzepte (23 → 9 Primitive) als Spezifikation, rag-wiki + Owledge als Umsetzung.

> **Leitlinie aus KEOS Strategieplan v1:** *"Der Engpass war nie Wissen. Er war, dass jede Regel als Text existiert und keine als Software."* — Plan v2.3 macht die KEOS-Regeln zu Software.

---

## 1 · Architektur-Entscheidung: Variante C

### Gewählt: rag-wiki + Nextcloud-Syncer-Add-on

```
┌──────────────────────────────────────────────────────────────┐
│  Nextcloud (SoT für Roh-Material — alle Dateitypen)            │
│  Ordner = Bereichs-Workspace = Isolierter Graph               │
│  10-business/, 20-branding/, 50-research/ etc.                │
│  Clients: Windows Desktop, Mobile, WebDAV                    │
└─────────────────┬────────────────────────────────────────────┘
                  │ (WebDAV-Sync, continuous reconciliation)
       ┌──────────▼──────────┐
       │  Nextcloud-Syncer   │  (NEU zu bauen, ~2000 Zeilen)
       │  - Folder→Workspace Mapping
       │  - WebDAV-Poll + Delta-Erkennung
       │  - File-Lifecycle-Reconciliation
       │  - Audit-Trail (sync_events)
       │  - Delete-Grace-Period
       │  - Frontmatter-Strip-Parser (Pre-Ingest)
       └──────────┬──────────┘
                  │ (HTTP an rag-wiki Gateway)
       ┌──────────▼──────────┐
       │  rag-wiki Gateway   │  (VORHANDEN, 80% fertig)
       │  - JWT-Auth + RBAC  │
       │  - Rate-Limiting    │
       │  - 4 Agent-API-Keys │
       │  - AI-Act-Audit     │
       │  - Smart-Routing    │
       │  - EINZIGER Schreiber│
       └──────────┬──────────┘
                  │
       ┌──────────▼──────────┐
       │  rag-wiki Core      │  (VORHANDEN)
       │  + LightRAG v1.5.4  │
       │  + 3 Workspaces     │
       │  + Qdrant (Vector)  │
       │  + Neo4j (Graph)    │
       │  + TEI (BGE-M3)     │
       │  + RAGAnything      │
       │  + MinerU (OCR)     │
       │  + Reranker (bge)   │
       └──────────┬──────────┘
                  │
    ┌─────────────┼─────────────────────┐
    │             │                      │
┌───▼────┐  ┌─────▼──────┐  ┌────────────▼────┐
│Auto-   │  │ Query API  │  │ MCP-Server      │
│Ingest  │  │ mode: mix  │  │ 15 Tools (stdio)│
│(sync   │  │ + reranker │  │ VORHANDEN       │
│→gw→lr) │  └─────┬──────┘  └────────────────┘
└────────┘        │
         ┌────────▼────────┐
         │  Agents          │
         │  Hermes (Docker) │
         │  Codex (native)  │
         │  Claude Code     │
         │  OpenCode        │
         │  pi.dev (future) │
         └─────────────────┘
```

### Warum Variante C (Kirks Entscheidung)

| Grund | Erklärung |
|-------|-----------|
| **rag-wiki ist 80% fertig** | M1 Knowledge Hub, eigenes Repo, jede Zeile bekannt |
| **MCP-Server vorhanden** | 15 Tools, stdio — kein Neubau (spart 8-12h) |
| **Gateway/RBAC vorhanden** | JWT-Auth, 4 Agent-Keys, Rate-Limiting (spart 4-8h) |
| **Reranker nur Config-Flip** | `ENABLE_RERANK: true` + TEI-Endpoint (spart Zeit) |
| **Dogfooding M1/M2** | rag-wiki = M1 Knowledge Hub = M2-Backend. Selber nutzen = Produkt härtten |
| **Nextcloud-Syncer leichtgewichtig** | Gegen rag-wiki-Gateway-API schreiben, nicht PolyGraphRAG-REST adaptieren |
| **Mehraufwand minimal** | ~30-40h vs 41-51h (Variante A) oder 37-45h (Variante B) |
| **KEOS-L2-Anforderung erfüllt** | Gateway als einziger Schreiber — rag-wiki hat das schon |

### Was aus PolyGraphVault übernommen wird (Inspiration, nicht Abhängigkeit)

| Konzept | Übernahme | Wie |
|---------|-----------|-----|
| Folder→Graph Mapping | ja | Nextcloud-Ordner → rag-wiki Workspace-ID |
| WebDAV-Poll + Delta | ja | `source_hash` Vergleich, nur geänderte Dateien re-embedden |
| Continuous Reconciliation | ja | Poll-Loop alle 60s, async Ingest via Gateway |
| Delete-Grace-Period | ja | 24h Grace vor Graph-Node-Löschung |
| sync_events Audit-Trail | ja | JSONL-Log in rag-wiki's AI-Act-Audit-Vault |
| Frontmatter-Strip-Parser | ja | Als Pre-Ingest-Hook im Syncer |

---

## 2 · KEOS-Konzept-Integration (N1-N10)

### Alle 10 Lücken aus dem KEOS-Abgleich, integriert

| # | KEOS-Konzept | Integration in v2.3 | Phase |
|---|--------------|---------------------|-------|
| **N1** | Gateway als einziger Schreiber (KEOS L2) | rag-wiki Gateway = einziger Schreiber. Agents bekommen nie Dateipfade, nur MCP-Tools. | Phase 1 (vorhanden) |
| **N2** | Boot-Kontext-Budget <2.000 Token (KEOS B04) | AGENTS.md <3KB, DESIGN.md aus Boot entfernen, über `kb_search` erreichbar | Phase 3 |
| **N3** | 60%-Mess-Kriterium für Semantik (KEOS T65) | BM25 über Frontmatter zuerst. PolyGraphRAG/Semantik nur wenn <60% Trefferquote | Phase 4 (Eval) |
| **N4** | Agent-Registry (KEOS P5a) | `15-agents/_REGISTRY.md` mit Rolle/Modell/Schreibrecht pro Agent. rag-wiki hat schon 4 Agent-Keys. | Phase 3 |
| **N5** | Projekt-Registry (KEOS P5c) | `60-projects/_REGISTRY.md` mit F1-F3 + Fundus-Struktur | Phase 3 |
| **N6** | Konzept-Ernte / K003 (KEOS P5d) | `concepts/main/` (K001-K023) übernehmen. `conceptctl.py` (996 Zeilen) integrieren. Vor jedem Neuentwurf: Konzept-Suche. | Phase 3 |
| **N7** | KEOS-Tools integrieren | `keos-lint.py` (79 Zeilen) als Pre-Commit-Hook. `keos-check.py` als Pre-Write-Hook. `conceptctl.py` für Konzept-Suche. | Phase 2-3 |
| **N8** | ADR als `doc_type` (Kirks Schema-Vorschlag) | Neu in Frontmatter-Contract v2.3. Template mit project/decisions/architecture/security/learnings/evidence. | Phase 3 |
| **N9** | Stop-Loss-Datum (KEOS Strategieplan) | Hardes Datum: KB-Skelett + Pilot bis 15.08., Vollmigration bis 31.08. | Phasen-Plan |
| **N10** | rag-wiki als Basis | Variante C — rag-wiki + Syncer-Add-on | gesamte Architektur |

### KEOS Agent-Primitive → rag-wiki-Features Mapping

| KEOS-Primitive | rag-wiki-Feature | Status |
|---------------|-----------------|--------|
| AP-1 Write-Gate (Schema-Validierung, ablehnen nicht reparieren) | rag-wiki Gateway + `keos-lint.py` als Pre-Write-Gate | ✅ Gateway da, Lint integrieren |
| AP-2 Hash-Vergleich statt Single-Writer-Prosa | `source_hash` in Frontmatter, Syncer vergleicht | ✅ neu im Syncer |
| AP-3 Strukturiertes Ereignis statt ERR-Datei | rag-wiki AI-Act-Audit-Vault (JSONL) | ✅ vorhanden |
| AP-4 Statische Operationsliste + Warteschlange | `[CONFIRM]`-Gates + Quality-Gate (draft→active) | ✅ neu |
| AP-5 Such-Vertrag (Metadaten vs semantisch) | MCP `kb_search` mit `modus: auto/metadaten/semantisch` | ✅ MCP da, Router erweitern |
| AP-6 Inkrement-Gate (inhaltlich) | Quality-Gate: Score >70 oder [CONFIRM] für Promotion | ✅ neu |
| AP-7 Context-Pack (Owledge) | Abstract + LinkMap als Router in Frontmatter | ✅ neu im Contract |

---

## 3 · Frontmatter-Strip-Parser (Kritische Komponente)

### Identisch zu v2.2, integriert in Syncer

```
Nextcloud-Ordner → Syncer erkennt neue/geänderte Datei
  │
  ├─ 1. frontmatter_strip_parser.py
  │     → Parse Frontmatter (YAML → metadata Dict)
  │     → Strip Frontmatter from Body
  │     → Clean Body (Wikilinks, HTML-Kommentare, Versions-Footer)
  │     → source_hash (SHA-256 des clean_body)
  │     → should_embed() check (PII, archived → skip)
  │
  ├─ 2. Upload zu rag-wiki Gateway
  │     → POST /v1/pipeline/upload/{workspace}
  │     → content: clean_body (Frontmatter-frei)
  │     → metadata: als Filter-Schicht (nicht embedded)
  │     → source_hash: für Delta-Reindex
  │
  └─ 3. rag-wiki Gateway → LightRAG
        → BGE-M3 Embedding (nur clean_body)
        → Entity-Extraction (nur clean_body)
        → Qdrant: Vector | Neo4j: Graph | Audit: JSONL
```

### Parser-Code

Identisch zu v2.2 Abschnitt 2 (`tools/frontmatter_strip_parser.py`). Der Coding-Agent implementiert:
- `parse_md_file()` — Frontmatter/Body-Trennung
- `clean_md_body()` — Wikilink-Reduktion, HTML-Kommentar-Entfernung, Versions-Footer-Strip
- `metadata_to_filter_dict()` — Frontmatter → Filter-Schicht
- `should_embed()` — PII/Archived-Skip
- `process_for_polygraphrag()` → `process_for_ragwiki()` — Hauptfunktion

### Eval-Vergleich (Phase 4)

1. **Baseline:** 10 Notizen MIT Frontmatter → Recall@k messen
2. **Stripped:** dieselben 10 OHNE Frontmatter → Recall@k messen
3. **Erwartung:** +15-30% Recall@10 (Kirks K25: 27% Rauschen-Reduktion)

---

## 4 · Frontmatter-Contract v2.3

### Universelle Pflichtfelder

```yaml
---
memory_id: "mem:kirk:personal:keos-kb:<area>:<slug>"
doc_type: "canonical|research|moc|lesson|pattern|idea|session|handoff|daily|project_context|adr"
status: "draft|active|reviewed|promoted|superseded|archived"
visibility: "private|shared|tenant"
data_class: "public|internal|confidential|personal|special-category"
semantic_title: "Klarer, suchbarer Titel"
summary: "Abstract — Kernbotschaft in 2-3 Sätzen (max 500 Zeichen)"
concept_tags: ["business", "branding"]
stack_tags: ["nuxt", "ollama"]
confidence: 0.8
universality: "🟢|🟡|🔴"
version: "1.0"
created_at: "2026-07-31T10:00:00Z"
updated_at: "2026-07-31T10:00:00Z"
source_agent: "hermes|codex|claude-code|opencode|pi.dev|human"
source_hash: "sha256:..."
embedding_model: "bge-m3|mistral-embed|text-embedding-3-large"
embedding_status: "pending|embedded|stale|error"
metadata_separated: true
nextcloud_path: "/10-business/01-canonical/note.md"
workspace_id: "default"
edges:
  - type: "relates_to|similar_to|derived_from|shared_lesson_for"
    target: "[[path/to/note]]"
    weight: 0.8
---
```

### NEU: `doc_type: adr` (Architecture Decision Record)

Für alle Architektur-Entscheidungen. Body-Template:

```markdown
# ADR: <Entscheidungs-Titel>

## Project
- name: 
- problem: 
- target_users: 
- current_status: 

## Decision
- decision: 
- reason: 
- alternatives: 
- tradeoffs: 
- result: 

## Architecture
- components: 
- data_flow: 
- models: 
- storage: 
- integrations: 

## Security
- data_classification: 
- permissions: 
- risks: 
- mitigations: 

## Learnings
- assumption: 
- observation: 
- consequence: 

## Evidence
- sources: 
- metrics: 
- limitations: 
```

### ADR-Regeln

1. ADR-Pflicht bei jeder Architektur-Entscheidung
2. ADRs in `10-business/01-canonical/adr/` ablegen
3. Jedes ADR verlinkt auf `PLAN-v2.3` via `edges: relates_to`
4. ADRs sind versioniert (`version` + `updated_at`)
5. **K003-Regel:** Vor jedem Neuentwurf: `conceptctl.py list` + ADR-Suche. Wer ohne Scan neu entwirft, produziert die fünfte Fassung derselben Idee.

### Dateityp-spezifische Felder

| doc_type | Zusätzliche Pflichtfelder | Optional |
|----------|--------------------------|----------|
| `canonical` | `area`, `moc_parent` | `retention_class`, `review_cycle` |
| `research` | `area`, `source_url`, `research_date` | `methodology`, `sample_size` |
| `moc` | `area`, `child_notes[]` | `description_long` |
| `lesson` | `scope`, `evidence[]`, `supersedes` | `score`, `score_breakdown` |
| `session` | `project_id`, `session_id`, `agent_id`, `parent_session` | `delta_summary` |
| `idea` | `area`, `origin` | `priority`, `linked_concepts[]` |
| `daily` | `date` | `energy_level`, `top_3_tasks[]` |
| `project_context` | `project_id`, `phase` | `blockers[]`, `next_actions[]` |
| `adr` (NEU) | `area`, `decision_status` | `alternatives[]`, `tradeoffs` |

### Verbotene Felder
- `tags:` als Inline-Liste → `concept_tags` + `stack_tags`
- `description:` als langer Text → `summary:` (max 500 Zeichen)
- `related:` als einfache Liste → `edges:` mit Typ + Gewicht

---

## 5 · Vollständige Architektur

### Container-Stack (Docker-Compose auf Windows)

```
VORHANDEN (rag-wiki, 80% fertig):
  1. lightrag-research     (Port 9621, Workspace: research)
  2. lightrag-agent-memory (Port 9622, Workspace: agent-memory)
  3. lightrag-docs         (Port 9623, Workspace: docs)
  4. qdrant                (Port 6333, Vector-Store)
  5. neo4j                 (Port 7474/7687, Graph-Store)
  6. tei                   (Port 80, BGE-M3 Embeddings, GPU)
  7. reranker              (Port 80, bge-reranker-v2-m3, GPU)  ← aktivieren
  8. gateway               (Port 8080, JWT-Auth + RBAC + MCP)
  9. caddy                 (Port 80/443, Reverse Proxy + TLS)
  10. prometheus           (Metrics)
  11. grafana              (Dashboards)

NEU (hinzuzufügen):
  12. nextcloud            (Port 8080→9090, SoT für Roh-Material)
  13. nextcloud-syncer     (Port 9624, WebDAV→Gateway Sync)  ← neu bauen
```

### Ressourcen-Bedarf (Laptop RTX 5070 8GB VRAM, 33GB RAM)

| Komponente | RAM | VRAM | Status |
|-----------|-----|------|--------|
| LightRAG ×3 | 1.5GB | 0 | idle |
| Qdrant | 512MB | 0 | idle |
| Neo4j | 1GB | 0 | idle |
| TEI (BGE-M3) | 512MB | 2GB | immer aktiv |
| Reranker (bge-reranker) | 256MB | 2GB | lazy (nur bei Query) |
| Gateway | 256MB | 0 | idle |
| Caddy | 64MB | 0 | idle |
| Prometheus + Grafana | 512MB | 0 | idle |
| **NEU: Nextcloud** | 512MB | 0 | idle |
| **NEU: Syncer** | 128MB | 0 | idle |
| **Total idle** | ~5.5GB | 2GB | OK (33GB RAM) |
| **Total bei Ingest** | ~6.5GB | 4GB | OK |
| **Total bei Query+Rerank** | ~6GB | 4GB | OK |

**VRAM 4 von 8GB.** RAM 5.5-6.5GB von 33GB. Beides im Budget. LLM-Query via API (Ollama qwen3.5:4b lokal oder Mistral/OpenAI).

### Workspace-Struktur (rag-wiki + Nextcloud)

```
rag-wiki Workspaces (vorhanden):
  - research     (Port 9621)  → 50-research/ Notizen
  - agent-memory (Port 9622)  → 60-projects/ Sessions + Learnings
  - docs         (Port 9623)  → 10-80/ kanonisches Wissen

NEU (Syncer mapped Nextcloud-Ordner → Workspace):
  Nextcloud/10-business/      → workspace: docs
  Nextcloud/20-branding/      → workspace: docs
  Nextcloud/30-design/        → workspace: docs
  Nextcloud/40-audiences/     → workspace: docs
  Nextcloud/50-research/      → workspace: research
  Nextcloud/60-projects/      → workspace: agent-memory
  Nextcloud/70-people/        → workspace: docs (PII-maskiert!)
  Nextcloud/80-tooling/       → workspace: docs
  Nextcloud/concepts/         → workspace: docs
  Nextcloud/global-memory/    → workspace: agent-memory (shared only)
```

### Datei-Fluss

```
1. Kirk droppt Datei in Nextcloud-Ordner
   → Nextcloud-Client synct zu Nextcloud-Server

2. Syncer pollt WebDAV alle 60s
   → Erkennt neue/geänderte Datei
   → frontmatter_strip_parser.py (Pre-Processing)
   → source_hash Vergleich (Delta-Reindex)
   → POST /v1/pipeline/upload/{workspace} an Gateway
   → Gateway: JWT-Auth + RBAC + Audit-Log
   → LightRAG: BGE-M3 Embedding (nur clean_body) + Entity-Extraction
   → Qdrant: Vector | Neo4j: Graph | Audit: JSONL

3. Query (Agent ruft MCP kb_search)
   → MCP-Server → Gateway → LightRAG query mode:mix
   → Frontmatter-Filter (aus metadata, nicht Embedding)
   → Graph-Traversal (Neo4j) + Vector-Similarity (Qdrant)
   → top-20 Kandidaten
   → bge-reranker-v2-m3 (Cross-Encoder)
   → top-5 reranked
   → Context-Assembly (Frontmatter + Abstract + Body bei Bedarf)
   → Audit-Log

4. Datei ändert sich
   → Syncer erkennt source_hash ≠
   → Re-Upload mit replace=true
   → alte Vektoren + Graph-Nodes gelöscht
   → neue Embedding + Entities
   → version bump in metadata
   → Archiv-Kopie in 90-archive/versioned/
```

---

## 6 · Phasen-Plan (für nativen Coding-Agent)

### Phase 0 — Voraussetzungen (diese Session, Hermes)
- [x] Plan v2.3 geschrieben
- [x] KEOS-Konzept-Abgleich durchgeführt (N1-N10 integriert)
- [x] rag-wiki vs PolyGraphVault Vergleich (Variante C gewählt)
- [x] ADR-Schema evaluiert und integriert
- [x] 3-Subagent-Hardening-Review (Red Team + Blindspot + Senior Engineer)
- [x] 4 blocking fixes + 16 non-blocking fixes integriert (v2.3.1)
- [x] Pain-Points-Datei angelegt
- [x] Coding-Agent Briefing extrahiert
- [x] **PLAN-FREEZE: v2.3.1 ist der letzte Plan. Keine v2.4. Nächster Schritt ist Code.**
- [ ] Kirk-Review + Freigabe v2.3.1
- [ ] Plan in Owledge-Repo ablegen

### Phase 0.5 — rag-wiki Smoke-Test (Coding-Agent, 2-4h) — **BLOCKING GATE**
> **Abbruch-Kriterium:** Wenn einer dieser Schritte fehlschlägt, muss der Coding-Agent zuerst den Code reparieren, bevor Phase 1 beginnt. Geschätzter Aufwand für Reparatur: 2-8h, nicht im Haupt-Plan enthalten.

- [ ] rag-wiki klonen: `gh repo clone elmokirk/rag-wiki C:\Users\Kirk\Documents\rag-wiki`
- [ ] `.env` aus `.env.example` erstellen
- [ ] `docker compose up -d` — alle 11 Container müssen starten ohne manuelle Fixes
- [ ] `GET http://localhost:8080/health` — muss 200 zurückgeben
- [ ] MCP-Server-Verbindung testen — `kb_search("test")` muss eine Antwort zurückgeben (auch leere)
- [ ] LightRAG-Version gegen aktuelle Release prüfen — Breaking Changes seit v1.5.4 identifizieren
- [ ] TEI: BGE-M3 Embedding-Test (kleiner Text → Vektor)
- [ ] Qdrant: Collection-Check
- [ ] Neo4j: Connection-Check
- [ ] **GATE:** Wenn alle Checks grün → Phase 1. Wenn nicht → Code reparieren (2-8h), dann nochmal.

### Phase 1 — rag-wiki + Nextcloud Docker-Stack (Coding-Agent, 5-8h)
- [ ] rag-wiki Repo klonen nach `C:\Users\Kirk\Documents\rag-wiki\` (falls nicht schon in Phase 0.5)
- [ ] `.env` aus `.env.example` erstellen (JWT, API-Keys, Neo4j, Qdrant)
- [ ] Reranker aktivieren: `ENABLE_RERANK: true`, `RERANK_BINDING: openai`, `RERANK_BINDING_HOST: http://tei:80/v1`
- [ ] **Port-Mapping fixen (B4):** Nextcloud `9090:80` (Host:Container), TEI intern 80, Reranker separater Port falls nötig, Gateway bleibt 8080
- [ ] Nextcloud-Service zur `docker-compose.yml` hinzufügen (Standard-Image, Port `9090:80`)
- [ ] `docker compose up -d` → alle Services starten
- [ ] Port-Belegung verifizieren: `netstat -an | findstr :8080` und `:9090` und `:6333` und `:7474`
- [ ] rag-wiki Gateway health check (`GET /health` auf Port 8080)
- [ ] Nextcloud initial setup (Admin-Account + Service-Account für Syncer)
- [ ] TEI: BGE-M3 pullen/verifizieren
- [ ] Reranker: bge-reranker-v2-m3 in TEI aktivieren
- [ ] **Backup-Script (B4):** `tools/backup_ragwiki.sh` — Qdrant snapshot + Neo4j dump → Nextcloud-Backup-Ordner (weekly cron)
- [ ] Workspace-Struktur in Nextcloud anlegen (10-business/ bis 80-tooling/ + concepts/ + global-memory/)
- [ ] rag-wiki MCP-Server testen (`.mcp.json` in Claude Code/Codex konfigurieren)
- [ ] **VRAM-Check (NB3):** BGE-M3 (2GB) + Reranker (2GB lazy) + LLM Entity-Extraction → Ingest+Query nicht parallel bei lokalem LLM. LLM via API wenn möglich.

### Phase 2a — Frontmatter-Strip-Parser (Coding-Agent, 6-8h)
> **Vor Parser-Bau: Frontmatter-Varianten-Audit (NB6)** — 100 zufällige KEOS-Dateien samplen, welche Frontmatter-Strukturen existieren?

- [ ] `tools/frontmatter_strip_parser.py` implementieren (siehe Plan Abschnitt 3)
- [ ] Edge-Case-Tests: leeres Frontmatter, Frontmatter ohne Body, Body ohne Frontmatter, `---` im Code-Block, Unicode/Emoji-Tags (🟢), verschachtelte YAML, TOML/JSON-Frontmatter
- [ ] `metadata_to_filter_dict()` als **Schema-Mapping** (alt → v2.3), nicht nur Parse
- [ ] **Zwei-Hash-System (B3):** `content_hash` (SHA-256 clean_body → Re-Embed) + `metadata_hash` (SHA-256 Frontmatter → Re-Index Filter, kein Re-Embed)
- [ ] Test: 10 Probe-Notizen → Parser → Verifikation
- [ ] **Fehler-Quote als Abbruch-Kriterium:** Wenn >5% der 100-Sample-Dateien nicht korrekt geparsed → Parser überarbeiten
- [ ] Verifikation: Vektoren enthalten KEIN Frontmatter (Spot-Check via Qdrant-Query)
- [ ] Verifikation: Neo4j-Graph-Entities aus Inhalt, nicht aus Tags

### Phase 2b — Syncer-Kern (Coding-Agent, 10-15h)
> **Syncer ist der kritische Pfad. 20-30h total (2a+2b+2c), nicht 8-12h.**

- [ ] `tools/nextcloud_syncer.py` implementieren:
  - WebDAV-Poll alle 60s (oder 15s mit Backoff)
  - Folder→Workspace Mapping (Config-Datei `syncer_config.yaml`)
  - Delta-Erkennung: `content_hash` + `metadata_hash` Vergleich
  - Upload: `POST http://localhost:8080/v1/pipeline/upload/{workspace}` an Gateway
  - `should_embed()` PII-Check vor Upload
  - **SQLite-Queue (B3):** `queue.db` mit `id, file_path, workspace, content_hash, status, retries, error_msg, created_at, processed_at`. Max 50 `processing` gleichzeitig. Retry: 3x exponential backoff. Dead-Letter bei 3 Fehlschlägen.
  - **Idempotenz (B3):** `sync_state.json` mit `{file_path, content_hash, gateway_doc_id, synced_at}`. Beim Restart: nur Dateien mit `content_hash ≠` oder `gateway_doc_id = null` re-syncen.
  - **Gateway-Fehler-Response-Schema (NB10):** `{ "error": "frontmatter_validation_failed", "violations": [...], "suggested_fix": "..." }`
- [ ] Syncer als Docker-Service oder Python-Script mit auto-restart
- [ ] Test: 10 Probe-Notizen → Nextcloud → Syncer → rag-wiki Ingest
- [ ] Query-Test: MCP `kb_search` mode:mix + Reranking → top-5

### Phase 2c — Syncer-Hardening (Coding-Agent, 4-6h)
- [ ] **Delete-Grace-Period (NB2):** 24h bevor Graph-Node **und Edges** gelöscht werden (Neo4j Cypher: Match + Edges + Delete)
- [ ] **PII-Masker (NB1):** Regex-Vorphase + Ollama qwen2.5:7b → vor jeglicher Migration
- [ ] sync_events Audit-Log (JSONL an rag-wiki AI-Act-Audit-Vault)
- [ ] `keos-lint.py` (aus KEOS) als Pre-Write-Gate im Gateway (Prüfung gegen v2.3-Schema, nicht altes Schema — NB7)
- [ ] Error-Paths: Dead-Letter-Queue, Retry-Logic bei Gateway-Ausfall (B3)

### Phase 3 — KB-Skelett + Core-Files + Registries (Coding-Agent, 2-3h)
- [ ] Ordnerstruktur in `C:\Users\Kirk\Documents\KEOS_KB\` anlegen (lokaler Git-Mirror)
- [ ] `AGENTS.md` (<3 KB, <2.000 Token, schlank, nicht-deterministisch)
- [ ] `OWLEDGE.md` (Projekt-Router, Memory-Core-Locations)
- [ ] `USER_CONTEXT.md` (PII-Layer, Owledge-Schema)
- [ ] `SOUL.md` (aus KEOS kopiert, unverändert)
- [ ] `.gitignore` (Build-Artefakte, Postgres/Neo4j Data, .owledge/indexes cache)
- [ ] Frontmatter-Validator als Pre-Commit-Hook (`keos-lint.py` + Owledge-Schema)
- [ ] Single-Writer-Lock-Datei + Stale-Reaper (PID-basiert)
- [ ] **Agent-Registry** (N4): `15-agents/_REGISTRY.md` mit Rolle/Modell/Schreibrecht pro Agent
- [ ] **Projekt-Registry** (N5): `60-projects/_REGISTRY.md` mit F1-F3 + Fundus
- [ ] **Konzept-Layer** (N6): `concepts/main/` (K001-K023) aus KEOS kopieren, `conceptctl.py` integrieren
- [ ] **ADR-Template** (N8): `10-business/01-canonical/adr/` + erstes ADR ("Warum rag-wiki + Syncer?")
- [ ] Git init + commit + GitHub-Repo `KEOS_KB` (private)

### Phase 4 — Eval-Loop + 60%-Kriterium (Coding-Agent, 6-8h)
- [ ] Golden-Dataset erstellen (**150 Test-Queries** für statistische Signifikanz — NB5)
- [ ] `tools/eval_golden_dataset.py`:
  - Recall@5, Recall@10, MRR, nDCG@10, **Precision@5** (NB11)
  - **p50/p95 Latenz** (NB11)
  - **Difficulty-Tiers:** easy (metadata), medium (semantic), hard (cross-project) (NB11)
  - Vergleich: mode:mix vs hybrid vs local vs global
  - Vergleich: mit vs ohne Reranking
  - Vergleich: MIT vs OHNE Frontmatter-Strip
- [ ] **60%-Kriterium operationalisieren (NB5):** Recall@10 als Metrik. ≥60% der Queries haben ≥1 korrekten Treffer in Top-10.
- [ ] **BM25-Implementierung klären (NB5):** Qdrant sparse vectors (ab v1.7) ODER SQLite-FTS5 ODER Tantivy. Fallback: mode:hybrid mit hohem Keyword-Gewicht.
- [ ] BM25-Baseline (N3): Frontmatter-Only-Suche → Trefferquote messen
  - Wenn >60% → Semantik nicht sofort nötig, parken
  - Wenn <60% → LightRAG mode:mix aktivieren
- [ ] Eval-Report in `.owledge/reviews/`
- [ ] **Nightly Cron-Eval (NB11):** 10 zufällige Queries → Alert bei Recall-Drop >5%

### Phase 5 — Migrations-Pilot (Coding-Agent, 3-4h)
- [ ] `tools/migrate_keos.py` schreiben
- [ ] KEOS-Clone nach `C:\Users\Kirk\Documents\AI_AGENCY_SYSTEM\KEOS\` (read-only!)
- [ ] Pilot: 50-research (50 wertvollste Notizen aus KEOS)
- [ ] Frontmatter-Transformation (tags → concept_tags/stack_tags)
- [ ] Split bei >5KB (Heading-basiert)
- [ ] MOC-Generierung
- [ ] Upload zu Nextcloud → Syncer → rag-wiki Auto-Ingest
- [ ] Eval gegen golden-dataset (nach Pilot-Ingest)
- [ ] **Quality-Gate-Scoring-Rubrik (NB9, AP-6):** Frontmatter-Completeness (0-30) + Content-Uniqueness via BGE-M3 cosine (0-40) + Cross-Reference-Density/edges (0-30). Score >70 → auto-promote. 50-70 → [CONFIRM]. <50 → reject + feedback.
- [ ] Review mit Kirk

### Phase 6 — Vollmigration (Coding-Agent, bis 30.09.) — **Stop-Loss angepasst**
> **Migration-Scope reduziert (NB8):** 500-800 Kern-Notizen priorisieren, Rest archiviert als "legacy-available" ohne Ingest. Nicht alle 2717 Dateien migrieren.

- [ ] migrate_keos.py Batch-Lauf über Top-3-Bereiche (50-research, 10-business, 60-projects)
- [ ] Pro Bereich MOCs generieren
- [ ] concepts/ Layer übernehmen (K001-K023)
- [ ] Archiv-Kopien in 90-archive/legacy-migration/
- [ ] Dedup-Check + Quality-Audit
- [ ] rag-wiki Voll-Ingest via Nextcloud
- [ ] Eval-Loop gegen golden-dataset (nach Voll-Ingest)
- [ ] Rest (2717 - 800 = ~1900) als `status: archived` in `90-archive/legacy-available/` — ohne Ingest, bei Bedarf später

### Phase 7 — Automatisierung (Coding-Agent + Hermes, KW 33-34)
- [ ] Hermes-Cronjobs: 10:00 / 16:00 / 20:00 (Triage, Session-Scribe, Eval)
- [ ] **Hermes-Cron → Gateway Netzwerk (NB4):** HTTP-Transport (nicht stdio) — `host.docker.internal:8080` in Hermes-Docker konfiguriert. In Phase 7 bauen, nicht Phase 8.
- [ ] PII-Masker-Pipeline aktiv (bereits in Phase 2c)
- [ ] MCP `kb_search` um `modus: auto/metadaten/semantisch` erweitern (AP-5)
  - **auto-Modus (NB13):** Heuristik-Routing — Query <3 Tokens oder exakt Tag-Match → `metadaten`, sonst `semantisch`. Fallback `semantisch` bei Unsicherheit.
  - **metadaten-Modus:** BM25 über `concept_tags` + `stack_tags` + `semantic_title` + `doc_type`
  - **semantisch-Modus:** LightRAG mode:mix + Reranker (vorhanden)
- [ ] **Context-Pack-Generation (NB12):** Syncer-Post-Ingest-Hook — LLM (qwen2.5:4b) generiert Abstract + LinkMap-Vorschlag → Agent reviewt → bestätigt
- [ ] Query-Logging/Observability (AI-Act-Audit-Vault erweitern)
- [ ] Backpressure: Queue mit Max 50 pro Cron-Run, Priorisierung nach universality
- [ ] Git-Pre-Commit-Hook (Frontmatter-Validator + source_hash-Update + keos-lint)
- [ ] Boot-Diät (N2): AGENTS.md <2.000 Token (NB15: ≤800T AGENTS + ≤600T OWLEDGE + ≤600T USER_CONTEXT), DESIGN.md aus Boot → über kb_search
- [ ] **conceptctl.py Tests (NB7):** Mindestens 5 Integration-Tests: list, search, new, link, supersede

### Phase 8 — External Embedding + HTTP API (KW 34-35, optional)
- [ ] Externes Embedding (Mistral/OpenAI/Vertex via rag-wiki Smart-Routing)
- [ ] Re-Embedding (source_hash-basiert)
- [ ] Eval-Vergleich: BGE-M3 vs Mistral-Embed vs text-embedding-3-large
- [ ] MCP Streamable HTTP-Wrapper (für pi.dev + Websites)
- [ ] Auth: API-Key + Tailscale

### Phase 9 — Desktop-Sync (07.08.2026, separat)
- [ ] Tailscale Laptop ↔ Desktop
- [ ] Nextcloud-Client auf Desktop
- [ ] Ollama-Dedicated-Mode auf Desktop (BGE-M3 + Reranker + qwen2.5)
- [ ] VRAM final verifiziert (nvidia-smi)
- [ ] Optional: rag-wiki + Neo4j + Qdrant auf Desktop (mit mehr VRAM)

---

## 7 · Coding-Agent Briefing

### An den Coding-Agent (Claude Code / Codex / OpenCode auf Windows)

```
AUFGABE: Baue die KEOS_KB v2.3 auf Windows auf. Basis: rag-wiki (80% fertig) + Nextcloud-Syncer (neu).

KONTEXT:
- Du bist ein nativer Coding-Agent auf Windows (nicht in Docker).
- Du hast vollen Zugriff auf Dateisystem, Docker Desktop, Git, GitHub.
- Plan liegt unter: C:\Users\Kirk\Documents\KEOS_KB\docs\PLAN-v2.3.md
- rag-wiki Repo: C:\Users\Kirk\Documents\rag-wiki\ (klonen von elmokirk/rag-wiki)
- KEOS (alte KB): C:\Users\Kirk\Documents\AI_AGENCY_SYSTEM\KEOS\ (READ-ONLY!)
- GitHub: elmokirk/KEOS_KB (private, wird erstellt)

ARCHITEKTUR:
- rag-wiki (M1 Knowledge Hub, 80% fertig) als RAG-Backend
  - LightRAG + Qdrant + Neo4j + TEI (BGE-M3) + Reranker + Gateway/RBAC + MCP (15 Tools)
- Nextcloud als zentrales Ablagesystem (Folder-as-Ingestion-API)
- Nextcloud-Syncer (NEU zu bauen): WebDAV-Poll → Frontmatter-Strip → rag-wiki-Gateway
- MCP-Server (vorhanden): kb_search, kb_read, kb_write, kb_related, kb_similar, kb_ingest

HAUPTKOMPONENTEN:
1. rag-wiki docker-compose.yml + Nextcloud-Service hinzufügen
2. tools/frontmatter_strip_parser.py (KRITISCH — verhindert Vektor-Pollution)
3. tools/nextcloud_syncer.py (NEU — WebDAV→Gateway Sync, Delta via source_hash)
4. tools/reranker.py (aktiviere vorhandenen bge-reranker-v2-m3)
5. tools/eval_golden_dataset.py (Eval-Loop)
6. tools/migrate_keos.py (Migration von KEOS)
7. MCP-Server erweitern (modus: auto/metadaten/semantisch)
8. Agent-Registry + Projekt-Registry + Konzept-Layer + ADR-Template

REGELN:
- KEOS (alte KB) ist READ-ONLY. Niemals darin schreiben.
- Frontmatter wird VOR dem Embedding gestript. Niemals Frontmatter embedden.
- PII-Dateien (data_class: personal) werden nie embedded.
- source_hash für Delta-Reindex. Bei Hash-Änderung → re-embed.
- 5KB max für kanonische Notizen. Split bei >5KB (Heading-basiert).
- rag-wiki Gateway = einziger Schreiber (KEOS L2). Agents bekommen nie Dateipfade.
- Pre-Commit-Hook: keos-lint + Frontmatter-Validator MUSS vor jedem Commit laufen.
- Vor jedem Neuentwurf: conceptctl.py list + ADR-Suche (KEOS K003).
- Boot-Kontext <2.000 Token. AGENTS.md schlank, DESIGN.md über kb_search.

KEOS-KONZEPTE ALS SPEZIFIKATION (nicht neu erfinden):
- AP-1 Write-Gate: keos-lint.py als Pre-Write-Gate im Gateway
- AP-2 Hash-Vergleich: source_hash statt Single-Writer-Prosa
- AP-5 Such-Vertrag: kb_search mit modus auto/metadaten/semantisch
- AP-6 Quality-Gate: draft → active braucht Score >70
- K003 Konzept-Ernte: conceptctl.py vor jedem Neuentwurf
- K25 Frontmatter-Pollution: Strip vor Embedding

PHASEN:
Phase 1: rag-wiki + Nextcloud Docker-Stack (3-4h)
Phase 2: Frontmatter-Parser + Syncer (8-12h)
Phase 3: Skelett + Core-Files + Registries + Konzepte (2-3h)
Phase 4: Eval-Loop + 60%-Kriterium (3-4h)
Phase 5: Migrations-Pilot 50-research (3-4h)
Phase 6: Vollmigration (bis 31.08.)
Phase 7: Automatisierung (KW 33-34)
Phase 8: External Embedding + HTTP (optional)
Phase 9: Desktop-Sync (07.08., separat)

STOP-LOSS:
- 15.08.: KB-Skelett + Pilot stehen
- 31.08.: Vollmigration fertig oder dokumentierte Verschiebung
```

---

## 8 · Offene Entscheidungen (final)

| # | Frage | Status |
|---|-------|--------|
| E1-E15 | wie v2.1/v2.2 empfohlen | ✅ akzeptiert |
| E16 | Frontmatter-Strip-Parser | ✅ akzeptiert |
| E17 | Metadata als separate Filter-Schicht | ✅ akzeptiert |
| E18 | Plan für nativen Coding-Agent | ✅ akzeptiert |
| E19 (neu) | Variante C (rag-wiki + Syncer) | ✅ akzeptiert |
| E20 (neu) | ADR als doc_type | ✅ akzeptiert |
| E21 (neu) | KEOS-Konzepte (K001-K023, AP-1 bis AP-7) als Spezifikation | ✅ akzeptiert |
| E22 (neu) | rag-wiki Gateway als einziger Schreiber (KEOS L2) | ✅ akzeptiert |
| E23 (neu) | 60%-Kriterium: BM25 zuerst, Semantik nur bei <60% | ✅ akzeptiert |
| E24 (neu) | Boot-Kontext <2.000 Token (KEOS B04) | ✅ akzeptiert |
| E25 (neu) | Stop-Loss 31.08. für Vollmigration | ✅ akzeptiert |

---

## 9 · Risiken (final)

| # | Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|---|--------|-------------------|--------|------------|
| R1 | rag-wiki hat 5 Wochen kein Commit (seit 22.06.) | hoch | mittel | Coding-Agent frischt Code auf, Dogfooding treibt Updates |
| R2 | Syncer ist komplex (WebDAV + Delta + Grace + Audit) | mittel | hoch | PolyGraphVault-Syncer als Inspiration, leichtgewichtige Version gegen rag-wiki-Gateway |
| R3 | VRAM 8GB für BGE-M3 + Reranker + VLM | mittel | mittel | BGE-M3 2GB idle, Reranker 2GB lazy, VLM nur bei Multimodal-Ingest, LLM via API |
| R4 | Neo4j + Qdrant + LightRAG×3 = viel RAM | gering | gering | 33GB RAM, ~6GB idle — passt |
| R5 | Frontmatter-Strip-Parser fehlerhaft | gering | hoch | Test mit 10 Notizen, Spot-Check Vektoren, Eval-Vergleich |
| R6 | Migration produziert Chaos | mittel | hoch | Pilot 50 Notizen, manuelle Review |
| R7 | PII-Leak | gering | hoch | `should_embed()` checkt data_class. PII niemals in RAG. |
| R8 | Hermes-Cron erreicht rag-wiki Gateway nicht | mittel | mittel | Hermes via MCP (stdio) oder HTTP auf Gateway (Port 8080) |
| R9 | Externes Embedding-Wechsel | mittel | hoch | source_hash-basiertes Re-Embedding. Eval vor/nach. |
| R10 | 40k-Skalierung | hoch | mittel | Laptop bis 15k. Desktop-Server ab 2028. Multi-Tenant separater Track. |
| R11 | rag-wiki Neo4j/Qdrant vs PolyGraphVault Postgres/pgvector | gering | gering | Neo4j+Qdrant sind production-proven, mehr RAM aber 33GB vorhanden |
| R12 | Stop-Loss 31.08. verpasst | mittel | mittel | Pilot bis 15.08., bei Verpassen dokumentierte Verschiebung |

---

## 10 · Skalierungspfad (2-5 Jahre)

| Jahr | Notizen | Stack | Erweiterung |
|------|---------|-------|-------------|
| 2026 | ~3.000 | rag-wiki + Nextcloud + BGE-M3 + Reranking | Basis, lokal, M1-Dogfooding |
| 2027 | ~8.000 | + MCP-HTTP + Eval-Loop + Mission-Control | Multi-Agent, Observability |
| 2028 | ~15.000 | + Externes Embedding + Desktop-Server | Neo4j/Qdrant auf Desktop, LLM lokal |
| 2029 | ~25.000 | + VPS-Mirror + Multi-Workspace pro Bereich | Always-on, Remote |
| 2030 | ~40.000 | + Multi-Tenant (KMU) + Sharding + ACL | CEO OS Produkt (M1/M2) |

### Embedding-Skalierung
| Phase | Modell | Wo | Warum |
|-------|--------|-----|-------|
| 2026 | BGE-M3 | TEI lokal (GPU) | DSGVO, kostenlos, multilingual, 8192 Token |
| 2028 | Mistral-Embed / text-embedding-3-large | API via rag-wiki Smart-Routing | maximale Qualität |
| 2029+ | VertexAI / Custom | API | Enterprise-Grade, Multi-Tenant |

---

## 11 · Deliverables

1. rag-wiki als RAG-Backend (M1 Knowledge Hub, 80% fertig → 100% durch Dogfooding)
2. Nextcloud als zentrales Ablagesystem (alle Dateitypen, Folder-as-API)
3. Nextcloud-Syncer (WebDAV→Gateway, Delta-Reindex, Audit-Trail, Delete-Grace)
4. Frontmatter-Strip-Parser (verhindert Vektor-Pollution, Kirks K25)
5. BGE-M3 Embeddings + bge-reranker-v2-m3 Reranking
6. MCP-Server (15 Tools, stdio → HTTP in Phase 8) für alle Agents
7. Gateway als einziger Schreiber (KEOS L2, JWT-Auth, RBAC, 4 Agent-Keys)
8. PII-Schutz (5-Schicht + Hybrid-Masker + should_embed-Check)
9. Eval-Loop (Golden-Dataset + Recall@k + MRR + nDCG@10 + 60%-Kriterium)
10. Delta-Reindex (source_hash-basiert)
11. Migrations-Pipeline KEOS → KEOS_KB (via Nextcloud)
12. Frontmatter-Contract v2.3 (Owledge + KEOS + PII + Version + ADR)
13. Konzept-Layer (K001-K023) übernommen + conceptctl.py integriert
14. Agent-Registry + Projekt-Registry (KEOS P5a/P5c)
15. ADR-Template für Architektur-Entscheidungen
16. Git-History + GitHub-Backup
17. Single-Writer-Disziplin (Gateway) + Working-Layer (Codex/Claude/OpenCode)
18. Query-Logging/Observability (AI-Act-Audit-Vault)
19. Boot-Kontext <2.000 Token (KEOS B04)
20. Stop-Loss 31.08. für Vollmigration
