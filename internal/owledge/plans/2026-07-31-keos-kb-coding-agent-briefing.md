# Coding-Agent Briefing — KEOS_KB v2.3

> **Kopiere diesen Text vollständig in Claude Code / Codex / OpenCode auf Windows.**

---

## AUFGABE

Baue die KEOS_KB v2.3 auf Windows auf. Basis: rag-wiki (80% fertig, M1 Knowledge Hub) + Nextcloud-Syncer (neu zu bauen).

## KONTEXT

- Du bist ein nativer Coding-Agent auf Windows (nicht in Docker).
- Du hast vollen Zugriff auf Dateisystem, Docker Desktop, Git, GitHub.
- Plan liegt unter: `C:\Users\Kirk\Documents\KEOS_KB\docs\PLAN-v2.3.md`
- rag-wiki Repo: `C:\Users\Kirk\Documents\rag-wiki\` (klonen von `elmokirk/rag-wiki`, private)
- KEOS (alte KB): `C:\Users\Kirk\Documents\AI_AGENCY_SYSTEM\KEOS\` (**READ-ONLY! Niemals darin schreiben!**)
- GitHub: `elmokirk/KEOS_KB` (private, wird erstellt)
- Pain-Points: `C:\Users\Kirk\Documents\KEOS_KB\10-business\_meta\pain-points-history.md`

## ARCHITEKTUR

- **rag-wiki** (M1 Knowledge Hub, 80% fertig) als RAG-Backend
  - LightRAG v1.5.4 + Qdrant (Vector) + Neo4j (Graph) + TEI (BGE-M3, GPU)
  - Gateway mit JWT-Auth + RBAC + Rate-Limiting + 4 Agent-API-Keys
  - MCP-Server (15 Tools, stdio)
  - RAGAnything + MinerU (Multimodal: PDF, Office, Audio, Bilder)
  - Reranker (bge-reranker-v2-m3, nur Config-Flip)
  - AI-Act-Audit-Vault
- **Nextcloud** als zentrales Ablagesystem (Folder-as-Ingestion-API)
- **Nextcloud-Syncer** (NEU zu bauen, ~2000 Zeilen):
  - WebDAV-Poll alle 60s
  - Folder → Workspace Mapping
  - Delta-Erkennung via `source_hash`
  - Frontmatter-Strip-Parser als Pre-Ingest-Hook
  - Delete-Grace-Period (24h)
  - sync_events Audit-Log
- **MCP-Server** (vorhanden, erweitern): `kb_search`, `kb_read`, `kb_write`, `kb_related`, `kb_similar`, `kb_ingest`

## HAUPTKOMPONENTEN

1. `docker-compose.yml`: rag-wiki + Nextcloud-Service hinzufügen
2. `tools/frontmatter_strip_parser.py` (**KRITISCH** — verhindert Vektor-Pollution)
3. `tools/nextcloud_syncer.py` (NEU — WebDAV→Gateway Sync, Delta via source_hash)
4. Reranker aktivieren (`ENABLE_RERANK: true` in `.env`)
5. `tools/eval_golden_dataset.py` (Eval-Loop: Recall@5, Recall@10, MRR, nDCG@10)
6. `tools/migrate_keos.py` (Migration von KEOS → Nextcloud)
7. MCP-Server erweitern (`modus: auto/metadaten/semantisch`)
8. Agent-Registry + Projekt-Registry + Konzept-Layer + ADR-Template

## REGELN (Non-Negotiables)

1. **KEOS (alte KB) ist READ-ONLY.** Niemals darin schreiben.
2. **Frontmatter wird VOR dem Embedding gestript.** Niemals Frontmatter embedden. (Kirks Learning K25)
3. **PII-Dateien** (`data_class: personal` oder `special-category`) werden **nie embedded**. `should_embed()` checkt das.
4. **`source_hash` für Delta-Reindex.** Bei Hash-Änderung → re-embed. Bei Gleichheit → skip.
5. **5KB max** für kanonische Notizen. Split bei >5KB (Heading-basiert). Raw-Layer darf länger sein.
6. **rag-wiki Gateway = einziger Schreiber** (KEOS L2). Agents bekommen nie Dateipfade, nur MCP-Tools.
7. **Pre-Commit-Hook:** `keos-lint.py` + Frontmatter-Validator MUSS vor jedem Commit laufen.
8. **Vor jedem Neuentwurf:** `conceptctl.py list` + ADR-Suche (KEOS K003). Wer ohne Scan neu entwirft, produziert die fünfte Fassung derselben Idee.
9. **Boot-Kontext <2.000 Token.** AGENTS.md schlank (<3KB), DESIGN.md über `kb_search` erreichbar, nicht im Boot.
10. **[CONFIRM] vor destruktiven Aktionen**, Mass-Updates >4, System-Config-Änderungen.
11. **Niemals löschen, nur archivieren.** Alte Versionen in `90-archive/`.

## KEOS-KONZEPTE ALS SPEZIFIKATION (nicht neu erfinden)

Die KEOS-Konzepte (23 → 9 Primitive) sind die Spezifikation. rag-wiki + Owledge sind die Umsetzung. Der Engpass war nie Wissen, sondern dass Regeln als Text existierten und nicht als Software. Du machst sie zu Software.

| KEOS-Primitive | Umsetzung in rag-wiki |
|---------------|----------------------|
| AP-1 Write-Gate | `keos-lint.py` als Pre-Write-Gate im Gateway. Ablehnen, nicht reparieren. |
| AP-2 Hash-Vergleich | `source_hash` in Frontmatter, Syncer vergleicht vor Re-Embed. |
| AP-3 Strukturiertes Ereignis | rag-wiki AI-Act-Audit-Vault (JSONL), nicht ERR-Datei. |
| AP-4 Statische Ops-Liste | `[CONFIRM]`-Gates + Quality-Gate (draft → active braucht Score >70). |
| AP-5 Such-Vertrag | MCP `kb_search` mit `modus: auto/metadaten/semantisch`. |
| AP-6 Inkrement-Gate | Quality-Gate: Score >70 oder [CONFIRM] für Promotion zu `active`. |
| AP-7 Context-Pack | Abstract + LinkMap als Router in Frontmatter. |

## PHASEN

### Phase 1: rag-wiki + Nextcloud Docker-Stack (3-4h)
- [ ] rag-wiki klonen: `gh repo clone elmokirk/rag-wiki C:\Users\Kirk\Documents\rag-wiki`
- [ ] `.env` aus `.env.example` erstellen (JWT, API-Keys, Neo4j, Qdrant)
- [ ] Reranker aktivieren: `ENABLE_RERANK=true`, `RERANK_BINDING=openai`, `RERANK_BINDING_HOST=http://tei:80/v1`
- [ ] Nextcloud-Service zur `docker-compose.yml` hinzufügen (Standard-Image, Port 9090)
- [ ] `docker compose up -d` → alle Services starten
- [ ] Gateway health check (`GET http://localhost:8080/health`)
- [ ] Nextcloud setup (Admin + Service-Account für Syncer)
- [ ] TEI: BGE-M3 verifizieren
- [ ] Reranker: bge-reranker-v2-m3 aktivieren
- [ ] Nextcloud-Ordnerstruktur anlegen: `10-business/`, `20-branding/`, `30-design/`, `40-audiences/`, `50-research/`, `60-projects/`, `70-people/`, `80-tooling/`, `concepts/`, `global-memory/`
- [ ] rag-wiki MCP in Claude Code/Codex konfigurieren (`.mcp.json`)

