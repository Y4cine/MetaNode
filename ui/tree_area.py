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

    def load_model(self, model):
        self.node_tree.load_model(model)

    def select_node_by_id(self, node_id):
        self.node_tree.select_node_by_id(node_id)

    def setFocus(self):
        """Setzt den Fokus auf den Tree (QTreeWidget)."""
        self.node_tree.setFocus()

    # Add more pass-through methods as needed
