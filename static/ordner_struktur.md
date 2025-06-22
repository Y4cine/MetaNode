# Projektstruktur – TreeEditor
Ordner sortiert nach Nutzung und Wichtigkeit.

## 1. Organisation
### "specs/"
Projektspezifikation, ToDos und Arbeitshinweise. Dient auch als Vorlage für die spätere Projektzusammenfassung.
  
### "static/"  
Temporäre Dateien zur automatisierten Generierung der Projektdoku. Keine Runtime-Funktion.

## 2. Quellcode

### "models/"  
Datenmodelle: Klassen für Tree-Struktur, Nodes, Contents und Metadaten.

{models}

### "ui/"
GUI-Struktur für das Hauptfenster mit Bereichen wie TreeView, RightPanel, Node-Metadaten und Content-Panels.

{ui}

### "widgets/"  
Modular aufgebaute, wiederverwendbare Widgets für Content-Editor, Metadaten-Anzeige etc.

{widgets}

### "core/"
Zentrale Hilfskomponenten wie "content_filter_parser", "paths_registry", "schemas_registry", "undo_manager".

{core}

### "utils/"
(Derzeit leer) – reserviert für allgemeine Hilfsfunktionen.

## 3. Ressourcen

### "resources/"  
Projektstartdaten wie z. B. Beispielbaum ("beispielbaum.json").
  
### "resources/icons/"  
Toolbar-Icons (SVG).
  
### "schemas/" 
JSON-Schemas zur Definition von Metadatenfeldern für Nodes und Contents.

{schemas}