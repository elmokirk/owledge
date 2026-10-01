# Prüfstand 0.1.0-rc.1

Am 1. Oktober 2026 lokal unter Linux mit Python 3.13.5 und Node.js v22.16.0 geprüft.

**29 Tests entdeckt: 27 bestanden, 2 bewusst übersprungen.** Die übersprungenen
Prüfungen benötigen Claude Code beziehungsweise Codex. Beide CLIs sind in dieser
Testumgebung nicht installiert. Die nativen Validator-/Discovery-Tests werden
nur ausgeführt, wenn das jeweilige Programm vorhanden ist.

Geprüft wurden Paketpfade, eindeutige JSON-Schlüssel, Versionskonsistenz, die acht
Regel-IDs, ausgeschlossene Runtime-/Secret-Dateien, standardmäßig inaktive Hooks,
reproduzierbare Archive und Prüfsummen. Der optionale Hinweis-Hook wurde mit
normaler, ungültiger, zu großer und manipulativ verlinkter Eingabe ausgeführt.
Testdateien blieben unverändert; Geheimnisse aus Testeingaben wurden nicht ausgegeben.

Dies sind eigene Paket- und Script-Tests, keine vollständige Prüfung durch die
Plugin-Hosts und keine Modell-Evals. Keine GBrain-/OpenKnowledge-Instanz und kein
Kundendatenbestand wurde verbunden. Die Skill-Szenarien sind offene Host-Abnahme.
Der vollständige Legacy-Runtime-Preflight wurde nicht ausgeführt.

Reproduktion aus einem Checkout:

```sh
python -B -m unittest discover -s tests/governance_plugin -p 'test_*.py' -v
```

Der dedizierte GitHub-Workflow prüft dieses separate Paket auf Linux und Windows.
Sein Ergebnis muss am konkreten Commit nachgesehen werden. Dieser Bericht behauptet
keinen erfolgreichen CI-Lauf und keine offizielle Directory-Freigabe.
