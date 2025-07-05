# -*- coding: utf-8 -*-
"""toolbar_manager.py
Handles creation and setup of the main application toolbars.
"""

from PyQt5.QtWidgets import QAction, QActionGroup
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from core.project_paths import get_path


class ToolbarManager:
    def __init__(self, main_window):
        self.main_window = main_window
        # TODO: Move toolbar setup logic from MainWindow here

    def setup_toolbar(self):
        """Create and configure the main toolbar."""
        toolbar = self.main_window.addToolBar("Bearbeiten")
        toolbar.setIconSize(QSize(24, 24))

        mode_group = QActionGroup(self.main_window)
        mode_group.setExclusive(True)

        self.main_window.action_json_edit_mode = QAction(
            QIcon(str(get_path("icons", "mode_edit.svg"))), "JSON Edit Mode", self.main_window)
        self.main_window.action_json_edit_mode.setCheckable(True)
        self.main_window.action_json_edit_mode.setChecked(True)
        # Connect to ModeManager's set_edit_mode instead of removed MainWindow.set_json_edit_mode
        self.main_window.action_json_edit_mode.triggered.connect(self.main_window.mode_manager.set_edit_mode)
        mode_group.addAction(self.main_window.action_json_edit_mode)
        toolbar.addAction(self.main_window.action_json_edit_mode)

        self.main_window.action_read_mode = QAction(
            QIcon(str(get_path("icons", "mode_read.svg"))), "Read Mode", self.main_window)
        self.main_window.action_read_mode.setCheckable(True)
        self.main_window.action_read_mode.triggered.connect(self.main_window.mode_manager.set_read_mode)
        mode_group.addAction(self.main_window.action_read_mode)
        toolbar.addAction(self.main_window.action_read_mode)

        self.main_window.action_json_mode = QAction(
            QIcon(str(get_path("icons", "mode_json.svg"))), "JSON View", self.main_window)
        self.main_window.action_json_mode.setCheckable(True)
        # Use mode_manager to switch modes, just like the menu
        self.main_window.action_json_mode.triggered.connect(lambda: self.main_window.mode_manager.set_json_mode())
        mode_group.addAction(self.main_window.action_json_mode)
        toolbar.addAction(self.main_window.action_json_mode)

        toolbar.addSeparator()

        toolbar.addAction(QIcon(str(get_path("icons", "new.svg"))),
                          "Neu", self.main_window.file_manager.new_file)
        toolbar.addAction(QIcon(str(get_path("icons", "open.svg"))),
                          "Öffnen", self.main_window.file_manager.open_file)
        toolbar.addAction(QIcon(str(get_path("icons", "save.svg"))),
                          "Speichern", self.main_window.file_manager.save_file)
        toolbar.addSeparator()

        toolbar.addAction(QIcon(str(get_path("icons", "undo.svg"))), "Undo",
                          self.main_window.do_combined_undo)
        toolbar.addAction(QIcon(str(get_path("icons", "redo.svg"))), "Redo",
                          self.main_window.do_combined_redo)
        toolbar.addSeparator()

        toolbar.addAction(QIcon(str(get_path("icons", "add_child.svg"))),
                          "Unterknoten hinzufügen",
                          lambda: self.main_window.tree_area.add_child_to(self.main_window.tree_area.currentItem()))
        toolbar.addAction(QIcon(str(get_path("icons", "add_sibling.svg"))), "Nachbarknoten hinzufügen",
                          lambda: self.main_window.tree_area.add_sibling_after(self.main_window.tree_area.currentItem()))
        toolbar.addAction(QIcon(str(get_path("icons", "delete.svg"))), "Knoten löschen",
                          lambda: self.main_window.tree_area.delete_item(self.main_window.tree_area.currentItem()))
        toolbar.addAction(QIcon(str(get_path("icons", "rename.svg"))), "Knoten umbenennen",
                          lambda: self.main_window.tree_area.rename_item(self.main_window.tree_area.currentItem()))
