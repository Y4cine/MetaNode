## [Unreleased]
### 23.06.2025
- Implemented the renderer Factory
- Fixed write back bug, contents where lost after editing.
- Renderer encapsulates dynamic editor panels, they raise their own edited events, pass them to the editor panel, which in turn ensures that the data are written back.
- Implemented writing content metadata back

### Added
- Right panel refactored into split layout with separate NodeMetadataPanel and multi-panel content area
- Introduced `SingleContentPanel` with filter, metadata tree, and renderer-based editor
- Implemented `ContentMetadataPanel` showing content metadata in editable tree view
- Synchronized editor ↔ metadata view with content selection and updates
