# Refactor Log (Feature-Based Struktur)

## Phase 0 — Baseline

### 0.1 Entry Point & Run Command
- Entry Point: `main.py::main`
- Reproduzierbarer Startbefehl (lokal):
  - `/bin/python3 main.py`
- Headless-Smoke (für CI/ohne Display):
  - `QT_QPA_PLATFORM=offscreen /bin/python3 - <<'PY' ... MainWindow ... PY`

### 0.2 Smoke-Test hinzugefügt
- Datei: `tests/test_smoke_import.py`
- Inhalt:
  - Import-Smoke für `main`.
  - Minimaler Modell-Roundtrip (`TreeDataModel` load/save/load).

### 0.3 Baseline-Checks
- `pytest -q` -> **2 passed**
- Headless MainWindow smoke -> **SMOKE_MAINWINDOW_OK**

---

## Phase 1 — Skeleton & Facades
- Status: abgeschlossen
- Erstellt:
  - `app/`
  - `app/shell/`
  - `app/features/{document,tree_nav,inspector,settings}/`
  - `app/shared/`
- Facades ergänzt über jeweilige `__init__.py`.
- Dokumentation ergänzt: `docs/ARCHITECTURE_BOXES.md`.
- Checks:
  - `pytest -q` -> **2 passed**
  - Headless Startup (old/new shell) -> **SMOKE_OLD_ENTRY_OK**, **SMOKE_NEW_SHELL_OK**

## Phase 2 — Moves mit Shims
- Status: abgeschlossen (inkrementell, shim-basiert)
- 2.1 Document:
  - Neue kanonische Module unter `app/features/document/`:
    - `tree_data.py`, `node_model.py`, `content_model.py`, `metadata_model.py`, `undo_manager.py`, `schema_registry.py`
  - Kompatibilitäts-Shims gesetzt:
    - `models/tree_data.py`, `models/node_model.py`, `models/content_model.py`, `models/metadata_model.py`
    - `core/undo_manager.py`, `core/schema_registry.py`
  - Qt-freiheit in `app/features/document/` eingehalten.
- 2.2–2.4 feature-canonical Module ergänzt:
  - `app/features/tree_nav/{tree_area.py,tree_view.py}`
  - `app/features/inspector/{node_editor_panel.py,content_panel_stack.py,single_content_panel.py}`
  - `app/features/settings/{project_settings.py,user_settings.py}`
- 2.5 Shell Wiring ergänzt:
  - `app/shell/wiring.py::create_main_window`
  - `app/main.py` nutzt zentrale Wiring-Erzeugung.
- Checks:
  - `pytest -q` -> **2 passed**
  - Headless Startup -> **SMOKE_AFTER_DOC_MOVE_OK**, **SMOKE_APP_MAIN_OK**

## Phase 3 — Boundary Enforcement
- Status: abgeschlossen
- Implementiert: `tools/check_import_boundaries.py`
- Ergebnis:
  - `/bin/python3 tools/check_import_boundaries.py` -> **OK: Keine verbotenen Cross-Feature-Imports gefunden.**

## Phase 4 — Finalisierung
- Status: abgeschlossen
- Legacy Entry stabil auf neue Struktur geroutet:
  - `main.py` delegiert auf `app.main::main`.
- Smoke-Flow ergänzt:
  - `tools/smoke_ui_flow.py` (create/select/edit/save/reopen)
  - Ergebnis: **SMOKE_UI_FLOW_OK**
- Doku ergänzt:
  - `docs/README.md` um Run-/Test-/Boundary-/Smoke-Befehle.

### Shim-Entscheidung
- Temporäre Kompatibilitäts-Shims bleiben vorerst aktiv (sicherheitsorientiert), da die Legacy-Importpfade im UI-Code noch breit genutzt werden.
- Diese Shims sind bewusst explizit markiert und können in einem separaten Cleanup-Schritt entfernt werden, sobald alle internen Imports vollständig auf `app/features/*` umgestellt sind.

## Phase 5 — Restore-Recheck (2026-03-01)
- Status: abgeschlossen
- Anlass:
  - Nach Regression-Fix wurde der reguläre und der erweiterte Restore-Flow erneut validiert.
- Ergebnis:
  - `QT_QPA_PLATFORM=offscreen /bin/python3 tools/smoke_restore_core_actions.py` -> **SMOKE_RESTORE_CORE_ACTIONS_OK**
  - `QT_QPA_PLATFORM=offscreen /bin/python3 tools/smoke_ui_flow.py` -> **SMOKE_UI_FLOW_OK**
  - `pytest -q` -> **5 passed**
- Dokumentation synchronisiert:
  - `docs/REGRESSION_CHECKLIST.md`
  - `docs/RESTORATION_NOTES.md`
