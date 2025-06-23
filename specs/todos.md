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
