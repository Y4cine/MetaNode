# -*- coding: utf-8 -*-
"""node_metadata_panel.py

This module defines the NodeMetadataPanel class for displaying and editing metadata fields for a specific node.

"""

from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QMenu, QAction, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from models.metadata_model import Metadata


class NodeMetadataPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Feld", "Wert", "Default"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)

        self._metadata: Metadata = None
        self._metadata_clipboard = None  # Für Copy/Cut/Paste von Feldern

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)

    def set_metadata(self, metadata: Metadata):
        """Lädt die Metadaten in die Ansicht"""
        self._metadata = metadata
        self.tree.clear()

        schema = metadata.schema or {}
        defined_keys = set(schema.get("properties", {}).keys())

        # Zuerst: Felder aus dem Schema
        for key in defined_keys:
            actual = str(metadata.get(key, ""))
            default = str(schema["properties"][key].get("default", ""))
            self._add_row(key, actual, default)

        # Dann: zusätzliche Felder
        for key in metadata.data.keys():
            if key in defined_keys:
                continue
            val = str(metadata.get(key))
            self._add_row(key, val, "(frei)")

    def _add_row(self, key: str, actual: str, default: str):
        item = QTreeWidgetItem([key, actual, default])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.tree.addTopLevelItem(item)

    def get_metadata(self) -> Metadata:
        """Liest die bearbeiteten Werte aus dem TreeView"""
        new_data = {}
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            key = item.text(0).strip()
            val = item.text(1).strip()
            new_data[key] = val
        return Metadata(new_data, self._metadata.schema if self._metadata else {})

    def _show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return  # Nur auf Feldern
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
        if not ok or not key:
            return
        # Prevent duplicate keys
        for i in range(self.tree.topLevelItemCount()):
            if self.tree.topLevelItem(i).text(0) == key:
                QMessageBox.warning(self, "Fehler", f"Feld '{key}' existiert bereits.")
                return
        value, ok2 = QInputDialog.getText(self, "Feld hinzufügen", f"Wert für '{key}':")
        if ok2:
            new_child = QTreeWidgetItem([key, value, ""])
            new_child.setFlags(new_child.flags() | Qt.ItemIsEditable)
            self.tree.addTopLevelItem(new_child)

    def rename_metadata_field(self, item):
        key = item.text(0)
        new_key, ok = QInputDialog.getText(self, "Feld umbenennen", "Neuer Name:", text=key)
        if ok and new_key and new_key != key:
            # Prevent renaming to an existing key
            for i in range(self.tree.topLevelItemCount()):
                if self.tree.topLevelItem(i).text(0) == new_key:
                    QMessageBox.warning(self, "Fehler", f"Feld '{new_key}' existiert bereits.")
                    return
            item.setText(0, new_key)

    def delete_metadata_field(self, item):
        idx = self.tree.indexOfTopLevelItem(item)
        if idx >= 0:
            self.tree.takeTopLevelItem(idx)

    def copy_metadata_field(self, item):
        self._metadata_clipboard = (item.text(0), item.text(1))

    def cut_metadata_field(self, item):
        self.copy_metadata_field(item)
        self.delete_metadata_field(item)

    def paste_metadata_field(self, item):
        if not self._metadata_clipboard:
            return
        key, value = self._metadata_clipboard
        # Prevent duplicate keys
        for i in range(self.tree.topLevelItemCount()):
            if self.tree.topLevelItem(i).text(0) == key:
                QMessageBox.warning(self, "Fehler", f"Feld '{key}' existiert bereits.")
                return
        new_child = QTreeWidgetItem([key, value, ""])
        new_child.setFlags(new_child.flags() | Qt.ItemIsEditable)
        # Insert after the current item if possible
        idx = self.tree.indexOfTopLevelItem(item)
        if idx >= 0:
            self.tree.insertTopLevelItem(idx + 1, new_child)
        else:
            self.tree.addTopLevelItem(new_child)
