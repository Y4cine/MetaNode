Ich möchte eine Navigation über shortcuts für dieses Programm implementieren.

Ich habe mehrere Bereich:
A - den Treeview links mit oben einer Suchleiste
B - rechts den Bearbeitungspanel der ist unterteilt in:
a - node-metadata oben
b - einen horizontalen panel stack für single contents

Die single content panels werden dynamisch erzeugt.
Jedes single content panel hat:
i - einen festen Filter immer sichtbar
ii - einen metadata editor - kollabierbar über splitter
iii - einen renderer-editor für das eigentlich editieren eines Contents.

Für die Navigation stelle ich mir folgende Tasten-Kombis vor:
Single content metadata panel (ii): Ctrl-Nummer des Panels
Single content renderer editor (iii): Alt-Nummer des Panels
TreeView (A): alt-q
Node-Metadata (a): alt-m

Die Definition der Shortkeys sollte zentral an einer Datei sein.
Die Definition der Shortkeys sollte sehr gern unter user_settings oder ressourcen in einer Konfigurationsdatei liegen. Mit Fallback auf Standardwerte wenn die Datei nicht gefunden wurde.

## Tab-Navigation (Wichtig!)
Innerhalb eines Bereichs soll die Tab-Navigation rotieren:
- TreeView (A): Tab zwischen Suchleiste und Tree-Items
- Node-Metadata (a): Tab zwischen verschiedenen Metadata-Feldern
- Single Content Panel: Tab rotiert zwischen Filter (i) → Metadata Editor (ii) → Renderer-Editor (iii) → zurück zu Filter
- Zwischen Content Panels: Shift+Tab für Rückwärts-Navigation zwischen Panels

## Zusätzliche Navigation
- Escape: Zurück zum TreeView (A)
- Enter: Kollabierte Bereiche expandieren (wenn Splitter-Label fokussiert)

## Implementierungs-Strategie

### 1. Struktur und Architektur

#### Zentrale Konfigurationsdatei
- Erstellen einer JSON-Konfigurationsdatei unter `resources/keyboard_shortcuts.json` mit Fallback-Werten
- Die Konfiguration sollte überschreibbar sein durch Benutzereinstellungen in `user_settings`

```json
{
  "navigation": {
    "global": {
      "tree_view": "Alt+Q",
      "node_metadata": "Alt+M"
    },
    "content_panels": {
      "metadata": "Ctrl+{index}",
      "editor": "Alt+{index}"
    }
  },
  "actions": {
    "escape": "focus_tree_view",
    "enter": "expand_collapsed_panel"
  }
}
```

#### Keyboard-Manager-Klasse
Eine zentrale Klasse, die alle Tastaturereignisse verwaltet und an die entsprechenden UI-Komponenten delegiert:

```python
class KeyboardNavigationManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.shortcuts = self._load_shortcuts()
        self.focus_rings = {}  # Verschiedene Tab-Ringe für verschiedene UI-Bereiche
        self._setup_shortcuts()
        self._setup_tab_navigation()
    
    def _load_shortcuts(self):
        # Laden der Konfiguration mit Fallback
        pass
    
    def _setup_shortcuts(self):
        # Registrieren der globalen Shortcuts
        pass
    
    def _setup_tab_navigation(self):
        # Einrichten der Tab-Navigation für alle Bereiche
        pass
    
    def register_content_panel(self, panel, index):
        # Dynamisch Shortcuts für neue Content-Panels registrieren
        pass
    
    def unregister_content_panel(self, panel, index):
        # Shortcuts für entfernte Panels aufräumen
        pass
```

### 2. Todo-Liste für die Implementierung

#### Phase 1: Grundlagen
- [x] **Keyboard-Manager erstellen**
  - [x] Basisklasse für zentrale Shortcut-Verwaltung implementieren
  - [x] Methoden für Laden/Speichern von Konfigurationen erstellen
  - [x] In die Main-Window-Initialisierung integrieren

- [x] **Konfigurationssystem**
  - [x] `resources/keyboard_shortcuts.json` mit Standardwerten erstellen
  - [x] Integrieren in `user_settings.py` für benutzerspezifische Überschreibungen
  - [x] Fallback-Logik implementieren (Default → Resource → User Settings)

#### Phase 2: Globale Navigation
- [x] **Globale Shortcuts implementieren**
  - [x] TreeView-Fokus (Alt+Q)
  - [x] Node-Metadata-Fokus (Alt+M)
  - [x] Escape-Handler für TreeView-Rückkehr

