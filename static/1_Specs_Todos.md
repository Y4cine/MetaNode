## Specifications
Wir schreiben einen Editor, der erlaubt 
- ein Dokument als Hierarchie zu bearbeiten, ein Baum
- jeder Knoten im Baum hat
  - beliebig viele Contents (nicht Tree Children)
  - Metadaten nach einem Schema und zusätzliche freie
- Jeder Content eines Knotens hat
  - Metadaten nach einem Schema und zusätzliche freie
  - In den Metadaten ist auch ein Wert für Renderer angegeben, so dass unterschiedliche Contents eingefügt werden können.
- Mögliche Renderer: Text, Markdown, HTML, Bilder im base64-Format, Tabellen, etc.

Mögliche Applikationen:
- Bücher speichern für unterschiedliche Leser-Gruppen (z.B. Wissenschaftler, technische interessierte, Schüler) und in unterschiedlichen Sprachen
- Funktionale Spezifikation schreiben für unterschiedliche Leser-Gruppen (Kunden, unterschiedliche Abteilungen in der Wertschöpfungskette - Elektriker, Mechaniker, Projektierer, Inbetriebnehmer, usw.), in unterschiedlichen Sprachen
- Versionskontrolle über Teile der Dokumente.

Serialisierung:
- Die Dokumente werden als JSON-Dateien gespeichert
- Die Schemas für die Metadaten werden als JSON-Dateien gespeichert

UI:
- Das Programm öffnet immer nur eine Datei
- Das Fenster hat einen horizontalen Splitter, mit links den Treeview für den Knotenbaum und rechts alle Daten für den ausgewählten Knoten.
- der rechte Panel ist durch 2 vertikale Splitter in 2 Teile aufteilt.
1. Die Metadaten des Knotens
2. Der Contentsbereich
- Der Contents-Bereich hat als Basis nur einen Single-Content-Bereich. Per Knopfdruck können mehr solche Bereiche hinzugefügt, um die parallele Bearbeitung von Contents zu ermöglichen. Splitter teilen diesen Bereich auf, die Panels sind nebeneinander.
- Ein single-content-panel wird vertical in 2 Bereiche durch einen Splitter geteilt. Oben befindet sich der Filter, die Ergebnisse und die Metadaten, unten der Editor selbst.
- Der Editor des contents wird mittels renderers definiert.
- Das Layout der Splitter und die Panels werden mit ihren Filtern in den Metadaten des Dokuments gespeichert. Dies könnte vielleicht ein unsichtbarer Knoten um Baum sein (Am Anfang oder am Ende)

---

## 📐 Spezifikation: Rechter Panel (Stand: 2025-06-23)

### Ziel

Der rechte Panel stellt die Details des aktuell gewählten Knotens dar und ist auf komfortable parallele Bearbeitung von Inhalten ausgerichtet. Er soll Editorfokus bieten, aber auch Metadatenstruktur sichtbar und bearbeitbar machen.

---

### 1. **Grundstruktur**

Der rechte Panel (`RightPanel`) ist durch einen **vertikalen Splitter** in zwei Hauptbereiche geteilt:

#### 1.1. **NodeMetadataPanel**

* Zeigt die **Metadaten des Knotens** als TreeView
* Struktur:

  * Root: Knotentitel oder "Node"
  * Child-Nodes: Felder wie `title`, `status`, `preferred_renderer`, ...
  * Spalten:

    * `ActualValue` (editierbar)
    * `DefaultValue` (editierbar)
  * Quelle der Default-Werte:

    * Primär aus dem Schema
    * Überschreibbar im Knotenfeld `default_metadata`
* Optional: Freie Felder werden ebenfalls angezeigt (aber z. B. grau markiert)

#### 1.2. **ContentsPanel**

* Enthält einen **horizontalen Splitter**, der mehrere `SingleContentPanels` nebeneinander ermöglicht
* Jeder `SingleContentPanel` ist vertikal gegliedert:

---

### 2. **SingleContentPanel**

Aufbau (vertikaler Splitter, von oben nach unten):

#### 2.1. **Filterbereich**

