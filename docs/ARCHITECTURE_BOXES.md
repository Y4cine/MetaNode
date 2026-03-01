# Architektur-Boxen (Feature-basierte Zielstruktur)

## Ziel
Klare Kapselung in vier Boxen plus Shell und Shared, mit minimierter Kopplung und nachvollziehbaren Importregeln.

## Boxen

### 1) `app/shell/`
**Rolle**
- Kompositionswurzel der Anwendung.
- Verdrahtet Features (Signal/Slot bzw. Command-Orchestrierung).

**Darf importieren**
- Facades aus `app/features/*`
- `app/shared/*`

**Referenzen**
- `app/shell/__init__.py`
- `app/shell/main_window.py`
- `app/shell/wiring.py`

### 2) `app/features/document/`
**Rolle**
- SSOT für Dokumentzustand: Modell, Persistenz, Undo, Dirty-State.
- Muss Qt-frei bleiben.

**Derzeit exponiert (Phase 1 Facade)**
- `TreeDataModel`, `TreeNodeWrapper` (`models/tree_data.py`)
- `Node`, `Content`, `Metadata` (`models/*.py`)
- `UndoManager` (`core/undo_manager.py`)
- `SchemaRegistry` (`core/schema_registry.py`)

**Referenzen**
- `app/features/document/__init__.py`

### 3) `app/features/tree_nav/`
**Rolle**
- Tree-Navigation (Widgets, Selection, DnD, Context-Menü).

**Derzeit exponiert (Phase 1 Facade)**
- `TreeArea` (`ui/tree_area.py`)
- `NodeTree` (`ui/tree_view.py`)

**Referenzen**
- `app/features/tree_nav/__init__.py`

### 4) `app/features/inspector/`
**Rolle**
- Rechtes Panel: Node-Editor, Content-Panels, Metadaten + Editoren.

**Derzeit exponiert (Phase 1 Facade)**
- `NodeEditorPanel` (`ui/node_editor_panel.py`)
- `ContentPanelStack` (`widgets/content_panel_stack.py`)
- `SingleContentPanel` (`widgets/single_content_panel.py`)

**Referenzen**
- `app/features/inspector/__init__.py`

### 5) `app/features/settings/`
**Rolle**
- User-/Projektsettings lesen/schreiben und Layout-Wiederherstellung.

**Derzeit exponiert (Phase 1 Facade)**
- In-Document settings: `core/project_settings.py`
- User settings: `utils/user_settings.py`

**Referenzen**
- `app/features/settings/__init__.py`

### 6) `app/shared/`
**Rolle**
- Kleine, feature-neutrale Hilfsfunktionen.

**Derzeit exponiert (Phase 1 Facade)**
- `calculate_ratios` (`utils/ratios.py`)

**Referenzen**
- `app/shared/__init__.py`

## Erlaubte Abhängigkeiten (Ziel)
- `shell -> features facades`
- `features -> app/shared`
- optional `features -> features/document` (nur wenn nötig)

Nicht erlaubt:
- direkte Cross-Feature-Imports (z. B. `tree_nav -> inspector`, `inspector -> tree_nav`).

## Status
- Phase 1 abgeschlossen: Paket-Skeleton und Facades vorhanden.
- Phase 2+ verschiebt Implementierungen schrittweise und reduziert Legacy-Importpfade.
