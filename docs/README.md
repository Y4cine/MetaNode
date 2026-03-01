# Architektur-Dokumentation: Nutzung und Pflege

## Inhalt
- `ARCHITECTURE.md` — schriftliche Reverse-Engineering-Zusammenfassung mit Traceability.
- `diagrams/01_high_level_architecture.md` — C4-ish Komponentenübersicht.
- `diagrams/02_module_dependencies.md` — Modul-/Paket-Abhängigkeiten.
- `diagrams/03_runtime_flows.md` — Startup, Laden, Edit/Save Sequenzdiagramme.
- `diagrams/04_signal_slot_overview.md` — Qt Signal/Slot Überblick.
- `diagrams/05_state_model.md` — Zustandsmodell (Mode + Dirty/Save).

## Mermaid rendern
Optionen:
1. VS Code mit Mermaid-Plugin (Markdown-Vorschau öffnen).
2. Mermaid CLI:
   - Install: `npm i -g @mermaid-js/mermaid-cli`
   - Export: `mmdc -i docs/diagrams/01_high_level_architecture.md -o out.svg`

Hinweis: Für `.md`-Dateien mit mehreren Diagrammen ggf. Diagrammblock in `.mmd` kopieren oder pro Datei einen Block rendern.

## Aktualisierungsprozess (empfohlen)
1. Bei Änderungen an `ui/main_window.py`, `ui/file_manager.py`, `ui/node_editor_panel.py`, `widgets/single_content_panel.py`, `models/tree_data.py` zuerst Runtime-Flows prüfen.
2. Bei neuen Importbeziehungen `02_module_dependencies.md` aktualisieren.
3. Bei neuen Signals/Slots `04_signal_slot_overview.md` aktualisieren.
4. Bei neuen Modi/Statusübergängen `05_state_model.md` aktualisieren.
5. In `ARCHITECTURE.md` jede neue zentrale Aussage mit Datei + Symbol referenzieren.

## Traceability-Regeln
- Jede wesentliche Architekturbehauptung muss mindestens eine konkrete Referenz enthalten (Datei + Symbol).
- Bei Unsicherheit als Unsicherheit markieren und Verifikationsweg dokumentieren.
