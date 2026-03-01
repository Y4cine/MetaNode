# Qt Signal/Slot-Übersicht

**Legende**
- `Signal --> Slot`: direkte Verdrahtung über `.connect(...)`
- Darstellung fokussiert auf Hauptfenster und zentrale Widgets

**Basiert auf**
- `ui/main_window.py`
- `ui/tree_view.py`
- `widgets/content_panel_stack.py`
- `widgets/single_content_panel.py`
- `widgets/content_editor_base.py`
- `ui/toolbar_manager.py`

```mermaid
flowchart LR
    subgraph Tree
      TSel[node_selected(str)]
      TChanged[itemSelectionChanged]
    end

    subgraph MainWindow
      MOnNode[MainWindow.on_node_selected]
      MEdited[MainWindow.on_content_edited]
      MTreeFocus[focus_tree_view]
      MMetaFocus[focus_node_metadata]
      MUndo[do_combined_undo]
      MRedo[do_combined_redo]
    end

    subgraph ContentStack
      ReqAdd[request_add_panel]
      ReqClose[request_close_panel]
      FSel[filter_selected(str)]
      CEdited[content_edited]
      OnFSel[_on_panel_filter_selected]
      OnCEd[_on_panel_content_edited]
    end

    subgraph Editor
      EEdited[TextBlockEditor.content_edited]
      ERenderer[TextBlockEditor.renderer_changed]
      WriteBack[SingleContentPanel._write_back_current]
    end

    subgraph Commands
      MenuOpen[Datei->Öffnen]
      MenuSave[Datei->Speichern]
      TBUndo[Toolbar Undo]
      TBRedo[Toolbar Redo]
      ShortUndo[Ctrl+Z Shortcut]
      ShortRedo[Ctrl+Y Shortcut]
    end

    TChanged --> TSel
    TSel --> MOnNode

    ReqAdd -->|connect| ReqAddHandler[ContentPanelStack.add_panel]
    ReqClose -->|connect| ReqCloseHandler[ContentPanelStack.remove_panel]
    FSel -->|connect| OnFSel
    CEdited -->|connect| OnCEd
    OnCEd --> MEdited

    EEdited --> WriteBack
    WriteBack --> CEdited
    ERenderer --> WriteBack

    MenuOpen --> FMOpen[FileManager.open_file]
    MenuSave --> FMSave[FileManager.save_file]
    TBUndo --> MUndo
    TBRedo --> MRedo
    ShortUndo --> MUndo
    ShortRedo --> MRedo

    KTree[Global Shortcut tree_view] --> MTreeFocus
    KMeta[Global Shortcut node_metadata] --> MMetaFocus
```
