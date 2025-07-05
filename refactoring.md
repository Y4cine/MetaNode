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
- [ ] Extract `TreeArea` (tree view logic) into its own module/class
- [ ] Extract `RightPane` (right/content panel logic) into its own module/class
- [ ] Update imports and wiring in `MainWindow` to use new components
- [ ] Subclass QSplitter to create a custom splitter that, when collapsed, still shows a visible handle or indicator (prevents full collapse and provides a visual hint). Integrate this custom splitter everywhere splitters are used (main, content panels, per-panel splitters). [Deferred: revisit after main refactor]

### 3. Notes & Decisions
- Removed obsolete `set_read_mode` and `set_json_edit_mode` from `MainWindow` (now handled by `ModeManager`).
- Confirmed that all file, menu, toolbar, and mode logic is now delegated to managers.

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

## Completed
- Node switching logic is now fully delegated to `NodeEditorPanel` via `switch_node`, with `MainWindow` only coordinating selection events.
- All UI state (splitters, panels, filters) is managed by dedicated manager classes (`SplitterManager`, `PanelStateManager`), not duplicated in `MainWindow`.
- Undo/redo logic is modular and local to panels, with global fallback.
- File, mode, and menu/toolbar logic is fully modularized.
- All major responsibilities are now handled by dedicated classes; `MainWindow` is a thin coordinator.

## Remaining/Optional
- JSON editor logic remains in `MainWindow` (could be modularized if needed).
- Settings/user preferences logic (e.g., `edit_user_settings`) could be moved to a dedicated manager for further modularity.
- Advanced undo/redo scenarios or further maintainability improvements (optional).

## Next Steps
- Continue to document architecture and class responsibilities in `PROJECT_OVERVIEW.md`.
- Incrementally test and track any further refactor steps.

---

## Additional Infos
- Right pane is already subdivided (node metadata, content panels, etc.)
- Tree view and right pane should be independent components
- Keep this file updated as the refactor progresses

---

*Last updated: 2025-07-05*
