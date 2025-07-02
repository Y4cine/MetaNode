
# widgets/content_metadata_panel.py
# -*- coding: utf-8 -*-
"""content_metadata_panel.py
This module defines the ContentMetadataPanel class for displaying and managing metadata fields for content.
"""

from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QMenu, QAction, QInputDialog
)
from PyQt5.QtCore import Qt
from typing import List
from models.content_model import Content


class ContentMetadataPanel(QWidget):
    def __init__(self, schema: dict, default_metadata: dict = None, parent=None):
        super().__init__(parent)
        self.schema = schema or {}
        self.default_metadata = default_metadata or {}
        self._metadata_clipboard = None  # Für Copy/Cut/Paste von Feldern
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Feld", "Wert", "Default"])
        self.tree.setAlternatingRowColors(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)

    def set_contents(self, contents: List[Content]):
        self.tree.clear()

        for idx, content in enumerate(contents):
            top = QTreeWidgetItem([f"Content {idx + 1}", "", ""])
            top.setFirstColumnSpanned(True)
            self.tree.addTopLevelItem(top)

            all_keys = set(self.schema.get("properties", {}).keys()) | set(
                content.metadata.data.keys())
            for key in sorted(all_keys):
                actual = str(content.metadata.get(key, ""))
                default = self.default_metadata.get(key)
                if default is None:
                    default = self.schema.get("properties", {}).get(
                        key, {}).get("default", "")
                default = str(default)

                child = QTreeWidgetItem([key, actual, default])
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                top.addChild(child)

            self.tree.expandItem(top)

    def get_metadata_for_index(self, index: int) -> dict:
        """Liefert die aktuellen Metadaten für den Content an Position index als Dict zurück."""
        top = self.tree.topLevelItem(index)
        if not top:
            return {}
        metadata = {}
        for i in range(top.childCount()):
            child = top.child(i)
            key = child.text(0)
            value = child.text(1)
            metadata[key] = value
        return metadata

    def _show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item or not item.parent():
            return  # Nur auf Metadaten-Feldern
        menu = QMenu(self)
        action_add = QAction("Feld hinzufügen", self)
        action_rename = QAction("Feld umbenennen", self)
        action_delete = QAction("Feld löschen", self)
        action_copy = QAction("Feld kopieren", self)
        action_cut = QAction("Feld ausschneiden", self)
        action_paste = QAction("Feld einfügen", self)
        menu.addAction(action_add)
        menu.addAction(action_rename)
        menu.addAction(action_delete)
        menu.addSeparator()
        menu.addAction(action_copy)
        menu.addAction(action_cut)
        menu.addAction(action_paste)
        action_add.triggered.connect(lambda: self.add_metadata_field(item))
        action_rename.triggered.connect(lambda: self.rename_metadata_field(item))
        action_delete.triggered.connect(lambda: self.delete_metadata_field(item))
        action_copy.triggered.connect(lambda: self.copy_metadata_field(item))
        action_cut.triggered.connect(lambda: self.cut_metadata_field(item))
        action_paste.triggered.connect(lambda: self.paste_metadata_field(item))
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def add_metadata_field(self, item):
        key, ok = QInputDialog.getText(self, "Feld hinzufügen", "Name des neuen Felds:")
        if ok and key:
            value, ok2 = QInputDialog.getText(self, "Feld hinzufügen", f"Wert für '{key}':")
            if ok2:
                parent = item.parent()
                new_child = QTreeWidgetItem([key, value, ""])
                new_child.setFlags(new_child.flags() | Qt.ItemIsEditable)
                parent.addChild(new_child)
                parent.setExpanded(True)

    def rename_metadata_field(self, item):
        key = item.text(0)
        new_key, ok = QInputDialog.getText(self, "Feld umbenennen", "Neuer Name:", text=key)
        if ok and new_key and new_key != key:
            item.setText(0, new_key)

    def delete_metadata_field(self, item):
        parent = item.parent()
        if parent:
            parent.removeChild(item)

    def copy_metadata_field(self, item):
        self._metadata_clipboard = (item.text(0), item.text(1))

    def cut_metadata_field(self, item):
        self.copy_metadata_field(item)
        self.delete_metadata_field(item)

    def paste_metadata_field(self, item):
        if not self._metadata_clipboard:
            return
        parent = item.parent()
        if parent:
            key, value = self._metadata_clipboard
            new_child = QTreeWidgetItem([key, value, ""])
            new_child.setFlags(new_child.flags() | Qt.ItemIsEditable)
            parent.addChild(new_child)
            parent.setExpanded(True)
