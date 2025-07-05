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
[ ] Lokalisierung

### Renderer
[ ] Mehr Renderer implementieren (Bilder, Markdown, HTML, Tabellen, etc.)
[ ] **Split und Merge** - vertikal zu Knoten, horizontal zu Contents. Das löst das Attachment Problem. Erfordert die Auswahl mehrerer Contents.
[ ] **Formulare** als Editor. Formular-Definition als Dict im Content.

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