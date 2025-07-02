**CHANGELOG.md:**

## [Unreleased]

### 01.07.2025
- Saved filter status with file. Filters are now in ComboBoxes.

### 25.06.2025
- Refactored UI layout persistence: All relevant QSplitter ratios (main, right panel, content panels, and per-panel splitters) are now saved and restored explicitly using unique keys.
- Removed recursive splitter detection to prevent layout inconsistencies and ensure robust, workflow-safe restoration.
- Cleaned up all debug output for production readiness.
- The layout is now reliably restored for any panel configuration, supporting complex nested structures.

### 23.06.2025
- Implemented the renderer Factory
- Fixed write back bug, contents where lost after editing.
- Renderer encapsulates dynamic editor panels, they raise their own edited events, pass them to the editor panel, which in turn ensures that the data are written back.
- Implemented writing content metadata back
- Implemented managing contents (cut, copy, paste, new, delete, rename) with buttons
- Implemented managing metadata fields (cut, copy, paste, new, delete, rename) with context menü.




### Added
- Right panel refactored into split layout with separate NodeMetadataPanel and multi-panel content area
- Introduced `SingleContentPanel` with filter, metadata tree, and renderer-based editor
- Implemented `ContentMetadataPanel` showing content metadata in editable tree view
- Synchronized editor ↔ metadata view with content selection and updates
---

**core/content_filter_parser.py:**

import re
from models.content_model import Content


def is_valid_filter(filter_str):
    """Returns True if the filter string is non-empty and can be parsed without error."""
    if not filter_str or not filter_str.strip():
        return False
    try:
        ContentFilterParser(filter_str)
        return True
    except Exception:
        return False


class ContentFilterParser:
    def __init__(self, filter_text: str):
        self.filter_text = filter_text.strip()

    def match(self, content: Content) -> bool:
        if not self.filter_text:
            return True

        expr = self._parse_expression(self.filter_text)
        return expr(content)

    def _parse_expression(self, text: str):
        # Tokenisierung
        tokens = re.findall(r'\w+\s*=\s*"[^"]*"|AND|OR|NOT', text)

        def parse_token(token: str):
            if "=" in token:
                key, val = token.split("=")
                key = key.strip()
                val = val.strip().strip('"')
                return lambda c: str(c.metadata.get(key, "")).strip() == val
            elif token == "NOT":
                return "NOT"
            elif token == "AND":
                return "AND"
            elif token == "OR":
                return "OR"
            return None

        # Einfacher Evaluierungsstack (ohne Klammern)
        stack = []
        for tok in tokens:
            op = parse_token(tok)
            if callable(op):
                stack.append(op)
            elif op == "NOT":
                prev = stack.pop()
                stack.append(lambda c, p=prev: not p(c))
            elif op == "AND":
                right = stack.pop()
                left = stack.pop()
                stack.append(lambda c, left_func=left,
                             r=right: left_func(c) and r(c))
            elif op == "OR":
                right = stack.pop()
                left = stack.pop()
                stack.append(lambda c, left_func=left,
                             r=right: left_func(c) or r(c))

        return stack[-1] if stack else lambda c: True
---

**core/project_paths.py:**

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FOLDERS = {
    "root": BASE_DIR,
    "resources": BASE_DIR / "resources",
    "schemas": BASE_DIR / "schemas",
    "static": BASE_DIR / "static",
    "specs": BASE_DIR / "specs",
    "utils": BASE_DIR / "utils",
    "icons": BASE_DIR / "resources" / "icons",
}


def get_path(folder: str, filename: str = None, create: bool = False) -> Path:
    """
    Gibt Pfad zum Ordner oder zu einer Datei im Ordner zurück.
    
    :param folder: Einer der Keys aus FOLDERS
    :param filename: Optionaler Dateiname (relativ zu diesem Ordner)
    :param create: Wenn True, wird der Ordner (ggf. samt Unterordnern) angelegt
    :return: Path-Objekt
    """
    if folder not in FOLDERS:
        raise ValueError(f"Unknown folder alias '{folder}'. Valid: {list(FOLDERS.keys())}")

    path = FOLDERS[folder]
    
    if filename:
        path = path / filename

    if create:
        path.parent.mkdir(parents=True, exist_ok=True)

    return path


def file_exists(folder: str, filename: str) -> bool:
    """Prüft, ob Datei existiert."""
    return get_path(folder, filename).exists()
---

**core/project_settings.py:**

# core/project_settings.py
from PyQt5.QtCore import QTimer


def get_settings_node(tree_data):
    """
    Sucht den Settings-Knoten (id == '_settings') im Baum.
    Legt ihn an, falls er nicht existiert.
    Gibt das Settings-Node-Dict zurück.
    """
    for node in tree_data.get('children', []):
        if node.get('id') == '_settings':
            return node
    # Falls nicht vorhanden, anlegen
    settings_node = {'id': '_settings', 'settings': {}}
    tree_data.setdefault('children', []).append(settings_node)
    return settings_node


def get_settings(tree_data):
    """Gibt das settings-Dict aus dem Settings-Knoten zurück."""
    node = get_settings_node(tree_data)
    return node.get('settings', {})


def set_settings(tree_data, settings_dict):
    """Setzt das settings-Dict im Settings-Knoten."""
    node = get_settings_node(tree_data)
    node['settings'] = settings_dict


def get_global_filters(tree_data):
    """
    Gibt die globale Filterliste aus dem Settings-Knoten zurück.
    Falls nicht vorhanden, wird eine leere Liste zurückgegeben.
    """
    settings = get_settings(tree_data)
    return settings.get('global_filters', [])


def set_global_filters(tree_data, filter_list):
    """
    Setzt die globale Filterliste im Settings-Knoten.
    """
    settings = get_settings(tree_data)
    settings['global_filters'] = filter_list
    set_settings(tree_data, settings)


def restore_layout_from_settings(settings, right_area, main_window):
    """
    Stellt das Layout (Panels, Splitter, Filter) anhand der Settings wieder her.
    - Entfernt alle bestehenden ContentPanels
    - Erzeugt für jeden Filter-Eintrag ein Panel (auch für leere Filter)
    - Setzt Splitter-Größen (erst nach Panel-Erzeugung und Event-Loop!)
    - Trägt Filtertexte ein
    - Entfernt überzählige Panels
    """
    # Panels zurücksetzen
    if hasattr(right_area.content_stack, 'clear_panels'):
        right_area.content_stack.clear_panels()
    # Panels gemäß Filter-Settings anlegen
    filters = settings.get('filters', {})
    num_panels = len(filters)
    if hasattr(right_area.content_stack, 'ensure_panel_count'):
        right_area.content_stack.ensure_panel_count(num_panels)
    panels = right_area.get_all_content_panels() if hasattr(
        right_area, 'get_all_content_panels') else []
    # Überzählige Panels entfernen (Leichen)
    if hasattr(right_area.content_stack, 'remove_panels_after'):
        right_area.content_stack.remove_panels_after(num_panels - 1)
    # Splitter wiederherstellen (nach Panel-Erzeugung und Event-Loop!)
    splitters = settings.get('splitters', {})

    def set_splitters():
        for key, sizes in splitters.items():
            if hasattr(main_window, '_restore_splitter_sizes'):
                main_window._restore_splitter_sizes(
                    main_window.centralWidget(), key, sizes)
        # Debug-Ausgabe für Splittergrößen
        from PyQt5.QtWidgets import QSplitter

        def print_splitter_sizes(widget, key):
            if isinstance(widget, QSplitter):
                print(f"DEBUG Splitter {key} sizes:", widget.sizes(), "sum:",
                      sum(widget.sizes()), "width:", widget.size().width())
            if hasattr(widget, 'children'):
                for i, child in enumerate(widget.children()):
                    if isinstance(child, QSplitter):
                        name = f"{key}_splitter{i}"
                        print_splitter_sizes(child, name)
                    elif hasattr(child, 'children'):
                        print_splitter_sizes(child, f"{key}_child{i}")

        print_splitter_sizes(main_window.centralWidget(), "main")
    QTimer.singleShot(0, set_splitters)
    # Filtertexte setzen
    for idx in range(num_panels):
        key = f"panel{idx}"
        if key in filters and idx < len(panels):
            panel = panels[idx]
            if hasattr(panel, 'filter_input'):
                panel.filter_input.setEditText(filters[key])
---

**core/schema_registry.py:**

# schema_registry.py
import json
import os
from typing import Dict
from core.project_paths import get_path, file_exists


class SchemaRegistry:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.cache: Dict[str, Dict] = {}

    def load_schema(self, name: str) -> Dict:
        if name in self.cache:
            return self.cache[name]
        filename = f"{name}.json"
        path = get_path("schemas", filename)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.cache[name] = data
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema not found: {path}")

    def get(self, name: str) -> Dict:
        """Alias für load_schema."""
        return self.load_schema(name)
---

**core/undo_manager.py:**

import copy
from typing import Any, List


class UndoManager:
    def __init__(self):
        self.stack: List[Any] = []
        self.index: int = -1

    def push(self, snapshot: Any):
        # entferne Redo-Pfad
        self.stack = self.stack[:self.index + 1]
        self.stack.append(copy.deepcopy(snapshot))
        self.index += 1

    def can_undo(self) -> bool:
        return self.index > 0

    def can_redo(self) -> bool:
        return self.index < len(self.stack) - 1

    def undo(self) -> Any:
        if self.can_undo():
            self.index -= 1
            return copy.deepcopy(self.stack[self.index])
        return None

    def redo(self) -> Any:
        if self.can_redo():
            self.index += 1
            return copy.deepcopy(self.stack[self.index])
        return None

    def reset(self):
        self.stack.clear()
        self.index = -1
---

**gitignore:**

# === Python ===
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.pdb
*.so
*.egg-info/
*.log

# Bytecode caches (PEP 3147)
__pycache__/
*.pyc

# === Virtual environments ===
.venv/
venv/
env/
ENV/
.build/

# === OS junk ===
.DS_Store
Thumbs.db
desktop.ini

# === Qt Designer artifacts ===
*.ui
*.qrc

# === IDEs ===
.vscode/
.idea/
*.swp

# === Output / builds / backup ===
dist/
build/
*.bak
*.tmp

# === Test artifacts ===
.coverage
.tox/
.nox/

# === Custom folders ===
Archive/
---

**LICENSE:**

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
---

**main.py:**

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
---

**models/content_model.py:**

# content_model.py

from typing import Dict, Any
from models.metadata_model import Metadata


class Content:
    def __init__(self, raw: Dict[str, Any], metadata_schema: Dict[str, Any]):
        self.content_type: str = raw.get("content_type", "text")
        self.title: str = raw.get("title", "")
        self.data: Dict[str, Any] = raw.get("data", {})
        self.renderer: str = raw.get("renderer", "")
        self.metadata = Metadata(raw.get("metadata", {}), metadata_schema)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_type": self.content_type,
            "title": self.title,
            "data": self.data,
            "renderer": self.renderer,
            "metadata": self.metadata.to_dict()
        }

    def validate(self):
        self.metadata.validate()
        # TODO: Später: Datenvalidierung für self.data ergänzen

