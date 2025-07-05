# MetaNode Refactoring Plan

## July 2025: Major Refactor Summary
- All in-place and sub-node JSON editing is removed. JSON editing is now only possible via a modal dialog for the full model.
- The right pane always shows structured editors; no more direct JSON editing for nodes or content.
- All file, menu, toolbar, and mode logic is delegated to manager classes.
- UI state, undo/redo, and data flows are robust and modular.
- The codebase is ready for further modularization and extension.

## Goals
- Modularize the codebase for maintainability and clarity
- Split large modules (especially `main_window.py`) into focused components
- Improve separation of concerns between UI, logic, and data
- **Enable a flexible, pluggable editor/renderer architecture for different content types**

## Vision: Pluggable Editors and Renderers
A core long-term goal is to support switching between different editors and renderers for any given node or content type. For example, the JSON editor is just one possible view; in the future, nodes could be rendered as tree views, tables, images, forms, or even external files. The architecture should make it easy to add, register, and switch between these editors/renderers dynamically, both at runtime and via configuration.

This vision drives the following refactoring principles:
- Editors and renderers should be modular, discoverable, and replaceable.
- The right/content panel should act as a host/container for pluggable editor/renderer widgets.
- Manager/factory patterns and clear interfaces should be used to support dynamic switching and extension.
- UI state and user preferences should be tracked per editor/renderer where appropriate.

## Todo List

### 1. High-Level Architecture
- [ ] Keep `MainWindow` as a coordinator only
- [ ] Extract `TreeArea` (navigation/tree view logic)
- [ ] Extract `RightPane` (node/content/metadata panels, mode switching)
- [x] Extract toolbar and menu logic into managers
- [x] Extract file and settings logic into managers
- [x] Document all new module responsibilities here (see below)

### 2. Immediate Next Steps
- [x] Move toolbar/menu setup to `toolbar_manager.py` and `menu_manager.py` (done)
- [x] Move file open/save/recent logic to `file_manager.py` (done, including save prompt and window title update)
- [x] Fix: Edits in content panels are now always saved before file operations
- [x] Fix: Deleting content in one panel updates all panels
- [x] Fix: Settings node is hidden from tree view
- [x] Fix: Window title updates after 'Save As'
- [x] Move mode switching logic to `mode_manager.py` (done, including restoring working read mode logic)
- [x] Move splitter/filters logic to `splitter_manager.py` (done)
- [x] Move undo/redo logic to `undo_manager.py` (done)
- [x] Extract `TreeArea` (tree view logic) into its own module/class
- [x] Modularize `NodeTree` using mixins for search, context menu, clipboard, and drag-and-drop (done)
- [x] Modularize right/content panel (`ContentPanelView`) using mixins for filtering, table, and editor management (done)
  - Note: Modularization was achieved via mixins, not a single monolithic class/module, for maintainability and flexibility.
- [x] Update imports and wiring in `MainWindow` to use new components (done)
- [x] Restore layout/panel state on startup when last file is loaded (done)
- [x] Restore minimum width (80px) for single content panels and metadata panels (done)
- [ ] Subclass QSplitter to create a custom splitter that, when collapsed, still shows a visible handle or indicator (prevents full collapse and provides a visual hint). Integrate this custom splitter everywhere splitters are used (main, content panels, per-panel splitters). [Deferred: revisit after main refactor]

### 3. Notes & Decisions
- Removed obsolete `set_read_mode` and `set_json_edit_mode` from `MainWindow` (now handled by `ModeManager`).
- Confirmed that all file, menu, toolbar, and mode logic is now delegated to managers.
- Layout/panel state is now restored on startup when the last file is loaded, matching manual file open behavior.
- Minimum width for single content panels and metadata panels is set to 80px, preventing full collapse but allowing compact layouts.

