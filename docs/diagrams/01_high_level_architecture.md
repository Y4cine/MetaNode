# High-Level-Architektur (C4-ish)

**Legende**
- `UI`: Qt Widgets, Fenster, Panels
- `Domain`: Baum-/Node-/Content-Objekte
- `Core Services`: Schema, Filter, Undo, Layout/Pfade
- `Persistence`: JSON-Dateien (Projekt + User-Settings)

**Basiert auf**
- `main.py::main`
- `ui/main_window.py::MainWindow`
- `ui/file_manager.py::FileManager`
- `models/tree_data.py::TreeDataModel`
- `ui/node_editor_panel.py::NodeEditorPanel`
- `widgets/content_panel_stack.py::ContentPanelStack`
- `widgets/single_content_panel.py::SingleContentPanel`
- `core/schema_registry.py::SchemaRegistry`
- `core/project_settings.py`
- `utils/user_settings.py`

```mermaid
flowchart LR
    U[Benutzer]

    subgraph UI[Qt UI Layer]
      MW[MainWindow]
      TA[TreeArea / NodeTree]
      NEP[NodeEditorPanel]
      CPS[ContentPanelStack]
      SCP[SingleContentPanel]
      NMP[NodeMetadataPanel]
      CMP[ContentMetadataPanel]
      ED[ContentEditor]
      FM[FileManager]
      MM[ModeManager]
    end

    subgraph DOMAIN[Domain Model]
      TDM[TreeDataModel]
      TNW[TreeNodeWrapper]
      NODE[Node]
      CNT[Content]
      META[Metadata]
    end

    subgraph CORE[Core Services]
      SR[SchemaRegistry]
      PS[project_settings]
      UM[UndoManager]
      CFP[ContentFilterParser]
      KM[KeyboardNavigationManager]
    end

    subgraph PERSIST[Persistence]
      PJ[(Projekt JSON)]
      US[(User Settings JSON)]
      SCH[(JSON Schemas)]
    end

    U --> MW
    MW --> TA
    MW --> NEP
    MW --> FM
    MW --> MM
    MW --> KM

    TA --> TDM
    NEP --> NMP
    NEP --> CPS
    CPS --> SCP
    SCP --> CMP
    SCP --> ED
    SCP --> CFP

    FM --> TDM
    FM --> PS
    FM --> US

    TDM --> TNW
    NEP --> NODE
    NODE --> CNT
    NODE --> META
    CNT --> META

    SR --> SCH
    MW --> SR

    TDM --> UM
    NEP --> UM

    TDM <--> PJ
    PS <--> PJ
    MW <--> US
```