---

**models/metadata_model.py:**

# metadata_model.py

from typing import Any, Dict, Optional


class Metadata:
    def __init__(self, data: Optional[Dict[str, Any]] = None,
                 schema: Optional[Dict[str, Any]] = None):
        self.data = data or {}
        self.schema = schema or {}

    def get(self, key: str, default=None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.data)

    def update_from_dict(self, updates: Dict[str, Any]):
        self.data.update(updates)

    def keys(self):
        return self.data.keys()

    def validate(self):
        # TODO: Später → optional mit jsonschema.validate(self.data, self.schema)
        pass
---

**models/node_model.py:**

# node_model.py

from typing import Dict, Any, List
from models.metadata_model import Metadata
from models.content_model import Content


class Node:
    def __init__(self, raw: Dict[str, Any], meta_schema: Dict[str, Any],
                 content_schema: Dict[str, Any]):
        self.id: str = raw.get("id", "")
        self.title: str = raw.get("title", "")
        self.metadata = Metadata(raw.get("metadata", {}), meta_schema)
        self.contents: List[Content] = [
            Content(c, content_schema) for c in raw.get("contents", [])
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "metadata": self.metadata.to_dict(),
            "contents": [c.to_dict() for c in self.contents]
        }
---

**models/tree_data.py:**

# Summary:


import uuid
import json
from typing import Any, Dict, List, Optional
import copy
from core.undo_manager import UndoManager
from core.project_paths import get_path, file_exists


class TreeNodeWrapper:
    def __init__(self, node_data: Dict[str, Any],
                 parent: Optional["TreeNodeWrapper"] = None):
        self.node = node_data
        self.parent = parent
        self.children: List["TreeNodeWrapper"] = [
            TreeNodeWrapper(child_data, parent=self)
            for child_data in self.node.get("children", [])
        ]

    @property
    def id(self) -> str:
        return self.node.get("id", "")

    @property
    def title(self) -> str:
        return self.node.get("title", "")

    @title.setter
    def title(self, new_title: str):
        self.node["title"] = new_title

    def add_child(self, child_data: Dict[str, Any]) -> "TreeNodeWrapper":
        child_data.setdefault("id", str(uuid.uuid4()))
        child_data.setdefault("children", [])
        self.node.setdefault("children", []).append(child_data)
        child = TreeNodeWrapper(child_data, parent=self)
        self.children.append(child)
        return child

    def remove_child(self, child_id: str) -> bool:
        for i, child in enumerate(self.children):
            if child.id == child_id:
                self.children.pop(i)
                self.node.get("children", []).pop(i)
                return True
        return False

    def find_by_id(self, node_id: str) -> Optional["TreeNodeWrapper"]:
        if self.id == node_id:
            return self
        for child in self.children:
            found = child.find_by_id(node_id)
            if found:
                return found
        return None

    def to_dict(self) -> Dict[str, Any]:
        self.node["children"] = [child.to_dict() for child in self.children]
        return self.node


