# Regression Checklist (Feature Restoration)

## A) Prüfschritte

- [x] App startet ohne Exception
  - `QT_QPA_PLATFORM=offscreen /bin/python3 - <<'PY'`
  - `from PyQt5.QtWidgets import QApplication`
  - `from PyQt5.QtCore import QTimer`
  - `from app.shell.wiring import create_main_window`
  - `app = QApplication([]); w = create_main_window(); w.show(); QTimer.singleShot(200, app.quit); app.exec_(); print("START_OK")`
  - `PY`

- [x] Node-Auswahl synchronisiert Inspector
- [x] Child-Node erstellen
- [x] Sibling-Node erstellen
- [x] Node umbenennen
- [x] Node löschen
- [x] Node bewegen
- [x] Content editieren
- [x] Speichern, neu laden, Inhalte verifizieren

## B) Reproduzierbarer Komplett-Check

Ein Kommando deckt die Kern-Regressionen ab:
- `QT_QPA_PLATFORM=offscreen /bin/python3 tools/smoke_restore_core_actions.py`

Erwartete Ausgabe:
- `SMOKE_RESTORE_CORE_ACTIONS_OK`

Zusätzlicher UI-Flow-Check:
- `QT_QPA_PLATFORM=offscreen /bin/python3 tools/smoke_ui_flow.py`

Erwartete Ausgabe:
- `SMOKE_UI_FLOW_OK`

Zusätzlicher Save-E2E-Check:
- `QT_QPA_PLATFORM=offscreen /bin/python3 tools/smoke_save_e2e.py`

Erwartete Ausgabe:
- `SMOKE_SAVE_E2E_OK`

## Diagnose: Action-Pfade „Node erstellen“

### Toolbar-Pfad
- Action-Quelle: `ui/toolbar_manager.py::ToolbarManager.setup_toolbar`
- Aufrufkette:
  - `tree_area.add_child_to(tree_area.currentItem())`
  - `tree_area.add_sibling_after(tree_area.currentItem())`
- Vorheriger Bruch:
  - `TreeArea` hatte diese Pass-through-Methoden nicht vollständig.

### Kontextmenü-Pfad
- Action-Quelle: `ui/tree_context_menu_mixin.py::open_context_menu`
- Aufrufkette:
  - `add_child_to(item)` / `add_sibling_after(item)`
- Wiederhergestellte Kette:
  - `tree_nav` emit -> `shell wiring` -> `DocumentStore.insert_*` -> `Tree refresh` -> `Selection` -> `Inspector`.

### Tastatur-Pfad
- Action-Quelle: `ui/tree_view.py::NodeTree.keyPressEvent`
  - `Insert` -> child
  - `Return` -> sibling
  - `Delete` -> delete
  - `F2` -> rename
- Wiederhergestellte Kette wie oben via Request-Signale.
