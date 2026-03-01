# MetaNode Architektur (Reverse Engineering)

Stand: 2026-03-01

## 1) Inventory (Repository-Karte)

### Top-Level
- `main.py` — App-Entry-Point, erzeugt `QApplication` und `MainWindow` (`main`).
- `core/` — Querschnittslogik: Filterparser, Undo, Schema-Laden, Pfad-/Projektsettings, Keyboard-Konfiguration.
- `models/` — Domänenobjekte und Baumdatenhaltung (`TreeDataModel`, `Node`, `Content`, `Metadata`).
- `ui/` — Hauptfenster, Orchestrierung, Tree-Interaktionen, Modus-/Menü-/Toolbar-/State-Manager.
- `widgets/` — zusammengesetzte UI-Bausteine (Node-/Content-Metadaten, Content-Editoren, Stack/Panel).
- `schemas/` — JSON-Schemas (`chapter_meta.json`, `content_schema.json`) für metadatengetriebene UI.
- `resources/` — Beispiel-JSON, Themes, Icons, Keyboard-Shortcuts.
- `utils/` — Hilfsfunktionen (User-Settings, Ratios, Filter-Helfer).
- `specs/`, `static/` — Spezifikationen und Hilfsskripte (nicht Teil des Runtime-Spines).

### UI-Konstruktion
- UI wird **code-first** gebaut; es gibt keine `.ui`-Designer-Dateien im Workspace.
- Hauptkomposition erfolgt in `ui/main_window.py::MainWindow.__init__` über `QWidget`, `QVBoxLayout`, `CustomSplitter`, `TreeArea`, `NodeEditorPanel`.

### Tests
- Keine dedizierten Testdateien gefunden (`tests/`, `test_*.py`, `*_test.py` leer).

## 2) Main Spine (minimaler Laufzeitkern)

Die minimale Spine, die für App-Start + Kerninteraktion nötig ist:
1. `main.py::main`
2. `ui/main_window.py::MainWindow`
3. `models/tree_data.py::TreeDataModel`
4. `core/schema_registry.py::SchemaRegistry`
5. `ui/tree_area.py::TreeArea` + `ui/tree_view.py::NodeTree`
6. `ui/node_editor_panel.py::NodeEditorPanel`
7. `widgets/content_panel_stack.py::ContentPanelStack`
8. `widgets/single_content_panel.py::SingleContentPanel`
9. `ui/file_manager.py::FileManager`

Diese Kette deckt Boot, Laden, Knotenselektion, Content-Editing und Speichern ab.

---

## 3) Schichten, Verantwortungen, Abhängigkeiten

## 3.1 UI-/Orchestrierungsschicht

### `ui/main_window.py::MainWindow`
**Verantwortung**
- Root-Composition des Fensters, Initialisierung von Model, Schemata und Subsystemen.
- Verdrahtung von Tree-Selektion auf Detailpanel.
- Initiales Laden letzter Datei aus User-Settings.

**Wichtige Methoden**
- `__init__` (UI-Aufbau, Manager-Initialisierung, optionales Autoload)
- `on_node_selected` (delegiert an `ui/node_selection_manager.py`)
- `_init_menus_and_toolbars`, `_setup_keyboard_navigation_shortcuts`
- `do_combined_undo` / `do_combined_redo` (delegiert an `ui/undo_manager_helper.py`)

**Kollaboration**
- `TreeDataModel`, `SchemaRegistry`, `TreeArea`, `NodeEditorPanel`, `FileManager`, `ModeManager`, `PanelStateManager`, `SplitterManager`.

### `ui/file_manager.py::FileManager`
**Verantwortung**
- Öffnen/Speichern/Neu, Recent Files, Dirty-Check vor Verlassen.
- Persistiert zusätzlich Layout-/Filter-Settings in `_settings`-Knoten.

**Wichtige Methoden**
- `open_file`, `save_file`, `save_file_as`, `open_recent_file`, `new_file`.

**Kollaboration**
- `TreeDataModel`, `Node`, `project_settings` (`get_settings`, `set_settings`, `restore_layout_from_settings`), `user_settings`.

### `ui/node_selection_manager.py::on_node_selected`
**Verantwortung**
- Mapping `node_id` -> `Node`-Objekt und Übergabe an aktiven rechten Bereich (`NodeEditorPanel`/`JsonEditor`).

### `ui/mode_manager.py::ModeManager`
**Verantwortung**
- Umschalten zwischen Normal-/Read-/JSON-Modus.

