# Future Data Layer Specification

## Ziel
Ein flexibler und erweiterbarer Daten-Layer, der verschiedene Speicherformate (z. B. JSON, SQLite, Ordnerstruktur) unterstützt und die Trennung zwischen Datenrepräsentation und Anwendungslogik sicherstellt. Dies ermöglicht es, die Anwendung zukunftssicher zu gestalten und neue Features wie Attachments, Tagging oder komplexe Abfragen einfach zu integrieren.

---

## Anforderungen

### 1. **Unterstützte Speicherformate**
- **JSON**: Für einfache, lesbare und portable Daten.
- **Zip**: Für JSON mit Attachments.
- **SQLite**: Für robuste, transaktionssichere und abfrageoptimierte Daten.
- **Ordnerstruktur**: Für flexible Speicherung von Attachments und hierarchischen Daten.

### 2. **Features**
- **Hierarchische Daten**: Unterstützung für verschachtelte oder parent-child Beziehungen.
- **Attachments**: Speicherung von Dateien wie Bildern, Excel-Dokumenten oder anderen Binärdaten.
- **Tagging und Abfragen**: Möglichkeit, Inhalte mit Tags zu versehen und komplexe Abfragen durchzuführen.
- **Versionierung**: Unterstützung für die Nachverfolgung von Änderungen (z. B. mit Git).
- **Datenintegrität**: Sicherstellung der Konsistenz durch Transaktionen oder andere Mechanismen.

---

## Konzept

### 1. **Daten-Layer-Interface**
Ein Interface, das grundlegende Operationen definiert:
```python
class DataLayer:
    def load_node(self, node_id: str) -> dict:
        raise NotImplementedError

    def save_node(self, node_id: str, data: dict) -> None:
        raise NotImplementedError

    def get_children(self, node_id: str) -> list:
        raise NotImplementedError

    def save_attachment(self, file_path: str):
        raise NotImplementedError
```

### 2. **Implementierungen**
- **JSONDataLayer**: Arbeitet mit JSON-Dateien.
- **SQLiteDataLayer**: Nutzt SQLite als Backend.
- **FolderDataLayer**: Interpretiert Ordner und Dateien als Knoten und Inhalte.

### 3. **Integration**
Der Editor kommuniziert nur mit dem Daten-Layer, nicht direkt mit JSON, SQLite oder dem Dateisystem.

Beispiel:
```python
data_layer = JSONDataLayer("path/to/file.json")
root_node = data_layer.load_node("root")
data_layer.save_node("root", root_node)
```

### 4. **Feature-Erkennung**
Der Daten-Layer sollte erkennen, welche Features das aktuelle Backend unterstützt, und ggf. Fehler werfen, wenn ein Feature nicht verfügbar ist.

Beispiel:
```python
class JSONDataLayer(DataLayer):
    def save_attachment(self, file_path: str):
        raise NotImplementedError("Attachments werden in JSON nicht unterstützt.")
```

---

## Beispiele für Speicherformate

### JSON
```json
{
  "id": "root",
  "name": "Dokument",
  "children": [
    {
      "id": "child1",
      "name": "Kapitel 1",
      "content": "Inhalt von Kapitel 1"
    }
  ]
}
```

### SQLite
- Tabelle `nodes`: Speichert Knoten.
- Tabelle `attachments`: Speichert Dateien.

### Ordnerstruktur
```
/Dokument
    /Kapitel1
        meta.json
        inhalt.txt
        bild.png
    /Kapitel2
        meta.json
        tabelle.xlsx
```

---

## Vorteile
- **Flexibilität**: Einfacher Wechsel zwischen Speicherformaten.
- **Erweiterbarkeit**: Neue Features können leicht integriert werden.
- **Robustheit**: SQLite bietet Transaktionen und Datenintegrität.

---

## Nächste Schritte
1. **Prototyping**: Kleine Prototypen für JSON, SQLite und Ordnerstruktur erstellen.
2. **Feature-Liste priorisieren**: Welche Features sind essenziell?
3. **Daten-Layer implementieren**: Mit JSON beginnen und später erweitern.
4. **Tests**: Sicherstellen, dass alle Backends konsistent funktionieren.
