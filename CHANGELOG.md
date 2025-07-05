## [Unreleased]

### 2025-07-05 (Custom Splitter & UI Modularization)
- All splitters (main, content, per-panel) now use a custom `CustomSplitter`/`CustomSplitterHandle`:
    - Prevents full collapse, always shows a visible, labeled handle.
    - Draws a label for collapsed regions (rotated for horizontal splitters).
    - Label dynamically reflects the content of the hidden/collapsed panel, or uses explicit label from `addWidget`.
    - Robustly saves/restores layout state as ratios.
    - Visually clean, theme-aware, and does not overlap content.
    - All code is maintainable, modular, and documented.
- All major UI components are modularized (tree view, content panel, main window) using mixins and manager/helper modules.
- Debug code and unused imports removed, docstrings added, linter warnings minimized.

### 2025-07-05 (Major Refactor)
- Removed all in-place and sub-node JSON editing. JSON editing is now only possible via a modal dialog for the full model.
- The right pane always shows structured editors; no more direct JSON editing for nodes or content.
- All file, menu, toolbar, and mode logic is now delegated to manager classes.
- UI state, undo/redo, and data flows are robust and modular.
- The codebase is ready for further modularization and extension.

### 2025-07-04 (UI/UX)
- User settings can now be opened via menu and edited in your standard text editor.
- User settings has now an option "open_last" to open the last opened file.
- The app title shows now the current open file.
- Toolbar now features three exclusive toggle buttons for Edit, Read, and JSON view modes (icons: `mode_edit.svg`, `mode_read.svg`, `mode_json.svg`).
- Synchronization between menu and toolbar: switching the view mode via menu or toolbar always updates the other (toggle state and enabled/disabled state).
- Placeholder icons are used; can be replaced by user-supplied icons with the same names in the `icons` folder.

### 2025-07-04 (Addendum)
- File menu: Submenu "Recently Opened" shows the last opened files, direct navigation possible.
- Recent files list is managed automatically, only existing files are shown, no duplicates due to slash mix.
- Paths are normalized on save and load (`os.path.normpath`).
- Initial example (`memetik.json`) is automatically added to recent files on first start (if present).
- Extensive debug output for user settings and file handling added (can be removed after debugging phase).
- Theme switching no longer affects recent files or file handling.
- Improved error handling when loading the initial file and for path issues.

### 2025-07-04
- User settings are now automatically saved in the user profile and restored on startup (e.g. selected theme).
- Settings are stored cross-platform in the appropriate user folder (`AppData/Roaming/MetaNode` etc.) as JSON.
- New utility file: `utils/user_settings.py` for robust, extensible settings handling.
- Theme switching for the entire application via menu item under "View" implemented (CSS stylesheets for light/dark mode).
- Theme change takes effect immediately and without duplicates in menus/toolbars – menu structure always remains correct.
- Robust menu and toolbar initialization: No more duplicates when switching themes.
- Two example themes (`resources/theme_light.css`, `resources/theme_dark.css`) added.

### 2025-07-01
- Saved filter status with file. Filters are now in ComboBoxes.

### 2025-06-25
- Refactored UI layout persistence: All relevant QSplitter ratios (main, right panel, content panels, and per-panel splitters) are now saved and restored explicitly using unique keys.
- Removed recursive splitter detection to prevent layout inconsistencies and ensure robust, workflow-safe restoration.
- Cleaned up all debug output for production readiness.
- The layout is now reliably restored for any panel configuration, supporting complex nested structures.

### 2025-06-23
- Implemented the renderer factory.
- Fixed write-back bug, contents were lost after editing.
- Renderer encapsulates dynamic editor panels, they raise their own edited events, pass them to the editor panel, which in turn ensures that the data are written back.
- Implemented writing content metadata back.
- Implemented managing contents (cut, copy, paste, new, delete, rename) with buttons.
- Implemented managing metadata fields (cut, copy, paste, new, delete, rename) with context menu.

### Added
- Right panel refactored into split layout with separate NodeMetadataPanel and multi-panel content area.
- Introduced `SingleContentPanel` with filter, metadata tree, and renderer-based editor.
- Implemented `ContentMetadataPanel` showing content metadata in editable tree view.
- Synchronized editor ↔ metadata view with content selection and updates.