* `QLineEdit` mit Textfilter (z. B. `lang = "DE" AND audience = "POP"`)
* Filter wirkt auf alle Contents
* Parser ist boolesch mit AND/OR/NOT

#### 2.2. **ContentMetadataPanel**

* TreeView mit allen gefilterten Contents
* Struktur:

  * Root: „Content1“, „Content2“, ...
  * Child-Nodes: Metadaten-Felder
  * Spalten:

    * `ActualValue` (editierbar)
    * `DefaultValue` (aus Schema oder DefaultMetadata)
  * Optional: Visualisierung der Herkunft (Schema, Default, explizit gesetzt)

#### 2.3. **Editorbereich**

* Weitere vertikale Aufteilung:

  * Renderer-Auswahl (Dropdown)
  * Titel-Eingabefeld
  * Editor-Widget (abhängig vom Renderer)
* Inhalt und Metadaten werden beim Wechsel gespeichert

---

### 3. **Vererbung und Default-Werte**

* Schema-Default ist **immer vorhanden**, wenn im Schema definiert
* Knoten können mit `default_metadata` bestimmte Felder überschreiben
* Contents erben diese Defaults, **wenn sie das Feld leer lassen**
* Beim Anzeigen im TreeView wird unterschieden:

  * explizit gesetzter Wert
  * vererbter Wert aus `default_metadata`
  * Fallback auf Schema-Default

---

### 4. **Speicherlogik (für Layout)**

* Die Position und Größe der Splitter sowie die Anzahl und Filter der ContentPanels sollen gespeichert werden.
* Dafür wird ein **unsichtbarer Systemknoten** im Dokument verwendet, z. B. `id = _layout`.
* Dieser enthält Konfiguration wie:

```json
{
  "splitter_sizes": [200, 600],
  "panels": [
    {"filter": "lang = 'DE'", "selected": 0},
    {"filter": "audience = 'POP'", "selected": 1}
  ]
}
```

---

### 5. **GUI-Verhalten**

* Bei Auswahl eines neuen Knotens:

  * NodeMetadataPanel lädt Knotendaten
  * ContentsPanel lädt Contents
  * Erste Content-Zeile wird automatisch selektiert
* Filter aktualisieren TreeView und Auswahl
* Editor wird bei Wechsel aktualisiert
* Buttons zum Hinzufügen/Schließen von Panels sind vorhanden

---



## Todos
## Todos

### erledigt
[x] Metadata-Panel überarbeiten  
[x] Rechten Panel überarbeiten  
[x] Renderer implementieren 

[x] Metadaten hinzufügen, löschen, umbenennen. Methoden und Knöpfe
[x] Contents hinzufügen, löschen, sortieren? Methoden und Knöpfe

### UI
[ ] Icons überarbeiten - selbst zeichnen  
[ ] Commands registry
[ ] Anzeige-Modi: Standard Panels, JSON-Struktur, Lese-Modus
[ ] Zumindest Darkmode, besser Themes.

### Renderer
[ ] Mehr Renderer implementieren (Bilder, Markdown, HTML, Tabellen, etc.)

[ ] Split und Merge - vertikal zu Knoten, horizontal zu Contents. Das löst das Attachment Problem. Erfordert die Auswahl mehrerer Contents.

### Import-Export
[ ] Drag and Drop nach Außen von Knoten und Contents. (Akzeptiert Files aus Explorer, Selektionen, usw.). Kontext-Menü: Import/Export.


## Bugs
[ ] New Content --> "AttributeError: 'QComboBox' object has no attribute 'text'"
[ ] Die Filter Combos are not populated right away. They are only after switching between them.

---
## Ideen 
1. Wenn man die json zipped, könnte man auch beliebige Attachments dem Dokument hinzufügen (PDF, Bilder, etc.). Bei den Bildern hätte das den Vorteil, dass sie nicht mehr als base64 gespeichert werden müssen. MetaNode müsste dann mit 2 Arten von Dateien arbeiten: json und "mdx". mdx = gezippte Meta Node Datei.
2. Speicherformat flexibel machen JSON, SQLite, zip
3. Medienplan-Handbuch in MetaNode schreiben.
