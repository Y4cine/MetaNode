# -*- coding: utf-8 -*-
"""tree_context_menu_mixin.py
Provides context menu and node edit functionality for QTreeWidget-based tree views.
"""

from PyQt5.QtWidgets import QMenu, QInputDialog
import uuid


class TreeContextMenuMixin:
    def open_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return
        menu = QMenu()
        menu.addAction("Neuer Knoten darunter",
                       lambda: self.add_sibling_after(item))
        menu.addAction("Neuer Unterknoten", lambda: self.add_child_to(item))
        menu.addAction("Umbenennen", lambda: self.rename_item(item))
        menu.addAction("Löschen", lambda: self.delete_item(item))
        menu.exec_(self.viewport().mapToGlobal(position))

    def add_child_to(self, item):
        self.model.push_undo_snapshot()
        parent_id = item.data(0, 32)  # Qt.UserRole == 32
        text, ok = QInputDialog.getText(
            self, "Neuer Knoten", "Titel eingeben:")
        if ok and text:
            parent_node = self.model.find_node(parent_id)
            new_node = parent_node.add_child({
                "title": text,
                "id": str(uuid.uuid4()),
                "children": [], "metadata": {}, "contents": []
            })
            self.model.mark_dirty()
            self.load_model(self.model)
            self.select_node_by_id(new_node.id)

    def add_sibling_after(self, item):
        self.model.push_undo_snapshot()
        node_id = item.data(0, 32)
        node = self.model.find_node(node_id)
        if not node or not node.parent:
            return
        text, ok = QInputDialog.getText(
            self, "Neuer Knoten", "Titel eingeben:")
        if ok and text:
            new_node_data = {
                "title": text, "id": str(uuid.uuid4()),
                "children": [], "metadata": {}, "contents": []
            }
            parent = node.parent
            index = parent.children.index(node)
            parent.children.insert(
                index + 1, type(node)(new_node_data, parent))
            parent.node.setdefault("children", []).insert(
                index + 1, new_node_data)
            self.model.mark_dirty()
            self.load_model(self.model)
            self.select_node_by_id(new_node_data["id"])

    def rename_item(self, item):
        self.model.push_undo_snapshot()
        old_title = item.text(0)
        node_id = item.data(0, 32)
        text, ok = QInputDialog.getText(
            self, "Knoten umbenennen", "Neuer Titel:", text=old_title)
        if ok and text:
            node = self.model.find_node(node_id)
            node.title = text
            self.model.mark_dirty()
            self.load_model(self.model)
            self.select_node_by_id(node_id)

    def delete_item(self, item):
        self.model.push_undo_snapshot()
        node_id = item.data(0, 32)
        node = self.model.find_node(node_id)
        if node and node.parent:
            node.parent.remove_child(node_id)
            self.model.mark_dirty()
            self.load_model(self.model)
