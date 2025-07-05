
# -*- coding: utf-8 -*-
"""node_tree.py
This module defines the NodeTree class for displaying and managing a tree structure of nodes
with features like drag-and-drop, context menus, and search functionality.
"""

from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog,
    QVBoxLayout, QLineEdit, QCheckBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
import json
import uuid

from models.tree_data import TreeDataModel, TreeNodeWrapper


class NodeTree(QTreeWidget):
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
        parent_id = item.data(0, Qt.UserRole)
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
        node_id = item.data(0, Qt.UserRole)
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
                index + 1, TreeNodeWrapper(new_node_data, parent))
            parent.node.setdefault("children", []).insert(
                index + 1, new_node_data)
            self.model.mark_dirty()
            self.load_model(self.model)
            self.select_node_by_id(new_node_data["id"])

    def rename_item(self, item):
        self.model.push_undo_snapshot()
        old_title = item.text(0)
        node_id = item.data(0, Qt.UserRole)
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
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        if node and node.parent:
            node.parent.remove_child(node_id)
            self.model.mark_dirty()
            self.load_model(self.model)

    # -------------------
    # Drag & Drop
    # -------------------

    def dropEvent(self, event):
        pos = event.pos()
        target_item = self.itemAt(pos)
        drop_pos = self.dropIndicatorPosition()
        dragged_item = self.currentItem()
        if not dragged_item or not target_item:
            return

        dragged_id = dragged_item.data(0, Qt.UserRole)
        target_id = target_item.data(0, Qt.UserRole)
        target_node = self.model.find_node(target_id)

        if drop_pos == QTreeWidget.OnItem:
            success = self.model.move_node(dragged_id, target_id)
        else:
            parent_item = target_item.parent()
            parent_id = parent_item.data(
                0, Qt.UserRole) if parent_item else self.model.root.id
            parent_node = self.model.find_node(parent_id)
            target_index = parent_node.children.index(target_node)
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
        parent.children[index], parent.children[index -
                                                1] = parent.children[index - 1], parent.children[index]
        parent.node["children"][index], parent.node["children"][index -
                                                                1] = parent.node["children"][index - 1], parent.node["children"][index]
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
        parent.children[index], parent.children[index +
                                                1] = parent.children[index + 1], parent.children[index]
        parent.node["children"][index], parent.node["children"][index +
                                                                1] = parent.node["children"][index + 1], parent.node["children"][index]
        self.model.mark_dirty()
        self.load_model(self.model)
        self.select_node_by_id(node_id)

    # -------------------
    # Zwischenablage (Copy/Cut/Paste)
    # -------------------

    def assign_new_ids(self, node_dict):
        node_dict["id"] = str(uuid.uuid4())
        for child in node_dict.get("children", []):
            self.assign_new_ids(child)

    def copy_item(self, item):
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        self.clipboard_node_dict = node.to_dict()

    def cut_item(self, item):
        node_id = item.data(0, Qt.UserRole)
        node = self.model.find_node(node_id)
        self.clipboard_node_dict = node.to_dict()
        if node.parent:
            self.model.push_undo_snapshot()
            node.parent.remove_child(node_id)
            self.model.mark_dirty()
            self.load_model(self.model)

    def paste_item(self, item):
        if not self.clipboard_node_dict:
            return
        parent_id = item.data(0, Qt.UserRole)
        parent_node = self.model.find_node(parent_id)
        if not parent_node:
            return
        self.model.push_undo_snapshot()
        new_node = json.loads(json.dumps(self.clipboard_node_dict))
        self.assign_new_ids(new_node)
        parent_node.add_child(new_node)
        self.model.mark_dirty()
        self.load_model(self.model)
        self.select_node_by_id(new_node["id"])

    def copy_selected(self):
        item = self.currentItem()
        if item:
            self.copy_item(item)

    def cut_selected(self):
        item = self.currentItem()
        if item:
            self.cut_item(item)

    def paste_to_selected(self):
        item = self.currentItem()
        if item:
            self.paste_item(item)

    # -------------------
    # Suche
    # -------------------

    def on_search(self):
        text = self.search_input.text().strip().lower()
        deep = self.deep_search_checkbox.isChecked()
        self.filter_tree(text, deep)

    def filter_tree(self, query: str, deep: bool):
        def recurse_filter(item: QTreeWidgetItem) -> bool:
            node_id = item.data(0, Qt.UserRole)
            node = self.model.find_node(node_id)
            matched = self.node_matches(node, query, deep)
            visible_child = any(recurse_filter(item.child(i))
                                for i in range(item.childCount()))
            item.setHidden(not (matched or visible_child))
            return matched or visible_child

        for i in range(self.topLevelItemCount()):
            recurse_filter(self.topLevelItem(i))

    def node_matches(self, node: TreeNodeWrapper, query: str, deep: bool) -> bool:
        if not query:
            return True

        def match_value(value):
            if isinstance(value, str):
                return query in value.lower()
            elif isinstance(value, list):
                return any(match_value(v) for v in value)
            elif isinstance(value, dict):
                return any(match_value(v) for v in value.values())
            return False

        return match_value(node.node) if deep else query in node.title.lower()
