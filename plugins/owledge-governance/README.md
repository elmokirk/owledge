# Owledge Governance

**0.1.0-rc.1** ist ein eigenständiges Governance-Plugin für Claude Code und Codex.

Owledge ergänzt dein vorhandenes Second Brain um einen einheitlichen Ablauf:
Agents belegen Aussagen, trennen Vorschläge von freigegebenem Wissen und prüfen
den relevanten Stand vor Änderungen. Begrenztes Nichtfinden bleibt eine
Suchgrenze, keine behauptete Nichtexistenz.

Der Mehrwert ist ein portabler Arbeitsvertrag mit klaren Stop-Bedingungen.
Das Plugin ersetzt weder GBrain noch OpenKnowledge. OKF bleibt das Dateiformat.
Installation erteilt keine zusätzlichen Rechte und erzeugt keinen Wissensbestand.
Die Regeln stehen einmalig in `skills/governance/SKILL.md`.

## Installieren und ausprobieren

Diese Befehle verwenden den **Community-Marktplatz im Repository**. Es gibt noch
keine Freigabe in den offiziellen Verzeichnissen. Native Installationen sind
noch nicht durch die lokalen Pakettests bestätigt.

### Claude Code

```sh
claude plugin marketplace add 'elmokirk/owledge#feat/owledge-governance-plugins'
claude plugin install owledge-governance@owledge-labs
```

Eine neue Session starten und `/owledge-governance:governance` aufrufen.
Für einen lokalen Test aus dem Checkout dieses Branches:

```sh
claude plugin validate --strict ./plugins/owledge-governance
claude --plugin-dir ./plugins/owledge-governance
```

### Codex

```sh
codex plugin marketplace add elmokirk/owledge --ref feat/owledge-governance-plugins
codex plugin marketplace list
```

Danach die ChatGPT-Desktop-App neu starten und in Codex den Plugin-Browser öffnen.
Die lokale Quelle **Owledge Labs** auswählen und **Owledge Governance** installieren.
In einer neuen Session den Governance-Skill ausdrücklich auswählen. Verfügbarkeit
lokaler Marktplätze hängt von der Oberfläche ab. Die CLI-Befehle oben registrieren
zunächst die Quelle, nicht die offizielle Directory-Veröffentlichung.

Die Verpackung enthält das portable `plugin.json` und einen Codex-Kompatibilitäts-
Overlay unter `.codex-plugin/plugin.json`. Beide Hosts laden dieselbe Skill-Datei.
Für dieses Skills-only-Paket ist keine neue Service-Anmeldung nötig.

### Erste Aufgabe

```text
Wende Owledge Governance auf diese Knowledge Base an.
Prüfe zunächst nur die vorhandene Konfiguration: Host/Version, erlaubte Sources,
Entwurfsort, Freigabeweg und Versionsprüfung. Ändere keine Dateien oder Rechte.
Benenne fehlende Kontrollen und bleibe ohne sicheren Schreibweg beim Entwurf.
```

Automatische Skill-Auswahl ist keine zuverlässige Pflichtausführung. Für einen
verbindlichen Arbeitsablauf muss eine vertrauenswürdige Agent-Anweisung das Laden
vor Wissenssuche, Import, Änderungen und Handoffs verlangen. Ein Suchtreffer auf
die Skill-Datei aktiviert keine Regelautorität.

## Projektordner und Umfang

