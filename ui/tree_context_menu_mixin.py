# -*- coding: utf-8 -*-
"""tree_context_menu_mixin.py
Provides context menu and request emission for node edit actions.
"""

from PyQt5.QtWidgets import QMenu, QInputDialog
from PyQt5.QtCore import Qt


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
        parent_id = item.data(0, Qt.UserRole)
        text, ok = QInputDialog.getText(
            self, "Neuer Knoten", "Titel eingeben:")
        if ok and text:
            self.request_insert_child.emit(parent_id, text)

    def add_sibling_after(self, item):
        node_id = item.data(0, Qt.UserRole)
        text, ok = QInputDialog.getText(
            self, "Neuer Knoten", "Titel eingeben:")
        if ok and text:
            self.request_insert_sibling_after.emit(node_id, text)

    def rename_item(self, item):
        old_title = item.text(0)
        node_id = item.data(0, Qt.UserRole)
        text, ok = QInputDialog.getText(
            self, "Knoten umbenennen", "Neuer Titel:", text=old_title)
        if ok and text:
            self.request_rename.emit(node_id, text)

    def delete_item(self, item):
        node_id = item.data(0, Qt.UserRole)
        self.request_delete.emit(node_id)
