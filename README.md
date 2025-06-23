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

## 📁 File Overview

| File                    | Purpose                          |
|-------------------------|----------------------------------|
| `main.py`               | Entry point                      |
| `ui_main_window.py`     | Window layout, loading/saving    |
| `tree_data.py`          | Tree model with undo support     |
| `node_model.py`         | Node structure (metadata + content) |
| `content_model.py`      | Content structure + metadata     |
| `content_editor_widget.py` | Editor for a single content     |
| `content_panel_stack.py`   | Manages horizontal panels       |
| `content_filter_parser.py` | Simple `AND/OR/NOT` logic       |

## 📜 License

MetaNode is released under the [MIT License](LICENSE).
