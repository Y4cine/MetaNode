# -*- coding: utf-8 -*-
"""node_editor_panel.py
This module defines the NodeEditorPanel class for editing nodes in the application.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt5.QtCore import Qt
from typing import Optional

from widgets.node_metadata_panel import NodeMetadataPanel
from widgets.content_panel_stack import ContentPanelStack
from models.node_model import Node
from models.content_model import Content


class NodeEditorPanel(QWidget):
    def switch_node(self, node_obj, model, meta_schema, content_schema):
        # Save current node if needed
        if hasattr(self, '_node') and self._node is not None:
            node_wrapper = model.find_node(self._node.id)
            if node_wrapper:
                updated = self.update_and_return_node()
                node_wrapper.node.update(updated.to_dict())
                model.mark_dirty()
        # Load new node
        if node_obj is not None:
            self.load_node(node_obj)

    def on_content_edited(self):
        # Push undo snapshot on every content edit
        self.push_undo_snapshot()
        # Forward to main window if possible
        main_win = self.parent()
        while main_win and not hasattr(main_win, 'on_content_edited'):
            main_win = main_win.parent()
        if main_win and hasattr(main_win, 'on_content_edited'):
            main_win.on_content_edited()

    def __init__(self, meta_schema, content_schema, parent=None, splitter_manager=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema

        self.meta_panel = NodeMetadataPanel()
        self.content_stack = ContentPanelStack(meta_schema, content_schema, splitter_manager=splitter_manager)

        if splitter_manager is not None:
            self.splitter = splitter_manager.create_splitter(Qt.Vertical)
        else:
            from ui.custom_splitter import CustomSplitter
            self.splitter = CustomSplitter(Qt.Vertical, collapsed_label="Node Metadata")
        self.splitter.addWidget(self.meta_panel, "Node Metadata")
        self.splitter.addWidget(self.content_stack, "Content Panel")

        self.splitter.setSizes([200, 600])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)

        self._node: Optional[Node] = None

    def load_node(self, node: Optional[Node]):
        self._node = node
        if node:
            self.meta_panel.set_metadata(node.metadata)

            if not node.contents:
                dummy = Content({
                    "content_type": "text",
                    "title": "Neuer Inhalt",
                    "data": {"text": ""},
                    "renderer": "text_blocks",
                    "metadata": {}
                }, self.content_schema)
                node.contents.append(dummy)

            self.content_stack.set_contents_for_all(node.contents)
        # Clear undo stack and push initial state
        self.undo_manager = self.UndoManager()
        self.push_undo_snapshot()

    def update_and_return_node(self) -> Node:
        # Metadaten aus TreeView holen
        self._node.metadata = self.meta_panel.get_metadata()

        # --- NEW: Flush all content editors before collecting contents ---
        for panel in self.content_stack.panel_views:
            if hasattr(panel, '_write_back_current'):
                panel._write_back_current()

        contents = []
        # Use the first panel's _all_contents as the source of truth
        for c in self.content_stack.panel_views[0]._all_contents:
            if not c.title.strip() and not c.data.get("text", "").strip():
                continue  # leere Dummies überspringen
            contents.append(c)

        self._node.contents = contents
        # --- NEW: Sync all panels after update ---
        self.content_stack.set_contents_for_all(contents)
        # Push undo snapshot after update
        self.push_undo_snapshot()
        return self._node

    # --- Undo/Redo Integration ---
    from core.undo_manager import UndoManager

    def do_undo(self):
        result = self.undo_manager.undo()
        if result is not None:
            self.restore_from_snapshot(result)

    def do_redo(self):
        result = self.undo_manager.redo()
        if result is not None:
            self.restore_from_snapshot(result)

    @property
    def undo(self):
        return self.undo_manager

    def push_undo_snapshot(self):
        snapshot = self.create_snapshot()
        self.undo_manager.push(snapshot)

    def create_snapshot(self):
        # Capture the current state of the panel (content, metadata, etc.)
        return {
            'content': self.get_current_content(),
            'metadata': self.get_current_metadata()
        }

    def restore_from_snapshot(self, snapshot):
        self.set_content(snapshot.get('content'))
        self.set_metadata(snapshot.get('metadata'))

    def get_current_content(self):
        if hasattr(self, '_node') and self._node is not None:
            return self._node.contents
        return None

    def get_current_metadata(self):
        if hasattr(self, '_node') and self._node is not None:
            return self._node.metadata
        return None

    def get_all_content_panels(self):
        """Gibt alle aktiven SingleContentPanel-Instanzen im ContentPanelStack zurück."""
        if hasattr(self.content_stack, 'get_all_content_panels'):
            return self.content_stack.get_all_content_panels()
        # Fallback: Versuche, auf panel_views zuzugreifen
        if hasattr(self.content_stack, 'panel_views'):
            return self.content_stack.panel_views
        return []