### Phase 2: Frontmatter-Parser + Syncer (8-12h)
- [ ] `tools/frontmatter_strip_parser.py` implementieren:
  - `parse_md_file()`: Frontmatter/Body-Trennung
  - `clean_md_body()`: Wikilinks reduzieren (`[[Note|Display]]` → `Display`), HTML-Kommentare entfernen, Versions-Footer strip
  - `metadata_to_filter_dict()`: Frontmatter → Filter-Schicht (nicht Embedding)
  - `should_embed()`: PII/Archived → skip
  - `process_for_ragwiki()`: Hauptfunktion, gibt `content` (clean) + `metadata` (Filter) + `source_hash` zurück
- [ ] `tools/nextcloud_syncer.py` implementieren:
  - WebDAV-Poll alle 60s
  - Folder→Workspace Mapping (Config-Datei `syncer_config.yaml`)
  - Delta-Erkennung: `source_hash` Vergleich mit gespeicherten Hashes
  - Upload: `POST http://localhost:8080/v1/pipeline/upload/{workspace}` an Gateway
  - Delete-Grace-Period: 24h bevor Graph-Node gelöscht wird
  - sync_events: JSONL-Log an rag-wiki AI-Act-Audit-Vault
  - `should_embed()` PII-Check vor Upload
- [ ] Syncer als Docker-Service oder Python-Script mit auto-restart
- [ ] Test: 10 Probe-Notizen → Nextcloud → Syncer → rag-wiki Ingest
- [ ] Verifikation: Vektoren enthalten KEIN Frontmatter (Spot-Check via Qdrant-Query)
- [ ] Verifikation: Neo4j-Graph-Entities aus Inhalt, nicht aus Tags
- [ ] Query-Test: MCP `kb_search` mode:mix + Reranking → top-5
- [ ] `keos-lint.py` (aus KEOS `system-health/tools/`) als Pre-Write-Gate im Gateway

