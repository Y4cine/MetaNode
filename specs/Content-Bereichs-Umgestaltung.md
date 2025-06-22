
## 🧭 Spezifikation: Content-Bereichs-Umgestaltung (rechte Seite)

### 🎯 Ziel

Den Content-Bereich rechts des Hauptfensters so umgestalten, dass:

* **mehrere Inhaltspanels** nebeneinander bearbeitbar sind (horizontal via Splitter)
* **Filter** auf die Contents angewendet werden können
* die Benutzeroberfläche **flexibel und fokussiert** auf Inhalt ist

---

### 🧱 Layoutstruktur

```plaintext
┌──────────────────────────────────────────────┐
│ Knoten-Metadaten (oben)                      │
├──────────────────────────────────────────────┤
│ ContentPanelView 1 ┆ ContentPanelView 2 ┆ …  │
└──────────────────────────────────────────────┘
```

* Trennung Knoten-Metadaten und ContentPanels über **Vertikalen Splitter**
* `ContentPanelView` = horizontales Panel mit:

  * **Filter-Feld**
  * **Liste gefilterter Contents**
  * **Editor** (für einen ausgewählten Content)
  * **Buttons**:

    * `+` neues Panel rechts hinzufügen
    * `x` Panel schließen
    * `Duplizieren` (aktuellen Content duplizieren)
    * `Neu` (neuer leerer Content, aber Metadaten übernehmen)

---

### 🔍 Filter pro Panel

* Syntax: z. B. `lang = "DE" AND audience = "POP" AND NOT version = "draft"`
* Nur einfache Regeln: `AND`, `OR`, `NOT`, `=`, keine Klammern
* leerer Filter → zeigt alle Contents
* bei Treffer:

  * Liste zeigt passende Contents
  * Editor zeigt den ausgewählten Content

---

### 🧠 Verhalten

* initial ist **ein Panel** offen, ohne Filter
* Auswahl eines Contents → Editor & Metadaten sichtbar
* jeder Content-Panel-View zeigt **nur einen** Editor
* derselbe Content darf in mehreren Panels geöffnet werden → Warnung möglich

---

### 💾 Layout-Speicherung

Speicherung in JSON-Datei des Baums, z. B. als `_ui_state` im Wurzelobjekt.

Zu speichern:

* Position der Splitter
* Anzahl & Reihenfolge der Panels
* Filtertext je Panel
* ggf. aktiver Content (per ID)

---

### 🔄 Undo/Redo-Verhalten

| Aktion                     | Undo-fähig?    |
| -------------------------- | -------------- |
| Filter ändern              | ❌ (UI-Zustand) |
| Content löschen/hinzufügen | ✅              |
| Panel schließen/hinzufügen | ❌              |

---

### 🧩 Neue Klassen

| Klasse                | Aufgabe                               |
| --------------------- | ------------------------------------- |
| `ContentPanelStack`   | enthält horizontale Splitter & Panels |
| `ContentPanelView`    | zeigt Filter, Liste, Editor, Buttons  |
| `ContentFilterParser` | einfache Filter-Syntax verarbeiten    |
| `PanelLayoutState`    | Layout-Zustand speichern/laden        |

---

### 🧪 Besondere Antworten

* Mehrere Inhaltstypen vorgesehen (Text, Bild, HTML …)
* Keine Tabs je Panel → nur 1 Editor gleichzeitig
* Sortierung der Contentliste durch Klick auf Spaltenköpfe
* Änderungen an Contents erfolgen **sofort** (kein „Speichern“-Button)

---
