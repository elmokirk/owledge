# Datenschutz und Datenfluss

Das Paket hat keinen eigenen Server, keine Telemetrie, keine Credentials und
keine MCP-Verbindung. Installation erweitert keine Host-Berechtigungen.
Der optionale Hook liest nur die installierte SKILL.md und gibt deren Pfad
und Hash an den Agent-Host weiter. Er liest keine Projektdateien.

Wenn der Agent den Skill anwendet, verwendet er die bereits verbundenen Tools.
Deren Datenverarbeitung und die Verarbeitung durch den Modellanbieter bleiben
bestehen. Dieses Plugin macht einen Cloud-Agent nicht offline oder lokal.
Protokolle sollen keine Geheimnisse oder nicht zugänglichen Ressourcennamen enthalten.

Deinstallation entfernt das Plugin, nicht bestehende Wissensdaten. Ein manuell
hinzugefuegter Verweis in AGENTS.md/CLAUDE.md muss separat entfernt werden.