### `ui/panel_state_manager.py::PanelStateManager`
**Verantwortung**
- Sammeln/Wiederherstellen von Filter- und Splitterzuständen.

## 3.2 Domain-/Modellschicht

### `models/tree_data.py::TreeDataModel`, `TreeNodeWrapper`
**Verantwortung**
- Baumstruktur halten, suchen, verschieben, serialisieren, Undo-Snapshots verwalten.

**Wichtige Methoden**
- `load_from_dict`, `to_dict`, `load_from_file`, `save_to_file`
- `find_node`, `move_node`, `move_node_to_index`
- `push_undo_snapshot`, `undo`, `redo`

### `models/node_model.py::Node`
**Verantwortung**
- Typed View über Raw-Node-Dict (`metadata`, `contents`) mit `to_dict`/`from_dict`.

### `models/content_model.py::Content`
**Verantwortung**
- Content-Entity inkl. Renderer, Daten und Metadata.

### `models/metadata_model.py::Metadata`
**Verantwortung**
- Schlüssel/Wert-Metadaten + optionales Schemaobjekt; Validierung aktuell Platzhalter.

## 3.3 Widget-/Editor-Schicht

### `ui/node_editor_panel.py::NodeEditorPanel`
**Verantwortung**
- Kombiniert Node-Metadatenpanel und Content-Panel-Stack.
- Knoten laden/speichern/wechseln; lokales Undo für Editorzustand.

### `widgets/content_panel_stack.py::ContentPanelStack`
**Verantwortung**
- Verwalten mehrerer `SingleContentPanel` nebeneinander inkl. globaler Filterliste.
- Weiterreichen von Änderungsereignissen nach oben.

### `widgets/single_content_panel.py::SingleContentPanel`
**Verantwortung**
- Filterbare Content-Liste + Metadatenbaum + dynamischer Editor in einem Panel.
- Content CRUD, Copy/Cut/Paste, Rendererwechsel.

### `widgets/node_metadata_panel.py::NodeMetadataPanel`
**Verantwortung**
- Editierbare Darstellung von Node-Metadaten inkl. Kontextmenüaktionen.

### `widgets/content_metadata_panel.py::ContentMetadataPanel`
**Verantwortung**
- Darstellung/Änderung von Content-Metadaten pro gefiltertem Content.

### `widgets/content_editor_base.py::TextBlockEditor`
**Verantwortung**
- Standardeditor (Titel/Text/Renderer) + `content_edited`-Signal.

## 3.4 Core-/Service-Schicht

### `core/schema_registry.py::SchemaRegistry`
- Lädt/cacht Schemata aus `schemas/`.

### `core/project_settings.py`
- Speichert/liest in-tree Projektsettings (`_settings`) und stellt Layout wieder her.

### `core/undo_manager.py::UndoManager`
- Generischer Snapshot-Undo/Redo-Stack.

### `core/content_filter_parser.py::ContentFilterParser`
- Einfacher Ausdrucksparser für `key = "value"` mit `AND/OR/NOT`.

### `core/keyboard_manager.py::KeyboardNavigationManager`
- Lädt Shortcut-Konfiguration mit Fallback-Reihenfolge.

---

## 4) Wie die App bootet (Trace)

1. `main.py::main` erstellt `QApplication` und `MainWindow`.
2. `MainWindow.__init__` erstellt `TreeDataModel`, lädt Schemata über `SchemaRegistry.get`.
3. `MainWindow` baut Split-Layout (`TreeArea` links, `NodeEditorPanel` rechts).
4. `MainWindow` initialisiert Manager (`FileManager`, `ModeManager`, `PanelStateManager`, `SplitterManager`, Menü/Toolbar).
5. Über `utils.user_settings.get_setting("open_last")` wird optional letzte Datei geladen; sonst `FileManager.new_file`.
6. Bei Laden: `TreeDataModel.load_from_file` -> `TreeArea.load_model`; `project_settings.restore_layout_from_settings` stellt Panelzustände wieder her.

Evidenz: `main.py::main`, `ui/main_window.py::MainWindow.__init__`, `ui/file_manager.py::open_file/new_file`, `models/tree_data.py::load_from_file`, `core/project_settings.py::restore_layout_from_settings`.

## 5) Datenmodell & Persistenz

- Primärer Persistenzträger ist JSON-Datei des Baums (`TreeDataModel.save_to_file`, `load_from_file`).
- Projektbezogene UI-Zustände liegen im versteckten Baumknoten `id == "_settings"` (`core/project_settings.py`).
- User-spezifische globale Settings (Recent Files, Theme, open_last) liegen in `~/.config/MetaNode/user_settings.json` auf Linux (`utils/user_settings.py::get_user_settings_path`).
- Domänenobjekte `Node`/`Content`/`Metadata` sind dünne Adapter über dict-basierten Strukturen.

