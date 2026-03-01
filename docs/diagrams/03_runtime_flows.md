# Runtime-Flows (Sequence)

## A) App-Startup

**Basiert auf**
- `main.py::main`
- `ui/main_window.py::MainWindow.__init__`
- `core/schema_registry.py::SchemaRegistry.get`
- `ui/file_manager.py::new_file/open_file`

```mermaid
sequenceDiagram
    actor User
    participant Main as main.py::main
    participant Qt as QApplication
    participant MW as MainWindow
    participant SR as SchemaRegistry
    participant FM as FileManager
    participant TDM as TreeDataModel
    participant TA as TreeArea

    User->>Main: Startet Anwendung
    Main->>Qt: QApplication(sys.argv)
    Main->>MW: MainWindow()
    MW->>TDM: TreeDataModel()
    MW->>SR: get("chapter_meta"), get("content_schema")
    MW->>MW: Build UI (TreeArea + NodeEditorPanel)
    MW->>FM: FileManager(self)
    MW->>MW: open_last prüfen
    alt open_last + recent vorhanden
        MW->>TDM: load_from_file(path)
        MW->>TA: load_model(model)
        MW->>MW: restore_layout_from_settings(...)
    else
        MW->>FM: new_file()
        FM->>TDM: load_from_dict(root)
        FM->>TA: load_model(model)
    end
    Main->>MW: show()
    Main->>Qt: exec_()
```

## B) Dokument öffnen/laden

**Basiert auf**
- `ui/file_manager.py::open_file`
- `models/tree_data.py::load_from_file`
- `core/project_settings.py::restore_layout_from_settings`
- `ui/node_editor_panel.py::load_node`

```mermaid
sequenceDiagram
    actor User
    participant MW as MainWindow
    participant FM as FileManager
    participant TDM as TreeDataModel
    participant TA as TreeArea
    participant PS as project_settings
    participant NEP as NodeEditorPanel
    participant Node as Node model

    User->>MW: Datei > Öffnen
    MW->>FM: open_file()
    FM->>FM: maybe_save_before_exit()
    FM->>TDM: load_from_file(path)
    FM->>TA: load_model(model)
    FM->>TDM: to_dict()
    FM->>PS: get_settings(tree_data)
    FM->>PS: restore_layout_from_settings(...)
    FM->>TDM: find_node(last_node_id|"root")
    alt node gefunden
        FM->>Node: Node(raw_node,...)
        FM->>NEP: load_node(node)
    else
        FM->>NEP: load_node(None)
    end
    FM->>FM: add_recent_file(path)
    FM->>FM: update_recent_files_menu()
```

## C) Node/Edit/Save

**Basiert auf**
- `ui/tree_view.py::on_selection_changed`
- `ui/node_selection_manager.py::on_node_selected`
- `ui/node_editor_panel.py::switch_node/update_and_return_node`
- `widgets/single_content_panel.py::_write_back_current`
- `ui/file_manager.py::save_file`

```mermaid
sequenceDiagram
    actor User
    participant Tree as NodeTree
    participant MW as MainWindow
    participant NSM as node_selection_manager
    participant NEP as NodeEditorPanel
    participant SCP as SingleContentPanel
    participant CPS as ContentPanelStack
    participant FM as FileManager
    participant TDM as TreeDataModel

    User->>Tree: Wählt Knoten
    Tree->>MW: node_selected(node_id)
    MW->>NSM: on_node_selected(node_id)
    NSM->>NEP: switch_node(new_node,...)
    NEP->>NEP: update_and_return_node() für alten Knoten

    User->>SCP: Editiert Titel/Text/Metadata
    SCP->>SCP: _write_back_current()
    SCP->>CPS: content_edited Signal
    CPS->>MW: on_content_edited()
    MW->>TDM: mark_dirty()

    User->>FM: Speichern
    FM->>NEP: update_and_return_node()
    FM->>TDM: model.to_dict()
    FM->>FM: collect panel/filter/splitter state
    FM->>TDM: load_from_dict(tree_data+settings)
    FM->>TDM: save_to_file()
```
