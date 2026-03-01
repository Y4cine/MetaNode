# -*- coding: utf-8 -*-
"""tree_area.py
Encapsulates the navigation/tree view logic for MetaNode.
"""

from PyQt5.QtCore import pyqtSignal
from ui.tree_view import NodeTree


class TreeArea:
    """
    Wrapper for the NodeTree and its container, exposing a clean interface for MainWindow.
    """
    node_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        self.node_tree = NodeTree(parent)
        self.container = self.node_tree.container
        self.node_selected = self.node_tree.node_selected
        self.selected = self.node_tree.selected
        self.request_insert_child = self.node_tree.request_insert_child
        self.request_insert_sibling_after = self.node_tree.request_insert_sibling_after
        self.request_delete = self.node_tree.request_delete
        self.request_rename = self.node_tree.request_rename
        self.request_move = self.node_tree.request_move

    def load_model(self, model):
        self.node_tree.load_model(model)

    def select_node_by_id(self, node_id):
        self.node_tree.select_node_by_id(node_id)

    def setFocus(self):
        """Setzt den Fokus auf den Tree (QTreeWidget)."""
        self.node_tree.setFocus()

    def currentItem(self):
        return self.node_tree.currentItem()

    def add_child_to(self, item):
        return self.node_tree.add_child_to(item)

    def add_sibling_after(self, item):
        return self.node_tree.add_sibling_after(item)

    def delete_item(self, item):
        return self.node_tree.delete_item(item)

    def rename_item(self, item):
        return self.node_tree.rename_item(item)

    def refresh_from_store(self, store):
        self.node_tree.load_model(store)