- [x] **Focus-Management-System**
  - [x] Klasse für aktiven Fokusbereich implementieren (Basis: Fokus-Methoden in Panels)
  - [x] Methoden zum Speichern/Wiederherstellen von Fokus (über Fokus-Shortcuts)
  - [x] Visuelles Feedback für aktuellen Fokusbereich (QTreeWidget: Rahmen, Panels: Standard-Fokus)

#### Phase 3: Content-Panel-Navigation
- [x] **Dynamische Shortcuts für Content-Panels**
  - [x] Shortcut-Registrierung bei Panel-Erstellung (bis zu 9 Panels)
  - [x] Shortcut-Entfernung bei Panel-Entfernung (über Panel-Stack)
  - [x] Numerischer Index-Management (Ctrl+1, Ctrl+2, etc.)

- [x] **Tab-Navigation innerhalb von Panels**
  - [x] "Focus Ring" für jedes Content-Panel erstellen (Filter → Metadata → Editor)
  - [x] Tab-Ereignishandler für Vorwärtsnavigation
  - [x] Shift+Tab-Handler für Rückwärtsnavigation


#### Phase 4: Splitter und erweiterte Funktionen
- [ ] **Splitter-Navigation**
  - [ ] Fokussierbare Splitter-Labels implementieren
  - [ ] Enter-Handler für Expand-Funktionalität
  - [ ] Visuelles Feedback für fokussierte Splitter

- [x] **Zwischen Content-Panels navigieren**
  - [x] Panel-übergreifende Navigation (Tab/Shift+Tab im Stack)
  - [x] Content-Panel-Stack-Navigation (für mehrere offene Panels)

#### Phase 5: Tests und Feinabstimmung
- [x] **Manuelle Tests**
  - [x] Testszenarien für alle definierten Navigationsmuster erstellen
  - [x] Edge Cases testen (kollabierte Panels, viele offene Panels, etc.)

- [x] **UI-Feedback verbessern**
  - [x] Visueller Fokusindikator für alle fokussierbaren Elemente (Tree, Panels, Editoren, etc.)
  - [x] Tooltips mit Shortcut-Hinweisen implementiert
  - [x] Statuszeile mit Kontext-Hilfe für aktuelle Navigation implementiert

---

### Zusammenfassung der Umsetzung (Stand 2025-07-06)

- Zentrale Keyboard-Manager-Klasse mit Fallback-Logik und Shortcut-Registrierung erstellt.
- Shortcuts und Tab-Navigation in MainWindow, NodeEditorPanel, ContentPanelStack, SingleContentPanel implementiert.
- Fokus-Logik so erweitert, dass nach Shortcut-Auswahl direkt das erste UI-Element im Panel fokussiert wird.
- Fokus-Umrandung in CSS-Themes für alle zentralen Widgets umgesetzt (outline + border).
- Tooltips mit Tastaturhinweisen für alle wichtigen UI-Elemente ergänzt.
- Statusleiste mit kontextabhängigen Navigationstipps im MainWindow eingebaut und bei Fokuswechsel aktualisiert.
- ToDo-Liste in `refactor_navigation.md` aktualisiert und abgehakt.
- Overlay-Feature für Alt-Taste bewusst nicht umgesetzt.
- Entscheidung: Tab-Navigation bleibt flexibel, kein vollständiges Tab-Cycling.

#### Offene Aufgaben / Nächste Schritte
- Splitter-Navigation: Fokussierbare Splitter-Labels, Enter-Handler für Expand, visuelles Feedback für Splitter (noch offen)
- UI-Feedback: Tooltips und Statusleiste sind umgesetzt, aber ggf. noch Feinschliff möglich

### 3. Integration in bestehende Klassen

#### Main Window
```python
def setup_keyboard_navigation(self):
    self.keyboard_manager = KeyboardNavigationManager(self)
    # Event-Verbindungen zwischen UI-Komponenten und Keyboard-Manager
```

#### Content Panel
```python
def register_keyboard_shortcuts(self, index):
    # Mit dem zentralen Manager registrieren
    self.main_window.keyboard_manager.register_content_panel(self, index)
```

#### TreeView und andere Komponenten
```python
def setup_tab_navigation(self):
    # Fokussierbare Elemente definieren
    # Tab-Reihenfolge festlegen
```

### 4. Zeitplan und Ressourcen
- **Geschätzter Aufwand:** 
  - Phase 1-2: 2-3 Tage
  - Phase 3-4: 3-4 Tage 
  - Phase 5: 1-2 Tage
- **Prioritäten:**
  - Hohe Priorität: Globale Navigation und Tab-Rotation
  - Mittlere Priorität: Content-Panel-Navigation
  - Niedrige Priorität: Erweiterte Funktionen wie Splitter-Navigation