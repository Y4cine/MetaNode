# Zustandsmodell (vereinfachte State Machine)

**Legende**
- Modelliert UI-/Editor-Zustände auf hoher Ebene.
- `dirty` bezieht sich auf `TreeDataModel._dirty` und/oder Editor-Änderungen.

**Basiert auf**
- `ui/mode_manager.py::ModeManager`
- `ui/file_manager.py` (`maybe_save_before_exit`, `open_file`, `save_file`, `new_file`)
- `models/tree_data.py` (`mark_dirty`, `mark_clean`)
- `widgets/single_content_panel.py::_write_back_current`

```mermaid
stateDiagram-v2
    [*] --> AppStart
    AppStart --> NormalMode : MainWindow.__init__

    state NormalMode {
      [*] --> NoDocument
      NoDocument --> DocumentLoaded : new_file/open_file
      DocumentLoaded --> Dirty : edit node/content
      Dirty --> Clean : save_file
      Clean --> Dirty : edit node/content
    }

    NormalMode --> ReadMode : ModeManager.set_read_mode
    ReadMode --> NormalMode : ModeManager.set_edit_mode

    NormalMode --> JsonModeDialog : ModeManager.set_json_mode
    ReadMode --> JsonModeDialog : ModeManager.set_json_mode
    JsonModeDialog --> NormalMode : Dialog close (bei Start aus Normal)
    JsonModeDialog --> ReadMode : Dialog close (bei Start aus Read)

    DocumentLoaded --> PromptSave : maybe_save_before_exit + dirty
    Dirty --> PromptSave : maybe_save_before_exit
    PromptSave --> DocumentLoaded : No
    PromptSave --> Clean : Yes + save
    PromptSave --> DocumentLoaded : Cancel (kein Übergang)

    Clean --> [*] : App schließen
```