| Bereich | Standalone-Plugin | Begründung / Verantwortung |
| --- | --- | --- |
| Projektordner | Nutzt bestehende Roots und erlaubte Sources. Erzeugt keine `.owledge/`, `OWLEDGE.md` oder Global-Memory-Ordner. | Keine Migration oder zweite Projektwahrheit. |
| Regeln | Vollständiger Vertrag W01 bis W08 in einer Skill-Datei. | Die kleinste portable Einheit. |
| Pläne und Handoffs | Verlangt Belege, Status, Unsicherheit und nächsten Schritt in vorhandenen Artefakten. | Keine Task-Engine und keine Ordnergeneratoren. |
| Suche | Budget und sichtbare Suchgrenzen als Agent-Verhalten. | Index, Embeddings, Graph und Search-API liefert der Host. |
| Entwurf und Review | Vorschlag und nachvollziehbare Freigabe bleiben getrennt. | Keine eigene Review-Datenbank oder Approval-API. |
| Revision und Hash | Verlangt passende native Versionskontrolle; sonst Patch/Handoff. | Keine implementierten Transaktionen, Sperren oder atomaren Schreibprüfungen. |
| Rechte | Respektiert die eingerichtete Bindung und meldet fehlende Befugnisse. | Enforcement liegt bei Host, Credentials und Betriebssystem. |
| Quellen | Regelt Erhalt und Provenance. | Kein Importer und keine bytegenauen Source-Snapshots. |
| Receipts | Kurzer Abschluss in vorhandenen PRs, Notizen oder Aufgaben. | Kein automatischer Audit-Store und keine Telemetrie. |
| Hook | Optionaler SessionStart-Hinweis, standardmäßig deaktiviert. | Kein Tool-Blocker und keine Autorisierungsprüfung. |
| Backup/Recovery | Nicht implementiert. | Host-Backups bleiben nötig; Runtime-Recovery wird nicht übertragen. |
| Host-Integration | Semantische Zuordnung für GBrain, OpenKnowledge und OKF. | Keine mitgelieferten Connectoren oder zertifizierten Integrationen. |

## Optionaler Hinweis-Hook

Standardmäßig läuft **kein Script**. Nach Codeprüfung kann für einen lokalen Test
`hooks/hooks.example.json` nach `hooks/hooks.json` kopiert werden. Den lokalen
Plugin-Checkout neu laden; keine verwalteten Cache-Dateien verändern.
Node.js 18+ muss in der Host-Ausführungsumgebung verfügbar sein.

Der Hook liest nur die installierte Skill-Datei und liefert Pfad und SHA-256 als
Hinweis. Er liest keine Knowledge Base, nutzt kein Netzwerk und schreibt keine
Dateien. Ein Fehler verhindert den Hinweis, blockiert aber nicht die Session.
Codex-Hooks benötigen zusätzlich die ausdrückliche Vertrauensfreigabe des Nutzers.
Die Variable `CLAUDE_PLUGIN_ROOT` ist dort als Kompatibilitätsalias dokumentiert.
Der Hook ersetzt weder das Laden des Skills noch native Zugriffskontrollen.

## Testen und bauen

Aus dem Repository-Root mit Python 3.10+ und Node.js 18+:

```sh
python -B -m unittest discover -s tests/governance_plugin -p 'test_*.py' -v
python tools/build_governance_plugin.py --output /tmp/owledge-governance-artifacts
```

Unter Windows einen eigenen Ausgabeordner statt `/tmp/...` angeben. Der Builder
liefert ein Plugin-ZIP, ein Marketplace-ZIP und Prüfsummen. Eine feste Dateiliste
schließt Runtime, Projektwissen und Secrets aus. Vorhandene Artefakte werden nicht
überschrieben. Der Prüfstand steht in [VALIDATION.md](VALIDATION.md).

Strukturtests ersetzen keine Agent-Evals. Die Szenarien in `SKILL.md` zusätzlich
mit Testdaten im tatsächlichen Host durchführen. Das Plugin verbessert die
Arbeitsanweisung, garantiert aber weder faktische Richtigkeit noch Isolation.

## Entfernen und veröffentlichen

Das Plugin im jeweiligen Host deinstallieren. Wissensdateien bleiben erhalten.
Manuelle Verweise in `AGENTS.md` oder `CLAUDE.md` separat entfernen.

[Veröffentlichungsweg](PUBLISHING.md) · [Datenschutz](PRIVACY.md) · [MIT-Lizenz](LICENSE)
