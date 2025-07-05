# -*- coding: utf-8 -*-
"""mode_manager.py
Handles mode switching (edit, read, JSON view) for the main window.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox, QSplitter
from widgets.json_editor import JsonEditor


class ModeManager:
    def __init__(self, main_window):
        self.main_window = main_window
        # Track current mode if needed (e.g., 'edit', 'read', 'json')
        self.current_mode = None
        # Save the original editor panel reference at startup
        self.main_window._editor_panel = self.main_window.right_area

    def set_edit_mode(self):
        # Synchronize toolbar and menu
        if hasattr(self.main_window, 'action_json_edit_mode'):
            self.main_window.action_json_edit_mode.setChecked(True)
        if hasattr(self.main_window, 'menu_action_json_edit_mode'):
            self.main_window.menu_action_json_edit_mode.setEnabled(False)
            self.main_window.menu_action_read_mode.setEnabled(True)
            self.main_window.menu_action_json_mode.setEnabled(True)
        # Restore the original editor panel if coming from JSON or read mode
        splitter = self.main_window.centralWidget().findChild(QSplitter)
        if splitter:
            # Save reference to the current editor panel if not already
            if not hasattr(self.main_window, '_editor_panel') or self.main_window._editor_panel is None:
                self.main_window._editor_panel = self.main_window.right_area
            # Remove JSON or read panel and restore editor panel
            if isinstance(self.main_window.right_area, (JsonEditor,)) or getattr(self.main_window, '_read_panel', None) is not None:
                idx = splitter.indexOf(self.main_window.right_area)
                editor_panel = getattr(self.main_window, '_editor_panel', None)
                if editor_panel:
                    splitter.insertWidget(idx, editor_panel)
                    next_widget = splitter.widget(idx+1)
                    if next_widget is not None:
                        next_widget.setParent(None)
                    self.main_window.right_area = editor_panel
            self.main_window._read_panel = None
            self.main_window._json_editor = None
        self.current_mode = 'edit'

    def set_read_mode(self):
        # Synchronize toolbar and menu
        if hasattr(self.main_window, 'action_json_edit_mode'):
            self.main_window.action_json_edit_mode.setChecked(False)
        if hasattr(self.main_window, 'action_json_mode'):
            self.main_window.action_json_mode.setChecked(False)
        if hasattr(self.main_window, 'menu_action_read_mode'):
            self.main_window.menu_action_read_mode.setEnabled(False)
            if hasattr(self.main_window, 'menu_action_json_edit_mode'):
                self.main_window.menu_action_json_edit_mode.setEnabled(True)
            if hasattr(self.main_window, 'menu_action_json_mode'):
                self.main_window.menu_action_json_mode.setEnabled(True)
        # Only switch if not already in read mode
        if hasattr(self.main_window, '_read_panel') and self.main_window._read_panel is not None:
            self.current_mode = 'read'
            return
        # Save reference to the editor panel if not already
        if not hasattr(self.main_window, '_editor_panel') or self.main_window._editor_panel is None:
            self.main_window._editor_panel = self.main_window.right_area
        # Create and insert NodeReadPanel
        from widgets.node_read_panel import NodeReadPanel
        splitter = self.main_window.centralWidget().findChild(QSplitter)
        if splitter:
            idx = splitter.indexOf(self.main_window.right_area)
            read_panel = NodeReadPanel(
                tree_model=self.main_window.model,
                tree_view=self.main_window.tree_area,
                meta_schema=self.main_window.meta_schema,
                content_schema=self.main_window.content_schema,
                parent=self.main_window
            )
            if hasattr(self.main_window.right_area, '_node') and self.main_window.right_area._node is not None:
                node = self.main_window.right_area._node
                if hasattr(read_panel, 'set_node'):
                    read_panel.set_node(node)
            splitter.insertWidget(idx, read_panel)
            splitter.widget(idx+1).setParent(None)
            self.main_window.right_area = read_panel
            self.main_window._read_panel = read_panel
            self.main_window._json_editor = None
        self.current_mode = 'read'

    def set_json_mode(self):
        # Synchronize toolbar and menu
        if hasattr(self.main_window, 'action_json_mode'):
            self.main_window.action_json_mode.setChecked(True)
        if hasattr(self.main_window, 'menu_action_json_mode'):
            self.main_window.menu_action_json_mode.setEnabled(False)
            if hasattr(self.main_window, 'menu_action_json_edit_mode'):
                self.main_window.menu_action_json_edit_mode.setEnabled(True)
            if hasattr(self.main_window, 'menu_action_read_mode'):
                self.main_window.menu_action_read_mode.setEnabled(True)
        # Instead of replacing the right pane, open the modal dialog for full model editing
        if hasattr(self.main_window, 'show_json_view'):
            self.main_window.show_json_view()
        # After closing the dialog, remain in the previous mode (do not change right_area)
        self.current_mode = 'json'

    def get_mode(self):
        return self.current_mode
