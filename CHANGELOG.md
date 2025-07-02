## [Unreleased]

### 01.07.2025
- Saved filter status with file. Filters are now in ComboBoxes.

### 25.06.2025
- Refactored UI layout persistence: All relevant QSplitter ratios (main, right panel, content panels, and per-panel splitters) are now saved and restored explicitly using unique keys.
- Removed recursive splitter detection to prevent layout inconsistencies and ensure robust, workflow-safe restoration.
- Cleaned up all debug output for production readiness.
- The layout is now reliably restored for any panel configuration, supporting complex nested structures.

### 23.06.2025
- Implemented the renderer Factory
- Fixed write back bug, contents where lost after editing.
- Renderer encapsulates dynamic editor panels, they raise their own edited events, pass them to the editor panel, which in turn ensures that the data are written back.
- Implemented writing content metadata back
- Implemented managing contents (cut, copy, paste, new, delete, rename) with buttons
- Implemented managing metadata fields (cut, copy, paste, new, delete, rename) with context menü.




### Added
- Right panel refactored into split layout with separate NodeMetadataPanel and multi-panel content area
- Introduced `SingleContentPanel` with filter, metadata tree, and renderer-based editor
- Implemented `ContentMetadataPanel` showing content metadata in editable tree view
- Synchronized editor ↔ metadata view with content selection and updates
