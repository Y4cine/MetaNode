# PROJECT OVERVIEW (Updated 2025-07-05)

## Architecture Summary
- `MainWindow`: Thin coordinator. Handles high-level app events, delegates all logic to manager classes and panels.
- `NodeEditorPanel`: Handles node switching, local undo/redo, and right-side content panel logic.
- `SplitterManager`: Centralizes creation and management of all splitters (main, per-panel, etc.).
- `PanelStateManager`: Collects and restores all UI state (splitters, filters, panel visibility, etc.).
- `FileManager`: Handles all file open/save/recent logic, always prompts for unsaved changes, flushes editor state before saving.
- `ModeManager`: Handles mode switching (read, edit, JSON, etc.).
- `ToolbarManager`/`MenuManager`: Setup and manage toolbars and menus.
- `SingleContentPanel`/`ContentPanelStack`: Encapsulate content panel logic, splitter/metadata panel handling.
- `UndoManager`: Integrated into `NodeEditorPanel` for local undo/redo.

## Vision: Pluggable Editors and Renderers
A core architectural goal is to support flexible, pluggable editors and renderers for any node or content type. The system should allow dynamic switching between different editors (e.g., JSON, tree, table, image, form, external file) at runtime or via configuration. This is achieved by:
- Designing the right/content panel as a host for interchangeable editor/renderer widgets.
- Using manager/factory patterns to register and instantiate editors/renderers as needed.
- Defining clear interfaces for editors/renderers to ensure discoverability and replaceability.
- Tracking UI state and user preferences per editor/renderer where appropriate.

## Data Flows
- Node selection in tree triggers `MainWindow.on_node_selected`, which delegates to `NodeEditorPanel.switch_node`.
- All UI state changes (splitters, filters, panel visibility) are routed through `SplitterManager` and `PanelStateManager`.
- File operations are always routed through `FileManager`, which uses `PanelStateManager` for UI state.
- Content edits emit `content_edited` signals, which propagate up to mark the model as dirty.

## Class List (Key)
- `MainWindow`
- `NodeEditorPanel`
- `SplitterManager`
- `PanelStateManager`
- `FileManager`
- `ModeManager`
- `ToolbarManager`
- `MenuManager`
- `SingleContentPanel`
- `ContentPanelStack`
- `UndoManager`

## Key Architectural Changes (July 2025)

### 1. Modularization & Manager Classes
- **MainWindow** is now a thin coordinator. All major logic is delegated to manager classes:
  - `ToolbarManager`, `MenuManager`, `FileManager`, `ModeManager`, `SplitterManager`, `PanelStateManager`, `UndoManager`.
- **Node switching, undo/redo, and panel logic** are handled by dedicated classes.
- **Pluggable editor interface** (`BaseEditor`) allows for future extension of content editors/renderers.

### 2. JSON Editing Policy (NEW)
- **In-place JSON editing in the right pane and content panels is fully removed.**
- **JSON editing is now only possible via a modal dialog** (from the menu/toolbar), and only for the full model (not sub-nodes or content).
- This ensures robust validation, prevents data corruption, and makes the editing workflow safer for users.

### 3. UI/UX Improvements
- Menu and toolbar actions are fully synchronized and managed by dedicated classes.
- File operations, mode switching, and panel changes are robust and context-aware.
- All UI state (splitters, filters, panels) is managed by dedicated managers.

### 4. Extensibility
- The architecture supports pluggable editors/renderers for future content types.
- Settings and user preferences logic is modular and can be further extended.

---

## Recent Refactoring Highlights
- Removed all in-place and sub-node JSON editing. Only full-model JSON editing via modal dialog is allowed.
- All file, menu, toolbar, and mode logic is now delegated to manager classes.
- UI state and data flows are robust, with strong validation and error handling.
- The codebase is ready for further modularization and extension.

---

*For more details, see `refactoring.md`, `CHANGELOG.md`, and `README.md`.*

## Notes
- All major logic is now modular and encapsulated.
- Only minor logic (e.g., JSON editor, settings) remains in `MainWindow`.
- The architecture is designed to support future extension with new editors and renderers.
- See `refactoring.md` for detailed change log and pending tasks.