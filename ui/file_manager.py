# -*- coding: utf-8 -*-
"""file_manager.py
Handles file open, save, save as, and recent files logic for the application.
"""

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from core.project_settings import get_settings, set_settings
from models.tree_data import TreeDataModel
from models.node_model import Node

from utils.user_settings import get_recent_files, add_recent_file
from PyQt5.QtCore import Qt


class FileManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def open_file(self):
        if not self.maybe_save_before_exit():
            return
        path, _ = QFileDialog.getOpenFileName(
            self.main_window, "Datei öffnen", "", "JSON-Dateien (*.json)")
        if path:
            print(f"[DEBUG] Datei öffnen: {path}")
            self.main_window.set_window_title_with_path(path)
            if hasattr(self.main_window, 'set_json_edit_mode'):
                self.main_window.set_json_edit_mode()
            self.main_window.model.load_from_file(path)
            self.main_window.tree_area.load_model(self.main_window.model)
            tree_data = self.main_window.model.to_dict()
            settings = get_settings(tree_data)
            if 'global_filters' in settings and hasattr(self.main_window.right_area, 'content_stack') and hasattr(self.main_window.right_area.content_stack, 'set_global_filters'):
                self.main_window.right_area.content_stack.set_global_filters(settings['global_filters'])
            set_settings(tree_data, settings)
            self.main_window.model.load_from_dict(tree_data)
            from core.project_settings import restore_layout_from_settings
            restore_layout_from_settings(settings, self.main_window.right_area, self.main_window)
            node_id = self.main_window.last_node_id or "root"
            node_wrapper = self.main_window.model.find_node(node_id)
            if node_wrapper:
                raw_node = node_wrapper.node
                node_obj = Node(raw_node, self.main_window.meta_schema, self.main_window.content_schema)
                self.main_window.right_area.load_node(node_obj)
            else:
                self.main_window.right_area.load_node(None)
            print(f"[DEBUG] Füge Datei zu Recent Files hinzu: {path}")
            add_recent_file(path)
            print("[DEBUG] Aktualisiere Recent Files Menü")
            self.update_recent_files_menu()

    def save_file(self):
        if self.main_window.right_area._node is not None:
            node_wrapper = self.main_window.model.find_node(self.main_window.right_area._node.id)
            if node_wrapper:
                updated = self.main_window.right_area.update_and_return_node()
                node_wrapper.node.update(updated.to_dict())
                self.main_window.model.mark_dirty()
        tree_data = self.main_window.model.to_dict()
        settings = get_settings(tree_data)
        # Use PanelStateManager to collect all relevant state
        panel_state = self.main_window.panel_state_manager.collect_state()
        settings['splitters'] = panel_state.get('splitters', {})
        settings['filters'] = panel_state.get('filters', {})
        if 'global_filters' in panel_state:
            settings['global_filters'] = panel_state['global_filters']
        set_settings(tree_data, settings)
        self.main_window.model.load_from_dict(tree_data)
        try:
            self.main_window.model.save_to_file()
        except ValueError:
            self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self.main_window, "Speichern unter", "", "JSON-Dateien (*.json)")
        if path:
            self.main_window.model.save_to_file(path)
            self.main_window.set_window_title_with_path(path)
            return True
        return False

    def maybe_save_before_exit(self):
        if not self.main_window.model or not self.main_window.model.is_dirty():
            return True
        reply = QMessageBox.question(
            self.main_window,
            "Änderungen speichern?",
            "Möchten Sie die Änderungen vor dem Schließen speichern?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        if reply == QMessageBox.Yes:
            try:
                self.main_window.model.save_to_file()
            except ValueError:
                return self.save_file_as()
            return True
        elif reply == QMessageBox.No:
            return True
        else:
            return False

    def update_recent_files_menu(self):
        self.main_window.recent_files_menu.clear()
        recent_files = get_recent_files()
        if not recent_files:
            self.main_window.recent_files_menu.addAction("(Keine)").setEnabled(False)
            return
        for path in recent_files:
            action = self.main_window.recent_files_menu.addAction(path)
            action.triggered.connect(lambda checked, p=path: self.open_recent_file(p))

    def open_recent_file(self, path):
        if not self.maybe_save_before_exit():
            return
        if path:
            self.main_window.set_window_title_with_path(path)
            if hasattr(self.main_window, 'set_edit_mode'):
                self.main_window.set_edit_mode()
            self.main_window.model.load_from_file(path)
            self.main_window.tree_area.load_model(self.main_window.model)
            tree_data = self.main_window.model.to_dict()
            settings = get_settings(tree_data)
            if 'global_filters' in settings and hasattr(self.main_window.right_area, 'content_stack') and hasattr(self.main_window.right_area.content_stack, 'set_global_filters'):
                self.main_window.right_area.content_stack.set_global_filters(settings['global_filters'])
            set_settings(tree_data, settings)
            self.main_window.model.load_from_dict(tree_data)
            from core.project_settings import restore_layout_from_settings
            restore_layout_from_settings(settings, self.main_window.right_area, self.main_window)
            node_id = self.main_window.last_node_id or "root"
            node_wrapper = self.main_window.model.find_node(node_id)
            # Only call load_node if right_area supports it (e.g., NodeEditorPanel)
            if hasattr(self.main_window.right_area, "load_node"):
                if node_wrapper:
                    raw_node = node_wrapper.node
                    node_obj = Node(raw_node, self.main_window.meta_schema, self.main_window.content_schema)
                    self.main_window.right_area.load_node(node_obj)
                else:
                    self.main_window.right_area.load_node(None)
            # If right_area is a JsonEditor, optionally set the node or skip
            elif hasattr(self.main_window.right_area, "set_node"):
                if node_wrapper:
                    raw_node = node_wrapper.node
                    node_obj = Node(raw_node, self.main_window.meta_schema, self.main_window.content_schema)
                    self.main_window.right_area.set_node(node_obj)
                else:
                    self.main_window.right_area.set_node(None)
            # Otherwise, do nothing (for other pluggable editors)
            add_recent_file(path)
            self.update_recent_files_menu()

    def new_file(self):
        if not self.maybe_save_before_exit():
            return
        self.main_window.model = TreeDataModel()
        self.main_window.model.load_from_dict({
            "id": "root",
            "title": "Neue Struktur",
            "children": [],
            "metadata": {},
            "contents": []
        })
        self.main_window.tree_area.load_model(self.main_window.model)
        self.main_window.right_area.load_node(None)
        self.main_window.set_window_title_with_path(None)