### Phase 3: KB-Skelett + Core-Files + Registries (2-3h)
- [ ] Ordnerstruktur in `C:\Users\Kirk\Documents\KEOS_KB\` anlegen (lokaler Git-Mirror)
- [ ] `AGENTS.md` (<3 KB, <2.000 Token, schlank, nicht-deterministisch)
- [ ] `OWLEDGE.md` (Projekt-Router, Memory-Core-Locations)
- [ ] `USER_CONTEXT.md` (PII-Layer, Owledge-Schema)
- [ ] `SOUL.md` (aus KEOS kopiert, unverändert)
- [ ] `.gitignore` (Build-Artefakte, Neo4j/Qdrant Data, .owledge/indexes)
- [ ] Frontmatter-Validator als Pre-Commit-Hook (`keos-lint.py` + Owledge JSON-Schema)
- [ ] Single-Writer-Lock (`~/.kb-write.lock`, PID-basiert) + Stale-Reaper
- [ ] `15-agents/_REGISTRY.md` (Agent-Registry: Name, Rolle, Modell, Schreibrecht, I/O-Vertrag)
- [ ] `60-projects/_REGISTRY.md` (Projekt-Registry: F1 Providos, F2 KM2 RAG, F3 Website, Fundus)
- [ ] `concepts/main/` (K001-K023) aus KEOS kopieren, `conceptctl.py` integrieren
- [ ] `10-business/01-canonical/adr/` + erstes ADR: "Warum rag-wiki + Syncer (Variante C)?"
- [ ] `git init` + commit + `gh repo create elmokirk/KEOS_KB --private --source=.`
- [ ] Pain-Points-Datei kopieren nach `10-business/_meta/pain-points-history.md`

### Phase 4: Eval-Loop + 60%-Kriterium (3-4h)
- [ ] Golden-Dataset erstellen (20-50 Test-Queries aus KEOS-Notizen, mit erwarteten Treffern)
- [ ] `tools/eval_golden_dataset.py`:
  - Recall@5, Recall@10, MRR (Mean Reciprocal Rank), nDCG@10, Precision@5
  - Vergleich: mode:mix vs hybrid vs local vs global
  - Vergleich: mit vs ohne Reranking
  - Vergleich: MIT vs OHNE Frontmatter-Strip
- [ ] **BM25-Baseline zuerst** (KEOS T65 / N3): Frontmatter-Only-Suche → Trefferquote messen
  - Wenn >60% → Semantik nicht sofort nötig, parken
  - Wenn <60% → LightRAG mode:mix aktivieren
- [ ] Eval-Report in `.owledge/reviews/eval-2026-07-31.md`

### Phase 5: Migrations-Pilot (3-4h)
- [ ] `tools/migrate_keos.py`:
  - Liest KEOS-Clone (read-only)
  - Frontmatter-Transformation: `tags` → `concept_tags` + `stack_tags`, `related` → `edges`
  - Split bei >5KB (Heading-basiert) + MOC-Generierung
  - `source_hash` berechnen
  - Upload nach Nextcloud (Syncer übernimmt Ingest)
  - Archiv-Kopie in `90-archive/legacy-migration/`
- [ ] Pilot: 50 wertvollste Notizen aus `KEOS/KEOS-Work/20-areas/` oder `50-research/`
- [ ] Eval gegen golden-dataset (nach Pilot-Ingest)
- [ ] Quality-Gate (AP-6): `status: draft` → `active` braucht Score >70 oder [CONFIRM]
- [ ] Review mit Kirk

### Phase 6: Vollmigration (bis 31.08.)
- [ ] `migrate_keos.py` Batch-Lauf über alle Bereiche
- [ ] Pro Bereich MOCs generieren
- [ ] `concepts/` Layer (K001-K023) übernehmen
- [ ] Archiv-Kopien in `90-archive/legacy-migration/`
- [ ] Dedup-Check + Quality-Audit
- [ ] rag-wiki Voll-Ingest via Nextcloud
- [ ] Eval-Loop gegen golden-dataset (nach Voll-Ingest)
- [ ] **STOP-LOSS:** bis 31.08. Vollmigration fertig oder dokumentierte Verschiebung mit Begründung

### Phase 7: Automatisierung (KW 33-34, mit Hermes)
- [ ] Hermes-Cronjobs: 10:00 / 16:00 / 20:00 (Triage, Session-Scribe, Eval)
- [ ] PII-Masker-Pipeline aktiv (Regex + Ollama qwen2.5:7b)
- [ ] MCP `kb_search` um `modus: auto/metadaten/semantisch` erweitern (AP-5)
- [ ] Query-Logging (AI-Act-Audit-Vault erweitern)
- [ ] Backpressure: Queue mit Max 50 pro Cron-Run, Priorisierung nach `universality` (🟢 zuerst)
- [ ] Git-Pre-Commit-Hook (Frontmatter-Validator + source_hash-Update + keos-lint)
- [ ] Boot-Diät: AGENTS.md <2.000 Token, DESIGN.md aus Boot → über `kb_search`

## STOP-LOSS-DATEN (angepasst nach Hardening-Review)

| Bis | Kriterium | Realistisch? |
|-----|----------|-------------|
| **15.08.** | Phase 0.5 (Smoke-Test) + Phase 1 (Docker-Stack) + Phase 2a-c (Parser+Syncer) + Phase 3 (Skelett) | Ja, wenn Smoke-Test grün |
| **31.08.** | Phase 4 (Eval) + Phase 5 (Pilot 50 Notizen) | Ja |
| **30.09.** | Phase 6 (Vollmigration Top-3-Bereiche, 500-800 Notizen) | Angepasst (war 31.08.) |
| **KW 33-34** | Phase 7 (Automatisierung) | Nach Migration |

> **Plan-Freeze (NB16):** v2.3.1 ist der letzte Plan. Keine v2.4. Nächster Schritt ist Code, nicht Planung. (Blindspot BS-10: "Plan reproduziert PP-5-Muster — Strategie-Dokumentation statt Code")

## FRONTMATTER-CONTRACT v2.3 (Pflicht für alle neuen Dateien)

```yaml
---
memory_id: "mem:kirk:personal:keos-kb:<area>:<slug>"
doc_type: "canonical|research|moc|lesson|pattern|idea|session|handoff|daily|project_context|adr"
status: "draft|active|reviewed|promoted|superseded|archived"
visibility: "private|shared|tenant"
data_class: "public|internal|confidential|personal|special-category"
semantic_title: "Klarer, suchbarer Titel"
summary: "Abstract — max 500 Zeichen"
concept_tags: ["business"]
stack_tags: ["ollama"]
confidence: 0.8
universality: "🟢|🟡|🔴"
version: "1.0"
created_at: "2026-07-31T10:00:00Z"
updated_at: "2026-07-31T10:00:00Z"
source_agent: "hermes|codex|claude-code|opencode|pi.dev|human"
source_hash: "sha256:..."
embedding_model: "bge-m3"
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

