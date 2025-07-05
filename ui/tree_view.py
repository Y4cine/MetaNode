
# -*- coding: utf-8 -*-
"""node_tree.py
This module defines the NodeTree class for displaying and managing a tree structure of nodes
with features like drag-and-drop, context menus, and search functionality.
"""

from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QLineEdit, QCheckBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal

from models.tree_data import TreeDataModel, TreeNodeWrapper

from .tree_search_mixin import TreeSearchMixin
from .tree_context_menu_mixin import TreeContextMenuMixin
from .tree_clipboard_mixin import TreeClipboardMixin
from .tree_dragdrop_mixin import TreeDragDropMixin


class NodeTree(QTreeWidget, TreeSearchMixin, TreeContextMenuMixin, TreeClipboardMixin, TreeDragDropMixin):

    def refresh_tree_integrity(self):
        """
        Ensures there is only one root. If any extra top-level items exist, move them as children of the real root.
        """
        if not self.model or not self.model.root:
            return
        # Collect all top-level items except the real root
        real_root_id = self.model.root.id
        illegal_roots = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            node_id = item.data(0, Qt.UserRole)
            if node_id != real_root_id:
                illegal_roots.append(item)
        if not illegal_roots:
            return
        # Move each illegal root under the real root (as last child)
        for item in illegal_roots:
            node_id = item.data(0, Qt.UserRole)
            node = self.model.find_node(node_id)
            if node and node.parent:
                # Remove from old parent
                node.parent.remove_child(node_id)
            # Add as child of real root
            self.model.root.add_child(node.node)
        self.model.mark_dirty()
        self.load_model(self.model)
        # Optionally, show a warning (uncomment if desired)
        # from PyQt5.QtWidgets import QMessageBox
        # QMessageBox.warning(self, "Tree Integrity Restored", "Some nodes were moved under the root to prevent multiple roots.")

    # -------------------
    # Drag & Drop
    # -------------------
    # (drag-and-drop logic moved to TreeDragDropMixin)
    node_selected = pyqtSignal(str)  # signalisiert node_id

    def __init__(self, parent=None):
        super().__init__(parent)

        # Model und interne Daten
        self.model: TreeDataModel = None
        self.clipboard_node_dict = None

        # Suchfeld + Optionen
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suche...")
        self.search_input.textChanged.connect(self.on_search)

        self.deep_search_checkbox = QCheckBox("Tiefensuche")
        self.deep_search_checkbox.stateChanged.connect(self.on_search)

        # Eingebetteter Container mit Layout
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.search_input)
        layout.addWidget(self.deep_search_checkbox)
        layout.addWidget(self)
        self.container = container

        # Baum-Darstellung konfigurieren
        self.setHeaderLabels(["Knoten"])
        self.setColumnCount(1)
        self.setStyleSheet("""
            QTreeWidget:focus {
                border: 2px solid #0078d7;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)
        self.itemSelectionChanged.connect(self.on_selection_changed)

        # Drag & Drop aktivieren
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QTreeWidget.InternalMove)

    # ------------------------
    # Modellbindung + Aufbau
    # ------------------------

    def load_model(self, model: TreeDataModel):
        self.model = model
        self.clear()
        if model.root:
            root_item = self._build_item_recursive(model.root)
            if root_item is not None:
                self.addTopLevelItem(root_item)
            self.expandAll()

    def _build_item_recursive(self, node: TreeNodeWrapper) -> QTreeWidgetItem:
        # Skip settings node
        if node.id == '_settings':
            return None
        item = QTreeWidgetItem([node.title])
        item.setData(0, Qt.UserRole, node.id)
        for child in node.children:
            child_item = self._build_item_recursive(child)
            if child_item is not None:
                item.addChild(child_item)
        return item

    def select_node_by_id(self, node_id: str):
        def recurse(item):
            if item.data(0, Qt.UserRole) == node_id:
                self.setCurrentItem(item)
                return True
            return any(recurse(item.child(i)) for i in range(item.childCount()))

        for i in range(self.topLevelItemCount()):
            if recurse(self.topLevelItem(i)):
                break

    def on_selection_changed(self):
        items = self.selectedItems()
        if items:
            node_id = items[0].data(0, Qt.UserRole)
            if node_id:
                self.node_selected.emit(node_id)

    # -------------------
    # Kontextmenü + Edit
    # -------------------
    # (context menu and edit logic moved to TreeContextMenuMixin)

    # -------------------
    # Drag & Drop
    # -------------------

    # (drag-and-drop logic moved to TreeDragDropMixin)

    # -------------------
    # Tastaturbedienung
    # -------------------

    def keyPressEvent(self, event):
        item = self.currentItem()
        if not item:
            return super().keyPressEvent(event)

        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key_Return:
            self.add_sibling_after(item)
        elif key == Qt.Key_Insert:
            self.add_child_to(item)
        elif key == Qt.Key_Delete:
            self.delete_item(item)
        elif key == Qt.Key_F2:
            self.rename_item(item)
        elif key == Qt.Key_Up and modifiers == Qt.AltModifier:
            self.move_up(item)
        elif key == Qt.Key_Down and modifiers == Qt.AltModifier:
            self.move_down(item)
        elif key == Qt.Key_C and modifiers == Qt.ControlModifier:
            self.copy_item(item)
        elif key == Qt.Key_X and modifiers == Qt.ControlModifier:
            self.cut_item(item)
        elif key == Qt.Key_V and modifiers == Qt.ControlModifier:
            self.paste_item(item)
        else:
            super().keyPressEvent(event)

    def move_up(self, item):
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        parent = node.parent
        if not parent:
            return
        index = parent.children.index(node)
        if index <= 0:
            return
        self.model.push_undo_snapshot()
        parent.children[index], parent.children[index - 1] = parent.children[index - 1], parent.children[index]
        parent.node["children"][index], parent.node["children"][index - 1] = (
            parent.node["children"][index - 1], parent.node["children"][index]
        )
        self.model.mark_dirty()
        self.load_model(self.model)
        self.select_node_by_id(node_id)

    def move_down(self, item):
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        parent = node.parent
        if not parent:
            return
        index = parent.children.index(node)
        if index >= len(parent.children) - 1:
            return
        self.model.push_undo_snapshot()
        parent.children[index], parent.children[index + 1] = parent.children[index + 1], parent.children[index]
        parent.node["children"][index], parent.node["children"][index + 1] = (
            parent.node["children"][index + 1], parent.node["children"][index]
        )
        self.model.mark_dirty()
        self.load_model(self.model)
        self.select_node_by_id(node_id)
