# PROJECT OVERVIEW (Updated 2025-07-05)

## Keyboard Navigation & Accessibility (July 2025)
- **Central KeyboardManager**: All keyboard shortcuts and Tab-rotation logic are managed by a central class, ensuring robust, user-friendly navigation across the app.
- **Configurable Shortcuts**: Shortcuts are defined in `resources/keyboard_shortcuts.json` and can be overridden by user settings.
- **Tab-Rotation & Focus Management**: Tab and Shift+Tab rotate focus within all core areas (TreeView, Node-Metadata, ContentPanels). After shortcut navigation, the first relevant UI element is focused automatically.
- **Visual Focus Feedback**: All key widgets provide a visible focus outline/border, theme-aware for accessibility.
- **Tooltips & Status Bar**: All important UI elements have tooltips with keyboard hints. The status bar shows context-sensitive navigation tips and updates on focus change.
- **Escape**: Always returns focus to the TreeView.
- **Design Decisions**: Overlay for Alt-key navigation was considered but not implemented. Tab navigation is flexible and can leave the current area if needed.
- **See also**: `refactor_navigation.md` for specification, ToDo-list, and implementation details.

## Architecture Summary
- `CustomSplitter`/`CustomSplitterHandle`: Custom QSplitter subclass used everywhere in the UI. Prevents full collapse, always shows a visible, labeled handle, and is theme-aware. Pane labels are set via addWidget for clarity. Robustly saves/restores layout state as ratios. All splitters (main, content, per-panel) now use this class.
- `MainWindow`: Thin coordinator. Handles high-level app events, delegates all logic to manager classes and panels.
- `NodeEditorPanel`: Handles node switching, local undo/redo, and right-side content panel logic.
- `SplitterManager`: Centralizes creation and management of all splitters (main, per-panel, etc.).
- `PanelStateManager`: Collects and restores all UI state (splitters, filters, panel visibility, etc.).
- `FileManager`: Handles all file open/save/recent logic, always prompts for unsaved changes, flushes editor state before saving.
- `ModeManager`: Handles mode switching (read, edit, JSON, etc.).
- `ToolbarManager`/`MenuManager`: Setup and manage toolbars and menus.
- `SingleContentPanel`/`ContentPanelStack`: Encapsulate content panel logic, splitter/metadata panel handling.
- `UndoManager`: Integrated into `NodeEditorPanel` for local undo/redo.
- `NodeTree`: Now a modular class composed of mixins for all major behaviors:
    - `TreeSearchMixin` (search/filter)
    - `TreeContextMenuMixin` (context menu/edit)
    - `TreeClipboardMixin` (copy/cut/paste)
    - `TreeDragDropMixin` (drag-and-drop)
  This makes the tree view robust, maintainable, and easy to extend.
- `ContentPanelView`: Now a modular class composed of mixins for all major behaviors:
    - `ContentFilterMixin` (filtering)
    - `ContentTableMixin` (table setup/columns)
    - `ContentEditorManagerMixin` (editor instantiation/switching)
  This makes the right/content panel robust, maintainable, and easy to extend.

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
- `NodeTree`

## Key Architectural Changes (July 2025)
- **CustomSplitter and CustomSplitterHandle** are now used for all splitters (main, content, per-panel):
    - Prevents full collapse, always shows a visible, labeled handle.
    - Draws a label for collapsed regions (rotated for horizontal splitters).
    - Label dynamically reflects the content of the hidden/collapsed panel, or uses explicit label from addWidget.
    - Robustly saves/restores layout state as ratios.
    - Visually clean, theme-aware, and does not overlap content.
    - All code is maintainable, modular, and documented.
    - Debug code and unused imports removed, docstrings added, linter warnings minimized.

### 1. Modularization & Manager Classes
- **MainWindow** is now a thin coordinator. All major logic is delegated to manager classes:
  - `ToolbarManager`, `MenuManager`, `FileManager`, `ModeManager`, `SplitterManager`, `PanelStateManager`, `UndoManager`.
- **Node switching, undo/redo, and panel logic** are handled by dedicated classes.
- **Pluggable editor interface** (`BaseEditor`) allows for future extension of content editors/renderers.
- **Layout/panel state is restored on startup** when the last file is loaded, matching manual file open behavior.
- **Minimum width for single content panels and metadata panels is set to 80px**, preventing full collapse but allowing compact layouts.
- **All modularization and event wiring is complete as of July 2025.**

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
- `NodeTree` in `tree_view.py` is now fully modularized using mixins for search, context menu, clipboard, and drag-and-drop logic. The class is declarative and easy to maintain.
- `ContentPanelView` in `content_panel_view.py` is now modularized using mixins for filtering, table, and editor management. The class is declarative and easy to maintain.

---

*For more details, see `refactoring.md`, `CHANGELOG.md`, and `README.md`.*

## Notes
- All major logic is now modular and encapsulated.
- Only minor logic (e.g., JSON editor, settings) remains in `MainWindow`.
- The architecture is designed to support future extension with new editors and renderers.
- See `refactoring.md` for detailed change log and pending tasks.