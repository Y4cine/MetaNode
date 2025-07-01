## Todos

[x] Metadata-Panel überarbeiten  
[x] Rechten Panel überarbeiten  
[x] Renderer implementieren 
[ ] Metadaten hinzufügen, löschen, umbenennen. Methoden und Knöpfe
[ ] Contents hinzufügen, löschen, sortieren? Methoden und Knöpfe

[ ] Icons überarbeiten - selbst zeichnen  
[ ] Mehr Renderer implementieren (Bilder, Markdown, HTML, Tabellen, etc.)

[ ] Split und Merge - vertikal zu Knoten, horizontal zu Contents. Das löst das Attachment Problem. Erfordert die Auswahl mehrerer Contents.
[ ] Drag and Drop nach Außen von Knoten und Contents. (Akzeptiert Files aus Explorer, Selektionen, usw.). Kontext-Menü: Import/Export.

## Bugs
[ ] New Content --> "AttributeError: 'QComboBox' object has no attribute 'text'"


---
Idee: Wenn man die json zipped, könnte man auch beliebige Attachments dem Dokument hinzufügen (PDF, Bilder, etc.). Bei den Bildern hätte das den Vorteil, dass sie nicht mehr als base64 gespeichert werden müssen. MetaNode müsste dann mit 2 Arten von Dateien arbeiten: json und "mdx". mdx = gezippte Meta Node Datei.