## RAG-WIKI WORKSPACE MAPPING

```
Nextcloud-Ordner → rag-wiki Workspace:
  10-business/      → workspace: docs (Port 9623)
  20-branding/      → workspace: docs
  30-design/        → workspace: docs
  40-audiences/     → workspace: docs
  50-research/      → workspace: research (Port 9621)
  60-projects/      → workspace: agent-memory (Port 9622)
  70-people/        → workspace: docs (PII-maskiert!)
  80-tooling/       → workspace: docs
  concepts/         → workspace: docs
  global-memory/    → workspace: agent-memory (shared only, personal wird nicht embedded)
```

## WICHTIGE DATEIEN

- **Plan v2.3:** `C:\Users\Kirk\Documents\KEOS_KB\docs\PLAN-v2.3.md`
- **Pain-Points:** `C:\Users\Kirk\Documents\KEOS_KB\10-business\_meta\pain-points-history.md`
- **rag-wiki:** `C:\Users\Kirk\Documents\rag-wiki\` (README.md, SETUP-GUIDE.md, docker-compose.yml, .env.example)
- **KEOS (READ-ONLY):** `C:\Users\Kirk\Documents\AI_AGENCY_SYSTEM\KEOS\`
- **KEOS conceptctl.py:** `KEOS/concepts/tools/conceptctl.py` (996 Zeilen, für Konzept-Suche)
- **KEOS keos-lint.py:** `KEOS/KEOS-Work/system-health/tools/keos-lint.py` (79 Zeilen, als Pre-Write-Gate)

## BEI FRAGEN

Wenn etwas unklar ist oder eine Entscheidung gebraucht wird, die nicht im Plan steht:
1. Prüfe `conceptctl.py list` ob ein KEOS-Konzept dazu existiert
2. Prüfe ADR-Ordner ob eine Entscheidung schon getroffen wurde
3. Wenn nein: frag Kirk, mach keine Annahmen über Architektur-Entscheidungen