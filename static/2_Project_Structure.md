# Projektstruktur – TreeEditor
Ordner sortiert nach Nutzung und Wichtigkeit.

## 1. Organisation

### "."

### "specs"
Projektspezifikation, ToDos und Arbeitshinweise. Dient auch als Vorlage für die spätere Projektzusammenfassung.
  
### "static"  
Temporäre Dateien zur automatisierten Generierung der Projektdoku. Keine Runtime-Funktion.

## 2. Quellcode

### "models"  
Datenmodelle: Klassen für Tree-Struktur, Nodes, Contents und Metadaten.

**Dateien:**
- {filepath: "models/content_model.py", purpose: "Content model with metadata and renderer"}
- {filepath: "models/metadata_model.py", purpose: "Metadata handling and (future) validation"}
- {filepath: "models/node_model.py", purpose: "Node model with metadata and content"}
- {filepath: "models/tree_data.py", purpose: "Tree structure with undo support"}

### "ui"
GUI-Struktur für das Hauptfenster mit Bereichen wie TreeView, RightPanel, Node-Metadaten und Content-Panels.

**Dateien:**
- {filepath: "ui/content_panel_view.py", purpose: "Single content view with filter + editor"}
- {filepath: "ui/main_window.py", purpose: "GUI entry, sets up main layout and actions"}
- {filepath: "ui/node_editor_panel.py", purpose: "Main right panel (metadata + content stack)"}
- {filepath: "ui/tree_view.py", purpose: "Tree widget with search, edit, drag&drop"}

### "widgets"  
Modular aufgebaute, wiederverwendbare Widgets für Content-Editor, Metadaten-Anzeige etc.

**Dateien:**
- {filepath: "widgets/content_editor_base.py"}
- {filepath: "widgets/content_editor_factory.py"}
- {filepath: "widgets/content_editor_widget.py", purpose: "Editor for single content (title + text)"}
- {filepath: "widgets/content_list_widget.py", purpose: "Multi-content editor with add/delete"}
- {filepath: "widgets/content_metadata_panel.py"}
- {filepath: "widgets/content_panel_stack.py", purpose: "Manages multiple parallel content views"}
- {filepath: "widgets/metadata_widget.py", purpose: "(To be replaced by TreeView editor)"}
- {filepath: "widgets/node_metadata_panel.py"}
- {filepath: "widgets/single_content_panel.py"}

### "core"
Zentrale Hilfskomponenten wie "content_filter_parser", "paths_registry", "schemas_registry", "undo_manager".

**Dateien:**
- {filepath: "core/content_filter_parser.py", purpose: "Filter engine for AND/OR/NOT queries"}
- {filepath: "core/project_paths.py", purpose: "Path registry for key folders"}
- {filepath: "core/project_settings.py"}
- {filepath: "core/schema_registry.py", purpose: "JSON schema loader and cache"}
- {filepath: "core/undo_manager.py", purpose: "Simple undo/redo stack"}

### "utils"
(Derzeit leer) – reserviert für allgemeine Hilfsfunktionen.

## 3. Ressourcen

### "resources"  
Projektstartdaten wie z. B. Beispielbaum ("beispielbaum.json").
  
### "resources/icons"  
Toolbar-Icons (SVG).
  
### "schemas" 
JSON-Schemas zur Definition von Metadatenfeldern für Nodes und Contents.

**Dateien:**
- {filepath: "schemas/chapter_meta.json", purpose: "JSON schema for node metadata"}
- {filepath: "schemas/content_schema.json", purpose: "JSON schema for content metadata"}