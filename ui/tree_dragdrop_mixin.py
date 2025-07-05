# -*- coding: utf-8 -*-
"""tree_dragdrop_mixin.py
Provides drag-and-drop functionality for QTreeWidget-based tree views.
"""

from PyQt5.QtWidgets import QTreeWidget


class TreeDragDropMixin:
    def dropMimeData(self, parent, index, data, action):
        # Block all drops that would create a new root (parent is None and not root node)
        selected_items = self.selectedItems()
        if parent is None and selected_items:
            dragged_id = selected_items[0].data(0, 32)  # Qt.UserRole == 32
            if self.model.root and dragged_id != self.model.root.id:
                return False
        return super().dropMimeData(parent, index, data, action)

    def dragMoveEvent(self, event):
        # Prevent dropping as a new root (no new top-level items)
        pos = event.pos()
        target_item = self.itemAt(pos)
        drop_pos = self.dropIndicatorPosition()
        dragged_item = self.currentItem()
        # Block all drops where target_item is None (empty area = new root)
        if not dragged_item or not target_item:
            event.ignore()
            return
        # If dropping at top level (no parent) and not on the root, block
        if not target_item.parent() and drop_pos != QTreeWidget.OnItem:
            event.ignore()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event):
        pos = event.pos()
        target_item = self.itemAt(pos)
        drop_pos = self.dropIndicatorPosition()
        dragged_item = self.currentItem()
        # Block all drops where target_item is None (empty area = new root)
        if not dragged_item or not target_item:
            event.ignore()
            return
        # Prevent dropping as a new root (no new top-level items)
        if not target_item.parent() and drop_pos != QTreeWidget.OnItem:
            # Only allow dropping the root node itself at the top level
            dragged_id = dragged_item.data(0, 32)
            if self.model.root and dragged_id != self.model.root.id:
                event.ignore()
                return
        dragged_id = dragged_item.data(0, 32)
        target_id = target_item.data(0, 32)
        target_node = self.model.find_node(target_id)

        if drop_pos == QTreeWidget.OnItem:
            success = self.model.move_node(dragged_id, target_id)
        else:
            parent_item = target_item.parent()
            # Block promoting any node to root (parent_item is None and not root)
            if parent_item is None and (not self.model.root or dragged_id != self.model.root.id):
                event.ignore()
                return
            parent_id = parent_item.data(0, 32) if parent_item else self.model.root.id
            parent_node = self.model.find_node(parent_id)
            try:
                target_index = parent_node.children.index(target_node)
            except ValueError:
                return  # Prevent crash if structure is inconsistent
            if drop_pos == QTreeWidget.BelowItem:
                target_index += 1
            success = self.model.move_node_to_index(
                dragged_id, parent_id, target_index)

        if success:
            self.model.push_undo_snapshot()
            self.model.mark_dirty()
            self.load_model(self.model)
            self.select_node_by_id(dragged_id)
        super().dropEvent(event)
        # Always check for illegal roots after a drop (call after super to catch all cases)
        self.refresh_tree_integrity()
