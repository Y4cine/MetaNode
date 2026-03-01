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
1. Bei Änderungen an `app/shell/ui/main_window.py`, `app/shell/ui/file_manager.py`, `app/shell/ui/node_editor_panel.py`, `app/features/inspector/widgets/single_content_panel.py`, `app/features/document/tree_data.py` zuerst Runtime-Flows prüfen.
2. Bei neuen Importbeziehungen `02_module_dependencies.md` aktualisieren.
3. Bei neuen Signals/Slots `04_signal_slot_overview.md` aktualisieren.
4. Bei neuen Modi/Statusübergängen `05_state_model.md` aktualisieren.
5. In `ARCHITECTURE.md` jede neue zentrale Aussage mit Datei + Symbol referenzieren.

## Traceability-Regeln
- Jede wesentliche Architekturbehauptung muss mindestens eine konkrete Referenz enthalten (Datei + Symbol).
- Bei Unsicherheit als Unsicherheit markieren und Verifikationsweg dokumentieren.

## Refactor-Checks ausführen
- Tests: `pytest -q`
- Import-Boundaries: `/bin/python3 tools/check_import_boundaries.py`
- Headless Startup-Smoke: `QT_QPA_PLATFORM=offscreen /bin/python3 - <<'PY'\nfrom PyQt5.QtWidgets import QApplication\nfrom PyQt5.QtCore import QTimer\nfrom app.shell.wiring import create_main_window\napp = QApplication([])\nwindow = create_main_window()\nwindow.show()\nQTimer.singleShot(200, app.quit)\napp.exec_()\nprint("SMOKE_APP_MAIN_OK")\nPY`
- Headless Edit/Save/Reopen-Smoke: `QT_QPA_PLATFORM=offscreen /bin/python3 tools/smoke_ui_flow.py`
