# Veröffentlichung und Abnahme

Version 0.1.0-rc.1, Stand 1. Oktober 2026.

## Kanäle unterscheiden

Der Repository-Marktplatz verteilt den Community-Prerelease. Ein Git-Push ist
keine Aufnahme in ein offizielles Verzeichnis. Vor stabiler Freigabe sind echte
Claude-Code-/Codex-Installation und die Szenarien in `SKILL.md` erforderlich.
Pakettests ersetzen diese Abnahme nicht.

Für Claude: Plugin und Marktplatz mit `claude plugin validate --strict` prüfen,
installieren und Skill-Aufruf in neuer Session testen. Den aktuellen öffentlichen
Einreichungsweg über die Claude-Plugin-Dokumentation beziehungsweise das
Publisher-Portal prüfen. Die Aufnahme in `claude-plugins-official` liegt bei
Anthropic und folgt nicht automatisch aus einer Community-Veröffentlichung.

Für OpenAI: den aktuellen Einreichungsweg unter
https://developers.openai.com/plugins/deploy/submission verwenden. Skills-only
ist zulässig; keine erfundenen MCP-Endpunkte oder OAuth-Verbindungen hinzufügen.
Die Publisher-Identität muss verifiziert sein. Einreichung benötigt die passenden
Organisationsrechte und startet eine externe Prüfung. Nach Zustimmung entscheidet
der Publisher über die Veröffentlichung im gemeinsamen ChatGPT-/Codex-Verzeichnis.
Bedingungen und Policy-Attestierungen muss der Publisher selbst prüfen.

Die verfügbaren verbundenen Tools liefern hier keinen Publisher-Portalzugriff.
Offizielle Einreichung und Freigabe werden deshalb nicht behauptet.

## GitHub-Prerelease

Das eigene Tag `owledge-governance-v0.1.0-rc.1` ist vom Runtime-Release getrennt.
Der dedizierte Workflow kann nach seinen Linux-/Windows-Pakettests die beiden ZIPs
und Prüfsummen veröffentlichen. Nur ein Push auf `feat/owledge-governance-plugins`
mit dem Commit-Marker `[publish-governance]` aktiviert diesen Publish-Job.
Bestehende Releases werden nicht überschrieben. `VERSION` und PyPI bleiben unberührt.
Ein erfolgreicher Workflow ist am konkreten Commit zu prüfen, nicht vorauszusetzen.

## Offene Host-Abnahme

Pro Host Version, Betriebssystem, Installationsquelle/Commit, geladener Skill,
Scope, Rechte und Ergebnisse dokumentieren. Kontrollen als angewiesen, nativ
erzwungen oder nicht vorhanden kennzeichnen. Ohne sicheren Schreibweg muss der
Agent beim Entwurf bleiben. Für die OpenAI-Einreichung mindestens fünf positive
und drei negative nachvollziehbare Testfälle samt Fixture-Anforderungen vorbereiten.
Die vorhandenen Skill-Szenarien allein sind noch kein vollständiger Submission-Testbericht.

## Primärquellen

- https://agentskills.io/specification
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/deploy/submission
- https://code.claude.com/docs/en/plugin-marketplaces
- https://code.claude.com/docs/en/plugins-reference
- https://code.claude.com/docs/en/discover-plugins

Dies sind Dokumentationsquellen, keine Partner- oder Kompatibilitätszertifizierung.
