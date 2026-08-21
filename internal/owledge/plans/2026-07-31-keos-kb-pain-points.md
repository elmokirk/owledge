---
title: "KEOS Knowledge Base — Pain Points History"
description: "Kirks dokumentierte Schmerzpunkte aus 6 Monaten KEOS-Nutzung. Grundlage für KEOS_KB v2.3. Extrahiert aus Planning-Session 31.07.2026."
type: lesson
doc_type: lesson
status: active
visibility: shared
data_class: internal
semantic_title: "Pain Points: warum die aktuelle KB unbrauchbar wurde"
summary: "8 dokumentierte Schmerzpunkte aus 6 Monaten KEOS: fehlender zentraler Wissenszugriff, halbfertige Projekte, verloren Learnings, statische KB ohne Execution, Ideen-Logging schwierig, keine Mission-Control, Dateien zu lang, keine Parallelen-Erkennung."
concept_tags: [pain-points, keos, knowledge-base, migration]
stack_tags: []
confidence: 1.0
universality: "🟢"
version: "1.0"
created_at: "2026-07-31T14:00:00Z"
updated_at: "2026-07-31T14:00:00Z"
source_agent: human
source_hash: ""
area: business
scope: global
evidence:
  - "Planning-Session 31.07.2026, Kirks Bonus-Antwort"
  - "KEOS-Audit: 2717 .md, 525KB größte Datei, AGENTS.md 18KB"
supersedes: null
edges:
  - type: "relates_to"
    target: "external KEOS vault: PLAN-v2.3"
    weight: 1.0
  - type: "relates_to"
    target: "external KEOS vault: KEOS-Strategieplan-v1"
    weight: 0.8
external_reference_scope: "Historical KEOS strategy references live in the separate KEOS vault, not this repository."
---

# Pain Points History

> **Quelle:** Planning-Session 31.07.2026, Kirks Bonus-Antwort.
> **Zweck:** Zentrale Dokumentation der Schmerzpunkte, die zur KEOS_KB v2.3 geführt haben. Extrahierbar für andere Bereiche.

---

## PP-1 · Agents können nicht zentral auf Wissen zugreifen

**Schmerz:** Agents können nicht zentral auf Wissen zugreifen. Ich muss teilweise Sachen öfter erklären.

**Beweis:** KEOS hat 2717 .md-Dateien, aber kein semantisches Retrieval. Agents laden Dateien per explizitem Pfad, nicht per Such-Vertrag.

**Lösung in v2.3:** rag-wiki MCP-Server (15 Tools), `kb_search` mit `modus: auto/metadaten/semantisch` (KEOS AP-5). Gateway als einziger Schreibberechtigter (KEOS L2).

---

## PP-2 · Halbfertige Projekte durch fehlende zentrale Projekt-Registry

**Schmerz:** Durch fehlendes zentrales Wissen und keine zentrale Projekt-Anlage habe ich sehr oft ähnliche Projekte gebaut, die in dieselbe Richtung gehen, aber keins richtig fertiggestellt. Halbfertige Projekte finden keine reale Anwendung.

**Beweis:** KEOS Strategieplan v1: "19 DEV-Repos plus 3 aktive KEOS-Projekte, kein gemeinsames Register". M1-M3 Cluster zeigen Überschneidungen (rag-wiki in M1 und M2).

**Lösung in v2.3:** Projekt-Registry (`60-projects/_REGISTRY.md`, KEOS P5c) mit F1-F3 + Fundus. Konzept-Ernte (K003): `conceptctl.py list` vor jedem Neuentwurf. Parallelen-Erkennung via Graph-Traversal.

---

## PP-3 · Tokens und Zeit an ähnlichen Projekten verschwendet

**Schmerz:** Token und Zeit an ähnlichen Projekten geracet, weil Konzepte und Lösungsvorschläge nicht filterbar waren.

**Beweis:** KEOS hat dieselbe Idee in 5 Fassungen über TSOS, EAOS, KEOS, CEO-OS, Owledge (KEOS K003: "Wer ohne Scan neu entwirft, produziert die fünfte Fassung derselben Idee").

**Lösung in v2.3:** Konzept-Layer `concepts/main/` (K001-K023) zentral. `conceptctl.py` (996 Zeilen) als Pflicht-Check vor jedem Neuentwurf. ADR-Pflicht dokumentiert Entscheidungen.

---

## PP-4 · Learnings gehen in verschiedenen Harnesses unter

**Schmerz:** In verschiedenen Harnesses (Codex, Claude Code, OpenCode) gehen eine Menge Learnings unter. Das führt zu unnötiger Wiederholung, unnötigem Bugfixing und hält mich zurück.

**Beweis:** KEOS hat `15-agents/learnings/` aber nur 5 Dateien — Learnings werden nicht systematisch von allen Agents zurückgeschrieben.

**Lösung in v2.3:** Working-Layer für alle Agents: `60-projects/*/sessions/` + `global-memory/shared/lessons/`. Session-Scribe-Cron (Hermes) sammelt Learnings. Delta-Outputs werden kanonisch durch Triage. `keos_log` Tool für strukturierte Learning-Rückmeldung.

---

## PP-5 · Aktueller Vault kann nicht exekutieren

**Schmerz:** Aktueller Vault ist ein riesiges Sammelsurium an Produkten und Konzepten, aber er hilft nicht wirklich, Sachen zu exekutieren. Besonders der private Assistant funktioniert nicht, weil nur eine statische Wissensbasis vorhanden ist.

