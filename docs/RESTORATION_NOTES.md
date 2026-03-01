# Restoration Notes (Feature-based Refactor 2)

## Was war kaputt?

1. Node-Erstellung über Toolbar/indirekte Pfade war regressiv.
2. Shell-Wiring war Placeholder und koordinierte Features nicht.
3. Tree-Mutationen liefen direkt in `tree_nav` statt Request -> Shell -> Store.
4. Es fehlte ein expliziter, testbarer SSOT-API-Layer (`DocumentStore`).
5. Node-IDs wurden in mehreren Tree-Pfaden über eine falsche Data-Role gelesen (harte `32` statt `Qt.UserRole`), wodurch Requests mit `None`-IDs gesendet wurden.

## Warum ist es beim Refactor passiert?

- Die Struktur wurde auf Feature-Boxen umgestellt, aber zentrale Ablaufpfade blieben teilweise in Legacy-UI-Klassen.
- `app/shell/wiring.py` war als Placeholder belassen.
- `ui/tree_area.py` kapselte den Tree unvollständig (fehlende Pass-through Methoden).

## Was wurde geändert?

### 1) DocumentStore eingeführt
- Datei: `app/features/document/store.py`
- Symbol: `DocumentStore`
- APIs ergänzt:
  - `insert_child`, `insert_sibling_after`, `delete_node`, `move_node`, `rename_node`
  - `update_node_content`, `apply_patch`, `get_node`, `get_children`
  - plus Proxy-APIs: `to_dict`, `load_from_dict`, `load_from_file`, `save_to_file`, Undo/Dirty.

### 2) TreeNavigator auf Request-Pfade gebracht
- Dateien:
  - `ui/tree_view.py::NodeTree`
  - `ui/tree_context_menu_mixin.py`
  - `ui/tree_dragdrop_mixin.py`
  - `ui/tree_area.py::TreeArea`
- Neue Signale:
  - `request_insert_child(node_id, title)`
  - `request_insert_sibling_after(node_id, title)`
  - `request_delete(node_id)`
  - `request_rename(node_id, new_title)`
  - `request_move(node_id, new_parent_id, index)`
  - `selected(node_id)`
- Direkte Mutationen in Child/Sibling/Delete/Rename/Move-Pfaden entfernt.
- Data-Role-Handling stabilisiert:
  - Harte Role-Konstante entfernt, überall `Qt.UserRole` verwendet.
  - Betroffene Dateien: `ui/tree_context_menu_mixin.py`, `ui/tree_dragdrop_mixin.py`, `ui/tree_search_mixin.py`, `ui/tree_clipboard_mixin.py`.

### 3) Inspector Patch-Signal ergänzt
- Datei: `ui/node_editor_panel.py`
- Symbol: `NodeEditorPanel.request_apply_patch`
- Bei Content-Edit wird Patch emittiert:
  - `{title, metadata, contents}`

### 4) Shell-Wiring als Koordinator hergestellt
- Datei: `app/shell/wiring.py::wire_application`
- Verdrahtet:
  - Tree-Selection -> Inspector (`show_node_in_inspector`)
  - Tree-Requests -> `DocumentStore` Mutationen -> Tree-Refresh -> Selection
  - Inspector-Patches -> `DocumentStore.apply_patch` -> Tree-Refresh
- `main_window.model` wird auf `DocumentStore` gehoben, ohne UI-Neudesign.

### 5) Stabilität bei New File
- Datei: `ui/file_manager.py::FileManager.new_file`
- `DocumentStore`-Instanz bleibt erhalten (statt Überschreiben), damit Shell-Wiring intakt bleibt.

## Verifikation

- Unit Tests:
  - `pytest -q` -> grün
  - Neue Tests: `tests/test_document_store.py`

- Smokes:
  - Startup wired: `SMOKE_WIRED_START_OK`
  - Bestehender Flow: `SMOKE_UI_FLOW_OK`
  - Neuer Restore-Flow: `tools/smoke_restore_core_actions.py` erwartet `SMOKE_RESTORE_CORE_ACTIONS_OK`
  - Re-Check: `tools/smoke_ui_flow.py` erneut ausgeführt -> `SMOKE_UI_FLOW_OK`

## Grenzen / offene Punkte

- Clipboard-Cut/Paste in `tree_nav` nutzt weiterhin direkte Modellmutation (`ui/tree_clipboard_mixin.py`).
  - Für die angeforderten Kernregressionen (create/edit/save/load/selection sync) ist der Restore vollständig.
  - Optionaler nächster Schritt: Clipboard ebenfalls auf Request-Route umstellen.