class TreeDataModel:
    def __init__(self):
        self.root: Optional[TreeNodeWrapper] = None
        self.file_path: Optional[str] = None
        self._dirty: bool = False
        self._undo = UndoManager()

    def load_from_dict(self, data: Dict[str, Any]):
        self.root = TreeNodeWrapper(data)
        self._undo.reset()
        self._undo.push(self.to_dict())
        self.mark_clean()

    def to_dict(self) -> Dict[str, Any]:
        return self.root.to_dict() if self.root else {}

    def load_from_file(self, path: str):
        full_path = get_path("resources", path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.file_path = full_path
            self.load_from_dict(data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Datei nicht gefunden: {full_path}")

    def save_to_file(self, path: Optional[str] = None):
        if path is None:
            if not self.file_path:
                raise ValueError("No file path specified for saving.")
            path = self.file_path
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        self.mark_clean()

    def find_node(self, node_id: str) -> Optional[TreeNodeWrapper]:
        return self.root.find_by_id(node_id) if self.root else None

    def move_node(self, child_id: str, new_parent_id: str) -> bool:
        node_to_move = self.find_node(child_id)
        new_parent = self.find_node(new_parent_id)
        if not node_to_move or not new_parent or not node_to_move.parent:
            return False

        if not node_to_move.parent.remove_child(child_id):
            return False

        node_to_move.parent = new_parent
        new_parent.children.append(node_to_move)
        new_parent.node.setdefault(
            "children", []).append(node_to_move.to_dict())
        return True

    def move_node_to_index(self, child_id: str,
                           new_parent_id: str, index: int) -> bool:
        node_to_move = self.find_node(child_id)
        new_parent = self.find_node(new_parent_id)
        if not node_to_move or not new_parent or not node_to_move.parent:
            return False

        if not node_to_move.parent.remove_child(child_id):
            return False

        node_to_move.parent = new_parent
        new_parent.children.insert(index, node_to_move)
        new_parent.node.setdefault("children", []).insert(
            index, node_to_move.to_dict())
        return True

    def is_dirty(self) -> bool:
        return self._dirty

    def mark_dirty(self):
        self._dirty = True

    def mark_clean(self):
        self._dirty = False

    def push_undo_snapshot(self):
        self._undo.push(self.to_dict())

    def can_undo(self):
        return self._undo.can_undo()

    def can_redo(self):
        return self._undo.can_redo()

    def undo(self):
        snapshot = self._undo.undo()
        if snapshot:
            self.load_from_dict(copy.deepcopy(snapshot))
            self.mark_dirty()

    def redo(self):
        snapshot = self._undo.redo()
        if snapshot:
            self.load_from_dict(copy.deepcopy(snapshot))
            self.mark_dirty()
---

**README.md:**

# MetaNode

**MetaNode** is a modular, schema-driven editor for hierarchical structures (trees), where each node can contain multiple content variants — for different languages, audiences, or purposes.

> 🛠️ **Work in Progress**  
> MetaNode is under active development. Expect rapid improvements and breaking changes.

## 🧠 Why MetaNode?

Writing complex content for **multiple target groups** or **in several languages** often leads to chaos — duplicated files, endless folders, or tangled markup.  
MetaNode brings structure into this mess:

- Each **node** holds its own **metadata** and a list of **contents**
- Each **content** is versioned by metadata (e.g. `lang`, `audience`, `version`)
- Multiple **edit panels** let you filter, view and edit in parallel

Whether you're documenting software, writing educational materials, or mapping a fictional world — MetaNode helps you **manage versions without redundancy**.

![UI](resources/UI_20250623.PNG)

## 🔧 Key Features

- **Tree-based Node Editor**
  - Add, rename, move, delete nodes
  - Search with optional deep-search
  - Full drag-and-drop with undo support

- **Multi-Content Architecture**
  - Each node can hold multiple contents (text, image, HTML, etc.)
  - Each content has structured metadata (e.g. language, audience, version)

- **Filterable, Multi-Panel Editing**
  - Define content filters (e.g. `lang = "DE" AND audience = "POP"`)
  - Open several filtered views side-by-side
  - Each panel shows a table of matches + live editor

- **Extensible Renderers**
  - New content types and renderers can be added
  - Current default: `text_blocks` for plain/structured text

- **Schema-Based Validation**
  - Node and content metadata are driven by JSON Schema
  - UI adapts to the defined fields

- **Undo/Redo**
  - Tree and content changes are tracked separately
  - Keyboard shortcuts: `Ctrl+Z`, `Ctrl+Y`

## 📦 Example Use Cases

- Multilingual documentation with audience-specific content
- Educational books with POP/SCI/INT tracks
- World-building tools (chapters, notes, internal lore)
- Legal or technical documents with layered annotations

## 🚀 Getting Started

```bash
pip install PyQt5
python main.py
```

## 📁 Project Structure

MetaNode is organized into clear subfolders:

- `models/` – Data classes for nodes, contents, metadata, and tree logic  
- `ui/` – Main window and layout modules for tree, editor, and panels  
- `widgets/` – Modular editor widgets for content and metadata  
- `core/` – Filtering, schema registry, undo, and path utilities  
- `schemas/` – JSON Schemas for metadata structure  
- `resources/` – Icons, examples, and saved trees  
- `specs/` – Project specs, todos, and internal documentation

📄 For a detailed architectural breakdown, see [`static/2_Project_Structure.md`](static/2_Project_Structure.md)


## 📜 License

MetaNode is released under the [MIT License](LICENSE).

## 🧾 Disclaimer and Origin

MetaNode was born out of necessity. As a process engineer, I write specifications for various stakeholders — clients, mechanical, electrical, and software teams. I also work on a book about memetics that requires multilingual, multi-level content. Managing all these versions in Access became too painful.

So I switched to Python and PyQt. ChatGPT (4o) — codename "Kai" — was my sparring partner throughout. Many architectural decisions emerged from these dialogues. Thanks to OpenAI for creating such a brilliant tool. What a time to build.
---

**schemas/chapter_meta.json:**

{
  "type": "object",
  "properties": {
    "status": { "type": "string" },
    "print": { "type": "string" }
  }
}
---

**schemas/content_schema.json:**

{
  "type": "object",
  "properties": {
    "lang": { "type": "string" },
    "audience": { "type": "string", "enum": ["POP", "SCI", "INT"] },
    "version": { "type": "string" },
    "main": { "type" : "string"},
    "status": { "type" : "string"}
  }
}
---

**specs/Specs_20250622.md:**

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

---

**specs/todos.md:**

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
3. Medienplan-Handbuch in MetaNode schreiben.---

**ui/content_panel_view.py:**

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem,
    QPushButton, QLabel
)
from PyQt5.QtCore import pyqtSignal
from datetime import datetime
from models.content_model import Content
from widgets.content_editor_widget import ContentEditorWidget
from core.content_filter_parser import ContentFilterParser


class ContentPanelView(QWidget):
    request_add_panel = pyqtSignal()
    request_close_panel = pyqtSignal()

    def __init__(self, meta_schema, content_schema, filter_text="", parent=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema
        self._all_contents: list[Content] = []
        self._current_editor: ContentEditorWidget = None

        layout = QVBoxLayout(self)

        # --- Filterzeile ---
        top_row = QHBoxLayout()
        self.filter_input = QLineEdit(filter_text)
        self.filter_input.setPlaceholderText(
            "Filter z.B. lang = \"DE\" AND audience = \"POP\"")
        self.filter_input.textChanged.connect(self.apply_filter)
        top_row.addWidget(QLabel("Filter:"))
        top_row.addWidget(self.filter_input)

        # Buttons rechts
        btn_add = QPushButton("+")
        btn_close = QPushButton("x")
        btn_dup = QPushButton("Duplizieren")
        btn_new = QPushButton("Neu")
        top_row.addWidget(btn_add)
        top_row.addWidget(btn_close)
        top_row.addWidget(btn_dup)
        top_row.addWidget(btn_new)

        btn_add.clicked.connect(self.request_add_panel.emit)
        btn_close.clicked.connect(self.request_close_panel.emit)
        # btn_dup.clicked.connect(...) später
        # btn_new.clicked.connect(...) später

        layout.addLayout(top_row)

        # --- Tabelle & Editor ---
        self.content_table = QTableWidget()
        self.content_table.setColumnCount(len(self._all_columns()))
        self.content_table.setHorizontalHeaderLabels(self._all_columns())
        self.content_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.content_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.content_table.setEditTriggers(
            QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        self.content_table.cellClicked.connect(self.on_table_cell_clicked)
        self.content_table.cellChanged.connect(self.on_table_cell_changed)
        layout.addWidget(self.content_table)

        self.editor_placeholder = QLabel("Kein Content ausgewählt")
        layout.addWidget(self.editor_placeholder)

    def set_contents(self, contents: list[Content]):
        self._all_contents = contents
        self.apply_filter()

    def apply_filter(self):
        self.content_table.setRowCount(0)
        columns = self._all_columns()

        parser = ContentFilterParser(self.filter_input.text())
        matching_contents = [c for c in self._all_contents if parser.match(c)]

        for row, content in enumerate(matching_contents):
            self.content_table.insertRow(row)
            for col, key in enumerate(columns):
                val = self._get_column_value(content, key)
                item = QTableWidgetItem(val)
                if col == 0:
                    item.setData(1000, content)
                self.content_table.setItem(row, col, item)

        # automatische Auswahl
        selected = self.select_default_content()
        if selected:
            for row in range(self.content_table.rowCount()):
                item = self.content_table.item(row, 0)
                if item and item.data(1000) is selected:
                    self.content_table.selectRow(row)
                    self.on_table_cell_clicked(row, 0)
                    break

    def _get_column_value(self, content: Content, key: str) -> str:
        if key == "ID":
            return str(id(content))
        elif key == "Titel":
            return content.title or ""
        elif key in ("main", "modified"):
            return str(content.metadata.get(key, ""))
        else:
            return str(content.metadata.get(key, ""))

    def on_table_cell_clicked(self, row: int, column: int):
        item = self.content_table.item(row, 0)
        if not item:
            return
        content = item.data(1000)

        if self._current_editor:
            self.layout().removeWidget(self._current_editor)
            self._current_editor.deleteLater()

        self._current_editor = ContentEditorWidget(
            content, excluded_fields=self._schema_columns())
        self.layout().addWidget(self._current_editor)

    def on_table_cell_changed(self, row: int, col: int):
        if row < 0 or col < 0:
            return

        item = self.content_table.item(row, 0)
        if not item:
            return
        content = item.data(1000)
        if not isinstance(content, Content):
            return
        if not content:
            return

        key = self._all_columns()[col]
        value = self.content_table.item(row, col).text()

        if key == "Titel":
            content.title = value
        elif key in self.content_schema["properties"]:
            content.metadata.set(key, value)
        elif key in ("main", "modified"):
            content.metadata.set(key, value)
        content.metadata.set(
            "modified", datetime.now().isoformat(timespec="seconds"))
        mod_col = self._column_index("modified")

        self.content_table.blockSignals(True)
        self.content_table.setItem(row, mod_col, QTableWidgetItem(
            content.metadata.get("modified", "")))
        self.content_table.blockSignals(False)

    def on_content_selected(self, current, previous):
        if self._current_editor:
            self.layout().removeWidget(self._current_editor)
            self._current_editor.deleteLater()
            self._current_editor = None

        if current:
            content = current.data(1000)
            editor = ContentEditorWidget(
                content, excluded_fields=self._schema_columns())
            self._current_editor = editor
            self.layout().addWidget(editor)
        else:
            self.layout().addWidget(self.editor_placeholder)

    def select_default_content(self):
        if not self._all_contents:
            return

        # Hauptkandidat: main = "1", "true", "yes"
        for c in self._all_contents:
            val = str(c.metadata.get("main", "")).lower()
            if val in ("1", "true", "yes"):
                return c

        # Fallback: jüngster – optionales Feld "modified"
        def get_timestamp(c):
            # ISO-Zeitstempel z. B. "2025-06-18T10:23:00"
            return c.metadata.get("modified", "")

        sorted_by_time = sorted(
            self._all_contents, key=get_timestamp, reverse=True)
        return sorted_by_time[0] if sorted_by_time else None

    def _schema_columns(self):
        dynamic = list(self.content_schema.get("properties", {}).keys())
        for fixed in ("main", "modified"):
            if fixed in dynamic:
                dynamic.remove(fixed)
        return dynamic

    def _all_columns(self):
        return ["ID", "Titel", "main", "modified"] + self._schema_columns()

    def _column_index(self, name: str) -> int:
        return self._all_columns().index(name)
---

**ui/main_window.py:**

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout,
    QFileDialog, QMessageBox, QShortcut
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QIcon

from ui.tree_view import NodeTree
from models.tree_data import TreeDataModel
from ui.node_editor_panel import NodeEditorPanel
from core.schema_registry import SchemaRegistry
from models.node_model import Node
from core.project_paths import get_path
from core.project_settings import get_settings, set_settings
from utils.ratios import calculate_ratios


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.last_node_id = None
        # print("\n==================== MainWindow Konstruktor ====================\n")
        self.setWindowTitle("MetaNode")
        self.resize(1200, 800)

        self.model = TreeDataModel()

        # Schemas vorbereiten
        # oder „schemas“, je nach Pfadstruktur
        self.schemas = SchemaRegistry(base_dir=".")
        self.meta_schema = self.schemas.get("chapter_meta")
        self.content_schema = self.schemas.get(
            "content_schema")  # oder einfach ein Dummy für jetzt

        # Hauptlayout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Linke Seite: Tree mit Suche
        self.tree_area = NodeTree()
        splitter.addWidget(self.tree_area.container)
        self.tree_area.node_selected.connect(self.on_node_selected)

        # Rechte Seite: neue Inhaltsansicht mit mehreren Panels
        self.right_area = NodeEditorPanel(
            meta_schema=self.meta_schema,
            content_schema=self.content_schema
        )
        splitter.addWidget(self.right_area)

        splitter.setSizes([300, 900])

        # Datei-Menü
        self._init_file_menu()
        # Toolbar initialisieren
        self._init_toolbar()
        # Ansicht-Menü ergänzen
        self._init_view_menu()

        # Initiales Beispiel laden
        self.model.load_from_file("memetik.json")
        self.tree_area.load_model(self.model)
        # Settings prüfen und anwenden (wie in open_file)
        tree_data = self.model.to_dict()
        settings = get_settings(tree_data)
        node_id = self.last_node_id or "root"
        node_wrapper = self.model.find_node(node_id)
        if node_wrapper:
            raw_node = node_wrapper.node
            node_obj = Node(raw_node, self.meta_schema, self.content_schema)
            self.right_area.load_node(node_obj)
        else:
            self.right_area.load_node(None)
        # Splitter wiederherstellen
        if 'splitters' in settings:
            for key, sizes in settings['splitters'].items():
                self._restore_splitter_sizes(self.centralWidget(), key, sizes)
        # Filter wiederherstellen und Panels ggf. anlegen
        if 'filters' in settings and hasattr(self.right_area, 'get_all_content_panels'):
            panels = self.right_area.get_all_content_panels()
            num_needed = len(settings['filters'])
            # Panels ggf. dynamisch erzeugen
            if hasattr(self.right_area.content_stack, 'ensure_panel_count'):
                self.right_area.content_stack.ensure_panel_count(num_needed)
                panels = self.right_area.get_all_content_panels()
            for idx in range(num_needed):
                key = f"panel{idx}"
                if key in settings['filters'] and idx < len(panels):
                    panel = panels[idx]
                    if hasattr(panel, 'filter_input'):
                        panel.filter_input.setEditText(settings['filters'][key])

        # Shortcuts
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.do_combined_undo)

        redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_shortcut.activated.connect(self.do_combined_redo)

        # print("\n==================== Nach Konstruktor: Initiales Beispiel geladen ====================\n")

    # ----------------------------
    # Menüleiste und Toolbar
    # ----------------------------

    def _init_file_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Datei")

        file_menu.addAction("Neu", self.new_file)
        file_menu.addAction("Öffnen...", self.open_file)
        file_menu.addAction("Speichern", self.save_file)
        file_menu.addAction("Speichern unter...", self.save_file_as)
        file_menu.addSeparator()
        file_menu.addAction("Schließen", self.close)

    def _init_toolbar(self):
        toolbar = self.addToolBar("Bearbeiten")
        toolbar.setIconSize(QSize(24, 24))

        # Dateiaktionen
        toolbar.addAction(QIcon(str(get_path("icons", "new.svg"))),
                          "Neu", self.new_file)
        toolbar.addAction(QIcon(str(get_path("icons", "open.svg"))),
                          "Öffnen", self.open_file)
        toolbar.addAction(QIcon(str(get_path("icons", "save.svg"))),
                          "Speichern", self.save_file)
        toolbar.addSeparator()

        # Undo/Redo
        toolbar.addAction(QIcon(str(get_path("icons", "undo.svg"))), "Undo",
                          self.do_combined_undo)
        toolbar.addAction(QIcon(str(get_path("icons", "redo.svg"))), "Redo",
                          self.do_combined_redo)
        toolbar.addSeparator()

        # Tree-spezifische Aktionen – nur wenn etwas selektiert ist
        toolbar.addAction(QIcon(str(get_path("icons", "add_child.svg"))),
                          "Unterknoten hinzufügen",
                          lambda: self.tree_area.add_child_to(self.tree_area.currentItem()))
        toolbar.addAction(QIcon(str(get_path("icons", "add_sibling.svg"))), "Nachbarknoten hinzufügen",
                          lambda: self.tree_area.add_sibling_after(self.tree_area.currentItem()))
        toolbar.addAction(QIcon(str(get_path("icons", "delete.svg"))), "Knoten löschen",
                          lambda: self.tree_area.delete_item(self.tree_area.currentItem()))
        toolbar.addAction(QIcon(str(get_path("icons", "rename.svg"))), "Knoten umbenennen",
                          lambda: self.tree_area.rename_item(self.tree_area.currentItem()))

    def _init_view_menu(self):
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("Ansicht")
        view_menu.addAction("SingleContentPanels angleichen",
                            self.equalize_single_content_panels)

    # ----------------------------
    # Dateioperationen
    # ----------------------------

    def new_file(self):
        if not self.maybe_save_before_exit():
            return
        self.model = TreeDataModel()
        self.model.load_from_dict({
            "id": "root",
            "title": "Neue Struktur",
            "children": [],
            "metadata": {},
            "contents": []
        })
        self.tree_area.load_model(self.model)
        self.right_area.load_node(None)  # ← leert das rechte Panel

    def open_file(self):
        # print("\n==================== LADEN: open_file ====================\n")
        path, _ = QFileDialog.getOpenFileName(
            self, "Datei öffnen", "", "JSON-Dateien (*.json)")
        if path:
            self.model.load_from_file(path)
            self.tree_area.load_model(self.model)
            # Settings auslesen
            tree_data = self.model.to_dict()
            settings = get_settings(tree_data)
            # Globale Filterliste aus Settings laden
            if 'global_filters' in settings and hasattr(self.right_area, 'content_stack') and hasattr(self.right_area.content_stack, 'set_global_filters'):
                self.right_area.content_stack.set_global_filters(settings['global_filters'])
            # Settings-Knoten im Modell explizit überschreiben (alte Settings entfernen)
            set_settings(tree_data, settings)
            self.model.load_from_dict(tree_data)
            # Panels/Splitter komplett zurücksetzen und nach Settings neu aufbauen
            from core.project_settings import restore_layout_from_settings
            restore_layout_from_settings(settings, self.right_area, self)
            # Nach Panel-Aufbau Node laden (damit Contents gesetzt werden)
            node_id = self.last_node_id or "root"
            node_wrapper = self.model.find_node(node_id)
            if node_wrapper:
                raw_node = node_wrapper.node
                node_obj = Node(raw_node, self.meta_schema,
                                self.content_schema)
                self.right_area.load_node(node_obj)
            else:
                self.right_area.load_node(None)
        # print("\n==================== ENDE open_file ====================\n")

    def save_file(self):
        # print("\n==================== SPEICHERN: save_file ====================\n")
        # Änderungen aus GUI ins Modell übernehmen
        if self.right_area._node is not None:
            node_wrapper = self.model.find_node(self.right_area._node.id)
            if node_wrapper:
                updated = self.right_area.update_and_return_node()
                node_wrapper.node.update(updated.to_dict())
                self.model.mark_dirty()
        # Layout und Filter speichern
        tree_data = self.model.to_dict()
        settings = get_settings(tree_data)
        # Alle relevanten Splitter speichern
        splitters = {}
        for key, splitter in self.get_all_relevant_splitters().items():
            if splitter.orientation() == Qt.Horizontal:
                sizes = [splitter.widget(i).width() for i in range(splitter.count())]
            else:
                sizes = [splitter.widget(i).height() for i in range(splitter.count())]
            splitters[key] = calculate_ratios(sizes)
        settings['splitters'] = splitters
        # Filter sammeln
        settings['filters'] = self._collect_filters()
        # Globale Filterliste speichern
        if hasattr(self.right_area, 'content_stack') and hasattr(self.right_area.content_stack, 'get_global_filters'):
            settings['global_filters'] = self.right_area.content_stack.get_global_filters()
        # print("\n--- Settings to save ---\n", settings, "\n------------------------\n")
        set_settings(tree_data, settings)
        # Modell mit neuen Settings neu laden, damit sie beim Speichern im JSON landen
        self.model.load_from_dict(tree_data)
        try:
            self.model.save_to_file()
        except ValueError:
            self.save_file_as()

    def save_file_as(self) -> bool:
        path, _ = QFileDialog.getSaveFileName(
            self, "Speichern unter", "", "JSON-Dateien (*.json)")
        if path:
            self.model.save_to_file(path)
            return True
        return False

    def maybe_save_before_exit(self) -> bool:
        if not self.model or not self.model.is_dirty():
            return True

        reply = QMessageBox.question(
            self,
            "Änderungen speichern?",
            "Möchten Sie die Änderungen vor dem Schließen speichern?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )

        if reply == QMessageBox.Yes:
            try:
                self.model.save_to_file()
            except ValueError:
                return self.save_file_as()
            return True
        elif reply == QMessageBox.No:
            return True
        else:
            return False

    def closeEvent(self, event):
        if self.maybe_save_before_exit():
            event.accept()
        else:
            event.ignore()

    # ----------------------------
    # Node-Auswahl → rechts anzeigen
    # ----------------------------

    def on_node_selected(self, node_id):
        # vorherigen Node sichern
        if self.right_area._node is not None:
            node_wrapper = self.model.find_node(self.right_area._node.id)
            if node_wrapper:
                updated = self.right_area.update_and_return_node()
                node_wrapper.node.update(updated.to_dict())
                self.model.mark_dirty()

        # neuen Node laden
        node_wrapper = self.model.find_node(node_id)
        if node_wrapper:
            raw_node = node_wrapper.node
            node_obj = Node(raw_node, self.meta_schema, self.content_schema)
            self.right_area.load_node(node_obj)
        self.last_node_id = node_id

    # ----------------------------
    # Undo / Redo
    # ----------------------------

    def do_combined_undo(self):
        if self.right_area.undo.can_undo():
            self.right_area.do_undo()
        elif self.model.can_undo():
            self.model.undo()
            self.tree_area.load_model(self.model)  # UI aktualisieren

    def do_combined_redo(self):
        if self.right_area.undo.can_redo():
            self.right_area.do_redo()
        elif self.model.can_redo():
            self.model.redo()
            self.tree_area.load_model(self.model)
            if self.last_node_id:
                self.tree_area.select_node_by_id(self.last_node_id)

    def equalize_single_content_panels(self):
        """Setzt alle SingleContentPanels im Splitter auf gleiche Breite."""
        if hasattr(self.right_area, 'content_stack'):
            splitter = self.right_area.content_stack.splitter
            count = splitter.count()
            if count > 0:
                total = splitter.size().width()
                size = total // count if count > 0 else 100
                splitter.setSizes([size] * count)

    def get_all_relevant_splitters(self):
        """Gibt ein Dict aller zu sichernden Splitter mit eindeutigen Keys zurück."""
        splitters = {}
        # Splitter 1: zwischen TreeView und RightPanel
        main_splitter = self.centralWidget().findChild(QSplitter)
        if main_splitter:
            splitters['main'] = main_splitter
        # Splitter 2: im RightPanel zwischen Knoten-Metadata und PanelStack
        if hasattr(self.right_area, 'splitter'):
            splitters['right_panel'] = self.right_area.splitter
        # PanelStack: mehrere Panels nebeneinander
        if hasattr(self.right_area, 'content_stack'):
            splitters['content_panels'] = self.right_area.content_stack.splitter
            # Innerhalb jedes SingleContentPanel: Splitter zwischen Metadata und Editor
            if hasattr(self.right_area.content_stack, 'panel_views'):
                for idx, panel in enumerate(self.right_area.content_stack.panel_views):
                    if hasattr(panel, 'splitter'):
                        splitters[f'panel{idx}_splitter'] = panel.splitter
        return splitters

    def _restore_splitter_sizes(self, widget, key, ratios, prefix="main"):
        splitters = self.get_all_relevant_splitters()
        if key in splitters and ratios:
            splitter = splitters[key]
            total = splitter.size().width() if splitter.orientation() == Qt.Horizontal else splitter.size().height()
            sizes = [max(30, int(r * total)) for r in ratios]
            splitter.setSizes(sizes)

    def _collect_filters(self):
        """Sammelt alle Filtertexte aus den Content-Panels (sofern vorhanden)."""
        filters = {}
        if hasattr(self.right_area, 'get_all_content_panels'):
            for idx, panel in enumerate(self.right_area.get_all_content_panels()):
                if hasattr(panel, 'filter_input'):
                    filters[f"panel{idx}"] = panel.filter_input.currentText()
        return filters

    def _collect_splitter_sizes(self, widget, prefix="main"):
        """Rekursiv alle Splitter und deren tatsächlichen Widget-Größen als Verhältnis sammeln (mit Debug)."""
        from PyQt5.QtWidgets import QSplitter
        from PyQt5.QtCore import Qt
        splitters = {}
        if isinstance(widget, QSplitter):
            if widget.orientation() == Qt.Horizontal:
                sizes = [widget.widget(i).width() for i in range(widget.count())]
            else:
                sizes = [widget.widget(i).height() for i in range(widget.count())]
            # print(f"DEBUG Sammeln Splitter {prefix}: widget-sizes={sizes}, sum={sum(sizes)}")
            # Debug: Zeige die enthaltenen Widgets und deren Typen
            # for i in range(widget.count()):
            #     w = widget.widget(i)
            #     print(f"  Splitter {prefix} Widget {i}: {type(w)}, visible={w.isVisible()}, size={w.size()}")
            ratios = calculate_ratios(sizes)
            splitters[prefix] = ratios
        if hasattr(widget, 'children'):
            for i, child in enumerate(widget.children()):
                if isinstance(child, QSplitter):
                    name = f"{prefix}_splitter{i}"
                    splitters.update(self._collect_splitter_sizes(child, name))
                elif hasattr(child, 'children'):
                    splitters.update(self._collect_splitter_sizes(child, f"{prefix}_child{i}"))
        return splitters

    def debug_panel_splitter_ratios(self):
        """Gibt die Ratios und Breiten der SingleContentPanels im Haupt-Panel-Splitter aus."""
        if hasattr(self.right_area, 'content_stack'):
            splitter = self.right_area.content_stack.splitter
            count = splitter.count()
            sizes = [splitter.widget(i).width() for i in range(count)]
            ratios = calculate_ratios(sizes)
            # print("\n==== DEBUG: SingleContentPanels Splitter ====")
            for i in range(count):
                w = splitter.widget(i)
                # print(f"  Panel {i}: {type(w)}, width={w.width()}, visible={w.isVisible()}")
            # print(f"  sizes={sizes}")
            # print(f"  ratios={ratios}, sum={sum(ratios)}")
            # print("===========================================\n")
        else:
            pass
            # print("[WARN] Kein content_stack mit Splitter gefunden!")

    # WICHTIG: Trennung der Filter-Listen in den Settings
    # 'filters': Panel-spezifische Filterzuordnung, z.B. {'panel0': 'lang="DE"', ...}
    # 'global_filters': Sammlung aller gültigen Filter für die Dropdown-Auswahl in allen Panels
    # Diese Listen dürfen nicht verwechselt oder überschrieben werden!
---

**ui/node_editor_panel.py:**

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt5.QtCore import Qt
from typing import Optional

from widgets.node_metadata_panel import NodeMetadataPanel
from widgets.content_panel_stack import ContentPanelStack
from models.node_model import Node
from models.content_model import Content


class NodeEditorPanel(QWidget):
    def __init__(self, meta_schema, content_schema, parent=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema

        self.meta_panel = NodeMetadataPanel()
        self.content_stack = ContentPanelStack(meta_schema, content_schema)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.meta_panel)
        self.splitter.addWidget(self.content_stack)

        self.splitter.setSizes([200, 600])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)

        self._node: Optional[Node] = None

    def load_node(self, node: Optional[Node]):
        self._node = node
        if node:
            self.meta_panel.set_metadata(node.metadata)

            if not node.contents:
                dummy = Content({
                    "content_type": "text",
                    "title": "Neuer Inhalt",
                    "data": {"text": ""},
                    "renderer": "text_blocks",
                    "metadata": {}
                }, self.content_schema)
                node.contents.append(dummy)

            self.content_stack.set_contents_for_all(node.contents)

    def update_and_return_node(self) -> Node:
        # Metadaten aus TreeView holen
        self._node.metadata = self.meta_panel.get_metadata()

        contents = []
        for c in self.content_stack.panel_views[0]._all_contents:
            if not c.title.strip() and not c.data.get("text", "").strip():
                continue  # leere Dummies überspringen
            contents.append(c)

        self._node.contents = contents
        return self._node

    def do_undo(self):
        pass  # später definieren

    def do_redo(self):
        pass

    @property
    def undo(self):
        class Dummy:
            def can_undo(self): return False
            def can_redo(self): return False
        return Dummy()

    def get_all_content_panels(self):
        """Gibt alle aktiven SingleContentPanel-Instanzen im ContentPanelStack zurück."""
        if hasattr(self.content_stack, 'get_all_content_panels'):
            return self.content_stack.get_all_content_panels()
        # Fallback: Versuche, auf panel_views zuzugreifen
        if hasattr(self.content_stack, 'panel_views'):
            return self.content_stack.panel_views
        return []
---

**ui/tree_view.py:**

from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog,
    QVBoxLayout, QLineEdit, QCheckBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
import json
import uuid

from models.tree_data import TreeDataModel, TreeNodeWrapper


class NodeTree(QTreeWidget):
    node_selected = pyqtSignal(str)  # signalisiert node_id

    def __init__(self, parent=None):
        super().__init__(parent)

        # Model und interne Daten
        self.model: TreeDataModel = None
        self.clipboard_node_dict = None

        # Suchfeld + Optionen
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suche...")
        self.search_input.textChanged.connect(self.on_search)

        self.deep_search_checkbox = QCheckBox("Tiefensuche")
        self.deep_search_checkbox.stateChanged.connect(self.on_search)

        # Eingebetteter Container mit Layout
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.search_input)
        layout.addWidget(self.deep_search_checkbox)
        layout.addWidget(self)
        self.container = container

        # Baum-Darstellung konfigurieren
        self.setHeaderLabels(["Knoten"])
        self.setColumnCount(1)
        self.setStyleSheet("""
            QTreeWidget:focus {
                border: 2px solid #0078d7;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)
        self.itemSelectionChanged.connect(self.on_selection_changed)

        # Drag & Drop aktivieren
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QTreeWidget.InternalMove)

    # ------------------------
    # Modellbindung + Aufbau
    # ------------------------

    def load_model(self, model: TreeDataModel):
        self.model = model
        self.clear()
        if model.root:
            root_item = self._build_item_recursive(model.root)
            self.addTopLevelItem(root_item)
            self.expandAll()

    def _build_item_recursive(self, node: TreeNodeWrapper) -> QTreeWidgetItem:
        item = QTreeWidgetItem([node.title])
        item.setData(0, Qt.UserRole, node.id)
        for child in node.children:
            item.addChild(self._build_item_recursive(child))
        return item

    def select_node_by_id(self, node_id: str):
        def recurse(item):
            if item.data(0, Qt.UserRole) == node_id:
                self.setCurrentItem(item)
                return True
            return any(recurse(item.child(i)) for i in range(item.childCount()))

        for i in range(self.topLevelItemCount()):
            if recurse(self.topLevelItem(i)):
                break

    def on_selection_changed(self):
        items = self.selectedItems()
        if items:
            node_id = items[0].data(0, Qt.UserRole)
            if node_id:
                self.node_selected.emit(node_id)

    # -------------------
    # Kontextmenü + Edit
    # -------------------

    def open_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return
        menu = QMenu()
        menu.addAction("Neuer Knoten darunter",
                       lambda: self.add_sibling_after(item))
        menu.addAction("Neuer Unterknoten", lambda: self.add_child_to(item))
        menu.addAction("Umbenennen", lambda: self.rename_item(item))
        menu.addAction("Löschen", lambda: self.delete_item(item))
        menu.exec_(self.viewport().mapToGlobal(position))

    def add_child_to(self, item):
        self.model.push_undo_snapshot()
        parent_id = item.data(0, Qt.UserRole)
        text, ok = QInputDialog.getText(
            self, "Neuer Knoten", "Titel eingeben:")
        if ok and text:
            parent_node = self.model.find_node(parent_id)
            new_node = parent_node.add_child({
                "title": text,
                "id": str(uuid.uuid4()),
                "children": [], "metadata": {}, "contents": []
            })
            self.model.mark_dirty()
            self.load_model(self.model)
            self.select_node_by_id(new_node.id)

    def add_sibling_after(self, item):
        self.model.push_undo_snapshot()
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        if not node or not node.parent:
            return
        text, ok = QInputDialog.getText(
            self, "Neuer Knoten", "Titel eingeben:")
        if ok and text:
            new_node_data = {
                "title": text, "id": str(uuid.uuid4()),
                "children": [], "metadata": {}, "contents": []
            }
            parent = node.parent
            index = parent.children.index(node)
            parent.children.insert(
                index + 1, TreeNodeWrapper(new_node_data, parent))
            parent.node.setdefault("children", []).insert(
                index + 1, new_node_data)
            self.model.mark_dirty()
            self.load_model(self.model)
            self.select_node_by_id(new_node_data["id"])

    def rename_item(self, item):
        self.model.push_undo_snapshot()
        old_title = item.text(0)
        node_id = item.data(0, Qt.UserRole)
        text, ok = QInputDialog.getText(
            self, "Knoten umbenennen", "Neuer Titel:", text=old_title)
        if ok and text:
            node = self.model.find_node(node_id)
            node.title = text
            self.model.mark_dirty()
            self.load_model(self.model)
            self.select_node_by_id(node_id)

    def delete_item(self, item):
        self.model.push_undo_snapshot()
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        if node and node.parent:
            node.parent.remove_child(node_id)
            self.model.mark_dirty()
            self.load_model(self.model)

    # -------------------
    # Drag & Drop
    # -------------------

    def dropEvent(self, event):
        pos = event.pos()
        target_item = self.itemAt(pos)
        drop_pos = self.dropIndicatorPosition()
        dragged_item = self.currentItem()
        if not dragged_item or not target_item:
            return

        dragged_id = dragged_item.data(0, Qt.UserRole)
        target_id = target_item.data(0, Qt.UserRole)
        target_node = self.model.find_node(target_id)

        if drop_pos == QTreeWidget.OnItem:
            success = self.model.move_node(dragged_id, target_id)
        else:
            parent_item = target_item.parent()
            parent_id = parent_item.data(
                0, Qt.UserRole) if parent_item else self.model.root.id
            parent_node = self.model.find_node(parent_id)
            target_index = parent_node.children.index(target_node)
            if drop_pos == QTreeWidget.BelowItem:
                target_index += 1
            success = self.model.move_node_to_index(
                dragged_id, parent_id, target_index)

        if success:
            self.model.push_undo_snapshot()
            self.model.mark_dirty()
            self.load_model(self.model)
            self.select_node_by_id(dragged_id)
        super().dropEvent(event)

    # -------------------
    # Tastaturbedienung
    # -------------------

    def keyPressEvent(self, event):
        item = self.currentItem()
        if not item:
            return super().keyPressEvent(event)

        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key_Return:
            self.add_sibling_after(item)
        elif key == Qt.Key_Insert:
            self.add_child_to(item)
        elif key == Qt.Key_Delete:
            self.delete_item(item)
        elif key == Qt.Key_F2:
            self.rename_item(item)
        elif key == Qt.Key_Up and modifiers == Qt.AltModifier:
            self.move_up(item)
        elif key == Qt.Key_Down and modifiers == Qt.AltModifier:
            self.move_down(item)
        elif key == Qt.Key_C and modifiers == Qt.ControlModifier:
            self.copy_item(item)
        elif key == Qt.Key_X and modifiers == Qt.ControlModifier:
            self.cut_item(item)
        elif key == Qt.Key_V and modifiers == Qt.ControlModifier:
            self.paste_item(item)
        else:
            super().keyPressEvent(event)

    def move_up(self, item):
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        parent = node.parent
        if not parent:
            return
        index = parent.children.index(node)
        if index <= 0:
            return
        self.model.push_undo_snapshot()
        parent.children[index], parent.children[index -
                                                1] = parent.children[index - 1], parent.children[index]
        parent.node["children"][index], parent.node["children"][index -
                                                                1] = parent.node["children"][index - 1], parent.node["children"][index]
        self.model.mark_dirty()
        self.load_model(self.model)
        self.select_node_by_id(node_id)

    def move_down(self, item):
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        parent = node.parent
        if not parent:
            return
        index = parent.children.index(node)
        if index >= len(parent.children) - 1:
            return
        self.model.push_undo_snapshot()
        parent.children[index], parent.children[index +
                                                1] = parent.children[index + 1], parent.children[index]
        parent.node["children"][index], parent.node["children"][index +
                                                                1] = parent.node["children"][index + 1], parent.node["children"][index]
        self.model.mark_dirty()
        self.load_model(self.model)
        self.select_node_by_id(node_id)

    # -------------------
    # Zwischenablage (Copy/Cut/Paste)
    # -------------------

    def assign_new_ids(self, node_dict):
        node_dict["id"] = str(uuid.uuid4())
        for child in node_dict.get("children", []):
            self.assign_new_ids(child)

    def copy_item(self, item):
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        self.clipboard_node_dict = node.to_dict()

    def cut_item(self, item):
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        self.clipboard_node_dict = node.to_dict()
        if node.parent:
            self.model.push_undo_snapshot()
            node.parent.remove_child(node_id)
            self.model.mark_dirty()
            self.load_model(self.model)

    def paste_item(self, item):
        if not self.clipboard_node_dict:
            return
        parent_id = item.data(0, Qt.UserRole)
        parent_node = self.model.find_node(parent_id)
        if not parent_node:
            return
        self.model.push_undo_snapshot()
        new_node = json.loads(json.dumps(self.clipboard_node_dict))
        self.assign_new_ids(new_node)
        parent_node.add_child(new_node)
        self.model.mark_dirty()
        self.load_model(self.model)
        self.select_node_by_id(new_node["id"])

    def copy_selected(self):
        item = self.currentItem()
        if item:
            self.copy_item(item)

    def cut_selected(self):
        item = self.currentItem()
        if item:
            self.cut_item(item)

    def paste_to_selected(self):
        item = self.currentItem()
        if item:
            self.paste_item(item)

    # -------------------
    # Suche
    # -------------------

    def on_search(self):
        text = self.search_input.text().strip().lower()
        deep = self.deep_search_checkbox.isChecked()
        self.filter_tree(text, deep)

    def filter_tree(self, query: str, deep: bool):
        def recurse_filter(item: QTreeWidgetItem) -> bool:
            node_id = item.data(0, Qt.UserRole)
            node = self.model.find_node(node_id)
            matched = self.node_matches(node, query, deep)
            visible_child = any(recurse_filter(item.child(i))
                                for i in range(item.childCount()))
            item.setHidden(not (matched or visible_child))
            return matched or visible_child

        for i in range(self.topLevelItemCount()):
            recurse_filter(self.topLevelItem(i))

    def node_matches(self, node: TreeNodeWrapper, query: str, deep: bool) -> bool:
        if not query:
            return True

        def match_value(value):
            if isinstance(value, str):
                return query in value.lower()
            elif isinstance(value, list):
                return any(match_value(v) for v in value)
            elif isinstance(value, dict):
                return any(match_value(v) for v in value.values())
            return False

        return match_value(node.node) if deep else query in node.title.lower()
---

**utils/filters.py:**

---

**utils/ratios.py:**

def calculate_ratios(sizes):
    """Berechnet Ratios aus einer Liste von Größen, sodass sum(ratios) == 1 (bis auf Floating-Point-Genauigkeit).
    Gibt eine leere Liste zurück, wenn keine sinnvollen Verhältnisse berechnet werden können
    (z.B. nur Nullen oder leere Eingabe).
    """
    total = sum(sizes)
    n = len(sizes)
    if total > 0 and n > 0:
        ratios = [s / total for s in sizes]
        # Korrigiere den gesamten Rundungsfehler auf das letzte Element
        diff = 1.0 - sum(ratios)
        ratios[-1] += diff
        print(
            f"DEBUG: calculate_ratios sizes={sizes}, total={total}, ratios={ratios}, sum={sum(ratios)}")
        return ratios
    return []
---

**widgets/content_editor_base.py:**

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTextEdit, QComboBox, QLabel
from PyQt5.QtCore import pyqtSignal


class BaseContentEditor(QWidget):
    content_edited = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def set_content(self, content: dict):
        """Setzt die anzuzeigenden Daten im Editor. Erwartet ein Content-Dict."""
        raise NotImplementedError

    def get_content(self) -> dict:
        """Liefert das aktuelle Content-Dict aus dem Editor zurück."""
        raise NotImplementedError


class TextBlockEditor(BaseContentEditor):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(["text_blocks", "markdown", "html"])
        layout.addWidget(QLabel("Renderer:"))
        layout.addWidget(self.renderer_combo)
        self.title_input = QLineEdit()
        layout.addWidget(QLabel("Titel:"))
        layout.addWidget(self.title_input)
        self.text_edit = QTextEdit()
        layout.addWidget(QLabel("Text:"))
        layout.addWidget(self.text_edit)
        self.title_input.installEventFilter(self)
        self.text_edit.installEventFilter(self)
        self.renderer_combo.currentIndexChanged.connect(self._on_renderer_changed)
        self._content = None  # Das aktuell bearbeitete Content-Dict

    def set_content(self, content: dict):
        self._content = content.copy()  # Kopie, um Änderungen zu speichern
        self.title_input.setText(content.get("title", ""))
        self.text_edit.setPlainText(content.get("data", {}).get("text", ""))
        renderer = content.get("renderer", "text_blocks")
        idx = self.renderer_combo.findText(renderer)
        if idx >= 0:
            self.renderer_combo.setCurrentIndex(idx)
        else:
            self.renderer_combo.setCurrentIndex(0)

    def get_content(self) -> dict:
        if not self._content:
            return {}
        result = self._content.copy()
        result["title"] = self.title_input.text()
        result["renderer"] = self.renderer_combo.currentText()
        if "data" not in result:
            result["data"] = {}
        result["data"]["text"] = self.text_edit.toPlainText()
        return result

    def eventFilter(self, obj, event):
        if event.type() == event.FocusOut:
            self.content_edited.emit()
        return super().eventFilter(obj, event)

    def _on_renderer_changed(self):
        self.content_edited.emit()
---

**widgets/content_editor_factory.py:**

from widgets.content_editor_base import TextBlockEditor
# Hier können weitere Editor-Implementierungen importiert werden


def create_content_editor(renderer: str, parent=None):
    """
    Factory-Funktion: Erzeugt den passenden Editor für den angegebenen Renderer.
    """
    if renderer == "text_blocks":
        return TextBlockEditor(parent)
    # Beispiel für weitere Renderer:
    # elif renderer == "markdown":
    #     return MarkdownEditor(parent)
    # elif renderer == "html":
    #     return HtmlEditor(parent)
    # ...
    else:
        # Fallback: TextBlockEditor
        return TextBlockEditor(parent)
---

**widgets/content_editor_widget.py:**

# content_editor_widget.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QGroupBox, QHBoxLayout,
                             QPushButton, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime
from models.content_model import Content
from widgets.metadata_widget import MetadataEditor


class ContentEditorWidget(QWidget):
    delete_requested = pyqtSignal("PyQt_PyObject")

    def __init__(self, content: Content, excluded_fields=None, parent=None):

        super().__init__(parent)
        self._content = content


        self.title_input = QLineEdit(content.title)
        self.text_area = QTextEdit()
        self.text_area.setPlainText(content.data.get("text", ""))

        self.meta_editor = MetadataEditor()
        self.meta_editor.load_metadata(
            content.metadata, exclude=excluded_fields or [])

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Titelzeile mit "Titel" + Löschen-Button
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Titel"))
        top_row.addWidget(self.title_input)
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Inhalt löschen")
        delete_btn.setFixedWidth(30)
        delete_btn.clicked.connect(self._on_delete)
        top_row.addWidget(delete_btn)
        layout.addLayout(top_row)

        layout.addWidget(QLabel("Inhalt (Text)"))
        layout.addWidget(self.text_area)

        meta_group = QGroupBox("Metadaten")
        meta_layout = QVBoxLayout(meta_group)
        meta_layout.addWidget(self.meta_editor)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.text_area)
        splitter.addWidget(meta_group)
        layout.addWidget(splitter)
        splitter.setSizes([300, 100])  # anfängliche Größe

    def _on_delete(self):
        self.delete_requested.emit(self)

    def get_content(self) -> Content:
        self._content.title = self.title_input.text()
        self._content.data["text"] = self.text_area.toPlainText()
        self._content.metadata = self.meta_editor.get_metadata()
        self._content.metadata.set(
            "modified", datetime.now().isoformat(timespec='seconds'))
        return self._content
---

**widgets/content_list_widget.py:**

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from typing import List
from models.content_model import Content
from content_editor_widget import ContentEditorWidget


class ContentListEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._editors: List[ContentEditorWidget] = []
        self._schema = None

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)

        self.add_button = QPushButton("+ Inhalt hinzufügen")
        self.add_button.clicked.connect(self.add_empty_content)

        self.layout.addWidget(self.add_button)
        self.layout.addStretch()

    def load_contents(self, contents: List[Content], schema=None):
        self._schema = schema
        # Alte löschen
        for editor in self._editors:
            self.layout.removeWidget(editor)
            editor.setParent(None)
        self._editors.clear()

        for content in contents:
            self._add_editor(content)

    def _add_editor(self, content: Content):
        editor = ContentEditorWidget(content)
        editor.delete_requested.connect(self._remove_editor)
        self.layout.insertWidget(self.layout.count() - 2, editor)
        self._editors.append(editor)

    def _remove_editor(self, editor: ContentEditorWidget):
        if editor in self._editors:
            if hasattr(self.parent(), "push_undo_snapshot"):
                self.parent().push_undo_snapshot()
            self._editors.remove(editor)
            self.layout.removeWidget(editor)
            editor.setParent(None)

    def add_empty_content(self):
        if not self._schema:
            return
        if hasattr(self.parent(), "push_undo_snapshot"):
            self.parent().push_undo_snapshot()
        new_data = {
            "content_type": "text",
            "title": "Neuer Inhalt",
            "data": {"text": ""},
            "renderer": "text_blocks",
            "metadata": {}
        }
        content = Content(new_data, self._schema)
        self._add_editor(content)

    def get_contents(self) -> List[Content]:
        return [editor.get_content() for editor in self._editors]
---

**widgets/content_metadata_panel.py:**

from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QMenu, QAction, QInputDialog
)
from PyQt5.QtCore import Qt
from typing import List
from models.content_model import Content


class ContentMetadataPanel(QWidget):
    def __init__(self, schema: dict, default_metadata: dict = None, parent=None):
        super().__init__(parent)
        self.schema = schema or {}
        self.default_metadata = default_metadata or {}
        self._metadata_clipboard = None  # Für Copy/Cut/Paste von Feldern
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Feld", "Wert", "Default"])
        self.tree.setAlternatingRowColors(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)

    def set_contents(self, contents: List[Content]):
        self.tree.clear()

        for idx, content in enumerate(contents):
            top = QTreeWidgetItem([f"Content {idx + 1}", "", ""])
            top.setFirstColumnSpanned(True)
            self.tree.addTopLevelItem(top)

            all_keys = set(self.schema.get("properties", {}).keys()) | set(
                content.metadata.data.keys())
            for key in sorted(all_keys):
                actual = str(content.metadata.get(key, ""))
                default = self.default_metadata.get(key)
                if default is None:
                    default = self.schema.get("properties", {}).get(
                        key, {}).get("default", "")
                default = str(default)

                child = QTreeWidgetItem([key, actual, default])
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                top.addChild(child)

            self.tree.expandItem(top)

    def get_metadata_for_index(self, index: int) -> dict:
        """Liefert die aktuellen Metadaten für den Content an Position index als Dict zurück."""
        top = self.tree.topLevelItem(index)
        if not top:
            return {}
        metadata = {}
        for i in range(top.childCount()):
            child = top.child(i)
            key = child.text(0)
            value = child.text(1)
            metadata[key] = value
        return metadata

    def _show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item or not item.parent():
            return  # Nur auf Metadaten-Feldern
        menu = QMenu(self)
        action_add = QAction("Feld hinzufügen", self)
        action_rename = QAction("Feld umbenennen", self)
        action_delete = QAction("Feld löschen", self)
        action_copy = QAction("Feld kopieren", self)
        action_cut = QAction("Feld ausschneiden", self)
        action_paste = QAction("Feld einfügen", self)
        menu.addAction(action_add)
        menu.addAction(action_rename)
        menu.addAction(action_delete)
        menu.addSeparator()
        menu.addAction(action_copy)
        menu.addAction(action_cut)
        menu.addAction(action_paste)
        action_add.triggered.connect(lambda: self.add_metadata_field(item))
        action_rename.triggered.connect(lambda: self.rename_metadata_field(item))
        action_delete.triggered.connect(lambda: self.delete_metadata_field(item))
        action_copy.triggered.connect(lambda: self.copy_metadata_field(item))
        action_cut.triggered.connect(lambda: self.cut_metadata_field(item))
        action_paste.triggered.connect(lambda: self.paste_metadata_field(item))
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def add_metadata_field(self, item):
        key, ok = QInputDialog.getText(self, "Feld hinzufügen", "Name des neuen Felds:")
        if ok and key:
            value, ok2 = QInputDialog.getText(self, "Feld hinzufügen", f"Wert für '{key}':")
            if ok2:
                parent = item.parent()
                new_child = QTreeWidgetItem([key, value, ""])
                new_child.setFlags(new_child.flags() | Qt.ItemIsEditable)
                parent.addChild(new_child)
                parent.setExpanded(True)

    def rename_metadata_field(self, item):
        key = item.text(0)
        new_key, ok = QInputDialog.getText(self, "Feld umbenennen", "Neuer Name:", text=key)
        if ok and new_key and new_key != key:
            item.setText(0, new_key)

    def delete_metadata_field(self, item):
        parent = item.parent()
        if parent:
            parent.removeChild(item)

    def copy_metadata_field(self, item):
        self._metadata_clipboard = (item.text(0), item.text(1))

    def cut_metadata_field(self, item):
        self.copy_metadata_field(item)
        self.delete_metadata_field(item)

    def paste_metadata_field(self, item):
        if not self._metadata_clipboard:
            return
        parent = item.parent()
        if parent:
            key, value = self._metadata_clipboard
            new_child = QTreeWidgetItem([key, value, ""])
            new_child.setFlags(new_child.flags() | Qt.ItemIsEditable)
            parent.addChild(new_child)
            parent.setExpanded(True)
---

**widgets/content_panel_stack.py:**

from PyQt5.QtWidgets import QWidget, QSplitter, QHBoxLayout
from PyQt5.QtCore import Qt
from typing import List

from widgets.single_content_panel import SingleContentPanel
from models.content_model import Content
from utils.ratios import calculate_ratios


class ContentPanelStack(QWidget):
    def __init__(self, meta_schema, content_schema, parent=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema
        self.global_filters = []  # Globale Filterliste für alle Panels

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)

        self.panel_views: List[SingleContentPanel] = []
        self._last_contents: list[Content] = []
        self.add_panel()  # initial ein Panel

    def add_panel(self, filter_text: str = ""):
        panel = SingleContentPanel(self.meta_schema, self.content_schema, filter_text)
        panel.request_add_panel.connect(self.add_panel)
        panel.request_close_panel.connect(lambda: self.remove_panel(panel))
        # Synchronisierung: Wenn ein gültiger Filter ausgewählt/eingegeben wird, global updaten
        panel.filter_selected.connect(self._on_panel_filter_selected)

        self.panel_views.append(panel)
        self.splitter.addWidget(panel)
        # Falls bereits ein Node geladen wurde, Daten sofort setzen:
        if self.panel_views and self.panel_views[0]._all_contents:
            panel.set_contents(self.panel_views[0]._all_contents)
        if self._last_contents:
            panel.set_contents(self._last_contents)

    def remove_panel(self, panel: SingleContentPanel):
        if panel in self.panel_views and len(self.panel_views) > 1:
            self.panel_views.remove(panel)
            self.splitter.widget(self.splitter.indexOf(panel)).deleteLater()

    def set_contents_for_all(self, contents: list[Content]):
        self._last_contents = contents
        for panel in self.panel_views:
            panel.set_contents(contents)

    def clear_panels(self):
        """Entfernt alle Panels aus dem Stack."""
        while self.panel_views:
            panel = self.panel_views.pop()
            self.splitter.widget(self.splitter.indexOf(panel)).deleteLater()

    def ensure_panel_count(self, count: int):
        """Stellt sicher, dass genau 'count' Panels existieren (fügt hinzu oder entfernt)."""
        current = len(self.panel_views)
        if current < count:
            for _ in range(count - current):
                self.add_panel()
        elif current > count:
            for _ in range(current - count):
                self.remove_panel(self.panel_views[-1])

    def get_all_content_panels(self):
        """Gibt alle SingleContentPanel-Instanzen zurück."""
        return self.panel_views

    def remove_panels_after(self, idx: int):
        """Entfernt alle Panels nach dem Index idx (inklusive idx+1 bis Ende)."""
        while len(self.panel_views) > idx + 1:
            self.remove_panel(self.panel_views[-1])

    def _collect_splitter_ratios(self):
        """Gibt die Ratios (Verhältnisse) der Panel-Breiten im Splitter zurück, sodass sum(ratios) == 1."""
        count = self.splitter.count()
        print(f"DEBUG: splitter.count={count}, len(panel_views)={len(self.panel_views)}")
        sizes = []
        for i in range(count):
            w = self.splitter.widget(i)
            width = w.width() if w else -1
            print(f"  Panel {i}: widget={w}, width={width}")
            sizes.append(width)
        total = sum(sizes)
        print(f"  sizes={sizes}, total={total}")
        ratios = calculate_ratios(sizes)
        print(f"  ratios={ratios}, sum={sum(ratios)}")
        return ratios

    def _restore_splitter_ratios(self, ratios):
        """Setzt die Panel-Breiten anhand der Ratios (Verhältnisse) im Splitter."""
        count = self.splitter.count()
        if count == 0 or not ratios:
            return
        total = self.splitter.size().width()
        sizes = [int(r * total) for r in ratios[:-1]]
        # Letztes Panel bekommt den Rest, damit sum(sizes) == total
        last_size = total - sum(sizes)
        sizes.append(max(30, last_size))  # Mindestbreite 30px
        self.splitter.setSizes(sizes)

    def set_global_filters(self, filters: list):
        """Setzt die globale Filterliste und synchronisiert alle Panels."""
        self.global_filters = filters
        self.update_all_filter_dropdowns()

    def get_global_filters(self) -> list:
        """Gibt die globale Filterliste zurück."""
        return self.global_filters

    def update_all_filter_dropdowns(self):
        """Aktualisiert die Filter-Dropdowns in allen Panels mit der globalen Filterliste."""
        for panel in self.panel_views:
            if hasattr(panel, 'update_filter_list'):
                panel.update_filter_list(self.global_filters)

    def _on_panel_filter_selected(self, filter_str):
        """Fügt einen neuen gültigen Filter zur globalen Liste hinzu und synchronisiert alle Dropdowns."""
        if filter_str and filter_str not in self.global_filters:
            self.global_filters.append(filter_str)
            self.update_all_filter_dropdowns()
---

**widgets/metadata_widget.py:**

# metadata_widget.py

from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QCheckBox, QComboBox
from PyQt5.QtCore import Qt
from typing import Dict, Any
from models.metadata_model import Metadata


class MetadataEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._schema: Dict[str, Any] = {}
        self._inputs: Dict[str, QWidget] = {}
        self.layout = QFormLayout(self)

    def load_metadata(self, metadata: Metadata, exclude=None):
        exclude = set(exclude or [])
        self._schema = metadata.schema
        self._inputs.clear()
        # Layout löschen
        while self.layout.count():
            self.layout.removeRow(0)

        # Felder aus Schema anzeigen
        for key, prop in self._schema.get("properties", {}).items():
            if key in exclude:
                continue
            value = metadata.get(key, "")

            widget = self._create_input_widget(prop, value)
            self._inputs[key] = widget
            self.layout.addRow(key, widget)

    def _create_input_widget(self, prop: Dict[str, Any], value: Any) -> QWidget:
        t = prop.get("type")
        if t == "string":
            line = QLineEdit(str(value))
            return line
        elif t == "boolean":
            box = QCheckBox()
            box.setChecked(bool(value))
            return box
        elif t == "array" and prop.get("items", {}).get("type") == "string":
            line = QLineEdit(", ".join(value if isinstance(value, list) else []))
            line.setPlaceholderText("kommagetrennt")
            return line
        else:
            fallback = QLineEdit(str(value))
            fallback.setPlaceholderText("Typ nicht erkannt")
            return fallback

    def get_metadata(self) -> Metadata:
        data = {}
        for key, widget in self._inputs.items():
            if isinstance(widget, QLineEdit):
                val = widget.text()
                if "," in val:
                    data[key] = [s.strip() for s in val.split(",")]
                else:
                    data[key] = val
            elif isinstance(widget, QCheckBox):
                data[key] = widget.isChecked()
            # Weitere Typen hier ergänzen
        return Metadata(data, self._schema)
---

**widgets/node_metadata_panel.py:**

from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QMenu, QAction, QInputDialog
)
from PyQt5.QtCore import Qt
from models.metadata_model import Metadata


class NodeMetadataPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Feld", "Wert", "Default"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)

        self._metadata: Metadata = None
        self._metadata_clipboard = None  # Für Copy/Cut/Paste von Feldern

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)

    def set_metadata(self, metadata: Metadata):
        """Lädt die Metadaten in die Ansicht"""
        self._metadata = metadata
        self.tree.clear()

        schema = metadata.schema or {}
        defined_keys = set(schema.get("properties", {}).keys())

        # Zuerst: Felder aus dem Schema
        for key in defined_keys:
            actual = str(metadata.get(key, ""))
            default = str(schema["properties"][key].get("default", ""))
            self._add_row(key, actual, default)

        # Dann: zusätzliche Felder
        for key in metadata.data.keys():
            if key in defined_keys:
                continue
            val = str(metadata.get(key))
            self._add_row(key, val, "(frei)")

    def _add_row(self, key: str, actual: str, default: str):
        item = QTreeWidgetItem([key, actual, default])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.tree.addTopLevelItem(item)

    def get_metadata(self) -> Metadata:
        """Liest die bearbeiteten Werte aus dem TreeView"""
        new_data = {}
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            key = item.text(0).strip()
            val = item.text(1).strip()
            new_data[key] = val
        return Metadata(new_data, self._metadata.schema if self._metadata else {})

    def _show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return  # Nur auf Feldern
        menu = QMenu(self)
        action_add = QAction("Feld hinzufügen", self)
        action_rename = QAction("Feld umbenennen", self)
        action_delete = QAction("Feld löschen", self)
        action_copy = QAction("Feld kopieren", self)
        action_cut = QAction("Feld ausschneiden", self)
        action_paste = QAction("Feld einfügen", self)
        menu.addAction(action_add)
        menu.addAction(action_rename)
        menu.addAction(action_delete)
        menu.addSeparator()
        menu.addAction(action_copy)
        menu.addAction(action_cut)
        menu.addAction(action_paste)
        action_add.triggered.connect(lambda: self.add_metadata_field(item))
        action_rename.triggered.connect(lambda: self.rename_metadata_field(item))
        action_delete.triggered.connect(lambda: self.delete_metadata_field(item))
        action_copy.triggered.connect(lambda: self.copy_metadata_field(item))
        action_cut.triggered.connect(lambda: self.cut_metadata_field(item))
        action_paste.triggered.connect(lambda: self.paste_metadata_field(item))
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def add_metadata_field(self, item):
        key, ok = QInputDialog.getText(self, "Feld hinzufügen", "Name des neuen Felds:")
        if ok and key:
            value, ok2 = QInputDialog.getText(self, "Feld hinzufügen", f"Wert für '{key}':")
            if ok2:
                new_child = QTreeWidgetItem([key, value, ""])
                new_child.setFlags(new_child.flags() | Qt.ItemIsEditable)
                self.tree.addTopLevelItem(new_child)

    def rename_metadata_field(self, item):
        key = item.text(0)
        new_key, ok = QInputDialog.getText(self, "Feld umbenennen", "Neuer Name:", text=key)
        if ok and new_key and new_key != key:
            item.setText(0, new_key)

    def delete_metadata_field(self, item):
        idx = self.tree.indexOfTopLevelItem(item)
        if idx >= 0:
            self.tree.takeTopLevelItem(idx)

    def copy_metadata_field(self, item):
        self._metadata_clipboard = (item.text(0), item.text(1))

    def cut_metadata_field(self, item):
        self.copy_metadata_field(item)
        self.delete_metadata_field(item)

    def paste_metadata_field(self, item):
        if not self._metadata_clipboard:
            return
        key, value = self._metadata_clipboard
        new_child = QTreeWidgetItem([key, value, ""])
        new_child.setFlags(new_child.flags() | Qt.ItemIsEditable)
        self.tree.addTopLevelItem(new_child)
---

**widgets/single_content_panel.py:**

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSplitter,
    QComboBox, QTreeWidgetItem, QToolBar, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from typing import List
from models.content_model import Content
from widgets.content_metadata_panel import ContentMetadataPanel
from core.content_filter_parser import ContentFilterParser, is_valid_filter
from widgets.content_editor_factory import create_content_editor
from core.project_paths import get_path


class SingleContentPanel(QWidget):
    request_add_panel = pyqtSignal()
    request_close_panel = pyqtSignal()
    filter_selected = pyqtSignal(str)  # Signal für Filterauswahl/-eingabe

    def __init__(self, meta_schema, content_schema, filter_text="", parent=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema
        self._all_contents: List[Content] = []
        self._current_content = None  # aktuell bearbeiteter Content
        self.content_editor = None  # Dynamischer Editor
        self._content_clipboard = None  # Für Copy/Cut/Paste
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- Content-Toolbar ---
        self.content_toolbar = QToolBar("Content-Aktionen")
        self.content_toolbar.setIconSize(QSize(20, 20))

        def icon_or_empty(icon_name):
            try:
                icon_path = str(get_path("icons", icon_name))
                icon = QIcon(icon_path)
                return icon if not icon.isNull() else QIcon()
            except Exception:
                return QIcon()
        self.action_add_content = QAction(icon_or_empty(
            "add_child.svg"), "Content hinzufügen", self)
        self.action_delete_content = QAction(icon_or_empty(
            "delete.svg"), "Content löschen", self)
        self.action_copy_content = QAction(icon_or_empty(
            "copy.svg"), "Content kopieren", self)
        self.action_cut_content = QAction(icon_or_empty(
            "cut.svg"), "Content ausschneiden", self)
        self.action_paste_content = QAction(icon_or_empty(
            "paste.svg"), "Content einfügen", self)
        self.action_rename_content = QAction(icon_or_empty(
            "rename.svg"), "Content umbenennen", self)
        self.content_toolbar.addAction(self.action_add_content)
        self.content_toolbar.addAction(self.action_delete_content)
        self.content_toolbar.addAction(self.action_copy_content)
        self.content_toolbar.addAction(self.action_cut_content)
        self.content_toolbar.addAction(self.action_paste_content)
        self.content_toolbar.addAction(self.action_rename_content)
        layout.addWidget(self.content_toolbar)

        # --- obere Button- und Filterzeile ---
        top_row = QHBoxLayout()
        self.filter_input = QComboBox()
        self.filter_input.setEditable(True)
        self.filter_input.setInsertPolicy(QComboBox.NoInsert)
        self.filter_input.setEditText(filter_text)
        self.filter_input.setPlaceholderText(
            "z.B. lang = 'DE' AND audience = 'POP'")
        self.filter_input.lineEdit().editingFinished.connect(self.on_filter_edit_finished)
        self.filter_input.currentIndexChanged.connect(lambda _: self.on_filter_edit_finished())
        self.filter_input.editTextChanged.connect(lambda _: self.apply_filter())
        top_row.addWidget(QLabel("Filter:"))
        top_row.addWidget(self.filter_input)

        btn_add = QPushButton("+")
        btn_close = QPushButton("×")
        top_row.addWidget(btn_add)
        top_row.addWidget(btn_close)

        btn_add.clicked.connect(self.request_add_panel.emit)
        btn_close.clicked.connect(self.request_close_panel.emit)

        layout.addLayout(top_row)

        # --- vertikaler Splitter für Inhalte ---
        self.splitter = QSplitter(Qt.Vertical)
        layout.addWidget(self.splitter)

        # self.metadata_placeholder = QLabel(...)
        self.metadata_panel = ContentMetadataPanel(
            schema=self.content_schema,
            default_metadata={}  # ← später ersetzen durch Node-Vererbung
        )
        self.metadata_panel.tree.itemClicked.connect(self.on_tree_item_clicked)
        self.splitter.addWidget(self.metadata_panel)

        # Editorbereich
        self.editor_area = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_area)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(self.editor_area)

        self.splitter.setSizes([150, 400])

        # --- Verbindungen für Toolbar-Actionen ---
        self.action_add_content.triggered.connect(self.add_content)
        self.action_delete_content.triggered.connect(self.delete_content)
        self.action_copy_content.triggered.connect(self.copy_content)
        self.action_cut_content.triggered.connect(self.cut_content)
        self.action_paste_content.triggered.connect(self.paste_content)
        self.action_rename_content.triggered.connect(self.rename_content)

    def _set_content_editor(self, content_dict):
        # Entferne alten Editor
        if self.content_editor:
            self.editor_layout.removeWidget(self.content_editor)
            self.content_editor.deleteLater()
            self.content_editor = None
        renderer = content_dict.get("renderer", "text_blocks")
        self.content_editor = create_content_editor(
            renderer, parent=self.editor_area)
        self.editor_layout.addWidget(self.content_editor)
        self.content_editor.set_content(content_dict)
        self.content_editor.content_edited.connect(self._write_back_current)

    def set_contents(self, contents: List[Content]):
        """Übergibt die vollständige Content-Liste an dieses Panel"""
        self._all_contents = contents

        # Filter anwenden
        parser = ContentFilterParser(self.filter_input.currentText())
        matching = [c for c in contents if parser.match(c)]

        self.metadata_panel.set_contents(matching)

        if matching:
            first = matching[0]
            self._current_content = first
            self._set_content_editor(first.__dict__)
        else:
            self._current_content = None
            self._set_content_editor(
                {"title": "", "renderer": "text_blocks", "data": {}})

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        self._write_back_current()  # Änderungen vor Auswahlwechsel speichern
        # Nur Top-Level-Nodes (Content-Nodes) abfangen
        parent = item.parent()
        if not parent:  # Nur reagieren, wenn Kind-Node (Feld) angeklickt wurde
            return

        content_title = parent.text(0)
        index = self.metadata_panel.tree.indexOfTopLevelItem(parent)
        if index < 0 or index >= len(self._all_contents):
            return

        # Neuen Inhalt laden
        selected = self._all_contents[index]
        self._current_content = selected

        self._set_content_editor(selected.__dict__)

    def _write_back_current(self):
        if not self._current_content or not self.content_editor:
            return
        content_dict = self.content_editor.get_content()
        self._current_content.title = content_dict.get("title", "")
        self._current_content.renderer = content_dict.get(
            "renderer", self._current_content.renderer)
        if hasattr(self._current_content, "data") and "data" in content_dict:
            self._current_content.data.update(content_dict["data"])
        # Metadaten übernehmen
        index = self._all_contents.index(self._current_content)
        metadata = self.metadata_panel.get_metadata_for_index(index)
        if hasattr(self._current_content, "metadata") and hasattr(self._current_content.metadata, "data"):
            self._current_content.metadata.data.update(metadata)
        # ⇨ Aktualisiere TreeView (falls noch sichtbar)
        root_item = self.metadata_panel.tree.topLevelItem(index)
        if root_item:
            for i in range(root_item.childCount()):
                child = root_item.child(i)
                key = child.text(0)
                if key == "title":
                    child.setText(1, self._current_content.title)
                elif key == "renderer":
                    child.setText(1, self._current_content.renderer)
                elif key == "text":
                    text = self._current_content.data.get("text", "")
                    child.setText(
                        1, text[:40] + "..." if len(text) > 40 else text)

    def on_filter_edit_finished(self):
        filter_str = self.filter_input.currentText().strip()
        if is_valid_filter(filter_str):
            self.filter_selected.emit(filter_str)
        self.apply_filter()

    def update_filter_list(self, filter_list):
        """Aktualisiert die Dropdown-Liste der Filter."""
        current = self.filter_input.currentText()
        self.filter_input.blockSignals(True)
        self.filter_input.clear()
        self.filter_input.addItems(filter_list)
        self.filter_input.setEditText(current)
        self.filter_input.blockSignals(False)

    def apply_filter(self):
        self._write_back_current()  # Änderungen vor Filterwechsel speichern
        self.set_contents(self._all_contents)

    def add_content(self):
        filter_str = self.filter_input.text()
        print(f"[DEBUG] Aktueller Filter-String: '{filter_str}'")
        import re
        filter_values = dict(re.findall(r"(\w+)\s*=\s*['\"]([^'\"]+)['\"]", filter_str))
        print(f"[DEBUG] Neue Content-Metadaten: {filter_values}")  # Debug-Ausgabe
        metadata = filter_values.copy() if filter_values else {}
        new_content = Content(
            {
                "content_type": "text",
                "title": "Neuer Content",
                "renderer": "text_blocks",
                "data": {"text": ""},
                "metadata": metadata
            },
            self.meta_schema
        )
        self._all_contents.append(new_content)
        self.apply_filter()  # Filter sofort neu anwenden!
        self._current_content = new_content
        self._set_content_editor(new_content.__dict__)

    def delete_content(self):
        if not self._current_content:
            return
        if self._current_content in self._all_contents:
            idx = self._all_contents.index(self._current_content)
            del self._all_contents[idx]
            # Nächsten Content auswählen
            if self._all_contents:
                new_idx = max(0, idx - 1)
                self._current_content = self._all_contents[new_idx]
                self._set_content_editor(self._current_content.__dict__)
            else:
                self._current_content = None
                self._set_content_editor(
                    {"title": "", "renderer": "text_blocks", "data": {}})
            self.set_contents(self._all_contents)

    def copy_content(self):
        if not self._current_content:
            return
        import copy
        self._content_clipboard = copy.deepcopy(self._current_content)

    def cut_content(self):
        self.copy_content()
        self.delete_content()

    def paste_content(self):
        if not self._content_clipboard:
            return
        import copy
        pasted = copy.deepcopy(self._content_clipboard)
        pasted.title += " (Kopie)"
        self._all_contents.append(pasted)
        self.set_contents(self._all_contents)
        self._current_content = pasted
        self._set_content_editor(pasted.__dict__)

    def rename_content(self):
        if not self._current_content:
            return
        from PyQt5.QtWidgets import QInputDialog
        new_title, ok = QInputDialog.getText(
            self, "Content umbenennen", "Neuer Titel:", text=self._current_content.title)
        if ok and new_title:
            self._current_content.title = new_title
            self._set_content_editor(self._current_content.__dict__)
            self.set_contents(self._all_contents)
---