**Beweis:** KEOS Strategieplan: "Seit 22.06. ist kein einziger Codecommit an CEO OS entstanden. In diesen fünf Wochen sind ausschliesslich Strategie-, Gap-, Validierungs- und Reflexionsdokumente produziert worden." — Strategie-Dokumentation als Produktivitätsillusion.

**Lösung in v2.3:** Hermes-Cronjobs (10/16/20h) für autonome Triage. Stop-Loss 31.08. für Vollmigration. Plan v2.3 ist Umsetzungsplan, nicht Konzept-Plan. Coding-Agent Briefing für nativen Build auf Windows.

---

## PP-6 · Ideen-Logging (Sparks/Blitzideen) schwierig

**Schmerz:** Durch viele Ideen im Alltag muss ich rapid loggen können (Sparks, Blitzideen). Ticket Boards wie ClickUp und Jira funktionieren nicht gut für mich.

**Beweis:** KEOS hat `00-inbox/` mit 41+6 Dateien, aber kein Rapid-Log-Frontend. Sparks landen als unstrukturierte MD-Dateien, keine Bullet-Capture-Pipeline.

**Lösung in v2.3:** Nextcloud als Rapid-Log-Ziel (Mobile-Client, Windows-Client). `global-memory/personal/sparks/` als strukturierte Ablage. Hermes Triage-Cron (10:00) verarbeitet Sparks täglich. `doc_type: idea` im Frontmatter-Contract.

---

## PP-7 · Kein zentrales Mission-Control

**Schmerz:** Ich brauche ein zentrales Mission-Control, wo alle Tasks gefiltert sind, angegeben sind und ich mir einen Überblick raussuchen kann, inklusive Filterung zu verschiedenen Bereichen.

**Beweis:** KEOS hat 55 Tickets mit 11 verschiedenen Status-Werten, 3 gleichzeitig active Roadmaps, doppelt belegte Ticket-IDs (T14, T67). Kein Dashboard, keine Filterung.

**Lösung in v2.3:** Agent-Registry (`15-agents/_REGISTRY.md`) + Projekt-Registry (`60-projects/_REGISTRY.md`). MCP `kb_search` mit Frontmatter-Filter (area, status, universality). Später: Mission-Control-Frontend (Phase 7+).

---

## PP-8 · Dateien zu lang, Context Pollution

**Schmerz:** Dateien sind unglaublich lang und komplex. Teilweise am Ende der Dateien durch Cowork noch Checkpoints gemacht, weswegen sehr viele Inhalte untergehen.

**Beweis:** KEOS-Audit: größte Datei 525 KB, Top-10 alle über 40 KB. Frontmatter-Pollution-Learning K25: Tags, Related, Version rauschen Vektorraum. KEOS B04: Boot-Kontext ca. 779T + AGENTS.md.

**Lösung in v2.3:** 5KB max für kanonische Notizen, Split bei >5KB (Heading-basiert). Frontmatter-Strip-Parser vor Embedding (K25). Abstract max 500 Zeichen als Entscheidungskarte. LinkMap als Router. Boot-Kontext <2.000 Token (KEOS B04).

---

## Meta-Pain: Kontext-Verschmierung

**Schmerz:** Bereiche verschwimmen, Kontext-Bereiche sind nicht sauber getrennt. AGENTS.md zu deterministisch.

**Beweis:** KEOS-Audit: 8 Bereiche in `20-areas/` aber keine harte Trennung. AGENTS.md 18 KB — zu lang, zu starr.

**Lösung in v2.3:** Bereichs-Autonomie (jeder Bereich eigener 00-Raw/ + 01-canonical/ + 02-MOC/). Globaler Graph (LightRAG) für Cross-Bereichs-Cluster, Frontmatter-Filter für Bereichs-Isolation. AGENTS.md <3 KB, nicht-deterministisch.

---

## Verwendung dieser Datei

Diese Pain-Points sind:
1. **Beweis** dass KEOS_KB v2.3 nötig ist
2. **Akzeptanzkriterien** für die neue KB (jeder PP muss gelöst sein)
3. **Extrahierbar** für andere Bereiche (LinkedIn-Content, Sales-Pitches, Produkt-Positionierung)
4. **Referenz** für Eval-Loop (Golden-Dataset-Queries testen ob Pains gelöst sind)

## Erfolgskriterien

| Pain | Gelöst wenn | Messbar |
|------|------------|---------|
| PP-1 | `kb_search("X")` liefert Treffer in <2s in 3 Runtimes | Eval-Loop |
| PP-2 | Neue Projekt-Idee → Konzept-Suche findet Parallelen | conceptctl + Graph |
| PP-3 | Vor Neuentwurf: ADR-Suche zeigt existierende Entscheidung | ADR-Registry |
| PP-4 | Agent-Session endet → Learning in `shared/lessons/` | Session-Scribe-Cron |
| PP-5 | Hermes-Cron triages autonom, Kirk nur [CONFIRM] | Cron-Log |
| PP-6 | Spark via Nextcloud-Mobile → Triage-Cron sortiert | Triage-Log |
| PP-7 | `kb_search(area="business", status="active")` filtert | MCP-Test |
| PP-8 | Keine Datei >5KB in 01-canonical/ | Lint-Gate |