#### Next Refactoring Steps (as of July 4, 2025)
- `MainWindow` still contains a lot of coordination, splitter/filter, undo/redo, and panel logic.
- Next, extract splitter/filters logic to a `SplitterManager`.
- Move undo/redo logic to a dedicated `UndoManager`.
- Extract the tree area (`TreeArea`) and right/content panel (`RightPane`) into their own modules/classes for further modularity.
- After each extraction, update wiring in `MainWindow` and test incrementally.
- Continue to keep `MainWindow` as a thin coordinator.
- Toolbar and menu setup logic is now delegated to `ToolbarManager` and `MenuManager`.
- File open/save/recent logic is now in `FileManager` and fully wired in `MainWindow`.
- All file operations now prompt for unsaved changes as expected.
- Edits in content panels are reliably saved before file operations.
- Deleting content in one panel updates all panels and prevents stale references.
- The settings node (`_settings`) is now hidden from the tree view.
- Window title updates after 'Save As'.
- **Important:** Test the application after each major refactor step to catch wiring or import issues early.
- Consider extracting `TreeArea` (see `tree_view.py`) and `RightPane` soon for further modularization.
- Use this file to track architectural decisions, todos, and migration notes.
- Add any design notes, open questions, or migration blockers here as you proceed.

---

# Refactoring Progress (2025-07-05)

## Completed (2025-07-05)
- All major UI components are modularized (tree view, content panel, main window) using mixins and manager/helper modules.
- CustomSplitter and CustomSplitterHandle implemented and integrated everywhere:
    - Prevents full collapse, always shows a visible, labeled handle.
    - Draws a label for collapsed regions (rotated for horizontal splitters).
    - Label dynamically reflects the content of the hidden/collapsed panel, or uses explicit label from addWidget.
    - Robustly saves/restores layout state as ratios.
    - Visually clean, theme-aware, and does not overlap content.
- All splitters (main, content, per-panel) now use CustomSplitter with labeled, non-collapsing handles.
- Splitter state is saved as ratios and restored robustly for any window size.
- Collapsed panels show a label and remain restorable.
- All code is maintainable, modular, and documented.
- Debug code and unused imports removed, docstrings added, linter warnings minimized.

## Remaining/Optional
- JSON editor logic remains in MainWindow (could be modularized if needed).
- Settings/user preferences logic (e.g., edit_user_settings) could be moved to a dedicated manager for further modularity.
- Advanced undo/redo scenarios or further maintainability improvements (optional).
- Minor linter warnings (e.g., long docstring lines, unused imports) can be cleaned up.
- Further visual fine-tuning or code cleanup if desired.

## Next Steps
- Continue to document architecture and class responsibilities in PROJECT_OVERVIEW.md.
- Incrementally test and track any further refactor steps.

---

## Modularization of NodeTree (tree_view.py)

- The `NodeTree` class has been fully modularized using mixins:
    - `TreeSearchMixin`: search/filter logic
    - `TreeContextMenuMixin`: context menu and node edit logic
    - `TreeClipboardMixin`: copy/cut/paste logic
    - `TreeDragDropMixin`: drag-and-drop logic
- All major logic is now separated into focused, testable components. `NodeTree` is now a clean, declarative composition of these behaviors.
- The tree view is robust against multiple roots, and all user actions are validated and modular.
- This pattern can be applied to other large widgets for maintainability.

## Modularization of ContentPanelView (right/content panel)

- The `ContentPanelView` class is now modularized using mixins:
    - `ContentFilterMixin`: filtering logic (UI, parser, matching)
    - `ContentTableMixin`: table setup, column/row management
    - `ContentEditorManagerMixin`: editor instantiation and switching
- All major logic is now separated into focused, testable components. `ContentPanelView` is now a clean, declarative composition of these behaviors.
- This pattern matches the modularization of `NodeTree` and can be applied to other large widgets for maintainability.

## Additional Infos
- Right pane is already subdivided (node metadata, content panels, etc.)
- Tree view and right pane should be independent components
- Keep this file updated as the refactor progresses

---

*Last updated: 2025-07-05*
