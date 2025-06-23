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

... more to follow.

## Todos
[ ] Metadata-Panel überarbeiten  
[ ] Rechten Panel überarbeiten  
[ ] Renderer implementieren  
[ ] Icons überarbeiten - selbst zeichnen  

---

### Metadata-Panel überarbeiten  23.06.2025
Vorschlag:
- Die Metadaten kommen in ein TreeView (Beim Node gibt es nur Root, dann die Metadaten als Nodes)
- Bei den Contents, sind die Contents die Nodes auf der Ebene unter Root, die Metadata sind dann Nodes des jeweiligen Content.
- Der Treeview hat mehrere Spalten: actual_value, default_value
- Die Metadata nach Schema sollen als erste im Tree stehen, die zusätzlichen darunter

### Rechten Panel überarbeiten 23.06.2025
Ziel ist es komfortabel schreiben zu können. Metadaten sind wichtig, aber erst nachträglich.  
Der gerenderte Bereich sollte möglichst groß.  
Und apropos Renderer: Knoten sollten ein "prefered_renderer" als Metadata haben. Diese Eigenschaft sollte sich an die Kind-Knoten vererben, aber muss editierbar bleiben - bei den Knoten und bei den Contents.  

Das bringt uns zu den Splittern.
Der erste ist vertikal und trennt Knoten-Metadata vom Contents-Panel.
Im Single-Content-Panel sollte oben der Filter-Input sein, darunter das Metadata-Widget. Im Metadata-Widget werden nur die Ergebnisse des Filters gezeigt, dann die Metadata wie bereits oben für den Knoten beschrieben.
Unter dem Metadata-Bereich kommt:
- ein vertikaler Splitter
- Renderer-Pulldown (redundant im Metadata-Bereich)
- Titel (redundant im Metadata-Bereich)
- Gerenderter Editor

