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
- {filepath: "models/content_model.py"}
- {filepath: "models/metadata_model.py"}
- {filepath: "models/node_model.py"}
- {filepath: "models/tree_data.py"}

### "ui"
GUI-Struktur für das Hauptfenster mit Bereichen wie TreeView, RightPanel, Node-Metadaten und Content-Panels.

**Dateien:**
- {filepath: "ui/content_panel_view.py"}
- {filepath: "ui/main_window.py", purpose: "Main module, called by main."}
- {filepath: "ui/node_editor_panel.py"}
- {filepath: "ui/tree_view.py"}

### "widgets"  
Modular aufgebaute, wiederverwendbare Widgets für Content-Editor, Metadaten-Anzeige etc.

**Dateien:**
- {filepath: "widgets/content_editor_widget.py"}
- {filepath: "widgets/content_list_widget.py"}
- {filepath: "widgets/content_panel_stack.py"}
- {filepath: "widgets/content_panel_view.py"}
- {filepath: "widgets/metadata_widget.py"}

### "core"
Zentrale Hilfskomponenten wie "content_filter_parser", "paths_registry", "schemas_registry", "undo_manager".

**Dateien:**
- {filepath: "core/content_filter_parser.py", purpose: "Filter contents by their metadata."}
- {filepath: "core/project_paths.py", purpose: "Registry for Foldernames"}
- {filepath: "core/schema_registry.py", purpose: "Registry for Node and Content Schemas. Schemas base on JSON"}
- {filepath: "core/undo_manager.py", purpose: "Undo manager"}

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
- {filepath: "schemas/chapter_meta.json"}
- {filepath: "schemas/content_schema.json"}