## 6) UI-Komposition

- Root: `MainWindow` mit horizontalem `CustomSplitter` (Tree vs rechter Bereich).
- Rechts: `NodeEditorPanel` mit vertikalem Splitter (Node-Metadaten oben, Content-Stack unten).
- Unten rechts: `ContentPanelStack` mit mehreren `SingleContentPanel` (horizontal).
- Einzelpanel: Toolbar + Filterzeile + vertikaler Splitter (`ContentMetadataPanel` / dynamischer Content-Editor).

Evidenz: `ui/main_window.py`, `ui/node_editor_panel.py`, `widgets/content_panel_stack.py`, `widgets/single_content_panel.py`, `ui/custom_splitter.py`.

## 7) Event-Flow (Signals/Slots, Commands)

- Tree-Selektion: `NodeTree.node_selected` -> `MainWindow.on_node_selected` -> `node_selection_manager.on_node_selected` -> `NodeEditorPanel.switch_node/load_node`.
- Content-Änderung: `TextBlockEditor.content_edited` -> `SingleContentPanel._write_back_current` -> `SingleContentPanel.content_edited` -> `ContentPanelStack._on_panel_content_edited` -> `MainWindow.on_content_edited`.
- Dateiaktionen: Menü/Toolbar -> `FileManager` (`open/save/new`), inkl. Recent-Menu-Trigger.
- Undo/Redo: Shortcut/Toolbar -> `MainWindow.do_combined_undo/redo` -> `undo_manager_helper` priorisiert Editor-Undo vor Tree-Undo.

## 8) Erweiterungspunkte

1. Neue Renderer/Editoren:
   - `widgets/content_editor_factory.py::create_content_editor`
   - neue Editor-Subklasse von `BaseContentEditor`.
2. Zusätzliche Metadatenfelder/Schemata:
   - `schemas/*.json`, geladen über `SchemaRegistry`.
3. Neue Tree-Aktionen:
   - `ui/tree_context_menu_mixin.py`, `ui/tree_dragdrop_mixin.py`, `ui/tree_clipboard_mixin.py`.
4. Neue Persistenz-/Projektzustände:
   - `core/project_settings.py` (in-file) und/oder `utils/user_settings.py` (global).

## 9) Bekannte Risiken / Technical Debt Hotspots (gerankt)

1. **UI und Persistenz eng gekoppelt (hoch)**
   - `FileManager` mutiert Modell, lädt Layout, baut `Node`-Objekte und steuert UI-Refresh in einer Methode (`open_file`).
2. **Dictionary-getriebene Struktur statt stabiler Typgrenzen (hoch)**
   - Mehrere Ebenen arbeiten direkt auf verschachtelten dicts (`TreeNodeWrapper.node`, `Node.to_dict/from_dict`).
3. **State-/Layout-Wiederherstellung ist fragil (mittel-hoch)**
   - Splittersuche über `findChild(type(...))`, key-basierte Heuristik in `restore_layout_from_settings`.
4. **Undo-Strategie doppelt und nicht transaktional (mittel)**
   - Tree-Undo und Editor-Undo nebeneinander mit Prioritätslogik; kein gemeinsames Command-Modell.
5. **Globaler JSON-Editiermodus kann Struktur brechen (mittel)**
   - `JsonEditorManager.show_json_view` erlaubt Full-Model-Manipulation; Warntext vorhanden, aber keine Schemahärtung.
6. **Uneinheitliche Architektur (mittel)**
   - Legacy-/Refactor-Artefakte parallel (`content_panel_view.py` vs neue Stack-Widgets, Delegationsmanager in MainWindow).
7. **Debug-Prints in Produktivpfaden (niedrig-mittel)**
   - `utils/user_settings.py`, `ui/file_manager.py`.

## 10) Unsicherheiten und Verifikation

- Unsicherheit: Einige Module wirken historisch/teilweise ungenutzt (`ui/content_panel_view.py`, diverse Mixins). 
  - Verifikation: Laufzeit-Importgraph erfassen (z. B. mit `modulefinder`/`pydeps`) und tatsächliche Pfade gegen statische Imports matchen.
- Unsicherheit: Shortcut-Overrides via `user_settings.py`-dynamischem Import können je nach Inhalt variieren.
  - Verifikation: `KeyboardNavigationManager._load_shortcuts` mit konkreter User-Settings-Datei testen.
